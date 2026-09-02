"""cts_v3_models.py — CTS V3 PHASE 2: three representations under identical chronological walk-forward (4 date-blocks, expanding, purge 96).
A = CTS_V2 baseline (setup-relative static + generic, logistic+tree). B = event aggregates (gE_*, logistic+tree). C = EVENT-RELATIONAL
n-gram model over the ordered interleaved [event-symbol, relation] token stream (1/2/3-grams, train winner-mean-R scoring; order- AND relation-
sensitive; NOT raw-bar). Winner-retention frontier 80/60/40/20. Controls: label-perm x100, matched-random x100, EVENT-ORDER destruction x20,
RELATION destruction x20 (§25). BASE + STRESS. Writes CTS_V3_RETENTION_FRONTIER.csv, CTS_V3_WALK_FORWARD.csv, CTS_V3_NEGATIVE_CONTROLS.csv, CTS_V3_EVENT_MOTIFS.csv.
"""
import os, numpy as np, pandas as pd
from collections import defaultdict
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
EL=pd.read_parquet(OUT+r"\CTS_V3_EVENT_LEDGER.parquet")
V2=pd.read_parquet(OUT+r"\CTS_V2_SETUP_RELATIVE_FEATURES.parquet"); V2=V2[V2.setup=="SETUP_2"]
Abase=[c for c in V2.columns if c.startswith("gA_") or c.startswith("gB_")]
M=EL.merge(V2[["si"]+Abase],on="si",how="left").reset_index(drop=True)
Bfeat=[c for c in EL.columns if c.startswith("gE_")]
for c in Abase+Bfeat:
    x=M[c].to_numpy(float).copy(); x[~np.isfinite(x)]=np.nan
    lo,hi=np.nanpercentile(x,[1,99]); M[c]=np.clip(x,lo,hi)
SEC_YR=365.25*86400; PURGE=96; RET=[0.8,0.6,0.4,0.2]; COST=0.419; MINSUP=25
M["R_stress"]=M["R"]-COST/np.maximum(np.abs(M["gB_stop_dist_atr"].to_numpy())*1.0,1e-6)
N=len(M); R=M["R"].to_numpy(); Rs=M["R_stress"].to_numpy(); si=M["si"].to_numpy()
days=M["decision_time"].to_numpy()//86400; ud=np.unique(days); cuts=[ud[int(len(ud)*k/4)] for k in range(1,4)]; blk=np.digitize(days,cuts)
FOLDS=[([0],1),([0,1],2),([0,1,2],3)]; yrs=(M.decision_time.max()-M.decision_time.min())/SEC_YR

def stdz(tr,te):
    mu=np.nanmedian(tr,0); mu=np.where(np.isnan(mu),0,mu); tr=np.where(np.isnan(tr),mu,tr); te=np.where(np.isnan(te),mu,te)
    sd=tr.std(0); sd=np.where(np.isfinite(sd)&(sd>0),sd,1); return np.nan_to_num((tr-mu)/sd),np.nan_to_num((te-mu)/sd)
def logit(X,y,l2=1.,it=250,lr=.3):
    Xb=np.hstack([np.ones((len(X),1)),X]); w=np.zeros(Xb.shape[1])
    for _ in range(it): p=1/(1+np.exp(-np.clip(Xb@w,-30,30))); g=Xb.T@(p-y)/len(y); g[1:]+=l2*w[1:]/len(y); w-=lr*g
    return w
def lp(w,X): return 1/(1+np.exp(-np.clip(np.hstack([np.ones((len(X),1)),X])@w,-30,30)))
def toks_of(seq,relseq):
    ev=seq.split("|") if seq else []; rl=relseq.split("|") if relseq else []; out=[]
    for i,e in enumerate(ev):
        out.append(e)
        if 2*i+1<len(rl): out.append("R:"+rl[2*i]+rl[2*i+1])
    return out
def ngram_fit(toks_list,Rtr,minsup=MINSUP):
    tab=defaultdict(lambda:[0.,0])
    for toks,r in zip(toks_list,Rtr):
        gr=set()
        for nn in (1,2,3):
            for i in range(len(toks)-nn+1): gr.add(tuple(toks[i:i+nn]))
        for g in gr: tab[g][0]+=r; tab[g][1]+=1
    return {g:s/ct for g,(s,ct) in tab.items() if ct>=minsup}
def ngram_score(toks,tab):
    vals=[tab[tuple(toks[i:i+nn])] for nn in (1,2,3) for i in range(len(toks)-nn+1) if tuple(toks[i:i+nn]) in tab]
    return float(np.mean(vals)) if vals else 0.0
def tokfn(row, order_destroy=False, relation_destroy=False, seed=0):
    ev=row.seq.split("|") if row.seq else []; rl=row.relseq.split("|") if row.relseq else []
    rng=np.random.RandomState(seed+hash(row.seq)%99999)
    if order_destroy: ev=list(ev); rng.shuffle(ev)
    if relation_destroy and rl: rl=list(rl); rng.shuffle(rl)
    out=[]
    for i,e in enumerate(ev):
        out.append(e)
        if 2*i+1<len(rl): out.append("R:"+rl[2*i]+rl[2*i+1])
    return out

def thr_ret(score_tr,ytr,targets):
    w=score_tr[ytr>0]; return {t:(np.quantile(w,1-t) if len(w) else 0.) for t in targets}
def metrics(sel,tested):
    if (sel&tested).sum()==0: return None
    s=sel&tested; r=R[s]; rs=Rs[s]; wtot=(R[tested]>0).sum(); ltot=(R[tested]<=0).sum()
    return dict(sel_N=int(s.sum()),sel_exp=float(r.mean()),sel_exp_stress=float(rs.mean()),PF=float((r[r>0].sum())/(abs(r[r<=0].sum())+1e-9)),
                WR=float((r>0).mean()),winners_retained=float((r>0).sum()/wtot),losers_avoided=float(1-(r<=0).sum()/ltot),
                drop5=float(np.sort(r)[:int(len(r)*0.95)].mean()),sel_per_year=round(s.sum()/yrs,1))

def run(kind, feats=None, order_destroy=False, relation_destroy=False, seed=0):
    pooled={t:np.zeros(N,bool) for t in RET}; tested=np.zeros(N,bool); foldpos={t:[] for t in RET}
    for trb,teb in FOLDS:
        tr=np.where(np.isin(blk,trb))[0]; te=np.where(blk==teb)[0]; te=te[si[te]>si[tr].max()+PURGE]
        if len(tr)<400 or len(te)<80: continue
        if kind=="ngram":
            tl_tr=[tokfn(M.iloc[k],order_destroy,relation_destroy,seed) for k in tr]
            tl_te=[tokfn(M.iloc[k],order_destroy,relation_destroy,seed) for k in te]
            tab=ngram_fit(tl_tr,R[tr]); str_=np.array([ngram_score(t,tab) for t in tl_tr]); ste=np.array([ngram_score(t,tab) for t in tl_te])
        else:
            Xtr,Xte=stdz(M[feats].to_numpy()[tr],M[feats].to_numpy()[te]); w=logit(Xtr,(R[tr]>0).astype(float))
            str_=lp(w,Xtr); ste=lp(w,Xte)
        thr=thr_ret(str_,R[tr],RET); tested[te]=True
        for t in RET:
            sel=ste>=thr[t]; pooled[t][te]=sel
            m=metrics(_bool(te,sel,N),tested);
        # fold exps at each retention
        for t in RET:
            sel_te=np.zeros(N,bool); sel_te[te]=ste>=thr[t]; mm=metrics(sel_te,tested)
            if mm: foldpos[t].append(mm["sel_exp"])
    rows=[]
    for t in RET:
        m=metrics(pooled[t]&tested,tested)
        if m: rows.append(dict(rep=kind if feats is None else kind,retention=t,folds_pos=sum(1 for e in foldpos[t] if e>0),fold_exps=[round(e,4) for e in foldpos[t]],**m))
    return rows,pooled
def _bool(idx,val,n): b=np.zeros(n,bool); b[idx]=val; return b

front=[]
front+= [{**r,"rep":"A_cts_v2_baseline"} for r in run("logit",feats=Abase)[0]]
front+= [{**r,"rep":"B_event_aggregates"} for r in run("logit",feats=Bfeat)[0]]
front+= [{**r,"rep":"C_event_relational"} for r in run("ngram")[0]]
FR=pd.DataFrame(front); FR.to_csv(OUT+r"\CTS_V3_RETENTION_FRONTIER.csv",index=False); FR.to_csv(OUT+r"\CTS_V3_WALK_FORWARD.csv",index=False)
print("== RETENTION FRONTIER (pooled TEST) ==")
print(FR[["rep","retention","sel_exp","sel_exp_stress","winners_retained","losers_avoided","sel_N","sel_per_year","drop5","folds_pos"]].to_string(index=False))

# ---- controls at 60% retention ----
nc=[]
realC=[r for r in front if r["rep"]=="C_event_relational" and r["retention"]==0.6][0]["sel_exp"]
# EVENT-ORDER destruction x20
od=[run("ngram",order_destroy=True,seed=s)[0] for s in range(20)]
od60=[[x for x in rows if x["retention"]==0.6][0]["sel_exp"] for rows in od if [x for x in rows if x["retention"]==0.6]]
nc.append(dict(control="EVENT_ORDER_DESTROY",real=round(realC,4),null_mean=round(float(np.mean(od60)),4),n=len(od60),passes=bool(realC>np.mean(od60)+0.05)))
# RELATION destruction x20
rd=[run("ngram",relation_destroy=True,seed=s)[0] for s in range(20)]
rd60=[[x for x in rows if x["retention"]==0.6][0]["sel_exp"] for rows in rd if [x for x in rows if x["retention"]==0.6]]
nc.append(dict(control="RELATION_DESTROY",real=round(realC,4),null_mean=round(float(np.mean(rd60)),4),n=len(rd60),passes=bool(realC>np.mean(rd60)+0.05)))
# label perm x100 + matched random x100 on C @60 (fixed 60% retention threshold)
def wfC(Ry):
    sel=np.zeros(N,bool); tested=np.zeros(N,bool)
    for trb,teb in FOLDS:
        tr=np.where(np.isin(blk,trb))[0]; te=np.where(blk==teb)[0]; te=te[si[te]>si[tr].max()+PURGE]
        if len(tr)<400 or len(te)<80: continue
        tl_tr=[toks_of(M.iloc[k].seq,M.iloc[k].relseq) for k in tr]; tl_te=[toks_of(M.iloc[k].seq,M.iloc[k].relseq) for k in te]
        tab=ngram_fit(tl_tr,Ry[tr]); str_=np.array([ngram_score(t,tab) for t in tl_tr]); ste=np.array([ngram_score(t,tab) for t in tl_te])
        thr=np.quantile(str_[Ry[tr]>0],0.4); sel[te]=ste>=thr; tested[te]=True
    return sel,tested
selR,tst=wfC(R); realE=R[selR&tst].mean(); k=int((selR&tst).sum())
perm=[]
for s in range(100):
    rp=R.copy(); np.random.RandomState(300+s).shuffle(rp); se,tt=wfC(rp); perm.append(R[se&tt].mean() if (se&tt).sum() else np.nan)
perm=np.array(perm); rnd=[R[tst][np.random.RandomState(7+i).choice(int(tst.sum()),k,replace=False)].mean() for i in range(100)]
nc.append(dict(control="LABEL_PERM_C",real=round(float(realE),4),null_mean=round(float(np.nanmean(perm)),4),n=100,passes=bool(realE>np.nanpercentile(perm,95))))
nc.append(dict(control="MATCHED_RANDOM_C",real=round(float(realE),4),null_mean=round(float(np.mean(rnd)),4),n=100,passes=bool(realE>np.percentile(rnd,95))))
NC=pd.DataFrame(nc); NC.to_csv(OUT+r"\CTS_V3_NEGATIVE_CONTROLS.csv",index=False)
print("\n== NEGATIVE CONTROLS (C @60% retention) =="); print(NC.to_string(index=False))
# top motifs (full-data n-gram table, for interpretation)
tl=[toks_of(r.seq,r.relseq) for r in M.itertuples()]; tab=ngram_fit(tl,R)
mot=pd.DataFrame([(("|".join(g)),v,len(g)) for g,v in tab.items()],columns=["motif","train_mean_R","len"]).sort_values("train_mean_R")
mot.to_csv(OUT+r"\CTS_V3_EVENT_MOTIFS.csv",index=False)
print("\nworst motifs:"); print(mot.head(4).to_string(index=False)); print("best motifs:"); print(mot.tail(4).to_string(index=False))
