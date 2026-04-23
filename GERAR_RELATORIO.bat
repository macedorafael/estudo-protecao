@echo off
title Gerar Relatorio
set "PROJ=%~dp0"

echo Gerando Estudo de Protecao...
echo (O backend precisa estar rodando via start.bat)
echo.

call "%PROJ%backend\.venv\Scripts\activate.bat"
python "%PROJ%gerar_relatorio.py"
