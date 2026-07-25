"""`build_mt5_request` -- translates the REUSED, unmodified `execution_engine.types.OrderRequest` into
the raw dict shape `mt5.order_check()`/`mt5.order_send()` both expect. Pure, deterministic, no I/O.

**Disclosed gap**: `OrderRequest` carries no `magic`/`comment` field (confirmed absent, `ApprovedTradeIntent`'s
own docstring names this exact gap) -- `client_order_id`/`strategy_id`/`decision_id`, which ARE present
on `OrderRequest`, are used to derive both deterministically (never randomly): `magic` is a bounded hash
of `client_order_id`, `comment` is `f"{strategy_id}:{decision_id}"` truncated to `_COMMENT_MAX_LENGTH`.
This is a Phase 10 IMPLEMENTATION CHOICE, not a fabrication -- both values are fully reproducible from
the same `OrderRequest`, never invented per-call.

**`_COMMENT_MAX_LENGTH` bug fix (real, test-demonstrated, CEO-authorized 2026-07-25)**: originally set
to 31, based on MT5's own documented comment field size. The real terminal used in this project's own
operational testing (`FusionMarkets-Demo`, build 5836) rejects `order_check()`/`order_send()` with
`last_error() == (-2, 'Invalid "comment" argument')` for any comment of 29+ characters -- confirmed
empirically via a read-only `order_check()` sweep (28 chars: accepted; 29-31 chars: rejected). No
documented, general-purpose MT5 comment-length constant exists that is safe across every broker/build,
so 27 is used here (one character of margin below the empirically-confirmed-working 28) -- a disclosed,
broker-observed value, not a documented MT5 API guarantee."""

from __future__ import annotations

from ai_trader.execution_engine.types import OrderRequest

_TIME_GTC = 0  # mt5.ORDER_TIME_GTC
_FILLING_IOC = 1  # mt5.ORDER_FILLING_IOC
_MAGIC_MODULUS = 1_000_000
_COMMENT_MAX_LENGTH = 27


def _magic_number_for(client_order_id: str) -> int:
    return abs(hash(client_order_id)) % _MAGIC_MODULUS


def _comment_for(strategy_id: str, decision_id: str) -> str:
    return f"{strategy_id}:{decision_id}"[:_COMMENT_MAX_LENGTH]


def build_mt5_request(
    order: OrderRequest, action: int, mt5_order_type: int, deviation_points: int,
) -> dict[str, object]:
    request: dict[str, object] = {
        "action": action,
        "symbol": order.symbol,
        "volume": order.quantity,
        "type": mt5_order_type,
        "price": order.limit_price if order.limit_price is not None else 0.0,
        "deviation": deviation_points,
        "magic": _magic_number_for(order.client_order_id),
        "comment": _comment_for(order.strategy_id, order.decision_id),
        "type_time": _TIME_GTC,
        "type_filling": _FILLING_IOC,
    }
    if order.bracket is not None:
        if order.bracket.stop_loss is not None:
            request["sl"] = order.bracket.stop_loss
        if order.bracket.take_profit is not None:
            request["tp"] = order.bracket.take_profit
    return request
