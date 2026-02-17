@echo off
title Teste do Detector de Intencoes
cd /d "%~dp0"
call venv\Scripts\activate
python teste_detector.py
pause
