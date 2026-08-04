"""FAZA 1 — screening rapid (triaj DESCRIPTIV) al politicilor cu Part B completă, prin motorul DEMO gardat.

O singură întrebare: există vreun indiciu de edge? NU verdict, NU p-value, NU corecție de testare multiplă, NU
optimizare, NU ajustare de parametri. Screening-ul NU consumă familia (ca fișele medicale). Nicio cifră nu e
dovadă de edge — doar triaj. Backtest STANDARDIZAT, IDENTIC pentru toți: descoperirea M15_v2 (130.491 bare),
contractul de execuție înghețat al fiecărei politici, motorul `demo_gate_engine` cu gardurile S1/S2/S3.

⚠ Costuri MODELATE (backtest): `effective_spread`/`cost`/`tick_size` sunt constantele frozen ale laboratorului
(spread 0,10; cost round-trip 0,20; tick 0,01) — pe backtest nu există spread REAL observat (acela e cerința S2
la DEMO live). Identice pentru toți candidații. Termenul 0,10×ATR domină podeaua pt. XAUUSD.

Stabilitate anuală: descoperirea are OPT ani DISCONTINUI (2011-2013, 2016-2018, 2020-2021); 2014/2015/2019
sunt în jumătatea sigilată. Maxim 8 puncte, cu goluri — NU extrapolez, NU netezesc. Sub n=25/an → suprimat (doar n).

GARD 1 ridicat EXCLUSIV pentru rulări, coborât după (rularea reală se face din afară, cu flagul comutat). GARD 2
neatins. NU comit rezultate JSON.
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
_ENGINE = os.path.join(os.path.dirname(_ROOT), "ai_quant_lab-alpha-automation", "demo_gate_engine")
for _p in (_HERE, _ROOT, os.path.join(_ROOT, "edge_research"), _ENGINE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from edge_research._common import PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC, load
import split_manifest as SM  # type: ignore[import-not-found]
from market_structure import Block
from market_state import ATR_WINDOW, compression, expansion
from institutional_levels import (LevelKind, compute_prior_day_levels, compute_prior_week_levels,
                                  derive_week_index, detect_level_touches)
from imbalance_mechanics import FVGKind, detect_fvgs, detect_fvg_reactions
from order_block_void import OrderBlockKind, detect_liquidity_voids
from order_flow import detect_demand_zones, detect_mitigations, detect_order_blocks, detect_rejections
from market_structure import BreakKind, SwingKind, detect_breaks, detect_swings, label_structure
from liquidity_mechanics import LiquidityPool, PoolSide, PoolTier, build_pools, detect_sweeps
from session_levels import (SessionLevel, SessionLevelKind, compute_persistent_session_levels,
                            compute_prior_session_levels, derive_session_index,
                            detect_session_level_touches, detect_session_mid_touches, session_labels)
from pdh_pdl_demo_engine import DemoSignal, DemoTradeResult, ExitReason, simulate_demo_trades
from dynamic_exit_engine import simulate_demo_trades_dynamic

EFF_SPREAD, COST, TICK_SIZE = 0.10, 0.20, 0.01     # constante frozen, MODELATE pt. backtest, IDENTICE pt. toți
N_MIN = 25
REGIMES = ["bear", "bull", "correction"]
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}
GateFn = Callable[["RegimeData"], list[DemoSignal]]
RunFn = Callable[["RegimeData"], tuple[list[DemoSignal], list[DemoTradeResult]]]


def _day_index(time: Any) -> np.ndarray:
    dt = pd.to_datetime(time, unit="s", utc=True)
    ny = dt.dt.tz_convert("America/New_York").dt.tz_localize(None)
    d = (ny - pd.Timedelta(hours=17)).dt.floor("D").values.astype("datetime64[D]").astype("int64")
    return np.asarray(d, dtype=np.int64)


def _eod_per_bar(day: np.ndarray, n: int) -> np.ndarray:
    eod = np.empty(n, dtype=np.int64); last = n - 1
    for j in range(n - 1, -1, -1):
        if j < n - 1 and day[j] != day[j + 1]:
            last = j
        eod[j] = last
    return eod


class RegimeData:
    """Barele + derivatele unui regim (bloc unic), sursă comună pt. generatoarele de semnal."""
    def __init__(self, label: str, o: list[float], h: list[float], l: list[float], c: list[float],
                 tm: list[int], atr: np.ndarray, day: np.ndarray, eod: np.ndarray, year: np.ndarray, n: int,
                 session_index: list[int], session_label: list[str], session_eod: np.ndarray,
                 bias_up: np.ndarray, bias_dn: np.ndarray) -> None:
        self.label = label; self.o = o; self.h = h; self.l = l; self.c = c; self.tm = tm
        self.atr = atr; self.day = day; self.eod = eod; self.year = year; self.n = n
        self.session_index = session_index; self.session_label = session_label; self.session_eod = session_eod
        self.bias_up = bias_up; self.bias_dn = bias_dn
        self.horizon_override: int | None = None     # v3: dacă e setat, time-stop = min(entry+H, n-1)

    def sig(self, entry_idx: int, direction: int, stop_price: float, target_price: float,
            block_horizon: bool = False, horizon_bars: int | None = None,
            day_end_override: int | None = None) -> DemoSignal | None:
        """time-stop: `horizon_override` (v3) > `day_end_override` (explicit, ex. graniță de sesiune) >
        `horizon_bars` (fix) > block (n-1) > zi (`eod`)."""
        if entry_idx >= self.n:
            return None
        a = float(self.atr[entry_idx - 1]) if entry_idx - 1 >= 0 else float("nan")
        if not np.isfinite(a) or a <= 0:
            return None
        if self.horizon_override is not None:
            dend = min(entry_idx + self.horizon_override, self.n - 1)
        elif day_end_override is not None:
            dend = min(max(day_end_override, entry_idx), self.n - 1)
        elif horizon_bars is not None:
            dend = min(entry_idx + horizon_bars, self.n - 1)
        elif block_horizon:
            dend = self.n - 1
        else:
            dend = int(self.eod[entry_idx])
        return DemoSignal(entry_idx=entry_idx, direction=direction, strategy_stop_price=stop_price,
                          target_price=target_price, atr=a, effective_spread=EFF_SPREAD, cost=COST,
                          day_end_idx=dend)


# ───────────────────────────── generatoare de semnal (contract frozen per politică) ─────────────────────────────
def gen_cand0001_pdh_pdl(rd: RegimeData) -> list[DemoSignal]:
    """PDH→short (stop=high[touch], target=PDL); PDL→long (stop=low[touch], target=PDH). entry=touch+1."""
    blk = [Block(0, rd.n)]
    levels = compute_prior_day_levels(rd.h, rd.l, rd.day.tolist(), blk)
    opp: dict[int, dict[str, float]] = {}
    for lv in levels:
        opp.setdefault(lv.source_period_start, {})[
            "PDH" if lv.kind is LevelKind.PDH else "PDL"] = lv.price
    out: list[DemoSignal] = []
    for t in detect_level_touches(rd.h, rd.l, levels, rd.day.tolist(), blk):
        lv = t.level
        pair = opp.get(lv.source_period_start, {})
        if lv.kind is LevelKind.PDH:
            d = -1; stop = rd.h[t.touch_idx]; tgt = pair.get("PDL")
        else:
            d = 1; stop = rd.l[t.touch_idx]; tgt = pair.get("PDH")
        if tgt is None:
            continue
        s = rd.sig(t.touch_idx + 1, d, stop, float(tgt))
        if s is not None:
            out.append(s)
    return out


def gen_cand0003_fvg_ce50(rd: RegimeData) -> list[DemoSignal]:
    """FVG CE-50 reaction: entry la ce50_touch+1; long pt FVG bullish (stop=lower far edge, target=upper near
    edge), short pt bearish (stop=upper, target=lower). Nivelurile FVG sunt cele frozen (`detect_fvgs`)."""
    blk = [Block(0, rd.n)]
    fvgs = detect_fvgs(rd.h, rd.l, blk)
    reactions = detect_fvg_reactions(rd.h, rd.l, rd.c, fvgs, blk)
    by_formed = {f.formed_idx: f for f in fvgs}
    out: list[DemoSignal] = []
    for r in reactions:
        if r.ce50_touch_idx is None:
            continue
        f = by_formed.get(r.formed_idx)
        if f is None:
            continue
        if f.kind is FVGKind.BULLISH:
            d = 1; stop = f.lower; tgt = f.upper          # far edge = lower (Q4 inversion boundary), near edge = upper
        else:
            d = -1; stop = f.upper; tgt = f.lower
        s = rd.sig(r.ce50_touch_idx + 1, d, float(stop), float(tgt), block_horizon=True)   # time-stop = granița de BLOC
        if s is not None:
            out.append(s)
    return out


def gen_cand0007_level_fvg_confluence(rd: RegimeData) -> list[DemoSignal]:
    """Confluență SAME-BAR (contract frozen): bara e ATÂT atingere de nivel CÂT ȘI atingere CE-50 a unui FVG de
    polaritate aliniată (touch_idx == ce50_touch_idx). PDL×FVG bullish → long; PDH×FVG bearish → short. Stop =
    sub AMBELE structuri = min(low[touch],FVG.lower) (long) / max(high[touch],FVG.upper) (short); target = nivelul
    opus al zilei; entry=touch+1; time-stop de ZI. (Reutilizează exit-ul CAND-0001, zona ⊂ CAND-0003.)"""
    blk = [Block(0, rd.n)]
    levels = compute_prior_day_levels(rd.h, rd.l, rd.day.tolist(), blk)
    opp: dict[int, dict[str, float]] = {}
    for lv in levels:
        opp.setdefault(lv.source_period_start, {})["PDH" if lv.kind is LevelKind.PDH else "PDL"] = lv.price
    fvgs = detect_fvgs(rd.h, rd.l, blk)
    by_formed = {f.formed_idx: f for f in fvgs}
    # mapă: bara de atingere CE-50 → FVG-ul reacționat, per polaritate
    ce50: dict[int, dict[FVGKind, Any]] = {}
    for r in detect_fvg_reactions(rd.h, rd.l, rd.c, fvgs, blk):
        if r.ce50_touch_idx is None:
            continue
        f = by_formed.get(r.formed_idx)
        if f is not None:
            ce50.setdefault(r.ce50_touch_idx, {}).setdefault(f.kind, f)
    out: list[DemoSignal] = []
    for t in detect_level_touches(rd.h, rd.l, levels, rd.day.tolist(), blk):
        lv = t.level
        want_long = lv.kind is LevelKind.PDL                        # PDL→long, PDH→short
        want_kind = FVGKind.BULLISH if want_long else FVGKind.BEARISH
        conf = ce50.get(t.touch_idx, {}).get(want_kind)             # CE-50 touch pe ACEEAȘI bară, polaritate aliniată
        if conf is None:
            continue
        pair = opp.get(lv.source_period_start, {})
        if want_long:
            d = 1; stop = min(rd.l[t.touch_idx], conf.lower); tgt = pair.get("PDH")
        else:
            d = -1; stop = max(rd.h[t.touch_idx], conf.upper); tgt = pair.get("PDL")
        if tgt is None:
            continue
        s = rd.sig(t.touch_idx + 1, d, float(stop), float(tgt))
        if s is not None:
            out.append(s)
    return out


def gen_cand0002_compression_expansion(rd: RegimeData, exp: list[bool]) -> list[DemoSignal]:
    """Declanșator = prima bară de expansiune imediat după o bară comprimată (`expansion[i] ∧ is_compressed[i-1]`).
    direcție = sign(close[i]-open[i]); entry=i+1; stop = extrema opusă a barei de expansiune (low[i] long /
    high[i] short); target IGNORAT (exit dinamic); time-stop = granița de BLOC."""
    is_comp, is_valid = compression(rd.h, rd.l)                # trailing-460 P10 Parkinson, block-local
    out: list[DemoSignal] = []
    for i in range(1, rd.n - 1):
        if not exp[i] or not (is_valid[i - 1] and is_comp[i - 1]):
            continue
        d = 1 if rd.c[i] > rd.o[i] else -1
        stop = rd.l[i] if d > 0 else rd.h[i]
        s = rd.sig(i + 1, d, float(stop), float("nan"), block_horizon=True)
        if s is not None:
            out.append(s)
    return out


# ── helpers partajate ──
def _opp_level_map(levels: list[Any]) -> dict[int, dict[str, float]]:
    opp: dict[int, dict[str, float]] = {}
    for lv in levels:
        opp.setdefault(lv.source_period_start, {})["PDH" if lv.kind is LevelKind.PDH else "PDL"] = lv.price
    return opp


def _obs_with_events(rd: RegimeData, kind: str, visit1_only: bool) -> list[tuple[Any, Any]]:
    """(OB, ReactionEvent) pentru mitigare/rejecție; `kind`='mitigation'/'rejection'."""
    blk = rd.n
    det = detect_mitigations if kind == "mitigation" else detect_rejections
    out: list[tuple[Any, Any]] = []
    for ob in detect_order_blocks(rd.o, rd.h, rd.l, rd.c, blk):
        for ev in det(ob, rd.h, rd.l, rd.c, blk):
            if visit1_only and ev.visit_number != 1:
                continue
            out.append((ob, ev))
    return out


# ── val 2: CAND-0008/0009 (exit dinamic) ──
def gen_cand0008_void_displacement(rd: RegimeData, exp: list[bool]) -> list[DemoSignal]:
    """Void (at_idx=c) → bara i=c+1 e expansiune. dir=sign(close[i]-open[i]); stop=extrema opusă a barei i;
    exit dinamic; horizon de BLOC."""
    out: list[DemoSignal] = []
    for v in detect_liquidity_voids(rd.o, rd.c, rd.tm):
        i = v.at_idx + 1
        if i >= rd.n or not exp[i]:
            continue
        d = 1 if rd.c[i] > rd.o[i] else -1
        stop = rd.l[i] if d > 0 else rd.h[i]
        s = rd.sig(i + 1, d, float(stop), float("nan"), block_horizon=True)
        if s is not None:
            out.append(s)
    return out


def gen_cand0009_level_break_drive(rd: RegimeData, exp: list[bool], block: bool = False,
                                   horizon: int = ATR_WINDOW) -> list[DemoSignal]:
    """Atingere de nivel + expansiune PE ACEEAȘI bară, în direcția RUPERII prin nivel: PDH+bull→long (break-up),
    PDL+bear→short. stop=nivelul rupt (level.price); exit dinamic. (Opus CAND-0001.)
    v3 (default): time-stop = `ATR_WINDOW`=14 bare (live-valid). `block=True` → vechiul horizon de BLOC (v2,
    discovery-only, NU există live) — păstrat DOAR pentru comparația vechi-vs-nou din re-screening."""
    blk = [Block(0, rd.n)]
    levels = compute_prior_day_levels(rd.h, rd.l, rd.day.tolist(), blk)
    out: list[DemoSignal] = []
    for t in detect_level_touches(rd.h, rd.l, levels, rd.day.tolist(), blk):
        ti = t.touch_idx
        if not exp[ti]:
            continue
        up = rd.c[ti] > rd.o[ti]
        if t.level.kind is LevelKind.PDH and up:
            d = 1
        elif t.level.kind is LevelKind.PDL and not up:
            d = -1
        else:
            continue
        if block:
            s = rd.sig(ti + 1, d, float(t.level.price), float("nan"), block_horizon=True)
        else:
            s = rd.sig(ti + 1, d, float(t.level.price), float("nan"), horizon_bars=horizon)
        if s is not None:
            out.append(s)
    return out


# ── val 3: fixed-target ──
def gen_cand0010_fvg_stack_density(rd: RegimeData) -> list[DemoSignal]:
    """FVG CE-50 reaction al cărei ce_50 se află într-un ALT FVG confirmat de aceeași polaritate (stack).
    stop=far edge; target=near edge; horizon de BLOC."""
    blk = [Block(0, rd.n)]
    fvgs = detect_fvgs(rd.h, rd.l, blk)
    by_formed = {f.formed_idx: f for f in fvgs}
    out: list[DemoSignal] = []
    for r in detect_fvg_reactions(rd.h, rd.l, rd.c, fvgs, blk):
        if r.ce50_touch_idx is None:
            continue
        f = by_formed.get(r.formed_idx)
        if f is None:
            continue
        ce = f.ce_50
        stacked = any(g is not f and g.kind is f.kind and g.confirmed_idx <= r.ce50_touch_idx
                      and g.lower <= ce <= g.upper for g in fvgs)
        if not stacked:
            continue
        if f.kind is FVGKind.BULLISH:
            d = 1; stop = f.lower; tgt = f.upper
        else:
            d = -1; stop = f.upper; tgt = f.lower
        s = rd.sig(r.ce50_touch_idx + 1, d, float(stop), float(tgt), block_horizon=True)
        if s is not None:
            out.append(s)
    return out


def gen_cand0011_ob_rejection(rd: RegimeData) -> list[DemoSignal]:
    """OB + rejecție (D6). stop=low/high[formation_idx] (RAW); target=OB body far edge; horizon de BLOC."""
    out: list[DemoSignal] = []
    for ob, ev in _obs_with_events(rd, "rejection", visit1_only=False):
        if ob.kind is OrderBlockKind.BULLISH:
            d = 1; stop = rd.l[ob.formation_idx]; tgt = ob.zone_upper
        else:
            d = -1; stop = rd.h[ob.formation_idx]; tgt = ob.zone_lower
        s = rd.sig(ev.event_idx + 1, d, float(stop), float(tgt), block_horizon=True)
        if s is not None:
            out.append(s)
    return out


def gen_cand0014_ob_mitigation(rd: RegimeData) -> list[DemoSignal]:
    """OB + prima mitigare (visit 1). stop=low/high[formation_idx] (RAW); target=OB body far edge; horizon de BLOC."""
    out: list[DemoSignal] = []
    for ob, ev in _obs_with_events(rd, "mitigation", visit1_only=True):
        if ob.kind is OrderBlockKind.BULLISH:
            d = 1; stop = rd.l[ob.formation_idx]; tgt = ob.zone_upper
        else:
            d = -1; stop = rd.h[ob.formation_idx]; tgt = ob.zone_lower
        s = rd.sig(ev.event_idx + 1, d, float(stop), float(tgt), block_horizon=True)
        if s is not None:
            out.append(s)
    return out


def gen_cand0013_demand_zone_reentry(rd: RegimeData) -> list[DemoSignal]:
    """Prima re-intrare (j>formation_idx) în DemandZone. stop=far edge; target=near edge; horizon de BLOC."""
    out: list[DemoSignal] = []
    for z in detect_demand_zones(rd.o, rd.h, rd.l, rd.c, rd.n):
        j = -1
        for k in range(z.formation_idx + 1, rd.n):
            if rd.l[k] <= z.zone_upper and rd.h[k] >= z.zone_lower:
                j = k; break
        if j < 0:
            continue
        if z.kind is OrderBlockKind.BULLISH:
            d = 1; stop = z.zone_lower; tgt = z.zone_upper
        else:
            d = -1; stop = z.zone_upper; tgt = z.zone_lower
        s = rd.sig(j + 1, d, float(stop), float(tgt), block_horizon=True)
        if s is not None:
            out.append(s)
    return out


def gen_cand0018_obrej_void_confluence(rd: RegimeData) -> list[DemoSignal]:
    """Rejecție a cărei bară (event_idx=i) urmează unui void (at_idx==i-1, proximitate). stop=raw OB floor;
    target=OB body far edge; horizon de BLOC."""
    void_at = {v.at_idx for v in detect_liquidity_voids(rd.o, rd.c, rd.tm)}
    out: list[DemoSignal] = []
    for ob, ev in _obs_with_events(rd, "rejection", visit1_only=False):
        if (ev.event_idx - 1) not in void_at:
            continue
        if ob.kind is OrderBlockKind.BULLISH:
            d = 1; stop = rd.l[ob.formation_idx]; tgt = ob.zone_upper
        else:
            d = -1; stop = rd.h[ob.formation_idx]; tgt = ob.zone_lower
        s = rd.sig(ev.event_idx + 1, d, float(stop), float(tgt), block_horizon=True)
        if s is not None:
            out.append(s)
    return out


def _confl_ob_level(rd: RegimeData, kind: str) -> list[DemoSignal]:
    """OB rejecție/mitigare × atingere de nivel PE ACEEAȘI bară, aliniate (bull OB × PDL→long, bear × PDH→short).
    stop=min/max(raw OB floor, raw level-touch extreme); target=nivelul opus al zilei; horizon de ZI."""
    blk = [Block(0, rd.n)]
    levels = compute_prior_day_levels(rd.h, rd.l, rd.day.tolist(), blk)
    opp = _opp_level_map(levels)
    touch_at: dict[int, Any] = {t.touch_idx: t for t in detect_level_touches(rd.h, rd.l, levels, rd.day.tolist(), blk)}
    out: list[DemoSignal] = []
    for ob, ev in _obs_with_events(rd, kind, visit1_only=(kind == "mitigation")):
        t = touch_at.get(ev.event_idx)
        if t is None:
            continue
        bull = ob.kind is OrderBlockKind.BULLISH
        if bull and t.level.kind is LevelKind.PDL:
            d = 1; stop = min(rd.l[ob.formation_idx], rd.l[t.touch_idx]); tgt = opp.get(t.level.source_period_start, {}).get("PDH")
        elif (not bull) and t.level.kind is LevelKind.PDH:
            d = -1; stop = max(rd.h[ob.formation_idx], rd.h[t.touch_idx]); tgt = opp.get(t.level.source_period_start, {}).get("PDL")
        else:
            continue
        if tgt is None:
            continue
        s = rd.sig(ev.event_idx + 1, d, float(stop), float(tgt))       # horizon de ZI
        if s is not None:
            out.append(s)
    return out


def gen_cand0012_obrej_level(rd: RegimeData) -> list[DemoSignal]:
    return _confl_ob_level(rd, "rejection")


def gen_cand0016_mitig_level(rd: RegimeData) -> list[DemoSignal]:
    return _confl_ob_level(rd, "mitigation")


def gen_cand0015_obrej_fvg_confluence(rd: RegimeData) -> list[DemoSignal]:
    """OB rejecție × FVG CE-50 PE ACEEAȘI bară, aliniate. stop=min/max(raw OB floor, FVG edge); target=latura
    îndepărtată a zonei combinate; horizon de BLOC."""
    blk = [Block(0, rd.n)]
    fvgs = detect_fvgs(rd.h, rd.l, blk)
    by_formed = {f.formed_idx: f for f in fvgs}
    ce50: dict[int, dict[FVGKind, Any]] = {}
    for r in detect_fvg_reactions(rd.h, rd.l, rd.c, fvgs, blk):
        if r.ce50_touch_idx is None:
            continue
        f = by_formed.get(r.formed_idx)
        if f is not None:
            ce50.setdefault(r.ce50_touch_idx, {}).setdefault(f.kind, f)
    out: list[DemoSignal] = []
    for ob, ev in _obs_with_events(rd, "rejection", visit1_only=False):
        bull = ob.kind is OrderBlockKind.BULLISH
        want = FVGKind.BULLISH if bull else FVGKind.BEARISH
        f = ce50.get(ev.event_idx, {}).get(want)
        if f is None:
            continue
        if bull:
            d = 1; stop = min(rd.l[ob.formation_idx], f.lower); tgt = max(ob.zone_upper, f.upper)
        else:
            d = -1; stop = max(rd.h[ob.formation_idx], f.upper); tgt = min(ob.zone_lower, f.lower)
        s = rd.sig(ev.event_idx + 1, d, float(stop), float(tgt), block_horizon=True)
        if s is not None:
            out.append(s)
    return out


def _dz_by_kind(rd: RegimeData) -> dict[OrderBlockKind, list[Any]]:
    m: dict[OrderBlockKind, list[Any]] = {OrderBlockKind.BULLISH: [], OrderBlockKind.BEARISH: []}
    for z in detect_demand_zones(rd.o, rd.h, rd.l, rd.c, rd.n):
        m[z.kind].append(z)
    return m


def gen_cand0017_dz_fvg_confluence(rd: RegimeData) -> list[DemoSignal]:
    """FVG CE-50 a cărui bară se suprapune cu o DemandZone de aceeași polaritate. stop=min/max(DZ edge, FVG edge);
    target=latura îndepărtată combinată; horizon de BLOC."""
    blk = [Block(0, rd.n)]
    fvgs = detect_fvgs(rd.h, rd.l, blk)
    by_formed = {f.formed_idx: f for f in fvgs}
    dz = _dz_by_kind(rd)
    out: list[DemoSignal] = []
    for r in detect_fvg_reactions(rd.h, rd.l, rd.c, fvgs, blk):
        if r.ce50_touch_idx is None:
            continue
        f = by_formed.get(r.formed_idx)
        if f is None:
            continue
        ti = r.ce50_touch_idx
        want_ob = OrderBlockKind.BULLISH if f.kind is FVGKind.BULLISH else OrderBlockKind.BEARISH
        z = next((zz for zz in dz[want_ob] if zz.formation_idx < ti
                  and rd.l[ti] <= zz.zone_upper and rd.h[ti] >= zz.zone_lower), None)
        if z is None:
            continue
        if f.kind is FVGKind.BULLISH:
            d = 1; stop = min(z.zone_lower, f.lower); tgt = max(z.zone_upper, f.upper)
        else:
            d = -1; stop = max(z.zone_upper, f.upper); tgt = min(z.zone_lower, f.lower)
        s = rd.sig(ti + 1, d, float(stop), float(tgt), block_horizon=True)
        if s is not None:
            out.append(s)
    return out


def gen_cand0019_dz_level_confluence(rd: RegimeData) -> list[DemoSignal]:
    """Atingere de nivel a cărei bară se suprapune cu o DemandZone de aceeași polaritate (demand×PDL→long,
    supply×PDH→short). stop=min/max(DZ edge, raw touch extreme); target=nivelul opus; horizon de ZI."""
    blk = [Block(0, rd.n)]
    levels = compute_prior_day_levels(rd.h, rd.l, rd.day.tolist(), blk)
    opp = _opp_level_map(levels)
    dz = _dz_by_kind(rd)
    out: list[DemoSignal] = []
    for t in detect_level_touches(rd.h, rd.l, levels, rd.day.tolist(), blk):
        long_side = t.level.kind is LevelKind.PDL
        want = OrderBlockKind.BULLISH if long_side else OrderBlockKind.BEARISH
        ti = t.touch_idx
        z = next((zz for zz in dz[want] if zz.formation_idx < ti
                  and rd.l[ti] <= zz.zone_upper and rd.h[ti] >= zz.zone_lower), None)
        if z is None:
            continue
        pair = opp.get(t.level.source_period_start, {})
        if long_side:
            d = 1; stop = min(z.zone_lower, rd.l[ti]); tgt = pair.get("PDH")
        else:
            d = -1; stop = max(z.zone_upper, rd.h[ti]); tgt = pair.get("PDL")
        if tgt is None:
            continue
        s = rd.sig(ti + 1, d, float(stop), float(tgt))
        if s is not None:
            out.append(s)
    return out


# ══════════ lot 3 (CAND-0020..0025): sweep-uri, pool-uri, BOS/CHoCH ══════════
GROUP_A_HORIZON = 20
_C22_AMBIGUOUS: dict[str, int] = {}                        # audit F4: bare cu CHoCH dublu-semn, per regim


def _pools(rd: RegimeData) -> list[LiquidityPool]:
    sw = label_structure(detect_swings(rd.h, rd.l, [Block(0, rd.n)], k=2))
    return build_pools(sw, PoolTier.EXTERNAL)


def _nearest_pool(pools: list[LiquidityPool], side: PoolSide, entry_price: float, d: int, at_bar: int) -> float | None:
    """Prețul celui mai apropiat pool de partea `side`, disponibil (available_idx<=at_bar), dincolo de entry în
    direcția d. None dacă niciunul (→ backstop de orizont)."""
    best: float | None = None
    bestd = 0.0
    for p in pools:
        if p.side is not side or p.available_idx > at_bar:
            continue
        if (d > 0 and p.price <= entry_price) or (d < 0 and p.price >= entry_price):
            continue
        dd = abs(p.price - entry_price)
        if best is None or dd < bestd:
            best = p.price; bestd = dd
    return best


def _pool_target(rd: RegimeData, pools: list[LiquidityPool], d: int, entry_price: float, at_bar: int) -> float:
    """Ținta = cel mai apropiat pool opus SAU (dacă niciunul) o valoare inaccesibilă → doar stop/time-stop 20-bare."""
    side = PoolSide.ABOVE if d > 0 else PoolSide.BELOW
    tgt = _nearest_pool(pools, side, entry_price, d, at_bar)
    return tgt if tgt is not None else (entry_price + 1e9 if d > 0 else entry_price - 1e9)


def gen_cand0020_sweep_return(rd: RegimeData) -> list[DemoSignal]:
    """Sweep wick (close-back-inside) → reversie. BELOW→long, ABOVE→short; stop=extrema măturată (low/high[c]);
    țintă=cel mai apropiat pool OPUS OR orizont 20-bare."""
    blk = [Block(0, rd.n)]
    pools = _pools(rd)
    out: list[DemoSignal] = []
    for ev in detect_sweeps(rd.h, rd.l, rd.c, pools, blk, require_close_back_inside=True):
        c = ev.idx
        d = 1 if ev.pool.side is PoolSide.BELOW else -1
        stop = rd.l[c] if d > 0 else rd.h[c]
        entry = c + 1
        if entry >= rd.n:
            continue
        s = rd.sig(entry, d, float(stop), _pool_target(rd, pools, d, float(rd.o[entry]), c), horizon_bars=GROUP_A_HORIZON)
        if s is not None:
            out.append(s)
    return out


def gen_cand0021_bos_retest(rd: RegimeData) -> list[DemoSignal]:
    """BOS → primul retest (bara j>b cu low[j]<=P<=high[j]) în ≤20 bare; continuare. stop=extrema barei de
    retest; țintă=pool în DIRECȚIA trendului OR 20-bare."""
    blk = [Block(0, rd.n)]
    sw = label_structure(detect_swings(rd.h, rd.l, blk, k=2))
    pools = build_pools(sw, PoolTier.EXTERNAL)
    out: list[DemoSignal] = []
    for br in detect_breaks(rd.c, sw, blk):
        d = 1 if br.kind is BreakKind.BOS_BULL else (-1 if br.kind is BreakKind.BOS_BEAR else 0)
        if d == 0:
            continue
        P = br.reference_swing.price; b = br.idx; j = -1
        for k in range(b + 1, min(b + GROUP_A_HORIZON, rd.n - 1) + 1):
            if rd.l[k] <= P <= rd.h[k]:
                j = k; break
        if j < 0:
            continue
        entry = j + 1
        if entry >= rd.n:
            continue
        stop = rd.l[j] if d > 0 else rd.h[j]
        s = rd.sig(entry, d, float(stop), _pool_target(rd, pools, d, float(rd.o[entry]), j), horizon_bars=GROUP_A_HORIZON)
        if s is not None:
            out.append(s)
    return out


def gen_cand0022_choch_reversal(rd: RegimeData) -> list[DemoSignal]:
    """CHoCH auto-declanșator. F4: bare cu CHoCH de AMBELE semne (CHOCH_BULL ȘI CHOCH_BEAR la același idx) →
    NO TRADE (ambigue); numărul lor = câmp de audit. stop=extrema celui mai recent swing de tip OPUS înainte de c;
    țintă=pool opus OR 20-bare."""
    blk = [Block(0, rd.n)]
    sw = label_structure(detect_swings(rd.h, rd.l, blk, k=2))
    breaks = detect_breaks(rd.c, sw, blk)
    pools = build_pools(sw, PoolTier.EXTERNAL)
    by_bar: dict[int, set[BreakKind]] = {}
    for b in breaks:
        by_bar.setdefault(b.idx, set()).add(b.kind)
    ambiguous = {c for c, ks in by_bar.items() if BreakKind.CHOCH_BULL in ks and BreakKind.CHOCH_BEAR in ks}
    _C22_AMBIGUOUS[rd.label] = len(ambiguous)                # audit F4
    out: list[DemoSignal] = []
    for br in breaks:
        if br.idx in ambiguous:                             # F4 no-trade pe bara ambiguă
            continue
        d = 1 if br.kind is BreakKind.CHOCH_BULL else (-1 if br.kind is BreakKind.CHOCH_BEAR else 0)
        if d == 0:
            continue
        c = br.idx; entry = c + 1
        if entry >= rd.n:
            continue
        want = SwingKind.LOW if d > 0 else SwingKind.HIGH   # stop = swing OPUS cel mai recent înainte de c
        opp = [s for s in sw if s.confirmed_idx < c and s.kind is want]
        if not opp:
            continue
        stop = max(opp, key=lambda s: s.idx).price
        s = rd.sig(entry, d, float(stop), _pool_target(rd, pools, d, float(rd.o[entry]), c), horizon_bars=GROUP_A_HORIZON)
        if s is not None:
            out.append(s)
    return out


def gen_cand0023_level_bos_confluence(rd: RegimeData) -> list[DemoSignal]:
    """BOS confluent cu atingere de nivel PE ACEEAȘI bară, aliniate: BOS_BULL×PDL→long, BOS_BEAR×PDH→short.
    stop=nivelul (rupt/atins); țintă=nivelul opus al zilei; time-stop de ZI."""
    blk = [Block(0, rd.n)]
    sw = label_structure(detect_swings(rd.h, rd.l, blk, k=2))
    breaks = detect_breaks(rd.c, sw, blk)
    levels = compute_prior_day_levels(rd.h, rd.l, rd.day.tolist(), blk)
    opp = _opp_level_map(levels)
    touch_at = {t.touch_idx: t for t in detect_level_touches(rd.h, rd.l, levels, rd.day.tolist(), blk)}
    out: list[DemoSignal] = []
    for br in breaks:
        d = 1 if br.kind is BreakKind.BOS_BULL else (-1 if br.kind is BreakKind.BOS_BEAR else 0)
        if d == 0:
            continue
        t = touch_at.get(br.idx)
        if t is None:
            continue
        if d > 0 and t.level.kind is LevelKind.PDL:
            stop = t.level.price; tgt = opp.get(t.level.source_period_start, {}).get("PDH")
        elif d < 0 and t.level.kind is LevelKind.PDH:
            stop = t.level.price; tgt = opp.get(t.level.source_period_start, {}).get("PDL")
        else:
            continue
        if tgt is None:
            continue
        s = rd.sig(br.idx + 1, d, float(stop), float(tgt))   # time-stop de ZI
        if s is not None:
            out.append(s)
    return out


def gen_cand0024_sweep_fvg_confluence(rd: RegimeData) -> list[DemoSignal]:
    """Sweep × FVG de polaritate potrivită (suprapune bara de sweep, confirmat<=c). stop=min/max(extrema sweep,
    FVG edge); țintă=near edge FVG OR 20-bare."""
    blk = [Block(0, rd.n)]
    pools = _pools(rd)
    fvgs = detect_fvgs(rd.h, rd.l, blk)
    out: list[DemoSignal] = []
    for ev in detect_sweeps(rd.h, rd.l, rd.c, pools, blk, require_close_back_inside=True):
        c = ev.idx
        d = 1 if ev.pool.side is PoolSide.BELOW else -1
        want = FVGKind.BULLISH if d > 0 else FVGKind.BEARISH
        f = next((g for g in fvgs if g.kind is want and g.confirmed_idx <= c
                  and g.lower <= rd.h[c] and g.upper >= rd.l[c]), None)
        if f is None:
            continue
        entry = c + 1
        if entry >= rd.n:
            continue
        if d > 0:
            stop = min(rd.l[c], f.lower); tgt = f.upper
        else:
            stop = max(rd.h[c], f.upper); tgt = f.lower
        s = rd.sig(entry, d, float(stop), float(tgt), horizon_bars=GROUP_A_HORIZON)
        if s is not None:
            out.append(s)
    return out


def gen_cand0025_sweep_ob_confluence(rd: RegimeData) -> list[DemoSignal]:
    """Sweep în OB de polaritate potrivită (corpul OB conține extrema măturată, formation<c). stop=podeaua mai
    adâncă min(Low_OB, low[c]); țintă=latura îndepărtată a corpului OB OR 20-bare."""
    blk = [Block(0, rd.n)]
    pools = _pools(rd)
    obs = detect_order_blocks(rd.o, rd.h, rd.l, rd.c, rd.n)
    out: list[DemoSignal] = []
    for ev in detect_sweeps(rd.h, rd.l, rd.c, pools, blk, require_close_back_inside=True):
        c = ev.idx
        d = 1 if ev.pool.side is PoolSide.BELOW else -1
        want = OrderBlockKind.BULLISH if d > 0 else OrderBlockKind.BEARISH
        sx = rd.l[c] if d > 0 else rd.h[c]
        ob = next((o for o in obs if o.kind is want and o.formation_idx < c
                   and o.zone_lower <= sx <= o.zone_upper), None)
        if ob is None:
            continue
        entry = c + 1
        if entry >= rd.n:
            continue
        if d > 0:
            stop = min(rd.l[ob.formation_idx], rd.l[c]); tgt = ob.zone_upper
        else:
            stop = max(rd.h[ob.formation_idx], rd.h[c]); tgt = ob.zone_lower
        s = rd.sig(entry, d, float(stop), float(tgt), horizon_bars=GROUP_A_HORIZON)
        if s is not None:
            out.append(s)
    return out


# ══════════ lot 4 (CAND-0026..0031): niveluri de SESIUNE, primitiva A ══════════
_SH, _SL, _SM = SessionLevelKind.SESSION_HIGH, SessionLevelKind.SESSION_LOW, SessionLevelKind.SESSION_MID


def _session_ctx(rd: RegimeData) -> tuple[dict[int, dict[SessionLevelKind, float]], list[Any], list[Any]]:
    lv = compute_prior_session_levels(rd.h, rd.l, rd.session_index, rd.session_label, [Block(0, rd.n)])
    src: dict[int, dict[SessionLevelKind, float]] = {}
    for x in lv:
        src.setdefault(x.source_session_start, {})[x.kind] = x.price
    return src, list(detect_session_level_touches(rd.h, rd.l, lv)), list(detect_session_mid_touches(rd.h, rd.l, lv))


def gen_cand0027_session_touch(rd: RegimeData) -> list[DemoSignal]:
    """Atingere de nivel de sesiune (analog PDH/PDL): HIGH→short, LOW→long. stop=extrema barei de atingere;
    țintă=extrema OPUSĂ a aceleiași sesiuni-sursă; time-stop = granița de sesiune."""
    src, hl, _ = _session_ctx(rd)
    out: list[DemoSignal] = []
    for t in hl:
        lv = t.level; j = t.touch_idx
        if lv.kind is _SH:
            d = -1; stop = rd.h[j]; tgt = src[lv.source_session_start].get(_SL)
        else:
            d = 1; stop = rd.l[j]; tgt = src[lv.source_session_start].get(_SH)
        if tgt is None:
            continue
        s = rd.sig(j + 1, d, float(stop), float(tgt), day_end_override=lv.expiry_idx)
        if s is not None:
            out.append(s)
    return out


def gen_cand0026_session_sweep(rd: RegimeData) -> list[DemoSignal]:
    """Sweep de nivel de sesiune = atingere + close-back-inside pe ACEEAȘI bară (⊂ CAND-0027). Închidere DINCOLO
    (break) → NO TRADE. Reversie: HIGH→short, LOW→long."""
    src, hl, _ = _session_ctx(rd)
    out: list[DemoSignal] = []
    for t in hl:
        lv = t.level; j = t.touch_idx
        if lv.kind is _SH:
            if not (rd.c[j] < lv.price):                        # close-back-inside; altfel break → no trade
                continue
            d = -1; stop = rd.h[j]; tgt = src[lv.source_session_start].get(_SL)
        else:
            if not (rd.c[j] > lv.price):
                continue
            d = 1; stop = rd.l[j]; tgt = src[lv.source_session_start].get(_SH)
        if tgt is None:
            continue
        s = rd.sig(j + 1, d, float(stop), float(tgt), day_end_override=lv.expiry_idx)
        if s is not None:
            out.append(s)
    return out


def gen_cand0028_session_mid(rd: RegimeData) -> list[DemoSignal]:
    """Reacție la Mid (conținere). Direcție DECLARATĂ de latura de apropiere: close[j-1]>Mid→long (Mid ca suport),
    <Mid→short, ==Mid→NO TRADE. stop=extrema OPUSĂ (far) a barei de conținere; țintă=extrema sesiunii în direcție."""
    src, _, mid = _session_ctx(rd)
    out: list[DemoSignal] = []
    for t in mid:
        lv = t.level; j = t.touch_idx
        if j - 1 < 0:
            continue
        prev = rd.c[j - 1]; m = lv.price
        if prev > m:
            d = 1; stop = rd.l[j]; tgt = src[lv.source_session_start].get(_SH)
        elif prev < m:
            d = -1; stop = rd.h[j]; tgt = src[lv.source_session_start].get(_SL)
        else:
            continue                                            # tie → no trade
        if tgt is None:
            continue
        s = rd.sig(j + 1, d, float(stop), float(tgt), day_end_override=lv.expiry_idx)
        if s is not None:
            out.append(s)
    return out


def gen_cand0029_session_pdhpdl(rd: RegimeData) -> list[DemoSignal]:
    """Confluență nivel-sesiune × PDH/PDL PE ACEEAȘI bară, aliniate (HIGH×PDH→short, LOW×PDL→long). stop=extrema
    barei; țintă=nivelul opus al ZILEI; time-stop de ZI (singurul cu horizon de zi)."""
    src, hl, _ = _session_ctx(rd)
    blk = [Block(0, rd.n)]
    levels = compute_prior_day_levels(rd.h, rd.l, rd.day.tolist(), blk)
    opp = _opp_level_map(levels)
    day_touch = {dt.touch_idx: dt for dt in detect_level_touches(rd.h, rd.l, levels, rd.day.tolist(), blk)}
    out: list[DemoSignal] = []
    for t in hl:
        lv = t.level; j = t.touch_idx
        dt = day_touch.get(j)
        if dt is None:
            continue
        if lv.kind is _SH and dt.level.kind is LevelKind.PDH:
            d = -1; stop = rd.h[j]; tgt = opp.get(dt.level.source_period_start, {}).get("PDL")
        elif lv.kind is _SL and dt.level.kind is LevelKind.PDL:
            d = 1; stop = rd.l[j]; tgt = opp.get(dt.level.source_period_start, {}).get("PDH")
        else:
            continue
        if tgt is None:
            continue
        s = rd.sig(j + 1, d, float(stop), float(tgt))           # time-stop de ZI
        if s is not None:
            out.append(s)
    return out


def gen_cand0030_session_fvg(rd: RegimeData) -> list[DemoSignal]:
    """Nivel-sesiune × FVG de polaritate potrivită (bara de atingere suprapune FVG, confirmat<=j). stop=mai adânc
    (extrema barei / margine FVG); țintă=extrema opusă a sesiunii; time-stop de sesiune."""
    src, hl, _ = _session_ctx(rd)
    fvgs = detect_fvgs(rd.h, rd.l, [Block(0, rd.n)])
    out: list[DemoSignal] = []
    for t in hl:
        lv = t.level; j = t.touch_idx
        want = FVGKind.BEARISH if lv.kind is _SH else FVGKind.BULLISH
        f = next((g for g in fvgs if g.kind is want and g.confirmed_idx <= j
                  and g.lower <= rd.h[j] and g.upper >= rd.l[j]), None)
        if f is None:
            continue
        if lv.kind is _SH:
            d = -1; stop = max(rd.h[j], f.upper); tgt = src[lv.source_session_start].get(_SL)
        else:
            d = 1; stop = min(rd.l[j], f.lower); tgt = src[lv.source_session_start].get(_SH)
        if tgt is None:
            continue
        s = rd.sig(j + 1, d, float(stop), float(tgt), day_end_override=lv.expiry_idx)
        if s is not None:
            out.append(s)
    return out


def gen_cand0031_session_ob(rd: RegimeData) -> list[DemoSignal]:
    """Nivel-sesiune × OB de polaritate potrivită (corpul OB conține prețul nivelului, formation<j). stop=mai adânc
    (podeaua OB / extrema barei); țintă=latura îndepărtată a corpului OB; time-stop de sesiune."""
    src, hl, _ = _session_ctx(rd)
    obs = detect_order_blocks(rd.o, rd.h, rd.l, rd.c, rd.n)
    out: list[DemoSignal] = []
    for t in hl:
        lv = t.level; j = t.touch_idx
        want = OrderBlockKind.BEARISH if lv.kind is _SH else OrderBlockKind.BULLISH
        ob = next((o for o in obs if o.kind is want and o.formation_idx < j
                   and o.zone_lower <= lv.price <= o.zone_upper), None)
        if ob is None:
            continue
        if lv.kind is _SH:
            d = -1; stop = max(rd.h[ob.formation_idx], rd.h[j]); tgt = ob.zone_lower
        else:
            d = 1; stop = min(rd.l[ob.formation_idx], rd.l[j]); tgt = ob.zone_upper
        s = rd.sig(j + 1, d, float(stop), float(tgt), day_end_override=lv.expiry_idx)
        if s is not None:
            out.append(s)
    return out


# ══════════ CAND-0006: niveluri SĂPTĂMÂNALE (PWH/PWL), Route 3 (fără bias, direcție din tip) ══════════
def _week_last_bar(widx: list[int], n: int) -> dict[int, int]:
    last: dict[int, int] = {}
    for j in range(n):
        last[widx[j]] = j
    return last


def gen_cand0006_weekly(rd: RegimeData) -> list[DemoSignal]:
    """PWH→short (stop=high[touch], target=PWL aceleiași săptămâni-sursă); PWL→long (stop=low, target=PWH).
    DOAR săptămâni COMPLETE (≥5 zile); PARTIAL→no-trade. Atingere prin penetrare pe fereastra săptămânii curente
    (compusă din reguli ratificate, `detect_level_touches` sare weekly). time-stop = granița săptămânii. FĂRĂ bias."""
    blk = [Block(0, rd.n)]
    widx = derive_week_index(rd.day.tolist())
    levels = [lv for lv in compute_prior_week_levels(rd.h, rd.l, rd.day.tolist(), widx, blk)
              if lv.completeness == "COMPLETE"]
    opp: dict[int, dict[str, float]] = {}
    for lv in levels:
        opp.setdefault(lv.source_period_start, {})[
            "WH" if lv.kind is LevelKind.WEEKLY_HIGH else "WL"] = lv.price
    week_last = _week_last_bar(widx, rd.n)
    out: list[DemoSignal] = []
    for lv in levels:
        wk = widx[lv.available_idx]
        end = week_last[wk]
        j_touch = None
        for j in range(lv.available_idx, end + 1):
            touched = rd.h[j] >= lv.price if lv.kind is LevelKind.WEEKLY_HIGH else rd.l[j] <= lv.price
            if touched:
                j_touch = j
                break
        if j_touch is None:
            continue
        pair = opp.get(lv.source_period_start, {})
        if lv.kind is LevelKind.WEEKLY_HIGH:
            d = -1; stop = rd.h[j_touch]; tgt = pair.get("WL")
        else:
            d = 1; stop = rd.l[j_touch]; tgt = pair.get("WH")
        if tgt is None:
            continue
        s = rd.sig(j_touch + 1, d, float(stop), float(tgt), day_end_override=end)
        if s is not None:
            out.append(s)
    return out


# ══════════ lot 5 (CAND-0032..0036): niveluri de sesiune PERSISTENTE, primitiva B + filtru ATR k=1.0 ══════════
_K_FILTER = 1.0                                   # filtru de eligibilitate ATR (k=1.0 primar), manifest v2.7.41
_PTRIG: dict[str, dict[str, int]] = {}            # numărătoare de DECLANȘATOARE (înainte de performanță)


def _ptrig(cid: str, key: str, v: int = 1) -> None:
    d = _PTRIG.setdefault(cid, {})
    d[key] = d.get(key, 0) + v


def _persistent_levels(rd: RegimeData) -> list[SessionLevel]:
    return compute_persistent_session_levels(rd.h, rd.l, rd.session_index, rd.session_label, [Block(0, rd.n)])


def _feligible(price: float, j: int, rd: RegimeData) -> bool:
    """Filtru compus (NU lookahead): eligibil la bara `j` iff |price − close[j−1]| ≤ k×atr14[j−1]."""
    if j - 1 < 0:
        return False
    a = float(rd.atr[j - 1])
    return bool(np.isfinite(a) and a > 0 and abs(price - rd.c[j - 1]) <= _K_FILTER * a)


def _nearest_persistent(levels: list[SessionLevel], kind: SessionLevelKind, entry_price: float,
                        e: int, rd: RegimeData, above: bool) -> float | None:
    """Cel mai apropiat nivel persistent de tip `kind`, ACTIV la `e`, eligibil-filtru la `e`, pe latura cerută."""
    best: float | None = None
    for lv in levels:
        if lv.kind is not kind or not (lv.available_idx <= e <= lv.expiry_idx):
            continue
        p = lv.price
        if (above and p <= entry_price) or (not above and p >= entry_price):
            continue
        if not _feligible(p, e, rd):
            continue
        if best is None or abs(p - entry_price) < abs(best - entry_price):
            best = p
    return best


def gen_cand0032_persistent_sweep(rd: RegimeData) -> list[DemoSignal]:
    """B-sweep: nivel persistent H/L eligibil-filtru, penetrare + close-back-inside pe bara `j` (own-sel=sweep).
    HIGH→short, LOW→long. stop=fitilul sweep-ului; țintă=cel mai apropiat nivel persistent OPUS eligibil; 20 bare."""
    lv = _persistent_levels(rd)
    out: list[DemoSignal] = []
    for t in detect_session_level_touches(rd.h, rd.l, lv):
        L = t.level; j = t.touch_idx
        _ptrig("CAND-0032", "hl_touches")
        if j + 1 >= rd.n or not _feligible(L.price, j, rd):
            continue
        _ptrig("CAND-0032", "filter_eligible")
        ep = float(rd.o[j + 1])
        if L.kind is _SH:
            if not (rd.c[j] < L.price):
                continue
            d = -1; stop = rd.h[j]; tgt = _nearest_persistent(lv, _SL, ep, j + 1, rd, above=False)
        else:
            if not (rd.c[j] > L.price):
                continue
            d = 1; stop = rd.l[j]; tgt = _nearest_persistent(lv, _SH, ep, j + 1, rd, above=True)
        _ptrig("CAND-0032", "own_selectivity")
        if tgt is None:
            continue
        s = rd.sig(j + 1, d, float(stop), float(tgt), horizon_bars=GROUP_A_HORIZON)
        if s is not None:
            out.append(s)
    return out


def gen_cand0033_persistent_mid(rd: RegimeData) -> list[DemoSignal]:
    """B-Mid (flagship CEO): Mid persistent eligibil-filtru, CONȚINERE (own-sel). Direcție declarată de latura de
    apropiere (close[j-1]>Mid→long, <→short, ==→no-trade). stop=extrema far a barei; țintă=cel mai apropiat extrem
    persistent în direcție eligibil; 20 bare. ⚠ CONȚINERE = raportare DURĂ de declanșatoare înainte de performanță."""
    lv = _persistent_levels(rd)
    out: list[DemoSignal] = []
    for t in detect_session_mid_touches(rd.h, rd.l, lv):
        L = t.level; j = t.touch_idx
        _ptrig("CAND-0033", "mid_touches")
        if j - 1 < 0 or j + 1 >= rd.n or not _feligible(L.price, j, rd):
            continue
        _ptrig("CAND-0033", "filter_eligible")
        prev = rd.c[j - 1]; m = L.price
        if prev == m:
            continue
        _ptrig("CAND-0033", "own_selectivity")                # conținere eligibilă cu direcție declarabilă
        ep = float(rd.o[j + 1])
        if prev > m:
            d = 1; stop = rd.l[j]; tgt = _nearest_persistent(lv, _SH, ep, j + 1, rd, above=True)
        else:
            d = -1; stop = rd.h[j]; tgt = _nearest_persistent(lv, _SL, ep, j + 1, rd, above=False)
        if tgt is None:
            continue
        s = rd.sig(j + 1, d, float(stop), float(tgt), horizon_bars=GROUP_A_HORIZON)
        if s is not None:
            out.append(s)
    return out


def gen_cand0034_persistent_pdhpdl(rd: RegimeData) -> list[DemoSignal]:
    """B × PDH/PDL PE ACEEAȘI bară, aliniate (HIGH×PDH→short, LOW×PDL→long). stop=extrema barei; țintă=nivelul opus
    al ZILEI; time-stop de ZI (referință robustă la feed)."""
    lv = _persistent_levels(rd)
    blk = [Block(0, rd.n)]
    levels = compute_prior_day_levels(rd.h, rd.l, rd.day.tolist(), blk)
    opp = _opp_level_map(levels)
    day_touch = {dt.touch_idx: dt for dt in detect_level_touches(rd.h, rd.l, levels, rd.day.tolist(), blk)}
    out: list[DemoSignal] = []
    for t in detect_session_level_touches(rd.h, rd.l, lv):
        L = t.level; j = t.touch_idx
        _ptrig("CAND-0034", "hl_touches")
        if not _feligible(L.price, j, rd):
            continue
        _ptrig("CAND-0034", "filter_eligible")
        dt = day_touch.get(j)
        if dt is None:
            continue
        if L.kind is _SH and dt.level.kind is LevelKind.PDH:
            d = -1; stop = rd.h[j]; tgt = opp.get(dt.level.source_period_start, {}).get("PDL")
        elif L.kind is _SL and dt.level.kind is LevelKind.PDL:
            d = 1; stop = rd.l[j]; tgt = opp.get(dt.level.source_period_start, {}).get("PDH")
        else:
            continue
        _ptrig("CAND-0034", "own_selectivity")
        if tgt is None:
            continue
        s = rd.sig(j + 1, d, float(stop), float(tgt))         # time-stop de ZI
        if s is not None:
            out.append(s)
    return out


def gen_cand0035_persistent_fvg(rd: RegimeData) -> list[DemoSignal]:
    """B × FVG polaritate potrivită la nivel (bara de atingere suprapune FVG, confirmat<=j). stop=mai adânc
    (extrema barei / margine far FVG); țintă=margine near FVG (direcția reacției); 20 bare."""
    lv = _persistent_levels(rd)
    fvgs = detect_fvgs(rd.h, rd.l, [Block(0, rd.n)])
    out: list[DemoSignal] = []
    for t in detect_session_level_touches(rd.h, rd.l, lv):
        L = t.level; j = t.touch_idx
        _ptrig("CAND-0035", "hl_touches")
        if not _feligible(L.price, j, rd):
            continue
        _ptrig("CAND-0035", "filter_eligible")
        want = FVGKind.BEARISH if L.kind is _SH else FVGKind.BULLISH
        f = next((g for g in fvgs if g.kind is want and g.confirmed_idx <= j
                  and g.lower <= rd.h[j] and g.upper >= rd.l[j]), None)
        if f is None:
            continue
        _ptrig("CAND-0035", "own_selectivity")
        if L.kind is _SH:
            d = -1; stop = max(rd.h[j], f.upper); tgt = f.lower
        else:
            d = 1; stop = min(rd.l[j], f.lower); tgt = f.upper
        s = rd.sig(j + 1, d, float(stop), float(tgt), horizon_bars=GROUP_A_HORIZON)
        if s is not None:
            out.append(s)
    return out


def gen_cand0036_persistent_ob(rd: RegimeData) -> list[DemoSignal]:
    """B × OB polaritate potrivită (corpul OB conține prețul nivelului, formation<j). stop=mai adânc (podeaua OB /
    extrema barei); țintă=latura far a corpului OB; 20 bare."""
    lv = _persistent_levels(rd)
    obs = detect_order_blocks(rd.o, rd.h, rd.l, rd.c, rd.n)
    out: list[DemoSignal] = []
    for t in detect_session_level_touches(rd.h, rd.l, lv):
        L = t.level; j = t.touch_idx
        _ptrig("CAND-0036", "hl_touches")
        if not _feligible(L.price, j, rd):
            continue
        _ptrig("CAND-0036", "filter_eligible")
        want = OrderBlockKind.BEARISH if L.kind is _SH else OrderBlockKind.BULLISH
        ob = next((o for o in obs if o.kind is want and o.formation_idx < j
                   and o.zone_lower <= L.price <= o.zone_upper), None)
        if ob is None:
            continue
        _ptrig("CAND-0036", "own_selectivity")
        if L.kind is _SH:
            d = -1; stop = max(rd.h[ob.formation_idx], rd.h[j]); tgt = ob.zone_lower
        else:
            d = 1; stop = min(rd.l[ob.formation_idx], rd.l[j]); tgt = ob.zone_upper
        s = rd.sig(j + 1, d, float(stop), float(tgt), horizon_bars=GROUP_A_HORIZON)
        if s is not None:
            out.append(s)
    return out


def persistent_funnel(regimes: list[RegimeData]) -> dict[str, Any]:
    """Palnia pe niveluri PERSISTENTE (primitiva B) — populația CEA MAI VECHE din pipeline. Red Team a prezis
    INVERSAREA predicției Statisticianului (conflict structural MAXIM aici). Aceeași metrică: emise → atinse → aliniate."""
    kinds = [_SH, _SL, _SM]
    agg = {k: {"emitted": 0, "touched": 0, "aligned": 0} for k in kinds}
    per_regime: dict[str, Any] = {}
    for rd in regimes:
        lv = _persistent_levels(rd)
        f = {k: {"emitted": 0, "touched": 0, "aligned": 0} for k in kinds}
        for x in lv:
            f[x.kind]["emitted"] += 1
        for t in detect_session_level_touches(rd.h, rd.l, lv):
            k = t.level.kind; j = t.touch_idx; f[k]["touched"] += 1
            if (k is _SH and rd.bias_dn[j]) or (k is _SL and rd.bias_up[j]):
                f[k]["aligned"] += 1
        for t in detect_session_mid_touches(rd.h, rd.l, lv):
            j = t.touch_idx; f[_SM]["touched"] += 1
            if j - 1 >= 0:
                prev = rd.c[j - 1]; m = t.level.price
                if (prev > m and rd.bias_up[j]) or (prev < m and rd.bias_dn[j]):
                    f[_SM]["aligned"] += 1
        per_regime[rd.label] = {k.value: v for k, v in f.items()}
        for k in kinds:
            for m2 in ("emitted", "touched", "aligned"):
                agg[k][m2] += f[k][m2]
    return {"per_regime": per_regime, "aggregate": {k.value: v for k, v in agg.items()}}


def weekly_funnel(regimes: list[RegimeData]) -> dict[str, Any]:
    """Palnia PWH/PWL (perioada cea mai LUNGĂ) — reconfirmă colapsul (Statistician: 6/275=2,2% cu bias). Route 3
    NU folosește bias; aliniatul e raportat DOAR ca referință de conflict structural, nu ca filtru al politicii."""
    hi, lo = LevelKind.WEEKLY_HIGH, LevelKind.WEEKLY_LOW
    agg = {"weekly_high": {"emitted": 0, "touched": 0, "aligned": 0},
           "weekly_low": {"emitted": 0, "touched": 0, "aligned": 0}}
    for rd in regimes:
        widx = derive_week_index(rd.day.tolist())
        levels = [lv for lv in compute_prior_week_levels(rd.h, rd.l, rd.day.tolist(), widx, [Block(0, rd.n)])
                  if lv.completeness == "COMPLETE"]
        week_last = _week_last_bar(widx, rd.n)
        for lv in levels:
            key = "weekly_high" if lv.kind is hi else "weekly_low"
            agg[key]["emitted"] += 1
            wk = widx[lv.available_idx]; end = week_last[wk]
            for j in range(lv.available_idx, end + 1):
                touched = rd.h[j] >= lv.price if lv.kind is hi else rd.l[j] <= lv.price
                if touched:
                    agg[key]["touched"] += 1
                    if (lv.kind is hi and rd.bias_dn[j]) or (lv.kind is lo and rd.bias_up[j]):
                        agg[key]["aligned"] += 1
                    break
    return {"aggregate": agg}


def session_funnel(regimes: list[RegimeData]) -> dict[str, Any]:
    """Palnia Statisticianului per tip de nivel (High/Low/Mid SEPARAT): emise → atinse geometric → aliniate la bias.
    Aliniat: HIGH→bias jos (short), LOW→bias sus (long), MID→bias = direcția declarată de apropiere (close[j-1] vs Mid)."""
    kinds = [_SH, _SL, _SM]
    agg = {k: {"emitted": 0, "touched": 0, "aligned": 0} for k in kinds}
    per_regime: dict[str, Any] = {}
    for rd in regimes:
        lv = compute_prior_session_levels(rd.h, rd.l, rd.session_index, rd.session_label, [Block(0, rd.n)])
        f = {k: {"emitted": 0, "touched": 0, "aligned": 0} for k in kinds}
        for x in lv:
            f[x.kind]["emitted"] += 1
        for t in detect_session_level_touches(rd.h, rd.l, lv):
            k = t.level.kind; j = t.touch_idx; f[k]["touched"] += 1
            if (k is _SH and rd.bias_dn[j]) or (k is _SL and rd.bias_up[j]):
                f[k]["aligned"] += 1
        for t in detect_session_mid_touches(rd.h, rd.l, lv):
            j = t.touch_idx; f[_SM]["touched"] += 1
            if j - 1 >= 0:
                prev = rd.c[j - 1]; m = t.level.price
                if (prev > m and rd.bias_up[j]) or (prev < m and rd.bias_dn[j]):
                    f[_SM]["aligned"] += 1
        per_regime[rd.label] = {k.value: v for k, v in f.items()}
        for k in kinds:
            for m2 in ("emitted", "touched", "aligned"):
                agg[k][m2] += f[k][m2]
    return {"per_regime": per_regime, "aggregate": {k.value: v for k, v in agg.items()}}


def _run_fixed(gen: GateFn) -> RunFn:
    def r(rd: RegimeData) -> tuple[list[DemoSignal], list[DemoTradeResult]]:
        sigs = gen(rd)
        return sigs, simulate_demo_trades(sigs, rd.o, rd.h, rd.l, rd.c, TICK_SIZE)
    return r


def _run_dynamic(gen_exp: Callable[[RegimeData, list[bool]], list[DemoSignal]]) -> RunFn:
    """Pt. politicile cu exit = prima expansiune OPUSĂ (CAND-0002/0008/0009)."""
    def r(rd: RegimeData) -> tuple[list[DemoSignal], list[DemoTradeResult]]:
        exp = expansion(rd.o, rd.h, rd.l, rd.c)
        exp_dir = [(1 if rd.c[j] > rd.o[j] else -1) if exp[j] else 0 for j in range(rd.n)]
        sigs = gen_exp(rd, exp)
        return sigs, simulate_demo_trades_dynamic(sigs, rd.o, rd.h, rd.l, rd.c, exp_dir, TICK_SIZE)
    return r


CANDIDATES: list[tuple[str, str, RunFn]] = [
    ("CAND-0001", "PDH-PDL", _run_fixed(gen_cand0001_pdh_pdl)),
    ("CAND-0002", "COMPRESSION-EXPANSION", _run_dynamic(gen_cand0002_compression_expansion)),
    ("CAND-0003", "FVG-CE50-REACTION", _run_fixed(gen_cand0003_fvg_ce50)),
    ("CAND-0007", "LEVEL-FVG-CONFLUENCE", _run_fixed(gen_cand0007_level_fvg_confluence)),
    ("CAND-0008", "VOID-DISPLACEMENT", _run_dynamic(gen_cand0008_void_displacement)),
    ("CAND-0009", "LEVEL-BREAK-DRIVE", _run_dynamic(gen_cand0009_level_break_drive)),
    ("CAND-0010", "FVG-STACK-DENSITY", _run_fixed(gen_cand0010_fvg_stack_density)),
    ("CAND-0011", "OB-SWEEP-REJECTION", _run_fixed(gen_cand0011_ob_rejection)),
    ("CAND-0012", "OBREJ-LEVEL-CONFLUENCE", _run_fixed(gen_cand0012_obrej_level)),
    ("CAND-0013", "DEMAND-ZONE-REENTRY", _run_fixed(gen_cand0013_demand_zone_reentry)),
    ("CAND-0014", "OB-MITIGATION", _run_fixed(gen_cand0014_ob_mitigation)),
    ("CAND-0015", "OBREJ-FVG-CONFLUENCE", _run_fixed(gen_cand0015_obrej_fvg_confluence)),
    ("CAND-0016", "MITIG-LEVEL-CONFLUENCE", _run_fixed(gen_cand0016_mitig_level)),
    ("CAND-0017", "DZ-FVG-CONFLUENCE", _run_fixed(gen_cand0017_dz_fvg_confluence)),
    ("CAND-0018", "OBREJ-VOID-CONFLUENCE", _run_fixed(gen_cand0018_obrej_void_confluence)),
    ("CAND-0019", "DZ-LEVEL-CONFLUENCE", _run_fixed(gen_cand0019_dz_level_confluence)),
    ("CAND-0020", "LIQUIDITY-SWEEP-RETURN", _run_fixed(gen_cand0020_sweep_return)),
    ("CAND-0021", "BOS-RETEST", _run_fixed(gen_cand0021_bos_retest)),
    ("CAND-0022", "CHOCH-REVERSAL", _run_fixed(gen_cand0022_choch_reversal)),
    ("CAND-0023", "LEVEL-BOS-CONFLUENCE", _run_fixed(gen_cand0023_level_bos_confluence)),
    ("CAND-0024", "SWEEP-FVG-CONFLUENCE", _run_fixed(gen_cand0024_sweep_fvg_confluence)),
    ("CAND-0025", "SWEEP-OB-CONFLUENCE", _run_fixed(gen_cand0025_sweep_ob_confluence)),
    ("CAND-0026", "SESSION-SWEEP-REVERSAL", _run_fixed(gen_cand0026_session_sweep)),
    ("CAND-0027", "SESSION-TOUCH-REJECTION", _run_fixed(gen_cand0027_session_touch)),
    ("CAND-0028", "SESSION-MID-REACTION", _run_fixed(gen_cand0028_session_mid)),
    ("CAND-0029", "SESSION-PDHPDL-CONFLUENCE", _run_fixed(gen_cand0029_session_pdhpdl)),
    ("CAND-0030", "SESSION-FVG-CONFLUENCE", _run_fixed(gen_cand0030_session_fvg)),
    ("CAND-0031", "SESSION-OB-CONFLUENCE", _run_fixed(gen_cand0031_session_ob)),
    ("CAND-0006", "PWH-PWL-WEEKLY-R3", _run_fixed(gen_cand0006_weekly)),
    ("CAND-0032", "PERSISTENT-SESSION-SWEEP", _run_fixed(gen_cand0032_persistent_sweep)),
    ("CAND-0033", "PERSISTENT-SESSION-MID", _run_fixed(gen_cand0033_persistent_mid)),
    ("CAND-0034", "PERSISTENT-SESSION-PDHPDL", _run_fixed(gen_cand0034_persistent_pdhpdl)),
    ("CAND-0035", "PERSISTENT-SESSION-FVG", _run_fixed(gen_cand0035_persistent_fvg)),
    ("CAND-0036", "PERSISTENT-SESSION-OB", _run_fixed(gen_cand0036_persistent_ob)),
]
_PTRIG_ORDER = ["hl_touches", "mid_touches", "filter_eligible", "own_selectivity"]


def _mdd(equity: np.ndarray) -> float:
    peak = -1e18; mdd = 0.0
    for v in equity:
        peak = max(peak, float(v)); mdd = max(mdd, peak - float(v))
    return mdd


def _metrics(rows: list[tuple[int, str, DemoTradeResult]]) -> dict[str, Any]:
    valid = [r for (_y, _reg, r) in rows if r.traded and r.net_R is not None
             and r.exit_reason in (ExitReason.STOP.value, ExitReason.TARGET.value, ExitReason.TIME_STOP.value)]
    n_invalid = sum(1 for (_y, _reg, r) in rows if r.exit_reason == ExitReason.INVALID_EXECUTION.value)
    n_notrade = sum(1 for (_y, _reg, r) in rows if r.exit_reason == ExitReason.NO_TRADE.value)
    n = len(valid)
    n_stop = sum(1 for r in valid if r.exit_reason == ExitReason.STOP.value)
    n_target = sum(1 for r in valid if r.exit_reason == ExitReason.TARGET.value)
    n_time = sum(1 for r in valid if r.exit_reason == ExitReason.TIME_STOP.value)
    base: dict[str, Any] = {"n_trades": n, "n_invalid": n_invalid, "n_no_trade": n_notrade,
                            "invalid_fraction": round(n_invalid / (n + n_invalid), 4) if (n + n_invalid) else None,
                            "exit_stop": n_stop, "exit_target": n_target, "exit_time_stop": n_time,
                            "frac_time_stop": round(n_time / n, 4) if n else None}
    if n == 0:
        return base
    nr = np.array([r.net_R for (_y, _reg, r) in rows if r in valid], dtype=float)
    nd = np.array([float(r.net_dollars) for (_y, _reg, r) in rows if r in valid and r.net_dollars is not None])
    wins = nr[nr > 0]; losses = nr[nr < 0]
    pf = float(wins.sum() / abs(losses.sum())) if losses.size and losses.sum() != 0 else None
    sd = float(nr.std(ddof=1)) if n > 1 else 0.0
    eqR = np.cumsum(nr); eqD = np.cumsum(nd)
    # stabilitate anuală (doar ani cu n>=25; goluri păstrate)
    yr_valid = [(_y, r.net_R) for (_y, _reg, r) in rows if r in valid and r.net_R is not None]
    years: dict[int, list[float]] = {}
    for y, rr in yr_valid:
        years.setdefault(y, []).append(rr)
    ann: dict[str, Any] = {}
    elig = pos = 0
    for y in sorted(years):
        cnt = len(years[y])
        if cnt < N_MIN:
            ann[str(y)] = {"n": cnt, "INSUFFICIENT_N": True}
            continue
        elig += 1; s = float(np.sum(years[y])); positive = s > 0
        pos += 1 if positive else 0
        ann[str(y)] = {"n": cnt, "net_R": round(s, 3), "positive": positive}
    # stabilitate pe regimuri
    reg_valid: dict[str, list[float]] = {}
    for _y, reg, r in rows:
        if r in valid and r.net_R is not None:
            reg_valid.setdefault(reg, []).append(r.net_R)
    reg_stab: dict[str, Any] = {}
    reg_pos = 0
    for reg in REGIMES:
        v = reg_valid.get(reg, [])
        if not v:
            reg_stab[reg] = {"n": 0}
            continue
        s = float(np.sum(v)); reg_stab[reg] = {"n": len(v), "net_R": round(s, 3), "positive": s > 0}
        reg_pos += 1 if s > 0 else 0
    base.update(
        winrate=round(float((nr > 0).mean()), 4), profit_factor=round(pf, 4) if pf is not None else None,
        expectancy_R=round(float(nr.mean()), 5), expectancy_dollars=round(float(nd.mean()), 5),
        net_R=round(float(nr.sum()), 3), net_dollars=round(float(nd.sum()), 3),
        max_drawdown_R=round(_mdd(eqR), 3), max_drawdown_dollars=round(_mdd(eqD), 3),
        sharpe_per_trade=round(float(nr.mean() / sd), 4) if sd > 0 else None,
        annual_stability={"positive_years": pos, "eligible_years": elig, "by_year": ann},
        regime_stability={"positive_regimes": reg_pos, "of": 3, "by_regime": reg_stab})
    return base


def _htf_trend(dfh: Any, period: int) -> Any:
    ema20 = dfh["close"].ewm(span=20).mean(); ema50 = dfh["close"].ewm(span=50).mean()
    tu = (ema20 > ema50).astype(float)
    avail = dfh["time"].shift(-1); avail.iloc[-1] = int(dfh["time"].iloc[-1]) + period
    return pd.DataFrame({"avail": avail.astype("int64"), "trend_up": tu.to_numpy()})


def _session_eod(sidx: list[int], n: int) -> np.ndarray:
    eod = np.empty(n, dtype=np.int64); last = n - 1
    for j in range(n - 1, -1, -1):
        if j < n - 1 and sidx[j] != sidx[j + 1]:
            last = j
        eod[j] = last
    return eod


def load_regimes() -> list[RegimeData]:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh1, _ = load("H1_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    dfh4, _ = load("H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    if len(dfm) != 130_491:
        raise SystemExit(f"STOP: M15 {len(dfm)}.")
    dfm = dfm.sort_values("time").reset_index(drop=True)
    for name, dfh, per in (("h1", dfh1, 3600), ("h4", dfh4, 4 * 3600)):     # bias context-derived, forward-safe
        htf = _htf_trend(dfh, per).sort_values("avail")
        dfm = pd.merge_asof(dfm, htf.rename(columns={"trend_up": name}), left_on="time", right_on="avail",
                            direction="backward").drop(columns="avail")
    t_all = dfm["time"].to_numpy()
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]
    regimes: list[RegimeData] = []
    for i, seg in enumerate(segs):
        rlabel = REGIMES[i]
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(rlabel) not in (None, len(sub)):
            raise SystemExit(f"STOP: {rlabel} {len(sub)} bare.")
        n = len(sub)
        day = _day_index(sub["time"])
        tm = [int(x) for x in sub["time"].tolist()]
        sidx = derive_session_index(tm); slab = session_labels(tm)
        h1 = sub["h1"].to_numpy(); h4 = sub["h4"].to_numpy()
        bias_up = (h1 > 0.5) & (h4 > 0.5)
        bias_dn = (h1 <= 0.5) & (h4 <= 0.5) & np.isfinite(h1) & np.isfinite(h4)
        regimes.append(RegimeData(
            rlabel, sub["open"].tolist(), sub["high"].tolist(), sub["low"].tolist(), sub["close"].tolist(),
            tm, sub["atr14"].to_numpy(), day, _eod_per_bar(day, n),
            pd.to_datetime(sub["time"], unit="s", utc=True).dt.year.to_numpy(), n,
            sidx, slab, _session_eod(sidx, n), bias_up, bias_dn))
    return regimes


def main() -> int:
    print(f"loader v6 | costuri MODELATE spread={EFF_SPREAD} cost={COST} tick={TICK_SIZE} | N_MIN={N_MIN}")
    regimes = load_regimes()
    out: dict[str, Any] = {"note": "descriptive triage; NOT validation; no p-value; costs modeled",
                           "costs": {"effective_spread": EFF_SPREAD, "cost": COST, "tick_size": TICK_SIZE},
                           "candidates": {}}
    for cid, name, runner in CANDIDATES:
        rows: list[tuple[int, str, DemoTradeResult]] = []
        for rd in regimes:
            sigs, results = runner(rd)
            for s, res in zip(sigs, results):
                rows.append((int(rd.year[s.entry_idx]), rd.label, res))
        m = _metrics(rows)
        out["candidates"][cid] = {"policy": name, **m}
        print(f"\n########## {cid} {name} ##########")
        if cid in _PTRIG:                                     # numărul de DECLANȘATOARE, ÎNAINTE de performanță
            d = _PTRIG[cid]
            out["candidates"][cid]["triggers_before_performance"] = dict(d)
            print("  DECLANȘATOARE (înainte de performanță): "
                  + "  ".join(f"{k}={d[k]}" for k in _PTRIG_ORDER if k in d)
                  + f"  → semnale={len([1 for _y,_r,_x in rows])}")
        if m["n_trades"] == 0:
            print(f"  n=0 (invalid={m['n_invalid']} no_trade={m['n_no_trade']})"); continue
        print(f"  n={m['n_trades']} | invalid={m['n_invalid']} ({m['invalid_fraction']}) no_trade={m['n_no_trade']}")
        print(f"  WR={m['winrate']} PF={m['profit_factor']} | E_R={m['expectancy_R']:+.4f} E_$={m['expectancy_dollars']:+.4f}")
        print(f"  netR={m['net_R']:+.2f} net$={m['net_dollars']:+.2f} | maxDD_R={m['max_drawdown_R']} maxDD_$={m['max_drawdown_dollars']} | Sharpe/trade={m['sharpe_per_trade']}")
        a = m["annual_stability"]; g = m["regime_stability"]
        print(f"  ani pozitivi: {a['positive_years']}/{a['eligible_years']} (din 8 posibili, goluri 2014/15/19 sigilate)")
        yr_bits = []
        for y, v in a["by_year"].items():
            yr_bits.append(f"{y}:INSUF(n{v['n']})" if v.get("INSUFFICIENT_N") else f"{y}:{v['net_R']:+.1f}({'+'if v['positive'] else '-'})")
        print("    " + "  ".join(yr_bits))
        print(f"  regimuri pozitive: {g['positive_regimes']}/3  " +
              "  ".join(f"{r}:{g['by_regime'][r].get('net_R','n0')}" for r in REGIMES))

    out["CAND-0022_F4_audit"] = {"ambiguous_dual_sign_choch_bars_per_regime": dict(_C22_AMBIGUOUS),
                                 "total": sum(_C22_AMBIGUOUS.values())}
    print(f"\n### AUDIT F4 (CAND-0022) — bare cu CHoCH dublu-semn (NO-TRADE): "
          f"{dict(_C22_AMBIGUOUS)} | total={sum(_C22_AMBIGUOUS.values())}")

    # PALNIA de sesiune (predicția Statisticianului) — per tip de nivel, High/Low/Mid SEPARAT
    funnel = session_funnel(regimes)
    out["session_funnel"] = funnel
    print("\n### PALNIA DE SESIUNE (emise → atinse geometric → aliniate la bias), per tip (agregat) ###")
    for kind, v in funnel["aggregate"].items():
        em, tc, al = v["emitted"], v["touched"], v["aligned"]
        print(f"  {kind:13s} emise={em:5d} → atinse={tc:5d} ({100.0*tc/em:.1f}%) → aliniate={al:4d} "
              f"({100.0*al/em:.1f}% din emise, {100.0*al/tc if tc else 0:.1f}% din atinse)")
    print("  (PWH/PWL: 6/275=2,2% aliniate; predicție Statistician: SESIUNILE suferă CEL MAI PUȚIN — perioada cea mai scurtă)")

    # PALNIA PERSISTENTĂ (primitiva B) — a DOUA testare a predicției, în direcția OPUSĂ (Red Team: inversare la populația veche)
    pfunnel = persistent_funnel(regimes)
    out["persistent_funnel"] = pfunnel
    print("\n### PALNIA PERSISTENTĂ / primitiva B (populația CEA MAI VECHE — Red Team prezice INVERSAREA) ###")
    for kind, v in pfunnel["aggregate"].items():
        em, tc, al = v["emitted"], v["touched"], v["aligned"]
        print(f"  {kind:13s} emise={em:6d} → atinse={tc:6d} ({100.0*tc/em if em else 0:.1f}%) → aliniate={al:5d} "
              f"({100.0*al/tc if tc else 0:.1f}% din atinse)")

    # PALNIA SĂPTĂMÂNALĂ (PWH/PWL) — perioada cea mai LUNGĂ, reconfirmă colapsul
    wfunnel = weekly_funnel(regimes)
    out["weekly_funnel"] = wfunnel
    print("\n### PALNIA SĂPTĂMÂNALĂ / PWH-PWL (perioada cea mai LUNGĂ — colaps de referință) ###")
    for kind, v in wfunnel["aggregate"].items():
        em, tc, al = v["emitted"], v["touched"], v["aligned"]
        print(f"  {kind:12s} emise={em:5d} → atinse={tc:5d} ({100.0*tc/em if em else 0:.1f}%) → aliniate={al:4d} "
              f"({100.0*al/tc if tc else 0:.1f}% din atinse)")

    path = os.path.join(_ROOT, "reports", "phase1_screening_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/phase1_screening_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
