# backend/api/routes/query.py

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

from backend.models.schemas import QueryRequest, QueryResponse
from backend.core.agent.graph_builder import agentic_rag_graph
from backend.utils.file_manager import list_files
from backend.utils.logger import logger

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def handle_user_query(query_data: QueryRequest):
    """
    Unified Agentic Query Endpoint

    Supports:
      - General LLM answers
      - Document-based RAG
      - Database-based answers

    Execution Flow:
      1) Discover session context (uploaded docs)
      2) Build initial AgentState
      3) Run agentic LangGraph (assistant → tool → finalize)
      4) Return normalized QueryResponse
    """

    try:
        # --------------------------------------------------
        # 1️⃣ Validate input
        # --------------------------------------------------
        session_id = query_data.session_id
        query_text = query_data.query.strip()

        if not query_text:
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        logger.info(
            f"💬 /query received | session={session_id} | query='{query_text}'"
        )

        # --------------------------------------------------
        # 2️⃣ Discover uploaded documents (RAG context)
        # --------------------------------------------------
        try:
            docs = list_files(session_id)
        except Exception:
            docs = []

        logger.info(
            f"📄 Session context | session={session_id} | docs={docs}"
        )

        # --------------------------------------------------
        # 3️⃣ Build initial AgentState
        # --------------------------------------------------
        initial_state = {
            "session_id": session_id,
            "docs": docs,  # may be empty → OK
            "messages": [HumanMessage(content=query_text)],
        }

        # --------------------------------------------------
        # 4️⃣ Execute agentic graph
        # --------------------------------------------------
        final_state = await agentic_rag_graph.ainvoke(initial_state)

        # --------------------------------------------------
        # 5️⃣ Extract final_output (single source of truth)
        # --------------------------------------------------
        final_output = final_state.get("final_output")
        if not final_output:
            logger.error("❌ finalize_node did not produce final_output")
            raise RuntimeError("finalize_node did not produce final_output")

        logger.info(
            f"✅ Query resolved | session={session_id} | "
            f"mode={final_output.get('mode', 'unknown')}"
        )

        # --------------------------------------------------
        # 6️⃣ Normalize into QueryResponse
        # --------------------------------------------------
        return QueryResponse(
            query=final_output.get("query"),
            response=final_output.get("response"),
            model=final_output.get("model"),
            used_chunks=final_output.get("used_chunks", 0),
            citations=final_output.get("citations", []),
            formatted_citations=final_output.get(
                "formatted_citations",
                "No citations available.",
            ),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("❌ Error processing /query request")
        raise HTTPException(status_code=500, detail=str(e))