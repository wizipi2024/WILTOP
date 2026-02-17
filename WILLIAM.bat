@echo off
title William - Assistente IA
cd /d "%~dp0"
call venv\Scripts\activate
python run_william.py
pause
