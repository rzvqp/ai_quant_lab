"""ALPHA SCOUT V2 -- the 60-test bounded scan, scored on DEV ONLY (section 17)."""
from __future__ import annotations
import sys, os, json, math
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\scout2"
sys.path.insert(0, AD); os.chdir(AD)
import m5_data

PIP = 0.10
m = m5_data.load_m5()
h = m["high"].to_numpy(float); l = m["low"].to_numpy(float); c = m["close"].to_numpy(float)
o = m["open"].to_numpy(float); n = len(m)
L = lambda k: np.load(os.path.join(OUT, f"{k}.npy"), allow_pickle=True)
A1, A2, A3, A4 = L("A1"), L("A2"), L("A3"), L("A4")
B1, B2, B3, B4 = L("B1"), L("B2"), L("B3"), L("B4")
G1, G2, E1, MFE, MAE = L("G1"), L("G2"), L("E1"), L("MFE"), L("MAE")
day, yrs, hrs, DEV = L("day"), L("yrs"), L("hrs"), L("DEV")
TASYM = (A2 - A3) * 5 / 60.0     # hours: positive = DOWN-100p arrives first

# ---------------- causal state library (branches C,D,E,F,H) ----------------
tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1)))); tr[0] = h[0] - l[0]
atr = pd.Series(tr).rolling(14).mean().to_numpy()
volp = pd.Series(atr).rolling(2000).rank(pct=True).shift(1).to_numpy()      # causal ATR percentile
volp24 = pd.Series(volp).shift(24).to_numpy()
hi48 = pd.Series(h).rolling(48).max().shift(1).to_numpy()
lo48 = pd.Series(l).rolling(48).min().shift(1).to_numpy()
w48 = (hi48 - lo48) / np.maximum(atr, 1e-9)
w48p = pd.Series(w48).rolling(2000).rank(pct=True).shift(1).to_numpy()
loc48 = (c - lo48) / np.maximum(hi48 - lo48, 1e-9)
outer = ((loc48 > 0.8) | (loc48 < 0.2)).astype(float)
near_edge = pd.Series(outer).rolling(48).mean().shift(1).to_numpy()
broke_up = (h > hi48); broke_dn = (l < lo48)
closed_in = (c <= hi48) & (c >= lo48)
fail_up = broke_up & closed_in
fail_dn = broke_dn & closed_in
reentry = (pd.Series(broke_up.astype(float)).rolling(12).max().shift(1).to_numpy() > 0.5) & closed_in
ema20 = pd.Series(c).ewm(span=20 * 12, adjust=True).mean().to_numpy()
ema50 = pd.Series(c).ewm(span=50 * 12, adjust=True).mean().to_numpy()
trend_up = ema20 > ema50
r24 = (c - pd.Series(c).shift(24).to_numpy())
blk = lambda k: np.sign(pd.Series(c).shift(24 * k).to_numpy() - pd.Series(c).shift(24 * (k + 1)).to_numpy())
b0, b1, b2 = blk(0), blk(1), blk(2)
volq = pd.Series(volp).shift(0).to_numpy()
q0 = pd.Series(volp).to_numpy(); q1 = pd.Series(volp).shift(24).to_numpy(); q2 = pd.Series(volp).shift(48).to_numpy()

# causal H1 context for branch H (nominal-close contract, from the governed helper)
try:
    h1 = m5_data.htf_at_m5(m, "H1")
    h1atr = h1["h1_atr"].to_numpy(); h1c = h1["h1_close"].to_numpy()
    h1e20 = h1["h1_ema20"].to_numpy(); h1e50 = h1["h1_ema50"].to_numpy()
    h1volp = pd.Series(h1atr).rolling(2000).rank(pct=True).shift(1).to_numpy()
    h1_trend = h1e20 > h1e50
    H_OK = True
except Exception as e:
    print("  H1 context unavailable:", e); H_OK = False

STATES = {
    # ---- BRANCH C: volatility state TRANSITIONS ----
    "C1 low->expansion (q<.2 -> q>.5)":      (volp24 < 0.2) & (volp > 0.5),
    "C2 extreme->persist (q>.9 -> q>.9)":    (volp24 > 0.9) & (volp > 0.9),
    "C3 extreme->normalise (q>.9 -> q<.6)":  (volp24 > 0.9) & (volp < 0.6),
    "C4 mid->extreme (.4-.6 -> q>.9)":       (volp24 > 0.4) & (volp24 < 0.6) & (volp > 0.9),
    "C5 sustained low (q<.2 both)":          (volp24 < 0.2) & (volp < 0.2),
    # ---- BRANCH D: range / compression STATE (not range-location extremes) ----
    "D1 range compression (w48 pct<.2)":     w48p < 0.2,
    "D2 range expansion (w48 pct>.8)":       w48p > 0.8,
    "D3 pinned to edges (>60% of 48 bars)":  near_edge > 0.6,
    "D4 failed expansion UP (broke, closed in)": fail_up,
    "D5 re-entry after 48-bar break":        reentry,
    # ---- BRANCH E: sequential transitions (3 x 24-bar blocks) ----
    "E1 seq down,down,up":                   (b2 < 0) & (b1 < 0) & (b0 > 0),
    "E2 seq up,up,up (persistence)":         (b2 > 0) & (b1 > 0) & (b0 > 0),
    "E3 seq quiet,quiet,expand":             (q2 < 0.3) & (q1 < 0.3) & (q0 > 0.6),
    "E4 seq expand,quiet,expand":            (q2 > 0.7) & (q1 < 0.4) & (q0 > 0.7),
    # ---- BRANCH F: prospective regime conditionality ----
    "F1 compression x trend-up":             (w48p < 0.2) & trend_up,
    "F2 compression x trend-down":           (w48p < 0.2) & (~trend_up),
    "F3 low->expansion x trend-down":        (volp24 < 0.2) & (volp > 0.5) & (~trend_up),
}
if H_OK:
    STATES.update({
        "H1 M5 fail-up x H1 vol-high":       fail_up & (h1volp > 0.7),
        "H2 M5 compression x H1 trend-up":   (w48p < 0.2) & h1_trend,
        "H3 M5 re-entry x H1 trend-down":    reentry & (~h1_trend),
    })

TARGETS = {"A1 speed to +-100p (h)": A1 * 5 / 60.0,
           "TASYM t_up-t_dn (h)": TASYM,
           "B2 P(+100 before -100)": B2,
           "G1 P(MFE>=300p)": G1}


def cl(mask, y, sub):
    ok = mask & np.isfinite(y) & sub
    bm = (~mask) & np.isfinite(y) & sub
    if ok.sum() < 200 or bm.sum() < 200: return None
    yy = y[ok]; dd = day[ok]; mu = yy.mean(); base = y[bm].mean()
    g = pd.DataFrame({"d": dd, "y": yy}).groupby("d")["y"].agg(["sum", "count"])
    G = len(g); N = len(yy)
    resid = g["sum"].to_numpy() - g["count"].to_numpy() * mu
    se = math.sqrt(max((resid ** 2).sum() / N ** 2 * (G / max(G - 1, 1)), 1e-18))
    return dict(N=int(N), days=int(G), val=float(mu), base=float(base), lift=float(mu - base),
                se=float(se), z=float((mu - base) / se if se > 0 else 0.0))


print("=" * 112)
print("  SCOUT V2 -- 60-TEST BOUNDED SCAN, SCORED ON DEV ONLY (<= 2024-06-30)")
print("=" * 112)
print(f"  {'state':44}{'target':26}{'N':>8}{'days':>6}{'cond':>10}{'base':>10}{'lift':>10}{'z':>8}")
rows = []
for sn, sm in STATES.items():
    for tn, ty in TARGETS.items():
        r = cl(sm, ty, DEV)
        if r is None: continue
        rows.append(dict(branch=sn.split()[0][0], state=sn, target=tn, **r))
        print(f"  {sn:44}{tn:26}{r['N']:8d}{r['days']:6d}{r['val']:10.4f}{r['base']:10.4f}{r['lift']:+10.4f}{r['z']:+8.2f}")

df = pd.DataFrame(rows)
print(f"\n  TOTAL TESTS SCORED ON DEV: {len(df)}   (declared budget 60)")
df["absz"] = df["z"].abs()
print("\n  TOP 12 BY |z| (DEV only):")
print(df.sort_values("absz", ascending=False).head(12)[
    ["state", "target", "N", "days", "val", "base", "lift", "z"]].to_string(index=False))
df.to_json(os.path.join(OUT, "v2_dev_scan.json"), orient="records")
np.save(os.path.join(OUT, "volp.npy"), volp); np.save(os.path.join(OUT, "w48p.npy"), w48p)
np.save(os.path.join(OUT, "near_edge.npy"), near_edge); np.save(os.path.join(OUT, "fail_up.npy"), fail_up)
np.save(os.path.join(OUT, "reentry.npy"), reentry); np.save(os.path.join(OUT, "trend_up.npy"), trend_up)
np.save(os.path.join(OUT, "volp24.npy"), volp24); np.save(os.path.join(OUT, "TASYM.npy"), TASYM)
if H_OK:
    np.save(os.path.join(OUT, "h1volp.npy"), h1volp); np.save(os.path.join(OUT, "h1_trend.npy"), h1_trend)
print("\n  persisted DEV scan")
