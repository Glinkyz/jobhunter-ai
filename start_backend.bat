@echo off
title JobHunter AI - Backend Server
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"
echo ===================================================
echo   JobHunter AI - Backend Core
echo   Servidor disponible en: http://127.0.0.1:8000
echo   Documentacion interactiva: http://127.0.0.1:8000/docs
echo ===================================================
"C:\Program Files\Python313\python.exe" -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000 --reload
pause
