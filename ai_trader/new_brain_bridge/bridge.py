"""N1 -> Router -> Eligibility -> Tower chain (N2/N3/N4) -> `DecisionRequest` -> EV -> N6, for ONE real
closed bar, against the full canonical catalog (CEO Mandate 2 step 5, 2026-08-14; tower wiring added
Phase 2 step 5, 2026-08-14; chain-binding rewrite RT-TOWER-0008, 2026-08-17). This is the FIRST place in
`ai_trader` that constructs a `ve_brain.DecisionRequest` from real live data -- nothing here is a fixture.

**RT-TOWER-0008 (2026-08-17): the worker now runs a real `ve_tower.run_tower_chain` (N2+N3+N4 together)**,
`ve_tower` 0.5.0. N2 (bias, computed from real H1 bars) is a genuine, independently-contracted producer
INSIDE `ve_tower` -- this module no longer fabricates any N2 identity, no longer accepts a caller-supplied
`bias_direction` for the chain, and no longer defaults anything to `"LONG"`. `side` (the int the chain
needs, 1=LONG/-1=SHORT) is derived EXCLUSIVELY from the ELIGIBLE strategy's own contracted
`StrategyContract.allowed_directions[0]` -- never a module-level default, never an operator input, never
copied from N2's own output.

**`router_bias_direction` remains a SEPARATE, pre-existing `ve_brain.StrategyRouter.eligible` argument** --
an upstream regime-eligibility signal, unrelated to the tower chain's own `side`. No real, independently-
computed source for it exists yet upstream of the Router (that gap is disclosed, not invented around);
its default is honestly `None`, never a silently-assumed `"LONG"`.

**One structural gap remains, disclosed here rather than papered over** (see `probability_source.py` for
the full detail): `probability_inputs` is always `None` -- no validated per-regime outcome-count table
exists yet.

**`market_map_available`/`levels_available`/`confirmation_available` are now REAL** when `tower=` is
supplied (see `TowerDependencies` below) -- sourced from `ve_tower` 0.5.0's own `run_tower_chain`, called
once per (bar, side) -- not once per bar regardless of strategy, and not once per catalog strategy: N3/N4's
actual level computation does not depend on strategy identity, but N2/N4's SIDE does, so the memoization
key is `side`, not the bar alone. `tower=None` (the default) keeps all three `False`, byte-for-byte the
pre-Phase-2 behavior -- never `True` without a genuine `ve_tower` answer.

**Geometry is real-price-derived, not fabricated, but its SIZING CONVENTION is an explicit placeholder**:
`entry_price` is the real last close, `atr` is the real vendored ATR14 over the real accumulated bar
history (`RawAxesBuilder.atr14()`) -- both genuine numbers from genuine data. `stop_price` (`entry -
1xATR`, LONG-only, since every entry in `ve_brain.CANONICAL_STRATEGIES` has `allowed_directions=
("LONG",)`) and `target_param` (`_PLACEHOLDER_TARGET_RR = 2.0`) are a SIZING CONVENTION, not a validated
strategy rule -- they exist only so `ve_brain.validate_request` can be satisfied. Since gap 2 makes the
outcome `NO_TRADE` regardless of RR whenever the tower is genuinely unavailable, this convention has zero
effect on any decision produced by an unavailable tower."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, replace
from typing import Callable

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
    BAR_SECONDS_H1,
    BAR_SECONDS_M5,
    BAR_SECONDS_M15,
    detect_gaps,
    fetch_tower_chain_bar_windows,
)
from ai_trader.new_brain_bridge.tower_client import TowerClient, TowerUnavailableResult
from ai_trader.new_brain_bridge.tower_identity_pin import (
    EXPECTED_N2_CONTRACT_VERSION,
    EXPECTED_N3_CONTRACT_VERSION,
    EXPECTED_N4_CONTRACT_VERSION,
)
from ai_trader.new_brain_bridge.tower_protocol import PROTOCOL_VERSION, REQUEST_SCHEMA_VERSION, TowerChainRequest
from ai_trader.new_brain_bridge.wall_clock import ClockRollbackError

_PLACEHOLDER_TARGET_RR = 2.0
_FUTURE_EVENT_REJECTED = "FUTURE_EVENT_REJECTED"
_WALL_CLOCK_ROLLBACK_DETECTED = "WALL_CLOCK_ROLLBACK_DETECTED"
_ELIGIBILITY_POLICY_VERSION = "eligibility-v1"
_COST_MODEL_UNAVAILABLE = "COST_MODEL_UNAVAILABLE"
_COST_MODEL_FINGERPRINT_MISMATCH = "COST_MODEL_FINGERPRINT_MISMATCH"
_COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW = "COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW"
"""CEO correction, 2026-08-16: `bridge.py` no longer hardcodes `full_spread_price`/`entry_slippage_price`/
`exit_slippage_price` -- every `DecisionRequest` built here consumes
`mandate2_readiness.shadow_cost_model.resolve_cost_components(tier="BASE")` exclusively. A missing/
unavailable model (`CostModelUnavailableError`) OR a caller-pinned `expected_cost_model_fingerprint` that
doesn't match `shadow_cost_model.configuration_fingerprint()` both degrade EVERY strategy for that bar to
`decision=None` -- never a local calculator, never a manual copy, never `0.0` as a silent fallback."""

_TOWER_IDENTITY_UNAVAILABLE = "TOWER_IDENTITY_UNAVAILABLE"
_TOWER_IDENTITY_MISMATCH = "TOWER_IDENTITY_MISMATCH"
_N2_UNAVAILABLE = "N2_UNAVAILABLE"
_N3_UNAVAILABLE = "N3_UNAVAILABLE"
_N4_UNAVAILABLE = "N4_UNAVAILABLE"
_CHAIN_IDENTITY_MISMATCH = "CHAIN_IDENTITY_MISMATCH"
"""RT-TOWER-0008 remediation, 2026-08-17 (CEO section 5): "N2 indisponibil: NO_TRADE / N2_UNAVAILABLE. N3
indisponibil: NO_TRADE / N3_UNAVAILABLE. N4 indisponibil: NO_TRADE / N4_UNAVAILABLE. Chain identity
mismatch: NO_TRADE / CHAIN_IDENTITY_MISMATCH." A successful (`ok=True`) chain response is expected to
carry, on every node that IS present, its own `contract_version`/`event_fingerprint`/
`node_input_fingerprint`/`data_identity` -- missing any of these degrades to `TOWER_IDENTITY_UNAVAILABLE`.
`n2`/`n3`/`n4` event_fingerprints are expected to AGREE (same underlying market event) -- disagreement is
`CHAIN_IDENTITY_MISMATCH`. `node_input_fingerprint`/`data_identity` are DELIBERATELY never compared
against each other across nodes: N2 answers on H1, N3 on M15, N4 on M5 -- distinct data, distinct
identity, per the CEO's own explicit rule ("Nu forta identitatile per nod sa fie egale")."""


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
    """Everything `evaluate_bar` needs to make real tower chain calls (at most one per distinct `side`
    actually needed this bar). `client` must already be bound to an `EstablishedSession`
    (`TowerWorkerLauncher.launch_and_handshake` -> `TowerClient(session=...)`) -- session lifecycle
    (launch once at process start, re-handshake on worker restart/crash) is the CALLER's responsibility,
    not this module's; `evaluate_bar` never spawns or manages the worker process itself."""

    client: TowerClient
    gateway: MT5Gateway
    broker_offset_seconds: int = 0
    h1_count: int = 150
    m15_count: int = 150
    m5_count: int = 300
    h1_max_staleness_s: int | None = 2 * 3600
    m15_max_staleness_s: int | None = 2 * 900
    m5_max_staleness_s: int | None = 2 * 300
    """Threaded into the `TowerChainRequest`'s own per-timeframe `*_max_staleness_s` (`ve_tower`'s real
    `DATA_STALE` gate) -- each defaults to two bar periods of slack for ordinary polling latency while
    still catching a genuinely stale snapshot. `None` disables the check for that timeframe entirely."""
    wall_clock_provider: Callable[[], float] = time.time
    """RT-TIME-0001 section A (2026-08-17) remediation: replaces the former `now: int` field, which was
    captured ONCE (`int(time.time())`) at `TowerDependencies` construction time and then reused,
    unchanged, for every tower-chain bar fetch for the rest of that process's life -- the exact defect
    `LIVE_SHADOW_TIMEFRAME_AUDIT.md` (commit `85e2051`) found causes N4/N3/N2 to fail `DATA_STALE`
    roughly 10/30/120 minutes after any process start, permanently, until the next restart. `bar-fetch
    data selection now uses `event_as_of`/`data_cutoff` (per-call, derived from the bar actually being
    evaluated -- see `_query_tower_chain`), NEVER this field. `wall_clock_provider` exists ONLY to answer
    "what time is it right now" for health/staleness/latency reporting on the trace -- called FRESH on
    every single call, never cached, never reused across calls. Defaults to the real `time.time`; a
    caller wanting rollback detection should inject a `wall_clock.MonotonicWallClock()` instance
    instead."""


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


def _side_from_strategy(canon: ve_brain.StrategyContract) -> int:
    """RT-TOWER-0008 (2026-08-17, CEO section 3): `side` MUST come from the strategy the Router has
    already deemed eligible -- specifically its own contracted `allowed_directions[0]`, never a default,
    never an operator input, never a fixture, never `bias_direction`, never copied from N2's own output.
    Every entry in `ve_brain.CANONICAL_STRATEGIES` is `allowed_directions=("LONG",)` today -- `side=1` for
    all of them is a genuine fact read from the catalog, not a bridge.py-level constant."""
    return 1 if canon.allowed_directions[0] == "LONG" else -1


def _side_provenance(canon: ve_brain.StrategyContract) -> str:
    return f"StrategyContract.allowed_directions[0]={canon.allowed_directions[0]!r} (strategy_id={canon.strategy_id!r})"


@dataclass(frozen=True, slots=True, kw_only=True)
class _ChainQueryResult:
    """Every field here is copied verbatim from the worker's own verified `ve_tower.run_tower_chain`
    response, never fabricated locally. `n2_*`/`n3_*`/`n4_*` stay DISTINCT (never merged into one "tower
    identity"): N2 answers on H1, N3 on M15, N4 on M5, so their `data_identity`/`node_input_fingerprint`
    are legitimately different for the same event -- only `event_fingerprint` is expected to agree across
    all three (the shared correlation key for this event)."""

    market_map_available: bool
    levels_available: bool
    confirmation_available: bool
    bias_available: bool
    reason_codes: tuple[str, ...]
    tower_version: str
    side: int
    worker_session_id: str | None = None
    worker_identity_fingerprint: str | None = None
    chain_binding_version: str | None = None
    chain_response_contract_version: str | None = None
    chain_fingerprint: str | None = None
    chain_status: str | None = None
    terminal_reason_code: str | None = None
    n2_contract_version: str | None = None
    n2_code_version: str | None = None
    n2_event_fingerprint: str | None = None
    n2_node_input_fingerprint: str | None = None
    n2_data_identity: str | None = None
    n2_output_fingerprint: str | None = None
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

    # -- Request-scoped time fields (RT-TIME-0001 section A) -- see `EventIdentity`'s own docstring for
    # the exact meaning of each; `_query_tower_chain` populates every one of these on EVERY return path
    # (including every fail-closed one), never only on success.
    event_as_of: int | None = None
    data_cutoff: int | None = None
    wall_clock_now: int | None = None
    last_closed_h1: int | None = None
    last_closed_m15: int | None = None
    last_closed_m5: int | None = None
    fetch_timestamp: int | None = None
    staleness_reason_h1: str | None = None
    staleness_reason_m15: str | None = None
    staleness_reason_m5: str | None = None


def _last_closed_ts(bars: tuple[dict[str, object], ...], *, bar_seconds: int) -> int | None:
    """`ts_close` of the most recent bar in an already-sorted-oldest-first window, or `None` if empty."""
    if not bars:
        return None
    last_time = bars[-1]["time"]
    assert isinstance(last_time, int)
    return last_time + bar_seconds


def _staleness_reason(*, event_as_of: int, last_closed: int | None, max_staleness_s: int | None) -> str:
    """Bridge-side, INFORMATIONAL echo of the same staleness math `ve_tower`'s own `DATA_STALE` gate
    independently performs (`ve_tower/n2.py`/`n3.py`/`n4.py`: `(req.as_of - req.time[-1]) >
    max_staleness_s`) -- never the authority for the actual availability decision (that stays entirely
    `ve_tower`'s own, unchanged by this fix), only for the trace's own audit fields."""
    if last_closed is None:
        return "NO_BARS_FETCHED"
    age = event_as_of - last_closed
    if max_staleness_s is not None and age > max_staleness_s:
        return f"STALE:{age}s"
    return f"OK:{age}s"


def _query_tower_chain(
    tower: TowerDependencies, *, market_event_id: str, trace_id: str, symbol: str,
    event_as_of: int, data_cutoff: int,
    configuration_fingerprint: str, n1_fingerprint: str, regime_axes_status: tuple[str, ...],
    strategy_id: str, strategy_version: str, side: int,
) -> _ChainQueryResult:
    """ONE chain call per distinct `side` actually needed this bar (memoized by the caller -- see
    `evaluate_bar`'s own `_get_chain_result`). Fetches H1/M15/M5 history fresh (read-only,
    `tower_bar_source.fetch_tower_chain_bar_windows`), sends ONE `TowerChainRequest`, and reduces whatever
    comes back to the booleans `evaluate_bar` needs plus the full real identity -- fail-closed (all
    `False`) on ANY failure mode: bar-fetch failure, no established session, connection failure, protocol
    mismatch, contract-expectation mismatch, or `ve_tower` itself reporting the chain unavailable. Never
    raises -- a tower failure must degrade to `NO_TRADE`, never crash the bar-evaluation loop.

    **RT-TIME-0001 section A**: `event_as_of` is the bar/event actually being evaluated (`bar.ts_close`)
    -- never the process's own start time. `data_cutoff` is the most recent timestamp data may be drawn
    from, clamped here to never exceed `event_as_of` (the caller is expected to already pass
    `data_cutoff <= event_as_of`; this clamp is a defense-in-depth invariant, not the primary enforcement
    point). Bar selection uses `data_cutoff`, NEVER `wall_clock_now` and NEVER a value captured once at
    process start -- this is the exact fix for the frozen-`TowerDependencies.now` defect
    `LIVE_SHADOW_TIMEFRAME_AUDIT.md` found."""
    data_cutoff = min(data_cutoff, event_as_of)

    try:
        wall_clock_now = int(tower.wall_clock_provider())
    except ClockRollbackError as exc:
        return _ChainQueryResult(
            market_map_available=False, levels_available=False, confirmation_available=False,
            bias_available=False, reason_codes=(f"{_WALL_CLOCK_ROLLBACK_DETECTED}:{exc}",),
            tower_version="UNAVAILABLE", side=side, event_as_of=event_as_of, data_cutoff=data_cutoff,
        )

    if event_as_of > wall_clock_now:
        return _ChainQueryResult(
            market_map_available=False, levels_available=False, confirmation_available=False,
            bias_available=False,
            reason_codes=(f"{_FUTURE_EVENT_REJECTED}:event_as_of={event_as_of}:wall_clock_now={wall_clock_now}",),
            tower_version="UNAVAILABLE", side=side, event_as_of=event_as_of, data_cutoff=data_cutoff,
            wall_clock_now=wall_clock_now,
        )

    fetch_timestamp = wall_clock_now

    try:
        h1_bars, m15_bars, m5_bars = fetch_tower_chain_bar_windows(
            tower.gateway, symbol=symbol, now=data_cutoff, broker_offset_seconds=tower.broker_offset_seconds,
            h1_count=tower.h1_count, m15_count=tower.m15_count, m5_count=tower.m5_count,
        )
    except BarFeedError as exc:
        return _ChainQueryResult(
            market_map_available=False, levels_available=False, confirmation_available=False,
            bias_available=False, reason_codes=(f"TOWER_BAR_FETCH_FAILED:{exc}",), tower_version="UNAVAILABLE",
            side=side, event_as_of=event_as_of, data_cutoff=data_cutoff, wall_clock_now=wall_clock_now,
            fetch_timestamp=fetch_timestamp, staleness_reason_h1="NO_BARS_FETCHED",
            staleness_reason_m15="NO_BARS_FETCHED", staleness_reason_m5="NO_BARS_FETCHED",
        )

    last_closed_h1 = _last_closed_ts(h1_bars, bar_seconds=BAR_SECONDS_H1)
    last_closed_m15 = _last_closed_ts(m15_bars, bar_seconds=BAR_SECONDS_M15)
    last_closed_m5 = _last_closed_ts(m5_bars, bar_seconds=BAR_SECONDS_M5)
    staleness_reason_h1 = _staleness_reason(
        event_as_of=event_as_of, last_closed=last_closed_h1, max_staleness_s=tower.h1_max_staleness_s,
    )
    staleness_reason_m15 = _staleness_reason(
        event_as_of=event_as_of, last_closed=last_closed_m15, max_staleness_s=tower.m15_max_staleness_s,
    )
    staleness_reason_m5 = _staleness_reason(
        event_as_of=event_as_of, last_closed=last_closed_m5, max_staleness_s=tower.m5_max_staleness_s,
    )
    _time_fields: dict[str, object] = dict(
        event_as_of=event_as_of, data_cutoff=data_cutoff, wall_clock_now=wall_clock_now,
        last_closed_h1=last_closed_h1, last_closed_m15=last_closed_m15, last_closed_m5=last_closed_m5,
        fetch_timestamp=fetch_timestamp, staleness_reason_h1=staleness_reason_h1,
        staleness_reason_m15=staleness_reason_m15, staleness_reason_m5=staleness_reason_m5,
    )

    gap_reason_codes = tuple(
        f"GAP_DETECTED:H1:{gap.classification.value}:{gap.duration_seconds}s"
        for gap in detect_gaps(h1_bars, symbol=symbol, bar_seconds=BAR_SECONDS_H1)
    ) + tuple(
        f"GAP_DETECTED:M15:{gap.classification.value}:{gap.duration_seconds}s"
        for gap in detect_gaps(m15_bars, symbol=symbol, bar_seconds=BAR_SECONDS_M15)
    ) + tuple(
        f"GAP_DETECTED:M5:{gap.classification.value}:{gap.duration_seconds}s"
        for gap in detect_gaps(m5_bars, symbol=symbol, bar_seconds=BAR_SECONDS_M5)
    )
    # A gap in a window fed to the tower must be VISIBLE, never silently absorbed -- reported on the
    # relevant NodeTrace's own reason_codes, never used to block or repair the request itself.

    def _series(bars: tuple[dict[str, object], ...], field: str) -> tuple[float, ...]:
        return tuple(float(b[field]) for b in bars)  # type: ignore[arg-type]

    def _times(bars: tuple[dict[str, object], ...]) -> tuple[int, ...]:
        return tuple(int(b["time"]) for b in bars)  # type: ignore[call-overload]

    request = TowerChainRequest(
        protocol_version=PROTOCOL_VERSION, schema_version=REQUEST_SCHEMA_VERSION,
        request_id=_fp(market_event_id, str(side), "chain-request"), market_event_id=market_event_id,
        trace_id=trace_id, correlation_id=market_event_id, symbol=symbol, as_of=event_as_of,
        configuration_fingerprint=configuration_fingerprint, regime_axes_status=regime_axes_status,
        h1_open=_series(h1_bars, "open"), h1_high=_series(h1_bars, "high"), h1_low=_series(h1_bars, "low"),
        h1_close=_series(h1_bars, "close"), h1_time=_times(h1_bars),
        h1_source_identity=f"tower-client:{symbol}:H1",
        m15_open=_series(m15_bars, "open"), m15_high=_series(m15_bars, "high"), m15_low=_series(m15_bars, "low"),
        m15_close=_series(m15_bars, "close"), m15_time=_times(m15_bars),
        m15_source_identity=f"tower-client:{symbol}:M15",
        m5_high=_series(m5_bars, "high"), m5_low=_series(m5_bars, "low"), m5_close=_series(m5_bars, "close"),
        m5_time=_times(m5_bars), m5_source_identity=f"tower-client:{symbol}:M5",
        strategy_id=strategy_id, strategy_version=strategy_version, side=side,
        expected_n2_contract=EXPECTED_N2_CONTRACT_VERSION, expected_n3_contract=EXPECTED_N3_CONTRACT_VERSION,
        expected_n4_contract=EXPECTED_N4_CONTRACT_VERSION,
        h1_max_staleness_s=tower.h1_max_staleness_s, m15_max_staleness_s=tower.m15_max_staleness_s,
        m5_max_staleness_s=tower.m5_max_staleness_s,
    )
    result = tower.client.request_chain(request)
    if isinstance(result, TowerUnavailableResult):
        return _ChainQueryResult(
            market_map_available=False, levels_available=False, confirmation_available=False,
            bias_available=False, reason_codes=gap_reason_codes + (result.reason,), tower_version="UNAVAILABLE",
            side=side, **_time_fields,  # type: ignore[arg-type]
        )

    n2 = result.n2_output or {}
    n3 = result.n3_output or {}
    n4 = result.n4_output or {}
    market_map_available = n3.get("market_map_available") is True
    levels_available = n3.get("levels_available") is True
    confirmation_available = n4.get("confirmation_available") is True
    bias_available = n2.get("bias_available") is True

    n2_contract_version = _opt_str(n2.get("contract_version"))
    n2_code_version = _opt_str(n2.get("n2_code_version"))
    n2_event_fingerprint = _opt_str(n2.get("event_fingerprint"))
    n2_node_input_fingerprint = _opt_str(n2.get("node_input_fingerprint"))
    n2_data_identity = _canonical_data_identity(n2.get("data_identity"))
    n2_output_fingerprint = _opt_str(n2.get("output_fingerprint"))
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
    event_fingerprints_seen: list[str] = []

    def _check_node_identity(
        *, present: bool, contract_version: str | None, event_fingerprint: str | None,
        node_input_fingerprint: str | None, data_identity: str | None, unavailable_code: str,
    ) -> None:
        nonlocal identity_reason_codes
        if not present:
            return
        complete = (
            contract_version is not None and event_fingerprint is not None
            and node_input_fingerprint is not None and data_identity is not None
        )
        if not complete:
            identity_reason_codes += (_TOWER_IDENTITY_UNAVAILABLE, unavailable_code)
        elif event_fingerprint is not None:
            event_fingerprints_seen.append(event_fingerprint)

    _check_node_identity(
        present=result.n2_output is not None, contract_version=n2_contract_version,
        event_fingerprint=n2_event_fingerprint, node_input_fingerprint=n2_node_input_fingerprint,
        data_identity=n2_data_identity, unavailable_code=_N2_UNAVAILABLE,
    )
    _check_node_identity(
        present=result.n3_output is not None, contract_version=n3_contract_version,
        event_fingerprint=n3_event_fingerprint, node_input_fingerprint=n3_node_input_fingerprint,
        data_identity=n3_data_identity, unavailable_code=_N3_UNAVAILABLE,
    )
    _check_node_identity(
        present=result.n4_output is not None, contract_version=n4_contract_version,
        event_fingerprint=n4_event_fingerprint, node_input_fingerprint=n4_node_input_fingerprint,
        data_identity=n4_data_identity, unavailable_code=_N4_UNAVAILABLE,
    )
    if len(set(event_fingerprints_seen)) > 1:
        identity_reason_codes += (_CHAIN_IDENTITY_MISMATCH,)

    if identity_reason_codes:
        # Fail-closed: an incomplete or mismatched identity means this answer cannot be trusted as
        # genuinely belonging to a single, correlated event -- never surfaced as available with an
        # unverifiable or contradictory identity attached.
        return _ChainQueryResult(
            market_map_available=False, levels_available=False, confirmation_available=False,
            bias_available=False, reason_codes=gap_reason_codes + result.reason_codes + identity_reason_codes,
            tower_version=result.tower_version, side=side, **_time_fields,  # type: ignore[arg-type]
        )

    return _ChainQueryResult(
        market_map_available=market_map_available, levels_available=levels_available,
        confirmation_available=confirmation_available, bias_available=bias_available,
        reason_codes=gap_reason_codes + result.reason_codes, tower_version=result.tower_version, side=side,
        **_time_fields,  # type: ignore[arg-type]
        worker_session_id=result.session_id, worker_identity_fingerprint=result.worker_identity_fingerprint,
        chain_binding_version=result.chain_binding_version,
        chain_response_contract_version=result.chain_response_contract_version,
        chain_fingerprint=result.chain_fingerprint, chain_status=result.chain_status,
        terminal_reason_code=result.terminal_reason_code,
        n2_contract_version=n2_contract_version, n2_code_version=n2_code_version,
        n2_event_fingerprint=n2_event_fingerprint, n2_node_input_fingerprint=n2_node_input_fingerprint,
        n2_data_identity=n2_data_identity, n2_output_fingerprint=n2_output_fingerprint,
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
    router_bias_direction: str | None = None,
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
    callers use.

    `router_bias_direction` feeds ONLY `ve_brain.StrategyRouter.eligible`'s own pre-existing argument (a
    regime-eligibility signal, unrelated to the tower chain) -- honestly `None` by default, since no real,
    independently-computed source for it exists upstream of the Router today. It is NEVER used to derive
    the tower chain's own `side` (see `_side_from_strategy`)."""
    if bar.symbol != axes_builder.symbol:
        raise ValueError(f"evaluate_bar: bar symbol {bar.symbol!r} != axes_builder symbol "
                          f"{axes_builder.symbol!r}")

    received_at = int(time.time())
    axes = axes_builder.observe(bar)
    market_event_id = f"{bar.symbol}:{timeframe}:{bar.ts_close}"
    n1_input_fp = _fp(bar.symbol, timeframe, str(bar.ts_close))
    n1_output_fp = _fp(str(axes.is_compressed), str(axes.is_displacement), str(axes.direction),
                        str(axes.structure))
    # ve_tower's own ratified `bias_h1.Status` vocabulary is EXACTLY the two literal strings "available"/
    # "unavailable" (see `bias_h1.Status` enum, empirically confirmed via source introspection of the
    # installed 0.5.0 artifact -- `run_tower_chain`'s own `regime_available = any(s == "available" for s
    # in req.regime_axes_status)` depends on this exact vocabulary). An axis is "available" iff N1 actually
    # measured it this bar (`RawAxes`'s own `bool | None` / `str | None` fields are `None` until measured).
    regime_axes_status = tuple(
        "available" if value is not None else "unavailable"
        for value in (axes.is_compressed, axes.is_displacement, axes.direction, axes.structure)
    )

    router = ve_brain.StrategyRouter(catalog)
    eligibility_decisions = router.eligible(axes, market_event_id, router_bias_direction, confidence)
    router_input_fp = _fp(market_event_id, str(router_bias_direction), str(confidence))

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

    _chain_result_cache: dict[int, _ChainQueryResult] = {}

    def _get_chain_result(*, side: int, trace_id: str, configuration_fingerprint: str,
                           strategy_id: str, strategy_version: str) -> _ChainQueryResult:
        """Lazy, memoized PER `side` within this ONE `evaluate_bar` call -- N2/N4's own computation
        depends on `side`, so two strategies sharing the same contracted side correctly share ONE chain
        call, while a (hypothetical, not present in today's catalog) opposite-side strategy gets its own."""
        assert tower is not None  # only ever called from the `tower is not None` branch below
        if side not in _chain_result_cache:
            _chain_result_cache[side] = _query_tower_chain(
                tower, market_event_id=market_event_id, trace_id=trace_id, symbol=bar.symbol,
                event_as_of=bar.ts_close, data_cutoff=bar.ts_close,
                configuration_fingerprint=configuration_fingerprint,
                n1_fingerprint=n1_output_fp, regime_axes_status=regime_axes_status,
                strategy_id=strategy_id, strategy_version=strategy_version, side=side,
            )
        return _chain_result_cache[side]

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

        side = _side_from_strategy(canon)
        bias_direction = "LONG" if side == 1 else "SHORT"
        # RT-TOWER-0008 (2026-08-17): `bias_direction` fed to `ve_brain.DecisionRequest` (a REQUIRED
        # field of ve_brain's own external contract) is now derived from the SAME per-strategy `side` the
        # tower chain itself consumes -- see `_side_from_strategy`'s own docstring for the exact
        # provenance chain. Never a bridge.py-level default, never independent of the chain's own side.
        stop_price = entry_price - atr
        regime_label = eligibility.matched_regimes[0] if eligibility.matched_regimes else None
        probability_inputs = load_probability_inputs(canon.strategy_id, canon.strategy_version)

        if tower is not None:
            chain_result = _get_chain_result(
                side=side, trace_id=trace_id, configuration_fingerprint=configuration_fingerprint,
                strategy_id=canon.strategy_id, strategy_version=canon.strategy_version,
            )
            side_provenance = _side_provenance(canon)
            traces.append(NodeTrace(
                trace_id=trace_id, node_name="TowerN2",
                input_fingerprint=chain_result.n2_node_input_fingerprint or _fp(market_event_id, "n2-unavailable"),
                output=_fp(str(chain_result.bias_available), chain_result.n2_output_fingerprint or "",
                           str(side), side_provenance),
                reason_codes=chain_result.reason_codes, latency_seconds=0.0,
                component_version=chain_result.n2_contract_version or chain_result.tower_version,
            ))
            traces.append(NodeTrace(
                trace_id=trace_id, node_name="TowerN3",
                input_fingerprint=chain_result.n3_node_input_fingerprint or _fp(market_event_id, "n3-unavailable"),
                output=_fp(str(chain_result.market_map_available), str(chain_result.levels_available),
                           chain_result.n3_event_fingerprint or ""),
                reason_codes=chain_result.reason_codes, latency_seconds=0.0,
                component_version=chain_result.n3_contract_version or chain_result.tower_version,
            ))
            traces.append(NodeTrace(
                trace_id=trace_id, node_name="TowerN4",
                input_fingerprint=chain_result.n4_node_input_fingerprint or _fp(market_event_id, "n4-unavailable"),
                output=_fp(str(chain_result.confirmation_available), chain_result.n4_event_fingerprint or "",
                           chain_result.n3_event_fingerprint or ""),
                reason_codes=chain_result.reason_codes, latency_seconds=0.0,
                component_version=chain_result.n4_contract_version or chain_result.tower_version,
            ))
            event_identity = replace(
                event_identity,
                worker_session_id=chain_result.worker_session_id,
                worker_identity_fingerprint=chain_result.worker_identity_fingerprint,
                tower_version=chain_result.tower_version,
                chain_binding_version=chain_result.chain_binding_version,
                chain_response_contract_version=chain_result.chain_response_contract_version,
                chain_fingerprint=chain_result.chain_fingerprint,
                chain_status=chain_result.chain_status,
                terminal_reason_code=chain_result.terminal_reason_code,
                n2_contract_version=chain_result.n2_contract_version,
                n2_code_version=chain_result.n2_code_version,
                n2_event_fingerprint=chain_result.n2_event_fingerprint,
                n2_node_input_fingerprint=chain_result.n2_node_input_fingerprint,
                n2_data_identity=chain_result.n2_data_identity,
                n2_output_fingerprint=chain_result.n2_output_fingerprint,
                n3_contract_version=chain_result.n3_contract_version,
                n3_code_version=chain_result.n3_code_version,
                n3_event_fingerprint=chain_result.n3_event_fingerprint,
                n3_node_input_fingerprint=chain_result.n3_node_input_fingerprint,
                n3_data_identity=chain_result.n3_data_identity,
                n4_contract_version=chain_result.n4_contract_version,
                n4_code_version=chain_result.n4_code_version,
                n4_event_fingerprint=chain_result.n4_event_fingerprint,
                n4_node_input_fingerprint=chain_result.n4_node_input_fingerprint,
                n4_data_identity=chain_result.n4_data_identity,
                event_as_of=chain_result.event_as_of, data_cutoff=chain_result.data_cutoff,
                wall_clock_now=chain_result.wall_clock_now, last_closed_h1=chain_result.last_closed_h1,
                last_closed_m15=chain_result.last_closed_m15, last_closed_m5=chain_result.last_closed_m5,
                fetch_timestamp=chain_result.fetch_timestamp,
                staleness_reason_h1=chain_result.staleness_reason_h1,
                staleness_reason_m15=chain_result.staleness_reason_m15,
                staleness_reason_m5=chain_result.staleness_reason_m5,
            )
        else:
            chain_result = _ChainQueryResult(
                market_map_available=False, levels_available=False, confirmation_available=False,
                bias_available=False, reason_codes=("TOWER_NOT_WIRED",), tower_version="UNAVAILABLE",
                side=side,
            )

        candidate = ve_brain.DecisionRequest(
            contract_id=ve_brain.INPUT_CONTRACT_ID,
            strategy_id=canon.strategy_id, strategy_version=canon.strategy_version,
            validation_status=canon.validation_status, strategy_family=canon.strategy_family,
            strategy_policy_fingerprint=ve_brain.strategy_policy_fingerprint(canon),
            market_event_id=market_event_id, regime_fingerprint=eligibility.regime_fingerprint,
            market_state_ref=n1_output_fp, regime_label=regime_label, bias_direction=bias_direction,
            market_map_available=chain_result.market_map_available,
            levels_available=chain_result.levels_available,
            confirmation_available=chain_result.confirmation_available,
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


ChainQueryResult = _ChainQueryResult
"""Public alias (RT-TIME-0001 section B, the M5 dual-clock delivery) -- `new_brain_live`'s own M5-
triggered N4 path needs the EXACT SAME chain-calling function `evaluate_bar` itself uses, never a
reimplementation or a direct `run_n2`/`run_n3`/`run_n4` call (the CEO's own explicit "chain-binding"
rule). Exporting the existing private helper under a public name, unchanged, is the only way to satisfy
that rule without duplicating `_query_tower_chain`'s own logic."""
query_tower_chain = _query_tower_chain
side_from_strategy = _side_from_strategy
"""Public alias -- `side` must always come from the eligible strategy's own contracted
`allowed_directions[0]` (never a default, never hardcoded LONG); the M5 path reuses this EXACT
function rather than re-deriving it, for the same zero-drift reason `query_tower_chain` is exported."""
side_provenance = _side_provenance
PLACEHOLDER_TARGET_RR = _PLACEHOLDER_TARGET_RR
ELIGIBILITY_POLICY_VERSION = _ELIGIBILITY_POLICY_VERSION
FP = _fp
"""Public aliases for the two config constants and the generic fingerprint helper the M5 path's own
`DecisionRequest` construction must match byte-for-byte against `evaluate_bar`'s own -- importing the
real values rather than re-typing them as new literals is what makes "the same value, guaranteed" true
rather than merely intended."""
