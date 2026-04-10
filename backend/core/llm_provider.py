"""
LLM Provider Abstraction — Supports Groq, Gemini, and other LLM backends.
Provides token estimation and unified LLM interface.
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def invoke(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> Any:
        """Invoke the LLM with messages and optional tools."""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name being used."""
        pass


class GroqProvider(LLMProvider):
    """Groq LLM Provider using Mixtral."""
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768", temperature: float = 0):
        """Initialize Groq provider."""
        from langchain_groq import ChatGroq
        
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.llm = ChatGroq(
            model=model,
            api_key=api_key,
            temperature=temperature,
        )
        logger.info(f"Initialized GroqProvider with model: {model}")
    
    def invoke(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> Any:
        """Invoke Groq LLM."""
        if tools:
            llm_with_tools = self.llm.bind_tools(tools)
            return llm_with_tools.invoke(messages)
        return self.llm.invoke(messages)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using a rough heuristic (1 token ≈ 4 chars for Mixtral)."""
        # Mixtral uses roughly same tokenization as LLaMA
        # Approximation: 1 token ≈ 4 characters
        return max(1, len(text) // 4)
    
    def get_model_name(self) -> str:
        """Return model name."""
        return self.model


class GeminiProvider(LLMProvider):
    """Google Gemini LLM Provider (fallback for testing)."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite", temperature: float = 0):
        """Initialize Gemini provider."""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature,
        )
        logger.info(f"Initialized GeminiProvider with model: {model}")
    
    def invoke(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> Any:
        """Invoke Gemini LLM."""
        if tools:
            llm_with_tools = self.llm.bind_tools(tools)
            return llm_with_tools.invoke(messages)
        return self.llm.invoke(messages)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using rough heuristic (1 token ≈ 3.5 chars for Gemini)."""
        # Gemini tokenization is slightly different
        # Approximation: 1 token ≈ 3.5 characters
        return max(1, len(text) // 3)
    
    def get_model_name(self) -> str:
        """Return model name."""
        return self.model


def create_llm_provider(
    provider_type: str = "groq",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0,
) -> LLMProvider:
    """Factory function to create LLM provider."""
    provider_type = provider_type.lower()
    
    if provider_type == "groq":
        if not api_key:
            raise ValueError("api_key required for Groq provider")
        model = model or "mixtral-8x7b-32768"
        return GroqProvider(api_key=api_key, model=model, temperature=temperature)
    
    elif provider_type == "gemini":
        if not api_key:
            raise ValueError("api_key required for Gemini provider")
        model = model or "gemini-2.5-flash-lite"
        return GeminiProvider(api_key=api_key, model=model, temperature=temperature)
    
    else:
        raise ValueError(f"Unknown LLM provider type: {provider_type}")
