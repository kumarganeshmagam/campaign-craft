@echo off
REM CampaignCraft Master Startup Script
REM Starts backend, frontend, and runs tests with logging

echo ============================================================
echo CampaignCraft Application Startup
echo ============================================================
echo.
echo Starting application with full logging...
echo Logs will be written to: logs\ directory
echo.

cd /d "%~dp0"
python startup.py

pause
