"""Tests for :mod:`ai_trader.strategy_manager.required_context`."""

from __future__ import annotations

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.required_context import compute_required_context
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict

SYMBOLS = frozenset({"XAUUSD"})


class TestComputeRequiredContext:
    def test_single_timeframe(self) -> None:
        contract = parse_contract(make_contract_dict(required_data=[
            {"timeframe": "M15", "fields": ["m_atr", "m_rsi"], "lookback_bars": 20, "htf": None},
        ]))
        rc = compute_required_context(contract, SYMBOLS)
        assert rc.timeframes == frozenset({"M15"})
        assert rc.fields_by_timeframe == {"M15": frozenset({"m_atr", "m_rsi"})}
        assert rc.lookback_by_timeframe == {"M15": 20}
        assert rc.symbols == SYMBOLS
        assert rc.warmup_bars == 20
        assert rc.optional_fields_by_timeframe == {}

    def test_multiple_timeframes_and_htf(self) -> None:
        contract = parse_contract(make_contract_dict(required_data=[
            {"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 20, "htf": ["H1", "D1"]},
            {"timeframe": "H1", "fields": ["h1_trend_up"], "lookback_bars": 5, "htf": None},
        ]))
        rc = compute_required_context(contract, SYMBOLS)
        assert rc.timeframes == frozenset({"M15", "H1"})
        assert rc.htf == frozenset({"H1", "D1"})
        assert rc.warmup_bars == 20  # max lookback

    def test_duplicate_timeframe_entries_are_merged_not_collapsed(self) -> None:
        # The schema does not require distinct timeframes across required_data entries -- a second
        # entry for the same timeframe must union fields and max-win lookback, not silently replace
        # the first (compatibility.check() already validates every entry individually without
        # collapsing; required_context() must not under-report what compatibility already verified).
        contract = parse_contract(make_contract_dict(required_data=[
            {"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None},
            {"timeframe": "M15", "fields": ["m_rsi"], "lookback_bars": 30, "htf": ["H1"]},
        ]))
        rc = compute_required_context(contract, SYMBOLS)
        assert rc.timeframes == frozenset({"M15"})
        assert rc.fields_by_timeframe == {"M15": frozenset({"m_atr", "m_rsi"})}
        assert rc.lookback_by_timeframe == {"M15": 30}
        assert rc.htf == frozenset({"H1"})
        assert rc.warmup_bars == 30

    def test_no_required_data_gives_empty_context(self) -> None:
        contract = parse_contract(make_contract_dict(required_data=[]))
        rc = compute_required_context(contract, SYMBOLS)
        assert rc.timeframes == frozenset()
        assert rc.warmup_bars == 0

    def test_symbols_come_from_manager_not_contract(self) -> None:
        contract = parse_contract(make_contract_dict())
        rc = compute_required_context(contract, frozenset({"EURUSD", "GBPUSD"}))
        assert rc.symbols == frozenset({"EURUSD", "GBPUSD"})
