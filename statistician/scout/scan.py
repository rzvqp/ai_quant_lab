"""STATISTICIAN INDEPENDENT ALPHA SCOUT V1 -- bounded, preregistered discovery scan.
Native governed M5 only. Information-first (path distributions), NOT forced trades.
Read-only: nothing in S5/Q4/AI Trader/P007/MGMT004/MT5/StrategyCatalog is touched.
"""
from __future__ import annotations
import sys, os, json, math, hashlib
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\scout"
sys.path.insert(0, AD); os.chdir(AD)
import m5_data

PIP = 0.10
H = 288          # 24h forward horizon in M5 bars
PREREG = """
PREREGISTERED BOUNDED SEARCH SPACE (declared before any scoring)

  STATE VARIABLES (6, all strictly causal, computed from bars <= t only):
    S1 speed      = (c[t]-c[t-12]) / atr[t]                     1h displacement in ATR
    S2 vol_state  = atr[t] / mean(atr[t-288:t])                 vol vs its own 24h norm
    S3 range_loc  = (c[t]-min(low[t-288:t])) / (24h range)      location in the 24h range
    S4 session    = AS / LN / NY / LT (UTC hour buckets)
    S5b breakout  = c[t] > max(high[t-48:t])  (up) / < min(low[t-48:t]) (down)   <- DIRECTION REVEALED
    S6 path_order = over t-24..t, did MAE occur before MFE (adverse-first) or after

  TARGETS (path distribution, both sides, measured over t+1..t+288):
    T1  P(+100p before -80p)
    T2  P(+200p before -100p)
    T3  P(+300p before -150p)
    plus MFE, MAE, time-to-first-100p

  SAME-BAR AMBIGUITY: if both barriers fall inside one M5 bar, the ADVERSE side is assigned.

  DECLARED CELL BUDGET: 6 states x 3 targets x 2 sides = 36 primary cells,
                        + 8 preregistered 2-way interactions = 44 tests total.
  No other cell will be scored. Effect ranking is by |lift| with day-clustered SE, not by p alone.
"""
print(PREREG)

m = m5_data.load_m5()
t = pd.to_datetime(m["time"], unit="s", utc=True)
o = m["open"].to_numpy(float); h = m["high"].to_numpy(float)
l = m["low"].to_numpy(float); c = m["close"].to_numpy(float)
n = len(m)
sha = hashlib.sha256(open(m5_data.M5PATH, "rb").read()).hexdigest()
print("=" * 100)
print("  SECTION 7 -- NATIVE M5 DATA VERIFICATION")
print("=" * 100)
print(f"    rows={n}  span {t.min()} .. {t.max()}   sha256 {sha[:16]}")
DEV_END=pd.Timestamp("2024-06-30",tz="UTC")
print(f"    PREREGISTERED chronological split: DEV <= {DEV_END.date()} | OOS after (declared before scoring)")
yrs = t.dt.year.to_numpy()
print(f"    per-year bars: {dict(sorted(pd.Series(yrs).value_counts().items()))}")
gaps = np.diff(m['time'].to_numpy()) / 60.0
print(f"    modal step {pd.Series(gaps).mode().iloc[0]:.0f} min   gaps>60min: {int((gaps>60).sum())}")
print("    COVERAGE CAVEAT (carried on every finding): native M5 is 2021-07-27+ only = ONE macro-era.")
print("    No cross-era claim is possible; year/subperiod stability is the strongest available check.")

# ---------------- causal features (own implementation, fully auditable) ----------------
tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1)))); tr[0] = h[0] - l[0]
atr = pd.Series(tr).rolling(14).mean().to_numpy()
atr24 = pd.Series(atr).rolling(288).mean().shift(1).to_numpy()
hi48 = pd.Series(h).rolling(48).max().shift(1).to_numpy()
lo48 = pd.Series(l).rolling(48).min().shift(1).to_numpy()
hi288 = pd.Series(h).rolling(288).max().shift(1).to_numpy()
lo288 = pd.Series(l).rolling(288).min().shift(1).to_numpy()
c12 = pd.Series(c).shift(12).to_numpy()

S_speed = (c - c12) / atr
S_vol = atr / atr24
S_loc = (c - lo288) / np.maximum(hi288 - lo288, 1e-9)
hr = t.dt.hour.to_numpy()
S_sess = np.where(hr < 8, "AS", np.where(hr < 13, "LN", np.where(hr < 20, "NY", "LT")))
S_brk_up = c > hi48
S_brk_dn = c < lo48

# path order over the last 24 bars (causal): index of MAE vs MFE relative to c[t-24]
ref24 = pd.Series(c).shift(24).to_numpy()
mfe_i = np.full(n, np.nan); mae_i = np.full(n, np.nan)
for j in range(1, 25):
    hj = pd.Series(h).shift(24 - j).to_numpy(); lj = pd.Series(l).shift(24 - j).to_numpy()
    up = hj - ref24; dn = ref24 - lj
    mfe_i = np.where(np.isnan(mfe_i) & (up > 0), j, mfe_i)
    mae_i = np.where(np.isnan(mae_i) & (dn > 0), j, mae_i)
S_adverse_first = (np.nan_to_num(mae_i, nan=99) < np.nan_to_num(mfe_i, nan=99))

# ---------------- forward barrier engine ----------------
def barriers(up_p, dn_p, ref=c, horizon=H):
    """First-touch race from bar t (reference price ref[t]) over t+1..t+horizon.
    Returns +1 if the UP barrier is touched strictly first, 0 if DOWN first (or same bar), nan if unresolved."""
    U = ref + up_p * PIP; D = ref - dn_p * PIP
    hit_up = np.full(n, np.inf); hit_dn = np.full(n, np.inf)
    for j in range(1, horizon + 1):
        hj = np.concatenate([h[j:], np.full(j, np.nan)])
        lj = np.concatenate([l[j:], np.full(j, np.nan)])
        up_now = (hj >= U) & np.isinf(hit_up)
        dn_now = (lj <= D) & np.isinf(hit_dn)
        hit_up = np.where(up_now, j, hit_up)
        hit_dn = np.where(dn_now, j, hit_dn)
        if np.isfinite(hit_up).all() and np.isfinite(hit_dn).all(): break
    out = np.full(n, np.nan)
    both_inf = np.isinf(hit_up) & np.isinf(hit_dn)
    out = np.where(hit_up < hit_dn, 1.0, np.where(hit_dn <= hit_up, 0.0, np.nan))  # ties -> adverse (0)
    out = np.where(both_inf, np.nan, out)
    return out, hit_up, hit_dn


def mfe_mae(horizon=H):
    mx = np.full(n, -np.inf); mn = np.full(n, np.inf)
    for j in range(1, horizon + 1):
        hj = np.concatenate([h[j:], np.full(j, np.nan)])
        lj = np.concatenate([l[j:], np.full(j, np.nan)])
        mx = np.fmax(mx, hj); mn = np.fmin(mn, lj)
    return (mx - c) / PIP, (c - mn) / PIP


print("\n  computing forward path targets (this is the expensive step)...")
T1, u1, d1 = barriers(100, 80)
T2, u2, d2 = barriers(200, 100)
T3, u3, d3 = barriers(300, 150)
MFE, MAE = mfe_mae()
print(f"    baselines  P(+100 before -80) = {np.nanmean(T1):.4f}   n={int(np.isfinite(T1).sum())}")
print(f"               P(+200 before -100)= {np.nanmean(T2):.4f}   n={int(np.isfinite(T2).sum())}")
print(f"               P(+300 before -150)= {np.nanmean(T3):.4f}   n={int(np.isfinite(T3).sum())}")
print(f"               median MFE {np.nanmedian(MFE):.0f}p   median MAE {np.nanmedian(MAE):.0f}p")

np.save(os.path.join(OUT, "T1.npy"), T1); np.save(os.path.join(OUT, "T2.npy"), T2); np.save(os.path.join(OUT, "T3.npy"), T3)
np.save(os.path.join(OUT, "MFE.npy"), MFE); np.save(os.path.join(OUT, "MAE.npy"), MAE)
for nm, arr in (("speed", S_speed), ("vol", S_vol), ("loc", S_loc), ("brk_up", S_brk_up.astype(float)),
                ("brk_dn", S_brk_dn.astype(float)), ("adv_first", S_adverse_first.astype(float)),
                ("u1", u1), ("d1", d1)):
    np.save(os.path.join(OUT, f"{nm}.npy"), arr)
np.save(os.path.join(OUT, "sess.npy"), S_sess.astype(object), allow_pickle=True)
np.save(os.path.join(OUT, "yrs.npy"), yrs)
np.save(os.path.join(OUT, "tsec.npy"), m["time"].to_numpy())
print("  persisted arrays")
