@echo off
title Gerar Estudo FRIGOSUL
set "PROJ=%~dp0"

echo Gerando Estudo de Protecao - FRIGOSUL...
echo (O backend precisa estar rodando via start.bat)
echo.

call "%PROJ%backend\.venv\Scripts\activate.bat"
python "%PROJ%gerar_frigosul.py"
