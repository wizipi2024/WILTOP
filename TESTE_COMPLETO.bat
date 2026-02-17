@echo off
title Teste Completo do William
cd /d "%~dp0"
call venv\Scripts\activate
python teste_completo.py
pause
