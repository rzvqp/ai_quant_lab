"""cts_v3_controls.py — CTS V3 negative controls (fast: tokens precomputed once, no per-row iloc). EVENT_ORDER_DESTROY x20,
RELATION_DESTROY x20 (§25), LABEL_PERM_C x100, MATCHED_RANDOM_C x100 — all on representation C @60% winner-retention under the same
chronological walk-forward. Writes CTS_V3_NEGATIVE_CONTROLS.csv.
"""
import os, numpy as np, pandas as pd
from collections import defaultdict
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
EL=pd.read_parquet(OUT+r"\CTS_V3_EVENT_LEDGER.parquet").reset_index(drop=True)
N=len(EL); R=EL.R.to_numpy(); si=EL.si.to_numpy(); PURGE=96
days=EL.decision_time.to_numpy()//86400; ud=np.unique(days); cuts=[ud[int(len(ud)*k/4)] for k in range(1,4)]; blk=np.digitize(days,cuts)
FOLDS=[([0],1),([0,1],2),([0,1,2],3)]
EVs=[ (s.split("|") if isinstance(s,str) and s else []) for s in EL.seq ]
RLs=[ (s.split("|") if isinstance(s,str) and s else []) for s in EL.relseq ]
def toks(k, od=False, rd=False, rng=None):
    ev=EVs[k]; rl=RLs[k]
    if od and ev: ev=ev[:]; rng.shuffle(ev)
    if rd and rl: rl=rl[:]; rng.shuffle(rl)
    out=[]
    for i,e in enumerate(ev):
        out.append(e)
        if 2*i+1<len(rl): out.append("R:"+rl[2*i]+rl[2*i+1])
    return out
def ngram_fit(idxs,Ry,minsup=25,od=False,rd=False,seed=0):
    tab=defaultdict(lambda:[0.,0]); rng=np.random.RandomState(seed)
    for k in idxs:
        t=toks(k,od,rd,rng); gr=set()
        for nn in (1,2,3):
            for i in range(len(t)-nn+1): gr.add(tuple(t[i:i+nn]))
        for g in gr: tab[g][0]+=Ry[k]; tab[g][1]+=1
    return {g:s/ct for g,(s,ct) in tab.items() if ct>=minsup}
def score(k,tab,od=False,rd=False,rng=None):
    t=toks(k,od,rd,rng); vals=[tab[tuple(t[i:i+nn])] for nn in (1,2,3) for i in range(len(t)-nn+1) if tuple(t[i:i+nn]) in tab]
    return float(np.mean(vals)) if vals else 0.0
def wf(Ry, od=False, rd=False, seed=0, ret=0.6):
    sel=np.zeros(N,bool); tested=np.zeros(N,bool); rng=np.random.RandomState(seed)
    for trb,teb in FOLDS:
        tr=np.where(np.isin(blk,trb))[0]; te=np.where(blk==teb)[0]; te=te[si[te]>si[tr].max()+PURGE]
        if len(tr)<400 or len(te)<80: continue
        tab=ngram_fit(tr,Ry,od=od,rd=rd,seed=seed)
        str_=np.array([score(k,tab,od,rd,rng) for k in tr]); ste=np.array([score(k,tab,od,rd,rng) for k in te])
        thr=np.quantile(str_[Ry[tr]>0],1-ret); sel[te]=ste>=thr; tested[te]=True
    s=sel&tested; return (R[s].mean() if s.sum() else np.nan), int(s.sum()), tested

real,k,tst=wf(R);
print(f"C real @60: exp={real:+.4f} N={k}")
od=[wf(R,od=True,seed=s)[0] for s in range(20)]; odm=float(np.nanmean(od))
rd=[wf(R,rd=True,seed=100+s)[0] for s in range(20)]; rdm=float(np.nanmean(rd))
perm=[]
for s in range(100):
    rp=R.copy(); np.random.RandomState(300+s).shuffle(rp); perm.append(wf(rp,seed=s)[0])
perm=np.array(perm); permm=float(np.nanmean(perm))
rnd=[R[tst][np.random.RandomState(7+i).choice(int(tst.sum()),k,replace=False)].mean() for i in range(100)]; rndm=float(np.mean(rnd))
nc=pd.DataFrame([
 dict(control="EVENT_ORDER_DESTROY",real=round(real,4),null_mean=round(odm,4),n=20,passes=bool(real>odm+0.05)),
 dict(control="RELATION_DESTROY",real=round(real,4),null_mean=round(rdm,4),n=20,passes=bool(real>rdm+0.05)),
 dict(control="LABEL_PERM_C",real=round(real,4),null_mean=round(permm,4),n=100,passes=bool(real>np.nanpercentile(perm,95))),
 dict(control="MATCHED_RANDOM_C",real=round(real,4),null_mean=round(rndm,4),n=100,passes=bool(real>np.percentile(rnd,95))),
])
nc.to_csv(OUT+r"\CTS_V3_NEGATIVE_CONTROLS.csv",index=False)
print(nc.to_string(index=False))
