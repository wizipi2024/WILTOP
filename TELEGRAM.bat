@echo off
title William - Bot Telegram
cd /d "%~dp0"
call venv\Scripts\activate
pip install python-telegram-bot --quiet 2>nul
python run_telegram.py
pause
