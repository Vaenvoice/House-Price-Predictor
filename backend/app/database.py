"""
VaenEstate Database Layer
SQLite database for users, predictions, and model metadata.
"""
import sqlite3
from app.config import DB_PATH


def get_connection():
    """Get a new SQLite connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            area REAL NOT NULL,
            rooms INTEGER NOT NULL,
            location TEXT NOT NULL,
            age REAL NOT NULL,
            predicted_price REAL NOT NULL,
            confidence_low REAL,
            confidence_high REAL,
            model_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trained_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rmse REAL,
            mae REAL,
            r2_score REAL,
            is_best INTEGER DEFAULT 0,
            trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            model_path TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized")
