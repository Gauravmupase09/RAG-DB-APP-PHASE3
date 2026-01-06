# frontend/utils/api_client.py

import requests
from typing import Dict, Any, Optional
from utils.config import BACKEND_URL


# ============================================================
# 🧰 Internal helper
# ============================================================

def _safe_json(resp: requests.Response) -> Dict[str, Any]:
    """
    Safely parse JSON from backend response.
    Falls back to raw text if JSON decoding fails.
    """
    try:
        return resp.json()
    except Exception:
        return {
            "status": "error", 
            "detail": resp.text,
            "http_status": resp.status_code,
        }


# ================================
# Upload a file (POST /api/upload)
# ================================

def upload_file(session_id: Optional[str], file) -> Dict[str, Any]:
    """
    Upload a document to backend.
    If session_id is None, backend will create a new session and return it.
    Expects Streamlit's UploadedFile (file.getvalue()).
    """
    url = f"{BACKEND_URL}/api/upload"
    files = {"file": (file.name, file.getvalue())}
    data = {"session_id": session_id} if session_id else {}

    resp = requests.post(url, files=files, data=data)
    return _safe_json(resp)


# =====================================
# List uploaded documents (GET /api/list_docs)
# =====================================

def list_documents(session_id: str) -> Dict[str, Any]:
    """
    Fetch list of uploaded documents for a session.
    """
    url = f"{BACKEND_URL}/api/list_docs"
    params = {"session_id": session_id}
    resp = requests.get(url, params=params)
    return _safe_json(resp)


# =====================================
# Trigger processing (POST /api/process/{session_id})
# =====================================

def process_file(session_id: str) -> Dict[str, Any]:
    """
    Trigger document processing pipeline:
    extract → clean → chunk → embed
    """
    url = f"{BACKEND_URL}/api/process/{session_id}"
    resp = requests.post(url)
    return _safe_json(resp)


# =====================================
# Send query to RAG pipeline (POST /api/query)
# =====================================

def send_query(session_id: str, query: str) -> Dict[str, Any]:
    """
    Send a user query to the unified agentic endpoint.
    Supports:
      - General queries
      - RAG queries
      - Database queries
    """
    url = f"{BACKEND_URL}/api/query"
    payload = {
        "session_id": session_id,
        "query": query,
    }
    resp = requests.post(url, json=payload)
    return _safe_json(resp)


# ============================================================
# 🔌 Connect database (POST /api/db/connect)
# ============================================================

def connect_database(session_id: str, connection_string: str) -> Dict[str, Any]:
    """
    Connect a database to the current session.

    Args:
        session_id: User session ID
        connection_string: SQLAlchemy-compatible DB URL

    Returns:
        {
            "message": "...",
            "session_id": "...",
            "db_type": "postgresql | mysql | sqlite | ..."
        }
    """
    url = f"{BACKEND_URL}/api/db/connect"

    payload = {
        "session_id": session_id,
        "connection_string": connection_string,
    }

    resp = requests.post(url, json=payload)
    return _safe_json(resp)


# ============================================================
# 📊 Fetch DB schema (GET /api/db/schema)
# ============================================================

def fetch_db_schema(session_id: str) -> Dict[str, Any]:
    """
    Fetch database schema for the connected database.

    Returns:
        {
            "session_id": "...",
            "db_type": "...",
            "schema": {
                "tables": {
                    ...
                }
            }
        }
    """
    url = f"{BACKEND_URL}/api/db/schema"
    params = {"session_id": session_id}

    resp = requests.get(url, params=params)
    return _safe_json(resp)


# =====================================
# Reset session (DELETE /api/reset_session?session_id=...)
# =====================================

def reset_session(session_id: str) -> Dict[str, Any]:
    """
    Fully reset a session:
      - clears memory
      - deletes files
      - deletes Qdrant collection
      - disconnects DB
    """
    url = f"{BACKEND_URL}/api/reset_session"
    params = {"session_id": session_id}
    resp = requests.delete(url, params=params)
    return _safe_json(resp)