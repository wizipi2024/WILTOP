"""
William AI - Background Service (Always-on).
Roda William na bandeja do sistema com scheduler e triggers ativos.
Para rodar: python run_service.py
"""

import sys
import os
import time

# Adiciona raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import setup_logging, get_logger
from config.settings import settings

# Setup logging
setup_logging(log_file=settings.LOG_FILE, log_level=settings.LOG_LEVEL)
log = get_logger("service")


def main():
    """Entry point do servico background."""
    log.info("Iniciando William AI Service...")
    print("=" * 50)
    print("  WILLIAM AI - Background Service")
    print("=" * 50)

    # Tenta iniciar tray service
    try:
        from src.core.tray_service import get_tray_service

        service = get_tray_service()
        if service.start():
            print("[OK] System tray ativo - William na bandeja do sistema")
            print("     Clique no icone para abrir a GUI")
            print("     Scheduler e Triggers rodando em background")
            print("     Ctrl+C para encerrar")
            print("=" * 50)

            # Mantém processo rodando
            try:
                while service.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[--] Encerrando William Service...")
                service.stop()
                print("[OK] Servico encerrado.")
        else:
            print("[!!] System tray nao disponivel")
            print("     Instale: pip install pystray Pillow")
            print("")
            print("     Alternativa: rodando scheduler em modo console...")

            # Modo console (sem tray)
            _run_console_mode()

    except ImportError as e:
        print(f"[ERRO] Dependencia faltando: {e}")
        print("       Instale: pip install pystray Pillow")
        _run_console_mode()


def _run_console_mode():
    """Modo console fallback (sem system tray)."""
    print("=" * 50)
    print("  Modo Console - Scheduler ativo")
    print("  Ctrl+C para sair")
    print("=" * 50)

    try:
        from src.core.scheduler import get_scheduler
        scheduler = get_scheduler()
        scheduler.start()
        print("[OK] Scheduler ativo")

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[--] Encerrando...")
        try:
            scheduler.stop()
        except Exception:
            pass
    except Exception as e:
        print(f"[ERRO] {e}")


if __name__ == "__main__":
    main()
