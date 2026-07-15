"""The Portfolio Simulator -- the virtual account (``PORTFOLIO_SIMULATOR.md``).

Pure accounting + mark-to-market: books ``SimFillEvent``s from the Execution Simulator, maintains
positions, computes margin/exposure/drawdown, and projects the exact ``PortfolioState`` shape the Risk
Manager and Execution Engine consume live (``IMPLEMENTATION_CHOICES.md`` §2). No decisions -- it never
sizes, never denies, never trades.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.types import ClosedPosition, OpenPosition, PortfolioState
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.config import SimulationContext
from ai_trader.simulation.types import Bar, RiskEventRecord, SimFillEvent

_SECONDS_PER_DAY = 86400
_SECONDS_PER_WEEK = 7 * _SECONDS_PER_DAY


def _dir_sign(direction: Direction) -> float:
    return 1.0 if direction is Direction.LONG else -1.0


@dataclass(slots=True)
class Position:
    """One open position -- internal type, ``PORTFOLIO_SIMULATOR.md`` §3."""

    symbol: str
    strategy_id: str
    direction: Direction
    size: float
    avg_entry: float
    opened_as_of: int
    opened_bar_index: int
    correlation_group: str | None = None
    entry_stop_price: float | None = None
    mfe: float = 0.0
    mae: float = 0.0

    @property
    def notional(self) -> float:
        return self.size * self.avg_entry


@dataclass(frozen=True, slots=True)
class TradeRecord:
    """One closed trade (or partial exit) -- ``PORTFOLIO_SIMULATOR.md`` §6, feeds the trade-history
    artifact and the Performance Analyzer's attribution."""

    client_order_id: str
    strategy_id: str
    symbol: str
    direction: Direction
    entry_price: float
    exit_price: float
    entry_as_of: int
    exit_as_of: int
    qty: float
    gross_pnl: float
    fees: float
    net_pnl: float
    pnl_r: float | None
    holding_bars: int
    mfe: float
    mae: float


@dataclass(frozen=True, slots=True)
class EquityPoint:
    as_of: int
    balance: float
    equity: float
    drawdown_pct: float
    open_positions: int = 0
    phase_running: bool = True


@dataclass(slots=True)
class SimAccount:
    """The virtual account's full internal truth (``PORTFOLIO_SIMULATOR.md`` §2) -- richer than the
    ``PortfolioState`` wire shape it projects (``IMPLEMENTATION_CHOICES.md`` §2)."""

    starting_balance: float
    balance: float
    positions: dict[str, Position] = field(default_factory=dict)  # keyed by symbol (one per symbol, §3)
    pending_orders: int = 0
    equity_hwm: float = 0.0
    max_drawdown_pct: float = 0.0
    trade_ledger: list[TradeRecord] = field(default_factory=list)
    equity_curve: list[EquityPoint] = field(default_factory=list)
    #: The ordered stream of order-lifecycle/fill events (``PORTFOLIO_SIMULATOR.md`` §6: "the audit
    #: trail"). A gap a review caught: no such log ever existed -- ``artifacts.py`` was writing
    #: ``risk_events`` into a file literally named ``execution_log.jsonl``, under the wrong
    #: ``RecordConfig`` flag. This is the real thing that file is supposed to contain.
    execution_log: list[SimFillEvent] = field(default_factory=list)
    risk_events: list[RiskEventRecord] = field(default_factory=list)
    consecutive_losses: int = 0
    last_loss_as_of: int | None = None
    liquidation_halted: bool = False

    # last mark-to-market snapshot (recomputed every bar)
    equity: float = 0.0
    floating_pnl: float = 0.0
    used_margin: float = 0.0
    last_as_of: int = 0

    _day_key: int | None = field(default=None, repr=False)
    _day_start_equity: float = field(default=0.0, repr=False)
    _week_key: int | None = field(default=None, repr=False)
    _week_start_equity: float = field(default=0.0, repr=False)
    _realized_pnl_today: float = field(default=0.0, repr=False)
    _realized_pnl_this_week: float = field(default=0.0, repr=False)
    _unrealized_pnl_today: float = field(default=0.0, repr=False)
    _unrealized_pnl_this_week: float = field(default=0.0, repr=False)


class PortfolioSimulator:
    """One run's virtual account. Not thread-safe; one instance per run."""

    def __init__(self, context: SimulationContext, symbol_meta: dict[str, SymbolMeta]) -> None:
        self._context = context
        self._symbol_meta = symbol_meta
        self.account = SimAccount(
            starting_balance=context.starting_balance, balance=context.starting_balance,
            equity=context.starting_balance, equity_hwm=context.starting_balance,
        )
        self._stop_hints: dict[str, float] = {}

    # ------------------------------------------------------------------ inputs

    def register_stop_hint(self, client_order_id: str, stop_price: float | None) -> None:
        """The Harness registers a decision's protective stop distance, keyed by the resulting order's
        ``client_order_id``, before the fill arrives -- used to compute a trade's R-multiple
        (``pnl_R``). Absent (``None``): ``TradeRecord.pnl_r`` is ``None``, never fabricated
        (IMPLEMENTATION CHOICE, see the module docstring)."""
        if stop_price is not None:
            self._stop_hints[client_order_id] = stop_price

    def record_risk_event(self, event_type: str, as_of: int, detail: str | None = None) -> None:
        """Record a non-fill risk/account event (Risk Manager DENYs, SUSPENDED/EMERGENCY_STOP episodes,
        margin calls) for the Performance Analyzer's risk-event summary (``PERFORMANCE_ANALYZER.md``
        §6). A gap a review caught: only liquidation events were ever recorded here; the Harness now
        calls this for every non-ALLOW ``RiskDecision`` too."""
        self.account.risk_events.append(RiskEventRecord(type=event_type, as_of=as_of, detail=detail))

    def apply(self, fills: tuple[SimFillEvent, ...], bar_index: int) -> None:
        """Book ``fills`` -- open/increase, reduce, or close positions; realize PnL on any closing
        quantity; deduct commission from balance (``PORTFOLIO_SIMULATOR.md`` §5)."""
        for fill in sorted(fills, key=lambda f: f.client_order_id):
            self.account.execution_log.append(fill)
            self._apply_one(fill, bar_index)

    def _apply_one(self, fill: SimFillEvent, bar_index: int) -> None:
        acct = self.account
        existing = acct.positions.get(fill.symbol)
        fee = fill.commission
        acct.balance -= fee

        opening_direction = fill.direction
        if existing is None:
            if fill.reduce_only:
                return  # a stray reduce-only fill with nothing open -- nothing to reduce (defensive).
            acct.positions[fill.symbol] = Position(
                symbol=fill.symbol, strategy_id=fill.strategy_id, direction=opening_direction,
                size=fill.qty, avg_entry=fill.price, opened_as_of=fill.as_of, opened_bar_index=bar_index,
                entry_stop_price=self._stop_hints.pop(fill.client_order_id, None),
            )
            return

        if fill.direction is existing.direction and not fill.reduce_only:
            # Scale-in: weighted-average entry (``PORTFOLIO_SIMULATOR.md`` §3).
            total = existing.size + fill.qty
            existing.avg_entry = (existing.avg_entry * existing.size + fill.price * fill.qty) / total
            existing.size = total
            return

        # Reduce/close: opposite-direction (or explicit reduce_only) fill against an open position.
        close_qty = min(fill.qty, existing.size)
        gross = (fill.price - existing.avg_entry) * _dir_sign(existing.direction) * close_qty
        gross *= self._point_value(fill.symbol)
        net = gross - fee
        stop = existing.entry_stop_price
        pnl_r: float | None = None
        if stop is not None and stop != existing.avg_entry:
            risk_per_unit = abs(existing.avg_entry - stop)
            if risk_per_unit > 0:
                pnl_r = ((fill.price - existing.avg_entry) * _dir_sign(existing.direction)) / risk_per_unit

        acct.balance += gross
        self._book_realized(fill.as_of, net)
        if net < 0:
            acct.consecutive_losses += 1
            acct.last_loss_as_of = fill.as_of
        else:
            acct.consecutive_losses = 0

        acct.trade_ledger.append(TradeRecord(
            client_order_id=fill.client_order_id, strategy_id=existing.strategy_id, symbol=fill.symbol,
            direction=existing.direction, entry_price=existing.avg_entry, exit_price=fill.price,
            entry_as_of=existing.opened_as_of, exit_as_of=fill.as_of, qty=close_qty, gross_pnl=gross,
            fees=fee, net_pnl=net, pnl_r=pnl_r, holding_bars=bar_index - existing.opened_bar_index,
            mfe=existing.mfe, mae=existing.mae,
        ))

        existing.size -= close_qty
        if existing.size <= 1e-9:
            del acct.positions[fill.symbol]
        remainder = fill.qty - close_qty
        if remainder > 1e-9 and not fill.reduce_only:
            # The fill flipped the position: remainder opens a new one in the fill's own direction.
            acct.positions[fill.symbol] = Position(
                symbol=fill.symbol, strategy_id=fill.strategy_id, direction=fill.direction,
                size=remainder, avg_entry=fill.price, opened_as_of=fill.as_of, opened_bar_index=bar_index,
                entry_stop_price=self._stop_hints.pop(fill.client_order_id, None),
            )

    def _point_value(self, symbol: str) -> float:
        meta = self._symbol_meta.get(symbol)
        return meta.point_value if meta is not None else 1.0

    def _roll_periods(self, as_of: int) -> None:
        acct = self.account
        day_key = as_of // _SECONDS_PER_DAY
        week_key = as_of // _SECONDS_PER_WEEK
        if acct._day_key != day_key:
            acct._day_key = day_key
            acct._day_start_equity = acct.equity
            acct._realized_pnl_today = 0.0
        if acct._week_key != week_key:
            acct._week_key = week_key
            acct._week_start_equity = acct.equity
            acct._realized_pnl_this_week = 0.0

    def _book_realized(self, as_of: int, net_pnl: float) -> None:
        self._roll_periods(as_of)
        self.account._realized_pnl_today += net_pnl
        self.account._realized_pnl_this_week += net_pnl

    # ------------------------------------------------------------------ mark-to-market

    def mark_to_market(self, as_of: int, bars: dict[str, Bar], phase_running: bool = True) -> None:
        """Recompute equity/floating PnL/margin/drawdown from ``bars``' closes
        (``PORTFOLIO_SIMULATOR.md`` §2), update MFE/MAE from each open position's bar range, then check
        for a margin-call/liquidation event (``IMPLEMENTATION_CHOICES.md`` §6)."""
        self._roll_periods(as_of)
        acct = self.account
        acct.last_as_of = as_of
        floating = 0.0
        used_margin = 0.0
        margin_model = self._context.margin_model
        for symbol, pos in acct.positions.items():
            bar = bars.get(symbol)
            mark = bar.close if bar is not None else pos.avg_entry
            point_value = self._point_value(symbol)
            floating += (mark - pos.avg_entry) * _dir_sign(pos.direction) * pos.size * point_value
            used_margin += pos.size * mark * margin_model.initial_margin_pct
            if bar is not None:
                favorable = (bar.high - pos.avg_entry) if pos.direction is Direction.LONG else (pos.avg_entry - bar.low)
                adverse = (pos.avg_entry - bar.low) if pos.direction is Direction.LONG else (bar.high - pos.avg_entry)
                pos.mfe = max(pos.mfe, favorable)
                pos.mae = max(pos.mae, adverse)

        acct.floating_pnl = floating
        acct.used_margin = used_margin
        acct.equity = acct.balance + floating
        acct._unrealized_pnl_today = floating
        acct._unrealized_pnl_this_week = floating
        acct.equity_hwm = max(acct.equity_hwm, acct.equity)
        drawdown_pct = 0.0 if acct.equity_hwm <= 0 else max(0.0, (acct.equity_hwm - acct.equity) / acct.equity_hwm)
        acct.max_drawdown_pct = max(acct.max_drawdown_pct, drawdown_pct)
        acct.equity_curve.append(EquityPoint(
            as_of=as_of, balance=acct.balance, equity=acct.equity, drawdown_pct=drawdown_pct,
            open_positions=len(acct.positions), phase_running=phase_running,
        ))

        margin_level = (acct.equity / used_margin) if used_margin > 0 else float("inf")
        # A real bug a review caught: ``margin_level`` (equity/used_margin, a RATIO -- ~100 for a
        # healthy account at 1% initial margin) was being compared directly against
        # ``maintenance_margin_pct`` (a small PERCENTAGE, e.g. 0.005), so liquidation never fired
        # until equity was already catastrophically near zero. The correct, dimensionless threshold
        # is ``maintenance_margin_pct / initial_margin_pct`` -- IMPLEMENTATION_CHOICES.md §6's own
        # stated intent ("half of initial... margin call once equity has fallen to half the required
        # opening margin") is exactly ``margin_level < 0.5`` at the documented 0.005/0.01 defaults.
        margin_level_threshold = margin_model.maintenance_margin_pct / margin_model.initial_margin_pct
        if used_margin > 0 and margin_level < margin_level_threshold:
            self._liquidate(as_of, bars, margin_level_threshold)

    def _liquidate(self, as_of: int, bars: dict[str, Bar], margin_level_threshold: float) -> None:
        """Deterministic worst-loser-first liquidation (``IMPLEMENTATION_CHOICES.md`` §6): close
        positions, most-negative-floating-PnL first (ties by symbol id ascending), until
        ``margin_level`` clears maintenance or no positions remain."""
        acct = self.account
        margin_model = self._context.margin_model

        def floating_of(symbol: str, pos: Position) -> float:
            bar = bars.get(symbol)
            mark = bar.close if bar is not None else pos.avg_entry
            return (mark - pos.avg_entry) * _dir_sign(pos.direction) * pos.size * self._point_value(symbol)

        closed_any = False
        while acct.positions:
            ordered = sorted(acct.positions.items(), key=lambda kv: (floating_of(kv[0], kv[1]), kv[0]))
            symbol, pos = ordered[0]
            bar = bars.get(symbol)
            mark = bar.close if bar is not None else pos.avg_entry
            gross = (mark - pos.avg_entry) * _dir_sign(pos.direction) * pos.size * self._point_value(symbol)
            acct.balance += gross
            self._book_realized(as_of, gross)
            if gross < 0:
                acct.consecutive_losses += 1
                acct.last_loss_as_of = as_of
            acct.trade_ledger.append(TradeRecord(
                client_order_id=f"LIQUIDATION-{symbol}-{as_of}", strategy_id=pos.strategy_id, symbol=symbol,
                direction=pos.direction, entry_price=pos.avg_entry, exit_price=mark,
                entry_as_of=pos.opened_as_of, exit_as_of=as_of, qty=pos.size, gross_pnl=gross,
                fees=0.0, net_pnl=gross, pnl_r=None, holding_bars=0, mfe=pos.mfe, mae=pos.mae,
            ))
            del acct.positions[symbol]
            closed_any = True

            used_margin = sum(
                p.size * (bars[s].close if s in bars else p.avg_entry) * margin_model.initial_margin_pct
                for s, p in acct.positions.items()
            )
            equity = acct.balance + sum(floating_of(s, p) for s, p in acct.positions.items())
            acct.equity = equity
            acct.used_margin = used_margin
            margin_level = (equity / used_margin) if used_margin > 0 else float("inf")
            if margin_level >= margin_level_threshold:
                break

        if closed_any:
            acct.risk_events.append(RiskEventRecord(type="LIQUIDATION", as_of=as_of, detail=f"margin_level below {margin_level_threshold}"))
            if margin_model.halt_on_liquidation:
                acct.liquidation_halted = True

    # ------------------------------------------------------------------ output: PortfolioState projection

    def to_portfolio_state(self, as_of: int) -> PortfolioState:
        """Pure projection onto the Risk Manager/Execution Engine's own ``PortfolioState`` shape
        (``IMPLEMENTATION_CHOICES.md`` §2). Never mutates ``self.account``."""
        acct = self.account
        open_positions = tuple(
            OpenPosition(
                symbol=pos.symbol, strategy_id=pos.strategy_id, direction=pos.direction,
                size_units=pos.size, entry_price=pos.avg_entry,
                opened_bars_ago=0,  # bar-index bookkeeping lives on Position; RiskContext doesn't
                # thread the current bar_index into this projection call in v1 -- IMPLEMENTATION
                # CHOICE: 0 is the conservative default (never UNDER-counts a position's age-based
                # cooldown eligibility upstream; a real "bars ago" would only ever be >= 0 too).
                risk_pct=0.0, notional=pos.notional, correlation_group=pos.correlation_group,
            )
            for pos in sorted(acct.positions.values(), key=lambda p: p.symbol)
        )
        recent_closed = tuple(
            ClosedPosition(
                symbol=t.symbol, strategy_id=t.strategy_id, was_loss=t.net_pnl < 0,
                bars_since_close=0,
            )
            for t in acct.trade_ledger[-20:]
        )
        day_start = acct._day_start_equity if acct._day_start_equity > 0 else acct.starting_balance
        week_start = acct._week_start_equity if acct._week_start_equity > 0 else acct.starting_balance
        return PortfolioState(
            as_of=as_of, equity=acct.equity, equity_high_water_mark=acct.equity_hwm,
            open_positions=open_positions, recent_closed_positions=recent_closed,
            realized_pnl_pct_daily=acct._realized_pnl_today / day_start if day_start else 0.0,
            unrealized_pnl_pct_daily=acct._unrealized_pnl_today / day_start if day_start else 0.0,
            realized_pnl_pct_weekly=acct._realized_pnl_this_week / week_start if week_start else 0.0,
            unrealized_pnl_pct_weekly=acct._unrealized_pnl_this_week / week_start if week_start else 0.0,
            gross_notional=sum(p.notional for p in acct.positions.values()),
            consecutive_losses=acct.consecutive_losses,
            minutes_since_last_loss=(
                (as_of - acct.last_loss_as_of) / 60.0 if acct.last_loss_as_of is not None else None
            ),
            is_stale=False,
        )
