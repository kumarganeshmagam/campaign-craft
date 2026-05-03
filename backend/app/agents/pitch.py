import asyncio
from typing import Dict, Any

async def run_agent(input_data: Dict[str, Any], queue=None) -> Dict[str, Any]:
    usecase = input_data.get("usecase", {})
    if queue:
        await queue.put({"type": "progress", "agent": "PitchAgent", "message": "Creating pitch variations..."})
    await asyncio.sleep(0.2)
    pitches = {
        "short": f"Hi, we can help with {usecase.get('title', '')} - short pitch.",
        "persuasive": f"Our {usecase.get('title', '')} approach drives ROI quickly.",
        "technical": f"Technical deep-dive on {usecase.get('title', '')} with architecture and metrics."
    }
    if queue:
        await queue.put({"type": "progress", "agent": "PitchAgent", "message": "Pitches ready."})
    return {"pitches": pitches}
