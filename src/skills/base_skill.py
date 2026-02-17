"""
Base Skill - Classe abstrata base para todas as skills.
Define a interface que toda skill deve implementar.
Item 6 do plano arquitetural.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class SkillResult:
    """Resultado padrao de execucao de uma skill."""
    success: bool
    message: str
    data: Dict = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)
    next_step: Optional[str] = None
    proof: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "actions_taken": self.actions_taken,
            "next_step": self.next_step,
            "proof": self.proof,
        }


class BaseSkill(ABC):
    """
    Classe abstrata base para skills do William.

    Toda skill deve implementar:
    - name: identificador unico
    - display_name: nome legivel
    - execute(): executa a skill
    - can_handle(): retorna score 0-1 se pode lidar com o input
    """

    # Metadados da skill (devem ser definidos nas subclasses)
    name: str = "base_skill"
    display_name: str = "Base Skill"
    description: str = "Skill base abstrata"
    version: str = "1.0.0"
    author: str = "William System"
    category: str = "general"  # general, file, web, system, business
    icon: str = "🔧"

    # Configuracao
    enabled: bool = True
    requires_ai: bool = False       # Se precisa de AI Engine
    requires_network: bool = False   # Se precisa de internet
    max_risk_level: str = "green"    # green, yellow, red

    @abstractmethod
    def execute(self, command: str, params: Dict = None, context: Dict = None) -> SkillResult:
        """
        Executa a skill.

        Args:
            command: Comando/mensagem do usuario
            params: Parametros extraidos
            context: Contexto adicional (historico, memoria, etc)

        Returns:
            SkillResult com resultado da execucao
        """
        pass

    @abstractmethod
    def can_handle(self, command: str) -> float:
        """
        Retorna score (0.0-1.0) indicando se esta skill pode lidar com o comando.
        0.0 = nao pode lidar
        0.5 = talvez
        1.0 = certeza que pode lidar

        Args:
            command: Comando/mensagem do usuario

        Returns:
            Score de 0.0 a 1.0
        """
        pass

    def get_help(self) -> str:
        """Retorna texto de ajuda da skill."""
        return f"{self.icon} **{self.display_name}** v{self.version}\n{self.description}"

    def get_commands(self) -> List[str]:
        """Retorna lista de comandos/exemplos que esta skill entende."""
        return []

    def validate_params(self, params: Dict) -> bool:
        """Valida parametros antes de executar."""
        return True

    def get_info(self) -> Dict:
        """Retorna metadados da skill."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "category": self.category,
            "icon": self.icon,
            "enabled": self.enabled,
            "requires_ai": self.requires_ai,
            "requires_network": self.requires_network,
            "max_risk_level": self.max_risk_level,
            "commands": self.get_commands(),
        }

    def __repr__(self):
        return f"<Skill:{self.name} v{self.version}>"
