# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from contextlib import asynccontextmanager
import os

# ✅ Routers
from backend.api.routes.upload import router as upload_router
from backend.api.routes.process import router as process_router
from backend.api.routes.list_docs import router as list_docs_router
from backend.api.routes.reset_session import router as reset_router
from backend.api.routes.db_connect import router as db_connect_router
from backend.api.routes.db_schema import router as db_schema_router
from backend.api.routes.query import router as query_router

# ✅ Core
from backend.core.doc_processing_unit.model_manager import get_embedding_model
from backend.core.doc_processing_unit.qdrant_manager import client as qdrant_client
from backend.core.rag.resource_store import resource_store
from backend.utils.logger import logger

UPLOAD_DIR = "backend/data/uploads"

# ============================================================
# ⚙️ App Lifecycle Management
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load and clean up global resources using FastAPI lifespan."""
    logger.info("🚀 App startup — initializing embedding model and Qdrant connection...")

    # ✅ Load once at startup
    app.state.embedding_model = get_embedding_model()
    app.state.qdrant_client = qdrant_client


    # 🔥 NEW: Copy references for tools (LangGraph)
    resource_store.embedding_model = app.state.embedding_model
    resource_store.qdrant_client = app.state.qdrant_client

    logger.info("✅ Startup complete — model loaded and Qdrant connected.")
    yield

    # ✅ On shutdown
    logger.info("🧹 Shutting down — cleaning resources...")
    try:
        if app.state.qdrant_client is not None:
            app.state.qdrant_client.close()
            logger.info("🔌 Qdrant client connection closed.")
    except Exception as e:
        logger.warning(f"⚠️ Error closing Qdrant client: {e}")

    logger.info("👋 Shutdown complete.")


# ============================================================
# 🚀 App Initialization
# ============================================================
app = FastAPI(
    title="QueryVerse", 
    description="Agentic AI system to query documents and databases using natural language.", 
    version="3.0", 
    lifespan=lifespan
)


# ============================================================
# 🌍 Middleware
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 📂 Serve Uploaded Files Inline (Preview)
# ============================================================
@app.get("/uploads/{session_id}/{file_name:path}")
async def serve_uploaded_file(session_id: str, file_name: str):
    """
    Serve uploaded files with inline preview for PDF, TXT, CSV, DOCX.
    """
    file_path = os.path.join(UPLOAD_DIR, session_id, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    ext = os.path.splitext(file_path)[1].lower()

    # 🧩 PDF → open inline
    if ext == ".pdf":
        return FileResponse(file_path, media_type="application/pdf", headers={"Content-Disposition": "inline"})

    # 🧩 TXT → show as plain text
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return PlainTextResponse(content, media_type="text/plain")

    # 🧩 DOCX → convert to simple HTML (requires python-docx)
    if ext == ".docx":
        from docx import Document
        doc = Document(file_path)
        html = "<h3>📄 Document Preview:</h3><br>"
        for para in doc.paragraphs:
            html += f"<p>{para.text}</p>"
        return HTMLResponse(html)

    # 🧩 Default → just download
    return FileResponse(file_path, headers={"Content-Disposition": "attachment"})


# ============================================================
# 🔗 API Routers
# ============================================================
app.include_router(upload_router, prefix="/api", tags=["Upload"])
app.include_router(process_router, prefix="/api", tags=["Process"])
app.include_router(list_docs_router, prefix="/api", tags=["Documents List"])
app.include_router(reset_router, prefix="/api", tags=["Reset Session"])
app.include_router(db_connect_router, prefix="/api", tags=["Database Connection"])
app.include_router(db_schema_router, prefix="/api", tags=["Database Schema"])
app.include_router(query_router, prefix="/api", tags=["Query"])

# ============================================================
# 💓 Health Check
# ============================================================
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "RAG Backend is running 🚀"}