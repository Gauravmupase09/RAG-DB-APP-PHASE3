import os
import sys

# ✅ Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from backend.utils.config import QDRANT_HOST, QDRANT_PORT

session_id = "28735376-65a1-4808-82a6-556e58df9f06"
collection = f"session_{session_id}"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

resp = client.scroll(
    collection_name=collection,
    with_vectors=True,
    limit=1
)

print("\n✅ Qdrant Data Check ✅")
print(resp)