"""
LLM utilities - unified LLM manager using TinyLlama
"""
import logging
from typing import Optional, List, Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from config import settings
from .exceptions import LLMException

logger = logging.getLogger(__name__)


class LLMManager:
    """Unified LLM manager"""
    
    _instance: Optional['LLMManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.model = settings.llm_model
            self.base_url = settings.ollama_base_url
            self.temperature = settings.llm_temperature
            self._llm = None
            self.initialized = True
            logger.info(f"Initialized LLM Manager with model: {self.model}")
    
    def get_llm(self, temperature: Optional[float] = None, format: Optional[str] = None) -> ChatOllama:
        """
        Get LLM instance
        
        Args:
            temperature: Override default temperature
            format: Response format (e.g., "json")
        """
        temp = temperature if temperature is not None else self.temperature
        
        kwargs = {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": temp,
        }
        
        if format:
            kwargs["format"] = format
        
        return ChatOllama(**kwargs)
    
    async def ainvoke(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        format: Optional[str] = None
    ) -> str:
        """
        Async invoke LLM
        
        Args:
            messages: List of messages
            temperature: Override default temperature
            format: Response format
            
        Returns:
            LLM response content
        """
        try:
            llm = self.get_llm(temperature=temperature, format=format)
            response = await llm.ainvoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error invoking LLM: {e}", exc_info=True)
            raise LLMException(f"Failed to get LLM response: {str(e)}")
    
    def invoke(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        format: Optional[str] = None
    ) -> str:
        """
        Sync invoke LLM
        
        Args:
            messages: List of messages
            temperature: Override default temperature
            format: Response format
            
        Returns:
            LLM response content
        """
        try:
            llm = self.get_llm(temperature=temperature, format=format)
            response = llm.invoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error invoking LLM: {e}", exc_info=True)
            raise LLMException(f"Failed to get LLM response: {str(e)}")
    
    async def ainvoke_with_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        format: Optional[str] = None
    ) -> str:
        """
        Async invoke LLM with system and user prompts
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Override default temperature
            format: Response format
            
        Returns:
            LLM response content
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        return await self.ainvoke(messages, temperature=temperature, format=format)
    
    def invoke_with_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        format: Optional[str] = None
    ) -> str:
        """
        Sync invoke LLM with system and user prompts
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Override default temperature
            format: Response format
            
        Returns:
            LLM response content
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        return self.invoke(messages, temperature=temperature, format=format)


# Global LLM manager instance
_llm_manager = None


def get_llm(temperature: Optional[float] = None, format: Optional[str] = None) -> ChatOllama:
    """
    Get LLM instance from global manager
    
    Args:
        temperature: Override default temperature
        format: Response format
        
    Returns:
        ChatOllama instance
    """
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager.get_llm(temperature=temperature, format=format)


def get_llm_manager() -> LLMManager:
    """Get global LLM manager instance"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager

