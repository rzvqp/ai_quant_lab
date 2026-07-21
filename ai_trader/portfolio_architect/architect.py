"""Portfolio Architect -- Phase 1 (PASSTHROUGH scaffold only). See package ``__init__.py`` for the
full scope statement."""

from __future__ import annotations

from collections.abc import Sequence

from ai_trader.portfolio_architect.types import (
    POLICY_VERSION,
    ArchitectDiagnostics,
    ArchitectMode,
    PortfolioArchitectConfig,
    PortfolioArchitectResult,
)
from ai_trader.risk_manager.types import PortfolioState
from ai_trader.scoring_engine.types import OpportunityScore


class PortfolioArchitect:
    """Stateless -- no ``configure()`` step, no internal mutable state, matching the CEO's own explicit
    requirement that this interface "not depend directly on mutable global state." A single instance may
    be reused across every bar/call; nothing about it is per-run or per-symbol."""

    def evaluate(
        self,
        opportunities: Sequence[OpportunityScore],
        portfolio_state: PortfolioState | None,
        as_of: int,
        config: PortfolioArchitectConfig,
    ) -> PortfolioArchitectResult:
        """``portfolio_state`` is accepted (per the design doc's own input contract, §2/§5) but
        deliberately UNUSED in Phase 1 -- PASSTHROUGH is a pure function of ``opportunities`` alone.
        Future phases that implement a real arbitration policy will read it; reserving the parameter now
        avoids a signature change later.

        Phase 1 supports exactly one mode. An unsupported ``config.mode`` raises rather than silently
        falling back to some other behavior -- there is no other behavior to fall back to yet."""
        if config.mode is not ArchitectMode.PASSTHROUGH:
            raise ValueError(
                f"unsupported ArchitectMode {config.mode!r} -- Phase 1 implements PASSTHROUGH only "
                "(design doc §7/§14: every other policy is a separate, later, CEO-approved phase)"
            )
        del portfolio_state  # unused in Phase 1, see docstring above

        # Identity pass-through: same objects, same order, same `rank` values. No filtering, no
        # re-ranking, no mutation -- `tuple(...)` only normalizes the container type, it copies no
        # OpportunityScore field and reorders nothing.
        output = tuple(opportunities)

        diagnostics = ArchitectDiagnostics(
            policy_version=POLICY_VERSION, mode=config.mode, as_of=as_of,
            input_count=len(output), output_count=len(output),
        )
        return PortfolioArchitectResult(
            opportunities=output, diagnostics=diagnostics, policy_version=POLICY_VERSION,
            mode=config.mode, as_of=as_of,
        )
