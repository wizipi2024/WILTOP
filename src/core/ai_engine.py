"""
Motor de IA principal do Assistente William.
Gerencia provedores de IA e processa requisições.
v4: Multi-provider com fallback automatico (Item 24).
"""

import time
from typing import Optional, List, Dict, Any
from config.settings import settings
from src.ai_providers.groq_provider import GroqProvider
from src.utils.exceptions import AIProviderError, ConfigurationError
from src.utils.logger import get_logger

log = get_logger(__name__)

# Cooldown de providers com rate limit (segundos)
_RATE_LIMIT_COOLDOWN = 60

# Router importado de forma lazy para evitar circular imports
_router = None

def _get_router():
    global _router
    if _router is None:
        try:
            from src.core.intelligence_router import get_router
            _router = get_router()
            # Sincroniza modo mesclado com settings
            _router.mixed_mode = getattr(settings, 'MIXED_MODE', False)
        except Exception as e:
            log.debug(f"Router nao disponivel: {e}")
    return _router


class AIEngine:
    """
    Motor principal de IA do assistente.

    Gerencia múltiplos provedores e roteia requisições.
    v4: Suporta fallback automatico entre providers.
    """

    def __init__(self):
        """Inicializa o motor de IA."""
        self.providers = {}
        self.default_provider = settings.DEFAULT_AI_PROVIDER
        # Ordem de fallback: Groq primeiro (mais rápido), depois OpenAI/Anthropic (mais inteligentes), Ollama por último
        self.fallback_order = getattr(settings, 'PROVIDER_FALLBACK_ORDER',
                                       ['groq', 'openai', 'anthropic', 'ollama'])
        self._provider_errors: Dict[str, Dict] = {}  # Rastreia erros por provider
        self._rate_limited_until: Dict[str, float] = {}  # Provider → timestamp de liberacao
        self._initialize_providers()

    def _initialize_providers(self):
        """Inicializa provedores de IA disponíveis."""
        log.info("Inicializando provedores de IA...")

        # 1. Groq
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_key_here":
            try:
                self.providers["groq"] = GroqProvider(
                    api_key=settings.GROQ_API_KEY,
                    model=settings.AI_PROVIDERS["groq"]["default_model"]
                )
                log.info("[OK] Groq provider inicializado")
            except Exception as e:
                log.warning(f"[ERRO] Falha ao inicializar Groq: {e}")

        # 2. Ollama (local) - tenta sempre, silencioso se offline
        try:
            from src.ai_providers.ollama_provider import OllamaProvider
            ollama = OllamaProvider(
                model=getattr(settings, 'OLLAMA_MODEL', 'llama3.1:8b'),
                base_url=getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434'),
            )
            if ollama.is_available():
                self.providers["ollama"] = ollama
                # Descobre modelos instalados
                try:
                    models = ollama.list_models()
                    log.info(f"[OK] Ollama disponivel! Modelos: {models[:5]}")
                except Exception:
                    log.info("[OK] Ollama provider inicializado")
            else:
                log.debug("[--] Ollama nao esta rodando (opcional - instale em ollama.com)")
        except Exception as e:
            log.debug(f"[--] Ollama nao disponivel: {e}")

        # 3. OpenAI - OPCIONAL
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_key_here":
            try:
                from src.ai_providers.openai_provider import OpenAIProvider
                openai_prov = OpenAIProvider(
                    api_key=settings.OPENAI_API_KEY,
                    model=settings.AI_PROVIDERS.get("openai", {}).get(
                        "default_model", "gpt-4-turbo-preview"
                    ),
                )
                if openai_prov.is_available():
                    self.providers["openai"] = openai_prov
                    log.info("[OK] OpenAI provider inicializado")
            except Exception as e:
                log.warning(f"[ERRO] Falha ao inicializar OpenAI: {e}")

        # 4. Anthropic (Claude) - OPCIONAL
        if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your_anthropic_key_here":
            try:
                from src.ai_providers.anthropic_provider import AnthropicProvider
                anthropic_prov = AnthropicProvider(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model=settings.AI_PROVIDERS.get("anthropic", {}).get(
                        "default_model", "claude-3-5-sonnet-20241022"
                    ),
                )
                if anthropic_prov.is_available():
                    self.providers["anthropic"] = anthropic_prov
                    log.info("[OK] Anthropic provider inicializado")
            except Exception as e:
                log.warning(f"[ERRO] Falha ao inicializar Anthropic: {e}")

        if not self.providers:
            raise ConfigurationError(
                "Nenhum provider de IA disponível. Configure ao menos uma API key no .env"
            )

        log.info(f"Provedores disponíveis: {list(self.providers.keys())}")

    def _is_rate_limited(self, provider_name: str) -> bool:
        """Verifica se provider esta em cooldown de rate limit."""
        until = self._rate_limited_until.get(provider_name, 0)
        if time.time() < until:
            remaining = int(until - time.time())
            log.debug(f"{provider_name} em cooldown por mais {remaining}s")
            return True
        return False

    def _mark_rate_limited(self, provider_name: str, cooldown: int = _RATE_LIMIT_COOLDOWN):
        """Marca provider como rate limited por cooldown segundos."""
        self._rate_limited_until[provider_name] = time.time() + cooldown
        log.warning(f"Provider {provider_name} rate limited — cooldown {cooldown}s")

    def get_provider(self, provider_name: Optional[str] = None):
        """
        Retorna provider específico ou o padrão.

        Args:
            provider_name: Nome do provider (groq, claude, openai)

        Returns:
            Instância do provider

        Raises:
            AIProviderError: Se provider não estiver disponível
        """
        name = provider_name or self.default_provider

        if name not in self.providers:
            available = list(self.providers.keys())
            raise AIProviderError(
                f"Provider '{name}' não disponível. Disponíveis: {available}"
            )

        return self.providers[name]

    def chat(
        self,
        message: str,
        provider: Optional[str] = None,
        context: Optional[List[Dict]] = None,
        stream: bool = False,
        **kwargs
    ):
        """
        Processa mensagem com IA.

        Args:
            message: Mensagem do usuário
            provider: Provider a usar (opcional, usa padrão)
            context: Histórico de conversação
            stream: Se True, retorna generator para streaming
            **kwargs: Parâmetros adicionais (temperature, max_tokens, etc)

        Returns:
            Resposta da IA (string ou generator se stream=True)

        Raises:
            AIProviderError: Se houver erro no processamento
        """
        try:
            provider_instance = self.get_provider(provider)

            log.info(f"Processando mensagem com {provider or self.default_provider}")

            if stream:
                return provider_instance.chat_stream(message, context, **kwargs)
            else:
                return provider_instance.chat(message, context, **kwargs)

        except Exception as e:
            log.error(f"Erro ao processar mensagem: {e}")
            raise

    def chat_with_fallback(
        self,
        message: str,
        context: Optional[List[Dict]] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """
        Processa mensagem com fallback automatico entre providers.
        Tenta cada provider na ordem de fallback ate um funcionar.

        v4: Item 24 - Multi-provider fallback.

        Args:
            message: Mensagem do usuario
            context: Historico de conversacao
            stream: Se True, retorna generator (nao suportado em fallback)
            **kwargs: Parametros adicionais

        Returns:
            Resposta da IA

        Raises:
            AIProviderError: Se TODOS os providers falharem
        """
        # Constroi ordem de tentativa (com roteamento inteligente se disponivel)
        order = []
        router = _get_router()

        if router and message:
            # Usa roteador para escolher provider ideal
            preferred, preferred_model = router.route_with_fallback(
                message, list(self.providers.keys())
            )
            if preferred in self.providers:
                order.append(preferred)
                # Se tem modelo especifico do Ollama, seta temporariamente
                if preferred == "ollama" and preferred_model:
                    try:
                        self.providers["ollama"].model = preferred_model
                    except Exception:
                        pass

        # Depois o default (se nao ja incluido pelo router)
        if self.default_provider in self.providers and self.default_provider not in order:
            order.append(self.default_provider)

        # Depois os outros na ordem de fallback
        for name in self.fallback_order:
            if name in self.providers and name not in order:
                order.append(name)

        # Qualquer provider restante
        for name in self.providers:
            if name not in order:
                order.append(name)

        errors = []
        for provider_name in order:
            # Pula providers em cooldown de rate limit
            if self._is_rate_limited(provider_name):
                log.info(f"Pulando {provider_name} (rate limited), tentando proximo...")
                errors.append(f"{provider_name}: rate limited (em cooldown)")
                continue

            try:
                provider_instance = self.providers[provider_name]
                log.info(f"Tentando provider: {provider_name}")

                start = time.time()
                if stream:
                    response = provider_instance.chat_stream(message, context, **kwargs)
                else:
                    response = provider_instance.chat(message, context, **kwargs)
                elapsed = time.time() - start

                # Sucesso - limpa erros e cooldown
                self._provider_errors.pop(provider_name, None)
                self._rate_limited_until.pop(provider_name, None)
                log.info(f"Provider {provider_name} respondeu em {elapsed:.2f}s")

                # Log no observability
                try:
                    from src.core.observability import get_event_log
                    get_event_log().log_event(
                        "provider_success",
                        agent="ai_engine",
                        data={
                            "provider": provider_name,
                            "elapsed": round(elapsed, 2),
                            "fallback": provider_name != order[0],
                        }
                    )
                except Exception:
                    pass

                return response

            except Exception as e:
                elapsed = time.time() - start if 'start' in locals() else 0
                error_str = str(e).lower()
                error_msg = f"{provider_name}: {str(e)[:200]}"
                errors.append(error_msg)
                log.warning(f"Provider {provider_name} falhou: {e}")

                # Detecta 429 / rate limit — coloca em cooldown
                is_rate_limit = any(x in error_str for x in [
                    "429", "rate_limit", "rate limit", "too many requests",
                    "quota", "ratelimit", "tokens per minute", "requests per minute"
                ])
                if is_rate_limit:
                    self._mark_rate_limited(provider_name, cooldown=_RATE_LIMIT_COOLDOWN)
                    log.warning(f"429 detectado em {provider_name} — rotacionando para proximo provider")

                # Registra erro
                self._provider_errors[provider_name] = {
                    "error": str(e)[:200],
                    "timestamp": time.time(),
                    "rate_limited": is_rate_limit,
                }

                # Log no observability
                try:
                    from src.core.observability import get_event_log
                    get_event_log().log_event(
                        "provider_failed",
                        agent="ai_engine",
                        data={
                            "provider": provider_name,
                            "error": str(e)[:200],
                            "rate_limited": is_rate_limit,
                        },
                        risk_level="yellow",
                    )
                except Exception:
                    pass

                continue

        # Todos falharam
        all_errors = "; ".join(errors)
        raise AIProviderError(
            f"Todos os providers falharam: {all_errors}"
        )

    def get_available_providers(self) -> List[str]:
        """Retorna lista de providers disponiveis."""
        return list(self.providers.keys())

    def get_provider_health(self) -> Dict[str, Dict]:
        """Retorna saude de cada provider."""
        health = {}
        for name, provider in self.providers.items():
            error_info = self._provider_errors.get(name)
            rl_until = self._rate_limited_until.get(name, 0)
            is_rl = time.time() < rl_until
            health[name] = {
                "available": provider.is_available() and not is_rl,
                "model": provider.model,
                "last_error": error_info.get("error") if error_info else None,
                "error_time": error_info.get("timestamp") if error_info else None,
                "is_default": name == self.default_provider,
                "rate_limited": is_rl,
                "rate_limit_remaining": max(0, int(rl_until - time.time())) if is_rl else 0,
            }
        return health

    def get_status(self) -> Dict[str, Any]:
        """
        Retorna status do motor de IA.

        Returns:
            Dicionário com informações de status
        """
        return {
            "providers_available": list(self.providers.keys()),
            "default_provider": self.default_provider,
            "total_providers": len(self.providers),
            "fallback_order": self.fallback_order,
            "provider_errors": {
                k: v.get("error", "") for k, v in self._provider_errors.items()
            },
            "status": "operational" if self.providers else "no_providers"
        }


# Instância global do motor
_engine = None


def get_engine() -> AIEngine:
    """
    Retorna instância global do motor de IA.

    Returns:
        Instância do AIEngine
    """
    global _engine
    if _engine is None:
        _engine = AIEngine()
    return _engine
