@echo off
echo Starting Aigaane API Server...
cd C:\aigaane-master\api
python -m uvicorn kernel_api:app --reload --port 8000 --host 0.0.0.0
pause