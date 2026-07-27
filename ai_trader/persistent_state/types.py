"""Types owned by `persistent_state`."""

from __future__ import annotations


class PersistenceError(Exception):
    """Raised by `SqliteStateStore` whenever the backing database cannot be trusted -- a failed
    integrity check at open time, or a read/write that fails at the `sqlite3` layer. Never swallowed
    into a fresh/empty store: a store that might be corrupt must never be silently treated as a store
    that is merely new, matching this repository's established fail-closed convention (`mt5_pnl_source.
    PortfolioDataUnavailableError`, `mt5_account_bridge.AccountDataUnavailableError`)."""
