from fastapi import APIRouter, HTTPException, Query
from backend.utils.logger import logger
from backend.utils.file_manager import clear_session_data, session_exists
from backend.core.rag.session_memory import clear_session_memory

router = APIRouter()


@router.delete("/reset_session")
async def reset_session(session_id: str = Query(..., description="Session ID to reset")):
    """
    🧹 Reset entire session:
    - Deletes uploaded files
    - Deletes processed files
    - Deletes vector collection in Qdrant
    - Clears conversation memory
    """

    try:
        logger.info(f"🧹 Reset request received for session: {session_id}")

        # ✅ Check if session exists
        if not session_exists(session_id):
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
        
        # ✅ Remove memory
        clear_session_memory(session_id)
        logger.info("🧠 Session memory cleared.")

        # ✅ Remove local files + Qdrant collection
        result = clear_session_data(session_id)

        logger.info(f"✅ Session {session_id} reset complete.")
        
        return {
            "message": "✅ Session reset successfully",
            "session_id": session_id,
            **result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error resetting session {session_id}")
        raise HTTPException(status_code=500, detail=str(e))