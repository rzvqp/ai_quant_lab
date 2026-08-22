"""state_validate.py — rigorous validation of ST-TREND-EXH (trend-extension exhaustion state).
Key skeptical test: is the SHORT P(+100/-70) lift REAL/STABLE or 2022-concentrated? Measure LIFT over the
SAME-period base rate: per-year, DISC/CONF, multi-horizon, neighboring thresholds, cross-population b0/b1,
and trend x vol/effic interaction. Causal, price-only. state def = trend=(EMA20-EMA50)/ATR >= thr (structural,
population-independent). No threshold mining (report the whole curve). Frozen strategies untouched.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, state_path as sp
PIP=0.10; HMAX=96; THR=[70,100]  # pip thresholds needed for (100,70) both sides

def passage(df):
    c=df["close"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); n=len(df)
    up={t:np.full(n,np.inf) for t in THR}; dn={t:np.full(n,np.inf) for t in THR}
    for i in range(n):
        if i+1>=n: continue
        ref=c[i]; end=min(i+1+HMAX,n); need=2*len(THR); got=0
        seen_u={t:False for t in THR}; seen_d={t:False for t in THR}
        for j in range(i+1,end):
            fu=h[j]-ref; fd=ref-l[j]
            for t in THR:
                tu=t*PIP
                if not seen_u[t] and fu>=tu: up[t][i]=j-i; seen_u[t]=True; got+=1
                if not seen_d[t] and fd>=tu: dn[t][i]=j-i; seen_d[t]=True; got+=1
            if got>=need: break
    return up,dn

def P(up,dn,X,Y,side,H,mask):
    fav=(dn[X] if side=='S' else up[X]); adv=(up[Y] if side=='S' else dn[Y])
    win=(fav<=H)&(fav<adv)
    m=mask&np.isfinite(fav+0) ; m=mask
    return float(win[m].mean()), int(m.sum())

def liftrow(up,dn,side,H,base_mask,cond_mask,tag):
    b,nb=P(up,dn,100,70,side,H,base_mask); c,nc=P(up,dn,100,70,side,H,cond_mask)
    print(f"    {tag}: base={b:.3f}(n{nb})  extended={c:.3f}(n{nc})  lift={c-b:+.3f} ({100*(c-b)/max(b,1e-6):+.0f}pct)")
    return b,c,nb,nc

def main():
    tfs=sb.build_frames(); h1=tfs["H1"]; dev=h1["is_dev"].to_numpy()
    trend=((h1["ema20"]-h1["ema50"])/h1["atr"]).to_numpy()
    vr=(h1["atr"]/h1["atr_ma"]).to_numpy(); eff=h1["effic"].to_numpy()
    yr=h1["dt"].dt.year.to_numpy()
    up,dn=passage(h1)
    ext=trend>=1.0
    print(f"ST-TREND-EXH validation (2021-2023 native H1 DEV). extended=trend>=1.0 (frac={ext[dev].mean():.2f})")
    print("  === SHORT P(+100/-70) H=48: per-year lift over SAME-year base ===")
    for y in (2021,2022,2023):
        m=dev&(yr==y); liftrow(up,dn,'S',48,m,m&ext,f"{y}")
    print("  === SHORT per-year for LONG side (context) ===")
    for y in (2021,2022,2023):
        m=dev&(yr==y); liftrow(up,dn,'L',48,m,m&ext,f"{y} LONG")
    # DISC/CONF chronological
    idx=np.where(dev)[0]; cut=idx[int(len(idx)*0.6)]
    disc=dev&(np.arange(len(h1))<cut); conf=dev&(np.arange(len(h1))>=cut)
    print("  === SHORT DISC/CONF (freeze state before CONF) ===")
    liftrow(up,dn,'S',48,disc,disc&ext,"DISC"); liftrow(up,dn,'S',48,conf,conf&ext,"CONF")
    # multi-horizon
    print("  === SHORT multi-horizon extended lift (DEV) ===")
    for H in (8,16,24,48,96): liftrow(up,dn,'S',H,dev,dev&ext,f"H={H}")
    # neighboring thresholds
    print("  === neighboring trend thresholds (SHORT H=48, DEV) ===")
    for thr in (0.7,1.0,1.3): liftrow(up,dn,'S',48,dev,dev&(trend>=thr),f"trend>={thr}")
    # interactions
    print("  === interactions (SHORT H=48, DEV) ===")
    liftrow(up,dn,'S',48,dev,dev&ext&(vr<np.nanmedian(vr[dev])),"ext & low-vol")
    liftrow(up,dn,'S',48,dev,dev&ext&(eff<0),"ext & effic<0")
    liftrow(up,dn,'S',48,dev,dev&ext&(vr>=np.nanmedian(vr[dev])),"ext & high-vol")
    # cross-population b0/b1
    print("  === CROSS-POPULATION historical b0/b1 H1 (causal) ===")
    hh=hd.load()["H1"]; tr2=((hh["ema20"]-hh["ema50"])/hh["atr"]).to_numpy()
    up2,dn2=passage(hh); ext2=tr2>=1.0
    b0=hh["is_b0"].to_numpy(); b1=hh["is_b1"].to_numpy()
    for tag,mk in (("b0",b0),("b1",b1)):
        liftrow(up2,dn2,'S',48,mk,mk&ext2,f"{tag} SHORT"); liftrow(up2,dn2,'L',48,mk,mk&ext2,f"{tag} LONG")

if __name__=="__main__":
    main()
