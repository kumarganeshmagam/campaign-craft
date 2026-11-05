@echo off
REM Backend startup script with port cleanup
echo [INFO] Cleaning up port 8000...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo [INFO] Found process %%a on port 8000, killing it...
    taskkill /PID %%a /F
    timeout /t 1 /nobreak
)

echo [OK] Starting backend server...
echo [INFO] Server will start on http://127.0.0.1:8000
cd /d "%~dp0"
python run_server.py
pause
