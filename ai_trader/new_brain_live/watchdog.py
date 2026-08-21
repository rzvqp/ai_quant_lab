"""LIVE_SHADOW watchdog (RT-N1-PERSIST-0001 section 3). A SEPARATE process from `new_brain_live` --
run periodically (its own lightweight trigger, e.g. every few minutes; NOT the main `AITraderLiveShadow`
task), it only ever READS: the heartbeat, the Scheduled Task's own state, and a fresh, independent PID
identity check. It never touches MT5 order/position state, never calls `set_authority`, never modifies
the broker gate -- confirmed by this package's own AST guard (`tests/test_ast_guard.py`).

**Alerts only on STATE TRANSITIONS** (CEO's own explicit "Nu trimite notificari la fiecare bara
normala"): the last-alerted state is persisted (`SqliteStateStore.set_text`, same store the heartbeat
itself lives in) and a new alert fires only when the CURRENT evaluation differs from it -- a healthy
system checked every 5 minutes for a week produces exactly one `STARTUP` notification, not 2000 "still
fine" messages.

**Guarded restart** (section 3's five explicit preconditions) is a separate, deliberately NOT
auto-wired function (`restart_preconditions_met`) -- this delivery builds and tests the precondition
check; actually TRIGGERING `schtasks /Run` is left for after the Scheduled Task exists (there is nothing
to restart yet -- see the cutover section of the delivery report)."""

from __future__ import annotations

import dataclasses
import subprocess
import time
from enum import Enum
from typing import Callable

from ai_trader.new_brain_bridge.authority import DecisionAuthority
from ai_trader.new_brain_bridge.no_console_window import NO_CONSOLE_WINDOW_CREATIONFLAGS
from ai_trader.new_brain_live.heartbeat import HeartbeatMonitor, LiveShadowHeartbeat
from ai_trader.new_brain_live.singleton import ProcessIdentityRecord, verify_process_identity
from ai_trader.persistent_state.store import SqliteStateStore

TASK_NAME = "AITraderLiveShadow"
DEFAULT_STALE_THRESHOLD_SECONDS = 180.0  # 6x the 30s live-loop poll interval -- generous, avoids false positives
EXPECTED_AUTHORITY = DecisionAuthority.NEW_BRAIN
EXPECTED_BROKER_GATE_STATE = "DISABLED"
_LAST_ALERT_STATE_KEY = "new_brain_live.watchdog_last_alert_state"
_PROCESS_IDENTITY_MARKERS = ("ai_trader.new_brain_live.entrypoint",)


def _default_process_identity_check(record: ProcessIdentityRecord, markers: tuple[str, ...]) -> bool:
    return verify_process_identity(record, markers=markers)


class WatchdogState(Enum):
    OK = "OK"
    NOT_RUNNING = "NOT_RUNNING"
    LIVE_SHADOW_STALLED = "LIVE_SHADOW_STALLED"
    MT5_UNAVAILABLE = "MT5_UNAVAILABLE"
    TOWER_UNAVAILABLE = "TOWER_UNAVAILABLE"
    AUTHORITY_MISMATCH = "AUTHORITY_MISMATCH"
    BROKER_GATE_MISMATCH = "BROKER_GATE_MISMATCH"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class WatchdogCheckResult:
    state: WatchdogState
    detail: str
    heartbeat: LiveShadowHeartbeat | None


def evaluate(
    state_store: SqliteStateStore, *, stale_threshold_seconds: float = DEFAULT_STALE_THRESHOLD_SECONDS,
    identity_markers: tuple[str, ...] = _PROCESS_IDENTITY_MARKERS,
    process_identity_check: Callable[[ProcessIdentityRecord, tuple[str, ...]], bool] = _default_process_identity_check,
) -> WatchdogCheckResult:
    """Pure evaluation of CURRENT state from persisted evidence -- no side effects, no notification.
    Order matters: absence/staleness is checked before trusting anything the heartbeat itself claims
    (a heartbeat that is itself stale cannot be trusted to say "MT5 connected")."""
    monitor = HeartbeatMonitor(state_store)
    heartbeat = monitor.latest()
    if heartbeat is None:
        return WatchdogCheckResult(state=WatchdogState.NOT_RUNNING, detail="no heartbeat ever recorded", heartbeat=None)

    if monitor.is_stale(max_age_seconds=stale_threshold_seconds):
        return WatchdogCheckResult(
            state=WatchdogState.LIVE_SHADOW_STALLED,
            detail=f"heartbeat age {heartbeat.age_seconds:.0f}s exceeds {stale_threshold_seconds:.0f}s",
            heartbeat=heartbeat,
        )

    record = ProcessIdentityRecord(pid=heartbeat.pid, executable="", command_line="")
    if not process_identity_check(record, identity_markers):
        return WatchdogCheckResult(
            state=WatchdogState.NOT_RUNNING,
            detail=f"PID {heartbeat.pid} from the last heartbeat is not running our process anymore",
            heartbeat=heartbeat,
        )

    if not heartbeat.mt5_connected:
        return WatchdogCheckResult(state=WatchdogState.MT5_UNAVAILABLE, detail="heartbeat reports MT5 disconnected", heartbeat=heartbeat)

    if heartbeat.tower_worker_session_id is None:
        return WatchdogCheckResult(state=WatchdogState.TOWER_UNAVAILABLE, detail="heartbeat reports no tower worker session", heartbeat=heartbeat)

    if heartbeat.authority != EXPECTED_AUTHORITY.value:
        return WatchdogCheckResult(
            state=WatchdogState.AUTHORITY_MISMATCH,
            detail=f"authority={heartbeat.authority!r}, expected {EXPECTED_AUTHORITY.value!r}", heartbeat=heartbeat,
        )

    if heartbeat.broker_gate_state != EXPECTED_BROKER_GATE_STATE:
        return WatchdogCheckResult(
            state=WatchdogState.BROKER_GATE_MISMATCH,
            detail=f"broker_gate_state={heartbeat.broker_gate_state!r}, expected {EXPECTED_BROKER_GATE_STATE!r}",
            heartbeat=heartbeat,
        )

    return WatchdogCheckResult(state=WatchdogState.OK, detail="healthy", heartbeat=heartbeat)


def _alert_label(previous: str | None, current: WatchdogState) -> str | None:
    """Maps a state TRANSITION to one of the CEO's own 8 named notification triggers. Returns `None`
    when the transition is a no-op (current == previous) -- the caller must not notify in that case."""
    if previous == current.value:
        return None
    if current is WatchdogState.OK:
        return "STARTUP" if previous is None else "RESTART"
    if current is WatchdogState.NOT_RUNNING:
        return "CRASH"
    if current is WatchdogState.LIVE_SHADOW_STALLED:
        return "HEARTBEAT_STALE"
    return str(current.value)  # MT5_UNAVAILABLE / TOWER_UNAVAILABLE / AUTHORITY_MISMATCH / BROKER_GATE_MISMATCH


def check_and_notify_on_transition(
    state_store: SqliteStateStore, *, notify: Callable[[str, str], None],
    stale_threshold_seconds: float = DEFAULT_STALE_THRESHOLD_SECONDS,
    process_identity_check: Callable[[ProcessIdentityRecord, tuple[str, ...]], bool] = _default_process_identity_check,
) -> WatchdogCheckResult:
    """The watchdog's one real per-run action: evaluate, compare against the persisted last-alerted
    state, notify ONLY on an actual transition, then persist the new state either way (so the next run
    has the correct baseline even when nothing was sent)."""
    result = evaluate(
        state_store, stale_threshold_seconds=stale_threshold_seconds,
        process_identity_check=process_identity_check,
    )
    previous = state_store.get_text(_LAST_ALERT_STATE_KEY)
    label = _alert_label(previous, result.state)
    if label is not None:
        notify(label, result.detail)
    state_store.set_text(_LAST_ALERT_STATE_KEY, result.state.value)
    return result


def query_task_state(task_name: str = TASK_NAME) -> dict[str, str] | None:
    """Real, read-only `schtasks` query. Returns `None` if the task does not exist (never raises for
    that expected case) -- parses the `/FO LIST /V` key:value output into a dict, most usefully
    `"Status"` and `"Last Result"`."""
    try:
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name, "/FO", "LIST", "/V"],
            capture_output=True, text=True, timeout=15, creationflags=NO_CONSOLE_WINDOW_CREATIONFLAGS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    info: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            info[key.strip()] = value.strip()
    return info


def restart_preconditions_met(
    *, gate_state: str, order_send_calls: int, open_orders: int | None, open_positions: int | None,
    process_confirmed_gone: bool,
) -> tuple[bool, tuple[str, ...]]:
    """The CEO's own 5 named preconditions (section 3), as one pure, independently-testable check --
    `watermark citit`/`checkpoint flush` are structural guarantees of `SqliteStateStore`'s own WAL/
    commit-per-statement design (verified separately, not re-checked here as a runtime condition; see
    the delivery report). Returns `(True, ())` only if every applicable condition holds; otherwise
    `(False, <failed-condition-names>)` -- callers must never proceed on a partial pass."""
    failed: list[str] = []
    if not process_confirmed_gone:
        failed.append("process_not_confirmed_gone")
    if gate_state != EXPECTED_BROKER_GATE_STATE:
        failed.append("broker_gate_not_disabled")
    if order_send_calls != 0:
        failed.append("order_send_calls_nonzero")
    if open_orders is None or open_orders != 0:
        failed.append("open_orders_not_zero_or_unknown")
    if open_positions is None or open_positions != 0:
        failed.append("open_positions_not_zero_or_unknown")
    return (len(failed) == 0, tuple(failed))


def real_notify(label: str, detail: str) -> None:
    """Real Telegram send -- reuses the SAME external `notify.py` tool (registry credentials,
    `ai_trader.telegram_notifier`, redaction) every other CEO-facing notification in this project
    already uses, rather than re-implementing credential loading here."""
    subprocess.run(
        [
            "python", r"C:\Users\MEDION GAMING\tools\notify.py", "AI TRADER WATCHDOG",
            f"{label}: {detail}", "", label,
        ],
        timeout=20, creationflags=NO_CONSOLE_WINDOW_CREATIONFLAGS,
    )
