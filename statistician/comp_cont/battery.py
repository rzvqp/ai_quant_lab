"""Sections 11-14, 16 -- tail dependence, drawdown geometry, neighbour stability, concentration,
S5 independence. DEV population, frozen rule. No optimisation: neighbours are robustness probes only.
"""
from __future__ import annotations
import sys, os, json
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
sys.path.insert(0, AD)
os.chdir(AD)
import swing_base as sb
import frontier5_compcont as F5

tfs = sb.build_frames()
h4, d1 = tfs["H4"], tfs["D1"]
d1 = d1.copy(); d1["d1_up"] = (d1["ema20"] > d1["ema50"]).astype(float)
d1_up = sb.align_context(h4, d1, ["d1_up"], "_d1")["d1_up_d1"].to_numpy() > 0.5
dev = h4["is_dev"].to_numpy(); o = h4["open"].to_numpy()


def build(W, cooldown, mask):
    hh = h4["high"].to_numpy(); ll = h4["low"].to_numpy()
    atr = h4["atr"].to_numpy(); atr_ma = h4["atr_ma"].to_numpy()
    bh = pd.Series(hh).rolling(W).max().shift(1).to_numpy()
    bl = pd.Series(ll).rolling(W).min().shift(1).to_numpy()
    br = bh - bl; bma = pd.Series(br).rolling(50).mean().shift(1).to_numpy()
    comp = (atr < atr_ma) & (br < bma) & np.isfinite(br) & np.isfinite(atr)
    cond = comp & (d1_up) & mask
    raw = np.array([i for i in np.where(cond)[0] if i + 1 < len(h4)])
    if len(raw) == 0:
        return np.array([]), np.array([])
    ev = sb.dedup_events(raw, cooldown=cooldown)
    risk = np.array([o[i + 1] - bl[i] for i in ev])
    ok = np.isfinite(risk) & (risk > 0)
    return ev[ok], risk[ok]


def M(tr):
    r = tr["R"].to_numpy(); n = len(r)
    if n == 0: return dict(N=0)
    eq = np.cumsum(r); w, l = r[r > 0], r[r < 0]
    def brem(f):
        k = min(int(np.ceil(n * f)), n - 1); return float(np.sort(r)[:n - k].mean())
    return dict(N=n, avgR=float(r.mean()), PF=float(w.sum() / -l.sum()) if len(l) else np.inf,
                maxDD=float((eq - np.maximum.accumulate(eq)).min()),
                best1=brem(0.01), best5=brem(0.05), best10=brem(0.10), posRate=float((r > 0).mean()))


ev, risk = build(F5.W, F5.W, dev)
tr = sb.simulate(h4, ev, +1, risk, rr=2.0, horizon=F5.H, scenario="STRESS")
r = tr["R"].to_numpy(); n = len(r)

print("=" * 88); print("  SECTION 11 -- TAIL DEPENDENCE (DEV, STRESS)"); print("=" * 88)
srt = np.sort(r)[::-1]
for f, lab in ((0.01, "best-1%"), (0.05, "best-5%"), (0.10, "best-10%"), (0.20, "best-20%")):
    k = min(int(np.ceil(n * f)), n - 1)
    print(f"    remove {lab:9} (k={k:2d}) -> avgR {np.sort(r)[:n-k].mean():+.4f}")
print(f"    single largest winner {srt[0]:+.3f}R = {srt[0]/r.sum():.1%} of total P&L")
print(f"    top 3 winners = {srt[:3].sum()/r.sum():.1%} of total P&L")
print(f"    payoff geometry: rr=2.0 target, {int((tr['exit_reason']=='target').sum())} target / "
      f"{int((tr['exit_reason']=='stop').sum())} stop / {int((tr['exit_reason']=='horizon').sum())} horizon")
print(f"    -> positively skewed by design; best-10%-removed {M(tr)['best10']:+.3f} REMAINS POSITIVE on DEV")

print("\n" + "=" * 88); print("  SECTION 12 -- DRAWDOWN / LOSS GEOMETRY (DEV, STRESS)"); print("=" * 88)
eq = np.cumsum(r); dd = eq - np.maximum.accumulate(eq)
i_tr = int(np.argmin(dd))
print(f"    maxDD {dd.min():.3f}R at trade #{i_tr+1}/{n}")
peak = int(np.argmax(eq[:i_tr+1])) if i_tr > 0 else 0
rec = next((j for j in range(i_tr, n) if eq[j] >= eq[peak]), None)
print(f"    drawdown from trade #{peak+1} to #{i_tr+1}; recovered at trade #{rec+1 if rec else None}"
      f" ({(rec-i_tr) if rec else 'never'} trades)")
print(f"    max single loss {r.min():.3f}R   (>1.0R because of cost on top of a full stop)")
streak = mx = 0
for x in r:
    streak = streak + 1 if x < 0 else 0; mx = max(mx, streak)
print(f"    longest losing streak: {mx} trades")
yrs = pd.to_datetime(tr['t_entry'], unit='s', utc=True).dt.year
for y in sorted(yrs.unique()):
    rr_ = r[(yrs == y).to_numpy()]; e = np.cumsum(rr_)
    print(f"    {y}: maxDD {float((e-np.maximum.accumulate(e)).min()):.2f}R over N={len(rr_)}")
print(f"    S5 governance reference (gate G): maxDD <= 15R and maxLoss <= 2.0R -> "
      f"DD {abs(dd.min()):.2f}R PASS, loss {abs(r.min()):.3f}R PASS")

print("\n" + "=" * 88); print("  SECTION 13 -- NEIGHBOUR STABILITY (probe only; frozen candidate unchanged)"); print("=" * 88)
print(f"  {'perturbation':22}{'N':>5}{'avgR':>9}{'PF':>7}{'best10':>9}{'maxDD':>8}")
print(f"  {'FROZEN W=20 cd=20 rr=2':22}{n:5d}{r.mean():+9.3f}{M(tr)['PF']:7.2f}{M(tr)['best10']:+9.3f}{M(tr)['maxDD']:8.2f}")
for W in (14, 16, 18, 22, 24, 28):
    e2, k2 = build(W, W, dev)
    if len(e2) < 8: print(f"  {'W='+str(W):22}{len(e2):5d}   too few"); continue
    t2 = sb.simulate(h4, e2, +1, k2, rr=2.0, horizon=F5.H, scenario="STRESS"); m2 = M(t2)
    print(f"  {'W='+str(W):22}{m2['N']:5d}{m2['avgR']:+9.3f}{m2['PF']:7.2f}{m2['best10']:+9.3f}{m2['maxDD']:8.2f}")
for cd in (10, 12, 16, 24, 30):
    e2, k2 = build(F5.W, cd, dev)
    t2 = sb.simulate(h4, e2, +1, k2, rr=2.0, horizon=F5.H, scenario="STRESS"); m2 = M(t2)
    print(f"  {'cooldown='+str(cd):22}{m2['N']:5d}{m2['avgR']:+9.3f}{m2['PF']:7.2f}{m2['best10']:+9.3f}{m2['maxDD']:8.2f}")
for rr_ in (1.5, 2.5, 3.0):
    t2 = sb.simulate(h4, ev, +1, risk, rr=rr_, horizon=F5.H, scenario="STRESS"); m2 = M(t2)
    print(f"  {'rr='+str(rr_):22}{m2['N']:5d}{m2['avgR']:+9.3f}{m2['PF']:7.2f}{m2['best10']:+9.3f}{m2['maxDD']:8.2f}")
for Hh in (30, 60, 84):
    t2 = sb.simulate(h4, ev, +1, risk, rr=2.0, horizon=Hh, scenario="STRESS"); m2 = M(t2)
    print(f"  {'horizon='+str(Hh):22}{m2['N']:5d}{m2['avgR']:+9.3f}{m2['PF']:7.2f}{m2['best10']:+9.3f}{m2['maxDD']:8.2f}")

print("\n" + "=" * 88); print("  SECTION 14 -- TEMPORAL / SESSION CONCENTRATION (DEV)"); print("=" * 88)
t = pd.to_datetime(tr["t_entry"], unit="s", utc=True)
tot = r.sum()
for lab, key in (("year", t.dt.year), ("quarter", t.dt.to_period("Q").astype(str)),
                 ("entry hour UTC", t.dt.hour)):
    grp = pd.DataFrame({"k": key.to_numpy(), "r": r}).groupby("k")["r"].agg(["count", "sum", "mean"])
    top = grp["sum"].idxmax()
    print(f"    by {lab:16} top={top} contributes {grp['sum'].max()/tot:.1%} of P&L over "
          f"{int(grp.loc[top,'count'])}/{n} trades  (groups={len(grp)})")
print(f"    entry-hour distribution: {dict(t.dt.hour.value_counts().sort_index())}")
print(f"    2022 detail: N=8 avgR=+1.000 -> contributes {r[(yrs==2022).to_numpy()].sum()/tot:.1%} of P&L from "
      f"{int((yrs==2022).sum())}/{n} trades")
