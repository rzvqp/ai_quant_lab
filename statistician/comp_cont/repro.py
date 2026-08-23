"""Sections 5/6/7/8 -- independent reproduction of frozen COMP-CONT-L-rr2.
Uses the frozen implementation (it IS the contract under validation) but recomputes EVERY metric
from the trade ledger rather than trusting the frozen reporting layer.
"""
from __future__ import annotations
import sys, os, json
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\cc"
sys.path.insert(0, AD)
os.chdir(AD)
import swing_base as sb
import frontier5_compcont as F5

tfs = sb.build_frames()
h4, d1 = tfs["H4"], tfs["D1"]
d1 = d1.copy(); d1["d1_up"] = (d1["ema20"] > d1["ema50"]).astype(float)
h4c = sb.align_context(h4, d1, ["d1_up"], "_d1")
d1_up = h4c["d1_up_d1"].to_numpy() > 0.5
dev = h4["is_dev"].to_numpy()
cal = h4["is_cal"].to_numpy()
o = h4["open"].to_numpy()

comp, bh, bl = F5.comp_mask(h4)
print(f"  W={F5.W}  H={F5.H}  cooldown={F5.W}  COST={sb.COST}  PIP={sb.PIP}")
print(f"  H4 bars total={len(h4)}  DEV={int(dev.sum())}  CALIB={int(cal.sum())}")
print(f"  compression bars (any regime, any split): {int(np.isfinite(comp).sum() and comp.sum())}")


def build(mask_split, side=+1):
    want_up = side > 0
    cond = comp & (d1_up == want_up) & mask_split
    raw = np.array([i for i in np.where(cond)[0] if i + 1 < len(h4)])
    ev = sb.dedup_events(raw, cooldown=F5.W)
    risk = np.array([o[i + 1] - bl[i] for i in ev]) if side > 0 else np.array([bh[i] - o[i + 1] for i in ev])
    ok = np.isfinite(risk) & (risk > 0)
    return raw, ev[ok], risk[ok]


raw_dev, ev_dev, risk_dev = build(dev, +1)
print(f"\n  RAW triggers (DEV, LONG, D1-up, compression) : {len(raw_dev)}")
print(f"  after cooldown-{F5.W} dedup                    : {len(ev_dev)}")
print(f"  after risk>0 filter (effective trades)        : {len(ev_dev)}")


def M(tr, label=""):
    r = tr["R"].to_numpy(); n = len(r)
    if n == 0: return {}
    eq = np.cumsum(r); dd = float((eq - np.maximum.accumulate(eq)).min())
    wins = r[r > 0]; losses = r[r < 0]
    streak = mx = 0
    for x in r:
        streak = streak + 1 if x < 0 else 0
        mx = max(mx, streak)
    def brem(frac):
        k = int(np.ceil(n * frac)); k = min(k, n - 1)
        return float(np.sort(r)[:n - k].mean())
    t = pd.to_datetime(tr["t_entry"], unit="s", utc=True)
    days = t.dt.date.nunique()
    months = (t.max() - t.min()).days / 30.44
    return dict(N=n, avgR=float(r.mean()), medR=float(np.median(r)),
                WR_target=float((tr["exit_reason"] == "target").mean()),
                posRate=float((r > 0).mean()),
                PF=float(wins.sum() / -losses.sum()) if len(losses) else np.inf,
                maxDD=dd, maxLoss=float(r.min()), maxWin=float(r.max()),
                loss_streak=mx, unique_days=days, trades_per_month=n / months if months > 0 else np.nan,
                best1=brem(0.01), best5=brem(0.05), best10=brem(0.10),
                top1_contrib=float(np.sort(r)[-1] / r.sum()) if r.sum() != 0 else np.nan,
                med_sl_pips=float(tr["sl_pips"].median()), med_tp_pips=float(tr["tp_pips"].median()),
                med_hold=float(tr["hold"].median()))


print("\n" + "=" * 86)
print("  SECTION 5/7/8 -- INDEPENDENT REPRODUCTION, DEV, rr=2.0")
print("=" * 86)
res = {}
for scen in ("GROSS", "BASE", "STRESS"):
    tr = sb.simulate(h4, ev_dev, +1, risk_dev, rr=2.0, horizon=F5.H, scenario=scen)
    res[scen] = (tr, M(tr))
frozen = dict(N=53, avgR=0.443, PF=1.94, WR_target=0.396, posRate=0.509, medR=0.257,
              maxLoss=-1.114, maxDD=-6.19, best1=0.414, best5=0.350, best10=0.246,
              med_sl_pips=190, med_tp_pips=379, med_hold=8, trades_per_month=2.79)
m = res["STRESS"][1]
print(f"  {'metric':22}{'reproduced':>13}{'frozen spec':>13}   ")
for k, fv in frozen.items():
    mv = m.get(k)
    tol = 0.0015 if isinstance(fv, float) and abs(fv) < 10 else 1.0
    ok = "MATCH" if (mv is not None and abs(mv - fv) <= max(tol, abs(fv) * 0.01)) else "DIFFER"
    print(f"  {k:22}{mv:13.4f}{fv:13.4f}   {ok}")
print(f"\n  BASE avgR = {res['BASE'][1]['avgR']:+.4f}   (frozen spec: +0.46)")
print(f"  GROSS avgR= {res['GROSS'][1]['avgR']:+.4f}")
for k in ("unique_days", "loss_streak", "maxWin", "top1_contrib"):
    print(f"  {k:22}{m[k]:13.4f}   (not in the frozen spec -- reported per section 8)")

print("\n  EXIT-REASON DECOMPOSITION (STRESS):")
tr = res["STRESS"][0]
print("   ", tr["exit_reason"].value_counts().to_dict())

print("\n" + "=" * 86)
print("  SECTION 6 -- POSITION ACCOUNTING / OVERLAP")
print("=" * 86)
ent = tr["ei"].to_numpy(); ext = tr["exit_j"].to_numpy()
ov = sum(1 for k in range(1, len(ent)) if ent[k] <= ext[k - 1])
print(f"  trades whose entry bar is at/inside the previous trade's holding window: {ov} of {len(tr)} "
      f"= {ov/len(tr):.1%}")
print(f"  cooldown={F5.W} bars but horizon={F5.H} bars -> overlap is structurally possible")
maxconc = 0
for k in range(len(ent)):
    conc = sum(1 for j in range(len(ent)) if ent[j] <= ent[k] <= ext[j])
    maxconc = max(maxconc, conc)
print(f"  maximum concurrent open positions: {maxconc}")
print(f"  NOTE: metrics/maxDD are computed on a sequential cumsum of R, which implicitly assumes")
print(f"        one position at a time. With {ov} overlapping entries this is an approximation.")

json.dump(dict(dev=tr.to_dict(orient="records")), open(os.path.join(OUT, "ledger_dev.json"), "w"), default=str)

print("\n" + "=" * 86)
print("  SECTION 10 -- DISC / CONF (chronological 60/40, frozen definition)")
print("=" * 86)
n = len(tr)
cut = int(n * 0.6)
tr_s = tr.sort_values("t_entry").reset_index(drop=True)
disc, conf = tr_s.iloc[:cut], tr_s.iloc[cut:]
for nm, part in (("DISC", disc), ("CONF", conf)):
    mm = M(part)
    print(f"  {nm}: N={mm['N']:3d} avgR={mm['avgR']:+.3f} PF={mm['PF']:.2f} posRate={mm['posRate']:.3f} "
          f"maxDD={mm['maxDD']:.2f} best10={mm['best10']:+.3f}")
print(f"  frozen spec claims DISC +0.52 / CONF +0.33")

print("\n" + "=" * 86)
print("  PER-YEAR (STRESS, DEV)")
print("=" * 86)
yrs = pd.to_datetime(tr["t_entry"], unit="s", utc=True).dt.year
for y in sorted(yrs.unique()):
    sub = tr[yrs == y]; mm = M(sub)
    print(f"  {y}: N={mm['N']:3d} avgR={mm['avgR']:+.3f} PF={mm['PF']:.2f} maxDD={mm['maxDD']:.2f} "
          f"posRate={mm['posRate']:.3f}")

print("\n" + "=" * 86)
print("  CALIB 2024 (out-of-selection, frozen claim: N=24 avgR +0.223 PF 1.47 posRate 0.50)")
print("=" * 86)
raw_c, ev_c, risk_c = build(cal, +1)
trc = sb.simulate(h4, ev_c, +1, risk_c, rr=2.0, horizon=F5.H, scenario="STRESS")
mc = M(trc)
print(f"  reproduced: N={mc['N']} avgR={mc['avgR']:+.4f} PF={mc['PF']:.3f} posRate={mc['posRate']:.3f} "
      f"maxDD={mc['maxDD']:.2f} best10={mc['best10']:+.3f}")
