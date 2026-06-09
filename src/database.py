import sqlite3
from datetime import datetime
from pathlib import Path
from src.config import DEFAULT_SETTINGS

def init_db(db_path: Path):
    with sqlite3.connect(db_path) as conn:
        conn.execute(""" CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        
        conn.execute(""" CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            session_id TEXT,
            created_at TIMESTAMP
        )""")
        
        conn.execute(""" CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT, 
            cpu_percent REAL,
            ram_used REAL,
            ram_total REAL,
            disk_used REAL,
            disk_free REAL,
            collected_at TIMESTAMP
        )""")
        conn.commit()
        
def init_default_settings(db_path: Path):
    with sqlite3.connect(db_path) as conn:
        for key, value in DEFAULT_SETTINGS.items():
            conn.execute(""" INSERT OR IGNORE INTO settings(key, value) 
                         VALUES(?, ?)""", (key, value))
        conn.commit()

               
def save_user_settings(db_path: Path, key: str, value: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute(""" INSERT OR REPLACE INTO settings(key, value) 
                     VALUES(?, ?)""", (key, value))

def save_chat_history(db_path: Path, role: str, content: str, session_id: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute(""" INSERT INTO chat_history(role, content, session_id, created_at) 
                     VALUES(?, ?, ?, ?)""", (role, content, session_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

def save_coll_metrics(db_path: Path, scan_id: str, cpu_percent: float, ram_used: float, 
                    ram_total: float, disk_used: float, disk_free: float):
    
    with sqlite3.connect(db_path) as conn:
        conn.execute(""" INSERT INTO metrics(scan_id, cpu_percent, ram_used, ram_total, disk_used, disk_free, collected_at) 
                     VALUES(?, ?, ?, ?, ?, ?, ?)""", 
                     (scan_id, cpu_percent, ram_used, ram_total, disk_used, disk_free, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))) 
        conn.commit()

def get_metrics(db_path: Path, scan_id: str):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(""" SELECT * FROM metrics 
                               WHERE scan_id = ?
                               ORDER BY collected_at DESC """, (scan_id,))
        return cursor.fetchall()
        
def get_chat_history(db_path: Path, session_id: str):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(""" SELECT * FROM chat_history
                              WHERE session_id = ? 
                              ORDER BY created_at DESC LIMIT 25 """, (session_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_settings_by_key(db_path: Path, key: str):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(""" SELECT value FROM settings
                              WHERE key = ? """, (key,))
        return cursor.fetchone()

def clean_old_metrics(db_path: Path):
    """ If count of rows exceeded it's limit it's going to clean oldest ones """
    with sqlite3.connect(db_path) as conn:
        conn.execute(""" DELETE FROM metrics 
                     WHERE id NOT IN (
                         SELECT id FROM metrics
                         ORDER BY collected_at DESC LIMIT 400) """)
        conn.commit()

def get_latest_session_id(db_path: Path):
    """ To continue conversation with AI we should get latest session's id """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(""" SELECT session_id FROM chat_history
                     ORDER BY created_at DESC LIMIT 1 """)
        return cursor.fetchone()

def get_latest_metrics(db_path: Path):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(""" SELECT * FROM metrics
                              ORDER BY collected_at DESC LIMIT 20 """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    