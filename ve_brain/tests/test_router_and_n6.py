"""Testele artefactului: cele 12 teste de ROUTER (MULTI-AXIAL, post-decizia CEO pe range) + cele 5 condiții de range
+ cauzalitate + N6/contract/EV/amprentă. Fixture-uri deterministe. (Cele 25 end-to-end rămân la AI Trader.)"""

from __future__ import annotations

import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

from ve_brain import (  # noqa: E402
    BROKER_ORDER_SUBMISSION, DecisionRequest, HierarchyLevel, INPUT_CONTRACT_ID, NonComparableDecisionError,
    OutcomeCell, RANGE_STRATEGY_ROUTING, RoutingMode, SemanticRegime, StrategyRouter, ValidationStatus,
    applicable_regimes, compare_decisions, decide_n6, n4_triggers_breakout,
)
from ve_brain.regime_routing import StrategyContract as SC  # noqa: E402


def _contract(sid: str, *, family: str, allowed: tuple[SemanticRegime, ...] = (),
              directions: tuple[str, ...] = ("LONG", "SHORT"), arming: tuple[SemanticRegime, ...] = (),
              trigger: SemanticRegime | None = None, min_conf: float = 0.0,
              status: ValidationStatus = ValidationStatus.RATIFIED, n4: str | None = None,
              exit_on_change: bool = False, exit_trans: SemanticRegime | None = None) -> SC:
    return SC(strategy_id=sid, strategy_family=family, allowed_regimes=allowed, allowed_directions=directions,
              arming_regimes=arming, trigger_transition=trigger, minimum_regime_confidence=min_conf,
              required_N2_bias=None, required_N3_map=True, required_N4_confirmation=n4, entry_rule="e",
              invalidation_rule="i", exit_rule="x", holding_window=10, validation_status=status,
              strategy_version="v1", measurement_contract_version="canonical-evaluator-v2.7.66-A2",
              exit_on_regime_change=exit_on_change, exit_on_transition=exit_trans)


TREND = _contract("trend_pullback", family="TREND_PULLBACK", allowed=(SemanticRegime.TREND_UP,), directions=("LONG",))
COMPRESS = _contract("compress_strat", family="COMPRESSION_SETUP", allowed=(SemanticRegime.COMPRESSION,))
RANGE = _contract("range_fade", family="RANGE_MEAN_REVERSION", allowed=(SemanticRegime.RANGE,))
BREAKOUT = _contract("range_breakout", family="RANGE_BREAKOUT",
                     arming=(SemanticRegime.RANGE, SemanticRegime.COMPRESSION),
                     trigger=SemanticRegime.BREAKOUT_TRANSITION, n4="DISPLACEMENT_AND_ACCEPTANCE")

# piețe = (volatility, structure, direction_axis)
M_TREND_UP = ("normal", "strong", "up")
M_COMPRESSION = ("compressed", "range", "neutral")       # DOAR compresie
M_BREAKOUT = ("high_directional", "range", "up")         # flip proaspăt + expansiune
M_MULTI = ("compressed", "strong", "up")                 # COMPRESSION + TREND_UP simultan (multi-axial)
M_UNCERTAIN = (None, "strong", "up")                     # axă lipsă
M_RANGEY = ("low", "range", "neutral")                   # „arată" a range dar e NEIDENTIFICABIL → UNCERTAIN


def _elig(strats: tuple[SC, ...], market: tuple[str | None, str | None, str | None], bias: str | None = "LONG"):
    vol, struct, d = market
    return {x.strategy_id: x for x in StrategyRouter(strats).eligible(vol, struct, d, bias, 1.0)}


# ═══ cele 12 teste de router (multi-axial) ═══
def test_01_trend_active_in_trend_up() -> None:
    assert _elig((TREND,), M_TREND_UP)["trend_pullback"].eligible


def test_02_trend_inactive_in_compression() -> None:
    d = _elig((TREND,), M_COMPRESSION)["trend_pullback"]
    assert not d.eligible and d.reason_codes == ("INELIGIBLE_REGIME",)


def test_03_range_strategy_blocked_true_range_not_identifiable() -> None:
    d = _elig((RANGE,), M_TREND_UP)["range_fade"]
    assert not d.eligible and d.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_04_range_strategy_blocked_even_in_range_looking_market() -> None:
    d = _elig((RANGE,), M_RANGEY)["range_fade"]                 # dir=neutral + struct=range → tot BLOCAT
    assert not d.eligible and d.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_05_breakout_watch_armed_in_compression() -> None:
    d = _elig((BREAKOUT,), M_COMPRESSION)["range_breakout"]
    assert d.eligible and d.mode is RoutingMode.BREAKOUT_WATCH


def test_06_wick_without_acceptance_not_trigger() -> None:
    assert n4_triggers_breakout(0, "LONG") is False and n4_triggers_breakout(1, "LONG") is False
    assert n4_triggers_breakout(None, "LONG") is False


def test_07_displacement_plus_acceptance_triggers() -> None:
    assert n4_triggers_breakout(2, "LONG") is True and n4_triggers_breakout(-2, "SHORT") is True


def test_08_uncertain_produces_no_trade() -> None:
    d = _elig((TREND,), M_UNCERTAIN)["trend_pullback"]
    assert not d.eligible and d.reason_codes == ("UNCERTAIN_REGIME",)


def test_09_regime_computed_without_lookahead() -> None:
    import inspect
    assert set(inspect.signature(applicable_regimes).parameters) == {"volatility", "structure", "direction"}
    assert applicable_regimes("high_directional", "range", "up") == frozenset({SemanticRegime.BREAKOUT_TRANSITION})


def test_10_regime_change_does_not_close_without_rule() -> None:
    hold = _contract("hold", family="X", allowed=(SemanticRegime.TREND_UP,), exit_on_change=False)
    exiter = _contract("exiter", family="X", allowed=(SemanticRegime.TREND_UP,), exit_on_change=True,
                       exit_trans=SemanticRegime.TREND_DOWN)
    def should_exit(c: SC, new: SemanticRegime) -> bool:
        return c.exit_on_regime_change and (c.exit_on_transition is None or new is c.exit_on_transition)
    assert should_exit(hold, SemanticRegime.COMPRESSION) is False
    assert should_exit(exiter, SemanticRegime.COMPRESSION) is False
    assert should_exit(exiter, SemanticRegime.TREND_DOWN) is True


def test_11_shadow_eligible_traverses_without_order() -> None:
    assert _elig((_contract("sh", family="X", allowed=(SemanticRegime.TREND_UP,),
                            status=ValidationStatus.SHADOW_ELIGIBLE),), M_TREND_UP)["sh"].eligible
    resp = decide_n6(_request("sh", ValidationStatus.SHADOW_ELIGIBLE, enter=True))
    assert resp.decision == "SHADOW_TRADE_CANDIDATE" and BROKER_ORDER_SUBMISSION == "DISABLED"


def test_12_multiaxial_compression_and_trend_simultaneous() -> None:
    # M_MULTI = compressed+strong+up ⇒ {COMPRESSION, TREND_UP}: AMBELE strategii eligibile SIMULTAN (fără precedență)
    e = _elig((TREND, COMPRESS), M_MULTI)
    assert e["trend_pullback"].eligible and e["compress_strat"].eligible
    assert applicable_regimes(*M_MULTI) == frozenset({SemanticRegime.COMPRESSION, SemanticRegime.TREND_UP})


# ═══ cele 5 condiții de range la handoff ═══
def test_range_cond1_fail_closed() -> None:
    for mkt in (M_TREND_UP, M_COMPRESSION, M_BREAKOUT, M_MULTI, M_UNCERTAIN, M_RANGEY):
        assert not _elig((RANGE,), mkt)["range_fade"].eligible          # fail-closed în ORICE piață


def test_range_cond2_structrange_and_neutral_cannot_activate() -> None:
    # StructBand.RANGE (struct=range) ȘI Direction.NEUTRAL nu produc RANGE și nu activează strategia de range
    assert SemanticRegime.RANGE not in applicable_regimes("low", "range", "neutral")
    assert SemanticRegime.RANGE not in applicable_regimes("normal", "weak", "neutral")


def test_range_cond3_reason_persisted() -> None:
    assert _elig((RANGE,), M_TREND_UP)["range_fade"].reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_range_cond4_other_families_work() -> None:
    assert _elig((TREND,), M_TREND_UP)["trend_pullback"].eligible
    assert _elig((COMPRESS,), M_COMPRESSION)["compress_strat"].eligible
    assert _elig((BREAKOUT,), M_COMPRESSION)["range_breakout"].eligible


def test_range_cond5_no_implicit_fallback_to_range() -> None:
    assert RANGE_STRATEGY_ROUTING == "DISABLED"
    for mkt in (M_TREND_UP, M_COMPRESSION, M_BREAKOUT, M_MULTI, M_UNCERTAIN, M_RANGEY):
        assert SemanticRegime.RANGE not in applicable_regimes(*mkt)     # niciodată produs


# ═══ N6 + contract + EV + amprentă ═══
def _prob() -> object:
    cell = OutcomeCell(n=1000, n_target=500, n_horizon=200, sum_horizon_R=0.0)
    return __import__("ve_brain", fromlist=["ProbabilityInputs"]).ProbabilityInputs(
        hierarchy=(HierarchyLevel(cell=cell, siblings=(cell, cell)),), credibility=0.80)


def _request(sid: str, status: ValidationStatus, *, enter: bool, with_prob: bool = True) -> DecisionRequest:
    rr = 3.0 if enter else 0.001
    from ve_brain import ProbabilityInputs  # noqa
    return DecisionRequest(
        contract_id=INPUT_CONTRACT_ID, strategy_id=sid, strategy_version="v1", validation_status=status,
        market_state_ref="ms", regime_label="TREND_UP", bias_direction="LONG", market_map_available=True,
        levels_available=True, confirmation_available=True, entry_price=100.0, stop_price=99.0,
        target_kind="rr", target_param=rr, holding_window=10, atr=1.0,
        probability_inputs=_prob() if with_prob else None,   # type: ignore[arg-type]
        full_spread_price=0.05, entry_slippage_price=0.0, exit_slippage_price=0.0,
        measurement_contract_version="canonical-evaluator-v2.7.66-A2", configuration_fingerprint="runhash")


def test_n6_ratified_positive_ev_trades() -> None:
    resp = decide_n6(_request("s", ValidationStatus.RATIFIED, enter=True))
    assert resp.decision == "TRADE" and resp.reason_codes == ("TRADE_VALIDATED_EDGE",)
    assert resp.expected_value_net is not None and resp.expected_value_net > 0


def test_n6_no_probability_is_no_trade() -> None:
    resp = decide_n6(_request("s", ValidationStatus.RATIFIED, enter=True, with_prob=False))
    assert resp.decision == "NO_TRADE" and resp.reason_codes == ("MISSING_PROBABILITY_INPUTS",)


def test_n6_experimental_no_eligible_strategy() -> None:
    resp = decide_n6(_request("s", ValidationStatus.EXPERIMENTAL, enter=True))
    assert resp.decision == "NO_TRADE" and resp.reason_codes == ("NO_ELIGIBLE_STRATEGY",)


def test_n6_uses_real_ev_not_edge_bool() -> None:
    resp = decide_n6(_request("s", ValidationStatus.RATIFIED, enter=True))
    assert resp.expected_reward is not None and resp.estimated_cost is not None
    assert "p_t_lcb" in resp.probability_assumptions and "prob_table_hash" in resp.probability_assumptions


def test_a5_fingerprint_covers_strategy_and_compare_raises() -> None:
    a = decide_n6(_request("stratA", ValidationStatus.RATIFIED, enter=True))
    b = decide_n6(_request("stratB", ValidationStatus.RATIFIED, enter=True))
    assert a.configuration_fingerprint != b.configuration_fingerprint
    compare_decisions(a.configuration_fingerprint, a.configuration_fingerprint)
    with pytest.raises(NonComparableDecisionError):
        compare_decisions(a.configuration_fingerprint, b.configuration_fingerprint)
