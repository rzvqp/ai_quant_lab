"""ALPHA-XAUUSD-EARLY-SESSION-LIQUIDITY-TRAP-001. EARLY classification: at the sweep (E0) / first bars
(E1/E2/E3), can causal price ANATOMY distinguish TRAP (return toward Asia mid) from VALID BULLISH BREAKOUT,
while economic room still remains? Frozen 329-sweep Asia parent from session_trap (commit 722a0e0), UNCHANGED.
Outcome measured AFTER the landmark. Landmark economics MANDATORY. Univariate-first, DISC/CONF, matched-parent,
session-separate. NO execution/stop/target search. Price-only, DEV-only."""
import sys, os, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import session_trap as S
recs=S.recs; split=S.split; PIP=S.PIP
h=S.h; l=S.l; c=S.c; o=S.o; atr=S.atr; n=S.n; uday=S.uday; uh=S.uh; dt=S.dt
yr=dt.year.to_numpy()
print(f"FROZEN parent lineage: {len(recs)} Asia-High sweeps (from session_trap / 722a0e0), UNCHANGED.")

# ---- prior same-day attacks on Asia High before the frozen sweep bar (first-vs-repeat, S9) ----
def prior_attacks(r):
    sw=r["sw"]; d=r["d"]
    idx=np.where((uday==d)&(np.arange(n)<sw))[0]
    return int(np.sum(h[idx]>=r["hi"]))

# ---- early causal features at landmark (known by bar sw+k close) ----
def rng(i): return max(h[i]-l[i],1e-9)
def e_features(r):
    sw=r["sw"]; a=atr[sw] if np.isfinite(atr[sw]) else 1.0; hi=r["hi"]
    f={}
    # E0 sweep-candle anatomy
    f["e0_upperwick"]=(h[sw]-max(o[sw],c[sw]))/rng(sw)
    f["e0_body"]=abs(c[sw]-o[sw])/rng(sw)
    f["e0_closeloc"]=(c[sw]-l[sw])/rng(sw)                     # low = bearish rejection
    f["e0_close_above"]=(c[sw]-hi)/a                            # <0 = closed back below Asia High (rejection)
    f["e0_excursion"]=(h[sw]-hi)/a
    f["e0_attack_accel"]=(c[sw]-c[sw-3])/a if sw>=3 else 0.0    # speed into sweep
    # E1 path (bar sw+1)
    if sw+1<n:
        f["e1_extend"]=(h[sw+1]-h[sw])/a                        # <=0 = failed to extend (trap-like)
        f["e1_close_above"]=(c[sw+1]-hi)/a
        f["e1_contraction"]=rng(sw+1)/rng(sw)                   # <1 = rapid contraction
        f["e1_bear"]=(o[sw+1]-c[sw+1])/a                        # bearish body at E1
    else: f["e1_extend"]=f["e1_close_above"]=f["e1_contraction"]=f["e1_bear"]=np.nan
    # E2 path (bar sw+2)
    if sw+2<n:
        f["e2_lower_high"]=float(h[sw+2]<h[sw+1])
        f["e2_below_hi"]=(c[sw+2]-hi)/a
    else: f["e2_lower_high"]=f["e2_below_hi"]=np.nan
    f["n_prior_attacks"]=prior_attacks(r)
    return f

# ---- outcome measured AFTER landmark E_k (reach Asia mid; path survivability) ----
def landmark(r,k):
    sw=r["sw"]; ei=sw+k
    if ei+1>=n or not np.isfinite(atr[ei]): return None
    ref=c[ei]; remaining=(ref-r["mid"])/PIP
    path_tot=(r["hi"]-r["mid"]); consumed=(r["hi"]-ref)/path_tot if path_tot!=0 else np.nan
    sweep_hi=max(h[sw:ei+1]); reach=False; newhi=False; mae=0.0; mfe=0.0; adverse_before=0.0
    for j in range(ei+1,min(ei+1+24,n)):
        if uday[j]!=r["d"]: break
        up=(h[j]-ref)/PIP; mae=max(mae,up)
        if h[j]>sweep_hi: newhi=True
        if not reach: adverse_before=max(adverse_before,up)
        dn=(ref-l[j])/PIP; mfe=max(mfe,dn)
        if l[j]<=r["mid"]: reach=True; break
    return dict(ref=ref,remaining=remaining,consumed=consumed,reach=reach,newhi=newhi,mae=mae,mfe=mfe,adv=adverse_before)

# ---- landmark economics (S13) ----
print("\n=== LANDMARK ECONOMICS (all DEV parents): median %consumed | median pips remaining | P(reach mid) | P(new high>sweep) ===")
for k in range(4):
    outs=[landmark(r,k) for r in recs]; outs=[x for x in outs if x]
    cons=np.median([x["consumed"] for x in outs])*100; rem=np.median([x["remaining"] for x in outs])
    pm=np.mean([x["reach"] for x in outs]); pn=np.mean([x["newhi"] for x in outs])
    print(f"  E{k}: n={len(outs)} consumed={cons:5.1f}%  remaining={rem:5.1f}p  P(mid)={pm:.3f}  P(newhigh)={pn:.3f}")

# ---- univariate early-feature discrimination at E1 landmark (outcome from sw+2 fwd) ----
def auc(y,x):
    y=np.array(y); x=np.array(x); m=np.isfinite(x); y=y[m]; x=x[m]
    n1=y.sum(); n0=len(y)-n1
    if n1==0 or n0==0: return np.nan
    r=np.argsort(np.argsort(x))+1; return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
FEATS=["e0_upperwick","e0_body","e0_closeloc","e0_close_above","e0_excursion","e0_attack_accel",
       "e1_extend","e1_close_above","e1_contraction","e1_bear","e2_lower_high","e2_below_hi","n_prior_attacks"]
def feat_table(landmark_k):
    rows=[]
    for r in recs:
        lo=landmark(r,landmark_k)
        if not lo: continue
        f=e_features(r); rows.append((r,f,int(lo["reach"]),split(r)))
    return rows
print(f"\n=== UNIVARIATE EARLY-FEATURE DISCRIMINATION (landmark E1; outcome reach-mid AFTER E1) ===")
print(f"{'feature':16} {'DISC AUC':>9} {'CONF AUC':>9}  {'stable?':>7}")
rows=feat_table(1)
for f in FEATS:
    yd=[y for _,ff,y,s in rows if s=='D']; xd=[ff[f] for _,ff,y,s in rows if s=='D']
    yc=[y for _,ff,y,s in rows if s=='C']; xc=[ff[f] for _,ff,y,s in rows if s=='C']
    ad=auc(yd,xd); ac=auc(yc,xc)
    stable = (np.isfinite(ad) and np.isfinite(ac) and (ad-0.5)*(ac-0.5)>0 and abs(ad-0.5)>0.04 and abs(ac-0.5)>0.04)
    print(f"  {f:16} {ad:9.3f} {ac:9.3f}  {'YES' if stable else '.':>7}")

# ---- matched-parent: base P(mid) vs conditioned on the single strongest stable early feature (tercile) ----
print("\n=== SESSION SPLIT (base P(reach mid) at E1, matched parent) ===")
for sess in ("LONDON","OVERLAP"):
    for tag in ("D","C"):
        rr=[r for r in recs if r["sess"]==sess and split(r)==tag]
        outs=[landmark(r,1) for r in rr]; outs=[x for x in outs if x]
        if outs: print(f"  {sess:8} {tag}: n={len(outs)} P(mid)={np.mean([x['reach'] for x in outs]):.3f} medRemain={np.median([x['remaining'] for x in outs]):.1f}p")

print("\n=== FIRST vs REPEAT attack (P reach mid at E1) ===")
for lbl,cond in (("first (0 prior)",lambda r:prior_attacks(r)==0),("repeat (>=1 prior)",lambda r:prior_attacks(r)>=1)):
    for tag in ("D","C"):
        rr=[r for r in recs if cond(r) and split(r)==tag]; outs=[landmark(r,1) for r in rr]; outs=[x for x in outs if x]
        if outs: print(f"  {lbl:18} {tag}: n={len(outs)} P(mid)={np.mean([x['reach'] for x in outs]):.3f}")
