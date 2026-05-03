import asyncio
from typing import Dict, Any

async def run_agent(input_data: Dict[str, Any], queue=None) -> Dict[str, Any]:
    scrape = input_data.get("scrape", {})
    topic = scrape.get("topic", "")
    if queue:
        await queue.put({"type": "progress", "agent": "CampaignPlannerAgent", "message": "Analyzing scraped insights..."})
    await asyncio.sleep(0.4)
    plan = {
        "overview": f"Campaign for {topic}",
        "timeline": [
            {"week": 1, "activities": ["Research", "Messaging draft"]},
            {"week": 2, "activities": ["Outreach to early targets", "Refine content"]},
            {"week": 3, "activities": ["Scale outreach", "Run ads"]},
        ],
        "channels": ["email", "linkedin", "twitter"],
        "goals": {"meetings": 10, "responses": 50}
    }
    if queue:
        await queue.put({"type": "progress", "agent": "CampaignPlannerAgent", "message": "Plan created."})
    return plan
