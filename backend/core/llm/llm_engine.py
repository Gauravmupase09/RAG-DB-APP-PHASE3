# backend/core/llm/llm_engine.py

import os
import langchain
from typing import List, Dict, Optional

# 🩹 Compatibility patch for LangChain integrations (fix missing attrs)
for attr, default in {
    "verbose": False,
    "debug": False,
    "llm_cache": None,
}.items():
    if not hasattr(langchain, attr):
        setattr(langchain, attr, default)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

from backend.utils.logger import logger
from backend.utils.config import GEMINI_API_KEY


# ✅ Ensure Gemini API key is visible to the SDK
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY


# ======================================================
# 🔧 LLM FACTORY (used by assistant_node + others)
# ======================================================

def get_llm(
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.4,
) -> ChatGoogleGenerativeAI:
    """
    Return a base Gemini chat model instance.

    This is used by:
      - assistant_node (for tool vs general routing)
      - any other component that needs a "bare" LLM
    """
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
    )


# ======================================================
# 🧠 Shared Answer Prompt (RAG + General)
# ======================================================

def build_answer_prompt() -> PromptTemplate:
    """
    Builds a single, flexible prompt template that works for:
      - General conversation / Q&A
      - Document-grounded RAG answers
      - DB based answers

    `mode` controls behavior:
      - "general"  → no retrieved document chunks, maybe some chat history
      - "rag"      → answer grounded in provided document context
      - "DB"       → answer grounded in provided DB
    """
    template = """
You are a helpful AI assistant in a *multi-capability chat application*.

You operate in one of three modes:

1) MODE = "general"
   - Normal conversational or general knowledge question
   - No documents, no database
   - Use conversation context if provided

2) MODE = "rag"
   - The user’s question MUST be answered using the provided document context.
   - The text in the Context section comes from the user’s uploaded files
     (PDFs, reports, articles, etc.).
   - Treat the context as the primary source of truth.
   - If the context doesn’t contain enough information, say so and answer
     as best you can, but DO NOT invent very specific document details.

3) MODE = "db"
   - Answer MUST be based ONLY on the database query result rows
   - Explain what the data shows in clear human language
   - Do NOT invent rows or values
   - If rows are empty, clearly say no results were found
   - Do NOT assume anything beyond the given data

GENERAL GUIDELINES (for BOTH modes):
- Give clear, well-structured, and descriptive answers.
- Prefer short paragraphs and bullet points over long walls of text.
- Explain like you’re teaching a curious student.
- Be honest about uncertainty; do NOT hallucinate very specific facts.
- If something is explicitly stated in the Context, rely on that.

------------------------------------------------------
MODE: {mode}
------------------------------------------------------
📘 Context (may be conversation history and/or document chunks):
{context}

💬 User Question:
{question}

------------------------------------------------------
🧠 Your Response (helpful, clear, and well-structured):
"""
    return PromptTemplate(
        input_variables=["mode", "context", "question"],
        template=template.strip(),
    )


# ======================================================
# 🧵 INTERNAL HELPER: build chain
# ======================================================

def _build_chain(
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.4,
) -> RunnableSequence:
    """
    Internal helper to build a PromptTemplate → LLM runnable chain.
    Used by both general + RAG answer functions (streaming & non-streaming).
    """
    llm = get_llm(model_name=model_name, temperature=temperature)
    prompt = build_answer_prompt()
    # PromptTemplate | ChatGoogleGenerativeAI => RunnableSequence
    return RunnableSequence(prompt | llm)


# ======================================================
# 🌐 GENERAL ANSWER (NO DOCUMENT RETRIEVAL)
#   - Used by finalize_node when assistant_node says "NO_TOOL_REQUIRED"
# ======================================================

def generate_general_answer(
    query: str,
    memory_text: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> Dict:
    """
    Generate a GENERAL (non-RAG) answer.

    - `memory_text` is typically your sliding-window chat history,
      already formatted as a single string
      (e.g. "user: ...\\nassistant: ...\\n...").
    - No document chunks are used.
    """
    try:
        logger.info(f"🤖 [GENERAL] Generating answer for query: '{query}'")

        context_text = memory_text or "No prior conversation context is available."

        chain = _build_chain(model_name=model_name)

        result = chain.invoke(
            {
                "mode": "general",
                "context": context_text,
                "question": query,
            }
        )

        return {
            "query": query,
            "response": getattr(result, "content", str(result)),
            "used_chunks": 0,        # no document chunks in general mode
            "model": model_name,
        }

    except Exception as e:
        logger.exception(f"❌ [GENERAL] Error generating answer: {e}")
        return {
            "query": query,
            "response": f"⚠ Error generating response: {str(e)}",
            "used_chunks": 0,
            "model": model_name,
        }


# ======================================================
# 📄 RAG ANSWER (DOCUMENT-GROUNDED)
#   - Used by run_rag_generation() in rag_pipeline.py
# ======================================================

def generate_rag_answer(
    query: str,
    context_chunks: List[str],
    model_name: str = "gemini-2.5-flash",
) -> Dict:
    """
    Generate a DOCUMENT-GROUNDED (RAG) answer.

    - `context_chunks` should be a list of text chunks
       (document snippets + optionally conversation history)
       that you’ve already prepared in rag_pipeline.py.
    """
    try:
        logger.info(
            f"🤖 [RAG] Generating answer for query: '{query}' "
            f"with {len(context_chunks)} context chunks"
        )

        if context_chunks:
            # You can tune how many chunks to join here if needed.
            context_text = "\n\n".join(context_chunks)
        else:
            # RAG path but no context: model should be honest about that.
            context_text = (
                "No document context was retrieved for this query. "
                "Answer based on your general knowledge but say that "
                "no supporting document passage was found."
            )

        chain = _build_chain(model_name=model_name)

        result = chain.invoke(
            {
                "mode": "rag",
                "context": context_text,
                "question": query,
            }
        )

        return {
            "query": query,
            "response": getattr(result, "content", str(result)),
            "used_chunks": len(context_chunks),
            "model": model_name,
        }

    except Exception as e:
        logger.exception(f"❌ [RAG] Error generating RAG answer: {e}")
        return {
            "query": query,
            "response": f"⚠ Error generating response: {str(e)}",
            "used_chunks": len(context_chunks),
            "model": model_name,
        }
    

# ======================================================
# 🗄️ DATABASE ANSWER (DB-GROUNDED)
#   - Used by run_db_generation() in db_executor.py
# ======================================================

def generate_db_answer(
    query: str,
    rows: List[Dict],
    sql: str,
    db_type: str,
    memory_text: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> Dict:
    """
    Generate a natural-language explanation of DB query results.
    Used by run_db_generation().
    """
    try:
        logger.info(f"🤖 [DB] Query='{query}' | Rows={len(rows)}")

        context_parts = []

        if memory_text:
            context_parts.append("Conversation History:\n" + memory_text)

        context_parts.append(f"Database Type: {db_type}")
        context_parts.append(f"Executed SQL:\n{sql}")
        context_parts.append(f"Query Result Rows:\n{rows}")

        context = "\n\n".join(context_parts)

        chain = _build_chain(model_name=model_name, temperature=0.3)

        result = chain.invoke(
            {
                "mode": "db",
                "context": context,
                "question": query,
            }
        )

        return {
            "query": query,
            "response": getattr(result, "content", str(result)),
            "model": model_name,
        }

    except Exception as e:
        logger.exception("❌ DB answer failed")
        return {
            "query": query,
            "response": f"Error explaining database results: {e}",
            "model": model_name,
        }