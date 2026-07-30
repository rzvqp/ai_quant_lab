"""Cele 10 tipuri de zone — măsurătoarea în TREI BRAȚE (Statistician v2.7.27, d7a785f, doc 0d52475). READ-ONLY.

In-sample, M15_v2. FĂRĂ P&L, FĂRĂ rulări, GARD 1 neatins (măsurători). GARD 2 neatins, sigilat intact.
Aceeași metodologie ca măsurătoarea validată (`obdz_three_arm_windows.py`) — DOAR sursa populației braț-A se
schimbă per tip. OB și Demand/Supply deja măsurate (OBDZ, v2.7.21), NU se repetă.

DECLANȘATOR BRAȚ-A (decision_1, v2.7.27): PRIMA ATINGERE aliniată la bias a zonei, per convenția de
atingere/consumare deja înghețată a fiecărui tip — NU formarea. Dacă PRIMA atingere NU e aliniată la bias →
tipul NU produce declanșator (fără căutarea unei atingeri ulterioare). entry=atingere+1, direcție=polaritatea
zonei (BPR: direcția = bias-ul, zona n-are polaritate), atr=ATR14[atingere], entry_price=open[atingere+1].

CONVENȚII DE ATINGERE (înghețate, per tip):
  Breaker (track_breaker)          span-overlap corp după breaker_idx; polaritate = kind inversat.
  FVG (detect_fvgs)                span-overlap gap [lower,upper] după confirmed_idx; polaritate = FVG kind.
  CE-50 (detect_fvg_reactions)     nivel ce_50, atingere de FITIL (bull low<=ce / bear high>=ce), în bloc; pol=FVG kind.
  IFVG (detect_inverse_fvgs)       span-overlap [lower,upper] după bara de inversare; polaritate = kind inversat.
  Liquidity Void (detect_liquidity_voids)  zonă=[min(close[c],open[c+1]),max(close[c],open[c+1])],
                                   pol=BULLISH dacă open[c+1]>close[c] altfel BEARISH, formare=c (decision_2).
                                   span-overlap după bara de salt (c+2).
  BPR (perechi FVG bull×bear)      zonă=[max(a.lower,b.lower),min(a.upper,b.upper)], formare=max(formed);
                                   toleranță 0,0 strict, escaladare 0,10→0,25 DOAR dacă populația < 25 (decision_2).
                                   FĂRĂ polaritate de zonă → direcția = bias-ul la atingere.
  PDH/PDL (compute_prior_day_levels + detect_level_touches)  nivel; PDH high>=price (short), PDL low<=price (long).
  PWH/PWL (compute_prior_week_levels)  IDENTIC cu atingerea zilnică înghețată, dar fereastra = săptămâna curentă
                                   (fereastra explicit „alta" din docstring-ul detect_level_touches, oglindită zi→săpt).
                                   ⚠ DISCLOSURE: testul de atingere e verbatim cel înghețat; DOAR fereastra e lărgită.
  Mitigation Block (detect_mitigations)  prima Mitigation (ReactionEvent visit 1) a fiecărui OB; pol=OB kind.
  Rejection Block (detect_rejections)    prima Rejecție (visit 1) a fiecărui OB; pol=OB kind.

FERESTRE (end-offset de la entry, = cele 4 non-ref ale măsurătorii validate): [entry+1,entry+2] (=[t+2,t+3]),
[entry+1,entry+4] (=[t+2,t+5]), [entry+1,entry+9] (=[t+2,t+10]), [entry+1,entry+19] (=[t+2,t+20]). Fără ref92.
BRAȚE A/B/C + potrivire pe pullback_depth (Swing/StructureLabel) — verbatim din măsurătoarea validată. Semințe
per tip pt. independență (SEED+regim+31×tip / +1000+31×tip). NU interpretez, livrez cifrele.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Callable

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM  # type: ignore[import-not-found]
from market_structure import Block, StructureLabel, SwingKind, detect_swings, label_structure
from imbalance_mechanics import FVGKind, detect_fvgs, detect_fvg_reactions, detect_inverse_fvgs
from institutional_levels import (LevelKind, compute_prior_day_levels, compute_prior_week_levels,
                                  derive_week_index)
from order_block_void import OrderBlockKind, detect_liquidity_voids
from order_flow import detect_mitigations, detect_order_blocks, detect_rejections, track_breaker

SEED = 20260729
WINDOWS = {"w_t2_t3": 2, "w_t2_t5": 4, "w_t2_t10": 9, "w_t2_t20": 19}   # end-offset de la entry (fără ref92)
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}
Event = tuple[int, int, float, float]     # (entry_idx, direction, atr, entry_price)
Zone = tuple[int, float, float, int]      # (scan_start, zone_lower, zone_upper, polarity: +1/-1/0=BPR-none)


def _htf_trend(dfh: Any, period: int) -> Any:
    ema20 = dfh["close"].ewm(span=20).mean(); ema50 = dfh["close"].ewm(span=50).mean()
    tu = (ema20 > ema50).astype(float)
    avail = dfh["time"].shift(-1); avail.iloc[-1] = int(dfh["time"].iloc[-1]) + period
    return pd.DataFrame({"avail": avail.astype("int64"), "trend_up": tu.to_numpy()})


def _day_index(time: Any) -> np.ndarray:
    dt = pd.to_datetime(time, unit="s", utc=True)
    ny = dt.dt.tz_convert("America/New_York").dt.tz_localize(None)
    d = (ny - pd.Timedelta(hours=17)).dt.floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(d, dtype=np.int64)


def _dist(a: np.ndarray) -> dict[str, Any]:
    a = a[np.isfinite(a)]
    if not len(a):
        return {}
    return dict(n=int(len(a)), min=round(float(a.min()), 2), p10=round(float(np.percentile(a, 10)), 2),
                p25=round(float(np.percentile(a, 25)), 2), median=round(float(np.percentile(a, 50)), 2),
                p75=round(float(np.percentile(a, 75)), 2), p90=round(float(np.percentile(a, 90)), 2),
                max=round(float(a.max()), 2))


def _win(ev: Event, hi: np.ndarray, lo: np.ndarray, n: int, end_off: int) -> tuple[float, float, int] | None:
    entry, d, atr, ep = ev
    s = entry + 1
    e = min(entry + end_off, n - 1)
    if s > e or atr <= 0:
        return None
    hh = hi[s:e + 1]; ll = lo[s:e + 1]
    if d > 0:
        mae = ep - float(np.min(ll)); mfe = float(np.max(hh)) - ep
        bmae = int(np.argmin(ll)); bmfe = int(np.argmax(hh))
    else:
        mae = float(np.max(hh)) - ep; mfe = ep - float(np.min(ll))
        bmae = int(np.argmax(hh)); bmfe = int(np.argmin(ll))
    return max(0.0, mae) / atr, max(0.0, mfe) / atr, (0 if bmae < bmfe else 1 if bmae > bmfe else 2)


def _measure_pool(events: list[Event], hi: np.ndarray, lo: np.ndarray, n: int,
                  acc: dict[str, dict[str, list[float]]]) -> None:
    for wn, eo in WINDOWS.items():
        for ev in events:
            r = _win(ev, hi, lo, n, eo)
            if r is None:
                continue
            acc.setdefault(wn, {"MAE": [], "MFE": [], "ratio": [], "adv": []})
            acc[wn]["MAE"].append(r[0]); acc[wn]["MFE"].append(r[1])
            if r[0] > 0:
                acc[wn]["ratio"].append(r[1] / r[0])
            acc[wn]["adv"].append(1.0 if r[2] == 0 else 0.0)


def _summarize(acc: dict[str, dict[str, list[float]]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for wn, d in acc.items():
        out[wn] = dict(n=len(d["MAE"]), MAE=_dist(np.asarray(d["MAE"])), MFE=_dist(np.asarray(d["MFE"])),
                       MFE_over_MAE=_dist(np.asarray(d["ratio"])),
                       frac_adverse_first=round(float(np.mean(d["adv"])), 3) if d["adv"] else None)
    return out


def _pullback_depth_arrays(h: list[float], l: list[float], n: int) -> tuple[np.ndarray, np.ndarray]:
    swings = label_structure(detect_swings(h, l, [Block(0, n)], k=2))
    evs = sorted(((s.confirmed_idx, s.kind, s.price) for s in swings if s.label is not StructureLabel.UNCLASSIFIED),
                 key=lambda x: x[0])
    last_high = np.full(n, np.nan); last_low = np.full(n, np.nan)
    ch = cl = np.nan; si = 0
    for j in range(n):
        while si < len(evs) and evs[si][0] <= j:
            if evs[si][1] is SwingKind.HIGH:
                ch = evs[si][2]
            else:
                cl = evs[si][2]
            si += 1
        last_high[j] = ch; last_low[j] = cl
    return last_high, last_low


def _regime_label(seg: dict[str, Any], i: int) -> str:
    for k in ("regime", "label", "name"):
        v = seg.get(k)
        if isinstance(v, str):
            return v.lower()
    return ["bear", "bull", "correction"][i]


class Ctx:
    """Toate array-urile per regim, ca sursele braț-A să fie doar swap-uri de populație."""
    def __init__(self, o: list[float], h: list[float], l: list[float], c: list[float], tm: list[int],
                 atr: np.ndarray, bias_up: np.ndarray, bias_dn: np.ndarray, day: np.ndarray,
                 week: list[int], n: int) -> None:
        self.o = o; self.h = h; self.l = l; self.c = c; self.tm = tm; self.atr = atr
        self.bias_up = bias_up; self.bias_dn = bias_dn; self.day = day; self.week = week; self.n = n

    def bias(self, j: int) -> int:
        return 1 if self.bias_up[j] else (-1 if self.bias_dn[j] else 0)

    def event_from_touch(self, touch: int, pol: int) -> Event | None:
        """entry=touch+1; direcție = pol (sau bias dacă pol==0=BPR). Filtre: entry valid, atr>0."""
        entry = touch + 1
        if entry >= self.n:
            return None
        b = self.bias(touch)
        if pol != 0 and b != pol:               # atingere nealiniată → fără declanșator (fără căutare ulterioară)
            return None
        if pol == 0 and b == 0:                 # BPR: bias nedefinit la atingere → drop
            return None
        d = pol if pol != 0 else b
        a = float(self.atr[touch])
        if not np.isfinite(a) or a <= 0:
            return None
        return (entry, d, a, float(self.o[entry]))


def _span_events(ctx: Ctx, zones: list[Zone]) -> list[Event]:
    """Pentru fiecare zonă band: PRIMA bară span-overlap după scan_start = prima atingere. Apoi filtru bias."""
    evs: list[Event] = []
    for (start, zl, zh, pol) in zones:
        touch = -1
        for j in range(max(start, 0), ctx.n):
            if ctx.l[j] <= zh and ctx.h[j] >= zl:
                touch = j
                break
        if touch < 0:
            continue
        e = ctx.event_from_touch(touch, pol)
        if e is not None:
            evs.append(e)
    return evs


# ─────────────────────────── surse de populație braț-A, per tip ───────────────────────────
def src_breaker(ctx: Ctx) -> list[Event]:
    obs = detect_order_blocks(ctx.o, ctx.h, ctx.l, ctx.c, ctx.n)
    zones: list[Zone] = []
    for ob in obs:
        br = track_breaker(ob, ctx.h, ctx.l, ctx.c, ctx.n)
        if br is None:
            continue
        pol = 1 if br.kind is OrderBlockKind.BULLISH else -1
        zones.append((br.breaker_idx + 1, br.zone_lower, br.zone_upper, pol))
    return _span_events(ctx, zones)


def src_fvg(ctx: Ctx) -> list[Event]:
    fvgs = detect_fvgs(ctx.h, ctx.l, [Block(0, ctx.n)])
    zones = [(f.confirmed_idx + 1, f.lower, f.upper, 1 if f.kind is FVGKind.BULLISH else -1) for f in fvgs]
    return _span_events(ctx, zones)


def src_ce50(ctx: Ctx) -> list[Event]:
    fvgs = detect_fvgs(ctx.h, ctx.l, [Block(0, ctx.n)])
    evs: list[Event] = []
    for f in fvgs:
        pol = 1 if f.kind is FVGKind.BULLISH else -1
        ce = f.ce_50
        touch = -1
        for j in range(f.confirmed_idx + 1, ctx.n):
            if (pol > 0 and ctx.l[j] <= ce) or (pol < 0 and ctx.h[j] >= ce):
                touch = j
                break
        if touch < 0:
            continue
        e = ctx.event_from_touch(touch, pol)
        if e is not None:
            evs.append(e)
    return evs


def src_ifvg(ctx: Ctx) -> list[Event]:
    fvgs = detect_fvgs(ctx.h, ctx.l, [Block(0, ctx.n)])
    ifvgs = detect_inverse_fvgs(ctx.h, ctx.l, ctx.c, fvgs, [Block(0, ctx.n)])
    zones = [(f.confirmed_idx + 1, f.lower, f.upper, 1 if f.kind is FVGKind.BULLISH else -1) for f in ifvgs]
    return _span_events(ctx, zones)


def src_liquidity_void(ctx: Ctx) -> list[Event]:
    lvs = detect_liquidity_voids(ctx.o, ctx.c, ctx.tm)
    zones: list[Zone] = []
    for v in lvs:
        c = v.at_idx
        if c + 1 >= ctx.n:
            continue
        lower = min(ctx.c[c], ctx.o[c + 1]); upper = max(ctx.c[c], ctx.o[c + 1])
        pol = 1 if ctx.o[c + 1] > ctx.c[c] else -1
        zones.append((c + 2, lower, upper, pol))          # span-overlap după bara de salt
    return _span_events(ctx, zones)


def src_bpr(ctx: Ctx, tol: float) -> list[Event]:
    fvgs = detect_fvgs(ctx.h, ctx.l, [Block(0, ctx.n)])
    bulls = [f for f in fvgs if f.kind is FVGKind.BULLISH]
    bears = [f for f in fvgs if f.kind is FVGKind.BEARISH]
    zones: list[Zone] = []
    for a in bulls:
        for b in bears:
            if abs(a.formed_idx - b.formed_idx) > 3:
                continue
            gap = max(a.lower, b.lower) - min(a.upper, b.upper)   # <=tol → suprapunere
            if gap > tol:
                continue
            lower = max(a.lower, b.lower); upper = min(a.upper, b.upper)
            if lower > upper:                                    # bandă degenerată la toleranță laxă
                lower, upper = upper, lower
            zones.append((max(a.formed_idx, b.formed_idx) + 1, lower, upper, 0))   # pol=0 → direcția din bias
    return _span_events(ctx, zones)


def _level_events(ctx: Ctx, levels: list[Any], per_week: bool) -> list[Event]:
    """Atingere de nivel, consumat o dată în fereastra de disponibilitate (zi sau săptămână). Verbatim testul
    înghețat: PDH/WEEKLY_HIGH → high>=price (short, pol=-1); PDL/WEEKLY_LOW → low<=price (long, pol=+1)."""
    label = np.asarray(ctx.week) if per_week else ctx.day
    evs: list[Event] = []
    for lv in levels:
        is_high = lv.kind in (LevelKind.PDH, LevelKind.WEEKLY_HIGH)
        pol = -1 if is_high else 1
        start = lv.available_idx
        win = label[start]
        touch = -1
        for j in range(start, ctx.n):
            if label[j] != win:
                break
            if (is_high and ctx.h[j] >= lv.price) or ((not is_high) and ctx.l[j] <= lv.price):
                touch = j
                break
        if touch < 0:
            continue
        e = ctx.event_from_touch(touch, pol)
        if e is not None:
            evs.append(e)
    return evs


def src_pdh_pdl(ctx: Ctx) -> list[Event]:
    levels = compute_prior_day_levels(ctx.h, ctx.l, ctx.day.tolist(), [Block(0, ctx.n)])
    return _level_events(ctx, list(levels), per_week=False)


def src_pwh_pwl(ctx: Ctx) -> list[Event]:
    levels = compute_prior_week_levels(ctx.h, ctx.l, ctx.day.tolist(), ctx.week, [Block(0, ctx.n)])
    return _level_events(ctx, list(levels), per_week=True)


def _ob_reaction_events(ctx: Ctx, detector: Callable[..., list[Any]]) -> list[Event]:
    """Prima reacție (visit 1) a fiecărui OB = prima atingere; polaritate = OB kind."""
    obs = detect_order_blocks(ctx.o, ctx.h, ctx.l, ctx.c, ctx.n)
    evs: list[Event] = []
    for ob in obs:
        events = detector(ob, ctx.h, ctx.l, ctx.c, ctx.n)
        if not events:
            continue
        pol = 1 if ob.kind is OrderBlockKind.BULLISH else -1
        e = ctx.event_from_touch(events[0].event_idx, pol)       # prima atingere; drop dacă nealiniată
        if e is not None:
            evs.append(e)
    return evs


def src_mitigation_block(ctx: Ctx) -> list[Event]:
    return _ob_reaction_events(ctx, detect_mitigations)


def src_rejection_block(ctx: Ctx) -> list[Event]:
    return _ob_reaction_events(ctx, detect_rejections)


SOURCES: list[tuple[str, str, Callable[[Ctx], list[Event]]]] = [
    ("wave1", "Breaker", src_breaker), ("wave1", "FVG", src_fvg), ("wave1", "CE-50", src_ce50),
    ("wave1", "IFVG", src_ifvg), ("wave1", "Liquidity_Void", src_liquidity_void),
    ("wave1", "BPR", lambda c: src_bpr(c, 0.0)),           # placeholder; escaladarea de toleranță se face în main
    ("wave2", "PDH_PDL", src_pdh_pdl), ("wave2", "PWH_PWL", src_pwh_pwl),
    ("wave3", "Mitigation_Block", src_mitigation_block), ("wave3", "Rejection_Block", src_rejection_block),
]


def _build_bc(ctx: Ctx, last_high: np.ndarray, last_low: np.ndarray, A_full: list[Event],
              ti: int, ri: int) -> tuple[list[Event], list[Event], list[Event], dict[str, int]]:
    """Brațele B (bias-aleatoriu) și C (bias+pullback non-zonă, potrivit pe pullback_depth) — verbatim validat."""
    cl = np.asarray(ctx.c); op = np.asarray(ctx.o); atr = ctx.atr; n = ctx.n
    bias_up = ctx.bias_up; bias_dn = ctx.bias_dn
    aligned = bias_up | bias_dn

    def pdepth(j: int, bull: bool) -> float:
        if atr[j] <= 0:
            return float("nan")
        return float((last_high[j] - cl[j]) / atr[j] if bull else (cl[j] - last_low[j]) / atr[j])

    zone_t = {e[0] - 1 for e in A_full}                    # atingere = entry-1
    A_subset: list[Event] = []; pd_A: list[float] = []; undefined = 0
    for e in A_full:
        touch = e[0] - 1
        pdv = pdepth(touch, e[1] > 0)
        if not np.isfinite(pdv):
            undefined += 1
            continue
        A_subset.append(e); pd_A.append(pdv)

    pool_all = np.array([j for j in range(n - 1) if aligned[j] and np.isfinite(atr[j]) and atr[j] > 0], dtype=int)
    B: list[Event] = []
    if len(pool_all):
        rng = np.random.default_rng(SEED + ri + 31 * ti)
        bpick = rng.choice(pool_all, size=min(len(A_full), len(pool_all)), replace=False)
        B = [(int(j) + 1, 1 if bias_up[j] else -1, float(atr[j]), float(op[j + 1])) for j in bpick]

    cpool = np.array([j for j in pool_all if j not in zone_t and np.isfinite(pdepth(j, bool(bias_up[j])))], dtype=int)
    C: list[Event] = []; matched = 0; unmatched = 0
    if len(cpool):
        cpd = np.array([pdepth(int(j), bool(bias_up[j])) for j in cpool])
        order = np.argsort(cpd); spd = cpd[order]; sidx = cpool[order]
        used = np.zeros(len(cpool), dtype=bool)
        rngC = np.random.default_rng(SEED + ri + 1000 + 31 * ti)
        for (ev, pda) in zip(A_subset, pd_A):
            tol0 = max(0.25 * abs(pda), 0.5); cap = max(abs(pda), 2.0); tol = tol0; picked = -1
            while True:
                a = int(np.searchsorted(spd, pda - tol, "left")); b = int(np.searchsorted(spd, pda + tol, "right"))
                avail = [p for p in range(a, b) if not used[p]]
                if avail:
                    p = int(rngC.choice(avail)); used[p] = True; picked = int(sidx[p]); break
                if tol >= cap:
                    break
                tol = min(tol * 2, cap)
            if picked < 0:
                unmatched += 1
            else:
                matched += 1
                C.append((picked + 1, 1 if bias_up[picked] else -1, float(atr[picked]), float(op[picked + 1])))
    else:
        unmatched = len(A_subset)
    match = dict(A_full=len(A_full), A_subset=len(A_subset), pullback_undefined=undefined,
                 C_matched=matched, C_unmatched=unmatched, B=len(B))
    return A_subset, B, C, match


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)} | seed={SEED} | ferestre={list(WINDOWS.values())}")
    if len(dfm) != 130_491:
        print(f"STOP: M15 {len(dfm)}."); return 2
    dfm = dfm.sort_values("time").reset_index(drop=True)
    for name, dfh, per in (("h1", dfh1, 3600), ("h4", dfh4, 4 * 3600)):
        htf = _htf_trend(dfh, per).sort_values("avail")
        dfm = pd.merge_asof(dfm, htf.rename(columns={"trend_up": name}), left_on="time", right_on="avail",
                            direction="backward").drop(columns="avail")
    dfm["day"] = _day_index(dfm["time"])
    t_all = dfm["time"].to_numpy()
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]

    names = [nm for (_w, nm, _f) in SOURCES]
    agg: dict[str, dict[str, dict[str, dict[str, list[float]]]]] = {
        nm: {a: {} for a in ("A_full", "A_subset", "B", "C")} for nm in names}
    out: dict[str, Any] = {"windows": WINDOWS, "seed": SEED, "trigger": "first bias-aligned touch",
                           "per_regime": {}, "match": {}, "bpr_tolerance": {}}

    for ri, seg in enumerate(segs):
        label = _regime_label(seg, ri)
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(label) not in (None, len(sub)):
            print(f"STOP: {label} {len(sub)} bare."); return 3
        n = len(sub)
        o = sub["open"].tolist(); h = sub["high"].tolist(); l = sub["low"].tolist(); c = sub["close"].tolist()
        tm = [int(x) for x in sub["time"].tolist()]
        atr = sub["atr14"].to_numpy(); h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy(); day = sub["day"].to_numpy()
        week = derive_week_index(day.tolist())
        bias_up = (h1 > 0.5) & (h4 > 0.5)
        bias_dn = (h1 <= 0.5) & (h4 <= 0.5) & np.isfinite(h1) & np.isfinite(h4)
        ctx = Ctx(o, h, l, c, tm, atr, bias_up, bias_dn, day, week, n)
        last_high, last_low = _pullback_depth_arrays(h, l, n)
        hi = np.asarray(h); lo = np.asarray(l)

        out["per_regime"][label] = {}; out["match"][label] = {}; out["bpr_tolerance"][label] = {}
        print(f"\n############ {label.upper()} ({n} bare) ############")
        for ti, (wave, nm, fn) in enumerate(SOURCES):
            if nm == "BPR":                                   # escaladare de toleranță 0,0→0,10→0,25 dacă <25
                A_full: list[Event] = []
                used_tol = 0.0
                for tol in (0.0, 0.10, 0.25):
                    A_full = src_bpr(ctx, tol); used_tol = tol
                    if len(A_full) >= 25:
                        break
                out["bpr_tolerance"][label] = used_tol
            else:
                A_full = fn(ctx)
            A_subset, B, C, match = _build_bc(ctx, last_high, last_low, A_full, ti, ri)
            reg: dict[str, Any] = {}
            for aname, evlist in (("A_full", A_full), ("A_subset", A_subset), ("B", B), ("C", C)):
                acc: dict[str, dict[str, list[float]]] = {}
                _measure_pool(evlist, hi, lo, n, acc)
                reg[aname] = _summarize(acc)
                _measure_pool(evlist, hi, lo, n, agg[nm][aname])
            out["per_regime"][label][nm] = reg
            out["match"][label][nm] = match
            pw = "w_t2_t5"
            wa = reg["A_full"].get(pw, {}); wb = reg["B"].get(pw, {}); wc = reg["C"].get(pw, {})
            tolstr = f" tol={out['bpr_tolerance'][label]}" if nm == "BPR" else ""
            print(f"  [{wave}] {nm:16s} A={match['A_full']:4d} (sub={match['A_subset']:4d} "
                  f"C:{match['C_matched']}✓/{match['C_unmatched']}✗ B={match['B']}){tolstr}")
            print(f"       [t+2,t+5] MFE_med  A={wa.get('MFE',{}).get('median')}  "
                  f"B={wb.get('MFE',{}).get('median')}  C={wc.get('MFE',{}).get('median')}   "
                  f"MFE/MAE_med A={wa.get('MFE_over_MAE',{}).get('median')} adv1st A={wa.get('frac_adverse_first')}")

    out["aggregate"] = {nm: {a: _summarize(agg[nm][a]) for a in ("A_full", "A_subset", "B", "C")} for nm in names}
    print("\n############ AGREGAT — [t+2,t+5] MFE median (A vs B vs C) ############")
    for (_w, nm, _f) in SOURCES:
        a = out["aggregate"][nm]
        wa = a["A_full"].get("w_t2_t5", {}); wb = a["B"].get("w_t2_t5", {}); wc = a["C"].get("w_t2_t5", {})
        print(f"  {nm:16s} A={wa.get('MFE',{}).get('median')} (n={wa.get('n')})  "
              f"B={wb.get('MFE',{}).get('median')}  C={wc.get('MFE',{}).get('median')}")
    path = os.path.join(_ROOT, "reports", "zone_survey_three_arm_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/zone_survey_three_arm_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
