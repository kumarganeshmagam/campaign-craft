#!/usr/bin/env powershell
<#
CampaignCraft Master Startup Script
Starts backend, frontend, and runs tests with full logging
#>

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CampaignCraft Application Startup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting application with full logging..."
Write-Host "Logs will be written to: logs/ directory"
Write-Host ""

Set-Location $PSScriptRoot
python startup.py

Read-Host "Press Enter to exit"
