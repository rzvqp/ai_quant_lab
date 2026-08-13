"""N1 -> Router -> Eligibility -> `DecisionRequest` -> EV -> N6, for ONE real closed bar, against the
full canonical catalog (CEO Mandate 2 step 5, 2026-08-14). This is the FIRST place in `ai_trader` that
constructs a `ve_brain.DecisionRequest` from real live data -- nothing here is a fixture.

**Two structural gaps in TODAY's wiring, both disclosed here rather than papered over** (see
`probability_source.py` for the first one in full):

1. `probability_inputs` is always `None` -- no validated per-regime outcome-count table exists yet.
2. `market_map_available`/`levels_available`/`confirmation_available` are always `False` -- no live
   level-tower (N3) or N4-confirmation wiring exists in `ai_trader` for `ve_brain`'s canonical strategy
   IDs today (that is a DIFFERENT division's deliverable -- see this repo's own memory of the
   "Level-tower conformance sprint" work happening in a separate repo, `wp5b`). Setting these `True`
   without a real source would be exactly the kind of invented data this mandate forbids.

**Consequence, stated plainly and covered by this package's own tests**: `decide_n6` returns `NO_TRADE`
for every real event today, and the terminal reason is `MISSING_LEVEL_INPUT` for any strategy that
survives eligibility+catalog checks (gap 2 fires before gap 1 ever would). This is the CORRECT, EXPECTED
behavior of a SHADOW-only integration proving the wiring itself, not producing trades -- not a defect.

**Geometry is real-price-derived, not fabricated, but its SIZING CONVENTION is an explicit placeholder**:
`entry_price` is the real last close, `atr` is the real vendored ATR14 over the real accumulated bar
history (`RawAxesBuilder.atr14()`) -- both genuine numbers from genuine data. `stop_price` (`entry -
1xATR`, LONG-only, since every entry in `ve_brain.CANONICAL_STRATEGIES` has `allowed_directions=
("LONG",)`) and `target_param` (`_PLACEHOLDER_TARGET_RR = 2.0`) are a SIZING CONVENTION, not a validated
strategy rule -- they exist only so `ve_brain.validate_request` can be satisfied and the REAL current
terminal reason (`MISSING_LEVEL_INPUT`, gap 2 above) is reached honestly, instead of an earlier, less
informative `SCHEMA_VALIDATION_FAILED`. Since gap 2 makes the outcome `NO_TRADE` regardless of RR, this
convention has zero effect on any decision produced today."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

import ve_brain  # type: ignore[import-untyped]  # external VE artifact, no py.typed marker -- never modified

from ai_trader.live_signal_source.types import Bar
from ai_trader.mandate2_readiness.decision_provenance import NEW_BRAIN_SOURCE, DecisionProvenance
from ai_trader.mandate2_readiness.event_identity import EventIdentity, NodeTrace
from ai_trader.new_brain_bridge.probability_source import load_probability_inputs
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder

_PLACEHOLDER_TARGET_RR = 2.0
_ELIGIBILITY_POLICY_VERSION = "eligibility-v1"


@dataclass(frozen=True, slots=True, kw_only=True)
class NewBrainOutcome:
    """One per (bar, catalog strategy). `decision`/`provenance` stay `None` when Router refuses before
    a `DecisionRequest` is ever built (no wasted N6 call for a structurally-ineligible strategy)."""

    event_identity: EventIdentity
    strategy_id: str
    strategy_version: str
    node_traces: tuple[NodeTrace, ...]
    decision: ve_brain.DecisionResponse | None
    provenance: DecisionProvenance | None
    entry_price: float | None = None
    stop_price: float | None = None
    target_price: float | None = None
    """The SAME geometry actually passed to `ve_brain.decide_n6` -- `risk_gate.py`'s Risk Manager
    bridge reuses these, never recomputes its own, so Risk Manager evaluates exactly what N6 decided
    on. `None` whenever `decision` is also `None` (no candidate was ever built)."""


def _fp(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def evaluate_bar(
    bar: Bar,
    *,
    timeframe: str,
    axes_builder: RawAxesBuilder,
    bias_direction: str | None = "LONG",
    confidence: float = 1.0,
    catalog: tuple[ve_brain.StrategyContract, ...] = ve_brain.CANONICAL_STRATEGIES,
    segment_id: str = "live",
    manifest_hash: str = "live-manifest",
) -> tuple[NewBrainOutcome, ...]:
    """Feeds ONE real closed bar through the real chain for EVERY catalog strategy. Raises `ValueError`
    if `bar.symbol` doesn't match `axes_builder`'s own symbol -- the same fail-closed check
    `RawAxesBuilder.observe` itself performs, surfaced here too since this is the actual entrypoint
    callers use."""
    if bar.symbol != axes_builder.symbol:
        raise ValueError(f"evaluate_bar: bar symbol {bar.symbol!r} != axes_builder symbol "
                          f"{axes_builder.symbol!r}")

    received_at = int(time.time())
    axes = axes_builder.observe(bar)
    market_event_id = f"{bar.symbol}:{timeframe}:{bar.ts_close}"
    n1_input_fp = _fp(bar.symbol, timeframe, str(bar.ts_close))
    n1_output_fp = _fp(str(axes.is_compressed), str(axes.is_displacement), str(axes.direction),
                        str(axes.structure))

    router = ve_brain.StrategyRouter(catalog)
    eligibility_decisions = router.eligible(axes, market_event_id, bias_direction, confidence)
    router_input_fp = _fp(market_event_id, str(bias_direction), str(confidence))

    atr = axes_builder.atr14()
    entry_price = axes_builder.last_close

    outcomes: list[NewBrainOutcome] = []
    for canon in catalog:
        eligibility = next(
            d for d in eligibility_decisions
            if d.strategy_id == canon.strategy_id and d.strategy_version == canon.strategy_version
        )
        trace_id = _fp(market_event_id, canon.strategy_id, canon.strategy_version)
        configuration_fingerprint = _fp(trace_id, ve_brain.VE_BRAIN_VERSION)
        event_identity = EventIdentity(
            trace_id=trace_id, market_event_id=market_event_id, symbol=bar.symbol, timeframe=timeframe,
            bar_id=f"{bar.symbol}:{timeframe}:{bar.ts_close}", market_timestamp=bar.ts_close,
            received_timestamp=max(received_at, bar.ts_close), brain_version=ve_brain.VE_BRAIN_VERSION,
            catalog_hash=ve_brain.CANONICAL_CATALOG_HASH, configuration_fingerprint=configuration_fingerprint,
        )
        traces = [
            NodeTrace(trace_id=trace_id, node_name="N1", input_fingerprint=n1_input_fp,
                      output=n1_output_fp, reason_codes=(), latency_seconds=0.0,
                      component_version=ve_brain.N1_CONTRACT_VERSION),
            NodeTrace(trace_id=trace_id, node_name="Router", input_fingerprint=router_input_fp,
                      output=_fp(str(eligibility.eligible), str(eligibility.mode.value),
                                 ",".join(eligibility.matched_regimes)),
                      reason_codes=eligibility.reason_codes, latency_seconds=0.0,
                      component_version=ve_brain.ROUTER_VERSION),
        ]

        if not eligibility.eligible:
            outcomes.append(NewBrainOutcome(
                event_identity=event_identity, strategy_id=canon.strategy_id,
                strategy_version=canon.strategy_version, node_traces=tuple(traces), decision=None,
                provenance=None,
            ))
            continue

        if atr is None or entry_price is None:
            traces.append(NodeTrace(
                trace_id=trace_id, node_name="N6", input_fingerprint=_fp(trace_id, "no-geometry"),
                output="", reason_codes=("ATR_HISTORY_INSUFFICIENT",), latency_seconds=0.0,
                component_version=ve_brain.ENGINE_VERSION,
            ))
            outcomes.append(NewBrainOutcome(
                event_identity=event_identity, strategy_id=canon.strategy_id,
                strategy_version=canon.strategy_version, node_traces=tuple(traces), decision=None,
                provenance=None,
            ))
            continue

        stop_price = entry_price - atr
        regime_label = eligibility.matched_regimes[0] if eligibility.matched_regimes else None
        probability_inputs = load_probability_inputs(canon.strategy_id, canon.strategy_version)

        candidate = ve_brain.DecisionRequest(
            contract_id=ve_brain.INPUT_CONTRACT_ID,
            strategy_id=canon.strategy_id, strategy_version=canon.strategy_version,
            validation_status=canon.validation_status, strategy_family=canon.strategy_family,
            strategy_policy_fingerprint=ve_brain.strategy_policy_fingerprint(canon),
            market_event_id=market_event_id, regime_fingerprint=eligibility.regime_fingerprint,
            market_state_ref=n1_output_fp, regime_label=regime_label, bias_direction=bias_direction,
            market_map_available=False, levels_available=False, confirmation_available=False,
            entry_price=entry_price, stop_price=stop_price, target_kind="rr",
            target_param=_PLACEHOLDER_TARGET_RR, holding_window=canon.holding_window, atr=atr,
            probability_inputs=probability_inputs, full_spread_price=0.10, entry_slippage_price=0.05,
            exit_slippage_price=0.05, symbol=bar.symbol, timeframe=timeframe, block_start=0,
            block_end=bar.ts_close, segment_id=segment_id, manifest_hash=manifest_hash,
            n1_contract_version=ve_brain.N1_CONTRACT_VERSION,
            raw_axis_schema_version=ve_brain.RAW_AXIS_SCHEMA_VERSION, router_version=ve_brain.ROUTER_VERSION,
            eligibility_policy_version=_ELIGIBILITY_POLICY_VERSION,
            measurement_contract_version=ve_brain.MEASUREMENT_CONTRACT_VERSION,
            configuration_fingerprint=configuration_fingerprint,
        )

        response = ve_brain.decide_n6(candidate, eligibility)
        traces.append(NodeTrace(
            trace_id=trace_id, node_name="EV", input_fingerprint=_fp(trace_id, "ev"),
            output=_fp(str(response.expected_value_net)), reason_codes=(), latency_seconds=0.0,
            component_version=ve_brain.ENGINE_VERSION,
        ))
        traces.append(NodeTrace(
            trace_id=trace_id, node_name="N6", input_fingerprint=configuration_fingerprint,
            output=_fp(str(response.decision), str(response.configuration_fingerprint)),
            reason_codes=response.reason_codes, latency_seconds=0.0,
            component_version=str(response.engine_version),
        ))

        provenance = None
        if response.decision in ("TRADE", "SHADOW_TRADE_CANDIDATE"):
            provenance = DecisionProvenance(
                source=NEW_BRAIN_SOURCE, trace_id=trace_id, catalog_hash=ve_brain.CANONICAL_CATALOG_HASH,
                configuration_fingerprint=str(response.configuration_fingerprint),
            )

        outcomes.append(NewBrainOutcome(
            event_identity=event_identity, strategy_id=canon.strategy_id,
            strategy_version=canon.strategy_version, node_traces=tuple(traces), decision=response,
            provenance=provenance, entry_price=entry_price, stop_price=stop_price,
            target_price=entry_price + _PLACEHOLDER_TARGET_RR * (entry_price - stop_price),
        ))

    return tuple(outcomes)
