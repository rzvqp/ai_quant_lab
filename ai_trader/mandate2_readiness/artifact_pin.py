"""`BrainArtifactPin`/`verify_artifact_pin` -- CEO Mandate 2, pin correction 2026-08-14: "Schema se
extinde de la opt la zece campuri." VE's own manifest delivery (commit `296e3ac`) exposed a real
ambiguity in the original 8-field pin: a single `source_commit` field cannot mean BOTH "the core Red
Team validated" AND "the package actually installed" -- VE's delivered package (`296e3ac`) legitimately
differs from the validated core (`fbc0f20`) it contains. The schema now separates them explicitly.

**The three identities, not to be confused** (CEO's own framing): `validated_core_commit` (`fbc0f20`,
what Red Team's `VE_HANDOFF_PASS`/`ARTIFACT_MANIFEST_PASS` actually validated), `source_commit`
(`296e3ac`, the package this codebase actually installs, which CONTAINS `fbc0f20`'s changes), and a
third, separate measurement-source identity (`dc28e4a`) that belongs to `measurement_contract_version`'s
own provenance, not to this pin's ten fields directly.

**Every `observed` value here MUST come from calling the real, installed package's own
`artifact_manifest()` function -- never copied into this codebase's source as a literal.** The ten
`CURRENT_PIN` values below are the REFERENCE to compare against, supplied by the CEO; they are not
stand-ins for what `artifact_manifest()` should return, and this module never calls that function itself
(it doesn't exist here -- there is no `ve_brain` package installed in this environment as of this
writing, confirmed by `pip list`, a repo-wide grep for every one of the identity hashes below, and a
check for any `artifact_manifest` reference anywhere outside this package).

**Nine of ten fields are now pinned** (`manifest_schema_version` is explicitly deferred -- the CEO's own
wording, "valoarea verificata", names a concept without a concrete literal string; treated identically to
every other not-yet-supplied field before it: `None`, fails closed, never a wildcard). Once a value is
supplied, `CURRENT_PIN` gets it and that field starts actually discriminating; until then, every
verification attempt still fails on that one field alone, which is correct -- an unstated expectation
cannot be satisfied by any observed value, and cannot be treated as "one field doesn't matter"."""

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
    source_commit="296e3ac",
    validated_core_commit="fbc0f20",
    catalog_version="ve-canonical-catalog-v1",
    catalog_hash="37b95393df85dc2b",
    measurement_contract_version="canonical-evaluator-v2.7.66-A2",
    n1_contract_version="n1-additive-raw-axes-v1",
    router_version="router-v1",
    ev_engine_version="ev-core@bdd15e5+ev-adapter-v1",
    # manifest_schema_version left None -- see BrainArtifactPin.manifest_schema_version's own docstring.
)
"""Nine of ten fields pinned (CEO, 2026-08-14 correction). `manifest_schema_version` stays `None` --
`verify_artifact_pin(CURRENT_PIN)` will refuse EVERY observed manifest on that one field alone until the
CEO/VE supply a concrete value for it, by design."""


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
