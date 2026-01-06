# test/test_db_manager_manual.py

import os
from sqlalchemy import text
from dotenv import load_dotenv

from backend.core.db.db_manager import (
    connect_db,
    get_db_engine,
    get_db_type,
    disconnect_db,
)

# Load .env variables
load_dotenv()

SESSION_ID = "test_session"
DB_URL = os.getenv("SUPABASE_DB_URL")

if not DB_URL:
    raise RuntimeError("❌ SUPABASE_DB_URL not found in .env")

print("🔗 Connecting to database...")
connect_db(SESSION_ID, DB_URL)

engine = get_db_engine(SESSION_ID)
db_type = get_db_type(SESSION_ID)

db_type = get_db_type(SESSION_ID)

with engine.connect() as conn:
    print("\n📌 USERS TABLE")
    result = conn.execute(
        text("SELECT id, name, email, country FROM users ORDER BY id")
    )
    for row in result:
        print(dict(row._mapping))

    print("\n📌 ORDERS WITH USERS (JOIN)")
    result = conn.execute(
        text("""
            SELECT u.name, o.product, o.amount, o.created_at
            FROM users u
            JOIN orders o ON u.id = o.user_id
            ORDER BY o.amount DESC
        """)
    )
    for row in result:
        print(dict(row._mapping))

disconnect_db(SESSION_ID)

print("\n✅ DB Manager test completed successfully")