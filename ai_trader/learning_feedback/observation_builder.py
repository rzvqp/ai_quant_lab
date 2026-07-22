"""Observation construction -- Learning/Research Feedback Phase F, Architectural Decision Package
Decision 4. Bridges a :class:`~ai_trader.learning_feedback.market_snapshot.MarketSnapshotBundle` into a
real, non-degraded Context Memory :class:`~ai_trader.context_memory.contracts.Observation`, reusing
:mod:`ai_trader.decision_intelligence_v2.adapters`'s own already-approved translation functions
(Checkpoint 14) unmodified -- this module invents no new translation logic, only composes existing,
approved adapters.

``present_edges`` includes every strategy reading whose own ``EdgeState`` is PRESENT or POSSIBLE (both
carried faithfully, per Phase E's own fidelity correction to ``build_present_edge_reference`` -- ABSENT
edges are never given a ``PresentEdgeReference`` at all, matching that type's own documented purpose).

**Disclosed, deliberately accepted inefficiency**: ``load_strategy_contracts`` re-reads the Strategy
Library from disk on every call (``edge_intelligence/contracts.py``, no caching) -- ``evaluate_edges``
(inside ``market_snapshot.py``) already calls it once internally; this module calls it a second time to
recover each reading's own ``Contract`` (needed by ``build_present_edge_reference``, which
``EdgeIntelligenceSnapshot`` itself does not carry). Accepted for the same reason as the Market
Intelligence double-computation ``market_snapshot.py`` already discloses: avoiding it would require
reimplementing ``evaluate_edges``'s own internal composition here, a larger maintenance-coupling risk than
one extra, bounded, small-file disk read per bar.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory.contracts import Observation, PresentEdgeReference
from ai_trader.decision_intelligence_v2.adapters import build_context_snapshot, build_present_edge_reference
from ai_trader.edge_intelligence.contracts import load_strategy_contracts
from ai_trader.edge_intelligence.types import EdgeState
from ai_trader.learning_feedback.market_snapshot import MarketSnapshotBundle


def build_decision_observation(bundle: MarketSnapshotBundle, library_path: Path | None = None) -> Observation:
    """Build the real, non-degraded ``Observation`` for one ``(symbol, as_of)`` from a
    ``MarketSnapshotBundle``. Never fabricates a ``present_edges`` entry for a strategy Edge Intelligence
    classified ABSENT, and never fabricates a ``Contract`` for a strategy whose contract cannot be read
    (structurally unreachable in practice -- every reading in ``bundle.ei_snapshot`` was itself only
    produced for a strategy `evaluate_edges` could already read a valid ``Contract`` for -- but handled
    defensively rather than assumed)."""
    context_snapshot = build_context_snapshot(bundle.mi_snapshot)
    contracts = load_strategy_contracts(library_path)
    present_edges: list[PresentEdgeReference] = []
    for strategy_id, reading in bundle.ei_snapshot.readings.items():
        if reading.state is EdgeState.ABSENT:
            continue
        contract = contracts.get(strategy_id)
        if contract is None:
            continue  # defensive only -- never fabricate a Contract; see module docstring
        present_edges.append(build_present_edge_reference(strategy_id, contract, reading.state))
    return Observation(context_snapshot=context_snapshot, present_edges=tuple(present_edges))
