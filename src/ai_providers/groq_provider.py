"""
Provider de IA para Groq.
Integração com a API do Groq para modelos Llama, Mixtral, Gemma.
"""

from typing import Optional, Dict, List, Any
from groq import Groq
from groq._exceptions import APIError

from .base_provider import BaseAIProvider
from ..utils.exceptions import AIProviderError, RateLimitError, TokenLimitError
from ..utils.logger import get_logger

log = get_logger(__name__)


class GroqProvider(BaseAIProvider):
    """Provider para API do Groq."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", **kwargs):
        """
        Inicializa provider Groq.

        Args:
            api_key: Chave de API do Groq
            model: Modelo a usar (padrão: llama-3.3-70b-versatile)
            **kwargs: Configurações adicionais
        """
        super().__init__(api_key, model, **kwargs)

        try:
            self.client = Groq(api_key=api_key)
            log.info(f"GroqProvider inicializado com modelo: {model}")
        except Exception as e:
            log.error(f"Erro ao inicializar Groq: {e}")
            raise AIProviderError(f"Falha ao inicializar Groq: {str(e)}")

    def chat(self, message: str, context: Optional[List[Dict]] = None, **kwargs) -> str:
        """
        Envia mensagem para o Groq e retorna resposta.

        Args:
            message: Mensagem do usuário
            context: Histórico de mensagens anteriores
            **kwargs: Parâmetros como temperature, max_tokens

        Returns:
            Resposta do modelo

        Raises:
            AIProviderError: Se houver erro na API
        """
        try:
            # Prepara mensagens
            messages = []

            # Adiciona contexto se fornecido
            if context:
                messages.extend(context)

            # Adiciona mensagem atual
            messages.append({
                "role": "user",
                "content": message
            })

            # Parâmetros da requisição
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
            }

            log.debug(f"Enviando mensagem para Groq: {message[:100]}...")

            # Faz requisição
            completion = self.client.chat.completions.create(**params)

            # Extrai resposta
            response = completion.choices[0].message.content

            log.info(f"Resposta recebida do Groq ({len(response)} chars)")

            return response

        except APIError as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError("Limite de requisições excedido")
            elif "token" in str(e).lower():
                raise TokenLimitError("Limite de tokens excedido")
            else:
                raise AIProviderError(f"Erro na API Groq: {str(e)}")

        except Exception as e:
            log.error(f"Erro inesperado no Groq: {e}")
            raise AIProviderError(f"Erro ao processar com Groq: {str(e)}")

    def chat_stream(self, message: str, context: Optional[List[Dict]] = None, **kwargs):
        """
        Versão streaming da conversação.

        Args:
            message: Mensagem do usuário
            context: Histórico
            **kwargs: Parâmetros adicionais

        Yields:
            Chunks da resposta
        """
        try:
            messages = []

            if context:
                messages.extend(context)

            messages.append({
                "role": "user",
                "content": message
            })

            params = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
                "stream": True
            }

            log.debug("Iniciando streaming do Groq")

            stream = self.client.chat.completions.create(**params)

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            log.error(f"Erro no streaming do Groq: {e}")
            raise AIProviderError(f"Erro no streaming: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo Groq."""
        info = super().get_model_info()
        info.update({
            "provider": "groq",
            "models_available": [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ]
        })
        return info
