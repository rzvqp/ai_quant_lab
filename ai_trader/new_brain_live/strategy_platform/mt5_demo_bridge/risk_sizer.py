"""5%-of-CURRENT-equity, contract-aware position sizing (mandate sections 6-11, 18). The canonical S5
stop-loss is NEVER adjusted to hit a target risk -- position size adapts to the SL, never the reverse.
Monetary loss per lot is computed via the broker's own `order_calc_profit` (mandate section 8's own
explicit preference over an assumed/hardcoded $/pip or contract size) -- never a manually-derived
tick-value formula. Margin/leverage are NOT consulted here at all (mandate section 18: they may gate
feasibility elsewhere, they must never determine risk size)."""

from __future__ import annotations

import dataclasses
import math

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.gateway_ext import MT5BridgeGateway
from ai_trader.signal_engine.types import Direction

_ORDER_TYPE_BUY = 0  # mt5.ORDER_TYPE_BUY
_ORDER_TYPE_SELL = 1  # mt5.ORDER_TYPE_SELL

INVALID_EQUITY = "INVALID_EQUITY"
INVALID_SL_DISTANCE = "INVALID_SL_DISTANCE"
LOSS_CALCULATION_FAILED = "LOSS_CALCULATION_FAILED"
MIN_VOLUME_EXCEEDS_RISK_BUDGET = "MIN_VOLUME_EXCEEDS_RISK_BUDGET"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SizingResult:
    approved: bool
    reason: str | None = None
    volume: float | None = None
    loss_per_1_lot: float | None = None
    risk_budget_money: float | None = None
    modeled_risk_money: float | None = None
    modeled_risk_fraction: float | None = None
    capped_by_volume_max: bool = False

    def __post_init__(self) -> None:
        if not self.approved and self.reason is None:
            raise ValueError("SizingResult: approved=False must always carry a reason")
        if self.approved and self.volume is None:
            raise ValueError("SizingResult: approved=True must always carry a volume")


def _round_down_to_step(raw_volume: float, *, volume_step: float) -> float:
    # tiny epsilon guards against float round-trip noise (e.g. 0.03/0.01 landing on 2.9999999999996,
    # which floor() would wrongly truncate to 2 instead of the intended 3) -- never rounds UP through it.
    steps = math.floor(raw_volume / volume_step + 1e-9)
    return round(steps * volume_step, 8)


def loss_for_one_lot(
    gateway: MT5BridgeGateway, *, side: Direction, symbol: str, entry_price: float, sl_price: float,
) -> float | None:
    """Monetary loss of exactly 1.00 lot moving from `entry_price` to `sl_price`, via the broker's own
    `order_calc_profit`. Returns `None` (fail closed) on any calculation failure, non-finite result, or a
    non-positive magnitude -- never silently substitutes an estimate."""
    action = _ORDER_TYPE_BUY if side is Direction.LONG else _ORDER_TYPE_SELL
    try:
        profit = gateway.order_calc_profit(action, symbol, 1.0, entry_price, sl_price)
    except Exception:  # noqa: BLE001 -- any gateway-level failure fails closed, never silently estimated
        return None
    if profit is None or not math.isfinite(profit):
        return None
    loss = abs(float(profit))
    if loss <= 0.0:
        return None
    return loss


def compute_risk_sized_volume(
    *, gateway: MT5BridgeGateway, equity: float, side: Direction, symbol: str, entry_price: float,
    sl_price: float, volume_min: float, volume_max: float, volume_step: float, risk_fraction: float = 0.05,
) -> SizingResult:
    if not (math.isfinite(equity) and equity > 0.0):
        return SizingResult(approved=False, reason=INVALID_EQUITY)
    if side is Direction.LONG and not (sl_price < entry_price):
        return SizingResult(approved=False, reason=INVALID_SL_DISTANCE)
    if side is Direction.SHORT and not (sl_price > entry_price):
        return SizingResult(approved=False, reason=INVALID_SL_DISTANCE)

    risk_budget = equity * risk_fraction
    loss_1_lot = loss_for_one_lot(gateway, side=side, symbol=symbol, entry_price=entry_price, sl_price=sl_price)
    if loss_1_lot is None:
        return SizingResult(approved=False, reason=LOSS_CALCULATION_FAILED, risk_budget_money=risk_budget)

    raw_volume = risk_budget / loss_1_lot
    volume = _round_down_to_step(raw_volume, volume_step=volume_step)

    if volume < volume_min:
        min_lot_loss = loss_1_lot * volume_min
        return SizingResult(
            approved=False, reason=MIN_VOLUME_EXCEEDS_RISK_BUDGET, loss_per_1_lot=loss_1_lot,
            risk_budget_money=risk_budget, modeled_risk_money=min_lot_loss,
            modeled_risk_fraction=min_lot_loss / equity,
        )

    capped = False
    if volume > volume_max:
        # capping DOWN to volume_max only ever LOWERS modeled risk (loss scales linearly with volume) --
        # "economically identical except for lower risk" (mandate section 11) holds by construction.
        volume = _round_down_to_step(volume_max, volume_step=volume_step)
        capped = True

    modeled_risk_money = loss_1_lot * volume
    return SizingResult(
        approved=True, volume=volume, loss_per_1_lot=loss_1_lot, risk_budget_money=risk_budget,
        modeled_risk_money=modeled_risk_money, modeled_risk_fraction=modeled_risk_money / equity,
        capped_by_volume_max=capped,
    )
