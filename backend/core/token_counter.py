"""
Token Counter — Estimates token usage before LLM calls.
Uses tiktoken for accurate Groq/OpenAI token counting.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import tiktoken for accurate counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not available. Using fallback token estimation.")


def estimate_tokens(text: str, model: str = "mixtral-8x7b-32768") -> int:
    """
    Estimate token count for text using the specified model.
    
    Args:
        text: Text to estimate tokens for
        model: Model name (e.g., 'mixtral-8x7b-32768', 'gemini-2.5-flash-lite')
    
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    
    # If tiktoken available and it's an OpenAI-compatible model, use it
    if TIKTOKEN_AVAILABLE and "mixtral" in model.lower():
        try:
            # Mixtral uses similar tokenization to LLaMA
            encoding = tiktoken.get_encoding("cl100k_base")
            tokens = encoding.encode(text)
            return len(tokens)
        except Exception as e:
            logger.warning(f"tiktoken estimation failed: {e}. Using fallback.")
    
    # Fallback: character-based estimation
    # Mixtral: ~1 token per 4 characters
    # Gemini: ~1 token per 3.5 characters
    if "mixtral" in model.lower():
        return max(1, len(text) // 4)
    elif "gemini" in model.lower():
        return max(1, len(text) // 3)
    else:
        # Generic fallback
        return max(1, len(text) // 4)


def estimate_messages_tokens(messages: list, model: str = "mixtral-8x7b-32768") -> int:
    """
    Estimate token count for a list of messages.
    
    Args:
        messages: List of LangChain message objects
        model: Model name
    
    Returns:
        Estimated total token count
    """
    total_tokens = 0
    
    for msg in messages:
        # Extract content from different message types
        if hasattr(msg, "content"):
            content = msg.content
        else:
            content = str(msg)
        
        if isinstance(content, str):
            total_tokens += estimate_tokens(content, model)
        elif isinstance(content, list):
            # Handle list of content blocks
            for block in content:
                if isinstance(block, str):
                    total_tokens += estimate_tokens(block, model)
                elif isinstance(block, dict) and "text" in block:
                    total_tokens += estimate_tokens(block["text"], model)
    
    # Add overhead for message framing (roughly 4 tokens per message)
    total_tokens += len(messages) * 4
    
    return total_tokens


def estimate_response_tokens(text: str, model: str = "mixtral-8x7b-32768") -> int:
    """
    Estimate tokens for an LLM response.
    Typically responses are similar length to input or shorter.
    
    Args:
        text: Expected response text
        model: Model name
    
    Returns:
        Estimated token count
    """
    return estimate_tokens(text, model)


class TokenBudget:
    """Track token usage against a monthly budget."""
    
    def __init__(self, monthly_limit: int = 1_000_000):
        """Initialize token budget tracker."""
        self.monthly_limit = monthly_limit
        self.used_tokens = 0
    
    def check_budget(self, estimated_tokens: int, threshold_percent: float = 80.0) -> tuple[bool, str]:
        """
        Check if a call would exceed budget thresholds.
        
        Args:
            estimated_tokens: Tokens needed for the call
            threshold_percent: Warn if usage would exceed this % of budget
        
        Returns:
            Tuple of (is_safe: bool, message: str)
        """
        projected_total = self.used_tokens + estimated_tokens
        projected_percent = (projected_total / self.monthly_limit) * 100
        
        if projected_percent >= 100:
            return False, f"CRITICAL: Would exceed monthly budget. {projected_percent:.1f}% / 100%"
        
        if projected_percent >= threshold_percent:
            return True, f"WARNING: Approaching budget limit. {projected_percent:.1f}% / 100%"
        
        return True, f"OK: {projected_percent:.1f}% / 100% of budget"
    
    def record_usage(self, tokens_used: int):
        """Record tokens used in a call."""
        self.used_tokens += tokens_used
        logger.info(f"Token usage: {tokens_used} tokens. Total this month: {self.used_tokens}")
    
    def get_remaining_tokens(self) -> int:
        """Get remaining tokens for the month."""
        return max(0, self.monthly_limit - self.used_tokens)
    
    def get_usage_percent(self) -> float:
        """Get percentage of budget used."""
        return (self.used_tokens / self.monthly_limit) * 100 if self.monthly_limit > 0 else 0.0
