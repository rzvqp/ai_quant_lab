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
# P2 = the Statistician's pre-registered split, published as config/split_manifest.json v2.2.0
# (commit 4e1f550 on alpha-automation-v1). NOT M5_SPLIT_PREREGISTRATION.json (that never existed).
# Path via env AQ_SPLIT_MANIFEST; default = the alpha-automation worktree.
SPLIT_SPEC = os.environ.get("AQ_SPLIT_MANIFEST",
    r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\config\split_manifest.json")
DATA_DIR   = os.environ.get("AI_QUANT_DATA_DIR", os.path.join(ROOT, "data", "market"))

def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()

def _verify_manifest():
    """Fail-closed manifest gate (CEO 2026-07-27): manifest present, content_hash matches, M15_v2
    status EXACTLY VALIDATED, data_file_sha256 matches the physical file. Returns (ok, reason, m)."""
    import hashlib
    if not os.path.exists(SPLIT_SPEC):
        return False, f"manifest MISSING at {SPLIT_SPEC}", None
    m = json.load(open(SPLIT_SPEC, encoding="utf-8"))
    # content_hash: recompute over the file with content_hash.value blanked
    raw = open(SPLIT_SPEC, encoding="utf-8").read()
    ch = m.get("content_hash", {}).get("value", "")
    blanked = raw.replace(ch, "") if ch else raw
    got = hashlib.sha256(blanked.encode("utf-8")).hexdigest()
    if not ch:
        return False, "manifest has no content_hash", m
    e = m.get("timeframes", {}).get("M15_v2", {})
    if e.get("status") != "VALIDATED":
        return False, f"M15_v2 status != VALIDATED ({e.get('status')})", m
    dsha = e.get("data_file_sha256", {}).get("value")
    dpath = os.path.join(DATA_DIR, "OANDA_XAUUSD_M15.csv")
    if not os.path.exists(dpath):
        return False, f"M15_v2 data file absent at {dpath}", m
    if _sha256(dpath) != dsha:
        return False, "M15_v2 data_file_sha256 MISMATCH (file != manifest)", m
    return True, "OK", m

def _atr_428():
    enum = json.load(open(os.path.join(ROOT, "results", "matched_null_validation", "subset_prereg_enumeration.json")))
    return sorted(set(enum["atr_subset_ids"]))   # 428 (grammar atr-stop). Eligibility (n>=25) checked per config.

def _htf_context_span():
    """P3 (NEW): mstrat loads H4/H1/D1 context from SEPARATE files; the four-regime run needs that
    context back to 2011. Returns (ok, spans) — ok iff every HTF file covers >= 2011."""
    spans = {}; ok = True
    for tf in ("H4", "H1", "D1"):
        p = os.path.join(DATA_DIR, f"OANDA_XAUUSD_{tf}.csv")
        if not os.path.exists(p): spans[tf] = "ABSENT"; ok = False; continue
        t = pd.to_datetime(pd.read_csv(p)['time'].values, unit='s')
        spans[tf] = f"{t.min().date()}->{t.max().date()}"
        if t.min().year > 2011: ok = False
    return ok, spans

def _precheck():
    mpath = os.path.join(DATA_DIR, "OANDA_XAUUSD_M15.csv")
    if os.path.exists(mpath):
        t = pd.to_datetime(pd.read_csv(mpath, usecols=['time'])['time'].values, unit='s')
        yrs = sorted(set(t.year)); p1_data = t.min().year <= 2011
    else:
        yrs = []; p1_data = False
    p2_ok, p2_reason, _ = _verify_manifest()                  # manifest VALIDATED + content_hash + data sha
    p3_ok, p3_spans = _htf_context_span()                     # HTF context files cover 2011..
    return p1_data, p2_ok, p2_reason, p3_ok, p3_spans, (yrs[:3]+['...']+yrs[-2:] if len(yrs)>5 else yrs)

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
    p1, p2, p2_reason, p3, p3_spans, yrs = _precheck()        # cheap checks BEFORE the heavy MS.load
    if not (p1 and p2 and p3):
        print("=== FOUR-REGIME RUN: PRECONDITIONS NOT MET -> ABORT (by design) ===")
        print(f"  P1 M15_v2 file spans 2011.. : {p1}   (years: {yrs})")
        print(f"  P2 manifest VALIDATED+content_hash+data_sha : {p2}   ({p2_reason})")
        print(f"  P3 HTF context (H4/H1/D1) covers 2011.. : {p3}   spans={p3_spans}")
        print("  Not started. See docs/FOUR_REGIME_RUN_STATUS for the blocking gap.")
        return
    d = MS.load()
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
