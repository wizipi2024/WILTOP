"""
File Operations Skill - Operacoes de arquivo.
Wraps detectores de arquivo do SmartExecutorV2.
"""

import os
import re
from pathlib import Path
from typing import Dict, List
from src.skills.base_skill import BaseSkill, SkillResult


class FileOpsSkill(BaseSkill):
    """Skill de operacoes com arquivos e pastas."""

    name = "file_ops_skill"
    display_name = "Operacoes de Arquivo"
    description = "Criar, ler, listar, mover, copiar e organizar arquivos e pastas"
    version = "1.0.0"
    category = "file"
    icon = "📁"
    max_risk_level = "yellow"

    _keywords = [
        "crie arquivo", "criar arquivo", "crie pasta", "criar pasta",
        "crie uma pasta", "crie um arquivo",
        "apague", "delete", "remova", "excl",
        "mova", "mover", "copie", "copiar",
        "renomeie", "renomear", "rename",
        "liste", "listar", "mostrar arquivos",
        "abra pasta", "abrir pasta", "abra a pasta",
        "organize", "organizar",
        "leia", "ler", "conteudo",
    ]

    def can_handle(self, command: str) -> float:
        """Verifica se e operacao de arquivo."""
        cmd = command.lower()

        for kw in self._keywords:
            if kw in cmd:
                return 0.8

        # Extensoes de arquivo mencionadas
        if re.search(r'\.\w{1,5}\b', command):
            if any(w in cmd for w in ["crie", "abra", "delete", "copie", "mova"]):
                return 0.7

        return 0.0

    def execute(self, command: str, params: Dict = None, context: Dict = None) -> SkillResult:
        """
        Executa operacao de arquivo.
        Delega para SmartExecutorV2 que ja tem todos os detectores.
        """
        try:
            from src.core.smart_executor_v2 import SmartExecutorV2
            executor = SmartExecutorV2()
            result = executor.process_message(command)

            if result.get("executed"):
                actions = result.get("actions", [])
                success = all(a.get("success", False) for a in actions)
                messages = [a.get("message", "") for a in actions if a.get("message")]
                action_types = [a.get("type", "") for a in actions]

                return SkillResult(
                    success=success,
                    message="\n".join(messages) if messages else "Operacao executada.",
                    data={"actions": action_types},
                    actions_taken=action_types,
                )
            else:
                return SkillResult(
                    success=False,
                    message="Nao consegui identificar a operacao de arquivo.",
                )

        except Exception as e:
            return SkillResult(success=False, message=f"Erro: {str(e)}")

    def get_commands(self) -> List[str]:
        return [
            "crie uma pasta chamada Projetos no desktop",
            "liste os arquivos da pasta Downloads",
            "mova relatorio.pdf para Documentos",
            "organize os arquivos do desktop por tipo",
        ]
