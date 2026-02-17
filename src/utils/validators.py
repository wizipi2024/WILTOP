"""
Validadores de entrada para o Assistente IA William.

Fornece validação robusta de diferentes tipos de dados
e entradas do usuário.
"""

import re
from pathlib import Path
from typing import Any, List, Optional
from urllib.parse import urlparse
import validators as val

from .exceptions import ValidationError, InvalidInputError


class InputValidator:
    """Validador central para diferentes tipos de entrada."""

    @staticmethod
    def validate_api_key(key: str, provider: str = "generic") -> bool:
        """
        Valida formato de API key.

        Args:
            key: A chave de API
            provider: Provider da chave (groq, anthropic, openai)

        Returns:
            True se válida

        Raises:
            ValidationError: Se key inválida
        """
        if not key or not isinstance(key, str):
            raise ValidationError("API key não pode ser vazia")

        if key.strip() == "" or key.strip().lower() in ["your_key_here", "none", "null"]:
            raise ValidationError(f"API key do {provider} não foi configurada")

        # Validações específicas por provider
        min_length = {
            "groq": 30,
            "anthropic": 30,
            "openai": 40
        }.get(provider.lower(), 20)

        if len(key) < min_length:
            raise ValidationError(f"API key do {provider} parece inválida (muito curta)")

        return True

    @staticmethod
    def validate_url(url: str, require_https: bool = False) -> bool:
        """
        Valida uma URL.

        Args:
            url: URL a ser validada
            require_https: Se True, requer HTTPS

        Returns:
            True se válida

        Raises:
            ValidationError: Se URL inválida
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL não pode ser vazia")

        # Usa biblioteca validators
        if not val.url(url):
            raise ValidationError(f"URL inválida: {url}")

        if require_https:
            parsed = urlparse(url)
            if parsed.scheme != "https":
                raise ValidationError("URL deve usar HTTPS")

        return True

    @staticmethod
    def validate_file_path(path: str, must_exist: bool = False, extensions: Optional[List[str]] = None) -> bool:
        """
        Valida um caminho de arquivo.

        Args:
            path: Caminho do arquivo
            must_exist: Se True, arquivo deve existir
            extensions: Lista de extensões permitidas (ex: ['.txt', '.pdf'])

        Returns:
            True se válido

        Raises:
            ValidationError: Se caminho inválido
        """
        if not path or not isinstance(path, str):
            raise ValidationError("Caminho de arquivo não pode ser vazio")

        file_path = Path(path)

        # Verifica existência se necessário
        if must_exist and not file_path.exists():
            raise ValidationError(f"Arquivo não encontrado: {path}")

        # Verifica extensão se especificado
        if extensions:
            if file_path.suffix.lower() not in [ext.lower() for ext in extensions]:
                raise ValidationError(f"Extensão de arquivo inválida. Esperado: {extensions}")

        # Verifica path traversal
        try:
            file_path.resolve()
        except Exception:
            raise ValidationError(f"Caminho de arquivo inválido: {path}")

        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida endereço de e-mail.

        Args:
            email: Endereço de e-mail

        Returns:
            True se válido

        Raises:
            ValidationError: Se e-mail inválido
        """
        if not email or not isinstance(email, str):
            raise ValidationError("E-mail não pode ser vazio")

        if not val.email(email):
            raise ValidationError(f"E-mail inválido: {email}")

        return True

    @staticmethod
    def validate_port(port: Any) -> bool:
        """
        Valida número de porta.

        Args:
            port: Número da porta (int ou str)

        Returns:
            True se válido

        Raises:
            ValidationError: Se porta inválida
        """
        try:
            port_num = int(port)
        except (ValueError, TypeError):
            raise ValidationError(f"Porta deve ser um número: {port}")

        if not (1 <= port_num <= 65535):
            raise ValidationError(f"Porta deve estar entre 1 e 65535: {port_num}")

        return True

    @staticmethod
    def validate_model_name(model: str, provider: str = "groq") -> bool:
        """
        Valida nome de modelo de IA.

        Args:
            model: Nome do modelo
            provider: Provider do modelo

        Returns:
            True se válido

        Raises:
            ValidationError: Se modelo inválido
        """
        if not model or not isinstance(model, str):
            raise ValidationError("Nome do modelo não pode ser vazio")

        # Modelos conhecidos por provider
        valid_models = {
            "groq": [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "openai": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-4o"
            ]
        }

        provider_lower = provider.lower()
        if provider_lower in valid_models:
            if model not in valid_models[provider_lower]:
                # Apenas aviso, não erro (podem existir modelos novos)
                pass

        return True

    @staticmethod
    def validate_text_length(text: str, min_length: int = 1, max_length: int = 10000) -> bool:
        """
        Valida comprimento de texto.

        Args:
            text: Texto a validar
            min_length: Comprimento mínimo
            max_length: Comprimento máximo

        Returns:
            True se válido

        Raises:
            ValidationError: Se comprimento inválido
        """
        if not isinstance(text, str):
            raise ValidationError("Entrada deve ser texto")

        text_length = len(text.strip())

        if text_length < min_length:
            raise ValidationError(f"Texto muito curto (mínimo: {min_length} caracteres)")

        if text_length > max_length:
            raise ValidationError(f"Texto muito longo (máximo: {max_length} caracteres)")

        return True

    @staticmethod
    def validate_json(data: Any) -> bool:
        """
        Valida se dados são JSON válidos.

        Args:
            data: Dados a validar

        Returns:
            True se válido

        Raises:
            ValidationError: Se JSON inválido
        """
        import json

        if isinstance(data, str):
            try:
                json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"JSON inválido: {str(e)}")
        elif isinstance(data, (dict, list)):
            try:
                json.dumps(data)
            except (TypeError, ValueError) as e:
                raise ValidationError(f"Dados não serializáveis em JSON: {str(e)}")
        else:
            raise ValidationError("Dados devem ser string JSON, dict ou list")

        return True

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitiza nome de arquivo removendo caracteres inválidos.

        Args:
            filename: Nome do arquivo original

        Returns:
            Nome de arquivo sanitizado
        """
        # Remove caracteres inválidos
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

        # Remove espaços no início/fim
        sanitized = sanitized.strip()

        # Limita comprimento
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:250] + ('.' + ext if ext else '')

        return sanitized

    @staticmethod
    def sanitize_path(path: str) -> str:
        """
        Sanitiza caminho de arquivo prevenindo path traversal.

        Args:
            path: Caminho original

        Returns:
            Caminho sanitizado
        """
        # Remove path traversal
        path = path.replace('..', '')

        # Normaliza o caminho
        try:
            normalized = Path(path).resolve()
            return str(normalized)
        except Exception:
            raise ValidationError(f"Caminho inválido: {path}")

    @staticmethod
    def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """
        Valida formato de data.

        Args:
            date_str: String de data
            format: Formato esperado (padrão: YYYY-MM-DD)

        Returns:
            True se válido

        Raises:
            ValidationError: Se formato inválido
        """
        from datetime import datetime

        try:
            datetime.strptime(date_str, format)
        except ValueError as e:
            raise ValidationError(f"Data inválida: {str(e)}")

        return True


# ===== VALIDADORES ESPECÍFICOS DE MÓDULOS =====

class DocumentValidator:
    """Validadores específicos para módulo de documentos."""

    @staticmethod
    def validate_document_format(format: str) -> bool:
        """Valida formato de documento."""
        valid_formats = ['docx', 'xlsx', 'pdf', 'pptx', 'txt', 'csv']
        if format.lower() not in valid_formats:
            raise ValidationError(f"Formato de documento inválido: {format}. Válidos: {valid_formats}")
        return True


class SystemValidator:
    """Validadores específicos para operações de sistema."""

    @staticmethod
    def validate_directory_path(path: str, must_exist: bool = True) -> bool:
        """Valida caminho de diretório."""
        dir_path = Path(path)

        if must_exist and not dir_path.exists():
            raise ValidationError(f"Diretório não encontrado: {path}")

        if must_exist and not dir_path.is_dir():
            raise ValidationError(f"Caminho não é um diretório: {path}")

        return True


class AutomationValidator:
    """Validadores específicos para automação."""

    @staticmethod
    def validate_cron_expression(expression: str) -> bool:
        """Valida expressão cron."""
        # Expressão cron simples: min hour day month weekday
        parts = expression.split()

        if len(parts) != 5:
            raise ValidationError("Expressão cron deve ter 5 partes: min hour day month weekday")

        # Validação básica de ranges
        ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]

        for i, (part, (min_val, max_val)) in enumerate(zip(parts, ranges)):
            if part == '*':
                continue

            try:
                value = int(part)
                if not (min_val <= value <= max_val):
                    raise ValidationError(f"Valor fora do range na posição {i+1}: {value}")
            except ValueError:
                # Pode ser expressão complexa (*/5, 1-5, etc)
                pass

        return True


# ===== FUNÇÃO HELPER =====

def validate_all(*validations) -> bool:
    """
    Executa múltiplas validações e retorna True se todas passarem.

    Args:
        *validations: Tuplas de (função_validadora, *args)

    Returns:
        True se todas validações passarem

    Raises:
        ValidationError: Na primeira validação que falhar

    Example:
        validate_all(
            (InputValidator.validate_url, "https://example.com"),
            (InputValidator.validate_email, "user@example.com")
        )
    """
    for validation in validations:
        func, *args = validation
        func(*args)

    return True
