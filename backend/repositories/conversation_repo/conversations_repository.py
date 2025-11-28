import logging
import uuid

from backend.repositories.conversation_repo.database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_message(conversation_id: str, session_id: str, role: str, content: str):
    """Adds a new message and ensures a conversation entry exists."""
    logger.info(f"Adding message for conversation {conversation_id}. Role: {role}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if a conversation entry already exists
        cursor.execute("SELECT 1 FROM conversations WHERE id = ?", (conversation_id,))
        conversation_exists = cursor.fetchone() is not None

        # If it's the first user message, create the conversation entry
        if not conversation_exists and role == 'user':
            # Use the first user message as the title, truncating if necessary
            title = content if len(content) <= 100 else content[:97] + "..."
            cursor.execute(
                "INSERT INTO conversations (id, session_id, title) VALUES (?, ?, ?)",
                (conversation_id, session_id, title)
            )
            logger.info(f"Created new conversation entry for {conversation_id} with title '{title}'.")

        # Insert the message
        cursor.execute(
            "INSERT INTO messages (conversation_id, session_id, role, content) VALUES (?, ?, ?, ?)",
            (conversation_id, session_id, role, content)
        )

        conn.commit()
        conn.close()
        logger.info(f"Successfully added message for conversation {conversation_id}.")
    except Exception as e:
        logger.error(f"Failed to add message for conversation {conversation_id}: {e}")
        raise


def create_conversation(session_id: str, title: str) -> dict:
    """Creates a new conversation entry and returns it."""
    conversation_id = str(uuid.uuid4())
    logger.info(f"Creating new conversation for session {session_id} with conversation ID '{conversation_id}' and title '{title}'.")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (id, session_id, title) VALUES (?, ?, ?)",
            (conversation_id, session_id, title)
        )
        conn.commit()
        conn.close()
        logger.info(f"Successfully created new conversation {conversation_id}.")
        return {"conversation_id": conversation_id, "title": title}
    except Exception as e:
        logger.error(f"Failed to create new conversation for session {session_id}: {e}")
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


def get_conversations_by_session_id(session_id: str) -> list[dict]:
    """Retrieves all conversations for a given session from the 'conversations' table."""
    logger.info(f"Retrieving all conversations for session {session_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id as conversation_id, title FROM conversations WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,)
        )

        conversations = cursor.fetchall()
        conn.close()

        logger.info(f"Successfully retrieved {len(conversations)} conversations for session {session_id}.")
        return [dict(row) for row in conversations]

    except Exception as e:
        logger.error(f"Failed to retrieve conversations for session {session_id}: {e}")
        raise


def delete_conversation(conversation_id: str, session_id: str):
    """Deletes a conversation and all its associated messages."""
    logger.info(f"Deleting conversation {conversation_id} for session {session_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the conversation belongs to the session (for security)
        cursor.execute(
            "SELECT 1 FROM conversations WHERE id = ? AND session_id = ?",
            (conversation_id, session_id)
        )
        if cursor.fetchone() is None:
            logger.warning(f"Unauthorized attempt to delete conversation {conversation_id} by session {session_id}")
            raise Exception("Conversation not found or access denied.")

        # Delete from conversations table
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

        # Delete from messages table
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))

        conn.commit()
        conn.close()
        logger.info(f"Successfully deleted conversation {conversation_id}.")
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        raise


def update_conversation_title(conversation_id: str, session_id: str, new_title: str):
    """Updates the title of a specific conversation."""
    logger.info(f"Updating title for conversation {conversation_id} to '{new_title}'")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the conversation belongs to the session (for security)
        cursor.execute(
            "SELECT 1 FROM conversations WHERE id = ? AND session_id = ?",
            (conversation_id, session_id)
        )
        if cursor.fetchone() is None:
            logger.warning(f"Unauthorized attempt to update conversation {conversation_id} by session {session_id}")
            raise Exception("Conversation not found or access denied.")

        cursor.execute(
            "UPDATE conversations SET title = ? WHERE id = ?",
            (new_title, conversation_id)
        )
        conn.commit()
        conn.close()
        logger.info(f"Successfully updated title for conversation {conversation_id}.")
    except Exception as e:
        logger.error(f"Failed to update title for conversation {conversation_id}: {e}")
        raise
