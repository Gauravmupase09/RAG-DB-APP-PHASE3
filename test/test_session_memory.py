import requests
import time

BASE_URL = "http://localhost:8000/api/query"
SESSION_ID = "427c6e4e-174b-4456-b803-062dd11e4823"


def send_query(q):
    payload = {
        "session_id": SESSION_ID,
        "query": q,
        "top_k": 5
    }

    print("\n===============================")
    print("USER:", q)
    print("===============================")

    resp = requests.post(BASE_URL, json=payload)
    result = resp.json()

    print("ASSISTANT:", result.get("response"))
    print("used_chunks:", result.get("used_chunks"))
    print("citations:", result.get("citations"))
    print("formatted_citations:", result.get("formatted_citations"))
    print("===============================\n")

    return result


# -------------------------------------------------
# 1️⃣ Test first message (memory empty)
# -------------------------------------------------
send_query("Give me an overview of the document.")

time.sleep(1)

# -------------------------------------------------
# 2️⃣ Follow-up question referencing the previous answer
# -------------------------------------------------
send_query("Explain the key points you mentioned above.")

time.sleep(1)

# -------------------------------------------------
# 3️⃣ More memory chaining — expects LLM to use chat history
# -------------------------------------------------
send_query("Why is that important in the context of this document?")

time.sleep(1)

# -------------------------------------------------
# 4️⃣ Ask for summary (should summarize last 10 messages only)
# -------------------------------------------------
send_query("Summarize our chat so far.")