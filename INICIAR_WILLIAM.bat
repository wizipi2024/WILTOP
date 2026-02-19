@echo off
title William - Interface Completa
cd /d "%~dp0"
echo Iniciando William...
call venv\Scripts\activate
python run_william.py
pause
