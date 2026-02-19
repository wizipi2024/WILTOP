@echo off
title William - Bot Telegram
cd /d "%~dp0"
echo Iniciando Bot Telegram...
call venv\Scripts\activate
python run_telegram.py
pause
