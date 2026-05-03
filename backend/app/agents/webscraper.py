import asyncio
from typing import Dict, Any

async def run_agent(input_data: Dict[str, Any], queue=None) -> Dict[str, Any]:
    topic = input_data.get("topic", "")
    # Simulate scraping and summarization
    if queue:
        await queue.put({"type": "progress", "agent": "WebScraperAgent", "message": "Querying web sources (mock)..."})
    await asyncio.sleep(0.5)
    keywords = [w for w in topic.lower().split() if len(w) > 3]
    insights = [f"High interest in {topic}", "Competitors spotlight: ExampleCorp, DemoInc"]
    competitors = [
        {"name": "ExampleCorp", "reason": "Large marketing spend"},
        {"name": "DemoInc", "reason": "Strong product-market fit"},
    ]
    result = {"topic": topic, "keywords": keywords, "insights": insights, "competitors": competitors}
    if queue:
        await queue.put({"type": "progress", "agent": "WebScraperAgent", "message": "Scrape complete."})
    return result
