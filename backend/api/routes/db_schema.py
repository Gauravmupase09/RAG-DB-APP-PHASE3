# backend/api/routes/db_schema.py

from fastapi import APIRouter, HTTPException, Query

from backend.utils.logger import logger
from backend.core.db.schema_inspector import inspect_schema
from backend.core.db.db_manager import get_db_type

router = APIRouter()


@router.get("/db/schema")
async def get_db_schema(
    session_id: str = Query(..., description="User session identifier"),
):
    """
    📊 Fetch database schema for the connected DB (READ-ONLY).

    PURPOSE:
        - Expose database schema to frontend
        - Support debugging and transparency
        - Reuse the SAME schema used internally for NL → SQL

    SOURCE OF TRUTH:
        - backend.core.db.schema_inspector.inspect_schema

    REQUIREMENTS:
        - Database must already be connected for this session

    RETURNS (structured, LLM-safe):
        {
            "session_id": "...",
            "db_type": "postgresql | mysql | sqlite | ...",
            "schema": {
                "tables": {
                    "table_name": {
                        "columns": [
                            {"name": "...", "type": "...", "nullable": true}
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
        }
    """

    try:
        logger.info(f"📊 DB schema request | session={session_id}")

        # 🔹 Inspect schema using core logic
        schema = inspect_schema(session_id)

        db_type = get_db_type(session_id)

        logger.info(
            f"✅ Schema returned | session={session_id} | tables={len(schema.get('tables', {}))}"
        )

        return {
            "session_id": session_id,
            "db_type": db_type,
            "schema": schema,
        }

    except Exception as e:
        logger.exception("❌ Failed to fetch DB schema")
        raise HTTPException(status_code=400, detail=str(e))