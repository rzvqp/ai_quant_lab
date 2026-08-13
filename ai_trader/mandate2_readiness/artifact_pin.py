"""`BrainArtifactPin`/`verify_artifact_pin` -- CEO Mandate 2, 2026-08-14. Schema is ten fields (corrected
from eight once VE's manifest delivery, first at commit `296e3ac`, exposed that a single `source_commit`
field cannot mean BOTH "the core Red Team validated" AND "the package actually installed"). The
FINAL, ratified delivered package is commit `a1d2a6d` (`296e3ac` and an intermediate `d7d8912` were both
superseded -- `a1d2a6d` is the exact commit whose wheel Red Team's own `RT-PIN-0001_ve_brain_wheel
_a1d2a6d_PASS.md` grants `ARTIFACT_PIN_PASS` for, independently re-verified in this environment: the
wheel's SHA-256, `ai_quant_lab-wp5b`'s own `git rev-parse HEAD` at that commit, and the installed
package's own `artifact_manifest("a1d2a6d")` all agree).

**The three identities, not to be confused** (CEO's own framing, corroborated by Red Team's own report):
`validated_core_commit` (`fbc0f20`, what Red Team's `VE_HANDOFF_PASS` actually validated -- the decision
core, byte-identical across every packaging revision), `source_commit` (`a1d2a6d`, the package this
codebase actually installs -- packaging/manifest changes only, zero core-module diffs vs `fbc0f20`), and
a third, separate measurement-source identity (`dc28e4a`, `version.SOURCE_COMMIT` inside the installed
package) that belongs to `measurement_contract_version`'s own provenance, not to this pin's ten fields.

**Every `observed` value here MUST come from calling the real, installed package's own
`artifact_manifest(delivery_commit)` function -- never copied into this codebase's source as a literal.**
`delivery_commit` is itself required, non-optional, and fail-closed (the installed package's own
`DeliveryCommitRequiredError`, confirmed empirically: both `''` and `None` raise it, no placeholder) --
supplied as the actual `git rev-parse HEAD` of the checkout the wheel was built from (`a1d2a6d`), never
guessed. The ten `CURRENT_PIN` values below are the REFERENCE to compare `artifact_manifest()`'s return
against; this module itself never calls that function (that happens at the actual installation site, not
inside this pure-comparison module).

**All ten fields are now pinned.** `manifest_schema_version="1.0"` was the last one, supplied once the
real installed package actually emitted it (previously deferred, correctly, per this module's own
fail-closed discipline -- a concept named without a concrete literal never gets a guessed value)."""

from __future__ import annotations

from dataclasses import dataclass, fields

_PIN_FIELD_NAMES = (
    "package_version", "source_commit", "validated_core_commit", "catalog_version", "catalog_hash",
    "measurement_contract_version", "n1_contract_version", "router_version", "ev_engine_version",
    "manifest_schema_version",
)


class BrainArtifactIncompatibleError(Exception):
    """reason_code = BRAIN_ARTIFACT_INCOMPATIBLE. Raised on ANY mismatched or unpinned field -- never a
    warning, never a partial/"close enough" pass."""


@dataclass(frozen=True, slots=True, kw_only=True)
class BrainArtifactPin:
    """The REQUIRED pin, ten fields. `None` means "not yet supplied by the CEO/VE/Red Team" -- see
    module docstring for why that fails closed rather than being treated as a wildcard."""

    package_version: str | None = None
    source_commit: str | None = None
    """The DELIVERED PACKAGE's own commit -- what this codebase actually installs. Distinct from
    `validated_core_commit` below; conflating the two was the exact defect this schema correction
    fixed (2026-08-14)."""
    validated_core_commit: str | None = None
    """The commit Red Team's own `VE_HANDOFF_PASS`/`ARTIFACT_MANIFEST_PASS` validated -- the core the
    delivered package (`source_commit`) is required to CONTAIN, not necessarily equal."""
    catalog_version: str | None = None
    catalog_hash: str | None = None
    measurement_contract_version: str | None = None
    n1_contract_version: str | None = None
    router_version: str | None = None
    ev_engine_version: str | None = None
    manifest_schema_version: str | None = None
    """Deferred -- the CEO's own instruction named this "valoarea verificata" without a concrete literal
    value. Stays `None`, same fail-closed treatment as any other unpinned field, until an actual string
    is supplied."""


CURRENT_PIN = BrainArtifactPin(
    package_version="0.1.3",
    source_commit="a1d2a6d",
    validated_core_commit="fbc0f20",
    catalog_version="ve-canonical-catalog-v1",
    catalog_hash="37b95393df85dc2b",
    measurement_contract_version="canonical-evaluator-v2.7.66-A2",
    n1_contract_version="n1-additive-raw-axes-v1",
    router_version="router-v1",
    ev_engine_version="ev-core@bdd15e5+ev-adapter-v1",
    manifest_schema_version="1.0",
)
"""All ten fields pinned (CEO, 2026-08-14, final ARTIFACT_PIN_PASS). Independently re-verified against
the REAL installed package in this environment -- `verify_artifact_pin(CURRENT_PIN)` genuinely PASSES
against `artifact_manifest("a1d2a6d")`'s actual return value, not merely against a hand-typed fixture."""


@dataclass(frozen=True, slots=True, kw_only=True)
class ObservedArtifactManifest:
    """What `artifact_manifest()`, called on the REAL, installed package, is expected to return. Every
    field required, no `None` here -- an artifact that cannot report its own identity is itself a
    BRAIN_ARTIFACT_INCOMPATIBLE case, not a separate failure mode. This dataclass exists to give that
    return value a typed, exhaustive shape to compare `CURRENT_PIN` against -- it is never constructed
    from literals in this codebase's own source; only from whatever the installed package's own
    `artifact_manifest()` reports at runtime."""

    package_version: str
    source_commit: str
    validated_core_commit: str
    catalog_version: str
    catalog_hash: str
    measurement_contract_version: str
    n1_contract_version: str
    router_version: str
    ev_engine_version: str
    manifest_schema_version: str


def verify_artifact_pin(observed: ObservedArtifactManifest, pin: BrainArtifactPin = CURRENT_PIN) -> None:
    """Raises `BrainArtifactIncompatibleError` if ANY of the ten fields is unpinned (`None` in `pin`) or
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
