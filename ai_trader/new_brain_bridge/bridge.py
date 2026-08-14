"""N1 -> Router -> Eligibility -> Tower (N3/N4) -> `DecisionRequest` -> EV -> N6, for ONE real closed bar,
against the full canonical catalog (CEO Mandate 2 step 5, 2026-08-14; tower wiring added Phase 2 step 5,
2026-08-14). This is the FIRST place in `ai_trader` that constructs a `ve_brain.DecisionRequest` from real
live data -- nothing here is a fixture.

**One structural gap remains, disclosed here rather than papered over** (see `probability_source.py` for
the full detail): `probability_inputs` is always `None` -- no validated per-regime outcome-count table
exists yet.

**`market_map_available`/`levels_available`/`confirmation_available` are now REAL** when `tower=` is
supplied (see `TowerDependencies` below) -- sourced from `ve_tower` 0.3.0's own `run_n3`/`run_n4`, called
once per bar (not once per catalog strategy: N3/N4's actual computation does not depend on strategy
identity -- see `_query_tower`'s own docstring) via the isolated tower worker over the versioned IPC
boundary. `tower=None` (the default, and every call site before this Phase-2 wiring) keeps all three
`False`, byte-for-byte the pre-Phase-2 behavior -- never `True` without a genuine `ve_tower` answer.

**Consequence, stated plainly and covered by this package's own tests**: with `tower=None` (or the tower
genuinely unavailable), `decide_n6` returns `NO_TRADE` for every real event, terminal reason
`MISSING_LEVEL_INPUT` for any strategy that survives eligibility+catalog checks. This is the CORRECT,
EXPECTED behavior of a SHADOW-only integration proving the wiring itself, not producing trades -- not a
defect. With a real, available tower answer, the SAME reason can now genuinely clear for the first time --
still gated entirely by `ve_brain.decide_n6`'s own EV/probability logic, never bypassed here.

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

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.live_signal_source.types import Bar, BarFeedError
from ai_trader.mandate2_readiness.decision_provenance import NEW_BRAIN_SOURCE, DecisionProvenance
from ai_trader.mandate2_readiness.event_identity import EventIdentity, NodeTrace
from ai_trader.new_brain_bridge.probability_source import load_probability_inputs
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tower_bar_source import fetch_tower_bar_windows
from ai_trader.new_brain_bridge.tower_client import TowerClient, TowerUnavailableResult
from ai_trader.new_brain_bridge.tower_protocol import PROTOCOL_VERSION, REQUEST_SCHEMA_VERSION, TowerRequest

_PLACEHOLDER_TARGET_RR = 2.0
_ELIGIBILITY_POLICY_VERSION = "eligibility-v1"
_SHARED_TOWER_STRATEGY_ID = "tower-shared-n3n4-probe"
_SHARED_TOWER_STRATEGY_VERSION = "1.0"
"""N3/N4's own computation never reads `strategy_id`/`strategy_version` (see `ve_tower.n4.run_n4` -- they
enter only the node's own identity/audit fingerprint) -- one shared, clearly-labeled identity is used for
ONE tower call per bar, reused across every catalog strategy, rather than N (catalog size) IDENTICAL calls
that would only differ in an unused label. If a strategy-specific level-selection policy is ever needed,
this is the seam to change -- not something today's `ve_tower` API or catalog gives a reason to build yet
(every entry in `ve_brain.CANONICAL_STRATEGIES` is `allowed_directions=("LONG",)`, so every strategy would
share the same side regardless)."""


@dataclass(frozen=True, slots=True, kw_only=True)
class TowerDependencies:
    """Everything `evaluate_bar` needs to make ONE real tower call for the whole bar. `client` must
    already be bound to an `EstablishedSession` (`TowerWorkerLauncher.launch_and_handshake` ->
    `TowerClient(session=...)`) -- session lifecycle (launch once at process start, re-handshake on
    worker restart/crash) is the CALLER's responsibility, not this module's; `evaluate_bar` never spawns
    or manages the worker process itself, matching every other injected dependency in this file."""

    client: TowerClient
    gateway: MT5Gateway
    now: int
    broker_offset_seconds: int = 0
    m15_count: int = 150
    m5_count: int = 300


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


@dataclass(frozen=True, slots=True, kw_only=True)
class _TowerQueryResult:
    market_map_available: bool
    levels_available: bool
    confirmation_available: bool
    reason_codes: tuple[str, ...]
    tower_version: str


def _query_tower(
    tower: TowerDependencies, *, market_event_id: str, symbol: str, as_of: int,
    n1_available: bool, n1_fingerprint: str, bias_direction: str | None,
) -> _TowerQueryResult:
    """ONE call per bar, shared across the whole catalog -- see `_SHARED_TOWER_STRATEGY_ID`'s own
    docstring for why this is correct rather than a shortcut. Fetches M15/M5 history fresh (read-only,
    `tower_bar_source.fetch_tower_bar_windows`), sends ONE `TowerRequest`, and reduces whatever comes
    back to the three booleans `evaluate_bar` needs -- fail-closed (all `False`) on ANY failure mode:
    bar-fetch failure, no established session, connection failure, protocol mismatch, or `ve_tower`
    itself reporting unavailable. Never raises -- a tower failure must degrade to `NO_TRADE`
    (`MISSING_LEVEL_INPUT`), never crash the bar-evaluation loop."""
    try:
        m15_bars, m5_bars = fetch_tower_bar_windows(
            tower.gateway, symbol=symbol, now=tower.now, broker_offset_seconds=tower.broker_offset_seconds,
            m15_count=tower.m15_count, m5_count=tower.m5_count,
        )
    except BarFeedError as exc:
        return _TowerQueryResult(
            market_map_available=False, levels_available=False, confirmation_available=False,
            reason_codes=(f"TOWER_BAR_FETCH_FAILED:{exc}",), tower_version="UNAVAILABLE",
        )

    n2_output: dict[str, object] = {
        "available": bias_direction is not None,
        "fingerprint": _fp(market_event_id, "n2", str(bias_direction)),
    }
    if bias_direction is not None:
        n2_output["bias_direction"] = bias_direction

    request = TowerRequest(
        protocol_version=PROTOCOL_VERSION, schema_version=REQUEST_SCHEMA_VERSION,
        request_id=_fp(market_event_id, "tower-request"), market_event_id=market_event_id,
        event_fingerprint="", data_identity=_fp(market_event_id, "data-identity"),
        node_input_fingerprint=_fp(market_event_id, "node-input"),
        symbol=symbol, as_of=str(as_of),
        n1_output={"available": n1_available, "fingerprint": n1_fingerprint},
        n2_output=n2_output, m15_closed_bars=m15_bars, m5_closed_bars=m5_bars,
        strategy_id=_SHARED_TOWER_STRATEGY_ID, strategy_version=_SHARED_TOWER_STRATEGY_VERSION,
    )
    result = tower.client.request_n3_n4(request)
    if isinstance(result, TowerUnavailableResult):
        return _TowerQueryResult(
            market_map_available=False, levels_available=False, confirmation_available=False,
            reason_codes=(result.reason,), tower_version="UNAVAILABLE",
        )

    n3 = result.n3_output or {}
    n4 = result.n4_output or {}
    market_map_available = n3.get("market_map_available") is True
    levels_available = n3.get("levels_available") is True
    confirmation_available = n4.get("confirmation_available") is True
    return _TowerQueryResult(
        market_map_available=market_map_available, levels_available=levels_available,
        confirmation_available=confirmation_available, reason_codes=result.reason_codes,
        tower_version=result.tower_version,
    )


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
    tower: TowerDependencies | None = None,
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

    _tower_result_cache: list[_TowerQueryResult] = []

    def _get_tower_result() -> _TowerQueryResult:
        """Lazy, memoized within this ONE `evaluate_bar` call -- computed only if/when the first
        eligible, geometry-complete strategy actually needs it, never for a bar where every strategy is
        ineligible or `atr`/`entry_price` are still `None`."""
        assert tower is not None  # only ever called from the `tower is not None` branch below
        if not _tower_result_cache:
            _tower_result_cache.append(_query_tower(
                tower, market_event_id=market_event_id, symbol=bar.symbol, as_of=bar.ts_close,
                n1_available=True, n1_fingerprint=n1_output_fp, bias_direction=bias_direction,
            ))
        return _tower_result_cache[0]

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

        if tower is not None:
            tower_result = _get_tower_result()
            traces.append(NodeTrace(
                trace_id=trace_id, node_name="Tower", input_fingerprint=_fp(market_event_id, "tower"),
                output=_fp(str(tower_result.market_map_available), str(tower_result.levels_available),
                           str(tower_result.confirmation_available)),
                reason_codes=tower_result.reason_codes, latency_seconds=0.0,
                component_version=tower_result.tower_version,
            ))
        else:
            tower_result = _TowerQueryResult(
                market_map_available=False, levels_available=False, confirmation_available=False,
                reason_codes=("TOWER_NOT_WIRED",), tower_version="UNAVAILABLE",
            )

        candidate = ve_brain.DecisionRequest(
            contract_id=ve_brain.INPUT_CONTRACT_ID,
            strategy_id=canon.strategy_id, strategy_version=canon.strategy_version,
            validation_status=canon.validation_status, strategy_family=canon.strategy_family,
            strategy_policy_fingerprint=ve_brain.strategy_policy_fingerprint(canon),
            market_event_id=market_event_id, regime_fingerprint=eligibility.regime_fingerprint,
            market_state_ref=n1_output_fp, regime_label=regime_label, bias_direction=bias_direction,
            market_map_available=tower_result.market_map_available,
            levels_available=tower_result.levels_available,
            confirmation_available=tower_result.confirmation_available,
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
