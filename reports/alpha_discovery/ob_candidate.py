"""ob_candidate.py — ORDER_BLOCK_RETEST_FACTORY_V1: can a CAUSALLY-SELECTABLE OB cell reach positive net-R that beats controls cross-era?
Filters known before the retest: displacement bucket, retest session, target-space. Targets 1R/2R/3R. For each cell report net-R, WR, PF,
era D/C/O, DEV/OOS, best-trade-removed, N, indep-episodes, MFE pips — AND the matched CONTROL_C net-R in the SAME cell (incremental test).
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import ob_core as OB, htf_core as HC
from ob_contrast import limit_fill
from tsm_core import independent_episodes

def collect(P, m, direction, disp_min, tgtR):
    atr=P["atr"]; hi100=P["hi100"]; lo100=P["lo100"]; hr=m["dt"].dt.hour.values; yr=m["dt"].dt.year.values
    ev=OB.detect_obs(P,disp_min,direction); rows=[]
    for e in ev:
        d=e["dir"]; i=e["i"]; a=atr[i]
        lvl=e["bhi"] if d>0 else e["blo"]; stop=(e["blo"]-OB.FLOOR_ATR*a) if d>0 else (e["bhi"]+OB.FLOOR_ATR*a)
        if abs(lvl-stop)<0.5*a: stop=lvl-d*0.5*a
        k=limit_fill(P,e,lvl,d,i)
        if k is None: continue
        risk=abs(lvl-stop); room=(hi100[k]-lvl)/risk if d>0 else (lvl-lo100[k])/risk
        o=OB.retest_outcome(P,lvl,stop,d,k,tgtR,resolve_from=k)
        if o is None: continue
        # matched CONTROL_C in same event
        lc=e["bos_close"]-d*1.0*a; sc=lc-d*1.0*a; kc=limit_fill(P,e,lc,d,i)
        cc=None
        if kc is not None:
            oc=OB.retest_outcome(P,lc,sc,d,kc,tgtR,resolve_from=kc)
            if oc is not None: cc=oc["net_R"]
        H_=hr[k]; sess="AS" if H_<8 else ("LN" if H_<13 else ("NY" if H_<20 else "LT"))
        y=yr[k]; era="D" if y<=2018 else ("C" if y<=2022 else "O")
        rows.append(dict(net=o["net_R"],g=o["gross_R"],risk=risk,room=max(room,0),disp=e["disp"],sess=sess,era=era,k=k,cc=cc,mfe=o["mfe_R"]))
    return rows

def rep(rows,label,ctrl=True):
    if len(rows)<40: print(f"{label:40s} N={len(rows)} small"); return
    net=np.array([r["net"] for r in rows]); g=np.array([r["g"] for r in rows]); risk=np.array([r["risk"] for r in rows])
    era=np.array([r["era"] for r in rows]); k=np.array([r["k"] for r in rows]); mfe=np.array([r["mfe"] for r in rows])
    wins=g[g>0].sum() if (g>0).any() else 0; loss=-g[g<0].sum() if (g<0).any() else 1e-9
    pf=(g[g>0].sum())/(abs(g[g<0].sum())+1e-9)
    def me(x): return net[era==x].mean() if (era==x).sum()>0 else np.nan
    ie=len(independent_episodes(k,H=OB.RETEST_WIN)); bestrm=(net.sum()-net.max())/(len(net)-1)
    cc=[r["cc"] for r in rows if r["cc"] is not None]; ccm=np.mean(cc) if cc else np.nan
    incr = net.mean()-ccm if cc else np.nan
    print(f"{label:40s} N={len(net):4d} ie={ie:4d} net={net.mean():+.3f} WR={(g>0).mean():.3f} PF={pf:.2f} "
          f"D={me('D'):+.3f} C={me('C'):+.3f} O={me('O'):+.3f} bestrm={bestrm:+.3f} vsCTRL={incr:+.3f} MFEpip={np.median(mfe*risk)/HC.PIP:.0f}")

def main():
    m,H1,H4,P=OB.build()
    for dd in ("bull","bear"):
        print(f"\n########## {dd.upper()} ##########")
        for tg in (1.0,2.0,3.0):
            rows=collect(P,m,dd,1.5,tg)   # displacement>=1.5 (causally selectable)
            print(f"-- disp>=1.5, target {tg}R --")
            rep(rows,f"{dd}.disp15.all.{tg}R")
            for s in ("LN","NY"):
                rep([r for r in rows if r["sess"]==s], f"{dd}.disp15.{s}.{tg}R")
            rep([r for r in rows if r["sess"] in ("LN","NY")], f"{dd}.disp15.LN+NY.{tg}R")
            rep([r for r in rows if r["room"]>=2], f"{dd}.disp15.room>=2.{tg}R")

if __name__=="__main__":
    main()
