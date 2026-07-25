from __future__ import annotations

from ai_trader.mt5_demo_execution.request_builder import build_mt5_request
from ai_trader.mt5_demo_execution.tests._fixtures import make_order_request


def test_request_carries_symbol_volume_price() -> None:
    request = build_mt5_request(make_order_request(), action=1, mt5_order_type=0, deviation_points=20)
    assert request["symbol"] == "XAUUSD"
    assert request["volume"] == 0.01
    assert request["price"] == 2000.0
    assert request["type"] == 0
    assert request["action"] == 1


def test_request_carries_bracket_as_sl_tp() -> None:
    request = build_mt5_request(make_order_request(), action=1, mt5_order_type=0, deviation_points=20)
    assert request["sl"] == 1990.0
    assert request["tp"] == 2020.0


def test_request_omits_sl_tp_when_no_bracket() -> None:
    request = build_mt5_request(make_order_request(bracket=None), action=1, mt5_order_type=0, deviation_points=20)
    assert "sl" not in request
    assert "tp" not in request


def test_magic_and_comment_are_deterministic() -> None:
    order = make_order_request()
    first = build_mt5_request(order, action=1, mt5_order_type=0, deviation_points=20)
    second = build_mt5_request(order, action=1, mt5_order_type=0, deviation_points=20)
    assert first["magic"] == second["magic"]
    assert first["comment"] == second["comment"]
    assert first["comment"] == "S1:DEC-1"


def test_different_client_order_ids_produce_different_magic_numbers() -> None:
    a = build_mt5_request(make_order_request(client_order_id="CID-A"), action=1, mt5_order_type=0, deviation_points=20)
    b = build_mt5_request(make_order_request(client_order_id="CID-B"), action=1, mt5_order_type=0, deviation_points=20)
    assert a["magic"] != b["magic"]
