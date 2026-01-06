import os
import json
import asyncio
from dotenv import load_dotenv

from backend.core.db.db_manager import connect_db, disconnect_db
from backend.core.db.db_executor import run_db_execution
from backend.core.memory.session_memory import get_session_memory

# ------------------------------------------------------------
# 🔑 Load environment variables
# ------------------------------------------------------------
load_dotenv()

SESSION_ID = "db_execution_test_session"
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
        # 1️⃣ User question
        # ----------------------------------------------------
        question = "Show all users from India and their total order amount"

        print("\n💬 USER QUESTION:")
        print(question)

        # ----------------------------------------------------
        # 2️⃣ Run DB TOOL (NO LLM)
        # ----------------------------------------------------
        print("\n🧠 Running DB Execution Tool...")
        result = await run_db_execution(
            session_id=SESSION_ID,
            query=question,
        )

        # ----------------------------------------------------
        # 3️⃣ Output result
        # ----------------------------------------------------
        print("\n📤 TOOL OUTPUT (NO LLM):")
        print(json.dumps(result, indent=2, default=str))

        # ----------------------------------------------------
        # 4️⃣ Validate expectations
        # ----------------------------------------------------
        print("\n✅ BASIC VALIDATIONS:")

        assert "sql" in result, "❌ SQL missing in result"
        assert "rows" in result, "❌ Rows missing in result"
        assert isinstance(result["rows"], list), "❌ Rows must be a list"
        assert "confidence" in result, "❌ Confidence missing"

        print("✔ SQL generated")
        print(f"✔ Rows returned: {len(result['rows'])}")
        print(f"✔ Confidence: {result['confidence']}")

        # ----------------------------------------------------
        # 5️⃣ Memory check
        # ----------------------------------------------------
        memory = get_session_memory(SESSION_ID)

        print("\n🧠 SESSION MEMORY:")
        print(json.dumps(memory, indent=2))

        assert memory[-1]["role"] == "user", "❌ Last memory entry should be user"
        assert memory[-1]["content"] == question, "❌ User query not stored in memory"

        print("✔ User query saved in memory")

        print("\n🎉 DB Execution Tool test PASSED")

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