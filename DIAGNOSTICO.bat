@echo off
title Diagnostico do William
cd /d "%~dp0"
call venv\Scripts\activate
python diagnostico.py
pause
