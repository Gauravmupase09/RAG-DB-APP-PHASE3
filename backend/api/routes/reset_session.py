# backend/api/routes/reset_session.py

from fastapi import APIRouter, HTTPException, Query
from backend.utils.logger import logger

from backend.utils.file_manager import clear_session_data, session_exists
from backend.core.memory.session_memory import clear_session_memory
from backend.core.db.db_manager import disconnect_db

router = APIRouter()


@router.delete("/reset_session")
async def reset_session(session_id: str = Query(..., description="Session ID to reset")):
    """
    🧹 Reset entire session:
    - Clears conversation memory
    - Deletes uploaded + rocessed files 
    - Deletes Qdrant vector collection
    - Disconnects the database connection (if any) for this session
    """

    try:
        logger.info(f"🧹 Reset request received for session: {session_id}")

        # --------------------------------------------------
        # 1️⃣ Validate session existence
        # --------------------------------------------------
        if not session_exists(session_id):
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
        
        # --------------------------------------------------
        # 2️⃣ Clear session memory
        # --------------------------------------------------
        clear_session_memory(session_id)
        logger.info("🧠 Session memory cleared.")

        # --------------------------------------------------
        # 3️⃣ Disconnect DB for this session (if connected)
        # --------------------------------------------------
        disconnect_db(session_id)
        logger.info("🗄️ Session DB disconnected (if existed).")

        # --------------------------------------------------
        # 4️⃣ Remove files + Qdrant collection
        # --------------------------------------------------
        result = clear_session_data(session_id)

        logger.info(f"✅ Session reset complete | session={session_id}")
        
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