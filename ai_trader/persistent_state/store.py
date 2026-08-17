"""`SqliteStateStore` -- Mandate 2's ONE persistence solution (CEO instruction, 2026-07-27: "Vreau o
singura solutie de persistenta, nu trei separate"), reused by three independent, otherwise-unrelated
consumers instead of each inventing its own restart-recovery mechanism:

- `live_signal_source.bar_feed.LiveBarFeed` -- the bar-close watermark (`_last_emitted_ts_open`).
- `live_signal_source.journal.LiveSignalJournal` -- the full append-only observation history.
- `mt5_pnl_source.source.MT5PortfolioStateSource` -- the equity high-water mark.

**Why SQLite over hand-rolled binary files with a hash check** (justification, since the CEO left the
choice open): SQLite is stdlib (`sqlite3`), so no new dependency. Its own transaction log makes every
write atomic by construction -- a crash mid-write leaves the last COMMITTED state intact, never a torn
write -- which is exactly the "no duplicate bars, no emptied journal, no reset metrics" determinism the
CEO's acceptance criterion demands, without hand-rolling atomic rename-and-checksum logic myself (more
custom code, more edge cases, on a correctness-critical path). It also natively unifies BOTH access
patterns every consumer above needs -- upsert-latest-value (watermark, equity high-water mark) and
append-only log (the journal) -- in one file with two small tables, which is what makes this genuinely
ONE solution rather than three. `verify_integrity()` below plays the same role a hash check would have
for a binary format, using SQLite's own built-in `PRAGMA integrity_check` rather than a custom scheme.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ai_trader.persistent_state.types import PersistenceError


class SqliteStateStore:
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path, isolation_level=None)
        try:
            self._conn.execute("PRAGMA journal_mode=WAL")
            integrity_ok = self.verify_integrity()
        except sqlite3.DatabaseError as exc:
            self._conn.close()
            raise PersistenceError(f"SqliteStateStore: {exc}") from exc
        if not integrity_ok:
            self._conn.close()
            raise PersistenceError(f"SqliteStateStore: integrity check failed for {self._db_path!r}")
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS kv_state (key TEXT PRIMARY KEY, value REAL NOT NULL)"
        )
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS append_log ("
            "log_name TEXT NOT NULL, seq INTEGER NOT NULL, payload TEXT NOT NULL, "
            "PRIMARY KEY (log_name, seq))"
        )
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS kv_text_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )

    def verify_integrity(self) -> bool:
        try:
            row = self._conn.execute("PRAGMA integrity_check").fetchone()
        except sqlite3.DatabaseError as exc:
            raise PersistenceError(f"SqliteStateStore: {exc}") from exc
        return row is not None and str(row[0]) == "ok"

    def get_value(self, key: str) -> float | None:
        row = self._conn.execute("SELECT value FROM kv_state WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        return float(row[0])

    def set_value(self, key: str, value: float) -> None:
        self._conn.execute(
            "INSERT INTO kv_state (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    def get_text(self, key: str) -> str | None:
        """Overwrite-latest text storage -- for a value representing CURRENT status (e.g. a heartbeat
        snapshot), never an append-only history. Separate table from `kv_state` (`REAL`-only) rather
        than widening that column's type, so every existing `get_value`/`set_value` caller is
        unaffected (RT-N1-PERSIST-0001, additive extension, no existing behavior changed)."""
        row = self._conn.execute("SELECT value FROM kv_text_state WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        return str(row[0])

    def set_text(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO kv_text_state (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    def append_log_entry(self, log_name: str, payload: str) -> None:
        row = self._conn.execute(
            "SELECT COALESCE(MAX(seq), -1) FROM append_log WHERE log_name = ?", (log_name,)
        ).fetchone()
        next_seq = int(row[0]) + 1 if row is not None else 0
        self._conn.execute(
            "INSERT INTO append_log (log_name, seq, payload) VALUES (?, ?, ?)",
            (log_name, next_seq, payload),
        )

    def read_log_entries(self, log_name: str) -> tuple[str, ...]:
        rows = self._conn.execute(
            "SELECT payload FROM append_log WHERE log_name = ? ORDER BY seq ASC", (log_name,)
        ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def close(self) -> None:
        self._conn.close()
