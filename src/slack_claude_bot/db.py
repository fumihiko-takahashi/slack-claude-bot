import sqlite3
from contextlib import contextmanager

# TTL: runner TIMEOUT + 30分バッファ
_DEFAULT_LOCK_TTL = 60 * 60 * 3 + 60 * 30


class SessionDB:
    def __init__(self, db_path: str = "sessions.db", lock_ttl: int = _DEFAULT_LOCK_TTL):
        self.db_path = db_path
        self.lock_ttl = lock_ttl

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    thread_ts   TEXT PRIMARY KEY,
                    session_id  TEXT NOT NULL,
                    channel     TEXT NOT NULL,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS locks (
                    thread_ts   TEXT PRIMARY KEY,
                    locked_at   DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get_session(self, thread_ts: str) -> str | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT session_id FROM sessions WHERE thread_ts = ?", (thread_ts,)
            ).fetchone()
            return row["session_id"] if row else None

    def save_session(self, thread_ts: str, session_id: str, channel: str) -> None:
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO sessions (thread_ts, session_id, channel)
                VALUES (?, ?, ?)
                ON CONFLICT(thread_ts) DO UPDATE SET
                    session_id = excluded.session_id,
                    updated_at = CURRENT_TIMESTAMP
            """, (thread_ts, session_id, channel))

    def acquire_lock(self, thread_ts: str) -> bool:
        try:
            with self._conn() as conn:
                conn.execute(
                    "DELETE FROM locks WHERE locked_at < datetime('now', ? || ' seconds')",
                    (f"-{self.lock_ttl}",)
                )
                conn.execute("INSERT INTO locks (thread_ts) VALUES (?)", (thread_ts,))
            return True
        except sqlite3.IntegrityError:
            return False

    def release_lock(self, thread_ts: str) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM locks WHERE thread_ts = ?", (thread_ts,))

    def clear_all_locks(self) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM locks")
