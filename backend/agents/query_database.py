import sqlite3
import pandas as pd
import re

# def query_database(query: str) -> dict:
#     # Validation: Only allow SELECT statements
#     if not query.strip().lower().startswith("select"):
#         return {"error": "Only SELECT statements are allowed."}
#     try:
#         conn = sqlite3.connect("your_database.db")
#         df = pd.read_sql_query(query, conn)
#         conn.close()
#         # Convert DataFrame to JSON
#         return {"results": df.to_dict(orient="records")}
#     except Exception as e:
#         return {"error": str(e)}


def query_database(query: str) -> dict:
    # Validation: Only allow SELECT statements
    if not query.strip().lower().startswith("select"):
        return {"error": "Only SELECT statements are allowed."}

    try:
        # Parse the query to determine what kind of mock data to return
        query_lower = query.lower()

        # Check if the query contains specific tables or patterns
        if "users" in query_lower:
            return {
                "results": [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
                ]
            }
        elif "products" in query_lower:
            return {
                "results": [
                    {"id": 101, "name": "Laptop", "price": 999.99, "stock": 45},
                    {"id": 102, "name": "Smartphone", "price": 699.99, "stock": 120},
                    {"id": 103, "name": "Headphones", "price": 149.99, "stock": 78}
                ]
            }
        elif "count" in query_lower:
            # Extract the count target using regex
            match = re.search(r"count\(\*\)\s+from\s+(\w+)", query_lower)
            if match:
                table = match.group(1)
                return {"results": [{"count": 42, "table": table}]}
            else:
                return {"results": [{"count": 10}]}
        else:
            # Default generic response
            return {
                "results": [
                    {"column1": "value1", "column2": "value2", "column3": 123},
                    {"column1": "value4", "column2": "value5", "column3": 456}
                ]
            }
    except Exception as e:
        return {"error": str(e)}