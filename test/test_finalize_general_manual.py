import asyncio
from langchain_core.messages import HumanMessage, AIMessage

from backend.core.agent.graph_state import AgentState
from backend.core.agent.nodes.finalize_node import finalize_node
from backend.core.memory.session_memory import get_session_memory


async def main():
    session_id = "finalize_general_test"

    # Simulate graph state AFTER assistant_node
    state = AgentState(
        session_id=session_id,
        messages=[
            HumanMessage(content="What is machine learning?"),
            AIMessage(content="NO_TOOL_REQUIRED"),
        ],
        docs=[]
    )

    updated_state = await finalize_node(state)

    print("\nFINAL OUTPUT:")
    print(updated_state["final_output"])

    print("\nSESSION MEMORY:")
    print(get_session_memory(session_id))


if __name__ == "__main__":
    asyncio.run(main())