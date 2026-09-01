"""sc_L1.py — INDEPENDENT ALPHA REPLICATION of Statistician lead L1 (LONDON). Reproduce the INFORMATION first (no strategy).

Frozen L1 reconstructed from its stated properties (no event table copied; causal definition only):
  L1 EVENT = the first native-M5 bar at/after the DST-correct London open (08:00 Europe/London), ONE event per trading day.
  PHENOMENON = forward path from L1 reaches +/-100 project pips materially FASTER than a matched baseline (Statistician: ~3.4h vs ~6.9h).
Baselines: (U) unconditional = first M5 bar at/after a fixed non-London UTC hour (02:00, Asia) per day [same-1/day exposure];
           (A) all-bars random-time sample. Direction is NOT assumed. 1 project pip = $0.10. Native M5 2021-07-27+.
Report: N, independent episodes, time-to-+/-100/200/300p (median h), reach fractions, P(+100 before -100) (directional test),
MFE/MAE, per-year, non-overlap. NO optimization.
"""
import sys, numpy as np, pandas as pd, hashlib, datetime as dt
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import m5_core as MC, session_tz as STZ

PIP=0.10; MAXH=576  # 48h max horizon (avoid censoring)
SPEC="L1=first M5 bar at/after London-open(08:00 Europe/London, DST) per day; fwd time-to-+/-100p vs Asia-open(02:00 UTC) baseline; native M5"
def spec_hash(): return hashlib.sha256(SPEC.encode()).hexdigest()[:16]

def first_bar_after(t, target_epochs):
    """index of first M5 bar whose time >= target for each target (vectorized via searchsorted)."""
    return np.searchsorted(t, target_epochs, side="left")

def london_events(M):
    t=M["t"]; dates=pd.to_datetime(t,unit='s',utc=True).date
    uniq=sorted(set(dates.tolist()))
    lon=STZ.build_anchor_maps(uniq)["london_open"]
    tgt=np.array([lon[d] for d in uniq],dtype="int64")
    idx=first_bar_after(t,tgt); idx=idx[idx<M["n"]-MAXH-1]
    # keep only bars actually near the open (within 5 min)
    keep=[i for i,ep in zip(idx,tgt[:len(idx)]) if abs(int(t[i])-int(ep))<=300]
    return np.array(keep)

def baseline_events(M, utc_hour=2):
    t=M["t"]; hr=M["hr"]; dates=pd.to_datetime(t,unit='s',utc=True).date
    # first bar of each day at/after utc_hour
    df=pd.DataFrame({"i":np.arange(M["n"]),"d":dates,"hr":hr}); df=df[df.hr>=utc_hour]
    idx=df.groupby("d")["i"].first().to_numpy()
    return idx[idx<M["n"]-MAXH-1]

def fwd_stats(M, idx):
    c=M["c"];h=M["h"];l=M["l"];t=M["t"]; rows=[]
    for i in idx:
        c0=c[i]; up=None; dn=None; t100=t200=t300=np.nan; side100=0
        mfe=0.0; mae=0.0
        for j in range(i+1, min(i+MAXH, M["n"])):
            fu=(h[j]-c0)/PIP; fd=(c0-l[j])/PIP; mfe=max(mfe,fu); mae=max(mae,fd)
            hrs=(t[j]-t[i])/3600.0
            if np.isnan(t100):
                if fu>=100 or fd>=100:
                    t100=hrs; side100=1 if (fu>=100 and (fd<100 or h[j]-c0>=c0-l[j])) else -1
            if np.isnan(t200) and (fu>=200 or fd>=200): t200=hrs
            if np.isnan(t300) and (fu>=300 or fd>=300): t300=hrs
            if not np.isnan(t100) and not np.isnan(t300): break
        # directional: which of +100/-100 hit first
        yr=pd.to_datetime(t[i],unit='s',utc=True).year
        rows.append(dict(i=i,t100=t100,t200=t200,t300=t300,side100=side100,mfe=mfe,mae=mae,yr=yr,
                         r100=int(not np.isnan(t100)),r200=int(not np.isnan(t200)),r300=int(not np.isnan(t300))))
    return rows

def summ(rows,label):
    t100=np.array([r["t100"] for r in rows],float); r100=np.array([r["r100"] for r in rows])
    med100=np.nanmedian(t100)
    side=np.array([r["side100"] for r in rows]); up=np.mean(side[side!=0]>0) if (side!=0).any() else np.nan
    print(f"{label:26s} N={len(rows):5d} reach100={r100.mean():.3f} med_t100={med100:.1f}h "
          f"reach200={np.mean([r['r200'] for r in rows]):.3f} reach300={np.mean([r['r300'] for r in rows]):.3f} "
          f"P(+100 first)={up:.3f} MFE={np.median([r['mfe'] for r in rows]):.0f}p MAE={np.median([r['mae'] for r in rows]):.0f}p")
    return med100, up, t100

def main():
    M=MC.load()
    print(f"L1_SPEC_HASH={spec_hash()}")
    print(f"SPEC: {SPEC}")
    Lidx=london_events(M); Bidx=baseline_events(M,2)
    print(f"\nL1 London events={len(Lidx)}  baseline(Asia 02:00) events={len(Bidx)}")
    Lr=fwd_stats(M,Lidx); Br=fwd_stats(M,Bidx)
    print("\n== INFORMATION REPRODUCTION (time-to-expansion) ==")
    lm,lup,lt=summ(Lr,"L1_LONDON"); bm,bup,bt=summ(Br,"BASELINE_ASIA")
    print(f"\ntime-to-100p: London {lm:.1f}h vs baseline {bm:.1f}h  (Statistician clue ~3.4 vs 6.9h)")
    print(f"direction P(+100 first): London {lup:.3f} vs baseline {bup:.3f}  (~0.50 => EXPANSION not DIRECTION)")
    # per-year time-to-100
    print("\n== per-year median time-to-100p (London) — 6/6 consistency ==")
    for y in sorted(set(r['yr'] for r in Lr)):
        ly=[r['t100'] for r in Lr if r['yr']==y and not np.isnan(r['t100'])]
        by=[r['t100'] for r in Br if r['yr']==y and not np.isnan(r['t100'])]
        print(f"  {y}: London {np.median(ly):.1f}h (n{len(ly)}) vs baseline {np.median(by):.1f}h (n{len(by)}) -> faster={np.median(ly)<np.median(by)}")

if __name__=="__main__":
    main()
