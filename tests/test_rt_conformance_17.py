"""RED TEAM — cele 17 teste canonice (RT-AUDIT-MEAS-0002) rulate contra `canonical_evaluator`.
Acestea sunt testele RED TEAM (spec-ul lor), NU ale mele. Poarta de ratificare: un motor ratifică doar dacă trece
toate cele 17 contra rezultatelor canonice așteptate. Cele TREI motoare existente (SCREEN/MSTRAT/DEMO) au picat toate.

Marcaje:
  · trece  = evaluatorul canonic implementează semantica canonică a testului
  · BLOCAT = sub-specificare la Statistician (T4 precedența țintei pe bara de intrare; T12/13 spread full vs half)
  · UPSTREAM = ține de stratul day-index/bloc (T9/T10/T11), nu de evaluatorul de tranzacție (primește `block_end`)
"""

from __future__ import annotations

import os
import sys

import pytest

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from canonical_evaluator import (  # noqa: E402
    BASE_PROVISIONAL, STRESS_PROVISIONAL, ExecutedTrade, NoEntry, Rejection, Signal,
    evaluate_signal, evaluate_strategy,
)

Bars = tuple[list[float], list[float], list[float], list[float]]


def _sig(**kw: object) -> Signal:
    d: dict[str, object] = dict(strategy_id="RT", signal_id="t", signal_bar=0, direction=1,
                                requested_stop_price=90.0, target_kind="none", target_param=None,
                                max_holding_bars=5, spread_price=0.05, atr=1.0, timestamp=1)
    d.update(kw)
    return Signal(**d)  # type: ignore[arg-type]


# T1 — signal N → entry open N+1
def test_t1_entry_next_open() -> None:
    o = [100.0, 101.0, 101.0, 101.0]; h = [100.2, 101.2, 101.2, 101.2]
    l = [99.8, 100.8, 100.8, 100.8]; c = [100.0, 101.0, 101.0, 101.0]
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=80.0), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.entry_bar == 1 and out.entry_price == 101.0


# T2 — stop below minimum: D-2 = RESPINGERE (nu podea care extinde). Canonic ≠ cele 3 motoare (widen/no-floor).
def test_t2_stop_below_minimum_is_rejected() -> None:
    o, h, l, c = [100.0]*6, [100.2]*6, [99.8]*6, [100.0]*6
    out = evaluate_signal(_sig(requested_stop_price=99.99, spread_price=0.001, atr=5.0), o, h, l, c)
    assert isinstance(out, Rejection) and out.reason_code == "STOP_BELOW_MINIMUM"


# T3 — SL pe bara de intrare (scanată)
def test_t3_sl_on_entry_bar() -> None:
    o = [100.0, 100.0, 100.0, 100.0]; h = [100.2, 100.2, 100.2, 100.2]
    l = [99.8, 98.0, 99.8, 99.8]; c = [100.0, 100.0, 100.0, 100.0]
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=99.0), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "stop" and out.exit_bar == 1


# T4 — TP pe bara de intrare: SUB-SPEC (precedența la Statistician). NU o decid.
@pytest.mark.skip(reason="BLOCAT: sub-specificare Statistician — precedența țintei pe bara de intrare (a 6-a divergență)")
def test_t4_tp_on_entry_bar_blocked() -> None:
    pass


# T5 — SL & TP aceeași bară → SL PRIMEAZĂ (worst-case)
def test_t5_sl_tp_same_bar_stop_first() -> None:
    o = [100.0, 100.0, 100.0, 100.0]; h = [100.2, 103.0, 100.2, 100.2]
    l = [99.8, 98.0, 99.8, 99.8]; c = [100.0]*4
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=99.0, target_kind="price", target_param=102.0),
                          o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "stop"


# T6/T7 — fereastra inclusiv (bara de intrare = bara 1); expiry la ultima bară permisă = close-ul barei H
def test_t6_t7_inclusive_window_expiry() -> None:
    n = 12; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    out = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=10), o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "time" and out.exit_bar == 1 + 10 - 1


# T8 — granița datasetului NU e time-exit: over-orizont = still_open (raportat separat). Cele 3 motoare TOATE pică.
def test_t8_dataset_boundary_is_still_open_not_time_exit() -> None:
    n = 20; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    out = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=10), o, h, l, c, block_end=5)
    assert isinstance(out, ExecutedTrade) and out.still_open_at_end and out.exit_reason == "still_open_at_end"


# T9/T10/T11 — rollover 17:00-NY / DST / segmentare manifest: UPSTREAM (day-index/bloc), nu evaluatorul de tranzacție
@pytest.mark.skip(reason="UPSTREAM: strat day-index/bloc (17:00-NY / DST / manifest); evaluatorul primește block_end")
def test_t9_t10_t11_upstream_block_layer() -> None:
    pass


# T12/T13 — cost în USD, spread O DATĂ + slippage per execuție. STRUCTURA conformă; half/full = SUB-SPEC.
def test_t12_t13_cost_structure_spread_once() -> None:
    # STRESS = 1·spread(0.08) + entry_slip(0.08) + exit_slip(0.08) = 0.24 (NU 2·spread); USD direct, fără ×tick
    assert abs(STRESS_PROVISIONAL.total_cost_price - 0.24) < 1e-9
    assert abs(BASE_PROVISIONAL.total_cost_price - 0.05) < 1e-9
    # canonic Red Team: 1·0.25 + 2·0.05 = 0.35 (spread o dată, slip de două ori)
    from canonical_evaluator import CostScenario
    rt = CostScenario("RT", spread_price=0.25, entry_slippage_price=0.05, exit_slippage_price=0.05)
    assert abs(rt.total_cost_price - 0.35) < 1e-9   # spread O DATĂ, nu 0.60


@pytest.mark.skip(reason="BLOCAT: sub-specificare Statistician — spread FULL vs HALF (structura spread-once e conformă)")
def test_t12_t13_spread_half_full_blocked() -> None:
    pass


# T14 — net (cost scăzut), NU gross
def test_t14_net_not_gross() -> None:
    n = 6; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    out = evaluate_signal(_sig(requested_stop_price=90.0, max_holding_bars=3), o, h, l, c)
    assert isinstance(out, ExecutedTrade)
    base = next(r for r in out.results if r.scenario == BASE_PROVISIONAL.name)
    assert base.total_cost_price == 0.05 and base.net_R < 0   # gross~0 minus cost ⇒ net negativ (nu gross 0)


# T15/T16 — metrici fat-tail SIMETRICE (best-share + trim top-1%), în AMBELE scenarii
def test_t15_t16_symmetric_fat_tail_metrics() -> None:
    n = 40; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    sigs = [_sig(signal_id=f"s{i}", signal_bar=i, requested_stop_price=80.0, max_holding_bars=3)
            for i in range(0, 30)]
    rep, _ = evaluate_strategy("RT", sigs, o, h, l, c)
    assert rep.base_best_share_of_total is not None and rep.stress_best_share_of_total is not None   # T15 simetric
    assert rep.base_trimmed_top1pct_R is not None and rep.stress_trimmed_top1pct_R is not None        # T16 simetric


# T17 — config_id acoperă 13 dimensiuni (incl. simbol/date/manifest) + GARDĂ de comparabilitate (nu comentariu)
def test_t17_config_covers_run_dims_and_guard_enforces() -> None:
    from canonical_evaluator import RunContext, require_comparable, NonComparableError
    n = 6; o, h, l, c = [100.0]*n, [100.2]*n, [99.8]*n, [100.0]*n
    xau = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=3), o, h, l, c,
                          run=RunContext("XAUUSD", "M15_v2", "four_blocks_v1"))
    es = evaluate_signal(_sig(requested_stop_price=80.0, max_holding_bars=3), o, h, l, c,
                         run=RunContext("ES", "M15_v2", "four_blocks_v1"))
    assert isinstance(xau, ExecutedTrade) and isinstance(es, ExecutedTrade)
    assert xau.config_id != es.config_id                 # instrumente DIFERITE ⇒ id-uri diferite (gap-ul a)
    # GARDA impune comparația-pe-potrivire (ridică), nu doar un comentariu (gap-ul b)
    require_comparable(xau.config_id, xau.config_id)      # aceeași config → OK
    with pytest.raises(NonComparableError):
        require_comparable(xau.config_id, es.config_id)   # config diferit → RIDICĂ


# T18 — MEAS-9 gap-open: open dincolo de nivel ⇒ ieșire la PREȚUL DE INTRARE (spec Statistician T4)
def test_t18_meas9_gap_open_guard() -> None:
    n = 6; o = [100.0]*n; h = [100.2]*n; l = [99.8]*n; c = [100.0]*n
    out = evaluate_signal(_sig(signal_bar=0, requested_stop_price=90.0, target_kind="price", target_param=99.5),
                          o, h, l, c)
    assert isinstance(out, ExecutedTrade) and out.exit_reason == "gap_at_entry"
    assert all(r.gross_move_price == 0.0 for r in out.results)   # nu win/pierdere fictivă la nivel nominal
