"""
Security - Politica de risco e sandbox para agentes.
Classifica acoes por nivel de risco e limita escopo de cada agente.
Items 10 e 18 do plano arquitetural.
"""

import os
from typing import List, Optional, Set
from pathlib import Path
from src.utils.logger import get_logger

log = get_logger(__name__)

USER_HOME = str(Path.home())


class RiskPolicy:
    """Classifica acoes por nivel de risco (green/yellow/red)."""

    # Acoes VERDES - somente leitura, sem efeito colateral
    GREEN_ACTIONS: Set[str] = {
        "datetime", "system_info", "battery", "disk", "network",
        "process_list", "list", "read", "web_answer", "search_local",
        "ai_answer", "clipboard_read", "info", "ask_user", "wifi",
    }

    # Acoes AMARELAS - modificam estado mas de forma controlada
    YELLOW_ACTIONS: Set[str] = {
        "open_app", "open_site", "open_folder", "create_file",
        "create_folder", "create_script", "search", "organize",
        "schedule", "timer", "volume", "screenshot", "ai_execute",
        "ai_generate", "rename", "delegate_to_brain", "web_search",
        "clipboard_write",
    }

    # Acoes VERMELHAS - potencialmente destrutivas
    RED_ACTIONS: Set[str] = {
        "delete", "cleanup", "close_app", "close_all", "power",
        "command", "install_program", "move_copy", "direct_command",
    }

    def __init__(self, mode: str = "safe"):
        """
        Args:
            mode: "safe" (confirma red) ou "free" (executa tudo)
        """
        self.mode = mode

    def classify(self, action_type: str) -> str:
        """Classifica acao em green/yellow/red."""
        if action_type in self.GREEN_ACTIONS:
            return "green"
        if action_type in self.YELLOW_ACTIONS:
            return "yellow"
        if action_type in self.RED_ACTIONS:
            return "red"
        # Default: cautela
        return "yellow"

    def should_confirm(self, action_type: str) -> bool:
        """Se mode=safe, acoes red requerem confirmacao do usuario."""
        if self.mode == "free":
            return False
        return self.classify(action_type) == "red"

    def can_execute(self, action_type: str, agent_scopes: List[str] = None) -> bool:
        """Verifica se acao esta permitida pelo escopo do agente."""
        if agent_scopes is None:
            return True
        return action_type in agent_scopes or "all" in agent_scopes

    def get_risk_emoji(self, action_type: str) -> str:
        """Retorna emoji para o nivel de risco."""
        level = self.classify(action_type)
        return {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(level, "⚪")


class SandboxScope:
    """Define escopo de acesso para cada agente."""

    # Comandos perigosos que NUNCA devem ser executados
    BLOCKED_COMMANDS = [
        "format", "del /s /q", "rmdir /s /q", "rm -rf /",
        "shutdown /s", "shutdown /r", "reg delete",
        "net user", "net localgroup", "netsh",
        "powershell -enc", "base64", "iex(",
    ]

    def __init__(self, allowed_dirs: List[str] = None,
                 allowed_actions: List[str] = None,
                 blocked_commands: List[str] = None):
        """
        Args:
            allowed_dirs: Diretorios permitidos (ex: ["~/Desktop", "~/Documents"])
            allowed_actions: Tipos de acao permitidos (ex: ["create_file", "read"])
            blocked_commands: Comandos adicionais a bloquear
        """
        self.allowed_dirs = [
            os.path.expanduser(d).replace("/", os.sep)
            for d in (allowed_dirs or self._default_dirs())
        ]
        self.allowed_actions = set(allowed_actions or ["all"])
        self.blocked_commands = (blocked_commands or []) + self.BLOCKED_COMMANDS

    @staticmethod
    def _default_dirs() -> List[str]:
        """Diretorios seguros por padrao."""
        return [
            os.path.join(USER_HOME, "Desktop"),
            os.path.join(USER_HOME, "Documents"),
            os.path.join(USER_HOME, "Downloads"),
            os.path.join(USER_HOME, "Pictures"),
            os.path.join(USER_HOME, "Videos"),
            os.path.join(USER_HOME, "Music"),
            os.path.join(USER_HOME, ".william"),
        ]

    def validate_path(self, path: str) -> bool:
        """Verifica se path esta dentro dos diretorios permitidos."""
        try:
            abs_path = os.path.abspath(path).replace("/", os.sep)
            return any(
                abs_path.startswith(allowed.replace("/", os.sep))
                for allowed in self.allowed_dirs
            )
        except Exception:
            return False

    def validate_command(self, command: str) -> bool:
        """Verifica se comando NAO esta na blocklist."""
        cmd_lower = command.lower().strip()
        for blocked in self.blocked_commands:
            if blocked.lower() in cmd_lower:
                log.warning(f"Comando bloqueado pelo sandbox: {blocked}")
                return False
        return True

    def validate_action(self, action_type: str) -> bool:
        """Verifica se tipo de acao esta permitido."""
        if "all" in self.allowed_actions:
            return True
        return action_type in self.allowed_actions

    def get_summary(self) -> str:
        """Retorna resumo do escopo para debug/display."""
        dirs = [os.path.basename(d) for d in self.allowed_dirs]
        actions = list(self.allowed_actions)[:5]
        return f"Dirs: {dirs}, Actions: {actions}"


# ============================================================
# Singleton e helpers
# ============================================================

_risk_policy = None


def get_risk_policy(mode: str = None) -> RiskPolicy:
    """Retorna singleton do RiskPolicy."""
    global _risk_policy
    if _risk_policy is None:
        from config.settings import settings
        policy_mode = mode or getattr(settings, 'SECURITY_MODE', 'safe')
        _risk_policy = RiskPolicy(mode=policy_mode)
    return _risk_policy


def get_default_sandbox() -> SandboxScope:
    """Retorna sandbox padrao (diretorios do usuario)."""
    return SandboxScope()
