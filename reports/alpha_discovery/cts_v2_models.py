"""cts_v2_models.py — CTS V2 PHASE 3: chronological walk-forward (4 date-blocks, expanding B1->B2, B1B2->B3, B1B2B3->B4, purge=96), all five
representations (A generic / B setup-static / C path-aggregates / D path+generic via L2-logistic+depth2-tree; E ordered sequence via order-
sensitive nearest-centroid), the mandatory winner-retention FRONTIER (80/60/40/20% retention thresholds frozen on TRAIN, applied unchanged to
TEST), and ALL negative controls (label permutation x100, matched-random-N x100, sequence-order destruction x20). BASE + STRESS (double-cost).
Writes CTS_V2_WALK_FORWARD_RESULTS.csv, CTS_V2_RETENTION_FRONTIERS.csv, CTS_V2_REPRESENTATION_COMPARISON.csv, CTS_V2_NEGATIVE_CONTROLS.csv.
"""
import os, math, json, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
M=pd.read_parquet(OUT+r"\CTS_V2_SETUP_RELATIVE_FEATURES.parquet"); SEQ=np.load(OUT+r"\cts_v2_seq.npy")
A=[c for c in M.columns if c.startswith("gA_")]; B=[c for c in M.columns if c.startswith("gB_")]; Cc=[c for c in M.columns if c.startswith("gC_")]
REPS={"A_generic":A,"B_setup_static":B,"C_path_agg":Cc,"D_path_plus_generic":Cc+A}
SEC_YR=365.25*86400; PURGE=96; RET=[0.8,0.6,0.4,0.2]; COST=0.419
# --- clean features: kill inf, winsorize to robust [1,99] pct (per column) so no fold blows up the logistic ---
for ccln in A+B+Cc:
    x=M[ccln].to_numpy(float).copy(); x[~np.isfinite(x)]=np.nan
    lo,hi=np.nanpercentile(x,[1,99]); M[ccln]=np.clip(x,lo,hi)
M["R_stress"]=M["R"] - COST/np.maximum(np.abs(M["gB_stop_dist_atr"].to_numpy())*1.0, 1e-6)  # extra spread; stop_dist in ATR ~ risk proxy

def stdz(tr,te):
    mu=np.nanmedian(tr,0); mu=np.where(np.isnan(mu),0.0,mu)
    tr=np.where(np.isnan(tr),mu,tr); te=np.where(np.isnan(te),mu,te)
    sd=tr.std(0); sd=np.where(np.isfinite(sd)&(sd>0),sd,1); return np.nan_to_num((tr-mu)/sd),np.nan_to_num((te-mu)/sd)
def logit(X,y,l2=1.0,it=250,lr=0.3):
    Xb=np.hstack([np.ones((len(X),1)),X]); w=np.zeros(Xb.shape[1])
    for _ in range(it):
        p=1/(1+np.exp(-np.clip(Xb@w,-30,30))); g=Xb.T@(p-y)/len(y); g[1:]+=l2*w[1:]/len(y); w-=lr*g
    return w
def lpred(w,X): return 1/(1+np.exp(-np.clip(np.hstack([np.ones((len(X),1)),X])@w,-30,30)))
def tree2(X,r):
    def bs(idx):
        best=None
        for j in range(X.shape[1]):
            for th in np.unique(np.nanpercentile(X[idx,j],[30,50,70])):
                Lm=idx[X[idx,j]<=th]; Rm=idx[X[idx,j]>th]
                if len(Lm)<150 or len(Rm)<150: continue
                g=abs(r[Lm].mean()-r[Rm].mean())
                if best is None or g>best[0]: best=(g,j,th)
        return best
    root=bs(np.arange(len(X)))
    if root is None: m=r.mean(); return lambda Xte:np.full(len(Xte),m)
    _,j0,t0=root; lv={}
    for sd,idx in (("A",np.where(X[:,j0]<=t0)[0]),("B",np.where(X[:,j0]>t0)[0])):
        sp=bs(idx); lv[sd]=(None,None,r[idx].mean(),r[idx].mean()) if sp is None else (sp[1],sp[2],r[idx[X[idx,sp[1]]<=sp[2]]].mean(),r[idx[X[idx,sp[1]]>sp[2]]].mean())
    def pr(Xte):
        out=np.empty(len(Xte)); m0=Xte[:,j0]<=t0
        for sd,mk in (("A",m0),("B",~m0)):
            j1,t1,va,vb=lv[sd]; sub=np.where(mk)[0]
            if j1 is None: out[sub]=va
            else: ml=Xte[sub,j1]<=t1; out[sub[ml]]=va; out[sub[~ml]]=vb
        return out
    return pr
def seq_centroid(tr_rows,te_rows,Rtr, destroy=False, seed=0):
    Xtr=SEQ[tr_rows].copy(); Xte=SEQ[te_rows].copy()   # (n,32,6) ORDER PRESERVED
    if destroy:  # permute bar order within each 32-bar sequence (same values, same channels)
        rng=np.random.RandomState(seed)
        for k in range(len(Xtr)): Xtr[k]=Xtr[k][rng.permutation(32)]
        for k in range(len(Xte)): Xte[k]=Xte[k][rng.permutation(32)]
    Xtr=Xtr.reshape(len(Xtr),-1); Xte=Xte.reshape(len(Xte),-1)
    mu=np.nanmedian(Xtr,0); sd=Xtr.std(0); sd=np.where(sd>0,sd,1)
    Ztr=(np.where(np.isnan(Xtr),mu,Xtr)-mu)/sd; Zte=(np.where(np.isnan(Xte),mu,Xte)-mu)/sd
    yw=np.asarray(Rtr)>0; cw=Ztr[yw].mean(0); cls=Ztr[~yw].mean(0)
    def score(Z): return np.linalg.norm(Z-cls,axis=1)-np.linalg.norm(Z-cw,axis=1)  # >0 closer to winner-centroid
    return score(Ztr), score(Zte)

def thresholds(score_tr, ytr, targets):
     w=score_tr[ytr>0]; return {t:(np.quantile(w,1-t) if len(w) else 0.0) for t in targets}
def metrics(R,Rs,sel,wtot,ltot):
    if sel.sum()==0: return None
    r=R[sel]; rs=Rs[sel]; pf=(r[r>0].sum())/(abs(r[r<=0].sum())+1e-9)
    return dict(sel_N=int(sel.sum()),sel_exp=float(r.mean()),sel_exp_stress=float(rs.mean()),PF=float(pf),WR=float((r>0).mean()),
                winners_retained=float((r>0).sum()/wtot) if wtot else np.nan,losers_avoided=float(1-((r<=0).sum()/ltot)) if ltot else np.nan,
                losers_retained=float((r<=0).sum()/ltot) if ltot else np.nan)

wf=[]; front=[]; comp=[]; nctrl=[]
for sid,g in M.groupby("setup"):
    g=g.sort_values("decision_time").reset_index(drop=True); N=len(g); R=g["R"].to_numpy(); Rs=g["R_stress"].to_numpy()
    si=g["si"].to_numpy(); seqrow=g["seq_row"].to_numpy(); yrs=(g.decision_time.max()-g.decision_time.min())/SEC_YR
    days=g["decision_time"].to_numpy()//86400; ud=np.unique(days)
    # 4 date blocks (equal-ish trade counts, whole days)
    cuts=[ud[int(len(ud)*k/4)] for k in range(1,4)]
    blk=np.digitize(days,cuts)   # 0..3
    folds=[([0],1),([0,1],2),([0,1,2],3)]
    def run_rep(name, feats=None, seq=False):
        pooled_sel={t:np.zeros(N,bool) for t in RET}; tested=np.zeros(N,bool); foldmetrics={t:[] for t in RET}
        for trblk,teblk in folds:
            tr=np.where(np.isin(blk,trblk))[0]; te=np.where(blk==teblk)[0]
            te=te[si[te] > si[tr].max()+PURGE]
            if len(tr)<400 or len(te)<80: continue
            if seq: str_,ste=seq_centroid(seqrow[tr],seqrow[te],R[tr])
            else:
                Xtr,Xte=stdz(g[feats].to_numpy()[tr],g[feats].to_numpy()[te])
                w=logit(Xtr,(R[tr]>0).astype(float)); s1tr,s1te=lpred(w,Xtr),lpred(w,Xte)
                p=tree2(Xtr,R[tr]); s2tr,s2te=p(Xtr),p(Xte)
                # combine: rank-average of logistic + tree
                str_=0.5*(pd.Series(s1tr).rank(pct=True).to_numpy()+pd.Series(s2tr).rank(pct=True).to_numpy())
                ste=0.5*(pd.Series(s1te).rank(pct=True).to_numpy()+pd.Series(s2te).rank(pct=True).to_numpy())
            thr=thresholds(str_,R[tr],RET); wtot=(R[te]>0).sum(); ltot=(R[te]<=0).sum()
            tested[te]=True
            for t in RET:
                sel=ste>=thr[t]; pooled_sel[t][te]=sel
                m=metrics(R[te],Rs[te],sel,wtot,ltot)
                if m: foldmetrics[t].append(m["sel_exp"])
        # pooled
        wtotP=(R[tested]>0).sum(); ltotP=(R[tested]<=0).sum()
        for t in RET:
            sel=pooled_sel[t]&tested; m=metrics(R,Rs,sel,wtotP,ltotP)
            if not m: continue
            drop5=np.sort(R[sel])[:int(sel.sum()*0.95)].mean()
            pos_folds=sum(1 for e in foldmetrics[t] if e>0)
            front.append(dict(setup=sid,rep=name,retention=t,**m,sel_per_year=round(sel.sum()/yrs,1),
                              drop5_exp=round(float(drop5),4),folds_pos=pos_folds,fold_exps=[round(e,4) for e in foldmetrics[t]]))
        return pooled_sel,tested,foldmetrics
    reps_pooled={}
    for name,feats in REPS.items(): reps_pooled[name]=run_rep(name,feats=feats)
    reps_pooled["E_ordered_seq"]=run_rep("E_ordered_seq",seq=True)
    # ---- sequence-order destruction control (CONTROL_4) at 60% retention ----
    destroy_exps=[]
    for sd in range(20):
        ps={0.6:np.zeros(N,bool)}; tested=np.zeros(N,bool)
        for trblk,teblk in folds:
            tr=np.where(np.isin(blk,trblk))[0]; te=np.where(blk==teblk)[0]; te=te[si[te]>si[tr].max()+PURGE]
            if len(tr)<400 or len(te)<80: continue
            dtr,dte=seq_centroid(seqrow[tr],seqrow[te],R[tr],destroy=True,seed=sd*7+1)
            thr=thresholds(dtr,R[tr],[0.6]); ps[0.6][te]=dte>=thr[0.6]; tested[te]=True
        s=ps[0.6]&tested
        if s.sum(): destroy_exps.append(float(R[s].mean()))
    # real seq @60
    seqfront=[f for f in front if f["setup"]==sid and f["rep"]=="E_ordered_seq" and f["retention"]==0.6]
    seq_real=seqfront[0]["sel_exp"] if seqfront else np.nan
    seq_destroy_mean=float(np.mean(destroy_exps)) if destroy_exps else np.nan
    nctrl.append(dict(setup=sid,control="SEQ_ORDER_DESTROY",real_seq_exp=round(seq_real,4),destroy_mean_exp=round(seq_destroy_mean,4),
                      n=len(destroy_exps),passes=bool(np.isfinite(seq_real) and seq_real>seq_destroy_mean+0.05)))
print("phase3 core done; running label-perm + random-N controls...")
# ---- CONTROL_1 label permutation (100) + CONTROL_3 random-N (100) on rep D @60 ----
for sid,g in M.groupby("setup"):
    g=g.sort_values("decision_time").reset_index(drop=True); N=len(g); R=g["R"].to_numpy(); si=g["si"].to_numpy()
    days=g["decision_time"].to_numpy()//86400; ud=np.unique(days); cuts=[ud[int(len(ud)*k/4)] for k in range(1,4)]; blk=np.digitize(days,cuts)
    feats=REPS["D_path_plus_generic"]
    def wf_D(Ry):
        sel=np.zeros(N,bool); tested=np.zeros(N,bool)
        for trblk,teblk in [([0],1),([0,1],2),([0,1,2],3)]:
            tr=np.where(np.isin(blk,trblk))[0]; te=np.where(blk==teblk)[0]; te=te[si[te]>si[tr].max()+PURGE]
            if len(tr)<400 or len(te)<80: continue
            Xtr,Xte=stdz(g[feats].to_numpy()[tr],g[feats].to_numpy()[te]); w=logit(Xtr,(Ry[tr]>0).astype(float))
            str_=lpred(w,Xtr); ste=lpred(w,Xte); thr=np.quantile(str_[Ry[tr]>0],0.4); sel[te]=ste>=thr; tested[te]=True
        return sel,tested
    selR,tested=wf_D(R); realexp=R[selR&tested].mean() if (selR&tested).sum() else np.nan
    perm=[]
    for s in range(100):
        rp=R.copy(); np.random.RandomState(200+s).shuffle(rp); se,tt=wf_D(rp); perm.append(R[se&tt].mean() if (se&tt).sum() else np.nan)
    perm=np.array(perm); k=int((selR&tested).sum())
    rnd=[R[tested][np.random.RandomState(11+i).choice(int(tested.sum()),k,replace=False)].mean() for i in range(100)]
    nctrl.append(dict(setup=sid,control="LABEL_PERM_D",real_seq_exp=round(float(realexp),4),destroy_mean_exp=round(float(np.nanmean(perm)),4),
                      n=100,passes=bool(realexp>np.nanpercentile(perm,95))))
    nctrl.append(dict(setup=sid,control="RANDOM_MATCHED_N",real_seq_exp=round(float(realexp),4),destroy_mean_exp=round(float(np.mean(rnd)),4),
                      n=100,passes=bool(realexp>np.percentile(rnd,95))))

FR=pd.DataFrame(front); FR.to_csv(OUT+r"\CTS_V2_RETENTION_FRONTIERS.csv",index=False)
FR.to_csv(OUT+r"\CTS_V2_WALK_FORWARD_RESULTS.csv",index=False)
NC=pd.DataFrame(nctrl); NC.to_csv(OUT+r"\CTS_V2_NEGATIVE_CONTROLS.csv",index=False)
# representation comparison @60 retention
cmp=FR[FR.retention==0.6].pivot_table(index="setup",columns="rep",values="sel_exp")
cmp.to_csv(OUT+r"\CTS_V2_REPRESENTATION_COMPARISON.csv")
print("\n== RETENTION FRONTIER @60% winner-retention (pooled TEST) ==")
print(FR[FR.retention==0.6][["setup","rep","sel_exp","sel_exp_stress","winners_retained","losers_avoided","sel_N","sel_per_year","drop5_exp","folds_pos"]].to_string(index=False))
print("\n== NEGATIVE CONTROLS ==")
print(NC.to_string(index=False))
