"""ALPHA SCOUT V1 -- run 2: positive control (section 9) + bounded conditional scan (sections 4/8)."""
from __future__ import annotations
import sys, os, json, math
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
tsec = m["time"].to_numpy()
t = pd.to_datetime(tsec, unit="s", utc=True)
day = pd.Series(t).dt.floor("D").astype("int64").to_numpy()
yrs = np.load(os.path.join(OUT, "yrs.npy"))
T1 = np.load(os.path.join(OUT, "T1.npy")); T2 = np.load(os.path.join(OUT, "T2.npy")); T3 = np.load(os.path.join(OUT, "T3.npy"))
MFE = np.load(os.path.join(OUT, "MFE.npy")); MAE = np.load(os.path.join(OUT, "MAE.npy"))
S = {k: np.load(os.path.join(OUT, f"{k}.npy")) for k in ("speed", "vol", "loc", "brk_up", "brk_dn", "adv_first", "u1", "d1")}
sess = np.load(os.path.join(OUT, "sess.npy"), allow_pickle=True)
DEV = t <= pd.Timestamp("2024-06-30", tz="UTC")


def ncdf(z): return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def clustered(mask, y):
    """mean of y|mask with day-clustered SE, and lift vs the complement baseline."""
    ok = mask & np.isfinite(y)
    if ok.sum() < 200: return None
    yy = y[ok]; dd = day[ok]
    mu = yy.mean()
    base = np.nanmean(y[(~mask) & np.isfinite(y)])
    dfm = pd.DataFrame({"d": dd, "y": yy})
    g = dfm.groupby("d")["y"].agg(["sum", "count"])
    G = len(g); N = len(yy)
    resid = g["sum"].to_numpy() - g["count"].to_numpy() * mu
    se = math.sqrt(max((resid ** 2).sum() / N ** 2 * (G / max(G - 1, 1)), 1e-18))
    z = (mu - base) / se if se > 0 else 0.0
    return dict(N=int(N), days=int(G), p=float(mu), base=float(base), lift=float(mu - base),
                se=float(se), z=float(z), pval=float(2 * (1 - ncdf(abs(z)))))


# ---------------------------------------------------------------- SECTION 9: POSITIVE CONTROL
print("=" * 104)
print("  SECTION 9 -- POSITIVE CONTROL (end-to-end: inject a real price effect, confirm recovery)")
print("=" * 104)
rng = np.random.default_rng(20260831)
ctrl_state = rng.random(n) < 0.03                       # a synthetic rare causal state, 3% of bars
ctrl_state[:300] = False; ctrl_state[-H - 5:] = False
DRIFT_PIPS = 60.0                                        # inject +60p of drift over the next 288 bars
add = np.zeros(n)
idx = np.where(ctrl_state)[0]
for i in idx:
    end = min(i + H, n - 1)
    ramp = np.linspace(0, DRIFT_PIPS * PIP, end - i)
    add[i + 1:end + 1] += ramp
h2 = h + add; l2 = l + add; c2 = c + add


def barriers_on(hh, ll, cc, up_p, dn_p, horizon=H):
    U = cc + up_p * PIP; D = cc - dn_p * PIP
    hu = np.full(n, np.inf); hd = np.full(n, np.inf)
    for j in range(1, horizon + 1):
        hj = np.concatenate([hh[j:], np.full(j, np.nan)])
        lj = np.concatenate([ll[j:], np.full(j, np.nan)])
        hu = np.where((hj >= U) & np.isinf(hu), j, hu)
        hd = np.where((lj <= D) & np.isinf(hd), j, hd)
    out = np.where(hu < hd, 1.0, np.where(hd <= hu, 0.0, np.nan))
    return np.where(np.isinf(hu) & np.isinf(hd), np.nan, out)


T1c = barriers_on(h2, l2, c2, 100, 80)
r_inj = clustered(ctrl_state, T1c)
r_null = clustered(ctrl_state, T1)     # the SAME synthetic state on the REAL, uninjected data
print(f"    injected drift = +{DRIFT_PIPS:.0f} project pips over 24h on a random 3% of bars")
print(f"    RECOVERED on injected data : P={r_inj['p']:.4f} base={r_inj['base']:.4f} lift={r_inj['lift']:+.4f} z={r_inj['z']:+.2f} (N={r_inj['N']})")
print(f"    NULL check on real data    : P={r_null['p']:.4f} base={r_null['base']:.4f} lift={r_null['lift']:+.4f} z={r_null['z']:+.2f}")
POS_CONTROL = (r_inj["lift"] > 0.05 and r_inj["z"] > 4) and abs(r_null["z"]) < 3
print(f"    POSITIVE_CONTROL_PASSED = {POS_CONTROL}   (engine detects a real effect and does not hallucinate one)")

# ---------------------------------------------------------------- BOUNDED CONDITIONAL SCAN
print("\n" + "=" * 104)
print("  SECTIONS 4 / 8 -- BOUNDED CONDITIONAL SCAN (44 declared tests)")
print("=" * 104)
qs = lambda a, p: np.nanquantile(a, p)
states = {
    "S1 speed>+1.5ATR (fast up)":      S["speed"] > 1.5,
    "S1 speed<-1.5ATR (fast down)":    S["speed"] < -1.5,
    "S2 vol>1.3x24h (expansion)":      S["vol"] > 1.3,
    "S2 vol<0.7x24h (compression)":    S["vol"] < 0.7,
    "S3 range_loc>0.9 (at 24h high)":  S["loc"] > 0.9,
    "S3 range_loc<0.1 (at 24h low)":   S["loc"] < 0.1,
    "S4 session=LN":                   sess == "LN",
    "S4 session=NY":                   sess == "NY",
    "S5 breakout UP (48-bar)":         S["brk_up"] > 0.5,
    "S5 breakout DOWN (48-bar)":       S["brk_dn"] > 0.5,
    "S6 adverse-first (last 2h)":      S["adv_first"] > 0.5,
    "S6 favourable-first (last 2h)":   S["adv_first"] < 0.5,
}
targets = {"T1 P(+100 before -80)": T1, "T2 P(+200 before -100)": T2, "T3 P(+300 before -150)": T3}
rows = []
print(f"  {'state':34}{'target':26}{'N':>8}{'days':>6}{'P':>8}{'base':>8}{'lift':>9}{'z':>8}")
for sn, sm in states.items():
    for tn, ty in targets.items():
        r = clustered(sm, ty)
        if r is None: continue
        rows.append(dict(state=sn, target=tn, **r))
        print(f"  {sn:34}{tn:26}{r['N']:8d}{r['days']:6d}{r['p']:8.4f}{r['base']:8.4f}{r['lift']:+9.4f}{r['z']:+8.2f}")

# 8 preregistered interactions
inter = {
    "brkUP x NY":            (S["brk_up"] > 0.5) & (sess == "NY"),
    "brkUP x vol>1.3":       (S["brk_up"] > 0.5) & (S["vol"] > 1.3),
    "brkDOWN x NY":          (S["brk_dn"] > 0.5) & (sess == "NY"),
    "brkDOWN x vol>1.3":     (S["brk_dn"] > 0.5) & (S["vol"] > 1.3),
    "fastUP x loc>0.9":      (S["speed"] > 1.5) & (S["loc"] > 0.9),
    "fastDOWN x loc<0.1":    (S["speed"] < -1.5) & (S["loc"] < 0.1),
    "compression x LN":      (S["vol"] < 0.7) & (sess == "LN"),
    "advFirst x brkUP":      (S["adv_first"] > 0.5) & (S["brk_up"] > 0.5),
}
print(f"\n  --- 8 preregistered interactions (target T2) ---")
for nm, msk in inter.items():
    r = clustered(msk, T2)
    if r is None:
        print(f"  {nm:26} insufficient N"); continue
    rows.append(dict(state=nm, target="T2 P(+200 before -100)", **r))
    print(f"  {nm:26} N={r['N']:7d} days={r['days']:5d} P={r['p']:.4f} base={r['base']:.4f} lift={r['lift']:+.4f} z={r['z']:+.2f}")

df = pd.DataFrame(rows)
df["abs_lift"] = df["lift"].abs()
df = df.sort_values("abs_lift", ascending=False)
print(f"\n  TOTAL TESTS SCORED: {len(df)}  (declared budget 44)")
print("\n  TOP 10 BY |LIFT|:")
print(df.head(10)[["state", "target", "N", "days", "p", "base", "lift", "z"]].to_string(index=False))
df.to_json(os.path.join(OUT, "scan_results.json"), orient="records")
