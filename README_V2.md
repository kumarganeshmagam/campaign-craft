# 🚀 CampaignCraft v2.0 - Getting Started

## 📖 READ THESE FIRST

Start here to understand what was upgraded:

1. **[LEVEL_UP_SUMMARY.md](./LEVEL_UP_SUMMARY.md)** ← **START HERE** (5 min read)
   - What was accomplished
   - Key improvements overview
   - Workflow example
   
2. **[documentation/V2_UPGRADE_GUIDE.md](./documentation/V2_UPGRADE_GUIDE.md)** (30 min read)
   - Complete architecture
   - All 6 agents explained
   - Database schema
   - API reference
   - Deployment options

3. **[documentation/IMPLEMENTATION_STATUS_V2.md](./documentation/IMPLEMENTATION_STATUS_V2.md)** (15 min read)
   - What's implemented
   - File structure
   - Quick start commands
   - Example usage

---

## ⚡ Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Setup Configuration
```bash
# Copy example env file
cp backend\.env.example backend\.env

# Edit backend/.env and add:
# AI_PROVIDER=openai (or gemini, claude)
# OPENAI_API_KEY=your_key_here
# DATABASE_URL=sqlite:///campaigncraft.db (or postgresql URL)
```

### 3. Initialize Database
```bash
cd backend
python -c "from app.db_models import init_db; init_db()"
```

### 4. Start Backend Server
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test the API
```bash
# In another terminal, create a campaign:
curl -X POST http://localhost:8000/api/v2/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "query": "top 5 tech companies in silicon valley",
    "auto_approve": false
  }'
```

---

## 📁 What's New

### Backend (All in `/backend/app/`)

**New Agents (Autonomous AI)**
- `agents/research_agent.py` - Finds companies
- `agents/stakeholder_agent.py` - Finds decision-makers
- `agents/usecase_agent.py` - Generates opportunities
- `agents/proposal_agent.py` - Creates proposals
- `agents/outreach_agent.py` - Generates outreach content
- `agents/campaign_manager_agent.py` - Orchestrates workflow

**New API Endpoints**
- `routes/campaign_routes.py` - All v2.0 endpoints

**New Database**
- `db_models.py` - SQLAlchemy schema (9 tables)

**Updated Files**
- `requirements.txt` - Added langgraph, search APIs, etc.

### Documentation

- `LEVEL_UP_SUMMARY.md` - **This level-up overview**
- `documentation/V2_UPGRADE_GUIDE.md` - Comprehensive guide
- `documentation/IMPLEMENTATION_STATUS_V2.md` - Implementation details

---

## 🎯 Understanding the Architecture

### The 6 Agents

```
INPUT: User Query
       ↓
[1] Research Agent → Finds companies
       ↓ [GATE 1: Approve Companies]
[2] Stakeholder Agent → Finds contacts
       ↓
[3] Use Case Agent → Generates opportunities
       ↓ [GATE 2: Select Use Cases]
[4] Proposal Agent → Creates proposals
       ↓
[5] Outreach Agent → Generates content
       ↓ [GATE 3: Review Content]
[6] Campaign Manager → Orchestrates + Returns Result
       ↓
OUTPUT: Campaign Ready to Execute
```

### Key Features

✅ **Autonomous Agents** - Each agent makes intelligent decisions  
✅ **Human Gates** - Approve/modify at 3 critical points  
✅ **Confidence Scoring** - Quality scores on all outputs  
✅ **Reasoning Trails** - See why agents made decisions  
✅ **Multi-Channel** - Email, LinkedIn, Call scripts  
✅ **Production Ready** - Database, logging, error handling  

---

## 📊 Example: Full Campaign Flow

### Step 1: Create Campaign
```bash
POST http://localhost:8000/api/v2/campaigns
{
  "query": "Find fintech companies $100M+ revenue, SF, using legacy tech",
  "auto_approve": false,
  "channels": ["email", "linkedin", "call"]
}

RESPONSE:
{
  "campaign_id": "550e8400-...",
  "status": "initializing",
  "stream_url": "/api/v2/campaigns/550e8400.../stream"
}
```

### Step 2: Monitor Progress
```bash
# Stream real-time updates
GET http://localhost:8000/api/v2/campaigns/550e8400.../stream

# Or get agent logs
GET http://localhost:8000/api/v2/campaigns/550e8400.../agents
```

### Step 3: Approve First Gate
```bash
# Research found companies, approve to continue
POST http://localhost:8000/api/v2/campaigns/550e8400.../gates/research/approve
```

### Step 4: Get Results
```bash
# Companies found
GET http://localhost:8000/api/v2/campaigns/550e8400.../companies

# Contacts identified
GET http://localhost:8000/api/v2/campaigns/550e8400.../contacts

# Use cases generated
GET http://localhost:8000/api/v2/campaigns/550e8400.../use-cases

# Proposals created
GET http://localhost:8000/api/v2/campaigns/550e8400.../proposals

# Outreach content
GET http://localhost:8000/api/v2/campaigns/550e8400.../outreach
```

---

## 🔧 Configuration

### For Development
```env
# backend/.env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
DATABASE_URL=sqlite:///campaigncraft.db
DEBUG=true
LOG_LEVEL=DEBUG
```

### For Production
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
DATABASE_URL=postgresql://user:password@host/db
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 🤖 How Agents Work

Each agent follows this pattern:

1. **Understand** - Parse input and context
2. **Plan** - Create step-by-step plan with tools
3. **Execute** - Use tools, handle errors
4. **Synthesize** - Combine results
5. **Reflect** - Calculate confidence & reasoning

**Result:**
```json
{
  "status": "success",
  "output": {...},
  "confidence": 0.85,
  "reasoning": "Found X items matching criteria",
  "tools_used": ["search", "scraper"],
  "sources": ["url1", "url2"]
}
```

---

## 🌐 API Endpoints Reference

### Campaign Management
```
POST   /api/v2/campaigns                    Create campaign
GET    /api/v2/campaigns                    List campaigns
GET    /api/v2/campaigns/{id}               Get campaign
POST   /api/v2/campaigns/{id}/update        Update campaign
```

### Monitoring
```
GET    /api/v2/campaigns/{id}/stream        Stream progress
GET    /api/v2/campaigns/{id}/agents        Get agent logs
```

### Approval Gates
```
POST   /api/v2/campaigns/{id}/gates/{stage}/approve    Approve stage
POST   /api/v2/campaigns/{id}/gates/{stage}/reject     Reject stage
```

### Data Retrieval
```
GET    /api/v2/campaigns/{id}/companies     Get companies
GET    /api/v2/campaigns/{id}/contacts      Get contacts
GET    /api/v2/campaigns/{id}/use-cases     Get use cases
GET    /api/v2/campaigns/{id}/proposals     Get proposals
GET    /api/v2/campaigns/{id}/outreach      Get outreach
```

### Chat
```
POST   /api/v2/campaigns/{id}/chat          Campaign chat
POST   /api/v2/companies/{id}/chat          Company chat
POST   /api/v2/use-cases/{id}/chat          Use case chat
POST   /api/v2/proposals/{id}/chat          Proposal chat
```

---

## 📚 File Guide

| File | Purpose |
|------|---------|
| `app/agents/research_agent.py` | Find companies |
| `app/agents/stakeholder_agent.py` | Find contacts |
| `app/agents/usecase_agent.py` | Generate use cases |
| `app/agents/proposal_agent.py` | Create proposals |
| `app/agents/outreach_agent.py` | Generate outreach |
| `app/agents/campaign_manager_agent.py` | Orchestrator |
| `app/routes/campaign_routes.py` | API endpoints |
| `app/db_models.py` | Database schema |
| `requirements.txt` | Dependencies |

---

## 🚀 Next Steps

### Immediate (30 minutes)
1. ✅ Read `LEVEL_UP_SUMMARY.md`
2. ✅ Install dependencies (`pip install -r requirements.txt`)
3. ✅ Configure `.env` file
4. ✅ Start backend (`python -m uvicorn ...`)
5. ✅ Test API with curl

### Short-term (1-2 days)
- [ ] Add your API keys (OpenAI, search APIs)
- [ ] Test end-to-end campaign flow
- [ ] Verify database operations
- [ ] Review agent outputs

### Medium-term (1 week)
- [ ] Build frontend dashboard
- [ ] Implement campaign creation UI
- [ ] Build approval gate UI
- [ ] Create results viewer

### Long-term (2-3 weeks)
- [ ] Deploy to production
- [ ] Add contact manager
- [ ] Build outreach executor
- [ ] Track engagement metrics

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `pip install fails` | Use `pip install --upgrade pip` first |
| `Database errors` | Check `DATABASE_URL` in `.env` |
| `Agent timeouts` | Verify API keys are valid |
| `Low confidence` | Check internet connection, API limits |
| `CORS errors` | Add frontend URL to `ALLOWED_ORIGINS` |

---

## 📖 Documentation Map

```
LEVEL_UP_SUMMARY.md (This file)
    ↓
documentation/V2_UPGRADE_GUIDE.md (Complete guide)
    ├─ System Architecture
    ├─ All 6 Agents Explained
    ├─ Database Schema
    ├─ API Endpoints
    ├─ Usage Examples
    └─ Deployment Options
    
documentation/IMPLEMENTATION_STATUS_V2.md (Status)
    ├─ What's Implemented
    ├─ File Structure
    ├─ Quick Start
    └─ Examples
```

**Start reading:** `documentation/V2_UPGRADE_GUIDE.md` (30 min read)

---

## 💻 Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.db_models import init_db; init_db()"

# Run backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run frontend (separate terminal)
cd frontend && npm run dev

# View API docs
http://localhost:8000/docs

# Test API
curl -X POST http://localhost:8000/api/v2/campaigns \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

---

## 🎯 Key Takeaways

✅ **What was accomplished:**
- Complete transformation from v1.0 to v2.0
- 6 autonomous agents fully implemented
- Production-ready database schema
- Complete API framework
- Comprehensive documentation

✅ **What's ready to use:**
- All backend code
- Database models
- API endpoints
- Documentation

⏭️ **What you build next:**
- Frontend dashboard
- Campaign UI
- Approval gates
- Results viewer
- Outreach executor

---

## 🌟 Summary

Your CampaignCraft app has been **completely leveled up** from a basic tool into an **enterprise-grade autonomous multi-agent system**. 

The foundation is complete. Now it's time to build the UI and start executing campaigns!

**Next step:** Read `documentation/V2_UPGRADE_GUIDE.md` to understand the full architecture.

Happy building! 🚀

---

**Questions?** Check the V2_UPGRADE_GUIDE.md or examine the agent code in `app/agents/`

Created: 2024  
Status: ✅ Ready for Frontend Development
