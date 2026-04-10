"""
Token Logger — Logs all LLM calls for cost tracking and analysis.
"""
import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

LOGS_DIR = Path(__file__).parent.parent.parent / "data" / "logs"
TOKEN_LOG_FILE = LOGS_DIR / "token_usage.csv"


def ensure_log_file():
    """Create token usage log file if it doesn't exist."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if not TOKEN_LOG_FILE.exists():
        with open(TOKEN_LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "session_id", "endpoint", "model", "tokens_used", 
                "tokens_budget_remaining", "status"
            ])


def log_token_usage(
    session_id: str,
    endpoint: str,
    model: str,
    tokens_used: int,
    tokens_budget_remaining: int,
    status: str = "success"
):
    """Log a token usage event."""
    ensure_log_file()
    
    with open(TOKEN_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            session_id,
            endpoint,
            model,
            tokens_used,
            tokens_budget_remaining,
            status
        ])
    
    logger.info(f"Token usage logged: {endpoint}, {tokens_used} tokens, {tokens_budget_remaining} remaining")


def get_token_usage_summary() -> dict:
    """Get summary of token usage from logs."""
    ensure_log_file()
    
    if not TOKEN_LOG_FILE.exists():
        return {"total_tokens": 0, "total_calls": 0, "by_endpoint": {}, "by_model": {}}
    
    total_tokens = 0
    total_calls = 0
    by_endpoint = {}
    by_model = {}
    
    with open(TOKEN_LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tokens = int(row.get("tokens_used", 0))
            endpoint = row.get("endpoint", "unknown")
            model = row.get("model", "unknown")
            
            total_tokens += tokens
            total_calls += 1
            by_endpoint[endpoint] = by_endpoint.get(endpoint, 0) + tokens
            by_model[model] = by_model.get(model, 0) + tokens
    
    return {
        "total_tokens": total_tokens,
        "total_calls": total_calls,
        "by_endpoint": by_endpoint,
        "by_model": by_model,
        "log_file": str(TOKEN_LOG_FILE)
    }
