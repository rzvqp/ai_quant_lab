"""edge2_null.py — SECOND-EDGE search, phase 2: the MATCHED-TIMING NULL (the Statistician's decisive test) applied to the calendar-era survivors.
For each real trade (entry bar, direction, risk, rr), draw random entry bars in the SAME calendar month, same direction, same per-trade risk, same
rr, same governed simulator + real cost; REPS replicates. Edge = real_mean - null_mean; p = P(null_mean >= real_mean). A genuine edge supplies
TIMING information the month-matched null cannot; long-timing-beta does not. Reads EDGE2_CALENDAR_SURVIVORS.csv, regenerates each config, tests it."""
import os, sys, numpy as np, pandas as pd
from numpy.random import default_rng
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery"); sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, os.path.join(AA,"reports","alpha_discovery"))
import mstrat; import mstrat_ext as ME; import fh_panel
from alpha_lab import CFG
mstrat.TICK=0.01
if hasattr(ME,"TICK"): ME.TICK=0.01
d=fh_panel.build(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
month=(pd.to_datetime(T,unit="s",utc=True).to_period("M").astype(str)).to_numpy()
SB=0.05/2  # per-side (round-trip 0.05 -> 2*cost applied)
def cfg(rt): c=dict(CFG); c["spread_ticks"]=rt/(2*mstrat.TICK); c["slip_ticks"]=0.0; return c
def parse_hid(hid):
    fam,rest=hid.split("::",1); N=int(fam[1:]); h={"family":fam}
    for kv in rest.split("/"):
        k,v=kv.split("=",1)
        if v in ("True","False"): h[k]=(v=="True")
        else:
            try: h[k]=int(v)
            except:
                try: h[k]=float(v)
                except: h[k]=v
    return N,h
def sim_one(j, dirn, risk, rr, cost, horizon=48):
    """single trade entered at open[j+1] with given risk/rr, governed stop/target logic + cost."""
    ei=j+1
    if ei>=n-1: return None
    entry=O[ei]; stop=entry-dirn*risk; tgt=entry+dirn*rr*risk; end=min(ei+horizon,n-1); R=None
    for k in range(ei,end+1):
        if dirn>0:
            if L[k]<=stop: R=-1.0; break
            if H[k]>=tgt: R=float(rr); break
        else:
            if H[k]>=stop: R=-1.0; break
            if L[k]<=tgt: R=float(rr); break
    if R is None: R=dirn*(C[end]-entry)/risk
    return R - 2*cost/risk
def real_trades_of(su, cost):
    """reproduce the real ledger, keeping (ei, dir, risk, rr) for rr-exit trades."""
    o=O; last=-1; out=[]
    for s in sorted(su,key=lambda x:x["ei"]):
        ei=s["ei"]; si=s["si"]
        if ei<=last or ei>=n-1 or ei<1: continue
        dirn=s["dir"]; entry=o[ei]; stop=s["stop"]; risk=abs(entry-stop)
        if not np.isfinite(risk) or ATR[si]<=0 or np.isnan(ATR[si]): continue
        min_exec=max(2*cfg(0.05)["spread_ticks"]*mstrat.TICK,5*mstrat.TICK,0.10*ATR[si])
        if risk<min_exec: risk=min_exec; stop=entry-dirn*risk
        ek=s["exit_kind"]; ep=s.get("exit_param"); to=int(ep) if ek=="time" else 48
        rr=float(ep) if ek=="rr" else None
        # realize real R (for real_mean) with governed engine
        tgt=entry+dirn*ep*risk if ek=="rr" else (ep if ek in ("opp_liq","opp_struct") else None); ex=None; xi=None
        for jj in range(ei,min(ei+to,n)):
            if dirn>0:
                if L[jj]<=stop: ex=stop;xi=jj;break
                if tgt is not None and np.isfinite(tgt) and H[jj]>=tgt: ex=tgt;xi=jj;break
            else:
                if H[jj]>=stop: ex=stop;xi=jj;break
                if tgt is not None and np.isfinite(tgt) and L[jj]<=tgt: ex=tgt;xi=jj;break
        if ex is None: xi=min(ei+to,n-1); ex=C[xi]
        realR=(dirn*(ex-entry)-2*cost)/risk
        out.append(dict(ei=ei,dir=dirn,risk=risk,rr=rr,to=to,realR=realR)); last=xi
    return out
def matched_null(su, cost, reps=300, seed=7):
    rt=real_trades_of(su,cost)
    rr_tr=[t for t in rt if t["rr"] is not None]
    if len(rr_tr)<100: return None
    real_mean=float(np.mean([t["realR"] for t in rt]))  # full ledger real expectancy (net)
    # month -> eligible entry bars
    mbars={}
    for i in range(60,n-50): mbars.setdefault(month[i],[]).append(i)
    rng=default_rng(seed); null_means=[]
    for _ in range(reps):
        rs=[]
        for t in rr_tr:
            cand=mbars.get(month[t["ei"]])
            if not cand: continue
            j=int(rng.choice(cand)); R=sim_one(j,t["dir"],t["risk"],t["rr"],cost,horizon=t["to"])
            if R is not None: rs.append(R)
        if rs: null_means.append(float(np.mean(rs)))
    null_means=np.array(null_means); real_rr_mean=float(np.mean([t["realR"] for t in rr_tr]))
    p=float((null_means>=real_rr_mean).mean())
    return dict(N=len(rt),N_rr=len(rr_tr),real_mean=round(real_mean,4),real_rr_mean=round(real_rr_mean,4),
                null_mean=round(float(null_means.mean()),4),excess=round(real_rr_mean-float(null_means.mean()),4),
                null_captures_pct=round(100*float(null_means.mean())/(real_rr_mean+1e-9),0),p=round(p,4))
if __name__=="__main__":
    surv=pd.read_csv(OUT+r"\EDGE2_CALENDAR_SURVIVORS.csv")
    # dedup identical by (family, BASE, N)
    surv=surv.drop_duplicates(subset=["family","N","BASE","e1","e2","e3"]).sort_values("worst",ascending=False)
    print(f"matched-timing null on {len(surv)} distinct calendar-era survivors (real cost 0.05, reps=300)\n")
    res=[]
    for _,row in surv.head(15).iterrows():
        try:
            Nf,h=parse_hid(row["hid"]); mod=mstrat if getattr(mstrat,f"s{Nf}_setups",None) else ME
            su=getattr(mod,f"s{Nf}_setups")(d,h); m=matched_null(su,0.025)
        except Exception as e: m=None; print(f"ERR {row['hid'][:50]}: {e}")
        if m is None: continue
        verdict="EDGE (beats null)" if (m["p"]<0.05 and m["excess"]>0) else "long-timing-beta (fails null)"
        print(f"{row['hid'][:60]:60s} real={m['real_rr_mean']:+.4f} null={m['null_mean']:+.4f} excess={m['excess']:+.4f} null_capt={m['null_captures_pct']:.0f}% p={m['p']:.4f} -> {verdict}")
        res.append(dict(hid=row['hid'],family=row['family'],**m,verdict=verdict))
    pd.DataFrame(res).to_csv(OUT+r"\EDGE2_MATCHED_NULL.csv",index=False)
