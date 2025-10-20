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


def query_database(query: str):
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
                # Week 1 (baseline)
                {'id': 1, 'timestamp': '2025-09-22 09:15:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 25},
                {'id': 2, 'timestamp': '2025-09-22 14:30:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 40},
                {'id': 3, 'timestamp': '2025-09-23 11:05:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 35},
                {'id': 4, 'timestamp': '2025-09-23 15:10:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 55},
                {'id': 5, 'timestamp': '2025-09-24 13:55:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 45},
                {'id': 6, 'timestamp': '2025-09-25 08:40:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 28},
                {'id': 7, 'timestamp': '2025-09-25 14:20:00', 'machine_id': 'M3', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 50},
                {'id': 8, 'timestamp': '2025-09-26 12:55:00', 'machine_id': 'M2', 'reason_code': 'OPERATOR_ERROR',
                 'duration_minutes': 12},
                {'id': 9, 'timestamp': '2025-09-26 16:05:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 48},
                {'id': 10, 'timestamp': '2025-09-27 10:30:00', 'machine_id': 'M1', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 60},

                # Week 2 (escalation begins)
                {'id': 11, 'timestamp': '2025-09-29 09:05:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 30},
                {'id': 12, 'timestamp': '2025-09-29 13:35:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 52},
                {'id': 13, 'timestamp': '2025-09-30 10:50:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 38},
                {'id': 14, 'timestamp': '2025-09-30 14:55:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 60},
                {'id': 15, 'timestamp': '2025-10-01 03:30:00', 'machine_id': 'M2', 'reason_code': 'POWER_FAIL',
                 'duration_minutes': 240},
                {'id': 16, 'timestamp': '2025-10-01 13:25:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 55},
                {'id': 17, 'timestamp': '2025-10-02 08:50:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 32},
                {'id': 18, 'timestamp': '2025-10-02 14:10:00', 'machine_id': 'M3', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 55},
                {'id': 19, 'timestamp': '2025-10-03 10:05:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 40},
                {'id': 20, 'timestamp': '2025-10-03 15:05:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 65},
                {'id': 21, 'timestamp': '2025-10-04 11:10:00', 'machine_id': 'M1', 'reason_code': 'OPERATOR_ERROR',
                 'duration_minutes': 15},

                # Week 3 (increasing frequency M3 + longer jams M1)
                {'id': 22, 'timestamp': '2025-10-06 09:00:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 35},
                {'id': 23, 'timestamp': '2025-10-06 13:45:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 58},
                {'id': 24, 'timestamp': '2025-10-06 16:20:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 60},
                {'id': 25, 'timestamp': '2025-10-07 10:40:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 42},
                {'id': 26, 'timestamp': '2025-10-07 14:50:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 70},
                {'id': 27, 'timestamp': '2025-10-08 08:55:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 37},
                {'id': 28, 'timestamp': '2025-10-08 13:15:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 34},
                {'id': 29, 'timestamp': '2025-10-08 16:25:00', 'machine_id': 'M3', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 60},
                {'id': 30, 'timestamp': '2025-10-09 13:05:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 62},
                {'id': 31, 'timestamp': '2025-10-09 17:15:00', 'machine_id': 'M2', 'reason_code': 'OPERATOR_ERROR',
                 'duration_minutes': 18},
                {'id': 32, 'timestamp': '2025-10-10 09:10:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 38},
                {'id': 33, 'timestamp': '2025-10-10 14:55:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 65},

                # Week 4 (accelerating problems)
                {'id': 34, 'timestamp': '2025-10-13 08:50:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 40},
                {'id': 35, 'timestamp': '2025-10-13 11:35:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 39},
                {'id': 36, 'timestamp': '2025-10-13 13:40:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 68},
                {'id': 37, 'timestamp': '2025-10-14 10:35:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 45},
                {'id': 38, 'timestamp': '2025-10-14 14:45:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 78},
                {'id': 39, 'timestamp': '2025-10-15 08:55:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 41},
                {'id': 40, 'timestamp': '2025-10-15 13:05:00', 'machine_id': 'M3', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 65},
                {'id': 41, 'timestamp': '2025-10-15 15:25:00', 'machine_id': 'M2', 'reason_code': 'OPERATOR_ERROR',
                 'duration_minutes': 16},
                {'id': 42, 'timestamp': '2025-10-16 09:05:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 42},
                {'id': 43, 'timestamp': '2025-10-16 13:25:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 70},
                {'id': 44, 'timestamp': '2025-10-17 09:15:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 43},
                {'id': 45, 'timestamp': '2025-10-17 14:15:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 72},

                # Week 5 (notable surge)
                {'id': 46, 'timestamp': '2025-10-20 08:45:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 45},
                {'id': 47, 'timestamp': '2025-10-20 10:55:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 44},
                {'id': 48, 'timestamp': '2025-10-20 13:50:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 75},
                {'id': 49, 'timestamp': '2025-10-21 10:30:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 47},
                {'id': 50, 'timestamp': '2025-10-21 14:40:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 82},
                {'id': 51, 'timestamp': '2025-10-22 09:00:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 46},
                {'id': 52, 'timestamp': '2025-10-22 11:55:00', 'machine_id': 'M3', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 70},
                {'id': 53, 'timestamp': '2025-10-22 13:15:00', 'machine_id': 'M1', 'reason_code': 'OPERATOR_ERROR',
                 'duration_minutes': 20},
                {'id': 54, 'timestamp': '2025-10-23 08:50:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 47},
                {'id': 55, 'timestamp': '2025-10-23 13:30:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 78},
                {'id': 56, 'timestamp': '2025-10-24 09:10:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 48},
                {'id': 57, 'timestamp': '2025-10-24 14:05:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 80},

                # Week 6 (compounded issues)
                {'id': 58, 'timestamp': '2025-10-27 08:40:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 50},
                {'id': 59, 'timestamp': '2025-10-27 10:35:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 49},
                {'id': 60, 'timestamp': '2025-10-27 13:40:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 83},
                {'id': 61, 'timestamp': '2025-10-28 10:25:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 50},
                {'id': 62, 'timestamp': '2025-10-28 15:00:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 88},
                {'id': 63, 'timestamp': '2025-10-29 08:55:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 51},
                {'id': 64, 'timestamp': '2025-10-29 11:45:00', 'machine_id': 'M3', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 75},
                {'id': 65, 'timestamp': '2025-10-30 09:05:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 52},
                {'id': 66, 'timestamp': '2025-10-30 13:35:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 85},
                {'id': 67, 'timestamp': '2025-10-31 09:15:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 53},
                {'id': 68, 'timestamp': '2025-10-31 14:00:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 87},
                {'id': 69, 'timestamp': '2025-10-31 16:20:00', 'machine_id': 'M2', 'reason_code': 'POWER_FAIL',
                 'duration_minutes': 200},

                # Week 7 (stabilization attempt with lingering high values)
                {'id': 70, 'timestamp': '2025-11-03 09:00:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 54},
                {'id': 71, 'timestamp': '2025-11-03 11:20:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 52},
                {'id': 72, 'timestamp': '2025-11-03 13:50:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 88},
                {'id': 73, 'timestamp': '2025-11-04 10:20:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW',
                 'duration_minutes': 48},
                {'id': 74, 'timestamp': '2025-11-04 14:30:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 85},
                {'id': 75, 'timestamp': '2025-11-05 09:10:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 55},
                {'id': 76, 'timestamp': '2025-11-05 11:55:00', 'machine_id': 'M3', 'reason_code': 'OVERHEAT',
                 'duration_minutes': 78},
                {'id': 77, 'timestamp': '2025-11-06 09:05:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 54},
                {'id': 78, 'timestamp': '2025-11-06 13:30:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 89},
                {'id': 79, 'timestamp': '2025-11-07 09:15:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL',
                 'duration_minutes': 55},
                {'id': 80, 'timestamp': '2025-11-07 14:05:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM',
                 'duration_minutes': 90},
            ]
            return {"results": downtime_data}
    except Exception as e:
        return {"error": str(e)}