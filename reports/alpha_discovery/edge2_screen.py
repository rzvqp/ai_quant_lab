"""edge2_screen.py — SECOND-EDGE search, phase 1: re-screen the governed S1-S51 grammar on the FULL-HISTORY causal panel (fh_panel, fixes the
2023+ truncation) at REAL cost, gated by the decisive discriminator the Statistician's review implied: POSITIVE IN ALL THREE CALENDAR ERAS
(2011-16 / 2017-21 / 2022-26) — the S5 property that a current-regime long-beta candidate cannot have. Real cost BASE 0.05 / STRESS 0.24, TICK 0.01.
Survivors go to the matched-timing-null test (edge2_null.py). NOT mining: governed families, correct null-motivated gate, scored once."""
import os, sys, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery"); sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, os.path.join(AA,"reports","alpha_discovery"))
import mstrat; import mstrat_ext as ME; import fh_panel
from alpha_lab import CFG
mstrat.TICK=0.01
if hasattr(ME,"TICK"): ME.TICK=0.01
d=fh_panel.build(); T=d["time"].to_numpy(); yr=pd.to_datetime(T,unit="s",utc=True).year.to_numpy(); n=len(d); YRS=(T[-1]-T[0])/(365.25*86400)
def cfg(rt): c=dict(CFG); c["spread_ticks"]=rt/(2*mstrat.TICK); c["slip_ticks"]=0.0; return c
CB=cfg(0.05); CS=cfg(0.24)
mods={}
for N in range(1,52):
    for mod in (mstrat,ME):
        if getattr(mod,f"s{N}_grammar",None) and getattr(mod,f"s{N}_setups",None): mods[N]=mod; break
print(f"full-history panel | families={sorted(mods)} | screening at real cost, CALENDAR-era gate")
def score(tb, ts):
    if tb is None or len(tb)<150: return None
    r=tb.R.to_numpy(); ei=tb.ei.to_numpy(); N=len(r); y=yr[ei]
    wins=r[r>0]; los=r[r<=0]; pf=wins.sum()/(abs(los.sum())+1e-9); eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max())
    e1=r[y<=2016]; e2=r[(y>=2017)&(y<=2021)]; e3=r[y>=2022]
    if len(e1)<20 or len(e2)<20 or len(e3)<20: return None
    m1,m2,m3=float(e1.mean()),float(e2.mean()),float(e3.mean())
    S=np.sort(r)[::-1]; k5=max(1,int(N*0.05)); db5=float((r.sum()-S[:k5].sum())/(N-k5))
    strs=float(ts.R.mean()) if (ts is not None and len(ts)>=100) else np.nan
    return dict(N=N,tpy=round(N/(YRS if YRS>0 else 1),0),WR=round(float((r>0).mean()),3),BASE=round(float(r.mean()),4),STRESS=round(strs,4),PF=round(pf,3),maxDD=round(dd,1),
                e1=round(m1,4),e2=round(m2,4),e3=round(m3,4),worst=round(min(m1,m2,m3),4),db5=round(db5,4),n1=len(e1),n2=len(e2),n3=len(e3))
rows=[]; cnt=0
for Nf in sorted(mods):
    mod=mods[Nf]; grammar=getattr(mod,f"s{Nf}_grammar")(); setup=getattr(mod,f"s{Nf}_setups")
    for h in grammar:
        cnt+=1
        try: su=setup(d,h)
        except Exception: continue
        if not su or len(su)<150: continue
        try: tb=mstrat.simulate(d,su,CB); ts=mstrat.simulate(d,su,CS)
        except Exception: continue
        m=score(tb,ts)
        if m is None: continue
        hid=f"S{Nf}::"+"/".join(f"{k}={v}" for k,v in h.items() if k!="family")
        # DECISIVE gate: profitable at real cost AND positive in ALL 3 calendar eras
        gate = (m["BASE"]>0) and (m["STRESS"]>0) and (m["PF"]>=1.15) and (m["e1"]>0) and (m["e2"]>0) and (m["e3"]>0) and (m["db5"]>0)
        rows.append(dict(hid=hid,family=f"S{Nf}",**m,GATE=bool(gate)))
        if gate and len(tb): tb.to_parquet(OUT+rf"\_edge2_{hid.split('::')[0]}_{abs(hash(hid))%10**8}.parquet")
R=pd.DataFrame(rows); R.to_csv(OUT+r"\EDGE2_FULLHIST_SCREEN.csv",index=False)
g=R[R.GATE].copy().sort_values(["worst","STRESS"],ascending=False)
pd.set_option("display.width",240,"display.max_columns",40)
print(f"\nscored {cnt} | {len(R)} with N>=150 & 3-era-sample | ALL-CALENDAR-ERA-POSITIVE survivors = {len(g)}")
if len(g):
    print(g.head(20)[["hid","family","N","WR","BASE","STRESS","PF","e1","e2","e3","worst","db5"]].to_string(index=False))
    g.to_csv(OUT+r"\EDGE2_CALENDAR_SURVIVORS.csv",index=False)
    print("\nfamilies among survivors:", g.family.value_counts().to_dict())
else:
    print("NONE positive in all 3 calendar eras. Best by worst-era:")
    print(R.sort_values("worst",ascending=False).head(12)[["hid","N","BASE","STRESS","PF","e1","e2","e3","worst"]].to_string(index=False))
