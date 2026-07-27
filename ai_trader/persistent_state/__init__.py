"""Mandate 2 (2026-07-27): the ONE persistence solution for every in-memory value this session has
already disclosed as restart-vulnerable -- `LiveBarFeed`'s bar-close watermark, `LiveSignalJournal`'s
observation history, and `MT5PortfolioStateSource`'s equity high-water mark. See `store.py`'s own
docstring for why SQLite was chosen over hand-rolled binary files with a hash check, and why one engine
serving three consumers is the correct shape rather than three bespoke persistence mechanisms.

Shadow mode remains BLOCKED until every one of those three consumers is wired to this store and proven,
by a simulated-restart test, to resume deterministically -- per explicit CEO instruction. Live
loops/schedulers remain forbidden; this mandate is persistence only."""

from __future__ import annotations

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.persistent_state.types import PersistenceError

__all__ = ["PersistenceError", "SqliteStateStore"]
