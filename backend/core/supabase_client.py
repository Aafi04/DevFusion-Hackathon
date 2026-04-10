"""
Supabase Client — Persistent cache for pipeline runs and schemas.
Provides CRUD operations for caching enriched schemas to survive restarts.
"""
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import supabase (optional dependency)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("supabase package not available. Caching disabled.")


class SupabaseCache:
    """Supabase-backed persistent cache for pipeline runs."""
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """Initialize Supabase cache client."""
        self.enabled = False
        self.client: Optional[Client] = None
        
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase package not installed. Caching disabled.")
            return
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not provided. Caching disabled.")
            return
        
        try:
            self.client = create_client(supabase_url, supabase_key)
            self.enabled = True
            logger.info(f"✓ Supabase cache initialized: {supabase_url}")
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase cache: {e}")
            self.enabled = False
    
    def get_cached_run(self, run_id: str, session_id: str = "") -> Optional[Dict[str, Any]]:
        """Retrieve cached pipeline run from Supabase."""
        if not self.enabled or not self.client:
            return None
        
        try:
            response = self.client.table("pipeline_runs_cache").select("*").eq("run_id", run_id).single().execute()
            
            if response.data:
                data = response.data
                logger.info(f"✓ Cache hit for run {run_id}")
                
                # Parse JSON fields
                return {
                    "run_id": data["run_id"],
                    "session_id": data["session_id"],
                    "enriched_schema": json.loads(data["enriched_schema"]) if data.get("enriched_schema") else {},
                    "report_fields": json.loads(data["report_fields"]) if data.get("report_fields") else {},
                    "raw_schema": json.loads(data["raw_schema"]) if data.get("raw_schema") else {},
                    "created_at": data["created_at"],
                }
            return None
        except Exception as e:
            logger.debug(f"Cache lookup failed for {run_id}: {e}")
            return None
    
    def set_cached_run(
        self,
        run_id: str,
        session_id: str,
        enriched_schema: Dict[str, Any],
        report_fields: Optional[Dict[str, Any]] = None,
        raw_schema: Optional[Dict[str, Any]] = None,
        ttl_days: int = 7
    ) -> bool:
        """Store pipeline run in Supabase cache."""
        if not self.enabled or not self.client:
            return False
        
        try:
            expires_at = (datetime.now() + timedelta(days=ttl_days)).isoformat()
            
            data = {
                "run_id": run_id,
                "session_id": session_id,
                "enriched_schema": json.dumps(enriched_schema),
                "report_fields": json.dumps(report_fields or {}),
                "raw_schema": json.dumps(raw_schema or {}),
                "created_at": datetime.now().isoformat(),
                "expires_at": expires_at,
            }
            
            # Upsert (insert or update)
            response = self.client.table("pipeline_runs_cache").upsert(data).execute()
            logger.info(f"✓ Cached run {run_id} to Supabase (expires: {expires_at})")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache run {run_id}: {e}")
            return False
    
    def get_compressed_schema(self, schema_hash: str) -> Optional[str]:
        """Retrieve compressed schema from cache."""
        if not self.enabled or not self.client:
            return None
        
        try:
            response = self.client.table("schema_context_cache").select("compressed_json").eq("schema_hash", schema_hash).single().execute()
            
            if response.data:
                logger.info(f"✓ Cache hit for schema {schema_hash[:8]}")
                return response.data["compressed_json"]
            return None
        except Exception as e:
            logger.debug(f"Compressed schema cache miss: {e}")
            return None
    
    def set_compressed_schema(self, schema_hash: str, compressed_json: str) -> bool:
        """Store compressed schema in cache."""
        if not self.enabled or not self.client:
            return False
        
        try:
            data = {
                "schema_hash": schema_hash,
                "compressed_json": compressed_json,
                "created_at": datetime.now().isoformat(),
            }
            
            self.client.table("schema_context_cache").upsert(data).execute()
            logger.info(f"✓ Cached compressed schema {schema_hash[:8]}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache compressed schema: {e}")
            return False
    
    def cleanup_expired_cache(self, days_old: int = 7) -> int:
        """Remove expired cache entries (older than days_old)."""
        if not self.enabled or not self.client:
            return 0
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            # Delete from pipeline_runs_cache
            runs_response = self.client.table("pipeline_runs_cache").delete().lt("created_at", cutoff_date).execute()
            
            # Delete from schema_context_cache
            schema_response = self.client.table("schema_context_cache").delete().lt("created_at", cutoff_date).execute()
            
            logger.info(f"✓ Cleaned up expired cache entries older than {days_old} days")
            return 1  # Just return 1 to indicate cleanup ran
        except Exception as e:
            logger.warning(f"Cache cleanup failed: {e}")
            return 0
    
    def is_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self.enabled


# Singleton instance
_cache_instance: Optional[SupabaseCache] = None


def get_supabase_cache(supabase_url: Optional[str] = None, supabase_key: Optional[str] = None) -> SupabaseCache:
    """Get or create singleton Supabase cache instance."""
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = SupabaseCache(supabase_url, supabase_key)
    
    return _cache_instance
