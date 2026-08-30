"""CSV_CAUSAL_REPLAY_ADAPTER_V1 (CEO mandate, 2026-08-30): replaces TradingView live replay as the
Q4 apprenticeship's DATA SOURCE only -- the causal abstraction (current bar only, persistent
pointer, decision-commit handshake, next-bar lock) is unchanged from `causal_replay.js`
(`tradingview-mcp`), the mandate's own named conceptual reference. See
`docs/trader_apprenticeship/CSV_CAUSAL_REPLAY_ADAPTER_V1_SPEC.md` for the full design and
`CSV_CAUSAL_REPLAY_ADAPTER_V1_HANDOFF.md` for how to resume from bar 378.
"""

from ai_trader.csv_causal_replay.identity import ADAPTER_VERSION

__all__ = ["ADAPTER_VERSION"]
