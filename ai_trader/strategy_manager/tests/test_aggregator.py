"""Tests for :mod:`ai_trader.strategy_manager.aggregator`."""

from __future__ import annotations

from ai_trader.strategy_manager.aggregator import recompute
from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_manager.required_context import compute_required_context
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.types import CompatibilityResult, Health, Lifecycle, RegistryEntry

SYMBOLS = frozenset({"XAUUSD"})


def _active_entry(id_: str, required_data: list[dict], context_ok: bool = True) -> RegistryEntry:
    contract = parse_contract(make_contract_dict(id=id_, required_data=required_data))
    rc = compute_required_context(contract, SYMBOLS)
    return RegistryEntry(
        id=id_, slug=f"{id_}_slug", source_path=f"/lib/{id_}/strategy.json", lifecycle=Lifecycle.EXPLORATORY,
        health=Health.LOADED, loaded=True, active=True, contract=contract, required_context=rc,
        compatibility=CompatibilityResult(context_ok, True, True, True, context_ok),
    )


class TestRecompute:
    def test_empty_active_set(self) -> None:
        agg, skipped = recompute((), SYMBOLS, 1, "1.0.0")
        assert agg.timeframes == frozenset()
        assert agg.symbols == frozenset()  # no contributors -> empty, not the configured universe
        assert agg.contributor_ids == ()
        assert agg.warmup_bars is None
        assert skipped == ()

    def test_single_strategy(self) -> None:
        entry = _active_entry("S1", [{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None}])
        agg, skipped = recompute((entry,), SYMBOLS, 1, "1.0.0")
        assert agg.timeframes == frozenset({"M15"})
        assert agg.required_fields_by_timeframe == {"M15": frozenset({"m_atr"})}
        assert agg.lookback_by_timeframe == {"M15": 10}
        assert agg.symbols == SYMBOLS
        assert agg.contributor_ids == ("S1",)
        assert agg.warmup_bars == 10
        assert skipped == ()

    def test_union_of_fields_and_timeframes(self) -> None:
        e1 = _active_entry("S1", [{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None}])
        e2 = _active_entry("S2", [{"timeframe": "M15", "fields": ["m_rsi"], "lookback_bars": 5, "htf": None},
                                   {"timeframe": "H1", "fields": ["h1_trend_up"], "lookback_bars": 20, "htf": None}])
        agg, _ = recompute((e1, e2), SYMBOLS, 1, "1.0.0")
        assert agg.timeframes == frozenset({"M15", "H1"})
        assert agg.required_fields_by_timeframe["M15"] == frozenset({"m_atr", "m_rsi"})
        assert agg.contributor_ids == ("S1", "S2")

    def test_lookback_max_wins(self) -> None:
        e1 = _active_entry("S1", [{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None}])
        e2 = _active_entry("S2", [{"timeframe": "M15", "fields": ["m_rsi"], "lookback_bars": 50, "htf": None}])
        agg, _ = recompute((e1, e2), SYMBOLS, 1, "1.0.0")
        assert agg.lookback_by_timeframe["M15"] == 50

    def test_warmup_max_across_strategies(self) -> None:
        e1 = _active_entry("S1", [{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None}])
        e2 = _active_entry("S2", [{"timeframe": "M15", "fields": ["m_rsi"], "lookback_bars": 75, "htf": None}])
        agg, _ = recompute((e1, e2), SYMBOLS, 1, "1.0.0")
        assert agg.warmup_bars == 75

    def test_inconsistent_entry_skipped_defensively(self) -> None:
        bad = _active_entry("S1", [{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None}], context_ok=False)
        good = _active_entry("S2", [{"timeframe": "M15", "fields": ["m_rsi"], "lookback_bars": 5, "htf": None}], context_ok=True)
        agg, skipped = recompute((bad, good), SYMBOLS, 1, "1.0.0")
        assert skipped == ("S1",)
        assert agg.contributor_ids == ("S2",)
        assert "m_atr" not in agg.required_fields_by_timeframe.get("M15", frozenset())

    def test_metadata_passed_through(self) -> None:
        entry = _active_entry("S1", [{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None}])
        agg, _ = recompute((entry,), SYMBOLS, 3, "1.2.0")
        assert agg.feature_dictionary_major == 3
        assert agg.interface_version == "1.2.0"

    def test_optional_fields_unioned(self) -> None:
        # No real contract can express optional fields today (strategy_contract.v1.schema.json has
        # no per-field "optional" marker -- see required_context.py's own docstring), but the
        # aggregation LOGIC for it is real, forward-compatible code; inject it directly on the
        # RegistryEntry's required_context to prove the union/dedup logic works when it IS present.
        entry = _active_entry("S1", [{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None}])
        assert entry.required_context is not None
        entry.required_context.optional_fields_by_timeframe = {"M15": frozenset({"m_volrank"})}
        agg, _ = recompute((entry,), SYMBOLS, 1, "1.0.0")
        assert agg.optional_fields_by_timeframe == {"M15": frozenset({"m_volrank"})}

    def test_contributor_ids_sorted(self) -> None:
        e2 = _active_entry("S2", [{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 10, "htf": None}])
        e1 = _active_entry("S1", [{"timeframe": "M15", "fields": ["m_rsi"], "lookback_bars": 5, "htf": None}])
        agg, _ = recompute((e2, e1), SYMBOLS, 1, "1.0.0")
        assert agg.contributor_ids == ("S1", "S2")
