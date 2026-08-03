"""`PdhPdlLiveLoop` tests -- with fakes for `feed`/`rule`/`orchestrator`, never a real terminal. Plus one
`build_loop` wiring test with full-Protocol-satisfying fake gateways, confirming the real classes compose
without error."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.types import Bar, GapRecord, LiveCandidate
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.tests._fixtures import AS_OF, FakeMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.pdh_pdl_demo.entrypoint import PdhPdlLiveLoop, build_loop
from ai_trader.pdh_pdl_demo.recognition_rule import MAGIC_NUMBER, STRATEGY_ID, PdhPdlTrigger
from ai_trader.pdh_pdl_demo.risk_snapshot import LiveRiskSnapshotBuilder
from ai_trader.pdh_pdl_demo.types import PendingPdhPdlTrade
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.circuit_breaker import persist_circuit_state
from ai_trader.risk_manager_live.types import TradingCircuitState
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
BAR_SECONDS = 900


def _bar(ts_open: int) -> Bar:
    return Bar(symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + BAR_SECONDS,
               open=100.0, high=100.5, low=99.5, close=100.0, volume=10.0)


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
    """Scripted: emits `candidate_on_bar_index` (a candidate + trigger) exactly once, at the given
    zero-based bar position within a single `tick()` call's batch; `None` on every other bar."""

    def __init__(self, candidate_on_bar_index: int | None = None) -> None:
        self._candidate_on_bar_index = candidate_on_bar_index
        self._count = 0
        self._trigger = PdhPdlTrigger(
            touch_idx=0, entry_idx=1, direction=-1, strategy_stop_price=101.0, target_price=95.0,
            atr_at_touch=1.0, day_boundary_label=1_705_356_000, effective_spread=0.07,
            executable_stop_price=101.5, tick_size=0.01,
        )

    @property
    def current_bar_count(self) -> int:
        return self._count

    @property
    def current_arrays(self) -> tuple[list[float], list[float], list[float], list[float]]:
        return [100.0] * self._count, [100.5] * self._count, [99.5] * self._count, [100.0] * self._count

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        idx = self._count
        self._count += 1
        if idx == self._candidate_on_bar_index:
            return LiveCandidate(
                strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.SHORT, entry=100.0, stop=101.0,
                target=95.0, session="ny", magic_number=MAGIC_NUMBER, comment="test", as_of=bar.ts_close,
            )
        return None

    def last_trigger(self) -> PdhPdlTrigger | None:
        return self._trigger


def _pending(client_order_id: str, closed: bool) -> PendingPdhPdlTrade:
    return PendingPdhPdlTrade(
        symbol=SYMBOL, direction=-1, touch_idx=0, entry_idx=1, strategy_stop_price=101.0, target_price=95.0,
        atr_at_touch=1.0, day_end_idx=3, day_boundary_label=1_705_356_000, effective_spread=0.07,
        executable_stop_price=101.5, client_order_id=client_order_id, broker_order_id=None,
        entry_as_of=AS_OF, entry_requested_price=100.0, entry_realized_price=100.05,
        closed=closed, close_realized_price=101.0 if closed else None, close_reason="BROKER_SLTP" if closed else None,
    )


class _FakeOrchestrator:
    def __init__(self, pending_after_observe: PendingPdhPdlTrade | None = None) -> None:
        self.submit_calls: list[tuple[LiveCandidate, PdhPdlTrigger, dict[str, Any]]] = []
        self.observe_bar_calls: list[tuple[int, int, int]] = []
        self.audit_calls = 0
        self._pending = pending_after_observe

    @property
    def pending(self) -> PendingPdhPdlTrade | None:
        return self._pending

    def submit_candidate(self, candidate: LiveCandidate, trigger: PdhPdlTrigger, market_context: dict[str, Any]) -> Any:
        self.submit_calls.append((candidate, trigger, market_context))
        return None

    def observe_bar(self, bar_idx: int, day_boundary_label: int, ts_close: int) -> None:
        self.observe_bar_calls.append((bar_idx, day_boundary_label, ts_close))

    def run_post_hoc_audit(self, as_of: int, open_: list[float], high: list[float], low: list[float], close: list[float]) -> None:
        self.audit_calls += 1


def _loop(tmp_path: Path, feed: _FakeFeed, rule: _FakeRule, orchestrator: _FakeOrchestrator) -> tuple[PdhPdlLiveLoop, SqliteStateStore]:
    state_store = SqliteStateStore(tmp_path / "state.db")
    journal = LiveSignalJournal(state_store)
    risk_builder = LiveRiskSnapshotBuilder()
    loop = PdhPdlLiveLoop(feed, rule, orchestrator, journal, risk_builder, state_store, poll_interval_seconds=0.01)  # type: ignore[arg-type]
    return loop, state_store


def test_tick_short_circuits_before_touching_the_feed_when_circuit_not_ready(tmp_path: Path) -> None:
    feed = _FakeFeed([_bar(1_705_356_000)])
    loop, state_store = _loop(tmp_path, feed, _FakeRule(), _FakeOrchestrator())
    persist_circuit_state(state_store, TradingCircuitState(state=EngineState.SUSPENDED, reason_code="TEST", since=AS_OF), AS_OF)

    result = loop.tick()

    assert result is False
    assert feed.poll_calls == 0
    state_store.close()


def test_tick_processes_bars_when_circuit_is_ready(tmp_path: Path) -> None:
    bars = [_bar(1_705_356_000), _bar(1_705_356_900)]
    feed = _FakeFeed(bars)
    orchestrator = _FakeOrchestrator()
    loop, state_store = _loop(tmp_path, feed, _FakeRule(), orchestrator)

    result = loop.tick()

    assert result is True
    assert feed.poll_calls == 1
    assert len(orchestrator.observe_bar_calls) == len(bars)
    state_store.close()


def test_tick_submits_a_candidate_when_the_rule_produces_one_with_a_trigger(tmp_path: Path) -> None:
    bars = [_bar(1_705_356_000), _bar(1_705_356_900)]
    feed = _FakeFeed(bars)
    rule = _FakeRule(candidate_on_bar_index=1)
    orchestrator = _FakeOrchestrator()
    loop, state_store = _loop(tmp_path, feed, rule, orchestrator)

    loop.tick()

    assert len(orchestrator.submit_calls) == 1
    state_store.close()


def test_tick_runs_the_post_hoc_audit_once_when_a_position_is_freshly_closed(tmp_path: Path) -> None:
    bars = [_bar(1_705_356_000)]
    feed = _FakeFeed(bars)
    orchestrator = _FakeOrchestrator(pending_after_observe=_pending("CID-1", closed=True))
    loop, state_store = _loop(tmp_path, feed, _FakeRule(), orchestrator)

    loop.tick()

    assert orchestrator.audit_calls == 1
    state_store.close()


def test_tick_does_not_re_audit_the_same_already_audited_trade_on_a_later_tick(tmp_path: Path) -> None:
    feed = _FakeFeed([_bar(1_705_356_000)])
    orchestrator = _FakeOrchestrator(pending_after_observe=_pending("CID-1", closed=True))
    loop, state_store = _loop(tmp_path, feed, _FakeRule(), orchestrator)

    loop.tick()
    loop.tick()

    assert orchestrator.audit_calls == 1  # NOT 2 -- same client_order_id, already audited
    state_store.close()


def test_run_forever_stops_when_stop_is_called_and_closes_the_state_store(tmp_path: Path) -> None:
    import sqlite3

    import pytest

    feed = _FakeFeed([])
    loop, state_store = _loop(tmp_path, feed, _FakeRule(), _FakeOrchestrator())
    sleep_calls = []

    def _fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)
        loop.stop()

    loop.run_forever(sleep=_fake_sleep, install_signal_handlers=False)

    assert loop.stop_requested is True
    assert len(sleep_calls) == 1
    with pytest.raises(sqlite3.ProgrammingError):  # proves close() actually ran, not just that stop() fired
        state_store.get_value("anything")


def test_build_loop_wires_real_components_and_ticks_cleanly_with_fakes(tmp_path: Path) -> None:
    from ai_trader.mt5_demo_execution.gateway import RealMT5DemoGateway  # noqa: F401 -- typing only

    class _FakeOrderGateway(FakeMT5DemoGateway):
        def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any:
            return ()

    class _FakeHistoryGateway:
        def __init__(self) -> None:
            self.account = None

        def initialize(
            self, path: str | None = None, login: int | None = None, password: str | None = None,
            server: str | None = None,
        ) -> bool:
            return True

        def shutdown(self) -> None:
            pass

        def terminal_info(self) -> Any:
            return None

        def account_info(self) -> Any:
            return None

        def symbols_get(self) -> Any:
            return ()

        def symbol_info(self, symbol: str) -> Any:
            return None

        def symbol_select(self, symbol: str, enable: bool = True) -> bool:
            return True

        def symbol_info_tick(self, symbol: str) -> Any:
            return None

        def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any:
            return None

        def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any:
            return None

        def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any:
            return None

        def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any:
            return None

        def orders_get(self, symbol: str | None = None) -> Any:
            return ()

        def last_error(self) -> tuple[int, str]:
            return (0, "Success")

        def positions_get(self, symbol: str | None = None) -> Any:
            return ()

        def history_deals_get(self, date_from: int, date_to: int) -> Any:
            return ()

    order_gateway = _FakeOrderGateway(tick_time=AS_OF)
    history_gateway = _FakeHistoryGateway()
    demo_adapter = MT5DemoBrokerAdapter(gateway=order_gateway, config=MT5DemoConfig(max_order_volume=1000.0))
    demo_adapter.connect()
    state_store = SqliteStateStore(tmp_path / "wiring.db")

    loop = build_loop(order_gateway, history_gateway, demo_adapter, state_store, state_dir=tmp_path)  # type: ignore[arg-type]
    result = loop.tick()

    assert result is True
    state_store.close()
