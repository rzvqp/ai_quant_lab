"""`HeartbeatWriter`/`HeartbeatMonitor` tests."""

from __future__ import annotations

from pathlib import Path

from ai_trader.new_brain_live.heartbeat import HeartbeatMonitor, HeartbeatWriter, LiveShadowHeartbeat
from ai_trader.persistent_state.store import SqliteStateStore


def _heartbeat(**overrides: object) -> LiveShadowHeartbeat:
    base: dict[str, object] = dict(
        timestamp_utc=1_700_000_000, pid=1234, process_start_identity="1234:1_699_999_000",
        runtime_commit="abc1234", authority="NEW_BRAIN", broker_gate_state="DISABLED",
        tower_worker_session_id="sess-1", last_closed_bar_id="XAUUSD:M15:1700000000",
        last_market_event_id="XAUUSD:M15:1700000000", last_journal_sequence=5,
        last_outcome_reason="NO_DECISION", mt5_connected=True, balance=1800.34, equity=1800.34,
        open_orders=0, open_positions=0,
    )
    base.update(overrides)
    return LiveShadowHeartbeat(**base)  # type: ignore[arg-type]


def test_monitor_sees_none_before_any_heartbeat_written(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    monitor = HeartbeatMonitor(store)
    assert monitor.latest() is None
    assert monitor.is_stale(max_age_seconds=60.0) is True  # absence is fail-closed staleness


def test_write_then_read_round_trips(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat())
    latest = HeartbeatMonitor(store).latest()
    assert latest == _heartbeat()


def test_write_overwrites_not_appends(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    writer = HeartbeatWriter(store)
    writer.record(_heartbeat(pid=1))
    writer.record(_heartbeat(pid=2))
    writer.record(_heartbeat(pid=3))
    assert HeartbeatMonitor(store).latest() == _heartbeat(pid=3)


def test_heartbeat_persists_across_separate_store_instances(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    first = SqliteStateStore(db_path)
    HeartbeatWriter(first).record(_heartbeat())
    first.close()

    second = SqliteStateStore(db_path)
    assert HeartbeatMonitor(second).latest() == _heartbeat()


def test_is_stale_true_when_age_exceeds_threshold(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=1_000))
    assert HeartbeatMonitor(store).is_stale(max_age_seconds=60.0, now=1_100.0) is True


def test_is_stale_false_when_within_threshold(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=1_000))
    assert HeartbeatMonitor(store).is_stale(max_age_seconds=60.0, now=1_030.0) is False


def test_age_seconds_reflects_wall_clock(tmp_path: Path) -> None:
    import time
    hb = _heartbeat(timestamp_utc=int(time.time()) - 45)
    assert 40 <= hb.age_seconds <= 50
