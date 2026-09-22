"""gov_screen.py — GOVERNED GRAMMAR SCREEN at REAL live-shadow cost. Re-runs the whole governed S1-S51 strategy grammar (2448 configs, 45
families) through the ratified causal simulator (mstrat.simulate: next-open entry, stop-wins-ties, ENGINE-v2 stop floor) at the REAL round-turn
cost, multi-era + skepticism gate. TICK forced to 0.01 (the 0.1 is the known 10x bug). NOT mining: it is the campaign's own governed families scored
ONCE at real cost. Survivors = ALPHA_SURVIVOR / READY_FOR_STATISTICIAN (in-sample, materially-exposed; independent validation is the Statistician).
Arch-A HTF families = S7/S9/S11 (h4/h1 -> 15m); session = S5/S6; levels = S1/S2/S3. COST via env COST_RT_USD (round-turn $), STRESS_RT (default 0.24)."""
import os, sys, json, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery"); sys.path.insert(0, os.path.join(AA,"code"))
import mstrat; import mstrat_ext as ME
from alpha_lab import CFG
mstrat.TICK=0.01
if hasattr(ME,"TICK"): ME.TICK=0.01   # fix 10x bug in both modules
COST_RT=float(os.environ.get("COST_RT_USD","0.16")); STRESS_RT=float(os.environ.get("STRESS_RT","0.24"))
def cfg_for(rt):
    c=dict(CFG); c["spread_ticks"]=rt/(2*mstrat.TICK); c["slip_ticks"]=0.0; return c   # 2*cost = rt
CB=cfg_for(COST_RT); CS=cfg_for(STRESS_RT)
d=mstrat.load(); T=d["time"].to_numpy(); yr=pd.to_datetime(T,unit="s",utc=True).year.to_numpy(); n=len(d); YRS=(T[-1]-T[0])/(365.25*86400)
mods={};
for N in range(1,52):
    for mod in (mstrat,ME):
        if getattr(mod,f"s{N}_grammar",None) and getattr(mod,f"s{N}_setups",None): mods[N]=mod; break
print(f"COST_RT={COST_RT} STRESS_RT={STRESS_RT} | families={sorted(mods)} | TICK={mstrat.TICK}")
def score(tr_b, tr_s):
    if tr_b is None or len(tr_b)<100: return None
    r=tr_b.R.to_numpy(); ei=tr_b.ei.to_numpy(); N=len(r); yrsarr=yr[ei]
    wins=r[r>0]; los=r[r<=0]; pf=wins.sum()/(abs(los.sum())+1e-9); eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max())
    order=np.argsort(ei); rr=r[order]; th=np.array_split(rr,3); eras=[float(x.mean()) for x in th]; epos=sum(1 for x in th if x.mean()>0)
    S=np.sort(r)[::-1]; k5=max(1,int(N*0.05)); db5=float((r.sum()-S[:k5].sum())/(N-k5))
    rec=r[yrsarr>=2025]; recm=float(rec.mean()) if len(rec)>=20 else np.nan
    strs=float(tr_s.R.mean()) if (tr_s is not None and len(tr_s)>=50) else np.nan
    return dict(N=N,tpy=round(N/YRS,0),WR=round(float((r>0).mean()),3),BASE=round(float(r.mean()),4),STRESS=round(strs,4),PF=round(pf,3),
                maxDD=round(dd,1),db5=round(db5,4),era1=round(eras[0],4),era2=round(eras[1],4),era3=round(eras[2],4),epos=epos,
                worst_era=round(min(eras),4),recent=round(recm,4) if np.isfinite(recm) else None)
rows=[]; cnt=0
for N in sorted(mods):
    mod=mods[N]; grammar=getattr(mod,f"s{N}_grammar")(); setup=getattr(mod,f"s{N}_setups")
    for h in grammar:
        cnt+=1
        try: su=setup(d,h)
        except Exception: continue
        if not su or len(su)<100: continue
        try:
            tb=mstrat.simulate(d,su,CB); ts=mstrat.simulate(d,su,CS)
        except Exception: continue
        m=score(tb,ts)
        if m is None: continue
        hid=f"S{N}::"+"/".join(f"{k}={v}" for k,v in h.items() if k not in ("family",))
        survive = (m["BASE"]>0) and (m["STRESS"] is not None and np.isfinite(m["STRESS"]) and m["STRESS"]>0) and (m["PF"]>=1.15) \
                  and (m["epos"]>=2) and (m["db5"]>0) and (m["N"]>=150) and (m["recent"] is not None and m["recent"]>=0)
        rows.append(dict(hid=hid,family=f"S{N}",**m,SURVIVE=bool(survive)))
R=pd.DataFrame(rows)
R.to_csv(OUT+r"\GOV_SCREEN_ALL_RESULTS.csv",index=False)
surv=R[R.SURVIVE].copy().sort_values(["worst_era","BASE"],ascending=False)
print(f"\nscored {cnt} configs -> {len(R)} with >=100 trades | SURVIVORS (profitable at real cost, gated) = {len(surv)}")
pd.set_option("display.width",240,"display.max_columns",40)
if len(surv):
    print("\n== TOP SURVIVORS (ranked by worst-era expectancy, then BASE) ==")
    print(surv.head(15)[["hid","N","tpy","WR","BASE","STRESS","PF","worst_era","era1","era2","era3","recent","maxDD","db5"]].to_string(index=False))
    surv.to_csv(OUT+r"\GOV_SCREEN_SURVIVORS.csv",index=False)
else:
    print("\nNO SURVIVORS at real cost through the gate. Best 10 by BASE:")
    print(R.sort_values("BASE",ascending=False).head(10)[["hid","N","BASE","STRESS","PF","epos","worst_era","recent"]].to_string(index=False))
