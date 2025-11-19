# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.rag.llm_engine import generate_llm_response

# query = "Summarize how COVID-19 affected students emotionally and academically."
# context = [
#     "The pandemic disrupted in-person learning and increased feelings of isolation among students.",
#     "Many students reported higher stress and lower academic performance due to online transition."
# ]

# print("🔍 Running Gemini 2.5 Flash test...\n")
# res = generate_llm_response(query=query, context_chunks=context)
# print("✅ Model:", res["model"])
# print("\n💬 Response:\n", res["response"])

# test/test_llm_stream.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.rag.llm_engine import generate_llm_response, stream_llm_response

query = "Explain how COVID-19 affected education systems worldwide."
context = [
    "The pandemic forced schools and universities to shift to online learning.",
    "Many students faced challenges with internet access and motivation."
]

# Standard full response
res = generate_llm_response(query, context)
print("\n🧠 Full Response:\n", res["response"])

# Streaming response (typing effect)
print("\n⚡ Streaming Response:\n")
for token in stream_llm_response(query, context):
    print(token, end="", flush=True)