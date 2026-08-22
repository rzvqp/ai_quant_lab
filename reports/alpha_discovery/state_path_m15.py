"""state_path_m15.py — M15 information-first state->path engine + UNCONDITIONAL baselines (Stage 1).
Mandate ALPHA-XAUUSD-M15-CAUSAL-STATE-PATH-DISCOVERY-001. M15 owns the decision timestamp; H1/H4 causal context
later. First-passage P(+X before -Y) with predeclared M15 labels, MFE/MAE, adverse-first, multi-horizon. Causal,
price-only. Populations: 2021-2023 gated M15 (swing_base) + historical b0/b1 M15 (hist_m15_data, governance-proven).
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
PIP=0.10
LABELS_L=[(30,30),(50,40),(70,50),(100,70),(150,75)]  # (favorable, adverse) LONG
THR=sorted({30,40,50,70,75,100,150})
HMAX=32  # 8h in M15 bars
HORIZONS={"2h":8,"4h":16,"8h":32}

def passage_m15(df,Hmax=HMAX):
    c=df["close"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); n=len(df); tl=len(THR)
    ou={t:np.full(n,np.inf) for t in THR}; od={t:np.full(n,np.inf) for t in THR}
    mfe=np.zeros(n); mae=np.zeros(n)
    thr=np.array(THR)*PIP
    for i in range(n-1):
        ref=c[i]; rmh=-1e18; rml=1e18; pu=0; pd=0
        for j in range(i+1,min(i+1+Hmax,n)):
            if h[j]>rmh: rmh=h[j]
            if l[j]<rml: rml=l[j]
            ue=rmh-ref; de=ref-rml
            while pu<tl and ue>=thr[pu]: ou[THR[pu]][i]=j-i; pu+=1
            while pd<tl and de>=thr[pd]: od[THR[pd]][i]=j-i; pd+=1
        mfe[i]=(rmh-ref)/PIP; mae[i]=(ref-rml)/PIP
    return ou,od,mfe,mae

def Pm(ou,od,X,Y,side,H,mask):
    fav=(od[X] if side=='S' else ou[X]); adv=(ou[Y] if side=='S' else od[Y])
    win=(fav<=H)&(fav<adv); return float(win[mask].mean()), int(mask.sum())

def baselines(df,mask,tag,ou,od,mfe,mae):
    print(f"\n== {tag} (N={int(mask.sum())}) ==")
    for hn,H in HORIZONS.items():
        parts=[]
        for (X,Y) in LABELS_L:
            bl,_=Pm(ou,od,X,Y,'L',H,mask); bs,_=Pm(ou,od,X,Y,'S',H,mask)
            parts.append(f"+{X}/-{Y}:L{bl:.2f}/S{bs:.2f}")
        af=float((mae[mask]>= (70*PIP)/PIP).mean()) if False else float((mae[mask]>=70).mean())
        print(f"  {hn}: "+"  ".join(parts))
    print(f"  MFE med={np.median(mfe[mask]):.0f}p P75={np.percentile(mfe[mask],75):.0f}p P90={np.percentile(mfe[mask],90):.0f}p | "
          f"MAE med={np.median(mae[mask]):.0f}p P75={np.percentile(mae[mask],75):.0f}p P90={np.percentile(mae[mask],90):.0f}p "
          f"| adverse>=70p before move-frac~{float((mae[mask]>=70).mean()):.2f}")

def main():
    print("M15 UNCONDITIONAL PATH BASELINES (Stage 1). Horizons 2h/4h/8h. Labels=research (not TP/SL).")
    # 2021-2023 gated M15
    m=sb.build_frames()["M15"]; dev=m["is_dev"].to_numpy()
    ou,od,mfe,mae=passage_m15(m)
    baselines(m,dev,"2021-2023 gated M15 DEV",ou,od,mfe,mae)
    # historical b0/b1 M15 (governance-proven slice)
    h=m15d.build(verbose=True)["M15"]; b0=h["is_b0"].to_numpy(); b1=h["is_b1"].to_numpy()
    ou2,od2,mfe2,mae2=passage_m15(h)
    baselines(h,b0,"b0 2011-2013 M15",ou2,od2,mfe2,mae2)
    baselines(h,b1,"b1 2016-2018 M15",ou2,od2,mfe2,mae2)

if __name__=="__main__":
    main()
