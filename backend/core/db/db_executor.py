# backend/core/db/db_executor.py

from typing import Dict, Any, List
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Result

from backend.utils.logger import logger

# DB core
from backend.core.db.db_manager import get_db_engine
from backend.core.db.schema_inspector import inspect_schema
from backend.core.db.db_query_generator import generate_sql_query

# Memory
from backend.core.memory.session_memory import (
    add_to_session_memory,
    get_session_memory,
)

# LLM (final explanation only)
from backend.core.llm.llm_engine import generate_db_answer


# ============================================================
# 🔒 JSON SERIALIZATION — SINGLE SOURCE OF TRUTH
# ============================================================

def make_json_safe(value: Any) -> Any:
    """
    Recursively convert ANY Python object into JSON-serializable data.

    This function is the FINAL GATE before crossing the tool boundary.
    """

    # Fast-path JSON primitives
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    # Known non-JSON-safe primitives
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, UUID):
        return str(value)

    # Containers (recursive)
    if isinstance(value, dict):
        return {str(k): make_json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(v) for v in value]

    # Final safety net — NEVER let objects escape
    return str(value)


def _execute_sql(engine, sql: str) -> List[Dict[str, Any]]:
    """
    Execute a READ-ONLY SQL query and return JSON-safe rows.
    """
    with engine.connect() as conn:
        result: Result = conn.execute(text(sql))
        rows: List[Dict[str, Any]] = []

        for row in result:
            raw_row = dict(row._mapping)
            safe_row = make_json_safe(raw_row)
            rows.append(safe_row)

        return rows


# ============================================================
# 1️⃣ TOOL FUNCTION — NO LLM
# ============================================================

async def run_db_execution(
    session_id: str,
    query: str,
) -> Dict[str, Any]:
    """
    DB TOOL (tool-safe, NO LLM).

    This function MUST return JSON-serializable data only.
    """

    logger.info(f"🗄️ DB Execution | Session={session_id} | Query='{query}'")

    # Save user query
    add_to_session_memory(session_id, "user", query)

    # Inspect schema
    schema = inspect_schema(session_id)

    # Generate SQL
    sql_payload = generate_sql_query(
        session_id=session_id,
        user_question=query,
        schema=schema,
    )

    sql = sql_payload.get("sql")

    # Safety fallback
    if not sql or sql.upper().startswith("NO SQL"):
        logger.warning("🚫 SQL generation blocked")
        return {
            "query": query,
            "sql": None,
            "db_type": sql_payload.get("db_type"),
            "tables_used": [],
            "rows": [],
            "row_count": 0,
            "confidence": "low",
        }

    # Execute SQL
    engine = get_db_engine(session_id)
    rows = _execute_sql(engine, sql)

    logger.info(f"✅ DB Execution Complete | Rows={len(rows)}")

    # 🔒 TOOL-SAFE PAYLOAD (ABSOLUTELY JSON)
    return {
        "query": query,
        "sql": sql,
        "db_type": sql_payload["db_type"],
        "tables_used": sql_payload["tables_used"],
        "rows": rows,
        "row_count": len(rows),
        "confidence": sql_payload["confidence"],
    }


# ============================================================
# 2️⃣ FINAL GENERATION — LLM EXPLANATION
# ============================================================

async def run_db_generation(
    session_id: str,
    tool_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    FINAL DB ANSWER GENERATION (LLM).

    tool_payload is GUARANTEED JSON-safe here.
    """

    logger.info(f"🤖 DB Generation | Session={session_id}")

    query = tool_payload["query"]
    rows = tool_payload["rows"]
    sql = tool_payload["sql"]
    db_type = tool_payload["db_type"]
    tables_used = tool_payload["tables_used"]

    # Load memory (exclude current user query)
    memory = get_session_memory(session_id)
    memory_for_context = (
        memory[:-1] if memory and memory[-1]["role"] == "user" else memory
    )

    memory_text = (
        "\n".join(f"{m['role']}: {m['content']}" for m in memory_for_context)
        if memory_for_context else None
    )

    # LLM explanation
    llm_result = generate_db_answer(
        query=query,
        sql=sql,
        rows=rows,
        db_type=db_type,
        memory_text=memory_text,
    )

    # Save assistant reply
    add_to_session_memory(session_id, "assistant", llm_result["response"])

    # Citations
    db_citation = {
        "type": "database",
        "db_type": db_type,
        "tables": tables_used,
        "sql": sql,
    }

    formatted_citations = (
        f"🗄️ Source: {db_type.upper()} database\n"
        f"📊 Tables used: {', '.join(tables_used)}\n"
        f"🧠 Generated SQL:\n{sql}"
    )

    return {
        "query": query,
        "response": llm_result["response"],
        "model": llm_result["model"],
        "used_chunks": 0,
        "rows": rows,
        "row_count": tool_payload["row_count"],
        "confidence": tool_payload["confidence"],
        "citations": [db_citation],
        "formatted_citations": formatted_citations,
    }