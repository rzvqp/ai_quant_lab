"""gc_cot_v1_controls.py — CFTC COT negative controls on the strongest COT representation (G_vol_oi_cot) @60% per setup: COT-destruction
(permute COT features across trades within year buckets, x100), time-shift (roll COT features by 20 trades), label-permutation (x100),
matched-random (x100). Confirms the tiny COT effect is within the null.
"""
import os, json, numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
J=pd.read_parquet(OUT+r"\GC_COT_JOINED.parquet"); proto=json.load(open(OUT+r"\CFTC_COT_PROTOCOL.json"))
A=[c for c in J.columns if c.startswith("gA_") or c.startswith("gB_")]; Vv=[c for c in proto["volume_features"] if c in J]; OIf=[c for c in proto["oi_features"] if c in J]; COTf=[c for c in proto["cot_features"] if c in J]
G=A+Vv+OIf+COTf; PURGE=96; RET=0.6
for c in set(G):
    x=J[c].to_numpy(float).copy(); x[~np.isfinite(x)]=np.nan; lo,hi=np.nanpercentile(x,[1,99]); J[c]=np.clip(x,lo,hi)
J["yr"]=pd.to_datetime(J.decision_time,unit="s",utc=True).dt.year.to_numpy()
def stdz(tr,te):
    mu=np.nanmedian(tr,0); mu=np.where(np.isnan(mu),0,mu); tr=np.where(np.isnan(tr),mu,tr); te=np.where(np.isnan(te),mu,te)
    sd=tr.std(0); sd=np.where(np.isfinite(sd)&(sd>0),sd,1); return np.nan_to_num((tr-mu)/sd),np.nan_to_num((te-mu)/sd)
def logit(X,y,l2=1.,it=200,lr=.3):
    Xb=np.hstack([np.ones((len(X),1)),X]); w=np.zeros(Xb.shape[1])
    for _ in range(it): p=1/(1+np.exp(-np.clip(Xb@w,-30,30))); grd=Xb.T@(p-y)/len(y); grd[1:]+=l2*w[1:]/len(y); w-=lr*grd
    return w
def lp(w,X): return 1/(1+np.exp(-np.clip(np.hstack([np.ones((len(X),1)),X])@w,-30,30)))
def wf(g,Ry=None,cotperm=None,seed=0):
    g=g.reset_index(drop=True); N=len(g); R=g["R"].to_numpy(); Ry=R if Ry is None else Ry; si=g["si"].to_numpy()
    days=g["decision_time"].to_numpy()//86400; ud=np.unique(days); cuts=[ud[int(len(ud)*k/4)] for k in range(1,4)]; blk=np.digitize(days,cuts)
    X=g[G].to_numpy(float).copy()
    if cotperm is not None:
        rng=np.random.RandomState(seed); cidx=[G.index(c) for c in COTf]; yr=g["yr"].to_numpy()
        for b in np.unique(yr):
            idx=np.where(yr==b)[0]
            if len(idx)>1:
                for vi in cidx: X[idx,vi]=X[rng.permutation(idx),vi]
    sel=np.zeros(N,bool); tested=np.zeros(N,bool)
    for trb,teb in [([0],1),([0,1],2),([0,1,2],3)]:
        tr=np.where(np.isin(blk,trb))[0]; te=np.where(blk==teb)[0]; te=te[si[te]>si[tr].max()+PURGE]
        if len(tr)<400 or len(te)<80: continue
        Xtr,Xte=stdz(X[tr],X[te]); w=logit(Xtr,(Ry[tr]>0).astype(float)); str_=lp(w,Xtr); ste=lp(w,Xte)
        thr=np.quantile(str_[Ry[tr]>0],1-RET); sel[te]=ste>=thr; tested[te]=True
    s=sel&tested; return (R[s].mean() if s.sum() else np.nan),int(s.sum()),tested
rows=[]
for sid,g in J.groupby("setup"):
    g=g.sort_values("decision_time"); real,k,tst=wf(g)
    cd=[wf(g,cotperm=COTf,seed=s)[0] for s in range(100)]; cdm=float(np.nanmean(cd))
    gsh=g.copy()
    for c in COTf: gsh[c]=np.roll(gsh[c].to_numpy(),20)
    tsh,_,_=wf(gsh)
    Rall=g["R"].to_numpy(); perm=[]
    for s in range(100): rp=Rall.copy(); np.random.RandomState(600+s).shuffle(rp); perm.append(wf(g,Ry=rp)[0])
    perm=np.array(perm); rnd=[Rall[tst][np.random.RandomState(9+i).choice(int(tst.sum()),k,replace=False)].mean() for i in range(100)]
    rows.append(dict(setup=sid,real_G=round(real,4),cot_destroy_mean=round(cdm,4),time_shift=round(float(tsh),4),
        label_perm_mean=round(float(np.nanmean(perm)),4),matched_random_mean=round(float(np.mean(rnd)),4),
        beats_cot_destroy=bool(real>cdm+0.02),beats_perm=bool(real>np.nanpercentile(perm,95)),beats_random=bool(real>np.percentile(rnd,95))))
    print(f"{sid}: real_G={real:+.4f} COT_destroy={cdm:+.4f} time_shift={tsh:+.4f} label_perm={np.nanmean(perm):+.4f} random={np.mean(rnd):+.4f} beats_COT_destroy={real>cdm+0.02}")
NC=pd.DataFrame(rows); NC.to_csv(OUT+r"\CFTC_COT_NEGATIVE_CONTROLS.csv",index=False)
print(f"\nNEGATIVE_CONTROL_GATE = {'PASS' if bool(NC.beats_cot_destroy.any()) else 'FAIL'} (no setup's real COT beats COT-destruction by >=0.02R)")
