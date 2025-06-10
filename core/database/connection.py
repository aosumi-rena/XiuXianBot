import os
import json
import logging
import sqlite3
from typing import Optional, Dict, Any, List

logger = logging.getLogger("Database")

sqlite_conn: Optional[sqlite3.Connection] = None

class DatabaseError(Exception):
    pass

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def connect_mongo(*_args, **_kwargs):
    raise DatabaseError("MongoDB support has been removed")

def connect_sqlite(path: str = None) -> sqlite3.Connection:
    global sqlite_conn

    if path is None:
        config = load_config()
        path = config.get('db', {}).get('sqlite_path', os.path.join('data', 'xiu_xian.db'))

    if not os.path.isabs(path):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(project_root, path)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        sqlite_conn = sqlite3.connect(path, check_same_thread=False)
        sqlite_conn.row_factory = sqlite3.Row
        logger.info(f"Connected to SQLite database: {path}")
    except Exception as e:
        logger.error(f"Failed to connect to SQLite: {e}")
        raise DatabaseError(f"Failed to connect to SQLite: {e}")

    return sqlite_conn

def get_sqlite() -> sqlite3.Connection:
    global sqlite_conn
    if sqlite_conn is None:
        return connect_sqlite()
    return sqlite_conn


def create_tables(conn: Optional[sqlite3.Connection] = None) -> None:
    if conn is None:
        conn = get_sqlite()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            in_game_username TEXT,
            lang TEXT DEFAULT 'CHS',
            state INTEGER DEFAULT 0,
            exp INTEGER DEFAULT 0,
            rank INTEGER DEFAULT 1,
            dy_times INTEGER DEFAULT 0,
            copper INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 0,
            asc_reduction INTEGER DEFAULT 0,
            sign INTEGER DEFAULT 0,
            element TEXT,
            discord_id TEXT,
            telegram_id TEXT,
            matrix_id TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS timings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            start_time INTEGER,
            type TEXT,
            base_gain INTEGER
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            item_type TEXT,
            item_name TEXT,
            quantity INTEGER,
            level INTEGER
        )
        """
    )
    conn.commit()


def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    conn = get_sqlite()
    cur = conn.execute(query, params)
    row = cur.fetchone()
    return dict(row) if row else None


def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_sqlite()
    cur = conn.execute(query, params)
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def execute(query: str, params: tuple = ()) -> int:
    conn = get_sqlite()
    cur = conn.execute(query, params)
    conn.commit()
    return cur.lastrowid

def get_collection(_collection_name: str):
    raise DatabaseError("MongoDB support has been removed")

def ensure_defaults(*_args, **_kwargs):
    raise DatabaseError("MongoDB support has been removed")

def backup_collection(*_args, **_kwargs) -> Optional[str]:
    raise DatabaseError("MongoDB support has been removed")


def backup_users_data() -> Optional[str]:
    return backup_collection("users")


def backup_items_data() -> Optional[str]:
    return backup_collection("items")


def backup_timings_data() -> Optional[str]:
    return backup_collection("timings")
