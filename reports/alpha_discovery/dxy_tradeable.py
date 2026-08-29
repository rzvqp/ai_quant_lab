"""dxy_tradeable.py — MECHANIZE test for DXY-NDX1: is the DXY-impulse expansion-amplification TRADEABLE, or just bigger-symmetric?
On the DXY-aligned XAU-H1 frames (b0/b1/y2123, 2024+ PROTECTED), compression-breakout (XAU supplies direction via the break),
compared:
 A BASELINE      = all compression breakouts (expect ~null, like VOLTIME-2 on M15).
 B IMP-FILTER    = only breakouts with a causal DXY IMPULSE present (|d_imp_l0| >= per-era median) — magnitude/timing filter.
 C DIR-CONFLUENCE= breakout direction AGREES with the DXY-inverse-implied direction (up-break AND DXY impulse DOWN, or mirror) —
   uses DXY as a weak direction-resolver (expected to INVERT across eras per prior/H-DIR1 — the cross-block gate will expose it).
Entry next-bar open, stop=opposite range extreme -/+0.1ATR, target=+2R. STRESS 0.24. Net per block + cross-block sign-stability.
A cell net>0 AND sign-stable across b0/b1/y2123 = tradeable DXY edge -> full gate. Else DXY-NDX1 stays INFORMATION-ONLY (magnitude
predictable, direction still unresolved)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import dxy_data as DX
COST=0.24; HMAX=60; M=12; D=6
def main():
    frames=DX.build()
    print("DXY tradeability (compression-breakout on XAU-H1, DXY-aligned blocks, STRESS 0.24). A=baseline B=DXY-imp-filter C=DXY-dir-confluence")
    res={"A":{},"B":{},"C":{}}
    for era,m in frames.items():
        c=m["close"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); o=m["open"].to_numpy(); n=len(c)
        tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
        atr=pd.Series(tr).rolling(14).mean().to_numpy(); atr_ma=pd.Series(atr).rolling(30).mean().shift(1).to_numpy()
        comp=(atr<atr_ma).astype(int); cd=np.zeros(n,int)
        for i in range(1,n): cd[i]=cd[i-1]+1 if comp[i] else 0
        d_imp=m["d_imp_l0"].to_numpy()  # signed DXY impulse (>0 = USD up)
        imp_abs=np.abs(d_imp); ithr=np.nanmedian(imp_abs[np.isfinite(imp_abs)])
        A=[]; B=[]; C=[]; T=40
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
            di=d_imp[T]  # causal DXY impulse at decision
            A.append(R)
            if np.isfinite(imp_abs[T]) and imp_abs[T]>=ithr: B.append(R)
            # dir-confluence: up-break agrees with DXY-inverse if DXY impulse DOWN (di<0); down-break if di>0
            if np.isfinite(di) and ((dirn>0 and di<0) or (dirn<0 and di>0)): C.append(R)
            T=j+3
        for key,arr in [("A",A),("B",B),("C",C)]:
            a=np.array(arr); res[key][era]=(len(a), (np.mean(a-COST) if len(a) else float('nan')))
    for key,name in [("A","BASELINE all breakouts"),("B","DXY-IMP-FILTER"),("C","DXY-DIR-CONFLUENCE")]:
        cells=res[key]; nets=[cells[e][1] for e in ["b0","b1","y2123"]]
        stable=(all(x>0 for x in nets) or all(x<0 for x in nets))
        print(f"  {name:22s}: " + " ".join(f"{e}(n{cells[e][0]}) net={cells[e][1]:+.3f}" for e in ["b0","b1","y2123"]) + f"  | sign-stable={stable}"+(" <== net>0 ALL" if all(x>0 for x in nets) else ""))
    print("\n=> DXY-IMP-FILTER or DIR-CONFLUENCE net>0 across ALL 3 blocks => tradeable DXY edge -> full gate. Else DXY-NDX1 = INFO-ONLY.")
if __name__=="__main__": main()
