"""Data model for the Strategy Health System. Deliberately decoupled from
``ai_trader.simulation.portfolio_simulator.TradeRecord`` (:func:`from_trade_record` adapts one) so
this module can score a strategy's history from ANY source of closed trades -- a simulation run
today, a live broker fill log tomorrow -- without depending on the Simulation Framework's own
internal types.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class ClosedTrade:
    """The minimal shape this module needs from one closed trade. ``pnl_r`` is optional (``None``
    when no stop-hint was registered, mirroring ``TradeRecord.pnl_r``'s own "never fabricates"
    convention) -- metrics that need it are themselves ``None`` when unavailable, never approximated
    from ``net_pnl`` alone."""

    strategy_id: str
    exit_as_of: int
    net_pnl: float
    pnl_r: float | None
    holding_bars: int


class HealthState(str, Enum):
    """The four states a strategy can occupy (CEO directive) -- re-derived from scratch on every
    evaluation, never a one-way ratchet. ``ACTIVE`` is the only state permitted to trade; the other
    three retain the strategy in the library, available to return to ``ACTIVE`` the moment its own
    recent performance supports it again."""

    ACTIVE = "ACTIVE"
    WATCHLIST = "WATCHLIST"
    PROBATION = "PROBATION"
    DISABLED = "DISABLED"


#: Canonical rolling-window lengths, in days -- 30-day months, per the CEO's own "3/6/12 months"
#: framing (a calendar-month calendar would make window boundaries depend on which day of the month
#: `as_of` falls on; a fixed day-count is deterministic and reproducible regardless of `as_of`).
WINDOW_DAYS: dict[str, int] = {"3m": 90, "6m": 180, "12m": 365}
_SECONDS_PER_DAY = 86400


@dataclass(frozen=True, slots=True)
class WindowMetrics:
    """Every metric the CEO asked for, computed over one rolling window ending at ``as_of``. ``None``
    fields mean the metric could not be computed from this window's own trades (e.g. `profit_factor`
    with zero losing trades) -- never fabricated, never silently defaulted to 0."""

    window: str  # "3m" / "6m" / "12m"
    as_of: int
    n_trades: int
    win_rate: float | None
    profit_factor: float | None
    expectancy_currency: float | None
    expectancy_r: float | None  # "average R per trade"
    net_r: float | None
    net_pnl: float
    max_drawdown: float
    monthly_consistency: float | None  # fraction of active months this window that were net-positive
    equity_stability: float | None  # mean / stdev of this window's own monthly PnL (higher = smoother)
    max_losing_streak: int
    avg_holding_bars: float | None


@dataclass(frozen=True, slots=True)
class WindowScore:
    """The 0-100 composite for one window, plus the confidence (credibility weight, from sample
    size) that went into shrinking it and the PCA-derived weight vector used to combine metrics --
    both carried through so the final report can show its own work, not just a bare number."""

    window: str
    score: float | None  # None if the strategy had zero trades in this window (no evidence)
    confidence: float  # 0..1, from sample-size credibility shrinkage
    metric_weights: dict[str, float]  # PCA-derived (or equal-weight fallback), sums to 1.0
    metric_percentiles: dict[str, float]  # this strategy's own raw (pre-shrinkage) percentile rank


@dataclass(frozen=True, slots=True)
class StrategyHealthReport:
    """The full, self-explanatory output for one strategy: every window's metrics and score, the
    blended overall Health Score, the regime-adaptation trend signal, the resulting state, and a
    plain-language rationale string (built once, at scoring time, from the actual numbers -- not a
    template filled in after the fact)."""

    strategy_id: str
    as_of: int
    window_metrics: dict[str, WindowMetrics]  # keyed "3m"/"6m"/"12m"
    window_scores: dict[str, WindowScore]
    overall_score: float | None
    trend_delta: float | None  # 3m score - 12m score, when both exist
    state: HealthState
    rationale: str


def from_trade_record(record: object) -> ClosedTrade:
    """Adapt an ``ai_trader.simulation.portfolio_simulator.TradeRecord`` (or any object exposing the
    same attribute names) into a :class:`ClosedTrade`. Kept as a plain function (not a classmethod
    tied to the simulator's own type) so this module never imports the Simulation Framework."""
    return ClosedTrade(
        strategy_id=record.strategy_id,  # type: ignore[attr-defined]
        exit_as_of=record.exit_as_of,  # type: ignore[attr-defined]
        net_pnl=record.net_pnl,  # type: ignore[attr-defined]
        pnl_r=record.pnl_r,  # type: ignore[attr-defined]
        holding_bars=record.holding_bars,  # type: ignore[attr-defined]
    )
