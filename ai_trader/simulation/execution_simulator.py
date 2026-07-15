"""The Execution Simulator -- the virtual Broker Adapter (``EXECUTION_SIMULATOR.md``).

Implements ``ai_trader.execution_engine.broker_adapter.BrokerAdapter`` **unmodified** -- the exact
five-method pull-based Protocol the Execution Engine's own ``pipeline.py``/``reconciler.py`` already
call -- plus one simulation-only method, :meth:`ExecutionSimulator.advance_bar`, that the Simulation
Harness calls once per replayed bar to process fills deterministically against historical bars. See
``IMPLEMENTATION_CHOICES.md`` §1 for the full rationale of this split (frozen before any code was
written).

Determinism (``EXECUTION_SIMULATOR.md`` §8): fill price/qty/fees/timing are a pure function of
``(WorkingOrder, bar, cost/fill/slippage models, seed)``. No wall-clock, no global RNG -- the only
stochastic model (``seeded_random`` slippage) draws from a PRNG seeded by
``hash(run_seed, client_order_id, as_of)`` (``SimulationContext.seed_for``).
"""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from ai_trader.execution_engine.broker_adapter import BrokerAdapter
from ai_trader.execution_engine.types import (
    BrokerAck,
    BrokerCapabilities,
    BrokerOrderState,
    MarketStatus,
    OrderRequest,
    OrderState,
    OrderType,
    TimeInForce,
)
from ai_trader.market_scanner.timeframes import timeframe_seconds
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.config import SimulationContext
from ai_trader.simulation.types import (
    Bar,
    EntryTiming,
    IntrabarRule,
    PartialFillPolicy,
    SimFillEvent,
    SlippageModelType,
    TERMINAL_WORKING_STATES,
    WorkingOrder,
    WorkingOrderState,
)

#: ``WorkingOrderState`` values map 1:1 onto the subset of ``execution_engine.types.OrderState`` a real
#: broker would ever report (never the engine-internal pre-submit states) -- both enums share the exact
#: same member names, so this is a pure re-tag, not a translation table.
_STATE_MAP: dict[WorkingOrderState, OrderState] = {
    WorkingOrderState.ACKNOWLEDGED: OrderState.ACKNOWLEDGED,
    WorkingOrderState.PARTIALLY_FILLED: OrderState.PARTIALLY_FILLED,
    WorkingOrderState.FILLED: OrderState.FILLED,
    WorkingOrderState.CANCELLED: OrderState.CANCELLED,
    WorkingOrderState.REJECTED: OrderState.REJECTED,
    WorkingOrderState.EXPIRED: OrderState.EXPIRED,
}


@dataclass(slots=True)
class _BracketPlan:
    parent_id: str
    strategy_id: str
    symbol: str
    direction_is_buy: bool  # the ENTRY side; children close in the opposite direction
    take_profit: float | None
    stop_loss: float | None


def _direction_is_buy(order: OrderRequest) -> bool:
    return order.side.value == "BUY"


class ExecutionSimulator:
    """One run's virtual venue. Not thread-safe; one instance per ``SimulationContext`` run, exactly
    like every other simulation-only component."""

    def __init__(self, context: SimulationContext, capabilities: BrokerCapabilities) -> None:
        self._context = context
        self._caps = capabilities
        self._base_tf_seconds = timeframe_seconds(context.base_timeframe)
        self._orders: dict[str, WorkingOrder] = {}
        #: parent client_order_id -> pending bracket spec, materialized into OCO children on fill.
        self._bracket_plans: dict[str, _BracketPlan] = {}
        #: oco_group_id -> {client_order_id, ...}; a fill/trigger on one member cancels the rest.
        self._oco_groups: dict[str, set[str]] = {}
        self._order_source: dict[str, OrderRequest] = {}
        #: ``IMPLEMENTATION_CHOICES.md`` §5's committed pre-fill margin gate ("if required_margin >
        #: free_margin at fill time, the fill is rejected back deterministically") -- wired by the
        #: Harness via :meth:`set_free_margin_provider`. ``None`` (no provider set, e.g. in a unit test
        #: that constructs an ``ExecutionSimulator`` standalone) means the gate is a no-op, matching
        #: every prior module's own "absent optional input -> fail open to the existing behavior, never
        #: crash" precedent -- a real Harness-driven run ALWAYS wires this.
        self._free_margin_fn: Callable[[], float] | None = None

    def set_free_margin_provider(self, fn: Callable[[], float]) -> None:
        """``fn: Callable[[], float]`` -- the Portfolio Simulator's current free margin (as of the last
        mark-to-market), consulted before any OPENING/INCREASING fill (never for a reduce-only closing
        fill, which can only shrink exposure)."""
        self._free_margin_fn = fn

    # ------------------------------------------------------------------ BrokerAdapter contract (unmodified)

    def capabilities(self) -> BrokerCapabilities:
        return self._caps

    def submit_order(self, order: OrderRequest) -> BrokerAck:
        """Never raises (``broker_adapter.py``: "expected to be synchronous and non-raising"). Records
        the order as WORKING, ineligible for matching until strictly after ``order.as_of``'s bar
        (``EXECUTION_SIMULATOR.md`` §3: never the signal bar)."""
        if order.client_order_id in self._orders:
            # A genuine duplicate submit should never reach here (Execution Engine's own duplicate
            # guard runs first, ``pipeline.py``) -- defensive, fail-safe idempotent ack rather than a
            # corrupted double-booked order.
            return BrokerAck(accepted=True, broker_order_id=order.client_order_id)

        status = self._caps.status_for(order.symbol)
        if status is MarketStatus.CLOSED:
            rejected = WorkingOrder(
                client_order_id=order.client_order_id, symbol=order.symbol, order_type=order.order_type,
                side_is_buy=_direction_is_buy(order), direction=order.direction, quantity=order.quantity,
                time_in_force=order.time_in_force, submitted_as_of=order.as_of, strategy_id=order.strategy_id,
                state=WorkingOrderState.REJECTED, reason="MARKET_CLOSED",
            )
            self._orders[order.client_order_id] = rejected
            return BrokerAck(accepted=False, reason="MARKET_CLOSED")
        if order.quantity < self._caps.min_qty or order.quantity > self._caps.max_qty:
            rejected = WorkingOrder(
                client_order_id=order.client_order_id, symbol=order.symbol, order_type=order.order_type,
                side_is_buy=_direction_is_buy(order), direction=order.direction, quantity=order.quantity,
                time_in_force=order.time_in_force, submitted_as_of=order.as_of, strategy_id=order.strategy_id,
                state=WorkingOrderState.REJECTED, reason="QTY_OUT_OF_BOUNDS",
            )
            self._orders[order.client_order_id] = rejected
            return BrokerAck(accepted=False, reason="QTY_OUT_OF_BOUNDS")

        valid_until = _resolve_valid_until(order, self._base_tf_seconds)
        wo = WorkingOrder(
            client_order_id=order.client_order_id, symbol=order.symbol, order_type=order.order_type,
            side_is_buy=_direction_is_buy(order), direction=order.direction, quantity=order.quantity,
            time_in_force=order.time_in_force, submitted_as_of=order.as_of, strategy_id=order.strategy_id,
            limit_price=order.limit_price, stop_price=order.stop_price,
            take_profit=order.bracket.take_profit if order.bracket else None,
            stop_loss=order.bracket.stop_loss if order.bracket else None,
            reduce_only=order.constraints.reduce_only, max_slippage=order.constraints.max_slippage,
            valid_until=valid_until,
            oco_group_id=order.oco_link.group_id if order.oco_link else None,
        )
        self._orders[order.client_order_id] = wo
        self._order_source[order.client_order_id] = order
        if wo.oco_group_id is not None:
            self._oco_groups.setdefault(wo.oco_group_id, set()).add(order.client_order_id)
        if order.bracket is not None and (order.bracket.take_profit or order.bracket.stop_loss):
            self._bracket_plans[order.client_order_id] = _BracketPlan(
                parent_id=order.client_order_id, strategy_id=order.strategy_id, symbol=order.symbol,
                direction_is_buy=wo.side_is_buy, take_profit=order.bracket.take_profit,
                stop_loss=order.bracket.stop_loss,
            )
        return BrokerAck(accepted=True, broker_order_id=order.client_order_id)

    def cancel_order(self, client_order_id: str) -> BrokerAck:
        wo = self._orders.get(client_order_id)
        if wo is None:
            return BrokerAck(accepted=False, reason="UNKNOWN_ORDER")
        if wo.is_terminal:
            return BrokerAck(accepted=False, reason=f"ALREADY_TERMINAL:{wo.state.value}")
        wo.state = WorkingOrderState.CANCELLED
        wo.reason = "CANCEL_REQUESTED"
        self._cancel_oco_siblings(wo)
        return BrokerAck(accepted=True, broker_order_id=client_order_id)

    def query_status(self, client_order_id: str) -> BrokerOrderState | None:
        wo = self._orders.get(client_order_id)
        if wo is None:
            return None
        return BrokerOrderState(
            client_order_id=wo.client_order_id, state=_STATE_MAP[wo.state],
            filled_qty=wo.filled_qty, avg_price=wo.avg_price, reason=wo.reason,
        )

    def query_open_orders(self) -> tuple[BrokerOrderState, ...]:
        return tuple(
            BrokerOrderState(
                client_order_id=wo.client_order_id, state=_STATE_MAP[wo.state],
                filled_qty=wo.filled_qty, avg_price=wo.avg_price, reason=wo.reason,
            )
            for wo in self._orders.values() if not wo.is_terminal
        )

    # ------------------------------------------------------------------ simulation-only: bar matching

    def advance_bar(self, as_of: int, bars: Mapping[str, Bar]) -> tuple[SimFillEvent, ...]:
        """Match every WORKING order whose ``submitted_as_of < as_of`` against ``bars`` (deterministic,
        lookahead-safe: an order is never matched against the bar it was submitted on). Order of
        processing is fixed (ascending ``client_order_id``) for reproducibility across runs.

        **Same-bar stop/target race** (``EXECUTION_SIMULATOR.md`` §3: "when a single bar could hit both
        a stop and a target, the stop is assumed hit first"): this is resolved EXPLICITLY by
        :func:`_resolve_intrabar_conflict` against the OCO group's actual trigger conditions for this
        bar -- never left to incidental ``client_order_id`` sort order (the exact bug class
        ``SIMULATION_HANDOFF.md`` §13 warns "prose ordering vs execution-order correctness" findings
        take: a string-sort accident that happens to agree with the rule today would silently break the
        moment an id format changes).
        """
        fills: list[SimFillEvent] = []
        processed: set[str] = set()
        for client_order_id in sorted(self._orders.keys()):
            if client_order_id in processed:
                continue
            wo = self._orders[client_order_id]
            processed.add(client_order_id)
            if wo.is_terminal or wo.submitted_as_of >= as_of:
                continue
            if wo.valid_until is not None and as_of > wo.valid_until:
                self._expire(wo)
                continue
            bar = bars.get(wo.symbol)
            if bar is None:
                continue  # no data this cycle -- stays working, never fabricates a price

            live_siblings = self._live_oco_siblings(wo, as_of)
            candidates = [wo, *live_siblings]
            triggered = [c for c in candidates if self._would_trigger(c, bar)]
            if len(triggered) > 1:
                winner = _resolve_intrabar_conflict(triggered, self._context.fill_model.intrabar)
                for c in candidates:
                    processed.add(c.client_order_id)
                fill = self._match_and_enforce_tif(winner, bar, as_of)
                if fill is not None:
                    fills.append(fill)
                continue

            fill = self._match_and_enforce_tif(wo, bar, as_of)
            if fill is not None:
                fills.append(fill)
        return tuple(fills)

    def _match_and_enforce_tif(self, wo: WorkingOrder, bar: Bar, as_of: int) -> SimFillEvent | None:
        """Match ``wo`` against ``bar``, then immediately enforce TIF -- fixing a real bug a review
        caught: enforcing TIF only AFTER the caller had already queued the returned ``SimFillEvent``
        meant a FOK order's partial fill got reverted in the order book (``wo.filled_qty`` reset to 0,
        state -> CANCELLED) while the ALREADY-EMITTED fill event still flowed to the Portfolio
        Simulator, permanently desyncing the two. TIF is now enforced INSIDE this method, before
        deciding what (if anything) to return, so a FOK-reverted fill is never emitted at all."""
        fill = self._match_one(wo, bar, as_of)
        self._enforce_tif(wo, as_of)
        if fill is not None and wo.time_in_force is TimeInForce.FOK and wo.reason == "FOK_NOT_FILLED":
            return None  # the fill was just reverted by _enforce_tif -- never report it.
        return fill

    def _live_oco_siblings(self, wo: WorkingOrder, as_of: int) -> list[WorkingOrder]:
        if wo.oco_group_id is None:
            return []
        return [
            self._orders[sid] for sid in self._oco_groups.get(wo.oco_group_id, ())
            if sid != wo.client_order_id and sid in self._orders
            and not self._orders[sid].is_terminal and self._orders[sid].submitted_as_of < as_of
        ]

    def _would_trigger(self, wo: WorkingOrder, bar: Bar) -> bool:
        if wo.order_type is OrderType.MARKET:
            return True
        if wo.order_type is OrderType.LIMIT:
            return _limit_touched(wo, bar)
        if wo.order_type in (OrderType.STOP, OrderType.STOP_LIMIT):
            return _stop_triggered(wo, bar)
        if wo.order_type in (OrderType.BRACKET, OrderType.OCO):
            return _limit_touched(wo, bar) if wo.limit_price is not None else True
        return False  # pragma: no cover -- exhaustive OrderType handling; defensive only

    def _match_one(self, wo: WorkingOrder, bar: Bar, as_of: int) -> SimFillEvent | None:
        cost = self._context.cost_model
        fill_model = self._context.fill_model
        # IMPLEMENTATION CHOICE, corrected after the conformance test caught a real mismatch: the
        # frozen research engine (`code/mstrat.py`: "cost=(spread_ticks+slip_ticks)*TICK") applies the
        # FULL configured tick count per leg, not a halved bid/ask-style spread -- so the "1 tick
        # spread" default v1 cost model (`EXECUTION_SIMULATOR.md` §4) means a full 1-tick offset on
        # each side, matching the research engine's own per-leg cost convention exactly (never halved).
        spread_price = cost.spread_ticks * self._caps.tick_size

        # ``apply_spread``/``apply_slippage`` are keyed off HOW the price was determined for THIS
        # fill, never off the raw ``order_type`` label alone (two real bugs tests caught): a resting
        # LIMIT (or a LIMIT-priced BRACKET/STOP_LIMIT leg) fills exactly "at limit_price"
        # (``EXECUTION_SIMULATOR.md`` §3) -- neither spread nor slippage. A triggered STOP fills "at
        # the trigger price +/- slippage" ONLY -- the doc's Stop row deliberately omits spread
        # (contrasted with the Market row's explicit "+/- spread +/- slippage"), so a stop is charged
        # slippage but not a separate spread on top of its own trigger price.
        trigger_price: float | None = None
        apply_spread = False
        apply_slippage = False
        if wo.order_type is OrderType.MARKET:
            trigger_price = bar.open
            apply_spread = True
            apply_slippage = True
        elif wo.order_type is OrderType.LIMIT:
            if _limit_touched(wo, bar):
                trigger_price = wo.limit_price  # fills at limit_price exactly (EXECUTION_SIMULATOR.md §3)
        elif wo.order_type in (OrderType.STOP, OrderType.STOP_LIMIT):
            if _stop_triggered(wo, bar):
                if wo.order_type is OrderType.STOP:
                    trigger_price = wo.stop_price
                    apply_slippage = True
                else:
                    # STOP_LIMIT: on trigger becomes a limit at limit_price, checked same bar (touch rule).
                    if wo.limit_price is not None and _price_in_range(wo.limit_price, bar):
                        trigger_price = wo.limit_price
                    # else: stays working as a resting limit for subsequent bars -- no state change
                    # needed here since order_type/limit_price already carry that shape.
        elif wo.order_type in (OrderType.BRACKET, OrderType.OCO):
            # A BRACKET parent with no explicit entry price behaves like MARKET (ExecConfig's own
            # default order-mapping policy uses a marketable LIMIT/MARKET for the entry leg; a bare
            # BRACKET order_type with a limit_price present is entry-priced like a resting LIMIT.
            if wo.limit_price is not None:
                if _limit_touched(wo, bar):
                    trigger_price = wo.limit_price
            else:
                trigger_price = bar.open
                apply_spread = True
                apply_slippage = True
        else:  # pragma: no cover -- exhaustive OrderType handling; defensive only
            trigger_price = None

        if trigger_price is None:
            return None

        fill_qty = self._fillable_qty(wo)
        fill_price, spread_cost, slippage_cost = self._priced_fill(
            wo, trigger_price, spread_price, as_of, fill_qty, apply_spread, apply_slippage,
        )
        commission = self._commission(fill_qty)

        if not wo.reduce_only and self._reject_for_insufficient_margin(wo, fill_qty, fill_price):
            wo.state = WorkingOrderState.REJECTED
            wo.reason = "INSUFFICIENT_MARGIN"
            self._cancel_oco_siblings(wo)
            return None

        wo.filled_qty += fill_qty
        wo.avg_price = fill_price if wo.avg_price is None else (
            (wo.avg_price * (wo.filled_qty - fill_qty) + fill_price * fill_qty) / wo.filled_qty
        )
        if wo.remaining_qty <= 1e-12:
            wo.state = WorkingOrderState.FILLED
            self._cancel_oco_siblings(wo)
            self._activate_bracket_children(wo, as_of)
        else:
            wo.state = WorkingOrderState.PARTIALLY_FILLED

        source = self._order_source.get(wo.client_order_id)
        return SimFillEvent(
            client_order_id=wo.client_order_id,
            order_request_id=source.order_request_id if source is not None else wo.client_order_id,
            strategy_id=wo.strategy_id, symbol=wo.symbol, direction=wo.direction,
            intent_close=wo.reduce_only, qty=fill_qty, price=fill_price,
            spread_cost=spread_cost, slippage_cost=slippage_cost, commission=commission, as_of=as_of,
            reduce_only=wo.reduce_only,
        )

    def _reject_for_insufficient_margin(self, wo: WorkingOrder, fill_qty: float, fill_price: float) -> bool:
        """``IMPLEMENTATION_CHOICES.md`` §5's committed pre-fill margin gate: "if required_margin >
        free_margin at fill time, the fill is rejected back deterministically" -- a real gap a review
        caught (the commitment was documented but never implemented). Mirrors the exact
        ``size * mark * initial_margin_pct`` convention ``PortfolioSimulator.mark_to_market`` already
        uses for ``used_margin`` (no point-value multiplier there either), so the two stay consistent.
        No-op (never rejects) when no free-margin provider is wired (see
        :meth:`set_free_margin_provider`'s own docstring)."""
        if self._free_margin_fn is None:
            return False
        required_margin = fill_qty * fill_price * self._context.margin_model.initial_margin_pct
        return required_margin > self._free_margin_fn()

    def _priced_fill(
        self, wo: WorkingOrder, reference_price: float, spread_price: float, as_of: int, fill_qty: float,
        apply_spread: bool, apply_slippage: bool,
    ) -> tuple[float, float, float]:
        """Apply spread and/or slippage around ``reference_price`` (``EXECUTION_SIMULATOR.md`` §4),
        per the flags :meth:`_match_one` resolved from HOW the price was determined (never from the
        raw ``order_type`` alone -- two real bugs regression-tested by
        ``test_conformance_vs_research_engine.py``): a resting LIMIT-style fill gets neither; a
        triggered STOP gets slippage only (the doc's Stop row omits spread); MARKET gets both."""
        spread_signed = (spread_price if wo.side_is_buy else -spread_price) if apply_spread else 0.0
        slippage = self._slippage(wo, as_of) if apply_slippage else 0.0
        slippage_signed = slippage if wo.side_is_buy else -slippage
        fill_price = reference_price + spread_signed + slippage_signed
        return fill_price, abs(spread_signed) * fill_qty, abs(slippage_signed) * fill_qty

    def _slippage(self, wo: WorkingOrder, as_of: int) -> float:
        model = self._context.fill_model.slippage_model
        tick = self._caps.tick_size
        if model.type is SlippageModelType.FIXED:
            raw = model.fixed_ticks * tick
        elif model.type is SlippageModelType.ATR_FRACTION:
            raw = 0.0  # IMPLEMENTATION CHOICE: no ATR is threaded into the Execution Simulator in v1
            # (ATR lives in the MarketContext the Signal/Scoring/Risk stages consume, not in the bare
            # OHLCV ``Bar`` this module matches against) -- disclosed limitation, falls back to zero
            # extra slippage rather than fabricating a value; FIXED/SEEDED_RANDOM are the two v1-
            # supported models in practice.
        elif model.type is SlippageModelType.SEEDED_RANDOM:
            seed = self._context.seed_for(f"{wo.client_order_id}:{as_of}")
            rng = random.Random(seed)
            raw = rng.uniform(0.0, model.max_slippage_ticks * tick)
        else:  # pragma: no cover
            raw = 0.0
        cap = wo.max_slippage if wo.max_slippage is not None else model.max_slippage_ticks * tick
        return min(raw, cap) if cap is not None else raw

    def _fillable_qty(self, wo: WorkingOrder) -> float:
        policy = self._context.fill_model.partial_fill_policy
        remaining = wo.remaining_qty
        if policy is PartialFillPolicy.FULL_FILL:
            return remaining
        fraction = self._context.fill_model.partial_fill_fraction
        return min(remaining, wo.quantity * fraction) if wo.filled_qty == 0.0 else remaining

    def _commission(self, qty: float) -> float:
        return self._context.cost_model.commission_per_lot * qty

    def _enforce_tif(self, wo: WorkingOrder, as_of: int) -> None:
        if wo.is_terminal:
            return
        if wo.time_in_force in (TimeInForce.IOC, TimeInForce.FOK):
            # First eligible bar already ran (this call); IOC keeps whatever filled and cancels the
            # remainder now, FOK cancels entirely unless it fully filled (``EXECUTION_SIMULATOR.md`` §6).
            if wo.time_in_force is TimeInForce.FOK and wo.filled_qty > 0.0 and wo.remaining_qty > 1e-12:
                wo.filled_qty = 0.0  # FOK: partial is not acceptable -- revert the partial, cancel fully.
                wo.state = WorkingOrderState.CANCELLED
                wo.reason = "FOK_NOT_FILLED"
                self._cancel_oco_siblings(wo)
            elif wo.remaining_qty > 1e-12:
                # IOC: cancel the unfilled remainder (``EXECUTION_SIMULATOR.md`` §6). A real bug a
                # review caught: this used to label a PARTIALLY-filled IOC order ``FILLED`` (since
                # ``filled_qty > 0``), which falsely implies the full requested quantity executed --
                # ``CANCELLED`` is correct regardless of whether some quantity filled; ``filled_qty``
                # on the record already carries the true partial amount for any consumer that needs it.
                wo.state = WorkingOrderState.CANCELLED
                wo.reason = "IOC_UNFILLED_REMAINDER" if wo.filled_qty == 0.0 else "IOC_PARTIAL_REMAINDER_CANCELLED"
                self._cancel_oco_siblings(wo)

    def _expire(self, wo: WorkingOrder) -> None:
        wo.state = WorkingOrderState.EXPIRED
        wo.reason = "EXPIRED_TIF"
        self._cancel_oco_siblings(wo)

    def _cancel_oco_siblings(self, wo: WorkingOrder) -> None:
        if wo.oco_group_id is None:
            return
        for sibling_id in self._oco_groups.get(wo.oco_group_id, ()):
            if sibling_id == wo.client_order_id:
                continue
            sibling = self._orders.get(sibling_id)
            if sibling is not None and not sibling.is_terminal:
                sibling.state = WorkingOrderState.CANCELLED
                sibling.reason = "OCO_SIBLING_FILLED"

    def _activate_bracket_children(self, parent: WorkingOrder, as_of: int) -> None:
        plan = self._bracket_plans.pop(parent.client_order_id, None)
        if plan is None or (plan.take_profit is None and plan.stop_loss is None):
            return
        group_id = f"OCO-{parent.client_order_id}"
        child_side_is_buy = not plan.direction_is_buy  # closing leg trades the opposite side
        close_direction = _opposite(parent.direction)
        if plan.take_profit is not None:
            tp_id = f"{parent.client_order_id}-TP"
            self._orders[tp_id] = WorkingOrder(
                client_order_id=tp_id, symbol=plan.symbol, order_type=OrderType.LIMIT,
                side_is_buy=child_side_is_buy, direction=close_direction, quantity=parent.filled_qty,
                time_in_force=TimeInForce.GTC, submitted_as_of=as_of, strategy_id=plan.strategy_id,
                limit_price=plan.take_profit, reduce_only=True, oco_group_id=group_id,
            )
            self._oco_groups.setdefault(group_id, set()).add(tp_id)
        if plan.stop_loss is not None:
            sl_id = f"{parent.client_order_id}-SL"
            self._orders[sl_id] = WorkingOrder(
                client_order_id=sl_id, symbol=plan.symbol, order_type=OrderType.STOP,
                side_is_buy=child_side_is_buy, direction=close_direction, quantity=parent.filled_qty,
                time_in_force=TimeInForce.GTC, submitted_as_of=as_of, strategy_id=plan.strategy_id,
                stop_price=plan.stop_loss, reduce_only=True, oco_group_id=group_id,
            )
            self._oco_groups.setdefault(group_id, set()).add(sl_id)


def _opposite(direction: Direction) -> Direction:
    return Direction.SHORT if direction is Direction.LONG else Direction.LONG


def _limit_touched(wo: WorkingOrder, bar: Bar) -> bool:
    assert wo.limit_price is not None
    return bar.low <= wo.limit_price if wo.side_is_buy else bar.high >= wo.limit_price


def _stop_triggered(wo: WorkingOrder, bar: Bar) -> bool:
    assert wo.stop_price is not None
    return bar.high >= wo.stop_price if wo.side_is_buy else bar.low <= wo.stop_price


def _price_in_range(price: float, bar: Bar) -> bool:
    return bar.low <= price <= bar.high


def _resolve_intrabar_conflict(triggered: list[WorkingOrder], rule: IntrabarRule) -> WorkingOrder:
    """Deterministically pick ONE winner among orders that would all trigger against the SAME bar
    (``EXECUTION_SIMULATOR.md`` §3). ``triggered`` is already in a fixed order (the caller's own
    ``sorted(client_order_id)`` traversal), so any fallback here is still deterministic."""
    stops = [c for c in triggered if c.order_type in (OrderType.STOP, OrderType.STOP_LIMIT)]
    targets = [c for c in triggered if c.order_type is OrderType.LIMIT]
    if rule is IntrabarRule.STOP_BEFORE_TARGET and stops:
        return stops[0]
    if rule is IntrabarRule.TARGET_BEFORE_STOP and targets:
        return targets[0]
    return triggered[0]  # PROPORTIONAL (or no stop/target among the candidates): fixed first-in-order.


def _resolve_valid_until(order: OrderRequest, base_tf_seconds: int) -> int | None:
    """Resolve ``order.constraints.valid_until`` to an absolute epoch-seconds deadline.

    IMPLEMENTATION CHOICE, corrected after a real test failure caught it: ``constraints.valid_until``
    is NOT an absolute timestamp here -- Risk Manager's own ``config.py`` (``ConstraintDefaults``
    docstring) documents storing it as a **bar COUNT** ("v1 uses a bar count since the Risk Manager
    has no wall-clock in its logic to convert it to an absolute timestamp itself"), since
    ``RISK_SCHEMA.json`` allows either ``string`` or ``integer`` for that field without fixing the
    convention. An integer ``valid_until`` is therefore interpreted as "expires after N base-timeframe
    bars from submission" -- ``order.as_of + N * base_tf_seconds`` -- never as a raw epoch value.
    A ``str`` value (an unspecified alternate convention, never produced by this repo's own Risk
    Manager) is not understood in v1 and is treated as "no expiry" rather than guessed at.
    """
    raw = order.constraints.valid_until
    if isinstance(raw, int):
        return order.as_of + raw * base_tf_seconds
    if order.time_in_force is TimeInForce.DAY:
        seconds_per_day = 86400
        return ((order.as_of // seconds_per_day) + 1) * seconds_per_day
    return None
