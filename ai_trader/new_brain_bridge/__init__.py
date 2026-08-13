"""Mandate 2, steps 5-12 (CEO, 2026-08-14): the REAL integration -- feed -> N1 -> Router -> Eligibility
-> EV -> N6 -> Risk Manager -> Execution Adapter (SHADOW only). Distinct from `mandate2_readiness`
(pure, standalone, not-yet-wired primitives) -- this package is the wiring itself, and DOES import both
`mandate2_readiness` and the installed `ve_brain` artifact.

**No fixtures, no synthetic data on the production path.** Every function in this package that builds a
`ve_brain.DecisionRequest`/`ve_brain.RawAxes` from a live event takes a real `ai_trader.live_signal_source
.types.Bar` and nothing else invented -- structure/direction/compression/displacement come from the
SAME vendored, frozen, already-live detectors `structural_observer` uses (`structural_observer
.vendor_bridge`), never a hand-typed value. Where a real input genuinely does not exist yet in this
codebase (`probability_inputs` -- no validated per-regime historical outcome-count table exists for
`ve_brain`'s canonical strategy IDs; that is Alpha/Statistician research territory, outside this
mandate's authority to invent), the honest behavior is `probability_inputs=None` -> N6 refuses with
`MISSING_PROBABILITY_INPUTS`, not a fabricated table. See `probability_source.py`'s own docstring.

**Never modifies `ve_brain` or `mandate2_readiness`.** Never allows `BROKER_ORDER_SUBMISSION=DISABLED`
to be bypassed -- `execution_shadow.py`'s entire purpose is proving a fully-approved candidate reaches
the broker barrier and is BLOCKED there, not merely that a denied candidate never tries.

**Authority**: exactly one of `LEGACY` or `NEW_BRAIN` holds decision rights at any instant --
`authority.py`'s `current_authority()` is the single source of truth every entrypoint must consult
before calling either `PdhPdlOrchestrator.submit_candidate`/`PolicyOrchestrator.submit_candidate`
(legacy) or this package's own `bridge.evaluate_bar` (new brain)."""

from __future__ import annotations
