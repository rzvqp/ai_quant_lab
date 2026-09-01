"""ALPHA SCOUT V2 -- top-5 FROZEN on DEV, then OOS inspected ONCE + robustness/controls."""
from __future__ import annotations
import sys, os, json, math
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\scout2"
sys.path.insert(0, AD); os.chdir(AD)

L = lambda k: np.load(os.path.join(OUT, f"{k}.npy"), allow_pickle=True)
A1 = L("A1") * 5 / 60.0
B2, G1, MFE = L("B2"), L("G1"), L("MFE")
day, yrs, hrs, DEV = L("day"), L("yrs"), L("hrs"), L("DEV")
volp, volp24, w48p = L("volp"), L("volp24"), L("w48p")
n = len(A1)

FROZEN = {
    "V2-1 range EXPANDED (w48/ATR pct>.8)":   w48p > 0.8,
    "V2-2 sustained LOW vol (q<.2 x2)":       (volp24 < 0.2) & (volp < 0.2),
    "V2-3 low->EXPANSION (q<.2 -> q>.5)":     (volp24 < 0.2) & (volp > 0.5),
    "V2-4 range COILED (w48/ATR pct<.2)":     w48p < 0.2,
    "V2-5 extreme->NORMALISE (q>.9 -> q<.6)": (volp24 > 0.9) & (volp < 0.6),
}
print("=" * 108)
print("  TOP 5 FROZEN ON DEV (section 17) -- conditions fixed before OOS is looked at")
print("=" * 108)
for k in FROZEN: print(f"    {k}")


def cl(mask, y, sub):
    ok = mask & np.isfinite(y) & sub; bm = (~mask) & np.isfinite(y) & sub
    if ok.sum() < 150 or bm.sum() < 150: return None
    yy = y[ok]; mu = yy.mean(); base = y[bm].mean()
    g = pd.DataFrame({"d": day[ok], "y": yy}).groupby("d")["y"].agg(["sum", "count"])
    G = len(g); N = len(yy)
    resid = g["sum"].to_numpy() - g["count"].to_numpy() * mu
    se = math.sqrt(max((resid ** 2).sum() / N ** 2 * (G / max(G - 1, 1)), 1e-18))
    return dict(N=int(N), days=int(G), val=float(mu), base=float(base), lift=float(mu - base),
                z=float((mu - base) / se if se > 0 else 0.0))


ALL = np.ones(n, bool)
print("\n" + "=" * 108)
print("  DEV -> OOS (inspected once)   target = A1 hours to the first +-100p touch")
print("=" * 108)
print(f"  {'phenomenon':42}{'DEV lift(h)':>13}{'DEV z':>8}{'OOS lift(h)':>13}{'OOS z':>8}{'sign':>7}")
res = {}
for k, msk in FROZEN.items():
    d = cl(msk, A1, DEV); oo = cl(msk, A1, ~DEV)
    res[k] = dict(dev=d, oos=oo)
    ok = "SAME" if d and oo and np.sign(d["lift"]) == np.sign(oo["lift"]) else "FLIP"
    print(f"  {k:42}{d['lift']:+13.3f}{d['z']:+8.2f}{oo['lift']:+13.3f}{oo['z']:+8.2f}{ok:>7}")

print("\n" + "=" * 108)
print("  MATCHED CONTROL (section 14) -- is this just the excluded London effect in disguise?")
print("=" * 108)
print("  Session is used ONLY as a control here. Effect re-measured WITHIN each session bucket.")
print(f"  {'phenomenon':42}{'AS':>10}{'LN':>10}{'NY':>10}{'LT':>10}   all-session sign agreement")
for k, msk in FROZEN.items():
    line = f"  {k:42}"; signs = []
    for s, lo, hi in (("AS", 0, 8), ("LN", 8, 13), ("NY", 13, 20), ("LT", 20, 24)):
        sub = (hrs >= lo) & (hrs < hi)
        r = cl(msk, A1, sub)
        line += f"{r['lift']:+10.3f}" if r else f"{'--':>10}"
        if r: signs.append(np.sign(r["lift"]))
    agree = len(set(signs)) == 1
    print(line + f"   {'4/4 AGREE' if agree else 'mixed'}")

print("\n" + "=" * 108)
print("  OVERLAP + YEAR + OUTLIER ROBUSTNESS (section 18)")
print("=" * 108)
keep = np.zeros(n, bool); last = -10 ** 9
for i in range(n):
    if i - last >= 288: keep[i] = True; last = i
for k, msk in FROZEN.items():
    r_all = cl(msk, A1, ALL); r_no = cl(msk, A1, keep)
    yl = {}
    for y in sorted(set(yrs)):
        r = cl(msk, A1, yrs == y)
        if r: yl[int(y)] = round(r["lift"], 2)
    same = sum(1 for v in yl.values() if np.sign(v) == np.sign(r_all["lift"]))
    # outlier robustness: winsorise A1 at the 99th pct
    cap = np.nanpercentile(A1, 99)
    r_w = cl(msk, np.minimum(A1, cap), ALL)
    print(f"  {k}")
    print(f"     pooled lift {r_all['lift']:+.3f}h (z {r_all['z']:+.2f}) | non-overlap N={r_no['N'] if r_no else 0} "
          f"lift {r_no['lift']:+.3f}h (z {r_no['z']:+.2f})" if r_no else
          f"     pooled lift {r_all['lift']:+.3f}h (z {r_all['z']:+.2f}) | non-overlap N too small")
    print(f"     winsorised(99pct) lift {r_w['lift']:+.3f}h | per-year {yl} -> {same}/{len(yl)} same sign")

print("\n" + "=" * 108)
print("  DIRECTIONAL / SKEW TARGETS ON THE SAME FROZEN STATES (are they informative about anything else?)")
print("=" * 108)
print(f"  {'phenomenon':42}{'B2 lift':>10}{'z':>7}{'G1 lift':>10}{'z':>7}{'medMFE':>9}{'base':>8}")
for k, msk in FROZEN.items():
    rb = cl(msk, B2, ALL); rg = cl(msk, G1, ALL)
    print(f"  {k:42}{rb['lift']:+10.4f}{rb['z']:+7.2f}{rg['lift']:+10.4f}{rg['z']:+7.2f}"
          f"{np.nanmedian(MFE[msk]):9.0f}{np.nanmedian(MFE[~msk]):8.0f}")
json.dump({k: {"dev": v["dev"], "oos": v["oos"]} for k, v in res.items()},
          open(os.path.join(OUT, "v2_oos.json"), "w"), indent=1, default=str)
