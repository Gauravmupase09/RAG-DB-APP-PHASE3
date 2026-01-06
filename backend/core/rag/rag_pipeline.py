# backend/core/rag/rag_pipeline.py

from typing import Dict, Any, List
from backend.utils.logger import logger

# Import core RAG components
from backend.core.rag.retriever import retrieve_top_k_chunks
from backend.core.rag.citation_handler import prepare_context_and_citations, format_citations_for_display
from backend.core.llm.llm_engine import generate_rag_answer

# Memory
from backend.core.memory.session_memory import add_to_session_memory, get_session_memory


# =======================================================================
# 1️⃣ RETRIEVAL-ONLY FUNCTION (⚡ Used by rag_tool inside LangGraph)
# =======================================================================
async def run_rag_retrieval(session_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Retrieve semantically relevant document chunks for a given query.
    This function is used ONLY by the rag_tool, and it MUST NOT generate
    an LLM answer. Tools return *data*, not reasoning.

    Workflow:
        - Save the user query in conversation memory
        - Retrieve top-K relevant chunks from Qdrant
        - Prepare clean chunks + structured citations
        - Return ONLY data (NO LLM generation)
    """

    logger.info(f"🔍 RAG Retrieval Start | Session={session_id} | Query='{query}'")

    # Add user message to sliding window memory
    add_to_session_memory(session_id, "user", query)

    # Step 1: Retrieve chunks from Qdrant
    retrieved = retrieve_top_k_chunks(session_id, query, top_k)

    # Step 2: Process raw results into:
    #   - context_chunks → for LLM
    #   - citations → metadata for frontend
    processed = prepare_context_and_citations(retrieved)

    chunks = processed["context_chunks"]
    citations = processed["citations"]

    logger.info(f"📄 Retrieved {len(chunks)} relevant context chunks.")

    # Tool-safe response (NO LLM answer here)
    return {
        "query": query,
        "chunks": chunks,         # clean context for LLM
        "citations": citations    # raw structured citations
    }


# =======================================================================
# 2️⃣ LLM GENERATION FUNCTION (⚡ Used after rag_tool is called)
# =======================================================================
async def run_rag_generation(session_id: str, query: str, chunks: List[str], citations: List[Dict]) -> Dict[str, Any]:
    """
    Generate the final answer for a RAG query *after* retrieval is done.
    This is used by assistant_node only when the LLM decides to call rag_tool.

    Workflow:
        - Load conversation memory
        - Combine memory + retrieved chunks
        - Generate final LLM answer
        - Save LLM answer to memory
        - Format citations for frontend display
    """

    logger.info(f"🤖 RAG Generation Start | Session={session_id}")

    # Load memory for context
    memory = get_session_memory(session_id)

    
    if memory and memory[-1]["role"] == "user":
        memory_for_context = memory[:-1]
    else:
        memory_for_context = memory

    memory_text = (
        "\n".join([f"{m['role']}: {m['content']}" for m in memory_for_context])
        if memory_for_context else None
    )

    # Build full LLM context
    master_context = []

    # Add conversation history first (if available)
    if memory_text:
        master_context.append("Conversation History:\n" + memory_text)

    # Add retrieved document chunks
    master_context.extend(chunks)

    # Produce the final contextual LLM answer
    llm_result = generate_rag_answer(query, master_context)

    # Save the assistant's reply to session memory
    add_to_session_memory(session_id, "assistant", llm_result["response"])

    # Create structured + readable citations for frontend
    formatted_citations = format_citations_for_display(citations)

    return {
        "query": query,
        "response": llm_result["response"],
        "model": llm_result["model"],
        "used_chunks": len(chunks),
        "citations": citations,
        "formatted_citations": formatted_citations
    }