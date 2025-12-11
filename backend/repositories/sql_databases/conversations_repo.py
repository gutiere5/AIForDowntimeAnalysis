import logging
import uuid
from backend.repositories.sql_databases.databases import get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_message(conversation_id: str, session_id: str, role: str, content: str):
    logger.info(f"Adding message for conversation {conversation_id}. Role: {role}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM conversations WHERE id = ?", (conversation_id,))
        conversation_exists = cursor.fetchone() is not None

        if not conversation_exists and role == 'user':
            title = content if len(content) <= 100 else content[:97] + "..."
            cursor.execute(
                "INSERT INTO conversations (id, session_id, title) VALUES (?, ?, ?)",
                (conversation_id, session_id, title)
            )
            logger.info(f"Created new conversation entry for {conversation_id} with title '{title}'.")

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
    logger.info(f"Retrieving messages for conversation {conversation_id} and session {session_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        

        cursor.execute(
            "SELECT 1 FROM messages WHERE conversation_id = ? AND session_id = ? LIMIT 1",
            (conversation_id, session_id)
        )
        

        cursor.execute("SELECT 1 FROM messages WHERE conversation_id = ? LIMIT 1", (conversation_id,))
        conversation_exists = cursor.fetchone() is not None

        if not conversation_exists:
            logger.info(f"No history found for new conversation_id: {conversation_id}")
            return []

        cursor.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? AND session_id = ? ORDER BY timestamp ASC",
            (conversation_id, session_id)
        )
        
        messages = cursor.fetchall()
        conn.close()
        
        if not messages and conversation_exists:
            logger.warning(f"Access denied for session {session_id} to conversation {conversation_id}.")
            return []

        logger.info(f"Successfully retrieved {len(messages)} messages for conversation {conversation_id}.")
        return [dict(row) for row in messages]

    except Exception as e:
        logger.error(f"Failed to retrieve messages for conversation {conversation_id}: {e}")
        raise


def get_conversations_by_session_id(session_id: str) -> list[dict]:
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
    logger.info(f"Deleting conversation {conversation_id} for session {session_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM conversations WHERE id = ? AND session_id = ?",
            (conversation_id, session_id)
        )
        if cursor.fetchone() is None:
            logger.warning(f"Unauthorized attempt to delete conversation {conversation_id} by session {session_id}")
            raise Exception("Conversation not found or access denied.")

        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))

        conn.commit()
        conn.close()
        logger.info(f"Successfully deleted conversation {conversation_id}.")
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        raise

def delete_all_conversations(session_id: str):
    logger.info(f"Deleting all conversations for session {session_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM conversations WHERE session_id = ?", (session_id,))
        conversation_ids = [row[0] for row in cursor.fetchall()]

        if not conversation_ids:
            logger.info(f"No conversations found for session {session_id}.")
            conn.close()
            return

        cursor.execute("DELETE FROM messages WHERE conversation_id IN ({})".format(
            ', '.join('?' for _ in conversation_ids)),
            conversation_ids
        )

        cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))

        conn.commit()
        conn.close()
        logger.info(f"Successfully deleted all conversations for session {session_id}.")
    except Exception as e:
        logger.error(f"Failed to delete all conversations for session {session_id}: {e}")
        raise

def update_conversation_title(conversation_id: str, session_id: str, new_title: str):
    logger.info(f"Updating title for conversation {conversation_id} to '{new_title}'")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

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


