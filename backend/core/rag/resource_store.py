# backend/core/rag/resource_store.py

class ResourceStore:
    """
    A lightweight global container that holds shared resources,
    accessible both from FastAPI routes and from LangGraph tools.
    """
    embedding_model = None
    qdrant_client = None

# Singleton instance
resource_store = ResourceStore()