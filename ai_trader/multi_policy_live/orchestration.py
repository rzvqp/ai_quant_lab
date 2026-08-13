"""`PolicyOrchestrator` -- the SAME glue `pdh_pdl_demo.orchestration.PdhPdlOrchestrator` implements for
CAND-0001, generalized so CAND-0007/CAND-0009/CAND-0019 can each get their OWN independent instance
without duplicating the orchestration logic three more times (CEO instruction, 2026-08-04: "un proces...
patru recognition rules cu orchestratori independenti" -- independent INSTANCES/STATE, not independent
IMPLEMENTATIONS).

**Why a new class instead of reusing `PdhPdlOrchestrator` directly**: that class imports `MAGIC_NUMBER`
at module level from `pdh_pdl_demo.recognition_rule` (CAND-0001's own fixed constant) and calls
`self._fill_reader.is_position_open(MAGIC_NUMBER, ...)` with it baked in -- a real, CAND-0001-specific
coupling, not a policy-behavior difference. Copying the ~150 lines of genuinely-shared logic (submit ->
observe -> post-hoc-audit lifecycle, day-end mechanical closer, realized-cost computation) into a SECOND
near-identical class would be actual duplication; this class takes `magic_number` as a constructor
parameter instead, and is otherwise IDENTICAL in behavior. `pdh_pdl_demo/orchestration.py` itself is left
completely untouched (it is already live, running as CAND-0001's own process, PID 29888 at the time this
was written) -- no risk to it, no git-stash proof needed for a file this change never touches.

Types (`PdhPdlTrigger`, `PendingPdhPdlTrade`, `PdhPdlAuditEntry`, `PdhPdlAuditKind`) and the
`RealizedFillReader`/`DemoDepsBundle`/`DemoDepsFactory` shapes are reused VERBATIM by import from
`pdh_pdl_demo` -- all already fully generic in their own field names (nothing PDH/PDL-specific), pure
data/Protocol definitions, not behavior; importing them is not a modification of that package.
`send_after_dry_run_gate` and the frozen `simulate_demo_trade`/`DemoSignal` are the SAME single import
every policy's orchestrator calls -- the one true "motorul comun, nu duplicat" instance.

**Pluggable mechanical-close strategy, added for CAND-0009**: CAND-0001/CAND-0007/CAND-0019 all share the
SAME third exit condition (day-boundary time-stop -- their target is a level anchoring a bounded daily
range). CAND-0009 (`POLICY_LEVEL_BREAK_DRIVE_v3.md`) is a break-and-CONTINUATION trade, not bounded by
the day: its own live-valid exit is "first opposing-direction expansion bar OR a 14-bar (`ATR_WINDOW`)
time-stop counted from entry" -- a genuinely different mechanical condition, not a parameter difference.
Rather than duplicate the whole submit/observe/audit lifecycle for one different exit rule, `observe_bar`
takes an injected `MechanicalCloseCheck` callable (defaulting to the day-boundary check, reproducing
CAND-0001/0007/0019's exact existing behavior byte-for-byte) -- CAND-0009's own orchestrator instance is
built with a DIFFERENT callable instead. Still one class, one shared submit/audit implementation."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from ai_trader.execution_orchestrator.types import CandidateSignal, OrchestratorConfig
from ai_trader.live_signal_source.types import LiveCandidate
from ai_trader.mt5_demo_execution.gating import GatedDemoOutcome, send_after_dry_run_gate
from ai_trader.multi_policy_live.vendor_bridge import DemoSignal, DemoTradeResult, simulate_demo_trade
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.orchestration import DemoDepsBundle, DemoDepsFactory, RealizedFillReader
from ai_trader.pdh_pdl_demo.recognition_rule import PdhPdlTrigger
from ai_trader.pdh_pdl_demo.slippage import SlippageLeg, SlippageLog, SlippageObservation
from ai_trader.pdh_pdl_demo.types import PdhPdlAuditEntry, PdhPdlAuditKind, PendingPdhPdlTrade

_NO_CONFIDENCE_CONFIG = OrchestratorConfig(recognition_pattern_id=None)
"""Matches EVERY existing gating test's own config exactly -- identical to `pdh_pdl_demo.orchestration`'s
own module-level constant of the same name (independent copy, not an import, so this file never depends
on `pdh_pdl_demo.orchestration`'s internals, only its public types)."""

BarArrays = tuple[list[float], list[float], list[float], list[float]]
"""`(open, high, low, close)` -- the same shape `recognition_rule.current_arrays` exposes on every
recognition rule in this package."""

MechanicalCloseCheck = Callable[[PendingPdhPdlTrade, int, int, BarArrays | None], str | None]
"""`(pending, bar_idx, day_boundary_label, arrays) -> close_reason | None`. Called every `observe_bar`
while a position is open and not yet broker-closed. Returning a non-`None` string closes the position
mechanically with that reason."""


def day_boundary_mechanical_close(
    pending: PendingPdhPdlTrade, bar_idx: int, day_boundary_label: int, arrays: BarArrays | None,
) -> str | None:
    """The exact day-boundary check `pdh_pdl_demo.orchestration.PdhPdlOrchestrator.observe_bar` already
    implements inline for CAND-0001 -- reproduced here as the DEFAULT strategy so CAND-0007/CAND-0019
    (both day-anchored, per their own Part B) get byte-identical behavior. `bar_idx`/`day_boundary_label`
    here already reflect the CALLER's own day-tracking update (see `PolicyOrchestrator.observe_bar`)."""
    if day_boundary_label != pending.day_boundary_label and pending.day_end_idx is not None:
        return "TIME_STOP"
    return None


class PolicyOrchestrator:
    """One instance per policy (CAND-0007/CAND-0009/CAND-0019), each with its OWN `magic_number`,
    `deps_factory`, `fill_reader`, `audit_journal` -- fully independent state, zero cross-policy
    coupling, matching `pdh_pdl_demo.orchestration.PdhPdlOrchestrator`'s exact lifecycle."""

    def __init__(
        self, symbol: str, tick_size: float, magic_number: int, deps_factory: DemoDepsFactory,
        fill_reader: RealizedFillReader, audit_journal: PdhPdlAuditJournal,
        mechanical_close: MechanicalCloseCheck = day_boundary_mechanical_close,
        target_price_for_audit: Callable[[PendingPdhPdlTrade, BarArrays], float] | None = None,
        slippage_log: SlippageLog | None = None,
    ) -> None:
        """`target_price_for_audit`, if given, OVERRIDES `pending.target_price` when building the
        post-hoc `DemoSignal` -- for a policy with no real price target (CAND-0009), this supplies a
        disclosed sentinel instead (see `recognition_level_break_drive.py`'s own module docstring).
        `None` (the default) uses `pending.target_price` as-is, matching every day-anchored policy.

        `slippage_log=None` (the default) is byte-for-byte the pre-Mandate-8 behavior -- see
        `pdh_pdl_demo.orchestration.PdhPdlOrchestrator`'s own identical parameter for the full rationale;
        this class's `submit_candidate`/`_close_pending` mirror that wiring exactly."""
        self._symbol = symbol
        self._tick_size = tick_size
        self._magic_number = magic_number
        self._deps_factory = deps_factory
        self._fill_reader = fill_reader
        self._audit = audit_journal
        self._mechanical_close = mechanical_close
        self._target_price_for_audit = target_price_for_audit
        self._slippage_log = slippage_log
        self._pending: PendingPdhPdlTrade | None = None

    @property
    def magic_number(self) -> int:
        return self._magic_number

    @property
    def pending(self) -> PendingPdhPdlTrade | None:
        return self._pending

    def submit_candidate(
        self, candidate: LiveCandidate, trigger: PdhPdlTrigger, market_context: dict[str, Any],
    ) -> GatedDemoOutcome | None:
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
            # `avg_price` is `None` until the broker ack reports a fill price -- nothing to record yet
            # if so, not a fabricated zero. Mirrors `pdh_pdl_demo.orchestration.PdhPdlOrchestrator`'s
            # own identical guard.
            self._slippage_log.record(SlippageObservation(
                symbol=self._symbol, magic_number=self._magic_number, client_order_id=order_result.client_order_id,
                leg=SlippageLeg.ENTRY, as_of=candidate.as_of, direction=trigger.direction,
                requested_price=candidate.entry, realized_price=order_result.avg_price,
                signed_slippage=order_result.avg_price - candidate.entry, close_reason=None,
            ))
        return outcome

    def observe_bar(
        self, bar_idx: int, day_boundary_label: int, ts_close: int, arrays: BarArrays | None = None,
    ) -> DemoTradeResult | None:
        """`arrays` is optional and unused by the default (day-boundary) mechanical-close strategy --
        only a policy whose OWN strategy needs bar-level OHLC (CAND-0009's opposing-expansion check)
        requires the caller to pass it."""
        if self._pending is None or self._pending.closed:
            return None

        if day_boundary_label == self._pending.day_boundary_label:
            self._pending = replace(self._pending, day_end_idx=bar_idx)

        is_open = self._fill_reader.is_position_open(self._magic_number, self._symbol)
        if is_open is False:
            self._close_pending("BROKER_SLTP", ts_close)
            return None

        close_reason = self._mechanical_close(self._pending, bar_idx, day_boundary_label, arrays)
        if close_reason is not None:
            self._close_pending(close_reason, ts_close)
            return None
        return None

    def _close_pending(self, reason: str, ts_close: int) -> None:
        assert self._pending is not None
        pending = self._pending
        exit_price = self._fill_reader.read_close_price(self._magic_number, self._symbol, pending.entry_as_of)
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
            # module docstring for why every other reason is deliberately skipped.
            reference = (
                pending.executable_stop_price
                if abs(exit_price - pending.executable_stop_price) < abs(exit_price - pending.target_price)
                else pending.target_price
            )
            self._slippage_log.record(SlippageObservation(
                symbol=self._symbol, magic_number=self._magic_number, client_order_id=pending.client_order_id,
                leg=SlippageLeg.EXIT, as_of=ts_close, direction=pending.direction,
                requested_price=reference, realized_price=exit_price,
                signed_slippage=exit_price - reference, close_reason=reason,
            ))

    def run_post_hoc_audit(
        self, as_of: int, open_: list[float], high: list[float], low: list[float], close: list[float],
    ) -> DemoTradeResult | None:
        if self._pending is None or not self._pending.closed or self._pending.day_end_idx is None:
            return None
        if len(close) <= self._pending.day_end_idx:
            self._audit.record(PdhPdlAuditEntry(
                symbol=self._symbol, as_of=as_of, kind=PdhPdlAuditKind.NO_TRADE,
                detail={"reason_code": "INCOMPLETE_DAY_ARRAY_AT_AUDIT_TIME"},
            ))
            return None

        realized_cost = self._compute_realized_cost()
        target_price = self._pending.target_price
        is_sentinel_target = False
        if self._target_price_for_audit is not None:
            target_price = self._target_price_for_audit(self._pending, (open_, high, low, close))
            is_sentinel_target = True
        signal = DemoSignal(
            entry_idx=self._pending.entry_idx, direction=self._pending.direction,
            strategy_stop_price=self._pending.strategy_stop_price, target_price=target_price,
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
                "target_price_is_sentinel": is_sentinel_target,
            },
        ))
        return result

    def _compute_realized_cost(self) -> float:
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


__all__ = ["PolicyOrchestrator", "DemoDepsBundle", "DemoDepsFactory", "RealizedFillReader"]
