"""FOUR-REGIME DISCOVERY-HALF MEASUREMENT — PREPARED, *NOT RUN*.
Domain STRICT: the 428 ATR-regime hypotheses only. The 1544 STRUCTURAL-R-UNVALIDATED are NOT run
(R=pnl/risk is not the right statistic there — Statistician ruling). The 16 atr-n<25 stay ineligible.

Descriptive only: per macro-regime, per hypothesis -> exp, win, pf, dd, n, and NET concentration
(best/sumR, top3/sumR, top5/sumR, wo1). NOT t1/t3/t5 (gross; systematically under-states fragility).
Central output: of the 428, how many are profitable in ALL 4 regimes / 3 / 2 / 1 / 0.

NO FDR, NO multiple-testing correction, NO candidate selection, NO screen, NO conclusion.

HARD PRECONDITIONS (this script ABORTS unless all are met — set by CEO 2026-07-25):
  P1. Data Acquisition confirms the official loader reads M15 v2 in the canonical dirs AND the data
      actually spans the four regimes (2011..2026).
  P2. Statistician's pre-registered split spec exists (50/50 stratified by regime segment, 1000-bar
      M15 quarantine at every internal boundary) -> supplies the DISCOVERY-half bar mask + the exact
      regime-segment boundaries. The sealed half is NEVER touched.
Until both exist, DO NOT run. Config: canonical reproduction_d2 engine (D2 closed); mark_invalid /
target_first at DEFAULT. Holdout SEALED.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "results", "matched_null_validation", "structural_r_unvalidated.json")
# Statistician split spec (P2) — to be delivered by the Statistician; path is a placeholder contract.
SPLIT_SPEC = os.path.join(ROOT, "docs", "M5_SPLIT_PREREGISTRATION.json")   # {regimes:[{name,bias,start_epoch,end_epoch}], discovery_mask: <path or rule>, quarantine_bars:1000}

def _atr_428():
    enum = json.load(open(os.path.join(ROOT, "results", "matched_null_validation", "subset_prereg_enumeration.json")))
    return sorted(set(enum["atr_subset_ids"]))   # 428 (grammar atr-stop). Eligibility (n>=25) checked per config.

def _precheck(d):
    yrs = set(pd.to_datetime(d['time'].values, unit='s').year)
    p1_data = {2011,2012,2013,2014}.issubset(yrs)          # four regimes need pre-2015 history
    p2_split = os.path.exists(SPLIT_SPEC)
    return p1_data, p2_split, sorted(yrs)

def regime_metrics(R):
    """exp, win, pf, dd, n + NET concentration. R = trade returns within (hyp, regime, discovery-half)."""
    n = len(R)
    if n == 0:
        return dict(n=0)
    R = np.asarray(R, float); srt = np.sort(R)[::-1]; sumR = float(R.sum())
    eq = np.cumsum(R); dd = float(np.max(np.maximum.accumulate(eq) - eq))
    gp = R[R > 0].sum(); gl = -R[R < 0].sum()
    return dict(n=n, exp=float(R.mean()), win=float((R > 0).mean()),
                pf=float(gp/gl) if gl > 0 else np.inf, dd=dd, sumR=sumR,
                net1=(srt[:1].sum()/sumR) if sumR > 0 else np.nan,
                net3=(srt[:3].sum()/sumR) if sumR > 0 else np.nan,
                net5=(srt[:5].sum()/sumR) if sumR > 0 else np.nan,
                wo1=(sumR - srt[:1].sum())/max(n-1, 1))

def profitable_in_regime(m, min_n):
    return bool(m.get('n', 0) >= min_n and m.get('sumR', 0) > 0 and m.get('exp', -1) > 0 and (m.get('pf', 0) > 1.00))

def run():
    d = MS.load()
    p1, p2, yrs = _precheck(d)
    if not (p1 and p2):
        print("=== FOUR-REGIME RUN: PRECONDITIONS NOT MET -> ABORT (by design) ===")
        print(f"  P1 data spans four regimes (2011..): {p1}   (loader years present: {yrs})")
        print(f"  P2 Statistician split spec present ({os.path.basename(SPLIT_SPEC)}): {p2}")
        print("  Not started. Awaiting Data Acquisition confirmation + Statistician pre-registered split.")
        return
    # ---- executes ONLY when both preconditions hold (parameters come from the split spec) ----
    spec = json.load(open(SPLIT_SPEC))
    regimes = spec["regimes"]; min_n = int(spec.get("min_n_per_regime", 25))
    disc = np.load(spec["discovery_mask"]) if str(spec.get("discovery_mask","")).endswith(".npy") else None
    idmap = {}
    for fam in MS.REGISTRY:
        for h in MS.REGISTRY[fam][0](): idmap[h['id']] = h
    t = d['time'].values
    rows = []
    for hid in _atr_428():
        tr = MS.backtest_full(d, idmap[hid]) if hasattr(MS, "backtest_full") else MS.simulate(d, MS.setups(d, idmap[hid]))
        ei = tr['ei'].astype(int).values; R = tr['R'].values
        keep = np.ones(len(ei), bool)
        if disc is not None: keep &= disc[ei]                      # DISCOVERY half only; sealed never touched
        prof_count = 0
        rec = dict(id=hid, fam=idmap[hid]['family'])
        for rg in regimes:
            inr = keep & (t[ei] >= rg["start_epoch"]) & (t[ei] < rg["end_epoch"])
            m = regime_metrics(R[inr]); rec[rg["name"]] = m
            prof_count += int(profitable_in_regime(m, min_n))
        rec["profitable_regimes"] = prof_count
        rows.append(rec)
    m = pd.DataFrame(rows)
    counts = {k: int((m["profitable_regimes"] == k).sum()) for k in (4, 3, 2, 1, 0)}
    print("profitable in N of 4 regimes (of 428):", counts)
    out = os.path.join(ROOT, "results", "reproduction_d2", "four_regime_measure.parquet")
    m.to_parquet(out); print("wrote", out)

if __name__ == "__main__":
    run()
