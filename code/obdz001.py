"""OBDZ-001 — mașina de stare a PRIMEI ipoteze compuse (Statistician v2.7.11, doc 155a696). PURĂ, inertă.

Compune primitive verificate: bias H1/H4 (context-derived, forward-safe — pasat ca intrare) × intersecția
cross-candle DemandZone × OB nemitigat (`order_flow`, înghețat) → SL/TP1/TP2 pe ATR → ieșire parțială
(`partial_exit`, 4aa2b21). NU citește prețuri de pe disc, NU apelează `load()`, NU folosește `mtf.py`/
`load_mtf` (calea nativă sigilată). mypy --strict. Teste sintetice.

SPECIFICAȚIE RATIFICATĂ (neschimbată în afara amendamentului de bias context-derived):
  bias           ema20>ema50 pe H1_from_M15_v2 ȘI H4_from_M15_v2, consistente (ambele up / ambele down),
                 forward-safe (pasate ca `h1_trend`/`h4_trend` per bară de către caller — NU calculate aici).
  intrare        M15, next-open (t+1), în direcția bias-ului; declanșator t = prima Mitigation calificată a
                 OB_B (scan `formation_idx+2`, post-fix circularitate), CONDIȚIONAT de existența unei
                 DemandZone_A cross-candle: kind_A==kind_B, formation_A != formation_B, formation_A < t
                 (forward-safe), |formation_A−formation_B| <= 460, ACELAȘI bloc, suprapunere de interval
                 (OB_B corp × DemandZone_A range).
  SL             0,7 × ATR(14)[t];  TP1 1,4×ATR (închide 75% → breakeven);  TP2 2,1×ATR (restul 25%).
  plasă          min(entry+20, EOD).   eligibilitate: doar podeaua ATR $0,857, FĂRĂ plafon.
  variabila      net_R (via `partial_exit`, breakeven=entry-exact, cost 0,20 agregat).

SEPARARE ANTI-E010 (ca la celelalte 9 familii): SELECȚIA (`detect_obdz001_signals`) e funcție PURĂ de bare
`<= entry_idx` (trigger, bias@t, OB/DemandZone formate < t, ATR[t], open[t+1]); MĂSURAREA (`evaluate_obdz001`)
folosește calea `[entry_idx, measurement_end]` prin `partial_exit`, disjunctă prin construcție.
`test_obdz001.py::test_no_lookahead` demonstrează: mutarea barelor din fereastra de măsurare nu schimbă niciun
semnal anterior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from order_block_void import OrderBlock, OrderBlockKind
from order_flow import DemandZone, detect_demand_zones, detect_order_blocks
from partial_exit import PartialExitResult, simulate_partial_exit

ATR_FLOOR = 3.0 * 0.20 / 0.7      # ≈ 0,857$
HORIZON = 20
WEEK_BARS = 460
SL_MULT, TP1_MULT, TP2_MULT = 0.7, 1.4, 2.1
COST = 0.20


@dataclass(frozen=True)
class Obdz001Signal:
    trigger_idx: int          # t = prima Mitigation a OB_B
    entry_idx: int            # t+1, next-open
    direction: int            # +1 long / -1 short
    atr: float                # ATR14[t]
    entry_price: float
    sl_price: float
    tp1_price: float
    tp2_price: float
    eod_idx: int              # ultima bară a zilei de intrare (min cu entry+20 dă plasa)
    selection_end: int        # = entry_idx; selecția folosește DOAR bare <= selection_end
    measurement_start: int    # = entry_idx
    measurement_end: int      # = min(entry_idx + HORIZON, eod_idx)


def _first_mitigation(ob: OrderBlock, high: Sequence[float], low: Sequence[float], close: Sequence[float],
                      n: int) -> int | None:
    """Prima Mitigation calificată = `detect_mitigations(...)[0].event_idx`, cu ieșire timpurie (perf).
    Replică EXACT logica înghețată post-fix: scan de la `formation_idx+2`, oprire la breaker."""
    zl, zh = ob.zone_lower, ob.zone_upper
    bull = ob.kind is OrderBlockKind.BULLISH
    fidx = ob.formation_idx
    floor, ceiling = low[fidx], high[fidx]
    for i in range(fidx + 2, n):
        if bull and close[i] < floor:
            return None
        if (not bull) and close[i] > ceiling:
            return None
        if low[i] <= zh and high[i] >= zl:
            return i
    return None


def _eod_per_bar(day_index: Sequence[int], n: int) -> list[int]:
    """Ultima bară (index) a zilei fiecărei bare, forward-safe la nivel de zi (EOD = ancora 17:00 NY, caller)."""
    eod = [n - 1] * n
    last = n - 1
    for j in range(n - 1, -1, -1):
        if j < n - 1 and day_index[j] != day_index[j + 1]:
            last = j
        eod[j] = last
    return eod


def detect_obdz001_signals(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    atr: Sequence[float], h1_trend: Sequence[float], h4_trend: Sequence[float], day_index: Sequence[int],
    block_end: int, atr_floor: float = ATR_FLOOR,
) -> list[Obdz001Signal]:
    """SELECȚIA (pură, bare <= entry_idx). Vezi docstring-ul modulului pentru separarea anti-E010."""
    n = block_end
    obs = detect_order_blocks(open_, high, low, close, n)
    dzs = detect_demand_zones(open_, high, low, close, n)
    eod = _eod_per_bar(day_index, n)
    dz_by_kind: dict[OrderBlockKind, list[DemandZone]] = {OrderBlockKind.BULLISH: [], OrderBlockKind.BEARISH: []}
    for dz in dzs:
        dz_by_kind[dz.kind].append(dz)

    out: list[Obdz001Signal] = []
    for ob in obs:
        t = _first_mitigation(ob, high, low, close, n)
        if t is None or t + 1 >= n:
            continue
        obdir = 1 if ob.kind is OrderBlockKind.BULLISH else -1
        bias_up = h1_trend[t] > 0.5 and h4_trend[t] > 0.5
        bias_dn = h1_trend[t] <= 0.5 and h4_trend[t] <= 0.5
        biasdir = 1 if bias_up else (-1 if bias_dn else 0)
        if biasdir != obdir:                                        # bias@t trebuie = polaritatea OB_B
            continue
        ok = False
        for dz in dz_by_kind[ob.kind]:                              # (a) kind_A == kind_B
            if dz.formation_idx == ob.formation_idx:                # (b) formare diferită
                continue
            if dz.formation_idx >= t:                               # (c) forward-safe
                continue
            if abs(dz.formation_idx - ob.formation_idx) > WEEK_BARS:  # (d)
                continue
            if ob.zone_lower <= dz.zone_upper and ob.zone_upper >= dz.zone_lower:  # suprapunere
                ok = True
                break
        if not ok:
            continue
        atr_t = float(atr[t])
        if atr_t < atr_floor:                                       # (4) podea ATR, fără plafon
            continue
        entry = t + 1
        ep = float(open_[entry])
        r = SL_MULT * atr_t
        if obdir > 0:
            sl, tp1, tp2 = ep - r, ep + TP1_MULT * atr_t, ep + TP2_MULT * atr_t
        else:
            sl, tp1, tp2 = ep + r, ep - TP1_MULT * atr_t, ep - TP2_MULT * atr_t
        out.append(Obdz001Signal(
            trigger_idx=t, entry_idx=entry, direction=obdir, atr=atr_t, entry_price=ep,
            sl_price=sl, tp1_price=tp1, tp2_price=tp2, eod_idx=eod[entry],
            selection_end=entry, measurement_start=entry, measurement_end=min(entry + HORIZON, eod[entry])))
    return out


def evaluate_obdz001(
    signal: Obdz001Signal, high: Sequence[float], low: Sequence[float], close: Sequence[float],
    cost: float = COST,
) -> PartialExitResult:
    """MĂSURAREA (disjunctă de selecție): rulează `partial_exit` pe calea forward `[entry_idx, min(entry+20,EOD)]`.
    Breakeven=entry-exact, cost 0,20 agregat proporțional, default-urile ratificate (stop_before_target,
    tp1_tp2_same_bar)."""
    return simulate_partial_exit(
        signal.entry_idx, signal.direction, signal.entry_price, signal.sl_price, signal.tp1_price,
        signal.tp2_price, high, low, close, horizon=HORIZON, day_end_idx=signal.eod_idx, cost=cost)
