# test/test_db_query_generator_manual.py

import os
import json
from dotenv import load_dotenv

from backend.core.db.db_manager import connect_db, disconnect_db
from backend.core.db.schema_inspector import inspect_schema
from backend.core.db.db_query_generator import generate_sql_query

# ------------------------------------------------------------
# 🔑 Load environment variables
# ------------------------------------------------------------
load_dotenv()

SESSION_ID = "db_query_test_session"
DB_URL = os.getenv("SUPABASE_DB_URL")

if not DB_URL:
    raise RuntimeError("❌ SUPABASE_DB_URL not found in .env")

# ------------------------------------------------------------
# 1️⃣ Connect to database
# ------------------------------------------------------------
print("\n🔗 Connecting to database...")
connect_db(SESSION_ID, DB_URL)

# ------------------------------------------------------------
# 2️⃣ Inspect schema
# ------------------------------------------------------------
print("\n🔍 Inspecting database schema...")
schema = inspect_schema(SESSION_ID)

print("\n📘 SCHEMA:")
print(json.dumps(schema, indent=2))

# ------------------------------------------------------------
# 3️⃣ Ask a natural language question
# ------------------------------------------------------------
question = "Show all users from India and their total order amount"

print("\n💬 USER QUESTION:")
print(question)

# ------------------------------------------------------------
# 4️⃣ Generate SQL
# ------------------------------------------------------------
print("\n🧠 Generating SQL...")
result = generate_sql_query(
    session_id=SESSION_ID,
    user_question=question,
    schema=schema
)

# ------------------------------------------------------------
# 5️⃣ Output result
# ------------------------------------------------------------
print("\n📤 GENERATED OUTPUT:")
print(json.dumps(result, indent=2))

# ------------------------------------------------------------
# 6️⃣ Disconnect
# ------------------------------------------------------------
disconnect_db(SESSION_ID)
print("\n✅ DB Query Generator test completed successfully")