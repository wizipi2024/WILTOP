"""
Skill Mercado Livre - Gerencia anuncios, vendas, precos e metricas.
Integracao com operacoes de Mercado Livre.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

CATALOGO_FILE = Path(__file__).parent.parent.parent / "data" / "business" / "mercadolivre_data.json"


class MercadoLivreSkill(BaseSkill):
    """Gerencia operacoes de Mercado Livre."""

    name = "mercadolivre_skill"
    display_name = "Mercado Livre"
    description = "Gerencia anuncios, vendas, precos, metricas e perguntas do Mercado Livre"
    version = "1.0.0"
    author = "William"
    category = "business"
    icon = "🛒"
    requires_network = True
    max_risk_level = "yellow"

    _keywords = [
        "mercado livre", "ml", "anuncio", "anuncios",
        "venda", "vendas", "frete", "comprador",
        "listagem", "listing", "publicar", "publicacao",
        "estoque ml", "performance", "reputacao",
        "perguntas", "reclamacoes", "envio",
        "mercadolivre", "ml vendas", "ml anuncio",
    ]

    def __init__(self):
        super().__init__()
        self.data = self._load_data()

    def can_handle(self, command: str) -> float:
        """Score de confianca para lidar com comando."""
        cmd_lower = command.lower()

        # Keyword matching
        for kw in self._keywords:
            if kw in cmd_lower:
                return 0.85

        # Intent matching
        if any(w in cmd_lower for w in ["venda no", "vendas no", "anuncio no"]):
            return 0.80

        return 0.0

    def execute(self, command: str, params: Dict = None, context: Dict = None) -> SkillResult:
        """Executa operacoes de Mercado Livre."""
        cmd_lower = command.lower()

        if any(w in cmd_lower for w in ["consultar", "buscar", "listar"]) and any(w in cmd_lower for w in ["anuncios", "listagem", "produtos"]):
            return self._listar_anuncios()

        if any(w in cmd_lower for w in ["vendas", "venda", "performance", "metricas"]):
            return self._consultar_vendas()

        if any(w in cmd_lower for w in ["pergunta", "perguntas", "duvida", "duvidas"]):
            return self._listar_perguntas()

        if any(w in cmd_lower for w in ["frete", "envio", "prazo"]):
            return self._consultar_frete()

        if any(w in cmd_lower for w in ["relatorio", "resumo", "status"]):
            return self._relatorio_vendas()

        return SkillResult(
            success=False,
            message="Comando de Mercado Livre nao reconhecido. Tente: consultar anuncios, vendas, perguntas, frete ou relatorio."
        )

    def _listar_anuncios(self) -> SkillResult:
        """Lista anuncios publicados."""
        if not self.data.get("anuncios"):
            return SkillResult(success=True, message="Nenhum anuncio publicado ainda.")

        anuncios = self.data["anuncios"]
        lista = f"Anuncios no Mercado Livre ({len(anuncios)}):\n"
        for a in anuncios[:5]:  # Top 5
            lista += f"- {a['titulo']} (ID: {a['id']}, Status: {a['status']})\n"

        return SkillResult(
            success=True,
            message=lista,
            data={"total": len(anuncios), "anuncios": anuncios[:5]}
        )

    def _consultar_vendas(self) -> SkillResult:
        """Consulta metricas de vendas."""
        vendas = self.data.get("vendas", {})

        msg = f"Performance de Vendas no Mercado Livre:\n"
        msg += f"- Total de vendas (mes): {vendas.get('total_vendas', 0)}\n"
        msg += f"- Faturamento: R$ {vendas.get('faturamento', 0):.2f}\n"
        msg += f"- Ticket medio: R$ {vendas.get('ticket_medio', 0):.2f}\n"
        msg += f"- Taxa de conversao: {vendas.get('taxa_conversao', 0):.1f}%\n"
        msg += f"- Reputacao: {vendas.get('reputacao', 'Boa')}\n"

        return SkillResult(
            success=True,
            message=msg,
            data=vendas
        )

    def _listar_perguntas(self) -> SkillResult:
        """Lista perguntas de compradores."""
        perguntas = self.data.get("perguntas", [])

        if not perguntas:
            return SkillResult(success=True, message="Nenhuma pergunta pendente.")

        msg = f"Perguntas pendentes ({len(perguntas)}):\n"
        for p in perguntas[:3]:
            msg += f"- {p['pergunta']} (Anuncio: {p['anuncio_id']})\n"

        return SkillResult(
            success=True,
            message=msg,
            data={"total": len(perguntas), "perguntas": perguntas[:3]}
        )

    def _consultar_frete(self) -> SkillResult:
        """Consulta informacoes de frete."""
        frete = self.data.get("frete", {})

        msg = f"Frete - Mercado Livre:\n"
        msg += f"- Metodos disponiveis: {', '.join(frete.get('metodos', []))}\n"
        msg += f"- Prazo medio: {frete.get('prazo_dias', 5)} dias\n"
        msg += f"- Cobertura: {frete.get('cobertura', 'Brasil')}\n"

        return SkillResult(success=True, message=msg, data=frete)

    def _relatorio_vendas(self) -> SkillResult:
        """Gera relatorio consolidado de vendas."""
        vendas = self.data.get("vendas", {})
        anuncios = self.data.get("anuncios", [])

        msg = f"RELATORIO MERCADO LIVRE\n"
        msg += f"=====================\n"
        msg += f"Anuncios ativos: {len(anuncios)}\n"
        msg += f"Vendas (mes): {vendas.get('total_vendas', 0)}\n"
        msg += f"Faturamento: R$ {vendas.get('faturamento', 0):.2f}\n"
        msg += f"Reputacao: {vendas.get('reputacao', 'Boa')}\n"

        return SkillResult(
            success=True,
            message=msg,
            data={"vendas": vendas, "anuncios": len(anuncios)}
        )

    def _load_data(self) -> Dict:
        """Carrega dados de catalogo ou cria demo."""
        if CATALOGO_FILE.exists():
            with open(CATALOGO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        # Demo data
        demo = {
            "anuncios": [
                {"id": "ML001", "titulo": "Produto A", "preco": 99.90, "estoque": 10, "status": "ativo"},
                {"id": "ML002", "titulo": "Produto B", "preco": 149.90, "estoque": 5, "status": "ativo"},
                {"id": "ML003", "titulo": "Produto C", "preco": 79.90, "estoque": 0, "status": "pausado"},
            ],
            "vendas": {
                "total_vendas": 150,
                "faturamento": 15890.50,
                "ticket_medio": 105.94,
                "taxa_conversao": 12.5,
                "reputacao": "Excelente",
            },
            "perguntas": [
                {"id": "P001", "anuncio_id": "ML001", "pergunta": "Tem em outra cor?", "resposta": "Nao disponivel"},
                {"id": "P002", "anuncio_id": "ML002", "pergunta": "Qual o prazo de envio?", "resposta": "5-7 dias uteis"},
            ],
            "frete": {
                "metodos": ["Mercado Envios", "Loggi", "Sedex"],
                "prazo_dias": 5,
                "cobertura": "Brasil"
            }
        }

        # Salva demo
        CATALOGO_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CATALOGO_FILE, "w", encoding="utf-8") as f:
            json.dump(demo, f, ensure_ascii=False, indent=2)

        log.info(f"Demo Mercado Livre criada em {CATALOGO_FILE}")
        return demo
