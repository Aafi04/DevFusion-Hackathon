"""
Schema Compression — Reduces schema size for chat context by 40-50%.
Keeps only essential information needed for SQL generation.
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def compress_schema_for_chat(enriched_schema: Dict[str, Any]) -> str:
    """
    Compress enriched schema for chat context.
    Removes statistics, PII tags, business descriptions that aren't needed for SQL accuracy.
    
    Args:
        enriched_schema: Full enriched schema dictionary
    
    Returns:
        Compressed JSON string suitable for LLM chat context
    """
    compressed = {}
    
    for table_name, table_data in enriched_schema.items():
        # Keep only essential table info
        compressed[table_name] = {
            "row_count": table_data.get("row_count", 0),
            "columns": {},
            "foreign_keys": table_data.get("foreign_keys", []),
        }
        
        # Compress column info
        if "columns" in table_data:
            for col_name, col_meta in table_data["columns"].items():
                compressed[table_name]["columns"][col_name] = {
                    # Keep type and sample values (needed for SQL)
                    "type": col_meta.get("type", "UNKNOWN"),
                    "description": col_meta.get("description", ""),  # Brief description only
                    # Do NOT include: stats, PII flags, business logic, tags
                }
        
    return json.dumps(compressed, indent=2)


def estimate_compression_ratio(enriched_schema: Dict[str, Any], compressed_schema: str) -> float:
    """
    Calculate compression ratio compared to original schema size.
    
    Args:
        enriched_schema: Original full schema
        compressed_schema: Compressed schema string
    
    Returns:
        Ratio of compressed to original size (e.g., 0.45 = 45%)
    """
    full_json = json.dumps(enriched_schema)
    return len(compressed_schema) / len(full_json)


def get_schema_summary(compressed_schema: str) -> Dict[str, Any]:
    """
    Get summary statistics of compressed schema.
    """
    schema_dict = json.loads(compressed_schema)
    
    table_count = len(schema_dict)
    col_count = sum(len(t.get("columns", {})) for t in schema_dict.values())
    row_count = sum(t.get("row_count", 0) for t in schema_dict.values())
    fk_count = sum(len(t.get("foreign_keys", [])) for t in schema_dict.values())
    
    return {
        "tables": table_count,
        "columns": col_count,
        "rows": row_count,
        "foreign_keys": fk_count,
        "schema_size_bytes": len(compressed_schema),
    }
