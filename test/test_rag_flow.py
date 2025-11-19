# tests/test_rag_flow.py
import sys, os
from pathlib import Path

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from backend.core.model_manager import get_embedding_model
from backend.core.qdrant_manager import client as qdrant_client
from backend.core.rag.retriever import retrieve_top_k_chunks
from backend.core.rag.citation_handler import prepare_context_and_citations, format_citations_for_display
from backend.core.rag.llm_engine import generate_llm_response
from backend.utils.logger import logger


# ===========================================================
# ⚙️ Setup Test Environment
# ===========================================================
app = FastAPI()

# Simulate FastAPI app.state resources (like in main.py lifespan)
app.state.qdrant_client = qdrant_client
app.state.embedding_model = get_embedding_model()

# Create a dummy request object (like FastAPI request)
class DummyRequest:
    app = app

request = DummyRequest()


# ===========================================================
# 🧠 Test Configuration
# ===========================================================
SESSION_ID = "427c6e4e-174b-4456-b803-062dd11e4823"
QUERY = "How did COVID-19 impact students emotionally and academically?"
TOP_K = 3


# ===========================================================
# 🚀 Step 1: Retrieve from Qdrant
# ===========================================================
logger.info(f"\n🔍 Step 1: Retrieving top {TOP_K} chunks for session {SESSION_ID}")
retrieved_chunks = retrieve_top_k_chunks(request, SESSION_ID, QUERY, top_k=TOP_K)

if not retrieved_chunks:
    print("❌ Retrieval failed or returned no results.")
    exit(1)

print(f"✅ Retrieved {len(retrieved_chunks)} chunks.")
print("-" * 80)
for r in retrieved_chunks:
    citation = r["citation"]
    print(f"📄 {citation['file_name']} (chunk {citation['chunk_index']}/{citation['total_chunks_in_file']})")
    print(f"🔹 Score: {citation['score']}")
    print(f"🧩 Text snippet: {r['text'][:200].replace('\n', ' ')}...\n")
print("=" * 80)


# ===========================================================
# 🧾 Step 2: Prepare Context + Citations
# ===========================================================
logger.info("\n🧾 Step 2: Preparing context and citations")
processed = prepare_context_and_citations(retrieved_chunks)

context_chunks = processed["context_chunks"]
citations = processed["citations"]

print(f"🧠 Extracted {len(context_chunks)} context chunks")
print(f"📚 Citations prepared: {len(citations)}")
print("-" * 80)

# Print formatted citations including clickable URLs
for c in citations:
    print(f"[{c.get('rank')}] {c.get('file_name')} (chunk {c.get('chunk_index')}/{c.get('total_chunks_in_file')})")
    print(f"🔗 Source URL: {c.get('public_url')}")
    print(f"📂 Local Path: {c.get('file_path')}")
    print("-" * 60)
print("=" * 80)


# ✅ Optional: Sanity check for public URLs
for c in citations:
    if not c.get("public_url"):
        print(f"⚠️ Missing public URL for: {c.get('file_name')}")
    else:
        assert c["public_url"].startswith("http"), f"Invalid public URL for {c['file_name']}"


# ===========================================================
# 💬 Step 3: Generate LLM Response
# ===========================================================
logger.info("\n💬 Step 3: Generating Gemini LLM response")

result = generate_llm_response(QUERY, context_chunks)

print(f"\n🧠 Model Used: {result['model']}")
print("\n💬 Response:\n")
print(result["response"])

# Display clickable citation summary
print("\n📚 Citations:\n")
print(format_citations_for_display(citations))

print("\n🎯 End-to-End RAG Flow Test Completed Successfully ✅")