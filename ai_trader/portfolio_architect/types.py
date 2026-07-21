"""Portfolio Architect data contracts -- Phase 1 (PASSTHROUGH scaffold only)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ai_trader.scoring_engine.types import OpportunityScore

#: Independent of any frozen module's own version fields -- this package's own contract version,
#: bumped only when this package's own public types/behavior change.
POLICY_VERSION = "1.0.0"


class ArchitectMode(str, Enum):
    """Which arbitration behavior :class:`~ai_trader.portfolio_architect.architect.PortfolioArchitect`
    applies. ``PASSTHROUGH`` is the only mode Phase 1 implements -- a strict, provable no-op. Further
    modes are future, separately-authorized phases (design doc §7/§14), not specified here."""

    PASSTHROUGH = "PASSTHROUGH"


@dataclass(frozen=True, slots=True)
class PortfolioArchitectConfig:
    """Passed to :meth:`~ai_trader.portfolio_architect.architect.PortfolioArchitect.evaluate`. The
    harness's own ``portfolio_architect_config`` constructor parameter defaults to ``None`` (the
    Portfolio Architect is not invoked at all in that case -- stronger than passing a
    ``PortfolioArchitectConfig(mode=PASSTHROUGH)``, since no call is made at all when disabled)."""

    mode: ArchitectMode = ArchitectMode.PASSTHROUGH


@dataclass(frozen=True, slots=True)
class ArchitectDiagnostics:
    """Diagnostics-only record: counts and provenance, never a decision. Nothing in
    :mod:`ai_trader.simulation.harness` reads this to make any choice -- it exists purely for test/audit
    visibility (design doc §5: "diagnostics may record counts and provenance only; diagnostics must not
    influence the harness")."""

    policy_version: str
    mode: ArchitectMode
    as_of: int
    input_count: int
    output_count: int


@dataclass(frozen=True, slots=True)
class PortfolioArchitectResult:
    """Return value of :meth:`~ai_trader.portfolio_architect.architect.PortfolioArchitect.evaluate`.
    ``opportunities`` is the sequence to hand to ``risk_manager.evaluate()`` in place of the caller's own
    input sequence -- in PASSTHROUGH mode this is always exactly the input, same objects, same order,
    same ``rank`` values (never re-ranked, never reordered, never filtered)."""

    opportunities: tuple[OpportunityScore, ...]
    diagnostics: ArchitectDiagnostics
    policy_version: str
    mode: ArchitectMode
    as_of: int
