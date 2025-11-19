import json
from pathlib import Path
from typing import List, Dict

from backend.utils.logger import logger
from backend.utils.config import PROCESSED_DIR
from backend.core.model_manager import get_embedding_model
from backend.core.qdrant_manager import upsert_embedding

def embed_chunks(session_id: str, model=None) -> List[Dict]:
    """
    Generate embeddings for all chunks in a session and upsert them into Qdrant.
    ✅ Uses the preloaded model from FastAPI's app.state if passed.
    """

    # ✅ Use preloaded model (from FastAPI app.state) if available
    if model is None:
        model = get_embedding_model()

    session_dir = PROCESSED_DIR / session_id
    doc_folders = [d for d in session_dir.iterdir() if d.is_dir() and d.name != "embeddings"]

    if not doc_folders:
        raise FileNotFoundError("❌ No document folders found. Run extraction + cleaning + chunking first.")

    logger.info(f"🧠 Generating embeddings for session: {session_id}")

    total_embeddings = []

    for doc_folder in doc_folders:
        chunk_root = doc_folder / f"chunks_{doc_folder.name}"
        if not chunk_root.exists():
            logger.warning(f"⚠️ No chunks for {doc_folder.name}, skipping.")
            continue

        embed_dir = doc_folder / "embeddings"
        embed_dir.mkdir(exist_ok=True)

        chunk_folders = sorted(chunk_root.glob("chunk_*"))

        for chunk_folder in chunk_folders:
            text_file = chunk_folder / "text.txt"
            meta_file = chunk_folder / "meta.json"

            if not text_file.exists() or not meta_file.exists():
                logger.warning(f"⚠️ Missing files in {chunk_folder}, skipping.")
                continue

            text = text_file.read_text(encoding="utf-8")
            meta = json.loads(meta_file.read_text(encoding="utf-8"))

            # ✅ Generate embedding
            vector = model.encode(text).tolist()

            embed_record = {
                "chunk_id": meta["chunk_id"],
                "session_id": meta["session_id"],
                "text": text,
                "vector": vector,
                "metadata": meta
            }

            # ✅ Save locally
            chunk_id = meta["chunk_index"]
            embed_file = embed_dir / f"chunk_{chunk_id}.json"
            embed_file.write_text(json.dumps(embed_record, indent=2), encoding="utf-8")

            # ✅ Upsert into Qdrant (uses global client from qdrant_manager)
            upsert_embedding(embed_record)

            total_embeddings.append(embed_record)
            logger.info(f"✅ Saved & upserted embedding for {embed_file}")

    logger.info(f"🎯 Total embeddings created & stored: {len(total_embeddings)}")
    return total_embeddings