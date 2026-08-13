"""RED TEAM — cele 18 teste canonice (RT-AUDIT-MEAS-0002, +T18 gap-open) rulate contra `canonical_evaluator` (v2.7.66).
Testele RED TEAM (spec-ul lor), poarta de ratificare. Cele 3 motoare (SCREEN/MSTRAT/DEMO) au picat toate.
  · trece  = evaluatorul canonic implementează semantica canonică
  · BLOCAT = sub-specificare Statistician (T4 non-gap entry-bar target)
  · UPSTREAM = strat day-index/bloc (T9/T10/T11)
"""

from __future__ import annotations

import os
import sys

import pytest

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from level_output import Ok, Unavailable  # noqa: E402
from canonical_evaluator import (  # noqa: E402
    BASE_PROVISIONAL, STRESS_PROVISIONAL, CostScenario, ExecutedTrade, InvalidExecution, Rejection, RunContext,
    Signal, SpreadFull, compare, evaluate_signal, evaluate_strategy, NonComparableError,
)


def _sig(**kw: object) -> Signal:
    d: dict[str, object] = dict(strategy_id="RT", signal_id="t", signal_bar=0, direction=1,
                                requested_stop_price=90.0, target_kind="none", target_param=None,
                                max_holding_bars=5, spread_price=SpreadFull(0.05), atr=1.0, timestamp=1)
    d.update(kw)
    return Signal(**d)  # type: ignore[arg-type]


def test_t1_entry_next_open() -> None:
    o = [100.0, 101.0, 101.0, 101.0]; h = [100.2, 101.2, 101.2, 101.2]
    l = [99.8, 100.8, 100.8, 100.8]; c = [100.0, 101.0, 101.0, 101.0]
    out = evaluate_signal(_sig(requested_stop_price=80.0), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.entry_bar == 1 and out.entry_price == 101.0


def test_t2_stop_below_minimum_rejected() -> None:
    o, h, l, c = [100.0]*6, [100.2]*6, [99.8]*6, [100.0]*6
    out = evaluate_signal(_sig(requested_stop_price=99.99, spread_price=SpreadFull(0.001), atr=5.0), o, h, l, c)
    assert isinstance(out, Rejection) and out.reason_code == "STOP_BELOW_MINIMUM"


def test_t3_sl_on_entry_bar() -> None:
    o = [100.0]*4; h = [100.2]*4; l = [99.8, 98.0, 99.8, 99.8]; c = [100.0]*4
    out = evaluate_signal(_sig(requested_stop_price=99.0), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "stop" and out.exit_bar == 1


@pytest.mark.skip(reason="BLOCAT: sub-spec Statistician — precedența țintei pe bara de intrare (cazul NON-gap)")
def test_t4_tp_on_entry_bar_nongap_blocked() -> None:
    pass


def test_t5_sl_tp_same_bar_stop_first() -> None:
    o = [100.0]*4; h = [100.2, 103.0, 100.2, 100.2]; l = [99.8, 98.0, 99.8, 99.8]; c = [100.0]*4
    out = evaluate_signal(_sig(requested_stop_price=99.0, target_kind="price", target_param=102.0), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "stop"


def test_t6_t7_inclusive_window() -> None:
    n = 12; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    out = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=10), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "time" and out.exit_bar == 1 + 10 - 1


def test_t8_dataset_boundary_still_open() -> None:
    n = 20; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    out = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=10), o, h, l, c, block_end=5)
    assert isinstance(out, ExecutedTrade) and out.still_open_at_end and out.exit_reason == "still_open_at_end"


@pytest.mark.skip(reason="UPSTREAM: strat day-index/bloc (17:00-NY/DST/manifest); evaluatorul primește block_end")
def test_t9_t10_t11_upstream() -> None:
    pass


def test_t12_t13_cost_spread_once() -> None:
    assert abs(STRESS_PROVISIONAL.total_cost_price - 0.24) < 1e-9 and abs(BASE_PROVISIONAL.total_cost_price - 0.05) < 1e-9
    rt = CostScenario("RT", SpreadFull(0.25), 0.05, 0.05)     # canonic Red Team: 1·0.25 + 2·0.05 = 0.35
    assert abs(rt.total_cost_price - 0.35) < 1e-9


def test_t14_net_not_gross() -> None:
    n = 6; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    out = evaluate_signal(_sig(requested_stop_price=90.0, max_holding_bars=3), o, h, l, c)
    assert isinstance(out, ExecutedTrade)
    base = next(r for r in out.results if r.scenario == BASE_PROVISIONAL.name)
    assert base.total_cost_price == 0.05 and base.net_R < 0


def test_t15_t16_concentration_on_canonical_report() -> None:
    # §7 MEAS-10: câmpurile de concentrare sunt pe RAPORT (nu doar în teste), în ambele scenarii
    n = 40; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    sigs = [_sig(signal_id=f"s{i}", signal_bar=i, requested_stop_price=80.0, max_holding_bars=3) for i in range(0, 30)]
    rep, _ = evaluate_strategy("RT", sigs, o, h, l, c)
    for conc in (rep.base_concentration, rep.stress_concentration):
        assert conc is not None
        assert isinstance(conc.best_trade_share, (Ok, Unavailable))   # LevelOutput
        assert isinstance(conc.trimmed_top1_avg_R, float) and isinstance(conc.sum_R, float)
        assert conc.n_trimmed >= 1 and isinstance(conc.wo1_still_positive, bool)


def test_t17_run_hash_covers_data_and_compare_raises() -> None:
    n = 6; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    a = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=3), o, h, l, c,
                        run=RunContext("XAUUSD", "M15_v2", "pre_holdout", "bmhash", 4, "2025-10-23"))
    b = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=3), o, h, l, c,
                        run=RunContext("ES", "M15_v2", "pre_holdout", "bmhash", 4, "2025-10-23"))
    assert isinstance(a, ExecutedTrade) and isinstance(b, ExecutedTrade)
    assert a.run_hash != b.run_hash                           # DATE diferite ⇒ run_hash diferit (T17a)
    with pytest.raises(NonComparableError):
        compare(a.run_hash, b.run_hash)                       # RIDICĂ, nu comentează (T17b)


def test_t18_meas9_strict_geometry_a2() -> None:
    # AMENDAMENT A2 (geometrie strictă): risc ≤ 0 OR recompensă ≤ 0 → INVALID_EXECUTION (ambele)
    o, h, l, c = [100.0]*6, [100.2]*6, [99.8]*6, [100.0]*6
    inv_stop = evaluate_signal(_sig(requested_stop_price=101.0), o, h, l, c)   # gap prin stop
    assert isinstance(inv_stop, InvalidExecution) and inv_stop.violation == "risk_nonpositive"
    inv_tgt = evaluate_signal(_sig(requested_stop_price=90.0, target_kind="price", target_param=99.5), o, h, l, c)
    assert isinstance(inv_tgt, InvalidExecution) and inv_tgt.violation == "reward_nonpositive"   # gap prin target
    exact = evaluate_signal(_sig(requested_stop_price=100.0), o, h, l, c)      # open EXACT pe stop
    assert isinstance(exact, InvalidExecution)
