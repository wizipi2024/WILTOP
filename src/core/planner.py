"""
Task Planner - Quebra tarefas complexas em subtasks.
Usa LLM para decompor pedidos multi-step em planos executaveis.
Item 3 do plano arquitetural.
"""

import json
import re
from typing import Dict, List, Optional
from src.utils.logger import get_logger

log = get_logger(__name__)


class TaskStep:
    """Um passo de um plano de execucao."""

    def __init__(self, order: int, description: str, agent: str = "general_agent",
                 action_type: str = "ai_execute", params: Dict = None,
                 depends_on: List[int] = None):
        self.order = order
        self.description = description
        self.agent = agent
        self.action_type = action_type
        self.params = params or {}
        self.depends_on = depends_on or []
        self.status = "pending"  # pending, in_progress, done, failed
        self.result = None

    def to_dict(self) -> Dict:
        return {
            "order": self.order,
            "description": self.description,
            "agent": self.agent,
            "action_type": self.action_type,
            "params": self.params,
            "depends_on": self.depends_on,
            "status": self.status,
            "result": self.result,
        }


class TaskPlan:
    """Plano completo de execucao."""

    def __init__(self, goal: str, steps: List[TaskStep] = None):
        self.goal = goal
        self.steps = steps or []
        self.status = "pending"

    def add_step(self, step: TaskStep):
        self.steps.append(step)

    def get_next_step(self) -> Optional[TaskStep]:
        """Retorna proximo step pendente cujas dependencias ja completaram."""
        for step in self.steps:
            if step.status != "pending":
                continue
            # Verifica dependencias
            deps_ok = all(
                self.steps[d].status == "done"
                for d in step.depends_on
                if d < len(self.steps)
            )
            if deps_ok:
                return step
        return None

    def is_complete(self) -> bool:
        """Se todos os steps estao done."""
        return all(s.status == "done" for s in self.steps)

    def has_failed(self) -> bool:
        """Se algum step falhou."""
        return any(s.status == "failed" for s in self.steps)

    def get_progress(self) -> Dict:
        """Progresso do plano."""
        total = len(self.steps)
        done = sum(1 for s in self.steps if s.status == "done")
        failed = sum(1 for s in self.steps if s.status == "failed")
        return {
            "total": total,
            "done": done,
            "failed": failed,
            "progress_pct": (done / total * 100) if total > 0 else 0,
        }

    def to_dict(self) -> Dict:
        return {
            "goal": self.goal,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "progress": self.get_progress(),
        }


class TaskPlanner:
    """
    Planner que quebra tarefas complexas em steps.
    Pode usar LLM ou heuristicas.
    """

    def __init__(self, engine=None):
        """
        Args:
            engine: AIEngine para usar LLM na decomposicao
        """
        self.engine = engine

    def set_engine(self, engine):
        """Define engine (pode ser setado depois)."""
        self.engine = engine

    def create_plan(self, task: str, context: Dict = None) -> TaskPlan:
        """
        Cria plano de execucao para uma tarefa.
        Tenta LLM primeiro, senao usa heuristicas.

        Args:
            task: Descricao da tarefa
            context: Contexto adicional

        Returns:
            TaskPlan com steps
        """
        # Tenta com LLM
        if self.engine:
            try:
                plan = self._create_plan_llm(task, context)
                if plan and plan.steps:
                    return plan
            except Exception as e:
                log.warning(f"Planner LLM falhou: {e}")

        # Fallback: heuristicas
        return self._create_plan_heuristic(task)

    def _create_plan_llm(self, task: str, context: Dict = None) -> Optional[TaskPlan]:
        """Cria plano usando LLM."""
        prompt = f"""Voce e um planejador de tarefas. Decomponha a seguinte tarefa em passos simples e sequenciais.

Tarefa: {task}

Responda APENAS com JSON no formato:
{{
  "steps": [
    {{"order": 1, "description": "descricao do passo", "agent": "tipo_agente", "action_type": "tipo_acao"}},
    ...
  ]
}}

Tipos de agente validos: file_agent, browser_agent, system_agent, general_agent
Tipos de acao validos: create_file, create_folder, search, web_search, open_site, system_info, ai_execute, ai_generate, calculate

Mantenha de 2 a 6 passos. Seja conciso e especifico."""

        try:
            # Usa chat_with_fallback se disponivel
            if hasattr(self.engine, 'chat_with_fallback'):
                response = self.engine.chat_with_fallback(prompt)
            else:
                response = self.engine.chat(prompt)

            # Extrai JSON da resposta
            plan_data = self._extract_json(response)
            if not plan_data or "steps" not in plan_data:
                return None

            plan = TaskPlan(goal=task)
            for step_data in plan_data["steps"]:
                step = TaskStep(
                    order=step_data.get("order", len(plan.steps) + 1),
                    description=step_data.get("description", ""),
                    agent=step_data.get("agent", "general_agent"),
                    action_type=step_data.get("action_type", "ai_execute"),
                    params=step_data.get("params", {}),
                    depends_on=step_data.get("depends_on", []),
                )
                plan.add_step(step)

            log.info(f"Plano LLM criado: {len(plan.steps)} steps")
            return plan

        except Exception as e:
            log.warning(f"Erro no planner LLM: {e}")
            return None

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extrai JSON de uma resposta de texto."""
        # Procura bloco JSON
        patterns = [
            r'```json\s*(.*?)```',
            r'```\s*(.*?)```',
            r'(\{[\s\S]*\})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue
        return None

    def _create_plan_heuristic(self, task: str) -> TaskPlan:
        """Cria plano usando heuristicas simples."""
        task_lower = task.lower()
        plan = TaskPlan(goal=task)

        # Divide por conectores
        parts = re.split(
            r'\s*(?:e depois|em seguida|alem disso|tambem|e tambem|,\s*depois|;\s*)\s*',
            task,
            flags=re.IGNORECASE
        )

        if len(parts) > 1:
            # Multi-step detectado
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                agent = self._guess_agent(part)
                action = self._guess_action(part)
                plan.add_step(TaskStep(
                    order=i + 1,
                    description=part,
                    agent=agent,
                    action_type=action,
                    depends_on=[i - 1] if i > 0 else [],
                ))
        else:
            # Single step mas marcado como complexo
            # Tenta decomposicao por verbos
            verbs = re.findall(
                r'\b(crie|abra|delete|pesquise|busque|organize|instale|execute|'
                r'calcule|compare|copie|mova|renomeie|liste|mostre)\b',
                task_lower
            )

            if len(verbs) >= 2:
                # Multiplos verbos = multiplos steps
                # Split simples por verbo
                current = task
                for i, verb in enumerate(verbs):
                    idx = current.lower().find(verb)
                    if idx > 0 and i > 0:
                        part = current[:idx].strip().rstrip(",;.")
                        if part:
                            plan.add_step(TaskStep(
                                order=i,
                                description=part,
                                agent=self._guess_agent(part),
                                action_type=self._guess_action(part),
                                depends_on=[i - 1] if i > 0 else [],
                            ))
                        current = current[idx:]

                # Ultimo pedaco
                if current.strip():
                    plan.add_step(TaskStep(
                        order=len(plan.steps) + 1,
                        description=current.strip(),
                        agent=self._guess_agent(current),
                        action_type=self._guess_action(current),
                        depends_on=[len(plan.steps) - 1] if plan.steps else [],
                    ))
            else:
                # Nao conseguiu decompor - single step
                plan.add_step(TaskStep(
                    order=1,
                    description=task,
                    agent=self._guess_agent(task),
                    action_type=self._guess_action(task),
                ))

        if not plan.steps:
            plan.add_step(TaskStep(
                order=1,
                description=task,
                agent="general_agent",
                action_type="ai_execute",
            ))

        log.info(f"Plano heuristico criado: {len(plan.steps)} steps")
        return plan

    def _guess_agent(self, text: str) -> str:
        """Adivinha melhor agente para o texto."""
        text_lower = text.lower()

        file_words = ["arquivo", "pasta", "criar", "deletar", "mover", "copiar", "organizar"]
        web_words = ["pesquise", "busque", "site", "google", "web", "navegue", "pagina"]
        system_words = ["sistema", "cpu", "ram", "disco", "processo", "bateria", "wifi"]

        if any(w in text_lower for w in file_words):
            return "file_agent"
        if any(w in text_lower for w in web_words):
            return "browser_agent"
        if any(w in text_lower for w in system_words):
            return "system_agent"
        return "general_agent"

    def _guess_action(self, text: str) -> str:
        """Adivinha tipo de acao para o texto."""
        text_lower = text.lower()

        action_keywords = {
            "create_file": ["crie arquivo", "criar arquivo"],
            "create_folder": ["crie pasta", "criar pasta", "crie uma pasta"],
            "web_search": ["pesquise", "busque", "procure"],
            "open_site": ["abra o site", "abra o", "navegue"],
            "system_info": ["info do sistema", "cpu", "ram", "disco"],
            "calculate": ["calcule", "quanto e", "some"],
        }

        for action, keywords in action_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return action

        return "ai_execute"

    def execute_plan(self, plan: TaskPlan, executor=None, brain=None) -> Dict:
        """
        Executa plano step-by-step.

        Args:
            plan: Plano a executar
            executor: SmartExecutorV2
            brain: AIBrain

        Returns:
            Dict com resultado da execucao
        """
        results = []
        plan.status = "in_progress"

        while True:
            step = plan.get_next_step()
            if step is None:
                break

            step.status = "in_progress"
            log.info(f"Executando step {step.order}: {step.description}")

            try:
                # Tenta executar via executor
                if executor:
                    result = executor.process_message(step.description)
                    if result.get("executed"):
                        step.status = "done"
                        step.result = result
                        results.append({
                            "step": step.order,
                            "description": step.description,
                            "success": True,
                            "actions": [a.get("type") for a in result.get("actions", [])],
                        })
                        continue

                # Fallback para brain
                if brain:
                    response = brain.process(step.description)
                    step.status = "done"
                    step.result = {"response": response}
                    results.append({
                        "step": step.order,
                        "description": step.description,
                        "success": True,
                        "response": response[:200] if response else "",
                    })
                    continue

                # Nenhum executor disponivel
                step.status = "failed"
                step.result = {"error": "Nenhum executor disponivel"}
                results.append({
                    "step": step.order,
                    "description": step.description,
                    "success": False,
                    "error": "Sem executor",
                })

            except Exception as e:
                step.status = "failed"
                step.result = {"error": str(e)}
                results.append({
                    "step": step.order,
                    "description": step.description,
                    "success": False,
                    "error": str(e),
                })

        plan.status = "done" if plan.is_complete() else "failed"

        return {
            "goal": plan.goal,
            "total_steps": len(plan.steps),
            "completed": sum(1 for s in plan.steps if s.status == "done"),
            "failed": sum(1 for s in plan.steps if s.status == "failed"),
            "results": results,
            "success": plan.is_complete(),
        }


# Singleton
_planner = None


def get_planner(engine=None) -> TaskPlanner:
    """Retorna singleton do TaskPlanner."""
    global _planner
    if _planner is None:
        _planner = TaskPlanner(engine)
    elif engine:
        _planner.set_engine(engine)
    return _planner
