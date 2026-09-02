"""ob_exec_compare.py — §20 primary comparison for OB_CAUSAL_EXECUTION_FACTORY_V1.
Reproduce the OLD fill artifact, run EXEC-A/B/C/D corrected, timing-matched controls (block shifted by its height), era/DEV/OOS/outlier/
cost/same-bar-ambiguity. cur_data M15, bull, disp>=1.5, LN+NY, 2R, conservative same-bar ordering.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import ob_core as OB, htf_core as HC, ob_exec as EX
from tsm_core import independent_episodes

def shifted_event(e):
    bh=e["bhi"]-e["blo"]; s=dict(e); s["blo"]=e["blo"]+bh; s["bhi"]=e["bhi"]+bh; s["bmid"]=(s["blo"]+s["bhi"])/2; return s

def collect_ctrl(P,m,mode,disp_min=1.5,session=("LN","NY")):
    atr=P["atr"]; hr=m["dt"].dt.hour.values; yr=m["dt"].dt.year.values
    ev=OB.detect_obs(P,disp_min,"bull"); rows=[]
    for e0 in ev:
        e=shifted_event(e0); a=atr[e["i"]]; stop=EX.stop_of(e,a)
        r=EX.exec_entry(P,e,mode)
        if r is None: continue
        entry,start=r; H_=hr[min(start,len(hr)-1)]; ss="AS" if H_<8 else ("LN" if H_<13 else ("NY" if H_<20 else "LT"))
        if ss not in session: continue
        if entry-stop<=0: continue
        risk=entry-stop
        if risk<0.5*a: stop=entry-0.5*a
        out=EX.resolve(P,entry,stop,1,start,2.0)
        if out is None: continue
        rows.append(out[0])
    return np.array(rows)

def stats(rows):
    net=np.array([r["net"] for r in rows]); g=np.array([r["g"] for r in rows]); era=np.array([r["era"] for r in rows])
    y=np.array([r["y"] for r in rows]); k=np.array([r["k"] for r in rows]); amb=np.array([r["amb"] for r in rows])
    pf=(g[g>0].sum())/(abs(g[g<0].sum())+1e-9); dev=y<=2018
    def me(x): return net[era==x].mean() if (era==x).sum()>0 else float('nan')
    ie=len(independent_episodes(k,H=OB.RETEST_WIN)); best1=(net.sum()-np.sort(net)[-max(1,len(net)//100):].sum())/(len(net)-max(1,len(net)//100))
    # max drawdown on equity (sequential by entry bar)
    order=np.argsort(k); eq=np.cumsum(net[order]); dd=np.max(np.maximum.accumulate(eq)-eq) if len(eq) else 0
    return dict(N=len(net),ie=ie,net=net.mean(),wr=(g>0).mean(),pf=pf,D=me('D'),C=me('C'),O=me('O'),
                dev=net[dev].mean() if dev.sum() else float('nan'),oos=net[~dev].mean() if (~dev).sum() else float('nan'),
                best1=best1,dd=dd,amb=int(amb.sum()),harsh=(g-0.24-0.15).mean(),medstop=np.median([r["risk"] for r in rows])/HC.PIP,
                mfe=np.median([r["mfe"] for r in rows]))

def main():
    m,H1,H4,P=OB.build()
    print("=== OLD fill artifact reproduction ===")
    old=EX.collect(P,m,"OLD"); os=stats(old)
    print(f"OLD_BUGGY_FILL   N={os['N']} net={os['net']:+.3f}  (drops same-bar filled-then-closed-below losers)")
    print("=== corrected causal executions ===")
    res={}
    for mode,name in [("A","EXEC_A_true_limit"),("B","EXEC_B_retestclose_next"),("C","EXEC_C_reject_next"),("D","EXEC_D_pen_reclaim_next")]:
        rows=EX.collect(P,m,mode)
        if len(rows)<40: print(f"{name}: N={len(rows)} small"); continue
        s=stats(rows); res[mode]=(s,rows)
        ctrl=collect_ctrl(P,m,mode); cnet=ctrl.mean() if len(ctrl)>=40 else float('nan')
        incr=s['net']-cnet
        print(f"{name:26s} N={s['N']:4d} ie={s['ie']:4d} net={s['net']:+.3f} WR={s['wr']:.3f} PF={s['pf']:.2f} "
              f"D={s['D']:+.3f} C={s['C']:+.3f} O={s['O']:+.3f} DEV={s['dev']:+.3f} OOS={s['oos']:+.3f} "
              f"best1rm={s['best1']:+.3f} ctrl={cnet:+.3f} OB-ctrl={incr:+.3f} harsh={s['harsh']:+.3f} amb={s['amb']} "
              f"stop={s['medstop']:.0f}pip MFE={s['mfe']:.1f}R DD={s['dd']:.1f}R")

if __name__=="__main__":
    main()
