"""STAT-OBR-BULL-1 run 2 -- eras/years, dose-response, controls (incl. STOP-MATCHED), outliers,
sessions, threshold surface, cost stress, M5 inheritance check. Both fill semantics throughout."""
from __future__ import annotations
import sys, os, json, math
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\obr"
sys.path.insert(0, AD); os.chdir(AD)
import ob_core as OB, htf_core as HC
from ob_contrast import limit_fill
from tsm_core import independent_episodes

m, H1, H4, P = OB.build()
atr = P["atr"]; hi100 = P["hi100"]; hr = m["dt"].dt.hour.values; yr = m["dt"].dt.year.values
h = P["h"]; l = P["l"]; c = P["c"]; n = P["n"]


def fill_frozen(e, lvl):
    return limit_fill(P, e, lvl, 1, e["i"])


def fill_causal(e, lvl):
    end = min(e["i"] + OB.RETEST_WIN, n - 1)
    for kk in range(e["i"] + 1, end + 1):
        if l[kk] <= lvl: return kk
        if c[kk] < e["blo"]: return None
    return None


def collect(disp_min=1.5, tgtR=2.0, causal=False, level_fn=None, stop_fn=None, sess_filter=True):
    ev = OB.detect_obs(P, disp_min, "bull"); rows = []
    for e in ev:
        i = e["i"]; a = atr[i]
        lvl = e["bhi"] if level_fn is None else level_fn(e, a)
        stop = (e["blo"] - OB.FLOOR_ATR * a) if stop_fn is None else stop_fn(e, a, lvl)
        if abs(lvl - stop) < 0.5 * a: stop = lvl - 0.5 * a
        k = fill_causal(e, lvl) if causal else fill_frozen(e, lvl)
        if k is None: continue
        o = OB.retest_outcome(P, lvl, stop, 1, k, tgtR, resolve_from=k)
        if o is None: continue
        H_ = hr[k]; sess = "AS" if H_ < 8 else ("LN" if H_ < 13 else ("NY" if H_ < 20 else "LT"))
        if sess_filter and sess not in ("LN", "NY"): continue
        y = int(yr[k]); era = "D" if y <= 2018 else ("C" if y <= 2022 else "O")
        rows.append(dict(net=o["net_R"], g=o["gross_R"], risk=o["risk_px"], disp=e["disp"],
                         sess=sess, era=era, k=k, year=y, i=i))
    return rows


def stat(rows):
    if len(rows) < 5: return dict(N=len(rows), net=np.nan)
    net = np.array([r["net"] for r in rows]); g = np.array([r["g"] for r in rows])
    k = np.array([r["k"] for r in rows]); eq = np.cumsum(net)
    return dict(N=len(net), ie=len(independent_episodes(k, H=OB.RETEST_WIN)), net=float(net.mean()),
                WR=float((g > 0).mean()), PF=float(g[g > 0].sum() / (abs(g[g < 0].sum()) + 1e-9)),
                maxDD=float((eq - np.maximum.accumulate(eq)).min()))


F = collect(); C = collect(causal=True)
print("=" * 100)
print("  SECTION 6/7 -- ERAS, YEARS, DEV/OOS   (F = frozen fill, C = causal fill)")
print("=" * 100)
for nm, R in (("FROZEN", F), ("CAUSAL", C)):
    net = np.array([r["net"] for r in R]); era = np.array([r["era"] for r in R]); yy = np.array([r["year"] for r in R])
    e = {x: (round(float(net[era == x].mean()), 3), int((era == x).sum())) for x in ("D", "C", "O")}
    dev = net[yy <= 2018]; oos = net[yy >= 2019]
    ypos = sum(1 for y in sorted(set(yy)) if net[yy == y].mean() > 0)
    tot = net.sum()
    ysum = {y: float(net[yy == y].sum()) for y in sorted(set(yy))}
    best = max(ysum, key=ysum.get); top3 = sum(sorted(ysum.values())[-3:])
    print(f"  {nm}: era D/C/O = {e}")
    print(f"        DEV(<=2018) {dev.mean():+.4f} (n{len(dev)})   OOS(2019+) {oos.mean():+.4f} (n{len(oos)})")
    print(f"        years positive {ypos}/{len(set(yy))}   best year {best} = {ysum[best]/tot:.1%} of total   top-3 years = {top3/tot:.1%}")
    print(f"        per-year: { {int(y): round(float(net[yy==y].mean()),3) for y in sorted(set(yy))} }")

print("\n" + "=" * 100)
print("  SECTION 8 -- DISPLACEMENT DOSE-RESPONSE")
print("=" * 100)
print(f"  {'disp>=':>8}{'FROZEN N':>10}{'FROZEN net':>12}{'CAUSAL N':>10}{'CAUSAL net':>12}   Alpha claim")
alpha_dr = {1.0: 0.099, 1.25: 0.112, 1.5: 0.154, 1.75: 0.184, 2.0: 0.226, 2.5: 0.239}
for d in (1.0, 1.25, 1.5, 1.75, 2.0, 2.5):
    a = stat(collect(disp_min=d)); b = stat(collect(disp_min=d, causal=True))
    print(f"  {d:8.2f}{a['N']:10d}{a['net']:+12.4f}{b['N']:10d}{b['net']:+12.4f}   {alpha_dr[d]:+.3f}")

print("\n" + "=" * 100)
print("  SECTION 9 -- MATCHED CONTROLS, INCLUDING THE STOP-MATCHED CONTROL (major gate)")
print("=" * 100)
print("  All controls use the SAME events, SAME fill semantics, SAME target, SAME session filter.")
for nm, causal in (("FROZEN", False), ("CAUSAL", True)):
    ob = stat(collect(causal=causal))
    # CONTROL_C: generic pullback 1 ATR below the BOS close, stop 1 ATR lower (Alpha's control)
    cc = stat(collect(causal=causal, level_fn=lambda e, a: e["bos_close"] - 1.0 * a,
                      stop_fn=lambda e, a, lvl: lvl - 1.0 * a))
    # CONTROL_SHIFT: height-matched non-OB level, shifted down by one block height
    ht = lambda e: (e["bhi"] - e["blo"])
    cs = stat(collect(causal=causal, level_fn=lambda e, a: e["bhi"] - ht(e),
                      stop_fn=lambda e, a, lvl: lvl - ht(e) - OB.FLOOR_ATR * a))
    # *** STOP-MATCHED CONTROL: same level as CONTROL_C but risk forced equal to the OB trade's risk ***
    def _sm_stop(e, a, lvl):
        ob_risk = abs(e["bhi"] - (e["blo"] - OB.FLOOR_ATR * a))
        if ob_risk < 0.5 * a: ob_risk = 0.5 * a
        return lvl - ob_risk
    sm = stat(collect(causal=causal, level_fn=lambda e, a: e["bos_close"] - 1.0 * a, stop_fn=_sm_stop))
    print(f"\n  {nm} fill semantics:")
    print(f"    OB level (OBR-BULL-1)          N={ob['N']:5d} net={ob['net']:+.4f}")
    print(f"    CONTROL_C generic pullback     N={cc['N']:5d} net={cc['net']:+.4f}   OB incremental {ob['net']-cc['net']:+.4f}")
    print(f"    CONTROL_SHIFT height-matched   N={cs['N']:5d} net={cs['net']:+.4f}   OB incremental {ob['net']-cs['net']:+.4f}")
    print(f"    CONTROL_STOPMATCHED (risk=OB)  N={sm['N']:5d} net={sm['net']:+.4f}   OB incremental {ob['net']-sm['net']:+.4f}")

print("\n" + "=" * 100)
print("  SECTION 10/11/12 -- OUTLIERS, SESSIONS, THRESHOLD SURFACE, COST STRESS")
print("=" * 100)
for nm, R in (("FROZEN", F), ("CAUSAL", C)):
    net = np.array([r["net"] for r in R]); nn = len(net); s = np.sort(net)
    k1 = max(1, int(np.ceil(nn * 0.01)))
    kk = np.array([r["k"] for r in R])
    ie = len(independent_episodes(kk, H=OB.RETEST_WIN))
    # clustered SE by episode
    ep = np.zeros(nn, int); order = np.argsort(kk); cur = 0; last = -10 ** 9
    for pos in order:
        if kk[pos] - last > OB.RETEST_WIN: cur += 1
        ep[pos] = cur; last = kk[pos]
    G = len(set(ep)); mu = net.mean()
    sums = np.array([net[ep == e].sum() for e in sorted(set(ep))]); cnts = np.array([(ep == e).sum() for e in sorted(set(ep))])
    resid = sums - cnts * mu
    se = math.sqrt(max((resid ** 2).sum() / nn ** 2 * (G / max(G - 1, 1)), 1e-18))
    print(f"  {nm}: N={nn} episodes={ie} net={mu:+.4f}  clustered SE={se:.4f}  95% CI [{mu-1.96*se:+.4f}, {mu+1.96*se:+.4f}]")
    print(f"        drop-best-1% ({k1}) -> {s[:nn-k1].mean():+.4f}   drop-best-trade -> {s[:-1].mean():+.4f}")
    for ses in ("LN", "NY"):
        ss = [r for r in R if r["sess"] == ses]; print(f"        {ses}: N={len(ss)} net={np.mean([r['net'] for r in ss]):+.4f}", end="")
    print()
    for extra in (0.0, 0.05, 0.10, 0.15, 0.20):
        print(f"        +{extra:.2f}R stress -> {mu-extra:+.4f}", end="")
    print()
    print(f"        expectancy crosses zero at +{mu:.4f}R additional cost")
