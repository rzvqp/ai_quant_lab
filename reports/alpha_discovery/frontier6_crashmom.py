"""F6-CRASHMOM — down-EXPANSION momentum SHORT with a TRAILING ride (distinct payoff, §7C/§7F).
Thesis: gold's DOWN moves are microstructurally different from its up-grind — risk-off spikes are fast and
one-directional. The 26 prior structural shorts used FIXED-RR structural stops (all dead). This tests a
velocity-gated momentum short that rides continuation with a chandelier trail. Diversifying (SHORT, risk-off).
Local trailing simulator (swing_base.py left UNTOUCHED to preserve COMP-CONT-L frozen fingerprint). DEV selection.
"""
import numpy as np, pandas as pd
import swing_base as sb

def sim_trail(df, sig_idx, side, init_risk, atr_arr, trail_mult, horizon, scenario="STRESS"):
    o=df["open"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); c=df["close"].to_numpy(); t=df["time"].to_numpy()
    n=len(df); cost=sb.COST[scenario]; rows=[]
    ir=np.asarray(init_risk,float)
    for k,i in enumerate(sig_idx):
        ei=i+1
        if ei>=n: continue
        risk=ir[k]; a=atr_arr[i]
        if not np.isfinite(risk) or risk<=0 or not np.isfinite(a): continue
        entry=o[ei]
        if side<0:
            hard=entry+risk  # initial structural stop (above)
            run_min=l[ei]; exit_px=None; exit_j=min(ei+horizon,n-1); mfe=0.0; mae=0.0
            for j in range(ei,min(ei+horizon+1,n)):
                fav=entry-l[j]; adv=h[j]-entry
                if fav>mfe: mfe=fav
                if adv>mae: mae=adv
                run_min=min(run_min,l[j])
                trail=min(hard, run_min+trail_mult*a)  # chandelier short stop, never worse than hard
                if h[j]>=trail:
                    exit_px=trail; exit_j=j; break
            if exit_px is None: exit_px=c[exit_j]
            gross=entry-exit_px
        else:
            hard=entry-risk; run_max=h[ei]; exit_px=None; exit_j=min(ei+horizon,n-1); mfe=0.0; mae=0.0
            for j in range(ei,min(ei+horizon+1,n)):
                fav=h[j]-entry; adv=entry-l[j]
                if fav>mfe: mfe=fav
                if adv>mae: mae=adv
                run_max=max(run_max,h[j])
                trail=max(hard, run_max-trail_mult*a)
                if l[j]<=trail:
                    exit_px=trail; exit_j=j; break
            if exit_px is None: exit_px=c[exit_j]
            gross=exit_px-entry
        net=gross-cost
        rows.append(dict(k=k,i=int(i),ei=int(ei),t_entry=int(t[ei]),side=side,entry=entry,risk=risk,
                         exit_px=exit_px,exit_j=int(exit_j),hold=int(exit_j-ei),
                         gross_R=gross/risk,R=net/risk,mfe_R=mfe/risk,mae_R=mae/risk,
                         sl_pips=risk/sb.PIP))
    return pd.DataFrame(rows)

N=10   # breakdown lookback
H=42
def signals(h4):
    o=h4["open"].to_numpy(); h=h4["high"].to_numpy(); l=h4["low"].to_numpy(); c=h4["close"].to_numpy()
    atr=h4["atr"].to_numpy(); atr_ma=h4["atr_ma"].to_numpy()
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1))))
    rng=h-l; closepos=np.where(rng>0,(c-l)/rng,0.5)
    ll=pd.Series(l).rolling(N).min().shift(1).to_numpy()
    downbar=(c<o); expansion=(tr>1.3*atr_ma); nearlow=(closepos<0.33); newlow=(c<ll)
    sig=downbar&expansion&nearlow&newlow&np.isfinite(atr_ma)
    # structural init stop = signal-bar high (crash-bar high)
    return sig, h

def run(h4,d1_up_aligned,dev_mask):
    o=h4["open"].to_numpy(); atr=h4["atr"].to_numpy(); sig,hi=signals(h4)
    raw=[i for i in np.where(sig)[0] if i+1<len(h4) and dev_mask[i]]
    ev=sb.dedup_events(np.array(raw),cooldown=N)
    for gate,tag in ((np.ones(len(ev),bool),"ALL"),(~d1_up_aligned[ev],"D1down")):
        e2=ev[gate]
        if len(e2)<8: print(f"  [{tag}] N={len(e2)} (too few)"); continue
        risk=np.array([hi[i]-o[i+1] for i in e2]); ok=np.isfinite(risk)&(risk>0); e2,r2=e2[ok],risk[ok]
        for tm in (2.0,3.0):
            scr=sim_trail(h4,e2,-1,r2,atr,trail_mult=tm,horizon=H,scenario="STRESS")
            if len(scr)<8: continue
            m=sb.metrics(scr.assign(tp_pips=0),h4,1.0); dc=sb.disc_conf(scr,h4,1.0)
            py=" ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
            dctxt=(f"DISC{dc['disc_avgR']:+.2f} CONF{dc['conf_avgR']:+.2f}" if dc else "dc n/a")
            print(f"  [{tag}] trail={tm}ATR: N={m['N']} posRate={m['WR_pos']:.2f} avgR={m['avgR']:+.3f} "
                  f"PF={m['PF']:.2f} best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} "
                  f"medMFE={scr['mfe_R'].median():.2f} medMAE={scr['mae_R'].median():.2f} advFirst={(scr['mae_R']>=1.0).mean():.2f} "
                  f"medSL={scr['sl_pips'].median():.0f}p | {dctxt} | {py}")

def main():
    tfs=sb.build_frames(); h4,d1=tfs["H4"],tfs["D1"]; dev_mask=h4["is_dev"].to_numpy()
    d1=d1.copy(); d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float)
    h4c=sb.align_context(h4,d1,["d1_up"],"_d1"); d1_up_aligned=(h4c["d1_up_d1"].to_numpy()>0.5)
    sig,_=signals(h4)
    print(f"F6-CRASHMOM  H4 DEV bars={int(dev_mask.sum())}  down-expansion events(DEV)={int((sig&dev_mask).sum())}")
    run(h4,d1_up_aligned,dev_mask)

if __name__=="__main__":
    main()
