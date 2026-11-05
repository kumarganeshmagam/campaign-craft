# CampaignCraft - Backend

This is a minimal FastAPI backend for CampaignCraft.

Features:
- Agents (mocked) that expose `run_agent(input_data)`
- AIProviderController and simple orchestrators (mocked)
- SSE-based streaming for campaign updates

Quick start

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and edit if you want to enable a real provider.

3. Run the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:
- POST /api/start-campaign  -> start a campaign; returns campaign_id
- GET /api/stream/{campaign_id} -> SSE stream of events for that campaign
- POST /api/chat -> simple chat endpoint to refine a plan (not fully implemented)

Notes:
- AI providers are mocked when `AI_PROVIDER=mock`.
- Add real orchestrator implementations in `app/orchestrators/`.
