# frontend/components/db_section.py

import streamlit as st
from utils.api_client import connect_database, fetch_db_schema

# ============================================================
# 🗄️ Database Connection & Schema Section
# ============================================================

def render_db_section():
    st.subheader("🗄️ Connect Database")

    # --------------------------------------------------
    # Session guard
    # --------------------------------------------------
    session_id = st.session_state.get("session_id")

    if not session_id:
        st.warning("⚠ Please start a session (upload a document or chat first).")
        return

    # --------------------------------------------------
    # Init DB state (frontend-only)
    # --------------------------------------------------
    if "db_connected" not in st.session_state:
        st.session_state.db_connected = False

    if "db_type" not in st.session_state:
        st.session_state.db_type = None

    # --------------------------------------------------
    # DB Connection Input
    # --------------------------------------------------
    with st.form("db_connect_form"):
        connection_string = st.text_input(
            "🔗 Database Connection String",
            placeholder="postgresql+psycopg2://user:password@host:5432/dbname",
            help="SQLAlchemy-compatible connection string",
        )

        submitted = st.form_submit_button("🔌 Connect Database")

    # --------------------------------------------------
    # Handle DB Connection
    # --------------------------------------------------
    if submitted:
        if not connection_string.strip():
            st.error("❌ Connection string cannot be empty.")
        else:
            with st.spinner("Connecting to database..."):
                response = connect_database(
                    session_id=session_id,
                    connection_string=connection_string,
                )

            if response.get("message"):
                st.session_state.db_connected = True
                st.session_state.db_type = response.get("db_type")

                st.success(
                    f"✅ Connected to **{st.session_state.db_type.upper()}** database"
                )
            else:
                st.error(f"❌ Connection failed: {response}")

    # --------------------------------------------------
    # Connection Status
    # --------------------------------------------------
    if st.session_state.db_connected:
        st.markdown("---")
        st.success(
            f"🟢 Database Connected ({st.session_state.db_type.upper()})"
        )

        # --------------------------------------------------
        # Fetch & Display Schema
        # --------------------------------------------------
        if st.button("📊 View Database Schema"):
            with st.spinner("Fetching database schema..."):
                schema_resp = fetch_db_schema(session_id)

            schema = schema_resp.get("schema", {}).get("tables", {})

            if not schema:
                st.info("ℹ️ No tables found or schema unavailable.")
                return

            st.markdown("### 📑 Database Schema")

            for table_name, table_info in schema.items():
                with st.expander(f"📁 {table_name}", expanded=False):
                    st.markdown("**Columns:**")
                    for col in table_info.get("columns", []):
                        nullable = "NULL" if col.get("nullable") else "NOT NULL"
                        st.markdown(
                            f"- `{col['name']}` ({col['type']}) — {nullable}"
                        )

                    if table_info.get("primary_key"):
                        st.markdown(
                            f"🔑 **Primary Key:** `{', '.join(table_info['primary_key'])}`"
                        )

                    if table_info.get("foreign_keys"):
                        st.markdown("🔗 **Foreign Keys:**")
                        for fk in table_info["foreign_keys"]:
                            st.markdown(
                                f"- `{fk['column']}` → `{fk['ref_table']}.{fk['ref_column']}`"
                            )

    else:
        st.info("ℹ️ No database connected yet.")