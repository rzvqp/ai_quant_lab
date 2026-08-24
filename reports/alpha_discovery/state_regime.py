"""state_regime.py — CAUSAL REGIME taxonomy (frozen BEFORE path outcomes) + reproducibility + regime-conditional
path baselines (ALPHA-XAUUSD-REGIME-CONDITIONAL-STATE-PATH-DISCOVERY-001). Price-only, causal. NOT P&L-defined;
NOT canonical RANGE (research-local QUIET label). Regime from causal H1 features known at bar close.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd
from state_validate import passage, P
LABELS=[(70,70),(100,70),(100,100)]  # computable with passage THR=[70,100]

def regime(df):
    """FROZEN causal taxonomy (priority: QUIET>UP>DOWN>CHOP>TRANSITION). effic=dir efficiency(20),
    trend=(EMA20-EMA50)/ATR, vr=ATR/ATR_ma. All causal (known at bar close)."""
    eff=df["effic"].to_numpy(); tr=((df["ema20"]-df["ema50"])/df["atr"]).to_numpy(); vr=(df["atr"]/df["atr_ma"]).to_numpy()
    lab=np.full(len(df),"TRANSITION",dtype=object)
    chop=(np.abs(eff)<0.25); lab[chop]="CHOP"
    dn=(eff<-0.35)&(tr<-0.2); lab[dn]="DOWN"
    up=(eff>0.35)&(tr>0.2); lab[up]="UP"
    quiet=(vr<0.9)&(np.abs(eff)<0.25)&np.isfinite(vr); lab[quiet]="QUIET"
    lab[~np.isfinite(eff)|~np.isfinite(tr)]="NA"
    return lab

def episodes(lab,mask):
    l=lab[mask]; n=len(l);
    if n==0: return {}
    ep={}; prev=None
    for x in l:
        if x!=prev: ep[x]=ep.get(x,0)+1
        prev=x
    return ep

def occ_report(df,lab,mask,tag):
    m=lab[mask]; vc=pd.Series(m).value_counts(); tot=len(m)
    ep=episodes(lab,mask)
    print(f"  [{tag}] N={tot}")
    for r in ["UP","DOWN","QUIET","CHOP","TRANSITION"]:
        n=int(vc.get(r,0)); print(f"     {r:11s} {n:5d} ({100*n/max(tot,1):4.1f}%)  episodes~{ep.get(r,0)}")

def main():
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy(); yr=h1["dt"].dt.year.to_numpy()
    lab=regime(h1); up,dn=passage(h1)
    print("CAUSAL REGIME taxonomy (frozen). Occurrence + reproducibility:")
    occ_report(h1,lab,dev,"DEV 2021-2023")
    for y in (2021,2022,2023): occ_report(h1,lab,dev&(yr==y),str(y))
    # cross-era b0/b1
    hh=hd.load()["H1"]; lab2=regime(hh); up2,dn2=passage(hh); b0=hh["is_b0"].to_numpy(); b1=hh["is_b1"].to_numpy()
    occ_report(hh,lab2,b0,"b0 2011-2013"); occ_report(hh,lab2,b1,"b1 2016-2018")
    # ---- REGIME-CONDITIONAL PATH BASELINES (P(+100/-70) + others), DEV ----
    print("\nREGIME-CONDITIONAL PATH BASELINES (DEV, H=48):")
    for r in ["UP","DOWN","QUIET","CHOP","TRANSITION"]:
        m=dev&(lab==r); n=int(m.sum())
        if n<100: print(f"  {r}: N={n} (thin)"); continue
        row=[]
        for (X,Y) in LABELS:
            bl,_=P(up,dn,X,Y,'L',48,m); bs,_=P(up,dn,X,Y,'S',48,m); row.append(f"{X}/{Y}:L{bl:.2f}/S{bs:.2f}")
        print(f"  {r} (N={n}): "+"  ".join(row))
    # same for b0/b1 combined (regime base rates cross-era for later same-regime comparison)
    print("\nREGIME-CONDITIONAL BASELINES (b0+b1, H=48) — for same-regime cross-era comparison:")
    hb=b0|b1
    for r in ["UP","DOWN","QUIET","CHOP","TRANSITION"]:
        m=hb&(lab2==r); n=int(m.sum())
        if n<100: print(f"  {r}: N={n} (thin)"); continue
        bl,_=P(up2,dn2,100,70,'L',48,m); bs,_=P(up2,dn2,100,70,'S',48,m)
        print(f"  {r} (N={n}): +100/-70 L={bl:.3f} S={bs:.3f}")

if __name__=="__main__":
    main()
