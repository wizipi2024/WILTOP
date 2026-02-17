"""
Auto Pecas Skill - Skill de dominio para autopecas.
Consulta catalogo, precos, compatibilidade de pecas automotivas.
Item 26 do plano arquitetural.
"""

import json
import os
import re
from typing import Dict, List, Optional
from pathlib import Path
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

CATALOG_FILE = os.path.join(
    str(Path.home()), "Desktop", "WILTOP", "data", "business", "catalogo_pecas.json"
)


class AutoPecasSkill(BaseSkill):
    """Skill de consulta e gerenciamento de autopecas."""

    name = "autopecas_skill"
    display_name = "Auto Pecas"
    description = "Consulta catalogo de pecas, precos, compatibilidade e estoque"
    version = "1.0.0"
    category = "business"
    icon = "🔧"
    max_risk_level = "green"

    _keywords = [
        "peca", "pecas", "peça", "peças",
        "alternador", "motor de arranque", "bomba", "filtro",
        "pastilha", "disco de freio", "amortecedor", "correia",
        "vela", "bobina", "radiador", "compressor", "embreagem",
        "junta", "retentor", "rolamento", "tensor", "valvula",
        "catalogo", "estoque", "compativel", "compatibilidade",
        "serve no", "serve na", "serve pro", "funciona no",
        "preco", "preço", "valor", "quanto custa",
    ]

    def __init__(self):
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> Dict:
        """Carrega catalogo de pecas."""
        try:
            if os.path.exists(CATALOG_FILE):
                with open(CATALOG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            log.debug(f"Catalogo nao encontrado: {e}")

        # Cria catalogo demo
        catalog = self._create_demo_catalog()
        self._save_catalog(catalog)
        return catalog

    def _save_catalog(self, catalog: Dict = None):
        """Salva catalogo."""
        if catalog is None:
            catalog = self.catalog
        try:
            os.makedirs(os.path.dirname(CATALOG_FILE), exist_ok=True)
            with open(CATALOG_FILE, "w", encoding="utf-8") as f:
                json.dump(catalog, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Erro ao salvar catalogo: {e}")

    def _create_demo_catalog(self) -> Dict:
        """Cria catalogo demo de pecas."""
        return {
            "pecas": [
                {
                    "id": "ALT001",
                    "nome": "Alternador",
                    "marca": "Bosch",
                    "codigo": "F000BL0759",
                    "preco": 450.00,
                    "estoque": 3,
                    "compatibilidade": ["Gol G4", "Gol G5", "Fox", "Polo", "Saveiro"],
                    "categoria": "eletrica",
                },
                {
                    "id": "ALT002",
                    "nome": "Alternador",
                    "marca": "Valeo",
                    "codigo": "437454",
                    "preco": 520.00,
                    "estoque": 1,
                    "compatibilidade": ["Corsa", "Celta", "Prisma", "Classic"],
                    "categoria": "eletrica",
                },
                {
                    "id": "FIL001",
                    "nome": "Filtro de Oleo",
                    "marca": "Tecfil",
                    "codigo": "PH6017",
                    "preco": 25.00,
                    "estoque": 15,
                    "compatibilidade": ["Gol G4", "Gol G5", "Fox", "Polo", "Voyage"],
                    "categoria": "filtros",
                },
                {
                    "id": "FIL002",
                    "nome": "Filtro de Ar",
                    "marca": "Mann",
                    "codigo": "C27006",
                    "preco": 35.00,
                    "estoque": 8,
                    "compatibilidade": ["Gol G5", "Fox", "Up", "Polo"],
                    "categoria": "filtros",
                },
                {
                    "id": "PAS001",
                    "nome": "Pastilha de Freio Dianteira",
                    "marca": "Frasle",
                    "codigo": "PD/285",
                    "preco": 85.00,
                    "estoque": 6,
                    "compatibilidade": ["Gol G4", "Gol G5", "Fox", "Polo", "Saveiro"],
                    "categoria": "freios",
                },
                {
                    "id": "AMO001",
                    "nome": "Amortecedor Dianteiro",
                    "marca": "Cofap",
                    "codigo": "GP32496",
                    "preco": 280.00,
                    "estoque": 4,
                    "compatibilidade": ["Gol G5", "Fox", "Voyage"],
                    "categoria": "suspensao",
                },
                {
                    "id": "COR001",
                    "nome": "Correia Dentada",
                    "marca": "Gates",
                    "codigo": "5549XS",
                    "preco": 95.00,
                    "estoque": 5,
                    "compatibilidade": ["Gol G4", "Gol G5", "Fox", "Polo", "Saveiro"],
                    "categoria": "motor",
                },
                {
                    "id": "VEL001",
                    "nome": "Vela de Ignicao",
                    "marca": "NGK",
                    "codigo": "BKR6E",
                    "preco": 18.00,
                    "estoque": 20,
                    "compatibilidade": ["Gol G4", "Gol G5", "Fox", "Polo", "Corsa", "Celta"],
                    "categoria": "ignicao",
                },
                {
                    "id": "BOB001",
                    "nome": "Bobina de Ignicao",
                    "marca": "Bosch",
                    "codigo": "0221604103",
                    "preco": 180.00,
                    "estoque": 3,
                    "compatibilidade": ["Gol G5", "Fox", "Polo", "Voyage", "Up"],
                    "categoria": "ignicao",
                },
                {
                    "id": "RAD001",
                    "nome": "Radiador",
                    "marca": "Visconde",
                    "codigo": "12835",
                    "preco": 350.00,
                    "estoque": 2,
                    "compatibilidade": ["Gol G4", "Gol G5", "Saveiro"],
                    "categoria": "arrefecimento",
                },
            ],
            "metadata": {
                "total_pecas": 10,
                "categorias": ["eletrica", "filtros", "freios", "suspensao",
                              "motor", "ignicao", "arrefecimento"],
                "marcas": ["Bosch", "Valeo", "Tecfil", "Mann", "Frasle",
                          "Cofap", "Gates", "NGK", "Visconde"],
            },
        }

    def can_handle(self, command: str) -> float:
        """Verifica se e consulta de autopecas."""
        cmd = command.lower()

        # Match forte de keywords de autopecas
        matches = sum(1 for kw in self._keywords if kw in cmd)
        if matches >= 2:
            return 0.9
        elif matches >= 1:
            return 0.6

        return 0.0

    def execute(self, command: str, params: Dict = None, context: Dict = None) -> SkillResult:
        """Executa consulta de autopecas."""
        cmd = command.lower()

        # Detecta intencao
        if any(w in cmd for w in ["preco", "preço", "valor", "quanto custa", "quanto sai"]):
            return self._consultar_preco(cmd)
        elif any(w in cmd for w in ["serve", "funciona", "encaixa", "compativel", "compatibilidade"]):
            return self._verificar_compatibilidade(cmd)
        elif any(w in cmd for w in ["estoque", "inventario", "quantas", "relatorio"]):
            return self._relatorio_estoque()
        elif any(w in cmd for w in ["adicionar", "cadastrar", "nova peca"]):
            return self._adicionar_peca(cmd, params)
        else:
            return self._consultar_peca(cmd)

    def _consultar_peca(self, query: str) -> SkillResult:
        """Consulta peca no catalogo."""
        results = []
        for peca in self.catalog.get("pecas", []):
            nome = peca.get("nome", "").lower()
            marca = peca.get("marca", "").lower()
            codigo = peca.get("codigo", "").lower()
            categoria = peca.get("categoria", "").lower()

            if (any(w in query for w in nome.split()) or
                marca in query or codigo in query or categoria in query):
                results.append(peca)

        if results:
            lines = [f"Encontrei {len(results)} peca(s):\n"]
            for p in results:
                compat = ", ".join(p.get("compatibilidade", [])[:5])
                lines.append(
                    f"  {p['nome']} ({p['marca']}) - R${p['preco']:.2f}\n"
                    f"    Codigo: {p['codigo']} | Estoque: {p['estoque']}un\n"
                    f"    Compativel: {compat}"
                )
            return SkillResult(
                success=True,
                message="\n".join(lines),
                data={"results": results, "count": len(results)},
                actions_taken=["consultar_peca"],
            )
        else:
            return SkillResult(
                success=False,
                message="Nao encontrei essa peca no catalogo.",
                data={"query": query},
            )

    def _consultar_preco(self, query: str) -> SkillResult:
        """Consulta preco de peca."""
        result = self._consultar_peca(query)
        if result.success:
            pecas = result.data.get("results", [])
            lines = ["Precos encontrados:\n"]
            for p in pecas:
                lines.append(
                    f"  {p['nome']} ({p['marca']}): R${p['preco']:.2f} "
                    f"({'Em estoque' if p['estoque'] > 0 else 'ESGOTADO'})"
                )
            return SkillResult(
                success=True,
                message="\n".join(lines),
                data=result.data,
                actions_taken=["consultar_preco"],
            )
        return result

    def _verificar_compatibilidade(self, query: str) -> SkillResult:
        """Verifica compatibilidade de peca com veiculo."""
        # Tenta extrair veiculo
        veiculos = ["gol", "fox", "polo", "saveiro", "voyage", "up",
                    "corsa", "celta", "prisma", "classic", "onix",
                    "ka", "fiesta", "ecosport", "palio", "uno", "siena"]

        veiculo_encontrado = None
        for v in veiculos:
            if v in query:
                veiculo_encontrado = v
                break

        if not veiculo_encontrado:
            return SkillResult(
                success=False,
                message="Me diga o veiculo. Ex: 'serve no gol g5?'",
            )

        # Busca pecas compativeis
        compativeis = []
        for peca in self.catalog.get("pecas", []):
            for compat in peca.get("compatibilidade", []):
                if veiculo_encontrado in compat.lower():
                    compativeis.append(peca)
                    break

        if compativeis:
            lines = [f"Pecas compativeis com '{veiculo_encontrado.title()}':\n"]
            for p in compativeis:
                lines.append(
                    f"  {p['nome']} ({p['marca']}) - R${p['preco']:.2f} "
                    f"[{p['estoque']}un]"
                )
            return SkillResult(
                success=True,
                message="\n".join(lines),
                data={"veiculo": veiculo_encontrado, "pecas": compativeis},
                actions_taken=["verificar_compatibilidade"],
            )
        else:
            return SkillResult(
                success=False,
                message=f"Nao encontrei pecas compativeis com '{veiculo_encontrado}'.",
            )

    def _relatorio_estoque(self) -> SkillResult:
        """Gera relatorio de estoque."""
        pecas = self.catalog.get("pecas", [])
        total_pecas = len(pecas)
        total_estoque = sum(p.get("estoque", 0) for p in pecas)
        valor_total = sum(p.get("preco", 0) * p.get("estoque", 0) for p in pecas)
        esgotados = [p for p in pecas if p.get("estoque", 0) == 0]
        baixo_estoque = [p for p in pecas if 0 < p.get("estoque", 0) <= 2]

        lines = [
            "RELATORIO DE ESTOQUE\n",
            f"  Total de itens: {total_pecas}",
            f"  Unidades em estoque: {total_estoque}",
            f"  Valor total do estoque: R${valor_total:.2f}",
            f"  Esgotados: {len(esgotados)}",
            f"  Baixo estoque (<=2): {len(baixo_estoque)}",
        ]

        if baixo_estoque:
            lines.append("\n  BAIXO ESTOQUE:")
            for p in baixo_estoque:
                lines.append(f"    ! {p['nome']} ({p['marca']}) - {p['estoque']}un")

        if esgotados:
            lines.append("\n  ESGOTADOS:")
            for p in esgotados:
                lines.append(f"    X {p['nome']} ({p['marca']})")

        return SkillResult(
            success=True,
            message="\n".join(lines),
            data={
                "total_pecas": total_pecas,
                "total_estoque": total_estoque,
                "valor_total": valor_total,
                "esgotados": len(esgotados),
                "baixo_estoque": len(baixo_estoque),
            },
            actions_taken=["relatorio_estoque"],
        )

    def _adicionar_peca(self, query: str, params: Dict = None) -> SkillResult:
        """Adiciona nova peca ao catalogo."""
        if not params:
            return SkillResult(
                success=False,
                message="Para adicionar peca, forneca: nome, marca, preco, compatibilidade.",
            )

        try:
            import time
            new_peca = {
                "id": f"USR{int(time.time())}",
                "nome": params.get("nome", "Nova Peca"),
                "marca": params.get("marca", "Generica"),
                "codigo": params.get("codigo", ""),
                "preco": float(params.get("preco", 0)),
                "estoque": int(params.get("estoque", 0)),
                "compatibilidade": params.get("compatibilidade", []),
                "categoria": params.get("categoria", "geral"),
            }

            self.catalog.setdefault("pecas", []).append(new_peca)
            self._save_catalog()

            return SkillResult(
                success=True,
                message=f"Peca adicionada: {new_peca['nome']} ({new_peca['marca']}) - R${new_peca['preco']:.2f}",
                data=new_peca,
                actions_taken=["adicionar_peca"],
            )

        except Exception as e:
            return SkillResult(success=False, message=f"Erro ao adicionar: {str(e)}")

    def get_commands(self) -> List[str]:
        return [
            "alternador do gol g5",
            "quanto custa filtro de oleo",
            "serve no fox?",
            "relatorio de estoque",
            "pecas compativeis com polo",
        ]
