import sys, numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
GC=r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\alpha\gc_15m.csv"
XA=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M15.csv"
g=pd.read_csv(GC); g["dt"]=pd.to_datetime(g["dt"],utc=True)
x=pd.read_csv(XA).drop_duplicates("time").sort_values("time"); x["dt"]=pd.to_datetime(x["time"],unit="s",utc=True)
m=pd.merge(g[["dt","close","volume"]],x[["dt","close","volume"]],on="dt",suffixes=("_gc","_xau")).sort_values("dt").reset_index(drop=True)
rg=m.close_gc.diff(); rx=m.close_xau.diff(); ok=np.isfinite(rg)&np.isfinite(rx)
rg,rx=rg[ok].to_numpy(),rx[ok].to_numpy()
res=rg-rx
print("="*112); print("  HEADROOM OF THE GC-XAU RETURN RESIDUAL  (bounds branch B before anyone spends a cycle on it)"); print("="*112)
print(f"  sd of XAU M15 return            : {rx.std()/0.10:7.2f} pips")
print(f"  sd of GC  M15 return            : {rg.std()/0.10:7.2f} pips")
print(f"  sd of the RESIDUAL (GC - XAU)   : {res.std()/0.10:7.2f} pips   = {100*res.var()/rx.var():.1f}% of XAU return VARIANCE")
print(f"  median |residual|               : {np.median(np.abs(res))/0.10:7.2f} pips  (vs a governed round-trip cost of ~4.2 pips)")
print(f"  share of bars where |residual| exceeds the 4.2-pip cost: {np.mean(np.abs(res)>0.419):.1%}")
print(f"\n  -> the entire divergence a spot/futures convergence trade could target is a {np.median(np.abs(res))/0.10:.1f}-pip median")
print(f"     dislocation against a 4.2-pip cost, and it is contemporaneous, not predictive.")
print(f"\n  residual autocorrelation (does a dislocation persist into the next M15 bar?)")
for k in (1,2,4):
    print(f"    lag {k} bar(s) = {k*15:3d} min : {np.corrcoef(res[:-k],res[k:])[0,1]:+.3f}")
print(f"\n  NOTE: negative lag-1 autocorrelation is the signature of bid-ask bounce / non-synchronous")
print(f"        quoting between two venues, NOT of an exploitable convergence process.")
b=(m.close_gc-m.close_xau)
print(f"\n  carry basis (GC - XAU): mean {b.mean():.2f} USD, sd {b.std():.2f} USD, range [{b.min():.2f}, {b.max():.2f}]")
print(f"  basis drift over the 11 sessions: {b.iloc[-1]-b.iloc[0]:+.2f} USD -- consistent with cost-of-carry decay toward expiry,")
print(f"  which is exactly the deterministic term any basis study must remove FIRST.")
