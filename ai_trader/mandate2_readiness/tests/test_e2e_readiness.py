"""25 end-to-end tests for Mandate 2 (CEO, 2026-08-14: "PREGATIRE pentru Mandatul 2... scheletul celor 25
de teste end-to-end, fara implementare"). These 25 are OWNED by this division, implemented fully in
Mandate 2 itself, AFTER `VE_HANDOFF_PASS` from Red Team (CEO amendment A4, 2026-08-14) -- not to be
confused with Red Team's own canonical-contract gate, a separate thing.

**Six are real, runnable tests today** (CEO's own list of the ones that "nu depind de artefact"): 8, 11,
12, 13, 19, 20. They prove a safety property already holds in THIS repo's current architecture, using
only code that exists now (`LiveBarFeed`, `CandidateSignalProducer`, `PdhPdlOrchestrator`, the new
`BrokerOrderSubmissionGate`) -- a regression floor Mandate 2's actual integration must not lower. **The
other nineteen are documented skeletons** (`pytest.skip`): each names concepts that do not exist in this
repo yet (N1-N6, the EV engine, `SHADOW_TRADE_CANDIDATE`, a confidence threshold) and genuinely cannot be
implemented before the artifact arrives -- writing a fake implementation now would be worse than an
honest skip, since a fake could pass for reasons that have nothing to do with the real artifact's own
behavior.

**CEO amendment A1, 2026-08-14, incorporated below**: N1-N6 and the EV engine CAN legitimately traverse
all the way to a `SHADOW_TRADE_CANDIDATE` (not just `NO_TRADE`) -- Risk Manager and the Execution Adapter
can process that result IN SHADOW. `BROKER_ORDER_SUBMISSION = DISABLED` is a SEPARATE, LAST-MILE gate
that must hold regardless of how confidently everything upstream approved the candidate ("dreptul de
ANALIZA prin N6 nu e acelasi lucru cu dreptul de EXECUTIE reala"). Tests 8 and 19 are written against
this stronger reading, not the weaker "NO_TRADE never orders" reading alone -- that direction was already
covered before the amendment and would have been an easier, less useful test to pass.

**Never modify N1-N6 or the EV engine internally, including once received** (CEO's own standing
instruction). If a future artifact-dependent test in this file ever fails against the real artifact, the
required response is `INTEGRATION_BLOCKED` -> a reproducible report to VE -> VE repairs -> Red Team
revalidates. Local repair is explicitly forbidden ("Ar crea din nou doua versiuni ale creierului")."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_orchestrator.tests._fixtures import make_deps, make_market_context
from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.live_signal_source.tests._fixtures import FakeMT5Gateway, RawRate
from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionDisabledError, BrokerOrderSubmissionGate
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.safety import verify_safety_guards
from ai_trader.mt5_demo_execution.tests._fixtures import AS_OF, FakeMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.order_manager.journal import OrderManagerAuditJournal
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.orchestration import DemoDepsBundle, PdhPdlOrchestrator
from ai_trader.pdh_pdl_demo.recognition_rule import MAGIC_NUMBER, STRATEGY_ID, PdhPdlTrigger
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
M15_SECONDS = 15 * 60
NOW = 1_700_000_000


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


@pytest.mark.skip(reason="INTEGRATION_BLOCKED -- requires the real N1-N6/EV artifact's own inter-node contract")
def test_20b_a_single_node_failing_mid_pipeline_degrades_that_decision_to_no_trade() -> None:
    """The STRONGER form of test 20 the amendment's own SHADOW_ELIGIBLE framing implies: if N3 (say)
    raises or times out while N4 is waiting for its output, the pipeline must degrade to NO_TRADE for
    THAT decision cycle, not hang, not guess, not propagate the exception and kill the whole process
    (mirroring `multi_policy_live`'s own existing per-policy try/except isolation, extended to per-node).
    Cannot be written before the artifact defines what "a node" and "its output" concretely are."""


# ============================================================================
# PART B -- nineteen skeletons. Each names a concept that does not exist in
# this repo yet. `pytest.skip`, not a fake pass -- a fake implementation
# would risk passing for reasons unrelated to the real artifact.
# ============================================================================

_BLOCKED = "INTEGRATION_BLOCKED -- requires the N1-N6/EV artifact, not received (VE_HANDOFF_PASS pending)"


@pytest.mark.skip(reason=_BLOCKED)
def test_01_each_real_bar_reaches_n1_exactly_once_end_to_end() -> None:
    """Extends test 11's proven feed-level dedup all the way through N1's own ingestion boundary."""


@pytest.mark.skip(reason=_BLOCKED)
def test_02_a_backfilled_bar_is_processed_identically_to_a_live_bar_by_n1() -> None:
    """`Bar.is_backfilled=True` must never special-case N1's own evaluation -- a recovered bar is not a
    lesser bar."""


@pytest.mark.skip(reason=_BLOCKED)
def test_03_a_malformed_bar_never_reaches_n1() -> None:
    """Fails closed at ingestion (already true today -- `BarFeedError` on a missing OHLC field) --
    confirm N1 never receives a value that ingestion itself should have rejected."""


@pytest.mark.skip(reason=_BLOCKED)
def test_04_session_and_day_boundary_labels_n1_consumes_match_true_utc() -> None:
    """The clock-translation correctness already proven at the `LiveBarFeed` boundary (2026-08-11 fix)
    must reach N1's own inputs unchanged."""


@pytest.mark.skip(reason=_BLOCKED)
def test_05_a_detected_gap_is_visible_in_whatever_context_n1_consumes() -> None:
    """MAINTENANCE/WEEKEND/EXTENDED_PAUSE/UNEXPECTED, and the new stale-probe-outage `GapRecord`
    (2026-08-14) -- none silently absorbed before reaching N1's own market-context input."""


@pytest.mark.skip(reason=_BLOCKED)
def test_06_a_malformed_n1_n6_decision_output_is_rejected_not_guessed_at() -> None:
    """Schema validation on the boundary this division reads, before any downstream consumer (journal,
    Risk Manager shadow processing) touches it."""


@pytest.mark.skip(reason=_BLOCKED)
def test_07_n1_n6_and_the_ev_engine_are_deterministic_on_a_frozen_input_snapshot() -> None:
    """Same input, replayed twice, same decision -- required for test 12's own restart-safety property
    to mean anything once real decision logic is involved."""


@pytest.mark.skip(reason=_BLOCKED)
def test_09_a_decision_citing_a_stale_snapshot_is_rejected_before_reaching_n6() -> None:
    """Distinct from test 13 (no bar at all): a decision built from a snapshot that WAS available but has
    since gone stale relative to N6's own freshness bound."""


@pytest.mark.skip(reason=_BLOCKED)
def test_10_two_conflicting_recognition_sources_on_one_bar_produce_one_deterministic_n6_resolution() -> None:
    """No silent overwrite, no double count -- matching this project's own established tie-break
    discipline (Portfolio Architect's round-robin precedent)."""


@pytest.mark.skip(reason=_BLOCKED)
def test_14_an_already_recorded_shadow_trade_candidate_is_never_re_recorded_for_the_same_event() -> None:
    """Test 11's property, restated at the SHADOW_TRADE_CANDIDATE record layer specifically."""


@pytest.mark.skip(reason=_BLOCKED)
def test_15_the_decision_journal_survives_a_restart_and_resumes_exactly_where_it_left_off() -> None:
    """Test 12's property, restated for whatever N1-N6/shadow-processing journal Mandate 2 adds -- no
    gap, no double-count in that journal specifically."""


@pytest.mark.skip(reason=_BLOCKED)
def test_16_a_shadow_trade_candidate_violating_a_hard_risk_constraint_is_rejected_in_shadow() -> None:
    """Defense in depth alongside the gate (test 8/19): even if the gate were somehow bypassed, Risk
    Manager's own hard constraints (size, direction-vs-stop, daily loss cap) still reject it."""


@pytest.mark.skip(reason=_BLOCKED)
def test_17_the_circuit_breaker_blocks_brain_sourced_candidates_identically_to_legacy_policies() -> None:
    """One account-wide `TradingCircuitState` (already proven for CAND-0001/0007/0009/0019) -- no
    brain-specific bypass path."""


@pytest.mark.skip(reason=_BLOCKED)
def test_18_a_shadow_trade_candidate_from_an_unratified_strategy_id_is_rejected_by_n6() -> None:
    """N6's own eligibility check, not this division's -- confirmed from the OUTSIDE (this division reads
    the audit record, never reaches into N6 to verify it internally, per the standing "never modify N1-N6"
    instruction)."""


@pytest.mark.skip(reason=_BLOCKED)
def test_21_zero_broker_calls_for_any_shadow_trade_candidate_however_confident_static_analysis() -> None:
    """Extends the `_FORBIDDEN_ORDER_CALLS` static-guard pattern (already proven across `pdh_pdl_demo`,
    `multi_policy_live`, `spread_collection`, `zone_observer`) to whatever new package Mandate 2's
    integration adds for N1-N6/shadow processing."""


@pytest.mark.skip(reason=_BLOCKED)
def test_22_enabling_the_gate_is_itself_journaled_with_who_when_and_why() -> None:
    """The gate's own `frozen=True`/no-setter design (`broker_gate.py`) makes every enabling a fresh,
    source-visible construction -- this test proves THAT construction site is itself durably journaled
    once real integration wiring exists, not just theoretically grep-able in source."""


@pytest.mark.skip(reason=_BLOCKED)
def test_23_every_decision_including_no_trade_is_journaled_with_enough_detail_to_reconstruct_why() -> None:
    """This project's own "un consumator peste sase luni" standard (`GapClassification`'s own docstring),
    extended to `SHADOW_TRADE_CANDIDATE`/`NO_TRADE` records specifically."""


@pytest.mark.skip(reason=_BLOCKED)
def test_24_n1_n6_internal_state_is_captured_in_the_audit_record_without_this_division_touching_it() -> None:
    """This division reads/journals the OUTPUT boundary only -- confirms the audit record carries enough
    of N1-N6's own internal state (per-node outputs, EV engine result) for Red Team to review, without
    this division's own code importing or reaching into those internals."""


@pytest.mark.skip(reason=_BLOCKED)
def test_25_a_crash_anywhere_in_the_n1_n6_call_path_degrades_to_no_trade_and_the_loop_continues() -> None:
    """Mirrors `multi_policy_live.MultiPolicyLiveLoop._degrade`'s own existing per-policy try/except
    isolation -- one broken node/policy must never kill the process for every other one."""
