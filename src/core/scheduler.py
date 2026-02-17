"""
Scheduler / Heartbeat do William.
Permite agendar tarefas proativas - monitora e executa em background.
Similar ao 'heartbeat' do OpenClaw.
"""

import threading
import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Callable, Optional
from src.utils.logger import get_logger

log = get_logger(__name__)

TASKS_FILE = os.path.join(str(Path.home()), ".william", "scheduled_tasks.json")


class TaskScheduler:
    """Gerencia tarefas agendadas e proativas."""

    def __init__(self):
        self.tasks: List[Dict] = []
        self.running = False
        self._thread = None
        self._callbacks: List[Callable] = []
        self._load_tasks()

    def _load_tasks(self):
        """Carrega tarefas salvas."""
        try:
            if os.path.exists(TASKS_FILE):
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
                log.info(f"Carregadas {len(self.tasks)} tarefas agendadas")
        except:
            self.tasks = []

    def _save_tasks(self):
        """Salva tarefas."""
        try:
            os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Erro ao salvar tasks: {e}")

    def add_callback(self, callback: Callable):
        """Adiciona callback para quando tarefas disparam."""
        self._callbacks.append(callback)

    def add_task(self, name: str, command: str, interval_minutes: int = 0,
                 run_at: str = None, one_shot: bool = False) -> Dict:
        """
        Adiciona tarefa agendada.

        Args:
            name: Nome da tarefa
            command: Comando/mensagem a executar
            interval_minutes: Intervalo de repeticao em minutos (0 = nao repete)
            run_at: Horario para executar (formato HH:MM)
            one_shot: Se True, executa uma vez e remove
        """
        task = {
            "id": f"task_{int(time.time())}_{len(self.tasks)}",
            "name": name,
            "command": command,
            "interval_minutes": interval_minutes,
            "run_at": run_at,
            "one_shot": one_shot,
            "enabled": True,
            "last_run": None,
            "next_run": None,
            "created": datetime.now().isoformat(),
            "run_count": 0,
        }

        # Calcula proximo horario
        if run_at:
            h, m = map(int, run_at.split(":"))
            now = datetime.now()
            next_run = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            task["next_run"] = next_run.isoformat()
        elif interval_minutes > 0:
            task["next_run"] = (datetime.now() + timedelta(minutes=interval_minutes)).isoformat()

        self.tasks.append(task)
        self._save_tasks()
        log.info(f"Tarefa adicionada: {name}")
        return task

    def remove_task(self, task_id: str) -> bool:
        """Remove tarefa pelo ID."""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        if len(self.tasks) < before:
            self._save_tasks()
            return True
        return False

    def list_tasks(self) -> List[Dict]:
        """Lista todas as tarefas."""
        return self.tasks

    def start(self):
        """Inicia o scheduler em background."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        log.info("Scheduler iniciado")

    def stop(self):
        """Para o scheduler."""
        self.running = False
        log.info("Scheduler parado")

    def _loop(self):
        """Loop principal do scheduler."""
        while self.running:
            try:
                now = datetime.now()
                for task in self.tasks:
                    if not task.get("enabled"):
                        continue
                    if not task.get("next_run"):
                        continue

                    next_run = datetime.fromisoformat(task["next_run"])
                    if now >= next_run:
                        # EXECUTA!
                        log.info(f"Executando tarefa: {task['name']}")
                        self._fire_task(task)

                        # Atualiza
                        task["last_run"] = now.isoformat()
                        task["run_count"] = task.get("run_count", 0) + 1

                        if task.get("one_shot"):
                            task["enabled"] = False
                        elif task.get("interval_minutes", 0) > 0:
                            task["next_run"] = (now + timedelta(
                                minutes=task["interval_minutes"])).isoformat()
                        elif task.get("run_at"):
                            # Proximo dia
                            h, m = map(int, task["run_at"].split(":"))
                            next_run = now.replace(hour=h, minute=m, second=0)
                            next_run += timedelta(days=1)
                            task["next_run"] = next_run.isoformat()

                        self._save_tasks()
            except Exception as e:
                log.error(f"Erro no scheduler loop: {e}")

            time.sleep(30)  # Checa a cada 30 segundos

    def _fire_task(self, task: Dict):
        """Dispara tarefa - chama callbacks."""
        max_retries = task.get("max_retries", 2)
        retry_count = 0
        success = False

        while retry_count <= max_retries and not success:
            for cb in self._callbacks:
                try:
                    cb(task["command"], task["name"])
                    success = True
                except Exception as e:
                    retry_count += 1
                    log.error(f"Erro ao executar callback (tentativa {retry_count}): {e}")
                    if retry_count <= max_retries:
                        # Backoff exponencial
                        wait = min(2 ** retry_count, 30)
                        log.info(f"Retry em {wait}s...")
                        time.sleep(wait)
            if success:
                break

        # Log no observability
        try:
            from src.core.observability import get_event_log
            get_event_log().log_event(
                "scheduled_task_fired",
                agent="scheduler_agent",
                data={
                    "task": task.get("name"),
                    "command": task.get("command", "")[:100],
                    "success": success,
                    "retries": retry_count,
                }
            )
        except Exception:
            pass

    # ===== Metodos v4 =====

    def pause_task(self, task_id: str) -> bool:
        """Pausa uma tarefa especifica."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["enabled"] = False
                self._save_tasks()
                log.info(f"Tarefa pausada: {task['name']}")
                return True
        return False

    def resume_task(self, task_id: str) -> bool:
        """Retoma uma tarefa pausada."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["enabled"] = True
                # Recalcula next_run
                if task.get("interval_minutes", 0) > 0:
                    task["next_run"] = (datetime.now() + timedelta(
                        minutes=task["interval_minutes"])).isoformat()
                self._save_tasks()
                log.info(f"Tarefa retomada: {task['name']}")
                return True
        return False

    def get_task_by_name(self, name: str) -> Optional[Dict]:
        """Busca tarefa pelo nome."""
        for task in self.tasks:
            if task["name"].lower() == name.lower():
                return task
        return None

    def get_stats(self) -> Dict:
        """Estatisticas do scheduler."""
        total = len(self.tasks)
        active = sum(1 for t in self.tasks if t.get("enabled"))
        total_runs = sum(t.get("run_count", 0) for t in self.tasks)
        return {
            "total_tasks": total,
            "active": active,
            "paused": total - active,
            "total_runs": total_runs,
            "running": self.running,
        }


_scheduler = None

def get_scheduler() -> TaskScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler
