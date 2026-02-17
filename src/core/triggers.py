"""
Event Triggers - Gatilhos baseados em eventos do sistema.
Complementa o Scheduler com triggers reativos.
Item 8 do plano arquitetural.
"""

import os
import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from src.utils.logger import get_logger

log = get_logger(__name__)

# Tenta importar watchdog
_watchdog_available = False
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    _watchdog_available = True
except ImportError:
    log.debug("watchdog nao instalado - file triggers indisponiveis")


@dataclass
class TriggerRule:
    """Define uma regra de trigger."""
    id: str
    name: str
    trigger_type: str       # "file_created", "file_modified", "file_deleted",
                             # "process_started", "process_stopped", "download_complete"
    condition: Dict         # Condicoes (path, pattern, process_name, etc)
    action: str             # Comando a executar quando trigger dispara
    enabled: bool = True
    cooldown_seconds: int = 30  # Tempo minimo entre disparos
    last_triggered: float = 0.0
    trigger_count: int = 0


class _FileEventHandler(FileSystemEventHandler if _watchdog_available else object):
    """Handler de eventos do file system."""

    def __init__(self, trigger_manager):
        if _watchdog_available:
            super().__init__()
        self.manager = trigger_manager

    def on_created(self, event):
        if not event.is_directory:
            self.manager._fire_event("file_created", {
                "path": event.src_path,
                "filename": os.path.basename(event.src_path),
            })

    def on_modified(self, event):
        if not event.is_directory:
            self.manager._fire_event("file_modified", {
                "path": event.src_path,
                "filename": os.path.basename(event.src_path),
            })

    def on_deleted(self, event):
        if not event.is_directory:
            self.manager._fire_event("file_deleted", {
                "path": event.src_path,
                "filename": os.path.basename(event.src_path),
            })


class TriggerManager:
    """
    Gerencia triggers baseados em eventos.
    Suporta: file watchers, process monitors.
    """

    def __init__(self):
        self.rules: Dict[str, TriggerRule] = {}
        self.callbacks: List[Callable] = []  # Callbacks quando trigger dispara
        self._observers: Dict[str, object] = {}  # Watchdog observers
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None

    def add_rule(self, name: str, trigger_type: str, condition: Dict,
                 action: str, cooldown: int = 30) -> TriggerRule:
        """
        Adiciona regra de trigger.

        Args:
            name: Nome descritivo
            trigger_type: Tipo de evento
            condition: Condicoes do trigger
            action: Comando a executar
            cooldown: Segundos entre disparos

        Returns:
            TriggerRule criada
        """
        rule_id = f"trigger_{int(time.time())}_{len(self.rules)}"
        rule = TriggerRule(
            id=rule_id,
            name=name,
            trigger_type=trigger_type,
            condition=condition,
            action=action,
            cooldown_seconds=cooldown,
        )
        self.rules[rule_id] = rule
        log.info(f"Trigger adicionado: {name} ({trigger_type})")

        # Se e file trigger, inicia watcher
        if trigger_type.startswith("file_") and _watchdog_available:
            watch_path = condition.get("path", "")
            if watch_path and os.path.exists(watch_path):
                self._start_file_watcher(watch_path)

        return rule

    def remove_rule(self, rule_id: str) -> bool:
        """Remove regra de trigger."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            log.info(f"Trigger removido: {rule_id}")
            return True
        return False

    def on_trigger(self, callback: Callable):
        """Registra callback para quando triggers disparam."""
        self.callbacks.append(callback)

    def _fire_event(self, event_type: str, event_data: Dict):
        """Dispara evento e verifica regras."""
        for rule in self.rules.values():
            if not rule.enabled or rule.trigger_type != event_type:
                continue

            # Verifica cooldown
            now = time.time()
            if now - rule.last_triggered < rule.cooldown_seconds:
                continue

            # Verifica condicoes
            if self._check_condition(rule, event_data):
                rule.last_triggered = now
                rule.trigger_count += 1
                log.info(f"Trigger disparado: {rule.name} ({event_type})")

                # Notifica callbacks
                for cb in self.callbacks:
                    try:
                        cb(rule, event_data)
                    except Exception as e:
                        log.error(f"Erro em callback de trigger: {e}")

                # Log no observability
                try:
                    from src.core.observability import get_event_log
                    get_event_log().log_event(
                        "trigger_fired",
                        data={
                            "rule": rule.name,
                            "type": event_type,
                            "action": rule.action[:100],
                            "count": rule.trigger_count,
                        }
                    )
                except Exception:
                    pass

    def _check_condition(self, rule: TriggerRule, event_data: Dict) -> bool:
        """Verifica se condicoes de uma regra sao satisfeitas."""
        condition = rule.condition

        # File triggers: verifica pattern/extensao
        if rule.trigger_type.startswith("file_"):
            filename = event_data.get("filename", "")
            filepath = event_data.get("path", "")

            # Pattern de nome
            pattern = condition.get("pattern", "")
            if pattern and pattern not in filename.lower():
                return False

            # Extensao
            extensions = condition.get("extensions", [])
            if extensions:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in extensions and ext.lstrip(".") not in extensions:
                    return False

            # Path deve conter
            path_contains = condition.get("path_contains", "")
            if path_contains and path_contains.lower() not in filepath.lower():
                return False

            return True

        # Process triggers
        if rule.trigger_type.startswith("process_"):
            process_name = event_data.get("process_name", "")
            target = condition.get("process_name", "")
            if target and target.lower() not in process_name.lower():
                return False
            return True

        return True

    def _start_file_watcher(self, path: str):
        """Inicia file watcher para um diretorio."""
        if not _watchdog_available:
            return

        if path in self._observers:
            return  # Ja tem watcher

        try:
            handler = _FileEventHandler(self)
            observer = Observer()
            observer.schedule(handler, path, recursive=False)
            observer.start()
            self._observers[path] = observer
            log.info(f"File watcher iniciado: {path}")
        except Exception as e:
            log.error(f"Erro ao iniciar file watcher: {e}")

    def start(self):
        """Inicia monitoramento de triggers."""
        if self._running:
            return

        self._running = True
        log.info("TriggerManager iniciado")

    def stop(self):
        """Para monitoramento."""
        self._running = False

        # Para file watchers
        for path, observer in self._observers.items():
            try:
                observer.stop()
                observer.join(timeout=5)
            except Exception:
                pass
        self._observers.clear()

        log.info("TriggerManager parado")

    def get_active_rules(self) -> List[Dict]:
        """Retorna regras ativas."""
        return [
            {
                "id": r.id,
                "name": r.name,
                "type": r.trigger_type,
                "action": r.action,
                "enabled": r.enabled,
                "trigger_count": r.trigger_count,
            }
            for r in self.rules.values()
            if r.enabled
        ]

    def get_stats(self) -> Dict:
        """Estatisticas dos triggers."""
        return {
            "total_rules": len(self.rules),
            "active_rules": sum(1 for r in self.rules.values() if r.enabled),
            "total_fired": sum(r.trigger_count for r in self.rules.values()),
            "watchers": len(self._observers),
            "watchdog_available": _watchdog_available,
            "running": self._running,
        }


# Singleton
_trigger_manager = None


def get_trigger_manager() -> TriggerManager:
    """Retorna singleton do TriggerManager."""
    global _trigger_manager
    if _trigger_manager is None:
        _trigger_manager = TriggerManager()
    return _trigger_manager
