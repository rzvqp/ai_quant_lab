"""Mandate 2 preparation (CEO, 2026-08-14): "PREGATIRE pentru Mandatul 2. NU integrezi inca." -- the
work this division can do BEFORE VE hands off the new decision-engine artifact and Red Team ratifies it
(`VE_HANDOFF_PASS`). Nothing in this package imports, wraps, or references N1-N6 or the EV engine --
those don't exist here yet, and this division is explicitly forbidden from modifying them internally
even once they arrive. Nothing in this package is wired into any of the 5 currently-running live
processes (`pdh_pdl_demo`, `multi_policy_live`, `live_observation`, `spread_collection`, `zone_observer`)
-- those stay exactly as they are ("Cele cinci procese... Neschimbate").

Original three deliverables, matching the CEO's own three sections:
1. Runtime inventory -- see `AI_TRADER_MANDATE2_PREP_RUNTIME_INVENTORY.md` at the repo root (a document,
   not code -- it describes what exists today, it doesn't change anything). Section 6 of that document
   is the explicit 5-process inventory the amendment below added.
2. `tests/test_e2e_readiness.py` -- skeletons for the 25 end-to-end tests Mandate 2's own integration
   will need. Six (the ones NOT depending on the artifact) are REAL, RUNNABLE tests proving the property
   already holds in the CURRENT architecture -- a regression floor Mandate 2's integration must not lower.
   The other nineteen are documented skeletons (`pytest.skip`), since they name concepts (confidence
   thresholds, N1-N6 outputs, the EV engine) that don't exist in this repo yet.
3. `broker_gate.py` -- `BrokerOrderSubmissionGate`, a freestanding, default-DISABLED safety primitive
   ready to be the mandatory choke point for whatever NEW order-producing code Mandate 2's integration
   eventually writes. Defended by code (no setter, no env-var fallback), config (the literal default),
   and test (`tests/test_broker_gate.py`, `tests/test_broker_gate_attack_surfaces.py`).

**CEO amendment, 2026-08-14 ("prevaleaza daca exista contradictie" -- the full integration spec for
AFTER `VE_HANDOFF_PASS`, plus more no-artifact-needed primitives)**:
4. `artifact_pin.py` -- `BrainArtifactPin`/`verify_artifact_pin`, the exact version/hash contract
   (section 2, corrected 2026-08-14 from 8 to 10 fields once VE's own manifest delivery first exposed
   that a single `source_commit` field can't mean both "the Red-Team-validated core" AND "the package
   actually installed"). All ten fields are now pinned (final `ARTIFACT_PIN_PASS`, delivered package
   `source_commit="a1d2a6d"`, `manifest_schema_version="1.0"`) -- see that module's own docstring for
   the full three-identity history.
5. `event_identity.py` -- `EventIdentity`/`NodeTrace` (section 4), the minimum per-cycle and per-node
   trace fields, typed and validated ahead of any real wiring.
6. `decision_provenance.py` -- `DecisionProvenance`/`verify_decision_provenance` (the `submit_candidate`
   section), the structural provenance check that will gate what may become Risk Manager input: only
   `source == NEW_BRAIN_SOURCE` with a non-empty `trace_id`/`catalog_hash`/`configuration_fingerprint`
   passes -- a single-value allowlist, not a legacy blocklist, so every existing legacy candidate (none
   of which set this field) is rejected by construction, not by enumeration.
7. `wheel_verification.py` -- `verify_wheel_hash`, the pre-install SHA-256/size/filename gate ("VERIFICI
   SHA-256 INAINTE DE INSTALARE"). Standalone, no import of the wheel's contents -- read-and-hash only.

**Mandate 2 status, 2026-08-14 -- integration ACTIVE, prep phase over.** `ve_brain-0.1.3` is installed and
independently verified (`verify_artifact_pin` genuinely PASSES against the real installed package). The
real integration package is `ai_trader.new_brain_bridge` (N1-Router-EV-N6, a provenance-gated Risk
Manager bridge, shadow execution, persisted telemetry) -- steps 1-8 of the CEO's 12-step list are done and
tested there. **This package (`mandate2_readiness`) is consequently no longer "not wired into anything"**
-- `new_brain_bridge` is its one and only legitimate importer (see `tests/test_import_independence.py
::test_only_new_brain_bridge_imports_this_package`); nothing else in `ai_trader/` reaches it, and this
package's own production code still imports nothing from `ve_brain`, `pdh_pdl_demo`, or
`multi_policy_live` (still true, still enforced by this package's own static guards).

**Legacy demotion + the atomic authority switch (steps 4-5) are built as CODE ONLY, per explicit CEO
instruction 2026-08-14 ("construieste codul, NU comuta inca")** -- `new_brain_bridge.authority
.DecisionAuthority`, persisted the same way `PolicyControl` already is; `pdh_pdl_demo`'s/
`multi_policy_live`'s own `submit_candidate` methods gained an optional `authority_check` parameter,
default `None`, byte-for-byte unchanged behavior. `set_authority()` is never called anywhere -- the 5 live
processes' real behavior is untouched. 22 of the 25 CEO-owned end-to-end tests are now real (4 stay
`BLOCKED_ON_TOWER_HANDOFF`, owner VE, each with a test -> owner -> remedy -> dovada -> verdict entry --
see `tests/test_e2e_readiness.py`'s own updated module docstring). Remaining: the CEO's explicit 15-item
property checklist (section 8, delivered) and the final `READY_FOR_LIVE_SHADOW_REVIEW` report. The CEO checkpoint
remains required only before `LIVE_SHADOW` itself; `BROKER_ORDER_SUBMISSION` stays `DISABLED` throughout."""

from __future__ import annotations
