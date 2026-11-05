# 🚀 Servers Status

## ✅ Current Status

Both application servers are running in background mode:

### Backend Server (FastAPI + Uvicorn)
```
Port: 8000
Host: 0.0.0.0 (localhost:8000)
Process: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Status: ✅ RUNNING
Last Started: This session
```

**Endpoints Available:**
- `GET  http://localhost:8000/docs` - Swagger UI API documentation
- `GET  http://localhost:8000/redoc` - ReDoc API documentation
- `POST http://localhost:8000/api/start-campaign` - Create new campaign
- `GET  http://localhost:8000/api/stream/{campaign_id}` - SSE stream
- `POST http://localhost:8000/api/generate-content` - Generate email content

### Frontend Server (Vite + React)
```
Port: 3001
Host: localhost:3001
Process: npm run dev
Status: ✅ RUNNING
Last Started: This session
```

**Application Access:**
- `http://localhost:3001/` - CampaignCraft web application

---

## 📡 How to Access

### Local Development
```
Frontend: http://localhost:3001
Backend:  http://localhost:8000

Backend Docs: http://localhost:8000/docs (Swagger UI)
```

### Test API Endpoint
```powershell
# Create a campaign
$body = @{
    topic = "AI automation in retail"
} | ConvertTo-Json

$response = Invoke-RestMethod `
  -Uri "http://localhost:8000/api/start-campaign" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

$response  # Shows campaign_id and stream_url
```

### View Campaign Stream
```powershell
# Subscribe to campaign updates
$campaign_id = "your_campaign_id_here"
$stream_url = "http://localhost:8000/api/stream/$campaign_id"

# Using curl/PowerShell to read SSE stream:
Invoke-WebRequest -Uri $stream_url -Method GET | Select-Object -ExpandProperty Content
```

---

## 🔍 Verify Servers Running

### Check Backend Port (8000)
```powershell
# PowerShell
netstat -ano -p tcp | findstr "8000"

# Or
Get-NetTcpConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

### Check Frontend Port (3001)
```powershell
# PowerShell
netstat -ano -p tcp | findstr "3001"

# Or
Get-NetTcpConnection -LocalPort 3001 -ErrorAction SilentlyContinue
```

---

## 🛑 Stopping Servers (if needed)

### Stop Backend
```powershell
# Find and kill uvicorn process
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*uvicorn*"} | Stop-Process -Force
```

### Stop Frontend
```powershell
# Find and kill node process
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force
```

---

## 🔄 Restarting Servers

### Restart Backend
```powershell
cd e:\AI\campaign-craft\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Restart Frontend
```powershell
cd e:\AI\campaign-craft\frontend
npm run dev
```

---

## 📝 Server Logs Location

### Backend Logs
- **Console Output:** See terminal running backend server
- **Location:** `backend/app/main.py` (FastAPI logs printed to console)

### Frontend Logs
- **Console Output:** See terminal running frontend server
- **Browser Console:** Open http://localhost:3001 and press F12

---

## 🧪 Quick Test

### Test 1: Backend Responds
```powershell
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET
    Write-Host "✅ Backend is responding: $($response.StatusCode)"
} catch {
    Write-Host "❌ Backend not responding"
}
```

### Test 2: Frontend Responds
```powershell
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001" -Method GET
    Write-Host "✅ Frontend is responding: $($response.StatusCode)"
} catch {
    Write-Host "❌ Frontend not responding"
}
```

### Test 3: API Endpoint
```powershell
try {
    $body = '{"topic":"test"}'
    $response = Invoke-RestMethod `
      -Uri "http://localhost:8000/api/start-campaign" `
      -Method POST `
      -ContentType "application/json" `
      -Body $body
    Write-Host "✅ API working: $($response.campaign_id)"
} catch {
    Write-Host "❌ API not working: $_"
}
```

---

## 🌐 Browser Access

### Open Application
1. Open any web browser
2. Navigate to: `http://localhost:3001`
3. You should see:
   - CampaignCraft logo/title
   - Blue gradient background
   - Search bar for campaign topic
   - "Start Campaign" button

### Test Campaign Generation
1. Enter campaign topic (e.g., "AI automation in retail")
2. Click "Start Campaign"
3. Watch real-time progress in message panel
4. After agents complete, click "Generate Campaign Content"
5. Switch tabs to view:
   - Plan (timeline, channels, goals)
   - Use Cases (clickable cards)
   - Contacts (table with target list)
   - Proposals (email templates)

---

## ⚙️ Configuration

### Backend Configuration (.env)
Located in: `backend/.env`

```bash
# AI Provider (gemini, openai, claude, mock)
AI_PROVIDER=gemini

# API Keys (optional)
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here

# CORS (for production)
ALLOWED_ORIGINS=http://localhost:3001
```

### Frontend Configuration
Located in: `frontend/vite.config.js`
- Proxy configured for API calls to http://localhost:8000

---

## 📊 Expected Data Flow

```
User opens http://localhost:3001
↓
Frontend loads React app
↓
User enters campaign topic & clicks "Start Campaign"
↓
Frontend POSTs to http://localhost:8000/api/start-campaign
↓
Backend returns: { campaign_id: "uuid", stream_url: "/api/stream/uuid" }
↓
Frontend opens EventSource to http://localhost:8000/api/stream/uuid
↓
Backend orchestrates agents:
  1. WebScraperAgent (research)
  2. CampaignPlannerAgent (planning)
  3. UseCaseAgent (parallel)
  4. TargetFinderAgent (parallel)
  5. ContentAgent (content generation)
  6. StrategyFormatterAgent (format & structure)
↓
Each agent emits progress to SSE stream
↓
Frontend receives SSE events and displays in real-time
↓
User clicks "Generate Campaign Content"
↓
Frontend POSTs to http://localhost:8000/api/generate-content
↓
Backend runs ContentAgent + StrategyFormatterAgent
↓
Results stream to frontend via SSE
↓
Frontend displays formatted content in tabs
```

---

## ✨ What's Included in Running Servers

### Backend (uvicorn on 8000)
- ✅ FastAPI application
- ✅ 7 AI agents
- ✅ Multi-provider LLM routing (Gemini/OpenAI/Claude/Mock)
- ✅ SSE streaming
- ✅ REST API endpoints
- ✅ Async orchestration
- ✅ CORS configuration

### Frontend (Vite dev server on 3001)
- ✅ React 18 application
- ✅ Modern gradient UI
- ✅ Tabbed dashboard
- ✅ EventSource SSE consumer
- ✅ Framer Motion animations
- ✅ Tailwind CSS styling
- ✅ Action buttons
- ✅ Error handling

---

## 🚨 Troubleshooting

### Backend won't start on 8000
**Problem:** "Port 8000 is already in use"  
**Solution:** Kill existing Python process or use different port

### Frontend won't start on 3001
**Problem:** "Port 3001 is in use"  
**Solution:** Kill existing node process or it will auto-increment to 3002, 3003, etc.

### API requests failing
**Problem:** "Cannot reach http://localhost:8000"  
**Solution:** Check backend is running, check firewall, check port with netstat

### Frontend shows blank page
**Problem:** No campaign topic entered or error in console  
**Solution:** Open browser DevTools (F12), check console for errors

### Campaign stream not updating
**Problem:** Messages aren't appearing in real-time  
**Solution:** Check browser console, verify EventSource connection, restart servers

---

## 📞 Need Help?

See the comprehensive documentation:
- **README.md** - Full setup & API docs
- **QUICKSTART.md** - 5-minute setup
- **IMPLEMENTATION_SUMMARY.md** - Architecture overview
- **DEPLOYMENT.md** - Production deployment
- **COMPLETION_REPORT.md** - Feature checklist
- **PROJECT_STATUS.md** - Project overview

---

**Status Report Generated:** Session Completion  
**Servers Status:** ✅ Both Running  
**Application Ready:** ✅ Yes, open http://localhost:3001

