"""S2 RANGE BREAKOUT — FROZEN deterministic test (EXTERNAL_RULE_MAPPING.md). LONG/SHORT separate.
Parent TFs H1,H4; 3 close-based box defs; consolidation gate; close-beyond breakout; no-chase $4;
entry A (breakout) vs B (retest); structural SL=opposite box side; RR{1.0,1.5,2.0}; free-path & volume increments.
"""
import numpy as np, pandas as pd
import swing_base as sb, external_common as ec

W=5; NOCHASE=4.0; FREEP=10.0  # $4 no-chase, 100 pip (=$10) free-path
HOR={"H1":48,"H4":30}

def boxes(df, kind):
    o=df["open"].to_numpy(); c=df["close"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy()
    body_hi=np.maximum(o,c); body_lo=np.minimum(o,c)
    if kind=="body_env":
        bh=pd.Series(body_hi).rolling(W).max().shift(1).to_numpy(); bl=pd.Series(body_lo).rolling(W).min().shift(1).to_numpy()
    elif kind=="close_ext":
        bh=pd.Series(c).rolling(W).max().shift(1).to_numpy(); bl=pd.Series(c).rolling(W).min().shift(1).to_numpy()
    else: # close_iqr
        bh=pd.Series(c).rolling(W).quantile(0.75).shift(1).to_numpy(); bl=pd.Series(c).rolling(W).quantile(0.25).shift(1).to_numpy()
    atr_ma=df["atr_ma"].to_numpy(); br=bh-bl; consol=(br<atr_ma)&np.isfinite(br)&np.isfinite(atr_ma)
    up=consol&(c>bh); dn=consol&(c<bl)
    return bh,bl,up,dn

def retest_events(df, brk_idx, side, bh, bl, window=20):
    """First causal retest of the broken edge: later bar wick-touches edge then closes back on breakout side."""
    h=df["high"].to_numpy(); l=df["low"].to_numpy(); c=df["close"].to_numpy(); n=len(df)
    out=[]
    for i in brk_idx:
        edge = bh[i] if side>0 else bl[i]
        for j in range(i+1, min(i+1+window,n)):
            if side>0 and l[j]<=edge and c[j]>edge: out.append((j,i)); break
            if side<0 and h[j]>=edge and c[j]<edge: out.append((j,i)); break
    return out

def run(df, tf, dev_mask, ph, pl, vol_ma):
    o=df["open"].to_numpy(); c=df["close"].to_numpy(); vol=df["volume"].to_numpy()
    for kind in ("body_env","close_ext","close_iqr"):
        bh,bl,up,dn=boxes(df,kind)
        for side,name,brkmask,edge in ((+1,"L",up,bh),(-1,"S",dn,bl)):
            raw=[i for i in np.where(brkmask)[0] if i+1<len(df) and dev_mask[i]]
            # no-chase: breakout close within $4 of edge
            raw=[i for i in raw if abs(c[i]-edge[i])<=NOCHASE]
            # ENTRY A
            evA=sb.dedup_events(np.array(raw),cooldown=W)
            if side>0: riskA=np.array([o[i+1]-bl[i] for i in evA])
            else:      riskA=np.array([bh[i]-o[i+1] for i in evA])
            okA=np.isfinite(riskA)&(riskA>0); evA,riskA=evA[okA],riskA[okA]
            emit(df,tf,kind,name,"A",evA,side,riskA,ph,pl,vol,vol_ma)
            # ENTRY B (retest)
            rt=retest_events(df,evA,side,bh,bl)
            evB=np.array([j for j,i in rt]); origB=np.array([i for j,i in rt])
            if len(evB):
                if side>0: riskB=np.array([o[j+1]-bl[i] for j,i in zip(evB,origB)])
                else:      riskB=np.array([bh[i]-o[j+1] for j,i in zip(evB,origB)])
                okB=np.isfinite(riskB)&(riskB>0)&(evB+1<len(df)); evB,riskB=evB[okB],riskB[okB]
                emit(df,tf,kind,name,"B",evB,side,riskB,ph,pl,vol,vol_ma)

def emit(df,tf,kind,name,entry,ev,side,risk,ph,pl,vol,vol_ma):
    if len(ev)<8:
        print(f"  {tf} {kind:9s} {name} {entry}: N={len(ev)} (too few)"); return
    H=HOR[tf]
    ps=ec.path_stats(df,ev,side,risk,H)
    tr,m,dc=ec.econ_line(df,ev,side,risk,1.0,H,"STRESS")
    _,m15,_=ec.econ_line(df,ev,side,risk,1.5,H,"STRESS")
    _,m20,_=ec.econ_line(df,ev,side,risk,2.0,H,"STRESS")
    allpos=all(v[0]>0 for v in m["per_year"].values())
    # increments: free-path & volume subsets (RR1.0)
    o=df["open"].to_numpy()
    ent=o[ev+1]
    if side>0: free=(ph[ev]<=ent)|((ph[ev]-ent)>=FREEP)
    else:      free=(pl[ev]>=ent)|((ent-pl[ev])>=FREEP)
    volok=vol[ev]>=1.3*vol_ma[ev]
    def sub(mask):
        if mask.sum()<8: return None
        t,mm,_=ec.econ_line(df,ev[mask],side,risk[mask],1.0,H,"STRESS"); return mm["avgR"]
    fp=sub(free); vv=sub(volok)
    print(f"  {tf} {kind:9s} {name} {entry}: N={m['N']:3d} medMFE={ps['medMFE']:.2f} medMAE={ps['medMAE']:.2f} "
          f"advF={ps['advFirst']:.2f} P(+1<-1)={ps['P_1']:.2f} mfe100p={ps['mfe100']:.2f} | "
          f"rr1={m['avgR']:+.3f}(b10 {m['best10']:+.2f}) rr1.5={m15['avgR']:+.3f} rr2={m20['avgR']:+.3f} "
          f"| DISC{(dc['disc_avgR'] if dc else 0):+.2f}/CONF{(dc['conf_avgR'] if dc else 0):+.2f} yr+={str(allpos)[0]} "
          f"| +free={('%.3f'%fp) if fp is not None else 'na'} +vol={('%.3f'%vv) if vv is not None else 'na'} "
          f"medSL={m['med_sl_pips']:.0f}p")

def main():
    tfs=sb.build_frames(); print("S2 RANGE BREAKOUT (FROZEN)  DEV selection, STRESS cost")
    for tf in ("H1","H4"):
        df=tfs[tf]; dev_mask=df["is_dev"].to_numpy(); ph,pl=ec.prior_swing(df,50)
        vol_ma=pd.Series(df["volume"]).rolling(20).mean().shift(1).to_numpy()
        run(df,tf,dev_mask,ph,pl,vol_ma)

if __name__=="__main__":
    main()
