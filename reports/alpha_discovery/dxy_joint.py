"""dxy_joint.py — last distinct DXY mechanism: JOINT XAU+DXY compression / CONVERGENCE. Economic rationale: when BOTH XAU and DXY are
compressed, a shared macro catalyst that breaks the joint compression supplies a COORDINATED direction (DXY breaks one way, XAU the
inverse). Test whether the XAU compression-breakout, gated on (DXY also compressed) AND (DXY simultaneously impulsing INVERSE to the XAU
break), has tradeable follow-through — per block. Also report per-block DIRECTION consistency to expose the expected regime inversion
(disinflation b0/b1 inverse vs inflation y2123 same-direction). Causal DXY lag0, blocks b0/b1/y2123, 2024+ PROTECTED, STRESS 0.24, no
mining. Baseline = XAU breakout. Cross-block sign-stability is the gate."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import dxy_data as DX
COST=0.24; HMAX=60; M=12; D=6
def main():
    frames=DX.build()
    print("DXY JOINT-compression / convergence (XAU-H1 breakout gated on DXY-compressed + DXY-inverse-impulse at break). STRESS 0.24.")
    res={"BASE":{},"JOINT":{},"JOINT_INV":{}}
    for era,m in frames.items():
        c=m["close"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); o=m["open"].to_numpy(); n=len(c)
        tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
        atr=pd.Series(tr).rolling(14).mean().to_numpy(); atr_ma=pd.Series(atr).rolling(30).mean().shift(1).to_numpy()
        comp=(atr<atr_ma).astype(int); cd=np.zeros(n,int)
        for i in range(1,n): cd[i]=cd[i-1]+1 if comp[i] else 0
        d_vr=m["d_vr_l0"].to_numpy(); d_imp=m["d_imp_l0"].to_numpy()  # DXY vol-ratio (<1 compressed), signed impulse
        BASE=[]; JOINT=[]; JINV=[]; T=40
        while T<n-HMAX-M-2:
            if cd[T]<D or not np.isfinite(atr[T]) or atr[T]<=0: T+=1; continue
            W=min(cd[T],40); rhi=np.max(h[T-W+1:T+1]); rlo=np.min(l[T-W+1:T+1]); brk=None
            for j in range(T+1,min(T+1+M,n-2)):
                if c[j]>rhi: brk=(j,1); break
                if c[j]<rlo: brk=(j,-1); break
            if brk is None: T+=M; continue
            j,dirn=brk; ei=j+1
            if ei>=n-HMAX: break
            entry=o[ei]; stop=(rlo-0.1*atr[T]) if dirn>0 else (rhi+0.1*atr[T]); risk=abs(entry-stop)
            if risk<=0.05*atr[T]: T=j+3; continue
            tgt=entry+2*risk*dirn; seg_l=l[ei:ei+HMAX]; seg_h=h[ei:ei+HMAX]
            if dirn>0: fs=np.where(seg_l<=stop)[0]; ft=np.where(seg_h>=tgt)[0]
            else: fs=np.where(seg_h>=stop)[0]; ft=np.where(seg_l<=tgt)[0]
            fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
            if fstop==ftgt==10**9: T=j+3; continue
            R=2.0 if ftgt<fstop else -1.0
            dxy_comp = np.isfinite(d_vr[j]) and d_vr[j]<1.0   # DXY also compressed at the break bar
            di=d_imp[j]  # DXY impulse at the break bar
            BASE.append(R)
            if dxy_comp: JOINT.append(R)
            # JOINT + DXY inverse impulse (up-break with DXY down-impulse / mirror) = coordinated inverse catalyst
            if dxy_comp and np.isfinite(di) and ((dirn>0 and di<0) or (dirn<0 and di>0)): JINV.append(R)
            T=j+3
        for key,arr in [("BASE",BASE),("JOINT",JOINT),("JOINT_INV",JINV)]:
            a=np.array(arr); res[key][era]=(len(a),(np.mean(a-COST) if len(a) else float('nan')))
    for key,name in [("BASE","XAU breakout baseline"),("JOINT","+ DXY-compressed"),("JOINT_INV","+ DXY-compressed + DXY-inverse-impulse")]:
        cs=res[key]; nets=[cs[e][1] for e in ["b0","b1","y2123"]]
        stable=all(x>0 for x in nets) or all(x<0 for x in nets)
        print(f"  {name:38s}: "+" ".join(f"{e}(n{cs[e][0]}) {cs[e][1]:+.3f}" for e in ["b0","b1","y2123"])+f" | sign-stable={stable}"+(" <== net>0 ALL" if all(x>0 for x in nets) else ""))
    print("\n=> JOINT_INV net>0 across ALL 3 blocks = tradeable joint-catalyst edge. If it flips sign (b0/b1 vs y2123) = regime inversion")
    print("   confirmed -> DXY frontier CONCLUSION: stable NON-DIRECTIONAL info (NDX1) but NO cross-era tradeable edge (direction regime-conditional).")
if __name__=="__main__": main()
