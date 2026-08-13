"""ADAPTAREA MOTORULUI EV (Pasul 4). Motorul EV real (`_ev_core`, vândut byte-identic din `bdd15e5`) consumă un
tabel de CONTEO empiric-Bayes + scalarii rr/r/cost — NU tipuri de nivel. Adaptorul mapează geometria produsă de
TURNUL ACTUAL (N1-N4 + strategie) în `DecisionInput`, FĂRĂ să reactiveze logica veche de niveluri.

INTERZIS: înlocuirea motorului EV cu un simplu edge=True/False. Aici rulează formula ratificată:
    EV_R = p_t·RR − p_s·1 + p_h·E[X|h] − c/R   (gardă pe LCB, strict > 0).

MATRICEA de adaptare (obligatorie înainte de conectare):
  input EV vechi   sursa veche                    echivalent actual N1-N4        conversie/adaptor         pierdere semantică                              test
  ─────────────    ───────────────────────────    ───────────────────────────    ──────────────────────    ──────────────────────────────────────────    ────────────────
  rr               RR = target/R (Alpha)          entry/stop/target (strategie)  target_param sau            NICIUNA (raport pur)                            test_adapter_rr
                                                                                  |target−entry|/r
  r                R post-podea min_exec           |entry−stop| (canonic R3)      abs(entry−stop)             podeaua R3 e SUS (respinge, nu extinde);        test_adapter_r
                                                                                                             r aici e riscul CERUT, deja validat de N4/R3
  cost             c dus-întors (upper bound)      full_spread+slip (canonic R4)  spread O DATĂ + 2×slip     spread nu se dublează (v2.7.66)                 test_adapter_cost
  hierarchy        tabel empiric-Bayes pre-construit  REZULTATE ISTORICE ale       probability_inputs         ⚠ MARE: turnul NU produce conteo per-bară;      test_adapter_hierarchy
                   (global→celulă)                 strategiei validate            (celule OutcomeCell)       conteoul vine din ISTORIC, cheiat pe regim/     test_missing_prob→NO_TRADE
                                                                                                             bias. Absent ⇒ NO_TRADE (nu se inventează).
  credibility      nivel de credibilitate          declarat de strategie          probability_inputs.cred.   NICIUNA                                         test_adapter_cred

Pierderea semantică centrală: starea bogată a turnului (benzi de regim, factori de bias, confluență de zonă,
ordinala de confirmare) e COMPRIMATĂ în (a) geometria rr/r/cost și (b) CHEIA celulei de ierarhie. Motorul EV nu vede
regimul/biasul direct — doar statisticile celulei în care starea curentă se mapează. Fără celulă ⇒ fără probabilități
⇒ NO_TRADE. Aceasta e prin construcție: motorul răspunde „merită riscul?", nu „ce e pe piață?".
"""

from __future__ import annotations

from dataclasses import dataclass

from . import _ev_core
from .contracts import DecisionRequest

EV_ENGINE_SOURCE_COMMIT: str = "bdd15e5"
EV_ENGINE_SPEC: str = "STAT-DECISION-ENGINE-SPEC-v1.0"
EV_ADAPTER_VERSION: str = "ev-adapter-v1"
ENGINE_VERSION: str = f"ev-core@{EV_ENGINE_SOURCE_COMMIT}+{EV_ADAPTER_VERSION}"


@dataclass(frozen=True)
class EVOutcome:
    """Rezultatul motorului EV, deja mapat pentru OUTPUT MINIM."""
    enter: bool
    reason: str
    expected_value_net: float | None       # ev_lcb
    expected_reward: float | None          # p_t_lcb · rr
    expected_loss: float | None            # p_s · 1
    estimated_cost: float | None           # c / r
    probability_assumptions: dict[str, object]


def _rr_r_cost(req: DecisionRequest) -> tuple[float, float, float]:
    """Conversia geometriei ACTUALE → (rr, r, cost). r = risc CERUT; cost = spread O DATĂ + 2×slip (canonic R4)."""
    r = abs(req.entry_price - req.stop_price)
    if req.target_kind == "rr" and req.target_param is not None:
        rr = float(req.target_param)
    elif req.target_kind == "price" and req.target_param is not None and r > 0.0:
        rr = abs(req.target_param - req.entry_price) / r
    else:
        rr = 0.0                            # fără țintă → fără termen de recompensă (feasibilitate va pica)
    cost = req.full_spread_price + req.entry_slippage_price + req.exit_slippage_price
    return rr, r, cost


def run_ev(req: DecisionRequest) -> EVOutcome:
    """Rulează motorul EV real pe geometria+probabilitățile actuale. `probability_inputs is None` ⇒ NO_TRADE
    (MISSING) — nu se inventează probabilități. NU folosește tipuri de nivel vechi."""
    if req.probability_inputs is None:
        return EVOutcome(False, _ev_core.Reason.NO_TRADE_MISSING.value, None, None, None, None,
                         {"missing": "probability_inputs"})

    rr, r, cost = _rr_r_cost(req)
    hierarchy = tuple(
        _ev_core.HierarchyLevel(
            cell=_ev_core.OutcomeCell(lv.cell.n, lv.cell.n_target, lv.cell.n_horizon, lv.cell.sum_horizon_R),
            siblings=tuple(_ev_core.OutcomeCell(s.n, s.n_target, s.n_horizon, s.sum_horizon_R) for s in lv.siblings))
        for lv in req.probability_inputs.hierarchy)
    inp = _ev_core.DecisionInput(rr=rr, r=r, cost=cost, hierarchy=hierarchy,
                                 credibility=req.probability_inputs.credibility)
    res = _ev_core.decide(inp)

    p_t_lcb = res.p_t_lcb if res.p_t_lcb is not None else 0.0
    p_h = res.p_h_hat if res.p_h_hat is not None else 0.0
    p_s = max(0.0, 1.0 - p_t_lcb - p_h)
    reward = p_t_lcb * rr if res.p_t_lcb is not None else None
    loss = p_s if res.p_t_lcb is not None else None
    cost_over_r = (cost / r) if r > 0.0 else None
    return EVOutcome(
        enter=res.enter, reason=res.reason, expected_value_net=res.ev_lcb,
        expected_reward=reward, expected_loss=loss, estimated_cost=cost_over_r,
        probability_assumptions={
            "p_t_hat": res.p_t_hat, "p_t_lcb": res.p_t_lcb, "p_h_hat": res.p_h_hat,
            "e_x_h": res.e_x_h, "e_x_h_missing": res.e_x_h_missing, "credibility": req.probability_inputs.credibility,
            "k_per_level": list(res.k_per_level), "prob_table_hash": res.prob_table_hash,
            "rr": rr, "r": r, "cost": cost, "rr_min": res.rr_min},
    )
