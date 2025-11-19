import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qdrant_client import QdrantClient
from backend.utils.config import QDRANT_HOST, QDRANT_PORT

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
session_id = "session ID"  # 👈 Replace with your session ID

collection_name = f"session_{session_id}"

try:
    client.delete_collection(collection_name)
    print(f"🗑️ Deleted collection: {collection_name}")
except Exception as e:
    print(f"⚠️ Error deleting collection: {e}")