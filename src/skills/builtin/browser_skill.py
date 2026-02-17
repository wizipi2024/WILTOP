"""
Browser Skill - Automatizacao de navegacao web.
Usa Playwright ou Selenium (se disponivel), senao abre com webbrowser.
Item 7 do plano arquitetural.
"""

import os
import re
import webbrowser
from typing import Dict, List, Optional
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

# Verifica disponibilidade do Playwright
_playwright_available = False
try:
    from playwright.sync_api import sync_playwright
    _playwright_available = True
except ImportError:
    log.debug("Playwright nao instalado - modo basico de browser")

# Verifica disponibilidade do Selenium
_selenium_available = False
try:
    from selenium import webdriver
    _selenium_available = True
except ImportError:
    log.debug("Selenium nao instalado")


class BrowserSkill(BaseSkill):
    """Skill de automacao de navegacao web."""

    name = "browser_skill"
    display_name = "Navegador Web"
    description = "Abre sites, extrai texto, faz screenshot e automatiza navegacao"
    version = "1.0.0"
    category = "web"
    icon = "🌐"
    requires_network = True
    max_risk_level = "yellow"

    _keywords = [
        "abra o site", "abrir site", "abra a pagina",
        "navegue para", "navegar para", "va para",
        "abra o", "abrir o", "acessar",
        "screenshot", "captura de tela", "print da pagina",
        "extraia texto", "extrair texto", "pegue o texto",
        "preencha", "preencher", "fill",
    ]

    _url_pattern = re.compile(
        r'(?:https?://)?(?:www\.)?[\w\-]+\.[\w\-]+(?:\.[\w\-]+)*(?:/[^\s]*)?'
    )

    def can_handle(self, command: str) -> float:
        """Verifica se e operacao de browser."""
        cmd = command.lower()

        # Keywords de navegacao
        for kw in self._keywords:
            if kw in cmd:
                return 0.75

        # URL detectada
        if self._url_pattern.search(command):
            return 0.8

        # Sites conhecidos
        sites = ["google", "youtube", "github", "stackoverflow", "wikipedia",
                 "gmail", "facebook", "twitter", "instagram", "linkedin",
                 "mercadolivre", "olx", "amazon"]
        if any(s in cmd for s in sites):
            if any(w in cmd for w in ["abra", "abrir", "abre", "acessar", "va para"]):
                return 0.85

        return 0.0

    def execute(self, command: str, params: Dict = None, context: Dict = None) -> SkillResult:
        """Executa acao de browser."""
        cmd = command.lower()

        # Detecta URL
        url = self._extract_url(command)

        # Detecta acao
        if "screenshot" in cmd or "captura" in cmd or "print" in cmd:
            return self._take_screenshot(url or "about:blank")
        elif "extraia" in cmd or "texto" in cmd:
            return self._extract_text(url)
        elif "preencha" in cmd or "fill" in cmd:
            return self._fill_form(command, params)
        else:
            # Acao padrao: abrir URL/site
            return self._navigate(command, url)

    def _extract_url(self, command: str) -> Optional[str]:
        """Extrai URL do comando."""
        match = self._url_pattern.search(command)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            return url

        # Sites conhecidos
        site_map = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://www.github.com",
            "gmail": "https://mail.google.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "wikipedia": "https://pt.wikipedia.org",
            "mercadolivre": "https://www.mercadolivre.com.br",
            "mercado livre": "https://www.mercadolivre.com.br",
            "olx": "https://www.olx.com.br",
            "amazon": "https://www.amazon.com.br",
            "stackoverflow": "https://stackoverflow.com",
            "whatsapp": "https://web.whatsapp.com",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com",
        }

        cmd = command.lower()
        for site_name, site_url in site_map.items():
            if site_name in cmd:
                return site_url

        return None

    def _navigate(self, command: str, url: Optional[str] = None) -> SkillResult:
        """Abre URL no navegador."""
        if not url:
            # Tenta buscar no Google
            query = command.lower()
            for prefix in ["abra o", "abrir o", "abra", "abrir", "acessar", "va para",
                          "navegue para", "abre o", "abre"]:
                query = query.replace(prefix, "").strip()

            if query:
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            else:
                return SkillResult(
                    success=False,
                    message="Nao encontrei URL para navegar.",
                )

        try:
            if _playwright_available:
                return self._navigate_playwright(url)
            else:
                # Fallback: abre com webbrowser padrao
                webbrowser.open(url)
                return SkillResult(
                    success=True,
                    message=f"Site aberto no navegador: {url}",
                    data={"url": url, "method": "webbrowser"},
                    actions_taken=["navigate"],
                    proof=f"URL aberta: {url}",
                )

        except Exception as e:
            return SkillResult(success=False, message=f"Erro ao navegar: {str(e)}")

    def _navigate_playwright(self, url: str) -> SkillResult:
        """Navega usando Playwright."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(url, timeout=30000)
                title = page.title()
                # Nao fecha o browser para o usuario usar
                return SkillResult(
                    success=True,
                    message=f"Navegando para: {url}\nTitulo: {title}",
                    data={"url": url, "title": title, "method": "playwright"},
                    actions_taken=["navigate"],
                    proof=f"Pagina carregada: {title}",
                )
        except Exception as e:
            # Fallback para webbrowser
            webbrowser.open(url)
            return SkillResult(
                success=True,
                message=f"Site aberto (fallback): {url}",
                data={"url": url, "method": "webbrowser_fallback"},
                actions_taken=["navigate"],
            )

    def _take_screenshot(self, url: str) -> SkillResult:
        """Tira screenshot de pagina."""
        if not _playwright_available:
            return SkillResult(
                success=False,
                message="Screenshot requer Playwright. Instale com: pip install playwright",
            )

        try:
            from pathlib import Path
            screenshot_dir = Path.home() / "Desktop" / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)

            import time
            filename = f"screenshot_{int(time.time())}.png"
            filepath = str(screenshot_dir / filename)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.screenshot(path=filepath)
                title = page.title()
                browser.close()

            return SkillResult(
                success=True,
                message=f"Screenshot salvo: {filepath}\nPagina: {title}",
                data={"path": filepath, "url": url, "title": title},
                actions_taken=["screenshot"],
                proof=f"Arquivo: {filepath}",
            )

        except Exception as e:
            return SkillResult(success=False, message=f"Erro no screenshot: {str(e)}")

    def _extract_text(self, url: Optional[str]) -> SkillResult:
        """Extrai texto de pagina."""
        if not url:
            return SkillResult(success=False, message="URL necessaria para extrair texto.")

        try:
            import requests
            from bs4 import BeautifulSoup

            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            })
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove scripts e styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            # Limita tamanho
            text = text[:5000]

            return SkillResult(
                success=True,
                message=f"Texto extraido de {url} ({len(text)} chars):\n\n{text[:2000]}",
                data={"url": url, "text_length": len(text), "text": text},
                actions_taken=["extract_text"],
            )

        except Exception as e:
            return SkillResult(success=False, message=f"Erro ao extrair texto: {str(e)}")

    def _fill_form(self, command: str, params: Dict = None) -> SkillResult:
        """Preenche formulario (requer Playwright)."""
        if not _playwright_available:
            return SkillResult(
                success=False,
                message="Preenchimento de formulario requer Playwright.",
            )

        return SkillResult(
            success=False,
            message="Preenchimento de formulario ainda nao implementado. Use a GUI do browser.",
        )

    def get_commands(self) -> List[str]:
        return [
            "abra o google",
            "navegue para github.com",
            "abra o mercado livre",
            "screenshot de google.com",
            "extraia texto de wikipedia.org",
        ]
