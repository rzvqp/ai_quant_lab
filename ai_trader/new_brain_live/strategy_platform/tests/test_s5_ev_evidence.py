"""`s5_ev_evidence.py` unit tests -- mandate `VE-S5-REAL-EV-RUNTIME-PACKAGING-001` sections 6/16/17.

Covers: construction-time validation (mirrors `real_ev_engine.CostModel`'s own established pattern),
`to_expected_edge()` rendering, and the required tamper-test matrix (section 17) -- including an HONEST
disclosure of what is and is not mechanically detectable without Red Team's un-published fingerprint
canonicalization recipe (confirmed unavailable by direct inspection of both source reports; see
`s5_ev_evidence.py`'s own module docstring and `VE_S5_REAL_EV_RUNTIME_PACKAGING_REPORT.md`)."""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.new_brain_live.strategy_platform.real_ev_engine import _decode_probability_inputs
from ai_trader.new_brain_live.strategy_platform.s5_ev_evidence import (
    EVEvidenceIdentityError,
    S5_REAL_EV_EVIDENCE_V1,
    ValidatedEVEvidence,
)

_VALID_KWARGS: dict[str, object] = {
    "schema_version": "s5-ev-evidence-v1",
    "strategy_id": "s5_c_2d587447_opening_range_breakout_long", "strategy_version": "rep_7472f3d412f2",
    "implementation_fingerprint": "s5_opening_range_breakout.py-impl-v1", "config_fingerprint": "cfg-v1",
    "alpha_candidate": "C_2d587447", "representative": "7472f3d412f2",
    "validation_mandate": "RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001", "validation_commit": "633bd5da",
    "validation_verdict": "INDEPENDENT_VALIDATION_PASS", "validation_ledger_sha256": "cd4e8d4a...",
    "validation_ledger_n": 295,
    "population_id": "S5_S20_CLEAN_VALIDATION_POPULATION", "population_ohlc_sha256": "bac65b1a...",
    "population_timeline_sha256": "4c9ce7b7...", "population_bars": 52572,
    "cost_model_id": "AI_TRADER_SHADOW_COST_MODEL_v1", "cost_scenario": "STRESS", "round_trip_price": 0.24,
    "n": 295, "n_target": 15, "n_horizon": 196, "sum_horizon_r": 102.2125344478, "credibility": 0.80,
    "evidence_fingerprint": "9ca6e2bd...", "source_artifact_fingerprint": "ff1384a2...",
    "source_artifact_id": "S5_VALIDATED_EV_AGGREGATES_V1", "source_commit": "b4cb441",
}


def _make(**overrides: object) -> ValidatedEVEvidence:
    kwargs = {**_VALID_KWARGS, **overrides}
    return ValidatedEVEvidence(**kwargs)  # type: ignore[arg-type]


# ═══════════════════════════════════ construction-time validation ═══════════════════════════════════

def test_valid_construction_succeeds() -> None:
    ev = _make()
    assert ev.n_stop == 295 - 15 - 196 == 84


@pytest.mark.parametrize("field", [
    "strategy_id", "strategy_version", "implementation_fingerprint", "config_fingerprint",
    "validation_mandate", "validation_commit", "validation_verdict", "validation_ledger_sha256",
    "population_id", "population_ohlc_sha256", "population_timeline_sha256",
    "cost_model_id", "cost_scenario", "evidence_fingerprint", "source_artifact_fingerprint",
    "source_artifact_id", "source_commit",
])
def test_rejects_empty_identity_field(field: str) -> None:
    with pytest.raises(EVEvidenceIdentityError):
        _make(**{field: ""})


def test_rejects_bad_cost_scenario() -> None:
    with pytest.raises(EVEvidenceIdentityError):
        _make(cost_scenario="MEDIUM")


@pytest.mark.parametrize("field", ["n", "n_target", "n_horizon"])
def test_rejects_negative_count(field: str) -> None:
    with pytest.raises(EVEvidenceIdentityError):
        _make(**{field: -1})


def test_rejects_impossible_count_geometry_at_construction() -> None:
    """Defense in depth (mandate section 4): the SAME guard `_decode_probability_inputs` enforces at
    decode-time is ALSO enforced here, at construction-time -- a broken evidence module constant could
    never even finish importing."""
    with pytest.raises(EVEvidenceIdentityError):
        _make(n=10, n_target=8, n_horizon=9)  # Statistician's own exact repro (9cfcc5f section 15B)


@pytest.mark.parametrize("bad_sum", [float("nan"), float("inf"), float("-inf")])
def test_rejects_non_finite_sum_horizon_r_at_construction(bad_sum: float) -> None:
    with pytest.raises(EVEvidenceIdentityError):
        _make(sum_horizon_r=bad_sum)


@pytest.mark.parametrize("bad_cred", [0.0, 1.0, -0.1, 1.1, float("nan")])
def test_rejects_bad_credibility(bad_cred: float) -> None:
    with pytest.raises(EVEvidenceIdentityError):
        _make(credibility=bad_cred)


@pytest.mark.parametrize("bad_rt", [float("nan"), float("inf"), -0.01])
def test_rejects_bad_round_trip_price(bad_rt: float) -> None:
    with pytest.raises(EVEvidenceIdentityError):
        _make(round_trip_price=bad_rt)


def test_n_stop_always_derived_never_stored() -> None:
    """`n_stop` cannot be independently tampered -- it is a `@property`, not a field; there is no
    `dataclasses.replace(..., n_stop=...)` possible (frozen dataclass, no such field)."""
    ev = _make()
    assert not any(f.name == "n_stop" for f in dataclasses.fields(ev))
    assert ev.n_stop == ev.n - ev.n_target - ev.n_horizon


# ═══════════════════════════════════ to_expected_edge() rendering ═══════════════════════════════════

def test_to_expected_edge_decodes_successfully() -> None:
    edge = S5_REAL_EV_EVIDENCE_V1.to_expected_edge()
    pi = _decode_probability_inputs(edge)
    assert pi is not None
    cell = pi.hierarchy[0].cell
    assert (cell.n, cell.n_target, cell.n_horizon) == (295, 15, 196)
    assert cell.sum_horizon_R == pytest.approx(102.2125344478)


def test_to_expected_edge_carries_identity_binding_keys() -> None:
    edge = S5_REAL_EV_EVIDENCE_V1.to_expected_edge()
    assert edge["evidence_strategy_id"] == S5_REAL_EV_EVIDENCE_V1.strategy_id
    assert edge["evidence_config_fingerprint"] == S5_REAL_EV_EVIDENCE_V1.config_fingerprint
    assert edge["evidence_fingerprint"] == S5_REAL_EV_EVIDENCE_V1.evidence_fingerprint
    assert edge["evidence_fingerprint"] == "9ca6e2bd9884389b822518bed2341f7273288018187974c468016b20070593b4"
    assert edge["source_artifact_fingerprint"] == "ff1384a2fba6d37c859613887d89837bdd11a94614ade0a1ed034176653dddd4"


# ═══════════════════════════════════ tamper tests (mandate section 17) ═══════════════════════════════════
#
# HONEST DISCLOSURE (also stated in s5_ev_evidence.py's own module docstring and the implementation
# report): Red Team's own restamp report explicitly does not publish the canonicalization recipe for
# `evidence_fingerprint`/`source_artifact_fingerprint` -- this codebase cannot independently recompute
# either digest and does not attempt to. What IS mechanically detected: (a) a mutation that violates the
# count-geometry guard (n_target+n_horizon>n) -- caught by the SAME Defect-B hardening in
# `_decode_probability_inputs`; (b) nothing else, for a mutation that stays internally consistent. Per
# mandate section 17's own instruction ("do not generate a new valid fingerprint inside the consumer test
# merely to make mutated evidence pass"), this suite does NOT fabricate a passing re-verification -- it
# tests the real, disclosed boundary of what is and is not caught.

def test_tamper_n_target_breaking_geometry_is_detected() -> None:
    """Mutating n_target alone to violate n_target+n_horizon<=n IS caught -- by the geometry guard, not
    by any fingerprint re-verification (there is none)."""
    tampered_edge = dict(S5_REAL_EV_EVIDENCE_V1.to_expected_edge())
    tampered_edge["n_target"] = 200.0  # 200 + 196 = 396 > 295
    # evidence_fingerprint is deliberately left UNCHANGED (mandate section 17: do not mint a new one)
    assert _decode_probability_inputs(tampered_edge) is None


def test_tamper_n_alone_keeping_geometry_valid_is_not_detected() -> None:
    """DISCLOSED LIMITATION: mutating `n` alone, in a way that keeps n_target+n_horizon<=n satisfied,
    decodes successfully -- there is no cryptographic re-verification of `evidence_fingerprint` against
    the economic fields (the recipe is not published), so this class of tamper is NOT mechanically
    detected by this codebase. Documented here as a real, disclosed gap, not silently hidden -- see
    VE_S5_REAL_EV_RUNTIME_PACKAGING_REPORT.md's own tamper-test-results section."""
    tampered_edge = dict(S5_REAL_EV_EVIDENCE_V1.to_expected_edge())
    tampered_edge["n"] = 400.0  # 15 + 196 = 211 <= 400 -- still geometrically valid
    # evidence_fingerprint deliberately left UNCHANGED, per section 17's own instruction
    assert _decode_probability_inputs(tampered_edge) is not None  # NOT caught -- disclosed, not hidden


def test_tamper_sum_horizon_r_keeping_it_finite_is_not_detected() -> None:
    """Same disclosed limitation as above, for `sum_horizon_r`: any finite value decodes -- only
    non-finite values are caught (Defect A), not an arbitrary changed-but-finite one."""
    tampered_edge = dict(S5_REAL_EV_EVIDENCE_V1.to_expected_edge())
    tampered_edge["sum_horizon_r"] = 50.0  # a different, still-finite value
    assert _decode_probability_inputs(tampered_edge) is not None  # NOT caught -- disclosed, not hidden


def test_tamper_n_horizon_breaking_geometry_is_detected() -> None:
    tampered_edge = dict(S5_REAL_EV_EVIDENCE_V1.to_expected_edge())
    tampered_edge["n_horizon"] = 290.0  # 15 + 290 = 305 > 295
    assert _decode_probability_inputs(tampered_edge) is None
