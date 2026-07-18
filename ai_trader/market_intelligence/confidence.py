"""Context confidence -- Phase 7 Checkpoint 5. A simple, disclosed, fully explainable composite of
THREE independently-inspectable components -- deliberately NOT a percentile-rank/PCA-derived score
(that is Strategy Health's own separate, unselected scoring methodology,
`PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md` §11, untouched anywhere in this package).

**The formula (disclosed in full, IMPLEMENTATION CHOICE, never tuned against results)**:
``score = mean(data_quality_component, agreement_component, 1 - volatility_penalty)``
where ``data_quality_component`` is 1.0 if data quality is OK else 0.0, ``agreement_component`` is the
multi-timeframe agreement score verbatim (0..1), and ``volatility_penalty`` is 0.5 in an EXTREME
volatility regime (readings are inherently less reliable in chaotic conditions) and 0.0 otherwise. Each
component is carried on :class:`~ai_trader.market_intelligence.types.ContextConfidence` individually,
so nothing about "why" a confidence score is what it is is ever hidden inside one opaque number.
"""

from __future__ import annotations

from ai_trader.market_intelligence.types import ContextConfidence, MultiTimeframeAgreement, VolatilityReading, VolatilityRegime

#: IMPLEMENTATION CHOICE: an EXTREME volatility regime halves the "reliability" contribution to
#: confidence -- a documented, conservative penalty, never tuned against results.
_EXTREME_VOLATILITY_PENALTY = 0.5


def compute_context_confidence(
    data_quality_level: str, agreement: MultiTimeframeAgreement, volatility: VolatilityReading,
) -> ContextConfidence:
    data_quality_ok = data_quality_level == "OK"
    volatility_penalty = _EXTREME_VOLATILITY_PENALTY if volatility.regime is VolatilityRegime.EXTREME else 0.0

    components = [1.0 if data_quality_ok else 0.0, 1.0 - volatility_penalty]
    if agreement.agreement_score is not None:
        components.append(agreement.agreement_score)
    score = sum(components) / len(components)

    return ContextConfidence(
        score=score, data_quality_ok=data_quality_ok,
        agreement_component=agreement.agreement_score, volatility_penalty=volatility_penalty,
    )
