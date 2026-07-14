"""Tests for :mod:`ai_trader.strategy_manager.handle`."""

from __future__ import annotations

import pytest

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.exceptions import StrategyApiNotImplementedError
from ai_trader.strategy_manager.handle import StrategyHandle, StrategyRuntimeHandle
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict

SYMBOLS = frozenset({"XAUUSD"})


class TestStrategyRuntimeHandle:
    def test_required_context_matches_contract(self) -> None:
        contract = parse_contract(make_contract_dict(required_data=[
            {"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 15, "htf": None},
        ]))
        api = StrategyRuntimeHandle("S1", contract, SYMBOLS)
        rc = api.required_context()
        assert rc.timeframes == frozenset({"M15"})
        assert rc.lookback_by_timeframe == {"M15": 15}
        assert rc.symbols == SYMBOLS

    def test_required_context_deterministic(self) -> None:
        contract = parse_contract(make_contract_dict())
        api = StrategyRuntimeHandle("S1", contract, SYMBOLS)
        assert api.required_context() == api.required_context()

    @pytest.mark.parametrize("method_name,args", [
        ("detect", (None,)),
        ("generate_signal", (None,)),
        ("get_score", (None,)),
        ("can_trade", (None, None)),
        ("can_open_position", (None, None)),
        ("explain_signal", (None,)),
        ("health", ()),
    ])
    def test_unimplemented_methods_raise(self, method_name: str, args: tuple) -> None:
        contract = parse_contract(make_contract_dict())
        api = StrategyRuntimeHandle("S1", contract, SYMBOLS)
        method = getattr(api, method_name)
        with pytest.raises(StrategyApiNotImplementedError) as exc_info:
            method(*args)
        assert exc_info.value.strategy_id == "S1"
        assert exc_info.value.method == method_name

    def test_health_accepts_no_args_via_defaults(self) -> None:
        contract = parse_contract(make_contract_dict())
        api = StrategyRuntimeHandle("S1", contract, SYMBOLS)
        with pytest.raises(StrategyApiNotImplementedError):
            api.health()


class TestStrategyHandle:
    def test_carries_id_contract_and_api(self) -> None:
        contract = parse_contract(make_contract_dict(id="S7"))
        api = StrategyRuntimeHandle("S7", contract, SYMBOLS)
        handle = StrategyHandle(id="S7", contract=contract, api=api)
        assert handle.id == "S7"
        assert handle.contract is contract
        assert handle.api is api
