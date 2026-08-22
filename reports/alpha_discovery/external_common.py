"""external_common.py — shared engine for the FROZEN S2/S4 external replication (see EXTERNAL_RULE_MAPPING.md).
Path-first metrics (§29), causal helpers. swing_base.py is imported READ-ONLY (COMP-CONT-L fingerprint preserved)."""
import numpy as np, pandas as pd
import swing_base as sb

PIP = sb.PIP  # 0.10 USD

def path_stats(df, ev, side, risk, horizon):
    """Frozen §29 path metrics. entry=open[i+1]. Favorable-before-adverse uses -1R = full risk adverse,
    conservative same-bar tie -> adverse wins (strict fav<stop)."""
    o=df["open"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); n=len(df)
    risk=np.asarray(risk,float)
    mfeR=[]; maeR=[]; win05=[]; win1=[]; win15=[]
    for k,i in enumerate(ev):
        ei=i+1
        if ei>=n: continue
        rk=risk[k]
        if not np.isfinite(rk) or rk<=0: continue
        entry=o[ei]; first_stop=np.inf; fh={0.5:np.inf,1.0:np.inf,1.5:np.inf}; mfe=0.0; mae=0.0
        for j in range(ei, min(ei+horizon+1,n)):
            fav=(h[j]-entry) if side>0 else (entry-l[j])
            adv=(entry-l[j]) if side>0 else (h[j]-entry)
            if fav>mfe: mfe=fav
            if adv>mae: mae=adv
            if adv>=rk and first_stop==np.inf: first_stop=j
            for kk in (0.5,1.0,1.5):
                if fh[kk]==np.inf and fav>=kk*rk: fh[kk]=j
        mfeR.append(mfe/rk); maeR.append(mae/rk)
        win05.append(1 if fh[0.5]<first_stop else 0)
        win1.append(1 if fh[1.0]<first_stop else 0)
        win15.append(1 if fh[1.5]<first_stop else 0)
    mfeR=np.array(mfeR); maeR=np.array(maeR)
    if len(mfeR)==0: return dict(N=0)
    mfe_pips=mfeR*(risk[:len(mfeR)]/PIP)  # approx per-trade pip MFE
    # recompute mfe in pips properly
    mfe_pips=np.array([m*r/PIP for m,r in zip(mfeR,risk[:len(mfeR)])])
    return dict(N=len(mfeR), medMFE=float(np.median(mfeR)), medMAE=float(np.median(maeR)),
                P75_MAE=float(np.percentile(maeR,75)), P90_MAE=float(np.percentile(maeR,90)),
                P_05=float(np.mean(win05)), P_1=float(np.mean(win1)), P_15=float(np.mean(win15)),
                advFirst=float(np.mean(maeR>=1.0)),
                mfe50=float(np.mean(mfe_pips>=50)), mfe70=float(np.mean(mfe_pips>=70)),
                mfe100=float(np.mean(mfe_pips>=100)), mfe150=float(np.mean(mfe_pips>=150)),
                mfe200=float(np.mean(mfe_pips>=200)))

def sim_rr(df, ev, side, risk, rr, horizon, scenario="STRESS", delay=0):
    """RR sim with optional +delay-bar entry (entry=open[i+1+delay]). Reuses sb.simulate semantics inline."""
    ev2=np.asarray(ev)+delay
    return sb.simulate(df, ev2, side, risk, rr=rr, horizon=horizon, scenario=scenario)

def econ_line(df, ev, side, risk, rr, horizon, scenario="STRESS", delay=0):
    tr=sim_rr(df,ev,side,risk,rr,horizon,scenario,delay)
    if len(tr)==0: return None,None,None
    m=sb.metrics(tr,df,rr); dc=sb.disc_conf(tr,df,rr)
    return tr,m,dc

def prior_swing(df, W=50):
    h=df["high"].to_numpy(); l=df["low"].to_numpy()
    ph=pd.Series(h).rolling(W).max().shift(1).to_numpy()
    pl=pd.Series(l).rolling(W).min().shift(1).to_numpy()
    return ph,pl
