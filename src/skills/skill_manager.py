"""
Skill Manager - Gerencia registro, busca e execucao de skills.
Item 6 do plano arquitetural.
"""

import os
import importlib
import inspect
from typing import Dict, List, Optional, Tuple
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)


class SkillManager:
    """
    Gerenciador central de skills.
    Registra, busca e executa skills disponiveis.
    """

    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
        self._load_builtin_skills()
        self._load_business_skills()

    def _load_builtin_skills(self):
        """Carrega skills builtin automaticamente."""
        builtin_dir = os.path.join(os.path.dirname(__file__), "builtin")
        if not os.path.exists(builtin_dir):
            log.debug("Diretorio builtin nao encontrado")
            return

        for filename in os.listdir(builtin_dir):
            if filename.endswith("_skill.py") and not filename.startswith("_"):
                module_name = filename[:-3]  # Remove .py
                try:
                    module = importlib.import_module(f"src.skills.builtin.{module_name}")

                    # Procura classes que herdam de BaseSkill
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseSkill) and obj is not BaseSkill:
                            skill_instance = obj()
                            self.register(skill_instance)
                            log.debug(f"Skill builtin carregada: {skill_instance.name}")

                except Exception as e:
                    log.warning(f"Erro ao carregar skill {module_name}: {e}")

        log.info(f"SkillManager: {len(self.skills)} builtin skills carregadas")

    def _load_business_skills(self):
        """Carrega skills de negocio automaticamente."""
        business_dir = os.path.join(os.path.dirname(__file__), "business")
        if not os.path.exists(business_dir):
            log.debug("Diretorio business nao encontrado")
            return

        for filename in os.listdir(business_dir):
            if filename.endswith("_skill.py") and not filename.startswith("_"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"src.skills.business.{module_name}")

                    # Procura classes que herdam de BaseSkill
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseSkill) and obj is not BaseSkill:
                            skill_instance = obj()
                            self.register(skill_instance)
                            log.debug(f"Skill business carregada: {skill_instance.name}")

                except Exception as e:
                    log.warning(f"Erro ao carregar skill business {module_name}: {e}")

        log.info(f"SkillManager: {len(self.skills)} skills total (builtin + business)")

    def register(self, skill: BaseSkill) -> bool:
        """
        Registra uma skill.

        Args:
            skill: Instancia da skill

        Returns:
            True se registrada com sucesso
        """
        if not isinstance(skill, BaseSkill):
            log.error(f"Objeto nao e uma skill: {type(skill)}")
            return False

        if skill.name in self.skills:
            log.warning(f"Skill {skill.name} ja registrada, substituindo")

        self.skills[skill.name] = skill
        log.info(f"Skill registrada: {skill.name} ({skill.display_name})")
        return True

    def unregister(self, skill_name: str) -> bool:
        """Remove skill do registro."""
        if skill_name in self.skills:
            del self.skills[skill_name]
            log.info(f"Skill removida: {skill_name}")
            return True
        return False

    def find_skill(self, command: str, min_score: float = 0.3) -> Optional[Tuple[BaseSkill, float]]:
        """
        Encontra a melhor skill para um comando.

        Args:
            command: Comando/mensagem do usuario
            min_score: Score minimo para considerar

        Returns:
            Tuple (skill, score) ou None se nenhuma skill pode lidar
        """
        best_skill = None
        best_score = 0.0

        for skill in self.skills.values():
            if not skill.enabled:
                continue
            try:
                score = skill.can_handle(command)
                if score > best_score and score >= min_score:
                    best_score = score
                    best_skill = skill
            except Exception as e:
                log.debug(f"Erro em can_handle de {skill.name}: {e}")

        if best_skill:
            return (best_skill, best_score)
        return None

    def find_all_skills(self, command: str, min_score: float = 0.1) -> List[Tuple[BaseSkill, float]]:
        """
        Encontra todas as skills que podem lidar com um comando.

        Returns:
            Lista de (skill, score) ordenada por score
        """
        results = []
        for skill in self.skills.values():
            if not skill.enabled:
                continue
            try:
                score = skill.can_handle(command)
                if score >= min_score:
                    results.append((skill, score))
            except Exception:
                continue

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def execute_skill(self, skill_name: str, command: str,
                      params: Dict = None, context: Dict = None) -> Optional[SkillResult]:
        """
        Executa uma skill especifica pelo nome.

        Args:
            skill_name: Nome da skill
            command: Comando a executar
            params: Parametros
            context: Contexto

        Returns:
            SkillResult ou None se skill nao encontrada
        """
        skill = self.skills.get(skill_name)
        if not skill:
            log.warning(f"Skill nao encontrada: {skill_name}")
            return None

        if not skill.enabled:
            log.warning(f"Skill desabilitada: {skill_name}")
            return SkillResult(success=False, message=f"Skill {skill_name} esta desabilitada")

        try:
            log.info(f"Executando skill: {skill_name}")
            result = skill.execute(command, params, context)

            # Log no observability
            try:
                from src.core.observability import get_event_log
                get_event_log().log_event(
                    "skill_executed",
                    agent=skill.category + "_agent",
                    data={
                        "skill": skill_name,
                        "success": result.success,
                        "message": result.message[:100],
                    }
                )
            except Exception:
                pass

            return result

        except Exception as e:
            log.error(f"Erro ao executar skill {skill_name}: {e}")
            return SkillResult(success=False, message=f"Erro na skill {skill_name}: {str(e)}")

    def auto_execute(self, command: str, params: Dict = None,
                     context: Dict = None) -> Optional[SkillResult]:
        """
        Encontra e executa a melhor skill automaticamente.

        Args:
            command: Comando do usuario
            params: Parametros
            context: Contexto

        Returns:
            SkillResult ou None se nenhuma skill pode lidar
        """
        match = self.find_skill(command)
        if match:
            skill, score = match
            log.info(f"Auto-execute: {skill.name} (score: {score:.2f})")
            return self.execute_skill(skill.name, command, params, context)
        return None

    def list_skills(self) -> List[Dict]:
        """Lista todas as skills registradas."""
        return [skill.get_info() for skill in self.skills.values()]

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """Retorna skill por nome."""
        return self.skills.get(name)

    def enable_skill(self, name: str) -> bool:
        """Habilita uma skill."""
        skill = self.skills.get(name)
        if skill:
            skill.enabled = True
            return True
        return False

    def disable_skill(self, name: str) -> bool:
        """Desabilita uma skill."""
        skill = self.skills.get(name)
        if skill:
            skill.enabled = False
            return True
        return False

    def get_stats(self) -> Dict:
        """Estatisticas do skill manager."""
        total = len(self.skills)
        enabled = sum(1 for s in self.skills.values() if s.enabled)
        categories = {}
        for s in self.skills.values():
            categories[s.category] = categories.get(s.category, 0) + 1

        return {
            "total": total,
            "enabled": enabled,
            "disabled": total - enabled,
            "categories": categories,
        }


# Singleton
_skill_manager = None


def get_skill_manager() -> SkillManager:
    """Retorna singleton do SkillManager."""
    global _skill_manager
    if _skill_manager is None:
        _skill_manager = SkillManager()
    return _skill_manager
