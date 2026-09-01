"""dae_scan.py — DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1. Two-sided OCO: anchor -> symmetric UP/DOWN activations -> first causal trigger
selects direction (opposite cancelled) -> harvest expansion. NO direction prediction. Native M15 2011-2026, one INDEPENDENT episode/day.
Conservative same-bar (both activations in one bar -> ambiguous=skip; entry+stop in one bar -> stop). Cost 0.419 price/trade. 24h=96 bars.
Architectures: continuation (follow first side) / failed-reversal (if first side stops out, take opposite). Benchmarks + drift positive control.
"""
import sys, math, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD
PIP=0.10; COST=0.419; H=96

def load():
    m=CD.load_m15().reset_index(drop=True)
    dt=m["dt"]; return dict(o=m["open"].to_numpy(float),h=m["high"].to_numpy(float),l=m["low"].to_numpy(float),
        c=m["close"].to_numpy(float),t=m["time"].to_numpy(),yr=dt.dt.year.to_numpy(),
        date=dt.dt.date.values,hr=dt.dt.hour.to_numpy(),n=len(m))

def day_starts(M):
    """first bar index of each UTC day + prior-day high/low (causal)."""
    date=M["date"]; h=M["h"]; l=M["l"]; starts=[]; pdh=[]; pdl=[]
    df=pd.DataFrame({"i":np.arange(M["n"]),"d":date,"h":h,"l":l})
    g=df.groupby("d"); firsts=g["i"].first(); dhi=g["h"].max(); dlo=g["l"].min()
    days=list(firsts.index)
    for k in range(1,len(days)):
        starts.append(int(firsts.iloc[k])); pdh.append(float(dhi.iloc[k-1])); pdl.append(float(dlo.iloc[k-1]))
    return np.array(starts), np.array(pdh), np.array(pdl)

def oco_episode(M, s, up_act, dn_act, arch="cont"):
    """From episode start s, over next H bars: OCO first trigger, then continuation (or failed-reversal). Returns net-R or None.
    risk = |up_act-dn_act| (stop = opposite activation). target = entry + dir*risk (1:1). same-bar conservative."""
    h=M["h"];l=M["l"];c=M["c"];n=M["n"]; end=min(s+H,n-1); risk=up_act-dn_act
    if risk<=0: return None
    trig=None
    for j in range(s+1,end+1):
        up=h[j]>=up_act; dn=l[j]<=dn_act
        if up and dn: return dict(net=np.nan, side=0, whip=1)   # both in one bar -> ambiguous, skip (whipsaw)
        if up: trig=(j,+1,up_act); break
        if dn: trig=(j,-1,dn_act); break
    if trig is None: return dict(net=np.nan, side=0, notrig=1)
    j,d,entry=trig
    stop = dn_act if d>0 else up_act; tgt = entry + d*risk
    # resolve continuation from trigger bar (conservative same-bar: both -> stop)
    def resolve(entry,stop,tgt,d,start):
        for k in range(start,end+1):
            ht=(h[k]>=tgt) if d>0 else (l[k]<=tgt); hs=(l[k]<=stop) if d>0 else (h[k]>=stop)
            if ht and hs: return -1.0,k
            if hs: return -1.0,k
            if ht: return +1.0,k
        return d*(c[end]-entry)/risk, end
    r,kexit=resolve(entry,stop,tgt,d,j)
    cost_R=COST/risk
    if arch=="cont":
        return dict(net=r-cost_R, side=d, risk=risk, whip=0)
    # failed-reversal: only trade if continuation STOPPED OUT (r==-1), then take opposite from the opposite activation
    if r>-1.0: return dict(net=np.nan, side=0, noreverse=1)   # first side didn't fail -> no reversal trade
    d2=-d; entry2=stop; stop2=entry; tgt2=entry2+d2*risk
    r2,_=resolve(entry2,stop2,tgt2,d2,kexit)
    return dict(net=r2-2*cost_R, side=d2, risk=risk, whip=0)  # 2 costs (first stop + reversal)

def agg(M, rows, label):
    net=np.array([r["net"] for r in rows if r and np.isfinite(r.get("net",np.nan))])
    tot=len(rows); notrig=sum(1 for r in rows if r and r.get("notrig")); whip=sum(1 for r in rows if r and r.get("whip"))
    if len(net)<40: print(f"{label:30s} traded={len(net)} notrig={notrig} both-same-bar={whip} (too few)"); return None
    starts=np.array([r["_s"] for r in rows if r and np.isfinite(r.get("net",np.nan))]); yE=M["yr"][starts]
    dev=yE<=2019; pre=yE<2021
    top1=np.sort(net)[-max(1,len(net)//100):].sum()/net.sum() if net.sum()>0 else float('nan')
    drop5=np.sort(net)[:int(len(net)*0.95)].mean()
    print(f"{label:30s} trades={len(net):5d} net={net.mean():+.3f} WR={(net>0).mean():.3f} "
          f"DEV={net[dev].mean():+.3f} OOS={net[~dev].mean():+.3f} PRE={net[pre].mean():+.3f} POST={net[~pre].mean():+.3f} "
          f"drop5%={drop5:+.3f} top1%={top1:.2f} notrig={notrig} both1bar={whip}")
    return net.mean()

def run_anchor(M, starts, up_acts, dn_acts, arch, label):
    rows=[]
    for s,ua,da in zip(starts,up_acts,dn_acts):
        r=oco_episode(M,s,ua,da,arch)
        if r is not None: r["_s"]=s; rows.append(r)
    return agg(M,rows,label)

def main():
    M=load(); starts,pdh,pdl=day_starts(M)
    o=M["o"]; anchor=o[starts]
    # daily-ATR proxy = prior-day range
    pdr=pdh-pdl; ok=(pdr>0)&np.isfinite(pdr)
    starts,anchor,pdh,pdl,pdr=starts[ok],anchor[ok],pdh[ok],pdl[ok],pdr[ok]
    print(f"episodes(days)={len(starts)}  median prior-day range={np.median(pdr):.1f} ({np.median(pdr)/PIP:.0f}p)")
    # POSITIVE CONTROL: inject strong drift so first-side continuation MUST pay
    print("\n== POSITIVE CONTROL (inject +2*ATR/day drift; continuation OCO must be strongly +) ==")
    Mc={k:(v.copy() if isinstance(v,np.ndarray) else v) for k,v in M.items()}
    drift=np.cumsum(np.where(M["hr"]==0, np.median(pdr)*1.0, 0.0))  # +~1 PDR per day upward
    for kk in ("o","h","l","c"): Mc[kk]=M[kk]+drift
    ua=Mc["o"][starts]+0.25*pdr; da=Mc["o"][starts]-0.25*pdr
    pc=run_anchor(Mc,starts,ua,da,"cont","  POSCTRL drift cont f=.25")
    print(f"  POSITIVE_CONTROL = {'PASS' if (pc is not None and pc>0.10) else 'FAIL'}")
    print("\n== ANCHOR A: daily-open +/- f*PDR, CONTINUATION ==")
    for f in (0.25,0.5):
        run_anchor(M,starts,anchor+f*pdr,anchor-f*pdr,"cont",f"  A.daily cont f={f}")
    print("== ANCHOR A: daily-open, FAILED-REVERSAL ==")
    for f in (0.25,0.5):
        run_anchor(M,starts,anchor+f*pdr,anchor-f*pdr,"rev",f"  A.daily failed-rev f={f}")
    print("== ANCHOR B: prior-day HIGH/LOW activation, CONTINUATION ==")
    run_anchor(M,starts,pdh,pdl,"cont","  B.priorday cont")
    run_anchor(M,starts,pdh,pdl,"rev","  B.priorday failed-rev")
    print("\n== BENCHMARK: random-direction at daily anchor (f=.5), 1:1 risk ==")
    rng=np.random.RandomState(7); rows=[]
    for s,a,p in zip(starts,anchor,pdr):
        d=1 if rng.random()<0.5 else -1; risk=1.0*p; entry=a; stop=a-d*risk; tgt=a+d*risk
        end=min(s+H,M["n"]-1); res=None
        for k in range(s+1,end+1):
            ht=(M["h"][k]>=tgt) if d>0 else (M["l"][k]<=tgt); hs=(M["l"][k]<=stop) if d>0 else (M["h"][k]>=stop)
            if ht and hs: res=-1.0;break
            if hs: res=-1.0;break
            if ht: res=1.0;break
        if res is None: res=d*(M["c"][end]-entry)/risk
        rows.append({"net":res-COST/risk,"_s":s})
    agg(M,rows,"  random-dir 1:1")

if __name__=="__main__":
    main()
