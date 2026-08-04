"""`PolicyOrchestrator` tests -- same submit->observe->audit lifecycle `pdh_pdl_demo`'s own
`PdhPdlOrchestrator` tests establish (this class's shared logic, verified independently here since it's
a separate file, not a byte-for-byte copy-paste trust), PLUS the two NEW pluggable hooks
(`mechanical_close`, `target_price_for_audit`) CAND-0009 needs and CAND-0001/0007/0019 don't."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Callable

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_orchestrator.tests._fixtures import make_deps, make_market_context
from ai_trader.live_signal_source.types import LiveCandidate
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.safety import verify_safety_guards
from ai_trader.mt5_demo_execution.tests._fixtures import AS_OF, FakeMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.multi_policy_live.orchestration import BarArrays, DemoDepsBundle, PolicyOrchestrator, day_boundary_mechanical_close
from ai_trader.order_manager.journal import OrderManagerAuditJournal
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.recognition_rule import PdhPdlTrigger
from ai_trader.pdh_pdl_demo.types import PdhPdlAuditKind, PendingPdhPdlTrade
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
TICK_SIZE = 0.01
MAGIC_NUMBER = 100_002


class _FakeFillReader:
    def __init__(self, is_open_sequence: list[bool | None], close_price: float | None) -> None:
        self._is_open_sequence = list(is_open_sequence)
        self._close_price = close_price
        self.is_position_open_calls: list[tuple[int, str]] = []

    def is_position_open(self, magic_number: int, symbol: str) -> bool | None:
        self.is_position_open_calls.append((magic_number, symbol))
        if not self._is_open_sequence:
            return True
        return self._is_open_sequence.pop(0)

    def read_close_price(self, magic_number: int, symbol: str, since_ts: int) -> float | None:
        return self._close_price


def _make_demo_deps_bundle(tmp_path: Path, entry_fill_price: float = 108.05) -> DemoDepsBundle:
    dry_run_deps = make_deps(tmp_path / "dry")
    order_send_result = SimpleNamespace(
        retcode=10009, comment="Request completed", order=123456, deal=654321, volume=0.01, price=entry_fill_price,
    )
    demo_gateway = FakeMT5DemoGateway(tick_time=AS_OF, order_send_result=order_send_result)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway, config=MT5DemoConfig(max_order_volume=1000.0))
    demo_adapter.connect()
    demo_deps = make_deps(
        tmp_path / "demo", ledger=OrderLedger(),
        order_journal=OrderManagerAuditJournal(tmp_path / "demo" / "journal.jsonl"), adapter=demo_adapter,
    )
    safety_report = verify_safety_guards(demo_adapter, MT5DemoConfig(max_order_volume=1000.0), symbol=SYMBOL, clock=lambda: AS_OF)
    return DemoDepsBundle(dry_run_deps=dry_run_deps, demo_deps=demo_deps, demo_adapter=demo_adapter, safety_guard_report=safety_report)


def _candidate(direction: Direction, entry: float, stop: float, target: float) -> LiveCandidate:
    return LiveCandidate(
        strategy_id="S9002", symbol=SYMBOL, direction=direction, entry=entry, stop=stop, target=target,
        session="ny", magic_number=MAGIC_NUMBER, comment="CAND-0007 test", as_of=AS_OF,
    )


def _trigger(direction: int, touch_idx: int, stop: float, target: float, day_label: int) -> PdhPdlTrigger:
    return PdhPdlTrigger(
        touch_idx=touch_idx, entry_idx=touch_idx + 1, direction=direction, strategy_stop_price=stop,
        target_price=target, atr_at_touch=1.0, day_boundary_label=day_label, effective_spread=0.2,
        executable_stop_price=stop + (0.5 if direction < 0 else -0.5), tick_size=TICK_SIZE,
    )


def test_submit_candidate_sends_through_the_existing_demo_pipeline(tmp_path: Path) -> None:
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path, entry_fill_price=108.05)
    orch = PolicyOrchestrator(SYMBOL, TICK_SIZE, MAGIC_NUMBER, lambda c, t: bundle, fill_reader, journal)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    outcome = orch.submit_candidate(candidate, trigger, make_market_context())

    assert outcome is not None and outcome.sent is True
    assert orch.pending is not None
    assert orch.pending.entry_realized_price == 108.05
    assert orch.magic_number == MAGIC_NUMBER


def test_a_second_candidate_while_one_is_open_is_refused(tmp_path: Path) -> None:
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PolicyOrchestrator(SYMBOL, TICK_SIZE, MAGIC_NUMBER, lambda c, t: bundle, fill_reader, journal)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    orch.submit_candidate(candidate, trigger, make_market_context())
    outcome2 = orch.submit_candidate(candidate, trigger, make_market_context())

    assert outcome2 is None
    reasons = [e.detail.get("reason_code") for e in journal.entries]
    assert "ALREADY_IN_POSITION" in reasons


def test_day_boundary_mechanical_close_matches_pdh_pdl_orchestrator_semantics() -> None:
    """`day_boundary_mechanical_close` alone, in isolation -- the default CAND-0007/CAND-0019 use."""
    pending = PendingPdhPdlTrade(
        symbol=SYMBOL, direction=-1, touch_idx=17, entry_idx=18, strategy_stop_price=111.0, target_price=90.0,
        atr_at_touch=1.0, day_end_idx=19, day_boundary_label=1_705_356_000, effective_spread=0.2,
        executable_stop_price=111.5, client_order_id="CID-1", broker_order_id=None, entry_as_of=AS_OF,
        entry_requested_price=108.0, entry_realized_price=108.05,
    )
    # same day -- never fires
    assert day_boundary_mechanical_close(pending, bar_idx=19, day_boundary_label=1_705_356_000, arrays=None) is None
    # new day, day_end_idx already set -- fires
    assert day_boundary_mechanical_close(pending, bar_idx=0, day_boundary_label=1_705_442_400, arrays=None) == "TIME_STOP"


def test_broker_side_close_is_detected_via_observe_bar(tmp_path: Path) -> None:
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[True, False], close_price=111.0)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PolicyOrchestrator(SYMBOL, TICK_SIZE, MAGIC_NUMBER, lambda c, t: bundle, fill_reader, journal)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    orch.submit_candidate(candidate, trigger, make_market_context())

    orch.observe_bar(bar_idx=18, day_boundary_label=1_705_356_000, ts_close=AS_OF + 900)
    assert orch.pending is not None and orch.pending.closed is False

    orch.observe_bar(bar_idx=19, day_boundary_label=1_705_356_000, ts_close=AS_OF + 1800)
    assert orch.pending is not None and orch.pending.closed is True
    assert orch.pending.close_reason == "BROKER_SLTP"


def _pending_trade(direction: int, entry_idx: int, stop: float, target: float, day_end_idx: int) -> PendingPdhPdlTrade:
    return PendingPdhPdlTrade(
        symbol=SYMBOL, direction=direction, touch_idx=entry_idx - 1, entry_idx=entry_idx,
        strategy_stop_price=stop, target_price=target, atr_at_touch=1.0, day_end_idx=day_end_idx,
        day_boundary_label=1_705_356_000, effective_spread=0.2,
        executable_stop_price=stop + (0.5 if direction < 0 else -0.5), client_order_id="CID-1",
        broker_order_id=None, entry_as_of=AS_OF, entry_requested_price=108.0, entry_realized_price=108.05,
        closed=True, close_realized_price=None, close_reason="BROKER_SLTP",
    )


def _audit(
    tmp_path: Path, pending: PendingPdhPdlTrade, open_: list[float], high: list[float], low: list[float],
    close: list[float],
    target_price_for_audit: Callable[[PendingPdhPdlTrade, BarArrays], float] | None = None,
) -> tuple[PolicyOrchestrator, PdhPdlAuditJournal]:
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PolicyOrchestrator(
        SYMBOL, TICK_SIZE, MAGIC_NUMBER, lambda c, t: bundle, fill_reader, journal,
        target_price_for_audit=target_price_for_audit,
    )
    orch._pending = pending
    orch.run_post_hoc_audit(AS_OF + 3600, open_, high, low, close)
    return orch, journal


def test_audit_example_stop(tmp_path: Path) -> None:
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 108.0; high[14] = 108.5; low[14] = 107.5; close[14] = 108.0
    high[15] = 112.0; low[15] = 107.0
    pending = _pending_trade(direction=-1, entry_idx=14, stop=111.0, target=90.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)
    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    assert result.detail["exit_reason"] == "stop"
    net_r = result.detail["net_R"]
    assert isinstance(net_r, float) and net_r < 0


def test_audit_example_stop_on_the_entry_bar_itself(tmp_path: Path) -> None:
    """RT-CODE-A-0005 D1 regression, exercised through THIS package's own PolicyOrchestrator (the
    demo_gate_engine's own D1 fix is already Red-Team-verified in isolation -- this proves the shared
    orchestrator, used by CAND-0007/CAND-0009/CAND-0019, triggers it correctly too). SHORT, entry bar's
    own HIGH breaches the executable stop before any later bar is ever scanned."""
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 108.0; high[14] = 112.0; low[14] = 107.5; close[14] = 108.0  # entry bar itself breaches
    pending = _pending_trade(direction=-1, entry_idx=14, stop=111.0, target=90.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)
    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    net_r = result.detail["net_R"]
    assert result.detail["exit_reason"] == "stop"
    assert result.detail["exit_idx"] == 14  # the entry bar itself, not a later scan bar
    assert isinstance(net_r, float) and net_r < 0  # a real loss, never a false TARGET/win


def test_audit_example_target(tmp_path: Path) -> None:
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 92.0; high[14] = 92.5; low[14] = 91.5; close[14] = 92.0
    high[15] = 110.5; low[15] = 91.8
    pending = _pending_trade(direction=1, entry_idx=14, stop=89.0, target=110.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)
    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    assert result.detail["exit_reason"] == "target"
    net_r = result.detail["net_R"]
    assert isinstance(net_r, float) and net_r > 0


def test_audit_example_time_stop(tmp_path: Path) -> None:
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 108.0; high[14] = 108.5; low[14] = 107.5; close[14] = 108.0
    close[19] = 107.0
    pending = _pending_trade(direction=-1, entry_idx=14, stop=111.0, target=90.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)
    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    assert result.detail["exit_reason"] == "time_stop"


def test_audit_example_invalid_execution(tmp_path: Path) -> None:
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 108.0; high[14] = 109.0; low[14] = 107.9; close[14] = 108.5
    pending = _pending_trade(direction=-1, entry_idx=14, stop=108.2, target=90.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)
    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    assert result.detail["exit_reason"] == "invalid_execution"


def test_audit_example_no_trade(tmp_path: Path) -> None:
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 111.5; high[14] = 112.0; low[14] = 111.0; close[14] = 111.8
    pending = _pending_trade(direction=-1, entry_idx=14, stop=111.0, target=90.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)
    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    assert result.detail["exit_reason"] == "no_trade"


def test_target_price_for_audit_hook_overrides_and_flags_sentinel(tmp_path: Path) -> None:
    """CAND-0009's own hook -- proves the override IS applied and the audit record discloses it."""
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 108.0; high[14] = 108.5; low[14] = 107.5; close[14] = 108.0
    close[19] = 107.5  # neither stop(111.0) nor the REAL target(90.0) touched -> would resolve time_stop anyway,
    # but this proves the override path runs without raising and flags the sentinel.
    pending = _pending_trade(direction=-1, entry_idx=14, stop=111.0, target=90.0, day_end_idx=19)

    calls: list[PendingPdhPdlTrade] = []

    def _sentinel(p: PendingPdhPdlTrade, arrays: BarArrays) -> float:
        calls.append(p)
        return -9999.0  # deliberately far from anything touchable

    orch, journal = _audit(tmp_path, pending, open_, high, low, close, target_price_for_audit=_sentinel)
    assert len(calls) == 1
    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    assert result.detail["target_price_is_sentinel"] is True
