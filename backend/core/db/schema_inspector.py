# backend/core/db/schema_inspector.py

from typing import Dict, Any
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from backend.core.db.db_manager import get_db_engine
from backend.utils.logger import logger


# ============================================================
# 🧠 DATABASE SCHEMA INSPECTOR
# ============================================================

def inspect_schema(session_id: str) -> Dict[str, Any]:
    """
    Inspect database schema for a given session.

    Returns a structured schema dictionary suitable for:
      - LLM prompting
      - NL → SQL generation
      - Debugging / UI display

    Structure:
    {
        "tables": {
            "table_name": {
                "columns": [
                    {"name": "...", "type": "...", "nullable": bool}
                ],
                "primary_key": ["id"],
                "foreign_keys": [
                    {
                        "column": "...",
                        "ref_table": "...",
                        "ref_column": "..."
                    }
                ]
            }
        }
    }
    """

    logger.info(f"🔍 Inspecting DB schema for session {session_id}")

    engine: Engine = get_db_engine(session_id)
    inspector = inspect(engine)

    schema: Dict[str, Any] = {"tables": {}}

    for table_name in inspector.get_table_names():
        logger.info(f"📄 Found table: {table_name}")

        # Columns
        columns_info = []
        for col in inspector.get_columns(table_name):
            columns_info.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"],
            })

        # Primary key
        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get("constrained_columns", [])

        # Foreign keys
        foreign_keys_info = []
        for fk in inspector.get_foreign_keys(table_name):
            for local_col, ref_col in zip(
                fk.get("constrained_columns", []),
                fk.get("referred_columns", []),
            ):
                foreign_keys_info.append({
                    "column": local_col,
                    "ref_table": fk.get("referred_table"),
                    "ref_column": ref_col,
                })

        schema["tables"][table_name] = {
            "columns": columns_info,
            "primary_key": primary_keys,
            "foreign_keys": foreign_keys_info,
        }

    logger.info(f"✅ Schema inspection completed for session {session_id}")

    return schema