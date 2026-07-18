"""Shadow Evidence configuration surface -- Phase 6.10 Implementation Checkpoints 1A + 1B + 3
(``PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md``). ``enabled=False`` (the default) and
``shadow_strategies=()`` (the default) together mean Shadow Mode is fully inert -- no existing caller
of :class:`~ai_trader.simulation.config.SimulationContext` needs to pass this field or know it exists.

``shadow_strategies`` is a plain, generic strategy-id allowlist -- nothing in this module or in
:mod:`ai_trader.shadow_evidence.engine` ever names a specific strategy. Configuring
``shadow_strategies=("S10",)`` today and ``shadow_strategies=("S10", "S21", "S39", "S40")`` next week
is the same code path, with no production-code change required. Checkpoint 3 adds
:func:`all_registered_strategies` -- a config-only helper for the largest such allowlist that already
exists (every registered production strategy), not a new code path either.
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


def all_registered_strategies() -> frozenset[str]:
    """The full set of currently-registered production strategies (Strategy Runtime's own registry)
    -- Checkpoint 3's own "first production strategy set": every existing, already-implemented
    strategy this repository has, no new strategy invented, no subset hand-picked (Design §3's own
    literal scaling example: ``shadow_strategies=registry.registered_strategy_ids()``, "already a
    one-line, existing repository call").

    Triggers the SAME lazy ``ai_trader.strategy_runtime.families`` import
    :func:`~ai_trader.strategy_runtime.registry.build_runtime_handles` already performs internally, so
    this returns the true full set (43 as of Checkpoint 3, S1-S31/S38-S46/S48/S50/S51 -- S32-S37
    NOT_IMPLEMENTED, S47/S49 technically invalid, per ``PROJECT_STATE_v2.md`` §2) even if called before
    any harness has run -- never an accidentally-empty set from an import that hasn't happened yet."""
    import ai_trader.strategy_runtime.families  # noqa: F401 -- trigger every family's own @register(...)
    from ai_trader.strategy_runtime.registry import registered_strategy_ids

    return registered_strategy_ids()
