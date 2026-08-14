"""The identity AI Trader EXPECTS the tower worker/`ve_tower` to be -- versioned, committed, read-only at
handshake time. CEO/Red Team delivery, 2026-08-14 (`TOWER_HANDOFF_CONDITIONAL`, `ve_tower` 0.3.0 PASS on
all material points): "Clientul citeste valorile asteptate din pinul sau versionat."

**Separated identities, per the CEO's own explicit correction** -- `6daf2aa` is NOT the source identity of
every ratified module; it is the commit `ve_tower 0.3.0` was BUILT from:

- `ve_tower_package_version` -- the package's own version string.
- `package_build_commit` -- the commit the package was built from (`6daf2aa`).
- `state_delivery_commit` -- the commit that delivered the underlying state (`0207ffa`), a SEPARATE fact
  from the build commit.
- `wheel_sha256` -- the exact wheel's hash, independent of `verify_tower_wheel.py`'s own pin (that check
  gates the one-time INSTALL action; this pin gates every runtime CONNECTION -- two different mechanisms,
  deliberately not merged into one).

**2026-08-14, `TOWER_METADATA_PASS` closure.** `vendored_source_identity`, `n3_contract_version`, and
`n4_contract_version` are CLOSED -- sourced from `HANDOFF_MANIFEST-0.3.0.json` (committed at
`ai_quant_lab-wp5b` commit `12f9241`), never from this conversation, never deduced. Verified by
`tower_worker/env/sidecar_verification.py` BEFORE being written here: `vendored_source_identity` was
INDEPENDENTLY RECOMPUTED from the sidecar's own 13 raw `(module_name, git_blob_sha1)` pairs using the
manifest's own documented algorithm -- exact match, not merely copied from the manifest's own declared
field. Red Team's own independent verification: `RT-TOWER-0004` (`ai_quant_lab` commit `ccb50c5`),
verdict `TOWER_METADATA_PASS`. Both this repo's own recomputation and Red Team's are INDEPENDENT of each
other and of the sidecar's own declared value -- three separate computations agreeing, not one claim
trusted three times.

**`artifact_fingerprint` is deliberately NOT a pin field.** Per Red Team's own `RT-TOWER-0004` finding:
reproducible from the wheel's own code, but "**not** used in the pin/handshake verification
(informational)." Consistent with that finding, this module never compares it to anything.

**2026-08-14, pin-closure correction**: this module's own docstring PREVIOUSLY CLAIMED `verify_pin`
compared `worker_package_version`/`worker_delivery_commit`/`protocol_version` too -- it did not; those
three fields were silently unchecked. Fixed here: `verify_pin` now genuinely checks every field
`WorkerIdentity` carries. Two different verification STRENGTHS, by necessity, not by choice:

- **Exact match** (`ve_tower_package_version`, `package_build_commit`, `state_delivery_commit`,
  `wheel_sha256`, `vendored_source_identity`, `n3_contract_version`, `n4_contract_version`,
  `worker_package_version`, `protocol_version`) -- every one of these is knowable IN ADVANCE, independent
  of this exact handshake: `ve_tower`'s own identity comes from VE/Red Team; `worker_package_version` and
  `protocol_version` are this repo's own static, compile-time facts (a package version string, a wire
  format version), not self-referential in the way a commit hash is.
- **Presence only, DOCUMENTARY** (`worker_delivery_commit`) -- CANNOT be exact-matched against a
  hardcoded expected value without recreating the exact self-reference bug this pin-closure fixes (the
  client's OWN pin constant would need to already know a commit hash that doesn't exist until this file
  is committed). Per the CEO's own instruction (2026-08-14, `TOWER_METADATA_PASS`): "Un camp verificat
  numai prin 'e prezent' NU e o identitate de securitate" -- this field is explicitly DOCUMENTARY, never
  treated as proof the worker is running the correct code. The handshake's actual SECURITY identities are
  the nine exact-match fields below, plus the HMAC session proof (`tower_launcher.py`) -- the same
  distinction VE already drew correctly for `ve_brain`."""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.new_brain_bridge.tower_protocol import PROTOCOL_VERSION, WorkerIdentity

EXPECTED_WORKER_PACKAGE_VERSION = "0.2.0"
EXPECTED_PROTOCOL_VERSION = PROTOCOL_VERSION
EXPECTED_VE_TOWER_PACKAGE_VERSION = "0.3.0"
EXPECTED_PACKAGE_BUILD_COMMIT = "6daf2aa"
EXPECTED_STATE_DELIVERY_COMMIT = "0207ffa"
EXPECTED_WHEEL_SHA256 = "0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2"
EXPECTED_VENDORED_SOURCE_IDENTITY = "sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c"
EXPECTED_N3_CONTRACT_VERSION = "tower-n3-request-v2"
EXPECTED_N4_CONTRACT_VERSION = "tower-n4-request-v2"
"""All three sourced from `HANDOFF_MANIFEST-0.3.0.json` (`ai_quant_lab-wp5b` @ `12f9241`), verified by
`tower_worker/env/sidecar_verification.py` and independently corroborated by Red Team's `RT-TOWER-0004`
(`ai_quant_lab` @ `ccb50c5`, verdict `TOWER_METADATA_PASS`) BEFORE being written here."""


@dataclass(frozen=True, slots=True, kw_only=True)
class PinMismatch:
    field: str
    expected: str | None
    actual: str | None


def verify_pin(claimed: WorkerIdentity) -> tuple[PinMismatch, ...]:
    """`claimed` is a `tower_protocol.WorkerIdentity`. Returns every field that fails to match -- empty
    tuple means the identity is fully verified. Checks EVERY field the handshake carries, per the CEO's
    own instruction ("Trebuie sa esueze INCHIS daca ORICARE camp lipseste sau nu coincide... Toate.")."""
    exact_match_checks = (
        ("worker_package_version", EXPECTED_WORKER_PACKAGE_VERSION, claimed.worker_package_version),
        ("protocol_version", EXPECTED_PROTOCOL_VERSION, claimed.protocol_version),
        ("ve_tower_package_version", EXPECTED_VE_TOWER_PACKAGE_VERSION, claimed.ve_tower_package_version),
        ("package_build_commit", EXPECTED_PACKAGE_BUILD_COMMIT, claimed.package_build_commit),
        ("state_delivery_commit", EXPECTED_STATE_DELIVERY_COMMIT, claimed.state_delivery_commit),
        ("wheel_sha256", EXPECTED_WHEEL_SHA256, claimed.wheel_sha256),
        ("vendored_source_identity", EXPECTED_VENDORED_SOURCE_IDENTITY, claimed.vendored_source_identity),
        ("n3_contract_version", EXPECTED_N3_CONTRACT_VERSION, claimed.n3_contract_version),
        ("n4_contract_version", EXPECTED_N4_CONTRACT_VERSION, claimed.n4_contract_version),
    )
    mismatches = []
    for field_name, expected, actual in exact_match_checks:
        # No EXPECTED_* constant above is None anymore (TOWER_METADATA_PASS closed the pin) -- this check
        # stays regardless, so a field that ever again became PENDING (e.g. a future new field with no
        # value supplied yet) would fail closed by construction, the same way the three just-closed
        # fields did throughout the period before their real values existed.
        if expected is None or expected != actual:
            mismatches.append(PinMismatch(field=field_name, expected=expected, actual=actual))

    if claimed.worker_delivery_commit is None:
        mismatches.append(
            PinMismatch(field="worker_delivery_commit", expected="<any non-null value>", actual=None)
        )

    return tuple(mismatches)
