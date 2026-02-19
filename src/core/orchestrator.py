"""
Agent Orchestrator - Roteador central do sistema multi-agente.
Decide se usa fast path (SmartExecutorV2) ou planner para tarefas complexas.
Item 13 do plano arquitetural.
"""

import re
import json
from typing import Dict, List, Optional, Any
from src.utils.logger import get_logger
from src.core.contracts import ActionResult, ProofCollector, enrich_legacy_result
from src.core.security import RiskPolicy, get_risk_policy
from src.core.observability import get_event_log
from src.core.task_queue import TaskQueue, get_task_queue
from src.core.roles import RoleCard, get_all_roles, select_best_role, DEFAULT_ROLES
from src.core.playbooks import get_playbook_manager
from src.core.quality_gate import get_quality_gate

log = get_logger(__name__)


class AgentOrchestrator:
    """
    Roteador central do William v4.

    Fluxo:
    1. NLP normalize (quando disponivel)
    2. SmartExecutorV2 (fast path - 35+ detectores)
    3. Se delegate_to_brain ou sem match:
       a. Verifica playbooks
       b. Avalia complexidade
       c. Simples -> AI Brain direto
       d. Complexo -> Planner quebra em subtasks
    """

    def __init__(self, executor=None, brain=None, engine=None):
        """
        Args:
            executor: SmartExecutorV2 instance
            brain: AIBrain instance
            engine: AIEngine instance (para planner)
        """
        self.executor = executor
        self.brain = brain
        self.engine = engine
        self.task_queue = get_task_queue()
        self.risk_policy = get_risk_policy()
        self.playbook_manager = get_playbook_manager()
        self.quality_gate = get_quality_gate()
        self.roles = get_all_roles()
        self._nlp_processor = None  # Lazy load

        log.info("AgentOrchestrator inicializado com QualityGate")

    def set_executor(self, executor):
        """Define executor (pode ser setado depois da init)."""
        self.executor = executor

    def set_brain(self, brain):
        """Define brain (pode ser setado depois da init)."""
        self.brain = brain

    def set_engine(self, engine):
        """Define engine (pode ser setado depois da init)."""
        self.engine = engine

    def process(self, message: str, context: List[Dict] = None) -> Dict:
        """
        Ponto de entrada principal. Processa mensagem do usuario.

        Retorna dict compativel com formato existente:
        {
            "executed": bool,
            "actions": [{"success": bool, "type": str, "message": str, ...}],
            "summary": str,
            "delegate_to_brain": bool,  # Se precisa do brain
            "brain_message": str,       # Mensagem para o brain
            "playbook": dict,           # Se encontrou playbook
        }
        """
        result = {
            "executed": False,
            "actions": [],
            "summary": "",
            "delegate_to_brain": False,
            "brain_message": None,
            "playbook": None,
        }

        # Log do evento
        event_log = get_event_log()
        event_log.log_event("message_received", data={"message": message[:200]})

        # ===== PASSO 1: NLP Normalize (se disponivel) =====
        normalized_msg = self._normalize(message)

        # ===== PASSO 2: Fast Path - SmartExecutorV2 =====
        if self.executor:
            exec_result = self.executor.process_message(normalized_msg)

            # Checa delegate_to_brain
            if exec_result["executed"]:
                for action in exec_result["actions"]:
                    if action.get("type") == "delegate_to_brain":
                        result["delegate_to_brain"] = True
                        result["brain_message"] = action.get("message", message)
                        exec_result = {"executed": False, "actions": [], "summary": ""}
                        break

            if exec_result["executed"]:
                # Enriquece resultados com contracts
                enriched_actions = []
                for action in exec_result["actions"]:
                    enriched = enrich_legacy_result(action)
                    # Classifica risco
                    enriched["risk_level"] = self.risk_policy.classify(
                        enriched.get("type", "unknown")
                    )
                    # Coleta prova
                    ar = ActionResult.from_legacy(enriched)
                    proof = ProofCollector.collect_proof(ar)
                    if proof:
                        enriched["proof"] = proof

                    enriched_actions.append(enriched)

                    # Log
                    event_log.log_event(
                        "action_executed",
                        agent=select_best_role(enriched.get("type", "")).name if select_best_role(enriched.get("type", "")) else "system",
                        data={"type": enriched.get("type"), "success": enriched.get("success")},
                        risk_level=enriched.get("risk_level", "green"),
                    )

                result["executed"] = True
                result["actions"] = enriched_actions
                result["summary"] = exec_result.get("summary", "")
                return result

        # ===== PASSO 2.5: Skill System (busca e executa skills) =====
        try:
            from src.skills.skill_manager import get_skill_manager
            skill_mgr = get_skill_manager()
            skill_match = skill_mgr.find_skill(normalized_msg, min_score=0.6)

            if skill_match:
                skill, score = skill_match
                log.info(f"Skill encontrada: {skill.name} (score: {score:.2f})")

                # Executa a skill
                try:
                    skill_result = skill.execute(normalized_msg, {}, context)

                    if skill_result and skill_result.success:
                        # === Quality Gate para skills de negocio ===
                        quality_badge = ""
                        business_skills = {"estrategia", "conversao", "n8n", "prospeccao", "vscode"}
                        if skill.name in business_skills:
                            result_type_map = {
                                "estrategia": "estrategia",
                                "conversao": "copy",
                                "n8n": "n8n",
                                "prospeccao": "all",
                                "vscode": "code",
                            }
                            qtype = result_type_map.get(skill.name, "all")
                            try:
                                eval_result = self.quality_gate.evaluate(qtype, skill_result.message)
                                quality_badge = "\n\n" + self.quality_gate.format_badge(eval_result)
                                log.info(f"QualityGate [{skill.name}]: {eval_result.score}/10 approved={eval_result.approved}")
                            except Exception as qe:
                                log.debug(f"QualityGate erro: {qe}")

                        # Converte SkillResult para o formato esperado
                        action = {
                            "success": True,
                            "type": f"skill_{skill.category}",
                            "message": skill_result.message + quality_badge,
                            "data": skill_result.data or {},
                            "proof": skill_result.proof,
                            "next_step": skill_result.next_step,
                            "risk_level": self.risk_policy.classify(f"skill_{skill.category}"),
                        }

                        event_log.log_event(
                            "skill_executed",
                            agent="skill_agent",
                            data={"skill": skill.name, "success": True},
                            risk_level=action.get("risk_level", "green"),
                        )

                        result["executed"] = True
                        result["actions"] = [action]
                        result["summary"] = skill_result.message
                        result["skill"] = skill.name
                        return result

                except Exception as e:
                    log.error(f"Erro ao executar skill {skill.name}: {e}")

        except ImportError:
            pass  # SkillManager não disponível
        except Exception as e:
            log.debug(f"Erro no skill system: {e}")

        # ===== PASSO 3: Verifica Playbooks =====
        playbook_match = self.playbook_manager.find_playbook(message)
        if playbook_match:
            playbook, variables = playbook_match
            result["playbook"] = {
                "name": playbook.name,
                "display_name": playbook.display_name,
                "steps": len(playbook.steps),
                "variables": variables,
            }
            log.info(f"Playbook encontrado: {playbook.name}")

            # Cria task principal no queue
            main_task = self.task_queue.create_task(
                title=playbook.display_name,
                description=f"Playbook: {playbook.description}",
                command=message,
                agent="general_agent",
            )

            # Cria subtasks para cada step
            for i, step in enumerate(playbook.steps):
                # Substitui variaveis nos params
                step_desc = step.description
                step_params = dict(step.params)
                for var_name, var_value in variables.items():
                    step_desc = step_desc.replace(f"{{{var_name}}}", str(var_value))
                    for k, v in step_params.items():
                        if isinstance(v, str):
                            step_params[k] = v.replace(f"{{{var_name}}}", str(var_value))

                self.task_queue.create_task(
                    title=step_desc,
                    description=f"Step {i+1}/{len(playbook.steps)}",
                    command=step_desc,
                    agent=step.agent,
                    parent_id=main_task.id,
                    order=i,
                )

            # Executa primeiro step via delegacao ao brain
            first_step = playbook.steps[0]
            first_desc = first_step.description
            for var_name, var_value in variables.items():
                first_desc = first_desc.replace(f"{{{var_name}}}", str(var_value))

            result["delegate_to_brain"] = True
            result["brain_message"] = first_desc
            return result

        # ===== PASSO 4: Avalia complexidade =====
        if not result["delegate_to_brain"]:
            complexity = self._assess_complexity(message)

            if complexity == "complex" and self.engine:
                # Tarefa complexa - usa Planner
                log.info(f"Tarefa complexa detectada: {message[:80]}")
                result["delegate_to_brain"] = True
                result["brain_message"] = message

                # Cria task no queue
                self.task_queue.create_task(
                    title=message[:80],
                    description="Tarefa complexa - AI Brain",
                    command=message,
                    agent="general_agent",
                )
            else:
                # Tarefa simples - AI Brain direto
                result["delegate_to_brain"] = True
                result["brain_message"] = message

        event_log.log_event(
            "routing_decision",
            data={
                "delegate_to_brain": result["delegate_to_brain"],
                "has_playbook": result["playbook"] is not None,
            }
        )

        return result

    def _normalize(self, message: str) -> str:
        """Normaliza mensagem com NLP PT-BR (se disponivel)."""
        try:
            if self._nlp_processor is None:
                from src.core.nlp_ptbr import get_nlp_processor
                self._nlp_processor = get_nlp_processor()
            if self._nlp_processor:
                return self._nlp_processor.normalize(message)
        except ImportError:
            pass  # NLP ainda nao implementado (Fase 4)
        except Exception as e:
            log.debug(f"NLP normalize falhou: {e}")
        return message

    def _assess_complexity(self, message: str) -> str:
        """
        Avalia complexidade da mensagem.
        Retorna "simple" ou "complex".
        """
        msg = message.lower()

        # Indicadores de multi-step
        multi_indicators = [
            "e depois", "em seguida", "tambem", "alem disso",
            "compare", "monte uma planilha", "crie um relatorio",
            "primeiro", "segundo", "terceiro",
            "analise e", "pesquise e", "busque e",
            "faca tudo", "resolva tudo",
        ]

        if any(ind in msg for ind in multi_indicators):
            return "complex"

        # Conta verbos de acao distintos
        action_verbs = [
            "abra", "crie", "delete", "pesquise", "busque",
            "organize", "instale", "execute", "calcule",
            "compare", "copie", "mova", "renomeie",
        ]
        verb_count = sum(1 for v in action_verbs if v in msg)
        if verb_count >= 2:
            return "complex"

        return "simple"

    def get_status(self) -> Dict:
        """Retorna status do orchestrator para display."""
        active_tasks = self.task_queue.get_active_tasks()
        return {
            "active_tasks": len(active_tasks),
            "total_tasks": len(self.task_queue.tasks),
            "roles_loaded": len(self.roles),
            "playbooks_loaded": len(self.playbook_manager.playbooks),
            "security_mode": self.risk_policy.mode,
            "executor_ready": self.executor is not None,
            "brain_ready": self.brain is not None,
            "engine_ready": self.engine is not None,
        }

    def get_kanban_view(self) -> Dict:
        """Retorna visao Kanban das tarefas."""
        return self.task_queue.get_kanban_view()


# Singleton
_orchestrator = None


def get_orchestrator(executor=None, brain=None, engine=None) -> AgentOrchestrator:
    """Retorna singleton do orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator(executor, brain, engine)
    else:
        if executor:
            _orchestrator.set_executor(executor)
        if brain:
            _orchestrator.set_brain(brain)
        if engine:
            _orchestrator.set_engine(engine)
    return _orchestrator
