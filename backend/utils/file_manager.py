# backend/utils/file_manager.py

import shutil
from typing import List
from fastapi import UploadFile

from backend.utils.config import UPLOAD_DIR, PROCESSED_DIR, DATA_DIR
from backend.utils.logger import logger
from backend.core.doc_processing_unit.qdrant_manager import delete_collection, get_collection_name


# ============================================================
# 🗂️ Session Folder Management
# ============================================================

def create_session_folders(session_id: str):
    """Create both upload and processed folders for a session."""
    session_upload_dir = UPLOAD_DIR / session_id
    session_processed_dir = PROCESSED_DIR / session_id

    session_upload_dir.mkdir(parents=True, exist_ok=True)
    session_processed_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"📁 Session folders created for: {session_id}")
    return session_upload_dir, session_processed_dir


def session_exists(session_id: str) -> bool:
    """Check if a session already exists."""
    return (UPLOAD_DIR / session_id).exists()


# ============================================================
# 📤 File Handling
# ============================================================

def save_file(file: UploadFile, session_id: str) -> str:
    """Save uploaded file to the upload folder for this session."""
    session_upload_dir, _ = create_session_folders(session_id)
    file_path = session_upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    logger.info(f"📥 Saved uploaded file: {file.filename} → {file_path}")
    return str(file_path)


def list_files(session_id: str) -> List[str]:
    """List uploaded files for a session."""
    session_upload_dir = UPLOAD_DIR / session_id

    if not session_upload_dir.exists():
        logger.warning(f"⚠️ No upload folder found for session: {session_id}")
        return []

    return [str(f) for f in session_upload_dir.iterdir() if f.is_file()]


def validate_file_limit(session_id: str, max_files: int = 3) -> bool:
    """Ensure user doesn't upload more than allowed number of files."""
    files = list_files(session_id)
    if len(files) >= max_files:
        logger.warning(f"🚫 Upload limit reached for session {session_id} ({max_files} files max).")
        return False
    return True


# ============================================================
# 🧹 Cleanup (Local + Qdrant)
# ============================================================

def clear_session_data(session_id: str):
    """
    Fully reset a session:
    - Deletes uploads
    - Deletes processed files
    - Deletes Qdrant collection
    - Deletes persisted DB config
    """
    logger.warning(f"🧹 Clearing ALL session data for: {session_id}")

    session_upload_dir = UPLOAD_DIR / session_id
    session_processed_dir = PROCESSED_DIR / session_id
    db_session_dir = DATA_DIR / "db" / session_id

    # -------------------------------
    # 1️⃣ Local folders
    # -------------------------------
    for folder in [session_upload_dir, session_processed_dir]:
        if folder.exists():
            shutil.rmtree(folder)
            logger.info(f"🗑️ Removed folder: {folder}")

    # -------------------------------
    # 2️⃣ Qdrant collection
    # -------------------------------
    try:
        delete_collection(get_collection_name(session_id))
        logger.info(f"🗑️ Deleted Qdrant collection for session: {session_id}")
    except Exception as e:
        logger.error(f"⚠️ Failed to delete Qdrant collection for {session_id}: {e}")

    # -------------------------------
    # 3️⃣ DB persisted config
    # -------------------------------
    if db_session_dir.exists():
        shutil.rmtree(db_session_dir)
        logger.info(f"🗑️ Removed DB config for session: {session_id}")

    return {
        "status": "cleared",
        "session_id": session_id,
    }