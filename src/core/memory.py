"""
Sistema de memoria AVANCADA do William.
Auto-aprendizado profundo com evolucao de personalidade.
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter
from src.utils.logger import get_logger

log = get_logger(__name__)

MEMORY_FILE = Path(__file__).parent.parent.parent / "data" / "memory" / "william_memory.json"


class WilliamMemory:
    """Memoria persistente avancada - aprende, evolui e cria personalidade."""

    def __init__(self):
        self.data = {
            "user_preferences": {},
            "learned_commands": {},
            "interaction_count": 0,
            "personality": {
                "nome": "William",
                "humor": "amigavel",
                "estilo": "direto e eficiente",
                "nivel": 1,
                "xp": 0,
                "titulo": "Assistente Novato",
                "criado_em": datetime.now().isoformat(),
                "tracos": ["eficiente", "objetivo", "prestativo"],
            },
            "user_info": {},
            "frequent_actions": {},
            "corrections": [],
            "conversation_patterns": {},
            "topics_discussed": {},
            "time_stats": {
                "horarios_ativos": {},
                "dias_ativos": {},
            },
            "command_aliases": {},
            "success_rate": {"total": 0, "success": 0},
            "vocabulary": {},
        }
        self._load()

    def _load(self):
        """Carrega memoria do disco."""
        try:
            MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            if MEMORY_FILE.exists():
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # Merge profundo - preserva campos novos
                    self._deep_merge(self.data, saved)
                log.info(f"Memoria carregada: {self.data['interaction_count']} interacoes")
        except Exception as e:
            log.error(f"Erro ao carregar memoria: {e}")

    def _deep_merge(self, base: dict, update: dict):
        """Merge profundo - atualiza sem perder campos novos."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _save(self):
        """Salva memoria no disco."""
        try:
            MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Erro ao salvar memoria: {e}")

    def record_interaction(self, user_msg: str, actions_executed: List[Dict], ai_response: str):
        """Registra interacao completa com aprendizado profundo."""
        self.data["interaction_count"] += 1

        # 1. Registra acao frequente
        for action in actions_executed:
            atype = action.get("type", "unknown")
            self.data["frequent_actions"][atype] = self.data["frequent_actions"].get(atype, 0) + 1
            # Registra sucesso/falha
            self.data["success_rate"]["total"] += 1
            if action.get("success"):
                self.data["success_rate"]["success"] += 1

        # 2. Aprende sobre o usuario
        self._learn_about_user(user_msg)

        # 3. Detecta padroes de conversa
        self._analyze_patterns(user_msg)

        # 4. Registra topicos discutidos
        self._track_topics(user_msg)

        # 5. Registra horario de uso
        self._track_time()

        # 6. Aprende vocabulario do usuario
        self._learn_vocabulary(user_msg)

        # 7. Detecta correcoes automaticas
        self._detect_corrections(user_msg)

        # 8. Evolui personalidade (XP + nivel)
        self._evolve_personality(actions_executed)

        # 9. Aprende aliases de comandos
        self._learn_aliases(user_msg, actions_executed)

        # Salva a cada 3 interacoes
        if self.data["interaction_count"] % 3 == 0:
            self._save()

    def _learn_about_user(self, msg: str):
        """Aprende sobre o usuario a partir das mensagens."""
        msg_lower = msg.lower()

        # Detecta nome
        name_patterns = [
            r'(?:meu nome e|me chamo|pode me chamar de|sou o|sou a)\s+([A-Za-z]+)',
            r'(?:me chama de|chama eu de)\s+([A-Za-z]+)',
        ]
        for p in name_patterns:
            m = re.search(p, msg, re.IGNORECASE)
            if m:
                self.data["user_info"]["nome"] = m.group(1).capitalize()
                self._save()

        # Detecta preferencias
        pref_patterns = [
            (r'(?:prefiro|gosto de|adoro|amo)\s+(.+?)(?:\.|,|!|$)', "gosta"),
            (r'(?:odeio|detesto|nao gosto de)\s+(.+?)(?:\.|,|!|$)', "nao_gosta"),
            (r'(?:uso sempre|sempre uso|meu favorito e)\s+(.+?)(?:\.|,|!|$)', "favorito"),
        ]
        for pattern, category in pref_patterns:
            m = re.search(pattern, msg_lower)
            if m:
                self.data["user_preferences"].setdefault(category, [])
                pref = m.group(1).strip()
                if pref not in self.data["user_preferences"][category]:
                    self.data["user_preferences"][category].append(pref)
                    # Limita a 20 por categoria
                    self.data["user_preferences"][category] = self.data["user_preferences"][category][-20:]
                self._save()

        # Detecta profissao
        prof_patterns = [
            r'(?:trabalho com|sou|trabalho de|minha profissao e)\s+(programador|dev|desenvolvedor|designer|estudante|professor|engenheiro|medico|advogado|freelancer|autonomo|empresario)[\s.,!]?',
        ]
        for p in prof_patterns:
            m = re.search(p, msg_lower)
            if m:
                self.data["user_info"]["profissao"] = m.group(1)
                self._save()

        # Detecta idade
        age_match = re.search(r'(?:tenho|to com|estou com)\s+(\d{1,2})\s+anos', msg_lower)
        if age_match:
            self.data["user_info"]["idade"] = int(age_match.group(1))
            self._save()

    def _analyze_patterns(self, msg: str):
        """Analisa padroes de conversa do usuario."""
        msg_lower = msg.lower()
        patterns = self.data["conversation_patterns"]

        # Detecta estilo de comunicacao
        if any(w in msg_lower for w in ["por favor", "poderia", "seria possivel"]):
            patterns["formal"] = patterns.get("formal", 0) + 1
        elif any(w in msg_lower for w in ["faz ai", "manda", "bora", "ae", "po"]):
            patterns["informal"] = patterns.get("informal", 0) + 1

        # Detecta se usuario e tecnico
        if any(w in msg_lower for w in ["python", "script", "codigo", "terminal", "api", "cmd", "git"]):
            patterns["tecnico"] = patterns.get("tecnico", 0) + 1

        # Detecta urgencia
        if any(w in msg_lower for w in ["rapido", "urgente", "agora", "ja", "depressa"]):
            patterns["urgente"] = patterns.get("urgente", 0) + 1

        # Comprimento medio das mensagens
        patterns.setdefault("msg_lengths", [])
        patterns["msg_lengths"].append(len(msg))
        if len(patterns["msg_lengths"]) > 100:
            patterns["msg_lengths"] = patterns["msg_lengths"][-100:]

    def _track_topics(self, msg: str):
        """Registra topicos discutidos."""
        msg_lower = msg.lower()
        topics = self.data["topics_discussed"]

        topic_keywords = {
            "programacao": ["codigo", "python", "javascript", "programar", "script", "bug", "debug"],
            "arquivos": ["arquivo", "pasta", "criar", "deletar", "copiar", "mover"],
            "sistema": ["cpu", "ram", "memoria", "disco", "sistema", "processo"],
            "rede": ["wifi", "ip", "internet", "rede", "conexao"],
            "midia": ["musica", "video", "foto", "imagem", "youtube", "spotify"],
            "produtividade": ["timer", "lembrete", "alarme", "organizar", "limpar"],
            "navegacao": ["site", "google", "pesquise", "busque", "navegador"],
            "diversao": ["jogo", "game", "steam", "jogar", "netflix"],
        }

        for topic, keywords in topic_keywords.items():
            if any(k in msg_lower for k in keywords):
                topics[topic] = topics.get(topic, 0) + 1

    def _track_time(self):
        """Registra padroes de tempo de uso."""
        now = datetime.now()
        hour = str(now.hour)
        day = now.strftime("%A")

        ts = self.data["time_stats"]
        ts["horarios_ativos"][hour] = ts["horarios_ativos"].get(hour, 0) + 1
        ts["dias_ativos"][day] = ts["dias_ativos"].get(day, 0) + 1

    def _learn_vocabulary(self, msg: str):
        """Aprende palavras mais usadas pelo usuario."""
        words = re.findall(r'\b[a-zA-Z\u00C0-\u00FF]{4,}\b', msg.lower())
        stop_words = {"para", "como", "esse", "essa", "este", "esta", "voce", "pode",
                      "quero", "qual", "onde", "quando", "porque", "mais", "muito",
                      "tambem", "fazer", "abra", "abrir", "feche", "fechar", "meu",
                      "minha", "aqui", "isso", "algo", "tudo", "nada", "favor"}
        vocab = self.data["vocabulary"]
        for w in words:
            if w not in stop_words:
                vocab[w] = vocab.get(w, 0) + 1
        # Mantém so top 200
        if len(vocab) > 200:
            top = sorted(vocab.items(), key=lambda x: -x[1])[:200]
            self.data["vocabulary"] = dict(top)

    def _detect_corrections(self, msg: str):
        """Detecta quando o usuario esta corrigindo o William."""
        msg_lower = msg.lower()
        correction_words = ["nao era isso", "errado", "nao quis", "nao foi isso",
                           "ta errado", "esta errado", "fez errado", "nao era",
                           "burro", "idiota", "nao entendeu", "de novo", "outra vez",
                           "tente novamente", "refaca", "corrija"]
        if any(w in msg_lower for w in correction_words):
            self.data["corrections"].append({
                "timestamp": datetime.now().isoformat(),
                "user_msg": msg,
                "issue": f"Usuario insatisfeito: {msg[:100]}"
            })
            if len(self.data["corrections"]) > 50:
                self.data["corrections"] = self.data["corrections"][-50:]
            self._save()

    def _evolve_personality(self, actions: List[Dict]):
        """Evolui personalidade baseado nas interacoes."""
        p = self.data["personality"]

        # Ganha XP por cada acao executada com sucesso
        xp_gain = sum(1 for a in actions if a.get("success"))
        if not actions:
            xp_gain = 1  # Conversa normal tambem ganha XP

        p["xp"] = p.get("xp", 0) + xp_gain

        # Sistema de niveis
        old_level = p.get("nivel", 1)
        new_level = 1 + p["xp"] // 20  # Nivel a cada 20 XP
        p["nivel"] = new_level

        # Titulos por nivel
        titles = {
            1: "Assistente Novato",
            2: "Assistente Aprendiz",
            3: "Assistente Capaz",
            5: "Assistente Experiente",
            8: "Assistente Avancado",
            12: "Assistente Expert",
            18: "Assistente Mestre",
            25: "Assistente Lendario",
            35: "Assistente Supremo",
            50: "William - O Onisciente",
        }
        for lvl in sorted(titles.keys(), reverse=True):
            if new_level >= lvl:
                p["titulo"] = titles[lvl]
                break

        # Evolui tracos baseado nos padroes
        patterns = self.data.get("conversation_patterns", {})
        tracos = set(p.get("tracos", []))

        if patterns.get("informal", 0) > patterns.get("formal", 0):
            tracos.add("descontraido")
        elif patterns.get("formal", 0) > 5:
            tracos.add("profissional")

        if patterns.get("tecnico", 0) > 10:
            tracos.add("tecnico")

        if patterns.get("urgente", 0) > 5:
            tracos.add("rapido")

        if self.data["interaction_count"] > 50:
            tracos.add("veterano")

        if self.data["interaction_count"] > 200:
            tracos.add("confidente")

        p["tracos"] = list(tracos)[:10]

        # Ajusta humor baseado em sucesso
        rate = self.data["success_rate"]
        if rate["total"] > 0:
            success_pct = rate["success"] / rate["total"]
            if success_pct > 0.9:
                p["humor"] = "confiante"
            elif success_pct > 0.7:
                p["humor"] = "amigavel"
            else:
                p["humor"] = "determinado"

    def _learn_aliases(self, msg: str, actions: List[Dict]):
        """Aprende formas alternativas que o usuario usa para comandos."""
        if not actions:
            return
        for action in actions:
            atype = action.get("type", "")
            if atype:
                aliases = self.data["command_aliases"]
                aliases.setdefault(atype, [])
                short_msg = msg[:80].lower()
                if short_msg not in aliases[atype]:
                    aliases[atype].append(short_msg)
                    if len(aliases[atype]) > 15:
                        aliases[atype] = aliases[atype][-15:]

    def record_correction(self, user_msg: str, what_went_wrong: str):
        """Registra quando o usuario corrige o William."""
        self.data["corrections"].append({
            "timestamp": datetime.now().isoformat(),
            "user_msg": user_msg,
            "issue": what_went_wrong
        })
        if len(self.data["corrections"]) > 50:
            self.data["corrections"] = self.data["corrections"][-50:]
        self._save()

    def get_context_prompt(self) -> str:
        """Retorna prompt de contexto baseado na memoria para a IA."""
        parts = []
        p = self.data["personality"]

        # Personalidade
        parts.append(f"[Personalidade: {p.get('titulo', 'William')} | "
                     f"Nivel {p.get('nivel', 1)} | "
                     f"Humor: {p.get('humor', 'amigavel')} | "
                     f"Tracos: {', '.join(p.get('tracos', []))}]")

        # Info do usuario
        user = self.data["user_info"]
        if user.get("nome"):
            info = f"Usuario: {user['nome']}"
            if user.get("profissao"):
                info += f", {user['profissao']}"
            if user.get("idade"):
                info += f", {user['idade']} anos"
            parts.append(info)

        # Preferencias
        prefs = self.data["user_preferences"]
        if prefs.get("gosta"):
            parts.append(f"Gosta de: {', '.join(prefs['gosta'][-5:])}")
        if prefs.get("favorito"):
            parts.append(f"Favoritos: {', '.join(prefs['favorito'][-3:])}")

        # Interacoes
        count = self.data["interaction_count"]
        if count > 0:
            parts.append(f"Interacoes: {count}")

        # Top 3 acoes
        fav = sorted(self.data["frequent_actions"].items(), key=lambda x: -x[1])[:3]
        if fav:
            parts.append(f"Acoes top: {', '.join(f'{k}({v}x)' for k, v in fav)}")

        # Topicos favoritos
        topics = sorted(self.data["topics_discussed"].items(), key=lambda x: -x[1])[:3]
        if topics:
            parts.append(f"Topicos: {', '.join(t[0] for t in topics)}")

        # Correcoes recentes (para evitar)
        corrections = self.data["corrections"][-3:]
        if corrections:
            issues = "; ".join(c["issue"][:60] for c in corrections)
            parts.append(f"[EVITAR: {issues}]")

        # Estilo de comunicacao
        patterns = self.data.get("conversation_patterns", {})
        if patterns.get("informal", 0) > patterns.get("formal", 0) + 3:
            parts.append("[Tom: informal/descontraido]")
        elif patterns.get("formal", 0) > patterns.get("informal", 0) + 3:
            parts.append("[Tom: formal/profissional]")

        return "\n".join(parts) if parts else ""

    def get_stats(self) -> str:
        """Retorna estatisticas detalhadas."""
        count = self.data["interaction_count"]
        p = self.data["personality"]
        user = self.data["user_info"]
        rate = self.data["success_rate"]

        success_pct = (rate["success"] / rate["total"] * 100) if rate["total"] > 0 else 0

        stats = f"""{'='*40}
  WILLIAM - {p.get('titulo', 'Assistente')}
{'='*40}
  Nivel: {p.get('nivel', 1)} | XP: {p.get('xp', 0)}
  Humor: {p.get('humor', 'amigavel')}
  Tracos: {', '.join(p.get('tracos', []))}
{'='*40}
  Usuario: {user.get('nome', 'N/A')}
  Profissao: {user.get('profissao', 'N/A')}
  Interacoes: {count}
  Taxa de sucesso: {success_pct:.0f}%
{'='*40}"""

        # Acoes mais usadas
        fav = sorted(self.data["frequent_actions"].items(), key=lambda x: -x[1])[:8]
        if fav:
            stats += "\n  Acoes mais usadas:"
            for k, v in fav:
                bar = '#' * min(v, 20)
                stats += f"\n    {k}: {bar} ({v}x)"

        # Topicos
        topics = sorted(self.data["topics_discussed"].items(), key=lambda x: -x[1])[:5]
        if topics:
            stats += "\n  Topicos favoritos:"
            for t, v in topics:
                stats += f"\n    {t}: {v}x"

        # Horarios mais ativos
        hours = self.data["time_stats"].get("horarios_ativos", {})
        if hours:
            top_hours = sorted(hours.items(), key=lambda x: -x[1])[:3]
            stats += f"\n  Horarios mais ativos: {', '.join(f'{h}h' for h, _ in top_hours)}"

        stats += f"\n{'='*40}"
        return stats

    def get_level_info(self) -> Dict:
        """Retorna info do nivel atual."""
        p = self.data["personality"]
        nivel = p.get("nivel", 1)
        xp = p.get("xp", 0)
        next_level_xp = nivel * 20
        xp_current = xp % 20

        return {
            "nivel": nivel,
            "titulo": p.get("titulo", "Assistente"),
            "xp": xp,
            "xp_progress": xp_current,
            "xp_needed": 20,
            "progress_pct": (xp_current / 20) * 100,
        }

    def save(self):
        """Salva memoria."""
        self._save()

    # ================================================================
    # === METODOS v4 (Overhaul Arquitetural - Fase 2) ===
    # ================================================================

    def log_interaction_jsonl(self, user_msg: str, actions: List[Dict],
                              ai_response: str = "", metadata: Dict = None):
        """
        Registra interacao em formato JSONL (append-only).
        Complementa o JSON principal - JSONL e mais seguro para append.

        Args:
            user_msg: Mensagem do usuario
            actions: Lista de acoes executadas
            ai_response: Resposta da IA (se houver)
            metadata: Dados extras (agent, task_id, etc)
        """
        try:
            jsonl_file = MEMORY_FILE.parent / "interactions.jsonl"
            jsonl_file.parent.mkdir(parents=True, exist_ok=True)

            entry = {
                "ts": datetime.now().isoformat(),
                "user_msg": user_msg[:500],
                "actions": [
                    {
                        "type": a.get("type", "unknown"),
                        "success": a.get("success", False),
                    }
                    for a in actions[:10]
                ],
                "ai_response": ai_response[:300] if ai_response else "",
                "metadata": metadata or {},
            }

            with open(jsonl_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        except Exception as e:
            log.debug(f"Erro ao gravar JSONL: {e}")

    def search_memory(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Busca nas interacoes passadas por keyword.
        Procura no JSONL de interacoes.

        Args:
            query: Texto de busca
            limit: Maximo de resultados

        Returns:
            Lista de interacoes relevantes (mais recentes primeiro)
        """
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        jsonl_file = MEMORY_FILE.parent / "interactions.jsonl"
        if not jsonl_file.exists():
            return results

        try:
            # Le de tras pra frente (mais recentes primeiro)
            lines = []
            with open(jsonl_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Processa do mais recente ao mais antigo
            for line in reversed(lines):
                if len(results) >= limit:
                    break
                try:
                    entry = json.loads(line.strip())
                    text = f"{entry.get('user_msg', '')} {entry.get('ai_response', '')}".lower()

                    # Match: query inteira ou palavras individuais
                    score = 0
                    if query_lower in text:
                        score = 5
                    else:
                        text_words = set(text.split())
                        common = query_words & text_words
                        score = len(common)

                    if score > 0:
                        entry["_relevance_score"] = score
                        results.append(entry)
                except (json.JSONDecodeError, KeyError):
                    continue

        except Exception as e:
            log.debug(f"Erro ao buscar memoria: {e}")

        # Ordena por relevancia
        results.sort(key=lambda x: x.get("_relevance_score", 0), reverse=True)
        return results[:limit]

    def export_to_markdown(self, output_path: str = None) -> str:
        """
        Exporta memoria completa em formato Markdown.

        Args:
            output_path: Caminho do arquivo (se None, usa MEMORY.md no data/memory/)

        Returns:
            Caminho do arquivo gerado
        """
        if output_path is None:
            output_path = str(MEMORY_FILE.parent / "MEMORY.md")

        try:
            lines = ["# William AI - Memory Export\n"]
            lines.append(f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

            # Personalidade
            p = self.data["personality"]
            lines.append("## Personalidade\n")
            lines.append(f"- **Titulo:** {p.get('titulo', 'William')}")
            lines.append(f"- **Nivel:** {p.get('nivel', 1)} (XP: {p.get('xp', 0)})")
            lines.append(f"- **Humor:** {p.get('humor', 'amigavel')}")
            lines.append(f"- **Tracos:** {', '.join(p.get('tracos', []))}")
            lines.append(f"- **Criado em:** {p.get('criado_em', 'N/A')}\n")

            # Info do usuario
            user = self.data.get("user_info", {})
            if user:
                lines.append("## Usuario\n")
                for k, v in user.items():
                    lines.append(f"- **{k.title()}:** {v}")
                lines.append("")

            # Preferencias
            prefs = self.data.get("user_preferences", {})
            if prefs:
                lines.append("## Preferencias\n")
                for cat, items in prefs.items():
                    if items:
                        lines.append(f"- **{cat.title()}:** {', '.join(items[:10])}")
                lines.append("")

            # Estatisticas
            lines.append("## Estatisticas\n")
            lines.append(f"- **Interacoes:** {self.data.get('interaction_count', 0)}")
            rate = self.data.get("success_rate", {})
            total = rate.get("total", 0)
            success = rate.get("success", 0)
            pct = (success / total * 100) if total > 0 else 0
            lines.append(f"- **Taxa de sucesso:** {pct:.0f}% ({success}/{total})")

            # Acoes frequentes
            fav = sorted(
                self.data.get("frequent_actions", {}).items(),
                key=lambda x: -x[1]
            )[:15]
            if fav:
                lines.append("\n## Acoes Mais Usadas\n")
                lines.append("| Acao | Vezes |")
                lines.append("|------|-------|")
                for k, v in fav:
                    lines.append(f"| {k} | {v} |")

            # Topicos
            topics = sorted(
                self.data.get("topics_discussed", {}).items(),
                key=lambda x: -x[1]
            )[:10]
            if topics:
                lines.append("\n## Topicos Discutidos\n")
                for t, v in topics:
                    lines.append(f"- **{t}:** {v}x")

            # Vocabulario top
            vocab = sorted(
                self.data.get("vocabulary", {}).items(),
                key=lambda x: -x[1]
            )[:20]
            if vocab:
                lines.append("\n## Vocabulario Frequente\n")
                lines.append(", ".join(f"{w}({v})" for w, v in vocab))

            # Correcoes
            corrections = self.data.get("corrections", [])
            if corrections:
                lines.append(f"\n## Correcoes Recentes ({len(corrections)})\n")
                for c in corrections[-5:]:
                    lines.append(f"- [{c.get('timestamp', '?')[:10]}] {c.get('issue', '')[:80]}")

            content = "\n".join(lines)

            # Salva arquivo
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            log.info(f"Memoria exportada para: {output_path}")
            return output_path

        except Exception as e:
            log.error(f"Erro ao exportar memoria: {e}")
            return ""

    def get_interaction_history(self, n: int = 20) -> List[Dict]:
        """Retorna ultimas N interacoes do JSONL."""
        jsonl_file = MEMORY_FILE.parent / "interactions.jsonl"
        if not jsonl_file.exists():
            return []

        try:
            with open(jsonl_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            entries = []
            for line in lines[-n:]:
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            return entries
        except Exception as e:
            log.debug(f"Erro ao ler historico: {e}")
            return []


# Instancia global
_memory = None

def get_memory() -> WilliamMemory:
    global _memory
    if _memory is None:
        _memory = WilliamMemory()
    return _memory
