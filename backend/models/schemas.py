# backend/models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# =====================================================
# 🧾 Unified Citation Schema
# =====================================================
class Citation(BaseModel):
    """
    Unified citation model supporting multiple answer sources.

    type:
      - "rag"      → document-based citation
      - "database" → database / SQL-based citation
    """

    type: Literal["rag", "database"]

    # -------------------------
    # 📄 RAG-specific fields
    # -------------------------
    rank: Optional[int] = Field(
        None, description="Rank of retrieved chunk (1 = most relevant)"
    )
    score: Optional[float] = Field(
        None, description="Relevance score from vector search"
    )
    file_name: Optional[str] = Field(
        None, description="Original uploaded file name"
    )
    file_path: Optional[str] = Field(
        None, description="Local storage path"
    )
    public_url: Optional[str] = Field(
        None, description="Public URL to view the document"
    )
    chunk_index: Optional[int] = Field(
        None, description="Chunk index within the file"
    )
    total_chunks_in_file: Optional[int] = Field(
        None, description="Total chunks in that document"
    )

    # -------------------------
    # 🗄️ Database-specific fields
    # -------------------------
    db_type: Optional[str] = Field(
        None, description="Database engine type (postgresql, mysql, sqlite, etc.)"
    )
    tables: Optional[List[str]] = Field(
        None, description="Database tables involved in the query"
    )
    sql: Optional[str] = Field(
        None, description="Generated SQL query used to answer the question"
    )


# =====================================================
# 💬 Query Request Schema
# =====================================================
class QueryRequest(BaseModel):
    session_id: str = Field(
        ..., description="Unique session ID of the user"
    )
    query: str = Field(
        ..., description="User query (general, RAG, or DB)"
    )


# =====================================================
# 🧠 Query Response Schema
# =====================================================
class QueryResponse(BaseModel):
    """
    Unified response schema for all query types:
      - General LLM answers
      - RAG-based answers
      - Database-based answers
    """

    query: str
    response: str
    model: str

    # For RAG → number of chunks used
    # For DB / General → always 0
    used_chunks: int = Field(
        0, description="Number of retrieved chunks used in the answer"
    )

    citations: List[Citation] = Field(
        default_factory=list,
        description="Structured provenance of the answer"
    )

    formatted_citations: str = Field(
        "No citations available.",
        description="Human-readable citation summary for display"
    )