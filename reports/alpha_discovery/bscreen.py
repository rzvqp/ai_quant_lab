"""bscreen.py — BROAD DISCOVERY CAMPAIGN v2 common screen (ALPHA-XAUUSD-BROAD-DISCOVERY-CAMPAIGN-V2-001).
Modernized S5 discovery process (P1-P6) on the RATIFIED sb engine across MULTIPLE ERAS (C1-C5):
ONE lookahead-safe simulator (sb.simulate: next-open entry, stop-wins-ties, STRESS RT 0.24 USD, structural stop,
event dedup) + ONE uniform scorecard + ONE fast-fail verdict for every hypothesis. No forked simulator.

A HYPOTHESIS supplies: name, info_class, side(+1/-1), rr, horizon, cooldown, and signal(frame)->(idx, sl_usd)
where sl_usd is the MECHANISM-OWNED structural risk at entry (entry = open[idx+1]). Direction fixed per hyp
(LONG/SHORT screened separately, §22). Market Mode is NOT applied here (optional conditioner, §4).

ERAS: b0/b1 (2011-2018, hist_m15_data) + DEV (2021-2023) + CALIB (2024, swing_base gated-M5). Cross-era
sign-consistency is the primary falsifier (§15): sign reversal with sufficient N = FAIL.

VERDICT: SCREEN_SURVIVOR / ELIMINATE(reason) with reasons NEG_STRESS, SIGN_REVERSAL, TAIL_ONLY,
INSUFFICIENT_N, INCONSISTENT; SESSION_ARTIFACT flag (>0.65 one session). Screen is exploratory (§37).
"""
import sys, os, numpy as np, pandas as pd
_HERE=os.path.dirname(os.path.abspath(__file__));
if _HERE not in sys.path: sys.path.insert(0,_HERE)
import swing_base as sb, hist_data as hd, hist_m15_data as m15d

NMIN=25       # min trades for an era to count in cross-era logic
POOL_MIN=60   # min total trades to render a verdict
SESS=[("Asia",0,7),("Lon",7,13),("NY",13,21),("Off",21,24)]

def build_eras():
    """Two M15 frames, four era masks. hm=hist(2011-2018), sm=gated(2021-2024)."""
    hm=m15d.build(verbose=False)["M15"]; sm=sb.build_frames()["M15"]
    eras=[("b0",hm,hm["is_b0"].to_numpy()),("b1",hm,hm["is_b1"].to_numpy()),
          ("DEV",sm,sm["is_dev"].to_numpy()),("CAL",sm,sm["is_cal"].to_numpy())]
    return eras

def build_eras_tf(tf):
    """Eras for an arbitrary timeframe (H1/H4): b0/b1 (2011-18, hist_data) + DEV/CAL (2021-24, swing_base)."""
    h=hd._load(tf); s=sb.build_frames()[tf]
    return [("b0",h,h["is_b0"].to_numpy()),("b1",h,h["is_b1"].to_numpy()),
            ("DEV",s,s["is_dev"].to_numpy()),("CAL",s,s["is_cal"].to_numpy())]

def _sess_hist(t_entry):
    hr=pd.Series(pd.to_datetime(t_entry,unit="s",utc=True)).dt.hour.to_numpy()
    tot=max(len(hr),1)
    return {nm:float(((hr>=lo)&(hr<hi)).sum())/tot for nm,lo,hi in SESS}

def _best_removed(r,frac):
    if len(r)==0: return np.nan
    k=int(np.ceil(len(r)*frac)); k=min(k,len(r)-1) if len(r)>1 else 0
    return float(np.sort(r)[:len(r)-k].mean()) if len(r)-k>0 else np.nan

def screen_one(hyp, eras, verbose=True):
    name=hyp["name"]; side=hyp["side"]; rr=hyp.get("rr",2.0); H=hyp.get("horizon",48); cool=hyp.get("cool",8)
    per=[]; allR=[]; allT=[]; eraR={}
    for tag,fr,mask in eras:
        idx,sl=hyp["signal"](fr)
        if idx is None or len(idx)==0: per.append((tag,0,np.nan,np.nan,np.nan,np.nan,np.nan)); continue
        idx=np.asarray(idx); sl=np.asarray(sl,float)
        keep=mask[idx]; idx=idx[keep]; sl=sl[keep]
        if len(idx)==0: per.append((tag,0,np.nan,np.nan,np.nan,np.nan,np.nan)); continue
        # event dedup on the era-restricted signal
        order=np.argsort(idx); idx=idx[order]; sl=sl[order]
        dd=sb.dedup_events(idx,cool); pos=np.isin(idx,dd); idx=idx[pos]; sl=sl[pos]
        ok=np.isfinite(sl)&(sl>0); idx=idx[ok]; sl=sl[ok]
        if len(idx)==0: per.append((tag,0,np.nan,np.nan,np.nan,np.nan,np.nan)); continue
        tr=sb.simulate(fr,idx,side,sl,rr=rr,horizon=H,scenario="STRESS")
        if len(tr)==0: per.append((tag,0,np.nan,np.nan,np.nan,np.nan,np.nan)); continue
        r=tr["R"].to_numpy(); rg=tr["gross_R"].to_numpy()
        avg=float(r.mean()); avgg=float(rg.mean()); pf=sb._pf(r); wr=float((r>0).mean()); med=float(np.median(r))
        per.append((tag,len(tr),avg,avgg,pf,wr,med))
        allR.append(r); allT.append(tr["t_entry"].to_numpy()); eraR[tag]=r
    # pooled
    R=np.concatenate(allR) if allR else np.array([]); T=np.concatenate(allT) if allT else np.array([])
    used=[p for p in per if p[1]>=NMIN]
    pooledN=len(R); pooled=float(R.mean()) if pooledN else np.nan
    pos=sum(1 for p in used if p[2]>0); neg_strong=sum(1 for p in used if p[2]<-0.03)
    posN=len(used)
    best10=_best_removed(R,0.10); best1=_best_removed(R,0.01)
    sess=_sess_hist(T) if pooledN else {}
    maxsess=max(sess.values()) if sess else 0.0
    # era-concentration (best-block removal, §13/§28): pooled without the single best era must stay positive
    eblk={t:float(v.mean()) for t,v in eraR.items() if len(v)>=15}
    if len(eblk)>=2:
        bt=max(eblk,key=eblk.get); rem=[v for t,v in eraR.items() if t!=bt]
        pooled_wo=float(np.concatenate(rem).mean()) if rem else np.nan
    else: pooled_wo=np.nan
    # verdict
    if pooledN<POOL_MIN or posN<2: verdict="ELIM:INSUFFICIENT_N"
    elif pooled<=0: verdict="ELIM:NEG_STRESS"
    elif pos>=1 and neg_strong>=1: verdict="ELIM:SIGN_REVERSAL"
    elif not np.isfinite(best1) or best1<=0.02: verdict="ELIM:IMMATERIAL"  # S5 gate-E: best-1%-removed materially >0 (best10 too harsh for high-RR)
    elif np.isfinite(pooled_wo) and pooled_wo<=0.02: verdict="ELIM:ERA_CONCENTRATION"  # edge collapses without its best era (era-trend leakage)
    elif pos==posN: verdict="SURVIVOR"+("*" if pooled>0.05 else "")
    elif pos>=posN-1 and pooled>0: verdict="SURVIVOR-weak"
    else: verdict="ELIM:INCONSISTENT"
    flag=" [SESSION_ARTIFACT]" if maxsess>0.65 else ""
    res=dict(name=name,info=hyp.get("info",""),side=side,rr=rr,verdict=verdict,per=per,
             pooledN=pooledN,pooled=pooled,best10=best10,best1=best1,pos=pos,posN=posN,sess=sess,maxsess=maxsess)
    if verbose:
        cells="  ".join(f"{t}:{n}/{a:+.3f}" if n else f"{t}:-" for (t,n,a,ag,pf,wr,md) in per)
        sess_s=" ".join(f"{k}{v:.0%}" for k,v in sess.items())
        print(f"[{verdict:18s}] {name:32s} {'L' if side>0 else 'S'} rr{rr} | poolN={pooledN} poolR={pooled:+.3f} best1={best1:+.3f} best10={best10:+.3f} | {cells} | {sess_s}{flag}")
    return res

def run_batch(hyps, eras=None, title=""):
    if eras is None: eras=build_eras()
    print(f"\n===== BROAD SCREEN{': '+title if title else ''} (STRESS RT0.24, eras b0/b1/DEV/CAL, dedup, cross-era sign) =====")
    out=[h for h in (screen_one(h,eras) for h in hyps)]
    surv=[r for r in out if r["verdict"].startswith("SURVIVOR")]
    print(f"----- {len(surv)}/{len(out)} SCREEN_SURVIVORS -----")
    for r in sorted(surv,key=lambda x:-x["pooled"]): print(f"   SURVIVOR {r['name']} ({r['info']}) poolR={r['pooled']:+.3f} N={r['pooledN']}")
    return out
