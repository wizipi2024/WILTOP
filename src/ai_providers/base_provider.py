"""
Interface base para provedores de IA.
Define o contrato que todos os provedores devem implementar.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class BaseAIProvider(ABC):
    """
    Classe abstrata base para todos os provedores de IA.

    Todos os provedores (Groq, Claude, OpenAI) devem herdar desta classe
    e implementar os métodos abstratos.
    """

    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Inicializa o provider.

        Args:
            api_key: Chave de API do provider
            model: Nome do modelo a usar
            **kwargs: Argumentos adicionais específicos do provider
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs

    @abstractmethod
    def chat(self, message: str, context: Optional[List[Dict]] = None, **kwargs) -> str:
        """
        Envia mensagem para o modelo e retorna resposta.

        Args:
            message: Mensagem do usuário
            context: Histórico de conversação (opcional)
            **kwargs: Parâmetros adicionais (temperature, max_tokens, etc)

        Returns:
            Resposta do modelo como string

        Raises:
            AIProviderError: Se houver erro na comunicação com a API
        """
        pass

    @abstractmethod
    def chat_stream(self, message: str, context: Optional[List[Dict]] = None, **kwargs):
        """
        Versão streaming do chat (retorna generator).

        Args:
            message: Mensagem do usuário
            context: Histórico de conversação (opcional)
            **kwargs: Parâmetros adicionais

        Yields:
            Chunks da resposta conforme são gerados
        """
        pass

    def is_available(self) -> bool:
        """
        Verifica se o provider está disponível.

        Returns:
            True se o provider pode ser usado
        """
        return bool(self.api_key and self.api_key.strip())

    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo atual.

        Returns:
            Dicionário com informações do modelo
        """
        return {
            "provider": self.__class__.__name__.replace("Provider", "").lower(),
            "model": self.model,
            "available": self.is_available()
        }
