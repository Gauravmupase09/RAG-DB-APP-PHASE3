## backend/core/memory/session_memory.py

# ============================================================
# 🧠 In-Memory Sliding Window Conversation Memory
# ============================================================

SESSION_MEMORY = {}
MAX_MEMORY_MESSAGES = 10   # stores last 5 user + 5 assistant messages


def add_to_session_memory(session_id: str, role: str, content: str):
    """
    Add message to sliding window memory for a session.
    Role = "user" or "assistant".
    """
    if session_id not in SESSION_MEMORY:
        SESSION_MEMORY[session_id] = []

    SESSION_MEMORY[session_id].append({
        "role": role,
        "content": content
    })

    # Sliding window (keep last MAX messages)
    if len(SESSION_MEMORY[session_id]) > MAX_MEMORY_MESSAGES:
        SESSION_MEMORY[session_id] = SESSION_MEMORY[session_id][-MAX_MEMORY_MESSAGES:]


def get_session_memory(session_id: str):
    """Return memory list (may be empty)."""
    return SESSION_MEMORY.get(session_id, [])


def clear_session_memory(session_id: str):
    """Clear stored memory for a session."""
    if session_id in SESSION_MEMORY:
        del SESSION_MEMORY[session_id]