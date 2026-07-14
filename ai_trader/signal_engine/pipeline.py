"""The fixed, per-strategy evaluation pipeline (``SIGNAL_ENGINE_ARCHITECTURE.md`` §3).

This module is deliberately **timeout-unaware and exception-permissive**: :func:`run_pipeline` calls
straight into the strategy's own Strategy API methods and may raise (a malformed response, an
unimplemented method, a genuine bug in the strategy's own code — anything). The caller
(:mod:`ai_trader.signal_engine.engine`) is responsible for wrapping every call to this function with
the timeout + exception boundary that turns any failure into a classified, non-actionable
``INVALID`` signal (architecture §5/§7: "corrupted/absent output from the strategy -> INVALID
[CORRUPTED_OUTPUT]"). Keeping that boundary OUTSIDE this module makes the pipeline logic itself a
plain, synchronous, easily-testable function.

**A note on what this module does NOT do**: it does not interpret a strategy's natural-language
``execution.entry``/``exit``/``stop`` rule descriptions into trading logic. No strategy anywhere in
this repository has executable entry/exit code (the Strategy Library's 51 entries are executable
*specifications*, not executable *code* -- see ``ai_trader/strategy_manager/handle.py``'s own module
docstring). This pipeline's job is the fixed ORCHESTRATION machinery around whatever the Strategy API
methods return -- it calls ``health``/``can_trade``/``detect``/``generate_signal``/``explain_signal``
exactly as the architecture specifies and turns their responses into a ``StrategySignal``. Today, the
only concrete ``StrategyHandle.api`` in this repository
(:class:`ai_trader.strategy_manager.handle.StrategyRuntimeHandle`) raises
``StrategyApiNotImplementedError`` for every one of those five methods by design -- which this
pipeline handles exactly like any other strategy failure: isolated, classified, never fabricated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from ai_trader.signal_engine.context_check import missing_context_items
from ai_trader.signal_engine.exceptions import SignalEngineError
from ai_trader.signal_engine.types import (
    ConditionRecord,
    Confirmations,
    Direction,
    MarketContext,
    QualityFlag,
    SignalState,
    TradeParams,
)
from ai_trader.strategy_manager.contract import Contract
from ai_trader.strategy_manager.types import RequiredContext


class MalformedStrategyResponseError(SignalEngineError):
    """Raised internally when a Strategy API call returns something that isn't a well-formed
    response for that method. Caught by the engine's outer boundary and classified as
    ``INVALID``/``CORRUPTED_OUTPUT`` -- never propagated to a caller."""

    def __init__(self, method: str, reason: str) -> None:
        self.method = method
        self.reason = reason
        super().__init__(f"malformed response from {method}(): {reason}")


class StrategyApiLike(Protocol):
    """Structural shape of ``StrategyHandle.api`` this pipeline calls. A ``Protocol`` so it works
    with ANY object satisfying this shape -- the real
    :class:`ai_trader.strategy_manager.handle.StrategyRuntimeHandle`, a test double, or a future
    fuller implementation -- without requiring inheritance."""

    def required_context(self) -> RequiredContext: ...
    def health(self, context: object | None = None, trader_state: object | None = None) -> object: ...
    def can_trade(self, context: object, trader_state: object) -> object: ...
    def detect(self, context: object) -> object: ...
    def generate_signal(self, context: object) -> object: ...
    def explain_signal(self, context: object) -> object: ...


class StrategyHandleLike(Protocol):
    # Read-only properties, not plain attributes: the real implementer
    # (ai_trader.strategy_manager.handle.StrategyHandle) is a frozen dataclass, and a Protocol with
    # plain mutable attributes structurally requires read-write compatibility -- mismatching a
    # frozen field. Properties correctly express the "read-only contract" this was always documented
    # to mean (StrategyHandle's own docstring: "id, contract (read-only), api").
    @property
    def id(self) -> str: ...
    @property
    def contract(self) -> Contract: ...
    @property
    def api(self) -> StrategyApiLike: ...


def _as_dict(response: object, method: str) -> dict[str, Any]:
    """Require ``response`` to be a plain dict (the convention every runtime response follows,
    matching ``MarketContext``'s own "the schema IS the canonical contract" choice) -- raises
    :class:`MalformedStrategyResponseError` otherwise, never guesses at a shape."""
    if not isinstance(response, dict):
        raise MalformedStrategyResponseError(method, f"expected a dict, got {type(response).__name__}")
    return response


def _require(d: dict[str, Any], key: str, method: str) -> Any:
    if key not in d:
        raise MalformedStrategyResponseError(method, f"missing required key {key!r}")
    return d[key]


@dataclass(slots=True)
class PipelineOutcome:
    """Everything :func:`run_pipeline` determined about one (strategy, context) evaluation --
    consumed by :mod:`ai_trader.signal_engine.assembler` to build the final ``StrategySignal``."""

    state: SignalState
    direction: Direction = Direction.NONE
    signal_strength: float = 0.0
    confidence: str = "NONE"
    required_confirmations: tuple[str, ...] = ()
    confirmations_met: bool = False
    missing_context: tuple[str, ...] = ()
    invalid_conditions: tuple[str, ...] = ()
    trade_params: TradeParams | None = None
    regime: str | None = None
    session: str | None = None
    why_exists: tuple[ConditionRecord, ...] = ()
    why_failed: tuple[ConditionRecord, ...] = ()
    required_condition_records: tuple[ConditionRecord, ...] = ()
    confirmations_detail: Confirmations = field(default_factory=Confirmations)
    explain_headline: str | None = None


def _health_outcome(health: dict[str, Any]) -> PipelineOutcome | None:
    state = _require(health, "state", "health")
    if not isinstance(state, str):
        raise MalformedStrategyResponseError("health", f"'state' must be a string, got {type(state).__name__}")
    if state == "INVALID":
        return PipelineOutcome(
            state=SignalState.INVALID,
            why_failed=(ConditionRecord(code="HEALTH_INVALID", satisfied=False, observed=state),),
        )
    if state == "DISABLED":
        return PipelineOutcome(
            state=SignalState.BLOCKED,
            invalid_conditions=("health:DISABLED",),
            why_failed=(ConditionRecord(code="HEALTH_DISABLED", satisfied=False, observed=state),),
        )
    return None


def _can_trade_outcome(gate: dict[str, Any]) -> PipelineOutcome | None:
    allowed = _require(gate, "allowed", "can_trade")
    if not isinstance(allowed, bool):
        raise MalformedStrategyResponseError("can_trade", f"'allowed' must be a bool, got {type(allowed).__name__}")
    if not allowed:
        reasons_raw = gate.get("reasons", [])
        if not isinstance(reasons_raw, list):
            raise MalformedStrategyResponseError("can_trade", "'reasons' must be a list")
        reasons = tuple(str(r) for r in reasons_raw)
        return PipelineOutcome(
            state=SignalState.BLOCKED,
            invalid_conditions=reasons,
            why_failed=tuple(ConditionRecord(code=r, satisfied=False) for r in reasons) or
            (ConditionRecord(code="CAN_TRADE_BLOCKED", satisfied=False),),
        )
    return None


def run_pipeline(
    context: MarketContext, handle: StrategyHandleLike, trader_state: object,
) -> PipelineOutcome:
    """Run the fixed evaluation pipeline for one strategy against one context (architecture §3).
    May raise :class:`MalformedStrategyResponseError` or any exception the strategy's own API raises
    -- the caller is responsible for the timeout + exception boundary (see module docstring).
    """
    contract = handle.contract

    # Stage 2: Precondition Validation.
    health_raw = handle.api.health(context, trader_state)
    health_outcome = _health_outcome(_as_dict(health_raw, "health"))
    if health_outcome is not None:
        return health_outcome

    gate_raw = handle.api.can_trade(context, trader_state)
    gate_outcome = _can_trade_outcome(_as_dict(gate_raw, "can_trade"))
    if gate_outcome is not None:
        return gate_outcome

    # Stage 3: Context Validation.
    required = handle.api.required_context()
    if not isinstance(required, RequiredContext):
        raise MalformedStrategyResponseError(
            "required_context", f"expected a RequiredContext, got {type(required).__name__}",
        )
    missing = missing_context_items(context, required)
    if missing:
        return PipelineOutcome(
            state=SignalState.NEED_CONTEXT,
            missing_context=tuple(missing),
            why_failed=tuple(ConditionRecord(code=f"MISSING:{m}", satisfied=False) for m in missing),
        )

    # Stage 4: Signal Evaluation.
    detect_raw = _as_dict(handle.api.detect(context), "detect")
    setup_forming = _require(detect_raw, "setup_forming", "detect")
    if not isinstance(setup_forming, bool):
        raise MalformedStrategyResponseError("detect", "'setup_forming' must be a bool")
    if not setup_forming:
        reason = detect_raw.get("reason")
        outcome = PipelineOutcome(
            state=SignalState.NO_SIGNAL,
            why_failed=(ConditionRecord(code="NO_SETUP", satisfied=False, observed=reason),),
        )
        return _attach_explanation(outcome, handle, context)

    signal_raw = _as_dict(handle.api.generate_signal(context), "generate_signal")
    present = _require(signal_raw, "present", "generate_signal")
    if not isinstance(present, bool):
        raise MalformedStrategyResponseError("generate_signal", "'present' must be a bool")
    if not present:
        reason = signal_raw.get("reason")
        outcome = PipelineOutcome(
            state=SignalState.NO_SIGNAL,
            why_failed=(ConditionRecord(code="NO_SIGNAL_PRESENT", satisfied=False, observed=reason),),
        )
        return _attach_explanation(outcome, handle, context)

    direction_str = _require(signal_raw, "direction", "generate_signal")
    if direction_str not in ("LONG", "SHORT", "NONE"):
        raise MalformedStrategyResponseError("generate_signal", f"invalid direction {direction_str!r}")
    if direction_str == "NONE":
        raise MalformedStrategyResponseError("generate_signal", "present=True but direction=NONE")

    required_confirmations = tuple(str(c) for c in contract.semantics.required_confirmations)
    confirmations_met = bool(signal_raw.get("required_confirmations_met", False))
    strength = signal_raw.get("strength", 0.0)
    if not isinstance(strength, (int, float)) or not (0.0 <= float(strength) <= 1.0):
        raise MalformedStrategyResponseError("generate_signal", f"'strength' out of [0,1]: {strength!r}")
    confidence = signal_raw.get("confidence", "NONE")
    regime = signal_raw.get("regime")
    trade_params = TradeParams(
        entry=signal_raw.get("entry"), stop=signal_raw.get("stop"), target=signal_raw.get("target"),
        risk_R=signal_raw.get("risk_R"), valid_until=signal_raw.get("valid_until"),
    )
    direction = Direction(direction_str)

    if not confirmations_met:
        pending = tuple(c for c in required_confirmations)
        # SIGNAL_SCHEMA.json's allOf rule requires direction=NONE and trade_params=null for every
        # non-actionable state, WAIT_CONFIRMATION included -- the strategy's own proposed
        # direction/prices are real (a setup IS forming), but they are not yet a tradeable
        # commitment, so the schema deliberately withholds them from the top-level actionable
        # fields. They remain visible via signal_strength/confidence and the pending confirmations.
        outcome = PipelineOutcome(
            state=SignalState.WAIT_CONFIRMATION,
            direction=Direction.NONE, signal_strength=float(strength), confidence=str(confidence),
            required_confirmations=required_confirmations, confirmations_met=False,
            regime=regime, trade_params=None,
            confirmations_detail=Confirmations(required=required_confirmations, met=(), pending=pending),
            why_failed=(ConditionRecord(code="CONFIRMATIONS_NOT_MET", satisfied=False),),
        )
        return _attach_explanation(outcome, handle, context)

    # present + confirmations met. The runtime response schema (runtime_responses.v1.schema.json)
    # has no field distinguishing "entry trigger is NOW" from "setup complete, entry pending" --
    # see the module docstring's design-decision note. v1 treats every present+confirmed signal as
    # immediately actionable (BUY/SELL), matching the frozen research engine's own "signal at bar
    # close, fill at next open" convention (the next-open fill is an execution-layer mechanic, not
    # a "still pending" setup state). LONG_READY/SHORT_READY remain fully implemented, reachable
    # states, ready for a future interface MINOR that adds an explicit pending/trigger field.
    state = SignalState.BUY if direction is Direction.LONG else SignalState.SELL

    outcome = PipelineOutcome(
        state=state, direction=direction, signal_strength=float(strength), confidence=str(confidence),
        required_confirmations=required_confirmations, confirmations_met=True,
        regime=regime, trade_params=trade_params,
        confirmations_detail=Confirmations(required=required_confirmations, met=required_confirmations, pending=()),
        why_exists=(ConditionRecord(code="SIGNAL_PRESENT", satisfied=True),),
    )
    return _attach_explanation(outcome, handle, context)


def _attach_explanation(
    outcome: PipelineOutcome, handle: StrategyHandleLike, context: MarketContext,
) -> PipelineOutcome:
    """Stage 5: call ``explain_signal(ctx)`` and fold its ``triggered_conditions``/``headline``
    into the outcome. Called for every state that reached Stage 4 (``detect()`` was invoked) --
    ``NO_SIGNAL``, ``WAIT_CONFIRMATION``, and the actionable states -- never for the earlier
    Precondition/Context short-circuits (``INVALID``/``BLOCKED``/``NEED_CONTEXT``), which have
    nothing for the strategy to explain yet (architecture §3: Stage 5 follows Stage 4).
    """
    explanation_raw = _as_dict(handle.api.explain_signal(context), "explain_signal")
    headline = explanation_raw.get("headline")
    if headline is not None and not isinstance(headline, str):
        raise MalformedStrategyResponseError("explain_signal", "'headline' must be a string or absent")
    triggered_raw = explanation_raw.get("triggered_conditions", [])
    if not isinstance(triggered_raw, list):
        raise MalformedStrategyResponseError("explain_signal", "'triggered_conditions' must be a list")
    triggered = tuple(ConditionRecord(code=str(c), satisfied=True) for c in triggered_raw)
    outcome.why_exists = outcome.why_exists + triggered
    outcome.explain_headline = headline
    return outcome
