"""On-demand uptime report -- run standalone, does NOT modify or need to touch the live
`spread_collection` process at all (opens its own short-lived connections, read-only against MT5,
appends to the SAME persisted state store the live process already writes to, exactly like every other
short-lived diagnostic script used in this project). Safe to run while the live collector keeps running.

    python -m ai_trader.spread_collection.uptime_report

Computes the window from the first ever recorded observation through now, reports bars_passed/
bars_recorded/ratio per session, persists it via `UptimeReportLog`, and prints a summary."""

from __future__ import annotations

import time

from ai_trader.execution_engine.adapters.mt5_gateway import RealMT5Gateway
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.spread_collection.entrypoint import BAR_SECONDS_M15, DEFAULT_DB_PATH, MT5_TIMEFRAME_M15, SYMBOL
from ai_trader.spread_collection.journal import SpreadObservationLog
from ai_trader.spread_collection.uptime import compute_session_uptime
from ai_trader.spread_collection.uptime_journal import UptimeReportLog


def main() -> None:
    now = int(time.time())
    state_store = SqliteStateStore(DEFAULT_DB_PATH)
    gateway = RealMT5Gateway()
    try:
        gateway.initialize()
        journal = SpreadObservationLog(state_store)
        if not journal.entries:
            print("no observations recorded yet -- nothing to measure")
            return
        window_start = min(obs.as_of for obs in journal.entries)
        window_end = now

        reports = compute_session_uptime(
            gateway, journal, SYMBOL, MT5_TIMEFRAME_M15, BAR_SECONDS_M15, window_start, window_end, now,
        )
        UptimeReportLog(state_store).record_all(reports)

        print(f"uptime report -- window {window_start} to {window_end} ({(window_end - window_start) / 3600:.1f}h)")
        for r in reports:
            ratio_str = "n/a (no bars in window)" if r.ratio is None else f"{r.ratio * 100:.1f}%"
            print(f"  {r.session:8s} passed={r.bars_passed:4d} recorded={r.bars_recorded:4d} ratio={ratio_str}")
    finally:
        gateway.shutdown()
        state_store.close()


if __name__ == "__main__":
    main()
