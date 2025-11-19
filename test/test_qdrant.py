import os, json
from pathlib import Path
import sys

# Add backend path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.qdrant_manager import upsert_embedding, create_collection_if_not_exists, get_collection_name
from backend.utils.config import PROCESSED_DIR
from backend.utils.logger import logger

session_id = "session id"

print(f"\n🔥 Testing Qdrant upsert for REAL embeddings: {session_id}\n")

session_dir = PROCESSED_DIR / session_id

# find any doc folder
doc_folders = [d for d in session_dir.iterdir() if d.is_dir()]

if not doc_folders:
    raise Exception("❌ No document folders found! Run extract/clean/chunk/embed pipeline first.")

embeddings = []

# Load first few embedding files
for doc in doc_folders:
    embed_dir = doc / "embeddings"
    if embed_dir.exists():
        for f in sorted(embed_dir.glob("chunk_*.json")):
            record = json.loads(f.read_text())
            embeddings.append(record)
        break

if not embeddings:
    raise Exception("❌ No embeddings found! Run embed pipeline first.")

print(f"✅ Found {len(embeddings)} embeddings. Testing upsert for first 3...")

# Ensure collection exists
create_collection_if_not_exists(session_id)

for i, rec in enumerate(embeddings[:3]):   # only 3 for test
    upsert_embedding(rec)
    print(f"📌 Upserted: {rec['chunk_id']}")

print("\n🎯 REAL Qdrant test completed successfully!")
print(f"📦 Collection: {get_collection_name(session_id)}")