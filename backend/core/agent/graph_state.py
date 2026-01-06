# backend/core/agent/graph_state.py

from typing import List, Optional, Dict, Any
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    AgentState extends LangGraph's MessagesState to add fields required
    for our agentic RAG workflow.

    Fields:
    --------
    session_id : str
        Unique session identifier for retrieving Qdrant vectors
        and storing sliding-window conversation memory.

    docs : Optional[List[str]]
        Optional list of uploaded document names.
        (Useful for system prompts, tool hints, etc.)

    final_output : Optional[Dict[str, Any]]
        This will hold the final response object that the FastAPI
        /query endpoint returns to the frontend. It can contain either:
            - a RAG answer (after tool call + generation), or
            - a general LLM answer (no tool used).
    """

    session_id: str
    docs: Optional[List[str]] = None
    final_output: Optional[Dict[str, Any]] = None