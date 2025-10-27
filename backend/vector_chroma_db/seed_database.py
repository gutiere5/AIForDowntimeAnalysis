import requests
import json
import time

# URL of the running FastAPI application
BASE_URL = "http://localhost:8000"

# Endpoint for indexing log entries
INDEX_ENDPOINT = f"{BASE_URL}/index_log"

# Path to the sample logs file
LOGS_FILE = "sample_logs.json"

def seed_database():
    """Reads sample logs and sends them to the /index_log endpoint."""
    time.sleep(5) # Wait for the server to start
    try:
        with open(LOGS_FILE, "r") as file:
            logs = json.load(file)
    except FileNotFoundError:
        print(f"Error: {LOGS_FILE} not found.")
        return

    for log in logs:
        try:
            response = requests.post(INDEX_ENDPOINT, json=log)
            response.raise_for_status()  # Raise an exception for bad status codes
            print(f"Successfully indexed log: {log['id']}")
        except requests.exceptions.RequestException as e:
            print(f"Error indexing log {log['id']}: {e}")

if __name__ == "__main__":
    seed_database()
