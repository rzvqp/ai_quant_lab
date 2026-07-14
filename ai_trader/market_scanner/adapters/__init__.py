"""Data Source Adapters (``MARKET_SCANNER_ARCHITECTURE.md`` §11).

Every adapter emits the same normalized :class:`~ai_trader.market_scanner.types.RawBar` /
:class:`~ai_trader.market_scanner.types.RawTick` / :class:`~ai_trader.market_scanner.types.CalendarEvent`
stream; the Market Scanner core is identical regardless of which adapter feeds it. Only the
``replay`` adapter is implemented here (Phase 6.1 scope: no broker/live/MetaTrader integration —
that is explicitly Phase 8+ and out of scope for this module).
"""

from ai_trader.market_scanner.adapters.base import DataSourceAdapter
from ai_trader.market_scanner.adapters.replay import ReplayAdapter

__all__ = ["DataSourceAdapter", "ReplayAdapter"]
