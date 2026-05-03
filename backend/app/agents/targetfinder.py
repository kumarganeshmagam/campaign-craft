import asyncio
from typing import Dict, Any

async def run_agent(input_data: Dict[str, Any], queue=None) -> Dict[str, Any]:
    topic = input_data.get("topic", "")
    if queue:
        await queue.put({"type": "progress", "agent": "TargetFinderAgent", "message": "Searching for public contacts (simulated)..."})
    await asyncio.sleep(0.4)
    contacts = [
        {"name": "Alex Johnson", "role": "Head of Partnerships", "company": "ExampleCorp", "contact_link": "https://example.com/alex"},
        {"name": "Priya Singh", "role": "VP Sales", "company": "DemoInc", "contact_link": "https://example.com/priya"},
        {"name": "Chen Wei", "role": "CTO", "company": "BetaTech", "contact_link": "https://example.com/chen"},
    ]
    if queue:
        await queue.put({"type": "progress", "agent": "TargetFinderAgent", "message": f"Found {len(contacts)} contacts."})
    return {"contacts": contacts}
