"""M15-F1 (historical intraday) — DISPLACEMENT -> FIRST PULLBACK -> RESUMPTION (class B), both sides, gated to
causal H4 regime. Economic reason (§8): b0/b1 trending regimes (2013 bear, 2016-17) may give intraday
displacement-continuation cleaner follow-through than choppy 2021-23 (where it was exhausted). Higher frequency.
Causal hist_m15_data (governance-proven slice). Path-first (§13), event-dedup (§12), overlap checks (§9/§10).
"""
import numpy as np, pandas as pd, json, os
import hist_m15_data as m15d, swing_base as sb, external_common as ec

ND=8; W=8; H=48  # displacement lookback, pullback window, horizon (M15 bars ~12h)
def disp_events(df, side, ctx, disc):
    o=df["open"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); c=df["close"].to_numpy()
    atr_ma=df["atr_ma"].to_numpy(); seg=df["seg"].to_numpy(); n=len(df)
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1))))
    rng=h-l; cpos=np.where(rng>0,(c-l)/rng,0.5)
    hh=pd.Series(h).rolling(ND).max().shift(1).to_numpy(); ll=pd.Series(l).rolling(ND).min().shift(1).to_numpy()
    exp=tr>1.3*atr_ma
    if side>0: disp=(c>hh)&exp&(cpos>0.66)
    else:      disp=(c<ll)&exp&(cpos<0.34)
    ev=[]; risk=[]
    for d in np.where(disp&ctx&disc)[0]:
        if d+2>=n: continue
        pb=None; had_dip=False
        if side>0:
            pbl=l[d]
            for j in range(d+1,min(d+1+W,n)):
                if seg[j]!=seg[d]: break
                if c[j]<o[j]: had_dip=True
                pbl=min(pbl,l[j])
                if had_dip and c[j]>h[d] and j+1<n:
                    pb=(j,pbl); break
            if pb: jj,plow=pb; r=o[jj+1]-(plow-0.2*(h[d]-l[d]))
        else:
            pbh=h[d]
            for j in range(d+1,min(d+1+W,n)):
                if seg[j]!=seg[d]: break
                if c[j]>o[j]: had_dip=True
                pbh=max(pbh,h[j])
                if had_dip and c[j]<l[d] and j+1<n:
                    pb=(j,pbh); break
            if pb: jj,phigh=pb; r=(phigh+0.2*(h[d]-l[d]))-o[jj+1]
        if pb and np.isfinite(r) and r>0: ev.append(jj); risk.append(r)
    ev=np.array(ev,dtype=int); risk=np.array(risk)
    # event dedup: one per cooldown (§12)
    if len(ev):
        keep=sb.dedup_events(ev,cooldown=W); m=np.isin(ev,keep); ev,risk=ev[m],risk[m]
    return ev,risk

def report(df, ev, side, risk, tag):
    if len(ev)<10: print(f"    [{tag}] N={len(ev)} (too few)"); return None
    ps=ec.path_stats(df,ev,side,risk,H)
    print(f"    [{tag}] N={ps['N']} medMFE={ps['medMFE']:.2f} medMAE={ps['medMAE']:.2f} P90MAE={ps['P90_MAE']:.2f} "
          f"advF={ps['advFirst']:.2f} P(+1<-1)={ps['P_1']:.2f} P(+1.5<-1)={ps['P_15']:.2f} mfe50={ps['mfe50']:.2f} mfe100={ps['mfe100']:.2f}")
    for rr in (1.0,1.5,2.0):
        tr=sb.simulate(df,ev,side,risk,rr=rr,horizon=H,scenario="STRESS"); m=sb.metrics(tr,df,rr); dc=sb.disc_conf(tr,df,rr)
        te=df["time"].to_numpy()[ev+1]; b0=(te<=m15d.BLOCKS["b0"][1]); rB=tr["R"].to_numpy()
        py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
        print(f"      rr={rr}: WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} best5={m['best5']:+.3f} "
              f"best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} medSL={m['med_sl_pips']:.0f}p tpm={m['trades_per_month']:.1f} "
              f"| DISC{(dc['disc_avgR'] if dc else 0):+.2f}/CONF{(dc['conf_avgR'] if dc else 0):+.2f} | b0 {rB[b0].mean():+.2f}(n{int(b0.sum())}) b1 {rB[~b0].mean():+.2f}(n{int((~b0).sum())}) | {py}")
    return ev

def main():
    tfs=m15d.build(verbose=True); m15=tfs["M15"]; h4=tfs["H4"].copy()
    h4["h4_up"]=(h4["ema20"]>h4["ema50"]).astype(float); h4["h4_dn"]=(h4["ema20"]<h4["ema50"]).astype(float)
    a=m15d.align_causal(m15,h4,["h4_up","h4_dn"],""); h4_up=(a["h4_up"].to_numpy()>0.5); h4_dn=(a["h4_dn"].to_numpy()>0.5)
    disc=m15["is_disc"].to_numpy()
    print("M15-F1 displacement->first-pullback->resume (both sides, H4-regime-gated)")
    print("  LONG (H4-up):")
    evL=report(m15, *disp_events(m15,+1,h4_up,disc)[:1], None) if False else None
    eL,rL=disp_events(m15,+1,h4_up,disc); print(f"   events={len(eL)}"); evL=report(m15,eL,+1,rL,"LONG H4-up")
    print("  SHORT (H4-down):")
    eS,rS=disp_events(m15,-1,h4_dn,disc); print(f"   events={len(eS)}"); evS=report(m15,eS,-1,rS,"SHORT H4-dn")

if __name__=="__main__":
    main()
