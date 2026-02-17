"""
Exceções customizadas para o Assistente IA William.

Este módulo define uma hierarquia de exceções específicas para tratamento
de erros em diferentes componentes do sistema.
"""


class WilliamException(Exception):
    """Exceção base para todas as exceções do assistente William."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message} | Detalhes: {self.details}"
        return self.message


# ===== EXCEÇÕES DE IA E PROVEDORES =====

class AIProviderError(WilliamException):
    """Erro relacionado a provedores de IA (Groq, Claude, OpenAI)."""
    pass


class ModelNotAvailableError(AIProviderError):
    """Modelo de IA solicitado não está disponível."""
    pass


class APIKeyError(AIProviderError):
    """Erro relacionado a chaves de API (ausente, inválida, etc)."""
    pass


class RateLimitError(AIProviderError):
    """Limite de requisições da API foi excedido."""
    pass


class TokenLimitError(AIProviderError):
    """Limite de tokens foi excedido."""
    pass


# ===== EXCEÇÕES DE MEMÓRIA =====

class MemoryError(WilliamException):
    """Erro no sistema de memória."""
    pass


class MemoryStorageError(MemoryError):
    """Erro ao armazenar dados na memória."""
    pass


class MemoryRetrievalError(MemoryError):
    """Erro ao recuperar dados da memória."""
    pass


# ===== EXCEÇÕES DE MÓDULOS =====

class ModuleExecutionError(WilliamException):
    """Erro na execução de um módulo funcional."""
    pass


class DocumentError(ModuleExecutionError):
    """Erro ao manipular documentos (Word, Excel, PDF, PPT)."""
    pass


class SystemOperationError(ModuleExecutionError):
    """Erro em operações de sistema (arquivos, limpeza, backup)."""
    pass


class NetworkError(ModuleExecutionError):
    """Erro relacionado a operações de rede (web scraping, downloads)."""
    pass


class AutomationError(ModuleExecutionError):
    """Erro no sistema de automação (scheduler, triggers, workflows)."""
    pass


class AnalysisError(ModuleExecutionError):
    """Erro na análise de dados."""
    pass


# ===== EXCEÇÕES DE CONFIGURAÇÃO =====

class ConfigurationError(WilliamException):
    """Erro na configuração do sistema."""
    pass


class InvalidConfigError(ConfigurationError):
    """Configuração inválida fornecida."""
    pass


class MissingConfigError(ConfigurationError):
    """Configuração obrigatória está ausente."""
    pass


# ===== EXCEÇÕES DE AUTENTICAÇÃO E SEGURANÇA =====

class AuthenticationError(WilliamException):
    """Erro de autenticação."""
    pass


class PermissionError(WilliamException):
    """Erro de permissão para executar operação."""
    pass


# ===== EXCEÇÕES DE ARQUIVOS =====

class FileOperationError(WilliamException):
    """Erro em operações com arquivos."""
    pass


class FileNotFoundError(FileOperationError):
    """Arquivo não encontrado."""
    pass


class FileFormatError(FileOperationError):
    """Formato de arquivo inválido ou não suportado."""
    pass


# ===== EXCEÇÕES DE VALIDAÇÃO =====

class ValidationError(WilliamException):
    """Erro de validação de dados."""
    pass


class InvalidInputError(ValidationError):
    """Entrada fornecida é inválida."""
    pass


# ===== EXCEÇÕES DE INTERFACE =====

class InterfaceError(WilliamException):
    """Erro relacionado às interfaces (GUI, CLI, API, Bots)."""
    pass


class APIError(InterfaceError):
    """Erro na API REST."""
    pass


class BotError(InterfaceError):
    """Erro em bots (Telegram, WhatsApp)."""
    pass


# ===== EXCEÇÕES DE PARSING =====

class ParsingError(WilliamException):
    """Erro ao fazer parsing de comandos ou dados."""
    pass


class CommandNotFoundError(ParsingError):
    """Comando não reconhecido."""
    pass


class InvalidSyntaxError(ParsingError):
    """Sintaxe inválida no comando."""
    pass


# ===== HELPER FUNCTIONS =====

def handle_exception(exception: Exception, context: str = "") -> str:
    """
    Processa uma exceção e retorna mensagem amigável para o usuário.

    Args:
        exception: A exceção capturada
        context: Contexto adicional sobre onde ocorreu o erro

    Returns:
        Mensagem de erro formatada e amigável
    """
    if isinstance(exception, WilliamException):
        message = f"⚠️ {exception.message}"
        if context:
            message += f"\n📍 Contexto: {context}"
        if exception.details:
            message += f"\n🔍 Detalhes: {exception.details}"
        return message

    # Exceção genérica do Python
    message = f"❌ Erro inesperado: {str(exception)}"
    if context:
        message += f"\n📍 Contexto: {context}"
    return message


def wrap_exception(func):
    """
    Decorador para capturar exceções e convertê-las em WilliamException.

    Usage:
        @wrap_exception
        def my_function():
            # código que pode lançar exceções
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except WilliamException:
            # Exceções do William já estão no formato correto
            raise
        except Exception as e:
            # Converte exceções genéricas em WilliamException
            raise WilliamException(
                f"Erro em {func.__name__}: {str(e)}",
                {"original_exception": type(e).__name__}
            ) from e
    return wrapper
