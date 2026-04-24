@echo off
echo Iniciando Academia Jiu-Jitsu...

start "Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Sistema iniciado!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo Docs API: http://localhost:8000/docs
