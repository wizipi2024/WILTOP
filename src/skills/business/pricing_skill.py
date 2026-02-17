"""Skill Precificacao - Calcula precos, margens e estrategias."""

import json
from pathlib import Path
from typing import Dict
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "business" / "pricing_data.json"


class PricingSkill(BaseSkill):
    """Gerencia precificacao e margens."""

    name = "pricing_skill"
    display_name = "Precificacao Automatica"
    description = "Calcula precos, margens, markup e estrategias de precificacao"
    version = "1.0.0"
    category = "business"
    icon = "💰"
    max_risk_level = "green"

    _keywords = [
        "preco", "precos", "precificar", "precificacao",
        "margem", "markup", "custo", "lucro",
        "desconto", "promocao", "competidor",
        "valor de venda", "preco de custo", "tabela",
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
        """Executa operacoes de precificacao."""
        cmd_lower = command.lower()

        if any(w in cmd_lower for w in ["calcular", "calcula", "qual preco"]):
            return self._calcular_preco()

        if any(w in cmd_lower for w in ["margem", "margem bruta", "margem liquida"]):
            return self._analisar_margem()

        if any(w in cmd_lower for w in ["sugerir", "recomendacao", "ideal"]):
            return self._sugerir_preco()

        if any(w in cmd_lower for w in ["competidor", "concorrente", "mercado"]):
            return self._comparar_precos()

        if any(w in cmd_lower for w in ["desconto", "promocao", "simular"]):
            return self._simular_desconto()

        return SkillResult(
            success=False,
            message="Comando de pricing nao reconhecido. Tente: calcular, margem, sugerir, competidor, desconto."
        )

    def _calcular_preco(self) -> SkillResult:
        """Calcula preco de venda."""
        template = self.data.get("calculo_template", {})

        msg = "CALCULO DE PRECO DE VENDA\n"
        msg += f"==========================\n"
        msg += f"Custo do produto: R$ 100.00\n"
        msg += f"Despesas (20%): R$ 20.00\n"
        msg += f"Margem desejada (30%): R$ 36.00\n"
        msg += f"PRECO DE VENDA: R$ 156.00\n"

        return SkillResult(success=True, message=msg, data=template)

    def _analisar_margem(self) -> SkillResult:
        """Analisa margem de lucro."""
        margens = self.data.get("margens", {})

        msg = "ANALISE DE MARGENS\n"
        msg += f"Margem bruta: {margens.get('bruta', 50)}%\n"
        msg += f"Margem operacional: {margens.get('operacional', 35)}%\n"
        msg += f"Margem liquida: {margens.get('liquida', 20)}%\n"
        msg += f"Markup padrao: {margens.get('markup', 1.67):.2f}x\n"

        return SkillResult(success=True, message=msg, data=margens)

    def _sugerir_preco(self) -> SkillResult:
        """Sugere preco ideal."""
        sugestao = self.data.get("preco_sugerido", {})

        msg = "PRECO SUGERIDO (Analise de mercado)\n"
        msg += f"Preco minimo: R$ {sugestao.get('minimo', 100):.2f}\n"
        msg += f"Preco ideal: R$ {sugestao.get('ideal', 150):.2f}\n"
        msg += f"Preco maximo: R$ {sugestao.get('maximo', 200):.2f}\n"
        msg += f"Elasticidade: {sugestao.get('elasticidade', 1.2):.2f}\n"

        return SkillResult(success=True, message=msg, data=sugestao)

    def _comparar_precos(self) -> SkillResult:
        """Compara precos com competidores."""
        competidores = self.data.get("competidores", [])

        msg = "COMPARACAO DE PRECOS\n"
        for c in competidores[:5]:
            msg += f"- {c['nome']}: R$ {c['preco']:.2f}\n"

        msg += f"\nNosso preco: R$ 150.00\n"
        msg += f"Posicao: {competidores[0]['posicao'] if competidores else 'intermediaria'}\n"

        return SkillResult(success=True, message=msg, data=competidores[:5])

    def _simular_desconto(self) -> SkillResult:
        """Simula impacto de desconto."""
        msg = "SIMULACAO DE DESCONTO\n"
        msg += f"====================\n"
        msg += f"Preco original: R$ 150.00\n"
        msg += f"10% de desconto: R$ 135.00 (margem -3%)\n"
        msg += f"20% de desconto: R$ 120.00 (margem -12%)\n"
        msg += f"30% de desconto: R$ 105.00 (margem -21%)\n"
        msg += f"\nRecomendacao: Limite a 15% para manter saude financeira.\n"

        return SkillResult(success=True, message=msg)

    def _load_data(self) -> Dict:
        """Carrega dados."""
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        demo = {
            "calculo_template": {"custo": 100, "despesas_pct": 20, "margem_pct": 30},
            "margens": {"bruta": 50, "operacional": 35, "liquida": 20, "markup": 1.67},
            "preco_sugerido": {"minimo": 100, "ideal": 150, "maximo": 200, "elasticidade": 1.2},
            "competidores": [
                {"nome": "Concorrente A", "preco": 145, "posicao": "mais barato"},
                {"nome": "Concorrente B", "preco": 160, "posicao": "mais caro"},
            ]
        }

        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(demo, f, ensure_ascii=False, indent=2)

        return demo
