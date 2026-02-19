@echo off
title William - Terminal CLI
cd /d "%~dp0"
echo Iniciando William modo terminal...
call venv\Scripts\activate
python run.py
pause
