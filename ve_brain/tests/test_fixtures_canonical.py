"""Fixture-uri CANONICE cu rezultate cunoscute (gate 7). Cazuri deterministe input→ieșire pentru motorul EV +
poarta N6. Rezultatele sunt reproductibile din cod semințat (stdlib-only)."""

from __future__ import annotations

import os
import sys

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

from ve_brain import (  # noqa: E402
    DecisionRequest, HierarchyLevel, INPUT_CONTRACT_ID, OutcomeCell, ProbabilityInputs, ValidationStatus, decide_n6,
)


def _req(*, rr: float, status: ValidationStatus, pt: int, ph: int, n: int, prob: bool = True,
         confirmation: bool = True) -> DecisionRequest:
    pi = None
    if prob:
        cell = OutcomeCell(n=n, n_target=pt, n_horizon=ph, sum_horizon_R=0.0)
        pi = ProbabilityInputs(hierarchy=(HierarchyLevel(cell=cell, siblings=(cell, cell)),), credibility=0.80)
    return DecisionRequest(
        contract_id=INPUT_CONTRACT_ID, strategy_id="fix", strategy_version="v1", validation_status=status,
        market_state_ref="ms", regime_label="TREND_UP", bias_direction="LONG", market_map_available=True,
        levels_available=True, confirmation_available=confirmation, entry_price=100.0, stop_price=99.0,
        target_kind="rr", target_param=rr, holding_window=10, atr=1.0, probability_inputs=pi,
        full_spread_price=0.05, entry_slippage_price=0.0, exit_slippage_price=0.0,
        measurement_contract_version="canonical-evaluator-v2.7.66-A2", configuration_fingerprint="fp")


# (descriere, request, decizie așteptată, reason așteptat)
CANONICAL_FIXTURES = [
    ("edge_puternic_RR3_pt0.5 → TRADE",   _req(rr=3.0, status=ValidationStatus.RATIFIED, pt=500, ph=200, n=1000),
     "TRADE", "TRADE_VALIDATED_EDGE"),
    ("shadow_același_edge → SHADOW",       _req(rr=3.0, status=ValidationStatus.SHADOW_ELIGIBLE, pt=500, ph=200, n=1000),
     "SHADOW_TRADE_CANDIDATE", "SHADOW_CANDIDATE_EV_POSITIVE"),
    ("RR mic (feasibility) → NO_TRADE",    _req(rr=0.001, status=ValidationStatus.RATIFIED, pt=500, ph=200, n=1000),
     "NO_TRADE", "NEGATIVE_EXPECTED_VALUE"),
    ("fără probabilități → NO_TRADE",      _req(rr=3.0, status=ValidationStatus.RATIFIED, pt=0, ph=0, n=0, prob=False),
     "NO_TRADE", "MISSING_PROBABILITY_INPUTS"),
    ("experimental → NO_ELIGIBLE",         _req(rr=3.0, status=ValidationStatus.EXPERIMENTAL, pt=500, ph=200, n=1000),
     "NO_TRADE", "NO_ELIGIBLE_STRATEGY"),
    ("fără confirmare N4 → NO_TRADE",      _req(rr=3.0, status=ValidationStatus.RATIFIED, pt=500, ph=200, n=1000,
                                               confirmation=False),
     "NO_TRADE", "MISSING_CONFIRMATION"),
    ("n=0 (probabilitate fabricată interzisă; EV fail-closed) → NO_TRADE",
     _req(rr=3.0, status=ValidationStatus.RATIFIED, pt=0, ph=0, n=0),
     "NO_TRADE", "MISSING_PROBABILITY_INPUTS"),   # motorul EV cade-închis la n<=0 → nu fabrică p̂=0.5
]


def test_canonical_fixtures_known_outcomes() -> None:
    for desc, req, want_decision, want_reason in CANONICAL_FIXTURES:
        resp = decide_n6(req)
        assert resp.decision == want_decision, f"{desc}: decizie {resp.decision} != {want_decision}"
        assert want_reason in resp.reason_codes, f"{desc}: reason {resp.reason_codes} nu conține {want_reason}"
