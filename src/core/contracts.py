"""
Output Contracts - Formato padronizado para resultados de acoes.
Garante que TODA acao retorna: sucesso, tipo, mensagem, prova, proximo passo.
Item 23 do plano arquitetural.
"""

import os
import psutil
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path


@dataclass
class ActionResult:
    """Contrato padrao para resultado de qualquer acao."""

    success: bool
    action_type: str              # "file_create", "web_search", "app_open", etc.
    message: str                  # Mensagem para o usuario
    proof: Optional[str] = None   # Evidencia (path, screenshot, output)
    next_step: Optional[str] = None  # Proxima acao sugerida
    risk_level: str = "green"     # green/yellow/red
    agent: str = "system"         # Qual agente executou
    task_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Serializa para dict (compativel com formato legado de actions)."""
        return {
            "success": self.success,
            "type": self.action_type,
            "message": self.message,
            "proof": self.proof,
            "next_step": self.next_step,
            "risk_level": self.risk_level,
            "agent": self.agent,
            "task_id": self.task_id,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_legacy(cls, old_result: Dict) -> 'ActionResult':
        """Converte resultado legado do SmartExecutorV2 (dict) para ActionResult."""
        return cls(
            success=old_result.get("success", False),
            action_type=old_result.get("type", "unknown"),
            message=old_result.get("message", ""),
            proof=old_result.get("proof"),
            next_step=old_result.get("next_step"),
            risk_level=old_result.get("risk_level", "green"),
            agent=old_result.get("agent", "system"),
            task_id=old_result.get("task_id"),
        )

    @classmethod
    def error(cls, message: str, action_type: str = "error") -> 'ActionResult':
        """Cria ActionResult de erro rapido."""
        return cls(success=False, action_type=action_type, message=message,
                   risk_level="red")

    @classmethod
    def info(cls, message: str) -> 'ActionResult':
        """Cria ActionResult informativo."""
        return cls(success=True, action_type="info", message=message)


class ProofCollector:
    """Coleta evidencias de acoes executadas."""

    @staticmethod
    def collect_proof(action_result: ActionResult) -> Optional[str]:
        """Gera prova dependendo do tipo de acao. Retorna string descritiva."""
        action_type = action_result.action_type
        message = action_result.message

        try:
            if action_type in ("create_file", "create_folder", "create_script",
                               "ai_generate"):
                return ProofCollector._proof_file_exists(message)

            elif action_type in ("open_app", "open_site"):
                return ProofCollector._proof_process_running(message)

            elif action_type in ("delete", "cleanup"):
                return ProofCollector._proof_file_deleted(message)

            elif action_type in ("web_answer", "search"):
                return ProofCollector._proof_web_result(message)

            elif action_type == "screenshot":
                return ProofCollector._proof_screenshot(message)

            elif action_type in ("system_info", "disk", "battery", "network"):
                return "Dados coletados do sistema em tempo real"

            elif action_type in ("datetime",):
                return "Horario obtido do sistema operacional"

            elif action_type in ("process_list",):
                return "Lista obtida via psutil.process_iter()"

            elif action_type in ("ai_execute",):
                return "Codigo executado via subprocess com Python do venv"

        except Exception:
            pass

        return None

    @staticmethod
    def _proof_file_exists(message: str) -> Optional[str]:
        """Verifica se arquivo/pasta mencionado existe."""
        import re
        # Tenta extrair path da mensagem
        path_match = re.search(r'[A-Z]:\\[^\n"\']+', message)
        if path_match:
            path = path_match.group(0).rstrip('.')
            if os.path.exists(path):
                if os.path.isdir(path):
                    items = len(os.listdir(path))
                    return f"Pasta existe: {path} ({items} itens)"
                else:
                    size = os.path.getsize(path)
                    return f"Arquivo existe: {path} ({size} bytes)"
            else:
                return f"AVISO: Path nao encontrado: {path}"
        return None

    @staticmethod
    def _proof_process_running(message: str) -> Optional[str]:
        """Verifica se processo/app esta rodando."""
        import re
        # Tenta extrair nome do app
        app_words = ["chrome", "notepad", "calc", "explorer", "code", "spotify",
                     "discord", "firefox", "edge", "cmd", "powershell", "steam"]
        msg_lower = message.lower()
        for app in app_words:
            if app in msg_lower:
                for proc in psutil.process_iter(['name']):
                    try:
                        if app in proc.info['name'].lower():
                            return f"Processo encontrado: {proc.info['name']} (PID {proc.pid})"
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return f"Processo '{app}' nao encontrado (pode ter aberto externamente)"
        return None

    @staticmethod
    def _proof_file_deleted(message: str) -> Optional[str]:
        """Verifica se arquivo foi realmente deletado."""
        import re
        path_match = re.search(r'[A-Z]:\\[^\n"\']+', message)
        if path_match:
            path = path_match.group(0).rstrip('.')
            if not os.path.exists(path):
                return f"Confirmado: '{path}' nao existe mais"
            else:
                return f"AVISO: '{path}' ainda existe"
        return None

    @staticmethod
    def _proof_web_result(message: str) -> Optional[str]:
        """Prova de resultado web."""
        if "[Fonte:" in message:
            return "Resultado obtido de fonte web verificada"
        return "Resultado obtido da busca web"

    @staticmethod
    def _proof_screenshot(message: str) -> Optional[str]:
        """Prova de screenshot."""
        import re
        path_match = re.search(r'[A-Z]:\\[^\n"\']+\.png', message, re.IGNORECASE)
        if path_match:
            path = path_match.group(0)
            if os.path.exists(path):
                size = os.path.getsize(path)
                return f"Screenshot salvo: {path} ({size} bytes)"
        return None


def enrich_legacy_result(result: Dict) -> Dict:
    """Enriquece resultado legado do SmartExecutorV2 com campos do contrato.
    Retrocompativel - adiciona campos extras sem quebrar formato existente."""
    if not result.get("success"):
        return result

    action_result = ActionResult.from_legacy(result)

    # Coleta prova
    proof = ProofCollector.collect_proof(action_result)
    if proof:
        result["proof"] = proof

    # Classifica risco (sera preenchido pelo RiskPolicy em security.py)
    if "risk_level" not in result:
        result["risk_level"] = "green"

    # Timestamp
    if "timestamp" not in result:
        result["timestamp"] = datetime.now().isoformat()

    return result
