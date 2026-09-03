"""gc_ctx_v1_controls.py — GC V1 negative controls on representation C (A+GC real volume) @60% retention, per setup: volume-destruction
(permute GC volume features within time-of-day buckets, x100), time-of-day-only (GC volume replaced by expected-TOD volume), matched-random
(x100), label-permutation (x100), and a time-shift. Since the primary real-volume-specific gate already fails, these formally confirm the tiny
GC-volume effect is within the null. Writes GC_REAL_VOLUME_NEGATIVE_CONTROLS.csv.
"""
import os, numpy as np, pandas as pd, json
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
J=pd.read_parquet(OUT+r"\GC_CTX_JOINED.parquet"); proto=json.load(open(OUT+r"\GC_REAL_VOLUME_PROTOCOL.json"))
A=[c for c in J.columns if c.startswith("gA_") or c.startswith("gB_")]; Vv=[c for c in proto["volume_features"] if c in J.columns]
RET60=0.6; PURGE=96
for c in set(A+Vv):
    if c in J: x=J[c].to_numpy(float).copy(); x[~np.isfinite(x)]=np.nan; lo,hi=np.nanpercentile(x,[1,99]); J[c]=np.clip(x,lo,hi)
dtb=pd.to_datetime(J.decision_time,unit="s",utc=True); J["tod"]=(dtb.dt.hour*4+dtb.dt.minute//15).to_numpy()
def stdz(tr,te):
    mu=np.nanmedian(tr,0); mu=np.where(np.isnan(mu),0,mu); tr=np.where(np.isnan(tr),mu,tr); te=np.where(np.isnan(te),mu,te)
    sd=tr.std(0); sd=np.where(np.isfinite(sd)&(sd>0),sd,1); return np.nan_to_num((tr-mu)/sd),np.nan_to_num((te-mu)/sd)
def logit(X,y,l2=1.,it=200,lr=.3):
    Xb=np.hstack([np.ones((len(X),1)),X]); w=np.zeros(Xb.shape[1])
    for _ in range(it): p=1/(1+np.exp(-np.clip(Xb@w,-30,30))); grd=Xb.T@(p-y)/len(y); grd[1:]+=l2*w[1:]/len(y); w-=lr*grd
    return w
def lp(w,X): return 1/(1+np.exp(-np.clip(np.hstack([np.ones((len(X),1)),X])@w,-30,30)))
def wf(g,feats,Ry=None,volperm=None,seed=0):
    g=g.reset_index(drop=True); N=len(g); R=g["R"].to_numpy(); Ry=R if Ry is None else Ry; si=g["si"].to_numpy()
    days=g["decision_time"].to_numpy()//86400; ud=np.unique(days); cuts=[ud[int(len(ud)*k/4)] for k in range(1,4)]; blk=np.digitize(days,cuts)
    X=g[feats].to_numpy(float).copy()
    if volperm is not None:  # permute volume cols within TOD buckets
        rng=np.random.RandomState(seed); vidx=[feats.index(c) for c in volperm]; tod=g["tod"].to_numpy()
        for b in np.unique(tod):
            idx=np.where(tod==b)[0]
            if len(idx)>1:
                for vi in vidx: X[idx,vi]=X[rng.permutation(idx),vi]
    sel=np.zeros(N,bool); tested=np.zeros(N,bool)
    for trb,teb in [([0],1),([0,1],2),([0,1,2],3)]:
        tr=np.where(np.isin(blk,trb))[0]; te=np.where(blk==teb)[0]; te=te[si[te]>si[tr].max()+PURGE]
        if len(tr)<400 or len(te)<80: continue
        Xtr,Xte=stdz(X[tr],X[te]); w=logit(Xtr,(Ry[tr]>0).astype(float)); str_=lp(w,Xtr); ste=lp(w,Xte)
        thr=np.quantile(str_[Ry[tr]>0],1-RET60); sel[te]=ste>=thr; tested[te]=True
    s=sel&tested; return (R[s].mean() if s.sum() else np.nan), int(s.sum()), tested
rows=[]
for sid,g in J.groupby("setup"):
    g=g.sort_values("decision_time"); featsC=A+Vv
    realC,k,tst=wf(g,featsC)
    vd=[wf(g,featsC,volperm=Vv,seed=s)[0] for s in range(100)]; vdm=float(np.nanmean(vd))
    # TOD-only: replace GC volume with expected-TOD volume proxy = g1_vol_rel_tod set to 1 (expected) -> A only (no real dev)
    todA,_,_=wf(g,A)  # A alone == GC volume replaced by its expectation (no real participation deviation)
    Rall=g["R"].to_numpy()
    perm=[]
    for s in range(100): rp=Rall.copy(); np.random.RandomState(400+s).shuffle(rp); perm.append(wf(g,featsC,Ry=rp)[0])
    perm=np.array(perm)
    rnd=[Rall[tst][np.random.RandomState(9+i).choice(int(tst.sum()),k,replace=False)].mean() for i in range(100)]
    # time-shift: shift GC volume features by +20 bars (wrong-time) -> approximate by rolling the vol columns
    gsh=g.copy();
    for c in Vv: gsh[c]=np.roll(gsh[c].to_numpy(),20)
    tsh,_,_=wf(gsh,featsC)
    rows.append(dict(setup=sid,real_C=round(realC,4),vol_destroy_mean=round(vdm,4),tod_only_A=round(todA,4),
        label_perm_mean=round(float(np.nanmean(perm)),4),matched_random_mean=round(float(np.mean(rnd)),4),time_shift=round(float(tsh),4),
        beats_vol_destroy=bool(realC>vdm+0.02),beats_tod=bool(realC>todA+0.02),beats_perm=bool(realC>np.nanpercentile(perm,95)),beats_random=bool(realC>np.percentile(rnd,95))))
    print(f"{sid}: realC={realC:+.4f} volDestroy={vdm:+.4f} TODonly(A)={todA:+.4f} labelPerm={np.nanmean(perm):+.4f} random={np.mean(rnd):+.4f} timeShift={tsh:+.4f}")
NC=pd.DataFrame(rows); NC.to_csv(OUT+r"\GC_REAL_VOLUME_NEGATIVE_CONTROLS.csv",index=False)
gate_pass=bool((NC.beats_vol_destroy & NC.beats_tod & NC.beats_random).any())
print(f"\nGC_VOLUME_BEYOND_TOD_VALUE = {'YES' if NC.beats_tod.any() else 'NO'}")
print(f"NEGATIVE_CONTROL_GATE = {'PASS' if gate_pass else 'FAIL'} (no setup's real GC-volume beats vol-destroy+TOD+random)")
