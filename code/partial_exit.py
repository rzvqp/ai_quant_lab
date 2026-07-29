"""PIESA 3 — mecanica de IEȘIRE PARȚIALĂ (Mandat curent, spec Statistician d9b4d12 Partea 4). PURĂ, inertă.

NU alege praguri de ATR, NU derivă filtre, NU decide bias — primește NIVELURILE (sl/tp1/tp2) ca PARAMETRI
și simulează doar MECANICA. NU citește prețuri de pe disc, NU rulează backtest. mypy --strict. Teste sintetice.

Mecanica cerută:
  TP1 atins  → închide 75% din poziție, MUTĂ stopul la BREAKEVEN pentru restul.
  TP2 atins  → închide restul de 25%.
  niciun TP  → închidere la limita de bare SAU la finalul zilei, ORICARE VINE PRIMA.

REZOLVAT în spec (nu le decid eu):
  • breakeven după TP1 = prețul de INTRARE EXACT (nu intrare+cost — costul e scăzut o singură dată, agregat).
  • limita de bare vs închiderea zilnică = `min(entry+horizon, day_end)` → ORIZONT VARIABIL (o tranzacție de
    seară are câteva bare, una de dimineață zeci); rezultatul se măsoară pe orizont variabil, nu fix.
  • cost TOTAL = 0,20$ agregat, proporțional pe tranșe (NU dublat): `cost_frac_leg = cost/R` fiecare, iar
    ponderarea 0,75/0,25 însumează exact `cost/R` o singură dată.
  • `net_R = 0,75×(R_leg1 − cost/R) + 0,25×(R_leg2 − cost/R)`.

ÎNTREBĂRI DESCHISE (implementate cu DEFAULT documentat + parametru; NU le decid — le semnalez, clasificare):
  Q-A [CLARIFICARE] Bara ambiguă TP1↔stop: dacă TP1 și stopul cad în ACEEAȘI bară, care câștigă? Convenția
     pre-înregistrată MIN_STOP_FLOOR_PREREG:31 (worst-case: stopul înaintea țintei, fill ambiguu = pierdere)
     e scrisă pentru ținta FINALĂ — se aplică IDENTIC la TP1? DEFAULT aici: `stop_before_target=True` (stopul
     câștigă, conservator). De confirmat.
  Q-B [CLARIFICARE] TP1 și TP2 în aceeași bară: se execută AMÂNDOUĂ? DEFAULT aici: `tp1_tp2_same_bar=True`
     (75% la TP1, apoi 25% la TP2, pe aceeași bară). De confirmat.
  (Bara de INTRARE însăși e exclusă din scanare — fill intrabar în aceeași bară = ambiguu/INVALID per
   MIN_STOP_FLOOR_PREREG:31; scanez de la `entry_idx+1`.)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

DEFAULT_COST = 0.20
LEG1_FRAC = 0.75
LEG2_FRAC = 0.25


@dataclass(frozen=True)
class PartialExitResult:
    net_R: float
    R_leg1: float          # multiplul de R al tranșei de 75%
    R_leg2: float          # multiplul de R al tranșei de 25%
    leg1_exit_idx: int
    leg2_exit_idx: int
    exit_reason: str       # stopped_full | tp1_then_tp2 | tp1_then_breakeven | tp1_then_timeout | timeout_no_tp1


def simulate_partial_exit(
    entry_idx: int, direction: int, entry_price: float, sl_price: float, tp1_price: float, tp2_price: float,
    high: Sequence[float], low: Sequence[float], close: Sequence[float], horizon: int, day_end_idx: int,
    cost: float = DEFAULT_COST, stop_before_target: bool = True, tp1_tp2_same_bar: bool = True,
) -> PartialExitResult:
    """Simulează mecanica 75/25 cu breakeven. `direction` = +1 long / −1 short. Nivelurile sunt PARAMETRI.
    `R = |entry − sl|` (risc în dolari). Vezi docstring-ul modulului pentru default-urile Q-A/Q-B."""
    n = len(close)
    R = abs(entry_price - sl_price)
    if R <= 0:
        raise ValueError("R (|entry − sl|) trebuie > 0")
    exit_limit = min(entry_idx + horizon, day_end_idx, n - 1)

    def tp_hit(j: int, level: float) -> bool:                # ținta = în favoarea direcției
        return float(high[j]) >= level if direction > 0 else float(low[j]) <= level

    def stop_hit(j: int, level: float) -> bool:              # stop/breakeven = contra direcției
        return float(low[j]) <= level if direction > 0 else float(high[j]) >= level

    def rmult(exit_price: float) -> float:
        return (exit_price - entry_price) * direction / R

    def result(reason: str, r1: float, r2: float, i1: int, i2: int) -> PartialExitResult:
        net = LEG1_FRAC * (r1 - cost / R) + LEG2_FRAC * (r2 - cost / R)
        return PartialExitResult(net_R=net, R_leg1=r1, R_leg2=r2, leg1_exit_idx=i1, leg2_exit_idx=i2, exit_reason=reason)

    r1 = 0.0
    tp1_idx = -1
    phase = 1
    for j in range(entry_idx + 1, exit_limit + 1):           # bara de intrare exclusă (Q intrabar → entry+1)
        if phase == 1:
            t1, s = tp_hit(j, tp1_price), stop_hit(j, sl_price)
            if s and (stop_before_target or not t1):         # Q-A default: stopul câștigă bara ambiguă
                r = rmult(sl_price)                          # = −1
                return result("stopped_full", r, r, j, j)
            if t1:
                r1, tp1_idx = rmult(tp1_price), j
                if tp1_tp2_same_bar and tp_hit(j, tp2_price):  # Q-B default: ambele pe aceeași bară
                    return result("tp1_then_tp2", r1, rmult(tp2_price), tp1_idx, j)
                phase = 2                                    # 25% rămas, stop mutat la breakeven (= entry)
        else:                                                # phase 2
            t2, be = tp_hit(j, tp2_price), stop_hit(j, entry_price)
            if be and (stop_before_target or not t2):        # breakeven câștigă bara ambiguă
                return result("tp1_then_breakeven", r1, 0.0, tp1_idx, j)
            if t2:
                return result("tp1_then_tp2", r1, rmult(tp2_price), tp1_idx, j)

    final = rmult(float(close[exit_limit]))                  # închidere pe timp (limită de bare / EOD)
    if phase == 1:
        return result("timeout_no_tp1", final, final, exit_limit, exit_limit)
    return result("tp1_then_timeout", r1, final, tp1_idx, exit_limit)
