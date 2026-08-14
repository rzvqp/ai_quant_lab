"""`tower_identity_pin.verify_pin` tests -- the SECOND, independent verification the launcher performs
after the HMAC proves session possession: does the claimed identity actually match what AI Trader was told
to expect for `ve_tower` 0.3.0."""

from __future__ import annotations

from ai_trader.new_brain_bridge import tower_identity_pin
from ai_trader.new_brain_bridge.tower_identity_pin import verify_pin
from ai_trader.new_brain_bridge.tower_protocol import WorkerIdentity


def _matching_identity(**overrides: object) -> WorkerIdentity:
    fields: dict[str, object] = {
        "worker_package_version": tower_identity_pin.EXPECTED_WORKER_PACKAGE_VERSION,
        "worker_delivery_commit": "some-real-manifest-backed-commit",
        "protocol_version": tower_identity_pin.EXPECTED_PROTOCOL_VERSION,
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


def test_matching_identity_has_no_mismatches_beyond_the_disclosed_pending_fields() -> None:
    """Not a claim that the pin can pass today -- it genuinely cannot, by design, until VE's manifest
    supplies the 3 still-PENDING fields (see `test_pending_fields_always_fail_closed_today`). This proves
    everything ELSE the pin-closure fix added (worker_package_version, protocol_version,
    worker_delivery_commit presence) is satisfied by a genuinely correct identity, isolating exactly which
    fields remain blocked rather than a blanket, uninformative failure."""
    identity = _matching_identity()
    mismatched_fields = {m.field for m in verify_pin(identity)}
    assert mismatched_fields == {"vendored_source_identity", "n3_contract_version", "n4_contract_version"}


def test_wrong_worker_package_version_is_a_mismatch() -> None:
    """2026-08-14 pin-closure fix: this module's own docstring previously CLAIMED
    worker_package_version was checked -- it was not. Now it genuinely is."""
    identity = _matching_identity(worker_package_version="0.1.0-old")
    mismatches = verify_pin(identity)
    assert any(m.field == "worker_package_version" for m in mismatches)


def test_wrong_protocol_version_is_a_mismatch() -> None:
    """Same fix, for protocol_version -- an old worker still speaking protocol 1.0 must be refused."""
    identity = _matching_identity(protocol_version="1.0")
    mismatches = verify_pin(identity)
    assert any(m.field == "protocol_version" for m in mismatches)


def test_missing_worker_delivery_commit_is_a_mismatch() -> None:
    """worker_delivery_commit can only ever be checked for PRESENCE, not exact match (checking exact
    match would recreate the self-reference bug this pin-closure fixes) -- but presence absent must still
    fail closed."""
    identity = _matching_identity(worker_delivery_commit=None)
    mismatches = verify_pin(identity)
    assert any(m.field == "worker_delivery_commit" and m.actual is None for m in mismatches)


def test_worker_delivery_commit_is_never_exact_matched_any_non_null_value_passes() -> None:
    """Confirms the presence-only design explicitly: two DIFFERENT non-null worker_delivery_commit values
    both pass this specific check (whatever other checks might independently fail is irrelevant here) --
    proving this field is deliberately not pinned to one hardcoded expected commit."""
    identity_a = _matching_identity(worker_delivery_commit="commit-aaaa")
    identity_b = _matching_identity(worker_delivery_commit="commit-bbbb")
    assert not any(m.field == "worker_delivery_commit" for m in verify_pin(identity_a))
    assert not any(m.field == "worker_delivery_commit" for m in verify_pin(identity_b))
