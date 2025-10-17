"""SQLite DB manager (stub) [ARCHIVED].
Moved from food_recommender/database/db_manager.py
"""
import sqlite3
from pathlib import Path
from typing import Dict, Any, List

DB_PATH = Path(__file__).resolve().parent / "food_log.db"

def init_db():
    pass

def insert_log(entry: Dict[str, Any]) -> int:
    return 0

def recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
    return []
