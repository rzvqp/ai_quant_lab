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
import json
import time
from dataclasses import dataclass, replace

import ve_brain  # type: ignore[import-untyped]  # external VE artifact, no py.typed marker -- never modified

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.live_signal_source.types import Bar, BarFeedError
from ai_trader.mandate2_readiness.decision_provenance import NEW_BRAIN_SOURCE, DecisionProvenance
from ai_trader.mandate2_readiness.event_identity import EventIdentity, NodeTrace
from ai_trader.mandate2_readiness.shadow_cost_model import (
    CALIBRATION_STATUS,
    SHADOW_COST_MODEL_VERSION,
    CostComponents,
    CostModelUnavailableError,
)
from ai_trader.mandate2_readiness.shadow_cost_model import configuration_fingerprint as cost_model_configuration_fingerprint
from ai_trader.mandate2_readiness.shadow_cost_model import is_within_provenance_window, resolve_cost_components
from ai_trader.new_brain_bridge.probability_source import load_probability_inputs
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tower_bar_source import (
    BAR_SECONDS_M5,
    BAR_SECONDS_M15,
    detect_gaps,
    fetch_tower_bar_windows,
)
from ai_trader.new_brain_bridge.tower_client import TowerClient, TowerUnavailableResult
from ai_trader.new_brain_bridge.tower_protocol import PROTOCOL_VERSION, REQUEST_SCHEMA_VERSION, TowerRequest

_PLACEHOLDER_TARGET_RR = 2.0
_ELIGIBILITY_POLICY_VERSION = "eligibility-v1"
_COST_MODEL_UNAVAILABLE = "COST_MODEL_UNAVAILABLE"
_COST_MODEL_FINGERPRINT_MISMATCH = "COST_MODEL_FINGERPRINT_MISMATCH"
_COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW = "COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW"
"""CEO correction, 2026-08-16: `bridge.py` no longer hardcodes `full_spread_price`/`entry_slippage_price`/
`exit_slippage_price` -- every `DecisionRequest` built here consumes
`mandate2_readiness.shadow_cost_model.resolve_cost_components(tier="BASE")` exclusively. A missing/
unavailable model (`CostModelUnavailableError`) OR a caller-pinned `expected_cost_model_fingerprint` that
doesn't match `shadow_cost_model.configuration_fingerprint()` both degrade EVERY strategy for that bar to
`decision=None` (this codebase's own NO_TRADE-equivalent, matching `ATR_HISTORY_INSUFFICIENT`'s own
established shape) -- never a local calculator, never a manual copy, never `0.0` as a silent fallback.
`_COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW` is NON-blocking (a real decision still proceeds) but is
always disclosed on the `CostModel` node trace when `bar.ts_close`'s own UTC calendar day falls outside
`shadow_cost_model.COST_PROVENANCE_WINDOW`'s exact observed day-set -- true for essentially every live
bar today, since the window is 4 specific days in the past. Applying the ratified cost model outside its
own provenance window is disclosed, never silently treated as validating the strategy further."""
_SHARED_TOWER_STRATEGY_ID = "tower-shared-n3n4-probe"
_SHARED_TOWER_STRATEGY_VERSION = "1.0"
"""N3/N4's own computation never reads `strategy_id`/`strategy_version` (see `ve_tower.n4.run_n4` -- they
enter only the node's own identity/audit fingerprint) -- one shared, clearly-labeled identity is used for
ONE tower call per bar, reused across every catalog strategy, rather than N (catalog size) IDENTICAL calls
that would only differ in an unused label. If a strategy-specific level-selection policy is ever needed,
this is the seam to change -- not something today's `ve_tower` API or catalog gives a reason to build yet
(every entry in `ve_brain.CANONICAL_STRATEGIES` is `allowed_directions=("LONG",)`, so every strategy would
share the same side regardless)."""

_TOWER_IDENTITY_UNAVAILABLE = "TOWER_IDENTITY_UNAVAILABLE"
_TOWER_IDENTITY_MISMATCH = "TOWER_IDENTITY_MISMATCH"
"""Red Team RT-MANDATE2-0002 remediation, 2026-08-16: "Camp lipsa sau incompatibil: NO_TRADE /
TOWER_IDENTITY_UNAVAILABLE, fail-closed, fara fallback. Mismatch intre raspuns si cerere: NO_TRADE /
TOWER_IDENTITY_MISMATCH." A successful (`ok=True`) worker response is expected to carry, on BOTH `n3_output`
and (when present) `n4_output`: `contract_version`, `event_fingerprint`, `node_input_fingerprint`,
`data_identity`. Missing any of these on a node that IS present degrades that whole query to
`TOWER_IDENTITY_UNAVAILABLE` (all three tower booleans forced `False`) -- never silently treated as
available with an absent identity. When both N3 and N4 are present, their `event_fingerprint`s are expected
to AGREE (same `market_event_id`, same underlying event) -- disagreement is `TOWER_IDENTITY_MISMATCH`, also
fail-closed. `node_input_fingerprint`/`data_identity` are DELIBERATELY never compared against each other
(N3 answers on M15, N4 on M5 -- see `_TowerQueryResult`'s own docstring): only `event_fingerprint` is the
shared correlation key."""


def _opt_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _canonical_data_identity(data_identity: object) -> str | None:
    """`ve_tower`'s own `DataIdentity` arrives here as an already-JSON-decoded dict (the wire format is
    opaque JSON, per `tower_client.py`'s own "does not interpret contents" convention) -- canonicalized
    (sorted keys) so the SAME identity always serializes to the SAME string, never re-derived or
    recomputed, only re-serialized for storage on a `NodeTrace`/`EventIdentity`'s own string fields."""
    if not isinstance(data_identity, dict):
        return None
    return json.dumps(data_identity, sort_keys=True, separators=(",", ":"))


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
    max_staleness_s: int | None = 2 * 900
    """Threaded into the `TowerRequest`'s own `max_staleness_s` (`ve_tower`'s real `DATA_STALE` gate) --
    default two M15 bar periods (30 min), generous slack for ordinary polling latency while still
    catching a genuinely stale snapshot (a worker that hasn't seen fresh bars in far longer than one
    normal poll cycle). `None` disables the check entirely, matching the pre-2026-08-16 behavior."""


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
    """`market_map_available`/`levels_available`/`confirmation_available` are the ONLY fields the pre-
    RT-MANDATE2-0002 version of this type carried -- every field below is new, and every value is copied
    verbatim from the worker's own verified response, never recomputed locally. `n3_*`/`n4_*` stay
    DISTINCT (never merged into one "tower identity"): N3 answers on M15, N4 on M5, so their
    `data_identity`/`node_input_fingerprint` are legitimately different for the same event -- only
    `event_fingerprint` is expected to agree between them (the shared correlation key for this event)."""

    market_map_available: bool
    levels_available: bool
    confirmation_available: bool
    reason_codes: tuple[str, ...]
    tower_version: str
    worker_session_id: str | None = None
    worker_identity_fingerprint: str | None = None
    n3_contract_version: str | None = None
    n3_code_version: str | None = None
    n3_event_fingerprint: str | None = None
    n3_node_input_fingerprint: str | None = None
    n3_data_identity: str | None = None
    n4_contract_version: str | None = None
    n4_code_version: str | None = None
    n4_event_fingerprint: str | None = None
    n4_node_input_fingerprint: str | None = None
    n4_data_identity: str | None = None


def _query_tower(
    tower: TowerDependencies, *, market_event_id: str, symbol: str, as_of: int,
    n1_available: bool, n1_fingerprint: str, bias_direction: str | None, n1_axes_direction: str,
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

    gap_reason_codes = tuple(
        f"GAP_DETECTED:M15:{gap.classification.value}:{gap.duration_seconds}s"
        for gap in detect_gaps(m15_bars, symbol=symbol, bar_seconds=BAR_SECONDS_M15)
    ) + tuple(
        f"GAP_DETECTED:M5:{gap.classification.value}:{gap.duration_seconds}s"
        for gap in detect_gaps(m5_bars, symbol=symbol, bar_seconds=BAR_SECONDS_M5)
    )
    # Test 05 (Mandate B point 5): a gap in the window fed to the tower must be VISIBLE, never silently
    # absorbed -- reported here on the Tower NodeTrace's own reason_codes, never used to block or repair
    # the request itself (ve_tower's own `_bars_closed_and_ordered` check only rejects non-ascending
    # order, not a gap in an otherwise-ascending sequence -- gaps are a real, common, non-fatal event,
    # e.g. weekend closures, and reporting one is not the same as refusing to proceed).

    n2_output: dict[str, object] = {
        "available": bias_direction is not None,
        "fingerprint": _fp(market_event_id, "n2", str(bias_direction), str(n1_axes_direction)),
    }
    if bias_direction is not None:
        n2_output["bias_direction"] = bias_direction
    """No independently-versioned N2 contract exists anywhere in the installed real artifacts -- confirmed
    empirically (2026-08-16, Red Team RT-MANDATE2-0002): neither `ve_brain` (only `N1_CONTRACT_VERSION`
    exists) nor `ve_tower` (only `N3_CONTRACT_VERSION`/`N4_CONTRACT_VERSION` exist) define an `N2` contract
    version, and `N3Response`/`N4Response` never echo an `n2_fingerprint` back for verification -- `n2_
    fingerprint` is a REQUIRED INPUT FIELD on `N3Request`/`N4Request` the CALLER asserts, unchecked and
    unvalidated by `ve_tower` itself. This fingerprint now folds in `n1_axes_direction` (the REAL, N1-
    computed `RawAxes.direction`) alongside the caller-supplied `bias_direction` -- an honest strengthening,
    NOT a claim that a real, independently-contracted N2 stage exists. Per the CEO's own explicit rule
    ("Nu inventa local un N2 pentru a obtine PASS"), this gap is disclosed, never papered over."""

    request = TowerRequest(
        protocol_version=PROTOCOL_VERSION, schema_version=REQUEST_SCHEMA_VERSION,
        request_id=_fp(market_event_id, "tower-request"), market_event_id=market_event_id,
        event_fingerprint="", data_identity=_fp(market_event_id, "data-identity"),
        node_input_fingerprint=_fp(market_event_id, "node-input"),
        symbol=symbol, as_of=str(as_of),
        n1_output={"available": n1_available, "fingerprint": n1_fingerprint},
        n2_output=n2_output, m15_closed_bars=m15_bars, m5_closed_bars=m5_bars,
        strategy_id=_SHARED_TOWER_STRATEGY_ID, strategy_version=_SHARED_TOWER_STRATEGY_VERSION,
        max_staleness_s=tower.max_staleness_s,
    )
    result = tower.client.request_n3_n4(request)
    if isinstance(result, TowerUnavailableResult):
        return _TowerQueryResult(
            market_map_available=False, levels_available=False, confirmation_available=False,
            reason_codes=gap_reason_codes + (result.reason,), tower_version="UNAVAILABLE",
        )

    n3 = result.n3_output or {}
    n4 = result.n4_output or {}
    market_map_available = n3.get("market_map_available") is True
    levels_available = n3.get("levels_available") is True
    confirmation_available = n4.get("confirmation_available") is True

    # Red Team RT-MANDATE2-0002 remediation, 2026-08-16: extract the worker's own REAL per-node identity
    # (never fabricated) instead of discarding everything but the three booleans above.
    n3_contract_version = _opt_str(n3.get("contract_version"))
    n3_code_version = _opt_str(n3.get("n3_version"))
    n3_event_fingerprint = _opt_str(n3.get("event_fingerprint"))
    n3_node_input_fingerprint = _opt_str(n3.get("node_input_fingerprint"))
    n3_data_identity = _canonical_data_identity(n3.get("data_identity"))
    n4_contract_version = _opt_str(n4.get("contract_version"))
    n4_code_version = _opt_str(n4.get("n4_version"))
    n4_event_fingerprint = _opt_str(n4.get("event_fingerprint"))
    n4_node_input_fingerprint = _opt_str(n4.get("node_input_fingerprint"))
    n4_data_identity = _canonical_data_identity(n4.get("data_identity"))

    identity_reason_codes: tuple[str, ...] = ()
    n3_identity_complete = (
        n3_contract_version is not None and n3_event_fingerprint is not None
        and n3_node_input_fingerprint is not None and n3_data_identity is not None
    )
    if result.n3_output is not None and not n3_identity_complete:
        identity_reason_codes += (_TOWER_IDENTITY_UNAVAILABLE,)
    if result.n4_output is not None:
        n4_identity_complete = (
            n4_contract_version is not None and n4_event_fingerprint is not None
            and n4_node_input_fingerprint is not None and n4_data_identity is not None
        )
        if not n4_identity_complete:
            identity_reason_codes += (_TOWER_IDENTITY_UNAVAILABLE,)
        elif n3_identity_complete and n3_event_fingerprint != n4_event_fingerprint:
            identity_reason_codes += (_TOWER_IDENTITY_MISMATCH,)

    if identity_reason_codes:
        # Fail-closed: an incomplete or mismatched identity means this answer cannot be trusted as
        # genuinely belonging to a single, correlated event -- never surfaced as available with an
        # unverifiable or contradictory identity attached.
        return _TowerQueryResult(
            market_map_available=False, levels_available=False, confirmation_available=False,
            reason_codes=gap_reason_codes + result.reason_codes + identity_reason_codes,
            tower_version=result.tower_version,
        )

    return _TowerQueryResult(
        market_map_available=market_map_available, levels_available=levels_available,
        confirmation_available=confirmation_available,
        reason_codes=gap_reason_codes + result.reason_codes,
        tower_version=result.tower_version,
        worker_session_id=result.session_id, worker_identity_fingerprint=result.worker_identity_fingerprint,
        n3_contract_version=n3_contract_version, n3_code_version=n3_code_version,
        n3_event_fingerprint=n3_event_fingerprint, n3_node_input_fingerprint=n3_node_input_fingerprint,
        n3_data_identity=n3_data_identity,
        n4_contract_version=n4_contract_version, n4_code_version=n4_code_version,
        n4_event_fingerprint=n4_event_fingerprint, n4_node_input_fingerprint=n4_node_input_fingerprint,
        n4_data_identity=n4_data_identity,
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
    expected_cost_model_fingerprint: str | None = None,
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

    cost_components: CostComponents | None
    cost_unavailable_reason_codes: tuple[str, ...]
    if (expected_cost_model_fingerprint is not None
            and expected_cost_model_fingerprint != cost_model_configuration_fingerprint()):
        cost_components = None
        cost_unavailable_reason_codes = (_COST_MODEL_FINGERPRINT_MISMATCH,)
    else:
        try:
            cost_components = resolve_cost_components(tier="BASE")
            cost_unavailable_reason_codes = ()
        except CostModelUnavailableError as exc:
            cost_components = None
            cost_unavailable_reason_codes = (_COST_MODEL_UNAVAILABLE, str(exc))
    cost_extrapolated_outside_window = not is_within_provenance_window(bar.ts_close)
    """Non-blocking: `True` for essentially every real live bar today (the ratified provenance window is
    4 specific past calendar days) -- disclosed on the `CostModel` node trace below, never silently
    treated as validating anything further about the strategy."""

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
                n1_axes_direction=str(axes.direction),
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

        if atr is None or entry_price is None or cost_components is None:
            missing_reasons: list[str] = []
            if atr is None or entry_price is None:
                missing_reasons.append("ATR_HISTORY_INSUFFICIENT")
            if cost_components is None:
                missing_reasons.extend(cost_unavailable_reason_codes)
            traces.append(NodeTrace(
                trace_id=trace_id, node_name="N6", input_fingerprint=_fp(trace_id, "no-geometry"),
                output="", reason_codes=tuple(missing_reasons), latency_seconds=0.0,
                component_version=ve_brain.ENGINE_VERSION,
            ))
            outcomes.append(NewBrainOutcome(
                event_identity=event_identity, strategy_id=canon.strategy_id,
                strategy_version=canon.strategy_version, node_traces=tuple(traces), decision=None,
                provenance=None,
            ))
            continue

        traces.append(NodeTrace(
            trace_id=trace_id, node_name="CostModel", input_fingerprint=cost_model_configuration_fingerprint(),
            output=_fp(str(cost_components.full_spread_price), str(cost_components.entry_slippage_price),
                       str(cost_components.exit_slippage_price)),
            reason_codes=(_COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW,) if cost_extrapolated_outside_window else (),
            latency_seconds=0.0, component_version=f"{SHADOW_COST_MODEL_VERSION}:{CALIBRATION_STATUS}",
        ))

        stop_price = entry_price - atr
        regime_label = eligibility.matched_regimes[0] if eligibility.matched_regimes else None
        probability_inputs = load_probability_inputs(canon.strategy_id, canon.strategy_version)

        if tower is not None:
            tower_result = _get_tower_result()
            # Red Team RT-MANDATE2-0002 remediation, 2026-08-16: ONE "Tower" trace with a locally-
            # fabricated `_fp(market_event_id, "tower")` input replaced with TWO traces -- "TowerN3"
            # (M15) and "TowerN4" (M5) -- each carrying the worker's own REAL, verified identity, never a
            # local guess. `TowerN4`'s `output` embeds `n3_event_fingerprint` alongside its own, making
            # the N4->N3 response linkage independently checkable straight from the persisted trace.
            traces.append(NodeTrace(
                trace_id=trace_id, node_name="TowerN3",
                input_fingerprint=tower_result.n3_node_input_fingerprint or _fp(market_event_id, "n3-unavailable"),
                output=_fp(str(tower_result.market_map_available), str(tower_result.levels_available),
                           tower_result.n3_event_fingerprint or ""),
                reason_codes=tower_result.reason_codes, latency_seconds=0.0,
                component_version=tower_result.n3_contract_version or tower_result.tower_version,
            ))
            traces.append(NodeTrace(
                trace_id=trace_id, node_name="TowerN4",
                input_fingerprint=tower_result.n4_node_input_fingerprint or _fp(market_event_id, "n4-unavailable"),
                output=_fp(str(tower_result.confirmation_available), tower_result.n4_event_fingerprint or "",
                           tower_result.n3_event_fingerprint or ""),
                reason_codes=tower_result.reason_codes, latency_seconds=0.0,
                component_version=tower_result.n4_contract_version or tower_result.tower_version,
            ))
            event_identity = replace(
                event_identity,
                worker_session_id=tower_result.worker_session_id,
                worker_identity_fingerprint=tower_result.worker_identity_fingerprint,
                tower_version=tower_result.tower_version,
                n3_contract_version=tower_result.n3_contract_version,
                n3_code_version=tower_result.n3_code_version,
                n3_event_fingerprint=tower_result.n3_event_fingerprint,
                n3_node_input_fingerprint=tower_result.n3_node_input_fingerprint,
                n3_data_identity=tower_result.n3_data_identity,
                n4_contract_version=tower_result.n4_contract_version,
                n4_code_version=tower_result.n4_code_version,
                n4_event_fingerprint=tower_result.n4_event_fingerprint,
                n4_node_input_fingerprint=tower_result.n4_node_input_fingerprint,
                n4_data_identity=tower_result.n4_data_identity,
            )
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
            probability_inputs=probability_inputs,
            full_spread_price=cost_components.full_spread_price,
            entry_slippage_price=cost_components.entry_slippage_price,
            exit_slippage_price=cost_components.exit_slippage_price,
            symbol=bar.symbol, timeframe=timeframe, block_start=0,
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
