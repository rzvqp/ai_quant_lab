"""Shadow Evidence configuration surface -- Phase 6.10 Implementation Checkpoint 1A
(``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md``). Structural only: no opportunity tap, virtual
risk evaluation, virtual orders/positions, or Strategy Health integration exists yet -- each is
deferred to a separate, later, CEO-approved checkpoint.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ShadowConfig:
    """The Shadow Evidence configuration surface for one simulation run. ``enabled=False`` (the
    default) means Shadow Mode is fully inert -- no shadow tap, no shadow risk evaluation, no shadow
    execution/portfolio instances, no shadow evidence records of any kind are created; no existing
    caller of :class:`~ai_trader.simulation.config.SimulationContext` needs to pass this field or know
    it exists. Additional fields (shadow-eligible strategy set, shadow-start policy, etc.) are added by
    later, separately approved checkpoints -- not this one."""

    enabled: bool = False
