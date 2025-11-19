import streamlit as st

# ============================================================
# 📚 Clean Citation Box Component
# ============================================================

def render_citation_box(citations):
    """
    Renders readable citation cards for RAG references.
    Each citation entry example:
    
    {
        "file_name": "abc.pdf",
        "public_url": "http://localhost:8000/uploads/session/file.pdf",
        "chunk_index": 1,
        "total_chunks_in_file": 10,
        "score": 0.91,
        "rank": 1
    }
    """

    if not citations or len(citations) == 0:
        st.info("📄 No citations used.")
        return

    st.markdown("### 📚 Source Citations")

    for cite in citations:
        file_name = cite.get("file_name", "Unknown File")
        public_url = cite.get("public_url")
        rank = cite.get("rank", "?")
        chunk = cite.get("chunk_index", "?")
        total = cite.get("total_chunks_in_file", "?")
        score = round(float(cite.get("score", 0)), 4)

        with st.container():
            st.markdown(f"**[{rank}] {file_name}**")
            st.markdown(f"- 🧩 Chunk: `{chunk}/{total}`")
            st.markdown(f"- 🎯 Score: `{score}`")

            if public_url:
                # Clickable URL (clean formatting)
                st.markdown(f"- 🔗 **Open Source:** [Click here]({public_url})")
            else:
                st.markdown("- 🔗 Source: N/A")

            st.markdown("---")