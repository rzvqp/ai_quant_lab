"""`CachedUpstreamContext` -- RT-TIME-0001 section B ("M5 DUAL-CLOCK"): N1/Router stay on their own
M15 cadence (the CEO's own explicit "Nu muta regimul pe M5") -- this module is the ONE place that
computes them, and the ONE place an M5-triggered decision may read them from. Never recomputed on an
M5 tick; never substituted, guessed, or interpolated between two real M15 closes.

`UpstreamContextBuilder` owns its own `RawAxesBuilder`/`ve_brain.StrategyRouter` calls -- the SAME real
primitives `bridge.evaluate_bar` itself uses, reused directly, never reimplemented. It consumes M15
bars via its own `LiveBarFeed` instance with its OWN watermark key (the "N1/context watermark" the CEO
named explicitly) -- deliberately separate from the main M15 decision loop's own watermark, so this
context-refresh path can run independently (even in-process alongside the main loop) without either one
disturbing the other's dedup state."""

from __future__ import annotations

import dataclasses
import json

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.persistent_state.store import SqliteStateStore

_DEFAULT_CONTEXT_KEY = "new_brain_live.dual_clock.upstream_context"


def _fp(*parts: str) -> str:
    """Same generic sha256-truncate-16 convention `bridge._fp` already establishes -- a local copy
    (not an import of bridge.py's private helper) so this package's only real dependency on
    `new_brain_bridge` stays `RawAxesBuilder` itself, matching `n1_replay`'s own established precedent."""
    import hashlib
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class CachedUpstreamContext:
    """One per M15 close -- the complete, real N1 + Router reading that context is valid FOR, plus
    enough identity (`context_id`) that a consumer can prove exactly which context it used."""

    context_id: str
    symbol: str
    timeframe: str
    market_event_id: str
    market_timestamp: int  # the M15 bar's own ts_close this context was computed from
    n1_output_fp: str
    regime_axes_status: tuple[str, ...]
    router_bias_direction: str | None
    confidence: float
    axes: ve_brain.RawAxes
    eligibility_decisions: tuple[object, ...]  # tuple[ve_brain.EligibilityDecision, ...]
    atr: float | None
    entry_price: float | None


def _compute_context_id(context: CachedUpstreamContext) -> str:
    return _fp(
        context.symbol, context.timeframe, context.market_event_id, str(context.market_timestamp),
        context.n1_output_fp, ",".join(context.regime_axes_status),
        ",".join(f"{d.strategy_id}:{d.eligible}:{d.mode.value}" for d in context.eligibility_decisions),  # type: ignore[attr-defined]
    )


def build_context(
    *, symbol: str, timeframe: str, bar: Bar, axes_builder: RawAxesBuilder,
    catalog: tuple[ve_brain.StrategyContract, ...] = ve_brain.CANONICAL_STRATEGIES,
    router_bias_direction: str | None = None, confidence: float = 1.0,
) -> CachedUpstreamContext:
    """Feeds `bar` (a real, already-closed M15 bar) into `axes_builder` (the SAME real
    `RawAxesBuilder`) and computes the SAME `ve_brain.StrategyRouter.eligible(...)` call
    `bridge.evaluate_bar` itself makes -- identical recipe, identical fingerprint formula (`bridge.py`'s
    own `n1_output_fp = _fp(str(is_compressed), str(is_displacement), str(direction), str(structure))`),
    so a context built here is byte-for-byte comparable against what the main M15 loop's own N1/Router
    trace would show for the same bar."""
    axes = axes_builder.observe(bar)
    market_event_id = f"{bar.symbol}:{timeframe}:{bar.ts_close}"
    n1_output_fp = _fp(str(axes.is_compressed), str(axes.is_displacement), str(axes.direction), str(axes.structure))
    regime_axes_status = tuple(
        "available" if value is not None else "unavailable"
        for value in (axes.is_compressed, axes.is_displacement, axes.direction, axes.structure)
    )
    router = ve_brain.StrategyRouter(catalog)
    eligibility_decisions = router.eligible(axes, market_event_id, router_bias_direction, confidence)

    context = CachedUpstreamContext(
        context_id="",  # filled in below, after every other field is known
        symbol=symbol, timeframe=timeframe, market_event_id=market_event_id, market_timestamp=bar.ts_close,
        n1_output_fp=n1_output_fp, regime_axes_status=regime_axes_status,
        router_bias_direction=router_bias_direction, confidence=confidence, axes=axes,
        eligibility_decisions=eligibility_decisions, atr=axes_builder.atr14(), entry_price=axes_builder.last_close,
    )
    return dataclasses.replace(context, context_id=_compute_context_id(context))


def _serialize(context: CachedUpstreamContext) -> str:
    axes = context.axes
    return json.dumps({
        "context_id": context.context_id, "symbol": context.symbol, "timeframe": context.timeframe,
        "market_event_id": context.market_event_id, "market_timestamp": context.market_timestamp,
        "n1_output_fp": context.n1_output_fp, "regime_axes_status": list(context.regime_axes_status),
        "router_bias_direction": context.router_bias_direction, "confidence": context.confidence,
        "atr": context.atr, "entry_price": context.entry_price,
        "axes": {
            "is_compressed": axes.is_compressed, "is_displacement": axes.is_displacement,
            "direction": axes.direction, "structure": axes.structure,
            "volatility_state": axes.volatility_state, "n1_contract_version": axes.n1_contract_version,
            "raw_axis_schema_version": axes.raw_axis_schema_version,
        },
        "eligibility_decisions": [
            {
                "strategy_id": d.strategy_id, "strategy_version": d.strategy_version,  # type: ignore[attr-defined]
                "market_event_id": d.market_event_id, "regime_fingerprint": d.regime_fingerprint,  # type: ignore[attr-defined]
                "router_version": d.router_version, "eligible": d.eligible,  # type: ignore[attr-defined]
                "mode": d.mode.value, "matched_regimes": list(d.matched_regimes),  # type: ignore[attr-defined]
                "reason_codes": list(d.reason_codes),  # type: ignore[attr-defined]
            }
            for d in context.eligibility_decisions
        ],
    })


def _deserialize(raw: str) -> CachedUpstreamContext:
    data = json.loads(raw)
    axes = ve_brain.RawAxes(**data["axes"])
    decisions = tuple(
        ve_brain.EligibilityDecision(
            strategy_id=d["strategy_id"], strategy_version=d["strategy_version"],
            market_event_id=d["market_event_id"], regime_fingerprint=d["regime_fingerprint"],
            router_version=d["router_version"], eligible=d["eligible"], mode=ve_brain.RoutingMode(d["mode"]),
            matched_regimes=tuple(d["matched_regimes"]), reason_codes=tuple(d["reason_codes"]),
        )
        for d in data["eligibility_decisions"]
    )
    return CachedUpstreamContext(
        context_id=data["context_id"], symbol=data["symbol"], timeframe=data["timeframe"],
        market_event_id=data["market_event_id"], market_timestamp=data["market_timestamp"],
        n1_output_fp=data["n1_output_fp"], regime_axes_status=tuple(data["regime_axes_status"]),
        router_bias_direction=data["router_bias_direction"], confidence=data["confidence"],
        axes=axes, eligibility_decisions=decisions, atr=data["atr"], entry_price=data["entry_price"],
    )


class UpstreamContextStore:
    """Overwrite-latest persistence (`SqliteStateStore.set_text`/`get_text`, the same mechanism
    `new_brain_live.heartbeat` already established) -- a context represents CURRENT state, never a
    history log."""

    def __init__(self, state_store: SqliteStateStore, key: str = _DEFAULT_CONTEXT_KEY) -> None:
        self._state_store = state_store
        self._key = key

    def latest(self) -> CachedUpstreamContext | None:
        raw = self._state_store.get_text(self._key)
        return None if raw is None else _deserialize(raw)

    def record(self, context: CachedUpstreamContext) -> None:
        self._state_store.set_text(self._key, _serialize(context))
