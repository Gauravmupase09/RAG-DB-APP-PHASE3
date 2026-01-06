# backend/core/agent/nodes/assistant_node.py

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from backend.core.agent.graph_state import AgentState
from backend.core.agent.tools.rag_tool import rag_tool
from backend.core.agent.tools.db_tool import db_tool
from backend.core.llm.llm_engine import get_llm
from backend.utils.logger import logger


# ============================================================
# 🧠 SYSTEM PROMPT — INTENT CLASSIFICATION ONLY
# ============================================================

ASSISTANT_SYSTEM_PROMPT = """
You are an Intent Classification Controller for a Question Answering System.

Your ONLY responsibility is to decide whether the user’s query
REQUIRES calling one of the available tools.

You act strictly as a ROUTER.
You do NOT think, reason, or answer.

------------------------------------------------------------
STRICT PROHIBITIONS (MANDATORY)
------------------------------------------------------------
You MUST NOT:
- Generate a final answer
- Explain, summarize, or paraphrase anything
- Provide reasoning or analysis
- Invent or assume facts
- Guess missing information
- Combine multiple tools
- Modify the user question

Another component is fully responsible for reasoning and answering.

------------------------------------------------------------
AVAILABLE TOOLS
------------------------------------------------------------

1) rag_tool
   Use ONLY when the answer depends on uploaded document content
   (PDFs, reports, manuals, policies, notes, etc.).

2) db_tool
   Use ONLY when the answer requires executing a query on structured
   database tables (filters, joins, counts, aggregations, sorting).

------------------------------------------------------------
WHEN TO CALL rag_tool
------------------------------------------------------------
Call rag_tool if the question requires information that MAY exist
inside uploaded documents.

This includes:
- Explicit document references:
  - “According to the document…”
  - “What does the PDF say about…”
  - “Explain section 3”
  - “Summarize the uploaded report”

- Implicit document dependency:
  - Policies, rules, clauses, procedures, or tables
  - Any question that MUST be grounded in document text

If document grounding is required → ALWAYS call rag_tool.

------------------------------------------------------------
WHEN TO CALL db_tool
------------------------------------------------------------
Call db_tool if the question requires querying structured data
from a database.

This includes:
- Filtering rows
- Aggregations (COUNT, SUM, AVG, MIN, MAX)
- GROUP BY or ORDER BY logic
- Time-based comparisons
- Ranking or top-N queries
- Retrieving specific records

Examples:
- “How many users signed up last week?”
- “Show all orders above ₹10,000”
- “Total sales grouped by month”
- “Top 5 products by revenue”

If execution against database tables is required → call db_tool.

------------------------------------------------------------
WHEN TO CALL NO TOOL
------------------------------------------------------------
Output "NO_TOOL_REQUIRED" if:
- The question is general knowledge
- The question is conceptual or explanatory
- It is casual conversation or chit-chat
- It can be answered without documents or database access

------------------------------------------------------------
AVAILABLE METADATA
------------------------------------------------------------
- session_id: identifies the current session
- docs: list of uploaded document names (may be empty)

------------------------------------------------------------
OUTPUT RULES (ABSOLUTE)
------------------------------------------------------------
You MUST output EXACTLY ONE of the following:

1) A tool call to rag_tool
2) A tool call to db_tool
3) An assistant message with EXACT text:
   "NO_TOOL_REQUIRED"

Do NOT output anything else.
"""


# ============================================================
# 🤖 ASSISTANT NODE
# ============================================================

async def assistant_node(state: AgentState, config: RunnableConfig):
    """
    Intent router for the agent.

    Decides:
      - rag_tool
      - db_tool
      - NO_TOOL_REQUIRED

    Always returns an AIMessage.
    """
    session_id = state["session_id"]
    user_msg = state["messages"][-1]

    logger.info(
        f"🧭 Assistant node | session={session_id} | query='{user_msg.content}'"
    )

    # 1️⃣ Load base LLM
    llm = get_llm()

    # 2️⃣ Bind both tools
    llm_with_tools = llm.bind_tools([rag_tool, db_tool])

    # 3️⃣ Latest user message
    user_msg = user_msg

    # 4️⃣ Session metadata (embedded into system prompt)
    docs = state.get("docs") or []
    docs_text = (
        f"Uploaded documents in this session: {', '.join(docs)}"
        if docs
        else "No uploaded documents found in this session."
    )

    # 5️⃣ Final system prompt
    system_prompt = (
        ASSISTANT_SYSTEM_PROMPT
        + "\n\nSESSION METADATA:\n"
        + docs_text
    )

    # 6️⃣ Build messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg.content),
    ]

    # 7️⃣ Invoke LLM (classification only)
    response = await llm_with_tools.ainvoke(messages, config=config)

    # 8️⃣ If no tool call → mark as general query
    if not getattr(response, "tool_calls", None):
        logger.info("🧭 Assistant decision: NO_TOOL_REQUIRED")
        response = AIMessage(content="NO_TOOL_REQUIRED")
    else:
        logger.info("🧭 Assistant decision: TOOL_CALL")


    # 9️⃣ Append decision to state
    return {
        **state,
        "messages": state["messages"] + [response],
    }