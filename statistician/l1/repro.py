"""STAT-L1-EXACT-SPEC-FREEZE -- verbatim reproduction of the Scout V1 L1 phenomenon.
Provenance only. No new research, no optimisation, no strategy content.
Every definition below is copied from statistician/scout/{scan.py,run2.py,run3.py}.
"""
from __future__ import annotations
import sys, os, json, math, hashlib
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\l1"
sys.path.insert(0, AD); os.chdir(AD)
import m5_data

PIP = 0.10          # scan.py:15
H = 288             # scan.py:16   24h forward horizon in M5 bars

m = m5_data.load_m5()                                   # scan.py:42
t = pd.to_datetime(m["time"], unit="s", utc=True)       # scan.py:43  -> UTC, no DST handling
h = m["high"].to_numpy(float); l = m["low"].to_numpy(float); c = m["close"].to_numpy(float)
n = len(m)
DATASET_HASH = hashlib.sha256(open(m5_data.M5PATH, "rb").read()).hexdigest()
day = pd.Series(t).dt.floor("D").astype("int64").to_numpy()
yrs = t.dt.year.to_numpy()
hr = t.dt.hour.to_numpy()                               # scan.py:74
S_sess = np.where(hr < 8, "AS", np.where(hr < 13, "LN", np.where(hr < 20, "NY", "LT")))  # scan.py:75
LN = (S_sess == "LN")

print("=" * 104)
print("  L1 EXACT SPECIFICATION -- recovered verbatim from Scout V1 source")
print("=" * 104)
print(f"  dataset      : native governed M5, {n} bars, {t.min()} .. {t.max()}")
print(f"  dataset hash : sha256 {DATASET_HASH}")
print(f"  timezone     : UTC throughout; hour taken from pd.to_datetime(time, unit='s', utc=True).dt.hour")
print(f"  DST handling : NONE -- fixed UTC hour buckets, no local-time or DST adjustment")
print(f"  L1 condition : UTC hour in {{8,9,10,11,12}}  i.e. the 08:00-13:00 UTC WINDOW")
print(f"  -> L1 is NOT a London OPEN event. It is EVERY M5 bar inside that 5-hour window.")
print(f"     eligible L1 bars = {int(LN.sum())} of {n} ({LN.mean():.1%})")


def barriers(up_p, dn_p, horizon=H):                    # scan.py:90-107, verbatim
    U = c + up_p * PIP; D = c - dn_p * PIP
    hit_up = np.full(n, np.inf); hit_dn = np.full(n, np.inf)
    for j in range(1, horizon + 1):
        hj = np.concatenate([h[j:], np.full(j, np.nan)])
        lj = np.concatenate([l[j:], np.full(j, np.nan)])
        hit_up = np.where((hj >= U) & np.isinf(hit_up), j, hit_up)
        hit_dn = np.where((lj <= D) & np.isinf(hit_dn), j, hit_dn)
    out = np.where(hit_up < hit_dn, 1.0, np.where(hit_dn <= hit_up, 0.0, np.nan))  # ties -> ADVERSE
    out = np.where(np.isinf(hit_up) & np.isinf(hit_dn), np.nan, out)
    return out, hit_up, hit_dn


def clustered(mask, y):                                 # run2.py, verbatim
    ok = mask & np.isfinite(y)
    yy = y[ok]; dd = day[ok]; mu = yy.mean()
    base = np.nanmean(y[(~mask) & np.isfinite(y)])
    g = pd.DataFrame({"d": dd, "y": yy}).groupby("d")["y"].agg(["sum", "count"])
    G = len(g); N = len(yy)
    resid = g["sum"].to_numpy() - g["count"].to_numpy() * mu
    se = math.sqrt(max((resid ** 2).sum() / N ** 2 * (G / max(G - 1, 1)), 1e-18))
    return dict(N=int(N), days=int(G), p=float(mu), base=float(base), lift=float(mu - base),
                se=float(se), z=float((mu - base) / se if se > 0 else 0.0))


print("\n  computing the three barrier races (scan.py:120-122) ...")
T1, u1, d1 = barriers(100, 80)
T2, u2, d2 = barriers(200, 100)
T3, u3, d3 = barriers(300, 150)

print("\n" + "=" * 104)
print("  STATISTIC 1 -- THE HEADLINE (this is what '0.466 -> 0.4286, z -3.59' means)")
print("=" * 104)
print("  T1 = P( +100 project pips touched BEFORE -80 project pips ), measured from the CLOSE of bar t,")
print("       over bars t+1 .. t+288 (24h). Ties inside one M5 bar are assigned to the ADVERSE side.")
print("       Unresolved within 288 bars -> excluded (NaN), not counted either way.")
print("       BASELINE = the COMPLEMENT of L1 (all AS + NY + LT bars), not 'all bars'.")
orig = {}
for nm, ty, claim in (("T1 P(+100 before -80)", T1, (0.4663, 0.4286, -3.59)),
                      ("T2 P(+200 before -100)", T2, (0.3260, 0.2993, -2.32)),
                      ("T3 P(+300 before -150)", T3, (0.3036, 0.2817, -1.57))):
    r = clustered(LN, ty); orig[nm] = r
    ok = (abs(r["base"] - claim[0]) < 5e-4 and abs(r["p"] - claim[1]) < 5e-4 and abs(r["z"] - claim[2]) < 0.02)
    print(f"    {nm:26} N={r['N']:6d} days={r['days']:5d}  base={r['base']:.4f} -> L1={r['p']:.4f}"
          f"  lift={r['lift']:+.4f}  z={r['z']:+.2f}   V1 claim {claim}   {'MATCH' if ok else 'DIFFER'}")

print("\n" + "=" * 104)
print("  STATISTIC 2 -- THE TIMING FIGURE (this is what '3.4h vs 6.9h' means)")
print("=" * 104)
print("  run3.py:118-119 computed  median( hit_up ) * 5/60  where hit_up is the first-touch bar index of")
print("  the +100p UP barrier ONLY (from barriers(100,80)).  Observations never touching +100p within")
print("  288 bars are INF and were DROPPED by np.isfinite -- i.e. censored cases are excluded, not censored.")
print("  It is therefore NOT 'median time to +-100p'. It is 'median time to +100p UP, given it was reached'.")
tt = u1[LN & np.isfinite(u1)]
tb = u1[(~LN) & np.isfinite(u1)]
print(f"    L1       : n={len(tt):6d}  median = {np.median(tt)*5/60:.2f} h   (V1 reported 3.4h)")
print(f"    baseline : n={len(tb):6d}  median = {np.median(tb)*5/60:.2f} h   (V1 reported 6.9h)")
print(f"    share of L1 bars whose +100p was reached within 24h : {np.isfinite(u1[LN]).mean():.3f}")
print(f"    share of baseline bars                              : {np.isfinite(u1[~LN]).mean():.3f}")

print("\n" + "=" * 104)
print("  STATISTIC 3 -- THE '6/6 YEARS' CLAIM")
print("=" * 104)
print("  V1's 6/6 was computed on T3 (P(+300 before -150)) per-year lift -- NOT on T1 and NOT on timing.")
for nm, ty in (("T3 (the original 6/6 basis)", T3), ("T1 (headline; provenance clarification)", T1)):
    yl = {}
    for y in sorted(set(yrs)):
        ym = LN & (yrs == y)
        ok = ym & np.isfinite(ty); bm = (~LN) & (yrs == y) & np.isfinite(ty)
        if ok.sum() < 300: continue
        yl[int(y)] = round(float(ty[ok].mean() - ty[bm].mean()), 3)
    same = sum(1 for v in yl.values() if v < 0)
    print(f"    {nm:42} {yl}  -> {same}/{len(yl)} negative")

print("\n" + "=" * 104)
print("  NON-OVERLAP ROBUSTNESS (run3.py:91-93)  -- 1 bar per 288, first-come")
print("=" * 104)
keep = np.zeros(n, bool); last = -10 ** 9
for i in range(n):
    if i - last >= H: keep[i] = True; last = i
for nm, ty, claim in (("T1", T1, (-0.0736, -2.38)), ("T2", T2, (-0.0610, -1.98)), ("T3", T3, (-0.0977, -2.85))):
    msk = LN & keep
    ok = msk & np.isfinite(ty); bm = (~LN) & keep & np.isfinite(ty)
    yy = ty[ok]; mu = yy.mean(); base = ty[bm].mean()
    g = pd.DataFrame({"d": day[ok], "y": yy}).groupby("d")["y"].agg(["sum", "count"])
    G = len(g); N = len(yy)
    resid = g["sum"].to_numpy() - g["count"].to_numpy() * mu
    se = math.sqrt(max((resid ** 2).sum() / N ** 2 * (G / max(G - 1, 1)), 1e-18))
    z = (mu - base) / se
    ok2 = abs(mu - base - claim[0]) < 5e-4 and abs(z - claim[1]) < 0.02
    print(f"    {nm}: N={N:5d} lift={mu-base:+.4f} z={z:+.2f}   V1 claim {claim}   {'MATCH' if ok2 else 'DIFFER'}")

SPEC = dict(
    phenomenon_id="L1-LONDON-WINDOW-PATH-ASYMMETRY-V1",
    dataset="OANDA_XAUUSD_M5.csv (native governed, no synthesis)",
    dataset_sha256=DATASET_HASH, bars=int(n),
    span=[str(t.min()), str(t.max())],
    timezone="UTC", dst_handling="NONE (fixed UTC hour buckets)",
    condition="UTC hour in {8,9,10,11,12}  == the 08:00-13:00 UTC window; EVERY M5 bar in the window",
    not_an_open_event=True,
    baseline="complement of the condition: all M5 bars with UTC hour outside [8,13)",
    headline_statistic="P(+100 project pips touched before -80 project pips)",
    reference_price="close of bar t", pip_usd=0.10,
    measurement_start="bar t+1", horizon_bars=288, horizon_hours=24,
    tie_rule="both barriers inside one M5 bar -> ADVERSE (0)",
    censoring="unresolved within 288 bars -> excluded (NaN)",
    dedup="NONE - every eligible M5 bar is one observation (overlapping)",
    overlap_handling="day-clustered standard errors; separate 1-per-288-bar non-overlap check",
    missing_data="weekend/holiday gaps left as-is; forward window walks bar index, not clock",
    timing_statistic="median of first-touch bar index of the +100p UP barrier ONLY, censored cases DROPPED",
)
SPEC_HASH = hashlib.sha256(json.dumps(SPEC, sort_keys=True).encode()).hexdigest()
print(f"\n  SPEC_HASH = {SPEC_HASH}")
json.dump(dict(spec=SPEC, spec_hash=SPEC_HASH, headline=orig), open(os.path.join(OUT, "l1_spec.json"), "w"), indent=1)
