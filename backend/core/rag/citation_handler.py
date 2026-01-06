# backend/core/rag/citation_handler.py

from typing import List, Dict
from urllib.parse import quote
from backend.utils.logger import logger

# Base public path for serving static files
BASE_UPLOAD_URL = "http://localhost:8000/uploads"


def prepare_context_and_citations(retrieved_chunks: List[Dict]) -> Dict:
    """
    Process retrieved chunks to:
    1️⃣ Build a clean text context for LLM
    2️⃣ Extract structured citation metadata (with clickable URLs)
    """

    if not retrieved_chunks:
        logger.warning("⚠️ No retrieved chunks provided for citation handling.")
        return {"context_chunks": [], "citations": []}

    context_chunks = []
    citations = []

    for item in retrieved_chunks:
        text = item.get("text", "").strip()
        citation = item.get("citation", {})

        if not text:
            continue

        # 🧩 Append context for LLM input
        context_chunks.append(text)

        # 🧾 Build public URL (with URL-encoded filename)
        session_id = citation.get("session_id")
        file_name = citation.get("file_name")

        encoded_file_name = quote(file_name) if file_name else None
        public_url = (
            f"{BASE_UPLOAD_URL}/{session_id}/{encoded_file_name}"
            if session_id and encoded_file_name
            else None
        )

        # 🧾 Prepare clean citation info
        citation_entry = {
            "type": "rag",
            "rank": citation.get("rank"),
            "score": citation.get("score"),
            "file_name": citation.get("file_name"),
            "file_path": citation.get("file_path"),
            "public_url": public_url,
            "chunk_index": citation.get("chunk_index"),
            "total_chunks_in_file": citation.get("total_chunks_in_file"),
        }
        
        citations.append(citation_entry)

    logger.info(f"🧾 Prepared {len(citations)} citations and {len(context_chunks)} context chunks.")
    return {
        "context_chunks": context_chunks,
        "citations": citations
    }


def format_citations_for_display(citations: List[Dict]) -> str:
    """
    Format citation list for front-end or display in response.
    Example:
        [1] impact_of_covid.pdf (chunk 3/76)
        Link: http://localhost:8000/uploads/<session_id>/<file_name>
    """

    if not citations:
        return "No citations available."

    formatted = []
    for c in citations:
        file_display = c.get("file_name", "unknown.pdf")
        chunk_info = f"(chunk {c.get('chunk_index')}/{c.get('total_chunks_in_file')})"
        link = c.get("public_url", "N/A")
        formatted.append(f"[{c.get('rank')}] {file_display} {chunk_info}\n🔗 {link}")

    return "\n".join(formatted)