# 🎉 CampaignCraft - Complete Setup & Testing Guide

## QUICK START - 30 Seconds to Success

### Step 1: Navigate to project
```bash
cd e:\AI\campaign-craft
```

### Step 2: Run everything
```bash
python startup.py
```

### Step 3: Open browser
http://localhost:3000

**That's it! You're done.** ✅

---

## WHAT JUST HAPPENED

When you ran `python startup.py`:

1. ✅ **Backend started** (http://127.0.0.1:8000)
   - Connected to real Gemini API
   - Logging to `logs/backend_startup.log`

2. ✅ **Frontend started** (http://localhost:3000)
   - React development server
   - Logging to `logs/frontend_startup.log`

3. ✅ **E2E Tests started** (automatically)
   - Playwright browser automation
   - Logging to `logs/test_results.log`

4. ✅ **All events logged** 
   - Every action recorded with timestamp
   - Logs in `logs/` directory

---

## MONITORING & DEBUGGING

### View Logs Interactively
```bash
python view_logs.py
```
Then select which log to view.

### View Specific Logs
```bash
python view_logs.py backend     # Backend logs
python view_logs.py tests       # Test results
python view_logs.py startup     # Startup process
python view_logs.py list        # List all logs
```

### Check Service Health
```bash
# Backend
curl http://127.0.0.1:8000/docs

# Frontend
curl http://localhost:3000
```

### Monitor Logs in Real-time
```bash
# On Windows with PowerShell
Get-Content logs/backend_startup.log -Wait

# Or check specific log files
cat logs/startup.log
cat logs/test_results.log
```

---

## UNDERSTANDING THE LOG FILES

### Master Startup Log
**File**: `logs/startup.log`
**Contains**: Overall startup process, service status, timing

**Example**:
```
[2025-11-14 14:39:49] CampaignCraft Application Startup
[2025-11-14 14:39:50] [Backend] Started with PID 20732
[2025-11-14 14:39:53] [Backend] [OK] Backend is ready on http://127.0.0.1:8000
[2025-11-14 14:39:54] [Frontend] Started with PID 18040
[2025-11-14 14:39:59] [Frontend] [OK] Frontend is ready on http://localhost:3000
```

### Backend Logs
**File**: `logs/backend_startup.log`
**Contains**: FastAPI startup, port binding, application initialization

**File**: `logs/backend.log` (runtime)
**Contains**: API calls, agent execution, data processing

### Frontend Logs
**File**: `logs/frontend_startup.log`
**Contains**: Vite dev server startup, bundling, module loading

### Test Logs
**File**: `logs/test_results.log`
**Contains**: Playwright test execution, assertions, results

**Example**:
```
test_e2e.py::TestCampaignCraft::test_backend_health PASSED [25%]
test_e2e.py::TestCampaignCraft::test_start_campaign_endpoint PASSED [50%]
```

### API Logs
**File**: `logs/api.log`
**Contains**: HTTP requests, responses, status codes

### Agent Logs
**File**: `logs/agents.log`
**Contains**: AI agent execution, Gemini API calls, results

### Error Logs
**File**: `logs/errors.log`
**Contains**: All errors from any component

---

## TESTING THE APPLICATION

### Automated Tests
Tests run automatically when you start the application:
1. Backend health check ✅
2. API endpoint test ✅
3. Frontend loads ⏳
4. Campaign submission ⏳

View results: `python view_logs.py tests`

### Manual Testing

#### Test 1: Backend API
```bash
curl -X POST http://127.0.0.1:8000/api/start-campaign \
  -H "Content-Type: application/json" \
  -d "{\"topic\": \"AI automation tools\"}"
```

Expected response:
```json
{
  "campaign_id": "uuid-string",
  "stream_url": "/api/stream/uuid-string"
}
```

#### Test 2: Frontend UI
1. Open http://localhost:3000
2. Enter topic: "SaaS marketing strategies"
3. Click "Start Campaign"
4. Watch real results stream in

#### Test 3: Real-time Streaming
The frontend uses Server-Sent Events (SSE) to stream results:
- Status updates in real-time
- AI-generated content as it arrives
- Campaign completion notification

---

## TROUBLESHOOTING

### Backend Won't Start
```bash
# 1. Check if port 8000 is in use
netstat -ano | findstr :8000

# 2. Kill the process using port 8000
taskkill /PID [PID] /F

# 3. Check logs
python view_logs.py backend
```

### Frontend Won't Start
```bash
# 1. Check if port 3000 is in use
netstat -ano | findstr :3000

# 2. Kill the process using port 3000
taskkill /PID [PID] /F

# 3. Reinstall dependencies
cd frontend
npm install

# 4. Check logs
python view_logs.py frontend
```

### Tests Failing
```bash
# 1. Check test logs
python view_logs.py tests

# 2. Verify both services are running
curl http://127.0.0.1:8000/docs
curl http://localhost:3000

# 3. Check for errors
python view_logs.py errors
```

### API Quota Exceeded
```
Error: ResourceExhausted: 429
```
Solution: The free tier allows 2 requests/minute. Wait and try again.

---

## FILE LOCATIONS

### Configuration
```
backend/.env                 # API keys here
```

### Logs Directory
```
logs/
├── startup.log             # Master startup
├── backend_startup.log     # Backend init
├── frontend_startup.log    # Frontend init
├── test_results.log        # Test output
├── backend.log             # Runtime logs
├── api.log                 # API requests
├── agents.log              # Agent execution
└── errors.log              # All errors
```

### Application Code
```
backend/
├── app/
│   ├── main.py             # FastAPI app
│   ├── logging_config.py   # Logging setup
│   ├── orchestrators/
│   │   └── gemini_orchestrator.py    # Real AI
│   ├── agents/
│   │   └── research_agent.py         # Research AI
│   └── router/
│       └── agent_router.py           # Routing
├── run_server.py           # Backend startup
└── test_e2e.py             # Tests

frontend/
├── src/
│   ├── App.jsx             # React app
│   └── components/
│       └── ChatUI.jsx      # Chat interface
├── run_frontend.bat        # Frontend startup
└── package.json            # Dependencies

startup.py                 # Master startup script
view_logs.py              # Log viewer utility
```

---

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│              CampaignCraft Full Stack                │
└─────────────────────────────────────────────────────┘

USER INTERFACE (http://localhost:3000)
    ↓
React App + Vite Dev Server
    ↓
[Logs: frontend_startup.log]
    ↓
HTTP POST /api/start-campaign
    ↓
FastAPI Backend (http://127.0.0.1:8000)
    ↓
[Logs: backend_startup.log, backend.log, api.log]
    ↓
Agent Router
    ↓
Research Agent
    ↓
[Logs: agents.log]
    ↓
Google Gemini API
    ↓
Results Stream (SSE)
    ↓
Frontend Displays in Real-time
    ↓
[Logs: test_results.log from automated tests]
```

---

## STOPPING THE APPLICATION

### Graceful Shutdown
```bash
# In the terminal where startup.py is running:
Press Ctrl+C
```

The script will:
1. Stop backend gracefully
2. Stop frontend gracefully
3. Clean up processes
4. Display shutdown message

### Force Stop
```bash
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Kill all Node processes
Get-Process node | Stop-Process -Force
```

---

## ENVIRONMENT SETUP

### Check Gemini API Key
```bash
# View current API key
type backend/.env
```

### Update API Key
```bash
# Edit backend/.env file
api_key=your-new-key-here
```

Get key at: https://makersuite.google.com/app/apikey

---

## PERFORMANCE TIPS

1. **Monitor Logs**: Use `python view_logs.py` to watch health
2. **Check Errors**: Review `logs/errors.log` immediately
3. **Watch API Usage**: Monitor `logs/api.log` for patterns
4. **Agent Status**: Check `logs/agents.log` for AI processing
5. **Test Results**: Review `logs/test_results.log` regularly

---

## ADVANCED FEATURES

### Custom Testing
Modify `backend/test_e2e.py` to add more tests

### Custom Logging
Edit `backend/app/logging_config.py` to change log levels

### API Customization
Modify `backend/app/main.py` to add new endpoints

### Frontend Customization
Edit `frontend/src/App.jsx` to change UI

---

## NEXT STEPS

### Immediate
1. Run: `python startup.py` ✅
2. Open: http://localhost:3000 ✅
3. Test: Enter a topic ✅
4. Monitor: `python view_logs.py` ✅

### Short Term
- Deploy to cloud
- Add user authentication
- Implement database persistence
- Add more AI providers

### Long Term
- Scale horizontally
- Add webhook notifications
- Build admin dashboard
- Implement caching layer

---

## SUPPORT & DOCUMENTATION

- **Startup Guide**: See `STARTUP_GUIDE.md`
- **Implementation**: See `IMPLEMENTATION_SUMMARY.md`
- **Status**: See `STATUS.md`
- **This Guide**: `README.md`

---

## FINAL CHECKLIST

✅ Backend running on http://127.0.0.1:8000
✅ Frontend running on http://localhost:3000
✅ Logging configured and writing to files
✅ E2E tests ready
✅ Port cleanup automated
✅ Log viewer available
✅ Documentation complete

**You're all set!** 🚀

Start the application:
```bash
python startup.py
```

Then open: http://localhost:3000

**Enjoy!** 🎉
