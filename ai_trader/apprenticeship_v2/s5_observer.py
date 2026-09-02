"""Read-only S5 observation -- reuses the frozen, ratified `S5OpeningRangeBreakoutLong` class
verbatim (never reimplemented, so this can never silently drift from the real, live strategy's own
formula) in a fresh, independent instance that is never wired to any execution/risk/broker
component. Satisfies the mandate's Section 24 ("AI Trader may observe S5 occurrences and
contextual behavior") without touching the already-running `AITraderS5MT5DemoSoak` process's own
state in any way -- this module holds its own separate `S5OpeningRangeBreakoutLong()` instance.

`S5OpeningRangeBreakoutLong` itself imports no MT5/execution/broker module (confirmed by direct
inspection of `s5_opening_range_breakout.py`) -- it is a pure, stateful decision function over
`Bar`/`MarketState` value objects. This module constructs a minimal, duck-typed `MarketState`
(`CachedUpstreamContext`, a plain frozen dataclass with no `__post_init__` validation) carrying only
the two fields `S5OpeningRangeBreakoutLong.evaluate()` actually reads (`entry_price`,
`market_timestamp`) plus `symbol` -- every other field is a harmless placeholder, since `evaluate()`
never touches them (verified by reading the strategy source directly, not assumed)."""

from __future__ import annotations

import dataclasses

from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar
from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_live.dual_clock.upstream_context import CachedUpstreamContext
from ai_trader.new_brain_live.strategy_platform.s5_opening_range_breakout import S5OpeningRangeBreakoutLong
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import StrategyEvaluationInput
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis


def _to_platform_bar(bar: ReadOnlyBar) -> Bar:
    return Bar(
        symbol=bar.symbol, ts_open=bar.ts_open, ts_close=bar.ts_close, open=bar.open, high=bar.high,
        low=bar.low, close=bar.close, volume=bar.volume, is_backfilled=False,
    )


def _minimal_market_state(bar: ReadOnlyBar) -> CachedUpstreamContext:
    return CachedUpstreamContext(
        context_id=f"apprenticeship_v2:{bar.symbol}:{bar.ts_close}",
        symbol=bar.symbol, timeframe="M15", market_event_id=f"{bar.symbol}:M15:{bar.ts_close}",
        market_timestamp=bar.ts_close, n1_output_fp="apprenticeship_v2_not_used",
        regime_axes_status=(), router_bias_direction=None, confidence=1.0, axes=None,
        eligibility_decisions=(), atr=None, entry_price=bar.close,
    )


@dataclasses.dataclass
class S5Observer:
    """Owns one independent `S5OpeningRangeBreakoutLong` instance. Call `observe(bar)` for every
    causally-closed M15 bar, in order (mirrors `S5OpeningRangeBreakoutLong.observe_bar`'s own
    documented calling convention). `observe` returns the `TradeHypothesis` S5 would have generated
    on this bar, or `None` -- this hypothesis is NEVER submitted anywhere; it exists purely as an
    "S5 occurrence" episode signal for the apprenticeship's own observation ledger."""

    _strategy: S5OpeningRangeBreakoutLong = dataclasses.field(default_factory=S5OpeningRangeBreakoutLong)

    def observe(self, bar: ReadOnlyBar) -> TradeHypothesis | None:
        platform_bar = _to_platform_bar(bar)
        self._strategy.observe_bar(platform_bar)
        market_state = _minimal_market_state(bar)
        evaluation_input = StrategyEvaluationInput(market_state=market_state, tower_context=None, config={})
        return self._strategy.evaluate(evaluation_input)
