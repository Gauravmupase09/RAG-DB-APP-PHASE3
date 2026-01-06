# backend/core/agent/nodes/tool_node.py

from langgraph.prebuilt import ToolNode
from backend.core.agent.tools.rag_tool import rag_tool
from backend.core.agent.tools.db_tool import db_tool


# Expose a ready-to-use ToolNode for the graph builder.
tool_node = ToolNode([rag_tool, db_tool])