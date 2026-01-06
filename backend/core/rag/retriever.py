# backend/core/rag/retriever.py

from typing import List, Dict
from backend.utils.logger import logger
from backend.core.rag.resource_store import resource_store


def retrieve_top_k_chunks(session_id: str, query: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve top K most relevant text chunks from Qdrant for this session.
    Returns structured output ready for citation handling and LLM context building.
    """

    logger.info(f"🔍 Retrieving for session={session_id} | top_k={top_k}")

    # 🧠 Access global model/client (FastAPI OR tool)
    client = resource_store.qdrant_client
    model = resource_store.embedding_model

    # ✅ Convert query → embedding vector
    query_vector = model.encode(query).tolist()
    collection_name = f"session_{session_id}"
    logger.info(f"📦 Searching collection: {collection_name}")

    # ✅ Perform semantic search with error handling
    try:
        response = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,     # include metadata + text
            with_vectors=False     # skip returning embeddings
        )
    except Exception as e:
        logger.error(f"⚠️ Retrieval failed for session {session_id}: {e}")
        return []

    # ✅ Format results (citation-friendly)
    results = []
    for idx, hit in enumerate(response.points, start=1):
        payload = hit.payload or {}

        # 🧾 Build citation info (used by citation_handler.py)
        citation_info = {
            "rank": idx,
            "score": round(hit.score, 4),
            "chunk_id": payload.get("chunk_id"),
            "session_id": payload.get("session_id"),
            "file_name": payload.get("original_file_name"),
            "file_path": payload.get("original_file_path"),
            "chunk_index": payload.get("chunk_index"),
            "total_chunks_in_file": payload.get("total_chunks_in_file"),
            "doc_type": payload.get("doc_type"),
        }

        # 🧹 Clean and structure final output
        results.append({
            "citation": citation_info,
            "text": payload.get("text", "").strip(),
            "metadata": payload  # keep full metadata (optional, may help in debug/future use)
        })

    logger.info(f"✅ Retrieved {len(results)} chunks for query → '{query}'")
    return results