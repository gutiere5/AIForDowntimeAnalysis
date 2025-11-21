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
    """Initializes the database by creating tables and indexes if they don't exist."""
    logger.info("Attempting to initialize the database...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create the messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Successfully verified 'messages' table exists.")

        # Create a composite index for efficient message retrieval
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON messages (conversation_id, timestamp)
        """)
        logger.info("Successfully verified 'idx_conversation_timestamp' index exists.")

        # Create the conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Successfully verified 'conversations' table exists.")

        # Create an index for retrieving conversations by session
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id ON conversations (session_id)
        """)
        logger.info("Successfully verified 'idx_session_id' index exists.")

        conn.commit()
        conn.close()
        logger.info("Database initialization complete.")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == '__main__':
    # This allows manual initialization by running `python -m backend.database`
    initialize_database()
