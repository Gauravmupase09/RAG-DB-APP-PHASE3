# # tests/test_retriever.py

# import sys, os, json
# from pathlib import Path

# # Add project root
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.model_manager import get_embedding_model
# from backend.core.qdrant_manager import client as qdrant_client
# from backend.core.qdrant_manager import get_collection_name
# from backend.utils.logger import logger

# # Change to your new session ID
# SESSION_ID = "427c6e4e-174b-4456-b803-062dd11e4823"
# QUERY = "How did covid impact students emotionally and academically?"
# TOP_K = 3

# print(f"🔍 Running retrieval test for session: {SESSION_ID}")
# print(f"Query: {QUERY}\n")

# # ✅ Load model + client
# model = get_embedding_model()
# collection_name = get_collection_name(SESSION_ID)

# # ✅ Encode query
# query_vector = model.encode(QUERY).tolist()

# # ✅ Perform Qdrant semantic search
# try:
#     search_results = qdrant_client.query_points(
#         collection_name=collection_name,
#         query=query_vector,
#         limit=TOP_K,
#         with_payload=True,
#         with_vectors=False
#     )
# except Exception as e:
#     print(f"❌ Retrieval failed: {e}")
#     sys.exit(1)

# # ✅ Display results
# print(f"✅ Retrieved {len(search_results)} chunks:\n")
# for i, hit in enumerate(search_results, start=1):
#     payload = hit.payload
#     print(f"Rank: {i} | Score: {hit.score:.4f}")
#     print(f"Source: {payload.get('original_file_name')}")
#     print(f"Chunk ID: {payload.get('chunk_id')}")
#     print("Text snippet:", payload.get("text", "")[:250].replace("\n", " "), "...")
#     print("-" * 70)

# print("\n🎯 Retrieval test completed successfully.")

# tests/test_retriever.py

import sys, os
from pathlib import Path

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.model_manager import get_embedding_model
from backend.core.qdrant_manager import client as qdrant_client
from backend.core.qdrant_manager import get_collection_name
from backend.utils.logger import logger

# 🔧 Config
SESSION_ID = "427c6e4e-174b-4456-b803-062dd11e4823"
QUERY = "How did covid impact students emotionally and academically?"
TOP_K = 3

print(f"🔍 Running retrieval test for session: {SESSION_ID}")
print(f"Query: {QUERY}\n")

# ✅ Load model + client
model = get_embedding_model()
collection_name = get_collection_name(SESSION_ID)

# ✅ Encode query
query_vector = model.encode(QUERY).tolist()

# ✅ Perform Qdrant semantic search
try:
    response = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_vector,           # ✅ correct param name
        limit=TOP_K,
        with_payload=True,
        with_vectors=False
    )
except Exception as e:
    print(f"❌ Retrieval failed: {e}")
    sys.exit(1)

# ✅ Extract points from QueryResponse
search_results = response.points or []

print(f"✅ Retrieved {len(search_results)} chunks:\n")

# ✅ Display results
for i, hit in enumerate(search_results, start=1):
    payload = hit.payload or {}
    print(f"Rank: {i} | Score: {hit.score:.4f}")
    print(f"Source: {payload.get('original_file_name')}")
    print(f"Chunk ID: {payload.get('chunk_id')}")
    print(f"Source Path: {payload.get('original_file_path')}")
    print("Text snippet:", payload.get("text", "")[:250].replace("\n", " "), "...")
    print("-" * 70)

print("\n🎯 Retrieval test completed successfully.")