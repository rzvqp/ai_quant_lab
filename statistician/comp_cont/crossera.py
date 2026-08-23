"""Section 9 -- cross-era falsification of the FROZEN COMP-CONT-L-rr2 rule on the lab's own authorized
b0/b1 corpus (2011-2013 + 2016-2018), via the governance-proven hist_m15_data loader.
The strategy is NOT modified: same W=20, H=42, cooldown=20, rr=2.0, D1 EMA20>EMA50 causal context,
box_low structural stop, next-bar-open entry, stop-wins-ties, STRESS cost.
"""
from __future__ import annotations
import sys, os
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
sys.path.insert(0, AD)
os.chdir(AD)
import swing_base as sb
import frontier5_compcont as F5
import hist_m15_data as H

tfs = H.build(verbose=True)
print("\n  frames:", {k: len(v) for k, v in tfs.items()})
h4, d1 = tfs["H4"], tfs["D1"]
print("  H4 columns:", [c for c in h4.columns][:18])
need = ["open", "high", "low", "close", "atr", "atr_ma", "ema20", "ema50"]
print("  required cols present in H4:", {c: (c in h4.columns) for c in need})
print("  required cols present in D1:", {c: (c in d1.columns) for c in ("ema20", "ema50", "close_time", "time")})

d1 = d1.copy()
d1["d1_up"] = (d1["ema20"] > d1["ema50"]).astype(float)
h4c = H.align_causal(h4, d1, ["d1_up"], "_d1")
d1_up = h4c["d1_up_d1"].to_numpy() > 0.5
o = h4["open"].to_numpy()
comp, bh, bl = F5.comp_mask(h4)

# causal margin check on this population too
idx = h4c["_hidx"].to_numpy() if "_hidx" in h4c.columns else None
if idx is not None:
    ok = idx >= 0
    marg = h4["time"].to_numpy().astype(np.int64)[ok] - d1["close_time"].to_numpy().astype(np.int64)[idx[ok]]
    print(f"\n  b0/b1 causal margin (H4.open - D1.close_time): min={marg.min()/3600:.2f}h  negatives={int((marg<0).sum())}")


def M(tr):
    r = tr["R"].to_numpy(); n = len(r)
    if n == 0:
        return dict(N=0)
    eq = np.cumsum(r)
    wins, losses = r[r > 0], r[r < 0]
    def brem(f):
        k = min(int(np.ceil(n * f)), n - 1)
        return float(np.sort(r)[:n - k].mean())
    return dict(N=n, avgR=float(r.mean()), medR=float(np.median(r)),
                PF=float(wins.sum() / -losses.sum()) if len(losses) else np.inf,
                posRate=float((r > 0).mean()),
                WR_target=float((tr["exit_reason"] == "target").mean()),
                maxDD=float((eq - np.maximum.accumulate(eq)).min()),
                maxLoss=float(r.min()), best1=brem(0.01), best5=brem(0.05), best10=brem(0.10),
                med_sl_pips=float(tr["sl_pips"].median()))


def build(mask, side=+1):
    want = side > 0
    cond = comp & (d1_up == want) & mask
    raw = np.array([i for i in np.where(cond)[0] if i + 1 < len(h4)])
    if len(raw) == 0:
        return raw, raw, np.array([])
    ev = sb.dedup_events(raw, cooldown=F5.W)
    risk = np.array([o[i + 1] - bl[i] for i in ev]) if side > 0 else np.array([bh[i] - o[i + 1] for i in ev])
    ok = np.isfinite(risk) & (risk > 0)
    return raw, ev[ok], risk[ok]


print("\n" + "=" * 92)
print("  SECTION 9 -- CROSS-ERA TABLE, FROZEN RULE UNCHANGED, LONG, rr=2.0, STRESS")
print("=" * 92)
eras = [("b0 2011-2013", h4["is_b0"].to_numpy()), ("b1 2016-2018", h4["is_b1"].to_numpy()),
        ("b0+b1 pooled", (h4["is_b0"] | h4["is_b1"]).to_numpy())]
print(f"  {'era':16}{'raw':>6}{'N':>5}{'avgR':>9}{'PF':>7}{'posRate':>9}{'WRtgt':>7}{'maxDD':>8}"
      f"{'maxLoss':>9}{'best1':>8}{'best5':>8}{'best10':>8}{'medSL':>7}")
rows = {}
for nm, mask in eras:
    raw, ev, risk = build(mask)
    if len(ev) == 0:
        print(f"  {nm:16}{len(raw):6d}    0   -- no events --")
        continue
    tr = sb.simulate(h4, ev, +1, risk, rr=2.0, horizon=F5.H, scenario="STRESS")
    m = M(tr); rows[nm] = m
    print(f"  {nm:16}{len(raw):6d}{m['N']:5d}{m['avgR']:+9.3f}{m['PF']:7.2f}{m['posRate']:9.3f}"
          f"{m['WR_target']:7.3f}{m['maxDD']:8.2f}{m['maxLoss']:9.3f}{m['best1']:+8.3f}{m['best5']:+8.3f}"
          f"{m['best10']:+8.3f}{m['med_sl_pips']:7.0f}")

print(f"\n  DEV 2021-2023 reference (M5-derived H4): N=53 avgR=+0.443 PF=1.94 best10=+0.246")
print(f"  CALIB 2024 reference                   : N=24 avgR=+0.223 PF=1.47 best10=-0.030")

print("\n  SIGN-REVERSAL GATE (the lab's own broad-discovery-v2 rule, section 15 of that contract):")
print("    ELIM:SIGN_REVERSAL = one era >0 and another < -0.03, BOTH with N>=25")
vals = [("DEV", 53, 0.443), ("CALIB", 24, 0.223)]
for nm, m in rows.items():
    vals.append((nm, m["N"], m["avgR"]))
pos = [(n, N, v) for n, N, v in vals if v > 0 and N >= 25]
neg = [(n, N, v) for n, N, v in vals if v < -0.03 and N >= 25]
print(f"    eras with N>=25 and avgR>0    : {[(n, N, round(v,3)) for n, N, v in pos]}")
print(f"    eras with N>=25 and avgR<-0.03: {[(n, N, round(v,3)) for n, N, v in neg]}")
print(f"    SIGN REVERSAL TRIGGERED: {bool(pos and neg)}")

print("\n  per-year within b0/b1 (STRESS):")
raw, ev, risk = build((h4["is_b0"] | h4["is_b1"]).to_numpy())
if len(ev):
    tr = sb.simulate(h4, ev, +1, risk, rr=2.0, horizon=F5.H, scenario="STRESS")
    yrs = pd.to_datetime(tr["t_entry"], unit="s", utc=True).dt.year
    for y in sorted(yrs.unique()):
        m = M(tr[yrs == y])
        print(f"    {y}: N={m['N']:3d} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} posRate={m['posRate']:.3f}")
    tr.to_json(r"C:\Users\MEDION~1\AppData\Local\Temp\cc\ledger_b0b1.json", orient="records")
