"""M15-F3 (historical intraday) — STRUCTURAL BREAK -> ACCEPTANCE -> FIRST RETEST (class D, §7D), both sides,
H4-regime-gated. Acceptance (price HOLDS beyond the level K bars, not a quick fail) is the strongest filter
against false-break noise (the M15-F1/F2 killer). Stop at the acceptance-base extreme (wider, thesis-owned).
Causal hist_m15_data (governance-proven). Path-first (§13), event-dedup (§12), overlap-checked if survives.
"""
import numpy as np, pandas as pd
import hist_m15_data as m15d, swing_base as sb, external_common as ec

ND=8; K=3; RW=10; H=48  # break lookback, acceptance bars, retest window, horizon
def events(df, side, ctx, disc):
    o=df["open"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); c=df["close"].to_numpy()
    atr=df["atr"].to_numpy(); seg=df["seg"].to_numpy(); n=len(df)
    hh=pd.Series(h).rolling(ND).max().shift(1).to_numpy(); ll=pd.Series(l).rolling(ND).min().shift(1).to_numpy()
    brk=(c>hh) if side>0 else (c<ll)
    ev=[]; risk=[]
    for b in np.where(brk&ctx&disc)[0]:
        lvl=hh[b] if side>0 else ll[b]
        if b+K+1>=n or not np.isfinite(lvl): continue
        if any(seg[b+i]!=seg[b] for i in range(1,K+1)): continue
        # acceptance: K bars all close beyond level
        acc=all((c[b+i]>lvl) if side>0 else (c[b+i]<lvl) for i in range(1,K+1))
        if not acc: continue
        base=b+K
        # base extreme (acceptance low/high) = wider structural stop
        if side>0: base_ext=l[b:base+1].min()
        else:      base_ext=h[b:base+1].max()
        # first retest: pull back to level and hold
        for j in range(base+1, min(base+1+RW,n)):
            if seg[j]!=seg[b]: break
            if side>0 and l[j]<=lvl and c[j]>lvl and j+1<n:
                r=o[j+1]-(min(base_ext,l[j])-0.2*atr[j]);
                if np.isfinite(r) and r>0: ev.append(j); risk.append(r)
                break
            if side<0 and h[j]>=lvl and c[j]<lvl and j+1<n:
                r=(max(base_ext,h[j])+0.2*atr[j])-o[j+1]
                if np.isfinite(r) and r>0: ev.append(j); risk.append(r)
                break
    ev=np.array(ev,dtype=int); risk=np.array(risk)
    if len(ev): keep=sb.dedup_events(ev,cooldown=RW); m=np.isin(ev,keep); ev,risk=ev[m],risk[m]
    return ev,risk

def report(df, ev, side, risk, tag):
    if len(ev)<10: print(f"    [{tag}] N={len(ev)} (too few)"); return
    ps=ec.path_stats(df,ev,side,risk,H)
    print(f"    [{tag}] N={ps['N']} medMFE={ps['medMFE']:.2f} medMAE={ps['medMAE']:.2f} advF={ps['advFirst']:.2f} "
          f"P(+1<-1)={ps['P_1']:.2f} mfe100={ps['mfe100']:.2f} medSLpre")
    for rr in (1.0,1.5,2.0):
        tr=sb.simulate(df,ev,side,risk,rr=rr,horizon=H,scenario="STRESS"); m=sb.metrics(tr,df,rr); dc=sb.disc_conf(tr,df,rr)
        te=df["time"].to_numpy()[ev+1]; b0=(te<=m15d.BLOCKS["b0"][1]); rB=tr["R"].to_numpy()
        py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
        print(f"      rr={rr}: WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} best5={m['best5']:+.3f} "
              f"best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} medSL={m['med_sl_pips']:.0f}p tpm={m['trades_per_month']:.1f} "
              f"| DISC{(dc['disc_avgR'] if dc else 0):+.2f}/CONF{(dc['conf_avgR'] if dc else 0):+.2f} | b0 {rB[b0].mean():+.2f}(n{int(b0.sum())}) b1 {rB[~b0].mean():+.2f}(n{int((~b0).sum())}) | {py}")

def main():
    tfs=m15d.build(verbose=True); m15=tfs["M15"]; h4=tfs["H4"].copy()
    h4["h4_up"]=(h4["ema20"]>h4["ema50"]).astype(float); h4["h4_dn"]=(h4["ema20"]<h4["ema50"]).astype(float)
    a=m15d.align_causal(m15,h4,["h4_up","h4_dn"],""); h4_up=(a["h4_up"].to_numpy()>0.5); h4_dn=(a["h4_dn"].to_numpy()>0.5)
    disc=m15["is_disc"].to_numpy()
    print("M15-F3 break->acceptance->first-retest (both sides, H4-regime-gated)")
    eL,rL=events(m15,+1,h4_up,disc); print(f"  LONG (H4-up) events={len(eL)}"); report(m15,eL,+1,rL,"LONG H4-up")
    eS,rS=events(m15,-1,h4_dn,disc); print(f"  SHORT (H4-dn) events={len(eS)}"); report(m15,eS,-1,rS,"SHORT H4-dn")

if __name__=="__main__":
    main()
