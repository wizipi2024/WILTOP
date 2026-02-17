@echo off
title William - Modo Forcado
cd /d "%~dp0"
call venv\Scripts\activate
python run_forcado.py
pause
