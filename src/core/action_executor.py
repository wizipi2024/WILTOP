"""
Executor de ações do sistema.
Interpreta comandos da IA e executa no sistema.
"""

import re
import json
from typing import Dict, Any, Optional
from src.modules.system.system_control import get_system_controller
from src.utils.logger import get_logger
from src.utils.exceptions import SystemOperationError

log = get_logger(__name__)


class ActionExecutor:
    """
    Executor de ações do sistema baseado em comandos da IA.

    IMPORTANTE: Requer autorização explícita do usuário!
    """

    def __init__(self, authorized: bool = False):
        """
        Inicializa o executor.

        Args:
            authorized: Se True, autoriza execução de comandos
        """
        self.authorized = authorized
        self.system = get_system_controller(authorized=authorized)
        log.info(f"ActionExecutor inicializado (autorizado: {authorized})")

    def authorize(self):
        """Autoriza execução de comandos."""
        self.authorized = True
        self.system.authorize()
        log.warning("ActionExecutor AUTORIZADO - pode executar comandos no sistema")

    def parse_and_execute(self, ai_response: str) -> Dict[str, Any]:
        """
        Analisa resposta da IA e executa ações se houver comandos.

        Args:
            ai_response: Resposta da IA

        Returns:
            Dicionário com resultado da execução
        """
        # Procura por blocos de ação no formato [ACTION:tipo:parametros]
        action_pattern = r'\[ACTION:(.*?)\]'
        actions = re.findall(action_pattern, ai_response)

        if not actions:
            return {"has_actions": False, "response": ai_response}

        results = []
        for action in actions:
            try:
                result = self._execute_action(action)
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})

        # Remove marcadores de ação da resposta
        clean_response = re.sub(action_pattern, '', ai_response).strip()

        return {
            "has_actions": True,
            "response": clean_response,
            "actions_results": results
        }

    def _execute_action(self, action_str: str) -> Dict[str, Any]:
        """
        Executa uma ação específica.

        Args:
            action_str: String da ação (ex: "execute:notepad.exe")

        Returns:
            Resultado da execução
        """
        if not self.authorized:
            return {
                "success": False,
                "error": "Ações não autorizadas. Peça ao usuário para autorizar."
            }

        parts = action_str.split(':', 1)
        if len(parts) < 2:
            return {"success": False, "error": "Formato de ação inválido"}

        action_type = parts[0].lower()
        params = parts[1]

        try:
            if action_type == "execute":
                # Executa comando
                result = self.system.execute_command(params)
                return {
                    "success": result["success"],
                    "action": "execute",
                    "command": params,
                    "output": result["stdout"]
                }

            elif action_type == "open":
                # Abre aplicação
                self.system.open_application(params)
                return {
                    "success": True,
                    "action": "open",
                    "app": params
                }

            elif action_type == "create_file":
                # Cria arquivo (formato: path|content)
                path, content = params.split('|', 1) if '|' in params else (params, "")
                self.system.create_file(path, content)
                return {
                    "success": True,
                    "action": "create_file",
                    "path": path
                }

            elif action_type == "read_file":
                # Lê arquivo
                content = self.system.read_file(params)
                return {
                    "success": True,
                    "action": "read_file",
                    "path": params,
                    "content": content[:500]  # Primeiros 500 chars
                }

            elif action_type == "list_files":
                # Lista arquivos
                files = self.system.list_files(params)
                return {
                    "success": True,
                    "action": "list_files",
                    "path": params,
                    "count": len(files),
                    "files": [f["name"] for f in files[:10]]  # Primeiros 10
                }

            elif action_type == "delete":
                # Deleta arquivo
                self.system.delete_file(params)
                return {
                    "success": True,
                    "action": "delete",
                    "path": params
                }

            elif action_type == "system_info":
                # Info do sistema
                info = self.system.get_system_info()
                return {
                    "success": True,
                    "action": "system_info",
                    "info": info
                }

            else:
                return {
                    "success": False,
                    "error": f"Tipo de ação desconhecido: {action_type}"
                }

        except SystemOperationError as e:
            return {
                "success": False,
                "error": str(e),
                "action": action_type
            }

    def execute_direct_command(self, command: str) -> Dict[str, Any]:
        """
        Executa comando diretamente (sem parsing).

        Args:
            command: Comando a executar

        Returns:
            Resultado da execução
        """
        if not self.authorized:
            raise SystemOperationError("Execução não autorizada")

        return self.system.execute_command(command)

    def list_capabilities(self) -> Dict[str, Any]:
        """
        Retorna lista de capacidades disponíveis.

        Returns:
            Dicionário com capacidades
        """
        return {
            "authorized": self.authorized,
            "capabilities": {
                "execute_commands": self.authorized,
                "file_operations": self.authorized,
                "system_info": True,
                "process_management": self.authorized,
                "application_control": self.authorized
            },
            "available_actions": [
                "execute:<comando>",
                "open:<aplicacao>",
                "create_file:<path>|<conteudo>",
                "read_file:<path>",
                "list_files:<diretorio>",
                "delete:<path>",
                "system_info"
            ]
        }


# Instância global
_executor = None


def get_action_executor(authorized: bool = False) -> ActionExecutor:
    """
    Retorna instância global do executor de ações.

    Args:
        authorized: Se True, autoriza operações

    Returns:
        Instância do ActionExecutor
    """
    global _executor
    if _executor is None:
        _executor = ActionExecutor(authorized=authorized)
    elif authorized and not _executor.authorized:
        _executor.authorize()

    return _executor
