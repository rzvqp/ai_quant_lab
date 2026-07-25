"""Live MT5 account/instrument bridge (Step 4 authorization, 2026-07-26): projects
`gateway.account_info()`/`gateway.symbol_info()` -- both already part of the frozen `MT5Gateway`
Protocol (Phase 1), no gateway extension needed -- into `risk_manager_live.types.AccountState`/
`InstrumentSpecification`. Read-only, never receives an execution-capable adapter. Fail-closed on any
missing/incomplete field: raises `AccountDataUnavailableError`, never estimates. **Never caches**: every
call re-reads the gateway; a stale value served as current would be the same permissive-default failure
mode Risk Audit #1 already identified for P&L, on a different variable."""

from __future__ import annotations

from ai_trader.mt5_account_bridge.source import MT5AccountBridge
from ai_trader.mt5_account_bridge.types import AccountDataUnavailableError

__all__ = ["MT5AccountBridge", "AccountDataUnavailableError"]
