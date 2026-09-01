"""sc_L1_strat.py — minimal strategy interpretations of L1 (London expansion/timing gate). L1 is direction-symmetric (P(+100 first)=0.507),
so the ONLY plausible monetizable form is conditional-response: L1 gate -> a SECOND causal event reveals direction -> continuation.
Interpretations (<=3): A) London-gated displacement-revealed continuation ; B) London directional bias (should fail, P~0.5) ;
C) L1 as non-directional timing filter (not a standalone trade). Matched control = SAME conditional-response at the non-London baseline.
No optimization. Conservative same-bar (m5_core.resolve). Native M5. 1 pip=$0.10.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import m5_core as MC, sc_L1 as L1

D_TRIG_PIP=50   # second event = first 50-pip displacement from the anchor (reveals direction)
WIN=48          # look for the trigger within 48 M5 bars (~4h) after the anchor

def gated_continuation(M, anchors):
    """From each anchor bar, wait for first +/-50pip displacement (reveals dir), enter continuation next bar; stop=pre-trigger extreme."""
    c=M["c"];h=M["h"];l=M["l"];atr=M["atr"];n=M["n"]; out=[]
    for a in anchors:
        c0=c[a]; trig=None
        for j in range(a+1, min(a+WIN, n-1)):
            if (c[j]-c0)/MC.PIP>=D_TRIG_PIP: trig=(j,+1); break
            if (c0-c[j])/MC.PIP>=D_TRIG_PIP: trig=(j,-1); break
        if trig is None: continue
        j,d=trig
        # stop = opposite structural extreme since anchor (pre-trigger)
        stop=(min(l[a:j+1])-0.1*atr[j]) if d>0 else (max(h[a:j+1])+0.1*atr[j])
        if (c[j]-stop)*d<=0: continue
        out.append((j+1,d,stop))
    return out

def ev(M,trades,mode="struct"):
    rows=[]
    for k,side,stop in trades:
        r=MC.resolve(M,k,side,stop,mode)
        if r is None: continue
        r["yr"]=M["yr"][min(k,M["n"]-1)]; rows.append(r)
    return rows

def rep(M,rows,label):
    if len(rows)<30: print(f"{label:30s} N={len(rows)} small"); return None
    net=np.array([r["net"] for r in rows]); g=np.array([r["g"] for r in rows]); k=np.array([r["k"] for r in rows]); yr=np.array([r["yr"] for r in rows])
    ie=len(MC.dedup_episodes(k)); ky=M["t"][np.clip(k,0,M["n"]-1)]; dev=ky<1719792000
    top1=np.sort(net)[-max(1,len(net)//100):].sum()/net.sum() if net.sum()>0 else float('nan')
    drop5=np.sort(net)[:int(len(net)*0.95)].mean()
    yrs=" ".join(f"{y}:{net[yr==y].mean():+.2f}" for y in sorted(set(yr.tolist())))
    print(f"{label:30s} N={len(net):4d} ie={ie:4d} net={net.mean():+.3f} WR={(g>0).mean():.3f} DEV={net[dev].mean():+.3f} OOS={net[~dev].mean():+.3f} drop5%={drop5:+.3f} top1%PnL={top1:.2f} | {yrs}")
    return net.mean()

def main():
    M=MC.load()
    L=L1.london_events(M); B=L1.baseline_events(M,2)
    print("=== Interpretation A: L1 London-gated displacement-revealed CONTINUATION (struct exit) ===")
    la=ev(M,gated_continuation(M,L),"struct"); lm=rep(M,la,"A.L1_LONDON_gated")
    print("=== MATCHED CONTROL: same conditional-response at non-London (Asia) baseline ===")
    ba=ev(M,gated_continuation(M,B),"struct"); bm=rep(M,ba,"A.CONTROL_ASIA_gated")
    if lm is not None and bm is not None:
        print(f"\nL1_INCREMENTAL over control = {lm-bm:+.3f}  (does London add to the tradeable response?)")
    print("=== Interpretation B: London directional bias (long-only & short-only at open, struct) — expected ~coinflip ===")
    rep(M,ev(M,[(a+1,+1,M['c'][a]-2*M['atr'][a]) for a in L],"struct"),"B.L1_LONG_bias")
    rep(M,ev(M,[(a+1,-1,M['c'][a]+2*M['atr'][a]) for a in L],"struct"),"B.L1_SHORT_bias")

if __name__=="__main__":
    main()
