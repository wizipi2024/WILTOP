"""Skill Atendimento - Gerencia tickets, FAQs e respostas ao cliente."""

import json
from pathlib import Path
from typing import Dict
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "business" / "atendimento_data.json"


class AtendimentoSkill(BaseSkill):
    """Gerencia atendimento ao cliente."""

    name = "atendimento_skill"
    display_name = "Atendimento ao Cliente"
    description = "Gerencia atendimentos, respostas automaticas e tickets"
    version = "1.0.0"
    category = "business"
    icon = "🎧"
    requires_ai = True
    max_risk_level = "yellow"

    _keywords = [
        "atendimento", "cliente", "clientes",
        "ticket", "tickets", "chamado", "chamados",
        "resposta", "responder", "mensagem",
        "reclamacao", "reclamacoes", "suporte",
        "duvida", "duvidas", "faq",
        "sac", "pos venda", "pos-venda",
        "feedback", "satisfacao", "insatisfacao",
    ]

    def __init__(self):
        super().__init__()
        self.data = self._load_data()

    def can_handle(self, command: str) -> float:
        """Score de confianca."""
        cmd_lower = command.lower()
        for kw in self._keywords:
            if kw in cmd_lower:
                return 0.85
        return 0.0

    def execute(self, command: str, params: Dict = None, context: Dict = None) -> SkillResult:
        """Executa operacoes de atendimento."""
        cmd_lower = command.lower()

        if any(w in cmd_lower for w in ["listar", "quais", "abertos"]):
            return self._listar_tickets()

        if any(w in cmd_lower for w in ["responder", "resposta", "reply"]):
            return self._responder_ticket()

        if any(w in cmd_lower for w in ["faq", "pergunta frequente", "duvida comum"]):
            return self._criar_faq()

        if any(w in cmd_lower for w in ["relatorio", "satisfacao", "nps"]):
            return self._relatorio_atendimento()

        if any(w in cmd_lower for w in ["sugerir", "template", "modelo"]):
            return self._sugerir_resposta()

        return SkillResult(
            success=False,
            message="Comando de atendimento nao reconhecido. Tente: tickets, responder, FAQ, relatorio, sugerir."
        )

    def _listar_tickets(self) -> SkillResult:
        """Lista tickets abertos."""
        tickets = self.data.get("tickets", [])

        if not tickets:
            return SkillResult(success=True, message="Nenhum ticket pendente. Equipe em dia!")

        msg = f"TICKETS PENDENTES ({len(tickets)}):\n"
        for t in tickets[:5]:
            msg += f"- [{t['prioridade']}] {t['assunto']} (Cliente: {t['cliente']})\n"

        return SkillResult(success=True, message=msg, data={"total": len(tickets), "tickets": tickets[:5]})

    def _responder_ticket(self) -> SkillResult:
        """Template de resposta para ticket."""
        msg = """TEMPLATE DE RESPOSTA
=====================
Prezado(a) [CLIENTE],

Obrigado por entrar em contato conosco!

[CORPO DA RESPOSTA]

Qualquer duvida adicional, estaremos disponiveis.

Atenciosamente,
Equipe de Suporte"""

        return SkillResult(success=True, message=msg)

    def _criar_faq(self) -> SkillResult:
        """Lista FAQs e permite criar novo."""
        faqs = self.data.get("faqs", [])

        msg = f"FAQs DISPONÍVEIS ({len(faqs)}):\n"
        for f in faqs[:5]:
            msg += f"P: {f['pergunta']}\nR: {f['resposta'][:60]}...\n\n"

        return SkillResult(success=True, message=msg, data=faqs[:5])

    def _relatorio_atendimento(self) -> SkillResult:
        """Relatorio de atendimento."""
        stats = self.data.get("stats", {})

        msg = "RELATORIO DE ATENDIMENTO\n"
        msg += f"========================\n"
        msg += f"Tickets resolvidos: {stats.get('resolvidos', 45)}\n"
        msg += f"Tempo medio resposta: {stats.get('tempo_resposta_min', 2)} minutos\n"
        msg += f"Satisfacao media: {stats.get('satisfacao_pct', 92)}%\n"
        msg += f"NPS: {stats.get('nps', 68)}\n"
        msg += f"Taxa resolucao 1a vez: {stats.get('resolucao_primeira_vez', 78)}%\n"
        msg += f"CSAT: {stats.get('csat', 4.5)}/5.0\n"

        return SkillResult(success=True, message=msg, data=stats)

    def _sugerir_resposta(self) -> SkillResult:
        """Sugere template de resposta baseado em categoria."""
        templates = self.data.get("templates", [])

        msg = "TEMPLATES DE RESPOSTA:\n"
        for t in templates[:3]:
            msg += f"- {t['tipo']}: {t['exemplo'][:70]}...\n"

        return SkillResult(success=True, message=msg, data=templates[:3])

    def _load_data(self) -> Dict:
        """Carrega dados."""
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        demo = {
            "tickets": [
                {"id": "T001", "cliente": "João Silva", "assunto": "Produto chegou com defeito", "prioridade": "alta"},
                {"id": "T002", "cliente": "Maria Santos", "assunto": "Duvida sobre tamanho", "prioridade": "media"},
                {"id": "T003", "cliente": "Pedro Costa", "assunto": "Atraso na entrega", "prioridade": "alta"},
            ],
            "faqs": [
                {"pergunta": "Qual o prazo de entrega?", "resposta": "De 5 a 10 dias uteis."},
                {"pergunta": "Como faço devolucao?", "resposta": "Entre em contato conosco no prazo de 30 dias."},
                {"pergunta": "Vcs aceitam parcelamento?", "resposta": "Sim, ate 12x no cartao de credito."},
            ],
            "stats": {
                "resolvidos": 45,
                "tempo_resposta_min": 2,
                "satisfacao_pct": 92,
                "nps": 68,
                "resolucao_primeira_vez": 78,
                "csat": 4.5
            },
            "templates": [
                {"tipo": "Devolucao", "exemplo": "Para solicitar devolucao, entre em contato..."},
                {"tipo": "Atraso", "exemplo": "Peço desculpas pelo atraso. Vamos..."},
                {"tipo": "Defeito", "exemplo": "Sinto muito! Vamos resolver de imediato..."},
            ]
        }

        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(demo, f, ensure_ascii=False, indent=2)

        return demo
