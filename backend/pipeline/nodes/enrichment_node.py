"""
AI Enrichment Node — LLM-powered semantic analysis with ReAct tool-calling.
Supports Groq, Gemini, and other LLM backends via abstraction layer.
"""
import json
import re
import copy
import logging
import hashlib
from decimal import Decimal
from typing import Dict, Any, List, Union
from datetime import datetime

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool

from backend.core.state import AgentState
from backend.core.config import AppConfig
from backend.core.llm_provider import create_llm_provider
from backend.core.token_counter import estimate_messages_tokens, TokenBudget
from backend.services.usage_search import usage_search
from backend.core.utils import DecimalEncoder

logger = logging.getLogger(__name__)


@tool
def lookup_column_usage(column_name: str) -> str:
    """
    Searches application logs to see how a specific column is used in SQL queries.
    Returns snippets of SQL code where the column appears.
    """
    return usage_search.search_column_usage(column_name)


def _extract_text_from_payload(content: Union[str, List, Dict]) -> str:
    """Robustly extracts text from LangChain content payload."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict):
                if "text" in part:
                    text_parts.append(part["text"])
                elif part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
            elif isinstance(part, str):
                text_parts.append(part)
        return "".join(text_parts)
    if isinstance(content, dict) and "text" in content:
        return content["text"]
    return str(content)


def _clean_json_string(s: str) -> str:
    """Regex-based JSON extractor. Finds the outermost valid JSON object."""
    if not s:
        return ""
    json_block = re.search(r"```json\s*(\{.*?\})\s*```", s, re.DOTALL)
    if json_block:
        return json_block.group(1)
    code_block = re.search(r"```\s*(\{.*?\})\s*```", s, re.DOTALL)
    if code_block:
        return code_block.group(1)
    match = re.search(r"(\{.*\})", s, re.DOTALL)
    if match:
        return match.group(1)
    return s.strip()


def enrich_metadata_node(state: AgentState) -> Dict[str, Any]:
    schema_raw = state.get("schema_raw", {})
    previous_errors = state.get("errors", [])

    # --- 1. Caching Logic ---
    # Hash includes table names AND column names for deeper invalidation
    schema_fingerprint = {
        t: sorted(d["columns"].keys()) for t, d in schema_raw.items()
    }
    schema_str = json.dumps(schema_fingerprint, sort_keys=True)
    current_hash = hashlib.md5(schema_str.encode()).hexdigest()
    cache_file = AppConfig.DATA_DIR / "schema_cache.json"

    if not previous_errors and cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                cache = json.load(f)
            if cache.get("hash") == current_hash:
                logger.info("Schema unchanged. Using cached enrichment.")
                return {"schema_enriched": cache["data"], "schema_hash": current_hash}
        except Exception:
            pass

    # --- 2. Prompt Setup ---
    simplified_schema = {
        table: {col: meta["original_type"] for col, meta in data["columns"].items()}
        for table, data in schema_raw.items()
    }
    table_list = list(simplified_schema.keys())

    system_prompt = f"""You are a Data Architect. Generate a JSON Data Dictionary.

INPUT SCHEMA ({len(table_list)} tables): {json.dumps(simplified_schema, separators=(',', ':'))}

RULES:
1. Output ONLY valid JSON — no markdown fences, no explanation text.
2. You MUST include ALL {len(table_list)} tables: {json.dumps(table_list)}
3. You MUST include EVERY column listed for each table — do not skip any.
4. If a column is ambiguous (e.g. 'val_x', 'status'), call 'lookup_column_usage' first.
5. Keep descriptions concise (1 sentence).

OUTPUT FORMAT:
{{
  "TableName": {{
    "columns": {{
      "col": {{"description":"...","business_logic":"...","tags":["PII"],"potential_pii":false}}
    }}
  }}
}}"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="Begin enrichment."),
    ]

    if previous_errors:
        messages.append(
            HumanMessage(content=f"Previous errors to fix: {json.dumps(previous_errors)}")
        )

    # --- 3. The Execution Loop ---
    
    # Initialize LLM provider
    try:
        if AppConfig.LLM_PROVIDER.lower() == "groq":
            llm_provider = create_llm_provider(
                provider_type="groq",
                api_key=AppConfig.GROQ_API_KEY,
                model=AppConfig.GROQ_MODEL,
                temperature=AppConfig.LLM_TEMPERATURE,
            )
        else:  # fallback to gemini
            llm_provider = create_llm_provider(
                provider_type="gemini",
                api_key=AppConfig.GEMINI_API_KEY,
                model=AppConfig.GEMINI_MODEL,
                temperature=AppConfig.LLM_TEMPERATURE,
            )
    except Exception as e:
        logger.error(f"Failed to initialize LLM provider: {e}")
        return {"errors": [f"LLM initialization error: {str(e)}"]}
    
    # Token budgeting
    token_budget = TokenBudget(monthly_limit=AppConfig.TOKEN_MONTHLY_BUDGET)
    estimated_prompt_tokens = estimate_messages_tokens(messages, llm_provider.get_model_name())
    is_safe, budget_msg = token_budget.check_budget(estimated_prompt_tokens, threshold_percent=AppConfig.TOKEN_BUDGET_THRESHOLD_PERCENT)
    
    if not is_safe:
        logger.error(f"Token budget check failed: {budget_msg}")
        return {"errors": [f"Token budget exceeded: {budget_msg}"]}
    
    logger.info(f"Token budget check: {budget_msg}. Estimated prompt tokens: {estimated_prompt_tokens}")

    max_turns = 6
    turn = 0
    final_content = ""

    while turn < max_turns:
        turn += 1
        try:
            response = llm_provider.invoke(messages, tools=[lookup_column_usage])
            messages.append(response)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    logger.info(
                        f"Turn {turn}: Calling tool '{tool_call['name']}' for {tool_call['args']}"
                    )
                    tool_result = usage_search.search_column_usage(**tool_call["args"])
                    messages.append(
                        ToolMessage(
                            content=str(tool_result), tool_call_id=tool_call["id"]
                        )
                    )
                continue

            raw_content = _extract_text_from_payload(response.content)
            if raw_content.strip():
                logger.info(f"Turn {turn}: Received content from AI.")
                final_content = raw_content
                break
            break

        except Exception as e:
            return {"errors": [str(e)]}

    # --- 4. Parsing & Merge Logic ---
    try:
        logger.info(f"EXTRACTING JSON FROM: {final_content[:200]}...")
        cleaned = _clean_json_string(final_content)
        parsed_enrichment = json.loads(cleaned)

        if isinstance(parsed_enrichment, list):
            logger.warning("AI returned a LIST of tables. Converting to Dict...")
            new_dict = {}
            for item in parsed_enrichment:
                if isinstance(item, dict):
                    new_dict.update(item)
            parsed_enrichment = new_dict

        final_enriched_state = {}
        logger.info(f"MERGE: AI returned keys: {list(parsed_enrichment.keys())}")
        logger.info(f"MERGE: Expected keys: {list(schema_raw.keys())}")

        for table_name, enriched_data in parsed_enrichment.items():
            match_found = False
            for raw_key in schema_raw.keys():
                if raw_key.lower() == table_name.lower():
                    table_state = copy.deepcopy(schema_raw[raw_key])
                    if "columns" in enriched_data:
                        for col_name, enriched_meta in enriched_data["columns"].items():
                            if col_name in table_state["columns"]:
                                for field in (
                                    "description",
                                    "tags",
                                    "business_logic",
                                    "potential_pii",
                                ):
                                    if field in enriched_meta:
                                        table_state["columns"][col_name][field] = (
                                            enriched_meta[field]
                                        )
                    final_enriched_state[raw_key] = table_state
                    match_found = True
                    break
            if not match_found:
                logger.warning(
                    f"SKIPPING AI Table '{table_name}' - No match in raw schema."
                )

        with open(cache_file, "w") as f:
            json.dump(
                {"hash": current_hash, "data": final_enriched_state},
                f,
                cls=DecimalEncoder,
            )

        return {"schema_enriched": final_enriched_state, "schema_hash": current_hash}

    except Exception as e:
        logger.error(f"Parsing/Merge Error: {e}")
        return {"errors": [f"Enrichment Error: {str(e)}"]}
