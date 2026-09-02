"""Entrypoint for the Windows Scheduled Task `AITraderApprenticeshipV2` -- run_forever, singleton-
locked (its OWN distinct mutex name, `AITraderApprenticeshipV2`, so it can never collide with or
interfere with the already-running `AITraderS5MT5DemoSoak`/`AITraderLiveShadow` tasks' own locks),
opens its own independent read-only MT5 client attachment via `mt5_session`, never touches either of
those other processes' state or database files.

Structurally observation-only: this module's only I/O against the trading terminal happens through
`mt5_read_only_source.mt5_session` / `fetch_causal_closed_bars` -- no other MT5 call is reachable
from this entrypoint."""

from __future__ import annotations

import json
import signal
import time
import traceback
from pathlib import Path

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.loop import ApprenticeshipTick
from ai_trader.apprenticeship_v2.mt5_read_only_source import MT5ReadOnlyUnavailable, mt5_session
from ai_trader.new_brain_live.singleton import AlreadyRunningError, SingletonLock

POLL_INTERVAL_SECONDS = 60.0
HEARTBEAT_PATH = durable_store.LIVE_STATE_DIR / "heartbeat.json"

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
    tick = ApprenticeshipTick()
    print("apprenticeship_v2: starting, symbol=XAUUSD timeframe=M15 poll_interval=60s", flush=True)

    while not _stop_requested:
        last_error: str | None = None
        result: dict[str, object] | None = None
        try:
            with mt5_session():
                result = tick.tick()
            print(f"apprenticeship_v2: tick ok -- {result}", flush=True)
        except MT5ReadOnlyUnavailable as exc:
            last_error = f"MT5ReadOnlyUnavailable: {exc}"
            print(f"apprenticeship_v2: {last_error}", flush=True)
        except Exception:  # noqa: BLE001 -- a single tick failure must never crash the daemon
            last_error = traceback.format_exc()
            print(f"apprenticeship_v2: tick raised:\n{last_error}", flush=True)
        _write_heartbeat(alive=last_error is None, last_result=result, last_error=last_error)

        for _ in range(int(POLL_INTERVAL_SECONDS)):
            if _stop_requested:
                break
            time.sleep(1.0)

    print("apprenticeship_v2: stop requested, exiting cleanly", flush=True)


def main() -> None:
    lock = SingletonLock(name="AITraderApprenticeshipV2")
    try:
        lock.acquire()
    except AlreadyRunningError as exc:
        print(f"apprenticeship_v2: ALREADY_RUNNING -- {exc}", flush=True)
        raise SystemExit(0)
    try:
        run_forever()
    finally:
        lock.release()


if __name__ == "__main__":
    main()
