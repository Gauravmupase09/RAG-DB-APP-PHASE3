# test/test_schema_inspector_manual.py

from dotenv import load_dotenv
import os
import json

from backend.core.db.db_manager import connect_db, disconnect_db
from backend.core.db.schema_inspector import inspect_schema

# Load environment variables
load_dotenv()

SESSION_ID = "schema_test_session"
DB_URL = os.getenv("SUPABASE_DB_URL")

if not DB_URL:
    raise RuntimeError("❌ SUPABASE_DB_URL not found")

print("🔗 Connecting to DB...")
connect_db(SESSION_ID, DB_URL)

print("\n🔍 Inspecting schema...\n")
schema = inspect_schema(SESSION_ID)

# Pretty print schema
print(json.dumps(schema, indent=2))

disconnect_db(SESSION_ID)
print("\n✅ Schema inspection test completed")