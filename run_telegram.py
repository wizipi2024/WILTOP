"""Inicia o Bot Telegram do William."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env
load_dotenv(Path(__file__).parent / ".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID", "")

if not TELEGRAM_TOKEN:
    print("="*60)
    print("CONFIGURACAO DO BOT TELEGRAM")
    print("="*60)
    print()
    print("Para usar o Bot Telegram, voce precisa:")
    print()
    print("1. Abra o Telegram e procure @BotFather")
    print("2. Envie: /newbot")
    print("3. Siga as instrucoes e copie o TOKEN")
    print("4. Cole o TOKEN abaixo:")
    print()
    TELEGRAM_TOKEN = input("Token do Bot: ").strip()

    if not TELEGRAM_TOKEN:
        print("[ERRO] Token vazio! Saindo...")
        sys.exit(1)

    # Salva no .env
    env_file = Path(__file__).parent / ".env"
    with open(env_file, "a", encoding="utf-8") as f:
        f.write(f"\nTELEGRAM_BOT_TOKEN={TELEGRAM_TOKEN}\n")

    print()
    print("[OK] Token salvo no .env!")
    print()
    print("OPCIONAL: Para seguranca extra, configure seu Telegram ID.")
    print("(Envie /start ao bot e ele mostrara seu ID)")
    user_id = input("Telegram User ID (ou ENTER para pular): ").strip()
    if user_id:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"TELEGRAM_ALLOWED_USER_ID={user_id}\n")
        TELEGRAM_USER_ID = user_id
        print(f"[OK] User ID {user_id} salvo!")

print()
print("="*60)
print("INICIANDO BOT TELEGRAM DO WILLIAM")
print("="*60)
print()
print(f"Token: {TELEGRAM_TOKEN[:10]}...{TELEGRAM_TOKEN[-5:]}")
if TELEGRAM_USER_ID:
    print(f"User ID autorizado: {TELEGRAM_USER_ID}")
else:
    print("AVISO: Qualquer usuario pode controlar o bot!")
    print("Configure TELEGRAM_ALLOWED_USER_ID no .env para seguranca.")
print()
print("O bot esta rodando! Abra o Telegram e envie /start")
print("Pressione Ctrl+C para parar.")
print()

from src.telegram.telegram_bot import start_telegram_bot

allowed_id = int(TELEGRAM_USER_ID) if TELEGRAM_USER_ID else None
start_telegram_bot(TELEGRAM_TOKEN, allowed_id)
