import streamlit as st
from components.upload_section import render_upload_section
from components.chat_section import render_chat_section
from utils.api_client import reset_session
from utils.config import BACKEND_URL

st.set_page_config(
    page_title="RAG Chat App",
    page_icon="📄",
    layout="wide"
)

# ============================================================
# 🔧 Session ID Handling (Frontend-side tracking)
# ============================================================
if "session_id" not in st.session_state:
    st.session_state.session_id = None  # Will be assigned after first upload

session_id = st.session_state.session_id

# ============================================================
# 🏷️ HEADER
# ============================================================
st.title("📘 RAG Chat App — Chat With Your Documents")

if session_id:
    st.success(f"🔗 Active Session: **{session_id}**")

st.markdown("---")


# ============================================================
# 🔄 RESET SESSION BUTTON
# ============================================================
col1, col2 = st.columns([1, 4])

with col1:
    if st.button("🧹 Reset Session"):
        if session_id:
            response = reset_session(session_id)
            st.session_state.session_id = None
            st.success("Session reset successfully!")
            st.rerun()
        else:
            st.warning("No active session to reset.")


with col2:
    st.info(f"Backend URL: {BACKEND_URL}")


st.markdown("---")


# ============================================================
# 🔀 TABS: Upload / Chat
# ============================================================
tab_upload, tab_chat = st.tabs(["📤 Upload & Process", "💬 Chat With Document"])


# ---------------------- 1️⃣ UPLOAD & PROCESS TAB ----------------------
with tab_upload:
    render_upload_section()   # Handles upload, processing, doc listing


# ---------------------- 2️⃣ CHAT TAB ----------------------
with tab_chat:
    if session_id is None:
        st.warning("⚠ Upload and process a document first to start chatting.")
    else:
        render_chat_section()   # Chat window UI