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

EXPECTED_WORKER_PACKAGE_VERSION = "0.3.0"
EXPECTED_PROTOCOL_VERSION = PROTOCOL_VERSION
EXPECTED_VE_TOWER_PACKAGE_VERSION = "0.5.0"
EXPECTED_PACKAGE_BUILD_COMMIT = "b128d8b"
EXPECTED_STATE_DELIVERY_COMMIT = "26470f5"
EXPECTED_WHEEL_SHA256 = "6d99baf62f9a245031722a3b59c4df59b98211707c26d587641eff424cd94df7"
EXPECTED_VENDORED_SOURCE_IDENTITY = "sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c"
EXPECTED_N3_CONTRACT_VERSION = "tower-n3-request-v2"
EXPECTED_N4_CONTRACT_VERSION = "tower-n4-request-v2"
EXPECTED_N2_CONTRACT_VERSION = "tower-n2-request-v1"
EXPECTED_CHAIN_REQUEST_CONTRACT_VERSION = "tower-chain-request-v1"
EXPECTED_CHAIN_RESPONSE_CONTRACT_VERSION = "tower-chain-response-v1"
EXPECTED_TOWER_CHAIN_BINDING_VERSION = "tower-chain-binding-v1"
EXPECTED_PRODUCTION_ENTRYPOINT = "run_tower_chain"
"""RT-TOWER-0008 remediation (2026-08-17, `ve_tower` 0.5.0, `N2_HANDOFF_PASS`/`N2_CHAIN_BINDING_PASS`,
Red Team `RT-TOWER-0008` @ `ai_quant_lab-wp5b` commit `d2f5a68`). Sourced from `HANDOFF_MANIFEST-0.5.0.json`
(`ai_quant_lab-wp5b` @ `26470f5`, schema `ve-tower-handoff-manifest-v2`), verified by
`tower_worker/env/sidecar_verification.py` (`_verify_sidecar_v2`) BEFORE being written here -- the wheel's
own SHA-256 was independently re-hashed against the committed file and against `SHA256SUMS.txt`, both
matching the manifest and each other.

**Three DISTINCT commit identities, never conflated** (CEO correction, 2026-08-17 -- the report and this
pin must never call two different commits "the delivery commit"):
- `package_build_commit` (`b128d8b`) -- the commit `ve_tower 0.5.0` was BUILT from (the chain orchestrator
  itself, "ve_tower 0.5.0: chain orchestrator run_tower_chain").
- `state_delivery_commit` (`26470f5`, THIS pin's authoritative value) -- the commit that physically
  delivered the wheel + sidecar manifest ("ve_tower: physical 0.5.0 wheel + sidecar handoff manifest") --
  the sidecar's OWN declared value, read from the manifest, never from a chat paraphrase.
- `d7d5bab` -- a LATER commit whose own message is literally "stamp manifest state_delivery_commit to
  26470f5": the act of publishing/back-referencing the delivery, not the delivery's own identity. This pin
  deliberately does NOT use `d7d5bab` for `state_delivery_commit` -- verified via `git log` that both
  commits are real and non-conflicting, but the sidecar (the cryptographically-tied-to-the-wheel artifact)
  is the authority for what `state_delivery_commit` means, not the stamping commit that references it.

**`EXPECTED_WORKER_PACKAGE_VERSION` bumped 0.2.0 -> 0.3.0** alongside this pin update -- see
`tower_worker/pyproject.toml`/`decision.py`'s own version bump for the `run_tower_chain`-exclusive
rewrite; a worker still reporting `0.2.0` is running pre-remediation code and must fail the pin.

**Vendored identity unchanged from 0.3.0's pin** -- confirmed byte-identical: `ve_tower` 0.5.0 adds the
NEW `run_tower_chain`/N2 orchestrator on top of the SAME ratified, byte-identical N1/N3/N4 vendored
modules, never re-vendored."""


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
        ("n2_contract_version", EXPECTED_N2_CONTRACT_VERSION, claimed.n2_contract_version),
        ("chain_request_contract_version", EXPECTED_CHAIN_REQUEST_CONTRACT_VERSION,
         claimed.chain_request_contract_version),
        ("chain_response_contract_version", EXPECTED_CHAIN_RESPONSE_CONTRACT_VERSION,
         claimed.chain_response_contract_version),
        ("tower_chain_binding_version", EXPECTED_TOWER_CHAIN_BINDING_VERSION, claimed.tower_chain_binding_version),
        ("production_entrypoint", EXPECTED_PRODUCTION_ENTRYPOINT, claimed.production_entrypoint),
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
