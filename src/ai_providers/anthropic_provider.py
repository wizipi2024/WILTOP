"""
Provider de IA para Anthropic (Claude).
Integração com a API da Anthropic para modelos Claude.
Item 24 do plano arquitetural - Multi-provider fallback.
"""

from typing import Optional, Dict, List, Any

from .base_provider import BaseAIProvider
from ..utils.exceptions import AIProviderError, RateLimitError, TokenLimitError
from ..utils.logger import get_logger

log = get_logger(__name__)


class AnthropicProvider(BaseAIProvider):
    """Provider para API da Anthropic (Claude)."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        """
        Inicializa provider Anthropic.

        Args:
            api_key: Chave de API da Anthropic
            model: Modelo a usar
            **kwargs: Configuracoes adicionais
        """
        super().__init__(api_key, model, **kwargs)
        self.client = None

        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
            log.info(f"AnthropicProvider inicializado com modelo: {model}")
        except ImportError:
            log.warning("Pacote 'anthropic' nao instalado. Instale com: pip install anthropic")
        except Exception as e:
            log.error(f"Erro ao inicializar Anthropic: {e}")
            raise AIProviderError(f"Falha ao inicializar Anthropic: {str(e)}")

    def is_available(self) -> bool:
        """Verifica se provider esta disponivel."""
        return self.client is not None and bool(self.api_key)

    def chat(self, message: str, context: Optional[List[Dict]] = None, **kwargs) -> str:
        """
        Envia mensagem para Claude e retorna resposta.

        Args:
            message: Mensagem do usuario
            context: Historico de mensagens
            **kwargs: Parametros como temperature, max_tokens

        Returns:
            Resposta do modelo

        Raises:
            AIProviderError: Se houver erro
        """
        if not self.client:
            raise AIProviderError("Anthropic client nao inicializado")

        try:
            # Converte contexto para formato Anthropic
            messages = []
            system_prompt = None

            if context:
                for msg in context:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "system":
                        system_prompt = content
                    else:
                        # Anthropic so aceita "user" e "assistant"
                        if role not in ("user", "assistant"):
                            role = "user"
                        messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": message})

            # Garante alternancia user/assistant (requisito da Anthropic)
            messages = self._ensure_alternating(messages)

            params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 2048),
                "temperature": kwargs.get("temperature", 0.7),
            }

            if system_prompt:
                params["system"] = system_prompt

            log.debug(f"Enviando para Claude: {message[:100]}...")

            response = self.client.messages.create(**params)

            # Extrai texto da resposta
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text

            log.info(f"Resposta Claude ({len(text)} chars)")
            return text

        except Exception as e:
            error_str = str(e).lower()
            if "rate_limit" in error_str:
                raise RateLimitError("Limite de requisicoes Anthropic excedido")
            elif "token" in error_str:
                raise TokenLimitError("Limite de tokens Anthropic excedido")
            else:
                log.error(f"Erro Anthropic: {e}")
                raise AIProviderError(f"Erro ao processar com Claude: {str(e)}")

    def _ensure_alternating(self, messages: List[Dict]) -> List[Dict]:
        """Garante que mensagens alternam entre user e assistant."""
        if not messages:
            return messages

        cleaned = [messages[0]]
        for msg in messages[1:]:
            if msg["role"] == cleaned[-1]["role"]:
                # Combina mensagens do mesmo role
                cleaned[-1]["content"] += "\n" + msg["content"]
            else:
                cleaned.append(msg)

        # Garante que comeca com user
        if cleaned and cleaned[0]["role"] != "user":
            cleaned.insert(0, {"role": "user", "content": "Ola"})

        return cleaned

    def chat_stream(self, message: str, context: Optional[List[Dict]] = None, **kwargs):
        """
        Versao streaming.

        Yields:
            Chunks da resposta
        """
        if not self.client:
            raise AIProviderError("Anthropic client nao inicializado")

        try:
            messages = []
            system_prompt = None

            if context:
                for msg in context:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "system":
                        system_prompt = content
                    else:
                        if role not in ("user", "assistant"):
                            role = "user"
                        messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": message})
            messages = self._ensure_alternating(messages)

            params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 2048),
                "temperature": kwargs.get("temperature", 0.7),
            }

            if system_prompt:
                params["system"] = system_prompt

            with self.client.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            log.error(f"Erro streaming Anthropic: {e}")
            raise AIProviderError(f"Erro no streaming Claude: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informacoes sobre o modelo Claude."""
        info = super().get_model_info()
        info.update({
            "provider": "anthropic",
            "models_available": [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
        })
        return info
