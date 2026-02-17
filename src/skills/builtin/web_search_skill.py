"""
Web Search Skill - Pesquisa na web.
Wraps o WebSearchEngine existente.
"""

import re
from typing import Dict, List
from src.skills.base_skill import BaseSkill, SkillResult


class WebSearchSkill(BaseSkill):
    """Skill de pesquisa na web usando WebSearchEngine."""

    name = "web_search_skill"
    display_name = "Pesquisa Web"
    description = "Busca informacoes na internet usando multiplas fontes"
    version = "1.0.0"
    category = "web"
    icon = "🔍"
    requires_network = True
    max_risk_level = "green"

    _keywords = [
        "pesquise", "pesquisar", "busque", "buscar", "procure", "procurar",
        "o que e", "o que sao", "quem e", "quem foi", "quando",
        "como funciona", "como fazer", "como e", "significado",
        "definicao", "explique", "me explique", "me fale sobre",
        "noticias", "news", "novidades",
    ]

    def can_handle(self, command: str) -> float:
        """Verifica se e um pedido de pesquisa."""
        cmd = command.lower()

        for kw in self._keywords:
            if kw in cmd:
                return 0.7

        # Perguntas genericas
        if cmd.endswith("?"):
            return 0.4

        return 0.0

    def execute(self, command: str, params: Dict = None, context: Dict = None) -> SkillResult:
        """Executa pesquisa na web."""
        try:
            from src.core.web_search import get_web_search

            ws = get_web_search()

            # Extrai query
            query = self._extract_query(command)
            if not query:
                query = command

            # Decide tipo de busca
            if any(w in command.lower() for w in ["noticias", "news", "novidades"]):
                result = ws.search_news(query)
            else:
                result = ws.search(query)

            if result.get("success"):
                return SkillResult(
                    success=True,
                    message=result.get("answer", ""),
                    data={
                        "query": query,
                        "sources": result.get("sources", []),
                        "source_count": result.get("source_count", 0),
                    },
                    actions_taken=["web_search"],
                    proof=f"Busca: {query} ({result.get('source_count', 0)} fontes)",
                )
            else:
                return SkillResult(
                    success=False,
                    message=result.get("answer", "Nao encontrei resultados."),
                )

        except Exception as e:
            return SkillResult(success=False, message=f"Erro na pesquisa: {str(e)}")

    def _extract_query(self, command: str) -> str:
        """Extrai query de busca do comando."""
        cmd = command.lower()

        # Remove prefixos comuns
        prefixes = [
            "pesquise sobre", "pesquise", "pesquisar",
            "busque sobre", "busque", "buscar",
            "procure sobre", "procure", "procurar",
            "o que e", "o que sao", "quem e", "quem foi",
            "como funciona", "como fazer",
            "me explique", "me fale sobre", "explique",
            "significado de", "definicao de",
        ]

        for prefix in prefixes:
            if cmd.startswith(prefix):
                return cmd[len(prefix):].strip()

        return command.strip()

    def get_commands(self) -> List[str]:
        return [
            "pesquise sobre inteligencia artificial",
            "o que e machine learning",
            "noticias do brasil",
            "como funciona blockchain",
        ]
