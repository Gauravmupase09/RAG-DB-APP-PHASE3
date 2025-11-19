from fastapi import Request
from typing import Dict, Any
from backend.utils.logger import logger

# Import core RAG components
from backend.core.rag.retriever import retrieve_top_k_chunks
from backend.core.rag.citation_handler import prepare_context_and_citations, format_citations_for_display
from backend.core.rag.llm_engine import generate_llm_response

# Memory
from backend.core.rag.session_memory import add_to_session_memory, get_session_memory


async def run_rag_pipeline(request: Request, session_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
    
    logger.info(f"🚀 RAG Pipeline Start | Session={session_id} | Query='{query}'")

    # ----------------------------------------------------------------------
    # 1️⃣ Save user message to sliding-window memory
    # ----------------------------------------------------------------------
    logger.debug("🧠 Adding user message to session memory...")
    add_to_session_memory(session_id, "user", query)

    # ----------------------------------------------------------------------
    # 2️⃣ Load memory FIRST (high priority for LLM)
    # ----------------------------------------------------------------------
    memory = get_session_memory(session_id)
    memory_text = (
        "\n".join([f"{m['role']}: {m['content']}" for m in memory])
        if memory else None
    )

    master_context = []
    if memory_text:
        logger.debug("🔗 Injecting conversation memory into context...")
        master_context.append("Conversation History:\n" + memory_text)
    else:
        logger.debug("ℹ️ No previous conversation memory.")

    # ----------------------------------------------------------------------
    # 3️⃣ Always retrieve document chunks for the query
    # ----------------------------------------------------------------------
    logger.info("🔍 Retrieving relevant chunks from Qdrant...")
    retrieved_chunks = retrieve_top_k_chunks(request, session_id, query, top_k)

    processed = prepare_context_and_citations(retrieved_chunks)
    rag_context_chunks = processed["context_chunks"]
    citations = processed["citations"]

    logger.info(f"📄 Retrieved {len(rag_context_chunks)} chunks.")

    # Append chunks AFTER memory
    master_context.extend(rag_context_chunks)

    # ----------------------------------------------------------------------
    # 4️⃣ Generate LLM response with BOTH memory + doc chunks
    # ----------------------------------------------------------------------
    logger.info("🤖 Generating final LLM response...")
    llm_result = generate_llm_response(query, master_context)

    # ----------------------------------------------------------------------
    # 5️⃣ Save assistant output to memory
    # ----------------------------------------------------------------------
    logger.debug("🧠 Adding assistant message to session memory...")
    add_to_session_memory(session_id, "assistant", llm_result["response"])

    # Format citations for frontend
    formatted_citations = format_citations_for_display(citations)

    logger.info("✅ RAG Pipeline Completed Successfully.")

    # ----------------------------------------------------------------------
    # Return final response object
    # ----------------------------------------------------------------------
    return {
        "query": query,
        "response": llm_result["response"],
        "model": llm_result["model"],
        "used_chunks": len(rag_context_chunks),
        "citations": citations,
        "formatted_citations": formatted_citations
    }