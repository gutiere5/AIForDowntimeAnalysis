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

analyze_trend_tool = {
    "type": "function",
    "function": {
        "name": "analyze_trend",
        "description": """Analyze data for statistical trends using linear regression.
                       Determines if there is a statistically significant trend in the data.""",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "description": "Array of data objects to analyze",
                    "items": {
                        "type": "object"
                    }
                },
                "value_column": {
                    "type": "string",
                    "description": "The name of the column containing values to analyze for trends"
                },
                "time_column": {
                    "type": "string",
                    "description": "Optional: The name of the column containing time/sequence information",
                    "default": None
                }
            },
            "required": ["data", "value_column"],
            "additionalProperties": False
        }
    }
}