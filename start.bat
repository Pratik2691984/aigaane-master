@echo off
start "Aigaane API" cmd /k "cd api && python -m uvicorn kernel_api:app --reload --port 8000 --host 0.0.0.0"
timeout /t 2
start "Aigaane Frontend" cmd /k "python -m http.server 5500"
echo Servers started!
echo Frontend: http://localhost:5500
echo API: http://localhost:8000