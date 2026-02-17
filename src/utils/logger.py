"""
Sistema de logging para o Assistente IA William.

Usa Loguru para logging avançado com rotação automática,
formatação colorida e níveis configuráveis.
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


class WilliamLogger:
    """
    Gerenciador de logs do sistema William.

    Fornece logging estruturado com suporte a:
    - Múltiplos níveis (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Rotação automática de arquivos
    - Formatação colorida no console
    - Logs separados por módulo
    """

    def __init__(
        self,
        log_file: Optional[str] = None,
        log_level: str = "INFO",
        rotation: str = "10 MB",
        retention: str = "1 week"
    ):
        """
        Inicializa o sistema de logging.

        Args:
            log_file: Caminho do arquivo de log (se None, usa apenas console)
            log_level: Nível mínimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            rotation: Quando rotacionar o arquivo ("10 MB", "1 day", etc)
            retention: Quanto tempo manter arquivos antigos
        """
        self.log_file = log_file
        self.log_level = log_level.upper()
        self.rotation = rotation
        self.retention = retention

        # Remove configuração padrão do loguru
        logger.remove()

        # Configura log no console
        self._setup_console_logging()

        # Configura log em arquivo se especificado
        if self.log_file:
            self._setup_file_logging()

    def _setup_console_logging(self):
        """Configura logging colorido no console."""
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level=self.log_level,
            colorize=True
        )

    def _setup_file_logging(self):
        """Configura logging em arquivo com rotação."""
        # Garante que o diretório existe
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            self.log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=self.log_level,
            rotation=self.rotation,
            retention=self.retention,
            compression="zip",  # Comprime logs antigos
            backtrace=True,  # Inclui traceback completo
            diagnose=True  # Informações de diagnóstico
        )

    @staticmethod
    def get_logger(name: str = "william"):
        """
        Retorna um logger para uso em módulos.

        Args:
            name: Nome do módulo/componente

        Returns:
            Logger configurado
        """
        return logger.bind(name=name)


# ===== FUNÇÕES DE CONVENIÊNCIA =====

def setup_logging(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "1 week"
) -> WilliamLogger:
    """
    Configura o sistema de logging global.

    Args:
        log_file: Caminho do arquivo de log
        log_level: Nível de log
        rotation: Política de rotação
        retention: Política de retenção

    Returns:
        Instância do WilliamLogger
    """
    return WilliamLogger(
        log_file=log_file,
        log_level=log_level,
        rotation=rotation,
        retention=retention
    )


def get_logger(module_name: str = "william"):
    """
    Obtém um logger para um módulo específico.

    Args:
        module_name: Nome do módulo

    Returns:
        Logger configurado

    Example:
        >>> log = get_logger("ai_engine")
        >>> log.info("Motor IA iniciado")
        >>> log.error("Erro ao processar requisição")
    """
    return logger.bind(module=module_name)


# ===== DECORADORES DE LOGGING =====

def log_function_call(func):
    """
    Decorador que registra chamadas de função.

    Args:
        func: Função a ser decorada

    Example:
        @log_function_call
        def process_data(data):
            # código da função
            pass
    """
    def wrapper(*args, **kwargs):
        log = get_logger(func.__module__)
        log.debug(f"Chamando {func.__name__} com args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            log.debug(f"{func.__name__} executado com sucesso")
            return result
        except Exception as e:
            log.error(f"Erro em {func.__name__}: {str(e)}")
            raise
    return wrapper


def log_execution_time(func):
    """
    Decorador que registra o tempo de execução de uma função.

    Args:
        func: Função a ser decorada

    Example:
        @log_execution_time
        def heavy_computation():
            # código pesado
            pass
    """
    import time

    def wrapper(*args, **kwargs):
        log = get_logger(func.__module__)
        start_time = time.time()
        log.debug(f"Iniciando {func.__name__}")

        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            log.info(f"{func.__name__} executado em {elapsed_time:.2f}s")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            log.error(f"{func.__name__} falhou após {elapsed_time:.2f}s: {str(e)}")
            raise
    return wrapper


# ===== CONTEXTO DE LOG =====

class LogContext:
    """
    Gerenciador de contexto para logging temporário.

    Example:
        with LogContext("ProcessandoDados", data_size=1000):
            # código que será logado
            process_data()
    """

    def __init__(self, operation: str, **context_data):
        """
        Inicializa contexto de log.

        Args:
            operation: Nome da operação
            **context_data: Dados contextuais adicionais
        """
        self.operation = operation
        self.context_data = context_data
        self.log = get_logger()
        self.start_time = None

    def __enter__(self):
        """Entra no contexto de log."""
        import time
        self.start_time = time.time()
        context_str = ", ".join(f"{k}={v}" for k, v in self.context_data.items())
        self.log.info(f"Iniciando: {self.operation} [{context_str}]")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sai do contexto de log."""
        import time
        elapsed = time.time() - self.start_time

        if exc_type is None:
            self.log.info(f"Concluído: {self.operation} em {elapsed:.2f}s")
        else:
            self.log.error(f"Erro em {self.operation} após {elapsed:.2f}s: {exc_val}")

        return False  # Propaga a exceção


# ===== FUNÇÕES DE LOG RÁPIDO =====

def log_info(message: str, **kwargs):
    """Log rápido de informação."""
    logger.info(message, **kwargs)


def log_debug(message: str, **kwargs):
    """Log rápido de debug."""
    logger.debug(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log rápido de aviso."""
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log rápido de erro."""
    logger.error(message, **kwargs)


def log_critical(message: str, **kwargs):
    """Log rápido de erro crítico."""
    logger.critical(message, **kwargs)


# ===== LOGGING DE EVENTOS ESPECÍFICOS =====

def log_ai_request(provider: str, model: str, tokens: int = 0):
    """Registra uma requisição à API de IA."""
    logger.info(f"Requisição IA | Provider: {provider} | Model: {model} | Tokens: {tokens}")


def log_ai_response(provider: str, tokens_used: int, response_time: float):
    """Registra uma resposta da API de IA."""
    logger.info(f"Resposta IA | Provider: {provider} | Tokens: {tokens_used} | Tempo: {response_time:.2f}s")


def log_module_execution(module: str, action: str, status: str = "success"):
    """Registra execução de um módulo."""
    level = "info" if status == "success" else "error"
    getattr(logger, level)(f"Módulo: {module} | Ação: {action} | Status: {status}")


def log_user_interaction(interface: str, user_id: str, action: str):
    """Registra interação do usuário."""
    logger.info(f"Interação | Interface: {interface} | Usuário: {user_id} | Ação: {action}")


# ===== EVENT LOG (Observability v4) =====

def get_event_log():
    """
    Retorna singleton do EventLog (sistema de observability).
    Lazy import para nao criar dependencia circular.
    """
    from src.core.observability import get_event_log as _get_event_log
    return _get_event_log()
