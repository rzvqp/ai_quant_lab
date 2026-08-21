"""Deduplication (AI Trader New Brain Architecture mandate, section 23). Identity =
`(strategy, instrument, market_state_identity)` -- `TradeHypothesis.dedup_key`. Rather than a SEPARATE
dedup store, this module reuses the `ShadowLedger`'s own append-only history as the single source of
truth for "has this MarketState already been fully evaluated" -- restarting the process re-reads the
SAME ledger (`ShadowLedger.__init__` loads all persisted entries), so a restart can never re-record or
re-submit a logically duplicate cycle as new."""

from __future__ import annotations

from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger


def already_processed(ledger: ShadowLedger, *, market_state_identity: str) -> bool:
    return any(e.market_state_identity == market_state_identity for e in ledger.entries)
