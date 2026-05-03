import asyncio
import os
import uuid
import logging
from typing import Dict

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from app.router.agent_router import AgentRouter
from app.utils.sse import format_sse
from app.logging_config import setup_logging

load_dotenv()

# Setup logging
logger = setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="CampaignCraft Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for campaign message queues
campaign_queues: Dict[str, asyncio.Queue] = {}

class StartCampaignRequest(BaseModel):
    topic: str


class GenerateContentRequest(BaseModel):
    campaign_id: str
    usecase_id: str | None = None


@app.post("/api/start-campaign")
async def start_campaign(req: StartCampaignRequest, background_tasks: BackgroundTasks):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    campaign_id = str(uuid.uuid4())
    q: asyncio.Queue = asyncio.Queue()
    campaign_queues[campaign_id] = q

    # Wrap the background task to catch exceptions
    async def safe_orchestrate():
        try:
            await _orchestrate_campaign(campaign_id, topic)
        except Exception as e:
            logger.error(f"Background task error: {e}", exc_info=True)
            try:
                await q.put({"type": "error", "message": f"Campaign failed: {str(e)}"})
                await q.put({"type": "complete", "message": "Campaign orchestration failed."})
            except:
                pass

    # start orchestration in background
    background_tasks.add_task(safe_orchestrate)

    return JSONResponse({"campaign_id": campaign_id, "stream_url": f"/api/stream/{campaign_id}"})


@app.post("/api/generate-content")
async def generate_content(req: GenerateContentRequest):
    """Trigger content generation for an existing campaign. Returns generated content or error."""
    campaign_id = req.campaign_id
    q = campaign_queues.get(campaign_id)
    if q is None:
        raise HTTPException(status_code=404, detail="campaign not found")

    # For demo: trigger ContentAgent with a simple payload. In a real app we'd fetch campaign state from DB.
    await q.put({"type": "status", "agent": "ContentAgent", "message": "Starting content generation..."})
    # run content agent synchronously and push result to the campaign queue.
    content = await AgentRouter.run_agent("content", {"usecase": {}, "targets": []}, q)
    await q.put({"type": "result", "agent": "ContentAgent", "data": content})

    # Also run the formatter to produce a combined readable summary and push it.
    formatted = await AgentRouter.run_agent("formatter", {"plan": {}, "usecases": {}, "contacts": {}, "content": content}, q)
    await q.put({"type": "result", "agent": "StrategyFormatterAgent", "data": formatted})

    # Return simple status; the frontend should consume the SSE stream for full content.
    return JSONResponse({"status": "ok"})


async def _orchestrate_campaign(campaign_id: str, topic: str):
    q = campaign_queues.get(campaign_id)
    if q is None:
        logger.error(f"Campaign queue not found for {campaign_id}")
        return

    logger.info(f"Starting orchestration for campaign {campaign_id} with topic: {topic}")
    
    # Use the new Gemini-powered Research Agent instead of the old mock agents
    await q.put({"type": "status", "agent": "ResearchAgent", "message": "Analyzing topic with Gemini AI..."})
    
    try:
        logger.info("Calling research agent...")
        research_result = await AgentRouter.run_agent("research", {"topic": topic}, q)
        logger.info(f"Research agent returned: {type(research_result)}")
        await q.put({"type": "result", "agent": "ResearchAgent", "data": research_result})
    except Exception as e:
        logger.error(f"Error in orchestration: {e}", exc_info=True)
        await q.put({"type": "error", "agent": "ResearchAgent", "error": str(e)})
        await q.put({"type": "complete", "message": "Campaign orchestration failed."})
        return

    logger.info("Orchestration complete")
    await q.put({"type": "complete", "message": "Campaign orchestration complete."})


@app.get("/api/stream/{campaign_id}")
async def stream_campaign(campaign_id: str):
    q = campaign_queues.get(campaign_id)
    if q is None:
        raise HTTPException(status_code=404, detail="campaign not found")

    async def event_generator():
        try:
            while True:
                data = await q.get()
                yield format_sse(data)
                if data.get("type") == "complete":
                    break
        finally:
            # cleanup
            campaign_queues.pop(campaign_id, None)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/chat")
async def chat(message: dict):
    # Simple passthrough for now
    res = await AgentRouter.call_llm("chat", message)
    return {"response": res}
