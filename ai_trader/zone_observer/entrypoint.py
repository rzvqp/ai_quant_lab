"""`build_loop`/`main()` -- the continuous, unattended entrypoint for zone observation (CEO instruction,
2026-08-04: "Cableaza... Doar observare, fara politici").

**A NEW, separate process, deliberately not folded into the already-running `live_observation`
process.** `structural_observer` (which `live_observation` already runs) is an already-imported,
already-running Python process -- editing its source files would not take effect until that process
restarts, and restarting it was never asked for and is explicitly out of scope ("Nu opri procesele
existente"). A fifth independent MT5-connected process, following the exact same composition pattern
already proven safe four times this session (`live_observation`, `pdh_pdl_demo`, `multi_policy_live`,
`spread_collection`), lets the new detectors run starting now without touching anything already alive.

Same composition as `spread_collection/entrypoint.py`: read-only `RealMT5Gateway`, `LiveBarFeed`, the
existing `CandidateSignalProducer`/`LiveSignalLoop` generic infra, wired through
`ZoneObservingNullRecognitionRule` exactly the way `ObservingNullRecognitionRule` wires
`StructuralObserver`."""

from __future__ import annotations

from pathlib import Path

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway, RealMT5Gateway
from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.live_loop.loop import LiveSignalLoop
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.zone_observer.journal import ZoneObservationLog
from ai_trader.zone_observer.observer import ZoneObserver
from ai_trader.zone_observer.observing_rule import ZoneObservingNullRecognitionRule

SYMBOL = "XAUUSD"
MT5_TIMEFRAME_M15 = 15
BAR_SECONDS_M15 = 15 * 60
POLL_INTERVAL_SECONDS = 30.0
DEFAULT_STATE_DIR = Path(__file__).resolve().parents[2] / "zone_observer_state"
DEFAULT_DB_PATH = DEFAULT_STATE_DIR / "xauusd_m15.db"


def build_loop(
    gateway: MT5Gateway, state_store: SqliteStateStore, symbol: str = SYMBOL,
    mt5_timeframe: int = MT5_TIMEFRAME_M15, bar_seconds: int = BAR_SECONDS_M15,
    poll_interval_seconds: float = POLL_INTERVAL_SECONDS,
) -> LiveSignalLoop:
    feed = LiveBarFeed(gateway, symbol, mt5_timeframe, bar_seconds, state_store=state_store)
    signal_journal = LiveSignalJournal(state_store)
    zone_journal = ZoneObservationLog(state_store)
    observer = ZoneObserver(symbol, zone_journal)
    rule = ZoneObservingNullRecognitionRule(observer)
    producer = CandidateSignalProducer(feed, rule, signal_journal)
    return LiveSignalLoop(producer, state_store, poll_interval_seconds)


def main() -> None:
    DEFAULT_STATE_DIR.mkdir(parents=True, exist_ok=True)

    gateway = RealMT5Gateway()
    if not gateway.initialize():
        raise SystemExit(f"zone_observer: MT5 initialize() failed -- {gateway.last_error()!r}")

    state_store = SqliteStateStore(DEFAULT_DB_PATH)
    try:
        loop = build_loop(gateway, state_store)
        print(
            f"zone_observer: starting -- symbol={SYMBOL} mt5_timeframe={MT5_TIMEFRAME_M15} "
            f"bar_seconds={BAR_SECONDS_M15} poll_interval_seconds={POLL_INTERVAL_SECONDS} "
            f"db={DEFAULT_DB_PATH} -- no orders, no cost, observation only",
            flush=True,
        )
        loop.run_forever()
    finally:
        gateway.shutdown()


if __name__ == "__main__":
    main()
