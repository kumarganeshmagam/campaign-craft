# 🔌 Gemini Integration - Architecture Diagram

## Before vs After

### BEFORE (Mock Responses)
```
┌─────────────────┐
│   Frontend UI   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Backend API     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Research Agent  │
└────────┬────────┘
         │
         ↓
    [MOCK RESPONSE]
    Generic text
    No intelligence
```

### AFTER (Real Gemini API)
```
┌─────────────────┐
│   Frontend UI   │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────┐
│   Backend API (/docs)       │
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│ Research Agent              │
│ - Parse query (with Gemini) │
│ - Research companies        │
│ - Confidence scoring        │
└────────┬────────────────────┘
         │
         ↓
    ┌─────────────────┐
    │  Gemini API     │ ← Real Intelligence
    │  - Real analysis│
    │  - JSON mode    │
    │  - Confidence   │
    └─────────────────┘
         ↓
┌─────────────────────────────┐
│ Real Response from Gemini   │
│ {                           │
│   "companies": [            │
│     {                       │
│       "name": "OpenAI",     │
│       "industry": "AI/ML",  │
│       "confidence": 0.92    │
│     }                       │
│   ]                         │
│ }                           │
└─────────────────────────────┘
```

---

## Data Flow

### Request Flow
```
1. User/Frontend
   │
   ├─→ POST /api/start-campaign
   │   └─→ {"topic": "SaaS companies"}
   │
   ↓
2. Backend (main.py)
   │
   ├─→ Create campaign_id
   ├─→ Queue message
   │
   ↓
3. _orchestrate_campaign()
   │
   ├─→ Research Agent
   │   ├─→ Parse query with Gemini
   │   ├─→ Research with Gemini
   │   └─→ Return real data
   │
   ↓
4. Send to SSE stream
   │
   ↓
5. Frontend receives real data
```

### API Layer
```
┌─────────────────────────────┐
│   FastAPI App               │
├─────────────────────────────┤
│ POST /api/start-campaign    │
│ GET  /api/stream/{id}       │
│ POST /api/generate-content  │
├─────────────────────────────┤
│ Backend Tasks               │
├─────────────────────────────┤
│ async def _orchestrate()    │
│ async def generate_content()│
└─────────────────────────────┘
         ↓↓↓
┌─────────────────────────────┐
│   Agent Router              │
├─────────────────────────────┤
│ ResearchAgent               │
│ StakeholderAgent            │
│ UseCaseAgent                │
│ ProposalAgent               │
│ OutreachAgent               │
│ CampaignManager             │
└─────────────────────────────┘
         ↓↓↓
┌─────────────────────────────┐
│   AI Provider Controller    │
├─────────────────────────────┤
│ generate_text()             │
│ generate_json()             │
│ test_connection()           │
└─────────────────────────────┘
         ↓↓↓
┌─────────────────────────────┐
│   Gemini Orchestrator       │
├─────────────────────────────┤
│ Real API calls              │
│ JSON mode                   │
│ Error handling              │
│ Logging                     │
└─────────────────────────────┘
         ↓↓↓
     GEMINI API
   (Real Intelligence)
```

---

## Component Overview

### 1. Research Agent
```
┌────────────────────────────────┐
│   Research Agent               │
├────────────────────────────────┤
│                                │
│ execute(task)                  │
│  ├─→ _parse_criteria_with_gemini()
│  │   └─→ Gemini parses query
│  │
│  ├─→ _research_companies_with_gemini()
│  │   ├─→ Gemini generates data
│  │   ├─→ Returns JSON with companies
│  │   └─→ Each has confidence score
│  │
│  └─→ Return results
│
└────────────────────────────────┘
         ↓
    Real company data
    with confidence
```

### 2. Gemini Orchestrator
```
┌────────────────────────────────┐
│  GeminiOrchestrator            │
├────────────────────────────────┤
│                                │
│ generate_text(prompt)          │
│  ├─→ Initialize Gemini API
│  ├─→ Configure parameters
│  ├─→ Call generate_content()
│  ├─→ Extract text
│  └─→ Return response
│
│ generate_json(prompt)          │
│  ├─→ Call generate_text()
│  ├─→ Parse JSON
│  ├─→ Validate schema
│  └─→ Return structured data
│
│ test_connection()              │
│  ├─→ Call simple prompt
│  ├─→ Check response
│  └─→ Return success/fail
│
└────────────────────────────────┘
```

### 3. AI Provider Controller
```
┌────────────────────────────────┐
│  AI Provider Controller        │
├────────────────────────────────┤
│                                │
│ generate_text(prompt)          │
│  ├─→ Check AI_PROVIDER env
│  ├─→ Route to provider
│  │   (gemini/openai/claude)
│  └─→ Return response
│
│ generate_json(prompt)          │
│  ├─→ Route to provider
│  ├─→ Parse JSON
│  └─→ Return structured
│
│ test_connection()              │
│  ├─→ Check all providers
│  └─→ Return status
│
└────────────────────────────────┘
```

---

## Configuration Flow

### .env File
```
GEMINI_API_KEY=abc123xyz...
    │
    ↓
GeminiOrchestrator._initialize()
    │
    ├─→ genai.configure(api_key)
    │
    ↓
Ready for API calls
```

### Environment Variables
```
┌─────────────────┐
│ .env file       │
├─────────────────┤
│ GEMINI_API_KEY  │ ← Your key
│ AI_PROVIDER     │ ← "gemini"
│ DATABASE_URL    │ ← Optional
│ HOST            │ ← Optional
│ PORT            │ ← Optional
│ LOG_LEVEL       │ ← Optional
└─────────────────┘
     ↓
load_dotenv()
     ↓
os.getenv("GEMINI_API_KEY")
```

---

## API Response Flow

### 1. Request
```json
POST /api/start-campaign
{
  "topic": "SaaS companies with $50M+ revenue"
}
```

### 2. Backend Processing
```
Campaign created
  │
  ├─→ WebScraper Agent (v1)
  ├─→ Planner Agent (v1)
  ├─→ Formatter Agent (v1)
  ├─→ UseCase Agent (v1)
  ├─→ TargetFinder Agent (v1)
  ├─→ Content Agent (v1)
  │
  └─→ Research Agent (v2 - Real Gemini) ← NEW
      ├─→ Parse with Gemini
      ├─→ Research with Gemini
      └─→ Real data returned
```

### 3. Response (SSE Stream)
```json
{
  "type": "result",
  "agent": "ResearchAgent",
  "data": {
    "companies": [
      {
        "name": "Slack",
        "industry": "SaaS",
        "revenue": "$100M+",
        "confidence_score": 0.89,
        "description": "..." (from Gemini)
      }
    ],
    "source": "Gemini API"
  }
}
```

---

## Error Handling Flow

### Missing API Key
```
Application Start
  │
  ├─→ GeminiOrchestrator._initialize()
  │
  ├─→ Check GEMINI_API_KEY
  │
  ├─→ Not found!
  │
  ├─→ Raise ValueError with helpful message:
  │   "GEMINI_API_KEY not set. Get key at ..."
  │
  └─→ Error message shown to user
```

### API Call Error
```
generate_text() called
  │
  ├─→ Try: genai.generate_content()
  │
  ├─→ Except Exception
  │
  ├─→ Log error with context
  │
  ├─→ Return error response
  │   {
  │     "status": "error",
  │     "error": "API error details"
  │   }
  │
  └─→ Caller handles gracefully
```

---

## Testing Flow

### test_gemini.py
```
1. Test Gemini Connection
   │
   ├─→ Import GeminiOrchestrator
   ├─→ generate_text("...") 
   ├─→ Check response
   └─→ ✓ Pass or ✗ Fail

2. Test JSON Mode
   │
   ├─→ generate_text("...", json_mode=True)
   ├─→ Parse JSON
   └─→ ✓ Pass or ✗ Fail

3. Test Research Agent
   │
   ├─→ Create agent
   ├─→ Execute with query
   ├─→ Verify real data
   └─→ ✓ Pass or ✗ Fail
```

---

## Request/Response Cycle

```
┌──────────────┐
│ Client/User  │
└──────┬───────┘
       │ HTTP POST
       ↓
┌──────────────────────────────────┐
│ FastAPI Backend (port 8000)      │
│                                  │
│ POST /api/start-campaign         │
│ {topic: "SaaS companies"}        │
└──────┬───────────────────────────┘
       │
       ↓ Create Queue & Task
┌──────────────────────────────────┐
│ Background Task                  │
│ _orchestrate_campaign()          │
└──────┬───────────────────────────┘
       │
       ├──→ WebScraperAgent (v1)
       ├──→ PlannerAgent (v1)
       ├──→ FormatterAgent (v1)
       ├──→ UseCaseAgent (v1)
       ├──→ TargetFinderAgent (v1)
       ├──→ ContentAgent (v1)
       │
       └──→ ResearchAgent (v2 - REAL GEMINI)
           │
           ├─→ parse_criteria_with_gemini()
           │  └─→ GEMINI API ← Real call
           │
           ├─→ research_companies_with_gemini()
           │  └─→ GEMINI API ← Real call
           │
           └─→ Return real data
       │
       ↓ Put results in queue
┌──────────────────────────────────┐
│ SSE Stream                       │
│ GET /api/stream/{campaign_id}    │
└──────┬───────────────────────────┘
       │ Streaming JSON
       ↓
┌──────────────────────────────────┐
│ Browser/Client                   │
│ Receives real data in real-time  │
└──────────────────────────────────┘
```

---

## Technology Stack

```
┌────────────────────────────────┐
│    Frontend (Not shown)        │
└────────────────────────────────┘
              │
              ↓
┌────────────────────────────────┐
│  Backend Layer                 │
├────────────────────────────────┤
│ • FastAPI - Web framework      │
│ • Uvicorn - ASGI server        │
│ • Pydantic - Validation        │
└────────────────────────────────┘
              │
              ↓
┌────────────────────────────────┐
│  Agent Layer                   │
├────────────────────────────────┤
│ • Research Agent (Real Gemini) │
│ • Stakeholder Agent            │
│ • UseCase Agent                │
│ • Proposal Agent               │
│ • Outreach Agent               │
│ • Campaign Manager             │
└────────────────────────────────┘
              │
              ↓
┌────────────────────────────────┐
│  LLM Layer                     │
├────────────────────────────────┤
│ • AI Provider Controller       │
│ • Gemini Orchestrator (REAL)   │
│ • OpenAI Orchestrator (mock)   │
│ • Claude Orchestrator (mock)   │
└────────────────────────────────┘
              │
              ↓
         GEMINI API
      (Google Cloud)
```

---

## Sequence Diagram

### Research Query Flow
```
User                Backend              Agent              Gemini API
│                     │                   │                   │
├─ POST Request ─────→│                   │                   │
│                     │                   │                   │
│                     ├─ Create Campaign ─│                   │
│                     │                   │                   │
│  ← Campaign ID ─────┤                   │                   │
│                     │                   │                   │
│                     ├─ Parse Query ────→│                   │
│                     │                   ├─ API Call ───────→│
│                     │                   │                   │
│                     │                   │ ← Parse Result ───┤
│                     │                   │                   │
│                     ├─ Research ───────→│                   │
│                     │                   ├─ API Call ───────→│
│                     │                   │                   │
│                     │                   │ ← Company Data ───┤
│                     │                   │                   │
│                     │ ← Real Data ──────┤                   │
│                     │                   │                   │
│ ← SSE Stream ───────┤                   │                   │
│   (Real Results)    │                   │                   │
```

---

## Summary

✅ **Frontend** → Sends query  
✅ **Backend** → Routes to Agent  
✅ **Agent** → Calls Gemini API  
✅ **Gemini** → Returns real intelligence  
✅ **Backend** → Streams to frontend  
✅ **Frontend** → Shows real data  

**No mock responses. Pure Gemini intelligence. 🚀**
