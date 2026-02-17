"""
Provider de IA para OpenAI.
Integração com a API da OpenAI para modelos GPT.
Item 24 do plano arquitetural - Multi-provider fallback.
"""

from typing import Optional, Dict, List, Any

from .base_provider import BaseAIProvider
from ..utils.exceptions import AIProviderError, RateLimitError, TokenLimitError
from ..utils.logger import get_logger

log = get_logger(__name__)


class OpenAIProvider(BaseAIProvider):
    """Provider para API da OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", **kwargs):
        """
        Inicializa provider OpenAI.

        Args:
            api_key: Chave de API da OpenAI
            model: Modelo a usar
            **kwargs: Configuracoes adicionais
        """
        super().__init__(api_key, model, **kwargs)
        self.client = None

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            log.info(f"OpenAIProvider inicializado com modelo: {model}")
        except ImportError:
            log.warning("Pacote 'openai' nao instalado. Instale com: pip install openai")
        except Exception as e:
            log.error(f"Erro ao inicializar OpenAI: {e}")
            raise AIProviderError(f"Falha ao inicializar OpenAI: {str(e)}")

    def is_available(self) -> bool:
        """Verifica se provider esta disponivel."""
        return self.client is not None and bool(self.api_key)

    def chat(self, message: str, context: Optional[List[Dict]] = None, **kwargs) -> str:
        """
        Envia mensagem para OpenAI e retorna resposta.

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
            raise AIProviderError("OpenAI client nao inicializado")

        try:
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": message})

            params = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
            }

            log.debug(f"Enviando para OpenAI: {message[:100]}...")

            completion = self.client.chat.completions.create(**params)
            response = completion.choices[0].message.content

            log.info(f"Resposta OpenAI ({len(response)} chars)")
            return response

        except Exception as e:
            error_str = str(e).lower()
            if "rate_limit" in error_str:
                raise RateLimitError("Limite de requisicoes OpenAI excedido")
            elif "token" in error_str and "limit" in error_str:
                raise TokenLimitError("Limite de tokens OpenAI excedido")
            else:
                log.error(f"Erro OpenAI: {e}")
                raise AIProviderError(f"Erro ao processar com OpenAI: {str(e)}")

    def chat_stream(self, message: str, context: Optional[List[Dict]] = None, **kwargs):
        """
        Versao streaming.

        Yields:
            Chunks da resposta
        """
        if not self.client:
            raise AIProviderError("OpenAI client nao inicializado")

        try:
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": message})

            params = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
                "stream": True,
            }

            stream = self.client.chat.completions.create(**params)

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            log.error(f"Erro streaming OpenAI: {e}")
            raise AIProviderError(f"Erro no streaming OpenAI: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informacoes sobre o modelo OpenAI."""
        info = super().get_model_info()
        info.update({
            "provider": "openai",
            "models_available": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-4o",
            ],
        })
        return info
