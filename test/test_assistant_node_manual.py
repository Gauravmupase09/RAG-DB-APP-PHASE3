import asyncio
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from backend.core.agent.nodes.assistant_node import assistant_node
from backend.core.agent.graph_state import AgentState


async def run_test(query: str, docs=None):
    print("\n" + "=" * 80)
    print(f"USER QUERY: {query}")

    state: AgentState = {
        "session_id": "assistant_node_test_session",
        "messages": [HumanMessage(content=query)],
        "docs": docs or [],
    }

    result = await assistant_node(
        state=state,
        config=RunnableConfig(),
    )

    last_msg = result["messages"][-1]

    print("\nASSISTANT OUTPUT:")
    print(last_msg)

    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        print("\n✅ TOOL CALLED:")
        for call in last_msg.tool_calls:
            print(f"- Tool name: {call['name']}")
            print(f"- Arguments: {call['args']}")
    else:
        print("\n✅ NO TOOL REQUIRED")


async def main():
    # ----------------------------
    # 1️⃣ DB query → db_tool
    # ----------------------------
    await run_test(
        "Show total sales grouped by month"
    )

    # ----------------------------
    # 2️⃣ Document query → rag_tool
    # ----------------------------
    await run_test(
        "According to the uploaded policy, what is the refund rule?",
        docs=["refund_policy.pdf"]
    )

    # ----------------------------
    # 3️⃣ General question → NO TOOL
    # ----------------------------
    await run_test(
        "What is machine learning?"
    )


if __name__ == "__main__":
    asyncio.run(main())