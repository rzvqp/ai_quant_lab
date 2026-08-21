"""Item 24 quantitative cost-wall: median per-trade RISK ($) on M15 vs H1 for the analogous
20-breakout+accept SHORT mechanism => STRESS round-trip 0.24 as a FRACTION of median risk on each TF.
DEVELOPMENT-gated. Uses mstrat native M15 (DEV<2018-05) and the H1 candidate risk already measured ($17.9)."""
import sys, os, numpy as np, pandas as pd
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code"
if WP5B not in sys.path: sys.path.insert(0, WP5B)
import mstrat
TICK = mstrat.TICK
d = mstrat.load(); d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
d = d[d["dt"] < pd.Timestamp("2018-05-01", tz="UTC")].reset_index(drop=True)
hi = d["high"].to_numpy(); lo = d["low"].to_numpy(); cl = d["close"].to_numpy(); o = d["open"].to_numpy(); atr = d["m_atr"].to_numpy(); n = len(d)
def rmin(a, w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()
def rmax(a, w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()
L = rmin(lo, 20); risks = []
for i in range(22, n - 2):
    if np.isfinite(L[i]) and cl[i] < L[i] and i + 1 < n and cl[i + 1] < cl[i]:  # 20-breakdown + acceptance short
        ei = i + 2 if i + 2 < n else i + 1; ref = o[min(ei, n - 1)]
        raw = rmax(hi, 20)[i]
        if not np.isfinite(raw): continue
        fl = max(0.05, 0.10 * atr[i]) if atr[i] == atr[i] else 0.05
        st = ref + max(abs(ref - raw), fl); risks.append(abs(ref - st))
risks = np.array([r for r in risks if r == r and r > 0])
med_m15 = float(np.median(risks)) if len(risks) else float("nan")
RT_STRESS = 0.24
print(f"M15 20-breakdown+accept SHORT: n_signals={len(risks)} median_risk=${med_m15:.3f}  STRESS_cost/median_risk={RT_STRESS/med_m15*100:.1f}%  (avg ATR M15=${np.nanmedian(atr):.2f})")
print(f"H1  20-breakout+accept  SHORT: median_risk=$17.876 (measured)               STRESS_cost/median_risk={RT_STRESS/17.876*100:.1f}%")
# H1 ATR median for context
import h1_protrend as HP  # noqa (re-runs; gives SLICES)
for bn in ("b0", "b1"):
    a = HP.SLICES[bn]["m_atr"].to_numpy(); print(f"  H1 {bn} median ATR14=${np.nanmedian(a):.2f}")
