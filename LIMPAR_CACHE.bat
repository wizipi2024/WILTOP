@echo off
title Limpar Cache Python
cd /d "%~dp0"

echo.
echo ===================================================================
echo                    LIMPANDO CACHE PYTHON
echo ===================================================================
echo.

echo Removendo arquivos __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo Removendo arquivos .pyc...
del /s /q *.pyc 2>nul

echo Removendo arquivos .pyo...
del /s /q *.pyo 2>nul

echo.
echo [OK] Cache limpo!
echo.
echo Agora voce pode abrir o William novamente com:
echo ABRIR_COMPLETO.bat
echo.
pause
