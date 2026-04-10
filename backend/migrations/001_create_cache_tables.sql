-- Supabase Migration: Create cache tables for SchemaDoc AI
-- Run this against your Supabase PostgreSQL database

-- Table 1: Pipeline runs cache
-- Stores enriched schemas, report fields, and raw schemas
CREATE TABLE IF NOT EXISTS public.pipeline_runs_cache (
  run_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  enriched_schema JSONB NOT NULL,
  report_fields JSONB,
  raw_schema JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on session_id for faster queries
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_session_id ON pipeline_runs_cache(session_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_expires_at ON pipeline_runs_cache(expires_at);

-- Table 2: Schema context cache
-- Stores compressed schemas for quick chat context retrieval
CREATE TABLE IF NOT EXISTS public.schema_context_cache (
  schema_hash TEXT PRIMARY KEY,
  compressed_json TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on created_at for cleanup
CREATE INDEX IF NOT EXISTS idx_schema_context_created_at ON schema_context_cache(created_at);

-- Enable Row Level Security (optional, for production)
-- ALTER TABLE pipeline_runs_cache ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE schema_context_cache ENABLE ROW LEVEL SECURITY;

-- Create a cleanup job trigger (optional, requires pg_cron extension)
-- SELECT cron.schedule('cleanup-expired-cache', '0 2 * * *', 
--   'DELETE FROM public.pipeline_runs_cache WHERE expires_at < NOW()');

COMMENT ON TABLE public.pipeline_runs_cache IS 'Cache for enriched pipeline run results';
COMMENT ON TABLE public.schema_context_cache IS 'Cache for compressed schema contexts for chat';
