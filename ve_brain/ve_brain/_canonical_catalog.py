"""CATALOGUL CANONIC INTERN — sursa de adevăr a definițiilor de strategie, ÎNCORPORATĂ în artefactul VE.

Principiul (verdict Red Team, a 6-a suprafață): AI Trader NU poate defini pentru o strategie canonică
`strategy_family` · `allowed_regimes` · `requires_true_range` · `validation_status` · `strategy_policy_fingerprint`.
Consumatorul poate CERE încărcarea unei strategii aprobate; nu poate decide conținutul ei.

Definițiile de mai jos sunt LITERALI Python încorporați (fără încărcare din fișier/mediu/rețea — nicio sursă
controlată de consumator). Ele sunt aprobate de VE, versionate, și sigilate de `build_sealed_catalog()`. Statutul
reflectă mecanismul contractului (can_reach_n6 / can_execute_real), gardat suplimentar de BROKER_ORDER_SUBMISSION.
"""

from __future__ import annotations

from .regime_routing import SealedRegistry, SemanticRegime, StrategyContract, catalog_hash
from .strategy_contract import ValidationStatus

CANONICAL_CATALOG_VERSION: str = "ve-canonical-catalog-v1"
_MC: str = "canonical-evaluator-v2.7.66-A2"


def _canon(strategy_id: str, *, family: str, allowed: tuple[SemanticRegime, ...],
           status: ValidationStatus, arming: tuple[SemanticRegime, ...] = ()) -> StrategyContract:
    return StrategyContract(
        strategy_id=strategy_id, strategy_family=family, allowed_regimes=allowed, allowed_directions=("LONG",),
        arming_regimes=arming, trigger_transition=None, minimum_regime_confidence=0.0, required_N2_bias=None,
        required_N3_map=True, required_N4_confirmation=None, entry_rule="e", invalidation_rule="i", exit_rule="x",
        holding_window=10, validation_status=status, strategy_version="v1", measurement_contract_version=_MC)


# Setul APROBAT — fixat de VE. range_fade rămâne în catalog cu definiția SA ADEVĂRATĂ (allowed=RANGE) tocmai ca N6
# să-l poată bloca; consumatorul nu poate redefini range_fade drept trend.
CANONICAL_STRATEGIES: tuple[StrategyContract, ...] = (
    _canon("trend_pullback", family="TREND_PULLBACK", allowed=(SemanticRegime.TREND_UP,),
           status=ValidationStatus.RATIFIED),
    _canon("range_fade", family="RANGE_MEAN_REVERSION", allowed=(SemanticRegime.RANGE,),
           status=ValidationStatus.RATIFIED),
    _canon("trend_shadow", family="TREND_PULLBACK", allowed=(SemanticRegime.TREND_UP,),
           status=ValidationStatus.SHADOW_ELIGIBLE),
    _canon("trend_experimental", family="TREND_PULLBACK", allowed=(SemanticRegime.TREND_UP,),
           status=ValidationStatus.EXPERIMENTAL),
)

# amprenta de integritate a catalogului aprobat (constantă încorporată; N6 verifică registrul contra ei)
CANONICAL_CATALOG_HASH: str = catalog_hash(CANONICAL_STRATEGIES)


def build_sealed_catalog() -> SealedRegistry:
    """Construiește registrul SIGILAT din catalogul încorporat. Apelat o dată, la importul lui n6."""
    return SealedRegistry.build(CANONICAL_STRATEGIES, CANONICAL_CATALOG_VERSION)
