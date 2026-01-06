# frontend/components/chat_section.py

import streamlit as st
from utils.api_client import send_query
from components.citation_box import render_citation_box


# ============================================================
# 💬 Chat Section (Document Q&A)
# ============================================================

def render_chat_section():
    st.subheader("💬 Chat With Your Documents")

    session_id = st.session_state.get("session_id", None)
    if session_id is None:
        st.warning("⚠ Please upload and process a document first.")
        return

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ---------------------------
    # Display chat history
    # ---------------------------
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            with st.chat_message("user"):
                st.write(chat["content"])

        else:
            with st.chat_message("assistant"):
                st.write(chat["content"])

                # Show citations (raw dicts only)
                if chat.get("citations"):
                    render_citation_box(chat["citations"])

    # ---------------------------
    # Input Box
    # ---------------------------
    user_input = st.chat_input("Ask something about your document...")

    if user_input:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_query(session_id, user_input)

            answer = response.get("response", "❌ Error generating response.")
            citations = response.get("citations", [])   # RAW citation dict list

            st.write(answer)

            # Render citation cards
            if citations:
                render_citation_box(citations)

        # Save assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "citations": citations  # Save RAW dicts, not strings
        })

        st.rerun()