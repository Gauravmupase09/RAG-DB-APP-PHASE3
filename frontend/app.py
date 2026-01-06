# frontend/app.py

import streamlit as st

from components.upload_section import render_upload_section
from components.chat_section import render_chat_section
from components.db_section import render_db_section

from utils.api_client import reset_session


# ============================================================
# ⚙️ Page Config
# ============================================================
st.set_page_config(
    page_title="QueryVerse",
    page_icon="🌌",
    layout="wide"
)


# ============================================================
# 🔧 Session ID Handling (Frontend-side tracking ONLY)
# ============================================================
if "session_id" not in st.session_state:
    st.session_state.session_id = None  # Assigned after first upload / session start

session_id = st.session_state.session_id


# ============================================================
# 🏷️ Header
# ============================================================
st.title("🌌 QueryVerse — Query Documents & Databases Intelligently")
st.caption("Query everything. One interface. One intelligence.")

if session_id:
    st.success(f"🔗 Active Session: **{session_id}**")

st.markdown("---")


# ============================================================
# 🔄 Reset Session Button
# ============================================================
col1, col2 = st.columns([1, 4])

with col1:
    if st.button("🧹 Reset Session"):
        if session_id:
            reset_session(session_id)
            st.session_state.session_id = None

            # Optional: clear frontend-only flags
            st.session_state.pop("chat_history", None)
            st.session_state.pop("db_connected", None)
            st.session_state.pop("db_type", None)

            st.success("✅ Session reset successfully!")
            st.rerun()
        else:
            st.warning("No active session to reset.")

st.markdown("---")


# ============================================================
# 🔀 Main Tabs
# ============================================================
tab_upload, tab_chat, tab_db = st.tabs(
    ["📤 Upload & Process", "💬 Chat", "🗄️ Database"]
)


# ---------------------- 1️⃣ Upload & Process ----------------------
with tab_upload:
    render_upload_section()


# ---------------------- 2️⃣ Chat ----------------------
with tab_chat:
    if session_id is None:
        st.warning("⚠ Upload and process a document first to start chatting.")
    else:
        render_chat_section()


# ---------------------- 3️⃣ Database ----------------------
with tab_db:
    render_db_section()