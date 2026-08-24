"""rs2_continuation.py — RANGE-regime specialist candidate RS-2: CROSS-SCALE range-continuation breakout (bull-flag/bear-flag).
The fade (RS-1) failed because range boundaries precede breaks. So trade the BREAK, with DIRECTION supplied by the higher-TF
(D1) trend (the winning cross-scale principle that found CRS-1, applied to a DIFFERENT regime + DIFFERENT mechanism -> not
CRS-1-adjacent). When a frozen RANGE_REGIME_V1 episode ends by breaking its box IN THE DIRECTION of the causal D1 trend, enter
WITH the break; stop = opposite boundary of the broken box (tight, structural); target = measured move (box width, rr from geom).

Causal: range box from range_regime (trailing extremes); D1 trend = D1 ema20>ema50 mapped merge_asof-backward (bars<=t). Entry
at the M15 bar of the H4 breakout (sim next-bar). Skepticism gate: per-year, DISC/CONF/OOS all>0, best/worst-10%-removed,
neighbor (rr), both directions contribute, regime+alignment specificity (counter-trend break & no-range control), STRESS.
Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
import range_regime as RR

def d1_trend_map(m):
    day=(m["time"]//86400)*86400
    g=m.assign(b=day).groupby("b")
    d=g.agg(open=("open","first"),high=("high","max"),low=("low","min"),close=("close","last"),
            volume=("volume","sum"),close_time=("time","last")).reset_index().rename(columns={"b":"time"})
    d=CD._feat(d); d["close_time"]=d["close_time"].to_numpy()+900
    up=(d["ema20"].to_numpy()>d["ema50"].to_numpy()).astype(float)
    hm=pd.DataFrame({"close_time":d["close_time"].to_numpy(),"d1up":up}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    j=pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()
    return j["d1up"].to_numpy()

def breakout_events(h4, inr, rlo, rhi):
    c=h4["close"].to_numpy(); n=len(h4); ev=[]  # (h4_idx, dir, box_lo, box_hi)
    for t in range(1,n):
        if inr[t-1] and not inr[t]:
            blo=rlo[t-1]; bhi=rhi[t-1]
            if not (np.isfinite(blo) and np.isfinite(bhi)): continue
            if c[t]>bhi: ev.append((t,1,blo,bhi))
            elif c[t]<blo: ev.append((t,-1,blo,bhi))
    return ev

def run(m, h4, ev, d1up, align=True, rr=2.0, verbose=True):
    ct=h4["close_time"].to_numpy(); mt=m["time"].to_numpy(); atr=m["atr"].to_numpy(); c=m["close"].to_numpy(); n=len(m)
    idxL=[]; slL=[]; idxS=[]; slS=[]
    for (t,d,blo,bhi) in ev:
        mi=int(np.searchsorted(mt, ct[t]))       # first M15 bar at/after the H4 breakout close
        if mi>=n-1: continue
        dd = d1up[mi]                              # causal D1 trend at entry
        if align and not ((d==1 and dd==1) or (d==-1 and dd==0)): continue
        if not align and not ((d==1 and dd==0) or (d==-1 and dd==1)): continue  # counter-trend control
        px=c[mi]
        if d==1:
            sl=px-blo   # stop = opposite (lower) boundary
            if sl>0: idxL.append(mi); slL.append(sl)
        else:
            sl=bhi-px
            if sl>0: idxS.append(mi); slS.append(sl)
    Rs=[]; sd=[]; te=[]
    for idx,sl,side in [(idxL,slL,1),(idxS,slS,-1)]:
        if len(idx)==0: continue
        idx=np.array(idx); sl=np.array(sl)
        tr=sb.simulate(m,idx,side,sl,rr=rr,horizon=96,scenario="STRESS")
        Rs.append(tr["R"].to_numpy()); sd.append(np.full(len(tr),side)); te.append(tr["t_entry"].to_numpy())
    if not Rs:
        if verbose: print("  no trades");
        return np.array([]),np.array([]),np.array([])
    r=np.concatenate(Rs); sd=np.concatenate(sd); te=np.concatenate(te)
    yr=pd.Series(pd.to_datetime(te,unit="s",utc=True)).dt.year.to_numpy()
    if not verbose: return r,yr,sd
    sr=np.sort(r); k10=max(1,len(r)//10); d=r[yr<=2021]; cf=r[(yr>=2022)&(yr<=2024)]; oos=r[yr>=2025]
    nL=int((sd==1).sum()); nS=int((sd==-1).sum())
    both=nL>=15 and nS>=15 and r[sd==1].mean()>0 and r[sd==-1].mean()>0
    surv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and oos.mean()>0 and sr[:-k10].mean()>0 and both
    tag="ALIGNED (with D1)" if align else "COUNTER (vs D1) control"
    print(f"  {tag} rr{rr}: N={len(r)} avgR={r.mean():+.4f} PF={sb._pf(r):.2f} WR={(r>0).mean():.3f} | long {r[sd==1].mean():+.3f}(n{nL}) short {r[sd==-1].mean():+.3f}(n{nS})")
    print(f"    best10%rm={sr[:-k10].mean():+.4f} | D {d.mean():+.3f}(n{len(d)}) C {cf.mean():+.3f}(n{len(cf)}) O {oos.mean():+.3f}(n{len(oos)}) -> {'SURVIVOR' if surv else 'no'}")
    return r,yr,sd

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); inr,rlo,rhi=RR.build_h4_range(h4); ev=breakout_events(h4,inr,rlo,rhi); d1up=d1_trend_map(m)
    print(f"RS-2 cross-scale range-continuation breakout. {len(ev)} range-breakout events (gated to {RR.FP}).")
    run(m,h4,ev,d1up,align=True,rr=2.0)
    run(m,h4,ev,d1up,align=False,rr=2.0)   # counter-trend control (should be worse)
    print("  neighbor rr:")
    for rr in (1.0,3.0): run(m,h4,ev,d1up,align=True,rr=rr)

if __name__=="__main__":
    main()
