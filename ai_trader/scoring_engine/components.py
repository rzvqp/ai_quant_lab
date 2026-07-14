"""The Component Scorer (``SCORING_ENGINE_ARCHITECTURE.md`` §5): the eight per-signal, deterministic
component functions from ``SCORING_MODEL.md`` §2 (all nine components except ``conflict_penalty``,
which needs the whole batch and lives in :mod:`ai_trader.scoring_engine.conflict`).

Every function is a pure function of its declared inputs (the signal, the bound evidence, fixed
config) — no wall-clock, no randomness, matching the model's own determinism requirement (§8). Where
``SCORING_MODEL.md`` names an input but not its exact normalization (marked "IMPLEMENTATION CHOICE" in
:mod:`ai_trader.scoring_engine.config`), missing/undisclosed evidence is always treated as the WORST
case for that component — never the best — the same honesty-preserving default used throughout.
"""

from __future__ import annotations

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.evidence import BoundEvidence
from ai_trader.scoring_engine.types import ACTIONABLE_STATES, READY_STATES, ReasonCode
from ai_trader.signal_engine.types import Direction, SignalState, StrategySignal
from ai_trader.strategy_manager.contract import Evidence as ContractEvidence, Regime, TestStatus
from ai_trader.strategy_manager.types import Lifecycle

#: ``SCORING_MODEL.md`` §3 ``maturity_prior`` table — keyed by the Strategy Manager's OWN operational
#: ``Lifecycle`` (see :mod:`ai_trader.scoring_engine.evidence`'s module docstring for why). ``DISABLED``
#: is not named in the model's table; extended to 0.0 alongside INVALID/NOT_IMPLEMENTED/RETIRED as the
#: conservative, honesty-preserving default for any lifecycle the model doesn't explicitly score.
MATURITY_PRIOR: dict[Lifecycle, float] = {
    Lifecycle.EXPERIMENTAL: 0.15,
    Lifecycle.EXPLORATORY: 0.30,
    Lifecycle.CANDIDATE: 0.45,
    Lifecycle.VALIDATED: 0.75,
    Lifecycle.PROMOTED: 1.00,
    Lifecycle.INVALID: 0.0,
    Lifecycle.NOT_IMPLEMENTED: 0.0,
    Lifecycle.RETIRED: 0.0,
    Lifecycle.DISABLED: 0.0,
}

_DATA_QUALITY_VALUE: dict[DataQualityLevel, float] = {
    DataQualityLevel.OK: 1.0,
    DataQualityLevel.DEGRADED: 0.6,
    DataQualityLevel.STALE: 0.3,
    DataQualityLevel.INSUFFICIENT: 0.0,
}


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _oos_factor(oos_expectancy_r: float | None) -> float:
    """``SCORING_MODEL.md`` §3: ``> 0 -> 1.0 ; == 0 or null -> 0.6 ; < 0 -> 0.4``."""
    if oos_expectancy_r is None or oos_expectancy_r == 0:
        return 0.6
    return 1.0 if oos_expectancy_r > 0 else 0.4


def _validation_bonus(ev: ContractEvidence) -> float:
    """``SCORING_MODEL.md`` §3: +0.1 per PASSing gate among matched-null/walk-forward/global-FDR."""
    bonus = 0.0
    if ev.matched_null_status.status is TestStatus.PASS:
        bonus += 0.1
    if ev.walk_forward_status is TestStatus.PASS:
        bonus += 0.1
    if ev.global_fdr_status is TestStatus.PASS:
        bonus += 0.1
    return bonus


def signal_strength(signal: StrategySignal) -> float:
    """Component 1: used directly -- ``StrategySignal.signal_strength`` is already normalized [0,1]
    by the Signal Engine's own schema validation. Defensively re-clamped."""
    return clamp(signal.signal_strength, 0.0, 1.0)


def historical_confidence(evidence: BoundEvidence) -> tuple[float, tuple[ReasonCode, ...]]:
    """Component 2 (the honesty anchor, ``SCORING_MODEL.md`` §3)."""
    if evidence.contract is None or evidence.lifecycle is None:
        return 0.0, (ReasonCode(code="EVIDENCE_MISSING", component="historical_confidence"),)

    maturity_prior = MATURITY_PRIOR.get(evidence.lifecycle, 0.0)
    if maturity_prior == 0.0:
        return 0.0, (
            ReasonCode(code="MATURITY_ZERO_PRIOR", component="historical_confidence", detail=evidence.lifecycle.value),
        )

    ev = evidence.contract.evidence
    oos_expectancy = ev.oos_metrics.expectancy_R
    oos_f = _oos_factor(oos_expectancy)
    bonus = _validation_bonus(ev)
    raw = maturity_prior * oos_f * (0.8 + bonus)
    # "capped so the product <= maturity_prior tier" (§3) -- an honesty ceiling on top of the
    # ordinary [0,1] clamp: no combination of OOS/validation evidence can push a strategy's score
    # above its OWN declared maturity tier.
    value = clamp(min(raw, maturity_prior), 0.0, 1.0)

    reasons: tuple[ReasonCode, ...] = ()
    if oos_expectancy is not None and oos_expectancy < 0:
        reasons = (ReasonCode(code="NEGATIVE_OOS_CAP", component="historical_confidence", detail=str(oos_expectancy)),)
    elif oos_f < 1.0:
        # oos_expectancy is None or == 0 -- genuinely undisclosed/neutral, NOT negative. A separate
        # code from NEGATIVE_OOS_CAP: reusing that name here would misreport "no OOS evidence yet" as
        # "OOS evidence says this strategy loses money", two very different, non-interchangeable facts.
        reasons = (ReasonCode(code="OOS_UNKNOWN", component="historical_confidence"),)
    return value, reasons


def market_alignment(signal: StrategySignal) -> float:
    """Component 3. IMPLEMENTATION CHOICE (``SCORING_MODEL.md`` §2 row 3 names "the context's
    short-term price/momentum tag" without naming a field): ``StrategySignal.regime`` is the only
    momentum-like tag published on the signal -- TREND_UP/TREND_DOWN are treated as directional,
    everything else (RANGE/HIGH_VOL/LOW_VOL/SESSION_OPEN/ANY/absent) as neutral."""
    regime = signal.regime
    direction = signal.direction
    if regime is None or direction is Direction.NONE:
        return 0.5
    if regime is Regime.TREND_UP:
        return 1.0 if direction is Direction.LONG else 0.0
    if regime is Regime.TREND_DOWN:
        return 1.0 if direction is Direction.SHORT else 0.0
    return 0.5


def regime_alignment(
    signal: StrategySignal, evidence: BoundEvidence,
) -> tuple[float, tuple[ReasonCode, ...]]:
    """Component 4 (``SCORING_MODEL.md`` §2 row 4, verbatim: "1.0 if current regime in contract
    applicable; 0.5 if ANY/unknown; 0.0 if in avoid"). ``avoid`` is checked before ``applicable`` --
    an explicit exclusion wins over a broad "works in any regime" declaration (IMPLEMENTATION CHOICE:
    the model does not state this precedence explicitly, but ``avoid`` existing as a distinct list
    from ``applicable`` only makes sense as an override).

    A contract declaring ``applicable=(ANY,)`` is the "ANY" case the spec's own "0.5 if ANY" clause
    names -- NOT a specific regime match. Only a genuine, specific membership (the signal's regime
    literally present in ``applicable``) earns 1.0; a contract that merely claims "works everywhere"
    provides no real directional edge for THIS regime and stays neutral, matching the honesty-
    preserving spirit of the rest of the model (an unrestricted claim is not the same as a verified,
    specific match).
    """
    regime = signal.regime
    if regime is None or evidence.contract is None:
        return 0.5, ()
    spec = evidence.contract.semantics.market_regime
    if regime in spec.avoid:
        return 0.0, (ReasonCode(code="REGIME_AVOID", component="regime_alignment", detail=regime.value),)
    if regime in spec.applicable:
        return 1.0, (ReasonCode(code="REGIME_MATCH", component="regime_alignment", detail=regime.value),)
    return 0.5, ()


_FULLY_CONFIRMED = (ReasonCode(code="FULLY_CONFIRMED", component="confirmation_quality"),)


def confirmation_quality(signal: StrategySignal) -> tuple[float, tuple[ReasonCode, ...]]:
    """Component 5: ``met / (met+pending)``; no confirmations required -> 1.0. Every path that
    resolves to 1.0 (including "nothing was required at all") reports ``FULLY_CONFIRMED`` -- a single
    consistent rule ("value==1.0 implies this reason code"), not two early-return paths that happen
    to share a value but disagree on disclosing it."""
    confirmations = signal.explanation.confirmations
    if not confirmations.required:
        return 1.0, _FULLY_CONFIRMED
    met, pending = len(confirmations.met), len(confirmations.pending)
    denom = met + pending
    if denom == 0:
        return 1.0, _FULLY_CONFIRMED
    value = met / denom
    reasons = _FULLY_CONFIRMED if value >= 1.0 else ()
    return value, reasons


def data_quality_component(signal: StrategySignal) -> tuple[float, tuple[ReasonCode, ...]]:
    """Component 6: OK->1.0, DEGRADED->0.6, STALE->0.3, INSUFFICIENT->0.0."""
    dq = signal.context_ref.data_quality
    value = _DATA_QUALITY_VALUE[dq]
    reasons = (
        (ReasonCode(code="DATA_DEGRADED", component="data_quality", detail=dq.value),)
        if dq is not DataQualityLevel.OK else ()
    )
    return value, reasons


def execution_readiness(signal: StrategySignal) -> tuple[float, tuple[ReasonCode, ...]]:
    """Component 7: BUY/SELL with valid entry/stop/target -> 1.0; LONG_READY/SHORT_READY -> 0.6;
    WAIT_CONFIRMATION -> 0.3; non-actionable -> 0.0."""
    state = signal.state
    if state in ACTIONABLE_STATES:
        tp = signal.trade_params
        if tp is not None and tp.entry is not None and tp.stop is not None and tp.target is not None:
            return 1.0, ()
        # Defensive: pipeline.py's own generate_signal() contract only requires 'present'/'direction'
        # -- entry/stop/target are not schema-enforced, so a real strategy could omit them even while
        # confirmed+present. Never fabricate the missing prices; just discount readiness and disclose.
        return 0.6, (ReasonCode(code="PARTIAL_TRADE_PARAMS", component="execution_readiness"),)
    if state in READY_STATES:
        return 0.6, ()
    if state is SignalState.WAIT_CONFIRMATION:
        return 0.3, ()
    return 0.0, ()


def risk_penalty(evidence: BoundEvidence, config: ScoringConfig) -> float:
    """Component 8 (a quality discount, NOT position risk -- ``SCORING_MODEL.md`` §1.3/§2 row 8).

    A contract that exists but omits a SPECIFIC field (drawdown/top1_share/n) contributes the
    WORST-case value for that one field -- an undisclosed risk metric is not evidence of safety.

    A WHOLLY missing contract (``evidence.contract is None``, e.g. the strategy is unknown to the
    Strategy Manager, or no Strategy Manager was configured at all) is a DIFFERENT situation and
    deliberately NOT treated the same way: that is an engine-operational condition, not a fact about
    the strategy's own historical risk, and ``historical_confidence`` already carries the
    spec-mandated honesty penalty for it (``EVIDENCE_MISSING`` -> 0). Forcing ``risk_penalty`` to
    1.0 as well would make ``penalty_factor = (1-risk_penalty)*(1-conflict_penalty)`` collapse to
    zero and silently force ``total_score=0`` for EVERY evidence-missing signal regardless of how
    strong the live signal itself is -- double-punishing the same underlying fact through two
    different components and conflating "the Strategy Manager wasn't reachable" with "this strategy
    is known to be risky". A neutral 0.5 here (matching this module's own market_alignment/
    regime_alignment "unknown -> neutral" convention) lets historical_confidence alone carry that
    signal, as the model's own §3 "honesty anchor" language intends.
    """
    if evidence.contract is None:
        return 0.5
    hist = evidence.contract.evidence.historical_metrics
    th = config.risk_penalty_thresholds
    w = config.risk_penalty_weights

    dd = hist.drawdown_R
    dd_norm = 1.0 if dd is None else clamp(dd / th.drawdown_norm_cap_r, 0.0, 1.0)

    top1 = hist.top1_share
    fragile = 1.0 if top1 is None else (1.0 if top1 > th.fragile_top1_share_threshold else 0.0)

    n = hist.n
    small_n = 1.0 if n is None else clamp(1.0 - (n / th.small_sample_full_n), 0.0, 1.0)

    return clamp(w.drawdown * dd_norm + w.fragile * fragile + w.small_sample * small_n, 0.0, 1.0)
