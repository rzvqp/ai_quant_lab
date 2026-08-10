"""`PdhPdlLiveLoop` / `main()` -- the real, continuous, unattended entrypoint for CAND-0001 PDH-PDL v2.0
DEMO trading (CEO instruction, 2026-08-03: "Porneste CAND-0001 PDH-PDL v2.0 pe cont DEMO.
Tranzactionare continua."). `compute_sizing` runs NORMALLY here (never bypassed) -- `LivePdhPdlDepsFactory`
feeds it real account/instrument/spread data every time a candidate is submitted.

**Why this is a dedicated loop, not `ai_trader.live_loop.LiveSignalLoop`**: `LiveSignalLoop.tick()` only
calls `producer.run_once()`, which does not expose the individual bars it processed to a caller -- but
this loop needs three additional per-bar hooks `CandidateSignalProducer` has no seam for: updating
`LiveRiskSnapshotBuilder`, calling `PdhPdlOrchestrator.observe_bar` (day-end tracking, broker-close
detection), and triggering the post-hoc audit once a position closes. So this loop drives
`LiveBarFeed.poll()` directly, evaluating each bar through `PdhPdlRecognitionRule` itself -- the SAME
circuit-breaker-consult-fresh-every-tick discipline `LiveSignalLoop` established (Mandate 4 Step 1) is
preserved here, unchanged.

**Disclosed, not solved**: this loop only audits the MOST RECENTLY closed trade (tracked by
`client_order_id`) -- since only one PDH-PDL position is ever open at a time (the orchestrator's own
"one position at a time" rule), this is sufficient, not an approximation of a harder problem.
"""

from __future__ import annotations

import signal
import time
from pathlib import Path
from typing import Callable

from ai_trader.live_signal_source.bar_feed import LiveBarFeed, make_broker_offset
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.types import LiveSignalJournalEntry
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.gateway import RealMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.mt5_pnl_source.gateway import RealMT5HistoryGateway
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.live_deps import LivePdhPdlDepsFactory
from ai_trader.pdh_pdl_demo.live_fill_reader import LiveMT5FillReader
from ai_trader.pdh_pdl_demo.live_tick_reader import LiveMT5TickReader
from ai_trader.pdh_pdl_demo.market_context import build_market_context
from ai_trader.pdh_pdl_demo.orchestration import PdhPdlOrchestrator
from ai_trader.pdh_pdl_demo.recognition_rule import PdhPdlRecognitionRule
from ai_trader.pdh_pdl_demo.risk_snapshot import LiveRiskSnapshotBuilder
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.circuit_breaker import load_persisted_circuit_state

SYMBOL = "XAUUSD"
MT5_TIMEFRAME_M15 = 15
BAR_SECONDS_M15 = 15 * 60
POLL_INTERVAL_SECONDS = 30.0
DEFAULT_STATE_DIR = Path(__file__).resolve().parents[2] / "pdh_pdl_live_state"
DEFAULT_DB_PATH = DEFAULT_STATE_DIR / "xauusd_m15.db"


def _default_sleep(seconds: float) -> None:
    time.sleep(seconds)


class PdhPdlLiveLoop:
    def __init__(
        self, feed: LiveBarFeed, rule: PdhPdlRecognitionRule, orchestrator: PdhPdlOrchestrator,
        signal_journal: LiveSignalJournal, risk_snapshot_builder: LiveRiskSnapshotBuilder,
        state_store: SqliteStateStore, poll_interval_seconds: float,
    ) -> None:
        self._feed = feed
        self._rule = rule
        self._orchestrator = orchestrator
        self._signal_journal = signal_journal
        self._risk_snapshot_builder = risk_snapshot_builder
        self._state_store = state_store
        self._poll_interval_seconds = poll_interval_seconds
        self._stop_requested = False
        self._last_audited_client_order_id: str | None = None

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested

    def stop(self) -> None:
        self._stop_requested = True

    def _handle_stop_signal(self, signum: int, frame: object) -> None:
        self.stop()

    def install_default_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, self._handle_stop_signal)
        signal.signal(signal.SIGTERM, self._handle_stop_signal)

    def tick(self) -> bool:
        circuit_state = load_persisted_circuit_state(self._state_store)
        if circuit_state.state is not EngineState.READY:
            return False

        bars = self._feed.poll()
        gaps_this_poll = self._feed.last_gaps()
        for bar in bars:
            candidate = self._rule.evaluate(bar)
            self._signal_journal.record(
                LiveSignalJournalEntry(symbol=bar.symbol, as_of=bar.ts_close, candidate=candidate)
            )
            self._risk_snapshot_builder.update(bar, gaps_this_poll=gaps_this_poll)

            if candidate is not None:
                trigger = self._rule.last_trigger()
                if trigger is not None:
                    market_context = build_market_context(bar.symbol, bar.ts_close, [bar])
                    self._orchestrator.submit_candidate(candidate, trigger, market_context)

            bar_idx = self._rule.current_bar_count - 1
            day_label = day_boundary_start_utc(bar.ts_open)
            self._orchestrator.observe_bar(bar_idx, day_label, bar.ts_close)

            pending = self._orchestrator.pending
            if (
                pending is not None and pending.closed
                and pending.client_order_id != self._last_audited_client_order_id
            ):
                open_, high, low, close = self._rule.current_arrays
                self._orchestrator.run_post_hoc_audit(bar.ts_close, open_, high, low, close)
                self._last_audited_client_order_id = pending.client_order_id

        for gap in gaps_this_poll:
            self._signal_journal.record_gap(gap)
        return True

    def run_forever(
        self, sleep: Callable[[float], None] = _default_sleep, install_signal_handlers: bool = True,
    ) -> None:
        if install_signal_handlers:
            self.install_default_signal_handlers()
        try:
            while not self._stop_requested:
                self.tick()
                sleep(self._poll_interval_seconds)
        finally:
            self._state_store.close()


def build_loop(
    order_gateway: RealMT5DemoGateway, history_gateway: RealMT5HistoryGateway,
    demo_adapter: MT5DemoBrokerAdapter, state_store: SqliteStateStore, state_dir: Path = DEFAULT_STATE_DIR,
) -> PdhPdlLiveLoop:
    feed = LiveBarFeed(
        order_gateway, SYMBOL, MT5_TIMEFRAME_M15, BAR_SECONDS_M15, state_store=state_store,
        broker_offset=make_broker_offset(order_gateway, SYMBOL),
    )
    signal_journal = LiveSignalJournal(state_store)
    audit_journal = PdhPdlAuditJournal(state_store)
    tick_reader = LiveMT5TickReader(order_gateway)

    raw_symbol_info = order_gateway.symbol_info(SYMBOL)
    tick_size = float(getattr(raw_symbol_info, "trade_tick_size", 0.01))
    rule = PdhPdlRecognitionRule(SYMBOL, tick_size, tick_reader, audit_journal)

    risk_snapshot_builder = LiveRiskSnapshotBuilder()
    # LivePdhPdlDepsFactory needs history_deals_get (MT5PortfolioStateSource's own realized-P&L read),
    # so it gets the history-capable gateway leg, not the order-capable one.
    deps_factory = LivePdhPdlDepsFactory(SYMBOL, history_gateway, demo_adapter, risk_snapshot_builder, state_dir)
    fill_reader = LiveMT5FillReader(history_gateway)
    orchestrator = PdhPdlOrchestrator(SYMBOL, tick_size, deps_factory, fill_reader, audit_journal)

    return PdhPdlLiveLoop(feed, rule, orchestrator, signal_journal, risk_snapshot_builder, state_store, POLL_INTERVAL_SECONDS)


def main() -> None:
    DEFAULT_STATE_DIR.mkdir(parents=True, exist_ok=True)

    # Two separate, already-approved gateway objects -- NOT one new combined class (pdh_pdl_demo's own
    # static test forbids this package from ever defining an order-capable gateway of its own; see
    # live_fill_reader.py's docstring). Both wrap the SAME underlying MetaTrader5 module-level connection
    # (RealMT5Gateway.__init__ only imports the module; initialize() is what actually connects, and MT5's
    # own initialize() is safe to call more than once against the same terminal).
    order_gateway = RealMT5DemoGateway()
    if not order_gateway.initialize():
        raise SystemExit(f"pdh_pdl_demo: MT5 initialize() failed -- {order_gateway.last_error()!r}")
    history_gateway = RealMT5HistoryGateway()
    if not history_gateway.initialize():
        order_gateway.shutdown()
        raise SystemExit(f"pdh_pdl_demo: MT5 initialize() failed (history leg) -- {history_gateway.last_error()!r}")

    demo_adapter = MT5DemoBrokerAdapter(gateway=order_gateway, config=MT5DemoConfig(expected_server="FusionMarkets-Demo"))
    connection = demo_adapter.connect()
    if not connection.accepted:
        order_gateway.shutdown()
        raise SystemExit(f"pdh_pdl_demo: demo_adapter.connect() refused -- {connection.reason}")

    state_store = SqliteStateStore(DEFAULT_DB_PATH)
    try:
        loop = build_loop(order_gateway, history_gateway, demo_adapter, state_store)
        print(
            f"pdh_pdl_demo: starting -- symbol={SYMBOL} mt5_timeframe={MT5_TIMEFRAME_M15} "
            f"bar_seconds={BAR_SECONDS_M15} poll_interval_seconds={POLL_INTERVAL_SECONDS} "
            f"db={DEFAULT_DB_PATH} -- CAND-0001 PDH-PDL v2.0, DEMO_BASELINE, compute_sizing NORMAL",
            flush=True,
        )
        loop.run_forever()
    finally:
        order_gateway.shutdown()  # shuts down the one, shared, process-wide MT5 terminal connection


if __name__ == "__main__":
    main()
