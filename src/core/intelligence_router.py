"""
Intelligence Router - Escolhe qual IA usar baseado no tipo de tarefa.
William v6: Cerebro Distribuido com Groq (cloud) + Ollama (local).
"""

import re
from typing import Tuple, Optional
from src.utils.logger import get_logger

log = get_logger(__name__)


class IntelligenceRouter:
    """
    Roteador de inteligencia distribuida.

    Em MODO GROQ (padrao): sempre usa Groq.
    Em MODO MESCLADO: escolhe Groq ou Ollama por tipo de pergunta.

    Tipos de tarefa:
    - business  → Groq 70B (estrategia, copy, funil — precisa de contexto rico)
    - code      → Ollama Mistral (codigo, scripts, logica)
    - general   → Ollama Llama (conversa geral, explicacoes)
    - search    → Groq (pesquisa web, noticias — contexto grande)
    - creative  → Groq (copy, criacao de texto profissional)
    - quick     → Ollama Phi3 (classificacao rapida, respostas curtas)
    """

    # Mapa: tipo → (provider, model)
    # Groq modelos: llama-3.3-70b-versatile (padrao)
    # Ollama modelos: gemma3:4b (instalado localmente)
    ROUTING_MAP = {
        "business":  ("groq",   "llama-3.3-70b-versatile"),
        "creative":  ("groq",   "llama-3.3-70b-versatile"),
        "search":    ("groq",   "llama-3.3-70b-versatile"),
        "code":      ("ollama", "gemma3:4b"),
        "general":   ("ollama", "gemma3:4b"),
        "quick":     ("ollama", "gemma3:4b"),
    }

    # Palavras-chave para classificar o tipo de mensagem
    TYPE_KEYWORDS = {
        "business": [
            "estrategia", "estratégia", "modelo de negocio", "oferta", "ticket",
            "funil", "vender", "vendas", "faturar", "receita", "cliente",
            "copy", "script de vendas", "abordagem", "proposta", "nicho",
            "consultoria", "marketing", "lead", "conversao", "conversão",
            "prospectar", "prospeccao", "prospecção",
        ],
        "creative": [
            "crie um texto", "escreva", "redija", "elabore", "componha",
            "gere um post", "caption", "legenda", "email marketing",
            "newsletter", "anuncio", "anúncio", "headline", "titulo",
        ],
        "code": [
            "codigo", "código", "script", "funcao", "função", "programa",
            "algoritmo", "bug", "erro no codigo", "debug", "python",
            "javascript", "html", "css", "sql", "api", "backend",
            "desenvolva", "programe", "implemente",
        ],
        "search": [
            "pesquise", "pesquisar", "busque", "buscar", "noticias",
            "notícias", "novidades", "manchetes", "o que aconteceu",
            "últimas", "ultimas", "hoje", "agora",
        ],
        "quick": [
            "sim", "nao", "não", "ok", "tudo bem", "obrigado", "certo",
            "entendi", "pode ser", "claro",
        ],
    }

    def __init__(self):
        self._mixed_mode = False  # Estado atual do modo mesclado

    @property
    def mixed_mode(self) -> bool:
        return self._mixed_mode

    @mixed_mode.setter
    def mixed_mode(self, value: bool):
        self._mixed_mode = value
        log.info(f"Modo Mesclado: {'ATIVADO' if value else 'DESATIVADO'}")

    def classify(self, message: str) -> str:
        """Classifica o tipo de mensagem. Retorna tipo como string."""
        msg = message.lower().strip()

        # Verifica cada tipo por palavras-chave
        for tipo, keywords in self.TYPE_KEYWORDS.items():
            if any(kw in msg for kw in keywords):
                return tipo

        # Fallback: geral
        return "general"

    def route(self, message: str, context: list = None) -> Tuple[str, Optional[str]]:
        """
        Decide qual provider e modelo usar.

        Returns:
            (provider_name, model_name_or_None)
            Se model_name=None, usa o modelo padrao do provider.
        """
        # Se modo mesclado desligado: sempre Groq padrao
        if not self._mixed_mode:
            return ("groq", None)

        tipo = self.classify(message)
        provider, model = self.ROUTING_MAP.get(tipo, ("groq", None))

        log.debug(f"Router: '{message[:50]}' → tipo={tipo} → {provider}:{model}")
        return (provider, model)

    def route_with_fallback(self, message: str, available_providers: list) -> Tuple[str, Optional[str]]:
        """
        Decide provider com fallback se o preferido nao estiver disponivel.

        Args:
            message: Mensagem do usuario
            available_providers: Lista de providers ativos (ex: ["groq", "ollama"])

        Returns:
            (provider_name, model_name_or_None)
        """
        preferred_provider, model = self.route(message)

        # Se provider preferido disponivel, usa
        if preferred_provider in available_providers:
            return (preferred_provider, model)

        # Fallback: se Ollama foi preferido mas nao tem, usa Groq
        if preferred_provider == "ollama" and "groq" in available_providers:
            log.debug(f"Ollama indisponivel, fallback para Groq")
            return ("groq", None)

        # Fallback geral: primeiro disponivel
        if available_providers:
            return (available_providers[0], None)

        return ("groq", None)

    def get_status(self) -> dict:
        """Retorna status do roteador para exibicao."""
        return {
            "mixed_mode": self._mixed_mode,
            "routing_map": {k: f"{v[0]}:{v[1]}" for k, v in self.ROUTING_MAP.items()},
        }

    def describe_routing(self, message: str, available_providers: list) -> str:
        """Retorna descricao legivel do roteamento para debug/UI."""
        provider, model = self.route_with_fallback(message, available_providers)
        tipo = self.classify(message)
        mode = "MESCLADO" if self._mixed_mode else "GROQ"
        model_str = f":{model}" if model else ""
        return f"[{mode}] {tipo} → {provider}{model_str}"


# Singleton
_router: Optional[IntelligenceRouter] = None


def get_router() -> IntelligenceRouter:
    """Retorna singleton do roteador."""
    global _router
    if _router is None:
        _router = IntelligenceRouter()
    return _router
