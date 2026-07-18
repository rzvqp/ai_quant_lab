"""Market Intelligence -- the single public entry point (Phase 7 Checkpoint 5). A pure, stateless,
read-only function: given a ``MarketContext`` (`market_scanner`'s own already-computed output for one
symbol/bar), produce a complete, immutable
:class:`~ai_trader.market_intelligence.types.MarketIntelligenceSnapshot`.

**Deliberately not wired into any live per-bar loop** (harness.py, competitive OR shadow) -- exactly
like Shadow Evidence's own Checkpoint 4 Research layer, this is a standalone library callable by
anyone holding a ``MarketContext`` (a test, a research script, or -- not part of this checkpoint -- a
future Edge Intelligence/Decision AI component). Calling it changes nothing about how the market
context was produced or how any other module behaves; it never submits an order, never scores an
opportunity, never touches Signal Engine/Scoring Engine/Risk Manager/Execution Engine/Shadow Evidence
in any way.

**Extension point**: adding a new Market Intelligence dimension means adding one new analyzer module
(the same shape as ``trend.py``/``volatility.py``/etc.: a pure function ``MarketContext -> SomeReading``)
and one new field on ``MarketIntelligenceSnapshot`` -- no existing analyzer or this orchestrator's own
control flow needs to change.
"""

from __future__ import annotations

from ai_trader.market_intelligence.agreement import analyze_multi_timeframe_agreement
from ai_trader.market_intelligence.confidence import compute_context_confidence
from ai_trader.market_intelligence.expansion import analyze_expansion
from ai_trader.market_intelligence.liquidity import analyze_liquidity
from ai_trader.market_intelligence.momentum import analyze_momentum
from ai_trader.market_intelligence.session_behavior import analyze_session
from ai_trader.market_intelligence.structure import analyze_structure
from ai_trader.market_intelligence.trend import analyze_trend
from ai_trader.market_intelligence.types import MarketIntelligenceSnapshot
from ai_trader.market_intelligence.volatility import analyze_volatility
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext


def build_market_intelligence(context: MarketContext) -> MarketIntelligenceSnapshot:
    """The one public entry point. Deterministic: the identical ``context`` always produces a
    byte-identical (field-for-field equal) snapshot -- every analyzer it calls is itself a pure
    function of ``context`` alone, with no hidden state anywhere in this package."""
    trend = analyze_trend(context)
    volatility = analyze_volatility(context)
    agreement = analyze_multi_timeframe_agreement(trend)
    confidence = compute_context_confidence(context_access.data_quality_level(context), agreement, volatility)

    return MarketIntelligenceSnapshot(
        symbol=context_access.symbol(context),
        as_of=context_access.as_of(context),
        trend=trend,
        momentum=analyze_momentum(context),
        structure=analyze_structure(context),
        volatility=volatility,
        liquidity=analyze_liquidity(context),
        expansion=analyze_expansion(context),
        session=analyze_session(context),
        multi_timeframe_agreement=agreement,
        confidence=confidence,
    )
