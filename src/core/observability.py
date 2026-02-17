"""
Observability - Sistema de logs estruturados e auditoria.
Registra TODOS os eventos em JSONL para replay, debug e auditoria.
Item 20 do plano arquitetural.
"""

import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional
from pathlib import Path
from src.utils.logger import get_logger

log = get_logger(__name__)

EVENTS_DIR = os.path.join(str(Path.home()), "Desktop", "WILTOP", "data", "logs", "events")


class EventLog:
    """Log estruturado em JSONL para replay e auditoria."""

    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or EVENTS_DIR
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_log_file(self, dt: date = None) -> str:
        """Retorna path do arquivo de log para a data."""
        dt = dt or date.today()
        return os.path.join(self.log_dir, f"{dt.isoformat()}.jsonl")

    def log_event(self, event_type: str, agent: str = "system",
                  data: Dict = None, task_id: str = None,
                  risk_level: str = "green", message: str = "") -> Dict:
        """
        Registra evento em JSONL com timestamp.

        Args:
            event_type: Tipo do evento (action_start, action_end, error, decision, etc.)
            agent: Qual agente executou (system, file_agent, browser_agent, etc.)
            data: Dados adicionais do evento
            task_id: ID da task relacionada (se houver)
            risk_level: Nivel de risco (green/yellow/red)
            message: Mensagem legivel
        """
        entry = {
            "ts": datetime.now().isoformat(),
            "type": event_type,
            "agent": agent,
            "task_id": task_id,
            "risk": risk_level,
            "message": message,
            "data": data or {},
        }

        try:
            filepath = self._get_log_file()
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            log.error(f"Erro ao registrar evento: {e}")

        return entry

    def get_recent(self, n: int = 50) -> List[Dict]:
        """Retorna N eventos mais recentes (hoje + ontem se necessario)."""
        events = []

        # Tenta hoje primeiro
        today_file = self._get_log_file()
        events.extend(self._read_log_file(today_file))

        # Se nao tem suficiente, tenta ontem
        if len(events) < n:
            from datetime import timedelta
            yesterday = date.today() - timedelta(days=1)
            yesterday_file = self._get_log_file(yesterday)
            events = self._read_log_file(yesterday_file) + events

        return events[-n:]

    def get_events_by_type(self, event_type: str, n: int = 50) -> List[Dict]:
        """Retorna eventos filtrados por tipo."""
        recent = self.get_recent(n * 3)  # Busca mais para ter margem
        filtered = [e for e in recent if e.get("type") == event_type]
        return filtered[-n:]

    def get_events_by_agent(self, agent: str, n: int = 50) -> List[Dict]:
        """Retorna eventos filtrados por agente."""
        recent = self.get_recent(n * 3)
        filtered = [e for e in recent if e.get("agent") == agent]
        return filtered[-n:]

    def replay_task(self, task_id: str) -> List[Dict]:
        """Retorna todos eventos de uma task para replay."""
        recent = self.get_recent(500)
        return [e for e in recent if e.get("task_id") == task_id]

    def get_error_events(self, n: int = 20) -> List[Dict]:
        """Retorna eventos de erro recentes."""
        return self.get_events_by_type("error", n)

    def get_stats(self) -> Dict:
        """Retorna estatisticas dos eventos de hoje."""
        events = self._read_log_file(self._get_log_file())
        if not events:
            return {"total": 0, "errors": 0, "actions": 0, "agents": {}}

        errors = sum(1 for e in events if e.get("type") == "error")
        actions = sum(1 for e in events if e.get("type") in ("action_start", "action_end"))

        agents = {}
        for e in events:
            agent = e.get("agent", "unknown")
            agents[agent] = agents.get(agent, 0) + 1

        risk_counts = {"green": 0, "yellow": 0, "red": 0}
        for e in events:
            risk = e.get("risk", "green")
            if risk in risk_counts:
                risk_counts[risk] += 1

        return {
            "total": len(events),
            "errors": errors,
            "actions": actions,
            "agents": agents,
            "risk_counts": risk_counts,
            "date": date.today().isoformat(),
        }

    def _read_log_file(self, filepath: str) -> List[Dict]:
        """Le arquivo JSONL e retorna lista de dicts."""
        events = []
        if not os.path.exists(filepath):
            return events
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            log.error(f"Erro ao ler log {filepath}: {e}")
        return events

    def clear_old_logs(self, keep_days: int = 30):
        """Remove logs mais antigos que keep_days."""
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=keep_days)
        try:
            for filename in os.listdir(self.log_dir):
                if not filename.endswith(".jsonl"):
                    continue
                try:
                    file_date = date.fromisoformat(filename.replace(".jsonl", ""))
                    if file_date < cutoff:
                        os.remove(os.path.join(self.log_dir, filename))
                        log.info(f"Log antigo removido: {filename}")
                except ValueError:
                    continue
        except Exception as e:
            log.error(f"Erro ao limpar logs antigos: {e}")


# Singleton
_event_log = None


def get_event_log() -> EventLog:
    """Retorna singleton do EventLog."""
    global _event_log
    if _event_log is None:
        _event_log = EventLog()
    return _event_log
