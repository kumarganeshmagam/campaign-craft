# CampaignCraft - Quick Start Guide

## 🚀 5-Minute Setup

### Start Backend (Terminal 1)

```powershell
# Navigate to backend
Set-Location -Path 'e:\AI\campaign-craft\backend'

# Activate venv
.\.venv\Scripts\Activate.ps1

# Start FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Start Frontend (Terminal 2)

```powershell
# Navigate to frontend
Set-Location -Path 'e:\AI\campaign-craft\frontend'

# Start Vite dev server
npm run dev
```

Expected output:
```
VITE v4.5.0  ready in XXX ms
➜  Local:   http://localhost:3001/
```

### Open Application

**http://localhost:3001** ← Click here!

---

## 📝 Example Workflow

### Step 1: Enter a Campaign Topic

In the search bar, type:
```
AI automation in retail
```

### Step 2: Start Campaign

Click **"Start Campaign"** button

You'll see:
- ✅ Real-time agent progress messages
- 📊 Campaign plan generation
- 💡 Use case creation
- 🎯 Target contact discovery
- 📧 Email/proposal generation

### Step 3: Explore Tabs

**Plan Tab 🧠**
- Timeline: Weekly campaign activities
- Channels: Email, LinkedIn, Twitter
- Goals: Target metrics (meetings, responses)

**Use Cases Tab 💡**
- See generated use cases
- Click "Generate Pitch" to refine

**Target Contact List Tab 🎯**
- Table of discovered contacts
- "Start Contact" button to begin outreach
- "Generate Message" to create personalized copy

**Proposals Tab 📄**
- Email templates ready to send
- Click "Copy Email" to clipboard

### Step 4: Generate Campaign Content

Click **"Generate Campaign Content"** button to:
- Trigger ContentAgent for emails/DMs
- Run StrategyFormatterAgent to combine all data
- See formatted output in chat

### Step 5: Copy & Send

- Click "Copy Email" on any proposal
- Paste into Gmail or CRM
- Or click action buttons for "Start Contact"

---

## 🔧 Configure AI Provider

### Default: Mock Mode (No API Key Needed)

Works out of the box! Returns simulated responses.

### Use Google Gemini

1. Get API key: https://makersuite.google.com/app/apikey

2. Create `backend/.env`:
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

3. Restart backend

### Use OpenAI

1. Get API key: https://platform.openai.com/account/api-keys

2. Create `backend/.env`:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

3. Restart backend

### Use Claude

1. Get API key: https://console.anthropic.com/account/keys

2. Create `backend/.env`:
```env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your_key_here
```

3. Restart backend

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to localhost:8000" | Check backend terminal - ensure server is running |
| Frontend won't start | Run `npm install --legacy-peer-deps` in frontend folder |
| Getting mock responses | Add API key to `.env` and restart backend |
| SSE not streaming | Refresh browser (F5) and try starting a new campaign |
| Port 3001 in use | Vite will automatically try 3002, 3003, etc. |

---

## 📊 What Each Agent Does

| Agent | Input | Output | Purpose |
|-------|-------|--------|---------|
| **WebScraper** | Topic | Keywords, insights, competitors | Analyze market |
| **CampaignPlanner** | Scraper output | Timeline, channels, goals | Create strategy |
| **Formatter** | All agent data | Readable summary + structured sections | Display to user |
| **UseCase** | Topic | Use cases with value props | Show benefits |
| **Pitch** | Use case | Short/persuasive/technical variants | Refine message |
| **Content** | Use case + targets | Emails, DMs, social posts | Create outreach |
| **TargetFinder** | Topic | Contact list (simulated) | Find prospects |

---

## 🎯 Next Steps

### Immediate
- [ ] Test with different campaign topics
- [ ] Try all 4 tabs and buttons
- [ ] Click "Generate Campaign Content" multiple times
- [ ] Check browser console (F12) for any errors

### Soon
- [ ] Add your own API key for real AI responses
- [ ] Deploy to production (Heroku, AWS, etc.)
- [ ] Connect to CRM (Salesforce, HubSpot)
- [ ] Add email sending integration

### Advanced
- [ ] Modify agents in `backend/app/agents/`
- [ ] Add new orchestrators in `backend/app/orchestrators/`
- [ ] Customize frontend tabs
- [ ] Add database persistence

---

## 📚 Useful Files

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI routes & orchestration |
| `backend/app/agents/*.py` | AI agent implementations |
| `backend/app/controllers/ai_provider.py` | Provider routing |
| `frontend/src/App.jsx` | Landing page & campaign start |
| `frontend/src/components/ChatUI.jsx` | Tabbed dashboard |
| `.env.example` | Environment template |
| `README.md` | Full documentation |

---

## 💡 Pro Tips

1. **Faster Testing**: Use mock mode (default) - no API keys needed
2. **Real Responses**: Add API key, set provider, restart backend
3. **Debug**: Open F12 browser console to see network calls
4. **SSE Logs**: Backend terminal shows agent progress
5. **Copy Output**: All formatted text can be copied to clipboard

---

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **React**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **Vite**: https://vitejs.dev
- **Framer Motion**: https://www.framer.com/motion

---

## 📞 Need Help?

1. Check the main **README.md** for detailed docs
2. Look at **Troubleshooting** section above
3. Check backend terminal for error messages
4. Open browser console (F12) for frontend errors
5. Review agent implementations in `backend/app/agents/`

---

**Happy campaigning! 🚀**
