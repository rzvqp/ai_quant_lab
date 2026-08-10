"""`build_loop` composes the real live pipeline from already-built, already-tested pieces; `main()` is
the actual process entrypoint the CEO's "Porneste observarea live" activates.

**Fixed for this run** (CEO specified XAUUSD; timeframe/poll-cadence are this package's own operational
choice, disclosed rather than left implicit): `SYMBOL = "XAUUSD"`, `MT5_TIMEFRAME_M15 = 15` /
`BAR_SECONDS_M15 = 900` (M15 -- the timeframe every `live_signal_source` test and prior report already
uses as this project's own working default; no other timeframe was specified). `POLL_INTERVAL_SECONDS =
30.0` -- frequent enough that a bar is picked up within 30s of closing, far below the 900s bar period, so
polling cadence never becomes the bottleneck for "at every closed bar."

**State**: one `SqliteStateStore` file, shared by the bar-feed watermark, the signal journal, and the
structural observation journal (Mandate 2's "one persistence solution" rule, extended the same way Step 3
already extended it to `StructuralObservationLog`). Default path is `live_observation_state/xauusd_m15.db`
at the repository root -- a new, gitignored, regenerable-by-rerun directory, matching this repo's own
established convention for non-source runtime data (`learning_feedback_data/`).
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway, RealMT5Gateway
from ai_trader.live_signal_source.bar_feed import LiveBarFeed, make_broker_offset
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.live_loop.loop import LiveSignalLoop
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.structural_observer.journal import StructuralObservationLog
from ai_trader.structural_observer.observer import StructuralObserver
from ai_trader.structural_observer.observing_rule import ObservingNullRecognitionRule

SYMBOL = "XAUUSD"
MT5_TIMEFRAME_M15 = 15
BAR_SECONDS_M15 = 15 * 60
POLL_INTERVAL_SECONDS = 30.0
DEFAULT_STATE_DIR = Path(__file__).resolve().parents[2] / "live_observation_state"
DEFAULT_DB_PATH = DEFAULT_STATE_DIR / "xauusd_m15.db"


def build_loop(
    gateway: MT5Gateway, state_store: SqliteStateStore, symbol: str = SYMBOL,
    mt5_timeframe: int = MT5_TIMEFRAME_M15, bar_seconds: int = BAR_SECONDS_M15,
    poll_interval_seconds: float = POLL_INTERVAL_SECONDS,
) -> LiveSignalLoop:
    """Pure composition -- no I/O beyond what `gateway`/`state_store` already do. Structural observation
    is wired through `ObservingNullRecognitionRule`, exactly Step 3's own wiring point: `evaluate()`
    forwards every bar to the `StructuralObserver`, then returns `None` unconditionally. No candidate is
    ever produced by this rule; the producer's own contract with a genuinely null rule is unchanged."""
    feed = LiveBarFeed(
        gateway, symbol, mt5_timeframe, bar_seconds, state_store=state_store,
        broker_offset=make_broker_offset(gateway, symbol),
    )
    signal_journal = LiveSignalJournal(state_store)
    structural_journal = StructuralObservationLog(state_store)
    observer = StructuralObserver(symbol, structural_journal)
    rule = ObservingNullRecognitionRule(observer)
    producer = CandidateSignalProducer(feed, rule, signal_journal)
    return LiveSignalLoop(producer, state_store, poll_interval_seconds)


def main() -> None:
    DEFAULT_STATE_DIR.mkdir(parents=True, exist_ok=True)

    gateway = RealMT5Gateway()
    if not gateway.initialize():
        raise SystemExit(f"live_observation: MT5 initialize() failed -- {gateway.last_error()!r}")

    state_store = SqliteStateStore(DEFAULT_DB_PATH)
    try:
        loop = build_loop(gateway, state_store)
        print(
            f"live_observation: starting -- symbol={SYMBOL} mt5_timeframe={MT5_TIMEFRAME_M15} "
            f"bar_seconds={BAR_SECONDS_M15} poll_interval_seconds={POLL_INTERVAL_SECONDS} "
            f"db={DEFAULT_DB_PATH}",
            flush=True,
        )
        loop.run_forever()
    finally:
        gateway.shutdown()


if __name__ == "__main__":
    main()
