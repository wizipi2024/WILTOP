"""
Role Cards - Perfis de agentes especializados.
Define capacidades, escopo e limites de cada agente virtual.
Item 14 do plano arquitetural.
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
from src.utils.logger import get_logger

log = get_logger(__name__)

ROLES_DIR = os.path.join(str(Path(__file__).resolve().parent.parent.parent), "config", "roles")


@dataclass
class RoleCard:
    """Define perfil de um agente especializado."""

    name: str                          # ID interno: "file_agent"
    display_name: str                  # Nome visual: "Agente de Arquivos"
    description: str                   # Descricao curta
    allowed_actions: List[str]         # Tipos de acao permitidos
    allowed_dirs: List[str] = field(default_factory=list)  # Diretorios de escopo
    tools: List[str] = field(default_factory=lambda: ["smart_executor"])
    max_risk_level: str = "yellow"     # Ate que nivel pode executar sem confirmar
    icon: str = "🤖"                   # Emoji identificador
    color: str = "#00f5ff"             # Cor no GUI

    def to_dict(self) -> Dict:
        """Serializa para dict."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "allowed_actions": self.allowed_actions,
            "allowed_dirs": self.allowed_dirs,
            "tools": self.tools,
            "max_risk_level": self.max_risk_level,
            "icon": self.icon,
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'RoleCard':
        """Cria de dict/JSON."""
        return cls(
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            description=data.get("description", ""),
            allowed_actions=data.get("allowed_actions", []),
            allowed_dirs=data.get("allowed_dirs", []),
            tools=data.get("tools", ["smart_executor"]),
            max_risk_level=data.get("max_risk_level", "yellow"),
            icon=data.get("icon", "🤖"),
            color=data.get("color", "#00f5ff"),
        )

    @classmethod
    def from_json_file(cls, path: str) -> 'RoleCard':
        """Carrega de arquivo JSON."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def can_do(self, action_type: str) -> bool:
        """Verifica se este role pode executar esta acao."""
        return "all" in self.allowed_actions or action_type in self.allowed_actions

    def get_summary(self) -> str:
        """Resumo para display."""
        return f"{self.icon} {self.display_name}: {self.description}"


# ============================================================
# Roles pre-definidos
# ============================================================

DEFAULT_ROLES: Dict[str, RoleCard] = {
    "file_agent": RoleCard(
        name="file_agent",
        display_name="Agente de Arquivos",
        description="Gerencia arquivos e pastas no PC",
        allowed_actions=[
            "create_file", "create_file_with_content", "delete", "read",
            "list", "rename", "move_copy", "create_folder", "organize",
            "search_local", "open_folder",
        ],
        allowed_dirs=["~/Desktop", "~/Documents", "~/Downloads"],
        tools=["smart_executor"],
        max_risk_level="yellow",
        icon="📁",
        color="#00ff88",
    ),

    "browser_agent": RoleCard(
        name="browser_agent",
        display_name="Agente de Navegacao",
        description="Navega web, busca informacoes, automatiza browser",
        allowed_actions=[
            "open_site", "search", "web_answer", "web_search",
            "screenshot", "ask_user",
        ],
        allowed_dirs=[],
        tools=["browser_automation", "web_search"],
        max_risk_level="yellow",
        icon="🌐",
        color="#0088ff",
    ),

    "system_agent": RoleCard(
        name="system_agent",
        display_name="Agente de Sistema",
        description="Informacoes e controle do sistema operacional",
        allowed_actions=[
            "system_info", "disk", "battery", "network", "wifi",
            "process_list", "volume", "cleanup", "open_app", "close_app",
            "datetime", "timer", "startup_apps", "installed_programs",
        ],
        allowed_dirs=[],
        tools=["smart_executor"],
        max_risk_level="yellow",
        icon="💻",
        color="#ff8800",
    ),

    "general_agent": RoleCard(
        name="general_agent",
        display_name="Agente Geral",
        description="Conversa, perguntas, geracoes de codigo pela IA",
        allowed_actions=[
            "ai_answer", "ai_execute", "ai_generate", "web_answer",
            "delegate_to_brain", "create_script", "info",
        ],
        allowed_dirs=["~/Desktop"],
        tools=["ai_brain", "web_search"],
        max_risk_level="red",
        icon="🧠",
        color="#b44aff",
    ),

    "scheduler_agent": RoleCard(
        name="scheduler_agent",
        display_name="Agente de Agendamento",
        description="Agenda e gerencia tarefas programadas",
        allowed_actions=[
            "schedule", "timer", "list_scheduled",
        ],
        allowed_dirs=[],
        tools=["scheduler"],
        max_risk_level="green",
        icon="⏰",
        color="#ffee00",
    ),

    "business_agent": RoleCard(
        name="business_agent",
        display_name="Agente de Negocios",
        description="Operacoes comerciais, vendas, estoque e financeiro",
        allowed_actions=[
            "skill_business", "mercadolivre", "autopecas", "leilao",
            "pricing", "reports", "marketing", "atendimento",
        ],
        allowed_dirs=["~/Desktop/WILTOP/data/business"],
        tools=["skill_manager"],
        max_risk_level="yellow",
        icon="💼",
        color="#3B82F6",
    ),

    "marketing_agent": RoleCard(
        name="marketing_agent",
        display_name="Agente de Marketing",
        description="Criacao de anuncios, campanhas e criativos",
        allowed_actions=[
            "skill_business", "marketing", "copy", "campaign",
            "ai_generate",
        ],
        allowed_dirs=["~/Desktop/WILTOP/data/business"],
        tools=["skill_manager", "ai_brain"],
        max_risk_level="yellow",
        icon="📢",
        color="#EC4899",
    ),

    "strategy_agent": RoleCard(
        name="strategy_agent",
        display_name="Agente de Estrategia",
        description="Define modelo de negocio, oferta, ticket e funil completo com IA",
        allowed_actions=[
            "skill_business", "estrategia", "modelo_negocio", "oferta",
            "ticket", "funil", "avatar", "canais", "ai_generate",
        ],
        allowed_dirs=["~/Desktop/WILTOP/data/business"],
        tools=["skill_manager", "ai_brain"],
        max_risk_level="yellow",
        icon="🎯",
        color="#F59E0B",
    ),

    "conversion_agent": RoleCard(
        name="conversion_agent",
        display_name="Agente de Conversao",
        description="Gera copy, scripts de vendas, sequencias de follow-up e propostas",
        allowed_actions=[
            "skill_business", "copy", "script", "mensagem", "proposta",
            "objecao", "sequencia", "follow_up", "ai_generate",
        ],
        allowed_dirs=["~/Desktop/WILTOP/data/business"],
        tools=["skill_manager", "ai_brain"],
        max_risk_level="yellow",
        icon="💬",
        color="#10B981",
    ),

    "n8n_agent": RoleCard(
        name="n8n_agent",
        display_name="Agente n8n",
        description="Cria e gerencia fluxos de automacao no n8n (captura, follow-up, CRM)",
        allowed_actions=[
            "skill_business", "n8n", "workflow", "automacao", "funil",
            "webhook", "crm", "integracao", "api_call",
        ],
        allowed_dirs=["~/Desktop/WILTOP/data/n8n"],
        tools=["skill_manager", "http_client"],
        max_risk_level="yellow",
        icon="⚙️",
        color="#6366F1",
    ),
}


def get_role(name: str) -> Optional[RoleCard]:
    """Retorna role card pelo nome."""
    return DEFAULT_ROLES.get(name)


def get_all_roles() -> Dict[str, RoleCard]:
    """Retorna todos os roles disponiveis."""
    roles = dict(DEFAULT_ROLES)

    # Carrega roles customizados de config/roles/
    if os.path.exists(ROLES_DIR):
        for filename in os.listdir(ROLES_DIR):
            if filename.endswith(".json"):
                try:
                    role = RoleCard.from_json_file(os.path.join(ROLES_DIR, filename))
                    roles[role.name] = role
                except Exception as e:
                    log.error(f"Erro ao carregar role {filename}: {e}")

    return roles


def select_best_role(action_type: str) -> Optional[RoleCard]:
    """Seleciona o melhor role para executar um tipo de acao."""
    for role in DEFAULT_ROLES.values():
        if role.can_do(action_type):
            return role
    return DEFAULT_ROLES.get("general_agent")
