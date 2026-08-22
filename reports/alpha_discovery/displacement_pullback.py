"""displacement_pullback.py — S10 canonical PULLBACK-FILL continuation entry (§14/§15/§16). After a mode-aligned
displacement that holds its origin, a LIMIT fill at ~50% (and 61.8%) of the displacement range; STRUCTURAL stop
just past the origin; target = continuation (small predeclared rr). Better entry price -> favorable R geometry.
Custom causal fill+sim with STRESS cost. Frozen mode taxonomy. Per cell x era, event-deduped.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd, hist_m15_data as m15d
from state_m15_discover import dedup
from displacement_info import disp
from liquidity_event import align_mode
COOL=8; H=32; KFILL=6; PIP=0.10; COST=0.24  # STRESS round-trip USD
CELLS=[
 ("PRIMARY_BULL_IMPULSE",'up',1,"C1 bull-disp->L"),
 ("BULL_CORRECTION",'dn',-1,"C2 bear-disp->S"),
 ("BEAR_CORRECTION",'dn',-1,"C3 bear-disp->S"),
 ("PRIMARY_BEAR_IMPULSE",'dn',-1,"C4 bear-disp->S"),
]

def sim_pullback(m, di, side, fillfrac, rr):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); n=len(m); R=[]
    for t in di:
        dhi=h[t]; dlo=l[t]; rng=dhi-dlo
        if rng<=0: continue
        origin=dlo if side==1 else dhi
        fill=(dhi-fillfrac*rng) if side==1 else (dlo+fillfrac*rng)
        risk=(fill-origin) if side==1 else (origin-fill)
        if risk<=0: continue
        target=(fill+rr*risk) if side==1 else (fill-rr*risk)
        filled=False; res=None
        for j in range(t+1, min(t+1+KFILL,n)):
            # invalidation before fill: origin reclaimed
            if side==1 and l[j]<origin: break
            if side==-1 and h[j]>origin: break
            if not filled:
                if (side==1 and l[j]<=fill) or (side==-1 and h[j]>=fill): filled=True; jf=j
                else: continue
            # from fill bar onward, resolve stop/target (stop checked first = conservative)
            for k in range(jf, min(t+1+KFILL+H,n)):
                if side==1:
                    if l[k]<=origin: res=-1.0; break
                    if h[k]>=target: res=rr; break
                else:
                    if h[k]>=origin: res=-1.0; break
                    if l[k]<=target: res=rr; break
            if res is None: res=0.0   # timeout ~ scratch
            break
        if filled and res is not None:
            R.append(res - COST/(risk if risk>0 else 1e9))   # net of STRESS cost in R units
    return np.array(R)

def run_era(tag, m, h4, af, mask):
    regc,uniq=align_mode(m,h4,af); up,dn=disp(m)
    print(f"\n[{tag}]")
    for md,dd_dir,side,lab in CELLS:
        if md not in uniq: continue
        code=uniq.index(md); dmask=(regc==code)&mask&(up if dd_dir=='up' else dn)
        di=np.where(dmask&dedup(dmask,COOL))[0]
        if len(di)<30: continue
        out=[]
        for ff in (0.5,0.618):
            for rr in (1.5,2.0,3.0):
                R=sim_pullback(m,di,side,ff,rr)
                if len(R)>=25: out.append((ff,rr,R.mean(),len(R),(R>0).mean()))
        if out:
            best=max(out,key=lambda x:x[2])
            s=" ".join(f"f{ff}rr{rr}:{avg:+.3f}(n{nn})" for ff,rr,avg,nn,wr in out)
            print(f"   {lab:16s}: {s}")

def main():
    print(f"S10 PULLBACK-FILL continuation (limit @50%/61.8% of displacement, structural stop=origin, STRESS net-R). H={H//4}h.")
    hm=m15d.build(verbose=False)["M15"]; hh4=hd._load("H4"); hh4["close_time"]=hh4["time"].to_numpy()+4*3600
    sm=sb.build_frames()["M15"]; sh4=sb.build_frames()["H4"]; yr=sm["dt"].dt.year.to_numpy(); dev=sm["is_dev"].to_numpy()
    run_era("b0",hm,hh4,m15d.align_causal,hm["is_b0"].to_numpy())
    run_era("b1",hm,hh4,m15d.align_causal,hm["is_b1"].to_numpy())
    for y in (2021,2022,2023): run_era(str(y),sm,sh4,sb.align_context,dev&(yr==y))

if __name__=="__main__":
    main()
