"""Per-signal pipeline stages (``SCORING_STATE_MACHINE.md`` §B): ``RECEIVED`` -> ``FILTERED`` ->
``EVIDENCE_BOUND`` -> ``COMPONENTS_SCORED``. The remaining stages (``CONFLICT_EVALUATED``,
``AGGREGATED``, ``RANKED``, ``REASONED``, ``VALIDATED``, ``EMITTED``) are batch-wide and live in
:mod:`ai_trader.scoring_engine.conflict`, :mod:`ai_trader.scoring_engine.aggregator`, and
:mod:`ai_trader.scoring_engine.ranker` — this module produces one :class:`PartialScore` per signal,
ready for those batch barriers.

**Literal to the state machine**: a non-actionable signal (``NEED_CONTEXT``/``BLOCKED``/``INVALID``/
``NO_SIGNAL``) is routed straight to ``SKIPPED`` at the ``FILTERED`` stage -- ``EVIDENCE_BOUND`` and
``COMPONENTS_SCORED`` never run for it (the state-machine diagram shows this branch happening BEFORE
those stages, not after). Its component scores are therefore genuinely never-computed defaults
(``ComponentScores()``, all zero) and ``base_quality``/``penalty_factor`` stay ``None`` (both are
optional in ``SCORING_SCHEMA.json`` precisely for this kind of early-exit terminal), not a coincidence
of the formula happening to evaluate to zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.scoring_engine import components
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.evidence import BoundEvidence, EvidenceCache, StrategyManagerLike, bind_evidence
from ai_trader.scoring_engine.types import NON_ACTIONABLE_STATES, ComponentScores, ReasonCode
from ai_trader.signal_engine.types import StrategySignal


@dataclass(slots=True)
class PartialScore:
    """One signal's state after Component Scoring, awaiting the batch-wide Conflict/Aggregation/
    Ranking stages. ``terminal_state``/``terminal_reasons`` are set (and every other field left at
    its default) for a signal that short-circuited to ``SKIPPED`` or ``SCORE_INVALID`` -- callers
    check ``is_terminal`` first."""

    signal: StrategySignal
    evidence: BoundEvidence = field(default_factory=lambda: BoundEvidence(None, None))
    components: ComponentScores = field(default_factory=ComponentScores)
    #: The weighted sum of the seven QUALITY components only (``SCORING_MODEL.md`` §5's
    #: ``base_quality``), computed WITHOUT conflict_penalty -- the "provisional quality" the Conflict
    #: Analyzer compares across the batch (§4: "order-independent and reproducible").
    base_quality_pre_conflict: float = 0.0
    reason_codes: tuple[ReasonCode, ...] = ()
    terminal_state: str | None = None  # "SKIPPED" | "SCORE_INVALID" | None
    terminal_recommendation: str | None = None  # "SKIP" | "INVALID" | None

    @property
    def is_terminal(self) -> bool:
        return self.terminal_state is not None


def _is_malformed(signal: StrategySignal) -> bool:
    """A defensive sanity boundary against a caller passing something that isn't a genuinely valid,
    Signal-Engine-produced ``StrategySignal`` (architecture §7: "signal fails to parse / schema
    mismatch"). A signal that reached here as an actual ``StrategySignal`` instance was already
    schema-validated by the Signal Engine that produced it -- this only guards against a
    hand-constructed or corrupted object slipping past that guarantee.

    Only checks structural integrity (is it really a ``StrategySignal``, and are its required nested
    objects present) -- NOT specific field values like ``as_of``/``strategy_id`` being "truthy".
    Regression note: an earlier version rejected ``as_of == 0`` here, but ``0`` is the Signal Engine's
    OWN documented sentinel for "context missing meta.as_of" (its ``_missing_as_of_signal``
    fallback), always paired with ``state=INVALID`` -- a legitimately-typed, well-formed signal
    reporting an upstream failure, not a parsing failure of THIS engine's input. Such a signal is
    correctly handled by the ordinary non-actionable-state routing below (-> SKIPPED), not rejected
    here as if it were garbage. Any OTHER kind of semantically-broken-but-well-typed value (an empty
    ``strategy_id``, etc.) is instead caught by schema validation + safe reassembly downstream
    (``ai_trader.scoring_engine.engine._finalize_one``), which never trusts an unvalidated field
    straight through to the emitted score.
    """
    if not isinstance(signal, StrategySignal):
        return True
    return signal.context_ref is None or signal.explanation is None


def score_signal_stage1(
    signal: StrategySignal, manager: StrategyManagerLike | None, cache: EvidenceCache, config: ScoringConfig,
) -> PartialScore:
    """Run Intake & Filter, Evidence Binding, and Component Scoring for one signal. Never raises: any
    unexpected condition degrades to ``SCORE_INVALID`` (fail-safe, ``SCORING_API.md`` "failure model").
    """
    if _is_malformed(signal):
        return PartialScore(signal=signal, terminal_state="SCORE_INVALID", terminal_recommendation="INVALID")

    if signal.state in NON_ACTIONABLE_STATES:
        return PartialScore(signal=signal, terminal_state="SKIPPED", terminal_recommendation="SKIP")

    evidence = bind_evidence(signal.strategy_id, manager, cache)

    hist_conf, hist_reasons = components.historical_confidence(evidence)
    regime_align, regime_reasons = components.regime_alignment(signal, evidence)
    confirm_q, confirm_reasons = components.confirmation_quality(signal)
    dq, dq_reasons = components.data_quality_component(signal)
    exec_ready, exec_reasons = components.execution_readiness(signal)

    sig_strength = components.signal_strength(signal)
    market_align = components.market_alignment(signal)
    risk_pen = components.risk_penalty(evidence, config)

    w = config.weights
    base_quality = (
        w.signal_strength * sig_strength + w.historical_confidence * hist_conf
        + w.market_alignment * market_align + w.regime_alignment * regime_align
        + w.confirmation_quality * confirm_q + w.data_quality * dq
        + w.execution_readiness * exec_ready
    )

    comp = ComponentScores(
        signal_strength=sig_strength, historical_confidence=hist_conf, market_alignment=market_align,
        regime_alignment=regime_align, confirmation_quality=confirm_q, data_quality=dq,
        execution_readiness=exec_ready, risk_penalty=risk_pen, conflict_penalty=0.0,
    )
    reasons = hist_reasons + regime_reasons + confirm_reasons + dq_reasons + exec_reasons

    return PartialScore(
        signal=signal, evidence=evidence, components=comp,
        base_quality_pre_conflict=base_quality, reason_codes=reasons,
    )
