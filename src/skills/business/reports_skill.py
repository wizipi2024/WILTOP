"""Skill Relatorios - Gera relatorios de vendas, financeiro e performance."""

import json
from pathlib import Path
from typing import Dict
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "business" / "reports_data.json"


class ReportsSkill(BaseSkill):
    """Gerencia relatorios estrategicos."""

    name = "reports_skill"
    display_name = "Relatorios Estrategicos"
    description = "Gera relatorios de vendas, estoque, financeiro e performance"
    version = "1.0.0"
    category = "business"
    icon = "📊"
    max_risk_level = "green"

    _keywords = [
        "relatorio", "relatorios", "report",
        "resumo", "balanco", "resultado",
        "faturamento", "receita", "despesa",
        "kpi", "indicador", "indicadores",
        "mensal", "semanal", "diario", "anual",
        "analise", "performance", "metricas",
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
        """Executa operacoes de relatorios."""
        cmd_lower = command.lower()

        if any(w in cmd_lower for w in ["vendas", "venda"]):
            return self._relatorio_vendas()

        if any(w in cmd_lower for w in ["financeiro", "financeira"]):
            return self._relatorio_financeiro()

        if any(w in cmd_lower for w in ["estoque", "inventario"]):
            return self._relatorio_estoque()

        if any(w in cmd_lower for w in ["kpi", "performance", "indicador"]):
            return self._relatorio_kpi()

        if any(w in cmd_lower for w in ["mensal", "semanal", "diario"]):
            return self._relatorio_periodo()

        return SkillResult(
            success=False,
            message="Comando de relatorio nao reconhecido. Tente: vendas, financeiro, estoque, KPI, periodo."
        )

    def _relatorio_vendas(self) -> SkillResult:
        """Relatorio de vendas consolidado."""
        vendas = self.data.get("vendas", {})

        msg = "RELATORIO DE VENDAS\n"
        msg += f"===================\n"
        msg += f"Periodo: {vendas.get('periodo', 'Janeiro')}\n"
        msg += f"Total de vendas: {vendas.get('total_vendas', 150)}\n"
        msg += f"Faturamento: R$ {vendas.get('faturamento', 15890.50):.2f}\n"
        msg += f"Ticket medio: R$ {vendas.get('ticket_medio', 105.94):.2f}\n"
        msg += f"Crescimento MoM: {vendas.get('crescimento_pct', 12.5)}%\n"
        msg += f"Top produto: {vendas.get('top_produto', 'Produto A')}\n"

        return SkillResult(success=True, message=msg, data=vendas)

    def _relatorio_financeiro(self) -> SkillResult:
        """Relatorio financeiro."""
        financeiro = self.data.get("financeiro", {})

        msg = "RELATORIO FINANCEIRO\n"
        msg += f"====================\n"
        msg += f"Receita total: R$ {financeiro.get('receita', 50000):.2f}\n"
        msg += f"Custos: R$ {financeiro.get('custos', 20000):.2f}\n"
        msg += f"Despesas: R$ {financeiro.get('despesas', 8000):.2f}\n"
        msg += f"Lucro bruto: R$ {financeiro.get('lucro_bruto', 30000):.2f}\n"
        msg += f"Lucro liquido: R$ {financeiro.get('lucro_liquido', 22000):.2f}\n"
        msg += f"Margem: {financeiro.get('margem_pct', 44)}%\n"

        return SkillResult(success=True, message=msg, data=financeiro)

    def _relatorio_estoque(self) -> SkillResult:
        """Relatorio de estoque."""
        estoque = self.data.get("estoque", {})

        msg = "RELATORIO DE ESTOQUE\n"
        msg += f"====================\n"
        msg += f"Total de SKUs: {estoque.get('total_skus', 45)}\n"
        msg += f"Valor total: R$ {estoque.get('valor_total', 85000):.2f}\n"
        msg += f"Itens criticos: {estoque.get('criticos', 3)}\n"
        msg += f"Itens em excesso: {estoque.get('excesso', 5)}\n"
        msg += f"Rotacao media: {estoque.get('rotacao_dias', 30)} dias\n"
        msg += f"Turnover: {estoque.get('turnover', 12.2)}x\n"

        return SkillResult(success=True, message=msg, data=estoque)

    def _relatorio_kpi(self) -> SkillResult:
        """Relatorio de KPIs."""
        kpis = self.data.get("kpis", {})

        msg = "DASHBOARD DE KPIs\n"
        msg += f"==================\n"
        msg += f"CAC (Custo Aquisicao Cliente): R$ {kpis.get('cac', 85):.2f}\n"
        msg += f"LTV (Lifetime Value): R$ {kpis.get('ltv', 500):.2f}\n"
        msg += f"Taxa conversao: {kpis.get('taxa_conversao', 3.2)}%\n"
        msg += f"Taxa retencao: {kpis.get('taxa_retencao', 75)}%\n"
        msg += f"NPS (Net Promoter Score): {kpis.get('nps', 65)}\n"
        msg += f"ROI marketing: {kpis.get('roi_marketing', 350)}%\n"

        return SkillResult(success=True, message=msg, data=kpis)

    def _relatorio_periodo(self) -> SkillResult:
        """Relatorio por periodo."""
        periodo = self.data.get("periodos", {})

        msg = "COMPARACAO POR PERIODO\n"
        msg += f"======================\n"
        for p, dados in list(periodo.items())[:3]:
            msg += f"{p}: R$ {dados['faturamento']:.2f} ({dados.get('crescimento', '+10')}%)\n"

        return SkillResult(success=True, message=msg, data=periodo)

    def _load_data(self) -> Dict:
        """Carrega dados."""
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        demo = {
            "vendas": {
                "periodo": "Janeiro",
                "total_vendas": 150,
                "faturamento": 15890.50,
                "ticket_medio": 105.94,
                "crescimento_pct": 12.5,
                "top_produto": "Produto A"
            },
            "financeiro": {
                "receita": 50000,
                "custos": 20000,
                "despesas": 8000,
                "lucro_bruto": 30000,
                "lucro_liquido": 22000,
                "margem_pct": 44
            },
            "estoque": {
                "total_skus": 45,
                "valor_total": 85000,
                "criticos": 3,
                "excesso": 5,
                "rotacao_dias": 30,
                "turnover": 12.2
            },
            "kpis": {
                "cac": 85,
                "ltv": 500,
                "taxa_conversao": 3.2,
                "taxa_retencao": 75,
                "nps": 65,
                "roi_marketing": 350
            },
            "periodos": {
                "Janeiro": {"faturamento": 15890, "crescimento": "+10%"},
                "Fevereiro": {"faturamento": 18000, "crescimento": "+13%"},
                "Marco": {"faturamento": 20500, "crescimento": "+14%"}
            }
        }

        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(demo, f, ensure_ascii=False, indent=2)

        return demo
