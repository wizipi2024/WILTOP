"""
Playbooks - Procedimentos padrao para tarefas comuns.
Quando o usuario pede algo que tem playbook, executa a sequencia automaticamente.
Item 17 do plano arquitetural.
"""

import json
import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from src.utils.logger import get_logger

log = get_logger(__name__)

PLAYBOOKS_DIR = os.path.join(
    str(Path(__file__).resolve().parent.parent.parent), "config", "playbooks"
)


@dataclass
class PlaybookStep:
    """Um passo de um playbook."""
    action: str              # Tipo de acao: "web_search", "create_file", etc.
    description: str         # Descricao do passo
    params: Dict = field(default_factory=dict)  # Parametros (podem ter {variaveis})
    agent: str = "general_agent"  # Qual agente executa
    condition: Optional[str] = None  # Condicao para executar (ex: "previous_success")
    timeout: int = 30        # Timeout em segundos


@dataclass
class Playbook:
    """Procedimento padrao com passos sequenciais."""

    name: str                          # ID: "pesquisa_completa"
    display_name: str                  # "Pesquisa Completa"
    description: str                   # Descricao
    steps: List[PlaybookStep]          # Passos na ordem
    trigger_patterns: List[str]        # Regex que ativam este playbook
    variables: List[str] = field(default_factory=list)  # Variaveis extraidas do input
    category: str = "geral"            # Categoria
    enabled: bool = True

    def matches(self, message: str) -> Optional[Dict]:
        """
        Verifica se a mensagem ativa este playbook.
        Retorna dict de variaveis extraidas ou None.
        """
        msg_lower = message.lower().strip()
        for pattern in self.trigger_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                variables = match.groupdict() if match.groupdict() else {}
                # Extrai texto restante como "topic" se nao tem grupo nomeado
                if not variables and match.groups():
                    variables["topic"] = match.group(1).strip()
                elif not variables:
                    # Pega texto apos o trigger
                    remaining = msg_lower[match.end():].strip()
                    if remaining:
                        variables["topic"] = remaining
                return variables
        return None

    def to_dict(self) -> Dict:
        """Serializa."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "steps": [
                {
                    "action": s.action,
                    "description": s.description,
                    "params": s.params,
                    "agent": s.agent,
                    "condition": s.condition,
                    "timeout": s.timeout,
                }
                for s in self.steps
            ],
            "trigger_patterns": self.trigger_patterns,
            "variables": self.variables,
            "category": self.category,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Playbook':
        """Cria de dict/JSON."""
        steps = [
            PlaybookStep(
                action=s["action"],
                description=s.get("description", ""),
                params=s.get("params", {}),
                agent=s.get("agent", "general_agent"),
                condition=s.get("condition"),
                timeout=s.get("timeout", 30),
            )
            for s in data.get("steps", [])
        ]
        return cls(
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            description=data.get("description", ""),
            steps=steps,
            trigger_patterns=data.get("trigger_patterns", []),
            variables=data.get("variables", []),
            category=data.get("category", "geral"),
            enabled=data.get("enabled", True),
        )


# ============================================================
# Playbooks pre-definidos
# ============================================================

BUILTIN_PLAYBOOKS: Dict[str, Playbook] = {
    "pesquisa_completa": Playbook(
        name="pesquisa_completa",
        display_name="Pesquisa Completa",
        description="Pesquisa um topico na web e salva resumo em arquivo",
        steps=[
            PlaybookStep(
                action="web_search",
                description="Buscar na web sobre {topic}",
                params={"query": "{topic}"},
                agent="browser_agent",
            ),
            PlaybookStep(
                action="ai_summarize",
                description="Resumir resultados da busca",
                params={"max_lines": 10},
                agent="general_agent",
            ),
            PlaybookStep(
                action="create_file",
                description="Salvar resumo em arquivo texto",
                params={"filename": "pesquisa_{topic}.txt", "dir": "Desktop"},
                agent="file_agent",
            ),
        ],
        trigger_patterns=[
            r"pesquise? tudo sobre (.+)",
            r"pesquisa completa sobre (.+)",
            r"fac?a uma pesquisa detalhada sobre (.+)",
        ],
        variables=["topic"],
        category="pesquisa",
    ),

    "backup_pasta": Playbook(
        name="backup_pasta",
        display_name="Backup de Pasta",
        description="Cria backup compactado de uma pasta",
        steps=[
            PlaybookStep(
                action="list_files",
                description="Listar arquivos da pasta {source}",
                params={"dir": "{source}"},
                agent="file_agent",
            ),
            PlaybookStep(
                action="create_backup",
                description="Comprimir pasta em ZIP",
                params={"source": "{source}", "format": "zip"},
                agent="file_agent",
            ),
        ],
        trigger_patterns=[
            r"fac?a backup (?:da pasta )?(.+)",
            r"backup (?:da )?(?:pasta )?(.+)",
        ],
        variables=["source"],
        category="sistema",
    ),

    "limpar_sistema": Playbook(
        name="limpar_sistema",
        display_name="Limpeza do Sistema",
        description="Limpa arquivos temporarios e mostra espaco liberado",
        steps=[
            PlaybookStep(
                action="disk",
                description="Verificar espaco em disco antes",
                agent="system_agent",
            ),
            PlaybookStep(
                action="cleanup",
                description="Limpar arquivos temporarios",
                agent="system_agent",
            ),
            PlaybookStep(
                action="disk",
                description="Verificar espaco em disco depois",
                agent="system_agent",
            ),
        ],
        trigger_patterns=[
            r"limpeza completa",
            r"limpe tudo",
            r"fac?a uma limpeza",
        ],
        category="sistema",
    ),

    "relatorio_sistema": Playbook(
        name="relatorio_sistema",
        display_name="Relatorio do Sistema",
        description="Gera relatorio completo do sistema (CPU, RAM, disco, rede)",
        steps=[
            PlaybookStep(
                action="system_info",
                description="Coletar info de CPU e RAM",
                agent="system_agent",
            ),
            PlaybookStep(
                action="disk",
                description="Coletar info de disco",
                agent="system_agent",
            ),
            PlaybookStep(
                action="battery",
                description="Verificar bateria",
                agent="system_agent",
            ),
            PlaybookStep(
                action="network",
                description="Verificar rede",
                agent="system_agent",
            ),
        ],
        trigger_patterns=[
            r"relatorio do sistema",
            r"relatorio completo",
            r"status completo do sistema",
            r"diagnostico do sistema",
        ],
        category="sistema",
    ),
}


class PlaybookManager:
    """Gerencia playbooks disponiveis."""

    def __init__(self):
        self.playbooks: Dict[str, Playbook] = dict(BUILTIN_PLAYBOOKS)
        self._load_custom()

    def _load_custom(self):
        """Carrega playbooks customizados de config/playbooks/."""
        if not os.path.exists(PLAYBOOKS_DIR):
            return
        for filename in os.listdir(PLAYBOOKS_DIR):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(PLAYBOOKS_DIR, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                    pb = Playbook.from_dict(data)
                    if pb.enabled:
                        self.playbooks[pb.name] = pb
                        log.info(f"Playbook carregado: {pb.name}")
                except Exception as e:
                    log.error(f"Erro ao carregar playbook {filename}: {e}")

    def find_playbook(self, message: str) -> Optional[tuple]:
        """
        Encontra playbook que match a mensagem.
        Retorna (Playbook, variables_dict) ou None.
        """
        for pb in self.playbooks.values():
            if not pb.enabled:
                continue
            variables = pb.matches(message)
            if variables is not None:
                return (pb, variables)
        return None

    def list_playbooks(self) -> List[Dict]:
        """Lista playbooks disponiveis."""
        return [
            {
                "name": pb.name,
                "display_name": pb.display_name,
                "description": pb.description,
                "steps_count": len(pb.steps),
                "category": pb.category,
            }
            for pb in self.playbooks.values()
            if pb.enabled
        ]

    def save_playbook(self, playbook: Playbook):
        """Salva playbook customizado."""
        os.makedirs(PLAYBOOKS_DIR, exist_ok=True)
        filepath = os.path.join(PLAYBOOKS_DIR, f"{playbook.name}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(playbook.to_dict(), f, ensure_ascii=False, indent=2)
        self.playbooks[playbook.name] = playbook


# Singleton
_playbook_manager = None


def get_playbook_manager() -> PlaybookManager:
    """Retorna singleton do PlaybookManager."""
    global _playbook_manager
    if _playbook_manager is None:
        _playbook_manager = PlaybookManager()
    return _playbook_manager
