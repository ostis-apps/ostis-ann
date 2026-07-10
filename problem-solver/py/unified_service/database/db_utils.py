"""
SQLite database utilities
"""
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from config import settings
from utils.exceptions import DatabaseException

logger = logging.getLogger(__name__)


def _ensure_column_exists(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    """Ensure column exists in table, add if missing."""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    columns = {row["name"] for row in cursor.fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        conn.commit()
        logger.info("Added missing column %s.%s", table, column)


def get_db_connection() -> sqlite3.Connection:
    """Get database connection"""
    try:
        conn = sqlite3.connect(settings.sqlite_db_name)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise DatabaseException(f"Failed to connect to database: {str(e)}")


def init_database() -> None:
    """Initialize database tables"""
    logger.info("Initializing database...")
    
    conn = get_db_connection()
    try:
        # Chat logs table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_query TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Document store table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS document_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Model creation table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_model_architectures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                architecture JSON NOT NULL,
                generated_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );''')
        
        # Session state table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS session_state (
                session_id TEXT PRIMARY KEY,
                category TEXT,
                original_query TEXT,
                collected_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Ensure optional columns exist (idempotent)
        _ensure_column_exists(conn, "chat_logs", "agent_meta", "TEXT")
        _ensure_column_exists(conn, "session_state", "title", "TEXT")
        _ensure_column_exists(conn, "session_state", "is_active", "INTEGER DEFAULT 1")
        _ensure_column_exists(conn, "session_state", "chat_mode", "TEXT DEFAULT 'auto'")
        
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise DatabaseException(f"Failed to initialize database: {str(e)}")
    finally:
        conn.close()


def insert_chat_log(
    session_id: str,
    user_query: str,
    agent_response: str,
    category: Optional[str] = None,
    agent_meta: Optional[Dict[str, Any]] = None
) -> None:
    """Insert chat log entry"""
    conn = get_db_connection()
    try:
        meta_json = json.dumps(agent_meta, ensure_ascii=False) if agent_meta else None
        conn.execute(
            '''INSERT INTO chat_logs (session_id, user_query, agent_response, category, agent_meta)
               VALUES (?, ?, ?, ?, ?)''',
            (session_id, user_query, agent_response, category, meta_json)
        )
        conn.commit()
        logger.debug(f"Inserted chat log for session {session_id}")
    except Exception as e:
        logger.error(f"Error inserting chat log: {e}")
        raise DatabaseException(f"Failed to insert chat log: {str(e)}")
    finally:
        conn.close()


def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    """Get chat history for a session"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT user_query, agent_response FROM chat_logs
               WHERE session_id = ?
               ORDER BY created_at''',
            (session_id,)
        )
        
        messages = []
        for row in cursor.fetchall():
            messages.extend([
                {"role": "human", "content": row['user_query']},
                {"role": "ai", "content": row['agent_response']}
            ])
        
        logger.debug(f"Retrieved {len(messages)} messages for session {session_id}")
        return messages
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise DatabaseException(f"Failed to get chat history: {str(e)}")
    finally:
        conn.close()


def insert_document_record(filename: str) -> int:
    """Insert document record and return file_id"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO document_store (filename) VALUES (?)',
            (filename,)
        )
        file_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Inserted document record: {filename} with id {file_id}")
        return file_id
    except Exception as e:
        logger.error(f"Error inserting document record: {e}")
        raise DatabaseException(f"Failed to insert document record: {str(e)}")
    finally:
        conn.close()


def delete_document_record(file_id: int) -> bool:
    """Delete document record"""
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM document_store WHERE id = ?', (file_id,))
        conn.commit()
        logger.info(f"Deleted document record with id {file_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting document record: {e}")
        raise DatabaseException(f"Failed to delete document record: {str(e)}")
    finally:
        conn.close()


def get_all_documents() -> List[Dict[str, Any]]:
    """Get all documents"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, filename, upload_timestamp FROM document_store
               ORDER BY upload_timestamp DESC'''
        )
        documents = cursor.fetchall()
        return [dict(doc) for doc in documents]
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise DatabaseException(f"Failed to get documents: {str(e)}")
    finally:
        conn.close()


def get_document_by_filename(filename: str) -> Optional[Dict[str, Any]]:
    """Return document metadata by filename"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, filename, upload_timestamp FROM document_store WHERE filename = ?''',
            (filename,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error("Error fetching document by filename: %s", e, exc_info=True)
        raise DatabaseException(f"Failed to get document: {str(e)}")
    finally:
        conn.close()


def create_session(
    session_id: str,
    category: Optional[str] = None,
    original_query: Optional[str] = None,
    collected_data: Optional[str] = None,
    title: Optional[str] = None,
    chat_mode: Optional[str] = None,
    is_active: bool = True
) -> None:
    """Create or update session metadata"""
    conn = get_db_connection()
    try:
        conn.execute(
            '''
            INSERT INTO session_state (session_id, category, original_query, collected_data, title, chat_mode, is_active, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(session_id) DO UPDATE SET
                category = COALESCE(excluded.category, session_state.category),
                collected_data = COALESCE(excluded.collected_data, session_state.collected_data),
                title = COALESCE(excluded.title, session_state.title),
                chat_mode = COALESCE(excluded.chat_mode, session_state.chat_mode),
                is_active = excluded.is_active,
                original_query = COALESCE(session_state.original_query, excluded.original_query),
                updated_at = CURRENT_TIMESTAMP
            ''',
            (session_id, category, original_query, collected_data, title, chat_mode or 'auto', 1 if is_active else 0)
        )
        conn.commit()
        logger.debug("Upserted session state for %s", session_id)
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise DatabaseException(f"Failed to create session: {str(e)}")
    finally:
        conn.close()


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session state"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM session_state WHERE session_id = ?',
            (session_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise DatabaseException(f"Failed to get session: {str(e)}")
    finally:
        conn.close()


def _get_last_message(conn: sqlite3.Connection, session_id: str) -> Optional[str]:
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT agent_response
        FROM chat_logs
        WHERE session_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        ''',
        (session_id,)
    )
    row = cursor.fetchone()
    if row and row["agent_response"]:
        return row["agent_response"]
    cursor.execute(
        '''
        SELECT user_query
        FROM chat_logs
        WHERE session_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        ''',
        (session_id,)
    )
    row = cursor.fetchone()
    return row["user_query"] if row else None


def delete_session(session_id: str) -> bool:
    """Delete session and all its chat logs"""
    conn = get_db_connection()
    try:
        # Delete chat logs first (foreign key constraint)
        conn.execute('DELETE FROM chat_logs WHERE session_id = ?', (session_id,))
        # Delete session state
        conn.execute('DELETE FROM session_state WHERE session_id = ?', (session_id,))
        conn.commit()
        logger.info(f"Deleted session {session_id} and all its messages")
        return True
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise DatabaseException(f"Failed to delete session: {str(e)}")
    finally:
        conn.close()


def list_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    """List recent dialog sessions"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT session_id, title, category, original_query, collected_data,
                   chat_mode, created_at, updated_at
            FROM session_state
            WHERE IFNULL(is_active, 1) = 1
            ORDER BY updated_at DESC
            LIMIT ?
            ''',
            (limit,)
        )
        sessions = []
        for row in cursor.fetchall():
            entry = dict(row)
            entry["last_message"] = _get_last_message(conn, entry["session_id"])
            sessions.append(entry)
        return sessions
    except Exception as e:
        logger.error("Error listing sessions: %s", e, exc_info=True)
        raise DatabaseException(f"Failed to list sessions: {str(e)}")
    finally:
        conn.close()


def get_structured_chat_history(session_id: str) -> List[Dict[str, Any]]:
    """Return chat history with role separation"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT id, user_query, agent_response, category, agent_meta, created_at
            FROM chat_logs
            WHERE session_id = ?
            ORDER BY created_at
            ''',
            (session_id,)
        )
        messages: List[Dict[str, Any]] = []
        for row in cursor.fetchall():
            created_at = row["created_at"]
            meta = json.loads(row["agent_meta"]) if row["agent_meta"] else None
            messages.append({
                "id": f"{row['id']}-user",
                "role": "user",
                "content": row["user_query"],
                "timestamp": created_at
            })
            messages.append({
                "id": f"{row['id']}-assistant",
                "role": "assistant",
                "content": row["agent_response"],
                "timestamp": created_at,
                "category": row["category"],
                "meta": meta
            })
        return messages
    except Exception as e:
        logger.error("Error getting structured chat history: %s", e, exc_info=True)
        raise DatabaseException(f"Failed to get chat history: {str(e)}")
    finally:
        conn.close()


def update_session(
    session_id: str,
    category: Optional[str] = None,
    collected_data: Optional[str] = None,
    title: Optional[str] = None,
    is_active: Optional[bool] = None
) -> None:
    """Update session state"""
    conn = get_db_connection()
    try:
        updates = []
        params = []
        
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        
        if collected_data is not None:
            updates.append("collected_data = ?")
            params.append(collected_data)
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(session_id)
        
        query = f"UPDATE session_state SET {', '.join(updates)} WHERE session_id = ?"
        conn.execute(query, params)
        conn.commit()
        logger.debug(f"Updated session state for {session_id}")
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        raise DatabaseException(f"Failed to update session: {str(e)}")
    finally:
        conn.close()


def delete_old_sessions(hours: int = 24) -> int:
    """Delete old sessions"""
    conn = get_db_connection()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM session_state WHERE updated_at < ?',
            (cutoff,)
        )
        deleted_count = cursor.rowcount
        conn.commit()
        logger.info(f"Deleted {deleted_count} old sessions")
        return deleted_count
    except Exception as e:
        logger.error(f"Error deleting old sessions: {e}")
        raise DatabaseException(f"Failed to delete old sessions: {str(e)}")
    finally:
        conn.close()

def save_user_model_architecture(user_id: str, model_name: str, architecture: dict, generated_code: str = None):
    """Save a model architecture for a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_model_architectures (user_id, model_name, architecture, generated_code)
        VALUES (?, ?, ?, ?)
    """, (user_id, model_name, json.dumps(architecture), generated_code))
    conn.commit()
    conn.close()

def get_user_model_architectures(user_id: str):
    """Get all model architectures for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_model_architectures WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_model_architecture(user_id: str, model_id: int):
    """Get a specific model architecture for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_model_architectures WHERE id = ? AND user_id = ?", (model_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_user_model(model_id: int, session_id: str) -> bool:
    """Delete a model by ID, checking session_id"""
    conn = get_db_connection()
    try:
        # Проверяем, что модель существует и принадлежит этой сессии
        cursor = conn.execute(
            "SELECT id FROM user_model_architectures WHERE id = ? AND user_id = ?",
            (model_id, session_id)
        )
        if not cursor.fetchone():
            logger.warning(f"Model {model_id} not found or access denied for session {session_id}")
            return False

        # Удаляем модель
        conn.execute('DELETE FROM user_model_architectures WHERE id = ?', (model_id,))
        conn.commit()
        logger.info(f"Deleted model {model_id} for session {session_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting model: {e}")
        return False
    finally:
        conn.close()

# Initialize database on module import
init_database()
