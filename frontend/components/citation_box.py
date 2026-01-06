# frontend/components/citation_box.py

import streamlit as st

# ============================================================
# 📚 Unified Citation Renderer
# ============================================================

def render_citation_box(citations):
    """
    Render citations for BOTH:
      - RAG (document-based)
      - Database (SQL-based)

    Citation format is driven by:
        citation["type"] ∈ {"rag", "database"}
    """

    if not citations:
        st.info("📄 No citations used.")
        return

    st.markdown("### 📚 Source Citations")

    for cite in citations:
        cite_type = cite.get("type")

        # ====================================================
        # 📄 RAG CITATION
        # ====================================================
        if cite_type == "rag":
            _render_rag_citation(cite)

        # ====================================================
        # 🗄️ DATABASE CITATION
        # ====================================================
        elif cite_type == "database":
            _render_db_citation(cite)

        # ====================================================
        # ❓ UNKNOWN (safety)
        # ====================================================
        else:
            st.warning(f"⚠️ Unknown citation type: {cite_type}")

        st.markdown("---")


# ============================================================
# 📄 RAG Citation Card
# ============================================================

def _render_rag_citation(cite: dict):
    file_name = cite.get("file_name", "Unknown file")
    public_url = cite.get("public_url")

    rank = cite.get("rank", "?")
    chunk = cite.get("chunk_index", "?")
    total = cite.get("total_chunks_in_file", "?")
    score = cite.get("score")

    with st.container():
        st.markdown(f"**[{rank}] 📄 {file_name}**")

        st.markdown(f"- 🧩 Chunk: `{chunk}/{total}`")

        if score is not None:
            st.markdown(f"- 🎯 Score: `{round(float(score), 4)}`")

        if public_url:
            st.markdown(f"- 🔗 **Open Source:** [Click here]({public_url})")
        else:
            st.markdown("- 🔗 Source: N/A")


# ============================================================
# 🗄️ DATABASE Citation Card
# ============================================================

def _render_db_citation(cite: dict):
    db_type = cite.get("db_type", "unknown").upper()
    tables = cite.get("tables", [])
    sql = cite.get("sql")

    with st.container():
        st.markdown(f"**🗄️ Database Source ({db_type})**")

        if tables:
            st.markdown(f"- 📊 Tables used: `{', '.join(tables)}`")

        if sql:
            st.markdown("```sql")
            st.markdown(sql)
            st.markdown("```")