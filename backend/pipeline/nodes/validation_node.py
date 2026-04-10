"""Deterministic Validation Gate — anti-hallucination guard with exponential backoff.
Ported from src/pipeline/nodes/validation_node.py with retry backoff and token budgeting.
"""
import logging
import time
from typing import Dict, Any, List, Set

from backend.core.state import AgentState
from backend.core.config import AppConfig
from backend.core.token_counter import TokenBudget

logger = logging.getLogger(__name__)


def validate_schema_node(state: AgentState) -> Dict[str, Any]:
    """
    DETERMINISTIC NODE:
    Compares the AI-enriched schema against the rigid 'schema_raw' source of truth.
    If the AI hallucinates or misses columns, this node fails the state, 
    triggering a retry or a fallback.
    """
    raw = state.get("schema_raw", {})
    enriched = state.get("schema_enriched", {})
    current_retries = state.get("retry_count", 0)

    errors: List[str] = []

    logger.info(
        f"Validating schema integrity (Attempt {current_retries + 1}/{AppConfig.MAX_RETRIES})..."
    )

    # 1. Check Table Counts
    if len(raw) != len(enriched):
        errors.append(
            f"CRITICAL: Table count mismatch. Raw has {len(raw)}, AI returned {len(enriched)}."
        )

    # 2. Deep Column Verification
    for table_name, raw_table_data in raw.items():
        if table_name not in enriched:
            errors.append(f"Missing Table: '{table_name}' was dropped by AI.")
            continue

        raw_cols: Set[str] = set(raw_table_data["columns"].keys())
        enriched_cols: Set[str] = set(enriched[table_name]["columns"].keys())

        missing = raw_cols - enriched_cols
        if missing:
            errors.append(f"Table '{table_name}' is missing columns: {list(missing)}")

        extra = enriched_cols - raw_cols
        if extra:
            errors.append(
                f"Table '{table_name}' has hallucinated columns: {list(extra)}"
            )

    # 3. Decision Logic with Token Budgeting
    if errors:
        logger.warning(f"Validation Failed with {len(errors)} errors.")
        
        # Check if we should retry
        if current_retries >= AppConfig.MAX_RETRIES:
            logger.error(f"Max retries ({AppConfig.MAX_RETRIES}) exceeded. Failing schema.")
            return {
                "errors": errors + ["Max retries exceeded. Schema enrichment failed."],
                "validation_status": "FAILED_FINAL",
                "retry_count": current_retries,
            }
        
        # Check token budget before retry
        token_budget = TokenBudget(monthly_limit=AppConfig.TOKEN_MONTHLY_BUDGET)
        remaining = token_budget.get_remaining_tokens()
        
        if remaining < 10_000:  # Need ~10k tokens for retry enrichment
            logger.error(f"Token budget insufficient for retry. Remaining: {remaining} tokens")
            errors.append(f"Token budget exhausted ({remaining} tokens remaining). Cannot retry.")
            return {
                "errors": errors,
                "validation_status": "FAILED_BUDGET",
                "retry_count": current_retries,
            }
        
        # Exponential backoff: retry with wait
        wait_time = 2 ** current_retries  # 1s, 2s, 4s, 8s
        logger.info(f"Scheduling retry #{current_retries + 1}/{AppConfig.MAX_RETRIES} after {wait_time}s...")
        time.sleep(wait_time)
        
        return {
            "errors": errors,
            "validation_status": "RETRY",
            "retry_count": current_retries + 1,
        }
    else:
        logger.info("Validation Passed. Schema integrity verified.")
        return {"errors": [], "validation_status": "PASSED"}
