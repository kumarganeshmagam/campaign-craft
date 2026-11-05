# ⚡ Quick Command Reference - Gemini Integration

## 🔑 Get Your API Key (2 minutes)

```
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
```

## ⚙️ Setup (3 minutes)

### 1. Add API Key to `.env`
```
GEMINI_API_KEY=your_key_here
```

### 2. Install Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

### 3. Test Connection
```powershell
python test_gemini.py
```

Should see: `✓ All tests passed!`

## 🚀 Run Backend

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Expected:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## 🧪 Test API

### Option 1: Browser
```
http://localhost:8000/docs
```
Interactive API documentation

### Option 2: PowerShell
```powershell
# Start campaign with research
$body = @{
    topic = "AI SaaS companies with $50M+ revenue"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/start-campaign" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body

# Get campaign ID
$campaignId = $response.campaign_id

# View results (replace with your campaign ID)
http://localhost:8000/api/stream/$campaignId
```

### Option 3: cURL
```bash
curl -X POST http://localhost:8000/api/start-campaign \
  -H "Content-Type: application/json" \
  -d '{"topic": "Enterprise AI startups"}'
```

## 📋 File Checklist

```
backend/
├── .env                                    # ← ADD YOUR API KEY HERE
├── requirements.txt                        # ✓ Updated with Gemini packages
├── test_gemini.py                         # ✓ Run to verify
├── app/
│   ├── controllers/
│   │   └── ai_provider.py                # ✓ Routes to real API
│   ├── orchestrators/
│   │   └── gemini_orchestrator.py        # ✓ Real Gemini integration
│   └── agents/
│       └── research_agent.py             # ✓ Uses real Gemini
```

## 🐛 Troubleshooting

### API key not working?
```
1. Go to https://makersuite.google.com/app/apikey
2. Get a fresh key
3. Update backend/.env
4. Run: python test_gemini.py
```

### Import errors?
```powershell
pip install --upgrade google-generativeai langchain-google-genai
```

### Port 8000 already in use?
```powershell
python -m uvicorn app.main:app --reload --port 8001
```

### Still getting mock responses?
```
Verify .env has GEMINI_API_KEY set
Run: python test_gemini.py
Check logs for errors
```

## 📊 What You Get Now

- ✅ Real Gemini API calls
- ✅ Zero mock responses
- ✅ Intelligent company research
- ✅ Confidence scoring
- ✅ Full error handling
- ✅ Production-ready code

## 📚 Documentation

| File | Purpose |
|------|---------|
| `GEMINI_SETUP.md` | Detailed setup guide |
| `GEMINI_INTEGRATION_COMPLETE.md` | Complete integration info |
| `test_gemini.py` | Verification script |

## 🎯 Next Steps

1. ✓ Get API key from https://makersuite.google.com/app/apikey
2. ✓ Add to `backend/.env`
3. ✓ Run `pip install -r requirements.txt`
4. ✓ Run `python test_gemini.py`
5. ✓ Start backend with `uvicorn`
6. ✓ Test at `http://localhost:8000/docs`

## 💡 Key Code Examples

### Python: Research Agent
```python
from app.agents.research_agent import ResearchAgent

agent = ResearchAgent()
result = await agent.execute({
    "query": "B2B SaaS companies",
    "max_companies": 5
})

# Real data from Gemini
print(result["companies"])
```

### Python: Direct Gemini
```python
from app.controllers import ai_provider

response = await ai_provider.generate_text("What are top AI companies?")
print(response)  # Real response, not mock
```

### Bash: API Call
```bash
curl -X POST http://localhost:8000/api/start-campaign \
  -H "Content-Type: application/json" \
  -d '{"topic": "SaaS startups"}'
```

## 🚨 Important

- **NEVER commit `.env` to git** - Add to .gitignore
- **API costs money** - Use free tier wisely
- **Rate limits** - Free tier has limits, respectable for testing
- **Keep key secret** - Regenerate if exposed

## ✅ Success Indicators

✓ `python test_gemini.py` passes  
✓ Backend starts without errors  
✓ `/docs` shows interactive API  
✓ Real company data in responses  
✓ No `[MOCK]` text in outputs  

---

**Status: Ready to Use!** 🎉
