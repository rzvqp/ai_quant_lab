"""`tower_identity_pin.verify_pin` tests -- the SECOND, independent verification the launcher performs
after the HMAC proves session possession: does the claimed identity actually match what AI Trader was told
to expect for `ve_tower` 0.3.0."""

from __future__ import annotations

from ai_trader.new_brain_bridge import tower_identity_pin
from ai_trader.new_brain_bridge.tower_identity_pin import verify_pin
from ai_trader.new_brain_bridge.tower_protocol import WorkerIdentity


def _matching_identity(**overrides: object) -> WorkerIdentity:
    fields: dict[str, object] = {
        "worker_package_version": "0.2.0", "worker_build_commit": "abc123", "protocol_version": "2.0",
        "ve_tower_package_version": tower_identity_pin.EXPECTED_VE_TOWER_PACKAGE_VERSION,
        "package_build_commit": tower_identity_pin.EXPECTED_PACKAGE_BUILD_COMMIT,
        "state_delivery_commit": tower_identity_pin.EXPECTED_STATE_DELIVERY_COMMIT,
        "wheel_sha256": tower_identity_pin.EXPECTED_WHEEL_SHA256,
        "vendored_source_identity": "some-digest", "n3_contract_version": "1.0", "n4_contract_version": "1.0",
    }
    fields.update(overrides)
    return WorkerIdentity(**fields)  # type: ignore[arg-type]


def test_pending_fields_always_fail_closed_today() -> None:
    """CEO's own disclosed gap: `vendored_source_identity`/`n3_contract_version`/`n4_contract_version`
    have no supplied expected value yet -- `verify_pin` must never pass while any expected field is
    `None`, even if the worker's claim happens to look plausible."""
    identity = _matching_identity()
    mismatches = verify_pin(identity)
    mismatched_fields = {m.field for m in mismatches}
    assert "vendored_source_identity" in mismatched_fields
    assert "n3_contract_version" in mismatched_fields
    assert "n4_contract_version" in mismatched_fields


def test_wrong_ve_tower_package_version_is_a_mismatch() -> None:
    identity = _matching_identity(ve_tower_package_version="0.1.0")
    mismatches = verify_pin(identity)
    assert any(m.field == "ve_tower_package_version" for m in mismatches)


def test_wrong_package_build_commit_is_a_mismatch() -> None:
    """#3-adjacent: the CEO's own correction that `6daf2aa` is `package_build_commit`, not a catch-all
    source identity -- a mismatch here must be reported under exactly that field name."""
    identity = _matching_identity(package_build_commit="wrongcommit")
    mismatches = verify_pin(identity)
    assert any(m.field == "package_build_commit" and m.expected == "6daf2aa" for m in mismatches)


def test_wrong_wheel_sha256_is_a_mismatch() -> None:
    identity = _matching_identity(wheel_sha256="0" * 64)
    mismatches = verify_pin(identity)
    assert any(m.field == "wheel_sha256" for m in mismatches)


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
