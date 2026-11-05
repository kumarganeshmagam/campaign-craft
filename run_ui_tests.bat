@echo off
REM Batch file to run UI tests with Playwright in headed mode
REM This runs the PowerShell script

echo.
echo ======================================================================
echo.
echo  CAMPAIGNCRAFT - PLAYWRIGHT UI TESTS (HEADED MODE)
echo.
echo  This script will:
echo  1. Kill any existing processes on ports 8000 and 3000
echo  2. Start the backend server (FastAPI on port 8000)
echo  3. Start the frontend server (Vite on port 3000)
echo  4. Run Playwright UI tests in HEADED mode with screenshots
echo.
echo  You will see a browser window open showing the tests executing
echo.
echo ======================================================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell is not available in PATH
    exit /b 1
)

REM Run the PowerShell script
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_ui_tests.ps1"

pause
