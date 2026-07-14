"""The Conflict Analyzer (``SCORING_ENGINE_ARCHITECTURE.md`` §5) — the only cross-signal component
(``SCORING_MODEL.md`` §4). Operates on a list of :class:`~ai_trader.scoring_engine.pipeline.PartialScore`
already narrowed to a single ``(symbol, as_of)`` group by the caller (:mod:`ai_trader.scoring_engine.
engine`) -- this module has no symbol/as_of awareness of its own, matching "the Conflict Analyzer ...
needs the whole batch" being a batch-BARRIER concern, not a cross-symbol one (ranking/conflict are
scoped within one symbol per ``SCORING_MODEL.md`` §7 / ``SCORING_SEQUENCE.md`` §3).

Only ``ACTIONABLE_STATES`` (``BUY``/``SELL``) signals participate — matching the model's own §4/§6
worked examples (both use BUY/SELL) -- WATCH-tier (``LONG_READY``/``SHORT_READY``/
``WAIT_CONFIRMATION``) and terminal (``SKIPPED``/``SCORE_INVALID``) signals always get
``conflict_penalty=0`` (they are not yet real trade commitments to conflict over).
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.scoring_engine.components import clamp
from ai_trader.scoring_engine.pipeline import PartialScore
from ai_trader.scoring_engine.types import ACTIONABLE_STATES, ReasonCode

#: SCORING_MODEL.md §4.
_OPPOSING_PENALTY = 0.5
_CORRELATED_PENALTY_PER_SIGNAL = 0.2
_CORRELATED_PENALTY_CAP = 0.4


@dataclass(frozen=True, slots=True)
class ConflictResult:
    conflict_penalty: float
    reason_codes: tuple[ReasonCode, ...]


def compute_conflict_penalties(partials: list[PartialScore]) -> list[ConflictResult]:
    """Returns one :class:`ConflictResult` per entry in ``partials``, same order/length. Uses each
    actionable signal's ``base_quality_pre_conflict`` (computed WITHOUT conflict_penalty) for the
    opposing-quality comparison -- order-independent and reproducible (``SCORING_MODEL.md`` §4)."""
    actionable_idx = [
        i for i, p in enumerate(partials) if not p.is_terminal and p.signal.state in ACTIONABLE_STATES
    ]

    results: list[ConflictResult] = []
    for i, p in enumerate(partials):
        if i not in actionable_idx:
            results.append(ConflictResult(0.0, ()))
            continue

        penalty = 0.0
        reasons: list[ReasonCode] = []

        opposing_found = any(
            partials[j].signal.direction is not p.signal.direction
            and partials[j].base_quality_pre_conflict > p.base_quality_pre_conflict
            for j in actionable_idx if j != i
        )
        if opposing_found:
            penalty += _OPPOSING_PENALTY
            reasons.append(ReasonCode(code="CONFLICT_OPPOSING", component="conflict_penalty"))

        my_class = p.evidence.contract.identity.klass if p.evidence.contract is not None else None
        correlated_count = 0
        if my_class is not None:
            for j in actionable_idx:
                if j == i:
                    continue
                other = partials[j]
                if other.signal.direction is not p.signal.direction:
                    continue
                other_class = other.evidence.contract.identity.klass if other.evidence.contract is not None else None
                if other_class == my_class:
                    correlated_count += 1
        if correlated_count > 0:
            correlated_penalty = min(_CORRELATED_PENALTY_PER_SIGNAL * correlated_count, _CORRELATED_PENALTY_CAP)
            penalty += correlated_penalty
            reasons.append(
                ReasonCode(code="CONFLICT_CORRELATED", component="conflict_penalty", detail=str(correlated_count)),
            )

        results.append(ConflictResult(clamp(penalty, 0.0, 1.0), tuple(reasons)))

    return results
