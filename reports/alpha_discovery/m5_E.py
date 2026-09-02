"""m5_E.py — drill into family E (impulse->rejection->opposite-acceptance): exit set {2R, struct3R, trail, time} x direction + matched
control (§19: fade first impulse WITHOUT the rejection+acceptance sequence). DEV/OOS + yearly. Does the FULL sequence + skew-exit monetize?
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import m5_core as MC, m5_families as MF

def control_fade(M, D=1.5, W1=6):
    """CONTROL: after the same impulse, immediately fade (enter -d1 next bar) WITHOUT waiting for rejection/opposite-acceptance."""
    o=M["o"];h=M["h"];l=M["l"];c=M["c"];atr=M["atr"];n=M["n"]; out=[]; last=-99
    for i in range(60,n-30):
        if i-last<6 or not (np.isfinite(atr[i]) and atr[i]>0): continue
        net=c[i]-c[i-W1]
        if abs(net)<D*atr[i]: continue
        d1=int(np.sign(net)); imp_ext=max(h[i-W1:i+1]) if d1>0 else min(l[i-W1:i+1]); d2=-d1
        stop=(imp_ext+0.1*atr[i]) if d2<0 else (imp_ext-0.1*atr[i]); out.append((i+1,d2,stop)); last=i
    return out

def ev(M, trades, mode):
    rows=[]
    for k,side,stop in trades:
        r=MC.resolve(M,k,side,stop,mode)
        if r is None: continue
        r["yr"]=M["yr"][min(k,M["n"]-1)]; rows.append(r)
    return rows

def rep(M, rows, label):
    if len(rows)<40: print(f"{label:30s} N={len(rows)} small"); return
    net=np.array([r["net"] for r in rows]); g=np.array([r["g"] for r in rows]); k=np.array([r["k"] for r in rows]); yr=np.array([r["yr"] for r in rows])
    ie=len(MC.dedup_episodes(k)); ky=M["t"][np.clip(k,0,M["n"]-1)]; dev=ky<1719792000
    pf=(g[g>0].sum())/(abs(g[g<0].sum())+1e-9)
    yrs=" ".join(f"{y}:{net[yr==y].mean():+.2f}" for y in sorted(set(yr.tolist())))
    print(f"{label:30s} N={len(net):4d} ie={ie:4d} net={net.mean():+.3f} WR={(g>0).mean():.3f} PF={pf:.2f} DEV={net[dev].mean():+.3f} OOS={net[~dev].mean():+.3f} | {yrs}")

def main():
    M=MC.load()
    E=MF.famE(M); CT=control_fade(M)
    print("=== FAMILY E exits x direction ===")
    for mode in ("2R","struct","trail","time"):
        rep(M,[r for r in ev(M,E,mode) if r["side"]>0],f"E.LONG.{mode}")
        rep(M,[r for r in ev(M,E,mode) if r["side"]<0],f"E.SHORT.{mode}")
    print("\n=== MATCHED CONTROL (fade first impulse, no reject/accept) ===")
    for mode in ("2R","trail"):
        rep(M,[r for r in ev(M,CT,mode) if r["side"]>0],f"CTRL.LONG.{mode}")
        rep(M,[r for r in ev(M,CT,mode) if r["side"]<0],f"CTRL.SHORT.{mode}")

if __name__=="__main__":
    main()
