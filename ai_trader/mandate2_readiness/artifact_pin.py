"""`BrainArtifactPin`/`verify_artifact_pin` -- CEO Mandate 2 amendment, 2026-08-14, section 2: "PIN
EXACT... La pornire, verifica OBLIGATORIU: package_version, source_commit, catalog_version,
catalog_hash, measurement_contract_version, N1 contract version, Router version, EV engine version.
Lipsa sau nepotrivire: NO_TRADE, reason_code = BRAIN_ARTIFACT_INCOMPATIBLE. Procesul NU poate continua
pe alta versiune 'compatibila aproximativ'."

Prepared and tested now, same discipline as `broker_gate.py`: the verification RULE exists before a
single byte of the real artifact has been received.

**Honest about what is actually pinned today**: the CEO's own amendment supplied exact values for only
TWO of the eight required fields (`package_version="0.1.3"`, `source_commit="fbc0f20"`). The other six
are `None` in `CURRENT_PIN` below -- NOT a placeholder meaning "any value is fine", but the opposite:
`verify_artifact_pin` treats an unpinned (`None`) expected field EXACTLY like a mismatch. An unknown
expectation cannot be satisfied by any observed value, ever -- the fail-closed response to "we don't
have the reference value yet" is refuse, never skip the check. Once VE/Red Team supply the remaining six
pinned values, `CURRENT_PIN` gets a real value for that field and the check that field participates in
starts actually discriminating; until then, EVERY verification attempt fails, which is correct: this
codebase cannot claim compatibility with an artifact it has never seen and has no full reference for.
"""

from __future__ import annotations

from dataclasses import dataclass, fields

_PIN_FIELD_NAMES = (
    "package_version", "source_commit", "catalog_version", "catalog_hash",
    "measurement_contract_version", "n1_contract_version", "router_version", "ev_engine_version",
)


class BrainArtifactIncompatibleError(Exception):
    """reason_code = BRAIN_ARTIFACT_INCOMPATIBLE. Raised on ANY mismatched or unpinned field -- never a
    warning, never a partial/"close enough" pass."""


@dataclass(frozen=True, slots=True, kw_only=True)
class BrainArtifactPin:
    """The REQUIRED pin. `None` means "not yet supplied by the CEO/VE/Red Team" -- see module docstring
    for why that fails closed rather than being treated as a wildcard."""

    package_version: str | None = None
    source_commit: str | None = None
    catalog_version: str | None = None
    catalog_hash: str | None = None
    measurement_contract_version: str | None = None
    n1_contract_version: str | None = None
    router_version: str | None = None
    ev_engine_version: str | None = None


CURRENT_PIN = BrainArtifactPin(package_version="0.1.3", source_commit="fbc0f20")
"""Only `package_version`/`source_commit` are pinned today (CEO, 2026-08-14). The other six fields stay
`None` until VE/Red Team supply them -- `verify_artifact_pin(CURRENT_PIN)` will refuse EVERY observed
manifest until they do, by design."""


@dataclass(frozen=True, slots=True, kw_only=True)
class ObservedArtifactManifest:
    """What the real artifact's own install-time manifest is expected to report, once it exists. Every
    field required, no `None` here -- an artifact that cannot report its own identity is itself a
    BRAIN_ARTIFACT_INCOMPATIBLE case, not a separate failure mode."""

    package_version: str
    source_commit: str
    catalog_version: str
    catalog_hash: str
    measurement_contract_version: str
    n1_contract_version: str
    router_version: str
    ev_engine_version: str


def verify_artifact_pin(observed: ObservedArtifactManifest, pin: BrainArtifactPin = CURRENT_PIN) -> None:
    """Raises `BrainArtifactIncompatibleError` if ANY of the 8 fields is unpinned (`None` in `pin`) or
    does not match `observed` exactly (byte-for-byte string equality -- no version-range parsing, no
    "compatible enough" semver logic, matching the CEO's own explicit "NU poate continua pe alta
    versiune 'compatibila aproximativ'"). Silent on success (returns `None`) -- the caller proceeds only
    if this does not raise, matching `BrokerOrderSubmissionGate.authorize()`'s own two-outcome contract."""
    mismatches: list[tuple[str, str | None, str]] = []
    for field_name in _PIN_FIELD_NAMES:
        expected = getattr(pin, field_name)
        actual = getattr(observed, field_name)
        if expected is None or expected != actual:
            mismatches.append((field_name, expected, actual))
    if mismatches:
        raise BrainArtifactIncompatibleError(
            f"BRAIN_ARTIFACT_INCOMPATIBLE: {len(mismatches)} of {len(_PIN_FIELD_NAMES)} field(s) "
            f"unpinned or mismatched: {mismatches}"
        )


def _all_pin_field_names() -> tuple[str, ...]:
    """Structural cross-check helper (used by this module's own tests) -- confirms `_PIN_FIELD_NAMES`
    hasn't drifted from the dataclass's own declared fields."""
    return tuple(f.name for f in fields(BrainArtifactPin))
