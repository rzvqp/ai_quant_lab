"""``RuntimeEvaluator`` -- the shared base every family evaluator subclasses, and
``RuntimeStrategyHandle`` -- the object handed to Signal Engine in place of Strategy Manager's own
``StrategyRuntimeHandle`` stub.

Both satisfy Signal Engine's own structural Protocols (``ai_trader.signal_engine.pipeline.
StrategyHandleLike``/``StrategyApiLike``, explicitly documented there as "works with ANY object
satisfying this shape... without requiring inheritance") -- **zero lines of
``ai_trader/strategy_manager/`` or ``ai_trader/signal_engine/`` are modified** to make this work; this
is pure structural-typing composition, the same non-invasive pattern
``STRATEGY_RUNTIME_INTEGRATION_GAP.md`` §7/§9 recommended.

A subclass implements exactly ONE method, :meth:`RuntimeEvaluator.evaluate`, returning a
:class:`SetupResult`. This base class translates that single, cacheable-per-bar result into the three
separate ``detect``/``generate_signal``/``explain_signal`` dict responses ``pipeline.run_pipeline``
calls in sequence -- every family module stays a short, focused translation of its own mechanism,
never re-deriving the Strategy API's own dict-shape plumbing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ai_trader.strategy_manager.contract import Contract
from ai_trader.strategy_manager.required_context import compute_required_context
from ai_trader.strategy_manager.types import RequiredContext
from ai_trader.strategy_runtime import context_access

MarketContext = dict[str, Any]


@dataclass(frozen=True, slots=True)
class SetupResult:
    """One evaluator's complete, honest verdict for one ``(symbol, as_of)`` -- never invents a field
    it cannot support from the context it was actually given."""

    setup_forming: bool
    present: bool = False
    direction: str = "NONE"  # "LONG" | "SHORT" | "NONE" -- the generate_signal wire literal
    confirmations_met: bool = False
    strength: float = 0.0
    confidence: str = "NONE"
    regime: str | None = None
    entry: float | None = None
    stop: float | None = None
    target: float | None = None
    risk_R: float | None = None
    reason: str | None = None
    triggered_conditions: tuple[str, ...] = ()
    headline: str | None = None

    @staticmethod
    def no_setup(reason: str) -> "SetupResult":
        return SetupResult(setup_forming=False, reason=reason, headline=reason)

    @staticmethod
    def no_signal(reason: str, headline: str | None = None) -> "SetupResult":
        return SetupResult(setup_forming=True, present=False, reason=reason, headline=headline or reason)

    @staticmethod
    def waiting(
        direction: str, strength: float, confidence: str, regime: str | None,
        triggered_conditions: tuple[str, ...], headline: str,
    ) -> "SetupResult":
        return SetupResult(
            setup_forming=True, present=True, direction=direction, confirmations_met=False,
            strength=strength, confidence=confidence, regime=regime,
            triggered_conditions=triggered_conditions, headline=headline,
        )

    @staticmethod
    def actionable(
        direction: str, entry: float, stop: float, target: float | None, strength: float,
        confidence: str, regime: str | None, risk_R: float | None,
        triggered_conditions: tuple[str, ...], headline: str,
    ) -> "SetupResult":
        return SetupResult(
            setup_forming=True, present=True, direction=direction, confirmations_met=True,
            strength=strength, confidence=confidence, regime=regime, entry=entry, stop=stop,
            target=target, risk_R=risk_R, triggered_conditions=triggered_conditions, headline=headline,
        )


class RuntimeEvaluator:
    """Subclass and implement :meth:`evaluate` only. ``required_context()``/``health()``/
    ``can_trade()`` have generic, correct implementations here -- override only if a specific family
    genuinely needs custom precondition/gating logic beyond data-quality (none of the 43
    runtime-eligible strategies' own contracts specify anything beyond that as of this phase)."""

    #: Bars after which an open position of this strategy is force-closed at market, regardless of
    #: stop/target, via the Simulation Framework's own generic time-stop overlay
    #: (:mod:`ai_trader.simulation.time_stop`) -- ``None`` (the default) means no time-stop for this
    #: strategy (its own contract's exit is purely stop/target-based). A family evaluator whose own
    #: v0 ``executable_default.exit == "time"`` sets this to the frozen research engine's own "time"
    #: exit horizon (``code/mstrat.py``'s own ``_exitmap``: ``exit_kind=='time' -> 24`` bars, read
    #: only, never imported) -- never invented, never a substitute for a different, non-evidence
    #: -backed exit rule.
    time_stop_bars: int | None = None

    def __init__(self, strategy_id: str, contract: Contract, symbols: frozenset[str]) -> None:
        self.strategy_id = strategy_id
        self.contract = contract
        self._required = compute_required_context(contract, symbols)
        self._cache_key: tuple[str, int] | None = None
        self._cache_value: SetupResult | None = None

    # ------------------------------------------------------------------ subclass hook

    def evaluate(self, context: MarketContext) -> SetupResult:
        """The ONE method every family evaluator implements. Must be a pure function of ``context``
        (no external state, no wall-clock, no randomness) -- exactly the discipline
        ``context_access.py``'s own lookahead-safety guarantee depends on."""
        raise NotImplementedError(f"{type(self).__name__} must implement evaluate()")

    def _cached_evaluate(self, context: MarketContext) -> SetupResult:
        key = (context_access.symbol(context), context_access.as_of(context))
        if self._cache_key != key:
            self._cache_value = self.evaluate(context)
            self._cache_key = key
        assert self._cache_value is not None
        return self._cache_value

    # ------------------------------------------------------------------ StrategyApiLike (STRATEGY_API_v1.md)

    def required_context(self) -> RequiredContext:
        return self._required

    def health(self, context: object | None = None, trader_state: object | None = None) -> dict[str, Any]:
        if context is not None:
            level = context_access.data_quality_level(context)  # type: ignore[arg-type]
            if level in ("STALE", "INSUFFICIENT"):
                return {"state": "DISABLED"}
        return {"state": "OK"}

    def can_trade(self, context: object, trader_state: object) -> dict[str, Any]:
        return {"allowed": True}

    def detect(self, context: object) -> dict[str, Any]:
        result = self._cached_evaluate(context)  # type: ignore[arg-type]
        return {"setup_forming": result.setup_forming, "reason": result.reason}

    def generate_signal(self, context: object) -> dict[str, Any]:
        result = self._cached_evaluate(context)  # type: ignore[arg-type]
        if not result.setup_forming or not result.present:
            return {"present": False, "reason": result.reason}
        return {
            "present": True, "direction": result.direction,
            "required_confirmations_met": result.confirmations_met,
            "strength": result.strength, "confidence": result.confidence, "regime": result.regime,
            "entry": result.entry, "stop": result.stop, "target": result.target,
            "risk_R": result.risk_R,
        }

    def explain_signal(self, context: object) -> dict[str, Any]:
        result = self._cached_evaluate(context)  # type: ignore[arg-type]
        return {"headline": result.headline, "triggered_conditions": list(result.triggered_conditions)}


@dataclass(frozen=True, slots=True)
class RuntimeStrategyHandle:
    """Structural ``StrategyHandleLike`` -- ``{id, contract, api}``. Built by
    :mod:`ai_trader.strategy_runtime.registry` by pairing a Strategy Manager-loaded ``StrategyHandle``
    (for its ``id``/``contract``, i.e. registry/lifecycle authority stays with Strategy Manager) with
    a real :class:`RuntimeEvaluator` as ``api`` (never Strategy Manager's own stub)."""

    id: str
    contract: Contract
    api: RuntimeEvaluator
