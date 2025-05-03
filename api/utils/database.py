import sqlite3
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

def get_db():
    """
    Connects to the database and returns the connection object.
    
    Returns:
        sqlite3.Connection: The database connection object with row factory set to sqlite3.Row
    """
    try:
        # Используем абсолютный путь к базе данных
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, 'crm.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f'Error connecting to database: {e}')
        raise 