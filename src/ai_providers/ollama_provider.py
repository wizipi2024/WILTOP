"""
Provider de IA para Ollama (modelos locais).
Integração com servidor Ollama local para inferencia offline.
Item 24 do plano arquitetural - Multi-provider fallback.
"""

import json
from typing import Optional, Dict, List, Any

from .base_provider import BaseAIProvider
from ..utils.exceptions import AIProviderError
from ..utils.logger import get_logger

log = get_logger(__name__)


class OllamaProvider(BaseAIProvider):
    """Provider para Ollama - modelos locais."""

    def __init__(self, api_key: str = "local", model: str = "llama3.1",
                 base_url: str = "http://localhost:11434", **kwargs):
        """
        Inicializa provider Ollama.

        Args:
            api_key: Nao usado (modelos locais), mas mantido por interface
            model: Modelo a usar (padrao: llama3.1)
            base_url: URL do servidor Ollama
            **kwargs: Configuracoes adicionais
        """
        super().__init__(api_key or "local", model, **kwargs)
        self.base_url = base_url.rstrip("/")
        self._available = False

        try:
            import requests
            self._requests = requests
            # Testa conexao
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                self._available = True
                models = [m["name"] for m in resp.json().get("models", [])]
                log.info(f"OllamaProvider conectado. Modelos: {models[:5]}")
            else:
                log.warning(f"Ollama respondeu com status {resp.status_code}")
        except Exception as e:
            log.info(f"Ollama nao disponivel: {e}")
            self._available = False

    def is_available(self) -> bool:
        """Verifica se Ollama esta rodando."""
        return self._available

    def chat(self, message: str, context: Optional[List[Dict]] = None, **kwargs) -> str:
        """
        Envia mensagem para Ollama e retorna resposta.

        Args:
            message: Mensagem do usuario
            context: Historico de mensagens
            **kwargs: Parametros como temperature, max_tokens

        Returns:
            Resposta do modelo

        Raises:
            AIProviderError: Se houver erro
        """
        if not self._available:
            raise AIProviderError("Ollama nao esta disponivel")

        try:
            # Prepara mensagens no formato Ollama
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": message})

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 2048),
                },
            }

            log.debug(f"Enviando para Ollama: {message[:100]}...")

            resp = self._requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=kwargs.get("timeout", 60),
            )

            if resp.status_code != 200:
                raise AIProviderError(f"Ollama erro HTTP {resp.status_code}: {resp.text[:200]}")

            data = resp.json()
            response = data.get("message", {}).get("content", "")

            log.info(f"Resposta Ollama ({len(response)} chars)")
            return response

        except AIProviderError:
            raise
        except Exception as e:
            log.error(f"Erro no Ollama: {e}")
            raise AIProviderError(f"Erro ao processar com Ollama: {str(e)}")

    def chat_stream(self, message: str, context: Optional[List[Dict]] = None, **kwargs):
        """
        Versao streaming.

        Yields:
            Chunks da resposta
        """
        if not self._available:
            raise AIProviderError("Ollama nao esta disponivel")

        try:
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": message})

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 2048),
                },
            }

            resp = self._requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=kwargs.get("timeout", 120),
                stream=True,
            )

            for line in resp.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            log.error(f"Erro streaming Ollama: {e}")
            raise AIProviderError(f"Erro no streaming Ollama: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informacoes sobre o modelo Ollama."""
        info = super().get_model_info()
        info.update({
            "provider": "ollama",
            "base_url": self.base_url,
            "local": True,
            "available": self._available,
        })
        return info

    def list_models(self) -> List[str]:
        """Lista modelos disponiveis no Ollama."""
        if not self._available:
            return []
        try:
            resp = self._requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            pass
        return []
