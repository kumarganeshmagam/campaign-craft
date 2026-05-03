# CampaignCraft

An AI-powered sales & marketing campaign generator. Input a topic, and CampaignCraft automatically generates campaign plans, use cases, target contacts, and outreach content using modular AI agents and multi-provider LLM support.

## ✨ Features

- **� AI-Driven Campaign Generation**: Automatic campaign planning with timelines, strategies, and goals
- **💡 Use Case Generation**: Relevant use cases with value propositions
- **🎯 Target Contact Discovery**: Find and display public contacts (extensible design)
- **📄 Proposal & Email Generation**: Create outreach templates and copy
- **🔄 Real-time SSE Streaming**: Watch agent progress in real-time
- **🧩 Modular AI Agents**: 7 specialized agents for different tasks
- **🌐 Multi-AI Provider Support**: Google Gemini (default), OpenAI GPT, Anthropic Claude
- **📊 Tabbed Dashboard**: Organized campaign data in Plan, Use Cases, Contacts, and Proposals tabs

## 🏗️ Architecture

### AI Agents

1. **WebScraperAgent** — Analyzes web content and identifies competitors
2. **CampaignPlannerAgent** — Creates strategic campaign plans with timelines
3. **StrategyFormatterAgent** — Formats all agent data into human-readable summaries
4. **UseCaseAgent** — Generates relevant use cases with value propositions
5. **PitchAgent** — Creates multiple pitch variants
6. **ContentAgent** — Generates DMs, emails, social posts
7. **TargetFinderAgent** — Discovers public contacts (simulated, extensible)

### Multi-Provider AI Routing

```
Agent → AgentRouter → AIProviderController → [GeminiOrchestrator | GPTOrchestrator | ClaudeOrchestrator]
```

## 📋 Prerequisites

- **Python 3.10+** (backend)
- **Node.js 16+** (frontend)
- **npm** or **yarn**

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional, uses mock by default)
# Create .env file with:
# AI_PROVIDER=gemini
# GEMINI_API_KEY=your_key_here

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start dev server
npm run dev
```

### 3. Access Application

Open **http://localhost:3001** in your browser

## ⚙️ Configuration

### Environment Variables (.env)

Create `backend/.env`:

```env
# AI Provider (default: gemini)
AI_PROVIDER=gemini

# API Keys (optional, uses mock responses if not provided)
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database (optional, future use)
DATABASE_URL=sqlite:///./campaign_craft.db
```

### Getting API Keys

1. **Google Gemini**: https://makersuite.google.com/app/apikey
2. **OpenAI GPT**: https://platform.openai.com/account/api-keys
3. **Anthropic Claude**: https://console.anthropic.com/account/keys

### Switching AI Providers

```env
# Use Gemini (default)
AI_PROVIDER=gemini

# Use OpenAI
AI_PROVIDER=openai

# Use Claude
AI_PROVIDER=claude

# Use Mock (no API key needed)
AI_PROVIDER=mock
```

## 📖 Usage

1. **Enter Campaign Topic**: Type a topic (e.g., "AI automation in retail")
2. **Start Campaign**: Click "Start Campaign" button
3. **View Results**:
   - **Plan Tab**: Campaign timeline, channels, and goals
   - **Use Cases Tab**: Generated use cases with refinement buttons
   - **Target Contact List Tab**: Table of contacts with action buttons
   - **Proposals Tab**: Email templates and copy
4. **Generate Content**: Click "Generate Campaign Content" to create emails
5. **Copy & Send**: Use "Copy Email" or other action buttons

## 🔌 API Reference

### POST /api/start-campaign
Start a new campaign

**Request**:
```json
{
  "topic": "AI automation in retail"
}
```

**Response**:
```json
{
  "campaign_id": "uuid-string",
  "stream_url": "/api/stream/{campaign_id}"
}
```

### GET /api/stream/{campaign_id}
Server-Sent Events stream of campaign progress

**Response** (text/event-stream):
```
data: {"type": "status", "agent": "WebScraperAgent", "message": "..."}
data: {"type": "result", "agent": "CampaignPlannerAgent", "data": {...}}
data: {"type": "complete", "message": "Campaign orchestration complete."}
```

### POST /api/generate-content
Trigger content generation

**Request**:
```json
{
  "campaign_id": "uuid-string",
  "usecase_id": "optional-uuid"
}
```

**Response**:
```json
{
  "status": "ok"
}
```

### POST /api/chat (Future)
Interactive campaign refinement

## 📁 Project Structure

```
campaign-craft/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI routes
│   │   ├── agents/
│   │   │   ├── webscraper.py
│   │   │   ├── planner.py
│   │   │   ├── formatter.py           # ⭐ Formats agent outputs
│   │   │   ├── usecase.py
│   │   │   ├── pitch.py
│   │   │   ├── content.py
│   │   │   └── targetfinder.py
│   │   ├── controllers/
│   │   │   └── ai_provider.py         # ⭐ Routes to providers
│   │   ├── orchestrators/
│   │   │   ├── gemini_orchestrator.py
│   │   │   ├── gpt_orchestrator.py
│   │   │   └── claude_orchestrator.py
│   │   ├── router/
│   │   │   └── agent_router.py        # ⭐ Dispatches agents
│   │   └── utils/
│   │       └── sse.py
│   ├── requirements.txt
│   └── .env (create this)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Main app & landing
│   │   ├── components/
│   │   │   └── ChatUI.jsx             # Tabbed dashboard
│   │   ├── index.css                  # Tailwind
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 🛠️ Development

### Adding a New AI Provider

1. Create `backend/app/orchestrators/myprovider_orchestrator.py`:

```python
class MyProviderOrchestrator:
    @staticmethod
    async def generate_text(prompt: str, stream=False, **kwargs) -> str:
        # Call your API
        return "response"
```

2. Update `backend/app/controllers/ai_provider.py`:

```python
if prov == "myprovider":
    from app.orchestrators.myprovider_orchestrator import MyProviderOrchestrator
    return await MyProviderOrchestrator.generate_text(prompt, stream=stream, **kwargs)
```

3. Set in `.env`:

```env
AI_PROVIDER=myprovider
MYPROVIDER_API_KEY=your_key
```

### Adding a New Agent

1. Create `backend/app/agents/myagent.py`:

```python
async def run_agent(input_data: dict, queue=None) -> dict:
    if queue:
        await queue.put({"type": "progress", "agent": "MyAgent", "message": "Starting..."})
    
    # Your logic
    result = {"data": "..."}
    
    if queue:
        await queue.put({"type": "progress", "agent": "MyAgent", "message": "Complete."})
    
    return result
```

2. Register in `backend/app/router/agent_router.py`:

```python
if agent_name == "myagent":
    from app.agents.myagent import run_agent as myagent
    return await myagent(payload, queue)
```

3. Use in `backend/app/main.py`:

```python
result = await AgentRouter.run_agent("myagent", {...}, q)
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused to localhost:8000 | Ensure backend is running on port 8000 |
| Module 'vite' not found | Run `npm install --legacy-peer-deps` in frontend |
| Getting mock responses with AI_PROVIDER=gemini | Add GEMINI_API_KEY to .env and restart backend |
| SSE not connecting | Check CORS headers, verify /api/stream/{id} returns event-stream |
| Frontend won't start on port 3001 | It will automatically use 3002, 3003, etc. if port is busy |

## 🚧 Future Roadmap

- [ ] Database persistence (SQLite/PostgreSQL)
- [ ] Real AI provider integration with streaming
- [ ] User authentication & multi-tenant support
- [ ] Campaign templates library
- [ ] A/B testing for proposals
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] Email sending integration
- [ ] Campaign analytics dashboard
- [ ] Mobile app version

## 📄 License

MIT

## 💬 Support

Found a bug or have a feature request? Open an issue!

---

**Built with ❤️ using FastAPI, React, Vite, and Tailwind CSS**