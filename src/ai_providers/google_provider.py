"""Google Gemini Provider - Integração com Google AI API."""

from typing import Optional, Dict, List, Any
from .base_provider import BaseAIProvider
from ..utils.logger import get_logger

log = get_logger(__name__)

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GoogleProvider(BaseAIProvider):
    """Provider para Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", **kwargs):
        """
        Inicializa Google Gemini provider.

        Args:
            api_key: Chave API do Google
            model: Modelo a usar (default: gemini-1.5-pro)
            **kwargs: Configurações adicionais
        """
        super().__init__(api_key, model, **kwargs)

        if not genai:
            raise ImportError("google-generativeai não instalado. Rode: pip install google-generativeai")

        genai.configure(api_key=api_key)
        self.model_obj = genai.GenerativeModel(model)
        log.info(f"GoogleProvider inicializado com modelo: {model}")

    def chat(self, message: str, context: Optional[List[Dict]] = None, **kwargs) -> str:
        """
        Processa mensagem com Gemini.

        Args:
            message: Mensagem do usuário
            context: Histórico de conversação
            **kwargs: Parâmetros adicionais

        Returns:
            Resposta da IA
        """
        try:
            # Construir histórico
            history = []
            if context:
                for msg in context:
                    if msg.get("role") == "user":
                        history.append({"role": "user", "parts": [msg.get("content", "")]})
                    elif msg.get("role") == "assistant":
                        history.append({"role": "model", "parts": [msg.get("content", "")]})

            # Criar chat session
            chat = self.model_obj.start_chat(history=history)

            # Enviar mensagem
            response = chat.send_message(message)
            return response.text

        except Exception as e:
            log.error(f"Erro ao chamar Google Gemini: {e}")
            raise

    def chat_stream(self, message: str, context: Optional[List[Dict]] = None, **kwargs):
        """
        Processa mensagem com streaming.

        Args:
            message: Mensagem do usuário
            context: Histórico de conversação
            **kwargs: Parâmetros adicionais

        Yields:
            Chunks de resposta
        """
        try:
            # Construir histórico
            history = []
            if context:
                for msg in context:
                    if msg.get("role") == "user":
                        history.append({"role": "user", "parts": [msg.get("content", "")]})
                    elif msg.get("role") == "assistant":
                        history.append({"role": "model", "parts": [msg.get("content", "")]})

            # Criar chat session
            chat = self.model_obj.start_chat(history=history)

            # Stream
            response = chat.send_message(message, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            log.error(f"Erro ao chamar Google Gemini (stream): {e}")
            raise
