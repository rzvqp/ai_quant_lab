"""ALPHA SCOUT V1 -- run 4: baseline path asymmetry vs the driftless benchmark (section 12 evidence)."""
from __future__ import annotations
import sys, os, math
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\scout"
sys.path.insert(0, AD); os.chdir(AD)
import m5_data

PIP = 0.10; H = 288
m = m5_data.load_m5()
h = m["high"].to_numpy(float); l = m["low"].to_numpy(float); c = m["close"].to_numpy(float)
n = len(m)
t = pd.to_datetime(m["time"].to_numpy(), unit="s", utc=True)
day = pd.Series(t).dt.floor("D").astype("int64").to_numpy()
yrs = t.year.to_numpy()
sess = np.load(os.path.join(OUT, "sess.npy"), allow_pickle=True)


def race(up_p, dn_p):
    U = c + up_p * PIP; D = c - dn_p * PIP
    hu = np.full(n, np.inf); hd = np.full(n, np.inf)
    for j in range(1, H + 1):
        hj = np.concatenate([h[j:], np.full(j, np.nan)])
        lj = np.concatenate([l[j:], np.full(j, np.nan)])
        hu = np.where((hj >= U) & np.isinf(hu), j, hu)
        hd = np.where((lj <= D) & np.isinf(hd), j, hd)
    out = np.where(hu < hd, 1.0, np.where(hd <= hu, 0.0, np.nan))
    return np.where(np.isinf(hu) & np.isinf(hd), np.nan, out)


def se_day(y, mask=None):
    ok = np.isfinite(y) if mask is None else (mask & np.isfinite(y))
    yy = y[ok]; dd = day[ok]; mu = yy.mean()
    g = pd.DataFrame({"d": dd, "y": yy}).groupby("d")["y"].agg(["sum", "count"])
    resid = g["sum"].to_numpy() - g["count"].to_numpy() * mu
    G = len(g); N = len(yy)
    return mu, math.sqrt(max((resid ** 2).sum() / N ** 2 * (G / max(G - 1, 1)), 1e-18)), N


print("=" * 100)
print("  BASELINE PATH ASYMMETRY vs the DRIFTLESS (martingale) BENCHMARK")
print("=" * 100)
print("  For a driftless random walk, P(+U before -D) = D / (U + D).")
print("  Gold roughly doubled over this 5-year native-M5 window, so naive intuition says P should be ABOVE it.\n")
print(f"  {'barriers (U,D)':>18}{'observed P':>13}{'driftless':>12}{'gap':>10}{'z':>9}{'N':>10}")
rows = []
for U, D in ((100, 80), (200, 100), (300, 150), (100, 100), (200, 200), (300, 300)):
    y = race(U, D)
    mu, se, N = se_day(y)
    bench = D / (U + D)
    z = (mu - bench) / se
    rows.append((U, D, mu, bench, mu - bench, z, N))
    print(f"  {f'(+{U}, -{D})':>18}{mu:13.4f}{bench:12.4f}{mu-bench:+10.4f}{z:+9.2f}{N:10d}")

print("\n  Buy-and-hold check over the same window:")
print(f"    first close {c[0]:.2f} -> last close {c[-1]:.2f}  = {100*(c[-1]/c[0]-1):+.1f}% over "
      f"{(t.max()-t.min()).days/365.25:.1f} years")

print("\n  Same asymmetry, per session (barriers +200/-200, a pure symmetric race):")
y = race(200, 200)
for s in ("AS", "LN", "NY", "LT"):
    mu, se, N = se_day(y, sess == s)
    print(f"    {s}: P(up first) = {mu:.4f}  (symmetric benchmark 0.5000)  gap {mu-0.5:+.4f}  z {(mu-0.5)/se:+.2f}  N={N}")

print("\n  Per year (+200/-200):")
for yy in sorted(set(yrs)):
    mu, se, N = se_day(y, yrs == yy)
    print(f"    {yy}: P(up first) = {mu:.4f}  gap {mu-0.5:+.4f}  z {(mu-0.5)/se:+.2f}  N={N}")
