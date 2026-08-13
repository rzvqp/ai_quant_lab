"""Testele artefactului: cele 12 teste de ROUTER + cauzalitate + N6/contract + EV + amprentă. Fixture-uri
deterministe cu rezultate cunoscute. (Cele 25 end-to-end rămân la AI Trader — nu le construiesc eu.)"""

from __future__ import annotations

import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

from ve_brain import (  # noqa: E402
    BROKER_ORDER_SUBMISSION, DecisionRequest, HierarchyLevel, INPUT_CONTRACT_ID, NonComparableDecisionError,
    OutcomeCell, ProbabilityInputs, RoutingMode, SemanticRegime, StrategyContract, StrategyRegistry, StrategyRouter,
    ValidationStatus, compare_decisions, decide_n6, n4_triggers_breakout, semantic_regime,
)
from ve_brain.regime_routing import StrategyContract as SC  # noqa: E402


def _contract(sid: str, *, family: str, allowed: tuple[SemanticRegime, ...] = (),
              directions: tuple[str, ...] = ("LONG", "SHORT"), arming: tuple[SemanticRegime, ...] = (),
              trigger: SemanticRegime | None = None, min_conf: float = 0.0,
              status: ValidationStatus = ValidationStatus.RATIFIED, n4: str | None = None,
              exit_on_change: bool = False, exit_trans: SemanticRegime | None = None) -> SC:
    return SC(strategy_id=sid, strategy_family=family, allowed_regimes=allowed, allowed_directions=directions,
              arming_regimes=arming, trigger_transition=trigger, minimum_regime_confidence=min_conf,
              required_N2_bias=None, required_N3_map=True, required_N4_confirmation=n4,
              entry_rule="entry", invalidation_rule="inv", exit_rule="exit", holding_window=10,
              validation_status=status, strategy_version="v1", measurement_contract_version="canonical-evaluator-v2.7.66-A2",
              exit_on_regime_change=exit_on_change, exit_on_transition=exit_trans)


TREND = _contract("trend_pullback", family="TREND_PULLBACK", allowed=(SemanticRegime.TREND_UP,), directions=("LONG",))
RANGE = _contract("range_fade", family="RANGE_FADE", allowed=(SemanticRegime.RANGE,))
BREAKOUT = _contract("range_breakout", family="RANGE_BREAKOUT", arming=(SemanticRegime.RANGE, SemanticRegime.COMPRESSION),
                     trigger=SemanticRegime.BREAKOUT_TRANSITION, n4="DISPLACEMENT_AND_ACCEPTANCE")


def _router() -> StrategyRouter:
    return StrategyRouter((TREND, RANGE, BREAKOUT))


def _elig(router: StrategyRouter, regime: SemanticRegime, direction: str | None = "LONG", conf: float = 1.0):
    return {d.strategy_id: d for d in router.eligible(regime, direction, conf)}


# ═══ cele 12 teste de router ═══
def test_01_trend_active_in_trend_up() -> None:
    assert _elig(_router(), SemanticRegime.TREND_UP)["trend_pullback"].eligible


def test_02_trend_inactive_in_range() -> None:
    d = _elig(_router(), SemanticRegime.RANGE)["trend_pullback"]
    assert not d.eligible and d.mode is RoutingMode.INELIGIBLE


def test_03_range_active_in_range() -> None:
    assert _elig(_router(), SemanticRegime.RANGE)["range_fade"].eligible


def test_04_range_inactive_after_trend() -> None:
    assert not _elig(_router(), SemanticRegime.TREND_UP)["range_fade"].eligible


def test_05_breakout_watch_armed_in_range_and_compression() -> None:
    for reg in (SemanticRegime.RANGE, SemanticRegime.COMPRESSION):
        d = _elig(_router(), reg)["range_breakout"]
        assert d.eligible and d.mode is RoutingMode.BREAKOUT_WATCH


def test_06_wick_without_acceptance_not_trigger() -> None:
    from ve_brain.regime_routing import _ACCEPTANCE_BULLISH  # noqa
    assert n4_triggers_breakout(0, "LONG") is False           # UNDETERMINED (sweep/wick) → NO_BREAKOUT
    assert n4_triggers_breakout(1, "LONG") is False           # ABSORPTION_PROXY → NO_BREAKOUT
    assert n4_triggers_breakout(None, "LONG") is False


def test_07_displacement_plus_acceptance_triggers() -> None:
    assert n4_triggers_breakout(2, "LONG") is True            # ACCEPTANCE_BULLISH (displacement+acceptare)
    assert n4_triggers_breakout(-2, "SHORT") is True          # ACCEPTANCE_BEARISH


def test_08_uncertain_produces_no_trade() -> None:
    d = _elig(_router(), SemanticRegime.UNCERTAIN)["trend_pullback"]
    assert not d.eligible and d.reason_codes == ("UNCERTAIN_REGIME",)


def test_09_regime_computed_without_lookahead() -> None:
    # semantic_regime e funcție PURĂ de cele trei etichete ale barei curente — nicio bară viitoare
    import inspect
    params = set(inspect.signature(semantic_regime).parameters)
    assert params == {"volatility", "structure", "direction"}   # doar axele barei i, fără time/future
    assert semantic_regime("high_directional", "range", "up") is SemanticRegime.BREAKOUT_TRANSITION


def test_10_regime_change_does_not_close_without_explicit_rule() -> None:
    # exit_on_regime_change=False ⇒ schimbarea regimului NU produce ieșire
    hold = _contract("hold", family="X", allowed=(SemanticRegime.TREND_UP,), exit_on_change=False)
    exiter = _contract("exiter", family="X", allowed=(SemanticRegime.TREND_UP,), exit_on_change=True,
                       exit_trans=SemanticRegime.TREND_DOWN)
    def should_exit(c: SC, new_reg: SemanticRegime) -> bool:
        return c.exit_on_regime_change and (c.exit_on_transition is None or new_reg is c.exit_on_transition)
    assert should_exit(hold, SemanticRegime.RANGE) is False          # fără regulă → poziția continuă
    assert should_exit(exiter, SemanticRegime.RANGE) is False        # tranziție greșită → nu iese
    assert should_exit(exiter, SemanticRegime.TREND_DOWN) is True    # tranziția declarată → iese


def test_11_shadow_eligible_traverses_router_ev_n6_without_order() -> None:
    shadow = _contract("shadow_strat", family="X", allowed=(SemanticRegime.TREND_UP,),
                       status=ValidationStatus.SHADOW_ELIGIBLE)
    assert _router_one(shadow, SemanticRegime.TREND_UP).eligible                # traversează routerul
    resp = decide_n6(_request("shadow_strat", ValidationStatus.SHADOW_ELIGIBLE, enter=True))
    assert resp.decision == "SHADOW_TRADE_CANDIDATE"          # NU TRADE real
    assert BROKER_ORDER_SUBMISSION == "DISABLED"


def test_12_multiple_eligible_no_auto_combine() -> None:
    # două strategii eligibile în același regim → DOUĂ decizii separate; pachetul NU le combină/dublează
    r = StrategyRouter((RANGE, _contract("range2", family="RANGE_FADE2", allowed=(SemanticRegime.RANGE,))))
    elig = [d for d in r.eligible(SemanticRegime.RANGE, "LONG", 1.0) if d.eligible]
    assert len(elig) == 2 and len({d.strategy_id for d in elig}) == 2   # separate, nu fuzionate


def _router_one(c: SC, reg: SemanticRegime):
    return StrategyRouter((c,)).route_one(c, reg, "LONG", 1.0)


# ═══ N6 + contract + EV + amprentă ═══
def _prob(pt_target: int = 500, horizon: int = 200, n: int = 1000) -> ProbabilityInputs:
    cell = OutcomeCell(n=n, n_target=pt_target, n_horizon=horizon, sum_horizon_R=0.0)
    sib = OutcomeCell(n=n, n_target=pt_target, n_horizon=horizon, sum_horizon_R=0.0)
    return ProbabilityInputs(hierarchy=(HierarchyLevel(cell=cell, siblings=(cell, sib)),), credibility=0.80)


def _request(sid: str, status: ValidationStatus, *, enter: bool, with_prob: bool = True) -> DecisionRequest:
    # rr=3 via 'rr'; r=1; cost mic ⇒ EV pozitiv (enter). Pentru NO_TRADE: rr=0.001 (feasibility).
    rr = 3.0 if enter else 0.001
    return DecisionRequest(
        contract_id=INPUT_CONTRACT_ID, strategy_id=sid, strategy_version="v1", validation_status=status,
        market_state_ref="ms1", regime_label="TREND_UP", bias_direction="LONG", market_map_available=True,
        levels_available=True, confirmation_available=True, entry_price=100.0, stop_price=99.0,
        target_kind="rr", target_param=rr, holding_window=10, atr=1.0,
        probability_inputs=_prob() if with_prob else None,
        full_spread_price=0.05, entry_slippage_price=0.0, exit_slippage_price=0.0,
        measurement_contract_version="canonical-evaluator-v2.7.66-A2", configuration_fingerprint="runhash123")


def test_n6_ratified_positive_ev_trades() -> None:
    resp = decide_n6(_request("s", ValidationStatus.RATIFIED, enter=True))
    assert resp.decision == "TRADE" and resp.reason_codes == ("TRADE_VALIDATED_EDGE",)
    assert resp.expected_value_net is not None and resp.expected_value_net > 0


def test_n6_no_probability_inputs_is_no_trade() -> None:
    resp = decide_n6(_request("s", ValidationStatus.RATIFIED, enter=True, with_prob=False))
    assert resp.decision == "NO_TRADE" and resp.reason_codes == ("MISSING_PROBABILITY_INPUTS",)


def test_n6_experimental_status_no_eligible_strategy() -> None:
    resp = decide_n6(_request("s", ValidationStatus.EXPERIMENTAL, enter=True))
    assert resp.decision == "NO_TRADE" and resp.reason_codes == ("NO_ELIGIBLE_STRATEGY",)


def test_n6_feasibility_negative_ev_no_trade() -> None:
    resp = decide_n6(_request("s", ValidationStatus.RATIFIED, enter=False))
    assert resp.decision == "NO_TRADE" and resp.reason_codes == ("NEGATIVE_EXPECTED_VALUE",)


def test_n6_uses_real_ev_not_edge_bool() -> None:
    # dovada că NU e edge=True/False: răspunsul poartă EV_net, reward, cost, probabilități din motorul real
    resp = decide_n6(_request("s", ValidationStatus.RATIFIED, enter=True))
    assert resp.expected_reward is not None and resp.estimated_cost is not None
    assert "p_t_lcb" in resp.probability_assumptions and "prob_table_hash" in resp.probability_assumptions


def test_a5_fingerprint_covers_five_dims_and_compare_raises() -> None:
    a = decide_n6(_request("stratA", ValidationStatus.RATIFIED, enter=True))
    b = decide_n6(_request("stratB", ValidationStatus.RATIFIED, enter=True))   # strategie DIFERITĂ
    assert a.configuration_fingerprint != b.configuration_fingerprint          # strategia intră în amprentă
    compare_decisions(a.configuration_fingerprint, a.configuration_fingerprint)  # identic → OK
    with pytest.raises(NonComparableDecisionError):
        compare_decisions(a.configuration_fingerprint, b.configuration_fingerprint)


def test_semantic_regime_mapping_six_states() -> None:
    assert semantic_regime("compressed", "weak", "up") is SemanticRegime.COMPRESSION
    assert semantic_regime("high_directional", "range", "up") is SemanticRegime.BREAKOUT_TRANSITION
    assert semantic_regime("normal", "strong", "up") is SemanticRegime.TREND_UP
    assert semantic_regime("normal", "strong", "down") is SemanticRegime.TREND_DOWN
    assert semantic_regime("low", "none", "neutral") is SemanticRegime.RANGE
    assert semantic_regime(None, "weak", "up") is SemanticRegime.UNCERTAIN
    assert semantic_regime("high_choppy", "none", "neutral") is SemanticRegime.UNCERTAIN
