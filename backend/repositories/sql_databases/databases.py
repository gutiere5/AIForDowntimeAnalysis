import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.path.join(os.path.dirname(__file__), 'conversations.db')

def get_db_connection():
    logger.info(f"Database connection established. {DATABASE_URL}")

    """Creates and returns a new database connection."""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    logger.info("Attempting to initialize the database...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                rating TEXT,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON messages (conversation_id, timestamp);
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_session_id ON conversations (session_id);
            CREATE TABLE IF NOT EXISTS known_issues (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                solution TEXT NOT NULL,
                author TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logger.info("Database schema initialized/verified successfully.")

        conn.commit()
        conn.close()
        logger.info("Database initialization complete.")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == '__main__':
    # This allows manual initialization by running `python -m backend.database`
    initialize_database()
