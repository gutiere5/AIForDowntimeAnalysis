import subprocess
import time
from seed_database import seed_database

def run_and_seed():
    """Starts the FastAPI server and then seeds the database."""
    # Command to run the FastAPI server
    server_command = ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

    # Start the server as a background process
    server_process = subprocess.Popen(server_command)

    # Give the server plenty of time to start up
    print("Starting server...")
    time.sleep(10)
    print("Server started.")

    # Now, seed the database
    print("Seeding database...")
    seed_database()
    print("Database seeded.")

    # Keep the script running to keep the server alive
    print("Server is running. Press Ctrl+C to stop.")
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    run_and_seed()
