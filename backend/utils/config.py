# backend/utils/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ==============================
# 📂 Paths
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"

# Create folders if not exist
for folder in [DATA_DIR, UPLOAD_DIR, PROCESSED_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# ==============================
# 🔑 Environment Variables
# ==============================
QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))

# Embedding Model
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# LLM Keys
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ==============================
# ⚙️ Chunking Config
# ==============================
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 100))

# ==============================
# ✅ App Config
# ==============================
APP_NAME = "RAG Chat App"
APP_VERSION = "1.0"
DEBUG = True