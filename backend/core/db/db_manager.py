# backend/core/db/db_manager.py

from typing import Dict, TypedDict
from pathlib import Path
import json

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from backend.utils.logger import logger
from backend.utils.config import DATA_DIR


# ============================================================
# 🧠 Session-scoped DB connection metadata (IN-MEMORY)
# ============================================================

class DBSession(TypedDict):
    engine: Engine
    db_type: str   # postgresql | mysql | sqlite | etc.


# session_id -> DBSession (runtime cache)
_DB_CONNECTIONS: Dict[str, DBSession] = {}


# ============================================================
# 📁 Persistent DB config path helpers
# ============================================================

def _get_db_session_dir(session_id: str) -> Path:
    return DATA_DIR / "db" / session_id

def _get_db_config_path(session_id: str) -> Path:
    return _get_db_session_dir(session_id) / "db_config.json"


# ============================================================
# 🔌 CONNECT TO DATABASE (EXPLICIT USER ACTION)
# ============================================================

def connect_db(session_id: str, connection_string: str) -> None:
    """
    Explicitly connect a database for a session.

    - Creates SQLAlchemy engine
    - Validates connection immediately
    - Detects DB type
    - Stores engine in memory
    - Persists connection config on disk

    Parameters:
    - session_id: user session identifier
    - connection_string: SQLAlchemy-compatible DB URL

    Example:
        postgresql+psycopg2://user:pass@host:5432/dbname
        mysql+pymysql://user:pass@host/dbname
        sqlite:///./local.db
    """

    if session_id in _DB_CONNECTIONS:
        logger.info(f"🔁 DB already connected for session {session_id}")
        return

    try:
        logger.info(f"🔌 Connecting DB for session {session_id}")

        engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            future=True
        )

        # Test connection immediately
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        db_type = engine.dialect.name  # DB type Detection

        # 🧠 Cache in memory
        _DB_CONNECTIONS[session_id] = {
            "engine": engine,
            "db_type": db_type
        }

        # 💾 Persist config to disk
        session_dir = _get_db_session_dir(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)

        config_path = _get_db_config_path(session_id)
        config_path.write_text(
            json.dumps(
                {
                    "connection_string": connection_string,
                    "db_type": db_type,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        logger.info(
            f"✅ DB connected & persisted| session={session_id} | db_type={db_type}"
        )

    except SQLAlchemyError as e:
        logger.exception("❌ Failed to connect to database")
        raise RuntimeError(f"Database connection failed: {str(e)}")


# ============================================================
# 📦 GET ACTIVE DB CONNECTION (LAZY INITIALIZATION)
# ============================================================

def get_db_engine(session_id: str) -> Engine:
    """
    Retrieve the SQLAlchemy Engine for a session.

    Behavior:
    1️⃣ If engine exists in memory → return it
    2️⃣ Else if persisted config exists → recreate engine (lazy init)
    3️⃣ Else → raise error (DB never connected)
    """

    # 1️⃣ Fast path: engine already in memory
    session = _DB_CONNECTIONS.get(session_id)
    if session:
        return session["engine"]
    
    # 2️⃣ Lazy load from disk
    config_path = _get_db_config_path(session_id)

    if not config_path.exists():
        raise RuntimeError(
            f"❌ No database connected for session {session_id}. "
            "User must provide a connection string first."
        )
    
    try:
        logger.info(f"♻️ Rehydrating DB connection for session {session_id}")

        config = json.loads(config_path.read_text(encoding="utf-8"))
        connection_string = config["connection_string"]
        db_type = config["db_type"]

        engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            future=True,
        )

        # Optional quick validation
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        _DB_CONNECTIONS[session_id] = {
            "engine": engine,
            "db_type": db_type,
        }

        logger.info(
            f"✅ DB connection restored | session={session_id} | db_type={db_type}"
        )

        return engine
    
    except Exception as e:
        logger.exception("❌ Failed to restore DB connection")
        raise RuntimeError(f"Failed to restore DB connection: {e}")


# ============================================================
# 🏷 GET DATABASE TYPE
# ============================================================

def get_db_type(session_id: str) -> str:
    """
    Return database type for a session.
    Works even after backend restart.
    """

    # In-memory fast path
    session = _DB_CONNECTIONS.get(session_id)
    if session:
        return session["db_type"]

    # Disk fallback
    config_path = _get_db_config_path(session_id)
    if not config_path.exists():
        raise RuntimeError(f"❌ No database configured for session {session_id}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    return config["db_type"]


# ============================================================
# 🔥 DISCONNECT DATABASE
# ============================================================

def disconnect_db(session_id: str) -> None:
    """
    Dispose and remove DB connection for a session.
    Does NOT delete persisted config (handled by reset_session).
    """

    session = _DB_CONNECTIONS.pop(session_id, None)

    if session:
        logger.info(f"🔌 Disconnecting DB for session {session_id}")
        session["engine"].dispose()
        logger.info(f"✅ DB disconnected for session {session_id}")


# ============================================================
# 🧹 GLOBAL CLEANUP (OPTIONAL - APP SHUTDOWN)
# ============================================================

def clear_all_db_connections() -> None:
    """
    Dispose ALL active DB connections.
    Used on app shutdown if needed.
    """

    logger.warning("🧹 Clearing ALL DB connections")

    for session_id, session in _DB_CONNECTIONS.items():
        logger.info(f"🔌 Closing DB for session {session_id}")
        session["engine"].dispose()

    _DB_CONNECTIONS.clear()