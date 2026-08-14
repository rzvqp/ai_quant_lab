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

**Fields not yet supplied are `None` -- PENDING, not fabricated.** `vendored_source_identity` (the
digest of the 13 `VENDORED_BLOB_SHA1` values), `n3_contract_version`, and `n4_contract_version` were named
as required handshake fields but no concrete value has been given for any of them yet. `verify_pin` fails
closed on ANY `None` expected field -- a partial identity check is not a real check. This is a genuine,
disclosed gap: even once `ve_tower` 0.3.0 is actually installed and reporting real values for these three
fields, the handshake CANNOT pass here until VE's manifest supplies what this pin should expect them to
equal. That is a blocker for Phase 2, not something this remediation can resolve on its own. Point 1 of
the CEO's own pin-closure instruction: these three, plus `TOWER_METADATA_PASS`'s own artifact identity,
get filled in EXCLUSIVELY with the exact values Red Team verifies and delivers -- never deduced, never
copied from conversation. Not done here, since no such values have been supplied yet.

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
- **Presence only** (`worker_delivery_commit`) -- CANNOT be exact-matched against a hardcoded expected
  value without recreating the exact self-reference bug this pin-closure fixes (the client's OWN pin
  constant would need to already know a commit hash that doesn't exist until this file is committed).
  The check that IS meaningful and non-circular: the field must not be `None` -- proving the worker's
  claim is genuinely backed by a real `worker_delivery_manifest.json` written by the installer, not merely
  absent."""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.new_brain_bridge.tower_protocol import PROTOCOL_VERSION, WorkerIdentity

EXPECTED_WORKER_PACKAGE_VERSION = "0.2.0"
EXPECTED_PROTOCOL_VERSION = PROTOCOL_VERSION
EXPECTED_VE_TOWER_PACKAGE_VERSION = "0.3.0"
EXPECTED_PACKAGE_BUILD_COMMIT = "6daf2aa"
EXPECTED_STATE_DELIVERY_COMMIT = "0207ffa"
EXPECTED_WHEEL_SHA256 = "0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2"
EXPECTED_VENDORED_SOURCE_IDENTITY: str | None = None  # PENDING -- 13 VENDORED_BLOB_SHA1 digest not yet supplied
EXPECTED_N3_CONTRACT_VERSION: str | None = None  # PENDING -- not yet supplied
EXPECTED_N4_CONTRACT_VERSION: str | None = None  # PENDING -- not yet supplied


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
        # None expected -> PENDING -> can never be verified -> always a mismatch, deliberately, so the
        # handshake fails closed until the real value is supplied, rather than silently skipping the check.
        if expected is None or expected != actual:
            mismatches.append(PinMismatch(field=field_name, expected=expected, actual=actual))

    if claimed.worker_delivery_commit is None:
        mismatches.append(
            PinMismatch(field="worker_delivery_commit", expected="<any non-null value>", actual=None)
        )

    return tuple(mismatches)
