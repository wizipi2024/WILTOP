"""
Skill Leiloes - Monitora e gerencia leiloes, lances e oportun idades.
"""

import json
from pathlib import Path
from typing import Dict
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "business" / "leiloes_data.json"


class LeilaoSkill(BaseSkill):
    """Gerencia operacoes de leiloes."""

    name = "leilao_skill"
    display_name = "Leiloes"
    description = "Monitora leiloes, analisa oportunidades e gerencia lances"
    version = "1.0.0"
    category = "business"
    icon = "🔨"
    max_risk_level = "yellow"

    _keywords = [
        "leilao", "leiloes", "lance", "lances",
        "arremate", "arrematar", "licitar", "licitacao",
        "hasta publica", "pregao", "edital",
        "lote", "lotes", "avaliacao", "oportunidade",
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
        """Executa operacoes de leiloes."""
        cmd_lower = command.lower()

        if any(w in cmd_lower for w in ["listar", "quais", "monitorados"]):
            return self._listar_leiloes()

        if any(w in cmd_lower for w in ["analisa", "analise", "oportunidade"]):
            return self._analisar_oportunidade()

        if any(w in cmd_lower for w in ["relatorio", "resumo", "status"]):
            return self._relatorio_leiloes()

        if any(w in cmd_lower for w in ["adicionar", "monitorar", "novo"]):
            return SkillResult(success=True, message="Para adicionar leilao, especifique o ID e descricao.")

        return SkillResult(
            success=False,
            message="Comando de leilao nao reconhecido. Tente: listar, analise, relatorio."
        )

    def _listar_leiloes(self) -> SkillResult:
        """Lista leiloes monitorados."""
        leiloes = self.data.get("leiloes", [])

        if not leiloes:
            return SkillResult(success=True, message="Nenhum leilao em monitoramento.")

        msg = f"Leiloes monitorados ({len(leiloes)}):\n"
        for l in leiloes[:5]:
            msg += f"- {l['descricao']} (Prox.lance: R${l['lance_minimo']})\n"

        return SkillResult(
            success=True,
            message=msg,
            data={"total": len(leiloes), "leiloes": leiloes[:5]}
        )

    def _analisar_oportunidade(self) -> SkillResult:
        """Analisa oportunidade em leiloes."""
        analise = self.data.get("analise", {})

        msg = f"ANALISE DE OPORTUNIDADES\n"
        msg += f"========================\n"
        msg += f"Leiloes com retorno > 50%: {analise.get('alto_retorno', 2)}\n"
        msg += f"Preco medio de lotes: R$ {analise.get('preco_medio', 5000):.2f}\n"
        msg += f"Taxa de sucesso de arrematacoes: {analise.get('taxa_sucesso', 75)}%\n"

        return SkillResult(success=True, message=msg, data=analise)

    def _relatorio_leiloes(self) -> SkillResult:
        """Relatorio de leiloes."""
        historico = self.data.get("historico", {})

        msg = f"RELATORIO LEILOES\n"
        msg += f"=================\n"
        msg += f"Total arrematados: {historico.get('total_arrematados', 12)}\n"
        msg += f"Investimento: R$ {historico.get('investimento', 45000):.2f}\n"
        msg += f"Lucro realizado: R$ {historico.get('lucro', 18000):.2f}\n"

        return SkillResult(success=True, message=msg, data=historico)

    def _load_data(self) -> Dict:
        """Carrega dados."""
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        demo = {
            "leiloes": [
                {"id": "LEI001", "descricao": "Imovel no centro", "lance_minimo": 250000, "status": "ativo"},
                {"id": "LEI002", "descricao": "Veiculo 2015", "lance_minimo": 15000, "status": "ativo"},
                {"id": "LEI003", "descricao": "Equipamentos", "lance_minimo": 5000, "status": "finalizado"},
            ],
            "analise": {
                "alto_retorno": 2,
                "preco_medio": 5000,
                "taxa_sucesso": 75,
            },
            "historico": {
                "total_arrematados": 12,
                "investimento": 45000,
                "lucro": 18000,
            }
        }

        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(demo, f, ensure_ascii=False, indent=2)

        return demo
