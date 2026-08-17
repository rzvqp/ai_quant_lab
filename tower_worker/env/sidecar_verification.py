"""Independent verification of VE's `ve_tower` handoff sidecar manifest (`HANDOFF_MANIFEST-*.json`) --
run BEFORE any of `tower_identity_pin.py`'s `EXPECTED_*` pin constants are ever written from it (CEO
mandate, 2026-08-14, `TOWER_METADATA_PASS`: "CITESTE SIDECAR-UL VERIFICAT... ABIA APOI generezi pinul").

Mirrors Red Team's own `RT-TOWER-0004` methodology exactly: `vendored_source_identity` is NOT trusted as
an emitter-only aggregate -- it is recomputed here, from the 13 raw `(module_name, git_blob_sha1)` pairs,
using the manifest's own documented algorithm, and compared against the declared value. A mismatch here
means the sidecar is not what it claims to be, independent of anyone's say-so, Red Team included.

Also cross-checks the sidecar's `ve_tower_package_version`/`package_build_commit`/`state_delivery_commit`/
`wheel_sha256` against whatever `tower_identity_pin.py` ALREADY has pinned (from the earlier
`TOWER_HANDOFF_CONDITIONAL` delivery) -- these should already agree; this function exists to catch it if
they silently don't, rather than assuming consistency across two separate deliveries.

**`artifact_fingerprint` is read and returned for the record, but deliberately never compared against
anything and never used to gate anything here.** Per Red Team's own `RT-TOWER-0004` finding: "computable
from the wheel's own code, not emitter-only; and it is **not** used in the pin/handshake verification
(informational)." Consistent with that finding, this field never becomes an `EXPECTED_*` pin constant.

Run with the MAIN venv (stdlib only -- no `ve_tower`/`ve_tower_worker` import needed here). An admin/
build-time check, never code the isolated worker itself runs."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

EXPECTED_MANIFEST_SCHEMA_VERSION_V1 = "ve-tower-handoff-manifest-v1"
EXPECTED_MANIFEST_SCHEMA_VERSION_V2 = "ve-tower-handoff-manifest-v2"
"""v2, RT-TOWER-0008 remediation (2026-08-17): `ve_tower` 0.5.0's sidecar adds the chain-binding fields
(`production_entrypoint`/`unbound_direct_api`/`chain_request_contract_version`/
`chain_response_contract_version`/`tower_chain_binding_version`/`n2_request_contract_version`) and drops
the redundant `vendored_module_count` declared-count field and the separate per-node request/response
version pair (v1 duplicated `n3_request_contract_version`/`n3_response_contract_version` as an internal
consistency check; v2 has exactly one version per node type, since the wire-level request/response split
was never a real degree of freedom in practice). Both schema versions remain independently verifiable --
v1 for auditing the 0.3.0/0.4.0 historical deliveries, v2 for 0.5.0 onward."""
EXPECTED_VENDORED_MODULE_COUNT = 13


class SidecarVerificationError(Exception):
    """Fail-closed: raised on any schema mismatch, recomputation mismatch, or missing/malformed field."""


@dataclass(frozen=True, slots=True, kw_only=True)
class VerifiedSidecar:
    ve_tower_package_version: str
    package_build_commit: str
    state_delivery_commit: str
    wheel_sha256: str
    wheel_filename: str
    artifact_fingerprint: str
    """Informational only -- see module docstring. Never compared, never gates anything."""
    n3_contract_version: str
    n4_contract_version: str
    vendored_source_identity: str
    """The RECOMPUTED value -- never the manifest's own declared string taken on faith."""
    vendored_module_count: int
    manifest_schema_version: str
    n2_contract_version: str | None = None
    chain_request_contract_version: str | None = None
    chain_response_contract_version: str | None = None
    tower_chain_binding_version: str | None = None
    production_entrypoint: str | None = None
    unbound_direct_api: tuple[str, ...] = ()
    """Chain-binding fields -- `None`/empty for a v1 (pre-0.5.0) sidecar, always populated for a
    successfully-verified v2 sidecar (see `_verify_sidecar_v2`'s own required-field check)."""
    atr_source_commit: str | None = None
    """RT-TOWER-0010 (2026-08-17, `ve_tower` 0.5.2): the `atr_source.source_commit` nested field -- `None`
    for a v2 sidecar predating 0.5.1 (0.5.0 has no `atr_source` key at all, matching
    `INTEGRATION_BLOCKED_TOWER_CHAIN_ATR_UNAVAILABLE`'s own finding). Only `source_commit` is pinned here
    (the concrete, git-blob-tied identity of the vendored module ATR is threaded from); the descriptive
    sub-fields (`n3_consumed_index`/`n4_band_index`/`n3_cross_check` in 0.5.2, differently-named in 0.5.1)
    are documentary, not a security identity."""


def recompute_vendored_source_identity(blob_sha1: dict[str, str]) -> str:
    """The manifest's own documented algorithm, verbatim: sort the (module_name, git_blob_sha1) pairs by
    name ascending; each line is `f"{module_name} {git_blob_sha1}"`; join with `\\n`; append one trailing
    `\\n`; `"sha256:" + sha256(payload).hexdigest()`."""
    pairs = sorted(blob_sha1.items(), key=lambda kv: kv[0])
    payload = "".join(f"{name} {sha1}\n" for name, sha1 in pairs)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _verify_common_identity_and_vendoring(obj: dict[str, object]) -> tuple[str, int]:
    """Shared across v1/v2: recompute `vendored_source_identity` from the raw blob-sha1 pairs (never trust
    the manifest's own declared string), and confirm exactly 13 vendored modules -- both schema versions
    vendor the SAME ratified N1/N3/N4 modules byte-identical; 0.5.0 adds `run_tower_chain`/N2 on top
    without re-vendoring them (confirmed: `vendored_source_identity` is IDENTICAL between the 0.3.0 and
    0.5.0 sidecars)."""
    blob_sha1 = obj.get("vendored_blob_sha1")
    if not isinstance(blob_sha1, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in blob_sha1.items()
    ):
        raise SidecarVerificationError("vendored_blob_sha1 missing or not a string->string object")
    if len(blob_sha1) != EXPECTED_VENDORED_MODULE_COUNT:
        raise SidecarVerificationError(
            f"vendored_blob_sha1 has {len(blob_sha1)} entries, expected {EXPECTED_VENDORED_MODULE_COUNT}"
        )
    recomputed_identity = recompute_vendored_source_identity(blob_sha1)
    declared_identity = obj.get("vendored_source_identity")
    if recomputed_identity != declared_identity:
        raise SidecarVerificationError(
            f"vendored_source_identity mismatch: recomputed={recomputed_identity!r} "
            f"declared={declared_identity!r}"
        )
    return recomputed_identity, len(blob_sha1)


def _verify_required_str_fields(obj: dict[str, object], *, field_names: tuple[str, ...]) -> None:
    for field_name in field_names:
        value = obj.get(field_name)
        if not isinstance(value, str) or not value:
            raise SidecarVerificationError(f"missing or empty required field: {field_name!r}")


def _verify_sidecar_v1(obj: dict[str, object]) -> VerifiedSidecar:
    declared_count = obj.get("vendored_module_count")
    recomputed_identity, module_count = _verify_common_identity_and_vendoring(obj)
    if declared_count != module_count:
        raise SidecarVerificationError(
            f"vendored_module_count ({declared_count!r}) does not match len(vendored_blob_sha1) ({module_count})"
        )

    n3_request = obj.get("n3_request_contract_version")
    n3_response = obj.get("n3_response_contract_version")
    if not isinstance(n3_request, str) or n3_request != n3_response:
        raise SidecarVerificationError(
            f"n3 request/response contract version mismatch or missing: {n3_request!r} != {n3_response!r}"
        )
    n4_request = obj.get("n4_request_contract_version")
    n4_response = obj.get("n4_response_contract_version")
    if not isinstance(n4_request, str) or n4_request != n4_response:
        raise SidecarVerificationError(
            f"n4 request/response contract version mismatch or missing: {n4_request!r} != {n4_response!r}"
        )

    _verify_required_str_fields(obj, field_names=(
        "ve_tower_package_version", "package_build_commit", "state_delivery_commit", "wheel_sha256",
        "wheel_filename", "artifact_fingerprint",
    ))

    return VerifiedSidecar(
        ve_tower_package_version=obj["ve_tower_package_version"],  # type: ignore[arg-type]
        package_build_commit=obj["package_build_commit"],  # type: ignore[arg-type]
        state_delivery_commit=obj["state_delivery_commit"],  # type: ignore[arg-type]
        wheel_sha256=obj["wheel_sha256"],  # type: ignore[arg-type]
        wheel_filename=obj["wheel_filename"],  # type: ignore[arg-type]
        artifact_fingerprint=obj["artifact_fingerprint"],  # type: ignore[arg-type]
        n3_contract_version=n3_request,
        n4_contract_version=n4_request,
        vendored_source_identity=recomputed_identity,
        vendored_module_count=module_count,
        manifest_schema_version=EXPECTED_MANIFEST_SCHEMA_VERSION_V1,
    )


def _verify_sidecar_v2(obj: dict[str, object]) -> VerifiedSidecar:
    recomputed_identity, module_count = _verify_common_identity_and_vendoring(obj)

    _verify_required_str_fields(obj, field_names=(
        "ve_tower_package_version", "package_build_commit", "state_delivery_commit", "wheel_sha256",
        "wheel_filename", "artifact_fingerprint", "n3_request_contract_version", "n4_request_contract_version",
        "n2_request_contract_version", "chain_request_contract_version", "chain_response_contract_version",
        "tower_chain_binding_version", "production_entrypoint",
    ))

    unbound_direct_api = obj.get("unbound_direct_api")
    if not isinstance(unbound_direct_api, list) or not all(isinstance(x, str) for x in unbound_direct_api):
        raise SidecarVerificationError("unbound_direct_api missing or not a list of strings")
    if set(unbound_direct_api) != {"run_n2", "run_n3", "run_n4"}:
        raise SidecarVerificationError(
            f"unbound_direct_api unexpected contents: {unbound_direct_api!r} "
            f"(expected exactly {{'run_n2', 'run_n3', 'run_n4'}})"
        )

    atr_source_commit: str | None = None
    atr_source = obj.get("atr_source")
    if atr_source is not None:
        if not isinstance(atr_source, dict) or not isinstance(atr_source.get("source_commit"), str):
            raise SidecarVerificationError("atr_source present but malformed (missing string source_commit)")
        atr_source_commit = atr_source["source_commit"]

    return VerifiedSidecar(
        ve_tower_package_version=obj["ve_tower_package_version"],  # type: ignore[arg-type]
        package_build_commit=obj["package_build_commit"],  # type: ignore[arg-type]
        state_delivery_commit=obj["state_delivery_commit"],  # type: ignore[arg-type]
        wheel_sha256=obj["wheel_sha256"],  # type: ignore[arg-type]
        wheel_filename=obj["wheel_filename"],  # type: ignore[arg-type]
        artifact_fingerprint=obj["artifact_fingerprint"],  # type: ignore[arg-type]
        n3_contract_version=obj["n3_request_contract_version"],  # type: ignore[arg-type]
        n4_contract_version=obj["n4_request_contract_version"],  # type: ignore[arg-type]
        vendored_source_identity=recomputed_identity,
        vendored_module_count=module_count,
        manifest_schema_version=EXPECTED_MANIFEST_SCHEMA_VERSION_V2,
        n2_contract_version=obj["n2_request_contract_version"],  # type: ignore[arg-type]
        chain_request_contract_version=obj["chain_request_contract_version"],  # type: ignore[arg-type]
        chain_response_contract_version=obj["chain_response_contract_version"],  # type: ignore[arg-type]
        tower_chain_binding_version=obj["tower_chain_binding_version"],  # type: ignore[arg-type]
        production_entrypoint=obj["production_entrypoint"],  # type: ignore[arg-type]
        unbound_direct_api=tuple(unbound_direct_api),  # type: ignore[arg-type]
        atr_source_commit=atr_source_commit,
    )


def verify_sidecar(path: Path) -> VerifiedSidecar:
    """Fail-closed on any structural or cryptographic inconsistency. Never returns a value it hasn't
    itself checked. Dispatches on `manifest_schema_version` -- v1 (0.3.0/0.4.0 historical) or v2 (0.5.0+
    chain-binding)."""
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SidecarVerificationError(f"cannot read/parse sidecar at {path}: {exc}") from exc
    if not isinstance(obj, dict):
        raise SidecarVerificationError("sidecar top-level JSON value is not an object")

    schema = obj.get("manifest_schema_version")
    if schema == EXPECTED_MANIFEST_SCHEMA_VERSION_V1:
        return _verify_sidecar_v1(obj)
    if schema == EXPECTED_MANIFEST_SCHEMA_VERSION_V2:
        return _verify_sidecar_v2(obj)
    raise SidecarVerificationError(
        f"unexpected manifest_schema_version: {schema!r} "
        f"(expected {EXPECTED_MANIFEST_SCHEMA_VERSION_V1!r} or {EXPECTED_MANIFEST_SCHEMA_VERSION_V2!r})"
    )


def cross_check_against_existing_pin(sidecar: VerifiedSidecar) -> tuple[str, ...]:
    """Returns every field name where `sidecar` disagrees with `tower_identity_pin.py`'s ALREADY-pinned
    constants (from the earlier `TOWER_HANDOFF_CONDITIONAL` delivery, a SEPARATE event from this one) --
    empty tuple means the two deliveries agree. These two things being consistent is expected, not
    assumed."""
    from ai_trader.new_brain_bridge import tower_identity_pin

    mismatches = []
    if sidecar.ve_tower_package_version != tower_identity_pin.EXPECTED_VE_TOWER_PACKAGE_VERSION:
        mismatches.append("ve_tower_package_version")
    if sidecar.package_build_commit != tower_identity_pin.EXPECTED_PACKAGE_BUILD_COMMIT:
        mismatches.append("package_build_commit")
    if sidecar.state_delivery_commit != tower_identity_pin.EXPECTED_STATE_DELIVERY_COMMIT:
        mismatches.append("state_delivery_commit")
    if sidecar.wheel_sha256 != tower_identity_pin.EXPECTED_WHEEL_SHA256:
        mismatches.append("wheel_sha256")
    if sidecar.manifest_schema_version == EXPECTED_MANIFEST_SCHEMA_VERSION_V2:
        if sidecar.n2_contract_version != tower_identity_pin.EXPECTED_N2_CONTRACT_VERSION:
            mismatches.append("n2_contract_version")
        if sidecar.chain_request_contract_version != tower_identity_pin.EXPECTED_CHAIN_REQUEST_CONTRACT_VERSION:
            mismatches.append("chain_request_contract_version")
        if sidecar.chain_response_contract_version != tower_identity_pin.EXPECTED_CHAIN_RESPONSE_CONTRACT_VERSION:
            mismatches.append("chain_response_contract_version")
        if sidecar.tower_chain_binding_version != tower_identity_pin.EXPECTED_TOWER_CHAIN_BINDING_VERSION:
            mismatches.append("tower_chain_binding_version")
        if sidecar.production_entrypoint != tower_identity_pin.EXPECTED_PRODUCTION_ENTRYPOINT:
            mismatches.append("production_entrypoint")
        if sidecar.atr_source_commit != tower_identity_pin.EXPECTED_ATR_SOURCE_COMMIT:
            mismatches.append("atr_source_commit")
    return tuple(mismatches)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: sidecar_verification.py <path-to-HANDOFF_MANIFEST.json>", file=sys.stderr)
        return 2
    try:
        sidecar = verify_sidecar(Path(argv[1]))
    except SidecarVerificationError as exc:
        print(f"SIDECAR_VERIFICATION_FAILED: {exc}", file=sys.stderr)
        return 1
    cross_check_mismatches = cross_check_against_existing_pin(sidecar)
    if cross_check_mismatches:
        print(f"CROSS_CHECK_MISMATCH against existing pin: {cross_check_mismatches}", file=sys.stderr)
        return 1
    print("SIDECAR_VERIFIED_OK")
    print(f"vendored_source_identity = {sidecar.vendored_source_identity}")
    print(f"n3_contract_version      = {sidecar.n3_contract_version}")
    print(f"n4_contract_version      = {sidecar.n4_contract_version}")
    print(f"artifact_fingerprint     = {sidecar.artifact_fingerprint}  (informational only, not pinned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
