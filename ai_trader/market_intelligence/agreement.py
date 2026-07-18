"""Multi-timeframe agreement -- Phase 7 Checkpoint 5. A pure function over already-computed
:class:`~ai_trader.market_intelligence.types.TrendReading` objects (never recomputes anything) --
how many of the timeframes with a KNOWN direction agree with the majority.
"""

from __future__ import annotations

from ai_trader.market_intelligence.types import AgreementLevel, MultiTimeframeAgreement, TrendDirection, TrendReading

#: IMPLEMENTATION CHOICE: purely descriptive bands (never tuned against results). STRONG requires
#: every known timeframe to agree; WEAK is anything at or below a 50/50 split.
_STRONG_THRESHOLD = 0.99  # effectively "all known timeframes agree" (float-safe >= 1.0 check)
_MODERATE_THRESHOLD = 0.5


def _level_for(score: float) -> AgreementLevel:
    # No None branch: the one caller below only invokes this once `known` is confirmed non-empty and
    # `score` is a real computed float -- the `agreement_score=None` case is handled entirely by the
    # early return, never by this helper.
    if score >= _STRONG_THRESHOLD:
        return AgreementLevel.STRONG
    if score > _MODERATE_THRESHOLD:
        return AgreementLevel.MODERATE
    return AgreementLevel.WEAK


def analyze_multi_timeframe_agreement(trend_readings: dict[str, TrendReading]) -> MultiTimeframeAgreement:
    directions = {timeframe: reading.direction for timeframe, reading in trend_readings.items()}
    # FLAT/UNKNOWN are not a "known direction" for agreement purposes -- only UP/DOWN count.
    known = [d for d in directions.values() if d in (TrendDirection.UP, TrendDirection.DOWN)]
    if not known:
        return MultiTimeframeAgreement(directions_by_timeframe=directions, agreement_score=None, level=AgreementLevel.UNKNOWN)

    n_up = sum(1 for d in known if d is TrendDirection.UP)
    n_down = len(known) - n_up
    score = max(n_up, n_down) / len(known)
    return MultiTimeframeAgreement(
        directions_by_timeframe=directions, agreement_score=score, level=_level_for(score),
    )
