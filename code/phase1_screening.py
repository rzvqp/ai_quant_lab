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
from institutional_levels import LevelKind, compute_prior_day_levels, detect_level_touches
from imbalance_mechanics import FVGKind, detect_fvgs, detect_fvg_reactions
from pdh_pdl_demo_engine import DemoSignal, DemoTradeResult, ExitReason, simulate_demo_trades  # type: ignore[import-not-found]

EFF_SPREAD, COST, TICK_SIZE = 0.10, 0.20, 0.01     # constante frozen, MODELATE pt. backtest, IDENTICE pt. toți
N_MIN = 25
REGIMES = ["bear", "bull", "correction"]
EXPECTED_BARS = {"bear": 52_403, "bull": 52_851, "correction": 25_237}
GateFn = Callable[["RegimeData"], list[DemoSignal]]


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
                 atr: np.ndarray, day: np.ndarray, eod: np.ndarray, year: np.ndarray, n: int) -> None:
        self.label = label; self.o = o; self.h = h; self.l = l; self.c = c
        self.atr = atr; self.day = day; self.eod = eod; self.year = year; self.n = n

    def sig(self, entry_idx: int, direction: int, stop_price: float, target_price: float,
            block_horizon: bool = False) -> DemoSignal | None:
        """block_horizon=True → time-stop pe granița de BLOC (n-1), conform contractelor cu horizon de bloc
        (CAND-0003); implicit = time-stop de ZI (`eod`), pt. politicile cu horizon zilnic (CAND-0001/0007)."""
        if entry_idx >= self.n:
            return None
        a = float(self.atr[entry_idx - 1]) if entry_idx - 1 >= 0 else float("nan")
        if not np.isfinite(a) or a <= 0:
            return None
        dend = self.n - 1 if block_horizon else int(self.eod[entry_idx])
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


CANDIDATES: list[tuple[str, str, GateFn]] = [
    ("CAND-0001", "PDH-PDL", gen_cand0001_pdh_pdl),
    ("CAND-0003", "FVG-CE50-REACTION", gen_cand0003_fvg_ce50),
    ("CAND-0007", "LEVEL-FVG-CONFLUENCE", gen_cand0007_level_fvg_confluence),
]
# CAND-0002 COMPRESSION-EXPANSION: exit = "prima expansiune opusă" (dinamic, nu preț fix) + time-stop pe
# graniță de BLOC (degenerat forward, Finding H). Motorul fixed-target NU-l reprezintă → RAPORTAT ca ne-rulabil.


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
    base: dict[str, Any] = {"n_trades": n, "n_invalid": n_invalid, "n_no_trade": n_notrade,
                            "invalid_fraction": round(n_invalid / (n + n_invalid), 4) if (n + n_invalid) else None}
    if n == 0:
        return base
    nr = np.array([r.net_R for (_y, _reg, r) in rows if r in valid], dtype=float)
    nd = np.array([float(r.net_dollars) for (_y, _reg, r) in rows if r in valid and r.net_dollars is not None])
    wins = nr[nr > 0]; losses = nr[nr < 0]
    pf = float(wins.sum() / abs(losses.sum())) if losses.size and losses.sum() != 0 else None
    sd = float(nr.std(ddof=1)) if n > 1 else 0.0
    eqR = np.cumsum(nr); eqD = np.cumsum(nd)
    # stabilitate anuală (doar ani cu n>=25; goluri păstrate)
    yr_valid = [(_y, r.net_R) for (_y, _reg, r) in rows if r in valid]
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


def main() -> int:
    dfm, _ = load("M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)
    print(f"loader v6 | M15={len(dfm)} | costuri MODELATE spread={EFF_SPREAD} cost={COST} tick={TICK_SIZE} | N_MIN={N_MIN}")
    if len(dfm) != 130_491:
        print(f"STOP: M15 {len(dfm)}."); return 2
    dfm = dfm.sort_values("time").reset_index(drop=True)
    t_all = dfm["time"].to_numpy()
    manifest = SM.load_manifest()
    segs = [s for s in manifest["timeframes"]["M15_v2"]["regime_segments"] if "discovery_range" in s]

    regimes: list[RegimeData] = []
    for i, seg in enumerate(segs):
        rlabel = REGIMES[i]
        s_ep, e_ep = seg["discovery_range"]["start_epoch"], seg["discovery_range"]["end_epoch"]
        sub = dfm[(t_all >= s_ep) & (t_all < e_ep)].reset_index(drop=True)
        if EXPECTED_BARS.get(rlabel) not in (None, len(sub)):
            print(f"STOP: {rlabel} {len(sub)} bare."); return 3
        n = len(sub)
        day = _day_index(sub["time"])
        regimes.append(RegimeData(
            rlabel, sub["open"].tolist(), sub["high"].tolist(), sub["low"].tolist(), sub["close"].tolist(),
            sub["atr14"].to_numpy(), day, _eod_per_bar(day, n),
            pd.to_datetime(sub["time"], unit="s", utc=True).dt.year.to_numpy(), n))

    out: dict[str, Any] = {"note": "descriptive triage; NOT validation; no p-value; costs modeled",
                           "costs": {"effective_spread": EFF_SPREAD, "cost": COST, "tick_size": TICK_SIZE},
                           "candidates": {}}
    for cid, name, fn in CANDIDATES:
        rows: list[tuple[int, str, DemoTradeResult]] = []
        for rd in regimes:
            sigs = fn(rd)
            results = simulate_demo_trades(sigs, rd.o, rd.h, rd.l, rd.c, TICK_SIZE)
            for s, res in zip(sigs, results):
                rows.append((int(rd.year[s.entry_idx]), rd.label, res))
        m = _metrics(rows)
        out["candidates"][cid] = {"policy": name, **m}
        print(f"\n########## {cid} {name} ##########")
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

    print("\n########## CAND-0002 COMPRESSION-EXPANSION — NU rulat în acest lot ##########")
    print("  Exit = 'prima expansiune opusă' (eveniment dinamic, nu preț fix) + time-stop pe graniță de BLOC")
    print("  (degenerat forward, Finding H). Motorul fixed-target nu-l reprezintă fără o extensie de exit dinamic.")

    path = os.path.join(_ROOT, "reports", "phase1_screening_results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("\nrecord -> reports/phase1_screening_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
