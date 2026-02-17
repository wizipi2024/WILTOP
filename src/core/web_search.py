"""
Web Search Engine v3 - Busca na web e TRAZ a resposta para o chat.
Usa duckduckgo-search (biblioteca oficial) + API DDG + Google scraping (fallback).
PRIORIDADE: SEMPRE trazer resposta no chat. NUNCA abrir navegador.
"""

import re
import requests
from typing import Optional, Dict, List
from src.utils.logger import get_logger

log = get_logger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class WebSearchEngine:
    """Busca na web e retorna a resposta direto no chat."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._ddgs = None

    def _get_ddgs(self):
        """Lazy init da biblioteca duckduckgo-search."""
        if self._ddgs is None:
            try:
                from ddgs import DDGS
                self._ddgs = DDGS()
            except ImportError:
                try:
                    from duckduckgo_search import DDGS
                    self._ddgs = DDGS()
                except ImportError:
                    log.warning("ddgs/duckduckgo-search nao instalado")
                    self._ddgs = False
            except Exception as e:
                log.warning(f"Erro ao inicializar DDGS: {e}")
                self._ddgs = False
        return self._ddgs if self._ddgs is not False else None

    def search(self, query: str, max_results: int = 5) -> Dict:
        """Pesquisa na web - tenta MULTIPLAS fontes ate achar resposta."""
        log.info(f"Buscando: {query}")

        # 1. Tenta duckduckgo-search (biblioteca - MAIS CONFIAVEL)
        result = self._search_ddgs_lib(query, max_results)
        if result and result.get("success"):
            log.info("Resultado via duckduckgo-search lib")
            return result

        # 2. Tenta DDG Instant Answer API
        result = self._search_ddg_api(query)
        if result and result.get("success"):
            log.info("Resultado via DDG API")
            return result

        # 3. Tenta DuckDuckGo HTML scraping
        result = self._search_duckduckgo_html(query)
        if result and result.get("success"):
            log.info("Resultado via DDG HTML")
            return result

        # 4. Fallback: Google scraping
        result = self._search_google(query, max_results)
        if result and result.get("success"):
            log.info("Resultado via Google")
            return result

        # 5. Ultimo recurso: Wikipedia
        result = self._search_wikipedia(query)
        if result and result.get("success"):
            log.info("Resultado via Wikipedia")
            return result

        log.warning(f"Nenhum resultado encontrado para: {query}")
        return {"success": False, "answer": "Nao encontrei resultados para esta busca.", "query": query}

    # =====================================================================
    # FONTE 1: duckduckgo-search (biblioteca Python - MAIS CONFIAVEL)
    # =====================================================================
    def _search_ddgs_lib(self, query: str, max_results: int = 5) -> Optional[Dict]:
        """Busca usando biblioteca duckduckgo-search (a mais confiavel)."""
        ddgs = self._get_ddgs()
        if not ddgs:
            return None

        try:
            # Busca de texto
            results = list(ddgs.text(query, region="br-pt", max_results=max_results))

            if not results:
                return None

            # Monta resposta com snippets
            lines = []
            for r in results:
                title = r.get("title", "")
                body = r.get("body", "")
                href = r.get("href", "")
                if body:
                    lines.append(f"- {title}: {body}")

            if lines:
                answer = "\n".join(lines)[:900]
                source = results[0].get("href", "DuckDuckGo")
                return {
                    "success": True,
                    "answer": answer,
                    "source": source,
                    "query": query
                }

            return None
        except Exception as e:
            log.debug(f"duckduckgo-search lib falhou: {e}")
            # Tenta recriar a instancia
            try:
                from ddgs import DDGS
                self._ddgs = DDGS()
            except:
                try:
                    from duckduckgo_search import DDGS
                    self._ddgs = DDGS()
                except:
                    self._ddgs = False
            return None

    # =====================================================================
    # FONTE 2: DuckDuckGo Instant Answer API
    # =====================================================================
    def _search_ddg_api(self, query: str) -> Optional[Dict]:
        """Busca usando API instant answer do DuckDuckGo."""
        try:
            url = f"https://api.duckduckgo.com/?q={requests.utils.quote(query)}&format=json&no_html=1&skip_disambig=1"
            resp = self.session.get(url, timeout=8)
            data = resp.json()

            # Abstract (resposta direta)
            if data.get("AbstractText"):
                return {
                    "success": True,
                    "answer": data["AbstractText"][:800],
                    "source": data.get("AbstractURL", "DuckDuckGo"),
                    "query": query
                }

            # Answer (calculo, conversao, etc)
            if data.get("Answer"):
                return {
                    "success": True,
                    "answer": str(data["Answer"])[:800],
                    "source": "DuckDuckGo",
                    "query": query
                }

            # Infobox
            infobox = data.get("Infobox", {})
            if infobox and infobox.get("content"):
                parts = []
                for item in infobox["content"][:10]:
                    label = item.get("label", "")
                    value = item.get("value", "")
                    if label and value:
                        parts.append(f"{label}: {value}")
                if parts:
                    return {
                        "success": True,
                        "answer": "\n".join(parts)[:800],
                        "source": "DuckDuckGo",
                        "query": query
                    }

            # Related topics
            topics = data.get("RelatedTopics", [])
            if topics:
                texts = []
                for t in topics[:5]:
                    if isinstance(t, dict) and t.get("Text"):
                        texts.append(f"- {t['Text']}")
                if texts:
                    return {
                        "success": True,
                        "answer": "\n".join(texts)[:800],
                        "source": "DuckDuckGo",
                        "query": query
                    }

            return None
        except Exception as e:
            log.debug(f"DDG API falhou: {e}")
            return None

    # =====================================================================
    # FONTE 3: DuckDuckGo HTML scraping
    # =====================================================================
    def _search_duckduckgo_html(self, query: str) -> Optional[Dict]:
        """Busca no DuckDuckGo HTML (scraping direto)."""
        try:
            from bs4 import BeautifulSoup
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            # Extrai resultados
            results = []
            for item in soup.select(".result"):
                title_el = item.select_one(".result__title a, .result__a")
                snippet_el = item.select_one(".result__snippet")

                if title_el and snippet_el:
                    title = title_el.get_text(strip=True)
                    snippet = snippet_el.get_text(strip=True)
                    if snippet and len(snippet) > 20:
                        results.append({"title": title, "snippet": snippet})
                        if len(results) >= 5:
                            break

            if results:
                # Usa snippets como resposta (NAO faz scraping de paginas individuais - muito lento)
                snippets = "\n".join(
                    f"- {r['title']}: {r['snippet']}" for r in results if r.get("snippet")
                )
                if snippets:
                    return {
                        "success": True,
                        "answer": snippets[:900],
                        "source": "DuckDuckGo",
                        "query": query
                    }

            return None
        except Exception as e:
            log.debug(f"DDG HTML falhou: {e}")
            return None

    # =====================================================================
    # FONTE 4: Google scraping
    # =====================================================================
    def _search_google(self, query: str, max_results: int = 5) -> Optional[Dict]:
        """Busca no Google (scraping)."""
        try:
            from bs4 import BeautifulSoup
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=pt-BR&num={max_results + 2}"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            # Featured snippet
            direct = self._extract_featured_snippet(soup)
            if direct:
                return {"success": True, "answer": direct, "source": "Google", "query": query}

            # Knowledge panel
            knowledge = self._extract_knowledge_panel(soup)
            if knowledge:
                return {"success": True, "answer": knowledge, "source": "Google", "query": query}

            # Resultados organicos (so snippets, sem scraping de paginas)
            results = []
            for item in soup.select("div.g, div.tF2Cxc"):
                title_el = item.select_one("h3")
                snippet_el = item.select_one("div.VwiC3b, span.aCOpRe, div.IsZvec")
                if title_el:
                    title = title_el.get_text(strip=True)
                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                    if snippet and len(snippet) > 20:
                        results.append({"title": title, "snippet": snippet})
                        if len(results) >= max_results:
                            break

            if results:
                snippets = "\n".join(
                    f"- {r['title']}: {r['snippet']}" for r in results
                )
                if snippets:
                    return {"success": True, "answer": snippets[:900], "source": "Google", "query": query}

            return None
        except Exception as e:
            log.debug(f"Google falhou: {e}")
            return None

    def _extract_featured_snippet(self, soup) -> Optional[str]:
        """Extrai featured snippet."""
        selectors = ["div.IZ6rdc", "div.hgKElc", "div.kno-rdesc", "div.LGOjhe",
                     "span.hgKElc", "div.V3FYCf", "div.wDYxhc"]
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                text = el.get_text(strip=True)
                if len(text) > 20:
                    return text[:800]
        return None

    def _extract_knowledge_panel(self, soup) -> Optional[str]:
        """Extrai knowledge panel."""
        parts = []
        title = soup.select_one("div.kno-ecr-pt span")
        if title:
            parts.append(title.get_text(strip=True))
        desc = soup.select_one("div.kno-rdesc span")
        if desc:
            parts.append(desc.get_text(strip=True))
        for row in soup.select("div.rVusze"):
            label = row.select_one("span.w8qArf")
            value = row.select_one("span.LrzXr")
            if label and value:
                parts.append(f"{label.get_text(strip=True)} {value.get_text(strip=True)}")
        return "\n".join(parts)[:800] if parts else None

    # =====================================================================
    # FONTE 5: Wikipedia API (ultimo recurso)
    # =====================================================================
    def _search_wikipedia(self, query: str) -> Optional[Dict]:
        """Busca na Wikipedia como ultimo recurso."""
        try:
            # Primeiro busca em PT-BR
            search_url = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(query)}&format=json&srlimit=3"
            resp = self.session.get(search_url, timeout=8)
            data = resp.json()

            results = data.get("query", {}).get("search", [])
            if not results:
                # Tenta em ingles
                search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(query)}&format=json&srlimit=3"
                resp = self.session.get(search_url, timeout=8)
                data = resp.json()
                results = data.get("query", {}).get("search", [])
                wiki_lang = "en"
            else:
                wiki_lang = "pt"

            if not results:
                return None

            # Pega o resumo do primeiro resultado
            title = results[0]["title"]
            summary_url = f"https://{wiki_lang}.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}"
            resp = self.session.get(summary_url, timeout=8)
            summary_data = resp.json()

            extract = summary_data.get("extract", "")
            if extract and len(extract) > 30:
                return {
                    "success": True,
                    "answer": extract[:800],
                    "source": f"Wikipedia ({wiki_lang})",
                    "query": query
                }

            # Se nao tem resumo, usa snippet da busca
            snippets = []
            for r in results[:3]:
                snippet = re.sub(r'<[^>]+>', '', r.get("snippet", ""))
                if snippet:
                    snippets.append(f"- {r['title']}: {snippet}")
            if snippets:
                return {
                    "success": True,
                    "answer": "\n".join(snippets)[:800],
                    "source": f"Wikipedia ({wiki_lang})",
                    "query": query
                }

            return None
        except Exception as e:
            log.debug(f"Wikipedia falhou: {e}")
            return None

    # =====================================================================
    # BUSCA DE NOTICIAS
    # =====================================================================
    def search_news(self, query: str, max_results: int = 5) -> Dict:
        """Busca especifica de noticias."""
        ddgs = self._get_ddgs()
        if ddgs:
            try:
                results = list(ddgs.news(query, region="br-pt", max_results=max_results))
                if results:
                    lines = []
                    for r in results:
                        title = r.get("title", "")
                        body = r.get("body", "")
                        source = r.get("source", "")
                        date = r.get("date", "")
                        if title:
                            line = f"- [{source}] {title}"
                            if body:
                                line += f": {body[:150]}"
                            lines.append(line)
                    if lines:
                        return {
                            "success": True,
                            "answer": "\n".join(lines)[:900],
                            "source": "DuckDuckGo News",
                            "query": query
                        }
            except Exception as e:
                log.debug(f"DDG News falhou: {e}")

        # Fallback: busca normal com "noticias" na query
        return self.search(f"{query} noticias hoje", max_results)

    # =====================================================================
    # BUSCA RAPIDA
    # =====================================================================
    def quick_answer(self, question: str) -> str:
        """Busca rapida - retorna so a resposta como string."""
        result = self.search(question)
        if result["success"]:
            return f"{result['answer']}\n\n[Fonte: {result.get('source', '')}]"
        return result["answer"]


_engine = None

def get_web_search() -> WebSearchEngine:
    global _engine
    if _engine is None:
        _engine = WebSearchEngine()
    return _engine
