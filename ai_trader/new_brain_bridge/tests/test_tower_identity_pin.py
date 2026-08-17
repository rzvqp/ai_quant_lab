"""`tower_identity_pin.verify_pin` tests -- the SECOND, independent verification the launcher performs
after the HMAC proves session possession: does the claimed identity actually match what AI Trader was told
to expect for `ve_tower` 0.3.0.

2026-08-14, `TOWER_METADATA_PASS`: the pin is now fully closed (no `None` fields remain). Test numbering
below follows the CEO's own 9-item retest list for this closure, items 1-6 (items 7-9 are suite-level,
covered in `test_tower_launcher.py`/`test_tower_isolation.py` and the final validation report)."""

from __future__ import annotations

from ai_trader.new_brain_bridge import tower_identity_pin
from ai_trader.new_brain_bridge.tower_identity_pin import verify_pin
from ai_trader.new_brain_bridge.tower_protocol import WorkerIdentity


def _matching_identity(**overrides: object) -> WorkerIdentity:
    """Every field set to the REAL, sidecar-verified pin value -- a genuinely fully-matching identity is
    possible for the first time as of this closure."""
    fields: dict[str, object] = {
        "worker_package_version": tower_identity_pin.EXPECTED_WORKER_PACKAGE_VERSION,
        "worker_delivery_commit": "some-real-manifest-backed-commit",
        "protocol_version": tower_identity_pin.EXPECTED_PROTOCOL_VERSION,
        "ve_tower_package_version": tower_identity_pin.EXPECTED_VE_TOWER_PACKAGE_VERSION,
        "package_build_commit": tower_identity_pin.EXPECTED_PACKAGE_BUILD_COMMIT,
        "state_delivery_commit": tower_identity_pin.EXPECTED_STATE_DELIVERY_COMMIT,
        "wheel_sha256": tower_identity_pin.EXPECTED_WHEEL_SHA256,
        "vendored_source_identity": tower_identity_pin.EXPECTED_VENDORED_SOURCE_IDENTITY,
        "n3_contract_version": tower_identity_pin.EXPECTED_N3_CONTRACT_VERSION,
        "n4_contract_version": tower_identity_pin.EXPECTED_N4_CONTRACT_VERSION,
        "n2_contract_version": tower_identity_pin.EXPECTED_N2_CONTRACT_VERSION,
        "chain_request_contract_version": tower_identity_pin.EXPECTED_CHAIN_REQUEST_CONTRACT_VERSION,
        "chain_response_contract_version": tower_identity_pin.EXPECTED_CHAIN_RESPONSE_CONTRACT_VERSION,
        "tower_chain_binding_version": tower_identity_pin.EXPECTED_TOWER_CHAIN_BINDING_VERSION,
        "production_entrypoint": tower_identity_pin.EXPECTED_PRODUCTION_ENTRYPOINT,
        "atr_source_commit": tower_identity_pin.EXPECTED_ATR_SOURCE_COMMIT,
    }
    fields.update(overrides)
    return WorkerIdentity(**fields)  # type: ignore[arg-type]


def test_1_verify_pin_passes_with_the_real_manifest_values() -> None:
    """The decisive proof the pin is genuinely closed: a fully-matching identity now produces ZERO
    mismatches -- not "everything except the 3 pending fields" (the old state), an actual empty tuple."""
    identity = _matching_identity()
    assert verify_pin(identity) == ()


def test_2a_vendored_source_identity_changed_alone_fails() -> None:
    identity = _matching_identity(vendored_source_identity="sha256:" + "0" * 64)
    mismatches = verify_pin(identity)
    assert {m.field for m in mismatches} == {"vendored_source_identity"}


def test_2b_n3_contract_version_changed_alone_fails() -> None:
    identity = _matching_identity(n3_contract_version="tower-n3-request-v1-old")
    mismatches = verify_pin(identity)
    assert {m.field for m in mismatches} == {"n3_contract_version"}


def test_2c_n4_contract_version_changed_alone_fails() -> None:
    identity = _matching_identity(n4_contract_version="tower-n4-request-v1-old")
    mismatches = verify_pin(identity)
    assert {m.field for m in mismatches} == {"n4_contract_version"}


def test_3a_vendored_source_identity_none_fails() -> None:
    identity = _matching_identity(vendored_source_identity=None)
    mismatches = verify_pin(identity)
    assert any(m.field == "vendored_source_identity" and m.actual is None for m in mismatches)


def test_3b_n3_contract_version_none_fails() -> None:
    identity = _matching_identity(n3_contract_version=None)
    mismatches = verify_pin(identity)
    assert any(m.field == "n3_contract_version" and m.actual is None for m in mismatches)


def test_3c_n4_contract_version_none_fails() -> None:
    identity = _matching_identity(n4_contract_version=None)
    mismatches = verify_pin(identity)
    assert any(m.field == "n4_contract_version" and m.actual is None for m in mismatches)


def test_4_different_wheel_sha256_fails() -> None:
    """'sidecar cu alt SHA -> fail': simulated at the pin level (a worker claiming a wheel hash the pin
    doesn't expect) -- the sidecar-level equivalent (a mutated HANDOFF_MANIFEST-*.json file) is covered
    in `test_sidecar_verification.py`."""
    identity = _matching_identity(wheel_sha256="0" * 64)
    mismatches = verify_pin(identity)
    assert any(m.field == "wheel_sha256" for m in mismatches)


def test_5_different_aggregate_identity_fails() -> None:
    """'sidecar cu alt aggregate identity -> fail': simulated at the pin level (a worker claiming a
    vendored_source_identity the pin doesn't expect)."""
    identity = _matching_identity(vendored_source_identity="sha256:" + "f" * 64)
    mismatches = verify_pin(identity)
    assert any(m.field == "vendored_source_identity" for m in mismatches)


def test_6_different_n3_or_n4_contract_fails() -> None:
    identity = _matching_identity(n3_contract_version="some-other-contract", n4_contract_version="some-other-contract")
    mismatches = verify_pin(identity)
    mismatched_fields = {m.field for m in mismatches}
    assert "n3_contract_version" in mismatched_fields
    assert "n4_contract_version" in mismatched_fields


def test_wrong_atr_source_commit_is_a_mismatch() -> None:
    """RT-TOWER-0010 (`ve_tower` 0.5.2): a worker claiming a different `market_state` source commit for
    ATR must fail closed -- the same discipline as every other exact-match identity field."""
    identity = _matching_identity(atr_source_commit="some-other-commit")
    mismatches = verify_pin(identity)
    assert any(m.field == "atr_source_commit" for m in mismatches)


def test_atr_source_commit_none_fails() -> None:
    identity = _matching_identity(atr_source_commit=None)
    mismatches = verify_pin(identity)
    assert any(m.field == "atr_source_commit" and m.actual is None for m in mismatches)


def test_wrong_ve_tower_package_version_is_a_mismatch() -> None:
    identity = _matching_identity(ve_tower_package_version="0.1.0")
    mismatches = verify_pin(identity)
    assert any(m.field == "ve_tower_package_version" for m in mismatches)


def test_wrong_package_build_commit_is_a_mismatch() -> None:
    """The CEO's own correction that `package_build_commit` is a distinct identity, never a catch-all
    source identity -- a mismatch here must be reported under exactly that field name."""
    identity = _matching_identity(package_build_commit="wrongcommit")
    mismatches = verify_pin(identity)
    assert any(
        m.field == "package_build_commit" and m.expected == tower_identity_pin.EXPECTED_PACKAGE_BUILD_COMMIT
        for m in mismatches
    )


def test_none_claimed_for_a_concrete_expected_field_is_a_mismatch() -> None:
    """A worker that honestly reports 'I don't know' for a field the pin expects a concrete value for
    must still be refused -- absence of a claim is not proof of anything, let alone a match."""
    identity = _matching_identity(ve_tower_package_version=None)
    mismatches = verify_pin(identity)
    assert any(m.field == "ve_tower_package_version" and m.actual is None for m in mismatches)


def test_state_delivery_commit_is_checked_as_its_own_separate_field() -> None:
    """CEO's own correction: state_delivery_commit is a SEPARATE identity from package_build_commit --
    a worker matching one but not the other must still fail."""
    identity = _matching_identity(state_delivery_commit="wrongstate")
    mismatches = verify_pin(identity)
    assert any(m.field == "state_delivery_commit" for m in mismatches)
    # package_build_commit itself still matches -- proving the two are checked independently
    assert not any(m.field == "package_build_commit" for m in mismatches)


def test_wrong_worker_package_version_is_a_mismatch() -> None:
    identity = _matching_identity(worker_package_version="0.1.0-old")
    mismatches = verify_pin(identity)
    assert any(m.field == "worker_package_version" for m in mismatches)


def test_wrong_protocol_version_is_a_mismatch() -> None:
    """An old worker still speaking protocol 1.0 must be refused."""
    identity = _matching_identity(protocol_version="1.0")
    mismatches = verify_pin(identity)
    assert any(m.field == "protocol_version" for m in mismatches)


def test_missing_worker_delivery_commit_is_a_mismatch() -> None:
    """worker_delivery_commit can only ever be checked for PRESENCE, not exact match (checking exact
    match would recreate the self-reference bug this pin-closure fixes) -- and it is explicitly
    DOCUMENTARY, never treated as a security identity. Absent must still fail closed."""
    identity = _matching_identity(worker_delivery_commit=None)
    mismatches = verify_pin(identity)
    assert any(m.field == "worker_delivery_commit" and m.actual is None for m in mismatches)


def test_worker_delivery_commit_is_never_exact_matched_any_non_null_value_passes() -> None:
    """Confirms the presence-only, DOCUMENTARY design explicitly: two DIFFERENT non-null
    worker_delivery_commit values both pass this specific check -- proving this field is deliberately not
    pinned to one hardcoded expected commit and is never used as a security identity."""
    identity_a = _matching_identity(worker_delivery_commit="commit-aaaa")
    identity_b = _matching_identity(worker_delivery_commit="commit-bbbb")
    assert not any(m.field == "worker_delivery_commit" for m in verify_pin(identity_a))
    assert not any(m.field == "worker_delivery_commit" for m in verify_pin(identity_b))


def test_artifact_fingerprint_is_not_a_worker_identity_field_at_all() -> None:
    """Per Red Team's own RT-TOWER-0004 finding: informational only, never part of pin/handshake
    verification. Confirmed structurally: WorkerIdentity carries no such field for verify_pin to check."""
    import dataclasses

    field_names = {f.name for f in dataclasses.fields(WorkerIdentity)}
    assert "artifact_fingerprint" not in field_names
