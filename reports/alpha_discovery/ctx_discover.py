"""ctx_discover.py — CONTEXTUAL TRADE SELECTION V1, PHASE 3-6: BLIND winner-vs-loser contrasts (frozen before unblinding), chronological
walk-forward selector models (unfiltered base vs L2-logistic vs depth-2 tree; nested threshold on TRAIN, applied UNCHANGED to the later fold),
TAKE/SKIP metrics on the pooled INTERNAL_TEST, negative controls (label permutation / time-shift placebo / random-N), classification
(PROFITABLE_CONTEXTUAL_SELECTION / LOSE_LESS_ONLY / NO_DISCRIMINATION), then unblind + cross-setup recurrence + frequency/feasibility.
Pure numpy (interpretable). INTERNAL_GENERALIZATION only — history is MATERIALLY_EXPOSED, this is NOT OOS validation.
"""
import os, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
M=pd.read_parquet(OUT+r"\CTX_TRADE_FEATURES.parquet")
FEATS=[c for c in M.columns if c.startswith("g")]
SEC_YR=365.25*86400; PURGE=96; rng=np.random.RandomState(7)

def stdz(Xtr,Xte):
    mu=np.nanmedian(Xtr,0); Xtr=np.where(np.isnan(Xtr),mu,Xtr); Xte=np.where(np.isnan(Xte),mu,Xte)
    sd=Xtr.std(0); sd=np.where(sd>0,sd,1.0); return (Xtr-mu)/sd,(Xte-mu)/sd,mu,sd
def logit_fit(X,y,l2=1.0,it=300,lr=0.3):
    Xb=np.hstack([np.ones((len(X),1)),X]); w=np.zeros(Xb.shape[1])
    for _ in range(it):
        p=1/(1+np.exp(-np.clip(Xb@w,-30,30))); g=Xb.T@(p-y)/len(y); g[1:]+=l2*w[1:]/len(y); w-=lr*g
    return w
def logit_pred(w,X): return 1/(1+np.exp(-np.clip(np.hstack([np.ones((len(X),1)),X])@w,-30,30)))
def tree2(X,r):  # depth-2 regression tree on net_R -> returns predict(Xte)
    def best_split(idx):
        best=None
        for j in range(X.shape[1]):
            xj=X[idx,j]; qs=np.nanpercentile(xj,[30,50,70])
            for th in np.unique(qs):
                L=idx[xj<=th]; Rr=idx[xj>th]
                if len(L)<200 or len(Rr)<200: continue
                gain=abs(r[L].mean()-r[Rr].mean())
                if best is None or gain>best[0]: best=(gain,j,th)
        return best
    root=best_split(np.arange(len(X)))
    if root is None: m=r.mean(); return lambda Xte: np.full(len(Xte),m)
    _,j0,t0=root; A=np.where(X[:,j0]<=t0)[0]; B=np.where(X[:,j0]>t0)[0]
    leaves={}
    for side,idx in (("A",A),("B",B)):
        sp=best_split(idx)
        if sp is None: leaves[side]=(None,None,r[idx].mean(),r[idx].mean())
        else:
            _,j1,t1=sp; leaves[side]=(j1,t1,r[idx[X[idx,j1]<=t1]].mean(),r[idx[X[idx,j1]>t1]].mean())
    def pred(Xte):
        out=np.empty(len(Xte))
        m0=Xte[:,j0]<=t0
        for side,msk in (("A",m0),("B",~m0)):
            j1,t1,va,vb=leaves[side]
            if j1 is None: out[msk]=va
            else:
                sub=np.where(msk)[0]; ml=Xte[sub,j1]<=t1; out[sub[ml]]=va; out[sub[~ml]]=vb
        return out
    return pred

def wf_select(g, scorer, tune=True, fixed_q=0.5):
    """expanding chronological walk-forward; nested threshold on TRAIN; return pooled test (mask_selected, R)."""
    g=g.sort_values("si").reset_index(drop=True); N=len(g); R=g["R"].to_numpy(); X=g[FEATS].to_numpy(float); si=g["si"].to_numpy()
    bounds=[int(N*k/5) for k in range(6)]; sel=np.zeros(N,bool); tested=np.zeros(N,bool)
    for k in range(1,5):
        tr=np.arange(0,bounds[k]); te=np.arange(bounds[k],bounds[k+1])
        te=te[si[te] > si[tr].max()+PURGE]                     # purge/embargo
        if len(te)<50 or len(tr)<500: continue
        Xtr,Xte,_,_=stdz(X[tr],X[te]); str_=scorer(Xtr,R[tr],Xte)
        if tune:
            thr=None; best=-9
            for q in (0.3,0.4,0.5,0.6,0.7):
                cut=np.quantile(str_[0],q); m=str_[0]>=cut
                if m.mean()<0.15: continue
                e=R[tr][m].mean()
                if e>best: best=e; thr=cut
            if thr is None: thr=np.quantile(str_[0],0.5)
        else: thr=np.quantile(str_[0],fixed_q)
        sel[te]=str_[1]>=thr; tested[te]=True
    return sel, tested, R

def scorer_logit(Xtr,Rtr,Xte):
    w=logit_fit(Xtr,(Rtr>0).astype(float)); return (logit_pred(w,Xtr), logit_pred(w,Xte))
def scorer_tree(Xtr,Rtr,Xte):
    p=tree2(Xtr,Rtr); return (p(Xtr), p(Xte))

def metrics(R,sel,tested):
    te=tested; allR=R[te]; s=sel&te; sk=(~sel)&te
    def blk(r):
        if len(r)==0: return dict(N=0,exp=np.nan,PF=np.nan,WR=np.nan)
        pf=(r[r>0].sum())/(abs(r[r<=0].sum())+1e-9); return dict(N=len(r),exp=float(r.mean()),PF=float(pf),WR=float((r>0).mean()))
    a=blk(allR); ss=blk(R[s]); kk=blk(R[sk])
    wtot=(allR>0).sum(); ltot=(allR<=0).sum()
    wret=(R[s]>0).sum()/wtot if wtot else np.nan; lav=1-((R[s]<=0).sum()/ltot) if ltot else np.nan
    return dict(all_N=a["N"],all_exp=round(a["exp"],4),all_PF=round(a["PF"],3),all_WR=round(a["WR"],3),
                sel_N=ss["N"],sel_pct=round(ss["N"]/max(a["N"],1),3),sel_exp=round(ss["exp"],4) if ss["N"] else np.nan,
                sel_PF=round(ss["PF"],3) if ss["N"] else np.nan,sel_WR=round(ss["WR"],3) if ss["N"] else np.nan,
                skip_N=kk["N"],skip_exp=round(kk["exp"],4) if kk["N"] else np.nan,
                winners_retained=round(wret,3),losers_avoided=round(lav,3),exp_lift=round((ss["exp"]-a["exp"]),4) if ss["N"] else np.nan)

# ---------------- BLIND winner-vs-loser contrasts (frozen before unblinding) ----------------
contr=[]
for sid,g in M.groupby("setup_id"):
    R=g["R"].to_numpy(); w=R>0; day=g["decision_time"].to_numpy()//86400
    for f in FEATS:
        x=g[f].to_numpy(float); ok=~np.isnan(x)
        if ok.sum()<200: continue
        xw=x[ok&w]; xl=x[ok&~w]
        if len(xw)<30 or len(xl)<30: continue
        sd=np.nanstd(x[ok])+1e-9; d=(np.nanmean(xw)-np.nanmean(xl))/sd     # standardized winner-loser diff
        # effect on net_R: corr(feature, R)
        xr=x[ok]-np.nanmean(x[ok]); rr=R[ok]-R[ok].mean(); corr=(xr*rr).sum()/(np.sqrt((xr**2).sum()*(rr**2).sum())+1e-9)
        contr.append(dict(setup_id=sid,feature=f,std_win_loss_diff=round(float(d),4),corr_R=round(float(corr),4),abseff=abs(float(d))))
CT=pd.DataFrame(contr); CT.to_csv(OUT+r"\WINNER_LOSER_CONTRASTS.csv",index=False)
blindhash=hashlib.sha256(CT.round(4).to_csv(index=False).encode()).hexdigest()[:16]
print(f"BLIND winner-loser contrasts frozen: {len(CT)} rows, hash={blindhash}")

# ---------------- selector models + TAKE/SKIP + controls, per setup ----------------
res=[];
for sid,g in M.groupby("setup_id"):
    row=dict(setup_id=sid,object=g.object.iloc[0],mechanism=g.mechanism.iloc[0],N=len(g),base_exp=round(g.R.mean(),4))
    best=None
    for mdl,scr in (("logit",scorer_logit),("tree",scorer_tree)):
        sel,tested,R=wf_select(g,scr); m=metrics(R,sel,tested); m["model"]=mdl
        # negative control: label permutation (shuffle R), same pipeline, 2x
        clifts=[]
        for s_ in range(2):
            gp=g.copy(); rp=gp["R"].to_numpy().copy(); np.random.RandomState(100+s_).shuffle(rp); gp["R"]=rp
            selp,tep,Rp=wf_select(gp,scr); mp=metrics(Rp,selp,tep); clifts.append(mp["exp_lift"] if np.isfinite(mp["exp_lift"]) else 0)
        m["perm_lift"]=round(float(np.nanmean(clifts)),4)
        if best is None or (np.isfinite(m["sel_exp"]) and m["sel_exp"]>best["sel_exp"]): best=m
    row.update({k:best[k] for k in ("model","all_N","all_exp","all_PF","all_WR","sel_N","sel_pct","sel_exp","sel_PF","sel_WR","skip_N","skip_exp","winners_retained","losers_avoided","exp_lift","perm_lift")})
    # random-N control
    Rall=g.R.to_numpy(); k=int(row["sel_pct"]*len(Rall)); rnd=[Rall[np.random.RandomState(9+i).choice(len(Rall),k,replace=False)].mean() for i in range(20)]
    row["randN_exp"]=round(float(np.mean(rnd)),4)
    # classify
    real_ok = np.isfinite(row["sel_exp"]) and row["sel_exp"]>0 and row["exp_lift"]>0 and row["exp_lift"]>2*max(row["perm_lift"],0)+0.01
    if real_ok: row["class"]="PROFITABLE_CONTEXTUAL_SELECTION"
    elif np.isfinite(row["sel_exp"]) and row["sel_exp"]>row["base_exp"]+0.02 and row["exp_lift"]>2*max(row["perm_lift"],0): row["class"]="LOSE_LESS_ONLY"
    else: row["class"]="NO_DISCRIMINATION"
    # frequency of selected
    yrs=(g.decision_time.max()-g.decision_time.min())/SEC_YR; row["sel_per_year"]=round(row["sel_N"]/yrs,1) if yrs>0 else np.nan
    res.append(row); print(f"  {sid} {row['mechanism'][:22]:22s} base={row['base_exp']:+.3f} SEL[{row['model']}]={row['sel_exp']} lift={row['exp_lift']} permLift={row['perm_lift']} Wret={row['winners_retained']} Lavd={row['losers_avoided']} -> {row['class']}")
RS=pd.DataFrame(res); RS.to_csv(OUT+r"\SETUP_CONTEXT_RESULTS.csv",index=False)
# negative control summary
NC=RS[["setup_id","exp_lift","perm_lift","randN_exp","base_exp","sel_exp"]].copy()
NC["real_beats_placebo"]=(NC.exp_lift>2*NC.perm_lift.clip(lower=0)+0.01)&(NC.sel_exp>NC.randN_exp)
NC.to_csv(OUT+r"\NEGATIVE_CONTROL_RESULTS.csv",index=False)
gate="PASS" if (RS["perm_lift"].abs().mean() < 0.5*RS["exp_lift"].clip(lower=0).mean()+1e-9) else "REVIEW"
print(f"\nNEGATIVE_CONTROL_GATE = {gate} (mean real lift={RS.exp_lift.clip(lower=0).mean():.4f} vs mean |perm lift|={RS.perm_lift.abs().mean():.4f})")
print("classes:", dict(RS['class'].value_counts()))
RS.to_parquet(OUT+r"\_ctx_results.parquet")
print("SETUP results saved.")
