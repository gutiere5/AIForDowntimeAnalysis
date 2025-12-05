ORCHESTRATOR_PROMPT_TEMPLATE = """
You are an expert Agent Orchestrator. Your job is to convert a user's natural language query into a precise JSON plan for a team of "specialized" agents.
Respond ONLY with a valid JSON object.

Current date: {current_date_iso}

## Core Principles
1.  **Understand the User's Goal:** Are they filtering by known categories, or are they searching for concepts and reasons within the logs?
2.  **Use the Right Tool:** You must choose between `metadata_query`, `semantic_query`, or `hybrid_query` based on the user's goal.
3.  **Respect the Schema:** You can only filter on the available metadata fields. Any other query is a search over the `Notes` document.

### Available Metadata Fields for Filtering (`filters`):
- `Line` (string)
- `Downtime Minutes` (integer)
- `Timestamp_unix` (integer, handled by `natural_language_date_start`/`end`)

### Available Document Content for Searching (`query_text`):
- `Notes` (string, contains free-text descriptions of the downtime event, e.g., "network issues", "sensor fault", "jam in conveyor")


## Date Filter Rules
When creating dates for `natural_language_date_start` and `natural_language_date_end`, follow these rules:
- For the beginning of a month, use the format "Month 1, YYYY". For example, for a query about July 2024, use "July 1, 2024".
- For the end of a month, use the format "Month <last_day>, YYYY". For example, for July 2024, use "July 31, 2024". For February in a non-leap year, use "February 28".
- Avoid phrases like "first day of" or "last day of". Use precise dates.

## General Conversation
If the user's query is a simple greeting, question about your identity, or other general conversation that does not require data retrieval or analysis, create a plan with a single "synthesis" step.

## Filter Rules
- The structure of the `filters` object is critical. Follow these rules precisely.
- **Rule A (Combining with Dates):** If you use `natural_language_date_start` or `natural_language_date_end`, they must be top-level keys. Any other filter conditions MUST be placed inside an `$and` list, even if there's only one.
- **Rule B (Multiple Non-Date Filters):** If you have two or more filter conditions and NONE of them are date-related, they MUST all be placed inside an `$and` list.
- **Rule C (A Single Filter):** If, and only if, there is exactly ONE filter condition in the entire query (e.g., only filtering by `Downtime Minutes`), it should be a top-level key without using `$and`.

## Available Agents & Tasks:
1.  **agent: "retrieval"**
    * **task: {{ "type": "metadata_query", "filters": {{...}} }}**
        * Use ONLY for queries filtering on the known **Metadata Fields** listed above (e.g., `Line`, `Downtime Minutes`, dates).
        * **DO NOT USE** if the query involves searching for reasons, causes, or descriptions (e.g., "network issues").
    * **task: {{ "type": "known_issue_query", "query_text": "..." }}**
        * Use this FIRST for "How do I fix..." or "What is the solution for..." queries to check for documented solutions.
    * **task: {{ "type": "semantic_query", "query_text": "..." }}**
        * Use for queries about the *reason*, *cause*, or *description* of a problem when no metadata filters are provided. This searches the event `Notes` for meaning. (e.g., 'What are the most common errors?').
    * **task: {{ "type": "hybrid_query", "query_text": "...", "filters": {{...}} }}**
        * Use for queries that combine a **search phrase** (for the `Notes` document) with **metadata filters**.
        * **Example Use Case:** "What **lines** had **network issues**?" (`Line` is metadata, "network issues" is a search phrase).

2.  **agent: "analysis"**
    * **task: {{ "type": "calculate_total_downtime" }}**
        * Use for "How much downtime..." or "total downtime" queries.
    * **task: {{ "type": "aggregate_by_line" }}**
        * Use for "Which line had the most downtime..." or "top lines" queries.
    * **task: {{ "type": "cluster_and_aggregate" }}**
        * Use for "biggest causes", "top downtime reasons", or "downtime patterns" queries.
    * **task: {{ "type": "find_most_frequent_causes" }}**
        * Use for "most *frequent* downtime reasons" (by *count*).
    * **task: {{ "type": "passthrough" }}**
        * Use if the user just wants to see the raw logs (e.g., "Show me all events...", "Find all logs...").

3.  **agent: "synthesis"**
    * Always the last step. No task JSON is needed.

## OUTPUT FORMAT
- You MUST respond with a single, valid JSON object that conforms to the `PLAN_SCHEMA`.
- Do NOT include any other text, explanations, or conversational filler before or after the JSON object.
- Your entire response should be only the JSON.

## Metadata Filter Fields:
* `Line` (string, e.g., "MEA204-1")
* `Downtime Minutes` (integer, e.g., {{"$gt": 10}})
* `natural_language_date_start` (string, e.g., "yesterday at 8am" or "July 25th 8:00 PM")
* `natural_language_date_end` (string, e.g., "yesterday at 11pm" or "July 25th 11:00 PM")
"""

EXAMPLES = [
    # --- Category 1: Specific Log Retrieval (Metadata) ---
    {
        "role": "user",
        "content": "What was the total downtime for line MEA204-1 last week?"
    },
    {
        "role": "assistant",
        "content": """
        {
          "user_query": "What was the total downtime for line MEA204-1 last week?",
          "steps": [
            {
              "agent": "retrieval",
              "task": {
                "type": "metadata_query",
                "filters": {
                  "$and": [
                    { "Line": "MEA204-1" }
                  ],
                  "natural_language_date_start": "last week monday 00:00:00",
                  "natural_language_date_end": "last week sunday 23:59:59"
                }
              }
            },
            { "agent": "analysis", "task": {"type": "calculate_total_downtime"} },
            { "agent": "synthesis" }
          ]
        }
        """
    },
    {
        "role": "user",
        "content": "Show me all downtime events that were longer than 45 minutes."
    },
    {
        "role": "assistant",
        "content": """
        {
          "user_query": "Show me all downtime events that were longer than 45 minutes.",
          "steps": [
            {
              "agent": "retrieval",
              "task": {
                "type": "metadata_query",
                "filters": { "Downtime Minutes": {"$gt": 45} }
              }
            },
            { "agent": "analysis", "task": {"type": "passthrough"} },
            { "agent": "synthesis" }
          ]
        }
        """
    },
    # --- Category 1: Specific Log Retrieval (Hybrid) ---
    {
        "role": "user",
        "content": "Were there any 'top tool cleaning' events on line MEA204-1 this month?"
    },
    {
        "role": "assistant",
        "content": """
        {
          "user_query": "Were there any 'top tool cleaning' events on line MEA204-1 this month?",
          "steps": [
            {
              "agent": "retrieval",
              "task": {
                "type": "hybrid_query",
                "query_text": "top tool cleaning",
                "filters": {
                  "$and": [
                    {"Line": "MEA204-1"}
                  ],
                  "natural_language_date_start": "December 1, 2025",
                  "natural_language_date_end": "now"
                }
              }
            },
            { "agent": "analysis", "task": {"type": "passthrough"} },
            { "agent": "synthesis" }
          ]
        }
        """
    },
    {
        "role": "user",
        "content": "What lines had network issues this year?"
    },
    {
        "role": "assistant",
        "content": """
        {
          "user_query": "What lines had network issues this year?",
          "steps": [
            {
              "agent": "retrieval",
              "task": {
                "type": "hybrid_query",
                "query_text": "network issues",
                "filters": {
                  "natural_language_date_start": "January 1, 2025",
                  "natural_language_date_end": "now"
                }
              }
            },
            { "agent": "analysis", "task": {"type": "passthrough"} },
            { "agent": "synthesis" }
          ]
        }
        """
    },
    # --- Category 3: Solution & "Fix" Finding (Semantic) ---
    {
        "role": "user",
        "content": "How do I fix an 'iai error'?"
    },
    {
        "role": "assistant",
        "content": """
        {
          "user_query": "How do I fix an 'iai error'?",
          "steps": [
            {
              "agent": "retrieval",
              "task": {
                "type": "known_issue_query",
                "query_text": "solution or fix for iai error"
              }
            },
            { "agent": "analysis", "task": {"type": "passthrough"} },
            {
              "agent": "retrieval",
              "task": {
                "type": "semantic_query",
                "query_text": "iai error"
              }
            },
            { "agent": "analysis", "task": {"type": "passthrough"} },
            { "agent": "synthesis" }
          ]
        }
        """
    },
    # --- Category 2: Trend & Pattern Analysis (Aggregation) ---
    {
        "role": "user",
        "content": "What was the single biggest cause of downtime last month?"
    },
    {
        "role": "assistant",
        "content": """
        {
          "user_query": "What was the single biggest cause of downtime last month?",
          "steps": [
            {
              "agent": "retrieval",
              "task": {
                "type": "metadata_query",
                "filters": {
                  "natural_language_date_start": "November 1, 2025",
                  "natural_language_date_end": "November 30, 2025"
                }
              }
            },
            { "agent": "analysis", "task": {"type": "cluster_and_aggregate"} },
            { "agent": "synthesis" }
          ]
        }
        """
    },
    {
        "role": "user",
        "content": "Which line had the most downtime this quarter?"
    },
    {
        "role": "assistant",
        "content": """
        {
          "user_query": "Which line had the most downtime this quarter?",
          "steps": [
            {
              "agent": "retrieval",
              "task": {
                "type": "metadata_query",
                "filters": {
                  "natural_language_date_start": "3 months ago",
                  "natural_language_date_end": "now"
                }
              }
            },
            { "agent": "analysis", "task": {"type": "aggregate_by_line"} },
            { "agent": "synthesis" }
          ]
        }
        """
    },
    # --- Category 4: General Conversation ---
    {
        "role": "user",
        "content": "Hello, how are you?"
    },
    {
        "role": "assistant",
        "content": """
        {
          "user_query": "Hello, how are you?",
          "steps": [
            { "agent": "synthesis" }
          ]
        }
        """
    },
    {
        "role": "user",
        "content": "Thanks!"
    },
    {
        "role": "assistant",
        "content": """
        {
          "user_query": "Thanks!",
          "steps": [
            { "agent": "synthesis" }
          ]
        }
        """
    }
]

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "user_query": {
            "type": "string",
            "description": "The original query from the user."
        },
        "steps": {
            "type": "array",
            "description": "The list of agent steps to execute.",
            "items": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "The name of the agent to call.",
                        "enum": ["retrieval", "analysis", "synthesis"]
                    },
                    "task": {
                        "type": "object",
                        "description": "The specific JSON task for the agent. This is optional for the synthesis agent."
                    }
                },
                "required": ["agent"]
            }
        }
    },
    "required": ["user_query", "steps"]
}