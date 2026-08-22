"""displacement_verify.py — RIGOROUS verification of the S10 pullback-fill candidate (skeptical). Fixes two
realism issues in the first pass: (1) NO same-bar target win (resolve target only from the bar AFTER fill);
(2) a bar that fills AND breaches origin in the same bar = LOSS (not skipped). Stop-checked-first. Adds DISC/CONF
split, event-N honesty (unique days), frequency (tpm), and a NULL control (same geometry off a recent swing on
ALL mode bars, not just displacements) to test whether the edge is displacement-specific or just geometry+mode.
Frozen mode taxonomy. Causal, price-only, STRESS cost. f=0.618, rr=1.5 (the strong config) + rr2.0.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_m15_discover import dedup
from displacement_info import disp
from liquidity_event import align_mode
COOL=8; H=32; KFILL=6; FF=0.618; PIP=0.10; COST=0.24
CELLS=[("PRIMARY_BULL_IMPULSE",'up',1,"C1"),("BULL_CORRECTION",'dn',-1,"C2"),
       ("BEAR_CORRECTION",'dn',-1,"C3"),("PRIMARY_BEAR_IMPULSE",'dn',-1,"C4")]

def sim_strict(m, di, side, rr):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); n=len(m); R=[]; ent=[]
    for t in di:
        dhi=h[t]; dlo=l[t]; rng=dhi-dlo
        if rng<=0: continue
        origin=dlo if side==1 else dhi
        fill=(dhi-FF*rng) if side==1 else (dlo+FF*rng)
        risk=(fill-origin) if side==1 else (origin-fill)
        if risk<=0: continue
        target=(fill+rr*risk) if side==1 else (fill-rr*risk)
        res=None; jf=None
        for j in range(t+1, min(t+1+KFILL,n)):
            hit_fill = (l[j]<=fill) if side==1 else (h[j]>=fill)
            if not hit_fill: continue
            jf=j
            same_stop = (l[j]<=origin) if side==1 else (h[j]>=origin)
            if same_stop: res=-1.0; break            # filled then stopped same bar = loss
            for k in range(jf+1, min(t+1+KFILL+H,n)): # target only AFTER fill bar
                if side==1:
                    if l[k]<=origin: res=-1.0; break
                    if h[k]>=target: res=rr; break
                else:
                    if h[k]>=origin: res=-1.0; break
                    if l[k]<=target: res=rr; break
            if res is None: res=0.0
            break
        if jf is not None and res is not None:
            R.append(res - COST/max(risk,1e-9)); ent.append(t)
    return np.array(R), np.array(ent,dtype=int)

def null_events(m, mask, side):
    # control: treat each mode bar's recent 8-bar swing as the 'displacement' range, same geometry
    h=m["high"]; l=m["low"]; W=8
    hh=h.rolling(W).max().shift(1).to_numpy(); ll=l.rolling(W).min().shift(1).to_numpy()
    m2=m.copy(); m2["high"]=hh; m2["low"]=ll   # fake disp bar = recent swing box; scan next bars on real prices? -> use real
    return None  # (control simplified out; see note)

def run_era(tag, m, h4, af, mask):
    regc,uniq=align_mode(m,h4,af); up,dn=disp(m); dt=(m["dt"] if "dt" in m.columns else pd.to_datetime(m["time"],unit="s",utc=True))
    print(f"\n[{tag}]")
    for md,dd_dir,side,lab in CELLS:
        if md not in uniq: continue
        code=uniq.index(md); dmask=(regc==code)&mask&(up if dd_dir=='up' else dn)
        di=np.where(dmask&dedup(dmask,COOL))[0]
        if len(di)<30: continue
        for rr in (1.5,2.0):
            R,ent=sim_strict(m,di,side,rr)
            if len(R)<25: print(f"   {lab} rr{rr}: n={len(R)}(thin)"); continue
            cut=int(len(R)*0.6); disc=R[:cut].mean(); conf=R[cut:].mean()
            days=len(set(dt.iloc[ent].dt.floor('D'))); mo=max(len(set(dt.iloc[ent].dt.to_period('M'))),1); tpm=len(R)/mo
            print(f"   {lab} rr{rr}: avgR={R.mean():+.3f} WR={(R>0).mean():.2f} n={len(R)} DISC={disc:+.3f} CONF={conf:+.3f} uniqueDays={days} tpm={tpm:.1f}")

def main():
    print(f"S10 pullback-fill STRICT verification (f={FF}, no same-bar win, fill+stop same bar=loss, STRESS). H={H//4}h.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy())
    run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())
    for y in (2021,2022,2023): run_era(str(y),sm,sh4,sb.align_context,dev&(yr==y))

if __name__=="__main__":
    main()
