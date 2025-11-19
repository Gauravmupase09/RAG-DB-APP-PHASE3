import streamlit as st
from utils.api_client import upload_file, process_file, list_documents


# ============================================================
# 📤 Document Upload + Process Section (Final Version)
# ============================================================

def render_upload_section():
    st.subheader("📄 Upload Document")

    # STEP 1 — Try to read existing session_id from Streamlit memory
    session_id = st.session_state.get("session_id", None)

    uploaded_file = st.file_uploader(
        "Upload PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"]
    )

    # -----------------------------------------------------------
    # 📥 FILE UPLOAD
    # -----------------------------------------------------------
    if uploaded_file:
        st.info(f"Selected File: **{uploaded_file.name}**")

        if st.button("⬆️ Upload File", key="upload_btn"):
            with st.spinner("Uploading file..."):
                response = upload_file(session_id, uploaded_file)

            if response.get("message"):
                st.success(response["message"])
            else:
                st.error("❌ Upload failed.")
                return
            
            # STEP 2 — Store session_id returned by backend (new or existing)
            backend_session = response.get("session_id")
            if backend_session:
                st.session_state.session_id = backend_session
                session_id = backend_session

            st.success(f"📌 Active Session: {session_id}")

    st.write("---")
    st.subheader("⚙️ Process Documents")

    # -----------------------------------------------------------
    # 🔄 PROCESS DOCUMENTS
    # -----------------------------------------------------------

    session_id = st.session_state.get("session_id", None)

    if st.button("🔍 Extract → Chunk → Embed", key="process_btn"):
        if session_id is None:
            st.error("⚠ Upload a file first to start a session.")
            return

        with st.spinner("Processing document..."):
            response = process_file(session_id)

        status = str(response.get("status", "")).lower()

        # Backend returns:  "status": "✅ Processing complete"
        if "complete" in status or "success" in status:
            st.success("🎉 Processing complete! Ready to chat.")
        else:
            st.error(f"❌ Processing failed: {response}")

    st.write("---")
    st.subheader("📚 Uploaded Documents")

    # -----------------------------------------------------------
    # 📄 LIST UPLOADED DOCUMENTS
    # -----------------------------------------------------------

    session_id = st.session_state.get("session_id", None)

    if session_id:
        try:
            docs = list_documents(session_id)
            files = docs.get("files", [])

            if files:
                for doc_path in files:
                    # Extract only file name (works for all OS)
                    filename = doc_path.replace("\\", "/").split("/")[-1]
                    st.write(f"• **{filename}**")
            else:
                st.info("No documents uploaded yet.")

        except Exception:
            st.info("No documents uploaded yet.")

    else:
        st.info("Upload a document to begin.")