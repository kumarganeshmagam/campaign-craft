# PowerShell script to run UI tests with Playwright in headed mode
# This script:
# 1. Kills any existing processes on ports 8000 and 3000
# 2. Starts the backend server
# 3. Starts the frontend server
# 4. Runs Playwright UI tests in HEADED mode with screenshots

param(
    [string]$TestFile = "test_ui_headed.py",
    [switch]$Headless = $false,
    [switch]$Debug = $false
)

$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

# Colors
$Green = [System.ConsoleColor]::Green
$Red = [System.ConsoleColor]::Red
$Yellow = [System.ConsoleColor]::Yellow
$Cyan = [System.ConsoleColor]::Cyan

function Write-Status {
    param([string]$Message, [System.ConsoleColor]$Color = $Green)
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
}

function Write-Header {
    param([string]$Message)
    Write-Host "`n$('='*70)" -ForegroundColor $Cyan
    Write-Host $Message -ForegroundColor $Cyan
    Write-Host "$('='*70)`n" -ForegroundColor $Cyan
}

try {
    # ==================== CLEANUP ====================
    Write-Header "🧹 CLEANUP: Killing old processes..."
    
    # Kill Python processes on port 8000
    Write-Status "Killing Python processes..." $Yellow
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    
    # Kill Node processes on port 3000
    Write-Status "Killing Node processes..." $Yellow
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    
    Write-Status "✅ Cleanup complete" $Green
    
    # ==================== START BACKEND ====================
    Write-Header "🚀 STARTING BACKEND SERVER..."
    
    $backendPath = Join-Path $PSScriptRoot "backend"
    if (-not (Test-Path $backendPath)) {
        throw "Backend directory not found at $backendPath"
    }
    
    Write-Status "Backend path: $backendPath" $Yellow
    
    # Activate virtual environment if exists
    $venvPath = Join-Path $backendPath ".venv"
    if (Test-Path (Join-Path $venvPath "Scripts\Activate.ps1")) {
        Write-Status "Activating virtual environment..." $Yellow
        & (Join-Path $venvPath "Scripts\Activate.ps1")
    }
    
    # Start backend in background
    Write-Status "Starting FastAPI backend on port 8000..." $Cyan
    $backendProcess = Start-Process `
        -FilePath "python" `
        -ArgumentList "-m uvicorn app.main:app --reload --port 8000" `
        -WorkingDirectory $backendPath `
        -PassThru `
        -RedirectStandardOutput (Join-Path $PSScriptRoot "logs\backend_startup.log") `
        -RedirectStandardError (Join-Path $PSScriptRoot "logs\backend_error.log")
    
    Write-Status "Backend process started (PID: $($backendProcess.Id))" $Green
    Start-Sleep -Seconds 3
    
    # ==================== START FRONTEND ====================
    Write-Header "🚀 STARTING FRONTEND SERVER..."
    
    $frontendPath = Join-Path $PSScriptRoot "frontend"
    if (-not (Test-Path $frontendPath)) {
        throw "Frontend directory not found at $frontendPath"
    }
    
    Write-Status "Frontend path: $frontendPath" $Yellow
    
    # Check if dependencies installed
    $packageJsonPath = Join-Path $frontendPath "node_modules"
    if (-not (Test-Path $packageJsonPath)) {
        Write-Status "Installing frontend dependencies..." $Yellow
        Push-Location $frontendPath
        npm install --legacy-peer-deps
        Pop-Location
    }
    
    # Start frontend in background
    Write-Status "Starting Vite frontend on port 3000..." $Cyan
    $frontendProcess = Start-Process `
        -FilePath "npm" `
        -ArgumentList "run dev" `
        -WorkingDirectory $frontendPath `
        -PassThru `
        -RedirectStandardOutput (Join-Path $PSScriptRoot "logs\frontend_startup.log") `
        -RedirectStandardError (Join-Path $PSScriptRoot "logs\frontend_error.log")
    
    Write-Status "Frontend process started (PID: $($frontendProcess.Id))" $Green
    Start-Sleep -Seconds 4
    
    # ==================== WAIT FOR SERVICES ====================
    Write-Header "⏳ WAITING FOR SERVICES TO BE READY..."
    
    $maxRetries = 15
    $backendReady = $false
    $frontendReady = $false
    
    # Check backend
    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            $response = curl.exe -s -o $null -w "%{http_code}" "http://127.0.0.1:8000/docs" -m 2
            if ($response -eq "200") {
                Write-Status "✅ Backend is ready (http://127.0.0.1:8000)" $Green
                $backendReady = $true
                break
            }
        } catch { }
        Write-Status "Waiting for backend... ($i/$maxRetries)" $Yellow
        Start-Sleep -Seconds 1
    }
    
    if (-not $backendReady) {
        Write-Status "❌ Backend failed to start" $Red
        Write-Status "Check logs: $backendPath\logs\backend_startup.log" $Yellow
    }
    
    # Check frontend
    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            $response = curl.exe -s -o $null -w "%{http_code}" "http://localhost:3000" -m 2
            if ($response -eq "200") {
                Write-Status "✅ Frontend is ready (http://localhost:3000)" $Green
                $frontendReady = $true
                break
            }
        } catch { }
        Write-Status "Waiting for frontend... ($i/$maxRetries)" $Yellow
        Start-Sleep -Seconds 1
    }
    
    if (-not $frontendReady) {
        Write-Status "⚠️  Frontend may not be fully ready, but proceeding..." $Yellow
    }
    
    # ==================== RUN UI TESTS ====================
    Write-Header "🎬 RUNNING PLAYWRIGHT UI TESTS - HEADED MODE"
    Write-Status "📸 Screenshots will be saved to: ./logs/screenshots" $Cyan
    Write-Status "📝 Test logs will be saved to: ./logs/ui_tests.log" $Cyan
    Write-Status "Opening browser in visible mode to watch tests execute..." $Cyan
    
    $testPath = Join-Path $PSScriptRoot "backend"
    
    # Create logs directory if needed
    $logsDir = Join-Path $PSScriptRoot "logs"
    if (-not (Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }
    
    # Run tests
    Write-Status "Starting test execution..." $Yellow
    Push-Location $testPath
    
    if ($Debug) {
        # Run with more verbosity and no capture
        pytest $TestFile -v -s --tb=short --capture=no
    } else {
        # Run normally
        pytest $TestFile -v -s --tb=short
    }
    
    $testExitCode = $LASTEXITCODE
    Pop-Location
    
    # ==================== RESULTS ====================
    Write-Header "✅ TEST EXECUTION COMPLETE"
    
    if ($testExitCode -eq 0) {
        Write-Status "✅ All tests PASSED!" $Green
    } else {
        Write-Status "❌ Some tests FAILED (Exit code: $testExitCode)" $Red
    }
    
    Write-Status "📸 Screenshots directory: $(Join-Path $PSScriptRoot 'logs\screenshots')" $Cyan
    Write-Status "📝 Test log file: $(Join-Path $PSScriptRoot 'logs\ui_tests.log')" $Cyan
    
    # ==================== KEEP SERVICES RUNNING ====================
    Write-Header "🔄 KEEPING SERVICES RUNNING FOR MANUAL TESTING"
    
    Write-Status "Backend running on: http://127.0.0.1:8000" $Green
    Write-Status "Frontend running on: http://localhost:3000" $Green
    Write-Status "API Docs on: http://127.0.0.1:8000/docs" $Cyan
    Write-Status "" $Yellow
    Write-Status "Press Ctrl+C to stop all services" $Yellow
    Write-Status "" $Yellow
    
    # Keep script running until Ctrl+C
    while ($true) {
        # Check if processes are still running
        if ($null -eq (Get-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Status "⚠️  Backend process died, restarting..." $Yellow
            $backendProcess = Start-Process `
                -FilePath "python" `
                -ArgumentList "-m uvicorn app.main:app --reload --port 8000" `
                -WorkingDirectory $backendPath `
                -PassThru `
                -RedirectStandardOutput (Join-Path $PSScriptRoot "logs\backend_startup.log") `
                -RedirectStandardError (Join-Path $PSScriptRoot "logs\backend_error.log")
        }
        
        if ($null -eq (Get-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Status "⚠️  Frontend process died, restarting..." $Yellow
            $frontendProcess = Start-Process `
                -FilePath "npm" `
                -ArgumentList "run dev" `
                -WorkingDirectory $frontendPath `
                -PassThru `
                -RedirectStandardOutput (Join-Path $PSScriptRoot "logs\frontend_startup.log") `
                -RedirectStandardError (Join-Path $PSScriptRoot "logs\frontend_error.log")
        }
        
        Start-Sleep -Seconds 5
    }

} catch {
    Write-Status "❌ ERROR: $_" $Red
    Write-Status "Stack trace: $($_.ScriptStackTrace)" $Red
    
    # Cleanup on error
    Write-Status "Cleaning up..." $Yellow
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    exit 1
} finally {
    Write-Status "`n[Cleanup] Stopping services..." $Yellow
    
    # Stop background processes
    if ($null -ne (Get-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue)) {
        $backendProcess | Stop-Process -Force -ErrorAction SilentlyContinue
    }
    
    if ($null -ne (Get-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue)) {
        $frontendProcess | Stop-Process -Force -ErrorAction SilentlyContinue
    }
    
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Status "Services stopped" $Green
}
