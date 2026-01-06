# backend/core/agent/graph_builder.py

"""
This file builds the complete Agentic RAG workflow graph.

Pipeline:
    START
      ↓
    assistant_node          (decides: general OR tool_call)
      ├── tool_call ─────→ tool_node  (executes rag_tool)
      │                        ↓
      └── NO_TOOL_REQUIRED → finalize_node (general answer)
                               ↓
                              END

The graph always ends in finalize_node, which returns
state["final_output"] — consumed by FastAPI /query route.
"""

from langgraph.graph import StateGraph, END

# --- State model ---
from backend.core.agent.graph_state import AgentState

# --- Nodes ---
from backend.core.agent.nodes.assistant_node import assistant_node
from backend.core.agent.nodes.tool_node import tool_node
from backend.core.agent.nodes.finalize_node import finalize_node


# =====================================================================
# 🔨 GRAPH BUILDER FUNCTION
# =====================================================================

def build_agentic_rag_graph():
    """
    Creates and compiles the Agentic RAG LangGraph workflow.

    Returns:
        graph (CompiledGraph): the fully compiled graph instance
                               with support for both async + sync.
    """

    # 1️⃣ Initialize graph with your AgentState as the data model
    workflow = StateGraph(AgentState)

    # 2️⃣ Register all nodes
    workflow.add_node("assistant", assistant_node)
    workflow.add_node("tool", tool_node)               # prebuilt ToolNode executes rag_tool
    workflow.add_node("finalize", finalize_node)

    # 3️⃣ Set the entry point
    workflow.set_entry_point("assistant")

    # =====================================================================
    # 4️⃣ Conditional routing FROM assistant_node
    #
    #     assistant → tool_node      (if a tool call exists)
    #     assistant → finalize_node  (if NO_TOOL_REQUIRED)
    #
    # NOTE:
    #     Your LangGraph version does NOT support keyword "condition=".
    #     It requires positional args: (source, condition_fn, path_map)
    # =====================================================================

    def route_decision(state):
        """
        Determine next node based on the last assistant output.
        """
        last_msg = state["messages"][-1]
        has_tool_call = hasattr(last_msg, "tool_calls") and last_msg.tool_calls
        return "tool" if has_tool_call else "finalize"

    workflow.add_conditional_edges(
        "assistant",       # source node
        route_decision,    # condition function
        {
            "tool": "tool",
            "finalize": "finalize"
        }
    )

    # After tool_node, ALWAYS go to finalize_node
    workflow.add_edge("tool", "finalize")

    # finalize_node → END
    workflow.add_edge("finalize", END)

    # 5️⃣ Compile the graph
    graph = workflow.compile()

    return graph


# =====================================================================
# Optional Singleton Instance (import anywhere in backend)
# =====================================================================

# Creating a ready-to-use global graph instance.
# If you prefer, you can remove this and construct the graph in main.py.
agentic_rag_graph = build_agentic_rag_graph()