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
d=mstrat.load(); o=d['open'].values; hi=d['high'].values; lo=d['low'].values; atr=d['m_atr'].values
T={}
for N in range(1,52):
    for mod in (mstrat,ME):
        g=getattr(mod,f"s{N}_grammar",None); s=getattr(mod,f"s{N}_setups",None)
        if not(g and s): continue
        for h in g():
            if h['id'] in ("85dfa65a9ce1","047d776a1bcb","601e20753a4a"): T[h['id']]=(f"S{N}",mod,h,s)
        break
print("="*112); print("  ACEEASI PATOLOGIE ATINGE CANDIDATII? (stop de partea gresita / atins pe bara de intrare)"); print("="*112)
for hid,(fam,mod,h,sfn) in T.items():
    su=sfn(d,h); bad=0; sb=0; floor=0; risks=[]
    for s in su:
        ei=s['ei']
        if ei>=len(d)-1 or ei<1: continue
        dirn=s['dir']; entry=o[ei]; stop=s['stop']; risk=abs(entry-stop)
        if not np.isfinite(risk) or np.isnan(atr[s['si']]) or atr[s['si']]<=0: continue
        if (dirn>0 and stop>=entry) or (dirn<0 and stop<=entry): bad+=1
        me=max(2*CB['spread_ticks']*mstrat.TICK,5*mstrat.TICK,0.10*atr[s['si']])
        if risk<me: floor+=1
        risks.append(max(risk,me))
        if dirn>0 and lo[ei]<=min(stop,entry-me): sb+=1
        elif dirn<0 and hi[ei]>=max(stop,entry+me): sb+=1
    tot=len(risks)
    print(f"  {fam:4} {hid}: setup-uri valide {tot:6d} | stop partea gresita {bad} ({bad/max(tot,1):.2%}) | "
          f"prins de podea {floor} ({floor/max(tot,1):.2%}) | stop pe bara de intrare {sb} ({sb/max(tot,1):.2%})")
    print(f"       risc median {np.median(risks):.3f} USD ({np.median(risks)/0.10:.1f} pipi) | cost BASE 0.05 = {0.05/np.median(risks):.3f} R")
print("\n"+"="*112); print("  CRONOMETRARE"); print("="*112)
t0=time.time(); n=0
for N in (1,9,20,17):
    mod=mstrat if getattr(mstrat,f"s{N}_grammar",None) else ME
    g=getattr(mod,f"s{N}_grammar")(); sfn=getattr(mod,f"s{N}_setups")
    for h2 in g[:5]:
        try:
            su2=sfn(d,h2)
            if su2 and len(su2)>=100: mstrat.simulate(d,su2,CB); n+=1
        except Exception: pass
el=time.time()-t0
print(f"  {n} configuratii in {el:.1f}s -> {el/max(n,1):.2f}s/config -> 2270 (x2 pentru BASE+STRESS) ~ {2*2270*el/max(n,1)/60:.0f} min")
