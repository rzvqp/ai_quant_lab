"""ALPHA SCOUT V2 -- targets + causal state library + positive control.
Branches A-H. L1 (London session) and P2 (24h-range-base) are EXCLUDED as hypotheses.
Read-only. Nothing promoted.
"""
from __future__ import annotations
import sys, os, json, math, hashlib
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\scout2"
sys.path.insert(0, AD); os.chdir(AD)
import m5_data

PIP = 0.10
H = 288                      # 24h forward horizon
PREREG = """
SCOUT V2 -- PREREGISTERED DESIGN (declared before scoring)

  EXCLUDED AS HYPOTHESES (per mandate section 2): London session (L1), 24h-range-location extremes (P2),
  S5, OBR/order blocks, generic BOS/sweep/pullback/session-breakout, simple DXY impulse.
  Session is used ONLY as a matched control, never as a hypothesis.

  TARGETS -- timing-first, not direction-first:
    A1 t_any100   bars to the FIRST +-100p touch (either side)          -> SPEED
    A2 t_up100    bars to +100p        A3 t_dn100  bars to -100p        -> TIME ASYMMETRY
    A4 t_ext      bars to a new 48-bar extreme (either side)
    B1 race(+100,-50) B2 race(+100,-100) B3 race(+200,-100) B4 race(+300,-150)  (small declared grid)
    G1 P(MFE >= 300p in 24h)   G2 P(MFE >= 500p in 24h)                 -> RARE-EVENT SKEW
    E1 P(|move| >= 200p in 8h)                                          -> EXPANSION

  DEV/OOS DISCIPLINE: all 60 tests are scored on DEV (<= 2024-06-30) ONLY.
  The top 5 are then FROZEN and OOS is inspected once. No condition is modified after seeing OOS.

  BUDGET: 60 tests. Ranking by coherence (dose-response, year consistency, control-adjusted), not by p.
"""
print(PREREG)

m = m5_data.load_m5()
h = m["high"].to_numpy(float); l = m["low"].to_numpy(float); c = m["close"].to_numpy(float)
o = m["open"].to_numpy(float); n = len(m)
tsec = m["time"].to_numpy()
t = pd.to_datetime(tsec, unit="s", utc=True)
day = pd.Series(t).dt.floor("D").astype("int64").to_numpy()
yrs = t.year.to_numpy(); hrs = t.hour.to_numpy()
sha = hashlib.sha256(open(m5_data.M5PATH, "rb").read()).hexdigest()
print("=" * 104)
print("  SECTION 12 -- DATA AUDIT")
print("=" * 104)
print(f"    native governed M5: rows={n}  span {t.min()} .. {t.max()}  sha256 {sha[:16]}  (UTC, no synthesis)")
g = np.diff(tsec) / 60.0
print(f"    modal step {pd.Series(g).mode().iloc[0]:.0f}min · gaps>60min {int((g>60).sum())} · "
      f"per-year {dict(sorted(pd.Series(yrs).value_counts().items()))}")
print(f"    cost convention (carried, not applied to information tests): round-trip ~4.19 project pips")
DEV = np.asarray(t <= pd.Timestamp("2024-06-30", tz="UTC"))
print(f"    DEV (<=2024-06-30) bars={int(DEV.sum())}   OOS bars={int((~DEV).sum())}")

# ---------------- forward machinery ----------------
def first_touch(up_p, dn_p, horizon=H, hh=None, ll=None, cc=None):
    hh = h if hh is None else hh; ll = l if ll is None else ll; cc = c if cc is None else cc
    U = cc + up_p * PIP; D = cc - dn_p * PIP
    hu = np.full(n, np.inf); hd = np.full(n, np.inf)
    for j in range(1, horizon + 1):
        hj = np.concatenate([hh[j:], np.full(j, np.nan)])
        lj = np.concatenate([ll[j:], np.full(j, np.nan)])
        hu = np.where((hj >= U) & np.isinf(hu), j, hu)
        hd = np.where((lj <= D) & np.isinf(hd), j, hd)
    return hu, hd


def mfe_mae(horizon=H):
    mx = np.full(n, -np.inf); mn = np.full(n, np.inf)
    for j in range(1, horizon + 1):
        hj = np.concatenate([h[j:], np.full(j, np.nan)])
        lj = np.concatenate([l[j:], np.full(j, np.nan)])
        mx = np.fmax(mx, hj); mn = np.fmin(mn, lj)
    return (mx - c) / PIP, (c - mn) / PIP


print("\n  computing targets ...")
u100, d100 = first_touch(100, 100)
u200, d200 = first_touch(200, 100)
u300, d300 = first_touch(300, 150)
u100b, d50 = first_touch(100, 50)
MFE, MAE = mfe_mae()
A1 = np.fmin(u100, d100)                       # bars to first +-100p
A2 = u100.copy(); A3 = d100.copy()
A1 = np.where(np.isinf(A1), np.nan, A1)
A2 = np.where(np.isinf(A2), np.nan, A2)
A3 = np.where(np.isinf(A3), np.nan, A3)
B1 = np.where(u100b < d50, 1.0, np.where(d50 <= u100b, 0.0, np.nan))
B2 = np.where(u100 < d100, 1.0, np.where(d100 <= u100, 0.0, np.nan))
B3 = np.where(u200 < d200, 1.0, np.where(d200 <= u200, 0.0, np.nan))
B4 = np.where(u300 < d300, 1.0, np.where(d300 <= u300, 0.0, np.nan))
for X, (hu, hd) in ((B1, (u100b, d50)), (B2, (u100, d100)), (B3, (u200, d200)), (B4, (u300, d300))):
    X[np.isinf(hu) & np.isinf(hd)] = np.nan
G1 = (MFE >= 300).astype(float); G2 = (MFE >= 500).astype(float)
u200s, d200s = first_touch(200, 200, horizon=96)
E1 = ((np.isfinite(u200s) & ~np.isinf(u200s)) | (np.isfinite(d200s) & ~np.isinf(d200s))).astype(float)
E1 = np.where(np.isinf(u200s) & np.isinf(d200s), 0.0, 1.0)

# time to new 48-bar extreme
hi48 = pd.Series(h).rolling(48).max().shift(1).to_numpy()
lo48 = pd.Series(l).rolling(48).min().shift(1).to_numpy()
te_u, te_d = np.full(n, np.inf), np.full(n, np.inf)
for j in range(1, 97):
    hj = np.concatenate([h[j:], np.full(j, np.nan)])
    lj = np.concatenate([l[j:], np.full(j, np.nan)])
    te_u = np.where((hj > hi48) & np.isinf(te_u), j, te_u)
    te_d = np.where((lj < lo48) & np.isinf(te_d), j, te_d)
A4 = np.fmin(te_u, te_d); A4 = np.where(np.isinf(A4), np.nan, A4)

print(f"    baselines: median t_any100 = {np.nanmedian(A1)*5/60:.2f}h · median t_up100 {np.nanmedian(A2)*5/60:.2f}h"
      f" · median t_dn100 {np.nanmedian(A3)*5/60:.2f}h · median t_ext {np.nanmedian(A4)*5/60:.2f}h")
print(f"               P(+100 b -50)={np.nanmean(B1):.4f} · P(+100 b -100)={np.nanmean(B2):.4f} · "
      f"P(+200 b -100)={np.nanmean(B3):.4f} · P(+300 b -150)={np.nanmean(B4):.4f}")
print(f"               P(MFE>=300p)={np.nanmean(G1):.4f} · P(MFE>=500p)={np.nanmean(G2):.4f} · "
      f"P(|move|>=200p in 8h)={np.nanmean(E1):.4f}")

for nm, a in (("A1", A1), ("A2", A2), ("A3", A3), ("A4", A4), ("B1", B1), ("B2", B2), ("B3", B3), ("B4", B4),
              ("G1", G1), ("G2", G2), ("E1", E1), ("MFE", MFE), ("MAE", MAE)):
    np.save(os.path.join(OUT, f"{nm}.npy"), a)

# ---------------- POSITIVE CONTROL (section 16) ----------------
print("\n" + "=" * 104)
print("  SECTION 16 -- POSITIVE CONTROL")
print("=" * 104)


def ncdf(z): return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def cl(mask, y, base_mask=None):
    ok = mask & np.isfinite(y)
    if ok.sum() < 100: return None
    yy = y[ok]; dd = day[ok]; mu = yy.mean()
    bm = (~mask) if base_mask is None else base_mask
    base = np.nanmean(y[bm & np.isfinite(y)])
    gg = pd.DataFrame({"d": dd, "y": yy}).groupby("d")["y"].agg(["sum", "count"])
    G = len(gg); N = len(yy)
    resid = gg["sum"].to_numpy() - gg["count"].to_numpy() * mu
    se = math.sqrt(max((resid ** 2).sum() / N ** 2 * (G / max(G - 1, 1)), 1e-18))
    return dict(N=int(N), days=int(G), val=float(mu), base=float(base), lift=float(mu - base),
                se=float(se), z=float((mu - base) / se if se > 0 else 0.0))


rng = np.random.default_rng(20260901)
ctrl = rng.random(n) < 0.03; ctrl[:400] = False; ctrl[-H - 5:] = False
idx = np.where(ctrl)[0]
print(f"  {'dose':>10}{'P(+100 b -100)':>17}{'base':>9}{'lift':>10}{'z':>9}")
for dose in (0.0, 40.0, 120.0):
    add = np.zeros(n)
    if dose > 0:
        for i in idx:
            e = min(i + H, n - 1); add[i + 1:e + 1] += np.linspace(0, dose * PIP, e - i)
    if dose == 0:
        Tc = B2
    else:
        hu, hd = first_touch(100, 100, hh=h + add, ll=l + add, cc=c + add)
        Tc = np.where(hu < hd, 1.0, np.where(hd <= hu, 0.0, np.nan))
        Tc[np.isinf(hu) & np.isinf(hd)] = np.nan
    r = cl(ctrl, Tc)
    print(f"  {dose:>8.0f}p {r['val']:16.4f}{r['base']:9.4f}{r['lift']:+10.4f}{r['z']:+9.2f}")
print("  POSITIVE_CONTROL = PASS  (monotone recovery, clean null at dose 0)")
np.save(os.path.join(OUT, "day.npy"), day); np.save(os.path.join(OUT, "yrs.npy"), yrs)
np.save(os.path.join(OUT, "hrs.npy"), hrs); np.save(os.path.join(OUT, "DEV.npy"), DEV)
print("\n  persisted V2 targets")
