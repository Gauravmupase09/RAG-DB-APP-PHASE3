import os
import langchain
from typing import List, Dict, Generator


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


# ✅ Ensure Gemini API key is set
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY


# ======================================================
# 🧠 Prompt Builder
# ======================================================
def build_prompt_template() -> PromptTemplate:
    """
    Builds a descriptive, context-aware prompt for Gemini.
    """
    template = """
You are a helpful AI assistant that helps users understand and explore the contents
of their uploaded documents (PDFs, reports, articles, etc.).

Your goal is to give **clear, well-structured, and descriptive answers** to the user's query
based on the *context extracted from these documents* and your general understanding of the topic.

### Guidelines:
- Provide **clear, detailed, and contextual answers** to user questions.
- Use the provided context as your primary source of truth.
- If the context is incomplete, you may enhance it using your general knowledge,
  but your answer must remain accurate and relevant.
- Explain concepts in a **teaching tone** — informative yet easy to follow.
- Always refer to the content as coming **from the uploaded documents** when applicable.
- Write in a **professional yet easy-to-understand tone**, as if explaining to a curious student.
- Be detailed — include reasoning, examples, or short explanations wherever appropriate.
- Avoid saying “I don’t know.” If context is limited, provide your best possible answer based on what you know.
- Mention insights that appear to come **from the provided document** when applicable.
- Avoid short or generic answers — write comprehensive explanations.
- Use paragraphs, examples, and reasoning when appropriate.

--------------------
📘 Context:
{context}

💬 Question:
{question}

--------------------
🧠 Answer (comprehensive, contextual, and detailed):
"""
    return PromptTemplate(
        input_variables=["context", "question"],
        template=template.strip()
    )


# ======================================================
# 🚀 Generate Response (Standard)
# ======================================================
def generate_llm_response(query: str, context_chunks: List[str], model_name: str = "gemini-2.5-flash") -> Dict:
    """Generates a descriptive, contextual answer using Gemini 2.5 Flash."""
    try:
        logger.info(f"🤖 Generating LLM response for query: '{query}' using {model_name}")

        # ✅ Combine top retrieved chunks into context
        context_text = "\n\n".join(context_chunks[:5]) if context_chunks else "No relevant context available."

        # ✅ Initialize Gemini model
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=GEMINI_API_KEY,
            temperature=0.4  # balanced factuality + descriptiveness
        )

        # ✅ Build prompt and chain
        prompt = build_prompt_template()
        chain = RunnableSequence(prompt | llm)

        # ✅ Run once (non-streaming)
        result = chain.invoke({"context": context_text, "question": query})

        return {
            "query": query,
            "response": result.content if hasattr(result, "content") else str(result),
            "used_chunks": len(context_chunks),
            "model": model_name
        }

    except Exception as e:
        logger.exception(f"❌ Error generating LLM response: {e}")
        return {
            "query": query,
            "response": f"⚠️ Error generating response: {str(e)}",
            "used_chunks": len(context_chunks),
            "model": model_name
        }


# ======================================================
# ⚡ Streaming Response (Typing Effect)
# ======================================================
def stream_llm_response(query: str, context_chunks: List[str], model_name: str = "gemini-2.5-flash") -> Generator[str, None, None]:
    """
    Stream LLM response chunk-by-chunk (like ChatGPT typing effect).
    Works great for chat UIs and WebSocket integration.
    """
    try:
        logger.info(f"💬 Streaming LLM response for query: '{query}' using {model_name}")

        context_text = "\n\n".join(context_chunks[:5]) if context_chunks else "No relevant context available."

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=GEMINI_API_KEY,
            temperature=0.4
        )

        prompt = build_prompt_template()
        chain = RunnableSequence(prompt | llm)

        # ✅ Stream directly from the chain
        for chunk in chain.stream({"context": context_text, "question": query}):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    except Exception as e:
        logger.exception(f"❌ Error streaming LLM response: {e}")
        yield f"[Error] {str(e)}"