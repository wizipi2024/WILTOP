"""
System Tray Service - William rodando 24/7 na bandeja do sistema.
Inicia scheduler e triggers em background, com menu de acoes rapidas.
Item 1 do plano arquitetural.
"""

import os
import sys
import threading
import time
from pathlib import Path
from typing import Optional, Callable
from src.utils.logger import get_logger

log = get_logger(__name__)

# Tenta importar pystray
_pystray_available = False
try:
    import pystray
    from PIL import Image
    _pystray_available = True
except ImportError:
    log.info("pystray/PIL nao instalados - system tray indisponivel")


class WilliamTrayService:
    """
    Servico de system tray que roda William 24/7.
    - Icone na bandeja
    - Menu: Abrir GUI, Status, Skills, Sair
    - Roda scheduler e triggers em background
    """

    def __init__(self, on_open_gui: Optional[Callable] = None):
        """
        Args:
            on_open_gui: Callback para abrir a GUI principal
        """
        self.on_open_gui = on_open_gui
        self._icon = None
        self._running = False
        self._scheduler = None
        self._trigger_manager = None

    def _create_icon_image(self):
        """Cria imagem do icone do tray."""
        # Tenta carregar icone customizado
        icon_path = os.path.join(
            str(Path(__file__).resolve().parent.parent.parent),
            "assets", "william_icon.png"
        )

        if os.path.exists(icon_path):
            try:
                return Image.open(icon_path)
            except Exception:
                pass

        # Fallback: gera icone simples programaticamente
        try:
            img = Image.new('RGBA', (64, 64), (10, 10, 26, 255))
            # Desenha um W simples
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            # Fundo
            draw.rectangle([4, 4, 60, 60], fill=(13, 17, 23, 255),
                          outline=(0, 245, 255, 255), width=2)
            # W
            draw.text((16, 15), "W", fill=(0, 245, 255, 255))
            return img
        except Exception:
            # Icone minimo
            return Image.new('RGBA', (64, 64), (0, 136, 255, 255))

    def _build_menu(self):
        """Constroi menu do tray."""
        if not _pystray_available:
            return None

        return pystray.Menu(
            pystray.MenuItem(
                "Abrir William",
                self._action_open_gui,
                default=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Status", self._action_status),
            pystray.MenuItem("Skills", self._action_list_skills),
            pystray.MenuItem("Memoria", self._action_memory_stats),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Pausar Scheduler", self._action_pause_scheduler),
            pystray.MenuItem("Retomar Scheduler", self._action_resume_scheduler),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair", self._action_quit),
        )

    def start(self):
        """Inicia servico de tray."""
        if not _pystray_available:
            log.warning("pystray nao disponivel - tray service nao pode iniciar")
            return False

        if self._running:
            return True

        self._running = True

        # Inicia scheduler
        try:
            from src.core.scheduler import get_scheduler
            self._scheduler = get_scheduler()
            self._scheduler.start()
            log.info("Scheduler iniciado via tray service")
        except Exception as e:
            log.warning(f"Scheduler nao disponivel: {e}")

        # Inicia triggers
        try:
            from src.core.triggers import get_trigger_manager
            self._trigger_manager = get_trigger_manager()
            self._trigger_manager.start()
            log.info("TriggerManager iniciado via tray service")
        except Exception as e:
            log.warning(f"TriggerManager nao disponivel: {e}")

        # Cria icone
        try:
            image = self._create_icon_image()
            menu = self._build_menu()

            self._icon = pystray.Icon(
                "william_ai",
                image,
                "William AI - Online",
                menu
            )

            # Roda em thread separada
            thread = threading.Thread(target=self._icon.run, daemon=True)
            thread.start()

            log.info("System tray iniciado - William AI online")
            return True

        except Exception as e:
            log.error(f"Erro ao criar system tray: {e}")
            self._running = False
            return False

    def stop(self):
        """Para servico de tray."""
        self._running = False

        if self._scheduler:
            try:
                self._scheduler.stop()
            except Exception:
                pass

        if self._trigger_manager:
            try:
                self._trigger_manager.stop()
            except Exception:
                pass

        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

        log.info("Tray service parado")

    # ===== Acoes do Menu =====

    def _action_open_gui(self, icon=None, item=None):
        """Abre GUI principal."""
        if self.on_open_gui:
            self.on_open_gui()
        else:
            # Tenta abrir GUI diretamente
            try:
                import subprocess
                william_bat = os.path.join(
                    str(Path(__file__).resolve().parent.parent.parent),
                    "WILLIAM.bat"
                )
                if os.path.exists(william_bat):
                    subprocess.Popen(william_bat, shell=True)
                else:
                    log.warning("WILLIAM.bat nao encontrado")
            except Exception as e:
                log.error(f"Erro ao abrir GUI: {e}")

    def _action_status(self, icon=None, item=None):
        """Mostra status."""
        try:
            from src.core.task_queue import get_task_queue
            tq = get_task_queue()
            stats = tq.get_stats()

            scheduler_status = "Ativo" if self._scheduler else "Inativo"
            trigger_status = "Ativo" if self._trigger_manager else "Inativo"

            status = (
                f"William AI - Status\n"
                f"Scheduler: {scheduler_status}\n"
                f"Triggers: {trigger_status}\n"
                f"Tasks: {stats['total']} (Ativos: {stats['active']})"
            )
            log.info(status)

            # Notificacao do sistema (se disponivel)
            if self._icon:
                self._icon.notify(status, "William AI")

        except Exception as e:
            log.error(f"Erro ao obter status: {e}")

    def _action_list_skills(self, icon=None, item=None):
        """Lista skills."""
        try:
            from src.skills.skill_manager import get_skill_manager
            sm = get_skill_manager()
            skills = sm.list_skills()
            names = [f"{s['icon']} {s['display_name']}" for s in skills]
            text = f"Skills ({len(skills)}):\n" + "\n".join(names)
            log.info(text)
            if self._icon:
                self._icon.notify(text[:200], "William Skills")
        except Exception as e:
            log.error(f"Erro ao listar skills: {e}")

    def _action_memory_stats(self, icon=None, item=None):
        """Mostra stats da memoria."""
        try:
            from src.core.memory import get_memory
            mem = get_memory()
            info = mem.get_level_info()
            text = f"Nivel {info['nivel']} - {info['titulo']}\nXP: {info['xp']}"
            if self._icon:
                self._icon.notify(text, "William Memoria")
        except Exception as e:
            log.error(f"Erro: {e}")

    def _action_pause_scheduler(self, icon=None, item=None):
        """Pausa scheduler."""
        if self._scheduler:
            self._scheduler.stop()
            log.info("Scheduler pausado")
            if self._icon:
                self._icon.notify("Scheduler pausado", "William")

    def _action_resume_scheduler(self, icon=None, item=None):
        """Retoma scheduler."""
        if self._scheduler:
            self._scheduler.start()
            log.info("Scheduler retomado")
            if self._icon:
                self._icon.notify("Scheduler retomado", "William")

    def _action_quit(self, icon=None, item=None):
        """Sai do servico."""
        self.stop()
        os._exit(0)

    @property
    def is_running(self) -> bool:
        return self._running


# Singleton
_tray_service = None


def get_tray_service(on_open_gui=None) -> WilliamTrayService:
    """Retorna singleton do tray service."""
    global _tray_service
    if _tray_service is None:
        _tray_service = WilliamTrayService(on_open_gui)
    return _tray_service
