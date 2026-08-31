"""ob_atlas.py — ORDER_BLOCK_RETEST_FACTORY_V1 census + baseline outcome (§30 counts, §17 excursion, subgroups).
Fresh first-retest, entry=limit at block edge, stop=beyond opposite edge (risk floored at 0.5 ATR, §16), target 2R.
Reports net-R by direction x era, P(+1R/+2R before -1R), MFE/MAE pips, and subgroups: displacement, target-space, depth, HTF, session.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import ob_core as OB, htf_core as HC

def eval_events(m,H1,H4,P, direction="bull", disp_min=0.75, entry_mode="close"):
    o=P["o"];h=P["h"];l=P["l"];c=P["c"];atr=P["atr"];hi100=P["hi100"];lo100=P["lo100"]
    ctxH4=H4["ctx"].values; h4imap=m["h4i"].values                    # causal H4 index per M15 bar (from htf_core)
    yr=m["dt"].dt.year.values; hr=m["dt"].dt.hour.values
    ev=OB.detect_obs(P,disp_min,direction); rows=[]
    for e in ev:
        rt=OB.first_retest(P,e)
        if rt is None: continue
        k,depth=rt; d=e["dir"]; a=atr[e["i"]]
        # CLOSE-of-retest entry (depth known => causal rejection filter, §15E); resolve from k+1
        entry=c[k]
        stop = (e["blo"]-OB.FLOOR_ATR*a) if d>0 else (e["bhi"]+OB.FLOOR_ATR*a)
        risk=abs(entry-stop)
        if risk<0.5*a: stop = entry - d*0.5*a; risk=abs(entry-stop)     # floor risk (disclose)
        if risk<=0: continue
        reject = (c[k]>e["bmid"]) if d>0 else (c[k]<e["bmid"])          # closed back beyond block mid = rejection
        out=OB.retest_outcome(P,entry,stop,d,k,2.0,resolve_from=k+1)
        if out is None: continue
        room = (hi100[k]-entry)/risk if d>0 else (entry-lo100[k])/risk
        room = max(room,0.0)
        h4i=h4imap[k]; ctx=ctxH4[h4i] if h4i>=0 else "NA"
        htf_al = "ALIGN" if ((d>0 and ctx=="TREND_UP") or (d<0 and ctx=="TREND_DOWN")) else ("COUNTER" if ((d>0 and ctx=="TREND_DOWN") or (d<0 and ctx=="TREND_UP")) else "NEUTRAL")
        H_=hr[k]; sess = "AS" if H_<8 else ("LN" if H_<13 else ("NY" if H_<20 else "LT"))
        y=yr[k]; era="D" if y<=2018 else ("C" if y<=2022 else "O")
        rows.append(dict(net=out["net_R"],g=out["gross_R"],mfe=out["mfe_R"],mae=out["mae_R"],risk=risk,
                         disp=e["disp"],depth=depth,room=room,ctx=ctx,htf=htf_al,sess=sess,era=era,k=k,dir=d,reject=int(reject)))
    return rows

def agg(rows,label):
    if len(rows)<30: print(f"{label:28s} N={len(rows)} small"); return
    net=np.array([r["net"] for r in rows]); g=np.array([r["g"] for r in rows])
    mfe=np.array([r["mfe"] for r in rows]); mae=np.array([r["mae"] for r in rows]); risk=np.array([r["risk"] for r in rows])
    era=np.array([r["era"] for r in rows])
    from tsm_core import independent_episodes
    ie=len(independent_episodes(np.array([r["k"] for r in rows]),H=OB.RETEST_WIN))
    def me(x): return net[era==x].mean() if (era==x).sum()>0 else np.nan
    p1=(mfe>=1).mean(); p2=(mfe>=2).mean()   # prob reach +1R/+2R (MFE proxy, before stop since mfe stops at barrier)
    print(f"{label:28s} N={len(rows):5d} ie={ie:4d} net={net.mean():+.3f} WR={(g>0).mean():.3f} "
          f"D={me('D'):+.3f} C={me('C'):+.3f} O={me('O'):+.3f} | P+2R={p2:.3f} MFEpip={np.median(mfe*risk)/HC.PIP:.0f} "
          f"riskpip={np.median(risk)/HC.PIP:.0f}")

def main():
    m,H1,H4,P=OB.build()
    for dd in ("bull","bear"):
        rows=eval_events(m,H1,H4,P,dd,0.75)
        print(f"\n=== {dd.upper()} OB fresh first-retest (disp>=0.75, 2R) ===")
        agg(rows,f"{dd}.ALL")
        # subgroups
        for name,key,bins in [("disp","disp",[(0.75,1.0),(1.0,1.5),(1.5,99)]),
                              ("room","room",[(0,1),(1,2),(2,3),(3,99)]),
                              ("depth","depth",[(0,0.25),(0.25,0.5),(0.5,0.75),(0.75,2)])]:
            for lo,hi in bins:
                sub=[r for r in rows if lo<=r[key]<hi]
                agg(sub,f"  {dd}.{name}[{lo},{hi})")
        for htf in ("ALIGN","NEUTRAL","COUNTER"):
            agg([r for r in rows if r["htf"]==htf], f"  {dd}.HTF_{htf}")
        for s in ("AS","LN","NY","LT"):
            agg([r for r in rows if r["sess"]==s], f"  {dd}.sess_{s}")

if __name__=="__main__":
    main()
