import logging
import sqlite3
import uuid
from repositories.sql_databases.databases import get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_issue(title, description, solution, author):
    logger.info(f"Creating issue for {title}, {description}, {solution}, {author}")
    issue_id = str(uuid.uuid4())
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO known_issues (id, title, description, solution, author) VALUES (?, ?, ?, ?, ?)",
            (issue_id, title, description, solution, author)
        )

        conn.commit()
        logger.info(f"Successfully created issue with id {issue_id} for {title}, {description}, {solution}, {author}")
        return issue_id

    except Exception as e:
        logger.error(f"Error inserting issue: {e}")
        conn.rollback()
        return None 
    finally:
        if conn:
            conn.close()

def get_issue_by_id(issue_id):
    logger.info(f"Getting known issue by id: {issue_id}")
    conn = None
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM known_issues WHERE id = ?", (issue_id,) )
        
        issue_row = cursor.fetchone()
        if issue_row:
            logger.info(f"Successfully retrieved known issue by id: {issue_id}")
            return dict(issue_row)

        else:
            return None
    except Exception as e:
        logger.error(f"Error getting known issue by id: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_issues():
    logger.info(f"Getting all known issues")
    conn = None
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM known_issues")

        issue_rows = cursor.fetchall()
        if issue_rows:
            logger.info(f"Successfully retrieved all known issues")
            return [dict(row) for row in issue_rows]
        else:
            return []
    except Exception as e:
        logger.error(f"Error getting all known issues: {e}")
        return []
    finally:
        if conn:
            conn.close()


def update_issue(issue_id, title, description, solution, author):
    logger.info(f"Updating known issue by id: {issue_id} with new {title}, {description}, {solution}, {author}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE known_issues 
            SET title = ?, description = ?, solution = ?, author = ?
            WHERE id = ?
            """,
            (title, description, solution, author, issue_id)
        )
        conn.commit()

        if cursor.rowcount > 0:
            logger.info(f"Successfully updated known issue by id: {issue_id}")
            return issue_id
        else:
            logger.info(f"No known issue found for id: {issue_id}")
            return None
    except Exception as e:
        logger.error(f"Error updating issue: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def delete_issue(issue_id):
    logger.info(f"Deleting known issue by id: {issue_id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM known_issues WHERE id = ?", (issue_id,))

        conn.commit()

        if cursor.rowcount > 0:
            logger.info(f"Successfully deleted known issue by id: {issue_id}")
            return issue_id
        else:
            logger.info(f"No known issue found for id: {issue_id}")
            return None
    except Exception as e:
        logger.error(f"Error deleting issue: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()