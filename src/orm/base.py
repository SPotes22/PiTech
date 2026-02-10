import sqlite3
from typing import Any, Dict, List, Optional, Tuple


class BaseORM:
    def __init__(self, db_path: str = "audit.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._create_tables()

    def connect(self) -> None:
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def _create_tables(self) -> None:
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_data TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                archived BOOLEAN DEFAULT FALSE,
                approved_by TEXT,
                declined_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                hmac_secret TEXT,
                api_key_hash TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.conn.commit()
        self.conn.close()

    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> int:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        result = cursor.lastrowid
        self.conn.close()
        return result

    def fetch(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        self.conn.close()
        return [dict(row) for row in rows]
