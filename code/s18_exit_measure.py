"""MEASUREMENT ONLY (no matched-null, no holdout). For each S18 signal (h13-short, h14-short, h20-long)
compares its two exit versions (time vs rr2): matched-null p (from existing scoped_fdr run), executed-entry
overlap, and whether the wo1-driving (best) trade is the same entry. Uses the deterministic OBSERVED engine
(MS.setups + MS.simulate) on the research segment only. Reports numbers; draws no conclusion."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sc = pd.read_parquet(os.path.join(ROOT, "results", "matched_null_validation", "scoped_fdr_research.parquet"))
fr = pd.read_parquet(os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet"))
pmap = dict(zip(sc['id'], sc['final_p'].fillna(sc['p'])))

idmap = {}
for fam in MS.REGISTRY:
    for h in MS.REGISTRY[fam][0](): idmap[h['id']] = h

d = MS.load(); a = int(len(d)*0.6); res = d.iloc[:a].copy()   # research only; holdout never loaded

SIGNALS = {
    'h13-short': {'time': 'ce76669a3b2a', 'rr2': 'ba3e8d0cdb51'},
    'h14-short': {'time': '42345e7a0115', 'rr2': 'f1704085cbda'},
    'h20-long':  {'time': '2341cf9911de', 'rr2': '00d840de0b48'},
}

def trades(hid):
    h = idmap[hid]; su = MS.setups(res, h)
    tr = MS.simulate(res, su)             # observed backtest, deterministic (NOT matched-null)
    return tr   # columns R, si, ei

for sig, vers in SIGNALS.items():
    print("="*78); print(f"SIGNAL {sig}")
    trs = {ex: trades(hid) for ex, hid in vers.items()}
    for ex, hid in vers.items():
        t = trs[ex]; frr = fr[fr.id==hid].iloc[0]
        best_i = int(t['R'].idxmax()); best = t.loc[best_i]
        mean_wo_best = (t['R'].sum()-best['R'])/(len(t)-1)
        print(f"  [{ex}] id={hid} p_mn={pmap.get(hid):.3e}  n_exec={len(t)}  meanR={t['R'].mean():+.4f}  "
              f"sumR={t['R'].sum():+.2f}  wo1(FR)={frr['wo1']:+.4f}  t5(FR)={frr['t5']:.4f}")
        print(f"       best trade: ei={int(best['ei'])} R={best['R']:+.3f}  meanR_without_best={mean_wo_best:+.4f}")
    A, B = trs['time'], trs['rr2']
    eiA, eiB = set(A['ei'].astype(int)), set(B['ei'].astype(int))
    inter = eiA & eiB
    print(f"  ENTRY OVERLAP time-AND-rr2: |time|={len(eiA)} |rr2|={len(eiB)} shared={len(inter)} "
          f"({100*len(inter)/max(1,len(eiA|eiB)):.1f}% of union)  time-only={len(eiA-eiB)} rr2-only={len(eiB-eiA)}")
    bestA_ei = int(A.loc[A['R'].idxmax(),'ei']); bestB_ei = int(B.loc[B['R'].idxmax(),'ei'])
    print(f"  BEST-TRADE ENTRY: time ei={bestA_ei}  rr2 ei={bestB_ei}  SAME={bestA_ei==bestB_ei}  "
          f"| best ei in the other version's entries? time-best in rr2:{bestA_ei in eiB} rr2-best in time:{bestB_ei in eiA}")
    # for shared entries, how different is R purely due to exit
    Am = A.set_index(A['ei'].astype(int))['R']; Bm = B.set_index(B['ei'].astype(int))['R']
    sh = sorted(inter)
    if sh:
        diff = (Am.loc[sh] - Bm.loc[sh])
        print(f"  shared entries: meanR(time)={Am.loc[sh].mean():+.4f} meanR(rr2)={Bm.loc[sh].mean():+.4f} "
              f"mean|Rdiff|={diff.abs().mean():.4f} (difference is exit-only on identical entries)")
