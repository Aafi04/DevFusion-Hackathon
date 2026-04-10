"""Schema API Routes — retrieve enriched schema data.
GET /api/schema/{run_id} — Get full schema
GET /api/schema/{run_id}/overview — Get AI overview
GET /api/schema/{run_id}/table/{table_name} — Get specific table
"""
import json
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage

from backend.services.pipeline_service import get_run
from backend.core.config import AppConfig
from backend.core.llm_provider import create_llm_provider
from backend.core.token_counter import estimate_messages_tokens, TokenBudget
from backend.core.utils import DecimalEncoder
from backend.core.rate_limiter import limiter, SCHEMA_OVERVIEW_LIMIT, READ_LIMIT

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/schema", tags=["Schema"])


def _sid(request: Request) -> str:
    return request.headers.get("x-session-id", "")


@router.get("/{run_id}")
@limiter.limit(READ_LIMIT)
async def get_schema(request: Request, run_id: str):
    """Get the full enriched schema for a pipeline run."""
    run = get_run(run_id, session_id=_sid(request))
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    
    response_data = {
        "run_id": run_id,
        "status": run["status"],
        "schema": run.get("schema_enriched"),
        "pipeline_log": run.get("pipeline_log", []),
    }
    
    # Add cache header (1 hour)
    response = JSONResponse(content=response_data)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@router.get("/{run_id}/table/{table_name}")
@limiter.limit(READ_LIMIT)
async def get_table(request: Request, run_id: str, table_name: str):
    """Get a specific table's schema data."""
    run = get_run(run_id, session_id=_sid(request))
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    schema = run.get("schema_enriched", {})
    if table_name not in schema:
        raise HTTPException(
            status_code=404, detail=f"Table '{table_name}' not found in run '{run_id}'"
        )
    
    response_data = schema[table_name]
    # Add cache header (1 hour)
    response = JSONResponse(content=response_data)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@router.get("/{run_id}/overview")
@limiter.limit(SCHEMA_OVERVIEW_LIMIT)
async def get_overview(request: Request, run_id: str):
    """Generate an AI database overview for a pipeline run."""
    run = get_run(run_id, session_id=_sid(request))
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    schema_data = run.get("schema_enriched", {})
    if not schema_data:
        raise HTTPException(status_code=400, detail="No schema data available")

    total_tables = len(schema_data)
    total_cols = sum(len(t.get("columns", {})) for t in schema_data.values())
    total_rows = sum(t.get("row_count", 0) for t in schema_data.values())
    avg_health = (
        sum(t.get("health_score", 100) for t in schema_data.values()) / total_tables
        if total_tables
        else 0
    )
    pii_cols = [
        f"{t}.{c}"
        for t, tm in schema_data.items()
        for c, cm in tm.get("columns", {}).items()
        if "PII" in (cm.get("tags") or [])
    ]
    fk_count = sum(len(t.get("foreign_keys", [])) for t in schema_data.values())
    fk_pairs = [
        f"{t}.{fk['column']}→{fk['referred_table']}"
        for t, tm in schema_data.items()
        for fk in tm.get("foreign_keys", [])
    ]

    prompt = f"""You are a data documentation expert. Write a concise 3-4 sentence overview paragraph about this database.

FACTS:
- {total_tables} tables, {total_cols} columns, {total_rows:,} total rows
- Tables: {', '.join(schema_data.keys())}
- Average health score: {avg_health:.1f}/100
- PII columns detected: {len(pii_cols)} ({', '.join(pii_cols[:8])}{'...' if len(pii_cols)>8 else ''})
- Foreign key relationships: {', '.join(fk_pairs[:10])}

RULES:
1. Start with what domain/purpose this database serves (infer from table/column names).
2. Mention the scale (tables, rows) and key entity relationships.
3. Note any data quality observations (health scores, PII presence).
4. Keep it to ONE paragraph, 3-4 sentences max. No bullet points. No markdown headers."""

    try:
        # Initialize LLM provider
        try:
            if AppConfig.LLM_PROVIDER.lower() == "groq":
                llm_provider = create_llm_provider(
                    provider_type="groq",
                    api_key=AppConfig.GROQ_API_KEY,
                    model=AppConfig.GROQ_MODEL,
                    temperature=0.3,
                )
            else:
                llm_provider = create_llm_provider(
                    provider_type="gemini",
                    api_key=AppConfig.GEMINI_API_KEY,
                    model=AppConfig.GEMINI_MODEL,
                    temperature=0.3,
                )
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            overview = f"Database contains {total_tables} tables with {total_cols} columns and {total_rows:,} rows."
            return {
                "overview": overview,
                "total_tables": total_tables,
                "total_columns": total_cols,
                "total_rows": total_rows,
                "avg_health": round(avg_health, 1),
                "pii_count": len(pii_cols),
                "fk_count": fk_count,
            }
        
        # Estimate tokens
        estimated_tokens = estimate_messages_tokens([HumanMessage(content=prompt)], llm_provider.get_model_name())
        logger.info(f"Schema overview - Estimated tokens: {estimated_tokens}")
        
        response = llm_provider.invoke([HumanMessage(content=prompt)])
        overview = response.content.strip()
    except Exception as e:
        overview = f"Database contains {total_tables} tables with {total_cols} columns and {total_rows:,} rows."

    response_data = {
        "overview": overview,
        "total_tables": total_tables,
        "total_columns": total_cols,
        "total_rows": total_rows,
        "avg_health": round(avg_health, 1),
        "pii_count": len(pii_cols),
        "fk_count": fk_count,
    }
    
    # Add cache header (1 hour)
    response = JSONResponse(content=response_data)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response
