"""F5-COMPCONT-LONG adversarial vetting: parameter-neighborhood stability, CALIB out-of-selection,
single-sequence ledger + fingerprints, overlap-with-frozen-trend-beta proxy. Skeptic's pass (§24-26).
The candidate is robust ONLY if the a-priori core (W=20,H=42,rr=2.0) sits inside a STABLE positive neighborhood
(not a knife-edge) AND holds signs out-of-selection. Reports the FULL grid (no peak-picking).
"""
import numpy as np, pandas as pd, hashlib, json, os
import swing_base as sb

def comp_signals(h4, W):
    h=h4["high"].to_numpy(); l=h4["low"].to_numpy(); atr=h4["atr"].to_numpy(); atr_ma=h4["atr_ma"].to_numpy()
    bh=pd.Series(h).rolling(W).max().shift(1).to_numpy(); bl=pd.Series(l).rolling(W).min().shift(1).to_numpy()
    br=bh-bl; bma=pd.Series(br).rolling(50).mean().shift(1).to_numpy()
    comp=(atr<atr_ma)&(br<bma)&np.isfinite(br)&np.isfinite(atr)
    return comp, bh, bl

def events_long(h4, d1_up_aligned, mask, W, cooldown):
    o=h4["open"].to_numpy(); comp,bh,bl=comp_signals(h4,W)
    cond=comp & (d1_up_aligned==True) & mask
    raw=[i for i in np.where(cond)[0] if i+1<len(h4)]
    ev=sb.dedup_events(np.array(raw),cooldown=cooldown)
    risk=np.array([o[i+1]-bl[i] for i in ev]); ok=np.isfinite(risk)&(risk>0)
    return ev[ok], risk[ok]

def grid(h4, d1_up_aligned, dev_mask):
    print("== PARAMETER-NEIGHBORHOOD (STRESS, LONG, DEV) — core = W20/H42/rr2.0 ==")
    print("  W   H   cd  rr |   N  WRt   avgR    PF   best10  allYrs+  DISC  CONF")
    for W in (14,20,28):
        for H in (30,42,60):
            for cd in (12,20):
                for rr in (1.5,2.0):
                    ev,risk=events_long(h4,d1_up_aligned,dev_mask,W,cd)
                    if len(ev)<10: continue
                    tr=sb.simulate(h4,ev,+1,risk,rr=rr,horizon=H,scenario="STRESS")
                    m=sb.metrics(tr,h4,rr); dc=sb.disc_conf(tr,h4,rr)
                    allpos=all(v[0]>0 for v in m["per_year"].values())
                    core = (W==20 and H==42 and cd==20 and rr==2.0)
                    print(f"  {W:2d} {H:3d} {cd:3d} {rr:.1f} | {m['N']:3d} {m['WR_target']:.2f} "
                          f"{m['avgR']:+.3f} {m['PF']:.2f} {m['best10']:+.3f}  {str(allpos):5s}  "
                          f"{(dc['disc_avgR'] if dc else 0):+.2f} {(dc['conf_avgR'] if dc else 0):+.2f}"
                          + ("   <== CORE" if core else ""))

def calib_check(h4, d1_up_aligned):
    cal_mask=h4["is_cal"].to_numpy()
    ev,risk=events_long(h4,d1_up_aligned,cal_mask,20,20)
    print(f"\n== CALIB (2024-01..2024-06, out-of-selection) W20/H42 ==  events={len(ev)}")
    for rr in (1.5,2.0):
        tr=sb.simulate(h4,ev,+1,risk,rr=rr,horizon=42,scenario="STRESS")
        if len(tr)==0: print(f"  rr={rr}: N=0"); continue
        m=sb.metrics(tr,h4,rr)
        print(f"  rr={rr}: N={m['N']} WRt={m['WR_target']:.2f} avgR={m['avgR']:+.3f} PF={m['PF']:.2f} "
              f"posRate={m['WR_pos']:.2f}")

def ledger_and_fp(h4, d1_up_aligned, dev_mask):
    ev,risk=events_long(h4,d1_up_aligned,dev_mask,20,20)
    tr=sb.simulate(h4,ev,+1,risk,rr=2.0,horizon=42,scenario="STRESS").sort_values("t_entry").reset_index(drop=True)
    m=sb.metrics(tr,h4,2.0)
    # single-sequence stats
    r=tr["R"].to_numpy()
    print(f"\n== FROZEN HEADLINE LEDGER (W20/H42/rr2.0 STRESS, DEV) ==")
    print(f"  N={len(tr)} avgR={r.mean():+.4f} medR={np.median(r):+.3f} PF={sb._pf(r):.3f} "
          f"maxDD={sb._maxdd(r):.3f}R maxloss={r.min():+.3f}R WRt={m['WR_target']:.3f} posRate={m['WR_pos']:.3f}")
    print(f"  best1={m['best1']:+.3f} best5={m['best5']:+.3f} best10={m['best10']:+.3f} "
          f"medSL={m['med_sl_pips']:.0f}p medTP={m['med_tp_pips']:.0f}p medHold={m['med_hold']:.0f}bars tpm={m['trades_per_month']:.2f}")
    ledger=tr[["t_entry","side","entry","stop","targ","risk","exit_px","exit_reason","hold","R","gross_R","mae_R","mfe_R"]].round(5)
    ljson=ledger.to_dict(orient="records")
    src=open(os.path.join(sb._HERE,"frontier5_compcont.py"),"rb").read()+open(os.path.join(sb._HERE,"swing_base.py"),"rb").read()
    impl_fp=hashlib.sha256(src).hexdigest()
    cfg=dict(strategy="COMP-CONT-L-rr2", W=20, H=42, cooldown=20, rr=2.0, side="LONG",
             d1_ctx="EMA20>EMA50", comp="atr<atr_ma AND box<box_ma(50)", stop="compression_box_low",
             cost="STRESS_RT_0.24", tick=0.01, population="gated_M5->H4 DEV 2021-07..2023-12")
    cfg_fp=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
    led_fp=hashlib.sha256(json.dumps(ljson,sort_keys=True,default=str).encode()).hexdigest()
    out=dict(config=cfg, metrics={k:(v if not isinstance(v,dict) else {str(a):b for a,b in v.items()}) for k,v in m.items()},
             fingerprints=dict(implementation=impl_fp, config=cfg_fp, ledger=led_fp),
             ledger=ljson)
    with open(os.path.join(sb._HERE,"comp_cont_L_package.json"),"w") as f: json.dump(out,f,indent=1,default=str)
    print(f"  impl_fp={impl_fp[:16]} cfg_fp={cfg_fp[:16]} ledger_fp={led_fp[:16]}")
    print(f"  per-year: "+" ".join(f"{y}:{v[0]:+.3f}(n{v[1]})" for y,v in sorted(m['per_year'].items())))
    return out

def overlap_proxy(h4, d1_up_aligned, dev_mask):
    # Proxy for independence vs generic trend-beta: what fraction of comp-cont LONG entries occur on bars
    # that are ALSO H4 TREND_UP regime (i.e., would a naive protrend also be long there)?
    ev,risk=events_long(h4,d1_up_aligned,dev_mask,20,20)
    reg=h4["regime"].to_numpy()
    same=np.mean([reg[i] in ("TREND_UP",) for i in ev])
    print(f"\n== OVERLAP PROXY vs generic H4 protrend ==")
    print(f"  {same*100:.0f}pct of comp-cont-L signal bars are also H4 TREND_UP; "
          f"the rest fire in RANGE/TRANSITION/INDEP under D1-up (compression-timing adds entries protrend misses).")

def main():
    tfs=sb.build_frames(); h4,d1=tfs["H4"],tfs["D1"]; dev_mask=h4["is_dev"].to_numpy()
    d1=d1.copy(); d1["d1_up"]=(d1["ema20"]>d1["ema50"]).astype(float)
    h4c=sb.align_context(h4,d1,["d1_up"],"_d1"); d1_up_aligned=(h4c["d1_up_d1"].to_numpy()>0.5)
    grid(h4,d1_up_aligned,dev_mask)
    calib_check(h4,d1_up_aligned)
    overlap_proxy(h4,d1_up_aligned,dev_mask)
    ledger_and_fp(h4,d1_up_aligned,dev_mask)

if __name__=="__main__":
    main()
