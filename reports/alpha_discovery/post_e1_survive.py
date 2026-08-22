"""ALPHA-XAUUSD-POST-E1-REVERSAL-SURVIVABILITY-001. NEW signal question on the FROZEN EARLY-TRAP-E1 parent
(118 episodes, unchanged): can native-M5 price behavior at P1-P4 (first 4 M5 bars after E1) distinguish
CLEAN_REVERSAL (mid before any new high above sweep_hi) from NEW_HIGH_FIRST, WHILE distance remains?
Univariate-first, condition on UNDECIDED-at-Pk (avoid lateness trap), DISC/CONF split. Price-only, DEV-only.
NO execution. NO EARLY-TRAP-E1 retuning. Future path = label only, never a feature."""
import sys, os, numpy as np, pandas as pd
DST=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
if DST not in sys.path: sys.path.insert(0,DST)
import early_trap_e1_signal as ES
PIP=0.10; HORIZON=32
tfs,_=ES.D.build(); episodes,meta=ES.evaluate(tfs)
assert meta["n_fires"]==118 and ES.implementation_fingerprint()=="33bec4498e72a05c486ec1763854edac17cc9da82556932d0f3257d62f6c2a16"
M=tfs["M15"]; mo=M["open"].to_numpy();mh=M["high"].to_numpy();ml=M["low"].to_numpy();mc=M["close"].to_numpy()
mt=M["time"].to_numpy().astype("int64"); muday=pd.to_datetime(mt,unit="s",utc=True).floor("D").astype("int64").to_numpy()
myr=pd.to_datetime(mt,unit="s",utc=True).year.to_numpy(); nM=len(mo)
M5=tfs["M5"]; f5o=M5["open"].to_numpy();f5h=M5["high"].to_numpy();f5l=M5["low"].to_numpy();f5c=M5["close"].to_numpy()
f5t=M5["time"].to_numpy().astype("int64"); f5day=pd.to_datetime(f5t,unit="s",utc=True).floor("D").astype("int64").to_numpy()

# ---- label: class A clean reversal (mid before any new high above sweep_hi), from M15 forward path ----
def classify(e):
    sw=e["sweep_index"]; e1=e["e1_index"]; ei=e1+1
    if ei>=nM: return None
    sweep_hi=mh[sw:e1+1].max(); mid=e["asia_mid"]; day=e["day"]; newhi=False
    for j in range(ei,min(ei+HORIZON,nM)):
        if muday[j]!=day: break
        if mh[j]>sweep_hi: newhi=True
        if ml[j]<=mid: return ("A_clean" if not newhi else "B_newhi_then_mid")
    return "C_newhi_never" if newhi else "D_none"

# ---- P1-P4 native M5 landmarks (first M5 with time >= e1 M15 end = e1_time+900, then +300 each, contiguous same-day) ----
def landmarks(e):
    e1=e["e1_index"]; end=mt[e1]+900
    p1=np.searchsorted(f5t,end,side="left")
    if p1>=len(f5t): return None
    idx=[p1,p1+1,p1+2,p1+3]
    if idx[-1]>=len(f5t): return None
    day=e["day"]
    for k,ix in enumerate(idx):
        if f5day[ix]!=day: return idx[:k] if k>=1 else None       # truncate at day boundary
    # contiguity (allow small gaps)
    return idx

# ---- features at landmark Pk (M5 bars idx[0..k-1]); resolved status; timeliness ----
def feats_at(e, idx, k):
    sw=e["sweep_index"]; e1=e["e1_index"]; sweep_hi=mh[sw:e1+1].max(); e1_hi=mh[e1]
    ah=e["asia_high"]; mid=e["asia_mid"]; e1c=mc[e1]
    seg=idx[:k]; hi=max(f5h[j] for j in seg); lo=min(f5l[j] for j in seg); cl=f5c[seg[-1]]
    up=(hi-e1c)/PIP; dn=(e1c-lo)/PIP; net=(e1c-cl)/PIP
    resolved = "newhi" if hi>sweep_hi else ("mid" if lo<=mid else "undecided")
    path_tot=(ah-mid); consumed=(ah-cl)/path_tot if path_tot else np.nan; remaining=(cl-mid)/PIP
    lc=sum(1 for j in seg[1:] if f5c[j]<f5c[j-1]); lh=sum(1 for j in seg[1:] if f5h[j]<f5h[j-1])
    last=seg[-1]; rng=max(f5h[last]-f5l[last],1e-9)
    F=dict(
        upside_retrace=up, downside_prog=dn, net_prog=net,
        dist_to_sweep=(sweep_hi-hi)/PIP, dist_to_e1hi=(e1_hi-hi)/PIP,
        ratio_dn_up=dn/(up+1.0), failed_extend=float(hi<sweep_hi and hi<e1_hi),
        consec_lower_close=lc, consec_lower_high=lh,
        last_bear_body=(f5o[last]-f5c[last])/PIP, last_close_loc=(f5c[last]-f5l[last])/rng,
        last_upper_wick=(f5h[last]-max(f5o[last],f5c[last]))/rng,
    )
    return F, resolved, consumed, remaining

# ---- assemble ----
recs=[]
for e in episodes:
    lab=classify(e); idx=landmarks(e)
    if lab is None or idx is None: continue
    recs.append(dict(e=e, label=int(lab=="A_clean"), cls=lab, idx=idx, day=e["day"],
                     sess=e["session"], yr=int(myr[e["e1_index"]]), st=e["signal_time"]))
recs.sort(key=lambda r:r["st"]); cut=recs[int(len(recs)*0.6)]["st"]
for r in recs: r["split"]="DISC" if r["st"]<cut else "CONF"
from collections import Counter
print(f"parent episodes={len(episodes)} | with P1-P4 M5 landmarks={len(recs)}")
print(f"class balance: {dict(Counter(r['cls'] for r in recs))}")
print(f"CLEAN_REVERSAL (A) rate={np.mean([r['label'] for r in recs]):.3f} | DISC n={sum(r['split']=='DISC' for r in recs)} CONF n={sum(r['split']=='CONF' for r in recs)}")

def auc(y,x):
    y=np.array(y);x=np.array(x);m=np.isfinite(x);y=y[m];x=x[m];n1=y.sum();n0=len(y)-n1
    if n1==0 or n0==0: return np.nan
    r=np.argsort(np.argsort(x))+1; return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)

FEATS=["upside_retrace","downside_prog","net_prog","dist_to_sweep","dist_to_e1hi","ratio_dn_up",
       "failed_extend","consec_lower_close","consec_lower_high","last_bear_body","last_close_loc","last_upper_wick"]
print("\n=== TIMELINESS + UNDECIDED N per landmark (economic room, S8/S10) ===")
for k in (1,2,3,4):
    und=[]; cons=[]; rem=[]
    for r in recs:
        if len(r["idx"])<k: continue
        F,res,cn,rm=feats_at(r["e"],r["idx"],k); r[f"res{k}"]=res
        if res=="undecided": und.append(r); cons.append(cn); rem.append(rm)
    print(f"  P{k} ({k*5}min after E1): undecided n={len(und)} | median %consumed={np.nanmedian(cons)*100:.1f}% median remaining={np.nanmedian(rem):.1f}p")

print("\n=== UNIVARIATE AUC (predict CLEAN_REVERSAL among UNDECIDED-at-Pk) DISC | CONF, per landmark ===")
print(f"{'feature':18} " + " ".join(f"P{k}D/P{k}C" for k in (1,2,3)))
for f in FEATS:
    cells=[]
    for k in (1,2,3):
        und=[r for r in recs if len(r["idx"])>=k and r.get(f"res{k}")=="undecided"]
        yd=[r["label"] for r in und if r["split"]=="DISC"]; xd=[feats_at(r["e"],r["idx"],k)[0][f] for r in und if r["split"]=="DISC"]
        yc=[r["label"] for r in und if r["split"]=="CONF"]; xc=[feats_at(r["e"],r["idx"],k)[0][f] for r in und if r["split"]=="CONF"]
        cells.append(f"{auc(yd,xd):.2f}/{auc(yc,xc):.2f}")
    print(f"  {f:18} " + "  ".join(cells))
