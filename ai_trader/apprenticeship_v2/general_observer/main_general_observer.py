"""Entrypoint for General Observer V1.1's OWN, SEPARATE run loop -- NOT part of the existing
`AITraderApprenticeshipV2` Windows Scheduled Task, and not started by it. Mirrors `main.py`'s own
structure (singleton-locked `run_forever`, per-tick fail-safe try/except, a heartbeat file) closely,
deliberately, so this subsystem follows the exact same operational shape the S5 entrypoint already
uses in production -- but under its OWN distinct singleton mutex name
(`AITraderGeneralObserverV1_1`), so it can never collide with `AITraderApprenticeshipV2` or either of
the other already-running tasks' own locks (the same non-collision guarantee `main.py`'s own
docstring describes for itself), and its OWN heartbeat file, so operational monitoring of the two
subsystems never conflates them.

This module is never imported by, and never imports, `main.py` or `loop.py`. Starting General
Observer at all requires a deliberate, separate action (running this module, or wiring a SECOND
Windows Scheduled Task pointed at it) -- nothing here runs automatically as a side effect of the
existing S5 task (Section 30: no automatic live-production enablement). Rollback is trivial and
total: simply never start this entrypoint (or stop the second scheduled task, if one is created) --
`main.py`/`loop.py` and the entire S5 path are completely unaffected either way, since neither
contains a single line referencing this module.
"""

from __future__ import annotations

import json
import signal
import time
import traceback

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.general_observer.tick import GeneralObserverTick
from ai_trader.apprenticeship_v2.mt5_read_only_source import MT5ReadOnlyUnavailable, mt5_session
from ai_trader.new_brain_live.singleton import AlreadyRunningError, SingletonLock

POLL_INTERVAL_SECONDS = 60.0
HEARTBEAT_PATH = durable_store.LIVE_STATE_DIR / "heartbeat_general_observer.json"

_stop_requested = False


def _handle_stop_signal(signum: int, frame: object) -> None:
    global _stop_requested
    _stop_requested = True


def _write_heartbeat(*, alive: bool, last_result: dict[str, object] | None, last_error: str | None) -> None:
    durable_store.ensure_dirs()
    HEARTBEAT_PATH.write_text(json.dumps({
        "alive_as_of_utc": time.time(), "mt5_connected": alive, "last_result": last_result,
        "last_error": last_error, "poll_interval_seconds": POLL_INTERVAL_SECONDS,
    }, indent=2, default=str), encoding="utf-8")


def run_forever() -> None:
    signal.signal(signal.SIGINT, _handle_stop_signal)
    signal.signal(signal.SIGTERM, _handle_stop_signal)

    durable_store.ensure_dirs()
    tick = GeneralObserverTick()
    print("general_observer: starting, symbol=XAUUSD trigger_timeframe=M15 audit_timeframe=H1 poll_interval=60s", flush=True)

    while not _stop_requested:
        last_error: str | None = None
        result: dict[str, object] | None = None
        try:
            with mt5_session():
                result = tick.tick()
            print(f"general_observer: tick ok -- {result}", flush=True)
        except MT5ReadOnlyUnavailable as exc:
            last_error = f"MT5ReadOnlyUnavailable: {exc}"
            print(f"general_observer: {last_error}", flush=True)
        except Exception:  # noqa: BLE001 -- a single tick failure must never crash the daemon
            last_error = traceback.format_exc()
            print(f"general_observer: tick raised:\n{last_error}", flush=True)
        _write_heartbeat(alive=last_error is None, last_result=result, last_error=last_error)

        for _ in range(int(POLL_INTERVAL_SECONDS)):
            if _stop_requested:
                break
            time.sleep(1.0)

    print("general_observer: stop requested, exiting cleanly", flush=True)


def main() -> None:
    lock = SingletonLock(name="AITraderGeneralObserverV1_1")
    try:
        lock.acquire()
    except AlreadyRunningError as exc:
        print(f"general_observer: ALREADY_RUNNING -- {exc}", flush=True)
        raise SystemExit(0)
    try:
        run_forever()
    finally:
        lock.release()


if __name__ == "__main__":
    main()
