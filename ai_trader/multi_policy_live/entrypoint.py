"""`MultiPolicyLiveLoop` / `main()` -- the continuous, unattended entrypoint for CAND-0007 and CAND-0019
(CEO instruction, 2026-08-04: "Construieste cablarea pentru politici multiple... CAND-0001 PDH-PDL...
CAND-0007... CAND-0019... CAND-0009 ramane INACTIV"). CAND-0001 is NOT part of this loop -- it keeps
running as its own separate, already-live process (PID confirmed at build time), untouched.

**Design** (`MULTI_POLICY_LIVE_DESIGN.md`, 9f6f08d): one process, one shared `LiveBarFeed` (all three
policies here watch the same XAUUSD M15 bars -- a second feed on the same `(symbol, mt5_timeframe)`
would collide on the bar-feed watermark key), four independent recognition-rule/orchestrator instances
(CAND-0001's own pair lives entirely in its own process; this loop owns CAND-0007/CAND-0009/CAND-0019's),
per-policy try/except isolation with auto-degrade, a persisted per-policy pause flag
(`policy_control.PolicyControl`), and per-policy audit/journal isolation (each policy gets its OWN
`PdhPdlAuditJournal` pointed at its OWN state file).

**Risk (CEO decision, 2026-08-04, option D): nothing shared, nothing capped.** Each policy gets its OWN
`LivePdhPdlDepsFactory` instance, each sizing independently at `RiskConfig()`'s own 0.5%-per-trade
default -- no cross-policy risk pool, no new gate. A day where all active policies signal costs up to
N x 0.5%; the CEO's own explicit reasoning: DEMO measures behavior, not capital protection, and
`risk_manager/limits.py`'s already-built portfolio caps activate when this moves to a real account.

**Circuit breaker stays account-wide** (design doc section 4): read fresh every tick from CAND-0001's
OWN state file (`pdh_pdl_live_state/xauusd_m15.db`), not a separate one for this process -- one
EMERGENCY_STOP/SUSPENDED halts every policy, including these three, exactly as the design specified.

**Exclusion** (CEO decision, 2026-08-04): only CAND-0009 is checked against CAND-0001's own journal
before every submission (see `exclusion.py`'s own disclosed limitation -- CAND-0009 stays inactive here
regardless, so this path is wired but not yet exercised by a live signal)."""

from __future__ import annotations

import signal
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.types import Bar, LiveCandidate, LiveSignalJournalEntry
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.gateway import RealMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.mt5_pnl_source.gateway import RealMT5HistoryGateway
from ai_trader.multi_policy_live.exclusion import LevelDayExclusion
from ai_trader.multi_policy_live.orchestration import PolicyOrchestrator, day_boundary_mechanical_close
from ai_trader.multi_policy_live.policy_control import PolicyControl
from ai_trader.multi_policy_live.recognition_dz_level_confluence import DzLevelConfluenceRecognitionRule
from ai_trader.multi_policy_live.recognition_level_break_drive import (
    LevelBreakDriveRecognitionRule,
    opposing_expansion_or_time_stop_close,
    sentinel_target_price,
)
from ai_trader.multi_policy_live.recognition_level_fvg_confluence import LevelFvgConfluenceRecognitionRule
from ai_trader.multi_policy_live.vendor_bridge import LevelKind
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.live_deps import LivePdhPdlDepsFactory
from ai_trader.pdh_pdl_demo.live_fill_reader import LiveMT5FillReader
from ai_trader.pdh_pdl_demo.live_tick_reader import LiveMT5TickReader
from ai_trader.pdh_pdl_demo.market_context import build_market_context
from ai_trader.pdh_pdl_demo.recognition_rule import PdhPdlTrigger
from ai_trader.pdh_pdl_demo.risk_snapshot import LiveRiskSnapshotBuilder
from ai_trader.pdh_pdl_demo.types import PdhPdlAuditEntry, PdhPdlAuditKind, PendingPdhPdlTrade
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.circuit_breaker import load_persisted_circuit_state

SYMBOL = "XAUUSD"
MT5_TIMEFRAME_M15 = 15
BAR_SECONDS_M15 = 15 * 60
POLL_INTERVAL_SECONDS = 30.0

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_DIR = _REPO_ROOT / "multi_policy_live_state"
DEFAULT_SHARED_DB_PATH = DEFAULT_STATE_DIR / "shared_xauusd_m15.db"
CAND0001_DB_PATH = _REPO_ROOT / "pdh_pdl_live_state" / "xauusd_m15.db"
"""CAND-0001's OWN state file -- read-only from this process, for the shared circuit breaker AND the
CAND-0009 exclusion check. Never written to from here."""


class RecognitionRule(Protocol):
    """The shared shape every recognition rule in this package (and `pdh_pdl_demo`'s own) implements --
    used only for typing this loop's policy registry, not a runtime base class."""

    def evaluate(self, bar: Bar) -> LiveCandidate | None: ...
    def last_trigger(self) -> PdhPdlTrigger | None: ...
    def last_touch_level_kind(self) -> LevelKind | None: ...

    @property
    def current_bar_count(self) -> int: ...

    @property
    def current_arrays(self) -> tuple[list[float], list[float], list[float], list[float]]: ...


class OrchestratorLike(Protocol):
    """The shape `PolicyOrchestrator` implements -- a Protocol (not the concrete class) so tests can
    inject a fake without needing to subclass or `type: ignore` past a nominal-type mismatch, matching
    this package's own `RecognitionRule` Protocol above."""

    @property
    def pending(self) -> PendingPdhPdlTrade | None: ...

    def submit_candidate(self, candidate: LiveCandidate, trigger: PdhPdlTrigger, market_context: dict[str, object]) -> object: ...

    def observe_bar(
        self, bar_idx: int, day_boundary_label: int, ts_close: int,
        arrays: tuple[list[float], list[float], list[float], list[float]] | None = None,
    ) -> object: ...

    def run_post_hoc_audit(
        self, as_of: int, open_: list[float], high: list[float], low: list[float], close: list[float],
    ) -> object: ...


@dataclass
class PolicyRuntime:
    policy_id: str
    rule: RecognitionRule
    orchestrator: OrchestratorLike
    audit_journal: PdhPdlAuditJournal
    check_exclusion_against_cand0001: bool = False
    last_audited_client_order_id: str | None = None


def _default_sleep(seconds: float) -> None:
    time.sleep(seconds)


class MultiPolicyLiveLoop:
    def __init__(
        self, feed: LiveBarFeed, policies: list[PolicyRuntime], signal_journal: LiveSignalJournal,
        risk_snapshot_builder: LiveRiskSnapshotBuilder, state_store: SqliteStateStore,
        policy_control: PolicyControl, exclusion: LevelDayExclusion, circuit_state_store_path: Path,
        poll_interval_seconds: float,
    ) -> None:
        self._feed = feed
        self._policies = policies
        self._signal_journal = signal_journal
        self._risk_snapshot_builder = risk_snapshot_builder
        self._state_store = state_store
        self._policy_control = policy_control
        self._exclusion = exclusion
        self._circuit_state_store_path = circuit_state_store_path
        self._poll_interval_seconds = poll_interval_seconds
        self._stop_requested = False
        self._degraded: set[str] = set()

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested

    @property
    def degraded_policy_ids(self) -> frozenset[str]:
        return frozenset(self._degraded)

    def stop(self) -> None:
        self._stop_requested = True

    def _handle_stop_signal(self, signum: int, frame: object) -> None:
        self.stop()

    def install_default_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, self._handle_stop_signal)
        signal.signal(signal.SIGTERM, self._handle_stop_signal)

    def _read_shared_circuit_ready(self) -> bool:
        """Reads CAND-0001's OWN circuit-breaker state, fresh, from its own state file -- a SEPARATE,
        short-lived `SqliteStateStore` connection, opened and closed within this one check, never held
        open (matching `exclusion.py`'s own cross-process read discipline)."""
        store = SqliteStateStore(self._circuit_state_store_path)
        try:
            circuit_state = load_persisted_circuit_state(store)
            return circuit_state.state is EngineState.READY
        finally:
            store.close()

    def _degrade(self, policy: PolicyRuntime, stage: str, exc: Exception, as_of: int) -> None:
        self._degraded.add(policy.policy_id)
        policy.audit_journal.record(PdhPdlAuditEntry(
            symbol=SYMBOL, as_of=as_of, kind=PdhPdlAuditKind.NO_TRADE,
            detail={
                "reason_code": f"POLICY_ERROR_{stage}", "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            },
        ))

    def tick(self) -> bool:
        if not self._read_shared_circuit_ready():
            return False

        bars = self._feed.poll()
        gaps_this_poll = self._feed.last_gaps()
        for bar in bars:
            self._risk_snapshot_builder.update(bar, gaps_this_poll=gaps_this_poll)
            self._process_bar(bar)

        for gap in gaps_this_poll:
            self._signal_journal.record_gap(gap)
        return True

    def _process_bar(self, bar: Bar) -> None:
        pending_candidates: list[tuple[PolicyRuntime, LiveCandidate, PdhPdlTrigger, LevelKind | None]] = []

        for policy in self._policies:
            if policy.policy_id in self._degraded:
                continue
            try:
                candidate = policy.rule.evaluate(bar)
            except Exception as exc:  # noqa: BLE001 -- deliberate: one policy's bug must not stop the others
                self._degrade(policy, "EVALUATE", exc, bar.ts_close)
                continue
            self._signal_journal.record(
                LiveSignalJournalEntry(symbol=bar.symbol, as_of=bar.ts_close, candidate=candidate)
            )
            if candidate is None or not self._policy_control.is_enabled(policy.policy_id):
                continue
            trigger = policy.rule.last_trigger()
            if trigger is None:
                continue
            level_kind = policy.rule.last_touch_level_kind()
            pending_candidates.append((policy, candidate, trigger, level_kind))

        for policy, candidate, trigger, level_kind in pending_candidates:
            if policy.policy_id in self._degraded:
                continue
            try:
                if policy.check_exclusion_against_cand0001 and level_kind is not None:
                    if self._exclusion.cand0001_already_entered_today(level_kind, trigger.day_boundary_label):
                        policy.audit_journal.record(PdhPdlAuditEntry(
                            symbol=SYMBOL, as_of=candidate.as_of, kind=PdhPdlAuditKind.NO_TRADE,
                            detail={
                                "reason_code": "EXCLUSION_LEVEL_CONFLICT_WITH_CAND0001",
                                "level_kind": level_kind.value, "touch_idx": trigger.touch_idx,
                            },
                        ))
                        continue
                market_context = build_market_context(bar.symbol, bar.ts_close, [bar])
                policy.orchestrator.submit_candidate(candidate, trigger, market_context)
            except Exception as exc:  # noqa: BLE001
                self._degrade(policy, "SUBMIT", exc, bar.ts_close)

        for policy in self._policies:
            if policy.policy_id in self._degraded:
                continue
            try:
                bar_idx = policy.rule.current_bar_count - 1
                day_label = day_boundary_start_utc(bar.ts_open)
                arrays = policy.rule.current_arrays
                policy.orchestrator.observe_bar(bar_idx, day_label, bar.ts_close, arrays)

                pending = policy.orchestrator.pending
                if (
                    pending is not None and pending.closed
                    and pending.client_order_id != policy.last_audited_client_order_id
                ):
                    policy.orchestrator.run_post_hoc_audit(bar.ts_close, *arrays)
                    policy.last_audited_client_order_id = pending.client_order_id
            except Exception as exc:  # noqa: BLE001
                self._degrade(policy, "OBSERVE", exc, bar.ts_close)

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
    demo_adapter: MT5DemoBrokerAdapter, shared_state_store: SqliteStateStore,
    state_dir: Path = DEFAULT_STATE_DIR, cand0001_db_path: Path = CAND0001_DB_PATH,
) -> MultiPolicyLiveLoop:
    feed = LiveBarFeed(order_gateway, SYMBOL, MT5_TIMEFRAME_M15, BAR_SECONDS_M15, state_store=shared_state_store)
    signal_journal = LiveSignalJournal(shared_state_store)
    risk_snapshot_builder = LiveRiskSnapshotBuilder()
    tick_reader = LiveMT5TickReader(order_gateway)
    fill_reader = LiveMT5FillReader(history_gateway)
    policy_control = PolicyControl(shared_state_store)
    exclusion = LevelDayExclusion(cand0001_db_path)

    raw_symbol_info = order_gateway.symbol_info(SYMBOL)
    tick_size = float(getattr(raw_symbol_info, "trade_tick_size", 0.01))

    def _policy_state_dir(policy_id: str) -> Path:
        d = state_dir / policy_id.lower().replace("-", "_")
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _audit_journal(policy_id: str) -> PdhPdlAuditJournal:
        d = _policy_state_dir(policy_id)
        store = SqliteStateStore(d / "audit.db")
        return PdhPdlAuditJournal(store, log_name=f"multi_policy_live.{policy_id.lower()}.audit")

    # CAND-0007 -- Level x FVG Confluence, day-boundary exit (default mechanical_close), no exclusion.
    cand0007_audit = _audit_journal("CAND-0007")
    cand0007_rule = LevelFvgConfluenceRecognitionRule(SYMBOL, tick_size, tick_reader, cand0007_audit)
    cand0007_deps = LivePdhPdlDepsFactory(
        SYMBOL, history_gateway, demo_adapter, risk_snapshot_builder, _policy_state_dir("CAND-0007"),
    )
    cand0007_orch = PolicyOrchestrator(
        SYMBOL, tick_size, 100_002, cand0007_deps, fill_reader, cand0007_audit,
    )

    # CAND-0019 -- DZ x Level Confluence, day-boundary exit, no exclusion.
    cand0019_audit = _audit_journal("CAND-0019")
    cand0019_rule = DzLevelConfluenceRecognitionRule(SYMBOL, tick_size, tick_reader, cand0019_audit)
    cand0019_deps = LivePdhPdlDepsFactory(
        SYMBOL, history_gateway, demo_adapter, risk_snapshot_builder, _policy_state_dir("CAND-0019"),
    )
    cand0019_orch = PolicyOrchestrator(
        SYMBOL, tick_size, 100_004, cand0019_deps, fill_reader, cand0019_audit,
    )

    # CAND-0009 -- Level-Break-Drive, its OWN mechanical close + sentinel-target audit hook, excluded
    # against CAND-0001. Wired fully; NOT enabled (PolicyControl.is_enabled defaults False).
    cand0009_audit = _audit_journal("CAND-0009")
    cand0009_rule = LevelBreakDriveRecognitionRule(SYMBOL, tick_size, tick_reader, cand0009_audit)
    cand0009_deps = LivePdhPdlDepsFactory(
        SYMBOL, history_gateway, demo_adapter, risk_snapshot_builder, _policy_state_dir("CAND-0009"),
    )
    cand0009_orch = PolicyOrchestrator(
        SYMBOL, tick_size, 100_003, cand0009_deps, fill_reader, cand0009_audit,
        mechanical_close=opposing_expansion_or_time_stop_close, target_price_for_audit=sentinel_target_price,
    )

    policies = [
        PolicyRuntime("CAND-0007", cand0007_rule, cand0007_orch, cand0007_audit, check_exclusion_against_cand0001=False),
        PolicyRuntime("CAND-0019", cand0019_rule, cand0019_orch, cand0019_audit, check_exclusion_against_cand0001=False),
        PolicyRuntime("CAND-0009", cand0009_rule, cand0009_orch, cand0009_audit, check_exclusion_against_cand0001=True),
    ]

    return MultiPolicyLiveLoop(
        feed, policies, signal_journal, risk_snapshot_builder, shared_state_store, policy_control,
        exclusion, cand0001_db_path, POLL_INTERVAL_SECONDS,
    )


def main() -> None:
    DEFAULT_STATE_DIR.mkdir(parents=True, exist_ok=True)

    order_gateway = RealMT5DemoGateway()
    if not order_gateway.initialize():
        raise SystemExit(f"multi_policy_live: MT5 initialize() failed -- {order_gateway.last_error()!r}")
    history_gateway = RealMT5HistoryGateway()
    if not history_gateway.initialize():
        order_gateway.shutdown()
        raise SystemExit(f"multi_policy_live: MT5 initialize() failed (history leg) -- {history_gateway.last_error()!r}")

    demo_adapter = MT5DemoBrokerAdapter(gateway=order_gateway, config=MT5DemoConfig(expected_server="FusionMarkets-Demo"))
    connection = demo_adapter.connect()
    if not connection.accepted:
        order_gateway.shutdown()
        raise SystemExit(f"multi_policy_live: demo_adapter.connect() refused -- {connection.reason}")

    shared_state_store = SqliteStateStore(DEFAULT_SHARED_DB_PATH)
    try:
        loop = build_loop(order_gateway, history_gateway, demo_adapter, shared_state_store)
        print(
            f"multi_policy_live: starting -- symbol={SYMBOL} mt5_timeframe={MT5_TIMEFRAME_M15} "
            f"bar_seconds={BAR_SECONDS_M15} poll_interval_seconds={POLL_INTERVAL_SECONDS} "
            f"policies=CAND-0007,CAND-0019(active) CAND-0009(built,inactive) -- DEMO_BASELINE",
            flush=True,
        )
        loop.run_forever()
    finally:
        order_gateway.shutdown()


if __name__ == "__main__":
    main()
