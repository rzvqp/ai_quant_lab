"""Shared, contract-independent context evidence -- Phase 7 Checkpoint 6. Context confidence,
multi-timeframe agreement, and volatility regime describe the CURRENT market as a whole, not any
one strategy -- the same three evidence items are attached to every strategy's reading, always
built from Market Intelligence's own already-computed snapshot fields, never recomputed here.
"""

from __future__ import annotations

from ai_trader.edge_intelligence.types import EdgeEvidenceItem, EvidenceContribution
from ai_trader.market_intelligence.types import AgreementLevel, MarketIntelligenceSnapshot, VolatilityRegime

#: IMPLEMENTATION CHOICE: below this context-confidence score, the whole context is considered too
#: unreliable to call any strategy's edge PRESENT. This is this layer's OWN disclosed threshold --
#: risk_manager is never imported here, no frozen module is touched.
_MIN_TRUSTED_CONFIDENCE = 0.5


def evaluate_context_confidence(snapshot: MarketIntelligenceSnapshot) -> EdgeEvidenceItem:
    score = snapshot.confidence.score
    if score is None:
        return EdgeEvidenceItem(
            "context_confidence", EvidenceContribution.UNKNOWN, "context confidence score is unavailable",
        )
    if score < _MIN_TRUSTED_CONFIDENCE:
        return EdgeEvidenceItem(
            "context_confidence", EvidenceContribution.CONTRADICTS,
            f"context confidence score {score:.2f} is below the {_MIN_TRUSTED_CONFIDENCE} trust threshold",
        )
    return EdgeEvidenceItem(
        "context_confidence", EvidenceContribution.SUPPORTS,
        f"context confidence score {score:.2f} meets the {_MIN_TRUSTED_CONFIDENCE} trust threshold",
    )


def evaluate_multi_timeframe_agreement(snapshot: MarketIntelligenceSnapshot) -> EdgeEvidenceItem:
    agreement = snapshot.multi_timeframe_agreement
    if agreement.level is AgreementLevel.UNKNOWN or agreement.agreement_score is None:
        return EdgeEvidenceItem(
            "multi_timeframe_agreement", EvidenceContribution.UNKNOWN,
            "no known multi-timeframe trend direction to measure agreement over",
        )
    if agreement.level is AgreementLevel.STRONG:
        return EdgeEvidenceItem(
            "multi_timeframe_agreement", EvidenceContribution.SUPPORTS,
            f"multi-timeframe agreement is STRONG (score={agreement.agreement_score:.2f})",
        )
    return EdgeEvidenceItem(
        "multi_timeframe_agreement", EvidenceContribution.NEUTRAL,
        f"multi-timeframe agreement is {agreement.level.value} (score={agreement.agreement_score:.2f}) "
        f"-- not a contradiction, just not a strong tailwind",
    )


def evaluate_volatility_regime(snapshot: MarketIntelligenceSnapshot) -> EdgeEvidenceItem:
    regime = snapshot.volatility.regime
    if regime is VolatilityRegime.UNKNOWN:
        return EdgeEvidenceItem(
            "volatility_regime", EvidenceContribution.UNKNOWN, "volatility regime is unavailable",
        )
    if regime is VolatilityRegime.NORMAL:
        return EdgeEvidenceItem(
            "volatility_regime", EvidenceContribution.SUPPORTS, "volatility regime is NORMAL",
        )
    return EdgeEvidenceItem(
        "volatility_regime", EvidenceContribution.NEUTRAL,
        f"volatility regime is {regime.value} -- informational only, not a contradiction on its own",
    )
