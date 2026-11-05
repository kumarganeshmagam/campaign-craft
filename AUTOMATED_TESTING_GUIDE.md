# Automated Testing Guide - CampaignCraft

## Overview
CampaignCraft includes a **fully automated testing pipeline** that:
1. ✅ Starts the backend server (port 8000)
2. ✅ Starts the frontend server (port 3000)
3. ✅ Waits for both services to be ready
4. ✅ Runs E2E tests with Playwright automatically
5. ✅ Logs everything to files in `logs/` directory

## Quick Start

### Run Everything with One Command
```powershell
cd e:\AI\campaign-craft
python startup.py
```

This single command will:
- Clean up ports 8000 and 3000 (kill any existing processes)
- Start backend on http://127.0.0.1:8000
- Start frontend on http://localhost:3000
- Run Playwright E2E tests automatically
- Keep both services running for manual testing

### Stop Everything
Press `Ctrl+C` in the terminal - it will gracefully shut down both services.

---

## Test Results

### E2E Tests Included (4 tests)
| Test | Purpose | Status |
|------|---------|--------|
| `test_backend_health` | Verify backend API is responding | ✅ PASSED |
| `test_start_campaign_endpoint` | Test `/api/start-campaign` endpoint | ✅ PASSED |
| `test_frontend_loads` | Verify frontend loads on port 3000 | ✅ PASSED |
| `test_campaign_submission` | Full campaign submission flow | ✅ PASSED |

### Most Recent Test Run
```
============================== 4 passed, 8 warnings in 18.71s ========================
```

Tests cover:
- ✅ Backend health check
- ✅ API endpoint functionality
- ✅ Frontend page loading
- ✅ Campaign creation and submission
- ✅ Streaming responses (SSE)

---

## Log Files

All activity is logged to `logs/` directory:

| Log File | Contains |
|----------|----------|
| `startup.log` | Master startup orchestration |
| `backend_startup.log` | Backend server startup events |
| `frontend_startup.log` | Frontend server startup events |
| `test_results.log` | E2E test execution results |
| `api.log` | FastAPI request/response logs |
| `agents.log` | Agent execution logs |
| `playwright_test.log` | Playwright test details |

### View Recent Logs
```powershell
# View startup log
Get-Content e:\AI\campaign-craft\logs\startup.log | Select-Object -Last 20

# View test results
Get-Content e:\AI\campaign-craft\logs\test_results.log | Select-Object -Last 50

# View backend log
Get-Content e:\AI\campaign-craft\logs\backend_startup.log | Select-Object -Last 30
```

---

## Workflow Diagram

```
┌─────────────────────────┐
│   python startup.py     │
└────────────┬────────────┘
             │
      ┌──────▼─────────────┐
      │  Kill old processes │
      │  (ports 8000, 3000)  │
      └──────┬──────────────┘
             │
      ┌──────▼──────────────┐
      │  Start Backend       │
      │  (http://127.0.0.1:8000)
      └──────┬──────────────┘
             │
      ┌──────▼──────────────┐
      │  Start Frontend      │
      │  (http://localhost:3000)
      └──────┬──────────────┘
             │
      ┌──────▼──────────────┐
      │  Wait 3 seconds      │
      └──────┬──────────────┘
             │
      ┌──────▼──────────────────────────────┐
      │  Run E2E Tests (Playwright)          │
      │  - test_backend_health               │
      │  - test_start_campaign_endpoint      │
      │  - test_frontend_loads               │
      │  - test_campaign_submission          │
      └──────┬──────────────────────────────┘
             │
      ┌──────▼──────────────┐
      │  Keep services      │
      │  running for manual │
      │  testing (Ctrl+C    │
      │  to stop)           │
      └─────────────────────┘
```

---

## Manual Testing (While Services Run)

### Test Backend API
```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/start-campaign" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"topic":"AI automation for small businesses"}'

$response | ConvertTo-Json
```

### Test Frontend
Open browser: http://localhost:3000
- Enter a topic in the input field
- Click "Start Campaign"
- Watch real-time responses stream in

### Test Endpoint Health
```powershell
# Backend health
curl.exe http://127.0.0.1:8000/docs

# Frontend
curl.exe http://localhost:3000
```

---

## Troubleshooting

### "Port Already in Use" Error
The startup script automatically cleans up ports, but if you see this:
```powershell
# Kill processes manually
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

# Then try again
python startup.py
```

### Tests Fail/Timeout
Check the logs:
```powershell
# Check test results
Get-Content e:\AI\campaign-craft\logs\test_results.log

# Check backend errors
Get-Content e:\AI\campaign-craft\logs\backend_startup.log | Select-String "ERROR"

# Check frontend errors
Get-Content e:\AI\campaign-craft\logs\frontend_startup.log | Select-String "ERROR"
```

### Backend Not Starting
1. Check if port 8000 is in use: `netstat -ano | findstr :8000`
2. Kill the process: `taskkill /PID <PID> /F`
3. Check Python installed: `python --version`
4. Check dependencies: `cd backend ; pip install -r requirements.txt`

### Frontend Not Starting
1. Check if port 3000 is in use: `netstat -ano | findstr :3000`
2. Kill the process: `taskkill /PID <PID> /F`
3. Check Node installed: `node --version`
4. Install dependencies: `cd frontend ; npm install`

---

## Advanced: Run Tests Only

### Run Playwright tests standalone
```powershell
cd e:\AI\campaign-craft\backend
python -m pytest test_e2e.py -v
```

### Run specific test
```powershell
python -m pytest test_e2e.py::TestCampaignCraft::test_backend_health -v
```

### Run with coverage
```powershell
python -m pytest test_e2e.py --cov --cov-report=html
```

---

## Architecture

### Services
- **Backend**: FastAPI on port 8000
  - Real Gemini API integration
  - SSE streaming responses
  - Full agent orchestration

- **Frontend**: React + Vite on port 3000
  - Campaign creation UI
  - Real-time streaming display
  - Framer Motion animations

### Testing Stack
- **Playwright**: Browser automation for E2E tests
- **pytest**: Test framework and runner
- **asyncio**: Async test support

### Logging
- **Python logging module**: Configured in `backend/app/logging_config.py`
- **Rotating file handlers**: 5MB per file, 5 backups
- **Timestamps**: All events timestamped and logged

---

## Next Steps

1. ✅ **Run tests**: `python startup.py`
2. ✅ **Monitor logs**: Open `logs/` directory
3. ✅ **Test manually**: Visit http://localhost:3000
4. ✅ **Submit campaign**: Enter topic and watch real-time AI responses
5. ✅ **Verify integration**: Check logs show Gemini API calls

---

## Support

For issues:
1. Check logs in `logs/` directory
2. Verify both services started in startup logs
3. Test endpoints manually with curl/PowerShell
4. Check that Gemini API key is in `.env`

All tests are automated and run every time you start the application!
