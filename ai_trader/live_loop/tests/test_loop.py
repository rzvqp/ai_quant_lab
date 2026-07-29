"""`LiveSignalLoop` tests -- Mandate 4, Item #7 (2026-07-28): the last infrastructure piece before
shadow mode. Every capability it orchestrates (restart-correct watermark, gap journaling, circuit-state
consultation) was already independently proven in Mandates 2 and 3; these tests prove the LOOP wires
them together correctly, not that the underlying pieces work (they already are)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.live_loop.loop import LiveSignalLoop
from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.live_signal_source.tests._fixtures import FakeMT5Gateway, RawRate
from ai_trader.live_signal_source.types import NullRecognitionRule
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.circuit_breaker import persist_circuit_state
from ai_trader.risk_manager_live.types import TradingCircuitState

SYMBOL = "XAUUSD"
M15_SECONDS = 15 * 60
NOW = 1_700_000_000


def _build_producer(store: SqliteStateStore, rates: list[RawRate], now: int = NOW) -> CandidateSignalProducer:
    gateway = FakeMT5Gateway(rates=rates)
    feed = LiveBarFeed(
        gateway, SYMBOL, mt5_timeframe=15, bar_seconds=M15_SECONDS, clock=lambda: now, state_store=store,
    )
    journal = LiveSignalJournal(state_store=store)
    return CandidateSignalProducer(feed, NullRecognitionRule(), journal)


def test_tick_processes_new_bars_when_circuit_is_ready(tmp_path: Path) -> None:
    """No circuit state ever persisted -- `load_persisted_circuit_state` defaults to READY -- so the
    very first tick must still process bars, not skip them."""
    store = SqliteStateStore(tmp_path / "state.db")
    closed_open = NOW - 1_000
    producer = _build_producer(store, [RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    loop = LiveSignalLoop(producer, store, poll_interval_seconds=1.0)

    ran = loop.tick()

    assert ran is True


def test_tick_skips_processing_when_suspended(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    persist_circuit_state(
        store, TradingCircuitState(state=EngineState.SUSPENDED, reason_code="LOSS_DAILY", since=NOW), NOW,
    )
    closed_open = NOW - 1_000
    producer = _build_producer(store, [RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    loop = LiveSignalLoop(producer, store, poll_interval_seconds=1.0)

    ran = loop.tick()

    assert ran is False
    # the producer's own feed/journal share this store -- if tick() had actually run the producer,
    # a bar would have been journaled. It must not have been.
    journal = LiveSignalJournal(state_store=store)
    assert journal.entries == ()


def test_tick_skips_processing_when_emergency_stopped(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    persist_circuit_state(
        store, TradingCircuitState(state=EngineState.EMERGENCY_STOP, reason_code="CIRCUIT_EMERGENCY_STOP_REQUESTED", since=NOW),
        NOW,
    )
    closed_open = NOW - 1_000
    producer = _build_producer(store, [RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)])
    loop = LiveSignalLoop(producer, store, poll_interval_seconds=1.0)

    assert loop.tick() is False


def test_circuit_breaker_is_consulted_from_the_persisted_store_not_a_stale_snapshot(tmp_path: Path) -> None:
    """The circuit breaker must be re-read from disk on every single tick -- not cached at
    construction -- so a suspension that happens between ticks takes effect immediately."""
    store = SqliteStateStore(tmp_path / "state.db")
    first_open = NOW - 2 * M15_SECONDS
    producer = _build_producer(
        store,
        [RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5),
         RawRate(time=first_open + M15_SECONDS, open=1.5, high=2.5, low=1.0, close=2.0)],
    )
    loop = LiveSignalLoop(producer, store, poll_interval_seconds=1.0)

    assert loop.tick() is True  # READY -- processes the first bar

    persist_circuit_state(
        store, TradingCircuitState(state=EngineState.EMERGENCY_STOP, reason_code="X", since=NOW), NOW,
    )
    assert loop.tick() is False  # now suspended -- must skip, even though nothing about `loop` changed


def test_run_forever_ticks_repeatedly_until_stop(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    producer = _build_producer(store, [])
    loop = LiveSignalLoop(producer, store, poll_interval_seconds=1.0)

    tick_count = 0
    real_tick = loop.tick

    def _counting_tick() -> bool:
        nonlocal tick_count
        tick_count += 1
        if tick_count >= 3:
            loop.stop()
        return real_tick()

    loop.tick = _counting_tick  # type: ignore[method-assign]
    sleeps: list[float] = []
    loop.run_forever(sleep=sleeps.append, install_signal_handlers=False)

    assert tick_count == 3
    assert sleeps == [1.0, 1.0, 1.0]  # one sleep after every tick, including the one that stopped it


def test_run_forever_closes_the_state_store_on_exit(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    producer = _build_producer(store, [])
    loop = LiveSignalLoop(producer, store, poll_interval_seconds=1.0)
    loop.stop()  # stop before the first tick -- run_forever must still close the store on the way out

    loop.run_forever(sleep=lambda _seconds: None, install_signal_handlers=False)

    with pytest.raises(Exception):
        store.get_value("anything")  # a closed sqlite3 connection raises on any further operation


def test_stop_can_be_called_before_run_forever_and_it_never_ticks(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    producer = _build_producer(store, [RawRate(time=NOW - 1_000, open=1.0, high=2.0, low=0.5, close=1.5)])
    loop = LiveSignalLoop(producer, store, poll_interval_seconds=1.0)
    loop.stop()

    ticked: list[int] = []

    def _tracking_tick() -> bool:
        ticked.append(1)
        return True

    loop.tick = _tracking_tick  # type: ignore[method-assign]
    loop.run_forever(sleep=lambda _seconds: None, install_signal_handlers=False)

    assert ticked == []


def test_signal_handler_calls_stop(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    producer = _build_producer(store, [])
    loop = LiveSignalLoop(producer, store, poll_interval_seconds=1.0)

    loop._handle_stop_signal(0, None)

    assert loop.stop_requested is True


# -- restart-correctness and gap journaling, proven END TO END through the loop, not just the feed --


def test_restart_resumes_from_the_persisted_watermark_through_the_loop(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    store_before_restart = SqliteStateStore(db_path)
    closed_open = NOW - 1_000
    producer_before_restart = _build_producer(
        store_before_restart, [RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)],
    )
    loop_before_restart = LiveSignalLoop(producer_before_restart, store_before_restart, poll_interval_seconds=1.0)
    assert loop_before_restart.tick() is True
    store_before_restart.close()

    store_after_restart = SqliteStateStore(db_path)
    producer_after_restart = _build_producer(
        store_after_restart, [RawRate(time=closed_open, open=1.0, high=2.0, low=0.5, close=1.5)],
    )
    loop_after_restart = LiveSignalLoop(producer_after_restart, store_after_restart, poll_interval_seconds=1.0)
    loop_after_restart.tick()  # same bar still returned by the gateway -- must NOT be reprocessed

    journal = LiveSignalJournal(state_store=store_after_restart)
    assert len(journal.entries) == 1  # not 2 -- the restart did not lose the watermark


def test_gaps_are_journaled_through_the_loop(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    first_open = NOW - 5 * 60 * 60
    second_open = NOW - 1_000
    producer = _build_producer(
        store,
        [RawRate(time=first_open, open=1.0, high=2.0, low=0.5, close=1.5),
         RawRate(time=second_open, open=1.5, high=2.5, low=1.0, close=2.0)],
    )
    loop = LiveSignalLoop(producer, store, poll_interval_seconds=1.0)

    loop.tick()

    journal = LiveSignalJournal(state_store=store)
    assert len(journal.gaps) == 1
    assert journal.gaps[0].gap_start == first_open
    assert journal.gaps[0].gap_end == second_open
