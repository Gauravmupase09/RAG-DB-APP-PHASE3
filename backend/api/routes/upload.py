from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from datetime import datetime
from pathlib import Path
import uuid
import json

from backend.utils.file_manager import save_file, validate_file_limit, list_files, create_session_folders
from backend.utils.config import PROCESSED_DIR
from backend.utils.logger import logger

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str | None = Form(None) # or just Optional[str] = None
):
    """
    📤 Upload a document (PDF/DOCX/TXT)
    - If `session_id` is not provided → creates a new session automatically.
    - Stores metadata under /data/processed/<session_id>/upload_metadata.json
    - Max 3 files allowed per session.
    """

    # ✅ Determine if this is a new or existing session
    is_new_session = session_id is None

    # ✅ Create new session if not provided
    if is_new_session:
        session_id = str(uuid.uuid4())
        create_session_folders(session_id)
        logger.info(f"🆕 Created new session: {session_id}")
    else:
        logger.info(f"📂 Using existing session: {session_id}")

    # ✅ Validate upload limit (max 3 files)
    if not validate_file_limit(session_id):
        raise HTTPException(
            status_code=400,
            detail="Upload limit reached. Max 3 files allowed per session."
        )

    # ✅ Save uploaded file to uploads directory
    file_path = save_file(file, session_id)

    # ✅ Prepare upload metadata
    meta_dir = PROCESSED_DIR / session_id
    meta_dir.mkdir(parents=True, exist_ok=True)
    meta_file = meta_dir / "upload_metadata.json"

    upload_entry = {
        "file_name": file.filename,
        "file_path": str(file_path),
        "file_type": Path(file.filename).suffix.lower(),
        "uploaded_at": datetime.now().isoformat()
    }

    # ✅ Append metadata
    if meta_file.exists():
        data = json.loads(meta_file.read_text(encoding="utf-8"))
    else:
        data = []
    data.append(upload_entry)
    meta_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    logger.info(f"🕓 Stored upload metadata → {meta_file}")

    return {
        "message": "✅ File uploaded successfully",
        "session_id": session_id,
        "new_session": is_new_session,
        "uploaded_files": list_files(session_id),
        "saved_path": str(file_path)
    }