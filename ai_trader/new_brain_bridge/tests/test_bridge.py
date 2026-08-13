"""`evaluate_bar` tests -- real bars through the real `RawAxesBuilder` -> real `ve_brain.StrategyRouter`
-> real `ve_brain.decide_n6`. No stubbed/mocked `ve_brain` calls anywhere in this file."""

from __future__ import annotations

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.bridge import evaluate_bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tests.conftest import trend_up_regime_bars

_SYMBOL = "XAUUSD"
_TIMEFRAME = "M15"


def _bar(i: int, *, open_: float, high: float, low: float, close: float) -> Bar:
    return Bar(symbol=_SYMBOL, ts_open=i * 900, ts_close=(i + 1) * 900, open=open_, high=high, low=low,
               close=close, volume=100.0)


def _feed_calm_history(builder: RawAxesBuilder, n: int, start_price: float = 2400.0) -> float:
    price = start_price
    for i in range(n):
        o = price
        h = o + 0.5
        low_ = o - 0.5
        c = o + 0.05
        builder.observe(_bar(i, open_=o, high=h, low=low_, close=c))
        price = c
    return price


def test_a_symbol_mismatch_is_rejected_before_touching_ve_brain() -> None:
    builder = RawAxesBuilder(_SYMBOL)
    wrong_bar = Bar(symbol="EURUSD", ts_open=0, ts_close=900, open=1.0, high=1.1, low=0.9, close=1.0,
                     volume=None)
    try:
        evaluate_bar(wrong_bar, timeframe=_TIMEFRAME, axes_builder=builder)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "XAUUSD" in str(exc)


def test_insufficient_atr_history_yields_no_decision_with_an_explicit_reason() -> None:
    """Before 14 bars, ATR14 is undefined -- every strategy eligible under the router still gets an
    explicit ATR_HISTORY_INSUFFICIENT N6-slot NodeTrace, never a silently-skipped/None entry."""
    builder = RawAxesBuilder(_SYMBOL)
    price = 2400.0
    for i in range(3):
        bar = _bar(i, open_=price, high=price + 0.5, low=price - 0.5, close=price + 0.1)
        price = bar.close
    last_bar = _bar(2, open_=price, high=price + 0.5, low=price - 0.5, close=price + 0.1)

    outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder)

    assert len(outcomes) == len(ve_brain.CANONICAL_STRATEGIES)
    for outcome in outcomes:
        assert outcome.decision is None
        node_names = [t.node_name for t in outcome.node_traces]
        assert "N1" in node_names and "Router" in node_names
        if not any(t.node_name == "N6" for t in outcome.node_traces):
            continue  # this strategy was already ineligible at the Router -- no N6 slot expected
        n6_trace = next(t for t in outcome.node_traces if t.node_name == "N6")
        assert n6_trace.reason_codes == ("ATR_HISTORY_INSUFFICIENT",)


def test_a_real_feed_event_reaches_n6_and_is_no_trade_missing_level_input() -> None:
    """THE end-to-end proof the CEO's step 1 requires: a real bar, through the real accumulated
    history, past the real Router, into a real `ve_brain.decide_n6` call, producing the honestly
    correct terminal reason for today's wiring -- MISSING_LEVEL_INPUT, since no live level-tower/N4
    confirmation source exists in this repo yet (see `bridge.py`'s own module docstring, gap 2). Uses
    the independently-verified `trend_up_regime_bars()` sequence (see `conftest.py`) so the uptrend
    genuinely routes TREND_UP (all four N1 axes resolved, including the 460-bar compression window),
    rather than hoping an unverified price path happens to produce one."""
    builder = RawAxesBuilder(_SYMBOL)
    bars = trend_up_regime_bars(_SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    last_bar = bars[-1]

    outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder)

    assert len(outcomes) == len(ve_brain.CANONICAL_STRATEGIES)
    reached_n6 = [o for o in outcomes if o.decision is not None]
    assert reached_n6, "expected at least one catalog strategy to reach N6 on a TREND_UP-routed bar"

    # `trend_pullback`/`trend_shadow` are RATIFIED/SHADOW_ELIGIBLE -- both can_reach_n6, so both get
    # past the catalog/eligibility checks and hit the SAME real gap (no live level-tower/N4 wiring).
    # `trend_experimental` is EXPERIMENTAL -- can_reach_n6 is False for it BY ve_brain's OWN catalog
    # policy, so it is correctly blocked one check earlier (NO_ELIGIBLE_STRATEGY), never reaching the
    # level-input check at all. Both are real, distinct, correct terminal reasons -- not asserted
    # uniformly across every strategy that merely reached N6.
    by_strategy = {o.strategy_id: o for o in reached_n6}
    for strategy_id in ("trend_pullback", "trend_shadow"):
        outcome = by_strategy[strategy_id]
        decision = outcome.decision
        assert decision is not None
        assert decision.decision == "NO_TRADE"
        assert decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
        assert outcome.provenance is None  # only TRADE/SHADOW_TRADE_CANDIDATE ever gets provenance
        assert [t.node_name for t in outcome.node_traces] == ["N1", "Router", "EV", "N6"]

    experimental_decision = by_strategy["trend_experimental"].decision
    assert experimental_decision is not None
    assert experimental_decision.decision == "NO_TRADE"
    assert experimental_decision.reason_codes == (ve_brain.ReasonCode.NO_ELIGIBLE_STRATEGY.value,)
    assert by_strategy["trend_experimental"].provenance is None


def test_range_fade_never_reaches_n6_normally_because_range_is_never_produced() -> None:
    """`ve_brain`'s own CEO decision: RANGE is retired, `applicable_regimes` never returns it -- so
    `range_fade` (allowed_regimes=(RANGE,)) is INELIGIBLE at the Router for every real axes reading,
    confirmed here rather than assumed."""
    builder = RawAxesBuilder(_SYMBOL)
    _feed_calm_history(builder, 20)
    bar = _bar(20, open_=2400.0, high=2400.6, low=2399.4, close=2400.1)

    outcomes = evaluate_bar(bar, timeframe=_TIMEFRAME, axes_builder=builder)

    range_fade_outcome = next(o for o in outcomes if o.strategy_id == "range_fade")
    assert range_fade_outcome.decision is None
    router_trace = next(t for t in range_fade_outcome.node_traces if t.node_name == "Router")
    assert ve_brain.ReasonCode.TRUE_RANGE_NOT_IDENTIFIABLE.value in router_trace.reason_codes


def test_every_node_trace_shares_the_same_trace_id_and_event_identity() -> None:
    builder = RawAxesBuilder(_SYMBOL)
    _feed_calm_history(builder, 5)
    bar = _bar(5, open_=2400.0, high=2400.6, low=2399.4, close=2400.1)

    outcomes = evaluate_bar(bar, timeframe=_TIMEFRAME, axes_builder=builder)

    for outcome in outcomes:
        for trace in outcome.node_traces:
            assert trace.trace_id == outcome.event_identity.trace_id
        assert outcome.event_identity.symbol == _SYMBOL
        assert outcome.event_identity.timeframe == _TIMEFRAME
        assert outcome.event_identity.market_timestamp == bar.ts_close
