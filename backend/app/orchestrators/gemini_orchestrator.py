import os
import asyncio
import json
import logging
from typing import Optional, Dict, Any, Union
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)


class GeminiOrchestrator:
    """
    Real Google Gemini API integration with langchain-google-genai
    """
    
    _api_key: Optional[str] = None
    _model_name: str = "gemini-2.5-pro"
    
    @classmethod
    def _initialize(cls):
        """Initialize Gemini API with API key from environment"""
        if cls._api_key is None:
            cls._api_key = os.getenv("GEMINI_API_KEY")
            if not cls._api_key:
                raise ValueError(
                    "GEMINI_API_KEY environment variable not set. "
                    "Get your API key at: https://makersuite.google.com/app/apikey"
                )
            genai.configure(api_key=cls._api_key)
            logger.info(f"Initialized Gemini API with model: {cls._model_name}")
    
    @classmethod
    async def generate_text(
        cls,
        prompt: str,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Union[str, dict]:
        """
        Generate text using Google Gemini API
        
        Args:
            prompt: The prompt to send to Gemini
            stream: Whether to stream the response (not yet fully implemented)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum output tokens
            **kwargs: Additional parameters
        
        Returns:
            Generated text response or structured output if JSON requested
        """
        cls._initialize()
        
        try:
            # Create generation config
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=kwargs.get("top_p", 0.95),
                top_k=kwargs.get("top_k", 40),
            )
            
            # Get the model
            model = genai.GenerativeModel(
                model_name=cls._model_name,
                generation_config=generation_config
            )
            
            # Check if we need JSON output
            needs_json = kwargs.get("json_mode", False)
            
            # If JSON is requested, add instruction to the prompt
            if needs_json:
                prompt_with_json = (
                    f"{prompt}\n\n"
                    "Please provide your response as valid JSON only, no other text."
                )
            else:
                prompt_with_json = prompt
            
            # Call Gemini API synchronously in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(prompt_with_json)
            )
            
            # Extract text from response
            text = response.text if hasattr(response, 'text') else str(response)
            
            logger.info(f"Gemini API call successful. Prompt length: {len(prompt)}, Response length: {len(text)}")
            
            # Try to parse as JSON if requested
            if needs_json:
                try:
                    # Try to extract JSON from the response
                    import re
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    else:
                        return json.loads(text)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from response, returning raw text")
                    return {"raw_response": text}
            
            return text
            
        except ValueError as e:
            logger.error(f"Gemini API Key Error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Gemini API Error: {type(e).__name__}: {str(e)}")
            raise
    
    @classmethod
    async def generate_json(
        cls,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate and parse JSON response from Gemini
        
        Args:
            prompt: The prompt
            schema: Optional JSON schema for validation
            **kwargs: Additional generation parameters
        
        Returns:
            Parsed JSON response
        """
        cls._initialize()
        
        # Add JSON schema to prompt if provided
        prompt_with_schema = prompt
        if schema:
            prompt_with_schema = (
                f"{prompt}\n\n"
                f"Expected JSON schema:\n{json.dumps(schema, indent=2)}"
            )
        
        result = await cls.generate_text(
            prompt_with_schema,
            json_mode=True,
            temperature=kwargs.get("temperature", 0.3),  # Lower temp for structured output
            **kwargs
        )
        
        if isinstance(result, dict):
            return result
        else:
            # Try to parse as JSON if it's a string
            try:
                import re
                json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return json.loads(str(result))
            except:
                return {"raw_response": str(result)}
    
    @classmethod
    async def generate_with_context(
        cls,
        prompt: str,
        context: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text with additional context
        
        Args:
            prompt: Main prompt
            context: Additional context to include
            **kwargs: Generation parameters
        
        Returns:
            Generated text
        """
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nPrompt:\n{prompt}"
        
        return await cls.generate_text(full_prompt, **kwargs)
    
    @classmethod
    def set_model(cls, model_name: str):
        """Set the Gemini model to use"""
        cls._model_name = model_name
        logger.info(f"Changed Gemini model to: {model_name}")
    
    @classmethod
    async def test_connection(cls) -> bool:
        """Test if Gemini API is accessible"""
        try:
            cls._initialize()
            response = await cls.generate_text(
                "Say 'Gemini API is working' if you can read this.",
                max_tokens=10
            )
            logger.info(f"Gemini test connection successful: {response}")
            return True
        except Exception as e:
            logger.error(f"Gemini test connection failed: {str(e)}")
            return False
