"""
Skill Store - Catalogo local de skills instalaveis.
Item 25 do plano arquitetural.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from src.utils.logger import get_logger

log = get_logger(__name__)

CATALOG_FILE = os.path.join(
    str(Path(__file__).resolve().parent.parent.parent),
    "config", "skill_catalog.json"
)


class SkillStore:
    """
    Catalogo de skills disponiveis e instalaveis.
    Gerencia metadados e status de instalacao.
    """

    def __init__(self, catalog_file: str = None):
        self.catalog_file = catalog_file or CATALOG_FILE
        self.catalog: Dict[str, Dict] = {}
        self._load_catalog()

    def _load_catalog(self):
        """Carrega catalogo do arquivo JSON."""
        try:
            if os.path.exists(self.catalog_file):
                with open(self.catalog_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        self.catalog[item["name"]] = item
                elif isinstance(data, dict):
                    self.catalog = data
            else:
                # Cria catalogo inicial com skills builtin
                self._create_default_catalog()
        except Exception as e:
            log.error(f"Erro ao carregar catalogo: {e}")
            self._create_default_catalog()

    def _create_default_catalog(self):
        """Cria catalogo padrao com skills builtin."""
        self.catalog = {
            "calculator_skill": {
                "name": "calculator_skill",
                "display_name": "Calculadora",
                "description": "Calculos matematicos e conversoes",
                "category": "general",
                "version": "1.0.0",
                "author": "William System",
                "installed": True,
                "builtin": True,
                "icon": "🧮",
            },
            "web_search_skill": {
                "name": "web_search_skill",
                "display_name": "Pesquisa Web",
                "description": "Busca informacoes na internet",
                "category": "web",
                "version": "1.0.0",
                "author": "William System",
                "installed": True,
                "builtin": True,
                "icon": "🔍",
            },
            "file_ops_skill": {
                "name": "file_ops_skill",
                "display_name": "Operacoes de Arquivo",
                "description": "Criar, ler, mover, copiar e organizar arquivos",
                "category": "file",
                "version": "1.0.0",
                "author": "William System",
                "installed": True,
                "builtin": True,
                "icon": "📁",
            },
            "browser_skill": {
                "name": "browser_skill",
                "display_name": "Navegador Web",
                "description": "Automatiza navegacao web com Playwright/Selenium",
                "category": "web",
                "version": "1.0.0",
                "author": "William System",
                "installed": True,
                "builtin": True,
                "icon": "🌐",
                "requires": ["playwright"],
            },
            "autopecas_skill": {
                "name": "autopecas_skill",
                "display_name": "Auto Pecas",
                "description": "Consulta catalogo de pecas automotivas, precos e compatibilidade",
                "category": "business",
                "version": "1.0.0",
                "author": "William System",
                "installed": False,
                "builtin": False,
                "icon": "🔧",
            },
        }
        self._save_catalog()

    def _save_catalog(self):
        """Salva catalogo."""
        try:
            os.makedirs(os.path.dirname(self.catalog_file), exist_ok=True)
            data = list(self.catalog.values())
            with open(self.catalog_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Erro ao salvar catalogo: {e}")

    def list_all(self) -> List[Dict]:
        """Lista todas as skills do catalogo."""
        return list(self.catalog.values())

    def list_installed(self) -> List[Dict]:
        """Lista skills instaladas."""
        return [s for s in self.catalog.values() if s.get("installed")]

    def list_available(self) -> List[Dict]:
        """Lista skills disponiveis para instalar."""
        return [s for s in self.catalog.values() if not s.get("installed")]

    def get_skill_info(self, name: str) -> Optional[Dict]:
        """Retorna info de uma skill."""
        return self.catalog.get(name)

    def mark_installed(self, name: str) -> bool:
        """Marca skill como instalada."""
        if name in self.catalog:
            self.catalog[name]["installed"] = True
            self._save_catalog()
            return True
        return False

    def mark_uninstalled(self, name: str) -> bool:
        """Marca skill como nao instalada."""
        if name in self.catalog:
            # Nao permite desinstalar builtins
            if self.catalog[name].get("builtin"):
                log.warning(f"Skill builtin nao pode ser desinstalada: {name}")
                return False
            self.catalog[name]["installed"] = False
            self._save_catalog()
            return True
        return False

    def add_to_catalog(self, skill_info: Dict) -> bool:
        """Adiciona skill ao catalogo."""
        name = skill_info.get("name")
        if not name:
            return False
        self.catalog[name] = skill_info
        self._save_catalog()
        return True

    def search(self, query: str) -> List[Dict]:
        """Busca skills no catalogo por keyword."""
        query_lower = query.lower()
        results = []
        for skill in self.catalog.values():
            text = f"{skill.get('name', '')} {skill.get('display_name', '')} {skill.get('description', '')} {skill.get('category', '')}".lower()
            if query_lower in text:
                results.append(skill)
        return results


# Singleton
_store = None


def get_skill_store() -> SkillStore:
    """Retorna singleton do SkillStore."""
    global _store
    if _store is None:
        _store = SkillStore()
    return _store
