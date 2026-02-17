@echo off
title Debug Autorizacao
cd /d "%~dp0"

echo.
echo ===================================================================
echo                    DEBUG DE AUTORIZACAO
echo ===================================================================
echo.

echo Verificando arquivo .authorized...
if exist .authorized (
    echo [OK] Arquivo .authorized EXISTE!
    echo Caminho: %cd%\.authorized
    type .authorized
) else (
    echo [ERRO] Arquivo .authorized NAO EXISTE!
    echo.
    echo Execute: python AUTORIZAR_TUDO.py
)

echo.
echo ===================================================================
echo Pressione qualquer tecla para continuar...
pause
