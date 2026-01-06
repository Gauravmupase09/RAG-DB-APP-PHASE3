import os
import json
import asyncio
from dotenv import load_dotenv

from backend.core.db.db_manager import connect_db, disconnect_db
from backend.core.agent.tools.db_tool import db_tool
from backend.core.memory.session_memory import get_session_memory

# ------------------------------------------------------------
# 🔑 Load environment variables
# ------------------------------------------------------------
load_dotenv()

SESSION_ID = "db_tool_test_session"
DB_URL = os.getenv("SUPABASE_DB_URL")

if not DB_URL:
    raise RuntimeError("❌ SUPABASE_DB_URL not found in .env")


# ------------------------------------------------------------
# 🧪 MAIN TEST
# ------------------------------------------------------------
async def main():
    print("\n🔗 Connecting to database...")
    connect_db(SESSION_ID, DB_URL)

    try:
        # ----------------------------------------------------
        # 1️⃣ User question (DB-type query)
        # ----------------------------------------------------
        query = "Show all users from India and their total order amount"

        print("\n💬 USER QUESTION:")
        print(query)

        # ----------------------------------------------------
        # 2️⃣ Call DB TOOL (NO LLM)
        # ----------------------------------------------------
        print("\n🧠 Running db_tool...")
        tool_result = await db_tool.ainvoke(
           {
        "session_id": SESSION_ID,
        "query": query,
           }
        )

        # ----------------------------------------------------
        # 3️⃣ Print tool output
        # ----------------------------------------------------
        print("\n📤 DB TOOL OUTPUT (RAW, NO LLM):")
        print(json.dumps(tool_result, indent=2, default=str))

        # ----------------------------------------------------
        # 4️⃣ Basic validations
        # ----------------------------------------------------
        print("\n✅ BASIC VALIDATIONS:")

        assert "sql" in tool_result, "❌ SQL missing"
        assert "rows" in tool_result, "❌ Rows missing"
        assert isinstance(tool_result["rows"], list), "❌ Rows must be list"
        assert "confidence" in tool_result, "❌ Confidence missing"

        print("✔ SQL generated")
        print(f"✔ Rows returned: {tool_result['row_count']}")
        print(f"✔ Confidence: {tool_result['confidence']}")

        # ----------------------------------------------------
        # 5️⃣ Memory check
        # ----------------------------------------------------
        memory = get_session_memory(SESSION_ID)

        print("\n🧠 SESSION MEMORY:")
        print(json.dumps(memory, indent=2))

        assert memory[-1]["role"] == "user", "❌ Last memory entry should be user"
        assert memory[-1]["content"] == query, "❌ User query not stored"

        print("✔ User query stored in memory")

        print("\n🎉 db_tool test PASSED")

    finally:
        # ----------------------------------------------------
        # 6️⃣ Disconnect DB
        # ----------------------------------------------------
        disconnect_db(SESSION_ID)
        print("\n🔌 Database disconnected")


# ------------------------------------------------------------
# ▶ Run test
# ------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())