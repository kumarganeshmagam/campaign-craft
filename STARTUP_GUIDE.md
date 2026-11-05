# CampaignCraft - Complete Startup Guide

## Quick Start

### Option 1: Batch File (Windows)
```bash
start_all.bat
```

### Option 2: PowerShell
```powershell
.\start_all.ps1
```

### Option 3: Python (Cross-platform)
```bash
python startup.py
```

## What Happens During Startup

1. **Port Cleanup**: Kills any processes running on ports 8000 and 3000
2. **Backend Start**: Starts FastAPI server on `http://127.0.0.1:8000`
3. **Frontend Start**: Starts Vite dev server on `http://localhost:3000`
4. **Health Check**: Verifies both services are running
5. **E2E Tests**: Runs Playwright tests to verify the full flow
6. **Real-time Logs**: All output is logged to files in the `logs/` directory

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## Log Files

All logs are written to the `logs/` directory:

- `startup.log` - Master startup process log
- `backend_startup.log` - Backend server logs
- `frontend_startup.log` - Frontend dev server logs  
- `test_results.log` - E2E test results
- `backend.log` - Backend application logs (from app runtime)
- `api.log` - API request/response logs
- `agents.log` - AI agent logs
- `errors.log` - Error logs

### Viewing Logs

#### Using the Log Viewer
```bash
python view_logs.py
```

Interactive menu to view and monitor all logs.

#### Using Command Line
```bash
# View backend logs
python view_logs.py backend

# View test results
python view_logs.py tests

# List all logs
python view_logs.py list
```

#### Using Tail Command
```bash
# Last 50 lines of backend log
tail -50 logs/backend_startup.log

# Follow backend log in real-time
tail -f logs/backend_startup.log
```

## Understanding the Flow

```
User Opens http://localhost:3000
    ↓
React Frontend Loads
    ↓
User Enters Campaign Topic
    ↓
Frontend POST /api/start-campaign
    ↓
Backend Processes with Gemini AI
    ↓
Server-Sent Events Stream Response
    ↓
Frontend Displays Real-time Results
```

## Troubleshooting

### Backend Won't Start
- Check `logs/backend_startup.log` for errors
- Verify port 8000 is free: `netstat -ano | findstr :8000`
- Check `.env` file has valid `GEMINI_API_KEY`

### Frontend Won't Start
- Check `logs/frontend_startup.log` for errors
- Verify port 3000 is free: `netstat -ano | findstr :3000`
- Ensure `npm install` has been run: `cd frontend && npm install`

### Tests Failing
- Check `logs/test_results.log` for details
- Verify both backend and frontend are running
- Check browser console for JavaScript errors

### API Quota Exceeded
- The Gemini API free tier has a 2-request/minute limit
- Wait ~1 minute before sending another request
- Consider upgrading to a paid API plan

## Features

✅ **Real Gemini AI Integration** - Not mock data
✅ **Full Logging** - All events logged to files
✅ **E2E Testing** - Playwright tests verify full flow
✅ **Automatic Port Cleanup** - No manual process killing
✅ **Real-time Streaming** - Server-Sent Events for live updates
✅ **Log Viewer** - Easy access to all logs

## Environment Variables

Create `.env` file in the backend directory:

```
GEMINI_API_KEY=your-api-key-here
AI_PROVIDER=gemini
```

Get your Gemini API key at: https://makersuite.google.com/app/apikey

## Development

### Backend
- FastAPI for API
- Gemini API for AI
- SQLAlchemy for database
- Python logging for monitoring

### Frontend  
- React 18
- Vite for bundling
- Framer Motion for animations
- Tailwind CSS for styling

### Testing
- Playwright for E2E tests
- Pytest for test framework
- Real browser automation

## Dependencies

### Backend
```
fastapi>=0.105.0
uvicorn[standard]==0.22.0
google-generativeai==0.5.4
langchain-google-genai==0.0.8
pytest==7.4.3
pytest-asyncio==0.21.1
playwright==1.42.0
```

### Frontend
```
react@18.2.0
react-dom@18.2.0
vite@4.5.0
framer-motion@10.12.16
```

## Stopping the Application

Press `Ctrl+C` in the terminal where `startup.py` is running.

The script will:
1. Stop the backend server
2. Stop the frontend dev server
3. Print shutdown message
4. Exit cleanly

## Performance Tips

1. **Monitor Logs**: Use `python view_logs.py` to monitor health
2. **Check Errors**: Review `logs/errors.log` for issues
3. **API Usage**: Watch `logs/api.log` for request patterns
4. **Agent Logs**: Check `logs/agents.log` for AI processing details
