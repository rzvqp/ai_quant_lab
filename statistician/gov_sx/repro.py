"""STAT-GOVERNED-Sx-VALIDATION — §2 exact reproduction of the three candidates + the S49 rejection."""
import os, sys, json
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
sys.path.insert(0, os.path.join(AA, "code"))
import mstrat, mstrat_ext as ME
from alpha_lab import CFG
mstrat.TICK = 0.01
if hasattr(ME, "TICK"): ME.TICK = 0.01
COST_RT, STRESS_RT = 0.05, 0.24
def cfg_for(rt):
    c = dict(CFG); c["spread_ticks"] = rt / (2 * mstrat.TICK); c["slip_ticks"] = 0.0; return c
CB, CS = cfg_for(COST_RT), cfg_for(STRESS_RT)
d = mstrat.load()
T = d["time"].to_numpy(); yr = pd.to_datetime(T, unit="s", utc=True).year.to_numpy()
YRS = (T[-1] - T[0]) / (365.25 * 86400)
print(f"  panel: {len(d)} bars  {pd.to_datetime(T[0],unit='s',utc=True)} -> {pd.to_datetime(T[-1],unit='s',utc=True)}  ({YRS:.2f} yr)")
print(f"  TICK={mstrat.TICK}  BASE round-turn={COST_RT}  STRESS={STRESS_RT}")
print(f"  spread_ticks BASE={CB['spread_ticks']}  STRESS={CS['spread_ticks']}  slip=0")
print(f"  -> cost per side = (spread+slip)*TICK = {(CB['spread_ticks']+CB['slip_ticks'])*mstrat.TICK:.4f}; R subtracts 2*cost = {COST_RT}")

TARGET = {"85dfa65a9ce1": ("S1", mstrat), "047d776a1bcb": ("S9", mstrat), "601e20753a4a": ("S20", ME)}
found = {}
for N in range(1, 52):
    for mod in (mstrat, ME):
        g = getattr(mod, f"s{N}_grammar", None); s = getattr(mod, f"s{N}_setups", None)
        if not (g and s): continue
        for h in g():
            if h["id"] in TARGET:
                found[h["id"]] = (N, mod, h, s)
        break
print(f"\n  grammar ids resolved: {sorted(found)}  (expected 3)")
for k, (fam, _) in TARGET.items():
    if k in found: print(f"    {k} -> S{found[k][0]}  spec={ {a:b for a,b in found[k][2].items() if a not in ('family','id')} }")
    else: print(f"    {k} -> NOT FOUND IN GRAMMAR")

def score(tb, ts):
    r = tb.R.to_numpy(); ei = tb.ei.to_numpy(); N = len(r); ya = yr[ei]
    w = r[r > 0]; l = r[r <= 0]; pf = w.sum() / (abs(l.sum()) + 1e-9)
    eq = np.cumsum(r); dd = float((np.maximum.accumulate(eq) - eq).max())
    order = np.argsort(ei); rr = r[order]; th = np.array_split(rr, 3)
    eras = [float(x.mean()) for x in th]; epos = sum(1 for x in th if x.mean() > 0)
    S = np.sort(r)[::-1]; k5 = max(1, int(N * 0.05)); db5 = float((r.sum() - S[:k5].sum()) / (N - k5))
    rec = r[ya >= 2025]; recm = float(rec.mean()) if len(rec) >= 20 else np.nan
    strs = float(ts.R.mean()) if (ts is not None and len(ts) >= 50) else np.nan
    return dict(N=N, tpy=round(N / YRS, 0), WR=round(float((r > 0).mean()), 3), BASE=round(float(r.mean()), 4),
                STRESS=round(strs, 4), PF=round(pf, 3), maxDD=round(dd, 1), db5=round(db5, 4),
                eras=[round(e, 4) for e in eras], epos=epos, recent=round(recm, 4))

CLAIM = {"85dfa65a9ce1": dict(BASE=0.222, STRESS=0.166, PF=1.39, WR=0.39, N=322, recent=0.285),
         "047d776a1bcb": dict(BASE=0.165, STRESS=0.146, PF=1.37, WR=0.46, N=665, recent=0.252),
         "601e20753a4a": dict(BASE=0.161, STRESS=0.119, PF=1.24, WR=0.32, N=777, recent=0.194)}
print("\n" + "=" * 118); print("  §2 REPRODUCERE EXACTA"); print("=" * 118)
RES = {}
for hid, (Nfam, mod, h, sfn) in found.items():
    su = sfn(d, h)
    tb = mstrat.simulate(d, su, CB); ts = mstrat.simulate(d, su, CS)
    m = score(tb, ts); RES[hid] = dict(m=m, tb=tb, ts=ts, su=su, fam=f"S{Nfam}", h=h)
    c = CLAIM[hid]
    ok = (abs(m["BASE"] - c["BASE"]) < 0.002 and abs(m["STRESS"] - c["STRESS"]) < 0.002 and
          abs(m["PF"] - c["PF"]) < 0.02 and m["N"] == c["N"] and abs(m["recent"] - c["recent"]) < 0.002)
    print(f"\n  {hid}  {RES[hid]['fam']}")
    print(f"    reprodus : N={m['N']:4d} tpy={m['tpy']:.0f} WR={m['WR']:.3f} BASE={m['BASE']:+.4f} STRESS={m['STRESS']:+.4f} "
          f"PF={m['PF']:.3f} recent={m['recent']:+.4f} db5={m['db5']:+.4f} eras={m['eras']} epos={m['epos']} maxDD={m['maxDD']}")
    print(f"    revendicat: N={c['N']:4d}               WR={c['WR']:.2f}  BASE={c['BASE']:+.3f} STRESS={c['STRESS']:+.3f} "
          f"PF={c['PF']:.2f}  recent={c['recent']:+.3f}")
    print(f"    -> REPRODUCED_EXACT = {'DA' if ok else 'NU'}")
    tr = tb.copy(); tr["year"] = yr[tb.ei.to_numpy()]
    print(f"    ani acoperiti (an intrare->iesire): {int(tr.year.min())}..{int(tr.year.max())}   "
          f"distributie: {tr.year.value_counts().sort_index().to_dict()}")
    tr.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"trades_{hid}.csv"), index=False)
json.dump({k: v["m"] for k, v in RES.items()}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "repro.json"), "w"), indent=1)
