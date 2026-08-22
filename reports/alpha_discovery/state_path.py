"""state_path.py — OUTCOME-FIRST state->future-path information engine (ALPHA-XAUUSD-CAUSAL-STATE-PATH-DISCOVERY-001).
Stage A: measure P(favorable before adverse) and MFE/MAE conditional on CAUSAL price-state variables, vs the
unconditional base rate, LONG/SHORT separate, multi-horizon. Price-only; causal (state known at bar i close,
forward path from i+1). Uses RAW causal price-state features (NOT the untrusted canonical RANGE/N1-N6 MI).
Population: 2021-2023 native gated H1 (DEV) via swing_base (firewall-compliant). Info-first, no strategy geometry yet.
"""
import numpy as np, pandas as pd
import swing_base as sb
PIP=0.10  # 1 project pip = 0.10 USD

# path outcome labels (favorable_pips, adverse_pips)
LABELS=[(50,50),(70,70),(100,70),(100,100),(150,75)]
UP_THR=sorted(set(x for x,_ in LABELS) | set(y for _,y in LABELS))  # USD thresholds via *PIP

def add_state(df):
    o,h,l,c=(df[k].to_numpy() for k in ("open","high","low","close"))
    atr=df["atr"].to_numpy(); atr_ma=df["atr_ma"].to_numpy(); e20=df["ema20"].to_numpy(); e50=df["ema50"].to_numpy()
    hh=df["hh20"].to_numpy(); ll=df["ll20"].to_numpy()
    S={}
    S["effic"]=df["effic"].to_numpy()                        # directional efficiency (signed)
    S["trend"]=(e20-e50)/atr                                  # trend separation in ATR (signed)
    S["vol_ratio"]=atr/atr_ma                                 # volatility state
    S["vol_change"]=atr/pd.Series(atr).shift(12).to_numpy()   # vol now vs 12h ago
    S["dist_ema"]=(c-e20)/atr                                 # distance from anchor (signed)
    S["pos_range"]=np.where((hh-ll)>0,(c-ll)/(hh-ll),0.5)     # position within prior-20 range [0..1]
    S["impulse6"]=(c-pd.Series(c).shift(6).to_numpy())/atr    # 6h net move in ATR (signed)
    S["body_eff"]=np.where((h-l)>0,(c-o)/(h-l),0.0)           # signed bar body efficiency
    # signed consecutive same-direction close run
    up=(c>np.roll(c,1)).astype(int); run=np.zeros(len(c));
    for i in range(1,len(c)): run[i]=run[i-1]+1 if up[i]==up[i-1] else 1
    S["persist"]=run*np.where(c>np.roll(c,1),1,-1)
    S["hour"]=df["dt"].dt.hour.to_numpy().astype(float)
    return S

def outcomes(df, H):
    c=df["close"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); n=len(df)
    up_thr=[t*PIP for t in UP_THR]
    Lout={lab:np.full(n,np.nan) for lab in LABELS}; Sout={lab:np.full(n,np.nan) for lab in LABELS}
    mfe=np.full(n,np.nan); mae=np.full(n,np.nan)
    for i in range(n):
        if i+1>=n: continue
        ref=c[i]; end=min(i+1+H,n)
        tup={t:0 for t in UP_THR}; tdn={t:0 for t in UP_THR}  # 0 = not reached
        mx=0.0; mn=0.0
        for j in range(i+1,end):
            fav=h[j]-ref; adv=ref-l[j]
            if fav>mx: mx=fav
            if adv>mn: mn=adv
            for t in UP_THR:
                tu=t*PIP
                if tup[t]==0 and (h[j]-ref)>=tu: tup[t]=j
                if tdn[t]==0 and (ref-l[j])>=tu: tdn[t]=j
        mfe[i]=mx/PIP; mae[i]=mn/PIP
        for (X,Y) in LABELS:
            tu_x=tup[X] or 10**9; td_y=tdn[Y] or 10**9
            Lout[(X,Y)][i]=1.0 if tu_x<td_y else 0.0
            td_x=tdn[X] or 10**9; tu_y=tup[Y] or 10**9
            Sout[(X,Y)][i]=1.0 if td_x<tu_y else 0.0
    return Lout,Sout,mfe,mae

def info_map(S, out, mask, base, headline, name):
    """Univariate decile response of headline outcome to each state var (continuous-first)."""
    y=out[headline]
    rows=[]
    for var,x in S.items():
        v=x[mask]; yy=y[mask]; ok=np.isfinite(v)&np.isfinite(yy)
        v,yy=v[ok],yy[ok]
        if len(v)<200: continue
        q=pd.qcut(pd.Series(v),10,labels=False,duplicates="drop")
        d=pd.DataFrame({"q":q,"y":yy}).groupby("q")["y"].agg(["mean","size"])
        lo=d["mean"].iloc[0]; hi=d["mean"].iloc[-1]; spread=d["mean"].max()-d["mean"].min()
        # monotonic-ish: correlation of decile index with mean
        mono=np.corrcoef(d.index.to_numpy(),d["mean"].to_numpy())[0,1] if len(d)>2 else 0
        rows.append((var,base,lo,hi,spread,mono,int(d["size"].min())))
    rows.sort(key=lambda r:-r[4])
    print(f"  [{name}] {headline} base={base:.3f}  (var: botDecile topDecile spread mono minN)")
    for var,b,lo,hi,sp,mono,mn in rows:
        print(f"    {var:11s} {lo:.3f} -> {hi:.3f}  spread={sp:.3f} mono={mono:+.2f} minN={mn}")

def main():
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy()
    S=add_state(h1)
    for H in (24,48):
        L,Sh,mfe,mae=outcomes(h1,H)
        print(f"\n===== HORIZON H={H} H1 bars ({H}h) — DEV 2021-2023, N={int(dev.sum())} =====")
        print("  BASELINES (unconditional, DEV):")
        for lab in LABELS:
            bl=np.nanmean(L[lab][dev]); bs=np.nanmean(Sh[lab][dev])
            print(f"    +{lab[0]}/-{lab[1]}p:  LONG base={bl:.3f}   SHORT base={bs:.3f}")
        print(f"    MFE median={np.nanmedian(mfe[dev]):.0f}p  MAE median={np.nanmedian(mae[dev]):.0f}p")
        # univariate info map on the headline labels
        info_map(S,L,dev,np.nanmean(L[(100,70)][dev]),(100,70),"LONG")
        info_map(S,Sh,dev,np.nanmean(Sh[(100,70)][dev]),(100,70),"SHORT")

if __name__=="__main__":
    main()
