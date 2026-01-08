# 📘 RAG-DB-APP(🌌 QueryVerse) — Phase 3: Agentic RAG + Database Intelligence

Phase 3 is a major architectural evolution of the RAG-APP system.
It extends the Agentic RAG pipeline from Phase 2 by introducing Database-aware reasoning, allowing the
LLM to autonomously choose between:
 - General reasoning
 
 - Document-based retrieval (RAG)
   
 - Structured database querying (SQL)
 
All within a single LangGraph agent workflow.

---

# 🚀 What’s New in Phase 3?

| Capability |	Phase 2	| Phase 3 (New 🚀) |
|------|--------------|-------------|
| **Agentic Routing** | RAG vs General | RAG vs DB vs General |
| **Database Support** | ❌ | ✅ Multi-DB querying |
| **NL → SQL** | ❌ | ✅ LLM-driven SQL generation |
| **DB Schema Awareness** |	❌ | ✅ Live schema inspection |
| **Persistent DB Sessions** | ❌ | ✅ Auto-reconnect per session |
| **Tool Contracts** | Partial	| ✅ Strict JSON-safe tools |
| **Unified Citations** | Docs only	| Docs + Database |
| **Frontend DB UI** | ❌ | ✅ DB connect + query panel |
| **Architecture** | Agentic RAG | Multi-tool Agent Platform |

---

# 🧠 High-Level Agentic Workflow
```bash
START
  ↓
assistant_node
  ├─ decides → NO_TOOL_REQUIRED
  │              ↓
  │         finalize_node
  │              ↓
  │           Final Answer
  │
  ├─ decides → rag_tool
  │              ↓
  │          tool_node
  │              ↓
  │         finalize_node
  │              ↓
  │     Final Answer (with citations)
  │
  └─ decides → db_tool
                 ↓
             tool_node
                 ↓
            finalize_node
                 ↓
        Final Answer (SQL-explained)
```
---

# 🧩 Decision Logic (Core Idea)

The assistant_node (LLM) reasons over the user query and decides:

 - General → no tool call

 - Document-based → calls rag_tool

 - Structured / tabular data → calls db_tool

This makes the system context-aware, cost-efficient, and intelligent.

---

# 🧠 Agent Nodes Explained
🔹 `assistant_node`

- Analyzes user intent

- Chooses one of three paths:

  - General reasoning

  - RAG retrieval

  - Database querying

- Never generates the final answer

---

🔹 `rag_tool`

- Retrieves top-k relevant document chunks

- Returns:

  - chunks

  - citation metadata

- No answer generation

---

🔹 `db_tool`

- Converts natural language → SQL (READ-ONLY)

- Inspects live database schema

- Executes SQL safely

- Returns:

  - rows (JSON-safe)

  - tables used

  - SQL query

  - confidence score

---

🔹 `finalize_node`

- Central answer generator

- Combines:

  - session memory

  - user query

  - tool output (RAG or DB)

- Produces:

  - final response

  - unified citations (documents / database)

**📌 Important Rule (Enforced):**

Tools must return Python dicts with JSON-serializable values only
(`datetime`, `Decimal`, `UUID`, custom objects never cross the tool boundary)

---

# 📁 Project Structure (Phase 3)
```bash
QUERYVERSE(RAG-DB-APP-PHASE3)/
│
├── backend/
│   ├── api/
│   │   └── routes/
│   │       ├── upload.py
│   │       ├── process.py
│   │       ├── query.py
│   │       ├── db_connect.py
│   │       ├── db_schema.py
│   │       ├── reset_session.py
│   │       └── list_docs.py
│   │
│   ├── core/
│   │   ├── agent/
│   │   │   ├── graph_state.py
│   │   │   ├── graph_builder.py
│   │   │   ├── nodes/
│   │   │   │   ├── assistant_node.py
│   │   │   │   ├── finalize_node.py
│   │   │   │   └── tool_node.py
│   │   │   └── tools/
│   │   │       ├── rag_tool.py
│   │   │       └── db_tool.py
│   │   │
│   │   ├── db/
│   │   │   ├── db_executor.py
│   │   │   ├── db_manager.py
│   │   │   ├── db_query_generator.py
│   │   │   ├── db_types.py
│   │   │   └── schema_inspector.py
│   │   │
│   │   ├── rag/
│   │   │   ├── rag_pipeline.py
│   │   │   ├── citation_handler.py
│   │   │   ├── retriever.py
│   │   │   └── resource_store.py
│   │   │
│   │   ├── llm/
│   │   │   └── llm_engine.py
│   │   │
│   │   ├── memory/
│   │   │   └── session_memory.py
│   │   │
│   │   ├── doc_processing_unit/
│   │   ├── text_extractor.py
│   │   ├── text_cleaner.py
│   │   ├── chunking.py
│   │   ├── embedding_engine.py
│   │   ├── model_manager.py
│   │   └── qdrant_manager.py
│   │
│   ├── data/
│   │   ├── db/
│   │   ├── uploads/
│   │   └── processed/
│   │
│   ├── model/
│   │   └── schemas.py
│   │
│   ├── utils/
│   │   ├── config.py
│   │   ├── file_manager.py
│   │   └── logger.py
│   │
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── components/
│   │   ├── upload_section.py
│   │   ├── chat_section.py
│   │   ├── db_section.py
│   │   └── citation_box.py
│   │
│   ├── utils/
│   │   ├── api_client.py
│   │   └── config.py
│   │
│   ├── app.py
│   └── requirements.txt
│
├── test/
│   ├── test_assistant_node_manual.py
│   ├── test_db_execution_manual.py
│   ├── test_db_generation_manual.py
│   ├── test_db_manager_manual.py
│   ├── test_db_query_generator_manual.py
│   ├── test_db_tool_manual.py
│   ├── test_schema_inspector_manual.py
│   └── test_finalize_general_manual.py
│
├── .env
├── .gitignore
└── README.md
```

---

# ⚙️ Tech Stack (Phase 3)

| Layer | Technology |
|--------------|-------------|
| **Agent** | Framework |	LangGraph |
| **LLM**	| Google Gemini 2.5 Flash |
| **Vector DB**	| Qdrant |
| **Embeddings**	| BAAI/bge-small-en-v1.5 |
| **Databases** | Any SQL database via connection string (SQLAlchemy-based) |
| **Backend**	| FastAPI |
| **Frontend**	| Streamlit |
| **Memory**	| Sliding window via session_memory |

⚠️ Important clarification
QueryVerse does not host databases.
It connects to user-provided databases via connection strings.

---

# 🔌 Database Capabilities (Phase 3)

- Natural language → SQL

- Live schema inspection

- Read-only enforcement

- Session-persistent connections

- Automatic reconnection (until reset)

- Unified database citations

Example:
```bash
User: "Show all users from the database"
→ assistant_node → db_tool → finalize_node
```
---

# 📡 API Endpoints

| Method | Route | Purpose |
|------|--------------|-------------|
| POST | `/api/upload` | Upload documents |
| POST | `/api/process/{session_id}`	| Process + embed docs |
| POST | `/api/query` | Agentic RAG / DB query |
| POST | `/api/db/connect`	| Connect database |
| GET | `/api/db/schema`	| View DB schema |
| GET	| `/api/list_docs`	| List uploaded docs |
| DELETE | `/api/reset_session`	| Reset session |

---

# 🛠️ Installation & Setup (Phase 3)

Phase 3 introduces dynamic database connectivity, multi-tool agent routing, and strict tool-boundary contracts.
Follow the steps carefully.

---

**1️⃣ Clone the Repository**
```bash
git clone https://github.com/Gauravmupase09/RAG-DB-APP-PHASE3.git
cd RAG-DB-APP-PHASE3
```
---

**2️⃣ Environment Configuration**

Create a .env file in the root directory:
```bash
# LLM
GOOGLE_API_KEY=your_google_api_key_here

# Embeddings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Vector DB
QDRANT_URL=http://localhost:6333
```
---

**3️⃣ Backend Setup (FastAPI + LangGraph)**
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux / macOS
```

**Install Dependencies**
```bash
pip install -r requirements.txt
```
---

**4️⃣ Start Qdrant (Vector Database)**

Using Docker (recommended):
```bash
docker run -p 6333:6333 qdrant/qdrant
```

Qdrant UI (optional):
👉 http://localhost:6333/dashboard

---

**5️⃣ Run Backend Server**
```bash
uvicorn main:app --reload
```

Backend available at:

 - http://localhost:8000

 - http://localhost:8000/docs

---

**6️⃣ Frontend Setup (Streamlit)**
```bash
cd ../frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Frontend UI:
👉 http://localhost:8501

---

**7️⃣ Database Connection (Phase 3 Feature)**

From the frontend DB section:

 - Provide a database connection string

 - Supported examples:

```bash
postgresql://user:password@localhost:5432/dbname
sqlite:///example.db
```

✔ No schema upload required

✔ Schema is inspected dynamically

✔ SQL is generated automatically

---

**🔁 End-to-End Flow**

1. Upload documents (optional)

2. Connect database (optional)

3. Ask a question

4. Agent decides:

 - `NO_TOOL_REQUIRED`

 - `rag_tool`

 - `db_tool`

5. Final answer generated by finalize_node

---

# 🧪 Testing (Manual & Debug-Friendly)

Phase 3 focuses on contract safety and tool isolation.

Run manual tests from /test directory:
```bash
python test_db_execution_manual.py
python test_db_tool_manual.py
python test_finalize_general_manual.py
```

Each test validates:

 - Tool contracts

 - JSON-safe boundaries

 - Agent routing correctness

---

# 🤝 Contributing

Contributions are welcome!
Phase 3 is designed for extension, not rewrites.

---

**🎯 Areas You Can Contribute**
**🧠 Agent Intelligence**

 - Better intent classification

 - Multi-tool chaining (RAG → DB → RAG)

 - Tool confidence scoring

**🗄️ Database Layer**

 - MySQL / MSSQL support

 - Query optimization heuristics

 - Read-only policy enforcement

 - Join safety validation

**📄 RAG Improvements**

 - Hybrid search (BM25 + vector)

 - Multi-document reasoning

 - Chunk re-ranking

 - Streaming responses

**🎨 Frontend**

 - Result tables

 - SQL preview toggles

 - DB schema visualization

 - Tool decision transparency

---

# 🧩 Contribution Rules (IMPORTANT)

✔ Tools MUST return JSON-serializable data only

❌ No datetime / Decimal / UUID across tool boundary

✔ Use make_json_safe() at execution layer

✔ finalize_node must remain orchestration-only

✔ No LLM calls inside tool execution

---

# 🧪 Before Submitting PR

 - Test at least one tool path

 - Validate JSON safety

 - Run agent end-to-end

 - Update README if behavior changes

---

**📜 License**

MIT License