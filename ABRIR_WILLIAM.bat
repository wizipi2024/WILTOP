@echo off
title Assistente IA William
cd /d "%~dp0"
call venv\Scripts\activate
python run_gui.py
pause
