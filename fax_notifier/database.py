from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, List, Optional

DB_PATH = "fax_notifier.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS fax_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    filepath TEXT NOT NULL,
    received_at TEXT NOT NULL,
    notified INTEGER NOT NULL DEFAULT 0,
    notified_at TEXT
);
"""


@contextmanager
def get_connection(db_path: str = DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute(CREATE_TABLE_SQL)


def insert_fax(filepath: str, db_path: str = DB_PATH) -> Optional[int]:
    """FAXレコードを登録する。重複ファイルの場合は None を返す。"""
    filename = filepath.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    received_at = datetime.now().isoformat()
    try:
        with get_connection(db_path) as conn:
            sql = (
                "INSERT INTO fax_records"
                " (filename, filepath, received_at) VALUES (?, ?, ?)"
            )
            cur = conn.execute(sql, (filename, filepath, received_at))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def mark_notified(record_id: int, db_path: str = DB_PATH) -> None:
    notified_at = datetime.now().isoformat()
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE fax_records SET notified = 1, notified_at = ? WHERE id = ?",
            (notified_at, record_id),
        )


def get_all_faxes(db_path: str = DB_PATH) -> List[dict]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM fax_records ORDER BY received_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_new_faxes(since: str, db_path: str = DB_PATH) -> List[dict]:
    """指定日時以降に受信した FAX 一覧を返す。"""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM fax_records WHERE received_at > ? ORDER BY received_at DESC",
            (since,),
        ).fetchall()
        return [dict(row) for row in rows]
