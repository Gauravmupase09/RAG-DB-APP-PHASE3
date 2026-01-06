# backend/core/db/db_types.py

from typing import Dict, Any


# ============================================================
# 🧠 DATABASE DIALECT DEFINITIONS
# ============================================================

DB_DIALECTS: Dict[str, Dict[str, Any]] = {
    "postgresql": {
        "name": "PostgreSQL",
        "supports_joins": True,
        "case_insensitive_like": "ILIKE",
        "boolean_true": "TRUE",
        "boolean_false": "FALSE",
        "date_now": "NOW()",
        "limit_syntax": "LIMIT {limit} OFFSET {offset}",
        "notes": "Use ILIKE for case-insensitive text search"
    },

    "mysql": {
        "name": "MySQL",
        "supports_joins": True,
        "case_insensitive_like": "LIKE",
        "boolean_true": "1",
        "boolean_false": "0",
        "date_now": "NOW()",
        "limit_syntax": "LIMIT {offset}, {limit}",
        "notes": "LIMIT offset, limit syntax"
    },

    "sqlite": {
        "name": "SQLite",
        "supports_joins": True,
        "case_insensitive_like": "LIKE",
        "boolean_true": "1",
        "boolean_false": "0",
        "date_now": "CURRENT_TIMESTAMP",
        "limit_syntax": "LIMIT {limit} OFFSET {offset}",
        "notes": "Limited ALTER TABLE support"
    },
}


# ============================================================
# 🏷 PUBLIC HELPERS
# ============================================================

def get_db_dialect(db_type: str) -> Dict[str, Any]:
    """
    Return dialect rules for a DB type.
    """
    dialect = DB_DIALECTS.get(db_type)

    if not dialect:
        raise ValueError(f"Unsupported database type: {db_type}")

    return dialect