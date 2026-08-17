"""`watchdog` decisive tests: state evaluation, transition-only alerting (never per-normal-bar), and
the guarded-restart preconditions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_trader.new_brain_live.heartbeat import HeartbeatWriter, LiveShadowHeartbeat
from ai_trader.new_brain_live.watchdog import (
    WatchdogState,
    check_and_notify_on_transition,
    evaluate,
    restart_preconditions_met,
)
from ai_trader.persistent_state.store import SqliteStateStore


def _heartbeat(**overrides: object) -> LiveShadowHeartbeat:
    base: dict[str, object] = dict(
        timestamp_utc=1_700_000_000, pid=1234, process_start_identity="1234:1_699_999_000",
        runtime_commit="abc1234", authority="NEW_BRAIN", broker_gate_state="DISABLED",
        tower_worker_session_id="sess-1", last_closed_bar_id=None, last_market_event_id=None,
        last_journal_sequence=0, last_outcome_reason=None, mt5_connected=True, balance=1.0, equity=1.0,
        open_orders=0, open_positions=0,
    )
    base.update(overrides)
    return LiveShadowHeartbeat(**base)  # type: ignore[arg-type]


_ALWAYS_ALIVE: Any = lambda record, markers: True
_NEVER_ALIVE: Any = lambda record, markers: False


def test_evaluate_not_running_when_no_heartbeat_ever_written(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    result = evaluate(store)
    assert result.state is WatchdogState.NOT_RUNNING


def test_evaluate_stalled_when_heartbeat_too_old(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=1_000))
    result = evaluate(store, stale_threshold_seconds=60.0, process_identity_check=_ALWAYS_ALIVE)
    assert result.state is WatchdogState.LIVE_SHADOW_STALLED


def test_evaluate_not_running_when_pid_identity_check_fails(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    import time
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time())))
    result = evaluate(store, process_identity_check=_NEVER_ALIVE)
    assert result.state is WatchdogState.NOT_RUNNING


def test_evaluate_mt5_unavailable(tmp_path: Path) -> None:
    import time
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time()), mt5_connected=False))
    result = evaluate(store, process_identity_check=_ALWAYS_ALIVE)
    assert result.state is WatchdogState.MT5_UNAVAILABLE


def test_evaluate_tower_unavailable(tmp_path: Path) -> None:
    import time
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time()), tower_worker_session_id=None))
    result = evaluate(store, process_identity_check=_ALWAYS_ALIVE)
    assert result.state is WatchdogState.TOWER_UNAVAILABLE


def test_evaluate_authority_mismatch(tmp_path: Path) -> None:
    import time
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time()), authority="LEGACY"))
    result = evaluate(store, process_identity_check=_ALWAYS_ALIVE)
    assert result.state is WatchdogState.AUTHORITY_MISMATCH


def test_evaluate_broker_gate_mismatch(tmp_path: Path) -> None:
    import time
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time()), broker_gate_state="ENABLED"))
    result = evaluate(store, process_identity_check=_ALWAYS_ALIVE)
    assert result.state is WatchdogState.BROKER_GATE_MISMATCH


def test_evaluate_ok_when_everything_healthy(tmp_path: Path) -> None:
    import time
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time())))
    result = evaluate(store, process_identity_check=_ALWAYS_ALIVE)
    assert result.state is WatchdogState.OK


def test_no_notification_on_repeated_ok_state(tmp_path: Path) -> None:
    """The CEO's own explicit "Nu trimite notificari la fiecare bara normala" -- a healthy system
    checked repeatedly must notify exactly once (the initial STARTUP), never again while it stays OK."""
    import time
    store = SqliteStateStore(tmp_path / "state.db")
    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time())))

    notifications: list[tuple[str, str]] = []
    for _ in range(5):
        check_and_notify_on_transition(
            store, notify=lambda label, detail: notifications.append((label, detail)),
            process_identity_check=_ALWAYS_ALIVE,
        )

    assert len(notifications) == 1
    assert notifications[0][0] == "STARTUP"


def test_notification_on_transition_to_stalled_then_recovery(tmp_path: Path) -> None:
    import time
    store = SqliteStateStore(tmp_path / "state.db")
    notifications: list[tuple[str, str]] = []

    def notify(label: str, detail: str) -> None:
        notifications.append((label, detail))

    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time())))
    check_and_notify_on_transition(store, notify=notify, process_identity_check=_ALWAYS_ALIVE)  # STARTUP
    assert [n[0] for n in notifications] == ["STARTUP"]

    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time()) - 1_000))
    check_and_notify_on_transition(store, notify=notify, stale_threshold_seconds=60.0, process_identity_check=_ALWAYS_ALIVE)  # -> STALLED
    assert [n[0] for n in notifications] == ["STARTUP", "HEARTBEAT_STALE"]

    HeartbeatWriter(store).record(_heartbeat(timestamp_utc=int(time.time())))
    check_and_notify_on_transition(store, notify=notify, process_identity_check=_ALWAYS_ALIVE)  # -> OK again == RESTART
    assert [n[0] for n in notifications] == ["STARTUP", "HEARTBEAT_STALE", "RESTART"]


def test_notification_state_survives_across_store_instances(tmp_path: Path) -> None:
    """The transition baseline is durable -- a watchdog restarted itself must not re-notify STARTUP for
    an already-known-OK system."""
    import time
    db_path = tmp_path / "state.db"
    first = SqliteStateStore(db_path)
    HeartbeatWriter(first).record(_heartbeat(timestamp_utc=int(time.time())))
    notified_first: list[tuple[str, str]] = []
    check_and_notify_on_transition(first, notify=lambda l, d: notified_first.append((l, d)), process_identity_check=_ALWAYS_ALIVE)
    first.close()
    assert notified_first == [("STARTUP", "healthy")]

    second = SqliteStateStore(db_path)
    notified_second: list[tuple[str, str]] = []
    check_and_notify_on_transition(second, notify=lambda l, d: notified_second.append((l, d)), process_identity_check=_ALWAYS_ALIVE)
    assert notified_second == []  # still OK -> OK, no re-notification


def test_restart_preconditions_all_met() -> None:
    ok, failed = restart_preconditions_met(
        gate_state="DISABLED", order_send_calls=0, open_orders=0, open_positions=0,
        process_confirmed_gone=True,
    )
    assert ok is True
    assert failed == ()


def test_restart_preconditions_fail_closed_on_process_not_confirmed_gone() -> None:
    ok, failed = restart_preconditions_met(
        gate_state="DISABLED", order_send_calls=0, open_orders=0, open_positions=0,
        process_confirmed_gone=False,
    )
    assert ok is False
    assert "process_not_confirmed_gone" in failed


def test_restart_preconditions_fail_closed_on_unknown_positions() -> None:
    """`open_positions=None` (couldn't be verified) must NEVER be treated as "assume zero" -- fail
    closed on missing evidence, exactly like every other gate in this codebase."""
    ok, failed = restart_preconditions_met(
        gate_state="DISABLED", order_send_calls=0, open_orders=0, open_positions=None,
        process_confirmed_gone=True,
    )
    assert ok is False
    assert "open_positions_not_zero_or_unknown" in failed


def test_restart_preconditions_fail_closed_on_nonzero_order_send_calls() -> None:
    ok, failed = restart_preconditions_met(
        gate_state="DISABLED", order_send_calls=1, open_orders=0, open_positions=0,
        process_confirmed_gone=True,
    )
    assert ok is False
    assert "order_send_calls_nonzero" in failed


def test_restart_preconditions_reports_all_failures_not_just_the_first() -> None:
    ok, failed = restart_preconditions_met(
        gate_state="ENABLED", order_send_calls=2, open_orders=None, open_positions=None,
        process_confirmed_gone=False,
    )
    assert ok is False
    assert set(failed) == {
        "process_not_confirmed_gone", "broker_gate_not_disabled", "order_send_calls_nonzero",
        "open_orders_not_zero_or_unknown", "open_positions_not_zero_or_unknown",
    }
