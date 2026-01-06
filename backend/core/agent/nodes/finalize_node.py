# backend/core/agent/nodes/finalize_node.py

import json
from typing import Any, Dict

from langchain_core.messages import AIMessage, ToolMessage

from backend.core.agent.graph_state import AgentState
from backend.utils.logger import logger

# LLM generation paths
from backend.core.llm.llm_engine import generate_general_answer
from backend.core.rag.rag_pipeline import run_rag_generation
from backend.core.db.db_executor import run_db_generation

# Session memory utilities
from backend.core.memory.session_memory import add_to_session_memory, get_session_memory


async def finalize_node(state: AgentState) -> AgentState:
    """
    FINAL NODE of the agent graph.

    This node is responsible for producing the FINAL ANSWER that will be
    returned to the frontend.

    It executes AFTER:
        - assistant_node (intent classification)
        - tool_node (optional tool execution)

    ------------------------------------------------------------
    SUPPORTED EXECUTION PATHS
    ------------------------------------------------------------

    1️⃣ NO_TOOL_REQUIRED
       - assistant_node decided no tool is needed
       - A general LLM answer is generated

    2️⃣ rag_tool
       - assistant_node chose rag_tool
       - tool_node executed document retrieval
       - This node runs RAG answer generation

    3️⃣ db_tool
       - assistant_node chose db_tool
       - tool_node executed database query
       - This node runs DB result explanation

    ------------------------------------------------------------
    IMPORTANT:
    ------------------------------------------------------------
    - This node DOES NOT decide intent
    - This node DOES NOT retrieve documents
    - This node DOES NOT execute SQL
    - This node ONLY orchestrates final answer generation
    """


    # Last message in the graph state determines the execution path
    last_msg = state["messages"][-1]
    session_id = state["session_id"]

    logger.info(f"🏁 Finalize node triggered | session={session_id}")

    # ============================================================
    # 1️⃣ CASE: NO TOOL → GENERAL ANSWER
    #    last_msg is AIMessage("NO_TOOL_REQUIRED")
    # ============================================================
    #
    # Pattern:
    #   HumanMessage(user query)
    #   AIMessage("NO_TOOL_REQUIRED")
    #
    # In this case we:
    #   - Save user query to memory
    #   - Load past conversation memory
    #   - Call general LLM
    #   - Save assistant reply
    #
    if isinstance(last_msg, AIMessage) and last_msg.content == "NO_TOOL_REQUIRED":
        # The previous message should be the user's query (HumanMessage)
        user_msg = state["messages"][-2]
        user_query = user_msg.content

        # (A) Save user message into session memory
        add_to_session_memory(session_id, "user", user_query)

        # (B) Build memory text for context, EXCLUDING current user query
        memory = get_session_memory(session_id)
        if memory and memory[-1]["role"] == "user":
            memory_for_context = memory[:-1]
        else:
            memory_for_context = memory
        

        memory_text = (
            "\n".join([f"{m['role']}: {m['content']}" for m in memory_for_context])
            if memory_for_context else None
        )

        # (C) Generate general answer using LLM
        llm_result = generate_general_answer(
            query=user_query,
            memory_text=memory_text,
        )

        # (D) Save assistant response to memory
        add_to_session_memory(session_id, "assistant", llm_result["response"])

        # (E) Build final_output (no citations for general answers)
        final_output: Dict[str, Any] = {
            "mode": "general",
            "query": user_query,
            "response": llm_result["response"],
            "model": llm_result["model"],
            "used_chunks": 0,
            "citations": [],
            "formatted_citations": "No citations available.",
        }

        # Optionally also append the final assistant reply to messages
        state["messages"].append(AIMessage(content=llm_result["response"]))

        return {**state, "final_output": final_output}

    # ============================================================
    # 2️⃣ CASE: TOOL WAS USED → RAG or DB
    # ============================================================
    #
    # Pattern:
    #   HumanMessage(user query)
    #   AIMessage(tool_call)
    #   ToolMessage(tool result)
    #
    # The specific tool is identified by:
    #   last_msg.name  → "rag_tool" or "db_tool"
    #
    if isinstance(last_msg, ToolMessage):

        tool_name = last_msg.name
        tool_payload = last_msg.content

        logger.info(f"🧰 Tool response received | tool={tool_name}")

        print(tool_payload)
        type(tool_payload)

        
        # 🔒 LangGraph boundary normalization
        if isinstance(tool_payload, str):
            try:
                tool_payload = json.loads(tool_payload)
            except Exception as e:
                raise ValueError(
                    f"❌ Tool payload is string but not valid JSON: {tool_payload}"
                )

        if not isinstance(tool_payload, dict):
            raise ValueError(
                f"❌ Tool contract violated: expected dict, got {type(tool_payload)}"
            )

        # ========================================================
        # 2️⃣ A) RAG TOOL PATH
        # ========================================================
        #
        # tool_payload structure:
        # {
        #   "query": "<user query>",
        #   "chunks": [...],
        #   "citations": [...]
        # }
        #
        if tool_name == "rag_tool":

            query = tool_payload.get("query")
            chunks = tool_payload.get("chunks", [])
            citations = tool_payload.get("citations", [])

            # Fallback: recover query from graph messages if missing
            if not query:
                query = state["messages"][-3].content

            # Run second-stage RAG generation
            rag_output = await run_rag_generation(
                session_id=session_id,
                query=query,
                chunks=chunks,
                citations=citations,
            )

            rag_output["mode"] = "rag"

            # Append final RAG answer to messages
            state["messages"].append(AIMessage(content=rag_output["response"]))

            return {**state, "final_output": rag_output}

        # ========================================================
        # 2️⃣ B) DB TOOL PATH
        # ========================================================
        #
        # tool_payload structure:
        # {
        #   "query": "<user query>",
        #   "sql": "...",
        #   "rows": [...],
        #   "db_type": "...",
        #   ...
        # }
        #
        if tool_name == "db_tool":

            # Run DB explanation generation
            db_output = await run_db_generation(
                session_id=session_id,
                tool_payload=tool_payload,
            )

            db_output["mode"] = "db"

            # Append final DB answer to messages
            state["messages"].append(AIMessage(content=db_output["response"]))

            return {**state, "final_output": db_output}

        # ========================================================
        # Unknown tool safeguard
        # ========================================================
        raise ValueError(f"❌ finalize_node: Unknown tool '{tool_name}'")

    # ============================================================
    # SAFETY NET — Should never happen
    # ============================================================
    raise ValueError(
        f"❌ finalize_node: Unexpected last message type: {type(last_msg)}"
    )