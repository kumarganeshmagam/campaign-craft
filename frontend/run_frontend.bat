@echo off
REM Frontend startup script with port cleanup
echo [INFO] Cleaning up port 3000...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo [INFO] Found process %%a on port 3000, killing it...
    taskkill /PID %%a /F
    timeout /t 1 /nobreak
)

echo [OK] Starting frontend development server...
echo [INFO] Server will start on http://localhost:5173
cd /d "%~dp0"
npm run dev
pause
