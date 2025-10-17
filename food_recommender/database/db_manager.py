"""SQLite DB manager (stub)."""
import sqlite3
from pathlib import Path
from typing import Dict, Any, List


DB_PATH = Path(__file__).resolve().parent / "food_log.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS food_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            meal_type TEXT NOT NULL, -- breakfast/lunch/dinner/snack
            category TEXT,
            dishes TEXT,
            taste TEXT,
            nutrition TEXT,
            image_path TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def insert_log(entry: Dict[str, Any]) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO food_logs (timestamp, meal_type, category, dishes, taste, nutrition, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entry.get("timestamp"),
            entry.get("meal_type"),
            ",".join(entry.get("category", [])),
            ",".join(entry.get("dishes", [])),
            ",".join(entry.get("taste", [])),
            ",".join(entry.get("nutrition", [])),
            entry.get("image_path"),
        ),
    )
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid


def recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM food_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
