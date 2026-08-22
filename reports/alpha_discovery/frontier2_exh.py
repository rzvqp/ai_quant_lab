"""F2-EXH-REV — exhaustion / over-extension reversal, SWING horizon.
Pre-entry info = statistical over-extension (NOT a generic fade): price far from anchor, or a long consecutive run.
Two mechanism variants, both cheap-screened path-first, both sides independent.
  A) ATR-extension: ext=(close-ema50)/atr14 on H4 beyond E -> reversal-confirm bar -> reversion trade.
  B) D1 consecutive-run: >=K consecutive D1 same-direction closes -> H4 reversal-confirm -> reversion trade.
Structural stop = beyond the exhaustion extreme (rolling max/min over W). RR {1.0,1.5,2.0}. Reversion toward anchor.
Firewall via swing_base. DEV selection.
"""
import numpy as np, pandas as pd
import swing_base as sb

W = 12   # extreme window for structural stop (H4)
H = 42   # swing horizon (H4 bars ~7d)

def conv_report(h4, ev, side, risk, tag):
    if len(ev) < 8:
        print(f"    [{tag}] N={len(ev)} (too few)"); return
    scr = sb.simulate(h4, ev, side, risk, rr=10.0, horizon=H, scenario="STRESS")
    af = float((scr["mae_R"] >= 1.0).mean())
    print(f"    [{tag}] SCREEN N={len(scr)} medMFE={scr['mfe_R'].median():.2f}R "
          f"medMAE={scr['mae_R'].median():.2f}R advFirst={af:.2f} medSL={scr['sl_pips'].median():.0f}p")
    for rr in (1.0, 1.5, 2.0):
        tr = sb.simulate(h4, ev, side, risk, rr=rr, horizon=H, scenario="STRESS")
        m = sb.metrics(tr, h4, rr); dc = sb.disc_conf(tr, h4, rr)
        py = " ".join(f"{y}:{v[0]:+.2f}(n{v[1]})" for y,v in sorted(m["per_year"].items()))
        dctxt = (f"DISC{dc['disc_avgR']:+.2f} CONF{dc['conf_avgR']:+.2f}" if dc else "dc n/a")
        print(f"      rr={rr}: WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} "
              f"best10={m['best10']:+.3f} maxDD={m['maxDD_R']:.1f} | {dctxt} | {py}")

def variantA(h4, dev_mask):
    c=h4["close"].to_numpy(); o=h4["open"].to_numpy(); h=h4["high"].to_numpy(); l=h4["low"].to_numpy()
    e50=h4["ema50"].to_numpy(); atr=h4["atr"].to_numpy()
    ext = (c - e50)/atr
    hh = pd.Series(h).rolling(W).max().to_numpy(); ll = pd.Series(l).rolling(W).min().to_numpy()
    for E in (2.5, 3.0):
        # SHORT: extended up, first down-close confirm
        up_ext = np.isfinite(ext) & (ext > E)
        conf_s = up_ext & (c < o)                      # reversal confirm bar
        raw = np.array([i for i in np.where(conf_s)[0] if i+1<len(c) and dev_mask[i]])
        ev = sb.dedup_events(raw, cooldown=W)
        risk = np.array([hh[i]-o[i+1] for i in ev])
        ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
        print(f"  A-SHORT E={E}: events={len(ev)}")
        conv_report(h4, ev, -1, risk, f"A-SHORT E={E}")
        # LONG: extended down, first up-close confirm
        dn_ext = np.isfinite(ext) & (ext < -E)
        conf_l = dn_ext & (c > o)
        raw = np.array([i for i in np.where(conf_l)[0] if i+1<len(c) and dev_mask[i]])
        ev = sb.dedup_events(raw, cooldown=W)
        risk = np.array([o[i+1]-ll[i] for i in ev])
        ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
        print(f"  A-LONG E={E}: events={len(ev)}")
        conv_report(h4, ev, +1, risk, f"A-LONG E={E}")

def variantB(h4, d1, dev_mask):
    # consecutive D1 run count, aligned causally to H4
    dc = d1["close"].to_numpy(); dup = (np.diff(dc, prepend=dc[0])>0).astype(int)
    run_up=np.zeros(len(dc),int); run_dn=np.zeros(len(dc),int)
    for i in range(1,len(dc)):
        run_up[i]=run_up[i-1]+1 if dup[i]==1 else 0
        run_dn[i]=run_dn[i-1]+1 if dup[i]==0 else 0
    d1=d1.copy(); d1["run_up"]=run_up; d1["run_dn"]=run_dn
    h4c = sb.align_context(h4, d1, ["run_up","run_dn"], "_d1")
    ru=h4c["run_up_d1"].to_numpy(); rd=h4c["run_dn_d1"].to_numpy()
    c=h4["close"].to_numpy(); o=h4["open"].to_numpy(); h=h4["high"].to_numpy(); l=h4["low"].to_numpy()
    hh=pd.Series(h).rolling(W).max().to_numpy(); ll=pd.Series(l).rolling(W).min().to_numpy()
    for K in (4,5):
        # SHORT after >=K up-days + H4 down-confirm
        cond_s=(ru>=K)&(c<o)
        raw=np.array([i for i in np.where(cond_s)[0] if i+1<len(c) and dev_mask[i]])
        ev=sb.dedup_events(raw,cooldown=W); risk=np.array([hh[i]-o[i+1] for i in ev])
        ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
        print(f"  B-SHORT K={K}: events={len(ev)}"); conv_report(h4,ev,-1,risk,f"B-SHORT K={K}")
        # LONG after >=K down-days + H4 up-confirm
        cond_l=(rd>=K)&(c>o)
        raw=np.array([i for i in np.where(cond_l)[0] if i+1<len(c) and dev_mask[i]])
        ev=sb.dedup_events(raw,cooldown=W); risk=np.array([o[i+1]-ll[i] for i in ev])
        ok=np.isfinite(risk)&(risk>0); ev,risk=ev[ok],risk[ok]
        print(f"  B-LONG K={K}: events={len(ev)}"); conv_report(h4,ev,+1,risk,f"B-LONG K={K}")

def main():
    tfs=sb.build_frames(); h4,d1=tfs["H4"],tfs["D1"]; dev_mask=h4["is_dev"].to_numpy()
    print(f"F2-EXH-REV  H4 DEV bars={int(dev_mask.sum())}")
    print("Variant A: ATR-extension reversal")
    variantA(h4, dev_mask)
    print("Variant B: D1 consecutive-run reversal")
    variantB(h4, d1, dev_mask)

if __name__=="__main__":
    main()
