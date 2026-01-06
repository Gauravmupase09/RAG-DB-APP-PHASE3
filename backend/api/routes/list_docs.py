# backend/api/routes/list_docs.py

from fastapi import APIRouter, Query, HTTPException
from backend.utils.file_manager import list_files
from backend.utils.logger import logger

router = APIRouter()

@router.get("/list_docs")
async def list_uploaded_docs(
    session_id: str = Query(..., description="User session ID")
):
    """
    List all uploaded documents for a given session.
    """

    logger.info(f"📄 Listing uploaded documents for session: {session_id}")

    files = list_files(session_id)

    if not files:
        raise HTTPException(
            status_code=404,
            detail=f"No uploaded files found for session: {session_id}"
        )

    return {
        "session_id": session_id,
        "files_count": len(files),
        "files": files
    }