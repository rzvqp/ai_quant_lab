from __future__ import annotations

from ai_trader.execution_engine.types import OrderIntent, OrderSide, OrderType
from ai_trader.order_manager import reason_codes as rc
from ai_trader.order_manager.builder import build_order_request
from ai_trader.order_manager.tests._fixtures import make_instrument, make_intent
from ai_trader.signal_engine.types import Direction


def test_build_succeeds_for_a_well_formed_long_intent() -> None:
    outcome = build_order_request(make_intent(), make_instrument())
    assert outcome.success is True
    assert outcome.order is not None
    assert outcome.order.side is OrderSide.BUY
    assert outcome.order.intent is OrderIntent.OPEN
    assert outcome.order.order_type is OrderType.BRACKET


def test_build_short_intent_produces_sell_side() -> None:
    outcome = build_order_request(
        make_intent(direction=Direction.SHORT, entry=2000.0, stop=2010.0, target=1980.0), make_instrument(),
    )
    assert outcome.success is True
    assert outcome.order is not None
    assert outcome.order.side is OrderSide.SELL


def test_build_rounds_prices_to_tick_size() -> None:
    outcome = build_order_request(
        make_intent(entry=2000.003, stop=1990.007, target=2020.001), make_instrument(tick_size=0.01),
    )
    assert outcome.success is True
    assert outcome.order is not None
    assert outcome.order.limit_price == 2000.0
    assert outcome.order.bracket is not None
    assert outcome.order.bracket.stop_loss == 1990.01
    assert outcome.order.bracket.take_profit == 2020.0


def test_build_carries_pre_rounded_volume_through_unchanged() -> None:
    outcome = build_order_request(make_intent(volume=0.37), make_instrument())
    assert outcome.success is True
    assert outcome.order is not None
    assert outcome.order.quantity == 0.37


def test_build_rejects_instrument_symbol_mismatch() -> None:
    outcome = build_order_request(make_intent(symbol="EURUSD"), make_instrument(symbol="XAUUSD"))
    assert outcome.success is False
    assert outcome.reason == rc.INSTRUMENT_SYMBOL_MISMATCH


def test_build_deterministic_ids_from_proposal_id() -> None:
    outcome_a = build_order_request(make_intent(proposal_id="SAME"), make_instrument())
    outcome_b = build_order_request(make_intent(proposal_id="SAME"), make_instrument())
    assert outcome_a.order is not None and outcome_b.order is not None
    assert outcome_a.order.client_order_id == outcome_b.order.client_order_id
    assert outcome_a.order.order_request_id == outcome_b.order.order_request_id


def test_build_different_proposal_ids_produce_different_client_order_ids() -> None:
    outcome_a = build_order_request(make_intent(proposal_id="P-A"), make_instrument())
    outcome_b = build_order_request(make_intent(proposal_id="P-B"), make_instrument())
    assert outcome_a.order is not None and outcome_b.order is not None
    assert outcome_a.order.client_order_id != outcome_b.order.client_order_id
