import asyncio
from typing import Dict, Any

async def run_agent(input_data: Dict[str, Any], queue=None) -> Dict[str, Any]:
    usecase = input_data.get("usecase") or {}
    targets = input_data.get("targets") or []
    if queue:
        await queue.put({"type": "progress", "agent": "ContentAgent", "message": "Generating outreach content..."})
    await asyncio.sleep(0.3)
    emails = [
        {"to": t.get("contact_link", "unknown"), "subject": f"Quick question about {usecase.get('title', 'your work')}", "body": f"Hi {t.get('name', 'there')},\nWe help with {usecase.get('summary', '')}. Interested?"}
        for t in (targets or [])[:3]
    ]
    dms = [f"Hey {t.get('name','there')}, quick note on {usecase.get('title','')}." for t in (targets or [])[:3]]
    if queue:
        await queue.put({"type": "progress", "agent": "ContentAgent", "message": "Content generated."})
    return {"emails": emails, "dms": dms}
