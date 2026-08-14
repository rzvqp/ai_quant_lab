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
equal. That is a blocker for Phase 2, not something this remediation can resolve on its own."""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.new_brain_bridge.tower_protocol import WorkerIdentity

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
    """`claimed` is a `tower_protocol.WorkerIdentity`. Returns every field that fails to match --
    empty tuple means the identity is fully verified. Compares `worker_package_version`/
    `worker_build_commit`/`protocol_version` too (not just the `ve_tower`-derived fields) since an
    old/wrong WORKER build is exactly the class of impostor this pin exists to catch, not only a wrong
    `ve_tower` artifact."""
    checks = (
        ("ve_tower_package_version", EXPECTED_VE_TOWER_PACKAGE_VERSION, claimed.ve_tower_package_version),
        ("package_build_commit", EXPECTED_PACKAGE_BUILD_COMMIT, claimed.package_build_commit),
        ("state_delivery_commit", EXPECTED_STATE_DELIVERY_COMMIT, claimed.state_delivery_commit),
        ("wheel_sha256", EXPECTED_WHEEL_SHA256, claimed.wheel_sha256),
        ("vendored_source_identity", EXPECTED_VENDORED_SOURCE_IDENTITY, claimed.vendored_source_identity),
        ("n3_contract_version", EXPECTED_N3_CONTRACT_VERSION, claimed.n3_contract_version),
        ("n4_contract_version", EXPECTED_N4_CONTRACT_VERSION, claimed.n4_contract_version),
    )
    mismatches = []
    for field_name, expected, actual in checks:
        # None expected -> PENDING -> can never be verified -> always a mismatch, deliberately, so the
        # handshake fails closed until the real value is supplied, rather than silently skipping the check.
        if expected is None or expected != actual:
            mismatches.append(PinMismatch(field=field_name, expected=expected, actual=actual))
    return tuple(mismatches)
