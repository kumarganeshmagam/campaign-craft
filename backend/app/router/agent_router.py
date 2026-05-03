import asyncio
from typing import Any, Dict

from app.controllers.ai_provider import generate_text

class AgentRouter:
    @staticmethod
    async def call_llm(task: str, payload: Dict[str, Any]) -> str:
        # Build a simple prompt based on task and payload
        prompt = f"Task: {task}\nPayload: {payload}"
        return await generate_text(prompt)

    @staticmethod
    async def run_agent(agent_name: str, payload: Dict[str, Any], queue: asyncio.Queue = None) -> Dict[str, Any]:
        """Dispatch to agent modules. Agents are lightweight and can optionally push progress messages to the queue."""
        agent_name = agent_name.lower()
        if agent_name == "webscraper":
            from app.agents.webscraper import run_agent as scraper
            return await scraper(payload, queue)
        if agent_name == "planner":
            from app.agents.planner import run_agent as planner
            return await planner(payload, queue)
        if agent_name == "formatter":
            from app.agents.formatter import run_agent as formatter
            return await formatter(payload, queue)
        if agent_name == "usecase":
            from app.agents.usecase import run_agent as usecase
            return await usecase(payload, queue)
        if agent_name == "pitch":
            from app.agents.pitch import run_agent as pitch
            return await pitch(payload, queue)
        if agent_name == "content":
            from app.agents.content import run_agent as content
            return await content(payload, queue)
        if agent_name == "targetfinder":
            from app.agents.targetfinder import run_agent as tf
            return await tf(payload, queue)
        if agent_name == "research":
            from app.agents.research_agent import run_agent as research
            return await research(payload, queue)

        # fallback: treat as LLM chat
        res = await AgentRouter.call_llm(agent_name, payload)
        return {"text": res}
