# CampaignCraft v2.0 - Agentic Orchestration System

## 🚀 Major Upgrade Overview

This is a complete transformation of CampaignCraft from a basic campaign generator into a **fully autonomous multi-agent orchestration system**. The system now uses **LangGraph** to orchestrate 6 specialized AI agents that autonomously research companies, identify stakeholders, generate use cases, create proposals, and draft outreach content—all with human-in-the-loop approval gates.

**Key Improvements:**
- ✅ 6 specialized autonomous agents
- ✅ LangGraph state machine orchestration
- ✅ Human-in-the-loop approval gates
- ✅ Comprehensive agent reasoning trails
- ✅ Production-grade database schema
- ✅ Real-time agent activity monitoring
- ✅ Multi-channel outreach (email, LinkedIn, calls)

---

## 📋 System Architecture

### Agent Orchestration Flow

```
User Query
    ↓
[Campaign Manager Agent] ← Orchestrates workflow
    ├→ [Research Agent] → Finds companies
    │   ↓ (Gate 1: Approve companies)
    ├→ [Stakeholder Agent] → Finds decision-makers
    ├→ [Use Case Agent] → Generates use cases
    │   ↓ (Gate 2: Select use cases)
    ├→ [Proposal Agent] → Creates variants
    ├→ [Outreach Agent] → Generates content
    │   ↓ (Gate 3: Review outreach)
    ↓
Campaign Ready for Execution
```

### 6 Autonomous Agents

#### 1. **Research Agent**
**Purpose:** Find and profile target companies
- **Inputs:** Query (e.g., "top 5 financial institutes $1B+ revenue")
- **Tools:** Web search (DuckDuckGo, Google), web scraper (Firecrawl, Playwright)
- **Process:**
  - Parse query criteria (industry, size, location, revenue)
  - Search for matching companies
  - Scrape company websites and financial data
  - Extract: name, revenue, employees, tech stack, pain points, news
  - Rank by relevance to query criteria
- **Output:** Structured company profiles with confidence scores

#### 2. **Stakeholder Intelligence Agent**
**Purpose:** Identify and profile decision-makers
- **Inputs:** Company profiles from Research Agent
- **Tools:** LinkedIn scraper, Apollo.io, Hunter.io, web search
- **Process:**
  - Search for C-suite, VPs, directors in each company
  - Extract: name, title, email, LinkedIn, Twitter
  - Identify recent posts and interests
  - Score by seniority and accessibility
- **Output:** Prioritized contact list per company

#### 3. **Use Case Generation Agent**
**Purpose:** Create contextual use cases matching services to company needs
- **Inputs:** Company profiles, services catalog
- **Tools:** LLM analysis, industry trend research
- **Process:**
  - Analyze company's industry, size, tech stack, pain points
  - Match services to challenges
  - Generate 3-5 specific, contextualized use cases
  - Calculate value potential and relevance
- **Output:** Ranked use cases with ROI estimates

#### 4. **Proposal Generation Agent**
**Purpose:** Create customized proposal variants
- **Inputs:** Use cases, company context, contact profiles
- **Tools:** LLM generation
- **Process:**
  - For each use case, create 3 variants:
    - **Executive Summary:** 1-page, high-level, for C-suite
    - **Technical Deep-Dive:** Detailed, for technical buyers
    - **ROI-Focused:** Metrics-heavy, for financial decision-makers
  - Personalize based on contact role and seniority
  - Include case studies and proof points
- **Output:** Proposal variants ready for customization

#### 5. **Outreach Content Agent**
**Purpose:** Generate multi-channel outreach content
- **Inputs:** Contacts, proposals, use cases
- **Tools:** LLM generation
- **Process:**
  - Analyze contact profile and interests
  - Generate for each channel:
    - **Email:** Initial + 2 follow-ups (spaced 3-5 days)
    - **LinkedIn:** Connection message + inmail
    - **Call:** Opening, value prop, objection handling, closing
  - Adapt tone based on seniority
  - Include personalization hooks
- **Output:** Ready-to-send outreach content

#### 6. **Campaign Manager Agent** (Orchestrator)
**Purpose:** Coordinate entire workflow
- **Inputs:** All other agents + user approvals
- **Process:**
  - Route tasks to appropriate agents
  - Manage approval gates
  - Handle errors and retries
  - Maintain campaign state
  - Generate reasoning trails
- **Output:** Complete campaign with all components

---

## 🗄️ Database Schema

### New Tables (SQLAlchemy Models)

**campaigns**
- id, name, query, status, created_at, updated_at

**companies**
- id, campaign_id, name, industry, revenue, employees, website
- data_json, pain_points, tech_stack, recent_news
- confidence_score, relevance_score, sources

**contacts**
- id, campaign_id, company_id, name, title, department, email, phone
- linkedin_url, twitter, recent_posts, interests, engagement_signals
- priority_score, confidence_score, seniority_level, sources

**use_cases**
- id, campaign_id, company_id, title, problem_statement, proposed_solution
- expected_roi, value_metrics, implementation_timeline
- relevance_score, confidence_score, conversion_likelihood
- user_approved

**proposals**
- id, campaign_id, use_case_id, variant_type (executive|technical|roi_focused)
- executive_summary, detailed_content, deliverables, pricing_tiers
- case_studies, version, user_approved

**outreach**
- id, campaign_id, contact_id, proposal_id, channel (email|linkedin|call)
- subject, content, personalization_hooks, sequence_step
- status (draft|approved|sent|opened|clicked|replied|bounced)
- engagement_score

**conversations**
- id, campaign_id, entity_type, entity_id, context, messages

**agent_logs**
- id, campaign_id, agent_name, task_input, task_output, reasoning
- tools_used, sources, confidence_score, execution_time, status

**metrics**
- Track success rates per: industry, use_case_type, contact_role, outreach_style

---

## 🔧 New API Endpoints (v2)

All endpoints use `/api/v2` prefix for backward compatibility.

### Campaign Management

```
POST   /api/v2/campaigns
       Create new campaign
       Request: { query, auto_approve?, channels? }
       Response: { campaign_id, stream_url, details_url }

GET    /api/v2/campaigns
       List all campaigns (paginated)

GET    /api/v2/campaigns/{campaign_id}
       Get campaign details

GET    /api/v2/campaigns/{campaign_id}/stream
       Stream campaign progress (Server-Sent Events)
```

### Agent Control

```
GET    /api/v2/campaigns/{campaign_id}/agents
       Get agent activity logs and reasoning

POST   /api/v2/campaigns/{campaign_id}/gates/{stage}/approve
       Approve stage gate

POST   /api/v2/campaigns/{campaign_id}/gates/{stage}/reject
       Reject stage gate

POST   /api/v2/campaigns/{campaign_id}/update
       Update campaign state
```

### Data Retrieval

```
GET    /api/v2/campaigns/{campaign_id}/companies
       Get researched companies

GET    /api/v2/campaigns/{campaign_id}/contacts
       Get identified contacts

GET    /api/v2/campaigns/{campaign_id}/use-cases
       Get generated use cases

GET    /api/v2/campaigns/{campaign_id}/proposals
       Get generated proposals

GET    /api/v2/campaigns/{campaign_id}/outreach
       Get outreach content
```

### Chat Interface

```
POST   /api/v2/campaigns/{campaign_id}/chat
       Chat about campaign strategy

POST   /api/v2/companies/{company_id}/chat
       Chat about specific company

POST   /api/v2/use-cases/{use_case_id}/chat
       Refine use case via chat

POST   /api/v2/proposals/{proposal_id}/chat
       Edit proposal via chat
```

---

## 🎛️ Configuration

### Environment Variables (.env)

```bash
# AI Provider
AI_PROVIDER=openai          # or gemini, claude, mock
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
CLAUDE_API_KEY=your_key

# Database
DATABASE_URL=postgresql://user:password@localhost/campaigncraft
# or SQLite (default):
DATABASE_URL=sqlite:///campaigncraft.db

# Search APIs
BRAVE_SEARCH_API_KEY=your_key      # Web search
SERPAPI_KEY=your_key               # Alternative search

# Scraping
FIRECRAWL_API_KEY=your_key         # Web scraping
# or Playwright for self-hosted scraping

# LinkedIn/Social
APOLLO_API_KEY=your_key            # Contact finding
HUNTER_API_KEY=your_key            # Email finding

# Vector DB (optional)
PINECONE_API_KEY=your_key
PINECONE_INDEX=campaign_index

# CORS
ALLOWED_ORIGINS=http://localhost:3001,http://localhost:5173

# Debug
DEBUG=true
LOG_LEVEL=INFO
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2. Setup Database

```bash
# For PostgreSQL (recommended for production)
# Set DATABASE_URL in .env to your PostgreSQL connection

# For SQLite (development)
# DATABASE_URL will default to sqlite:///campaigncraft.db
```

### 3. Configure AI Provider

```bash
# Copy .env.example to .env
cp .env.example .env

# Add your API keys:
# - OpenAI: OPENAI_API_KEY
# - Google Gemini: GEMINI_API_KEY
# - Anthropic Claude: CLAUDE_API_KEY
```

### 4. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start Frontend

```bash
cd frontend
npm run dev

# Opens on http://localhost:3001 (Vite) or http://localhost:5173
```

---

## 💬 Usage Examples

### Example 1: Create Campaign (with approval gates)

```bash
# Request
POST http://localhost:8000/api/v2/campaigns
Content-Type: application/json

{
  "query": "top 5 financial institutes with $1B+ revenue in past 2 years",
  "auto_approve": false,
  "channels": ["email", "linkedin", "call"]
}

# Response
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "top 5 financial institutes...",
  "status": "initializing",
  "stream_url": "/api/v2/campaigns/550e8400-e29b-41d4-a716-446655440000/stream",
  "details_url": "/api/v2/campaigns/550e8400-e29b-41d4-a716-446655440000"
}
```

### Example 2: Monitor Campaign Progress

```bash
# Stream real-time updates
GET http://localhost:8000/api/v2/campaigns/{campaign_id}/stream

# Response (Server-Sent Events)
data: {"type": "agent_start", "agent": "research", "message": "Starting research..."}
data: {"type": "agent_progress", "agent": "research", "companies_found": 3}
data: {"type": "agent_complete", "agent": "research", "confidence": 0.85}
data: {"type": "gate_request", "stage": "research", "action": "approve_companies"}
```

### Example 3: Approve Stage Gate

```bash
POST http://localhost:8000/api/v2/campaigns/{campaign_id}/gates/research/approve

# Workflow continues automatically
```

### Example 4: Get Campaign Companies

```bash
GET http://localhost:8000/api/v2/campaigns/{campaign_id}/companies

# Response
{
  "campaign_id": "550e8400...",
  "companies": [
    {
      "id": "comp-1",
      "name": "JPMorgan Chase",
      "industry": "Financial Services",
      "revenue": "$31.7B",
      "employees": 316000,
      "confidence_score": 0.92,
      "tech_stack": ["AWS", "Kubernetes", "Python"],
      "pain_points": ["Legacy system modernization", "Real-time data processing"],
      "sources": ["https://crunchbase.com/..."]
    }
  ],
  "total": 1
}
```

### Example 5: Get Agent Reasoning

```bash
GET http://localhost:8000/api/v2/campaigns/{campaign_id}/agents

# Response
{
  "campaign_id": "550e8400...",
  "agents": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "agent": "research",
      "status": "success",
      "reasoning": "Searched for: top 5 financial institutes...",
      "confidence": 0.85,
      "output_count": 5,
      "tools_used": ["google_search", "firecrawl_scraper", "llm_analysis"]
    }
  ]
}
```

---

## 🤖 How Agents Work

### Agent Structure

Each agent follows this pattern:

```python
class AutonomousAgent:
    async def execute(self, task: Dict) -> Dict:
        # 1. UNDERSTAND - Parse task and context
        parsed_task = self.understand_task(task)
        
        # 2. PLAN - Create step-by-step plan
        plan = self.create_plan(parsed_task)
        
        # 3. EXECUTE - Use tools, with self-correction
        results = []
        for step in plan:
            result = self.use_tool(step.tool, step.params)
            if quality_check_fails(result):
                result = self.retry_with_different_approach(step)
            results.append(result)
        
        # 4. SYNTHESIZE - Combine results
        final_output = self.synthesize(results)
        
        # 5. REFLECT - Calculate confidence
        confidence = self.calculate_confidence(final_output)
        reasoning = self.explain_reasoning()
        
        return {
            "output": final_output,
            "confidence": confidence,
            "reasoning": reasoning,
            "tools_used": [...],
            "sources": [...]
        }
```

### Human-in-the-Loop Gates

Gates occur at critical decision points:

**Gate 1: Research Stage**
```
Found 7 companies matching criteria:
- JPMorgan Chase (confidence: 0.92)
- Goldman Sachs (confidence: 0.88)
- ...

[Approve] [Modify] [Reject]
```

**Gate 2: Use Case Selection**
```
Generated 12 use cases from research.
Which to pursue?
- AI Automation (relevance: 0.89) [Select]
- Cloud Migration (relevance: 0.76) [Select]
- ...
```

**Gate 3: Outreach Review**
```
Generated outreach for 5 contacts.
Review before sending?
- [Review Email] [Review LinkedIn] [Review Call]

[Send All] [Edit] [Reject]
```

---

## 📊 Frontend Components (v2.0)

### New Pages

#### 1. Campaign Dashboard
- Create new campaign with query input
- Real-time agent activity timeline
- Agent reasoning logs with expandable details
- Approval gates with accept/reject/modify
- Progress bars for each stage

#### 2. Research Results
- Company cards with:
  - Profile summary
  - Confidence score
  - Tech stack badges
  - Pain points
  - Sources/links
- Filter and sort options

#### 3. Contact Manager
- Contact list with columns:
  - Name, Title, Company, Email, LinkedIn
  - Priority score
  - Engagement signals
- Bulk actions:
  - Select for outreach
  - Generate personalized content
  - Track engagement
- Search and filter

#### 4. Use Case Browser
- Cards showing:
  - Title
  - Problem statement
  - Expected ROI
  - Relevance score
- Click to expand details or edit

#### 5. Proposal Viewer
- Multi-variant display:
  - Executive Summary (1-page)
  - Technical Deep-Dive (detailed)
  - ROI-Focused (metrics-heavy)
- Side-by-side comparison
- Edit in-place or via chat

#### 6. Outreach Console
- Email template editor
- LinkedIn message builder
- Call script player
- A/B test setup
- Send tracking

#### 7. Agent Reasoning Dashboard
- Agent activity timeline (visual timeline)
- Decision logs with reasoning
- Tool usage and results
- Confidence scores
- Alternatives considered

---

## 🔄 Workflow Example: End-to-End

```
1. User enters: "Find financial services companies in SF, $500M+ revenue, using outdated tech"

2. Campaign Manager creates campaign and starts Research Agent

3. Research Agent:
   - Searches Google for SF financial services
   - Identifies 15 candidates
   - Scrapes websites for revenue, employees, tech
   - Filters to 7 matching criteria
   - Returns with 0.82 avg confidence
   
4. GATE 1: Frontend shows 7 companies
   - User reviews and approves
   
5. Stakeholder Intelligence Agent:
   - For each company, searches LinkedIn for C-suite, VPs
   - Finds 4-6 contacts per company
   - Returns 28 total contacts with priority scores
   
6. Use Case Agent:
   - Analyzes each company's stack (legacy systems identified)
   - Generates use cases:
     * "Cloud-native architecture migration"
     * "AI-powered data pipeline"
     * etc.
   - Returns 3-4 per company (21 total)
   
7. GATE 2: Frontend shows use cases
   - User selects top 8 to pursue
   
8. Proposal Agent:
   - For each selected use case, creates 3 variants:
     * Executive (1-page, for C-suite)
     * Technical (detailed architecture, for CTO)
     * ROI (metrics-heavy, for CFO)
   - Returns 24 proposal variants
   
9. Outreach Agent:
   - For each contact, generates personalized content:
     * Email sequence (initial + 2 follow-ups)
     * LinkedIn message + inmail
     * Call script with objection handling
   - Returns ready-to-send content for 28 contacts
   
10. GATE 3: Frontend shows outreach content
    - User reviews tone and personalization
    - Approves to send or edits
    
11. Campaign ready for execution
    - Can now send emails, LinkedIn messages
    - Track opens, clicks, replies
    - Update metrics for learning
```

---

## 📈 Learning & Improvement

The system learns from outcomes:

```python
# Track success metrics
- Email open rate
- Click rate
- Reply rate
- Conversion rate

# By dimensions:
- Industry
- Use case type
- Contact role
- Outreach style
- Time of day sent

# Agents use this to improve:
- Use Case Agent: Rank by historical conversion
- Outreach Agent: Adapt style based on what works
- Stakeholder Agent: Prioritize roles with best outcomes
```

---

## 🐛 Troubleshooting

### Common Issues

**Q: Agent times out during research**
A: Increase timeout or reduce search scope. Check web scraper API limits.

**Q: Getting low confidence scores**
A: Ensure API keys are valid, internet connection is good, try different search queries.

**Q: Database errors**
A: Check DATABASE_URL in .env, ensure database is running and accessible.

**Q: Approval gates not appearing**
A: Set `auto_approve: false` in campaign request, ensure frontend is polling for gates.

---

## 🚀 Production Deployment

### Docker

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db/campaigncraft
      AI_PROVIDER: openai
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3001:3001"
    environment:
      VITE_API_URL: http://backend:8000
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: campaigncraft
      POSTGRES_PASSWORD: password
  
  redis:
    image: redis:7-alpine
```

### Heroku Deployment

```bash
# Create app
heroku create campaigncraft

# Set environment
heroku config:set AI_PROVIDER=openai OPENAI_API_KEY=your_key

# Push
git push heroku main
```

---

## 📚 File Structure

```
backend/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py         # NEW
│   │   ├── stakeholder_agent.py      # NEW
│   │   ├── usecase_agent.py          # NEW
│   │   ├── proposal_agent.py         # NEW
│   │   ├── outreach_agent.py         # NEW
│   │   ├── campaign_manager_agent.py # NEW
│   │   └── webscraper.py (old v1)
│   │
│   ├── routes/                       # NEW
│   │   ├── __init__.py
│   │   └── campaign_routes.py        # NEW v2 endpoints
│   │
│   ├── db_models.py                  # NEW - SQLAlchemy models
│   ├── main.py                       # Updated with v2 routes
│   ├── models.py                     # Pydantic request/response models
│   ├── models_db.py                  # OLD - v1 models (deprecated)
│   └── ...
│
├── requirements.txt                  # Updated with new packages
├── .env.example
└── Dockerfile
```

---

## 🎯 Next Steps

1. **Install dependencies** - Run `pip install -r requirements.txt`
2. **Setup database** - Configure DATABASE_URL in .env
3. **Add API keys** - Get keys from OpenAI, Google, etc.
4. **Test agents** - Try example requests in docs
5. **Build frontend** - Create dashboard for campaign management
6. **Deploy** - Use Docker or cloud provider

---

## 📞 Support & Resources

### API Documentation
- Interactive Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Architecture Docs
- See `/documentation/ARCHITECTURE.md`
- Agent design: `/documentation/AGENTS.md`
- Database schema: `/documentation/DATABASE.md`

### Code Examples
- Start campaign: `/examples/create_campaign.py`
- Stream progress: `/examples/stream_campaign.py`
- Approval flow: `/examples/approval_gates.py`

---

## ✨ Summary

CampaignCraft v2.0 is a complete transformation into an **autonomous multi-agent system** with:

- ✅ 6 specialized agents orchestrated via LangGraph
- ✅ Human-in-the-loop approval gates at critical stages
- ✅ Comprehensive agent reasoning trails and logging
- ✅ Production-grade database schema
- ✅ Real-time agent activity monitoring
- ✅ Multi-channel outreach generation
- ✅ Learning system for continuous improvement

**Ready to build autonomous AI workflows!** 🚀

---

**Last Updated:** 2024  
**Version:** 2.0.0 - Agentic Orchestration System
