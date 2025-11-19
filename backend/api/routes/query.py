
from fastapi import APIRouter, Request, HTTPException
from backend.models.schemas import QueryRequest, QueryResponse
from backend.core.rag.rag_pipeline import run_rag_pipeline
from backend.utils.logger import logger

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def handle_user_query(request: Request, query_data: QueryRequest):
    """
    Handle user query for RAG pipeline.
    Steps:
    1️⃣ Retrieve top-k chunks from Qdrant
    2️⃣ Prepare context + citations
    3️⃣ Generate LLM response via Gemini
    4️⃣ Return structured response with citations
    """
    try:
        logger.info(f"💬 New query received for session {query_data.session_id}: '{query_data.query}'")

        # ✅ Await the async RAG pipeline
        result = await run_rag_pipeline(
            request=request,
            session_id=query_data.session_id,
            query=query_data.query,
            top_k=query_data.top_k or 5
        )

        # ✅ Build structured response
        response = QueryResponse(
            query=result["query"],
            response=result["response"],
            model=result["model"],
            used_chunks=result["used_chunks"],
            citations=result["citations"],
            formatted_citations=result["formatted_citations"]
        )

        logger.info(f"✅ Query handled successfully for session {query_data.session_id}")
        return response

    except Exception as e:
        logger.exception(f"❌ Error while processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error while processing query: {str(e)}")