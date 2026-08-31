"""ob_contrast.py — ORDER_BLOCK_RETEST_FACTORY_V1 §21/§26 matched-control information test.

Tradeable model = resting LIMIT at the block edge (fills causally on first touch; resolve from that bar). For each causal OB event we
compare the OB entry against matched controls that share the SAME displacement+BOS precondition but do NOT use the OB level:
  CONTROL_C  (displacement+BOS-only generic pullback): limit at bos_close -/+ 1*ATR, stop 1*ATR beyond -> is a generic pullback as good?
  CONTROL_SHIFT (non-OB level at matched distance): the frozen block shifted AWAY by 1x its own height (same retest distance, not the OB).
  CONTROL_BETA (trend/beta): random same-direction entries, same era, matched horizon+stop -> is a bull-OB just being long in a bull?
Central output: OB_INCREMENTAL_INFORMATION_FOUND = does OB net-R beat CONTROL_C / CONTROL_SHIFT cross-era? cur_data M15.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import ob_core as OB, htf_core as HC

def limit_fill(P, e, level, side, i, win=OB.RETEST_WIN):
    """First bar k>i where price touches `level` (from the displacement side). Return k or None (before close-invalidation of block)."""
    h=P["h"];l=P["l"];c=P["c"];n=P["n"]; end=min(i+win,n-1)
    for k in range(i+1,end+1):
        if side>0:
            if c[k]<e["blo"]: return None
            if l[k]<=level: return k
        else:
            if c[k]>e["bhi"]: return None
            if h[k]>=level: return k
    return None

def outcome_from(P, entry, stop, side, k):
    o=OB.retest_outcome(P, entry, stop, side, k, 2.0, resolve_from=k)
    return None if o is None else o["net_R"]

def run(P, direction, disp_min=0.75):
    atr=P["atr"]; ev=OB.detect_obs(P,disp_min,direction)
    import cur_data as CD  # for era via years already in P? use htf panel years
    yrs=None
    OBr=[]; C_C=[]; C_S=[]; kbars_ob=[]; kbars=[]
    import pandas as pd
    m=HC.build()[0]; yr=m["dt"].dt.year.values
    obrows=[]; ccrows=[]; csrows=[]
    for e in ev:
        d=e["dir"]; i=e["i"]; a=atr[i]
        # OB entry: limit at block edge
        lvl_ob=e["bhi"] if d>0 else e["blo"]
        stop_ob=(e["blo"]-OB.FLOOR_ATR*a) if d>0 else (e["bhi"]+OB.FLOOR_ATR*a)
        if abs(lvl_ob-stop_ob)<0.5*a: stop_ob=lvl_ob-d*0.5*a
        k=limit_fill(P,e,lvl_ob,d,i)
        if k is not None:
            r=outcome_from(P,lvl_ob,stop_ob,d,k)
            if r is not None: obrows.append((r,yr[k]))
        # CONTROL_C generic pullback: limit at bos_close -/+ 1 ATR
        lvl_c=e["bos_close"]-d*1.0*a; stop_c=lvl_c-d*1.0*a
        kc=limit_fill(P,e,lvl_c,d,i)
        if kc is not None:
            r=outcome_from(P,lvl_c,stop_c,d,kc)
            if r is not None: ccrows.append((r,yr[kc]))
        # CONTROL_SHIFT: block shifted away by its own height (non-OB level, matched distance)
        bh=e["bhi"]-e["blo"]
        lvl_s=(e["bhi"]+bh) if d>0 else (e["blo"]-bh)   # shifted farther from price into the impulse
        stop_s=(e["blo"]+bh-OB.FLOOR_ATR*a) if d>0 else (e["bhi"]-bh+OB.FLOOR_ATR*a)
        if abs(lvl_s-stop_s)<0.5*a: stop_s=lvl_s-d*0.5*a
        ks=limit_fill(P,e,lvl_s,d,i)
        if ks is not None:
            r=outcome_from(P,lvl_s,stop_s,d,ks)
            if r is not None: csrows.append((r,yr[ks]))
    return obrows, ccrows, csrows

def summ(rows,label):
    if len(rows)<50: print(f"{label:26s} N={len(rows)} small"); return
    r=np.array([x[0] for x in rows]); y=np.array([x[1] for x in rows])
    era=np.where(y<=2018,"D",np.where(y<=2022,"C","O"))
    def me(x): return r[era==x].mean() if (era==x).sum()>0 else np.nan
    print(f"{label:26s} N={len(r):5d} net={r.mean():+.3f} WR={(r>0).mean():.3f} D={me('D'):+.3f} C={me('C'):+.3f} O={me('O'):+.3f}")

def beta(P, direction, n_yr):
    """Random same-direction longs/shorts matched by era, ~1ATR stop, 2R, horizon RETEST_WIN."""
    m=HC.build()[0]; yr=m["dt"].dt.year.values; nm=P["n"]; atr=P["atr"]; c=P["c"]
    rng=np.random.RandomState(1); d=1 if direction=="bull" else -1
    out=[]
    for e,(y0,y1) in [("D",(2011,2018)),("C",(2019,2022)),("O",(2023,2026))]:
        pool=np.where((yr>=y0)&(yr<=y1)&(np.arange(nm)>300)&(np.arange(nm)<nm-OB.RETEST_WIN))[0]
        if len(pool)<200: continue
        s=rng.choice(pool,3000,True)
        for t in s:
            a=atr[t]; stop=c[t]-d*1.0*a
            o=OB.retest_outcome(P,c[t],stop,d,t,2.0,resolve_from=t)
            if o: out.append((o["net_R"],yr[t]))
    return out

def main():
    m,H1,H4,P=OB.build()
    for dd in ("bull","bear"):
        ob,cc,cs=run(P,dd,0.75); bt=beta(P,dd,None)
        print(f"\n=== {dd.upper()} — matched-control information test (limit entry, 2R) ===")
        summ(ob,f"{dd}.OB_RETEST"); summ(cc,f"{dd}.CONTROL_C(genericPB)"); summ(cs,f"{dd}.CONTROL_SHIFT"); summ(bt,f"{dd}.CONTROL_BETA")

if __name__=="__main__":
    main()
