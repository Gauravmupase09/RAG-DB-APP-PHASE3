import hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from backend.utils.config import QDRANT_HOST, QDRANT_PORT, EMBEDDING_MODEL
from backend.utils.logger import logger


# ✅ Connect to Qdrant (local docker or cloud)
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def string_to_int_id(s: str) -> int:
    """Convert string to deterministic integer ID (Qdrant requirement)"""
    return int(hashlib.sha256(s.encode()).hexdigest(), 16) % (10**12)


def get_collection_name(session_id: str) -> str:
    """Each session gets its own vector collection"""
    return f"session_{session_id}"


def create_collection_if_not_exists(session_id: str, vector_dim: int = 384):
    """
    Create Qdrant collection for a session if not exists.
    
    ⚠️ BGE-small embedding dimension = 384
    """

    collection_name = get_collection_name(session_id)

    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if collection_name in existing:
        logger.info(f"📦 Collection already exists: {collection_name}")
        return

    logger.info(f"🚀 Creating Qdrant collection: {collection_name}")

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_dim,
            distance=Distance.COSINE
        )
    )
    logger.info(f"🚀 Created Qdrant collection: {collection_name}")


def upsert_embedding(record: dict):
    """
    Upsert a single embedding into Qdrant.
    """

    session_id = record["session_id"]
    collection_name = get_collection_name(session_id)

    # Ensure collection exists
    create_collection_if_not_exists(session_id)

    # ✅ Convert chunk string ID → numeric ID for Qdrant
    point_id = string_to_int_id(record["chunk_id"])

    payload = {
        "chunk_id": record["chunk_id"],
        "session_id": record["session_id"],
        "text": record["text"],          # ✅ store text in Qdrant
        **record["metadata"]             # ✅ include metadata fields
    }

    point = PointStruct(
        id=point_id,        # Chunk ID as Qdrant ID
        vector=record["vector"],      # Embedding vector
        payload=payload
    )

    client.upsert(
        collection_name=collection_name,
        points=[point]
    )

    logger.info(f"📥 Upserted chunk to Qdrant: {record['chunk_id']}")
    

def delete_collection(collection_name: str):
    """
    Delete a Qdrant collection safely.
    Used when clearing or resetting a user session.
    """
    try:
        client.delete_collection(collection_name=collection_name)
        logger.info(f"🗑️ Deleted Qdrant collection: {collection_name}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to delete collection {collection_name}: {e}")