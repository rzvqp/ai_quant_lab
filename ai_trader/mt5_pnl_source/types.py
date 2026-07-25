"""Types owned by `mt5_pnl_source`. `DealRecord` is the one pure, MT5-independent representation the
computation functions operate on -- a real MT5 deal namedtuple is projected into this shape once, at the
gateway boundary, so the arithmetic never touches MT5's own field names/quirks directly."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DealRecord:
    """One closed deal's contribution to realized P&L. `close_time` is a unix epoch second, matching
    every other timestamp convention in this codebase."""

    profit: float
    close_time: int


class PortfolioDataUnavailableError(Exception):
    """Raised by `MT5PortfolioStateSource` whenever account/position/deal data cannot be read
    completely -- deliberately never swallowed into a 0.0/empty default here. Risk Audit #1's own
    finding: a silent default reads as "no losses," the most permissive outcome possible exactly when
    nothing is actually known -- the wrong direction of error for a circuit breaker's own data source.
    The caller (the circuit breaker's own caller, `execution_orchestrator.orchestrate()`) is responsible
    for treating this as a reason not to trade, not this class's job to decide.
    """
