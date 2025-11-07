
import logging
from backend.database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_message(conversation_id: str, session_id: str, role: str, content: str):
    """Adds a new message to the database for a given conversation."""
    logger.info(f"Adding message for conversation {conversation_id}. Role: {role}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (conversation_id, session_id, role, content) VALUES (?, ?, ?, ?)",
            (conversation_id, session_id, role, content)
        )
        conn.commit()
        conn.close()
        logger.info(f"Successfully added message for conversation {conversation_id}.")
    except Exception as e:
        logger.error(f"Failed to add message for conversation {conversation_id}: {e}")
        # Depending on the application's needs, you might want to handle this more gracefully
        raise

def get_messages_by_conversation_id(conversation_id: str, session_id: str) -> list[dict]:
    """Retrieves all messages for a conversation, ensuring the session_id matches."""
    logger.info(f"Retrieving messages for conversation {conversation_id} and session {session_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # The WHERE clause enforces our security rule: the session_id must match.
        # We select 1 to check for existence.
        cursor.execute(
            "SELECT 1 FROM messages WHERE conversation_id = ? AND session_id = ? LIMIT 1",
            (conversation_id, session_id)
        )
        
        # If the conversation exists but belongs to another session, this will fetch nothing.
        # We need to handle the case where the conversation is new vs. accessed by the wrong session.
        # A simple approach is to check if *any* messages exist for this conversation_id first.
        cursor.execute("SELECT 1 FROM messages WHERE conversation_id = ? LIMIT 1", (conversation_id,))
        conversation_exists = cursor.fetchone() is not None

        if not conversation_exists:
            logger.info(f"No history found for new conversation_id: {conversation_id}")
            return [] # It's a new conversation, return an empty list.

        # Now, fetch the messages only if the session ID is correct.
        cursor.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? AND session_id = ? ORDER BY timestamp ASC",
            (conversation_id, session_id)
        )
        
        messages = cursor.fetchall()
        conn.close()
        
        if not messages and conversation_exists:
            # This case means the conversation ID is valid, but it belongs to another session.
            logger.warning(f"Access denied for session {session_id} to conversation {conversation_id}.")
            return [] # Return empty list to enforce security boundary

        logger.info(f"Successfully retrieved {len(messages)} messages for conversation {conversation_id}.")
        return [dict(row) for row in messages]

    except Exception as e:
        logger.error(f"Failed to retrieve messages for conversation {conversation_id}: {e}")
        raise
