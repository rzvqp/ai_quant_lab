"""Data structures for the live Risk Manager (Phase 2, `RISK_MANAGER_LIVE_PHASE2_DESIGN.md`). The 3
genuinely-missing types the existing, frozen `ai_trader/risk_manager/` package never needed for
backtesting: `TradeProposal`, `AccountState`, `InstrumentSpecification`. `LiveRiskDecision` is a
deliberately NEW name -- not a reuse of `risk_manager.types.RiskDecision`, which has a different,
incompatible, scoring-engine-coupled field set.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ai_trader.risk_manager.types import EngineState, PortfolioState
from ai_trader.scoring_engine.types import Quality
from ai_trader.signal_engine.types import Direction


@dataclass(frozen=True, slots=True)
class TradeProposal:
    """A live trade candidate -- NOT yet risk-evaluated, NOT yet a broker order. Reuses `Direction`
    (`signal_engine.types`) and `Quality` (`scoring_engine.types`) verbatim rather than inventing
    parallel vocabularies. `confidence_quality` is optional -- Phase 8 (Confidence Engine) does not exist
    yet; a proposal built before it is wired carries `None`, and the live Risk Manager applies an
    explicit, disclosed, conservative default (never assumes favorable quality)."""

    proposal_id: str
    correlation_id: str
    strategy_id: str
    symbol: str
    direction: Direction
    entry: float
    stop: float
    target: float | None
    as_of: int
    confidence_quality: Quality | None = None

    def __post_init__(self) -> None:
        if not self.proposal_id:
            raise ValueError("TradeProposal.proposal_id must not be empty")
        if not self.correlation_id:
            raise ValueError("TradeProposal.correlation_id must not be empty")
        if not self.strategy_id:
            raise ValueError("TradeProposal.strategy_id must not be empty")
        if not self.symbol:
            raise ValueError("TradeProposal.symbol must not be empty")
        if not isinstance(self.direction, Direction):
            raise ValueError(f"TradeProposal.direction must be a Direction, got {self.direction!r}")
        if self.confidence_quality is not None and not isinstance(self.confidence_quality, Quality):
            raise ValueError(
                f"TradeProposal.confidence_quality must be a Quality or None, got {self.confidence_quality!r}"
            )


@dataclass(frozen=True, slots=True)
class AccountState:
    """Broker-agnostic account snapshot -- deliberately NOT imported from
    `ai_trader.simulation.portfolio_simulator.SimAccount` (backtest-internal) or any MT5 type (this
    package must never import the MT5 terminal API, CEO rule 9). A real caller (a future Execution Orchestrator,
    Phase 9) is responsible for projecting a live broker's own account state into this shape -- exactly
    mirroring how `PortfolioSimulator.to_portfolio_state()` already projects backtest state onto the
    existing, reused `risk_manager.types.PortfolioState`.

    `is_demo` is carried through for AUDIT ONLY -- Phase 2 itself never gates on it (that enforcement is
    `MT5ReadOnlyBrokerAdapter`'s/a future live adapter's own job, Phase 1/Phase 10); recorded here purely
    so `LiveRiskDecision.calculation_trace` can disclose which account type a decision was evaluated
    against, never silently omitted.
    """

    as_of: int
    currency: str
    balance: float
    equity: float
    margin_used: float
    margin_free: float
    margin_level: float | None
    leverage: float
    is_demo: bool

    def __post_init__(self) -> None:
        if not self.currency:
            raise ValueError("AccountState.currency must not be empty")
        if self.margin_used < 0:
            raise ValueError(f"AccountState.margin_used must be >= 0, got {self.margin_used!r}")
        if self.leverage <= 0:
            raise ValueError(f"AccountState.leverage must be > 0, got {self.leverage!r}")


@dataclass(frozen=True, slots=True)
class InstrumentSpecification:
    """Static contract facts for one symbol -- deliberately separate from the existing, reused
    `risk_manager.types.SymbolRiskSnapshot`/`RiskContext` (live/dynamic market state: spread, ATR,
    liquidity, gap flags -- still required as a 5th input to `evaluate_trade_proposal`, per the design
    document's own disclosed extension of the CEO's 4-input list). Neither `market_scanner.types.
    SymbolMeta` (no volume/margin fields) nor `execution_engine.types.BrokerCapabilities` (no spread/
    margin fields, and lives inside a package Phase 2 must not depend on) was a complete-enough fit --
    confirmed by reading both before defining this type, not assumed."""

    symbol: str
    tick_size: float
    lot_step: float
    min_volume: float
    max_volume: float
    contract_size: float
    point_value: float
    margin_currency: str

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("InstrumentSpecification.symbol must not be empty")
        if not self.margin_currency:
            raise ValueError("InstrumentSpecification.margin_currency must not be empty")


@dataclass(frozen=True, slots=True)
class CalculationTraceStep:
    """One gate/stage's own pass/fail record -- `LiveRiskDecision.calculation_trace` is an ordered tuple
    of these, covering every guard/limit/filter/sizing/volume-step/margin step actually run (CEO rule 12:
    "toate deciziile... trebuie să aibă reason codes și audit trail complet")."""

    stage: str
    passed: bool
    detail: str | None = None
    observed: float | str | bool | None = None
    limit: float | str | bool | None = None


@dataclass(frozen=True, slots=True)
class LiveRiskDecision:
    """The CEO's own explicitly-requested output shape (Phase 2 authorization, verbatim field list)."""

    approved: bool
    reason_codes: tuple[str, ...]
    requested_risk: float | None
    approved_risk: float | None
    calculated_volume: float | None
    monetary_risk: float | None
    stop_distance: float | None
    margin_estimate: float | None
    warnings: tuple[str, ...]
    calculation_trace: tuple[CalculationTraceStep, ...]
    #: Risk Audit #1 fix (2026-07-25): the worst `EngineState` any loss/drawdown guard signaled via its
    #: own `GuardResult.escalate_to` during this evaluation -- previously computed by `guards.py` and
    #: silently discarded by the caller loop (`risk_manager_live/engine.py`), never persisted anywhere.
    #: `None` means no guard escalated. Disclosing this is additive -- every existing caller that never
    #: reads this field observes byte-identical behavior.
    escalate_to: EngineState | None = None

    def __post_init__(self) -> None:
        if self.approved and not self.calculation_trace:
            raise ValueError(
                "LiveRiskDecision: an approved decision must carry a non-empty calculation_trace "
                "(CEO rule 12 -- complete audit trail, always)"
            )
        if not self.approved and not self.reason_codes:
            raise ValueError(
                "LiveRiskDecision: a denied decision must carry at least one reason code -- a refusal "
                "with no disclosed reason is exactly what this system must never produce"
            )


@dataclass(frozen=True, slots=True)
class TradingCircuitState:
    """Persistent, caller-owned circuit-breaker state (Risk Audit #1 fix). Unifies the three previously
    -disconnected mechanisms that finding named: `guards.py`'s `EngineState.SUSPENDED` escalation
    (previously discarded, see `LiveRiskDecision.escalate_to`), the daily/weekly loss + drawdown fields
    that trigger it, and `execution_orchestrator`'s own `emergency_stop` override -- all three now flow
    through this one object. Reuses `risk_manager.types.EngineState` verbatim rather than inventing a
    parallel vocabulary. Pure data: this package holds no state of its own; the caller persists this
    across calls, the same discipline already established for `PortfolioDailyState`
    (`portfolio_manager_live/types.py`)."""

    state: EngineState
    reason_code: str | None
    since: int | None

    def __post_init__(self) -> None:
        if self.state is not EngineState.READY and self.reason_code is None:
            raise ValueError(
                "TradingCircuitState: a non-READY state must carry a reason_code -- a suspension with "
                "no disclosed reason is exactly what this system must never produce"
            )
        if self.state is not EngineState.READY and self.since is None:
            raise ValueError("TradingCircuitState: a non-READY state must carry a since timestamp")


#: The starting state a caller with no prior persisted circuit state should use -- never fabricated as
#: "probably fine," an explicit, named constant.
READY_CIRCUIT_STATE = TradingCircuitState(state=EngineState.READY, reason_code=None, since=None)


class PortfolioStateSource(Protocol):
    """Injected dependency supplying the `PortfolioState` the circuit breaker evaluates against -- real
    (computed from live position/deal history, not yet built) or virtual/shadow (computed from a shadow
    journal, not yet built), same interface, never two parallel implementations (CEO instruction,
    2026-07-25: "sursa de P&L ca dependență injectată... aceeași interfață")."""

    def current_portfolio_state(self) -> PortfolioState: ...
