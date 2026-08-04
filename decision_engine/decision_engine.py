"""MOTORUL DE DECIZIE — nivelul 6 (STAT-DECISION-ENGINE-SPEC-v1.0, ccb31d9, manifest v2.7.47).

Funcție PURĂ: „merită riscul?" pentru un setup DEJA complet definit (direcție/stop/țintă = ale lui Alpha, NEatinse).
Fără MT5, fără date reale. Construită STRICT după spec — NU proiectez metoda, impun formula ratificată.

MODEL cu TREI rezultate (Partea 0-1): winrate NU e probabilitatea din EV. Probabilitatea care intră în EV e cea de
ATINGERE A ȚINTEI (`p_t`), separată de ieșirea pe orizont (`p_h`, cu R-ul ei mediu cu semn `E[X|h]`) și de stop
(`p_s = 1 − p_t − p_h`). Un model cu două rezultate ar atribui payoff-ul RR unor tranzacții time-stop care nu l-au
primit — supraevaluare cu un ordin de mărime.

    EV_R = p_t·RR − p_s·1 + p_h·E[X|h] − c/R            (Partea 1)

PROBABILITATE (Partea 2): contracție ierarhică empirical-Bayes. `p̂ = (n·p + k·p̂_părinte)/(n+k)`. `k` NU se alege:
se estimează prin momente din varianța ÎNTRE celule (Beta-Binomial) și SE RAPORTEAZĂ. La `n=0` formula dă exact
părintele — setup nou moștenește strămoșul, fără caz special. Fără nici măcar rata globală ⇒ refuz (fail-closed).

O SINGURĂ POARTĂ (Partea 3): pragurile de RR și „confidence" sunt CONȚINUTE în EV. Se intră ⇔ `EV_LCB > 0`, unde
`EV_LCB` folosește `p_t` la LIMITA INFERIOARĂ a intervalului de credibilitate (80% unilateral ⇒ cuantila 0,20 a
posteriorului Beta). Istoric bogat → interval îngust → LCB≈punct → trece; setup nou → interval lat → LCB mic → nu
trece; mai multe date → poartă mai relaxată, MONOTON. Fiecare input incert intră la capătul PESIMIST (`p_t` jos,
`c` sus). Nivelul 80% e SINGURA alegere, ancorată la DEMO (măsurare), se strânge la 95% după DEMO.

COST (Partea 4): `c` = PARAMETRU citit la decizie, niciodată constantă compilată. Rămâne 0,20 (0,10 spread + 0,10
slippage convențional) până există FILL-uri — 0,05 e o cifră de spread și ar seta tăcut slippage-ul la zero.

CRITERIU (Partea 5): fezabilitate `RR > c/R` (altfel NO-TRADE); `EV_LCB > 0` STRICT (egalitate → NO-TRADE, convenția
D2); orice input absent/ne-finit ⇒ NO-TRADE cu CÂMPUL NUMIT, fără valori implicite. EXCEPȚIE: `E[X|h]` lipsă intră ca
`−1` (cel mai rău, nu zero — zero ar strecura presupunerea că orizontul iese pe nul), fiind singurul termen care
poate ÎMBUNĂTĂȚI EV.

GUVERNANȚĂ: motorul NU e ipoteză testabilă, NU consumă slot de familie (agregare peste politici deja numărate).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence

# Praguri/limite DEGENERATE declarate (NU estimarea — aceea e prin momente, mai jos). `k` estimat se raportează.
_K_MAX: float = 1.0e6            # celule omogene (varianță între-celule ~0) ⇒ contracție ~totală spre părinte
_K_MIN_PRIOR: float = 1.0e-6     # podea numerică pentru a păstra Beta bine-definit (α,β>0)
_CREDIBILITY_DEFAULT: float = 0.80   # unilateral; LCB = cuantila (1 − 0,80) = 0,20
_EXH_MISSING: float = -1.0       # E[X|h] lipsă = cel mai rău (Partea 5), NU zero


class Reason(Enum):
    ENTER = "enter"
    NO_TRADE_EV_LCB = "no_trade_ev_lcb_not_positive"          # EV_LCB <= 0 (inclusiv egalitatea, D2)
    NO_TRADE_FEASIBILITY = "no_trade_feasibility"             # RR <= c/R
    NO_TRADE_MISSING = "no_trade_missing_input"               # fail-closed, câmp numit


@dataclass(frozen=True)
class OutcomeCell:
    """Numărătorile unei celule din ierarhie (un nod, un nivel). `n_stop` = n − n_target − n_horizon."""
    n: int                       # tranzacții totale în celulă
    n_target: int                # ieșiri la ȚINTĂ
    n_horizon: int               # ieșiri pe ORIZONT (time-stop)
    sum_horizon_R: float         # suma R-ului cu SEMN pe ieșirile de orizont (E[X|h] = sumă / n_horizon)


@dataclass(frozen=True)
class HierarchyLevel:
    """Un nivel al ierarhiei pentru ACEST setup: celula proprie + celulele-surori (pt. estimarea lui `k`)."""
    cell: OutcomeCell
    siblings: tuple[OutcomeCell, ...] = ()    # toate celulele de la acest nivel sub același părinte (incl. cell)


@dataclass(frozen=True)
class DecisionInput:
    """Descriptorii disponibili la momentul deciziei. `rr`/`r` = ale politicii (pe R PODIT); `cost` = parametru."""
    rr: float                    # RR = distanța până la țintă / R (adimensional, la intrare, pe R podit)
    r: float                     # R = distanța de risc în PREȚ, după podeaua min_executable_risk
    cost: float                  # c = cost round-trip în PREȚ, la limita SUPERIOARĂ (pesimist)
    hierarchy: tuple[HierarchyLevel, ...]     # nivel 0 (global) → cel mai adânc disponibil
    credibility: float = _CREDIBILITY_DEFAULT


@dataclass(frozen=True)
class DecisionResult:
    reason: str
    enter: bool
    ev_lcb: float | None
    ev_point: float | None       # EV la estimarea punctuală (audit)
    p_t_hat: float | None        # p_t contractat, estimare punctuală
    p_t_lcb: float | None        # p_t la limita inferioară a intervalului
    p_h_hat: float | None
    e_x_h: float | None          # E[X|h] (−1 dacă lipsește; vezi spec)
    e_x_h_missing: bool
    rr: float
    r: float
    cost: float
    rr_min: float                # c/R (fezabilitate)
    k_per_level: tuple[float, ...]           # `k` estimat pe fiecare nivel — RAPORTAT
    prob_table_hash: str         # hash-ul tabelei de probabilități (audit — cifrele se mișcă)
    missing_field: str | None


# ── incomplete beta regularizat + inversă (pure, fără scipy) ──
def _betacf(a: float, b: float, x: float) -> float:
    maxit, eps, fpmin = 300, 3.0e-14, 1.0e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, maxit + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def _betai(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a,b) = P(Beta(a,b) <= x)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def _beta_ppf(q: float, a: float, b: float) -> float:
    """Cuantila Beta(a,b) la q, prin bisecție pe CDF-ul regularizat. a,b>0, q∈(0,1)."""
    if q <= 0.0:
        return 0.0
    if q >= 1.0:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _betai(a, b, mid) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ── estimarea lui k prin momente (Beta-Binomial), din varianța ÎNTRE celule ──
def _estimate_k(siblings: Sequence[OutcomeCell], succ: Callable[[OutcomeCell], int]) -> float:
    """Potrivire de momente: k = m(1−m)/σ²_între − 1. σ²_între din descompunerea ANOVA ponderată.
    Omogen (σ²_între≤0) ⇒ k mare (contracție ~totală). Insuficiente surori (C<2) ⇒ k=0 (fără contracție,
    doar datele proprii — un setup nou fără bază comparativă rămâne cu interval lat). Se RAPORTEAZĂ."""
    cells = [s for s in siblings if s.n > 0]
    n_i = [float(s.n) for s in cells]
    y_i = [float(succ(s)) for s in cells]
    big_n = sum(n_i)
    ccount = len(cells)
    if ccount < 2 or big_n <= 0.0:
        return 0.0                                            # fără bază comparativă → nicio contracție
    m = sum(y_i) / big_n
    if m <= 0.0 or m >= 1.0:
        return _K_MAX                                         # toate celulele la 0 sau 1 → identice → părinte
    p_i = [y / n for y, n in zip(y_i, n_i)]
    ssb = sum(n * (p - m) ** 2 for p, n in zip(p_i, n_i))     # SS ponderat între-celule
    n0 = (big_n - sum(n * n for n in n_i) / big_n) / (ccount - 1)
    if n0 <= 0.0:
        return _K_MAX
    msb = ssb / (ccount - 1)
    sigma2_between = (msb - m * (1.0 - m)) / n0               # E[MSB] = m(1−m) + n0·σ²_între
    if sigma2_between <= 0.0:
        return _K_MAX                                         # omogen → contracție totală spre părinte
    k = m * (1.0 - m) / sigma2_between - 1.0
    return min(max(k, 0.0), _K_MAX)


# ── contracția unei PROPORȚII prin ierarhie; întoarce (media, α, β, k-uri) la cel mai adânc nivel ──
def _shrink_proportion(
    hierarchy: Sequence[HierarchyLevel], succ: Callable[[OutcomeCell], int],
) -> tuple[float, float, float, list[float]]:
    l0 = hierarchy[0].cell
    mu = succ(l0) / l0.n                                      # rata globală brută (l0.n>0 garantat de apelant)
    alpha = max(float(succ(l0)), _K_MIN_PRIOR)
    beta = max(float(l0.n - succ(l0)), _K_MIN_PRIOR)
    ks: list[float] = [0.0]                                   # nivelul 0 nu are părinte → fără k
    for lvl in hierarchy[1:]:
        k = _estimate_k(lvl.siblings, succ)
        ks.append(k)
        cell = lvl.cell
        y, n = float(succ(cell)), float(cell.n)
        # `k_eff>0` păstrează RAPORTUL α:β = μ:(1−μ) la orice k (deci la n=0 media = EXACT părintele, indiferent
        # de k); când k=0 (surori eterogene) `k_eff` e infinitezimal ⇒ interval MAXIM de lat (LCB→0), nu simetrizat.
        k_eff = max(k, _K_MIN_PRIOR)
        alpha = k_eff * mu + y                                # prior Beta(k·μ_părinte, k·(1−μ)) + date
        beta = k_eff * (1.0 - mu) + (n - y)
        if alpha <= 0.0:                                      # degenerat (μ=0 ȘI y=0) — doar atunci simetrizăm
            alpha = _K_MIN_PRIOR
        if beta <= 0.0:
            beta = _K_MIN_PRIOR
        mu = alpha / (alpha + beta)                           # media contractată devine părintele nivelului următor
    return mu, alpha, beta, ks


def _shrink_mean_horizon(hierarchy: Sequence[HierarchyLevel], ks: Sequence[float]) -> float | None:
    """E[X|h] contractat cu ACELAȘI k (ponderi = n_horizon). None dacă NICIUN strămoș nu are ieșiri de orizont."""
    running: float | None = None
    l0 = hierarchy[0].cell
    if l0.n_horizon > 0:
        running = l0.sum_horizon_R / l0.n_horizon
    for idx, lvl in enumerate(hierarchy[1:], start=1):
        cell = lvl.cell
        if cell.n_horizon <= 0:
            continue                                          # contracție la părinte (celulă fără date de orizont)
        cell_mean = cell.sum_horizon_R / cell.n_horizon
        if running is None:
            running = cell_mean
        else:
            k = ks[idx]
            running = (cell.n_horizon * cell_mean + k * running) / (cell.n_horizon + k)
    return running


def ev_from_terms(p_t: float, p_h: float, e_x_h: float, rr: float, cost_over_r: float) -> float:
    """EV_R = p_t·RR − p_s·1 + p_h·E[X|h] − c/R, cu p_s = 1 − p_t − p_h (clamp ≥0 pt. consistență de proporții)."""
    p_s = 1.0 - p_t - p_h
    if p_s < 0.0:                                             # p_t (LCB) + p_h > 1 din contracții separate → clamp
        p_s = 0.0
    return p_t * rr - p_s * 1.0 + p_h * e_x_h - cost_over_r


def _hash_hierarchy(hierarchy: Sequence[HierarchyLevel]) -> str:
    payload = [[[c.n, c.n_target, c.n_horizon, c.sum_horizon_R]
                for c in (lvl.cell,) + tuple(lvl.siblings)] for lvl in hierarchy]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _fail(field: str, inp: DecisionInput) -> DecisionResult:
    return DecisionResult(
        reason=Reason.NO_TRADE_MISSING.value, enter=False, ev_lcb=None, ev_point=None, p_t_hat=None,
        p_t_lcb=None, p_h_hat=None, e_x_h=None, e_x_h_missing=True, rr=inp.rr, r=inp.r, cost=inp.cost,
        rr_min=float("nan"), k_per_level=(), prob_table_hash="", missing_field=field)


def decide(inp: DecisionInput) -> DecisionResult:
    """Decizia + EV + intervalul lui p + motivul, pentru un setup complet definit. Funcție PURĂ."""
    # ── fail-closed: inputuri absente/ne-finite, CÂMPUL NUMIT, fără valori implicite ──
    for name, val in (("rr", inp.rr), ("r", inp.r), ("cost", inp.cost), ("credibility", inp.credibility)):
        if not math.isfinite(val):
            return _fail(name, inp)
    if inp.r <= 0.0:
        return _fail("r", inp)                                # R>0 prin definiție (distanța podită)
    if not (0.0 < inp.credibility < 1.0):
        return _fail("credibility", inp)
    if len(inp.hierarchy) == 0 or inp.hierarchy[0].cell.n <= 0:
        return _fail("global_rate", inp)                      # fără nici măcar rata globală → refuz

    cost_over_r = inp.cost / inp.r
    rr_min = cost_over_r
    table_hash = _hash_hierarchy(inp.hierarchy)

    # ── fezabilitate (filtru dur, Partea 5 pas 4): RR > c/R ──
    if inp.rr <= rr_min:
        return DecisionResult(
            reason=Reason.NO_TRADE_FEASIBILITY.value, enter=False, ev_lcb=None, ev_point=None, p_t_hat=None,
            p_t_lcb=None, p_h_hat=None, e_x_h=None, e_x_h_missing=True, rr=inp.rr, r=inp.r, cost=inp.cost,
            rr_min=rr_min, k_per_level=(), prob_table_hash=table_hash, missing_field=None)

    # ── probabilitatea din ierarhie (Partea 2) ──
    p_t_hat, alpha_t, beta_t, ks = _shrink_proportion(inp.hierarchy, lambda c: c.n_target)
    p_h_hat, _a_h, _b_h, _ks_h = _shrink_proportion(inp.hierarchy, lambda c: c.n_horizon)
    q_lcb = 1.0 - inp.credibility                             # 80% unilateral → cuantila 0,20
    p_t_lcb = _beta_ppf(q_lcb, alpha_t, beta_t)

    exh_raw = _shrink_mean_horizon(inp.hierarchy, ks)
    e_x_h_missing = exh_raw is None
    e_x_h = _EXH_MISSING if exh_raw is None else exh_raw      # lipsă → −1 (cel mai rău, NU zero)

    ev_point = ev_from_terms(p_t_hat, p_h_hat, e_x_h, inp.rr, cost_over_r)
    ev_lcb = ev_from_terms(p_t_lcb, p_h_hat, e_x_h, inp.rr, cost_over_r)

    enters = ev_lcb > 0.0                                     # STRICT; egalitate → NO-TRADE (D2)
    reason = Reason.ENTER.value if enters else Reason.NO_TRADE_EV_LCB.value
    return DecisionResult(
        reason=reason, enter=enters, ev_lcb=ev_lcb, ev_point=ev_point, p_t_hat=p_t_hat, p_t_lcb=p_t_lcb,
        p_h_hat=p_h_hat, e_x_h=e_x_h, e_x_h_missing=e_x_h_missing, rr=inp.rr, r=inp.r, cost=inp.cost,
        rr_min=rr_min, k_per_level=tuple(ks), prob_table_hash=table_hash, missing_field=None)
