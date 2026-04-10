"""
SchemaDoc AI — FastAPI Backend Entry Point.
Production-grade API server wrapping the LangGraph pipeline.
"""
import sys
import logging
import subprocess
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.config import settings
from backend.core.exceptions import register_exception_handlers
from backend.core.rate_limiter import setup_rate_limiting
from backend.api.routes import pipeline, chat, export, schema

# ── Logging ──
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("SchemaDoc_API")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown events."""
    logger.info("🚀 SchemaDoc AI API starting up...")
    try:
        settings.validate_keys()
        logger.info("✅ Configuration validated.")
        
        # Generate sample databases if they don't exist
        ensure_sample_databases()
        
    except Exception as e:
        logger.warning(f"⚠️ Config warning: {e}")
    yield
    logger.info("SchemaDoc AI API shutting down.")


def ensure_sample_databases():
    """Generate sample databases on startup if they don't exist."""
    import subprocess
    data_dir = settings.DATA_DIR
    required_dbs = ["demo.db", "ecommerce.db", "music.db"]
    missing_dbs = [db for db in required_dbs if not (data_dir / db).exists()]
    
    if missing_dbs:
        logger.info(f"🔄 Generating missing sample databases: {missing_dbs}")
        try:
            generator_script = Path(__file__).resolve().parent.parent / "data" / "generate_samples.py"
            if generator_script.exists():
                result = subprocess.run(
                    [sys.executable, str(generator_script)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    logger.info("✅ Sample databases generated successfully")
                else:
                    logger.warning(f"⚠️ Database generation warning: {result.stderr}")
            else:
                logger.warning(f"⚠️ Database generator script not found at {generator_script}")
        except Exception as e:
            logger.warning(f"⚠️ Could not generate sample databases: {e}")
    else:
        logger.info(f"✅ All {len(required_dbs)} sample databases present")


# ── App Instance ──
app = FastAPI(
    title="SchemaDoc AI",
    description="AI-Powered Data Dictionary Generator — API Backend",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Centralized Error Handling ──
register_exception_handlers(app)

# ── Rate Limiting ──
setup_rate_limiting(app)

# ── Routes ──
app.include_router(pipeline.router)
app.include_router(schema.router)
app.include_router(chat.router)
app.include_router(export.router)


# ── Reset Session ──
@app.post("/api/reset")
async def reset_session(request: Request):
    """Clear pipeline runs and report caches for the caller's session."""
    from backend.services.pipeline_service import clear_all_runs
    from backend.api.routes.export import clear_session_reports

    sid = request.headers.get("x-session-id", "")
    clear_all_runs(session_id=sid)
    clear_session_reports(session_id=sid)

    cache_file = settings.DATA_DIR / "schema_cache.json"
    if cache_file.exists():
        cache_file.unlink()

    logger.info(f"Session reset — session '{sid or 'global'}' cleared.")
    return {"status": "ok", "message": "Session reset successfully"}


# ── Health Check ──
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SchemaDoc AI API",
        "version": "2.0.0",
    }


@app.get("/")
async def root():
    return {
        "message": "SchemaDoc AI API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
