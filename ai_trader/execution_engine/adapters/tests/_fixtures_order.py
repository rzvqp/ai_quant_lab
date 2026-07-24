"""A minimal, valid `OrderRequest` builder for adapter tests -- only `NullBrokerAdapter`'s own
`submit_order`/`cancel_order` need one; `MT5ReadOnlyBrokerAdapter` never does (it has no such methods)."""

from __future__ import annotations

from ai_trader.execution_engine.types import (
    OrderConstraints,
    OrderIntent,
    OrderRefs,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
)
from ai_trader.signal_engine.types import Direction


def make_order_request(client_order_id: str = "CID-TEST-1", **overrides: object) -> OrderRequest:
    kwargs: dict[str, object] = {
        "order_schema_version": "1.0.0", "execution_engine_version": "1.0.0",
        "order_request_id": "REQ-TEST-1", "client_order_id": client_order_id,
        "decision_id": "DEC-1", "strategy_id": "S1", "symbol": "XAUUSD", "timestamp": 1_700_000_000,
        "as_of": 1_700_000_000, "side": OrderSide.BUY, "direction": Direction.LONG,
        "intent": OrderIntent.OPEN, "order_type": OrderType.MARKET, "time_in_force": TimeInForce.GTC,
        "quantity": 0.1,
        "constraints": OrderConstraints(max_slippage=0.01, reduce_only=False, post_only=False),
        "refs": OrderRefs(risk_schema_version="1.0.0", risk_policy_version="1.0.0"),
    }
    kwargs.update(overrides)
    return OrderRequest(**kwargs)  # type: ignore[arg-type]
