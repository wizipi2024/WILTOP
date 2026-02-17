@echo off
title Teste de Autorizacao
cd /d "%~dp0"
call venv\Scripts\activate
python teste_autorizacao.py
pause
