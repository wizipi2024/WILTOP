"""
Formatadores de saída para o Assistente IA William.

Fornece formatação consistente de respostas, dados e mensagens
para diferentes interfaces (GUI, CLI, API).
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path


class ResponseFormatter:
    """Formatador central de respostas."""

    @staticmethod
    def format_success(message: str, data: Optional[Dict] = None) -> Dict:
        """
        Formata resposta de sucesso.

        Args:
            message: Mensagem de sucesso
            data: Dados adicionais (opcional)

        Returns:
            Dicionário formatado
        """
        response = {
            "status": "success",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        if data:
            response["data"] = data

        return response

    @staticmethod
    def format_error(message: str, error_code: Optional[str] = None, details: Optional[Dict] = None) -> Dict:
        """
        Formata resposta de erro.

        Args:
            message: Mensagem de erro
            error_code: Código do erro (opcional)
            details: Detalhes do erro (opcional)

        Returns:
            Dicionário formatado
        """
        response = {
            "status": "error",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        if error_code:
            response["error_code"] = error_code

        if details:
            response["details"] = details

        return response

    @staticmethod
    def format_ai_response(text: str, provider: str, model: str, tokens_used: int = 0) -> Dict:
        """
        Formata resposta da IA.

        Args:
            text: Texto da resposta
            provider: Provider usado
            model: Modelo usado
            tokens_used: Tokens consumidos

        Returns:
            Dicionário formatado
        """
        return {
            "status": "success",
            "response": text,
            "metadata": {
                "provider": provider,
                "model": model,
                "tokens_used": tokens_used,
                "timestamp": datetime.now().isoformat()
            }
        }


class TextFormatter:
    """Formatador de texto para diferentes contextos."""

    @staticmethod
    def format_list(items: List[Any], bullet: str = "•") -> str:
        """
        Formata lista de itens com bullets.

        Args:
            items: Lista de itens
            bullet: Caractere bullet (padrão: •)

        Returns:
            String formatada
        """
        return "\n".join(f"{bullet} {item}" for item in items)

    @staticmethod
    def format_table(data: List[Dict], headers: Optional[List[str]] = None) -> str:
        """
        Formata dados como tabela ASCII.

        Args:
            data: Lista de dicionários
            headers: Cabeçalhos (opcional, usa keys do primeiro dict)

        Returns:
            Tabela formatada
        """
        if not data:
            return "Nenhum dado disponível"

        # Define headers
        if not headers and isinstance(data[0], dict):
            headers = list(data[0].keys())

        # Calcula larguras das colunas
        col_widths = {}
        for header in headers:
            col_widths[header] = max(
                len(str(header)),
                max(len(str(row.get(header, ""))) for row in data)
            )

        # Cria linha separadora
        separator = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+"

        # Monta tabela
        table_lines = [separator]

        # Header
        header_row = "|" + "|".join(f" {h:<{col_widths[h]}} " for h in headers) + "|"
        table_lines.append(header_row)
        table_lines.append(separator)

        # Dados
        for row in data:
            row_line = "|" + "|".join(
                f" {str(row.get(h, '')):<{col_widths[h]}} " for h in headers
            ) + "|"
            table_lines.append(row_line)

        table_lines.append(separator)

        return "\n".join(table_lines)

    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        Trunca texto longo.

        Args:
            text: Texto original
            max_length: Comprimento máximo
            suffix: Sufixo para texto truncado

        Returns:
            Texto truncado
        """
        if len(text) <= max_length:
            return text

        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def highlight_keywords(text: str, keywords: List[str], marker: str = "**") -> str:
        """
        Destaca palavras-chave no texto.

        Args:
            text: Texto original
            keywords: Lista de palavras para destacar
            marker: Marcador de destaque (padrão: ** para markdown bold)

        Returns:
            Texto com keywords destacadas
        """
        result = text
        for keyword in keywords:
            result = result.replace(
                keyword,
                f"{marker}{keyword}{marker}"
            )
        return result

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Formata tamanho de arquivo em formato legível.

        Args:
            size_bytes: Tamanho em bytes

        Returns:
            String formatada (ex: "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f} PB"

    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Formata duração em formato legível.

        Args:
            seconds: Duração em segundos

        Returns:
            String formatada (ex: "2h 30m 15s")
        """
        if seconds < 60:
            return f"{seconds:.1f}s"

        minutes = int(seconds // 60)
        seconds = int(seconds % 60)

        if minutes < 60:
            return f"{minutes}m {seconds}s"

        hours = minutes // 60
        minutes = minutes % 60

        return f"{hours}h {minutes}m {seconds}s"

    @staticmethod
    def format_percentage(value: float, total: float, decimals: int = 1) -> str:
        """
        Formata valor como percentual.

        Args:
            value: Valor atual
            total: Valor total
            decimals: Casas decimais

        Returns:
            String formatada (ex: "75.5%")
        """
        if total == 0:
            return "0%"

        percentage = (value / total) * 100
        return f"{percentage:.{decimals}f}%"


class ConsoleFormatter:
    """Formatador específico para console/terminal."""

    # Códigos de cor ANSI
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m'
    }

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """
        Adiciona cor ao texto (ANSI).

        Args:
            text: Texto original
            color: Nome da cor

        Returns:
            Texto colorido
        """
        color_code = cls.COLORS.get(color.lower(), '')
        reset_code = cls.COLORS['reset']
        return f"{color_code}{text}{reset_code}"

    @classmethod
    def format_header(cls, text: str) -> str:
        """Formata cabeçalho."""
        return cls.colorize(f"\n{'='*60}\n{text.center(60)}\n{'='*60}\n", 'cyan')

    @classmethod
    def format_success_message(cls, text: str) -> str:
        """Formata mensagem de sucesso."""
        return cls.colorize(f"✓ {text}", 'green')

    @classmethod
    def format_error_message(cls, text: str) -> str:
        """Formata mensagem de erro."""
        return cls.colorize(f"✗ {text}", 'red')

    @classmethod
    def format_warning_message(cls, text: str) -> str:
        """Formata mensagem de aviso."""
        return cls.colorize(f"⚠ {text}", 'yellow')

    @classmethod
    def format_info_message(cls, text: str) -> str:
        """Formata mensagem informativa."""
        return cls.colorize(f"ℹ {text}", 'blue')


class MarkdownFormatter:
    """Formatador para Markdown (GUI)."""

    @staticmethod
    def format_code_block(code: str, language: str = "") -> str:
        """
        Formata bloco de código.

        Args:
            code: Código
            language: Linguagem para syntax highlighting

        Returns:
            Markdown formatado
        """
        return f"```{language}\n{code}\n```"

    @staticmethod
    def format_heading(text: str, level: int = 1) -> str:
        """
        Formata cabeçalho.

        Args:
            text: Texto do cabeçalho
            level: Nível (1-6)

        Returns:
            Markdown formatado
        """
        return f"{'#' * level} {text}"

    @staticmethod
    def format_link(text: str, url: str) -> str:
        """
        Formata link.

        Args:
            text: Texto do link
            url: URL

        Returns:
            Markdown formatado
        """
        return f"[{text}]({url})"

    @staticmethod
    def format_bold(text: str) -> str:
        """Formata texto em negrito."""
        return f"**{text}**"

    @staticmethod
    def format_italic(text: str) -> str:
        """Formata texto em itálico."""
        return f"*{text}*"

    @staticmethod
    def format_quote(text: str) -> str:
        """Formata citação."""
        lines = text.split('\n')
        return '\n'.join(f"> {line}" for line in lines)


class JSONFormatter:
    """Formatador JSON para API."""

    @staticmethod
    def pretty_print(data: Any, indent: int = 2) -> str:
        """
        Formata JSON com indentação.

        Args:
            data: Dados a formatar
            indent: Nível de indentação

        Returns:
            JSON formatado
        """
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)

    @staticmethod
    def minify(data: Any) -> str:
        """
        Formata JSON compacto (sem espaços).

        Args:
            data: Dados a formatar

        Returns:
            JSON minificado
        """
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False, default=str)


class DataFormatter:
    """Formatador de estruturas de dados."""

    @staticmethod
    def format_dict_tree(data: Dict, indent: int = 0) -> str:
        """
        Formata dicionário como árvore.

        Args:
            data: Dicionário
            indent: Nível de indentação

        Returns:
            String formatada como árvore
        """
        lines = []
        for key, value in data.items():
            prefix = "  " * indent + "├─ "

            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(DataFormatter.format_dict_tree(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}: [{len(value)} itens]")
            else:
                lines.append(f"{prefix}{key}: {value}")

        return "\n".join(lines)

    @staticmethod
    def format_path_tree(root_path: Path, max_depth: int = 3, current_depth: int = 0) -> str:
        """
        Formata estrutura de diretórios como árvore.

        Args:
            root_path: Caminho raiz
            max_depth: Profundidade máxima
            current_depth: Profundidade atual

        Returns:
            String formatada como árvore
        """
        if current_depth >= max_depth:
            return ""

        lines = []
        prefix = "  " * current_depth + "├─ "

        try:
            for item in sorted(root_path.iterdir()):
                if item.is_dir():
                    lines.append(f"{prefix}{item.name}/")
                    subtree = DataFormatter.format_path_tree(item, max_depth, current_depth + 1)
                    if subtree:
                        lines.append(subtree)
                else:
                    size = TextFormatter.format_file_size(item.stat().st_size)
                    lines.append(f"{prefix}{item.name} ({size})")
        except PermissionError:
            lines.append(f"{prefix}[Acesso negado]")

        return "\n".join(lines)


# ===== FUNÇÕES DE CONVENIÊNCIA =====

def format_success(message: str, **kwargs) -> Dict:
    """Atalho para ResponseFormatter.format_success"""
    return ResponseFormatter.format_success(message, kwargs if kwargs else None)


def format_error(message: str, **kwargs) -> Dict:
    """Atalho para ResponseFormatter.format_error"""
    return ResponseFormatter.format_error(message, details=kwargs if kwargs else None)


def colorize(text: str, color: str) -> str:
    """Atalho para ConsoleFormatter.colorize"""
    return ConsoleFormatter.colorize(text, color)
