"""Data structures for the Decision Intelligence layer -- Phase 7 Checkpoint 7. Determines WHICH of
the currently-PRESENT edges (if any) deserves execution -- never a trade, never an order, never a risk-
sizing decision. Every verdict is explainable via a tuple of disclosed evidence strings, each naming an
actual observed value from a prior layer or an already-declared contract field -- never a hidden score,
never a probabilistic guess.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DecisionOutcome(str, Enum):
    """Whether a PRESENT edge is recommended as a candidate for execution. REJECT here is not the same
    as Edge Intelligence's own ABSENT/POSSIBLE -- it means the edge IS currently present in the market
    but fails a Decision-level eligibility gate (e.g. a RETIRED contract, no positive research
    confidence)."""

    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


@dataclass(frozen=True)
class ResearchStats:
    """A minimal, LOCAL echo of the research statistics a caller may already have computed elsewhere
    (e.g. via :func:`ai_trader.shadow_evidence.research.all_research_summaries`) -- deliberately NOT the
    :class:`~ai_trader.shadow_evidence.types.StrategyResearchSummary` type itself, and this package never
    imports anything from :mod:`ai_trader.shadow_evidence` (the CEO's own "completely independent from
    Shadow Evidence" directive). A caller that already has richer statistics adapts them into this
    shape; Decision Intelligence never computes or invents a number that was not supplied."""

    n_trades: int
    win_rate: float | None
    expectancy_r: float | None
    sharpe_ratio: float | None

    def __post_init__(self) -> None:
        if self.n_trades < 0:
            raise ValueError(f"n_trades must be >= 0, got {self.n_trades!r}")


@dataclass(frozen=True)
class DecisionCandidate:
    """One PRESENT edge's own decision verdict. ``evidence`` is a tuple of concrete, disclosed facts
    (never a vague phrase) -- each traceable to Edge Intelligence's own output or an already-declared
    Contract field, so a human can verify the verdict without re-deriving it."""

    strategy_id: str
    outcome: DecisionOutcome
    confidence: str
    evidence: tuple[str, ...]
    explanation: str

    def __post_init__(self) -> None:
        if not self.evidence:
            raise ValueError(
                "DecisionCandidate requires at least one evidence item -- a verdict with no disclosed "
                "reasoning is exactly what this layer must never produce"
            )


@dataclass(frozen=True)
class DecisionReport:
    """One point-in-time decision snapshot. ``candidates`` covers every currently-PRESENT edge (Edge
    Intelligence's own scope), each ACCEPT or REJECT; ``recommended_strategy_id`` is the single highest-
    ranked ACCEPT candidate, or ``None`` when no edge deserves execution (NO TRADE -- an explicit, valid
    decision, never an error or an omission). ``comparison_notes`` narrates, pairwise, why each ACCEPTed
    candidate outranks the next -- "why stronger or weaker than competing edges" (CEO Checkpoint 7
    directive), or that they are genuinely tied down to the final strategy_id tie-break."""

    symbol: str
    as_of: int
    candidates: tuple[DecisionCandidate, ...]
    recommended_strategy_id: str | None
    comparison_notes: tuple[str, ...]
