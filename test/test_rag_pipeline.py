# tests/test_rag_pipeline.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from backend.core.model_manager import get_embedding_model
from backend.core.qdrant_manager import client as qdrant_client
from backend.core.rag.rag_pipeline import run_rag_pipeline
from backend.utils.logger import logger


# Simulate FastAPI app with global state (like in main.py)
app = FastAPI()
app.state.embedding_model = get_embedding_model()
app.state.qdrant_client = qdrant_client

# Dummy request for pipeline
class DummyRequest:
    app = app

request = DummyRequest()

# Test config
SESSION_ID = "427c6e4e-174b-4456-b803-062dd11e4823"
QUERY = "How did COVID-19 impact students emotionally and academically?"

import asyncio

async def test_pipeline():
    logger.info("\n🚀 Starting Full RAG Pipeline Test")
    result = await run_rag_pipeline(request, SESSION_ID, QUERY, top_k=3)

    print("\n=============================")
    print("🔍 Query:", result["query"])
    print("🧠 Model Used:", result["model"])
    print("💬 Response:\n", result["response"])
    print("\n📚 Citations:\n", result["formatted_citations"])
    print("=============================\n")

    # ✅ Sanity checks
    assert "response" in result
    assert isinstance(result["citations"], list)
    assert len(result["citations"]) > 0
    print("✅ RAG Pipeline executed successfully!")

if __name__ == "__main__":
    asyncio.run(test_pipeline())