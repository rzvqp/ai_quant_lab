"""Tests for `real_ev_engine.py` (mandate VE-AI-TRADER-GENERIC-EV-AUTHORITY-001, sections 14/19).

Covers: unit/schema/artifact-identity tests, the fail-closed negative-test list (section 14) in full,
old-strategy (`ve_brain.decide_n6`) regression, the generic future-strategy fixture's positive AND negative
EV paths through the REAL engine, Mock/Real no-ambiguity, full shadow-pipeline integration, restart/dedup,
and a basic performance/latency measurement.

Run: python -m pytest ai_trader/new_brain_live/strategy_platform/tests/test_real_ev_engine.py -q
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import time
from pathlib import Path
from typing import Any, cast

import pytest
import ve_brain  # type: ignore[import-untyped]

from ai_trader.new_brain_live.market_state import MarketState, market_state_identity
from ai_trader.new_brain_live.strategy_platform.tests._fixtures import make_risk_execution_deps, real_trend_up_market_state
from ai_trader.new_brain_live.strategy_platform import pipeline
from ai_trader.new_brain_live.strategy_platform import reason_codes as rc
from ai_trader.new_brain_live.strategy_platform.catalog import CatalogEntry, StrategyCatalog, StrategyStatus
from ai_trader.new_brain_live.strategy_platform.dedup import already_processed
from ai_trader.new_brain_live.strategy_platform.ev_engine import (
    MOCK_EV_ENGINE_VERSION, NO_TRADE, TRADE_DECISION, MockEVDecisionEngine,
)
from ai_trader.new_brain_live.strategy_platform.future_strategy_fixture import (
    FUTURE_STRATEGY_CONFIG_FINGERPRINT,
    FUTURE_STRATEGY_VALIDATION_PROVENANCE,
    FutureValidatedStrategyNegativeEdge,
    FutureValidatedStrategyPositiveEdge,
    catalog_entry_for_future_strategy,
)
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import (
    REAL_EV_ENGINE_VERSION,
    CostModel,
    CostModelIdentityError,
    RealEVAuthorityError,
    RealEVDecisionEngine,
    _decode_probability_inputs,
    _parse_exit_specification,
)
from ai_trader.new_brain_live.strategy_platform.risk_execution_adapter import RiskExecutionDeps
from ai_trader.new_brain_live.strategy_platform.router import StrategyRouter
from ai_trader.new_brain_live.strategy_platform.shadow_ledger import ShadowLedger
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import StrategyEvaluationInput
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.signal_engine.types import Direction

_COST = CostModel(cost_model_id="test-cost-v1", full_spread_price=0.05, entry_slippage_price=0.02, exit_slippage_price=0.02)


def _catalog_and_state() -> tuple[
    MarketState, StrategyCatalog, FutureValidatedStrategyPositiveEdge, FutureValidatedStrategyNegativeEdge,
]:
    ms = real_trend_up_market_state()
    pos = FutureValidatedStrategyPositiveEdge()
    neg = FutureValidatedStrategyNegativeEdge()
    catalog = StrategyCatalog(entries=(catalog_entry_for_future_strategy(pos), catalog_entry_for_future_strategy(neg)))
    return ms, catalog, pos, neg


def _engine(catalog: StrategyCatalog, ms: MarketState) -> RealEVDecisionEngine:
    return RealEVDecisionEngine(catalog=catalog, market_state=ms, cost_model=_COST)


def _h(strategy: FutureValidatedStrategyPositiveEdge | FutureValidatedStrategyNegativeEdge,
      ms: MarketState) -> TradeHypothesis:
    """Both fixture strategies always produce a real hypothesis (never NO_SIGNAL) -- narrows
    `Strategy.evaluate`'s `TradeHypothesis | None` return type for mypy with an actual runtime assertion,
    not just a cast."""
    result = strategy.evaluate(StrategyEvaluationInput(market_state=ms, tower_context=None, config={}))
    assert result is not None, f"{strategy.strategy_id} must always produce a hypothesis, got NO_SIGNAL"
    return result


# ═══════════════════════════════════ unit / schema / artifact-identity ═══════════════════════════════════

def test_cost_model_rejects_empty_id() -> None:
    with pytest.raises(CostModelIdentityError):
        CostModel(cost_model_id="", full_spread_price=0.05, entry_slippage_price=0.02, exit_slippage_price=0.02)


@pytest.mark.parametrize("field", ["full_spread_price", "entry_slippage_price", "exit_slippage_price"])
def test_cost_model_rejects_nan_inf_negative(field: str) -> None:
    for bad in (float("nan"), float("inf"), float("-inf"), -0.01):
        kwargs: dict[str, Any] = dict(cost_model_id="t", full_spread_price=0.05, entry_slippage_price=0.02,
                                      exit_slippage_price=0.02)
        kwargs[field] = bad
        with pytest.raises(CostModelIdentityError):
            CostModel(**kwargs)


def test_engine_version_identity_distinct_from_mock() -> None:
    assert REAL_EV_ENGINE_VERSION != MOCK_EV_ENGINE_VERSION
    assert RealEVDecisionEngine(catalog=StrategyCatalog(entries=()), market_state=real_trend_up_market_state(),
                                cost_model=_COST).engine_version == REAL_EV_ENGINE_VERSION
    assert MockEVDecisionEngine().engine_version == MOCK_EV_ENGINE_VERSION


def test_parse_exit_specification() -> None:
    assert _parse_exit_specification("rr:2.5") == ("rr", 2.5)
    assert _parse_exit_specification("none") == ("none", None)
    assert _parse_exit_specification("time:40") == ("none", None)
    assert _parse_exit_specification("garbage") == (None, None)
    assert _parse_exit_specification("rr:notanumber") == (None, None)


def test_decode_probability_inputs_well_formed() -> None:
    edge: dict[str, float | str | None] = {
        "edge_schema": "real-ev-expected-edge-v1", "n": 200.0, "n_target": 110.0, "n_horizon": 60.0,
        "sum_horizon_r": 6.0, "credibility": 0.80,
    }
    pi = _decode_probability_inputs(edge)
    assert pi is not None
    assert pi.hierarchy[0].cell.n == 200
    assert pi.credibility == 0.80


@pytest.mark.parametrize("edge", [
    None, {}, {"edge_schema": "wrong-version"},
    {"edge_schema": "real-ev-expected-edge-v1", "n": "not_a_number", "n_target": 1, "n_horizon": 1, "sum_horizon_r": 1.0},
    {"edge_schema": "real-ev-expected-edge-v1", "n": 10, "n_target": 1, "n_horizon": 1, "sum_horizon_r": 1.0, "credibility": 1.5},
    {"mock_decision": "TRADE"},  # a MOCK-shaped edge must never be silently accepted as a REAL one
])
def test_decode_probability_inputs_rejects_malformed(edge: dict[str, Any] | None) -> None:
    assert _decode_probability_inputs(edge) is None


# ═══ fail-closed hardening (mandate VE-S5-REAL-EV-RUNTIME-PACKAGING-001 sections 3-5/16) -- both defects
# independently confirmed OPEN by the Statistician via direct execution of this exact function, section 15
# of STAT_S5_EV_AGGREGATE_RECONCILIATION_REPORT.md (commit 9cfcc5f) ═══

_BASE_EDGE: dict[str, float | str | None] = {
    "edge_schema": "real-ev-expected-edge-v1", "n": 295.0, "n_target": 15.0, "n_horizon": 196.0,
    "sum_horizon_r": 102.2125344478, "credibility": 0.80,
}


def test_decode_sane_baseline_still_accepted() -> None:
    """Sanity anchor: the exact Statistician-cited baseline (n=295/15/196/+102.2125) still decodes -- the
    hardening below must reject only genuinely bad inputs, never this one."""
    assert _decode_probability_inputs(dict(_BASE_EDGE)) is not None


@pytest.mark.parametrize("bad_sum", [float("nan"), float("inf"), float("-inf")])
def test_decode_rejects_non_finite_sum_horizon_r(bad_sum: float) -> None:
    """Defect A, reproduced with the Statistician's own exact repro shape (9cfcc5f section 15A)."""
    edge = {**_BASE_EDGE, "sum_horizon_r": bad_sum}
    assert _decode_probability_inputs(edge) is None


def test_decode_rejects_impossible_count_geometry_matches_statistician_repro() -> None:
    """Defect B, reproduced with the Statistician's OWN exact repro values (9cfcc5f section 15B):
    n=10, n_target=8, n_horizon=9 -> n_target+n_horizon=17 > n=10, implied n_stop=-7."""
    edge: dict[str, float | str | None] = {"edge_schema": "real-ev-expected-edge-v1", "n": 10.0, "n_target": 8.0,
                                            "n_horizon": 9.0, "sum_horizon_r": 1.0, "credibility": 0.80}
    assert _decode_probability_inputs(edge) is None


@pytest.mark.parametrize("field,value", [
    ("n_target", 296.0),   # n_target alone > n=295
    ("n_horizon", 296.0),  # n_horizon alone > n=295
])
def test_decode_rejects_single_count_exceeding_n(field: str, value: float) -> None:
    edge = {**_BASE_EDGE, field: value}
    assert _decode_probability_inputs(edge) is None


def test_decode_rejects_n_target_plus_n_horizon_exactly_one_over_n() -> None:
    """Boundary: n_target + n_horizon == n is VALID (n_stop == 0, a legitimate "never stopped out"
    population); == n + 1 must be rejected. Tests the boundary precisely, not just a grossly invalid case."""
    edge_ok = {**_BASE_EDGE, "n": 211.0, "n_target": 15.0, "n_horizon": 196.0}  # 15+196 == 211 exactly
    assert _decode_probability_inputs(edge_ok) is not None
    edge_bad = {**_BASE_EDGE, "n": 210.0, "n_target": 15.0, "n_horizon": 196.0}  # 15+196 == 211 > 210
    assert _decode_probability_inputs(edge_bad) is None


@pytest.mark.parametrize("field", ["n", "n_target", "n_horizon"])
def test_decode_rejects_negative_counts(field: str) -> None:
    edge = {**_BASE_EDGE, field: -1.0}
    assert _decode_probability_inputs(edge) is None


@pytest.mark.parametrize("field", ["n", "n_target", "n_horizon"])
def test_decode_rejects_fractional_counts(field: str) -> None:
    """Mandate section 5 -- a fractional count must be REJECTED, never silently truncated
    (`int(294.7) == 294` would otherwise corrupt the evidence without any signal)."""
    edge = {**_BASE_EDGE, field: 294.7}
    assert _decode_probability_inputs(edge) is None


@pytest.mark.parametrize("field", ["n", "n_target", "n_horizon"])
def test_decode_rejects_boolean_masquerading_as_count(field: str) -> None:
    """Mandate section 5 -- `bool` is a Python `int` subclass; `int(True) == 1` must not silently pass."""
    edge = {**_BASE_EDGE, field: True}
    assert _decode_probability_inputs(edge) is None


@pytest.mark.parametrize("bad_n", [float("inf"), float("-inf")])
def test_decode_rejects_non_finite_n_without_crashing(bad_n: float) -> None:
    """Pre-hardening, `int(float('inf'))` raises `OverflowError`, which the old `except (KeyError,
    TypeError, ValueError)` clause did NOT catch -- this would have CRASHED decide() instead of failing
    closed. Proves it now fails closed (returns None) instead of raising."""
    edge = {**_BASE_EDGE, "n": bad_n}
    assert _decode_probability_inputs(edge) is None  # must not raise


def test_decode_rejects_bool_credibility() -> None:
    edge = {**_BASE_EDGE, "credibility": True}
    assert _decode_probability_inputs(edge) is None


# ═══ evidence identity binding (mandate section 9) -- generic: exercised here via the pre-existing
# future-strategy fixture, no S5-specific code anywhere in real_ev_engine.py or this test ═══

def test_evidence_without_identity_keys_is_unaffected_backward_compat() -> None:
    """The pre-existing fixture's edge (5 keys only, no evidence_* keys) must decide EXACTLY as it did
    before this mandate -- proves the new identity-binding check is opt-in, not a regression."""
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    assert not any(k.startswith("evidence_") for k in (h.expected_edge or {}))
    d = _engine(catalog, ms).decide(h)
    assert d.decision == TRADE_DECISION
    assert d.evidence_fingerprint == ""  # no evidence package declared -> "" (mandate section 20/23)


@pytest.mark.parametrize("field,bad_value", [
    ("evidence_strategy_id", "not-the-real-strategy-id"),
    ("evidence_strategy_version", "not-the-real-version"),
    ("evidence_implementation_fingerprint", "TAMPERED-IMPL-FINGERPRINT"),
    ("evidence_config_fingerprint", "TAMPERED-CONFIG-FINGERPRINT"),
])
def test_evidence_identity_mismatch_fails_closed(field: str, bad_value: str) -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    entry = catalog.lookup(pos.strategy_id, pos.strategy_version)
    assert entry is not None
    tampered_edge = {
        **(h.expected_edge or {}), "evidence_strategy_id": entry.strategy_id,
        "evidence_strategy_version": entry.strategy_version,
        "evidence_implementation_fingerprint": entry.implementation_fingerprint,
        "evidence_config_fingerprint": entry.config_fingerprint,
        field: bad_value,  # tamper exactly one binding field
    }
    tampered = dataclasses.replace(h, expected_edge=tampered_edge)
    d = _engine(catalog, ms).decide(tampered)
    assert d.decision == NO_TRADE
    assert d.reason_codes == (rc.EVIDENCE_IDENTITY_MISMATCH,)


@pytest.mark.parametrize("field,bad_value", [
    ("evidence_cost_model_id", "not-the-real-cost-model-id"),
    ("evidence_round_trip_price", 999.0),
])
def test_evidence_cost_identity_mismatch_fails_closed(field: str, bad_value: float | str) -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    tampered_edge: dict[str, float | str | None] = {
        **(h.expected_edge or {}), "evidence_cost_model_id": _COST.cost_model_id,
        "evidence_round_trip_price": _COST.full_spread_price + _COST.entry_slippage_price + _COST.exit_slippage_price,
        field: bad_value,
    }
    tampered = dataclasses.replace(h, expected_edge=tampered_edge)
    d = _engine(catalog, ms).decide(tampered)
    assert d.decision == NO_TRADE
    assert d.reason_codes == (rc.EVIDENCE_COST_IDENTITY_MISMATCH,)


def test_evidence_identity_matching_all_fields_still_reaches_trade_decision() -> None:
    """Positive control for the two tests above: correctly-bound evidence identity (matching the real
    catalog entry and cost model exactly) must NOT be rejected -- proves the check is a real gate, not one
    that rejects everything."""
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    entry = catalog.lookup(pos.strategy_id, pos.strategy_version)
    assert entry is not None
    bound_edge = {
        **(h.expected_edge or {}), "evidence_strategy_id": entry.strategy_id,
        "evidence_strategy_version": entry.strategy_version,
        "evidence_implementation_fingerprint": entry.implementation_fingerprint,
        "evidence_config_fingerprint": entry.config_fingerprint,
        "evidence_cost_model_id": _COST.cost_model_id,
        "evidence_round_trip_price": _COST.full_spread_price + _COST.entry_slippage_price + _COST.exit_slippage_price,
        "evidence_fingerprint": "test-evidence-fp-abc123",
    }
    bound = dataclasses.replace(h, expected_edge=bound_edge)
    d = _engine(catalog, ms).decide(bound)
    assert d.decision == TRADE_DECISION
    assert d.evidence_fingerprint == "test-evidence-fp-abc123"  # propagated for audit (section 20/23)


# ═══════════════════════════════════ fail-closed: admission (mandate section 14) ═══════════════════════════════════

def test_unknown_strategy_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    empty_catalog = StrategyCatalog(entries=())
    d = _engine(empty_catalog, ms).decide(h)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.UNKNOWN_STRATEGY,)


def test_wrong_strategy_fingerprint_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    tampered = dataclasses.replace(h, strategy_config_fingerprint="TAMPERED-FINGERPRINT")
    d = _engine(catalog, ms).decide(tampered)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.STRATEGY_POLICY_MISMATCH,)


def test_wrong_strategy_version_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    tampered = dataclasses.replace(h, strategy_version="v999_never_registered")
    d = _engine(catalog, ms).decide(tampered)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.UNKNOWN_STRATEGY,)


@pytest.mark.parametrize("status", [StrategyStatus.MOCK_TEST_ONLY, StrategyStatus.RESEARCH_ONLY,
                                    StrategyStatus.ALPHA_CANDIDATE, StrategyStatus.DISABLED, StrategyStatus.RETIRED])
def test_unvalidated_status_no_trade(status: StrategyStatus) -> None:
    ms, _, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    entry = CatalogEntry(
        strategy_id=pos.strategy_id, strategy_version=pos.strategy_version, status=status, enabled=True,
        allowed_instruments=("XAUUSD",), allowed_directions=("LONG", "SHORT"), context_eligibility=None,
        implementation_fingerprint="impl-v1", config_fingerprint=FUTURE_STRATEGY_CONFIG_FINGERPRINT,
        validation_provenance=(FUTURE_STRATEGY_VALIDATION_PROVENANCE if status not in
                               (StrategyStatus.MOCK_TEST_ONLY, StrategyStatus.RESEARCH_ONLY, StrategyStatus.ALPHA_CANDIDATE)
                               else None),
        risk_contract_reference="risk_manager_live-v1", rollback_identity="rollback-v1", strategy=pos,
    )
    catalog = StrategyCatalog(entries=(entry,))
    d = _engine(catalog, ms).decide(h)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.NO_ELIGIBLE_STRATEGY,)


def test_strategy_disabled_no_trade() -> None:
    ms, _, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    entry = catalog_entry_for_future_strategy(pos)
    disabled_entry = dataclasses.replace(entry, enabled=False)
    catalog = StrategyCatalog(entries=(disabled_entry,))
    d = _engine(catalog, ms).decide(h)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.STRATEGY_DISABLED,)


# ═══════════════════════════════════ fail-closed: MarketState (section 14) ═══════════════════════════════════

def test_missing_market_state_atr_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    broken_ms = dataclasses.replace(ms, atr=None)
    d = _engine(catalog, broken_ms).decide(h)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.MARKET_STATE_INVALID,)


def test_missing_market_state_entry_price_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    broken_ms = dataclasses.replace(ms, entry_price=None)
    d = _engine(catalog, broken_ms).decide(h)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.MARKET_STATE_MISMATCH,) or d.reason_codes == (rc.MARKET_STATE_INVALID,)


def test_wrong_market_state_identity_no_trade() -> None:
    """A hypothesis produced from a DIFFERENT MarketState than the one this engine cycle is holding. The
    fixture builder (`real_trend_up_market_state`) is a pure, deterministic function over fixed synthetic
    bars -- two calls produce byte-identical `context_id`s, so a genuinely different identity is
    constructed directly rather than hoped for via a second builder call."""
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    mismatched = dataclasses.replace(h, market_state_identity="deliberately-different-context-id")
    d = _engine(catalog, ms).decide(mismatched)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.MARKET_STATE_MISMATCH,)


def test_incompatible_n1_contract_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    bad_axes = dataclasses.replace(ms.axes, n1_contract_version="some-other-n1-contract-v2")
    bad_ms = dataclasses.replace(ms, axes=bad_axes)
    # market_state_identity depends on n1_output_fp, not axes.n1_contract_version directly, so the hypothesis
    # (built against the ORIGINAL ms) still matches bad_ms's identity -- isolating the N1-contract check alone
    h_matching = dataclasses.replace(h, market_state_identity=market_state_identity(bad_ms))
    d = _engine(catalog, bad_ms).decide(h_matching)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.INCOMPATIBLE_N1_CONTRACT,)


# ═══════════════════════════════════ fail-closed: hypothesis schema / geometry (section 14) ═══════════════════════════════════

def test_nan_intended_entry_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    tampered = dataclasses.replace(h, intended_entry=float("nan"), invalidation=float("nan") - 1)
    # TradeHypothesis.__post_init__'s own LONG/SHORT geometry check uses >=/<= comparisons that are always
    # False against NaN, so construction itself would not raise here -- but dataclasses.replace re-runs
    # __post_init__, and NaN comparisons make the LONG invalidation<entry check trivially pass (False < False
    # is not evaluated the same way); guard by catching either outcome, since either is an acceptable proof
    # that a NaN geometry never reaches TRADE_DECISION.
    try:
        d = _engine(catalog, ms).decide(tampered)
    except ValueError:
        return  # TradeHypothesis itself refused construction -- also an acceptable fail-closed outcome
    assert d.decision == NO_TRADE


def test_inf_invalidation_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    tampered = dataclasses.replace(h, invalidation=float("-inf"))  # still satisfies LONG's invalidation<entry
    d = _engine(catalog, ms).decide(tampered)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.SCHEMA_VALIDATION_FAILED,)


def test_invalid_sl_tp_geometry_rejected_at_hypothesis_construction() -> None:
    """TradeHypothesis.__post_init__ itself is the fail-closed gate for LONG/SHORT SL/TP ordering -- proving
    invalid geometry can never even become an EVDecisionEngine input in the first place."""
    with pytest.raises(ValueError):
        TradeHypothesis(
            strategy_id="X", strategy_version="v1", instrument="XAUUSD", direction=Direction.LONG,
            signal_timestamp=0, eligible_entry_timestamp=0, entry_type="MARKET", intended_entry=100.0,
            invalidation=101.0,  # LONG requires invalidation < intended_entry -- this is backwards
            exit_specification="none", max_hold=1, expected_edge=None, reason_codes=("X",),
            market_state_identity="x", strategy_config_fingerprint="x", research_validation_identity=None,
            provenance="test",
        )


def test_expired_hypothesis_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    premature = dataclasses.replace(h, eligible_entry_timestamp=ms.market_timestamp + 10_000)
    d = _engine(catalog, ms).decide(premature)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.SCHEMA_VALIDATION_FAILED,)


def test_missing_probability_inputs_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    no_edge = dataclasses.replace(h, expected_edge=None)
    d = _engine(catalog, ms).decide(no_edge)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.MISSING_PROBABILITY_INPUTS,)


def test_invalid_target_kind_no_trade() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    tampered = dataclasses.replace(h, exit_specification="not_a_valid_spec_at_all")
    d = _engine(catalog, ms).decide(tampered)
    assert d.decision == NO_TRADE and d.reason_codes == (rc.SCHEMA_VALIDATION_FAILED,)


# ═══════════════════════════════════ fail-closed: EV authority installation / tampering (section 14) ═══════════════════════════════════

def test_tampered_ve_brain_version_fails_closed_at_construction() -> None:
    ms, catalog, _, _ = _catalog_and_state()
    real_version = ve_brain.VE_BRAIN_VERSION
    ve_brain.VE_BRAIN_VERSION = "9.9.9-tampered"
    try:
        with pytest.raises(RealEVAuthorityError):
            RealEVDecisionEngine(catalog=catalog, market_state=ms, cost_model=_COST)
    finally:
        ve_brain.VE_BRAIN_VERSION = real_version


def test_missing_ev_authority_fails_closed() -> None:
    ms, catalog, _, _ = _catalog_and_state()
    real_version = ve_brain.VE_BRAIN_VERSION
    ve_brain.VE_BRAIN_VERSION = None  # simulates an uninstalled/unreadable artifact
    try:
        with pytest.raises(RealEVAuthorityError):
            RealEVDecisionEngine(catalog=catalog, market_state=ms, cost_model=_COST)
    finally:
        ve_brain.VE_BRAIN_VERSION = real_version


def test_mock_and_real_engine_versions_never_collide_in_the_ledger() -> None:
    """Section 10 -- no ambiguity: whichever engine ACTUALLY ran is what the ledger's fingerprints record,
    proven by running one cycle with each and comparing the recorded ev_engine_version field."""
    ms, catalog, pos, _ = _catalog_and_state()
    mock_engine = MockEVDecisionEngine()
    real_engine = _engine(catalog, ms)
    assert mock_engine.engine_version != real_engine.engine_version
    fp_mock = pipeline._fingerprints(ms, ev_engine_version=mock_engine.engine_version)
    fp_real = pipeline._fingerprints(ms, ev_engine_version=real_engine.engine_version)
    assert fp_mock.ev_engine_version == MOCK_EV_ENGINE_VERSION
    assert fp_real.ev_engine_version == REAL_EV_ENGINE_VERSION


# ═══════════════════════════════════ positive / negative EV paths through the REAL engine (section 13) ═══════════════════════════════════

def test_future_strategy_positive_edge_reaches_real_trade_decision() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    h = _h(pos, ms)
    d = _engine(catalog, ms).decide(h)
    assert d.decision == TRADE_DECISION
    assert d.reason_codes == (rc.REAL_EV_VALIDATED_EDGE,)


def test_future_strategy_negative_edge_reaches_real_no_trade() -> None:
    ms, catalog, _, neg = _catalog_and_state()
    h = _h(neg, ms)
    d = _engine(catalog, ms).decide(h)
    assert d.decision == NO_TRADE
    assert d.reason_codes == (rc.NEGATIVE_EXPECTED_VALUE,)


def _strip_leading_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        return body[1:]
    return body


class _DocstringStripper(ast.NodeTransformer):
    """Strips the leading bare-string `Expr` (the docstring) from the module itself AND every
    function/async-function/class def anywhere in the tree -- not just the module's own top-level one.
    Explanatory prose (module OR function/class docstrings) legitimately names strategy ids/mandate ids
    when documenting why this module is unrelated to them; only executable logic is checked below."""

    def _visit_body_owner(self, node: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> ast.AST:
        self.generic_visit(node)
        node.body = _strip_leading_docstring(node.body)
        return node

    def visit_Module(self, node: ast.Module) -> ast.AST:
        return self._visit_body_owner(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        return self._visit_body_owner(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        return self._visit_body_owner(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        return self._visit_body_owner(node)


def _strip_all_docstrings(tree: ast.AST) -> ast.AST:
    # NodeTransformer.visit() is typed Any in typeshed (visitor return type is inherently dynamic) --
    # cast, don't silently let Any escape this function's own declared -> ast.AST return type.
    return cast(ast.AST, ast.fix_missing_locations(_DocstringStripper().visit(tree)))


def test_no_strategy_id_branch_exists_in_real_ev_engine_source() -> None:
    """Mechanical proof (not just a claim) that no strategy-specific branch exists: grep the real module's
    own CODE (every docstring excluded -- module, function, AND class -- since explanatory prose
    legitimately discusses these names, which is expected and correct to document, not a branch) for the
    fixture/mock strategy id literals -- they must not appear anywhere a real conditional branch could
    reference them."""
    import ai_trader.new_brain_live.strategy_platform.real_ev_engine as mod
    tree = ast.parse(inspect.getsource(mod))
    code_without_docstring = ast.unparse(_strip_all_docstrings(tree))
    for forbidden in ("FIXTURE_FUTURE_VALIDATED_STRATEGY", "MOCK_LONG_ON_FIXED_FIXTURE", "trend_pullback",
                     "range_fade", "trend_shadow", "trend_experimental", "S5"):
        assert forbidden not in code_without_docstring, \
            f"real_ev_engine.py's CODE must contain no strategy-specific reference to {forbidden!r}"


# ═══════════════════════════════════ old-strategy (ve_brain.decide_n6) regression (section 12) ═══════════════════════════════════

def _n6_probe(strategy_id: str, strategy_version: str, canon: "ve_brain.StrategyContract") -> tuple[str, tuple[str, ...]]:
    """Direct, minimal, deterministic decide_n6 probe -- byte-identical geometry/inputs regardless of this
    mandate's changes (ve_brain itself is never imported by anything this mandate modifies for this path)."""
    fp_stub = "0" * 16
    req = ve_brain.DecisionRequest(
        contract_id=ve_brain.INPUT_CONTRACT_ID, strategy_id=strategy_id, strategy_version=strategy_version,
        validation_status=canon.validation_status, strategy_family=canon.strategy_family,
        strategy_policy_fingerprint=ve_brain.strategy_policy_fingerprint(canon),
        market_event_id="regression-probe-event", regime_fingerprint=fp_stub,
        market_state_ref="regression-probe-ms", regime_label="strong", bias_direction="up",
        market_map_available=True, levels_available=True, confirmation_available=True,
        entry_price=100.0, stop_price=98.0, target_kind="rr", target_param=2.5, holding_window=20,
        atr=1.0, probability_inputs=None, full_spread_price=0.05, entry_slippage_price=0.02, exit_slippage_price=0.02,
        symbol="XAUUSD", timeframe="M15", block_start=0, block_end=0, segment_id="probe", manifest_hash="probe",
        n1_contract_version=ve_brain.N1_CONTRACT_VERSION, raw_axis_schema_version="raw-axis-v1",
        router_version="router-v1", eligibility_policy_version="eligibility-v1",
        measurement_contract_version=ve_brain.MEASUREMENT_CONTRACT_VERSION, configuration_fingerprint="probe-cfg-fp",
    )
    elig = ve_brain.EligibilityDecision(
        strategy_id=strategy_id, strategy_version=strategy_version, market_event_id="regression-probe-event",
        regime_fingerprint=fp_stub, router_version=ve_brain.ROUTER_VERSION, eligible=True,
        mode=ve_brain.RoutingMode.NORMAL, matched_regimes=(), reason_codes=(),
    )
    resp = ve_brain.decide_n6(req, elig)
    return resp.decision, resp.reason_codes


@pytest.mark.parametrize("strategy_id,strategy_version", [
    ("trend_pullback", "v1"), ("range_fade", "v1"), ("trend_shadow", "v1"), ("trend_experimental", "v1"),
])
def test_ve_brain_decide_n6_four_strategies_unchanged(strategy_id: str, strategy_version: str) -> None:
    """Regression (section 12): this mandate touches nothing in ve_brain -- decide_n6's own 4 sealed
    strategies must behave EXACTLY as they did before this mandate. Missing probability_inputs (None) is
    used deliberately so every strategy resolves at or before the EV step, keeping this probe about
    catalog/range-block/eligibility resolution, not EV math specifics."""
    canon = next(c for c in ve_brain.CANONICAL_STRATEGIES if c.strategy_id == strategy_id)
    decision, reasons = _n6_probe(strategy_id, strategy_version, canon)
    if strategy_id == "range_fade":
        assert (decision, reasons) == ("NO_TRADE", ("TRUE_RANGE_NOT_IDENTIFIABLE",))
    elif strategy_id == "trend_experimental":
        assert (decision, reasons) == ("NO_TRADE", ("NO_ELIGIBLE_STRATEGY",))
    elif strategy_id in ("trend_pullback", "trend_shadow"):
        assert decision == "NO_TRADE" and reasons == ("MISSING_PROBABILITY_INPUTS",)


def test_real_ev_engine_module_never_imports_or_calls_decide_n6() -> None:
    """Every docstring excluded -- module, function, AND class (it explains, in prose, that
    ve_brain.decide_n6 exists and why this module deliberately does not call it -- documenting that is
    correct; the CODE itself must never reference it)."""
    import ai_trader.new_brain_live.strategy_platform.real_ev_engine as mod
    tree = ast.parse(inspect.getsource(mod))
    code_without_docstring = ast.unparse(_strip_all_docstrings(tree))
    assert "decide_n6" not in code_without_docstring, \
        "real_ev_engine.py's CODE must never reference ve_brain.decide_n6 -- separate path"


# ═══════════════════════════════════ full shadow-pipeline integration (section 16) ═══════════════════════════════════

def test_full_shadow_pipeline_real_trade_decision_blocked_at_broker_gate(tmp_path: Path) -> None:
    ms, _, pos, _ = _catalog_and_state()
    only_pos_catalog = StrategyCatalog(entries=(catalog_entry_for_future_strategy(pos),))
    engine = _engine(only_pos_catalog, ms)
    store = SqliteStateStore(db_path=str(tmp_path / "ledger.db"))
    ledger = ShadowLedger(state_store=store, log_name="test_real_ev_integration")
    deps = RiskExecutionDeps(**make_risk_execution_deps())  # type: ignore[arg-type]
    result = pipeline.run_cycle(
        market_state=ms, catalog=only_pos_catalog, ev_engine=engine, risk_execution_deps=deps, ledger=ledger,
        router=StrategyRouter(),
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.final_reason_codes == (rc.BROKER_DISABLED,)
    assert result.record.ev_decisions == ((pos.strategy_id, TRADE_DECISION, ""),)  # "" -- no evidence package (mandate VE-S5-REAL-EV-RUNTIME-PACKAGING-001)
    assert result.record.broker_submission_state.startswith("BLOCKED_AT_GATE:")
    assert result.record.fingerprints.ev_engine_version == REAL_EV_ENGINE_VERSION  # the FIX under test


def test_full_shadow_pipeline_negative_edge_no_trade(tmp_path: Path) -> None:
    ms, catalog, _, neg = _catalog_and_state()
    only_neg_catalog = StrategyCatalog(entries=(catalog_entry_for_future_strategy(neg),))
    engine = _engine(only_neg_catalog, ms)
    store = SqliteStateStore(db_path=str(tmp_path / "ledger.db"))
    ledger = ShadowLedger(state_store=store, log_name="test_real_ev_negative")
    deps = RiskExecutionDeps(**make_risk_execution_deps())  # type: ignore[arg-type]
    result = pipeline.run_cycle(
        market_state=ms, catalog=only_neg_catalog, ev_engine=engine, risk_execution_deps=deps, ledger=ledger,
        router=StrategyRouter(),
    )
    assert result.record.final_decision == "NO_TRADE"
    assert result.record.ev_decisions == ((neg.strategy_id, NO_TRADE, ""),)  # "" -- no evidence package (mandate VE-S5-REAL-EV-RUNTIME-PACKAGING-001)
    assert result.record.fingerprints.ev_engine_version == REAL_EV_ENGINE_VERSION


# ═══════════════════════════════════ restart / dedup (section 17) ═══════════════════════════════════

def test_restart_replay_never_reprocesses_and_ledger_stays_consistent(tmp_path: Path) -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    db_path = str(tmp_path / "ledger.db")
    deps = RiskExecutionDeps(**make_risk_execution_deps())  # type: ignore[arg-type]

    store1 = SqliteStateStore(db_path=db_path)
    ledger1 = ShadowLedger(state_store=store1, log_name="test_restart")
    engine1 = _engine(catalog, ms)
    result1 = pipeline.run_cycle(market_state=ms, catalog=catalog, ev_engine=engine1, risk_execution_deps=deps,
                                 ledger=ledger1, router=StrategyRouter())
    assert result1.duplicate is False
    n_after_first = len(ledger1.entries)

    # simulate a restart: fresh store/ledger objects pointed at the SAME db_path, fresh engine instance
    store2 = SqliteStateStore(db_path=db_path)
    ledger2 = ShadowLedger(state_store=store2, log_name="test_restart")
    assert already_processed(ledger2, market_state_identity=market_state_identity(ms))
    engine2 = _engine(catalog, ms)
    result2 = pipeline.run_cycle(market_state=ms, catalog=catalog, ev_engine=engine2, risk_execution_deps=deps,
                                 ledger=ledger2, router=StrategyRouter())
    assert result2.duplicate is True
    assert result2.record == result1.record
    assert len(ledger2.entries) == n_after_first  # no new row written for the replay


def test_hypothesis_dedup_key_deterministic_across_identical_inputs() -> None:
    ms, _, pos, _ = _catalog_and_state()
    h1 = _h(pos, ms)
    h2 = _h(pos, ms)
    assert h1.dedup_key == h2.dedup_key


# ═══════════════════════════════════ performance (section 18) ═══════════════════════════════════

def test_decide_latency_is_not_pathological() -> None:
    ms, catalog, pos, _ = _catalog_and_state()
    engine = _engine(catalog, ms)
    h = _h(pos, ms)
    n = 200
    t0 = time.perf_counter()
    for _ in range(n):
        engine.decide(h)
    elapsed = time.perf_counter() - t0
    per_call_ms = (elapsed / n) * 1000
    assert per_call_ms < 5.0, f"decide() averaged {per_call_ms:.3f}ms/call over {n} calls -- investigate before shipping"
