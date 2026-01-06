# backend/core/db/db_query_generator.py

from typing import Dict, Any, List
import json
import re

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

from backend.core.llm.llm_engine import get_llm
from backend.core.db.db_manager import get_db_type
from backend.core.db.db_types import get_db_dialect
from backend.utils.logger import logger



# ============================================================
# 🧠 PROMPT BUILDER
# ============================================================

SQL_PROMPT_TEMPLATE = """
You are an expert SQL query generator.

Database Engine:
- Name: {db_name}

DIALECT RULES (STRICT):
- Case-insensitive text matching uses: {case_insensitive_like}
- Boolean TRUE is represented as: {boolean_true}
- Boolean FALSE is represented as: {boolean_false}
- Current timestamp function: {date_now}
- Pagination syntax: {limit_syntax}
- Notes: {notes}

SAFETY RULES (ABSOLUTE — NO EXCEPTIONS):
- ONLY generate READ-ONLY queries
- The query MUST start with SELECT
- The query MUST NOT contain:
  - DROP
  - DELETE
  - TRUNCATE
  - ALTER
  - INSERT
  - UPDATE
  - MERGE
- The query MUST NOT contain multiple statements
- The character ';' is strictly forbidden anywhere in the output
- If the user request implies data modification or schema changes, return NO SQL

STRICT RULES (MANDATORY):
- Use ONLY tables and columns from the schema
- Use ONLY the SQL syntax compatible with {db_name}
- DO NOT guess table or column names
- DO NOT hallucinate joins (use ONLY defined foreign keys)
- Do NOT use SELECT *
- DO NOT add explanations
- DO NOT add comments
- DO NOT use markdown
- DO NOT wrap output in backticks
- Return ONLY ONE valid SQL query

Database Schema (JSON):
{schema}

User Question:
{question}

Return ONLY SQL:
""".strip()



# ============================================================
# 🔧 BUILD SQL GENERATION CHAIN
# ============================================================

def _build_sql_chain() -> RunnableSequence:
    """
    Build Prompt → LLM chain for SQL generation.
    Deterministic output (temperature = 0).
    """
    llm = get_llm(
        model_name="gemini-2.5-flash",
        temperature=0.0  # deterministic SQL
    )

    prompt = PromptTemplate(
        input_variables=[
            "db_name",
            "case_insensitive_like",
            "boolean_true",
            "boolean_false",
            "date_now",
            "limit_syntax",
            "notes",
            "schema",
            "question",
        ],
        template=SQL_PROMPT_TEMPLATE,
    )

    return RunnableSequence(prompt | llm)



# ============================================================
# 🔍 TABLE EXTRACTION (POST-GENERATION)
# ============================================================

def _extract_tables_from_sql(sql: str) -> List[str]:
    """
    Extract table names from FROM / JOIN clauses.
    This parses the GENERATED SQL, not the schema.
    """
    pattern = r"(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    return list(set(re.findall(pattern, sql, re.IGNORECASE)))



# ============================================================
# 🧠 NATURAL LANGUAGE → SQL (PUBLIC API)
# ============================================================

def generate_sql_query(session_id: str, user_question: str, schema: Dict) -> Dict[str, Any]:
    """
    Generate structured SQL output from NL query.

    Returns:
    {
        sql: str,
        db_type: str,
        tables_used: List[str],
        confidence: "high" | "low"
    }
    """

    logger.info("🧠 Generating SQL query from natural language")

    # 1️⃣ Detect DB type
    db_type = get_db_type(session_id)

    # 2️⃣ Load dialect rules
    dialect = get_db_dialect(db_type)

    # 3️⃣ Build chain inputs
    chain_inputs = {
        "db_name": dialect["name"],
        "case_insensitive_like": dialect["case_insensitive_like"],
        "boolean_true": dialect["boolean_true"],
        "boolean_false": dialect["boolean_false"],
        "date_now": dialect["date_now"],
        "limit_syntax": dialect["limit_syntax"],
        "notes": dialect["notes"],
        "schema": json.dumps(schema, indent=2),
        "question": user_question,
    }

    # 4️⃣ Run LLM
    chain = _build_sql_chain()
    result = chain.invoke(chain_inputs)

    sql = getattr(result, "content", str(result)).strip()

    # 5️⃣ Extract tables
    tables_used = _extract_tables_from_sql(sql)

    # 6️⃣ Confidence heuristic
    confidence = "low" if "INSUFFICIENT_SCHEMA" in sql.upper() else "high"

    logger.info(f"✅ SQL generated | db={db_type} | tables={tables_used} | confidence={confidence}")

    return {
        "sql": sql,
        "db_type": db_type,
        "tables_used": tables_used,
        "confidence": confidence,
    }