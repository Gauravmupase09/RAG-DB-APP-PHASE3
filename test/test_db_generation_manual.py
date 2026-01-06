# test/test_db_generation_manual.py

import os
import json
import asyncio
from dotenv import load_dotenv

from backend.core.db.db_manager import connect_db, disconnect_db
from backend.core.db.db_executor import run_db_execution, run_db_generation
from backend.core.memory.session_memory import get_session_memory

load_dotenv()

SESSION_ID = "db_generation_test_session"
DB_URL = os.getenv("SUPABASE_DB_URL")

async def main():
    print("\n🔗 Connecting to database...")
    connect_db(SESSION_ID, DB_URL)

    query = "Show all users from India and their total order amount"

    print("\n🧠 STEP 1: DB EXECUTION (NO LLM)")
    tool_result = await run_db_execution(
        session_id=SESSION_ID,
        query=query,
    )

    print("\n📤 TOOL RESULT:")
    print(json.dumps(tool_result, indent=2, default=str))

    print("\n🧠 STEP 2: DB GENERATION (LLM)")
    final_result = await run_db_generation(
        session_id=SESSION_ID,
        tool_payload=tool_result,
    )

    print("\n📤 FINAL OUTPUT:")
    print(json.dumps(final_result, indent=2, default=str))

    print("\n🧠 SESSION MEMORY:")
    print(json.dumps(get_session_memory(SESSION_ID), indent=2, default=str))

    disconnect_db(SESSION_ID)
    print("\n✅ DB generation test completed")

if __name__ == "__main__":
    asyncio.run(main())