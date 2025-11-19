from typing import Optional
from sentence_transformers import SentenceTransformer
from backend.utils.config import EMBEDDING_MODEL
from backend.utils.logger import logger

# Global model cache
_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """
    Load and return the embedding model (cached globally).
    Ensures model is loaded only once for the whole app.
    """
    global _model

    if _model is not None:
        return _model

    try:
        logger.info(f"🔄 Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("✅ Embedding model loaded successfully!")
        return _model

    except Exception as e:
        logger.error(f"❌ Failed to load embedding model {EMBEDDING_MODEL}: {e}")
        raise RuntimeError(f"Error loading embedding model: {e}")