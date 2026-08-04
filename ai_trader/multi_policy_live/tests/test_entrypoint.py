"""`MultiPolicyLiveLoop` tests -- with fakes for `rule`/`orchestrator`, never a real terminal. Focuses on
this loop's OWN logic (two-phase per-bar processing, per-policy try/except isolation with auto-degrade,
the shared account-wide circuit-breaker read, exclusion-group refusal) -- recognition/orchestration
logic itself is already covered by their own dedicated test files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.types import Bar, GapRecord, LiveCandidate
from ai_trader.multi_policy_live.entrypoint import MultiPolicyLiveLoop, PolicyRuntime
from ai_trader.multi_policy_live.exclusion import LevelDayExclusion
from ai_trader.multi_policy_live.policy_control import PolicyControl
from ai_trader.multi_policy_live.recognition_dz_level_confluence import STRATEGY_ID, MAGIC_NUMBER
from ai_trader.multi_policy_live.vendor_bridge import LevelKind
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.recognition_rule import PdhPdlTrigger
from ai_trader.pdh_pdl_demo.risk_snapshot import LiveRiskSnapshotBuilder
from ai_trader.pdh_pdl_demo.types import PdhPdlAuditKind, PendingPdhPdlTrade
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager_live.circuit_breaker import persist_circuit_state
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.types import TradingCircuitState
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
BAR_SECONDS = 900
DAY1_START = 1_705_356_000


def _bar(ts_open: int) -> Bar:
    return Bar(symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + BAR_SECONDS, open=100.0, high=100.5, low=99.5, close=100.0, volume=10.0)


class _FakeFeed:
    def __init__(self, bars: list[Bar], gaps: tuple[GapRecord, ...] = ()) -> None:
        self._bars = bars
        self._gaps = gaps
        self.poll_calls = 0

    def poll(self) -> tuple[Bar, ...]:
        self.poll_calls += 1
        return tuple(self._bars)

    def last_gaps(self) -> tuple[GapRecord, ...]:
        return self._gaps


class _FakeRule:
    def __init__(self, candidate: LiveCandidate | None = None, raise_on_evaluate: bool = False) -> None:
        self._candidate = candidate
        self._raise = raise_on_evaluate
        self._count = 0
        self.evaluate_calls = 0
        self._trigger = PdhPdlTrigger(
            touch_idx=0, entry_idx=1, direction=1, strategy_stop_price=99.0, target_price=105.0,
            atr_at_touch=1.0, day_boundary_label=DAY1_START, effective_spread=0.07,
            executable_stop_price=98.5, tick_size=0.01,
        )

    @property
    def current_bar_count(self) -> int:
        return self._count

    @property
    def current_arrays(self) -> tuple[list[float], list[float], list[float], list[float]]:
        return [100.0] * self._count, [100.5] * self._count, [99.5] * self._count, [100.0] * self._count

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        self.evaluate_calls += 1
        self._count += 1
        if self._raise:
            raise RuntimeError("boom")
        return self._candidate

    def last_trigger(self) -> PdhPdlTrigger | None:
        return self._trigger if self._candidate is not None else None

    def last_touch_level_kind(self) -> LevelKind | None:
        return LevelKind.PDL if self._candidate is not None else None


class _FakeOrchestrator:
    def __init__(self, pending_after_observe: PendingPdhPdlTrade | None = None) -> None:
        self.submit_calls: list[Any] = []
        self.observe_calls: list[Any] = []
        self.audit_calls = 0
        self._pending = pending_after_observe

    @property
    def pending(self) -> PendingPdhPdlTrade | None:
        return self._pending

    def submit_candidate(self, candidate: LiveCandidate, trigger: PdhPdlTrigger, market_context: dict[str, Any]) -> None:
        self.submit_calls.append((candidate, trigger))
        return None

    def observe_bar(
        self, bar_idx: int, day_boundary_label: int, ts_close: int,
        arrays: tuple[list[float], list[float], list[float], list[float]] | None = None,
    ) -> None:
        self.observe_calls.append((bar_idx, day_boundary_label, ts_close))

    def run_post_hoc_audit(
        self, as_of: int, open_: list[float], high: list[float], low: list[float], close: list[float],
    ) -> None:
        self.audit_calls += 1


def _candidate() -> LiveCandidate:
    return LiveCandidate(
        strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.LONG, entry=100.0, stop=99.0, target=105.0,
        session="ny", magic_number=MAGIC_NUMBER, comment="test", as_of=DAY1_START,
    )


def _loop(
    tmp_path: Path, feed: _FakeFeed, policies: list[PolicyRuntime], cand0001_db: Path | None = None,
) -> tuple[MultiPolicyLiveLoop, SqliteStateStore]:
    state_store = SqliteStateStore(tmp_path / "state.db")
    signal_journal = LiveSignalJournal(state_store)
    risk_builder = LiveRiskSnapshotBuilder()
    policy_control = PolicyControl(state_store)
    exclusion = LevelDayExclusion(cand0001_db if cand0001_db is not None else tmp_path / "cand0001.db")
    circuit_path = cand0001_db if cand0001_db is not None else (tmp_path / "cand0001.db")
    loop = MultiPolicyLiveLoop(
        feed, policies, signal_journal, risk_builder, state_store, policy_control, exclusion, circuit_path, 0.01,  # type: ignore[arg-type]
    )
    return loop, state_store


def _enable_all(state_store: SqliteStateStore, policy_ids: list[str]) -> None:
    control = PolicyControl(state_store)
    for pid in policy_ids:
        control.set_enabled(pid, True)


def test_tick_short_circuits_when_circuit_not_ready(tmp_path: Path) -> None:
    feed = _FakeFeed([_bar(DAY1_START)])
    audit = PdhPdlAuditJournal()
    policy = PolicyRuntime("CAND-0007", _FakeRule(), _FakeOrchestrator(), audit)
    loop, state_store = _loop(tmp_path, feed, [policy])

    circuit_store = SqliteStateStore(tmp_path / "cand0001.db")
    persist_circuit_state(circuit_store, TradingCircuitState(state=EngineState.SUSPENDED, reason_code="TEST", since=DAY1_START), DAY1_START)
    circuit_store.close()

    result = loop.tick()

    assert result is False
    assert feed.poll_calls == 0
    state_store.close()


def test_enabled_policy_submits_a_candidate(tmp_path: Path) -> None:
    feed = _FakeFeed([_bar(DAY1_START)])
    audit = PdhPdlAuditJournal()
    orchestrator = _FakeOrchestrator()
    policy = PolicyRuntime("CAND-0007", _FakeRule(candidate=_candidate()), orchestrator, audit)
    loop, state_store = _loop(tmp_path, feed, [policy])
    _enable_all(state_store, ["CAND-0007"])

    loop.tick()

    assert len(orchestrator.submit_calls) == 1
    assert len(orchestrator.observe_calls) == 1
    state_store.close()


def test_disabled_policy_evaluates_for_the_signal_journal_but_never_submits(tmp_path: Path) -> None:
    feed = _FakeFeed([_bar(DAY1_START)])
    audit = PdhPdlAuditJournal()
    rule = _FakeRule(candidate=_candidate())
    orchestrator = _FakeOrchestrator()
    policy = PolicyRuntime("CAND-0009", rule, orchestrator, audit)
    loop, state_store = _loop(tmp_path, feed, [policy])
    # never enabled -- defaults False

    loop.tick()

    assert rule.evaluate_calls == 1
    assert len(orchestrator.submit_calls) == 0
    # observe_bar still runs regardless of pause state (monitors any pre-existing position)
    assert len(orchestrator.observe_calls) == 1
    state_store.close()


def test_a_policy_that_raises_on_evaluate_is_degraded_and_others_continue(tmp_path: Path) -> None:
    feed = _FakeFeed([_bar(DAY1_START)])
    audit_a = PdhPdlAuditJournal()
    audit_b = PdhPdlAuditJournal()
    rule_a = _FakeRule(raise_on_evaluate=True)
    orch_a = _FakeOrchestrator()
    rule_b = _FakeRule(candidate=_candidate())
    orch_b = _FakeOrchestrator()
    policy_a = PolicyRuntime("CAND-0007", rule_a, orch_a, audit_a)
    policy_b = PolicyRuntime("CAND-0019", rule_b, orch_b, audit_b)
    loop, state_store = _loop(tmp_path, feed, [policy_a, policy_b])
    _enable_all(state_store, ["CAND-0007", "CAND-0019"])

    loop.tick()

    assert "CAND-0007" in loop.degraded_policy_ids
    assert "CAND-0019" not in loop.degraded_policy_ids
    assert len(orch_b.submit_calls) == 1  # the OTHER policy still worked
    reasons = [e.detail.get("reason_code") for e in audit_a.entries]
    assert "POLICY_ERROR_EVALUATE" in reasons

    # a SECOND tick must not re-evaluate the degraded policy
    loop.tick()
    assert rule_a.evaluate_calls == 1
    state_store.close()


def test_exclusion_refuses_submission_when_cand0001_already_entered_same_level_same_day(tmp_path: Path) -> None:
    from ai_trader.pdh_pdl_demo.types import PdhPdlAuditEntry

    cand0001_db = tmp_path / "cand0001.db"
    store = SqliteStateStore(cand0001_db)
    PdhPdlAuditJournal(store, log_name="pdh_pdl_demo.audit").record(PdhPdlAuditEntry(
        symbol=SYMBOL, as_of=DAY1_START + 3600, kind=PdhPdlAuditKind.ENTRY_SUBMITTED,
        detail={"direction": 1, "client_order_id": "CID-CAND0001"},  # direction>0 -> PDL (CAND-0001 convention)
    ))
    store.close()

    feed = _FakeFeed([_bar(DAY1_START)])
    audit = PdhPdlAuditJournal()
    orchestrator = _FakeOrchestrator()
    policy = PolicyRuntime("CAND-0009", _FakeRule(candidate=_candidate()), orchestrator, audit, check_exclusion_against_cand0001=True)
    loop, state_store = _loop(tmp_path, feed, [policy], cand0001_db=cand0001_db)
    _enable_all(state_store, ["CAND-0009"])

    loop.tick()

    assert len(orchestrator.submit_calls) == 0
    reasons = [e.detail.get("reason_code") for e in audit.entries]
    assert "EXCLUSION_LEVEL_CONFLICT_WITH_CAND0001" in reasons
    state_store.close()


def test_run_forever_stops_when_stop_is_called(tmp_path: Path) -> None:
    feed = _FakeFeed([])
    audit = PdhPdlAuditJournal()
    policy = PolicyRuntime("CAND-0007", _FakeRule(), _FakeOrchestrator(), audit)
    loop, state_store = _loop(tmp_path, feed, [policy])
    calls = []

    def _fake_sleep(seconds: float) -> None:
        calls.append(seconds)
        loop.stop()

    loop.run_forever(sleep=_fake_sleep, install_signal_handlers=False)

    assert loop.stop_requested is True
    assert len(calls) == 1
