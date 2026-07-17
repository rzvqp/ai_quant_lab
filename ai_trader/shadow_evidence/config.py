"""Shadow Evidence configuration surface -- Phase 6.10 Implementation Checkpoints 1A + 1B
(``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md``). ``enabled=False`` (the default) and
``shadow_strategies=()`` (the default) together mean Shadow Mode is fully inert -- no existing caller
of :class:`~ai_trader.simulation.config.SimulationContext` needs to pass this field or know it exists.

``shadow_strategies`` is a plain, generic strategy-id allowlist -- nothing in this module or in
:mod:`ai_trader.shadow_evidence.engine` ever names a specific strategy. Configuring
``shadow_strategies=("S10",)`` today and ``shadow_strategies=("S10", "S21", "S39", "S40")`` next week
is the same code path, with no production-code change required.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ShadowConfig:
    """The Shadow Evidence configuration surface for one simulation run.

    ``enabled``: the master switch. ``False`` (the default) means Shadow Mode is fully inert
    regardless of ``shadow_strategies``.
    ``shadow_strategies``: the generic, CEO-configurable allowlist of strategy ids to shadow-track.
    Empty by default. Order is irrelevant -- :meth:`active_strategy_ids` returns a ``frozenset``.
    """

    enabled: bool = False
    shadow_strategies: tuple[str, ...] = ()

    def active_strategy_ids(self) -> frozenset[str]:
        """The strategies actually being shadow-tracked right now -- empty unless both ``enabled`` is
        ``True`` and ``shadow_strategies`` is non-empty. The single source of truth every consumer
        (the harness, the shadow engine) should read, rather than re-deriving this condition itself."""
        return frozenset(self.shadow_strategies) if self.enabled else frozenset()
