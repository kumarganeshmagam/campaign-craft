import os
import asyncio
import logging
from typing import Optional, Union, Dict, Any

logger = logging.getLogger(__name__)

# Controller that selects which orchestrator to use based on env var
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()


async def generate_text(
    prompt: str,
    *,
    stream: bool = False,
    json_mode: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """
    Central entry point for LLM calls. Routes to provider orchestrator.
    
    Args:
        prompt: The prompt to send to LLM
        stream: Whether to stream response
        json_mode: Return structured JSON
        temperature: Sampling temperature
        max_tokens: Maximum output tokens
        **kwargs: Additional parameters
    
    Returns:
        Generated text or structured JSON response
    """
    prov = AI_PROVIDER
    
    try:
        if prov == "gpt" or prov == "openai":
            from app.orchestrators.gpt_orchestrator import GPTOrchestrator
            return await GPTOrchestrator.generate_text(
                prompt,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
                **kwargs
            )
        
        if prov == "gemini":
            from app.orchestrators.gemini_orchestrator import GeminiOrchestrator
            return await GeminiOrchestrator.generate_text(
                prompt,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
                **kwargs
            )
        
        if prov == "claude":
            from app.orchestrators.claude_orchestrator import ClaudeOrchestrator
            return await ClaudeOrchestrator.generate_text(
                prompt,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
                **kwargs
            )
        
        # Fallback to mock if provider not recognized
        logger.warning(f"Unknown provider: {prov}, using mock response")
        await asyncio.sleep(0.2)
        return f"[MOCK {prov.upper()}] Response for prompt: {prompt[:200]}"
    
    except Exception as e:
        logger.error(f"Error in generate_text with provider {prov}: {str(e)}")
        raise


async def generate_json(
    prompt: str,
    schema: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate structured JSON response from LLM
    
    Args:
        prompt: The prompt
        schema: Optional JSON schema
        **kwargs: Additional parameters
    
    Returns:
        Parsed JSON response
    """
    prov = AI_PROVIDER
    
    try:
        if prov == "gemini":
            from app.orchestrators.gemini_orchestrator import GeminiOrchestrator
            return await GeminiOrchestrator.generate_json(prompt, schema=schema, **kwargs)
        
        # Fallback: generate text then parse as JSON
        result = await generate_text(prompt, json_mode=True, **kwargs)
        if isinstance(result, dict):
            return result
        return {"response": str(result)}
    
    except Exception as e:
        logger.error(f"Error in generate_json with provider {prov}: {str(e)}")
        raise


async def test_connection() -> bool:
    """Test if the configured AI provider is accessible"""
    prov = AI_PROVIDER
    
    try:
        if prov == "gemini":
            from app.orchestrators.gemini_orchestrator import GeminiOrchestrator
            return await GeminiOrchestrator.test_connection()
        
        if prov == "openai" or prov == "gpt":
            from app.orchestrators.gpt_orchestrator import GPTOrchestrator
            return await GPTOrchestrator.test_connection()
        
        if prov == "claude":
            from app.orchestrators.claude_orchestrator import ClaudeOrchestrator
            return await ClaudeOrchestrator.test_connection()
        
        logger.warning(f"Unknown provider: {prov}")
        return False
    
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False
