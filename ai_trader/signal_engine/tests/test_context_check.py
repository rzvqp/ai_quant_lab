"""Tests for :mod:`ai_trader.signal_engine.context_check`."""

from __future__ import annotations

from ai_trader.signal_engine.context_check import missing_context_items
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context
from ai_trader.strategy_manager.types import RequiredContext


def _required(
    timeframes: frozenset[str] = frozenset({"M15"}),
    fields: dict[str, frozenset[str]] | None = None,
    lookback: dict[str, int] | None = None,
) -> RequiredContext:
    return RequiredContext(
        timeframes=timeframes,
        fields_by_timeframe=fields if fields is not None else {"M15": frozenset({"m_atr"})},
        lookback_by_timeframe=lookback if lookback is not None else {"M15": 5},
        symbols=frozenset({"XAUUSD"}),
    )


class TestMissingContextItems:
    def test_fully_satisfied_context_reports_nothing_missing(self) -> None:
        context = make_context(features={"M15": {"m_atr": 1.23}}, bars_per_timeframe={"M15": 10})
        assert missing_context_items(context, _required()) == []

    def test_absent_timeframe_is_reported_by_name(self) -> None:
        context = make_context(features={"H1": {"m_atr": 1.23}}, bars_per_timeframe={"H1": 10})
        missing = missing_context_items(context, _required(timeframes=frozenset({"M15"})))
        assert missing == ["M15"]

    def test_missing_field_is_reported_as_timeframe_dot_field(self) -> None:
        context = make_context(features={"M15": {"m_atr": None}}, bars_per_timeframe={"M15": 10})
        missing = missing_context_items(context, _required())
        assert missing == ["M15.m_atr"]

    def test_field_absent_from_features_dict_entirely_is_reported(self) -> None:
        context = make_context(features={"M15": {}}, bars_per_timeframe={"M15": 10})
        missing = missing_context_items(context, _required())
        assert missing == ["M15.m_atr"]

    def test_insufficient_bars_is_reported_as_warmup(self) -> None:
        context = make_context(features={"M15": {"m_atr": 1.23}}, bars_per_timeframe={"M15": 2})
        missing = missing_context_items(context, _required(lookback={"M15": 5}))
        assert missing == ["M15.warmup"]

    def test_zero_lookback_never_triggers_warmup(self) -> None:
        context = make_context(features={"M15": {"m_atr": 1.23}}, bars_per_timeframe={"M15": 0})
        missing = missing_context_items(context, _required(lookback={"M15": 0}))
        assert missing == []

    def test_multiple_missing_items_all_reported_in_sorted_order(self) -> None:
        context = make_context(features={"M15": {}}, bars_per_timeframe={"M15": 0})
        required = _required(
            timeframes=frozenset({"M15", "H1"}),
            fields={"M15": frozenset({"m_atr", "m_rsi"})},
            lookback={"M15": 5},
        )
        missing = missing_context_items(context, required)
        assert missing == ["H1", "M15.m_atr", "M15.m_rsi", "M15.warmup"]

    def test_ignores_scanners_own_aggregate_sufficiency_field(self) -> None:
        """The module's own contract: it must judge sufficiency from THIS strategy's requirement
        against actual context content, never by trusting context["sufficiency"] (which reflects the
        union of every active strategy's requirement, not this one strategy's)."""
        context = make_context(features={"M15": {"m_atr": 1.23}}, bars_per_timeframe={"M15": 10})
        context["sufficiency"] = {"overall": "INSUFFICIENT", "missing_fields": ["something else"], "missing_timeframes": None, "note": None}
        assert missing_context_items(context, _required()) == []

    def test_deterministic_across_calls(self) -> None:
        context = make_context(features={"M15": {}}, bars_per_timeframe={"M15": 0})
        required = _required(timeframes=frozenset({"M15", "H1"}))
        assert missing_context_items(context, required) == missing_context_items(context, required)
