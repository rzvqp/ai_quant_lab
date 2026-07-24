"""Recognition Engine Phase 1A sufficiency policy -- explicit, versioned-by-value, never a hidden
constant embedded inline in `engine.py` (this project's own standing "no hidden constants" discipline,
`EvidencePolicy`'s own precedent). The CEO's own explicit Phase 1A instruction: the existing minimum-25
convention (`code/alpha_lab.py`'s own `MINTR=25`, already reused twice elsewhere in this project --
`PROJECT_AUDIT.md`'s own notes, Strategy Health's `MIN_EVIDENCE_TRADES`) must be kept unless a separate,
official document justifies otherwise. No such document exists yet, so the default here is 25.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SufficiencyPolicy:
    """`min_observations`: a bucket with fewer than this many `PositionOutcome` records is reported as
    `Sufficiency.INSUFFICIENT_EVIDENCE`, never a computed rate presented as if it were reliable."""

    min_observations: int = 25

    def __post_init__(self) -> None:
        if self.min_observations < 1:
            raise ValueError(f"SufficiencyPolicy.min_observations must be >= 1, got {self.min_observations!r}")
