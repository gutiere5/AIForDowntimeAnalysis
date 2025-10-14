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
    """
    Executes a read-only SQL query against a mock database and returns the results as a dictionary.
    Only SELECT statements are allowed.

    Available mock tables for querying:
    - 'downtime': Contains manufacturing downtime data with the following columns:
        - id (INTEGER)
        - timestamp (TEXT)
        - machine_id (TEXT)
        - reason_code (TEXT)
        - duration_minutes (INTEGER)
      Use this table to find trends related to specific machines, times of day, or escalating issues.
    """
    # Validation: Only allow SELECT statements
    if not query.strip().lower().startswith("select"):
        return {"error": "Only SELECT statements are allowed."}

    try:
        query_lower = query.lower()

        # --- Downtime Data with Built-in Trends ---
        if "downtime" in query_lower:
            downtime_data = [
                {'id': 1, 'timestamp': '2025-09-22 09:15:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 25},
                {'id': 2, 'timestamp': '2025-09-22 14:30:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 45},
                {'id': 3, 'timestamp': '2025-09-23 10:05:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 30},
                {'id': 4, 'timestamp': '2025-09-23 11:20:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 60},
                {'id': 5, 'timestamp': '2025-09-24 16:00:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 35},
                {'id': 6, 'timestamp': '2025-09-25 08:30:00', 'machine_id': 'M3', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 20},
                {'id': 7, 'timestamp': '2025-09-26 13:00:00', 'machine_id': 'M2', 'reason_code': 'OPERATOR_ERROR',
                 'duration_minutes': 10},
                {'id': 8, 'timestamp': '2025-09-29 09:45:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 28},
                {'id': 9, 'timestamp': '2025-09-29 15:00:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 55},
                {'id': 10, 'timestamp': '2025-09-30 11:00:00', 'machine_id': 'M1', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 75},
                {'id': 11, 'timestamp': '2025-10-01 03:30:00', 'machine_id': 'M2', 'reason_code': 'POWER_FAIL',
                 'duration_minutes': 240},
                {'id': 12, 'timestamp': '2025-10-01 13:10:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 40},
                {'id': 13, 'timestamp': '2025-10-02 08:55:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 35},
                {'id': 14, 'timestamp': '2025-10-02 14:20:00', 'machine_id': 'M3', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 80},
                {'id': 15, 'timestamp': '2025-10-03 10:15:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 15},
                {'id': 16, 'timestamp': '2025-10-04 11:00:00', 'machine_id': 'M1', 'reason_code': 'OPERATOR_ERROR',
                 'duration_minutes': 12},
                {'id': 17, 'timestamp': '2025-10-06 09:10:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 32},
                {'id': 18, 'timestamp': '2025-10-06 13:45:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 50},
                {'id': 19, 'timestamp': '2025-10-07 10:50:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 95},
                {'id': 20, 'timestamp': '2025-10-08 16:20:00', 'machine_id': 'M3', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 110},
                {'id': 21, 'timestamp': '2025-10-09 08:40:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 40},
                {'id': 22, 'timestamp': '2025-10-10 17:00:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 48},
            ]
            return {"results": downtime_data}
    except Exception as e:
        return {"error": str(e)}