"""`MT5PortfolioStateSource` -- the ONE real implementation of `risk_manager_live.types.
PortfolioStateSource` (CEO instruction, 2026-07-25: "o singură implementare a interfeței, nu două").
Reads live account/position/deal data through `MT5HistoryGateway` (read-only, additive extension of the
existing, already-validated MT5 gateway -- never a new path to MT5, never an execution-capable adapter).

**Fail-closed, by design, on every incomplete read**: `account_info()`/`positions_get()`/
`history_deals_get()` returning `None` (MT5's own documented failure signal) raises
`PortfolioDataUnavailableError` -- never substituted with an empty tuple or a 0.0 P&L. The prior
caller-supplied default of `0.0` for these fields reads as "no losses," the most permissive outcome
possible exactly when nothing is actually known (Risk Audit #1's own finding) -- the wrong direction of
error for a circuit breaker's own data source. The caller (`execution_orchestrator.orchestrate()`) is
responsible for treating this exception as a reason not to trade.

**Scope boundary, disclosed**: this source populates `equity`, `equity_high_water_mark`, and the daily/
weekly realized+unrealized P&L + consecutive-loss fields the loss/drawdown guards and cooldown checks
actually read. It deliberately leaves `open_positions`/`recent_closed_positions`/`gross_notional` at
their type's own empty defaults -- those feed `limits.py`'s position-count/correlation/leverage checks,
a separate concern from P&L, and reconstructing them would require mapping MT5 position/order tags back
onto `strategy_id`/`risk_pct`/`correlation_group`, which this step was not authorized to build.

**Equity high-water mark, disclosed limitation**: tracked from whichever equity value this object first
observes (or an optionally-seeded starting value) and only ratchets upward from there -- it does NOT
reconstruct the account's true all-time-high equity from history MT5 does not expose as a single value.
If the real historical peak exceeds what this object has observed since construction (and no seed was
supplied), drawdown will read smaller than reality until enough live observation accumulates. This is a
disclosed limitation, not a silent estimate.

**Mandate 2 (2026-07-27), persistence**: an optional injected `SqliteStateStore` makes the high-water
mark survive a process restart -- without one, behavior is byte-for-byte the prior in-memory-only
version (every pre-Mandate-2 test still passes unmodified). With one, the persisted value (a REAL prior
observation) takes precedence over `initial_equity_high_water_mark` (a fallback seed only meaningful
when nothing has been persisted yet), and every ratchet-up writes through immediately. Consecutive-loss
detection is NOT touched by this mandate -- it has no in-memory state to lose on restart, since
`compute_consecutive_losses` is recomputed from a live 7-day MT5 deal-history query on every single
call, restart or not; its own separately-disclosed limitation (bounded to that same 7-day window) is a
data-window question, not a persistence one, and remains its own, still-not-authorized graph item.
"""

from __future__ import annotations

import time
from typing import Callable

from ai_trader.mt5_pnl_source.computation import (
    compute_consecutive_losses,
    compute_realized_pnl_pct,
    compute_unrealized_pnl_pct,
)
from ai_trader.mt5_pnl_source.gateway import MT5HistoryGateway
from ai_trader.mt5_pnl_source.types import DealRecord, PortfolioDataUnavailableError
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import PortfolioState

_SECONDS_PER_DAY = 86_400
_SECONDS_PER_WEEK = 7 * _SECONDS_PER_DAY
_HIGH_WATER_MARK_KEY = "mt5_pnl_source.equity_high_water_mark"


def _default_clock() -> int:
    return int(time.time())


class MT5PortfolioStateSource:
    """Structurally satisfies `risk_manager_live.types.PortfolioStateSource` (a `Protocol` -- no
    inheritance required, matching this codebase's own established duck-typing convention for fake/real
    gateway implementations)."""

    def __init__(
        self, gateway: MT5HistoryGateway, clock: Callable[[], int] = _default_clock,
        initial_equity_high_water_mark: float | None = None,
        state_store: SqliteStateStore | None = None,
    ) -> None:
        self._gateway = gateway
        self._clock = clock
        self._state_store = state_store
        persisted = None if state_store is None else state_store.get_value(_HIGH_WATER_MARK_KEY)
        self._equity_high_water_mark = (
            persisted if persisted is not None else initial_equity_high_water_mark
        )

    def current_portfolio_state(self) -> PortfolioState:
        now = self._clock()
        equity = self._read_equity()
        open_profits = self._read_open_position_profits()
        deals = self._read_deals(now - _SECONDS_PER_WEEK, now)

        if self._equity_high_water_mark is None or equity > self._equity_high_water_mark:
            self._equity_high_water_mark = equity
            if self._state_store is not None:
                self._state_store.set_value(_HIGH_WATER_MARK_KEY, self._equity_high_water_mark)

        day_start = now - (now % _SECONDS_PER_DAY)
        week_start = now - _SECONDS_PER_WEEK
        consecutive_losses, minutes_since_last_loss = compute_consecutive_losses(deals, now)

        return PortfolioState(
            as_of=now,
            equity=equity,
            equity_high_water_mark=self._equity_high_water_mark,
            realized_pnl_pct_daily=compute_realized_pnl_pct(deals, day_start, equity),
            unrealized_pnl_pct_daily=compute_unrealized_pnl_pct(open_profits, equity),
            realized_pnl_pct_weekly=compute_realized_pnl_pct(deals, week_start, equity),
            unrealized_pnl_pct_weekly=compute_unrealized_pnl_pct(open_profits, equity),
            consecutive_losses=consecutive_losses,
            minutes_since_last_loss=minutes_since_last_loss,
        )

    def _read_equity(self) -> float:
        account = self._gateway.account_info()
        if account is None:
            raise PortfolioDataUnavailableError("account_info() returned None")
        equity = getattr(account, "equity", None)
        if equity is None:
            raise PortfolioDataUnavailableError("account_info() result has no equity field")
        equity = float(equity)
        if equity <= 0:
            raise PortfolioDataUnavailableError(f"account_info().equity is non-positive: {equity!r}")
        return equity

    def _read_open_position_profits(self) -> tuple[float, ...]:
        positions = self._gateway.positions_get()
        if positions is None:
            raise PortfolioDataUnavailableError("positions_get() returned None")
        profits: list[float] = []
        for position in positions:
            profit = getattr(position, "profit", None)
            if profit is None:
                raise PortfolioDataUnavailableError("a position record is missing its profit field")
            profits.append(float(profit))
        return tuple(profits)

    def _read_deals(self, date_from: int, date_to: int) -> tuple[DealRecord, ...]:
        deals = self._gateway.history_deals_get(date_from, date_to)
        if deals is None:
            raise PortfolioDataUnavailableError(
                f"history_deals_get({date_from}, {date_to}) returned None"
            )
        records: list[DealRecord] = []
        for deal in deals:
            profit = getattr(deal, "profit", None)
            close_time = getattr(deal, "time", None)
            if profit is None or close_time is None:
                raise PortfolioDataUnavailableError("a deal record is missing profit/time")
            records.append(DealRecord(profit=float(profit), close_time=int(close_time)))
        return tuple(records)
