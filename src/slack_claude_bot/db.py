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
                    thread_ts   TEXT NOT NULL,
                    provider    TEXT NOT NULL DEFAULT 'claude',
                    session_id  TEXT NOT NULL,
                    channel     TEXT NOT NULL,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (thread_ts, provider)
                )
            """)
            table_info = conn.execute("PRAGMA table_info(sessions)").fetchall()
            columns = {row["name"] for row in table_info}
            if "provider" not in columns:
                conn.execute("ALTER TABLE sessions ADD COLUMN provider TEXT NOT NULL DEFAULT 'claude'")
                table_info = conn.execute("PRAGMA table_info(sessions)").fetchall()

            primary_keys = [row["name"] for row in sorted(table_info, key=lambda row: row["pk"]) if row["pk"]]
            if primary_keys != ["thread_ts", "provider"]:
                conn.execute("""
                    CREATE TABLE sessions_new (
                        thread_ts   TEXT NOT NULL,
                        provider    TEXT NOT NULL DEFAULT 'claude',
                        session_id  TEXT NOT NULL,
                        channel     TEXT NOT NULL,
                        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (thread_ts, provider)
                    )
                """)
                conn.execute("""
                    INSERT OR REPLACE INTO sessions_new
                        (thread_ts, provider, session_id, channel, created_at, updated_at)
                    SELECT thread_ts, provider, session_id, channel, created_at, updated_at
                    FROM sessions
                """)
                conn.execute("DROP TABLE sessions")
                conn.execute("ALTER TABLE sessions_new RENAME TO sessions")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS locks (
                    thread_ts   TEXT PRIMARY KEY,
                    locked_at   DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get_session(self, thread_ts: str, provider: str = "claude") -> str | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT session_id FROM sessions WHERE thread_ts = ? AND provider = ?",
                (thread_ts, provider),
            ).fetchone()
            return row["session_id"] if row else None

    def save_session(self, thread_ts: str, session_id: str, channel: str, provider: str = "claude") -> None:
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO sessions (thread_ts, provider, session_id, channel)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(thread_ts, provider) DO UPDATE SET
                    session_id = excluded.session_id,
                    channel = excluded.channel,
                    updated_at = CURRENT_TIMESTAMP
            """, (thread_ts, provider, session_id, channel))

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
