"""
Task Queue - Fila de tarefas com state machine.
Gerencia tarefas multi-step com estados e persistencia.
Item 15 do plano arquitetural.
"""

import json
import os
import time
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from src.utils.logger import get_logger

log = get_logger(__name__)

TASKS_FILE = os.path.join(
    str(Path.home()), "Desktop", "WILTOP", "data", "tasks", "task_queue.json"
)


class TaskState(Enum):
    """Estados possiveis de uma tarefa."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_CONFIRM = "waiting_confirm"  # Acao red precisa aprovacao
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Transicoes validas de estado
VALID_TRANSITIONS = {
    TaskState.PENDING: {TaskState.IN_PROGRESS, TaskState.CANCELLED},
    TaskState.IN_PROGRESS: {TaskState.DONE, TaskState.FAILED, TaskState.WAITING_CONFIRM, TaskState.CANCELLED},
    TaskState.WAITING_CONFIRM: {TaskState.IN_PROGRESS, TaskState.CANCELLED},
    TaskState.DONE: set(),      # Terminal
    TaskState.FAILED: {TaskState.PENDING},  # Retry
    TaskState.CANCELLED: set(),  # Terminal
}


@dataclass
class Task:
    """Representa uma tarefa na fila."""

    id: str
    title: str
    description: str
    state: str = "pending"          # TaskState value
    assigned_agent: str = "general_agent"
    command: str = ""               # Mensagem/comando a executar
    parent_id: Optional[str] = None  # Se e subtask
    order: int = 0                  # Ordem dentro do parent
    result_message: str = ""
    result_success: Optional[bool] = None
    result_proof: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    retry_count: int = 0
    max_retries: int = 2

    def to_dict(self) -> Dict:
        """Serializa para dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Cria de dict."""
        # Remove campos extras que nao existem no dataclass
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    @property
    def is_terminal(self) -> bool:
        """Se esta em estado final (done/failed/cancelled)."""
        return self.state in ("done", "failed", "cancelled")

    @property
    def is_active(self) -> bool:
        """Se esta ativo (pending ou in_progress)."""
        return self.state in ("pending", "in_progress", "waiting_confirm")


class TaskQueue:
    """Fila de tarefas com estado. Persiste em JSON."""

    def __init__(self, tasks_file: str = None):
        self.tasks_file = tasks_file or TASKS_FILE
        self.tasks: Dict[str, Task] = {}
        self._load()

    def _load(self):
        """Carrega tarefas do arquivo."""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for task_data in data:
                    task = Task.from_dict(task_data)
                    self.tasks[task.id] = task
                log.info(f"TaskQueue: {len(self.tasks)} tarefas carregadas")
        except Exception as e:
            log.error(f"Erro ao carregar task queue: {e}")
            self.tasks = {}

    def _save(self):
        """Salva tarefas no arquivo."""
        try:
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            data = [task.to_dict() for task in self.tasks.values()]
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Erro ao salvar task queue: {e}")

    def create_task(self, title: str, description: str = "",
                    command: str = "", agent: str = "general_agent",
                    parent_id: str = None, order: int = 0) -> Task:
        """Cria nova tarefa."""
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        task = Task(
            id=task_id,
            title=title,
            description=description,
            command=command,
            assigned_agent=agent,
            parent_id=parent_id,
            order=order,
        )
        self.tasks[task_id] = task
        self._save()

        # Log no observability
        try:
            from src.core.observability import get_event_log
            get_event_log().log_event(
                "task_created", agent=agent,
                data={"task_id": task_id, "title": title},
                task_id=task_id
            )
        except Exception:
            pass

        log.info(f"Task criada: {task_id} - {title}")
        return task

    def update_state(self, task_id: str, new_state: str,
                     result_message: str = "", result_success: bool = None,
                     result_proof: str = None) -> bool:
        """
        Transicao de estado com validacao.
        Retorna True se transicao valida, False se invalida.
        """
        task = self.tasks.get(task_id)
        if not task:
            log.error(f"Task nao encontrada: {task_id}")
            return False

        # Valida transicao
        current = TaskState(task.state)
        target = TaskState(new_state)
        if target not in VALID_TRANSITIONS.get(current, set()):
            log.warning(f"Transicao invalida: {current.value} -> {target.value} para {task_id}")
            return False

        task.state = new_state
        task.updated_at = datetime.now().isoformat()
        if result_message:
            task.result_message = result_message
        if result_success is not None:
            task.result_success = result_success
        if result_proof:
            task.result_proof = result_proof

        self._save()

        # Log
        try:
            from src.core.observability import get_event_log
            get_event_log().log_event(
                "task_state_change", agent=task.assigned_agent,
                data={"from": current.value, "to": new_state, "task_id": task_id},
                task_id=task_id
            )
        except Exception:
            pass

        log.info(f"Task {task_id}: {current.value} -> {new_state}")
        return True

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retorna task por ID."""
        return self.tasks.get(task_id)

    def get_subtasks(self, parent_id: str) -> List[Task]:
        """Retorna subtasks de uma task, ordenadas."""
        subtasks = [t for t in self.tasks.values() if t.parent_id == parent_id]
        return sorted(subtasks, key=lambda t: t.order)

    def get_active_tasks(self) -> List[Task]:
        """Retorna tasks ativas (nao terminais)."""
        return [t for t in self.tasks.values() if t.is_active]

    def get_recent_tasks(self, n: int = 20) -> List[Task]:
        """Retorna N tasks mais recentes."""
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.created_at,
            reverse=True
        )
        return sorted_tasks[:n]

    def get_kanban_view(self) -> Dict[str, List[Dict]]:
        """Retorna tasks agrupadas por estado (para Kanban)."""
        kanban = {
            "pending": [],
            "in_progress": [],
            "waiting_confirm": [],
            "done": [],
            "failed": [],
        }

        for task in self.tasks.values():
            state = task.state
            if state in kanban:
                kanban[state].append(task.to_dict())

        # Ordena cada coluna por updated_at (mais recente primeiro)
        for state in kanban:
            kanban[state].sort(key=lambda t: t.get("updated_at", ""), reverse=True)
            # Limita a 20 por coluna
            kanban[state] = kanban[state][:20]

        return kanban

    def get_stats(self) -> Dict:
        """Estatisticas da fila."""
        total = len(self.tasks)
        states = {}
        for task in self.tasks.values():
            states[task.state] = states.get(task.state, 0) + 1

        return {
            "total": total,
            "active": len(self.get_active_tasks()),
            "states": states,
        }

    def cleanup_old_tasks(self, keep_days: int = 7):
        """Remove tasks terminais mais antigas que keep_days."""
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=keep_days)).isoformat()
        to_remove = [
            tid for tid, task in self.tasks.items()
            if task.is_terminal and task.updated_at < cutoff
        ]
        for tid in to_remove:
            del self.tasks[tid]
        if to_remove:
            self._save()
            log.info(f"Removidas {len(to_remove)} tasks antigas")

    def retry_task(self, task_id: str) -> bool:
        """Tenta re-executar uma task falha."""
        task = self.tasks.get(task_id)
        if not task or task.state != "failed":
            return False
        if task.retry_count >= task.max_retries:
            log.warning(f"Task {task_id} excedeu max retries ({task.max_retries})")
            return False
        task.retry_count += 1
        return self.update_state(task_id, "pending")


# Singleton
_task_queue = None


def get_task_queue() -> TaskQueue:
    """Retorna singleton da TaskQueue."""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
    return _task_queue
