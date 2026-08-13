"""`DecisionProvenance`/`verify_decision_provenance` -- CEO Mandate 2 activation, 2026-08-14, section
"submit_candidate": "Refactorizeaza contractul astfel incat DOAR outputul valid N6 sa poata deveni input
pentru Risk Manager. Outputurile legacy merg EXCLUSIV catre legacy telemetry sink. VERIFICARE
STRUCTURALA DE PROVENIENTA: source = NEW_BRAIN_N6, valid trace_id, valid catalog_hash, valid
configuration_fingerprint. Lipsa provenientei -> NO_TRADE, UNTRUSTED_DECISION_SOURCE."

Prepared and tested now, same discipline as `broker_gate.py`/`artifact_pin.py`: this is a pure
provenance-SHAPE check (does this candidate carry the four required fields, and does `source` say what
it claims) -- it needs no real N6 output to test, only the field shape `event_identity.py` already
defines (`trace_id`, `catalog_hash`, `configuration_fingerprint`).

**Not wired into `PdhPdlOrchestrator.submit_candidate`/`PolicyOrchestrator.submit_candidate` yet** --
that IS the actual Phase C work ("O SINGURA SCHIMBARE ATOMICA... legacy -> NEW_BRAIN"), and per the
CEO's own sequencing happens only after Faza A (install) and Faza B (verify on fixtures/replay) with the
REAL artifact -- neither of which has happened, since the artifact and its complete 8-field manifest
have not been received (checked: no `ve_brain` package installed, no manifest file, no trace of
`fbc0f20`/`46c462c` anywhere in this environment as of 2026-08-14). This module is the CONTRACT the
refactored `submit_candidate` will enforce, ready before the refactor itself."""

from __future__ import annotations

from dataclasses import dataclass

NEW_BRAIN_SOURCE = "NEW_BRAIN_N6"
"""The ONE value `DecisionProvenance.source` may hold for a candidate to reach Risk Manager. Anything
else -- including every legacy recognition rule's own output, which never sets this field at all -- is
UNTRUSTED_DECISION_SOURCE by construction, not by an explicit legacy-source blocklist (a blocklist would
need updating every time a new legacy path appeared; an allowlist of exactly one value does not)."""


class UntrustedDecisionSourceError(Exception):
    """reason_code = UNTRUSTED_DECISION_SOURCE. Raised by `verify_decision_provenance` whenever `source`
    is not exactly `NEW_BRAIN_SOURCE`, or any of `trace_id`/`catalog_hash`/`configuration_fingerprint`
    is missing/empty. NO_TRADE is the caller's own required response to this being raised -- this
    function only refuses, it never decides what happens next."""


@dataclass(frozen=True, slots=True, kw_only=True)
class DecisionProvenance:
    """Attached to a candidate at the boundary where it claims to be a real N6 decision. `source` is a
    free string field (not an enum) deliberately -- an enum would need every legacy source enumerated as
    a valid-but-rejected member; a plain string compared against the ONE allowed value has no such
    maintenance burden and no risk of a legacy source accidentally being added to an "acceptable to
    reject" enum that a future refactor treats as "acceptable"."""

    source: str
    trace_id: str
    catalog_hash: str
    configuration_fingerprint: str


def verify_decision_provenance(provenance: DecisionProvenance) -> None:
    """Raises `UntrustedDecisionSourceError` unless `source == NEW_BRAIN_SOURCE` AND all three identity
    fields are non-empty. Silent on success (returns `None`) -- same two-outcome contract as
    `BrokerOrderSubmissionGate.authorize()`/`verify_artifact_pin()`: proceed, or raise, nothing else."""
    if provenance.source != NEW_BRAIN_SOURCE:
        raise UntrustedDecisionSourceError(
            f"UNTRUSTED_DECISION_SOURCE: source={provenance.source!r}, expected {NEW_BRAIN_SOURCE!r}"
        )
    missing = [
        name for name, value in (
            ("trace_id", provenance.trace_id),
            ("catalog_hash", provenance.catalog_hash),
            ("configuration_fingerprint", provenance.configuration_fingerprint),
        )
        if not value
    ]
    if missing:
        raise UntrustedDecisionSourceError(f"UNTRUSTED_DECISION_SOURCE: missing field(s): {missing}")
