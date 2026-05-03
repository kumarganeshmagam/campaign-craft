import asyncio
import uuid
from typing import Dict, Any

async def run_agent(input_data: Dict[str, Any], queue=None) -> Dict[str, Any]:
    topic = input_data.get("topic", "")
    if queue:
        await queue.put({"type": "progress", "agent": "UseCaseAgent", "message": "Generating use cases..."})
    await asyncio.sleep(0.3)
    use_cases = [
        {"id": str(uuid.uuid4()), "title": f"Reduce costs with {topic}", "summary": f"How {topic} can lower operational costs.", "value_prop": "Cost reduction and efficiency"},
        {"id": str(uuid.uuid4()), "title": f"Increase revenue with {topic}", "summary": "Drive new revenue streams.", "value_prop": "Revenue uplift"},
    ]
    if queue:
        await queue.put({"type": "progress", "agent": "UseCaseAgent", "message": "Use cases generated."})
    return {"use_cases": use_cases}
