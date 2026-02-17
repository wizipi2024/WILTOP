"""
Bot Telegram do William - Controle remoto do PC.
Envia comandos pelo Telegram e o William executa no PC.
"""

import asyncio
import threading
from pathlib import Path
from typing import Optional

from src.core.smart_executor_v2 import SmartExecutorV2
from src.utils.logger import get_logger

log = get_logger(__name__)


class WilliamTelegramBot:
    """Bot Telegram para controle remoto."""

    def __init__(self, token: str, allowed_user_id: Optional[int] = None):
        """
        Args:
            token: Token do bot Telegram (@BotFather)
            allowed_user_id: ID do Telegram do dono (seguranca)
        """
        self.token = token
        self.allowed_user_id = allowed_user_id
        self.executor = SmartExecutorV2()
        self.running = False
        self._app = None
        log.info("TelegramBot inicializado")

    async def _start_handler(self, update, context):
        """Handler /start."""
        user = update.effective_user
        user_id = user.id

        if self.allowed_user_id and user_id != self.allowed_user_id:
            await update.message.reply_text(
                f"[BLOQUEADO] Voce nao esta autorizado.\nSeu ID: {user_id}\n"
                f"Configure este ID no .env como TELEGRAM_ALLOWED_USER_ID"
            )
            return

        await update.message.reply_text(
            "*** WILLIAM - Controle Remoto ***\n\n"
            f"Seu Telegram ID: {user_id}\n\n"
            "Comandos disponiveis:\n"
            "- Abra o [programa]\n"
            "- Feche o [programa]\n"
            "- Crie um arquivo [nome]\n"
            "- Liste arquivos da pasta [pasta]\n"
            "- Mostre uso de memoria\n"
            "- cmd: [comando]\n"
            "- /screenshot - Captura de tela\n"
            "- /status - Status do sistema\n"
            "- /ip - Mostra IP\n\n"
            "Envie qualquer comando!"
        )

    async def _status_handler(self, update, context):
        """Handler /status."""
        if not self._check_auth(update):
            return
        result = self.executor.process_message("mostre uso de memoria")
        if result["executed"]:
            text = "\n".join(a.get("message", "") for a in result["actions"])
            await update.message.reply_text(text)
        else:
            await update.message.reply_text("Erro ao obter status")

    async def _ip_handler(self, update, context):
        """Handler /ip."""
        if not self._check_auth(update):
            return
        result = self.executor.process_message("cmd: ipconfig")
        if result["executed"]:
            text = "\n".join(a.get("message", "")[:500] for a in result["actions"])
            await update.message.reply_text(text[:4000])

    async def _screenshot_handler(self, update, context):
        """Handler /screenshot - captura de tela."""
        if not self._check_auth(update):
            return
        try:
            import pyautogui
            screenshot_path = Path(__file__).parent.parent.parent / "data" / "screenshot.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            img = pyautogui.screenshot()
            img.save(str(screenshot_path))
            await update.message.reply_photo(
                photo=open(str(screenshot_path), "rb"),
                caption="Screenshot do PC"
            )
        except ImportError:
            await update.message.reply_text(
                "Instale pyautogui: pip install pyautogui"
            )
        except Exception as e:
            await update.message.reply_text(f"Erro ao capturar tela: {e}")

    async def _message_handler(self, update, context):
        """Handler de mensagens gerais."""
        if not self._check_auth(update):
            return

        message = update.message.text
        log.info(f"Telegram recebeu: {message}")

        # Executa acao
        result = self.executor.process_message(message)

        if result["executed"]:
            response_parts = []
            for action in result["actions"]:
                msg = action.get("message", "Executado")
                response_parts.append(msg)
            response = "\n".join(response_parts)
        else:
            response = "Comando nao reconhecido.\n\nExemplos:\n- abra o chrome\n- crie um arquivo teste.txt\n- mostre uso de ram\n- cmd: dir"

        # Limita tamanho para Telegram
        if len(response) > 4000:
            response = response[:4000] + "\n... (truncado)"

        await update.message.reply_text(response)

    def _check_auth(self, update) -> bool:
        """Verifica se usuario esta autorizado."""
        if not self.allowed_user_id:
            return True
        user_id = update.effective_user.id
        if user_id != self.allowed_user_id:
            asyncio.create_task(
                update.message.reply_text(f"[BLOQUEADO] ID {user_id} nao autorizado.")
            )
            return False
        return True

    def start(self):
        """Inicia o bot Telegram."""
        try:
            from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

            self._app = ApplicationBuilder().token(self.token).build()

            # Handlers
            self._app.add_handler(CommandHandler("start", self._start_handler))
            self._app.add_handler(CommandHandler("status", self._status_handler))
            self._app.add_handler(CommandHandler("ip", self._ip_handler))
            self._app.add_handler(CommandHandler("screenshot", self._screenshot_handler))
            self._app.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, self._message_handler
            ))

            log.info("Bot Telegram iniciado!")
            self.running = True
            self._app.run_polling()

        except ImportError:
            log.error("python-telegram-bot nao instalado!")
            print("\n[ERRO] Instale o python-telegram-bot:")
            print("pip install python-telegram-bot")
        except Exception as e:
            log.error(f"Erro no bot Telegram: {e}")
            print(f"\n[ERRO] {e}")

    def start_background(self):
        """Inicia bot em thread separada."""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread


def start_telegram_bot(token: str, allowed_user_id: Optional[int] = None):
    """Inicia bot Telegram."""
    bot = WilliamTelegramBot(token, allowed_user_id)
    bot.start()
    return bot
