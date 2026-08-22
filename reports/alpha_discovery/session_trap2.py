"""Phase 2: EXECUTION expectancy (R) per layer x target(mid/low) x disc/conf, with STRESS cost, tail metrics,
temporal (2021/22/23), session split; matched control (valid breakout vs trap); mean-reversion vs trend;
range-width / sweep-size / time-of-day effects; PDH comparison. Decides candidate vs signal-only vs negative."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import session_trap as S
recs=S.recs; outcome=S.outcome; layer_entry=S.layer_entry; split=S.split; PIP=S.PIP
uh=S.uh; uday=S.uday; h=S.h; l=S.l; c=S.c; o=S.o; atr=S.atr; n=S.n; dt=S.dt
COST=2.4
yr=dt.year.to_numpy()

def Rstats(Rs):
    Rs=np.array(Rs)
    if len(Rs)==0: return None
    s=np.sort(Rs)[::-1]; brem=lambda p:(s[int(len(s)*p):].mean() if int(len(s)*p)<len(s) else np.nan)
    top10=s[:max(1,int(len(s)*.1))].sum(); tot=Rs.sum()
    return dict(n=len(Rs),wr=round(float((Rs>0).mean()),3),avg=round(float(Rs.mean()),3),med=round(float(np.median(Rs)),3),
                b5=round(float(brem(.05)),3),b10=round(float(brem(.10)),3),
                top10=round(float(top10/tot),3) if tot>0 else None)

def layer_R(layer, target, split_tag=None, sess=None):
    Rs=[]; yrs=[]
    for r in recs:
        if split_tag and split(r)!=split_tag: continue
        if sess and r["sess"]!=sess: continue
        ei=r["sw"] if layer=="S0" else layer_entry(r,layer)
        ov=outcome(r,ei)
        if ov is None: continue
        R=(ov["R_mid"] if target=="mid" else ov["R_low"]) - COST/ov["risk"]
        Rs.append(R); yrs.append(int(yr[ei if ei else r["sw"]]))
    st=Rstats(Rs)
    if st: st["yy"]={y:round(float(np.array(Rs)[np.array(yrs)==y].mean()),3) for y in sorted(set(yrs))}
    return st

print("=== EXECUTION EXPECTANCY R (stop=sweep_hi+buf; STRESS cost) — MEAN-REVERSION (Asia MID) target ===")
print(f"{'layer':5} | DISC n/avg/med/b5/b10/top10 | CONF n/avg/med/b5/b10/top10 | CONF yy")
for layer in ("S1","S2","S4","S5"):
    d=layer_R(layer,"mid","D"); cf=layer_R(layer,"mid","C")
    if d and cf: print(f"{layer:5} | D n{d['n']} {d['avg']:+.3f}/{d['med']:+.3f}/{d['b5']:+.3f}/{d['b10']:+.3f}/{d['top10']} | C n{cf['n']} {cf['avg']:+.3f}/{cf['med']:+.3f}/{cf['b5']:+.3f}/{cf['b10']:+.3f}/{cf['top10']} | {cf['yy']}")
print("\n=== EXECUTION EXPECTANCY R — TREND (Asia LOW) target ===")
for layer in ("S1","S2","S4","S5"):
    d=layer_R(layer,"low","D"); cf=layer_R(layer,"low","C")
    if d and cf: print(f"{layer:5} | D n{d['n']} {d['avg']:+.3f}/{d['med']:+.3f}/{d['b5']:+.3f}/{d['b10']:+.3f}/{d['top10']} | C n{cf['n']} {cf['avg']:+.3f}/{cf['med']:+.3f}/{cf['b5']:+.3f}/{cf['b10']:+.3f}/{cf['top10']} | {cf['yy']}")

print("\n=== SESSION SPLIT (S2, MID target) ===")
for sess in ("LONDON","OVERLAP"):
    d=layer_R("S2","mid","D",sess); cf=layer_R("S2","mid","C",sess)
    if d and cf: print(f"  {sess:8}: DISC n{d['n']} avg{d['avg']:+.3f} b10{d['b10']:+.3f} | CONF n{cf['n']} avg{cf['avg']:+.3f} b10{cf['b10']:+.3f} med{cf['med']:+.3f} yy{cf['yy']}")

# ---- matched control: TRAP (S1 return inside) vs VALID BREAKOUT (accepted above, never returned within 8) ----
print("\n=== MATCHED CONTROL: trap (returned inside) vs valid breakout (accepted above) — P(reach mid) ====")
trap=[r for r in recs if r["ret"] is not None]; brk=[r for r in recs if r["ret"] is None]
def pmid(rr):
    ps=[outcome(r,r["sw"]) for r in rr]; ps=[p for p in ps if p]
    return (len(ps), round(np.mean([p["hit_mid"] for p in ps]),3) if ps else np.nan, round(np.mean([p["hit_low"] for p in ps]),3) if ps else np.nan)
print(f"  TRAP (returned inside): n{pmid(trap)[0]} P(mid)={pmid(trap)[1]} P(low)={pmid(trap)[2]}")
print(f"  VALID BREAKOUT (accepted): n{pmid(brk)[0]} P(mid)={pmid(brk)[1]} P(low)={pmid(brk)[2]}  <- separation = the trap signal")

# ---- range-width / sweep-size / time-of-day (broad buckets, S2 mid, all DEV) ----
def bucket_R(keyfn, edges, label):
    print(f"\n=== {label} (S2, MID target, all DEV) ===")
    for lo,hi in zip(edges[:-1],edges[1:]):
        Rs=[]
        for r in recs:
            k=keyfn(r);
            if not (lo<=k<hi): continue
            ov=outcome(r,layer_entry(r,"S2"))
            if ov: Rs.append(ov["R_mid"]-COST/ov["risk"])
        st=Rstats(Rs)
        if st and st["n"]>=8: print(f"  [{lo},{hi}): n{st['n']} avg{st['avg']:+.3f} wr{st['wr']} b10{st['b10']:+.3f}")
bucket_R(lambda r:r["wpip"],[0,50,80,120,1000],"ASIA RANGE WIDTH (pips)")
bucket_R(lambda r:r["dist"],[0,10,25,60,1000],"SWEEP MAGNITUDE above Asia High (pips)")
bucket_R(lambda r:r["t_lon"],[7,9,11,13,17],"TIME OF DAY (London local hour of sweep)")

# ---- PDH comparison: prior-day high sweep vs Asia-high sweep (P reach that day's Asia mid) ----
days=np.unique(uday); dayhi={}
for d in days:
    m=(uday==d)&np.isfinite(atr);
    if m.sum()>0: dayhi[d]=h[m].max()
print("\n=== PDH vs ASIA-HIGH sweep (diagnostic) ===")
print(f"  Asia-High parent sweeps={len(recs)} (session-specific). PDH generic-daily already covered by prior sweep campaigns (H4-bo-raw-S is the only frozen short).")
print(f"  Session-specific Asia-High sweep S2 CONF avg (mid) = {layer_R('S2','mid','C')['avg']:+.3f} vs generic swing-sweep (prior campaign) which failed execution -> session conditioning is the novel variable.")
