import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request

from backend.utils.logger import logger
from backend.utils.config import PROCESSED_DIR
from backend.utils.file_manager import session_exists

# ✅ Core pipeline imports
from backend.core.text_extractor import extract_all_files
from backend.core.text_cleaner import clean_all_raw_files
from backend.core.chunking import chunk_session_documents
from backend.core.embedding_engine import embed_chunks

router = APIRouter()


@router.post("/process/{session_id}")
async def process_documents(request: Request, session_id: str):
    """
    Full document processing pipeline:
    1️⃣ Extract text
    2️⃣ Clean text
    3️⃣ Chunk documents
    4️⃣ Embed chunks & upsert into Qdrant
    5️⃣ Update file_index.json
    """

    try:
        logger.info(f"🚀 Starting processing pipeline for session: {session_id}")

        # ✅ Check session existence
        if not session_exists(session_id):
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")

        # 1️⃣ Extract text
        extracted_files = extract_all_files(session_id)
        logger.info(f"📄 Extracted files: {len(extracted_files)}")

        # 2️⃣ Clean text
        cleaned_files = clean_all_raw_files(session_id)
        logger.info(f"🧽 Cleaned files: {len(cleaned_files)}")

        # 3️⃣ Chunk documents
        chunk_list = chunk_session_documents(session_id)
        chunk_summary = {}
        for meta in chunk_list:
            doc = meta["source_doc_folder"]
            chunk_summary[doc] = chunk_summary.get(doc, 0) + 1

        total_chunks = sum(chunk_summary.values())
        logger.info(f"✅ Total chunks created: {total_chunks}")

        # 4️⃣ Embed chunks + upsert to Qdrant
        embedding_model = request.app.state.embedding_model
        embeddings = embed_chunks(session_id, model=embedding_model)
        logger.info(f"🧠 Total embeddings generated & stored: {len(embeddings)}")

        # 5️⃣ Update metadata (mark processed)
        meta_file = PROCESSED_DIR / session_id / "file_index.json"
        if meta_file.exists():
            meta_data = json.loads(meta_file.read_text())
            for doc in meta_data:
                doc["processed"] = True
            meta_file.write_text(json.dumps(meta_data, indent=2), encoding="utf-8")
            logger.info("📁 Updated file_index.json: marked all docs as processed ✅")

        return {
            "session_id": session_id,
            "extracted_files": len(extracted_files),
            "cleaned_files": len(cleaned_files),
            "chunks_per_doc": chunk_summary,
            "total_chunks": total_chunks,
            "total_embeddings": len(embeddings),
            "status": "✅ Processing complete"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error during processing for session {session_id}")
        raise HTTPException(status_code=500, detail=str(e))