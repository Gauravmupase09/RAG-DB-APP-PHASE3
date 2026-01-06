# backend/core/agent/tools/rag_tool.py

from langchain_core.tools import tool
from backend.core.rag.rag_pipeline import run_rag_retrieval


@tool
async def rag_tool(session_id: str, query: str, top_k: int = 5):
    """
    DOCUMENT RETRIEVAL TOOL — Call this tool whenever the user's query
    requires information contained inside the uploaded documents.

    PURPOSE:
        - Retrieve the most relevant text chunks from the user's uploaded files.
        - Provide clean content + citation metadata for downstream answer generation.
        - This tool ONLY retrieves information; it does NOT generate answers.

    WHEN TO CALL THIS TOOL:
        - The user explicitly refers to the uploaded documents.
        - The question depends on document content:
              “According to the document…”
              “What does the PDF say about…”
              “Summarize the policy described in the file…”
              “Explain the section related to…”
        - The answer requires grounding in the document text.

    WHEN NOT TO CALL THIS TOOL:
        - General knowledge queries not related to uploaded files.
        - Conversational or social questions (“hi”, “tell me a joke”).
        - Questions answerable without referring to document text.

    NOTE:
        The tool does NOT produce the final answer. It only returns:
            - retrieved `chunks`
            - `citations` metadata
        A separate LLM call will use these chunks to produce the final answer.

    Args:
        session_id (str): The user's session identifier.
        query (str): The user's question.
        top_k (int): How many relevant chunks to retrieve.

    Returns:
        dict:
            {
                "query": "<user query>",
                "chunks": [ ... ],       # text chunks for LLM reasoning
                "citations": [ ... ]     # metadata for frontend display
            }
    """

    # Call retrieval-only part of the pipeline (NO LLM here)
    result = await run_rag_retrieval(session_id, query, top_k)

    return result