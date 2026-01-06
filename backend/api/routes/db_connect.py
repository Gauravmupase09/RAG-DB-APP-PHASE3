# backend/api/routes/db_connect.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.utils.logger import logger
from backend.core.db.db_manager import connect_db, get_db_type

router = APIRouter()


# ============================================================
# 📦 Request Schema
# ============================================================

class DBConnectRequest(BaseModel):
    session_id: str = Field(..., description="User session identifier")
    connection_string: str = Field(
        ...,
        description="SQLAlchemy-compatible DB connection string"
    )


# ============================================================
# 🔌 Connect Database Route
# ============================================================

@router.post("/db/connect")
async def connect_database(payload: DBConnectRequest):
    """
    🔌 Connect a database to a user session.

    PURPOSE:
        - Establish a DB connection for a given session
        - Validate the connection immediately
        - Detect database type (postgresql, mysql, sqlite, etc.)
        - Store the connection in session-scoped memory

    IMPORTANT:
        - This does NOT run queries
        - This does NOT inspect schema
        - This does NOT generate answers

    This endpoint must be called BEFORE:
        - Any db_tool usage
        - Any database-based questions
    """

    try:
        logger.info(
            f"🔌 DB connect request | session={payload.session_id}"
        )

        # 1️⃣ Create DB connection (stored internally per session)
        connect_db(
            session_id=payload.session_id,
            connection_string=payload.connection_string,
        )

        # 2️⃣ Fetch detected DB type
        db_type = get_db_type(payload.session_id)

        logger.info(
            f"✅ DB connected successfully | session={payload.session_id} | db_type={db_type}"
        )

        return {
            "message": "✅ Database connected successfully",
            "session_id": payload.session_id,
            "db_type": db_type,
        }

    except Exception as e:
        logger.exception("❌ Database connection failed")
        raise HTTPException(status_code=400, detail=str(e))