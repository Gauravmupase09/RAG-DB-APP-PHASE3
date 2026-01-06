# backend/core/agent/tools/db_tool.py

from langchain_core.tools import tool
from backend.core.db.db_executor import run_db_execution


@tool
async def db_tool(session_id: str, query: str):
    """
    DATABASE QUERY TOOL — Structured Data Retrieval (NO LLM RESPONSE)

    PURPOSE:
        Use this tool to retrieve information from a connected database
        when the user’s question requires structured, tabular, or
        aggregated data stored in database tables.

        This tool:
          - Translates natural language into SQL
          - Executes the SQL safely (READ-ONLY)
          - Returns raw rows and metadata
          - DOES NOT generate a natural-language answer

        A separate LLM step will later explain the results.

    WHEN TO CALL THIS TOOL:
        Call this tool whenever the user asks questions that:
          - Require querying database tables
          - Need filtering, aggregation, grouping, sorting, or counting
          - Depend on the current state of stored structured data

        Examples (generic, schema-agnostic):
          - “Show all records where condition X is true”
          - “How many entries were created last week?”
          - “Give me the total / average / sum grouped by a field”
          - “List top N items based on some metric”
          - “Compare values across categories”
          - “Fetch rows matching specific criteria”

        In short:
          → If the answer must come from executing SQL on a database,
            this tool SHOULD be called.

    WHEN NOT TO CALL THIS TOOL:
        - General knowledge or conversational questions
        - Questions answerable without querying stored data
        - Hypothetical or opinion-based questions
        - Questions that should be answered using documents (RAG)

    INPUT PARAMETERS:
        session_id (str):
            Unique identifier for the user/session.
            Used to resolve the correct database connection and schema.

        query (str):
            The user’s natural-language question describing
            what data they want from the database.

    RETURNS (dict — TOOL-SAFE OUTPUT):
        {
            "query": "<original user question>",
            "sql": "<generated SQL query or null>",
            "db_type": "<database engine name>",
            "tables_used": ["table1", "table2"],
            "rows": [
                { "column": value, ... },
                ...
            ],
            "row_count": <int>,
            "confidence": "<low | high>"
        }

    IMPORTANT NOTES FOR THE ASSISTANT:
        - Do NOT explain results here
        - Do NOT summarize data here
        - Do NOT modify rows
        - Always return raw data only
        - Final explanation will be handled by a separate LLM step
    """

    result = await run_db_execution(session_id=session_id, query=query)

    return result