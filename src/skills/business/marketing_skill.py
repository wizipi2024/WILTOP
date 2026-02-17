"""Skill Marketing - Cria anuncios, campanhas e criativos."""

import json
from pathlib import Path
from typing import Dict
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "business" / "marketing_data.json"


class MarketingSkill(BaseSkill):
    """Gerencia marketing, anuncios e criativos."""

    name = "marketing_skill"
    display_name = "Marketing & Criativos"
    description = "Cria anuncios, gera textos criativos e gerencia campanhas"
    version = "1.0.0"
    category = "business"
    icon = "📢"
    requires_ai = True
    max_risk_level = "yellow"

    _keywords = [
        "anuncio", "campanha", "marketing", "criativo",
        "banner", "post", "copy", "texto publicitario",
        "facebook ads", "google ads", "instagram ads",
        "headline", "descricao", "cta", "lead", "leads",
        "funil", "conversao", "ad", "ads",
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
        """Executa operacoes de marketing."""
        cmd_lower = command.lower()

        if any(w in cmd_lower for w in ["gerar", "criar", "escrever"]) and "copy" in cmd_lower:
            return self._gerar_copy()

        if any(w in cmd_lower for w in ["campanha", "campaign"]):
            return self._criar_campanha()

        if any(w in cmd_lower for w in ["criativo", "sugerir", "ideias"]):
            return self._sugerir_criativos()

        if any(w in cmd_lower for w in ["relatorio", "performance", "metricas"]):
            return self._relatorio_campanhas()

        return SkillResult(
            success=False,
            message="Comando de marketing nao reconhecido. Tente: copy, campanha, criativos, relatorio."
        )

    def _gerar_copy(self) -> SkillResult:
        """Gera copy publicitario."""
        templates = self.data.get("copy_templates", [])

        msg = "TEMPLATES DE COPY:\n"
        for i, t in enumerate(templates[:3], 1):
            msg += f"{i}. {t['titulo']}\n   {t['exemplo'][:80]}...\n"

        return SkillResult(success=True, message=msg, data=templates[:3])

    def _criar_campanha(self) -> SkillResult:
        """Template de campanha."""
        msg = """NOVO PLANEJAMENTO DE CAMPANHA
================================
1. Objetivo: [Aumentar vendas/Gerar leads/Brand awareness]
2. Publico-alvo: [Definir demografico]
3. Canais: [Google Ads, Facebook, Instagram]
4. Orcamento: [Definir valor]
5. KPIs: [Conversao, CPC, ROAS]
6. Timeline: [Definir periodo]

Proximos passos: Revisar com cliente e criar anuncios."""

        return SkillResult(success=True, message=msg)

    def _sugerir_criativos(self) -> SkillResult:
        """Sugere ideias criativas."""
        criativos = self.data.get("ideias_criativos", [])

        msg = f"IDEIAS DE CRIATIVOS ({len(criativos)}):\n"
        for c in criativos[:5]:
            msg += f"- {c['idea']}: {c['descricao']}\n"

        return SkillResult(success=True, message=msg, data=criativos[:5])

    def _relatorio_campanhas(self) -> SkillResult:
        """Relatorio de campanhas."""
        stats = self.data.get("stats", {})

        msg = "PERFORMANCE DE CAMPANHAS\n"
        msg += f"Campanhas ativas: {stats.get('campanhas_ativas', 5)}\n"
        msg += f"Impressoes: {stats.get('impressoes', 500000):,}\n"
        msg += f"Cliques: {stats.get('cliques', 15000):,}\n"
        msg += f"CTR: {stats.get('ctr', 3.0):.2f}%\n"
        msg += f"Conversoes: {stats.get('conversoes', 450)}\n"
        msg += f"ROAS: {stats.get('roas', 3.5):.2f}x\n"

        return SkillResult(success=True, message=msg, data=stats)

    def _load_data(self) -> Dict:
        """Carrega dados."""
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        demo = {
            "copy_templates": [
                {"titulo": "Copy para conversao", "exemplo": "Nao deixe passar! Oferta limitada..."},
                {"titulo": "Copy para urgencia", "exemplo": "Apenas hoje! Apenas 5 unidades disponiveis..."},
                {"titulo": "Copy para beneficio", "exemplo": "Economize 50% comprando agora..."},
            ],
            "ideias_criativos": [
                {"idea": "Video testimonial", "descricao": "Cliente falando resultado"},
                {"idea": "Carousel de produtos", "descricao": "Mostrar variedade"},
                {"idea": "Antes e depois", "descricao": "Transformacao visual"},
            ],
            "stats": {
                "campanhas_ativas": 5,
                "impressoes": 500000,
                "cliques": 15000,
                "ctr": 3.0,
                "conversoes": 450,
                "roas": 3.5,
            }
        }

        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(demo, f, ensure_ascii=False, indent=2)

        return demo
