import os,sys,time,numpy as np,pandas as pd
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; sys.path.insert(0,os.path.join(AA,"code"))
import mstrat, mstrat_ext as ME
from alpha_lab import CFG
mstrat.TICK=0.01
if hasattr(ME,"TICK"): ME.TICK=0.01
def cfg_for(rt):
    c=dict(CFG); c["spread_ticks"]=rt/(2*mstrat.TICK); c["slip_ticks"]=0.0; return c
CB=cfg_for(0.05)
d=mstrat.load(); o=d['open'].values; hi=d['high'].values; lo=d['low'].values
print("="*112); print("  S49 stop=bar — patologia, verificata direct din dict-urile de setup"); print("="*112)
h=[x for x in ME.s49_grammar() if x['id']=='27bbc9f88f34'][0]
print(f"  spec: { {k:v for k,v in h.items() if k not in ('family','id')} }")
su=ME.s49_setups(d,h)
print(f"  setup-uri generate: {len(su)}")
bad=0; samebar=0
for s in su[:20000]:
    ei=s['ei']; dirn=s['dir']; entry=o[ei]; stop=s['stop']
    if (dirn>0 and stop>=entry) or (dirn<0 and stop<=entry): bad+=1
    if dirn>0 and lo[ei]<=stop: samebar+=1
    elif dirn<0 and hi[ei]>=stop: samebar+=1
print(f"  din primele 20.000 setup-uri:")
print(f"    STOP DE PARTEA GRESITA a intrarii (stop>=entry pentru long): {bad}  ({bad/200:.1f}%)")
print(f"    stop atins CHIAR pe bara de intrare:                        {samebar}  ({samebar/200:.1f}%)")
tb=mstrat.simulate(d,su,CB)
hold=(tb.ei.to_numpy()[1:]-tb.ei.to_numpy()[:-1])
print(f"  tranzactii simulate: {len(tb)}   R median={tb.R.median():.4f}  R mean={tb.R.mean():.4f}")
print(f"  distributie R (cuantile): {np.round(np.quantile(tb.R,[0,.05,.25,.5,.75,.95,1]),3).tolist()}")
print(f"  fractiune R exact = -1 (stop pur): {float((np.abs(tb.R+1)<0.06).mean()):.3f}")
print("\n  => confirm: stopul cade de partea gresita, deci 'riscul' e minuscul/inversat si e prins de")
print("     podeaua ENGINE-v2; R devine un raport cu numitor artificial. NU e un edge. RESPINGERE CONFIRMATA.")
print("\n"+"="*112); print("  CRONOMETRARE pentru rularea completa a gramaticii"); print("="*112)
t0=time.time(); n=0
for N in (1,9,20):
    mod=mstrat if N in (1,9) else ME
    g=getattr(mod,f"s{N}_grammar")(); sfn=getattr(mod,f"s{N}_setups")
    for h2 in g[:6]:
        try:
            su2=sfn(d,h2)
            if su2 and len(su2)>=100: mstrat.simulate(d,su2,CB); n+=1
        except Exception: pass
el=time.time()-t0
print(f"  {n} configuratii in {el:.1f}s -> ~{el/max(n,1):.2f}s/config -> 2270 configuratii ~ {2270*el/max(n,1)/60:.1f} min")
