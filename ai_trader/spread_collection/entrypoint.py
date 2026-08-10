"""`build_loop`/`main()` -- the continuous, unattended entrypoint for spread collection (CEO instruction,
2026-08-04: "Construieste colectarea de spread... In paralel cu observarea live. Fara ordine, fara cost").

Same composition pattern `live_observation/entrypoint.py` already established: a read-only `RealMT5Gateway`
(no order capability at all -- this package never bridges `demo_gate_engine`, never sends anything),
`LiveBarFeed`, and the EXISTING, already-tested `CandidateSignalProducer`/`LiveSignalLoop` generic infra,
wired through `SpreadCollectingNullRecognitionRule` exactly the way `ObservingNullRecognitionRule` wires
`StructuralObserver` -- no new loop was written, this package needs no per-bar hook beyond
`RecognitionRule.evaluate()` already provides.

**A separate process, a separate state file** (`spread_collection_state/xauusd_m15.db`) -- NOT
`live_observation_state/xauusd_m15.db`. Two independent `LiveBarFeed` instances on the SAME
`(symbol, mt5_timeframe)` pair pointed at the SAME state file would collide on the bar-feed watermark
key (documented, established risk -- see `pdh_pdl_demo`/`multi_policy_live`'s own state-separation
docstrings); a dedicated file avoids this entirely, at the cost of one more MT5 terminal connection
(already proven safe -- three others already run this way: live_observation, CAND-0001, and the
multi-policy process)."""

from __future__ import annotations

from pathlib import Path

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway, RealMT5Gateway
from ai_trader.live_signal_source.bar_feed import LiveBarFeed, make_broker_clock
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.live_loop.loop import LiveSignalLoop
from ai_trader.pdh_pdl_demo.live_tick_reader import LiveMT5TickReader
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.spread_collection.journal import SpreadObservationLog
from ai_trader.spread_collection.observer import SpreadCollector
from ai_trader.spread_collection.observing_rule import SpreadCollectingNullRecognitionRule

SYMBOL = "XAUUSD"
MT5_TIMEFRAME_M15 = 15
BAR_SECONDS_M15 = 15 * 60
POLL_INTERVAL_SECONDS = 30.0
DEFAULT_STATE_DIR = Path(__file__).resolve().parents[2] / "spread_collection_state"
DEFAULT_DB_PATH = DEFAULT_STATE_DIR / "xauusd_m15.db"


def build_loop(
    gateway: MT5Gateway, state_store: SqliteStateStore, symbol: str = SYMBOL,
    mt5_timeframe: int = MT5_TIMEFRAME_M15, bar_seconds: int = BAR_SECONDS_M15,
    poll_interval_seconds: float = POLL_INTERVAL_SECONDS,
) -> LiveSignalLoop:
    feed = LiveBarFeed(
        gateway, symbol, mt5_timeframe, bar_seconds, state_store=state_store,
        clock=make_broker_clock(gateway, symbol),
    )
    signal_journal = LiveSignalJournal(state_store)
    spread_journal = SpreadObservationLog(state_store)
    tick_reader = LiveMT5TickReader(gateway)
    collector = SpreadCollector(symbol, tick_reader, spread_journal)
    rule = SpreadCollectingNullRecognitionRule(collector)
    producer = CandidateSignalProducer(feed, rule, signal_journal)
    return LiveSignalLoop(producer, state_store, poll_interval_seconds)


def main() -> None:
    DEFAULT_STATE_DIR.mkdir(parents=True, exist_ok=True)

    gateway = RealMT5Gateway()
    if not gateway.initialize():
        raise SystemExit(f"spread_collection: MT5 initialize() failed -- {gateway.last_error()!r}")

    state_store = SqliteStateStore(DEFAULT_DB_PATH)
    try:
        loop = build_loop(gateway, state_store)
        print(
            f"spread_collection: starting -- symbol={SYMBOL} mt5_timeframe={MT5_TIMEFRAME_M15} "
            f"bar_seconds={BAR_SECONDS_M15} poll_interval_seconds={POLL_INTERVAL_SECONDS} "
            f"db={DEFAULT_DB_PATH} -- no orders, no cost, observation only",
            flush=True,
        )
        loop.run_forever()
    finally:
        gateway.shutdown()


if __name__ == "__main__":
    main()
