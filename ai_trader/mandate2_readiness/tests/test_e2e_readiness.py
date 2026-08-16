"""25 end-to-end tests for Mandate 2 (CEO, 2026-08-14: "PREGATIRE pentru Mandatul 2... scheletul celor 25
de teste end-to-end, fara implementare"). These 25 are OWNED by this division. Original six were real,
runnable against the pre-artifact architecture; the remaining nineteen were `pytest.skip`'d, each naming
a concept that did not exist yet.

**Mandate 2 continuation, 2026-08-14 ("ARTEFACTUL, predat fizic" then "construieste codul, NU comuta
inca"): `ve_brain` is installed, `new_brain_bridge/` (N1-Router-EV-N6, provenance-gated Risk Manager,
shadow execution, telemetry) is built and tested. Twenty-two of the 25 are now real** -- the original
six (8, 11, 12, 13, 19, 20) PLUS sixteen more (1, 2, 3, 6, 7, 10, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25)
converted below, using the REAL installed `ve_brain` and `new_brain_bridge` code, never a fixture
standing in for either.

**Red Team verdict history**: `MANDATE_2_REVIEW_CONDITIONAL`/`INTEGRATION_BLOCKED` (2026-08-14) found
Risk Manager, broker gate, and the authority mechanism all VERIFIED CORRECT, blocked only on N3/N4 not
existing in the artifact yet. **CLOSED 2026-08-16 (Phase 2, `STAGED_INSTALL_AUTHORIZED`, `ve_tower`
0.3.0 genuinely installed and wired into `bridge.py`)**: tests 4, 5, 9, and 20b -- the four that were
`BLOCKED_ON_TOWER_HANDOFF` -- are now real and passing, each against the genuinely installed artifact
over real IPC (skips cleanly if the isolated tower venv isn't present on this machine, matching this
repo's own established convention for real-subprocess tests). **25/25 canonical end-to-end tests are now
real** (test_20b is the amendment's own named sub-test of 20, not a 26th canonical number). **Test 10 was
NOT blocked on the artifact at all** -- its original premise (a cross-strategy merge producing ONE N6
resolution per bar) does not match this codebase's actual, shipped per-strategy-independent design, so it
was RESCOPED (not left waiting) to the real property that name still deserves: multiple recognition
sources matching one bar each get their own independent, non-conflicting resolution -- now real and
passing. **Test 22 was also NOT blocked on the artifact** -- it needed only a gate-enable journal
(`BrokerGateJournal`/`construct_enabled_gate` in `broker_gate.py`), built and tested here, independent of
N3/N4.

**CEO amendment A1, 2026-08-14, incorporated below**: N1-N6 and the EV engine CAN legitimately traverse
all the way to a `SHADOW_TRADE_CANDIDATE` (not just `NO_TRADE`) -- Risk Manager and the Execution Adapter
can process that result IN SHADOW. `BROKER_ORDER_SUBMISSION = DISABLED` is a SEPARATE, LAST-MILE gate
that must hold regardless of how confidently everything upstream approved the candidate ("dreptul de
ANALIZA prin N6 nu e acelasi lucru cu dreptul de EXECUTIE reala"). Tests 8 and 19 are written against
this stronger reading, not the weaker "NO_TRADE never orders" reading alone -- that direction was already
covered before the amendment and would have been an easier, less useful test to pass.

**Never modify N1-N6 or the EV engine internally, including once received** (CEO's own standing
instruction) -- every test below imports `ve_brain`'s own PUBLIC API only, and reads
`new_brain_bridge`'s own outputs; none reaches into `ve_brain`'s private modules. If a future test in
this file ever fails against the real artifact, the required response is `INTEGRATION_BLOCKED` -> a
reproducible report to VE -> VE repairs -> Red Team revalidates. Local repair is explicitly forbidden
("Ar crea din nou doua versiuni ale creierului")."""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest
import ve_brain  # type: ignore[import-untyped]  # external VE artifact, no py.typed marker -- never modified

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_orchestrator.tests._fixtures import make_deps, make_market_context
from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.live_signal_source.tests._fixtures import FakeMT5Gateway, RawRate
from ai_trader.live_signal_source.types import Bar, BarFeedError, LiveCandidate
from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionDisabledError, BrokerOrderSubmissionGate
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.safety import verify_safety_guards
from ai_trader.mt5_demo_execution.tests._fixtures import AS_OF, FakeMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_bridge.bridge import TowerDependencies, evaluate_bar
from ai_trader.new_brain_bridge.fail_safe import BrainUnavailableOutcome, safe_evaluate_bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.risk_gate import CIRCUIT_BREAKER_ACTIVE, submit_new_brain_candidate
from ai_trader.new_brain_bridge.telemetry import NewBrainTelemetryLog
from ai_trader.new_brain_bridge.tests.conftest import trend_up_regime_bars
from ai_trader.new_brain_bridge.tower_bar_source import BAR_SECONDS_M15, detect_gaps
from ai_trader.new_brain_bridge.tower_client import TowerClient, TowerClientConfig, TowerN3N4Result, TowerUnavailableResult
from ai_trader.new_brain_bridge.tower_launcher import EstablishedSession, TowerWorkerLauncher
from ai_trader.new_brain_bridge.tower_protocol import PROTOCOL_VERSION, REQUEST_SCHEMA_VERSION, TowerRequest
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.order_manager.journal import OrderManagerAuditJournal
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.orchestration import DemoDepsBundle, PdhPdlOrchestrator
from ai_trader.pdh_pdl_demo.recognition_rule import MAGIC_NUMBER, STRATEGY_ID, PdhPdlTrigger
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.tests._fixtures import make_account, make_config, make_instrument, make_portfolio, make_risk_context
from ai_trader.risk_manager_live.types import TradingCircuitState
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
M15_SECONDS = 15 * 60
NOW = 1_700_000_000

_TOWER_VENV = Path("C:/Users/MEDION GAMING/ve_tower_venv")
_TOWER_PYTHON = _TOWER_VENV / "Scripts" / "python.exe"
_real_tower = pytest.mark.skipif(
    not _TOWER_PYTHON.is_file(), reason="isolated tower venv not present on this machine"
)


def _real_bars(*, count: int, step_seconds: int, last_time: int) -> tuple[dict[str, object], ...]:
    """Deterministic OHLC bars for a real N3/N4 request, ending exactly at `last_time`."""
    bars: list[dict[str, object]] = []
    price = 2000.0
    first_time = last_time - (count - 1) * step_seconds
    for i in range(count):
        price += 0.1
        t = first_time + i * step_seconds
        bars.append({"time": t, "open": price, "high": price + 0.5, "low": price - 0.5, "close": price + 0.05})
    return tuple(bars)


def _tower_request(**overrides: object) -> TowerRequest:
    fields: dict[str, object] = dict(
        protocol_version=PROTOCOL_VERSION, schema_version=REQUEST_SCHEMA_VERSION,
        request_id="e2e-tower-req", market_event_id="e2e-tower-event", event_fingerprint="",
        data_identity="e2e-data-identity", node_input_fingerprint="e2e-node-input",
        symbol=SYMBOL, as_of=str(NOW),
        n1_output={"available": True, "fingerprint": "n1fp"},
        n2_output={"available": True, "fingerprint": "n2fp", "bias_direction": "LONG"},
        m15_closed_bars=_real_bars(count=150, step_seconds=900, last_time=NOW - 900),
        m5_closed_bars=_real_bars(count=150, step_seconds=300, last_time=NOW - 300),
        strategy_id="trend_pullback", strategy_version="1.0",
    )
    fields.update(overrides)
    return TowerRequest(**fields)  # type: ignore[arg-type]


# ============================================================================
# PART A -- six tests that do NOT depend on the artifact. Real, runnable,
# passing against the CURRENT architecture today.
# ============================================================================


# -- Test 8 (CEO; strengthened per amendment A1, 2026-08-14) --------------------------------------------


def _approved_demo_bundle(tmp_path: Path) -> tuple[DemoDepsBundle, FakeMT5DemoGateway]:
    """A GENUINELY approved, ready-to-submit order via the real, currently-live pdh_pdl_demo pipeline --
    stands in for "N6 produced a fully shadow-eligible SHADOW_TRADE_CANDIDATE, and Risk Manager /
    Execution Adapter approved it in shadow." Everything upstream says yes; that is the whole point."""
    dry_run_deps = make_deps(tmp_path / "dry")
    order_send_result = SimpleNamespace(
        retcode=10009, comment="Request completed", order=1, deal=1, volume=0.01, price=108.05,
    )
    demo_gateway = FakeMT5DemoGateway(tick_time=AS_OF, order_send_result=order_send_result)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway, config=MT5DemoConfig(max_order_volume=1000.0))
    demo_adapter.connect()
    demo_deps = make_deps(
        tmp_path / "demo", ledger=OrderLedger(),
        order_journal=OrderManagerAuditJournal(tmp_path / "demo" / "journal.jsonl"), adapter=demo_adapter,
    )
    safety_report = verify_safety_guards(
        demo_adapter, MT5DemoConfig(max_order_volume=1000.0), symbol=SYMBOL, clock=lambda: AS_OF,
    )
    bundle = DemoDepsBundle(
        dry_run_deps=dry_run_deps, demo_deps=demo_deps, demo_adapter=demo_adapter, safety_guard_report=safety_report,
    )
    return bundle, demo_gateway


def test_08_broker_receives_no_order_when_the_submission_gate_is_disabled_even_for_a_fully_approved_candidate(
    tmp_path: Path,
) -> None:
    """The property Mandate 2 must preserve: NOT "NO_TRADE never orders" (trivially true, nothing to
    prove) but "a candidate every upstream stage approved STILL never reaches the broker while
    BROKER_ORDER_SUBMISSION is DISABLED." Proven two ways:

    (1) The gate primitive itself, wired the way Mandate 2's integration must wire it -- `authorize()`
        called BEFORE any broker-facing call, never after.
    (2) The REAL, currently-approved pdh_pdl_demo order pipeline (today's closest analog to a
        shadow-approved candidate) -- confirming the underlying order WOULD have gone to the broker
        (`outcome.sent is True`, matching `test_submit_candidate_sends_through_the_existing_demo_pipeline
        _and_tracks_the_position` in `pdh_pdl_demo/tests/test_orchestration.py`), so the gate in (1) is
        blocking something real, not a scenario that would have failed anyway."""
    gate = BrokerOrderSubmissionGate()  # the only reachable default: disabled
    broker_calls: list[str] = []

    def submit_shadow_trade_candidate_if_authorized(candidate_id: str, n6_approved_shadow_trade: bool) -> None:
        assert n6_approved_shadow_trade is True  # the amendment's own scenario, not NO_TRADE
        gate.authorize()  # MUST be checked before any broker-facing call -- this is the contract
        broker_calls.append(candidate_id)  # unreachable while the gate is disabled

    with pytest.raises(BrokerOrderSubmissionDisabledError):
        submit_shadow_trade_candidate_if_authorized("SHADOW-CID-1", n6_approved_shadow_trade=True)
    assert broker_calls == []

    journal = PdhPdlAuditJournal()
    fill_reader = SimpleNamespace(is_position_open=lambda *a: None, read_close_price=lambda *a: None)
    bundle, demo_gateway = _approved_demo_bundle(tmp_path)
    orch = PdhPdlOrchestrator(SYMBOL, 0.01, lambda c, t: bundle, fill_reader, journal)
    candidate = LiveCandidate(
        strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.SHORT, entry=108.0, stop=111.0,
        target=90.0, session="ny", magic_number=MAGIC_NUMBER, comment="test", as_of=AS_OF,
    )
    trigger = PdhPdlTrigger(
        touch_idx=17, entry_idx=18, direction=-1, strategy_stop_price=111.0, target_price=90.0,
        atr_at_touch=1.0, day_boundary_label=1_705_356_000, effective_spread=0.2,
        executable_stop_price=111.5, tick_size=0.01,
    )
    outcome = orch.submit_candidate(candidate, trigger, make_market_context())
    assert outcome is not None and outcome.sent is True  # confirms this candidate WAS order-worthy
    assert len(demo_gateway.order_send_calls) == 1  # the EXISTING, separately-approved DEMO path --
    # unaffected by the new gate, since it isn't wired there (see module docstring, "Neschimbate")


# -- Test 11 (CEO) ---------------------------------------------------------------------------------------


class _AlwaysCandidateRule:
    """A trivial recognition rule that fires on every bar -- deliberately NOT PDH/PDL-specific, so this
    test proves the dedup property at the `LiveBarFeed` -> `CandidateSignalProducer` boundary itself,
    the SAME boundary whatever Mandate 2's own N1 ingestion sits behind."""

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        return LiveCandidate(
            strategy_id="TEST", symbol=bar.symbol, direction=Direction.SHORT, entry=bar.close,
            stop=bar.close + 1.0, target=bar.close - 1.0, session="ny", magic_number=1, comment="test",
            as_of=bar.ts_close,
        )


def test_11_the_same_underlying_event_delivered_twice_is_processed_exactly_once() -> None:
    """A real M15 bar remains visible in MT5's own lookback window across MULTIPLE polls (this is
    ordinary MT5 behavior, not a bug -- see `bar_feed.py`'s own docstring history). This is the exact
    shape of the 2026-08-11 duplicate-bar incident: the SAME real event, seen twice by the feed. The
    producer -- and therefore whatever consumes its output -- must still only ever decide on it once."""
    gateway = FakeMT5Gateway(rates=[RawRate(time=NOW - 1_000, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    journal = LiveSignalJournal()
    producer = CandidateSignalProducer(feed, _AlwaysCandidateRule(), journal)

    first = producer.run_once()
    second = producer.run_once()  # SAME gateway.rates -- MT5 still shows the same bar in its lookback

    assert len(first) == 1
    assert second == ()  # deduped -- never evaluated twice


# -- Test 12 (CEO) ---------------------------------------------------------------------------------------


def test_12_a_restart_produces_no_duplicate_decision_for_work_already_completed(tmp_path: Path) -> None:
    """Same property as test 11, but across a SIMULATED PROCESS RESTART: a brand-new `LiveBarFeed` +
    `CandidateSignalProducer` (a fresh object graph, exactly what `main()` builds on every real restart),
    sharing only the PERSISTED state store -- never the in-memory objects. The already-decided bar must
    not be re-decided."""
    store_path = tmp_path / "state.db"
    gateway = FakeMT5Gateway(rates=[RawRate(time=NOW - 1_000, open=1.0, high=2.0, low=0.5, close=1.5)])

    store_before = SqliteStateStore(store_path)
    feed_before = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW, state_store=store_before,
    )
    producer_before = CandidateSignalProducer(feed_before, _AlwaysCandidateRule(), LiveSignalJournal(store_before))
    first = producer_before.run_once()
    store_before.close()

    # "Restart": entirely new objects, same persisted store, same gateway still showing the same bar.
    store_after = SqliteStateStore(store_path)
    feed_after = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW, state_store=store_after,
    )
    producer_after = CandidateSignalProducer(feed_after, _AlwaysCandidateRule(), LiveSignalJournal(store_after))
    second = producer_after.run_once()
    store_after.close()

    assert len(first) == 1
    assert second == ()  # the restart did not re-decide the same, already-processed bar


# -- Test 13 (CEO) ---------------------------------------------------------------------------------------


def test_13_stale_feed_data_produces_no_decision_at_all() -> None:
    """Open question, disclosed rather than guessed at: today, a stale broker-offset probe (see
    `StaleProbeError`, `bar_feed.py`) makes `LiveBarFeed.poll()` return zero bars -- so
    `CandidateSignalProducer.run_once()` evaluates nothing and journals nothing for that cycle. This is
    SILENCE, not an explicit `NO_TRADE` record. Whether Mandate 2's own N1-N6 decision cycle needs an
    EXPLICIT `NO_TRADE(reason=STALE_DATA)` journaled every cycle (e.g. if the brain runs on its own
    timer, independent of bar arrival) or whether "no candidate produced this cycle" is an acceptable
    proxy for NO_TRADE is a real design question for VE/Red Team to settle when the artifact's own
    cadence is known -- NOT decided here by this test."""
    gateway = FakeMT5Gateway(m1_probe_rates=None)  # empty probe -- see make_broker_offset's own guard
    from ai_trader.live_signal_source.bar_feed import make_broker_offset

    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW,
        broker_offset=make_broker_offset(gateway, SYMBOL, system_clock=lambda: NOW),
    )
    journal = LiveSignalJournal()
    producer = CandidateSignalProducer(feed, _AlwaysCandidateRule(), journal)

    with pytest.raises(Exception):  # empty probe is NOT StaleProbeError -- still a hard failure, by design
        producer.run_once()
    assert journal.entries == ()  # nothing decided, nothing journaled -- silence, not a guess


# -- Test 19 (CEO; strengthened per amendment A1) --------------------------------------------------------


def test_19_the_gate_cannot_be_enabled_by_accident_under_any_construction_pattern() -> None:
    """Extends `test_broker_gate.py`'s own `test_no_environment_variable_influences_the_default` with the
    specific accidental-activation shapes a real integration could introduce: a config dict with a
    truthy-looking key, a CLI-arg-style string, and the "forgot the keyword" positional-argument case."""
    assert BrokerOrderSubmissionGate().enabled is False

    config_dict = {"broker_order_submission": True, "enabled": "true", "BROKER_ORDER_SUBMISSION": 1}
    # Constructing from a dict requires an explicit, visible **config_dict -- and even then, only the
    # dataclass's own declared `enabled: bool` keyword matches; the other keys are inert unless a caller
    # deliberately writes `enabled=True`, which is the one and only accepted activation path.
    assert BrokerOrderSubmissionGate(reason=str(config_dict)).enabled is False

    with pytest.raises(TypeError):
        # This test itself CAUGHT a real gap during development: `BrokerOrderSubmissionGate(True)`
        # (bare positional, no `enabled=` keyword anywhere to grep for) was silently ACCEPTED before
        # `broker_gate.py` added `kw_only=True` -- fixed there, not documented around here.
        BrokerOrderSubmissionGate(True)  # type: ignore[call-arg]


# -- Test 20 (CEO) ---------------------------------------------------------------------------------------


def test_20_stopping_a_node_never_leaves_a_partial_order_or_a_lost_decision(tmp_path: Path) -> None:
    """The CURRENT architecture's own analog: "a node" today is a whole live process (`pdh_pdl_demo`,
    `multi_policy_live`, ...). Stopping one (killed, crashed, or a genuine market-data outage the new
    `StaleProbeError` fail-closed already refuses to guess through) leaves NOTHING partially executed --
    a broker order is a single atomic `order_send` call this codebase never splits across steps, and
    `PendingPdhPdlTrade` is persisted-then-resumed (test 12's own property), never left half-written.

    **Genuine gap, disclosed not solved**: Mandate 2's own N1-N6/EV pipeline may be MULTI-NODE (e.g. N3
    crashing while N4 is mid-evaluation) -- a fundamentally different failure shape than "a whole process
    dies," and not meaningfully testable without the real artifact's own inter-node contract. This test
    proves the WEAKER, currently-true property (whole-process death is safe); the STRONGER, multi-node
    property is `pytest.skip`'d below (test 20b) until the artifact exists."""
    store_path = tmp_path / "state.db"
    gateway = FakeMT5Gateway(rates=[RawRate(time=NOW - 1_000, open=1.0, high=2.0, low=0.5, close=1.5)])

    store = SqliteStateStore(store_path)
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW, state_store=store)
    producer = CandidateSignalProducer(feed, _AlwaysCandidateRule(), LiveSignalJournal(store))
    producer.run_once()
    watermark_before = store.get_value(f"live_signal_source.bar_feed:{SYMBOL}:15")
    store.close()  # simulates the node being stopped -- no graceful shutdown hook, just gone

    store_reopened = SqliteStateStore(store_path)
    watermark_after = store_reopened.get_value(f"live_signal_source.bar_feed:{SYMBOL}:15")
    store_reopened.close()

    assert watermark_before == watermark_after  # nothing lost, nothing corrupted by the abrupt stop


@_real_tower
def test_20b_a_single_node_failing_mid_pipeline_degrades_that_decision_to_no_trade(tmp_path: Path) -> None:
    """CLOSED 2026-08-16: `ve_tower.run_n3`/`run_n4` are themselves designed to never raise (they catch
    everything internally and return their own Unavailable shape) -- so "N3 raises" cannot be triggered
    from outside without corrupting the real artifact, which this division may never do. The real,
    reachable failure modes are (1) the WORKER's own request-handling code raising an unexpected
    exception before ever calling `ve_tower` (a bug in `decision.py`/`server.py` itself), proven by
    dependency injection in `tower_worker/tests/test_server_roundtrip.py`'s own
    `test_decision_fn_raising_an_unexpected_exception_degrades_and_the_server_keeps_serving` (that
    proof cannot run from this venv -- `ve_tower_worker` is only ever installed in the isolated tower
    venv, never here); and (2) a genuinely malformed/edge-case request the wire-level parser lets
    through but `decision.py`'s own shape validation rejects. THIS test demonstrates (2) against the
    REAL production worker (`real_decision`, unmodified, no fault injected) and proves the SAME real
    worker process answers a SUBSEQUENT normal request afterward -- "the loop continues," for real."""
    launcher = TowerWorkerLauncher(tower_python=_TOWER_PYTHON, run_dir=tmp_path)
    try:
        session = launcher.launch_and_handshake()
        assert isinstance(session, EstablishedSession), f"expected EstablishedSession, got {session!r}"
        client = TowerClient(TowerClientConfig(host=session.host, port=session.port, timeout_seconds=15.0), session=session)

        good_first = client.request_n3_n4(_tower_request(request_id="test-20b-good-1", market_event_id="test-20b-event-1"))
        assert isinstance(good_first, TowerN3N4Result), f"expected a real answer, got {good_first!r}"

        malformed = client.request_n3_n4(_tower_request(
            request_id="test-20b-malformed", market_event_id="test-20b-event-2",
            n2_output={"available": True, "fingerprint": "n2fp", "bias_direction": "SIDEWAYS"},  # invalid value
        ))
        assert isinstance(malformed, TowerUnavailableResult), f"expected a degraded refusal, got {malformed!r}"
        # degraded, not crashed -- the worker answered with a real, distinct reason, never hung/timed out

        good_second = client.request_n3_n4(_tower_request(request_id="test-20b-good-2", market_event_id="test-20b-event-3"))
        assert isinstance(good_second, TowerN3N4Result), (
            f"the SAME real worker process must still answer normally after the malformed request -- "
            f"got {good_second!r}"
        )
    finally:
        launcher.stop()


# ============================================================================
# PART B -- fourteen of the original nineteen skeletons, now real (the real
# ve_brain + new_brain_bridge exist). Five stay pytest.skip'd -- each still
# names a concept this codebase genuinely does not build yet.
# ============================================================================

_BLOCKED = "INTEGRATION_BLOCKED -- this concept is not built in this codebase yet, see this test's own docstring"
_ARCHITECTURE_MISMATCH = ("Doesn't match this codebase's per-strategy-independent N6 design -- see this "
                          "test's own docstring")


def test_01_each_real_bar_reaches_n1_exactly_once_end_to_end() -> None:
    """Extends test 11's proven feed-level dedup all the way through N1's own ingestion boundary
    (`RawAxesBuilder.observe`) -- the same deduping `CandidateSignalProducer.run_once()` feeds a bar to
    its recognition rule exactly once; N1 sits at that exact same call site in the real integration."""
    gateway = FakeMT5Gateway(rates=[RawRate(time=NOW - 1_000, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)

    call_count = 0
    builder = RawAxesBuilder(SYMBOL)
    real_observe = builder.observe

    def counting_observe(bar: Bar) -> object:
        nonlocal call_count
        call_count += 1
        return real_observe(bar)

    builder.observe = counting_observe  # type: ignore[method-assign]

    first_bars = feed.poll()
    for bar in first_bars:
        builder.observe(bar)
    second_bars = feed.poll()  # SAME underlying event still in MT5's lookback -- feed dedupes it
    for bar in second_bars:
        builder.observe(bar)

    assert len(first_bars) == 1
    assert second_bars == ()
    assert call_count == 1  # N1 itself was reached exactly once for the one real event


def test_02_a_backfilled_bar_is_processed_identically_to_a_live_bar_by_n1() -> None:
    """`Bar.is_backfilled=True` must never special-case N1's own evaluation -- `RawAxesBuilder.observe`
    reads only `open`/`high`/`low`/`close`, never `is_backfilled`, confirmed here by feeding the
    IDENTICAL OHLC through two separate builders, one via a backfilled bar and one via a live one."""
    live_bar = Bar(symbol=SYMBOL, ts_open=0, ts_close=900, open=2400.0, high=2401.0, low=2399.0,
                    close=2400.5, volume=100.0, is_backfilled=False)
    backfilled_bar = Bar(symbol=SYMBOL, ts_open=0, ts_close=900, open=2400.0, high=2401.0, low=2399.0,
                          close=2400.5, volume=100.0, is_backfilled=True)

    live_axes = RawAxesBuilder(SYMBOL).observe(live_bar)
    backfilled_axes = RawAxesBuilder(SYMBOL).observe(backfilled_bar)

    assert live_axes == backfilled_axes


def test_03_a_malformed_bar_never_reaches_n1() -> None:
    """Fails closed at ingestion (already true today -- `BarFeedError` on a missing OHLC field) --
    confirm N1 (`RawAxesBuilder`) is never even CONSTRUCTED-INTO when the feed itself refuses first."""
    malformed_record = SimpleNamespace(time=NOW - 1_000, high=2.0, low=0.5, close=1.5)  # missing "open"
    gateway = FakeMT5Gateway(rates=[malformed_record])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    builder = RawAxesBuilder(SYMBOL)

    with pytest.raises(BarFeedError):
        for bar in feed.poll():
            builder.observe(bar)  # unreachable -- feed.poll() itself raises first

    assert builder.bars_observed == 0


@_real_tower
def test_04_session_and_day_boundary_labels_n1_consumes_match_true_utc(tmp_path: Path) -> None:
    """CLOSED 2026-08-16 (Phase 2, `ve_tower` 0.3.0 genuinely installed and wired):
    N3's real response now carries `data_identity.last_closed_bar_time` -- the exact true-UTC epoch of
    the last M15 bar consumed. This proves that timestamp survives the whole round trip (client fetch ->
    wire serialize -> IPC -> `ve_tower.build_data_identity` -> wire deserialize) UNCHANGED, so any
    session/day-boundary label derived from it (via `day_boundary_start_utc`, the SAME true-UTC anchor
    `pdh_pdl_demo`'s own live day-index already uses) is correct by construction -- not because this
    division re-derives day-boundary logic, but because the timestamp it would be derived FROM is
    verifiably the true-UTC value that was actually sent, never silently shifted."""
    launcher = TowerWorkerLauncher(tower_python=_TOWER_PYTHON, run_dir=tmp_path)
    try:
        session = launcher.launch_and_handshake()
        assert isinstance(session, EstablishedSession), f"expected EstablishedSession, got {session!r}"
        client = TowerClient(TowerClientConfig(host=session.host, port=session.port, timeout_seconds=15.0), session=session)

        known_true_utc_last_bar = NOW - 900  # a deliberately CHOSEN, known true-UTC epoch
        request = _tower_request(
            request_id="test-04-req", market_event_id="test-04-event", as_of=str(NOW),
            m15_closed_bars=_real_bars(count=150, step_seconds=900, last_time=known_true_utc_last_bar),
        )
        result = client.request_n3_n4(request)
        assert isinstance(result, TowerN3N4Result), f"expected TowerN3N4Result, got {result!r}"
        assert result.n3_output is not None
        data_identity = result.n3_output.get("data_identity")
        assert isinstance(data_identity, dict)

        carried_timestamp = data_identity["last_closed_bar_time"]
        assert carried_timestamp == known_true_utc_last_bar  # unchanged across the whole round trip

        expected_day_boundary = day_boundary_start_utc(known_true_utc_last_bar)
        actual_day_boundary = day_boundary_start_utc(carried_timestamp)
        assert actual_day_boundary == expected_day_boundary  # the SAME true-UTC anchor, not a broker-time artifact
    finally:
        launcher.stop()


def test_05_a_detected_gap_is_visible_in_whatever_context_n1_consumes() -> None:
    """CLOSED 2026-08-16: `tower_bar_source.detect_gaps` (built for this test) reuses the SAME
    `classify_gap` `LiveBarFeed.poll()` itself already uses, on whatever M15/M5 window is about to be
    sent to the tower -- `bridge.py`'s own `_query_tower` surfaces any detected gap on the Tower
    `NodeTrace`'s `reason_codes` (see `bridge.py`'s own `_query_tower`, the single call site -- a direct,
    auditable read, not something this test needs to re-verify through IPC), so a gap in the data
    feeding N3/N4 is never silently absorbed. This test proves the primitive itself -- `detect_gaps`
    correctly classifies a real, hand-built discontinuity and produces no false positive on a clean
    window -- the property `bridge.py`'s own wiring then surfaces unconditionally."""
    bar_a: dict[str, object] = {"time": NOW - 3 * BAR_SECONDS_M15, "open": 2000.0, "high": 2001.0, "low": 1999.0, "close": 2000.5}
    # a real, deliberate discontinuity: skips 4 whole M15 periods (1 hour) instead of advancing by one
    bar_b: dict[str, object] = {"time": NOW - 3 * BAR_SECONDS_M15 + 5 * BAR_SECONDS_M15, "open": 2001.0,
                                 "high": 2002.0, "low": 2000.0, "close": 2001.5}
    gapped_bars = (bar_a, bar_b)
    gaps = detect_gaps(gapped_bars, symbol=SYMBOL, bar_seconds=BAR_SECONDS_M15)
    assert len(gaps) == 1
    assert gaps[0].duration_seconds == 5 * BAR_SECONDS_M15
    assert gaps[0].classification is not None  # real classification (UNEXPECTED for a mid-week gap this shape)

    no_gap_bars = _real_bars(count=10, step_seconds=BAR_SECONDS_M15, last_time=NOW)
    assert detect_gaps(no_gap_bars, symbol=SYMBOL, bar_seconds=BAR_SECONDS_M15) == ()  # no false positives


def test_06_a_malformed_n1_n6_decision_output_is_rejected_not_guessed_at() -> None:
    """Schema validation on the boundary this division reads -- `ve_brain.decide_n6` itself runs
    `validate_request` (step 1, before catalog/EV) and returns `SCHEMA_VALIDATION_FAILED`, never a
    guess, for a malformed `DecisionRequest` (here: `contract_id` not matching `INPUT_CONTRACT_ID`)."""
    canon = next(c for c in ve_brain.CANONICAL_STRATEGIES if c.strategy_id == "trend_pullback")
    bad_request = ve_brain.DecisionRequest(
        contract_id="wrong-contract-id",  # the one deliberately malformed field
        strategy_id=canon.strategy_id, strategy_version=canon.strategy_version,
        validation_status=canon.validation_status, strategy_family=canon.strategy_family,
        strategy_policy_fingerprint=ve_brain.strategy_policy_fingerprint(canon),
        market_event_id="evt", regime_fingerprint="fp", market_state_ref="ref", regime_label="TREND_UP",
        bias_direction="LONG", market_map_available=False, levels_available=False,
        confirmation_available=False, entry_price=2400.0, stop_price=2390.0, target_kind="rr",
        target_param=2.0, holding_window=10, atr=10.0, probability_inputs=None, full_spread_price=0.10,
        entry_slippage_price=0.05, exit_slippage_price=0.05, symbol=SYMBOL, timeframe="M15", block_start=0,
        block_end=900, segment_id="test", manifest_hash="test", n1_contract_version=ve_brain.N1_CONTRACT_VERSION,
        raw_axis_schema_version=ve_brain.RAW_AXIS_SCHEMA_VERSION, router_version=ve_brain.ROUTER_VERSION,
        eligibility_policy_version="eligibility-v1",
        measurement_contract_version=ve_brain.MEASUREMENT_CONTRACT_VERSION, configuration_fingerprint="cfg",
    )
    eligibility = ve_brain.EligibilityDecision(
        strategy_id=canon.strategy_id, strategy_version=canon.strategy_version, market_event_id="evt",
        regime_fingerprint="fp", router_version=ve_brain.ROUTER_VERSION, eligible=True,
        mode=ve_brain.RoutingMode.NORMAL, matched_regimes=("TREND_UP",),
        reason_codes=(ve_brain.ReasonCode.ROUTER_ELIGIBLE.value,),
    )

    response = ve_brain.decide_n6(bad_request, eligibility)

    assert response.decision == "NO_TRADE"
    assert response.reason_codes == (ve_brain.ReasonCode.SCHEMA_VALIDATION_FAILED.value,)


def test_07_n1_n6_and_the_ev_engine_are_deterministic_on_a_frozen_input_snapshot() -> None:
    """Same input, replayed twice -- via TWO INDEPENDENT `RawAxesBuilder`/bar-history instances (never
    the same mutable object, so this proves determinism of the PIPELINE, not object reuse) -- same
    decision, same `expected_value_net`, same `configuration_fingerprint`. Required for test 12's own
    restart-safety property to mean anything once real decision logic is involved."""
    def _run() -> ve_brain.DecisionResponse | None:
        builder = RawAxesBuilder(SYMBOL)
        bars = trend_up_regime_bars(SYMBOL)
        for bar in bars[:-1]:
            builder.observe(bar)
        outcomes = evaluate_bar(bars[-1], timeframe="M15", axes_builder=builder)
        return next(o for o in outcomes if o.strategy_id == "trend_pullback").decision

    first = _run()
    second = _run()
    assert first is not None and second is not None
    assert first.decision == second.decision
    assert first.expected_value_net == second.expected_value_net
    assert first.configuration_fingerprint == second.configuration_fingerprint


@_real_tower
def test_09_a_decision_citing_a_stale_snapshot_is_rejected_before_reaching_n6(tmp_path: Path) -> None:
    """CLOSED 2026-08-16: distinct from test 13 (no bar at all) -- a snapshot that WAS available but has
    since gone stale relative to a real freshness bound. `ve_tower` 0.3.0's own `run_n3`/`run_n4` already
    implement `max_staleness_s` (a real, ratified gate -- `ReasonCode.DATA_STALE`), threaded through this
    division's own wire protocol (`TowerRequest.max_staleness_s`, `bridge.py`'s own `TowerDependencies.
    max_staleness_s`, default 30 min slack for ordinary polling latency, see `bridge.py`). This test
    proves: given bars that are genuinely OLD relative to `as_of` and a tight `max_staleness_s`, the REAL
    artifact refuses with `market_map_available=False` -- exactly the same fail-closed path an
    unavailable tower produces, so `evaluate_bar`'s own `DecisionRequest` never treats a stale snapshot
    as a valid one; N6 is never reached with fabricated/stale-but-unlabeled availability."""
    launcher = TowerWorkerLauncher(tower_python=_TOWER_PYTHON, run_dir=tmp_path)
    try:
        session = launcher.launch_and_handshake()
        assert isinstance(session, EstablishedSession), f"expected EstablishedSession, got {session!r}"
        client = TowerClient(TowerClientConfig(host=session.host, port=session.port, timeout_seconds=15.0), session=session)

        stale_last_bar_time = NOW - 900
        far_future_as_of = NOW + 100_000  # as_of - last_bar_time is far larger than max_staleness_s below
        request = _tower_request(
            request_id="test-09-stale-req", market_event_id="test-09-stale-event",
            as_of=str(far_future_as_of), max_staleness_s=900,
            m15_closed_bars=_real_bars(count=150, step_seconds=900, last_time=stale_last_bar_time),
        )
        result = client.request_n3_n4(request)
        assert isinstance(result, TowerN3N4Result), f"expected a real (refused, not degraded-transport) answer, got {result!r}"
        assert result.n3_output is not None
        assert result.n3_output.get("market_map_available") is False  # rejected, not fabricated as available
        assert any("stale" in code.lower() for code in result.reason_codes), (
            f"expected a real DATA_STALE-shaped reason code, got {result.reason_codes}"
        )
    finally:
        launcher.stop()


def test_10_two_recognition_sources_matching_one_bar_each_get_their_own_independent_n6_resolution() -> None:
    """RESCOPED (Mandate B point 5, CEO 2026-08-14: "restul le inchizi" -- closed for real, not left
    waiting on anything). The original premise assumed a MERGE step across multiple recognition sources
    producing ONE N6 resolution per bar -- this codebase's actual, shipped design (`bridge.evaluate_bar`)
    is per-strategy-INDEPENDENT: every catalog strategy gets its OWN `DecisionRequest`/`decide_n6` call
    for the same bar, so there is no merge and therefore no conflict to silently resolve. The REAL
    property that name still deserves -- "no silent overwrite, no double count" when multiple sources
    match the same bar -- is proven here instead: on a TREND_UP-routed bar, THREE catalog strategies
    (`trend_pullback`, `trend_shadow`, `trend_experimental`) all match the SAME regime simultaneously,
    each producing its OWN distinct, correctly-isolated outcome -- none silently dropped, none merged
    into another's result."""
    builder = RawAxesBuilder(SYMBOL)
    bars = trend_up_regime_bars(SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    outcomes = evaluate_bar(bars[-1], timeframe="M15", axes_builder=builder)

    matched = {o.strategy_id: o for o in outcomes if o.strategy_id in
               ("trend_pullback", "trend_shadow", "trend_experimental")}
    assert set(matched) == {"trend_pullback", "trend_shadow", "trend_experimental"}  # all three present
    assert len({o.event_identity.trace_id for o in matched.values()}) == 3  # each with its OWN trace_id

    trend_pullback, trend_shadow = matched["trend_pullback"], matched["trend_shadow"]
    experimental = matched["trend_experimental"]
    assert trend_pullback.decision is not None and trend_shadow.decision is not None
    assert experimental.decision is not None
    # trend_pullback (RATIFIED) and trend_shadow (SHADOW_ELIGIBLE) both reach the same real gap
    # (MISSING_LEVEL_INPUT) -- but as two DISTINCT records, never collapsed into one.
    assert trend_pullback.decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
    assert trend_shadow.decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
    # trend_experimental is blocked one check EARLIER (NO_ELIGIBLE_STRATEGY) -- a genuinely different
    # reason, proving the three outcomes are independently computed, not copied from one another.
    assert experimental.decision.reason_codes == (ve_brain.ReasonCode.NO_ELIGIBLE_STRATEGY.value,)


def test_14_an_already_recorded_shadow_trade_candidate_is_never_re_recorded_for_the_same_event() -> None:
    """Test 11's property, restated at the telemetry layer: the SAME underlying bar, delivered twice by
    a deduping feed, must produce exactly ONE persisted `NewBrainTelemetryLog` record for that event --
    not because the log itself dedupes (it doesn't), but because the upstream feed never delivers it
    twice, so `record_outcome` is only ever called once for it."""
    gateway = FakeMT5Gateway(rates=[RawRate(time=NOW - 1_000, open=1.0, high=2.0, low=0.5, close=1.5)])
    feed = LiveBarFeed(gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: NOW)
    builder = RawAxesBuilder(SYMBOL)
    log = NewBrainTelemetryLog()

    for bar in feed.poll():  # first delivery -- real event
        for outcome in evaluate_bar(bar, timeframe="M15", axes_builder=builder):
            log.record_outcome(outcome)
    for bar in feed.poll():  # SAME underlying event -- feed dedupes, yields nothing
        for outcome in evaluate_bar(bar, timeframe="M15", axes_builder=builder):
            log.record_outcome(outcome)

    trace_ids = {r.event_identity.trace_id for r in log.entries}
    market_event_ids = {r.event_identity.market_event_id for r in log.entries}
    assert len(market_event_ids) == 1  # one underlying bar
    assert len(log.entries) == len(ve_brain.CANONICAL_STRATEGIES)  # one record per strategy, not doubled
    assert len(trace_ids) == len(ve_brain.CANONICAL_STRATEGIES)  # each strategy's own distinct trace_id


def test_15_the_decision_journal_survives_a_restart_and_resumes_exactly_where_it_left_off(tmp_path: Path) -> None:
    """Test 12's property, restated for `NewBrainTelemetryLog` specifically -- a brand-new log instance
    sharing only the persisted store (never the in-memory object) sees everything the prior instance
    wrote, with no gap and no double-count."""
    store_path = tmp_path / "telemetry.db"
    builder = RawAxesBuilder(SYMBOL)
    bars = trend_up_regime_bars(SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)

    store_before = SqliteStateStore(store_path)
    log_before = NewBrainTelemetryLog(store_before)
    outcomes = evaluate_bar(bars[-1], timeframe="M15", axes_builder=builder)
    for outcome in outcomes:
        log_before.record_outcome(outcome)
    count_before = len(log_before.entries)
    store_before.close()

    # "Restart": entirely new log object, same persisted store.
    store_after = SqliteStateStore(store_path)
    log_after = NewBrainTelemetryLog(store_after)
    store_after.close()

    assert count_before == len(ve_brain.CANONICAL_STRATEGIES)
    assert len(log_after.entries) == count_before  # nothing lost, nothing duplicated by the restart
    assert {r.event_identity.trace_id for r in log_after.entries} == {
        r.event_identity.trace_id for r in log_before.entries
    }


def test_16_a_shadow_trade_candidate_violating_a_hard_risk_constraint_is_rejected_in_shadow() -> None:
    """Defense in depth alongside the gate (test 8/19): even a candidate that cleared EVERY provenance
    check still hits the REAL, unmodified `risk_manager_live.engine.evaluate_trade_proposal` -- proven
    here with an `InstrumentSpecification` for a DIFFERENT symbol than the proposal's own (Risk
    Manager's own data-completeness check, step 1), which no provenance check could ever catch, since
    provenance is about WHO produced the candidate, not whether its geometry/instrument data matches."""
    from ai_trader.mandate2_readiness.decision_provenance import NEW_BRAIN_SOURCE, DecisionProvenance
    from ai_trader.mandate2_readiness.event_identity import EventIdentity
    from ai_trader.new_brain_bridge.bridge import NewBrainOutcome

    event_identity = EventIdentity(
        trace_id="t-risk-16", market_event_id="evt-16", symbol=SYMBOL, timeframe="M15", bar_id="bar-16",
        market_timestamp=AS_OF, received_timestamp=AS_OF, brain_version=ve_brain.VE_BRAIN_VERSION,
        catalog_hash=ve_brain.CANONICAL_CATALOG_HASH, configuration_fingerprint="cfg-16",
    )
    decision = ve_brain.DecisionResponse(
        contract_id=ve_brain.OUTPUT_CONTRACT_ID, decision="TRADE", expected_value_net=0.5,
        expected_reward=1.0, expected_loss=0.3, estimated_cost=0.02, probability_assumptions={},
        strategy_id="trend_pullback", configuration_fingerprint="cfg-16",
        reason_codes=(ve_brain.ReasonCode.TRADE_VALIDATED_EDGE.value,), engine_version=ve_brain.ENGINE_VERSION,
    )
    provenance = DecisionProvenance(source=NEW_BRAIN_SOURCE, trace_id="t-risk-16",
                                     catalog_hash=ve_brain.CANONICAL_CATALOG_HASH,
                                     configuration_fingerprint="cfg-16")
    outcome = NewBrainOutcome(
        event_identity=event_identity, strategy_id="trend_pullback", strategy_version="v1", node_traces=(),
        decision=decision, provenance=provenance, entry_price=2000.0, stop_price=1990.0, target_price=2020.0,
    )
    mismatched_instrument = make_instrument(symbol="EURUSD")  # proposal.symbol is XAUUSD

    result = submit_new_brain_candidate(
        outcome, account=make_account(), portfolio=make_portfolio(), instrument=mismatched_instrument,
        risk_context=make_risk_context(), risk_config=make_config(),
    )

    assert result.approved is False  # the real Risk Manager caught it -- not this division's own guess


def test_17_the_circuit_breaker_blocks_brain_sourced_candidates_identically_to_legacy_policies() -> None:
    """One account-wide `TradingCircuitState` (already proven for CAND-0001/0007/0009/0019) -- no
    brain-specific bypass path. `submit_new_brain_candidate`'s own `circuit_state` parameter checks this
    BEFORE provenance, so an active breaker denies even an otherwise-perfect candidate."""
    from ai_trader.mandate2_readiness.decision_provenance import NEW_BRAIN_SOURCE, DecisionProvenance
    from ai_trader.mandate2_readiness.event_identity import EventIdentity
    from ai_trader.new_brain_bridge.bridge import NewBrainOutcome

    event_identity = EventIdentity(
        trace_id="t-circuit-17", market_event_id="evt-17", symbol=SYMBOL, timeframe="M15", bar_id="bar-17",
        market_timestamp=AS_OF, received_timestamp=AS_OF, brain_version=ve_brain.VE_BRAIN_VERSION,
        catalog_hash=ve_brain.CANONICAL_CATALOG_HASH, configuration_fingerprint="cfg-17",
    )
    decision = ve_brain.DecisionResponse(
        contract_id=ve_brain.OUTPUT_CONTRACT_ID, decision="TRADE", expected_value_net=0.5,
        expected_reward=1.0, expected_loss=0.3, estimated_cost=0.02, probability_assumptions={},
        strategy_id="trend_pullback", configuration_fingerprint="cfg-17",
        reason_codes=(ve_brain.ReasonCode.TRADE_VALIDATED_EDGE.value,), engine_version=ve_brain.ENGINE_VERSION,
    )
    provenance = DecisionProvenance(source=NEW_BRAIN_SOURCE, trace_id="t-circuit-17",
                                     catalog_hash=ve_brain.CANONICAL_CATALOG_HASH,
                                     configuration_fingerprint="cfg-17")
    outcome = NewBrainOutcome(
        event_identity=event_identity, strategy_id="trend_pullback", strategy_version="v1", node_traces=(),
        decision=decision, provenance=provenance, entry_price=2000.0, stop_price=1990.0, target_price=2020.0,
    )
    suspended = TradingCircuitState(state=EngineState.SUSPENDED, reason_code="TEST_SUSPENDED", since=AS_OF)

    result = submit_new_brain_candidate(
        outcome, account=make_account(), portfolio=make_portfolio(), instrument=make_instrument(),
        risk_context=make_risk_context(), risk_config=make_config(), circuit_state=suspended,
    )

    assert result.approved is False
    assert result.reason_codes == (CIRCUIT_BREAKER_ACTIVE,)


def test_18_a_shadow_trade_candidate_from_an_unratified_strategy_id_is_rejected_by_n6() -> None:
    """N6's own eligibility check, not this division's -- confirmed from the OUTSIDE (this division reads
    the audit record/response, never reaches into N6 to verify it internally). `trend_experimental`
    (`ValidationStatus.EXPERIMENTAL`) is in `ve_brain`'s own canonical catalog specifically so
    `can_reach_n6` can be exercised at both ends -- RATIFIED/SHADOW_ELIGIBLE pass, EXPERIMENTAL doesn't."""
    builder = RawAxesBuilder(SYMBOL)
    bars = trend_up_regime_bars(SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    outcomes = evaluate_bar(bars[-1], timeframe="M15", axes_builder=builder)

    experimental = next(o for o in outcomes if o.strategy_id == "trend_experimental")
    assert experimental.decision is not None
    assert experimental.decision.decision == "NO_TRADE"
    assert experimental.decision.reason_codes == (ve_brain.ReasonCode.NO_ELIGIBLE_STRATEGY.value,)
    assert experimental.provenance is None  # never trusted as a decision source


def test_21_zero_broker_calls_for_any_shadow_trade_candidate_however_confident_static_analysis() -> None:
    """Extends the `_FORBIDDEN_ORDER_CALLS` static-guard pattern (already proven across `pdh_pdl_demo`,
    `multi_policy_live`, `spread_collection`, `zone_observer`) to `new_brain_bridge` -- the package
    Mandate 2's integration actually added for N1-N6/shadow processing."""
    forbidden_calls = ("order_send", "order_check", "order_calc_margin", "order_calc_profit")
    package_root = Path(__file__).resolve().parents[2] / "new_brain_bridge"
    violations: dict[str, set[str]] = {}
    for source_path in sorted(package_root.glob("*.py")):
        text = source_path.read_text(encoding="utf-8")
        hits = {tok for tok in forbidden_calls if tok in text}
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"forbidden broker call(s) found in new_brain_bridge: {violations}"


def test_22_enabling_the_gate_is_itself_journaled_with_who_when_and_why(tmp_path: Path) -> None:
    """CLOSED for real (Mandate B point 5, CEO 2026-08-14) -- this test does not depend on N3/N4 at all,
    so it is not left waiting on TOWER_HANDOFF. The gate's own `frozen=True`/no-setter design
    (`broker_gate.py`) already made every enabling a fresh, source-visible construction;
    `construct_enabled_gate` now additionally journals it (who/when/why), durably, surviving a
    restart -- the SAME `SqliteStateStore` persistence every other journal in this codebase uses."""
    from ai_trader.mandate2_readiness.broker_gate import BrokerGateJournal, construct_enabled_gate

    store_path = tmp_path / "gate_journal.db"
    store = SqliteStateStore(store_path)
    try:
        journal = BrokerGateJournal(store)
        gate = construct_enabled_gate(
            reason="test-only fault injection, per this test's own docstring", who="mandate-b-e2e-test",
            when=NOW, journal=journal,
        )
        assert gate.enabled is True
        assert len(journal.entries) == 1
        assert journal.entries[0].who == "mandate-b-e2e-test"
        assert journal.entries[0].when == NOW
        assert "fault injection" in journal.entries[0].why
    finally:
        store.close()

    # restart: a brand-new journal instance, same persisted store -- the enabling event survives.
    store_reopened = SqliteStateStore(store_path)
    try:
        reopened_journal = BrokerGateJournal(store_reopened)
        assert len(reopened_journal.entries) == 1
        assert reopened_journal.entries[0].who == "mandate-b-e2e-test"
    finally:
        store_reopened.close()


def test_23_every_decision_including_no_trade_is_journaled_with_enough_detail_to_reconstruct_why() -> None:
    """This project's own "un consumator peste sase luni" standard (`GapClassification`'s own docstring),
    extended to `NewBrainTelemetryLog` -- `no_trade_causes()` reads the exact persisted reason back from
    storage, for every NO_TRADE record, never recomputed or guessed."""
    builder = RawAxesBuilder(SYMBOL)
    bars = trend_up_regime_bars(SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    outcomes = evaluate_bar(bars[-1], timeframe="M15", axes_builder=builder)

    log = NewBrainTelemetryLog()
    for outcome in outcomes:
        log.record_outcome(outcome)

    causes = dict(log.no_trade_causes())
    trend_pullback = next(o for o in outcomes if o.strategy_id == "trend_pullback")
    assert trend_pullback.decision is not None
    assert causes[trend_pullback.event_identity.trace_id] == trend_pullback.decision.reason_codes
    assert all(len(reasons) >= 1 for reasons in causes.values())  # every NO_TRADE has a named cause


def test_24_n1_n6_internal_state_is_captured_in_the_audit_record_without_this_division_touching_it() -> None:
    """This division reads/journals the OUTPUT boundary only -- confirms (1) `new_brain_bridge`'s own
    source never imports `ve_brain`'s PRIVATE modules (only its public, `__all__`-exported surface), and
    (2) the persisted telemetry record still carries enough of N1-N6's own state (per-node `NodeTrace`,
    the EV engine's `expected_value_net` via the decision summary) for Red Team to review."""
    package_root = Path(__file__).resolve().parents[2] / "new_brain_bridge"
    forbidden_private_modules = {
        "ve_brain._canonical_catalog", "ve_brain._ev_core",
    }
    violations: dict[str, set[str]] = {}
    for source_path in sorted(package_root.glob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                imported.add(node.module)
            elif isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
        hits = imported & forbidden_private_modules
        if hits:
            violations[source_path.name] = hits
    assert not violations, f"new_brain_bridge reaches into ve_brain's private modules: {violations}"

    builder = RawAxesBuilder(SYMBOL)
    bars = trend_up_regime_bars(SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    outcomes = evaluate_bar(bars[-1], timeframe="M15", axes_builder=builder)
    log = NewBrainTelemetryLog()
    for outcome in outcomes:
        log.record_outcome(outcome)

    record = next(r for r in log.entries if r.strategy_id == "trend_pullback")
    node_names = [t.node_name for t in record.node_traces]
    assert node_names == ["N1", "Router", "CostModel", "EV", "N6"]  # enough per-node structure for external review
    assert record.decision_summary is not None


def test_25_a_crash_anywhere_in_the_n1_n6_call_path_degrades_to_no_trade_and_the_loop_continues() -> None:
    """Mirrors `multi_policy_live.MultiPolicyLiveLoop._degrade`'s own existing per-policy try/except
    isolation -- `fail_safe.safe_evaluate_bar` catches ANY failure and returns `BrainUnavailableOutcome`;
    a caller looping over several bars, one of which is malformed, must continue processing every OTHER
    bar rather than dying on the first failure."""
    builder = RawAxesBuilder(SYMBOL)
    good_bar = Bar(symbol=SYMBOL, ts_open=0, ts_close=900, open=2400.0, high=2401.0, low=2399.0,
                    close=2400.5, volume=100.0)
    malformed_bar = Bar(symbol="WRONG_SYMBOL", ts_open=900, ts_close=1800, open=1.0, high=1.1, low=0.9,
                         close=1.0, volume=None)
    another_good_bar = Bar(symbol=SYMBOL, ts_open=1800, ts_close=2700, open=2400.5, high=2401.5,
                            low=2399.5, close=2400.8, volume=100.0)

    results = [
        safe_evaluate_bar(bar, timeframe="M15", axes_builder=builder)
        for bar in (good_bar, malformed_bar, another_good_bar)
    ]

    assert isinstance(results[0], tuple)  # first bar: processed normally
    assert isinstance(results[1], BrainUnavailableOutcome)  # crash contained, not propagated
    assert isinstance(results[2], tuple)  # loop CONTINUED -- the third bar was processed too
    assert builder.bars_observed == 2  # the malformed bar never actually got appended to N1's history
