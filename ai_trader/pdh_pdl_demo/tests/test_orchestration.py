"""`PdhPdlOrchestrator` tests -- full submit->observe->audit lifecycle with fakes, plus ONE worked
audit example per `ExitReason`: STOP, TARGET, TIME_STOP, NO_TRADE, INVALID_EXECUTION (the CEO's own
required pre-first-order deliverable, 2026-08-03: "cate un exemplu de audit per tip de rezolvare")."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_orchestrator.tests._fixtures import make_deps, make_market_context
from ai_trader.live_signal_source.types import LiveCandidate
from ai_trader.mt5_demo_execution import gating
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.safety import verify_safety_guards
from ai_trader.mt5_demo_execution.tests._fixtures import AS_OF, FakeMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_bridge.authority import DecisionAuthority
from ai_trader.order_manager.journal import OrderManagerAuditJournal
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.orchestration import DemoDepsBundle, PdhPdlOrchestrator
from ai_trader.pdh_pdl_demo.recognition_rule import STRATEGY_ID, MAGIC_NUMBER, PdhPdlTrigger
from ai_trader.pdh_pdl_demo.slippage import SlippageLeg, SlippageLog
from ai_trader.pdh_pdl_demo.types import PdhPdlAuditKind, PendingPdhPdlTrade
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
TICK_SIZE = 0.01


@pytest.fixture(autouse=True)
def _legacy_trading_unquarantined_for_lifecycle_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """CEO decision (AI Trader New Brain Architecture mandate): CAND-0001 is LEGACY_NON_AUTHORITY,
    quarantined by default (`gating.LEGACY_TRADING_AUTHORITY_QUARANTINED = True`). THIS file tests
    submit -> observe -> close/slippage/audit PIPELINE MECHANICS -- a concern orthogonal to whether
    CAND-0001 should be allowed to trade live today. That safety question is owned and tested
    exclusively by `mt5_demo_execution/tests/test_gating.py` and `test_legacy_quarantine_ast_guard.py`,
    whose production-default assertions this fixture never touches (it patches the imported binding
    only within THIS test module's own monkeypatch scope, undone automatically after each test).
    Unquarantining here preserves this file's original diagnostic value -- proving the lifecycle
    machinery itself still works, for audit/rollback purposes -- without weakening the real default."""
    monkeypatch.setattr(gating, "LEGACY_TRADING_AUTHORITY_QUARANTINED", False)


class _FakeFillReader:
    """`RealizedFillReader` fake -- scripted per test, records every call."""

    def __init__(self, is_open_sequence: list[bool | None], close_price: float | None) -> None:
        self._is_open_sequence = list(is_open_sequence)
        self._close_price = close_price
        self.is_position_open_calls: list[tuple[int, str]] = []
        self.read_close_price_calls: list[tuple[int, str, int]] = []

    def is_position_open(self, magic_number: int, symbol: str) -> bool | None:
        self.is_position_open_calls.append((magic_number, symbol))
        if not self._is_open_sequence:
            return True
        return self._is_open_sequence.pop(0)

    def read_close_price(self, magic_number: int, symbol: str, since_ts: int) -> float | None:
        self.read_close_price_calls.append((magic_number, symbol, since_ts))
        return self._close_price


def _make_demo_deps_bundle(tmp_path: Path, entry_fill_price: float = 2000.0) -> DemoDepsBundle:
    from types import SimpleNamespace

    dry_run_deps = make_deps(tmp_path / "dry")
    order_send_result = SimpleNamespace(
        retcode=10009, comment="Request completed", order=123456, deal=654321, volume=0.01,
        price=entry_fill_price,
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
    return DemoDepsBundle(
        dry_run_deps=dry_run_deps, demo_deps=demo_deps, demo_adapter=demo_adapter,
        safety_guard_report=safety_report,
    )


def _candidate(direction: Direction, entry: float, stop: float, target: float) -> LiveCandidate:
    return LiveCandidate(
        strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=direction, entry=entry, stop=stop, target=target,
        session="ny", magic_number=MAGIC_NUMBER, comment="CAND-0001 PDH-PDL DEMO", as_of=AS_OF,
    )


def _trigger(direction: int, touch_idx: int, stop: float, target: float, day_label: int) -> PdhPdlTrigger:
    return PdhPdlTrigger(
        touch_idx=touch_idx, entry_idx=touch_idx + 1, direction=direction, strategy_stop_price=stop,
        target_price=target, atr_at_touch=1.0, day_boundary_label=day_label, effective_spread=0.2,
        executable_stop_price=stop + (0.5 if direction < 0 else -0.5), tick_size=TICK_SIZE,
    )


def test_submit_candidate_sends_through_the_existing_demo_pipeline_and_tracks_the_position(tmp_path: Path) -> None:
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path, entry_fill_price=108.05)
    orch = PdhPdlOrchestrator(SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    outcome = orch.submit_candidate(candidate, trigger, make_market_context())

    assert outcome is not None and outcome.sent is True
    assert orch.pending is not None
    assert orch.pending.entry_realized_price == 108.05
    submitted = [e for e in journal.entries if e.kind is PdhPdlAuditKind.ENTRY_SUBMITTED]
    assert len(submitted) == 1


# -- Slippage collection wiring, CEO Mandate Step 8 (2026-08-13): additive, `slippage_log=None` by
# default (every test above this section never passes it -- proves backward compatibility by never
# needing to know about it). --


def test_submit_candidate_records_entry_slippage_when_a_slippage_log_is_given(tmp_path: Path) -> None:
    journal = PdhPdlAuditJournal()
    slippage_log = SlippageLog()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path, entry_fill_price=108.05)
    orch = PdhPdlOrchestrator(SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal, slippage_log=slippage_log)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    orch.submit_candidate(candidate, trigger, make_market_context())

    assert len(slippage_log.entries) == 1
    obs = slippage_log.entries[0]
    assert obs.leg is SlippageLeg.ENTRY
    assert obs.magic_number == MAGIC_NUMBER
    assert obs.requested_price == 108.0
    assert obs.realized_price == 108.05
    assert obs.signed_slippage == pytest.approx(0.05)
    assert obs.close_reason is None


def test_no_slippage_recorded_when_the_order_is_rejected(tmp_path: Path) -> None:
    """A rejected order has no `order_result` at all -- nothing was filled, nothing to measure. Rejection
    reproduced exactly like `mt5_demo_execution/tests/test_gating.py::
    test_demo_never_attempted_when_dry_run_fails` -- a candidate `as_of` stale vs. `market_context`'s own
    `as_of` fails the dry-run gate before any order is ever sent."""
    journal = PdhPdlAuditJournal()
    slippage_log = SlippageLog()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PdhPdlOrchestrator(
        SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal, slippage_log=slippage_log,
    )
    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    candidate = replace(candidate, as_of=AS_OF + 999_999)  # stale vs. make_market_context()'s own as_of
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)

    outcome = orch.submit_candidate(candidate, trigger, make_market_context())

    assert outcome is not None and outcome.sent is False
    assert "DRY_RUN_DID_NOT_PASS" in outcome.reason_codes
    assert slippage_log.entries == ()


def test_broker_side_close_records_exit_slippage(tmp_path: Path) -> None:
    journal = PdhPdlAuditJournal()
    slippage_log = SlippageLog()
    fill_reader = _FakeFillReader(is_open_sequence=[True, False], close_price=111.3)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PdhPdlOrchestrator(SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal, slippage_log=slippage_log)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    orch.submit_candidate(candidate, trigger, make_market_context())
    orch.observe_bar(bar_idx=18, day_boundary_label=1_705_356_000, ts_close=AS_OF + 900)
    orch.observe_bar(bar_idx=19, day_boundary_label=1_705_356_000, ts_close=AS_OF + 1800)

    exit_obs = [e for e in slippage_log.entries if e.leg is SlippageLeg.EXIT]
    assert len(exit_obs) == 1
    obs = exit_obs[0]
    assert obs.close_reason == "BROKER_SLTP"
    assert obs.realized_price == 111.3
    # executable_stop_price = stop + 0.5 = 111.5 (SHORT convention, see `_trigger`); 111.3 is nearer to
    # 111.5 than to target=90.0, so the reference is the executable stop.
    assert obs.requested_price == pytest.approx(111.5)
    assert obs.signed_slippage == pytest.approx(111.3 - 111.5)


def test_time_stop_close_does_not_record_exit_slippage(tmp_path: Path) -> None:
    """The disclosed limitation: no closing deal exists for a TIME_STOP close today (see `slippage.py`'s
    own module docstring) -- recording a reference price for a fill that doesn't exist would misrepresent
    it as measured. Entry slippage IS still recorded (that leg is unaffected)."""
    journal = PdhPdlAuditJournal()
    slippage_log = SlippageLog()
    fill_reader = _FakeFillReader(is_open_sequence=[True, True], close_price=105.0)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PdhPdlOrchestrator(SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal, slippage_log=slippage_log)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    orch.submit_candidate(candidate, trigger, make_market_context())
    orch.observe_bar(bar_idx=18, day_boundary_label=1_705_356_000, ts_close=AS_OF + 900)
    orch.observe_bar(bar_idx=0, day_boundary_label=1_705_442_400, ts_close=AS_OF + 1800)  # TIME_STOP

    assert orch.pending is not None and orch.pending.close_reason == "TIME_STOP"
    legs = [e.leg for e in slippage_log.entries]
    assert legs == [SlippageLeg.ENTRY]  # exactly one entry observation, zero exit observations


def test_a_second_candidate_while_one_is_open_is_refused_and_journaled(tmp_path: Path) -> None:
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PdhPdlOrchestrator(SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    orch.submit_candidate(candidate, trigger, make_market_context())

    outcome2 = orch.submit_candidate(candidate, trigger, make_market_context())
    assert outcome2 is None
    reasons = [e.detail.get("reason_code") for e in journal.entries]
    assert "ALREADY_IN_POSITION" in reasons


def test_broker_side_close_is_detected_via_observe_bar(tmp_path: Path) -> None:
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[True, False], close_price=111.0)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PdhPdlOrchestrator(SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    orch.submit_candidate(candidate, trigger, make_market_context())

    orch.observe_bar(bar_idx=18, day_boundary_label=1_705_356_000, ts_close=AS_OF + 900)
    assert orch.pending is not None and orch.pending.closed is False  # still same day, still "open"

    orch.observe_bar(bar_idx=19, day_boundary_label=1_705_356_000, ts_close=AS_OF + 1800)
    assert orch.pending is not None and orch.pending.closed is True
    assert orch.pending.close_reason == "BROKER_SLTP"
    assert orch.pending.close_realized_price == 111.0


def test_day_end_closer_fires_mechanically_when_still_open_after_the_entry_day_ends(tmp_path: Path) -> None:
    """CEO's own constraint: mechanical, day-boundary-only, no other criteria."""
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[True, True], close_price=105.0)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PdhPdlOrchestrator(SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal)

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    orch.submit_candidate(candidate, trigger, make_market_context())

    orch.observe_bar(bar_idx=18, day_boundary_label=1_705_356_000, ts_close=AS_OF + 900)  # still same day
    assert orch.pending is not None and orch.pending.day_end_idx == 18

    orch.observe_bar(bar_idx=0, day_boundary_label=1_705_442_400, ts_close=AS_OF + 1800)  # NEW day started
    assert orch.pending is not None and orch.pending.closed is True
    assert orch.pending.close_reason == "TIME_STOP"
    assert orch.pending.day_end_idx == 18  # frozen at the LAST bar of the entry day, not the new day's


def _pending_trade(direction: int, entry_idx: int, stop: float, target: float, day_end_idx: int) -> PendingPdhPdlTrade:
    return PendingPdhPdlTrade(
        symbol=SYMBOL, direction=direction, touch_idx=entry_idx - 1, entry_idx=entry_idx,
        strategy_stop_price=stop, target_price=target, atr_at_touch=1.0, day_end_idx=day_end_idx,
        day_boundary_label=1_705_356_000, effective_spread=0.2,
        executable_stop_price=stop + (0.5 if direction < 0 else -0.5), client_order_id="CID-1",
        broker_order_id=None, entry_as_of=AS_OF, entry_requested_price=108.0, entry_realized_price=108.05,
        closed=True, close_realized_price=None, close_reason="BROKER_SLTP",
    )


def _audit(tmp_path: Path, pending: PendingPdhPdlTrade, open_: list[float], high: list[float],
           low: list[float], close: list[float]) -> tuple[PdhPdlOrchestrator, PdhPdlAuditJournal]:
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path)
    orch = PdhPdlOrchestrator(SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal)
    orch._pending = pending  # test-only direct injection -- exercising run_post_hoc_audit in isolation
    orch.run_post_hoc_audit(AS_OF + 3600, open_, high, low, close)
    return orch, journal


def test_audit_example_stop(tmp_path: Path) -> None:
    """SHORT (PDH touch): price rises and hits the executable stop before target or day-end."""
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 108.0; high[14] = 108.5; low[14] = 107.5; close[14] = 108.0  # entry bar (idx 14)
    high[15] = 112.0; low[15] = 107.0  # breaches executable_stop_price=111.5

    pending = _pending_trade(direction=-1, entry_idx=14, stop=111.0, target=90.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)

    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    net_r = result.detail["net_R"]
    assert result.detail["exit_reason"] == "stop"
    assert isinstance(net_r, float) and net_r < 0


def test_audit_example_stop_on_the_entry_bar_itself(tmp_path: Path) -> None:
    """RT-CODE-A-0005 D1 regression, exercised through THIS package's own orchestration code (the
    demo_gate_engine's own D1 fix is already Red-Team-verified in isolation -- this proves OUR caller
    triggers it correctly, not just that the vendored engine has it). Before the fix (submodule pinned
    at 86304e7, DemoSignal.day_end_idx), an entry-bar stop breach was silently ignored and the trade
    scanned onward from entry_idx+1 -- a real loss could be misreported as a win. SHORT, entry bar's own
    HIGH breaches the executable stop before any later bar is ever scanned."""
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
    """LONG (PDL touch): price falls then rises to the opposite level (target) before stop/day-end."""
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 92.0; high[14] = 92.5; low[14] = 91.5; close[14] = 92.0  # entry bar (idx 14)
    high[15] = 110.5; low[15] = 91.8  # reaches target=110.0 without breaching the stop first

    pending = _pending_trade(direction=1, entry_idx=14, stop=89.0, target=110.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)

    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    net_r = result.detail["net_R"]
    assert result.detail["exit_reason"] == "target"
    assert isinstance(net_r, float) and net_r > 0


def test_audit_example_time_stop(tmp_path: Path) -> None:
    """Neither stop nor target touched by day_end_idx -- exits at the day's own closing price."""
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 108.0; high[14] = 108.5; low[14] = 107.5; close[14] = 108.0
    close[19] = 107.0  # the day's own final close -- neither stop(111.5) nor target(90) ever touched

    pending = _pending_trade(direction=-1, entry_idx=14, stop=111.0, target=90.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)

    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    assert result.detail["exit_reason"] == "time_stop"
    assert result.detail["exit_price"] == 107.0


def test_audit_example_invalid_execution(tmp_path: Path) -> None:
    """A gap through the FLOORED stop right at entry (S2 floor > raw structural distance) -- the
    convention's own narrow INVALID_EXECUTION case, not a routine stop hit."""
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    # entry bar: reference/entry=108.0, structural stop=108.2 (tiny raw distance -> floored by S2),
    # but the SAME entry bar's own high already breaches the floored stop -> gap-through-floor.
    open_[14] = 108.0; high[14] = 109.0; low[14] = 107.9; close[14] = 108.5

    pending = _pending_trade(direction=-1, entry_idx=14, stop=108.2, target=90.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)

    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    assert result.detail["exit_reason"] == "invalid_execution"
    assert result.detail["floored"] is True


def test_audit_example_no_trade(tmp_path: Path) -> None:
    """The engine's OWN entry-guard NO_TRADE -- the LIVE tick passed the pre-trade check, but the
    ACTUAL recorded bar open (once available) is already beyond the structural stop: the disclosed
    "dual entry-price" divergence (live tick proxy vs. the bar's own official open), not a bug."""
    n = 20
    open_ = [100.0] * n; high = [100.5] * n; low = [99.5] * n; close = [100.0] * n
    open_[14] = 111.5  # the RECORDED bar open is already beyond the structural stop (111.0, SHORT)
    high[14] = 112.0; low[14] = 111.0; close[14] = 111.8

    pending = _pending_trade(direction=-1, entry_idx=14, stop=111.0, target=90.0, day_end_idx=19)
    orch, journal = _audit(tmp_path, pending, open_, high, low, close)

    result = [e for e in journal.entries if e.kind is PdhPdlAuditKind.AUDIT_RESULT][0]
    assert result.detail["exit_reason"] == "no_trade"
    assert result.detail["net_R"] is None


# -- Mandate 2, section 4 (CEO, 2026-08-14): the LEGACY_SHADOW_TELEMETRY demotion hook. `authority_check
# =None` (every test above this section) is byte-for-byte the pre-Mandate-2 behavior; these tests prove
# the NEW_BRAIN branch instead, using the exact same real demo-gate pipeline fixtures the ENTRY_SUBMITTED
# test above already established as genuine (not a stub), so "the gate was never called" is a real,
# checkable absence, not a mocked assumption. --

def test_new_brain_authority_skips_the_gate_entirely_and_records_legacy_shadow_telemetry(tmp_path: Path) -> None:
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path, entry_fill_price=108.05)
    orch = PdhPdlOrchestrator(
        SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal,
        authority_check=lambda: DecisionAuthority.NEW_BRAIN,
    )

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    outcome = orch.submit_candidate(candidate, trigger, make_market_context())

    assert outcome is None
    assert orch.pending is None  # never entered a position -- never called the gate at all
    kinds = [e.kind for e in journal.entries]
    assert kinds == [PdhPdlAuditKind.LEGACY_SHADOW_TELEMETRY]
    assert journal.entries[0].detail["reason_code"] == "NEW_BRAIN_AUTHORITY_ACTIVE"


def test_legacy_authority_explicit_still_uses_the_real_gate_unchanged(tmp_path: Path) -> None:
    """The `authority_check` callable itself returning `DecisionAuthority.LEGACY` (not just `None`) must
    behave identically to `authority_check=None` -- proves the branch is genuinely conditional on the
    VALUE returned, not merely on whether a callable was supplied."""
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path, entry_fill_price=108.05)
    orch = PdhPdlOrchestrator(
        SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal,
        authority_check=lambda: DecisionAuthority.LEGACY,
    )

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    outcome = orch.submit_candidate(candidate, trigger, make_market_context())

    assert outcome is not None and outcome.sent is True
    assert orch.pending is not None


def test_authority_check_is_called_fresh_every_submit_not_cached(tmp_path: Path) -> None:
    """Matches `PolicyControl`'s/the circuit breaker's own re-read-every-tick discipline -- a caller
    whose authority flips between two submissions must see the flip immediately, never a stale value
    cached from construction time."""
    journal = PdhPdlAuditJournal()
    fill_reader = _FakeFillReader(is_open_sequence=[], close_price=None)
    bundle = _make_demo_deps_bundle(tmp_path, entry_fill_price=108.05)
    calls: list[DecisionAuthority] = [DecisionAuthority.LEGACY, DecisionAuthority.NEW_BRAIN]
    orch = PdhPdlOrchestrator(
        SYMBOL, TICK_SIZE, lambda c, t: bundle, fill_reader, journal, authority_check=lambda: calls.pop(0),
    )

    candidate = _candidate(Direction.SHORT, entry=108.0, stop=111.0, target=90.0)
    trigger1 = _trigger(direction=-1, touch_idx=17, stop=111.0, target=90.0, day_label=1_705_356_000)
    first = orch.submit_candidate(candidate, trigger1, make_market_context())
    assert first is not None and first.sent is True  # popped LEGACY first -- normal path

    # already in a position, so the SECOND call would ordinarily hit ALREADY_IN_POSITION -- but the
    # authority check must run BEFORE that check, per submit_candidate's own top-of-function ordering.
    trigger2 = _trigger(direction=-1, touch_idx=25, stop=111.0, target=90.0, day_label=1_705_356_000)
    second = orch.submit_candidate(candidate, trigger2, make_market_context())
    assert second is None
    kinds = [e.kind for e in journal.entries]
    assert kinds[-1] == PdhPdlAuditKind.LEGACY_SHADOW_TELEMETRY
