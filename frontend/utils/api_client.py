import requests
from typing import Dict, Any, Optional
from utils.config import BACKEND_URL


def _safe_json(resp: requests.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {"status": "error", "detail": resp.text}


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
    url = f"{BACKEND_URL}/api/list_docs"
    params = {"session_id": session_id}
    resp = requests.get(url, params=params)
    return _safe_json(resp)


# =====================================
# Trigger processing (POST /api/process/{session_id})
# =====================================
def process_file(session_id: str) -> Dict[str, Any]:
    url = f"{BACKEND_URL}/api/process/{session_id}"
    resp = requests.post(url)
    return _safe_json(resp)


# =====================================
# Send query to RAG pipeline (POST /api/query)
# =====================================
def send_query(session_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
    url = f"{BACKEND_URL}/api/query"
    payload = {
        "session_id": session_id,
        "query": query,
        "top_k": top_k
    }
    resp = requests.post(url, json=payload)
    return _safe_json(resp)


# =====================================
# Reset session (DELETE /api/reset_session?session_id=...)
# =====================================
def reset_session(session_id: str) -> Dict[str, Any]:
    url = f"{BACKEND_URL}/api/reset_session"
    params = {"session_id": session_id}
    resp = requests.delete(url, params=params)
    return _safe_json(resp)