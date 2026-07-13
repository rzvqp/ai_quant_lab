import numpy as np, s1, mstrat as MS
d=MS.load(); res=d.iloc[:int(len(d)*0.6)].copy()
hs1=dict(side='low',liq_ref='pdh_pdl',liq_lb=None,confirm='consecutive2',imb='fvg',entry='market',stop='beyond_sweep',exit='rr2',window=4)
hms=dict(family='S1',side='low',liq_ref='pdh_pdl',liq_lb=None,confirm='consecutive2',imb='fvg',stop='beyond_sweep',exit='rr2',window=4)
# standalone ledger (monolithic s1._trades): returns Rs, eis
Rs_s,ei_s=s1._trades(res,hs1,MS.CFG)
# unified ledger: mstrat setups -> shared simulate
tr=MS.backtest(res,hms); ei_u=tr['ei'].tolist(); Rs_u=tr['R'].tolist()
A=dict(zip(ei_s,Rs_s)); B=dict(zip(ei_u,Rs_u))
setA=set(ei_s); setB=set(ei_u)
identical=[e for e in setA&setB if abs(A[e]-B[e])<1e-9]
same_diff=[e for e in setA&setB if abs(A[e]-B[e])>=1e-9]
only_s=sorted(setA-setB); only_u=sorted(setB-setA)
print(f"standalone n={len(ei_s)}  unified n={len(ei_u)}")
print(f"identical (same entry_idx & R): {len(identical)}")
print(f"same entry_idx, different R: {len(same_diff)}")
print(f"only in standalone: {len(only_s)}  only in unified: {len(only_u)}")
# investigate cause: standalone skip uses signal t0<=last; unified uses entry ei<=last
# show a few only-unified entries and their preceding standalone trade
def ctx(e,src):
    return f"entry_idx={e}"
print("only_unified entries:", only_u[:8])
print("only_standalone entries:", only_s[:8])
# Are the 'only' entries cases where entry overlaps a prior open trade under one skip rule?
# reconstruct standalone exits to see overlap
print("\nCAUSE PROBE: standalone skips next SWEEP if signal_idx<=last_exit; unified skips next ENTRY if entry_idx<=last_exit.")
# count how many only-unified entries fall while a standalone trade was still open
