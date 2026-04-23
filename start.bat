@echo off
title Gerador de Estudos de Protecao

echo ============================================================
echo  Gerador de Estudos de Protecao e Seletividade de MT
echo  ABNT NBR 14039 / NDU 002 ENERGISA
echo ============================================================
echo.

set "PROJ=%~dp0"
set "VENV=%PROJ%backend\.venv\Scripts\activate.bat"
set "NODE=%PROJ%frontend\node_modules"

if exist "%VENV%" goto :backend_ok

echo [1/4] Criando ambiente virtual Python...
python -m venv "%PROJ%backend\.venv"
echo [2/4] Instalando dependencias Python...
call "%PROJ%backend\.venv\Scripts\activate.bat"
pip install -r "%PROJ%backend\requirements.txt" --quiet
goto :check_node

:backend_ok
call "%VENV%"

:check_node
if exist "%NODE%" goto :start

echo [3/4] Instalando dependencias Node.js...
pushd "%PROJ%frontend"
npm install --silent
popd

:start
echo [4/4] Iniciando backend (porta 8000)...
start "Backend FastAPI" cmd /k "cd /d "%PROJ%" && call backend\.venv\Scripts\activate.bat && uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak > nul

echo [4/4] Iniciando frontend React (porta 5173)...
start "Frontend React" cmd /k "cd /d "%PROJ%frontend" && npx vite --port 5173"

timeout /t 4 /nobreak > nul

echo.
echo  Abrindo navegador...
start http://localhost:5173

echo.
echo ============================================================
echo  App: http://localhost:5173
echo  API: http://localhost:8000/docs
echo  Feche as janelas de terminal para encerrar.
echo ============================================================
pause
