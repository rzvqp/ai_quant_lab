"""Fixture-uri CANONICE cu rezultate cunoscute (gate 7), pe calea COMPLETĂ Router→EligibilityDecision→EV→N6, contra
CATALOGULUI SIGILAT încorporat. Deterministe, reproductibile din cod semințat."""

from __future__ import annotations

import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

import ve_brain.testing as vt  # noqa: E402
from ve_brain import (  # noqa: E402
    CANONICAL_STRATEGIES, DecisionRequest, ELIGIBILITY_POLICY_VERSION, HierarchyLevel, INPUT_CONTRACT_ID,
    N1_CONTRACT_VERSION, OutcomeCell, ProbabilityInputs, RAW_AXIS_SCHEMA_VERSION, ROUTER_VERSION, RawAxes,
    StrategyRouter, ValidationStatus, decide_n6, regime_fingerprint, strategy_policy_fingerprint,
)
from ve_brain.regime_routing import StrategyContract as SC  # noqa: E402

MC = "canonical-evaluator-v2.7.66-A2"
AXES = RawAxes(is_compressed=False, is_displacement=False, direction="up", structure="strong")   # {TREND_UP}

_CANON = {c.strategy_id: c for c in CANONICAL_STRATEGIES}
_BY_STATUS = {
    ValidationStatus.RATIFIED: _CANON["trend_pullback"],
    ValidationStatus.SHADOW_ELIGIBLE: _CANON["trend_shadow"],
    ValidationStatus.EXPERIMENTAL: _CANON["trend_experimental"],
}


@pytest.fixture(autouse=True)
def _canonical_catalog() -> None:
    vt.unlock_for_tests("VE-BRAIN-TEST-ONLY")
    vt.restore_production_catalog()


def _cand(c: SC, *, rr: float, prob: bool, confirmation: bool = True) -> DecisionRequest:
    pi = None
    if prob:
        cell = OutcomeCell(n=1000, n_target=500, n_horizon=200, sum_horizon_R=0.0)
        pi = ProbabilityInputs(hierarchy=(HierarchyLevel(cell=cell, siblings=(cell, cell)),), credibility=0.80)
    return DecisionRequest(
        contract_id=INPUT_CONTRACT_ID, strategy_id=c.strategy_id, strategy_version="v1",
        validation_status=c.validation_status, strategy_family=c.strategy_family,
        strategy_policy_fingerprint=strategy_policy_fingerprint(c), market_event_id="ev",
        regime_fingerprint=regime_fingerprint(AXES), market_state_ref="ms", regime_label="TREND_UP",
        bias_direction="LONG", market_map_available=True, levels_available=True, confirmation_available=confirmation,
        entry_price=100.0, stop_price=99.0, target_kind="rr", target_param=rr, holding_window=10, atr=1.0,
        probability_inputs=pi, full_spread_price=0.05, entry_slippage_price=0.0, exit_slippage_price=0.0,
        symbol="XAUUSD", timeframe="M15", block_start=0, block_end=100, segment_id="s", manifest_hash="m",
        n1_contract_version=N1_CONTRACT_VERSION, raw_axis_schema_version=RAW_AXIS_SCHEMA_VERSION,
        router_version=ROUTER_VERSION, eligibility_policy_version=ELIGIBILITY_POLICY_VERSION,
        measurement_contract_version=MC, configuration_fingerprint="rh")


def _decide(status: ValidationStatus, *, rr: float, prob: bool, confirmation: bool = True) -> object:
    c = _BY_STATUS[status]                                     # strategie din CATALOGUL SIGILAT (nu se înregistrează)
    elig = StrategyRouter((c,)).eligible(AXES, "ev", "LONG", 1.0)[0]
    return decide_n6(_cand(c, rr=rr, prob=prob, confirmation=confirmation), elig)


CANONICAL_FIXTURES = [
    ("edge RR3 pt0.5 → TRADE", ValidationStatus.RATIFIED, 3.0, True, True, "TRADE", "TRADE_VALIDATED_EDGE"),
    ("shadow → SHADOW", ValidationStatus.SHADOW_ELIGIBLE, 3.0, True, True,
     "SHADOW_TRADE_CANDIDATE", "SHADOW_CANDIDATE_EV_POSITIVE"),
    ("RR mic → NO_TRADE", ValidationStatus.RATIFIED, 0.001, True, True, "NO_TRADE", "NEGATIVE_EXPECTED_VALUE"),
    ("fără probabilități → NO_TRADE", ValidationStatus.RATIFIED, 3.0, False, True,
     "NO_TRADE", "MISSING_PROBABILITY_INPUTS"),
    ("experimental → NO_ELIGIBLE", ValidationStatus.EXPERIMENTAL, 3.0, True, True,
     "NO_TRADE", "NO_ELIGIBLE_STRATEGY"),
    ("fără confirmare → NO_TRADE", ValidationStatus.RATIFIED, 3.0, True, False, "NO_TRADE", "MISSING_CONFIRMATION"),
]


def test_canonical_fixtures_known_outcomes() -> None:
    for desc, status, rr, prob, conf, want_dec, want_reason in CANONICAL_FIXTURES:
        resp = _decide(status, rr=rr, prob=prob, confirmation=conf)
        assert resp.decision == want_dec, f"{desc}: {resp.decision} != {want_dec}"          # type: ignore[attr-defined]
        assert want_reason in resp.reason_codes, f"{desc}: {resp.reason_codes}"              # type: ignore[attr-defined]
