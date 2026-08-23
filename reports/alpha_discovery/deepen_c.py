"""deepen_c.py — §15/§16 deepening + adversarial check of Batch C flagged survivors.
Per-year avgR (era/year concentration §28), DISC/CONF (chronological), pooled-minus-best-era (era-trend leakage),
session distribution. Same ratified sb engine. Kills thin/era-concentrated/session-artifact false positives.
"""
import numpy as np, pandas as pd, bscreen as bs
from batch_a import _mk, swing
from batch_b import sb_break, vol_onset
from batch_c import trend_break

def deep(name, sigfn, side, tf, H, cool):
    eras=bs.build_eras_tf(tf); allr=[]; allt=[]
    for tag,fr,mask in eras:
        idx,sl=sigfn(fr); idx=np.asarray(idx); sl=np.asarray(sl,float)
        keep=mask[idx]; idx=idx[keep]; sl=sl[keep]
        if len(idx)==0: continue
        o=np.argsort(idx); idx=idx[o]; sl=sl[o]; dd=bs.sb.dedup_events(idx,cool); p=np.isin(idx,dd); idx=idx[p]; sl=sl[p]
        ok=np.isfinite(sl)&(sl>0); idx=idx[ok]; sl=sl[ok]
        if len(idx)==0: continue
        tr=bs.sb.simulate(fr,idx,side,sl,rr=2.0,horizon=H,scenario="STRESS")
        if len(tr): allr.append(tr["R"].to_numpy()); allt.append(tr["t_entry"].to_numpy())
    R=np.concatenate(allr); T=np.concatenate(allt)
    yr=pd.Series(pd.to_datetime(T,unit="s",utc=True)).dt.year.to_numpy()
    hr=pd.Series(pd.to_datetime(T,unit="s",utc=True)).dt.hour.to_numpy()
    order=np.argsort(T); Rs=R[order]; cut=int(len(Rs)*0.6)
    disc=Rs[:cut].mean(); conf=Rs[cut:].mean()
    py={int(y):(round(float(R[yr==y].mean()),3),int((yr==y).sum())) for y in np.unique(yr)}
    # per-era-block (b0=2011-13,b1=2016-18,DEV=2021-23,CAL=2024) removal of best block
    blk=np.where(yr<=2014,"b0",np.where(yr<=2018,"b1",np.where(yr<=2023,"DEV","CAL")))
    bavg={b:float(R[blk==b].mean()) for b in np.unique(blk)}
    best_b=max(bavg,key=bavg.get); rem=R[blk!=best_b]; rem_avg=float(rem.mean()) if len(rem) else np.nan
    sess={"Asia":float(((hr>=0)&(hr<7)).mean()),"Lon":float(((hr>=7)&(hr<13)).mean()),"NY":float(((hr>=13)&(hr<21)).mean())}
    print(f"\n### {name} (N={len(R)} avgR={R.mean():+.3f})")
    print(f"  per-year: {py}")
    print(f"  DISC={disc:+.3f} CONF={conf:+.3f} | best-block={best_b}({bavg[best_b]:+.3f}) -> pooled-w/o-best-block={rem_avg:+.3f}")
    print(f"  block avgs: {{k:round(v,3) for...}} = "+str({k:round(v,3) for k,v in bavg.items()})+f" | session NY={sess['NY']:.0%} Asia={sess['Asia']:.0%}")

if __name__=="__main__":
    print("BATCH C DEEPENING (§15/§16): year/era concentration, DISC/CONF, best-block removal, session.")
    deep("TREND_break_S@H4", lambda f:trend_break(f,-1), -1, "H4", 12, 3)
    deep("SB_break_L@H1",    lambda f:sb_break(f,1,10),   1, "H1", 24, 6)
    deep("VOLonset_L@H1",    lambda f:vol_onset(f,1),     1, "H1", 24, 6)
