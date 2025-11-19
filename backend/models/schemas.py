from pydantic import BaseModel, Field
from typing import List, Optional


# =====================================================
# 🧾 Citation Schema
# =====================================================
class Citation(BaseModel):
    rank: int = Field(..., description="Rank of retrieved chunk (1 = most relevant)")
    score: float = Field(..., description="Relevance score from vector search")
    file_name: Optional[str] = Field(None, description="Original uploaded file name")
    file_path: Optional[str] = Field(None, description="Local storage path")
    public_url: Optional[str] = Field(None, description="Clickable URL to view the document")
    chunk_index: Optional[int] = Field(None, description="Chunk number within the file")
    total_chunks_in_file: Optional[int] = Field(None, description="Total chunks in that document")


# =====================================================
# 💬 Query Request Schema
# =====================================================
class QueryRequest(BaseModel):
    session_id: str = Field(..., description="Unique session ID of the user")
    query: str = Field(..., description="User query for RAG pipeline")
    top_k: Optional[int] = Field(5, description="Number of top chunks to retrieve")


# =====================================================
# 🧠 Query Response Schema
# =====================================================
class QueryResponse(BaseModel):
    query: str
    response: str
    model: str
    used_chunks: int
    citations: List[Citation]
    formatted_citations: str