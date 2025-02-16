import httpx
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
import asyncio
from ..config import AIPROXY_TOKEN
from ..utils.logger import logger

class Message(BaseModel):
    """Model for chat message"""
    role: str = Field(..., regex='^(user|assistant|system)$')
    content: str
    
class ImageURL(BaseModel):
    """Model for image URL in vision requests"""
    url: str
    detail: str = "auto"

class VisionMessage(BaseModel):
    """Model for vision message"""
    role: str = Field(..., regex='^(user|assistant|system)$')
    content: Union[str, List[Union[str, Dict[str, Any]]]]

class LLMResponse(BaseModel):
    """Model for LLM API response"""
    choices: List[Dict[str, Any]]
    
class LLMClient:
    """Client for interacting with LLM API"""
    
    def __init__(self):
        if not AIPROXY_TOKEN:
            raise ValueError("AIPROXY_TOKEN is required")
            
        self.token = AIPROXY_TOKEN
        self.api_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
        self.max_retries = 3
        self.base_timeout = 30.0
        self.max_timeout = 90.0
        
    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text response from LLM
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
            
        Raises:
            ValueError: For invalid input
            RuntimeError: For API errors
        """
        # Validate input
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
        if not 0 <= temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1")
            
        message = Message(role="user", content=prompt)
        return await self._make_request([message.dict()], temperature)
        
    async def generate_vision(self, messages: List[VisionMessage], temperature: float = 0.7) -> str:
        """
        Generate response for vision tasks
        
        Args:
            messages: List of vision messages
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
            
        Raises:
            ValueError: For invalid input
            RuntimeError: For API errors
        """
        # Validate messages
        if not messages:
            raise ValueError("Messages list cannot be empty")
            
        validated_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                msg = VisionMessage(**msg)
            validated_messages.append(msg.dict())
            
        return await self._make_request(validated_messages, temperature)
        
    async def _make_request(self, messages: List[Dict[str, Any]], temperature: float) -> str:
        """Make request to LLM API with retries"""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": temperature
        }
        
        for attempt in range(self.max_retries):
            try:
                timeout = min(self.base_timeout * (attempt + 1), self.max_timeout)
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=timeout
                    )
                    
                    if response.status_code == 429:  # Rate limit
                        if attempt < self.max_retries - 1:
                            wait_time = min(2 ** attempt, 8)  # Exponential backoff
                            logger.warning(f"Rate limited, waiting {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                            
                    response.raise_for_status()
                    
                    # Validate response
                    try:
                        data = response.json()
                        validated_response = LLMResponse(**data)
                        return validated_response.choices[0]["message"]["content"]
                    except (KeyError, IndexError) as e:
                        raise RuntimeError(f"Invalid API response format: {str(e)}")
                        
            except httpx.TimeoutError:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Request timed out after {self.max_retries} attempts")
                logger.warning(f"Request timed out, attempt {attempt + 1}/{self.max_retries}")
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise RuntimeError(f"API request failed: {str(e)}")
                
            except Exception as e:
                logger.error(f"Unexpected error in LLM client: {str(e)}")
                raise RuntimeError(f"LLM request failed: {str(e)}")