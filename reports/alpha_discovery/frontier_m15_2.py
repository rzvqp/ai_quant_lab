"""M15-F2 (historical intraday) — SESSION impulse -> reset -> SECOND LEG (class E, §7E). London & NY sessions
(UTC), both directions. Opening-range (first 8 M15 = 2h) -> first break = impulse -> pullback/reset -> second
push beyond the impulse extreme = entry; stop at the reset extreme (session-structural, WIDER than M15-F1's tight
continuation stop, per the M15-F1 learning). Economic reason (§8): b0/b1 trending regimes may give session
second-legs cleaner follow-through than choppy 2021-23. Causal hist_m15_data (governance-proven). Path-first.
"""
import numpy as np, pandas as pd
import hist_m15_data as m15d, swing_base as sb, external_common as ec

ORN=8; H=24  # opening-range = 8 M15 (2h); horizon 24 M15 (~6h, rest of session)
SESSIONS={"London":(7,16),"NY":(13,21)}

def session_second_legs(df, sess):
    o=df["open"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); c=df["close"].to_numpy()
    dt=df["dt"]; hour=dt.dt.hour.to_numpy(); day=dt.dt.floor("D"); seg=df["seg"].to_numpy(); n=len(df)
    lo_h,hi_h=SESSIONS[sess]
    inwin=(hour>=lo_h)&(hour<hi_h)
    dfi=df.assign(_g=day.astype(str)+"|"+seg.astype(str))
    evL=[];rL=[];evS=[];rS=[]
    for _,grp in dfi[inwin].groupby("_g"):
        idx=grp.index.to_numpy()
        if len(idx)<ORN+4: continue
        or_hi=h[idx[:ORN]].max(); or_lo=l[idx[:ORN]].min(); post=idx[ORN:]
        # first break = impulse
        imp=None
        for k in post:
            if c[k]>or_hi: imp=(k,+1,h[k]); break
            if c[k]<or_lo: imp=(k,-1,l[k]); break
        if imp is None: continue
        ik,idir,iext=imp
        rest=[k for k in post if k>ik]
        if idir>0:
            reset_lo=l[ik]; had_pb=False
            for j in rest:
                if l[j]<reset_lo: reset_lo=l[j]
                if c[j]<o[j] or l[j]<or_hi: had_pb=True
                if had_pb and c[j]>iext and j+1<n:
                    r=o[j+1]-reset_lo
                    if np.isfinite(r) and r>0: evL.append(j); rL.append(r)
                    break
        else:
            reset_hi=h[ik]; had_pb=False
            for j in rest:
                if h[j]>reset_hi: reset_hi=h[j]
                if c[j]>o[j] or h[j]>or_lo: had_pb=True
                if had_pb and c[j]<iext and j+1<n:
                    r=reset_hi-o[j+1]
                    if np.isfinite(r) and r>0: evS.append(j); rS.append(r)
                    break
    return (np.array(evL,dtype=int),np.array(rL)),(np.array(evS,dtype=int),np.array(rS))

def report(df, ev, side, risk, tag):
    if len(ev)<10: print(f"    [{tag}] N={len(ev)} (too few)"); return
    ps=ec.path_stats(df,ev,side,risk,H)
    print(f"    [{tag}] N={ps['N']} medMFE={ps['medMFE']:.2f} medMAE={ps['medMAE']:.2f} advF={ps['advFirst']:.2f} "
          f"P(+1<-1)={ps['P_1']:.2f} mfe50={ps['mfe50']:.2f} mfe100={ps['mfe100']:.2f}")
    for rr in (1.0,1.5,2.0):
        tr=sb.simulate(df,ev,side,risk,rr=rr,horizon=H,scenario="STRESS"); m=sb.metrics(tr,df,rr); dc=sb.disc_conf(tr,df,rr)
        te=df["time"].to_numpy()[ev+1]; b0=(te<=m15d.BLOCKS["b0"][1]); rB=tr["R"].to_numpy()
        py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
        print(f"      rr={rr}: WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} best5={m['best5']:+.3f} "
              f"best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} medSL={m['med_sl_pips']:.0f}p tpm={m['trades_per_month']:.1f} "
              f"| DISC{(dc['disc_avgR'] if dc else 0):+.2f}/CONF{(dc['conf_avgR'] if dc else 0):+.2f} | b0 {rB[b0].mean():+.2f}(n{int(b0.sum())}) b1 {rB[~b0].mean():+.2f}(n{int((~b0).sum())}) | {py}")

def main():
    tfs=m15d.build(verbose=True); m15=tfs["M15"]
    print("M15-F2 session impulse->reset->second-leg (London & NY, both sides)")
    for sess in ("London","NY"):
        (evL,rL),(evS,rS)=session_second_legs(m15,sess)
        print(f"  {sess} 2nd-leg: LONG events={len(evL)} SHORT events={len(evS)}")
        report(m15,evL,+1,rL,f"{sess} LONG")
        report(m15,evS,-1,rS,f"{sess} SHORT")

if __name__=="__main__":
    main()
