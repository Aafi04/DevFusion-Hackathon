"""Pipeline orchestration service.
Manages pipeline runs, caches results, tracks execution.
Runs are scoped by session_id so each browser session is isolated.
Integrates with Supabase for persistent caching across restarts.
"""
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.pipeline.graph import build_pipeline
from backend.core.config import settings, AppConfig
from backend.core.utils import DecimalEncoder
from backend.core.supabase_client import get_supabase_cache

logger = logging.getLogger(__name__)


# In-memory store: session_id -> { run_id -> run_data }
_pipeline_runs: Dict[str, Dict[str, Dict[str, Any]]] = {}


def _session_store(session_id: str) -> Dict[str, Dict[str, Any]]:
    """Return (and lazily create) the run store for a session."""
    if session_id not in _pipeline_runs:
        _pipeline_runs[session_id] = {}
    return _pipeline_runs[session_id]


def clear_all_runs(session_id: str = ""):
    """Wipe pipeline runs. If session_id given, only that session; else everything."""
    if session_id:
        _pipeline_runs.pop(session_id, None)
    else:
        _pipeline_runs.clear()


def get_run(run_id: str, session_id: str = "") -> Optional[Dict[str, Any]]:
    """Look up a run. Checks Supabase cache first, then in-memory store."""
    # Check Supabase cache first
    if AppConfig.SUPABASE_URL and AppConfig.SUPABASE_KEY:
        cache = get_supabase_cache(AppConfig.SUPABASE_URL, AppConfig.SUPABASE_KEY)
        cached_run = cache.get_cached_run(run_id, session_id)
        if cached_run:
            # Reconstruct run_record from cache
            return {
                "run_id": run_id,
                "session_id": cached_run["session_id"],
                "status": "completed",
                "created_at": cached_run["created_at"],
                "schema_enriched": cached_run["enriched_schema"],
                "pipeline_log": [],  # For now, not cached
                "errors": [],
            }
    
    # Fall back to in-memory store
    if session_id:
        store = _session_store(session_id)
        if run_id in store:
            return store[run_id]
    
    # Fallback: search all sessions (so run_id-based URLs still work)
    for store in _pipeline_runs.values():
        if run_id in store:
            return store[run_id]
    
    return None


def list_runs(session_id: str = "") -> list:
    store = _session_store(session_id) if session_id else {}
    return [
        {
            "run_id": k,
            "status": v["status"],
            "created_at": v["created_at"],
            "schema_enriched": v.get("schema_enriched"),
            "pipeline_log": v.get("pipeline_log", []),
            "errors": v.get("errors", []),
        }
        for k, v in sorted(store.items(), key=lambda x: x[1]["created_at"], reverse=True)
    ]


def execute_pipeline(connection_string: str, session_id: str = "") -> Dict[str, Any]:
    """
    Execute the LangGraph pipeline synchronously and return results.
    Tracks execution steps for the pipeline integrity log.
    """
    run_id = str(uuid.uuid4())[:8]
    store = _session_store(session_id)

    run_record = {
        "run_id": run_id,
        "status": "running",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "connection_string": connection_string,
        "schema_enriched": None,
        "pipeline_log": [],
        "errors": [],
    }
    store[run_id] = run_record

    try:
        initial_state = {
            "connection_string": connection_string,
            "retry_count": 0,
            "errors": [],
            "schema_raw": {},
            "schema_enriched": {},
        }

        app = build_pipeline()
        pipeline_log = []
        enrich_count = 0
        final_state = dict(initial_state)

        for event in app.stream(initial_state):
            for node_name, node_output in event.items():
                final_state.update(node_output)

                if node_name == "extract":
                    table_count = len(node_output.get("schema_raw", {}))
                    total_cols = sum(
                        len(t.get("columns", {}))
                        for t in node_output.get("schema_raw", {}).values()
                    )
                    pipeline_log.append({
                        "step": "extract",
                        "status": "success",
                        "message": f"Extracted {table_count} tables, {total_cols} columns with statistical profiling",
                        "icon": "🔬",
                        "errors": [],
                    })

                elif node_name == "enrich":
                    enrich_count += 1
                    pipeline_log.append({
                        "step": "enrich",
                        "status": "success",
                        "message": f"AI enrichment pass {enrich_count} — Gemini analysis with ReAct tool-calling",
                        "icon": "🧠",
                        "errors": [],
                    })

                elif node_name == "validate":
                    v_status = node_output.get("validation_status", "PENDING")
                    v_errors = node_output.get("errors", [])
                    if v_status == "PASSED":
                        pipeline_log.append({
                            "step": "validate",
                            "status": "passed",
                            "message": "Validation PASSED — zero hallucinations, zero data loss",
                            "icon": "✅",
                            "errors": [],
                        })
                    else:
                        pipeline_log.append({
                            "step": "validate",
                            "status": "failed",
                            "message": f"Validation FAILED — {len(v_errors)} integrity violation(s) caught",
                            "icon": "🔄",
                            "errors": v_errors,
                        })

        # Finalize
        if final_state.get("validation_status") == "PASSED":
            # JSON-serialize to clean Decimal types
            clean_enriched = json.loads(
                json.dumps(final_state["schema_enriched"], cls=DecimalEncoder)
            )
            run_record["status"] = "completed"
            run_record["schema_enriched"] = clean_enriched
            run_record["pipeline_log"] = pipeline_log
            
            # Cache to Supabase (if configured)
            if AppConfig.SUPABASE_URL and AppConfig.SUPABASE_KEY:
                try:
                    cache = get_supabase_cache(AppConfig.SUPABASE_URL, AppConfig.SUPABASE_KEY)
                    if cache.is_enabled():
                        cache.set_cached_run(
                            run_id=run_id,
                            session_id=session_id,
                            enriched_schema=clean_enriched,
                            raw_schema=final_state.get("schema_raw", {}),
                            ttl_days=7
                        )
                except Exception as e:
                    logger.warning(f"Failed to cache run to Supabase: {e}. Continuing with in-memory storage.")
        else:
            run_record["status"] = "failed"
            run_record["errors"] = final_state.get("errors", [])
            run_record["pipeline_log"] = pipeline_log

    except Exception as e:
        logger.error(f"Pipeline execution error: {e}")
        run_record["status"] = "failed"
        run_record["errors"] = [str(e)]

    store[run_id] = run_record
    return run_record
