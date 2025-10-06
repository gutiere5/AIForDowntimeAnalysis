from backend.agents import query_database
query_database_tool = {
    "type": "function",
    "function": {
        "name": "query_database",
        "description": """Execute a SQL SELECT query and return the results.
                       Only SELECT queries are allowed for security reasons.
                       Returns data in JSON format.""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": """The SQL SELECT query to execute.
                                    Must start with SELECT and should not
                                    contain any data modification commands."""
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
}