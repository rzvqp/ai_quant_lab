"""Teste pentru motorul de decizie (nivelul 6). Un test per convenție: pică fără ea, trece cu ea.

Ținte explicite din spec: cei TREI termeni ai lui EV, limita INFERIOARĂ a intervalului, contracția la n=0,
`E[X|h]` lipsă ca −1, egalitatea D2, fezabilitatea, fail-closed cu câmp numit, `k` estimat (nu hardcodat).
"""

from __future__ import annotations

import math
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from decision_engine import (  # noqa: E402
    DecisionInput, HierarchyLevel, OutcomeCell, Reason, decide, ev_from_terms,
)


def _cell(n: int, nt: int, nh: int = 0, sumh: float = 0.0) -> OutcomeCell:
    return OutcomeCell(n=n, n_target=nt, n_horizon=nh, sum_horizon_R=sumh)


def _single(n: int, nt: int, nh: int = 0, sumh: float = 0.0) -> tuple[HierarchyLevel, ...]:
    return (HierarchyLevel(cell=_cell(n, nt, nh, sumh)),)


def _inp(hier: tuple[HierarchyLevel, ...], rr: float = 2.0, r: float = 1.0, cost: float = 0.0,
         cred: float = 0.80) -> DecisionInput:
    return DecisionInput(rr=rr, r=r, cost=cost, hierarchy=hier, credibility=cred)


# ───────────────────────────── PARTEA 1 — cei TREI termeni ai lui EV ─────────────────────────────
def test_ev_has_three_terms_each_moves_it() -> None:
    base = ev_from_terms(p_t=0.30, p_h=0.10, e_x_h=-0.2, rr=2.0, cost_over_r=0.05)
    assert ev_from_terms(0.40, 0.10, -0.2, 2.0, 0.05) > base        # p_t ↑ (termen țintă)
    assert ev_from_terms(0.30, 0.10, +0.5, 2.0, 0.05) > base        # E[X|h] ↑ (termen orizont)
    assert ev_from_terms(0.30, 0.10, -0.2, 2.0, 0.20) < base        # cost ↑
    # termenul de stop: p_s = 1 − p_t − p_h; mai mult p_h (cu E[X|h] > −1) ia din masa de stop → EV ↑
    assert ev_from_terms(0.30, 0.30, 0.0, 2.0, 0.05) > base


def test_two_outcome_model_systematically_overestimates() -> None:
    """Un model cu DOUĂ rezultate (ieșirile pe orizont numărate ca ținte, cu payoff RR) supraevaluează EV."""
    p_t, p_h, exh, rr = 0.051, 0.13, -0.1, 3.0                       # CAND-0001-like: țintă rară, orizont frecvent
    three = ev_from_terms(p_t, p_h, exh, rr, 0.0)
    naive_two = (p_t + p_h) * rr - (1.0 - p_t - p_h)                 # orizont tratat ca țintă (greșit)
    assert three < naive_two
    assert naive_two - three > 0.3                                   # supraevaluare materială


# ───────────────────────────── PARTEA 3 — poarta e la LIMITA INFERIOARĂ, nu la punct ─────────────────────────────
def test_lower_bound_gate_thin_history_blocked_rich_passes() -> None:
    thin = decide(_inp(_single(10, 4), rr=2.0))                      # p_t=0,4, dar n mic → interval lat
    assert thin.ev_point is not None and thin.ev_point > 0.0         # ar trece la estimarea punctuală
    assert thin.ev_lcb is not None and thin.ev_lcb <= 0.0            # dar NU la limita inferioară
    assert thin.reason == Reason.NO_TRADE_EV_LCB.value and thin.enter is False

    rich = decide(_inp(_single(1000, 400), rr=2.0))                 # aceleași proporții, n mare → interval îngust
    assert rich.p_t_lcb is not None and thin.p_t_lcb is not None
    assert rich.p_t_lcb > thin.p_t_lcb                               # mai multe date ⇒ LCB mai aproape de punct
    assert rich.reason == Reason.ENTER.value and rich.enter is True


def test_more_data_relaxes_the_gate_monotonically() -> None:
    lcbs = [decide(_inp(_single(n, int(0.4 * n)), rr=2.0)).p_t_lcb for n in (20, 100, 1000)]
    assert all(x is not None for x in lcbs)
    assert lcbs[0] < lcbs[1] < lcbs[2]                              # type: ignore[operator]


# ───────────────────────────── PARTEA 2 — contracția la n=0 moștenește părintele ─────────────────────────────
def test_contraction_at_n_zero_inherits_parent_exactly() -> None:
    parent = _cell(1000, 400)                                        # global p_t = 0,40
    new_cell = _cell(0, 0)                                           # setup NOU, fără istoric
    sibs = (_cell(50, 5), _cell(50, 45))                             # surori eterogene (k mic) — irelevant la n=0
    hier = (HierarchyLevel(cell=parent), HierarchyLevel(cell=new_cell, siblings=sibs))
    r = decide(_inp(hier, rr=2.0))
    assert r.p_t_hat is not None and abs(r.p_t_hat - 0.40) < 1e-9    # EXACT părintele, fără caz special
    # independent de surori (deci de k): alt set de surori → același p_t_hat
    hier2 = (HierarchyLevel(cell=parent), HierarchyLevel(cell=new_cell, siblings=(_cell(80, 40), _cell(80, 41))))
    r2 = decide(_inp(hier2, rr=2.0))
    assert r2.p_t_hat is not None and abs(r2.p_t_hat - r.p_t_hat) < 1e-12


# ───────────────────────────── PARTEA 5 — E[X|h] lipsă intră ca −1 (nu zero) ─────────────────────────────
def test_missing_horizon_expectation_is_minus_one_not_zero() -> None:
    r = decide(_inp(_single(200, 80, nh=0), rr=2.0))                # nicio ieșire de orizont nicăieri
    assert r.e_x_h_missing is True and r.e_x_h == -1.0              # −1, NU 0
    # contrast: cu date de orizont, E[X|h] e media reală, nu −1
    r2 = decide(_inp(_single(200, 80, nh=40, sumh=+8.0), rr=2.0))   # 40 ieșiri de orizont, R mediu +0,2
    assert r2.e_x_h_missing is False and abs(r2.e_x_h - 0.2) < 1e-9  # type: ignore[operator]


def test_minus_one_is_worst_case_lowers_ev_versus_zero() -> None:
    """−1 e cel mai rău: EV cu E[X|h]=−1 < EV cu E[X|h]=0 (ar strecura presupunerea de orizont-pe-nul)."""
    assert ev_from_terms(0.3, 0.13, -1.0, 2.0, 0.05) < ev_from_terms(0.3, 0.13, 0.0, 2.0, 0.05)


# ───────────────────────────── PARTEA 5 — egalitatea D2, fezabilitatea, fail-closed ─────────────────────────────
def test_equality_is_no_trade_strict_inequality() -> None:
    ev0 = ev_from_terms(p_t=0.25, p_h=0.0, e_x_h=0.0, rr=3.0, cost_over_r=0.0)   # 0,25·3 − 0,75 = 0 EXACT
    assert ev0 == 0.0
    assert not (ev0 > 0.0)                                           # EV_LCB == 0 → NU intră (D2, strict)


def test_feasibility_gate_rr_must_exceed_cost_over_r() -> None:
    blocked = decide(_inp(_single(1000, 900), rr=0.5, r=1.0, cost=0.6))   # RR 0,5 ≤ c/R 0,6
    assert blocked.reason == Reason.NO_TRADE_FEASIBILITY.value and blocked.enter is False
    assert blocked.rr_min == 0.6
    ok = decide(_inp(_single(1000, 900), rr=2.0, r=1.0, cost=0.6))        # RR 2 > c/R 0,6
    assert ok.reason != Reason.NO_TRADE_FEASIBILITY.value


def test_fail_closed_named_field_no_silent_defaults() -> None:
    assert decide(_inp(_single(100, 40), rr=float("nan"))).missing_field == "rr"
    assert decide(_inp(_single(100, 40), cost=float("inf"))).missing_field == "cost"
    assert decide(_inp(_single(100, 40), r=0.0)).missing_field == "r"
    assert decide(_inp((), rr=2.0)).missing_field == "global_rate"          # ierarhie goală
    assert decide(_inp(_single(0, 0), rr=2.0)).missing_field == "global_rate"  # nici rata globală
    for bad in decide(_inp(_single(100, 40), rr=float("nan"))), decide(_inp((), rr=2.0)):
        assert bad.reason == Reason.NO_TRADE_MISSING.value and bad.enter is False


# ───────────────────────────── PARTEA 2 — `k` estimat prin momente, RAPORTAT (nu hardcodat) ─────────────────────────────
def test_k_estimated_small_for_heterogeneous_large_for_homogeneous() -> None:
    parent = _cell(1000, 400)
    cell = _cell(60, 24)
    het = (HierarchyLevel(cell=parent),
           HierarchyLevel(cell=cell, siblings=(_cell(100, 10), _cell(100, 50), _cell(100, 90))))
    hom = (HierarchyLevel(cell=parent),
           HierarchyLevel(cell=cell, siblings=(_cell(100, 40), _cell(100, 40), _cell(100, 40))))
    k_het = decide(_inp(het, rr=2.0)).k_per_level
    k_hom = decide(_inp(hom, rr=2.0)).k_per_level
    assert len(k_het) == 2 and k_het[0] == 0.0                       # nivelul 0 nu are k
    assert k_het[1] < 100.0                                          # surori eterogene → k mic (datele proprii contează)
    assert k_hom[1] > 1000.0                                         # surori omogene → k mare (contracție spre părinte)
    assert all(math.isfinite(x) for x in k_het)                      # raportat, finit


# ───────────────────────────── motorul NU alege direcția/stopul/ținta ─────────────────────────────
def test_engine_does_not_choose_direction_stop_target() -> None:
    r = decide(_inp(_single(1000, 400), rr=2.0))
    for attr in ("direction", "stop", "target", "stop_price", "target_price"):
        assert not hasattr(r, attr)                                 # răspunde doar „merită riscul?"
    for field in ("direction", "stop", "target"):
        assert field not in DecisionInput.__dataclass_fields__


def test_happy_path_enter_logs_full_audit_with_hash() -> None:
    r = decide(_inp(_single(2000, 900, nh=260, sumh=+13.0), rr=2.5, cost=0.20))
    assert r.reason == Reason.ENTER.value and r.enter is True
    assert r.ev_lcb is not None and r.ev_lcb > 0.0
    assert r.prob_table_hash and len(r.prob_table_hash) == 16       # hash-ul tabelei, pt. audit
    assert r.cost == 0.20 and r.rr_min == 0.20 / 1.0                # `c` parametru, c/R raportat
    assert r.p_t_lcb is not None and r.p_t_hat is not None and r.p_t_lcb <= r.p_t_hat
