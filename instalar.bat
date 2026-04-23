@echo off
title Instalacao - Gerador de Estudos de Protecao

set "PROJ=%~dp0"

echo ============================================================
echo  Instalacao das dependencias
echo  Execute este script apenas uma vez
echo ============================================================
echo.

echo [1/3] Criando ambiente virtual Python...
python -m venv "%PROJ%backend\.venv"
if errorlevel 1 (
    echo ERRO: Python nao encontrado. Instale Python 3.11+ em https://python.org
    pause
    exit /b 1
)

echo [2/3] Instalando bibliotecas Python (FastAPI, ReportLab, Matplotlib)...
call "%PROJ%backend\.venv\Scripts\activate.bat"
pip install -r "%PROJ%backend\requirements.txt"
if errorlevel 1 (
    echo ERRO ao instalar dependencias Python.
    pause
    exit /b 1
)

echo [3/3] Instalando dependencias Node.js (React, Vite, Tailwind)...
pushd "%PROJ%frontend"
npm install
if errorlevel 1 (
    echo ERRO ao instalar dependencias Node.js.
    popd
    pause
    exit /b 1
)
popd

echo.
echo ============================================================
echo  Instalacao concluida! Execute START.BAT para iniciar.
echo ============================================================
pause
