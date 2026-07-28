"""Familiile SMC_S* formalizate ca mașini de stare discrete (MK, Mandat 5.9).

Interoghează funcțiile TIPIZATE din cele șapte module primitive ÎNGHEȚATE (market_structure,
liquidity_mechanics, imbalance_mechanics, institutional_levels, order_flow, market_state, interactions).
NU citește prețuri de pe disc, NU apelează `.load()`, NU rulează backtest. Module INERTE. mypy --strict.

Formalizări RATIFICATE integral din manifest v2.5.8 (`74de879`) + doc `e91c942`
(`statistician/STATISTICIAN_SMC_S_STATE_MACHINES_v1.0.md`, Mandat 3.18). NU reconstituite din mesaje.

NOUĂ familii complet formalizabile: S1, S2, S3, S7, S10, S11, S13, S16, S17.
NEformalizate (marcate, NU construite): S4/S8/S9/S14/**S15**/S20 (primitivă lipsă), S12 (parțial),
S5/S6/S19 (gol ieftin), S18 (dimensiune de stratificare, nu familie). Vezi `UNFORMALIZED_FAMILIES`.

⚠ CORECȚIE 1 (CEO): S15 „Trend Acceleration" NU e formalizat — Statisticianul l-a declarat GENUIN GOL la
   3.18 (niciun concept nu-l acoperă). NU inventez o mașină de stare pentru el.
⚠ CORECȚIE 3 (CEO): `net_R` per tranzacție cere PREȚURI de ieșire → NU se poate calcula cu module inerte.
   Aici implementez STRUCTURA + contractul de risc, cu SEMNĂTURA `net_R(...)` care l-ar produce, dar NU îl
   calculez. Calculul efectiv vine când LM-001 (= SMC_S1) se deblochează, cu prețuri reale.
⚠ Orizont per-familie: doc-ul RAFINEAZĂ contractul uniform „c+20" al mandatului — S1/S2/S3/S7/S10/S11/S13 =
   GRUPA A (20 bare); S16 = GRUPA C zi (92 bare); S17 = GRUPA C săptămână (460 bare). Urmez doc-ul (sursa
   autoritară desemnată) și SEMNALEZ rafinarea.

CONTRACTUL Open-R (identic tuturor, șablonul comun al doc-ului §„cadrul de risc"):
  `R_i = (spike_i + 2 pips) × TICK(0,10$)`, NICIODATĂ lărgit (stop structural la spike + 2 pips, fără podea).
  filtru eligibilitate: `spike_i ∈ [10,1 ; 65,0)` pips — altfel SKIP.
  `net_R_i = direcție_i × (preț_ieșire − preț_intrare)/R_i − cost/R_i`, cost = 0,40$. (SEMNĂTURĂ, nu calcul.)
  orizont: ieșire pură pe TIMP la `entry + H` bare M15, FĂRĂ take-profit.

SEPARARE ANTI-E010 (aceeași disciplină ca la order_flow MK-05): fiecare semnal poartă ferestre DISJUNCTE
prin construcție — SELECȚIA (trigger + spike + eligibilitate) e funcție PURĂ de barele `<= entry_idx`;
MĂSURAREA `[entry_idx, entry_idx+H]` NU alimentează niciodată selecția. `test_trading_strategies.py`
demonstrează per familie: mutarea barelor din fereastra de măsurare nu schimbă semnalul.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from market_structure import (
    Block, BreakKind, StructureBreak, StructureLabel, Swing, SwingKind,
    detect_breaks, detect_swings, label_structure,
)
from liquidity_mechanics import PoolSide, PoolTier, build_pools, detect_sweeps
from imbalance_mechanics import FVGKind, detect_fvg_reactions, detect_fvgs

TICK = 0.10
COST = 0.40
STOP_BUFFER_PIPS = 2.0
ELIG_LO = 10.1
ELIG_HI = 65.0
HORIZON_GROUP_A = 20          # reacție imediată (LM-001, london=5h=20 bare M15)
HORIZON_GROUP_C_DAY = 92      # mediană empirică zilnică (Statistician 3.18, calculată direct)
HORIZON_GROUP_C_WEEK = 460    # mediană empirică săptămânală (Statistician 3.18)
K_DEFAULT = 2

# Familii NEformalizate — marcate, NU construite (Corecția 1 + doc §11 goluri).
UNFORMALIZED_FAMILIES: dict[str, str] = {
    "S4": "GAPPED — cere clasificator de regim de volatilitate, absent din module",
    "S5": "GAP IEFTIN — cere high/low al primelor K bare de sesiune (opening range)",
    "S6": "GAP IEFTIN — cere high/low al sesiunii ANTERIOARE",
    "S8": "GAPPED — cere distanță relativă la ATR (există în lab, nu în module)",
    "S9": "GAPPED — cere trend multi-timeframe H1/H4/D1",
    "S12": "PARȚIAL — lipsește primitiva 'pereche de bazine ce delimitează un range stabil'",
    "S14": "GAPPED — cere indicator ROC/RSI",
    "S15": "GENUIN GOL (Statistician 3.18) — niciun concept nu-l acoperă; NU inventat",
    "S18": "NOT_A_STANDALONE_FAMILY — dimensiune de stratificare (oră/sesiune), nu declanșator",
    "S19": "GAP IEFTIN — cere preț de deschidere/închidere de sesiune",
    "S20": "GAPPED — depinde de aceeași lipsă MTF ca S9",
}


@dataclass(frozen=True)
class StrategySignal:
    """Un setup de intrare produs de o mașină de stare. NU conține net_R (cere prețuri — Corecția 3)."""
    family: str
    trigger_idx: int          # bara la care trigger-ul se COMPLETEAZĂ (forward-confirmat)
    entry_idx: int            # next-open = trigger_idx + 1
    direction: int            # +1 long / -1 short
    spike_pips: float         # distanța structurală (la extremul/nivelul de stop), în pips
    selection_end: int        # = entry_idx; selecția folosește DOAR bare <= selection_end
    measurement_start: int    # = entry_idx
    measurement_end: int      # = min(entry_idx + H, n); STRICT înainte, nu alimentează selecția


def risk_R_dollars(spike_pips: float) -> float:
    """R în $ = (spike + 2 pips) × TICK. NICIODATĂ lărgit, fără podea (contractul Open-R)."""
    return (spike_pips + STOP_BUFFER_PIPS) * TICK


def net_R(signal: StrategySignal, entry_price: float, exit_price: float) -> float:
    """SEMNĂTURA care PRODUCE net_R — Corecția 3: NU se apelează în detecție (module inerte, fără prețuri).
    Se apelează DOAR când LM-001 (=SMC_S1) se deblochează, cu preț real de intrare/ieșire.
    `net_R = direcție × (ieșire − intrare)/R − cost/R`."""
    R = risk_R_dollars(signal.spike_pips)
    return signal.direction * (exit_price - entry_price) / R - COST / R


def _emit(
    family: str, trigger_idx: int, entry_idx: int, direction: int, spike_price: float, horizon: int, n: int,
) -> StrategySignal | None:
    """Aplică filtrul de eligibilitate + separarea de ferestre. `spike_price` = distanța structurală în $
    (semn ignorat). Returnează None dacă intrarea iese din serie sau spike ∉ [10,1;65,0) (SKIP)."""
    if entry_idx < 0 or entry_idx >= n:
        return None
    spike_pips = abs(spike_price) / TICK
    if not (ELIG_LO <= spike_pips < ELIG_HI):
        return None
    return StrategySignal(
        family=family, trigger_idx=trigger_idx, entry_idx=entry_idx, direction=direction,
        spike_pips=spike_pips, selection_end=entry_idx, measurement_start=entry_idx,
        measurement_end=min(entry_idx + horizon, n))


def _labeled_swings(high: Sequence[float], low: Sequence[float], blocks: Sequence[Block],
                    k: int) -> list[Swing]:
    return label_structure(detect_swings(high, low, blocks, k))


# ─────────────────────────────── S1 — Liquidity Sweep Reversal (≡ LM-001) ───────────────────────────────
def detect_s1(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    blocks: Sequence[Block], k: int = K_DEFAULT, horizon: int = HORIZON_GROUP_A,
) -> list[StrategySignal]:
    """Sweep-reject de bazin extern (D6 fitil + D7 close-back-inside) → reversal. Intrare next-open,
    direcție mecanică. Spike = distanța de la open[c+1] la EXTREMUL FITILULUI de sweep (low[c]/high[c]),
    convenția LM-001 (lm001_geometry_audit). Orizont GRUPA A (20)."""
    n = len(close)
    swings = _labeled_swings(high, low, blocks, k)
    pools = build_pools(swings, PoolTier.EXTERNAL)
    sweeps = detect_sweeps(high, low, close, pools, blocks, require_close_back_inside=True)
    out: list[StrategySignal] = []
    for sw in sweeps:
        c = sw.idx
        entry = c + 1
        if entry >= n:
            continue
        if sw.pool.side is PoolSide.BELOW:
            direction = +1
            spike_price = open_[entry] - low[c]          # extremul fitilului = low-ul de sweep
        else:
            direction = -1
            spike_price = high[c] - open_[entry]
        sig = _emit("S1", c, entry, direction, spike_price, horizon, n)
        if sig is not None:
            out.append(sig)
    return out


def _first_break_after(breaks: Sequence[StructureBreak], kind: BreakKind, lo: int, hi: int) -> StructureBreak | None:
    """Primul break de tip `kind` cu idx în (lo, hi]. Forward-only: caută înainte, oprește la primul."""
    best: StructureBreak | None = None
    for b in breaks:
        if b.kind is kind and lo < b.idx <= hi:
            if best is None or b.idx < best.idx:
                best = b
    return best


# ─────────────────────────────── S2 — Failed Breakout / Failed Sweep (fade) ───────────────────────────────
def detect_s2(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    blocks: Sequence[Block], k: int = K_DEFAULT, horizon: int = HORIZON_GROUP_A,
) -> list[StrategySignal]:
    """BOS în direcția D → un CHoCH OPUS survine în ≤20 bare (fereastră de calificare GRUPA A) → intrare
    next-open după CHoCH, direcție = OPUSĂ BOS (fade). Fără CHoCH calificat → BOS neeligibil (exclus).
    Spike = distanța de la intrare la nivelul BOS spart (reference_swing.price)."""
    n = len(close)
    swings = _labeled_swings(high, low, blocks, k)
    breaks = detect_breaks(close, swings, blocks)
    out: list[StrategySignal] = []
    for br in breaks:
        if br.kind is BreakKind.BOS_BULL:
            opp, fade = BreakKind.CHOCH_BEAR, -1
        elif br.kind is BreakKind.BOS_BEAR:
            opp, fade = BreakKind.CHOCH_BULL, +1
        else:
            continue
        ch = _first_break_after(breaks, opp, br.idx, br.idx + horizon)   # calificare [b, b+20]
        if ch is None:
            continue
        entry = ch.idx + 1
        spike_price = open_[entry] - br.reference_swing.price if entry < n else 0.0
        sig = _emit("S2", ch.idx, entry, fade, spike_price, horizon, n)
        if sig is not None:
            out.append(sig)
    return out


# ─────────────────────────────── S3 — Breakout Retest Continuation ───────────────────────────────
def detect_s3(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    blocks: Sequence[Block], k: int = K_DEFAULT, horizon: int = HORIZON_GROUP_A,
) -> list[StrategySignal]:
    """BOS în direcția D → o bară ATINGE nivelul spart (fitil) în ≤20 bare DAR ÎNCHIDEREA rămâne de partea
    breakout-ului (nu se închide înapoi) → intrare next-open, direcție = ACEEAȘI ca BOS (continuare).
    Disjunct de S2 pe aceeași bară de retest (close-through vs nu-close-through). Spike = dist la nivel."""
    n = len(close)
    swings = _labeled_swings(high, low, blocks, k)
    breaks = detect_breaks(close, swings, blocks)
    out: list[StrategySignal] = []
    for br in breaks:
        if br.kind is BreakKind.BOS_BULL:
            direction = +1
        elif br.kind is BreakKind.BOS_BEAR:
            direction = -1
        else:
            continue
        level = br.reference_swing.price
        b = br.idx
        rt: int | None = None
        for j in range(b + 1, min(b + horizon, n - 1) + 1):              # retest în (b, b+20]
            if direction == +1 and low[j] <= level and close[j] > level:
                rt = j; break
            if direction == -1 and high[j] >= level and close[j] < level:
                rt = j; break
        if rt is None:
            continue
        entry = rt + 1
        spike_price = open_[entry] - level if entry < n else 0.0
        sig = _emit("S3", rt, entry, direction, spike_price, horizon, n)
        if sig is not None:
            out.append(sig)
    return out


# ─────────────────────────────── S7 — Trend-Pullback Continuation ───────────────────────────────
def detect_s7(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    blocks: Sequence[Block], k: int = K_DEFAULT, horizon: int = HORIZON_GROUP_A,
) -> list[StrategySignal]:
    """Trend stabilit prin ≥2 swing-uri clasificate de aceeași direcție (HH+HL / LH+LL) → următorul swing
    de continuare (nou HL în uptrend / nou LH în downtrend) → intrare next-open după confirmed_idx.
    Structura opusă (LL în uptrend / HH în downtrend) RESETEAZĂ trendul. Orizont GRUPA A (declarat)."""
    n = len(close)
    swings = _labeled_swings(high, low, blocks, k)
    out: list[StrategySignal] = []
    have_hh = have_hl = have_lh = have_ll = False
    for s in sorted(swings, key=lambda x: x.confirmed_idx):
        if s.label is StructureLabel.HH:
            have_hh, have_ll, have_lh = True, False, False
        elif s.label is StructureLabel.LL:
            have_ll, have_hh, have_hl = True, False, False
        elif s.label is StructureLabel.HL:
            if have_hh and have_hl:                                      # uptrend deja stabilit → continuă
                entry = s.confirmed_idx + 1
                spike_price = open_[entry] - s.price if entry < n else 0.0
                sig = _emit("S7", s.confirmed_idx, entry, +1, spike_price, horizon, n)
                if sig is not None:
                    out.append(sig)
            have_hl = True
        elif s.label is StructureLabel.LH:
            if have_ll and have_lh:                                      # downtrend deja stabilit → continuă
                entry = s.confirmed_idx + 1
                spike_price = s.price - open_[entry] if entry < n else 0.0
                sig = _emit("S7", s.confirmed_idx, entry, -1, spike_price, horizon, n)
                if sig is not None:
                    out.append(sig)
            have_lh = True
    return out


# ─────────────────────────────── S10 — Displacement Continuation (BOS ca displacement) ───────────────────────────────
def detect_s10(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    blocks: Sequence[Block], k: int = K_DEFAULT, horizon: int = HORIZON_GROUP_A,
) -> list[StrategySignal]:
    """Substituție DECLARATĂ (doc §S10): BOS joacă rolul de „displacement" (rupere direcțională decisivă
    prin închidere) — ATR-ul legacy e în afara modulelor. BOS confirmat → intrare next-open imediat,
    direcție = BOS, testează CONTINUAREA (spre deosebire de fade-ul S2). Spike = dist la nivelul BOS."""
    n = len(close)
    swings = _labeled_swings(high, low, blocks, k)
    breaks = detect_breaks(close, swings, blocks)
    out: list[StrategySignal] = []
    for br in breaks:
        if br.kind is BreakKind.BOS_BULL:
            direction = +1
        elif br.kind is BreakKind.BOS_BEAR:
            direction = -1
        else:
            continue
        entry = br.idx + 1
        if entry >= n:
            continue
        spike_price = open_[entry] - br.reference_swing.price
        sig = _emit("S10", br.idx, entry, direction, spike_price, horizon, n)
        if sig is not None:
            out.append(sig)
    return out


# ─────────────────────────────── S11 — Structure-Break Reversal (CHoCH primar) ───────────────────────────────
def detect_s11(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    blocks: Sequence[Block], k: int = K_DEFAULT, horizon: int = HORIZON_GROUP_A,
) -> list[StrategySignal]:
    """CHoCH ca semnal PRIMAR (nu urmarea unui BOS eșuat recent — distinct de S2) → intrare next-open după
    confirmarea CHoCH, direcție = NOUA direcție (opusă trendului anterior). Spike = dist la extremul CHoCH.
    S11 vs S2: ambele pe CHoCH — coliziune de dedublat prin hash la înrolare (doc §dedublare)."""
    n = len(close)
    swings = _labeled_swings(high, low, blocks, k)
    breaks = detect_breaks(close, swings, blocks)
    out: list[StrategySignal] = []
    for br in breaks:
        if br.kind is BreakKind.CHOCH_BULL:
            direction = +1
        elif br.kind is BreakKind.CHOCH_BEAR:
            direction = -1
        else:
            continue
        entry = br.idx + 1
        if entry >= n:
            continue
        spike_price = open_[entry] - br.reference_swing.price
        sig = _emit("S11", br.idx, entry, direction, spike_price, horizon, n)
        if sig is not None:
            out.append(sig)
    return out


# ─────────────────────────────── S13 — Liquidity Void / Imbalance Fill ───────────────────────────────
def detect_s13(
    open_: Sequence[float], high: Sequence[float], low: Sequence[float], close: Sequence[float],
    blocks: Sequence[Block], horizon: int = HORIZON_GROUP_A,
) -> list[StrategySignal]:
    """FVG se formează → atingere CE-50 (fitil, consumare D7 = `ce50_touch_idx`) → intrare next-open,
    direcție = ÎNAPOI spre direcția ORIGINALĂ a FVG (bullish→long, bearish→short; pariu pe golul respectat
    ca suport/rezistență). Spike = distanța de la intrare la CE-50. Orizont GRUPA A (20). Reutilizează
    `imbalance_mechanics` verbatim (MK-03); consumarea e deja implementată în `detect_fvg_reactions`."""
    n = len(close)
    fvgs = detect_fvgs(high, low, blocks)
    reactions = detect_fvg_reactions(high, low, close, fvgs, blocks)
    ce_by: dict[tuple[int, int], float] = {(f.formed_idx, f.block_index): f.ce_50 for f in fvgs}
    out: list[StrategySignal] = []
    for r in reactions:
        if r.ce50_touch_idx is None:                          # doar FVG-uri efectiv atinse la CE-50 (D7)
            continue
        ce = ce_by.get((r.formed_idx, r.block_index))
        if ce is None:
            continue
        t = r.ce50_touch_idx
        entry = t + 1
        if entry >= n:
            continue
        direction = +1 if r.kind is FVGKind.BULLISH else -1
        spike_price = open_[entry] - ce
        sig = _emit("S13", t, entry, direction, spike_price, horizon, n)
        if sig is not None:
            out.append(sig)
    return out
