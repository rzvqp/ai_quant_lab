"""`PdhPdlOrchestrator` -- the glue between `PdhPdlRecognitionRule`'s `LiveCandidate`/`PdhPdlTrigger`
and the EXISTING, already-proven `execution_orchestrator`/`mt5_demo_execution` pipeline
(`send_after_dry_run_gate`, Phase 10, BTCUSD-proven). Builds NO new order-construction logic: a
`CandidateSignal`'s own `stop`/`target` are automatically turned into a native SL/TP bracket by
`execution_engine.builder.py` (confirmed by reading it, not assumed) -- the broker then executes S1's
worst-case hierarchy itself, mechanically, with no monitoring loop of this package's own.

**Lifecycle, one position at a time** (Part A's own design -- one symbol, one signal at a time; PDH-PDL
does not specify concurrent trades, so this orchestrator refuses a new candidate while one is still
open, journaled as `ALREADY_IN_POSITION` rather than silently queuing or overwriting):

1. `submit_candidate` -- converts `LiveCandidate` 1:1 to `CandidateSignal` (confirmed field-identical,
   `live_signal_source/types.py`'s own docstring), runs it through `send_after_dry_run_gate` exactly as
   BTCUSD did. On a successful send, records a `PendingPdhPdlTrade` (client_order_id, requested vs.
   realized entry price from `OrderExecutionResult.avg_price`).
2. `observe_bar` -- called every closed bar while a position is pending: (a) detects a NEW day_index
   label and freezes `day_end_idx` the instant it does (the CEO's own confirmed rule -- the engine must
   never see a truncated day); (b) polls `positions_get()` (already on the read-only `MT5Gateway`
   Protocol) to detect a broker-side SL/TP close; (c) once `day_end_idx`'s bar has closed and the
   position is STILL open, submits ONE mechanical market CLOSE order -- the frozen policy's own third
   exit condition (CEO: "Nu e logica noua. E a treia conditie de iesire... Inchizi la granita de zi,
   atat. Nu adaugi conditii proprii, nu muti stopul, nu inchizi partial.").
3. `run_post_hoc_audit` -- called once the position is confirmed closed: reads the realized exit price
   via `history_deals_get` (already-proven `MT5HistoryGateway` capability, Mandate 3), computes realized
   cost (entry + exit slippage/spread vs. requested prices), then calls the FROZEN
   `pdh_pdl_demo_engine.simulate_demo_trade` EXACTLY ONCE with the complete day's bars -- its output is
   the authoritative audit record (CEO: "Motorul se cheama o data, dupa inchidere... Iesirea lui e
   inregistrare de audit, niciodata input de decizie live."). Never called before the position closes.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Protocol

from ai_trader.execution_orchestrator.types import (
    CandidateSignal,
    OrchestratorConfig,
    OrchestratorDependencies,
)
from ai_trader.live_signal_source.types import LiveCandidate
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.new_brain_bridge.authority import DecisionAuthority
from ai_trader.mt5_demo_execution.gating import GatedDemoOutcome, send_after_dry_run_gate
from ai_trader.mt5_demo_execution.types import SafetyGuardReport
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.recognition_rule import MAGIC_NUMBER, PdhPdlTrigger
from ai_trader.pdh_pdl_demo.slippage import SlippageLeg, SlippageLog, SlippageObservation
from ai_trader.pdh_pdl_demo.types import PdhPdlAuditEntry, PdhPdlAuditKind, PendingPdhPdlTrade
from ai_trader.pdh_pdl_demo.vendor_bridge import DemoSignal, DemoTradeResult, simulate_demo_trade

_NO_CONFIDENCE_CONFIG = OrchestratorConfig(recognition_pattern_id=None)
"""Matches EVERY existing `mt5_demo_execution` gating test's own config exactly -- Part A's trigger
lives entirely in `recognition_rule.py` (ratified primitives), not the generic feature-confidence path."""


class RealizedFillReader(Protocol):
    """Injected dependency -- reads the realized exit price for an already-closed position from MT5's
    own deal history (`history_deals_get`, already-proven, Mandate 3). Structurally typed, matching
    this codebase's own established injected-dependency convention."""

    def read_close_price(self, magic_number: int, symbol: str, since_ts: int) -> float | None: ...

    def is_position_open(self, magic_number: int, symbol: str) -> bool | None:
        """`None` = undeterminable (fail-closed by the caller, same convention as `SafetyGuardReport.market_open`)."""
        ...


@dataclass(frozen=True, slots=True)
class DemoDepsBundle:
    dry_run_deps: OrchestratorDependencies
    demo_deps: OrchestratorDependencies
    demo_adapter: MT5DemoBrokerAdapter
    safety_guard_report: SafetyGuardReport


DemoDepsFactory = Callable[[LiveCandidate, PdhPdlTrigger], DemoDepsBundle]


class PdhPdlOrchestrator:
    def __init__(
        self, symbol: str, tick_size: float, deps_factory: DemoDepsFactory,
        fill_reader: RealizedFillReader, audit_journal: PdhPdlAuditJournal,
        slippage_log: SlippageLog | None = None,
        authority_check: Callable[[], DecisionAuthority] | None = None,
    ) -> None:
        """`slippage_log=None` (the default) is byte-for-byte the pre-Mandate-8 behavior -- no existing
        caller or test needs to know about it. When given, `submit_candidate`/`_close_pending` additionally
        persist each leg's REALIZED slippage (see `slippage.py`'s own module docstring); nothing about the
        existing trading/audit behavior changes either way.

        `authority_check=None` (the default) is likewise byte-for-byte the pre-Mandate-2 behavior --
        `submit_candidate` proceeds exactly as it always has, unconditionally. Mandate 2, section 4 (CEO,
        2026-08-14): when given, `submit_candidate` calls it FRESH on every invocation (never cached) and,
        if it returns `DecisionAuthority.NEW_BRAIN`, records `LEGACY_SHADOW_TELEMETRY` and returns `None`
        WITHOUT ever calling `send_after_dry_run_gate` -- this orchestrator still recognizes and reports,
        but no longer produces the authoritative decision, calls Risk Manager, calls the Execution
        Adapter, or reaches the broker. No entrypoint passes a non-`None` value yet (CEO, 2026-08-14:
        "construieste codul, NU comuta inca") -- this parameter existing changes nothing about the 5 live
        processes' current behavior until an entrypoint is deliberately updated to pass one."""
        self._symbol = symbol
        self._tick_size = tick_size
        self._deps_factory = deps_factory
        self._fill_reader = fill_reader
        self._audit = audit_journal
        self._slippage_log = slippage_log
        self._authority_check = authority_check
        self._pending: PendingPdhPdlTrade | None = None

    @property
    def pending(self) -> PendingPdhPdlTrade | None:
        return self._pending

    def submit_candidate(
        self, candidate: LiveCandidate, trigger: PdhPdlTrigger, market_context: dict[str, Any],
    ) -> GatedDemoOutcome | None:
        if self._authority_check is not None and self._authority_check() is DecisionAuthority.NEW_BRAIN:
            self._audit.record(PdhPdlAuditEntry(
                symbol=self._symbol, as_of=candidate.as_of, kind=PdhPdlAuditKind.LEGACY_SHADOW_TELEMETRY,
                detail={"reason_code": "NEW_BRAIN_AUTHORITY_ACTIVE", "touch_idx": trigger.touch_idx},
            ))
            return None

        if self._pending is not None and not self._pending.closed:
            self._audit.record(PdhPdlAuditEntry(
                symbol=self._symbol, as_of=candidate.as_of, kind=PdhPdlAuditKind.NO_TRADE,
                detail={"reason_code": "ALREADY_IN_POSITION", "touch_idx": trigger.touch_idx},
            ))
            return None

        candidate_signal = CandidateSignal(
            strategy_id=candidate.strategy_id, symbol=candidate.symbol, direction=candidate.direction,
            entry=candidate.entry, stop=candidate.stop, target=candidate.target, session=candidate.session,
            magic_number=candidate.magic_number, comment=candidate.comment, as_of=candidate.as_of,
        )
        bundle = self._deps_factory(candidate, trigger)
        outcome = send_after_dry_run_gate(
            candidate_signal, market_context, bundle.dry_run_deps, bundle.demo_deps, bundle.demo_adapter,
            bundle.safety_guard_report, config=_NO_CONFIDENCE_CONFIG,
        )

        if not outcome.sent or outcome.demo_result is None or outcome.demo_result.order_result is None:
            self._audit.record(PdhPdlAuditEntry(
                symbol=self._symbol, as_of=candidate.as_of, kind=PdhPdlAuditKind.ENTRY_REJECTED,
                detail={"reason_codes": list(outcome.reason_codes), "touch_idx": trigger.touch_idx},
            ))
            return outcome

        order_result = outcome.demo_result.order_result
        self._pending = PendingPdhPdlTrade(
            symbol=self._symbol, direction=trigger.direction, touch_idx=trigger.touch_idx,
            entry_idx=trigger.entry_idx, strategy_stop_price=trigger.strategy_stop_price,
            target_price=trigger.target_price, atr_at_touch=trigger.atr_at_touch, day_end_idx=None,
            day_boundary_label=trigger.day_boundary_label, effective_spread=trigger.effective_spread,
            executable_stop_price=trigger.executable_stop_price, client_order_id=order_result.client_order_id,
            broker_order_id=None, entry_as_of=candidate.as_of, entry_requested_price=candidate.entry,
            entry_realized_price=order_result.avg_price,
        )
        self._audit.record(PdhPdlAuditEntry(
            symbol=self._symbol, as_of=candidate.as_of, kind=PdhPdlAuditKind.ENTRY_SUBMITTED,
            detail={
                "touch_idx": trigger.touch_idx, "direction": trigger.direction,
                "entry_requested_price": candidate.entry, "entry_realized_price": order_result.avg_price,
                "executable_stop_price": trigger.executable_stop_price, "target_price": trigger.target_price,
                "effective_spread": trigger.effective_spread, "client_order_id": order_result.client_order_id,
            },
        ))
        if self._slippage_log is not None and order_result.avg_price is not None:
            # `avg_price` is `None` until the broker ack reports a fill price (same fail-closed guard
            # `PendingPdhPdlTrade.entry_realized_price`'s own docstring already documents) -- nothing to
            # record yet if so, not a fabricated zero.
            self._slippage_log.record(SlippageObservation(
                symbol=self._symbol, magic_number=MAGIC_NUMBER, client_order_id=order_result.client_order_id,
                leg=SlippageLeg.ENTRY, as_of=candidate.as_of, direction=trigger.direction,
                requested_price=candidate.entry, realized_price=order_result.avg_price,
                signed_slippage=order_result.avg_price - candidate.entry, close_reason=None,
            ))
        return outcome

    def observe_bar(self, bar_idx: int, day_boundary_label: int, ts_close: int) -> DemoTradeResult | None:
        """Call once per closed bar while a position may be pending. Returns the post-hoc audit result
        the instant the position is confirmed closed (broker SL/TP or the mechanical day-end close) --
        `None` otherwise. The caller supplies the complete day's OHLC arrays separately, to
        `run_post_hoc_audit`, once this signals a close."""
        if self._pending is None or self._pending.closed:
            return None

        if day_boundary_label == self._pending.day_boundary_label:
            self._pending = replace(self._pending, day_end_idx=bar_idx)
            still_new_day = False
        else:
            still_new_day = True  # a NEW day started -- day_end_idx is now FROZEN at its last value

        is_open = self._fill_reader.is_position_open(MAGIC_NUMBER, self._symbol)
        if is_open is False:
            # Broker-side SL/TP already closed it -- detect the realized exit, mark closed, journal.
            self._close_pending("BROKER_SLTP", ts_close)
            return None

        if still_new_day and self._pending.day_end_idx is not None:
            # The entry day has genuinely ended (a bar from a DIFFERENT day has now closed) and the
            # position is STILL open -- the frozen policy's own third exit condition, executed
            # mechanically. No new criteria, no stop adjustment, no partial close (CEO's own constraint).
            self._close_pending("TIME_STOP", ts_close)
            return None
        return None

    def _close_pending(self, reason: str, ts_close: int) -> None:
        assert self._pending is not None
        pending = self._pending
        exit_price = self._fill_reader.read_close_price(MAGIC_NUMBER, self._symbol, pending.entry_as_of)
        self._pending = replace(pending, closed=True, close_realized_price=exit_price, close_reason=reason)
        self._audit.record(PdhPdlAuditEntry(
            symbol=self._symbol, as_of=ts_close, kind=PdhPdlAuditKind.POSITION_CLOSED,
            detail={
                "close_reason": reason, "close_realized_price": exit_price,
                "client_order_id": pending.client_order_id,
            },
        ))
        if self._slippage_log is not None and reason == "BROKER_SLTP" and exit_price is not None:
            # The ONE close reason with a genuine realized deal to read -- see `slippage.py`'s own
            # module docstring for why every other reason (TIME_STOP included) is deliberately skipped.
            reference = (
                pending.executable_stop_price
                if abs(exit_price - pending.executable_stop_price) < abs(exit_price - pending.target_price)
                else pending.target_price
            )
            self._slippage_log.record(SlippageObservation(
                symbol=self._symbol, magic_number=MAGIC_NUMBER, client_order_id=pending.client_order_id,
                leg=SlippageLeg.EXIT, as_of=ts_close, direction=pending.direction,
                requested_price=reference, realized_price=exit_price,
                signed_slippage=exit_price - reference, close_reason=reason,
            ))

    def run_post_hoc_audit(
        self, as_of: int, open_: list[float], high: list[float], low: list[float], close: list[float],
    ) -> DemoTradeResult | None:
        """Calls the FROZEN engine exactly once, with the COMPLETE day's bars, per the CEO's own
        confirmed design (Section 4: "Motorul se cheama o data, dupa inchidere"). Never called before
        `self._pending.closed` and `self._pending.day_end_idx` are both set -- returns `None` and
        journals a reason otherwise, rather than guessing. `as_of` is the CALLER's own current bar-close
        timestamp (the journal's own "decision timestamp, not recording timestamp" convention,
        Mandate 4) -- not derivable from the bare OHLC arrays."""
        if self._pending is None or not self._pending.closed or self._pending.day_end_idx is None:
            return None
        if len(close) <= self._pending.day_end_idx:
            self._audit.record(PdhPdlAuditEntry(
                symbol=self._symbol, as_of=as_of, kind=PdhPdlAuditKind.NO_TRADE,
                detail={"reason_code": "INCOMPLETE_DAY_ARRAY_AT_AUDIT_TIME"},
            ))
            return None

        realized_cost = self._compute_realized_cost()
        signal = DemoSignal(
            entry_idx=self._pending.entry_idx, direction=self._pending.direction,
            strategy_stop_price=self._pending.strategy_stop_price, target_price=self._pending.target_price,
            atr=self._pending.atr_at_touch, effective_spread=self._pending.effective_spread,
            cost=realized_cost, time_stop_idx=self._pending.day_end_idx,
        )
        result = simulate_demo_trade(signal, open_, high, low, close, self._tick_size)
        self._audit.record(PdhPdlAuditEntry(
            symbol=self._symbol, as_of=as_of, kind=PdhPdlAuditKind.AUDIT_RESULT,
            detail={
                "exit_reason": result.exit_reason, "net_R": result.net_R, "net_dollars": result.net_dollars,
                "intrabar_ordering": result.intrabar_ordering, "strategy_stop_distance": result.strategy_stop_distance,
                "min_executable_risk": result.min_executable_risk, "executable_stop_distance": result.executable_stop_distance,
                "floored": result.floored, "target_scan_start": result.target_scan_start,
                "target_scan_end": result.target_scan_end, "entry_price": result.entry_price,
                "exit_price": result.exit_price, "exit_idx": result.exit_idx,
                "realized_cost": realized_cost, "client_order_id": self._pending.client_order_id,
                "entry_requested_price": self._pending.entry_requested_price,
                "entry_realized_price": self._pending.entry_realized_price,
                "close_realized_price": self._pending.close_realized_price,
            },
        ))
        return result

    def _compute_realized_cost(self) -> float:
        """Round-trip realized cost: entry slippage (realized vs. requested) + exit slippage (realized
        exit vs. the STRATEGY's own stop/target reference, whichever the close reason implies) -- both
        REALIZED, never modeled (CEO: "din fill-urile REALIZATE, nu din valori modelate")."""
        assert self._pending is not None
        entry_slippage = 0.0
        if self._pending.entry_realized_price is not None:
            entry_slippage = abs(self._pending.entry_realized_price - self._pending.entry_requested_price)
        exit_slippage = 0.0
        if self._pending.close_realized_price is not None and self._pending.close_reason == "BROKER_SLTP":
            reference = (
                self._pending.executable_stop_price
                if self._pending.close_realized_price is not None
                and abs(self._pending.close_realized_price - self._pending.executable_stop_price)
                < abs(self._pending.close_realized_price - self._pending.target_price)
                else self._pending.target_price
            )
            exit_slippage = abs(self._pending.close_realized_price - reference)
        return entry_slippage + exit_slippage
