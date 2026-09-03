"""gc_ctx_v1_models.py — GC V1 four-representation walk-forward. A=XAU baseline, B=A+GC price, C=A+GC real volume, D=A+GC price+volume; SAME
L2-logistic capacity, chronological 4-block expanding walk-forward (purge 96), winner-retention frontier 80/60/40/20. Computes the primary GC
information gate (C/D vs A) and the CENTRAL real-volume-specific gate (best C/D vs B). BASE + STRESS. Writes representation comparison + frontier.
"""
import os, numpy as np, pandas as pd, json
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
J=pd.read_parquet(OUT+r"\GC_CTX_JOINED.parquet"); proto=json.load(open(OUT+r"\GC_REAL_VOLUME_PROTOCOL.json"))
A=[c for c in J.columns if c.startswith("gA_") or c.startswith("gB_")]; P=proto["price_features"]; Vv=proto["volume_features"]
REPS={"A_xau_baseline":A,"B_plus_gc_price":A+P,"C_plus_gc_volume":A+Vv,"D_plus_gc_price_vol":A+P+Vv}
RET=[0.8,0.6,0.4,0.2]; PURGE=96; SEC_YR=365.25*86400
for c in set(A+P+Vv):
    if c in J: x=J[c].to_numpy(float).copy(); x[~np.isfinite(x)]=np.nan; lo,hi=np.nanpercentile(x,[1,99]); J[c]=np.clip(x,lo,hi)
J["R_stress"]=J["R"]-0.05   # frozen STRESS proxy: +0.05R extra-cost haircut (wider spread)
def stdz(tr,te):
    mu=np.nanmedian(tr,0); mu=np.where(np.isnan(mu),0,mu); tr=np.where(np.isnan(tr),mu,tr); te=np.where(np.isnan(te),mu,te)
    sd=tr.std(0); sd=np.where(np.isfinite(sd)&(sd>0),sd,1); return np.nan_to_num((tr-mu)/sd),np.nan_to_num((te-mu)/sd)
def logit(X,y,l2=1.,it=250,lr=.3):
    Xb=np.hstack([np.ones((len(X),1)),X]); w=np.zeros(Xb.shape[1])
    for _ in range(it): p=1/(1+np.exp(-np.clip(Xb@w,-30,30))); grd=Xb.T@(p-y)/len(y); grd[1:]+=l2*w[1:]/len(y); w-=lr*grd
    return w
def lp(w,X): return 1/(1+np.exp(-np.clip(np.hstack([np.ones((len(X),1)),X])@w,-30,30)))
front=[]
for sid,g in J.groupby("setup"):
    g=g.sort_values("decision_time").reset_index(drop=True); N=len(g); R=g["R"].to_numpy(); Rs=g["R_stress"].to_numpy(); si=g["si"].to_numpy()
    days=g["decision_time"].to_numpy()//86400; ud=np.unique(days); cuts=[ud[int(len(ud)*k/4)] for k in range(1,4)]; blk=np.digitize(days,cuts)
    yrs=(g.decision_time.max()-g.decision_time.min())/SEC_YR; FOLDS=[([0],1),([0,1],2),([0,1,2],3)]
    for rep,feats in REPS.items():
        feats=[f for f in feats if f in g.columns]; pooled={t:np.zeros(N,bool) for t in RET}; tested=np.zeros(N,bool); foldE={t:[] for t in RET}
        for trb,teb in FOLDS:
            tr=np.where(np.isin(blk,trb))[0]; te=np.where(blk==teb)[0]; te=te[si[te]>si[tr].max()+PURGE]
            if len(tr)<400 or len(te)<80: continue
            Xtr,Xte=stdz(g[feats].to_numpy()[tr],g[feats].to_numpy()[te]); w=logit(Xtr,(R[tr]>0).astype(float)); str_=lp(w,Xtr); ste=lp(w,Xte)
            wtr=str_[R[tr]>0]
            for t in RET:
                thr=np.quantile(wtr,1-t) if len(wtr) else 0; sel=ste>=thr; pooled[t][te]=sel
                st=np.zeros(N,bool); st[te]=sel; foldE[t].append(R[st].mean() if st.sum() else np.nan)
            tested[te]=True
        wtot=(R[tested]>0).sum(); ltot=(R[tested]<=0).sum()
        for t in RET:
            s=pooled[t]&tested
            if s.sum()==0: continue
            r=R[s]; rs=Rs[s]; drop5=np.sort(r)[:int(len(r)*0.95)].mean()
            front.append(dict(setup=sid,rep=rep,retention=t,sel_N=int(s.sum()),sel_exp=round(float(r.mean()),4),sel_exp_stress=round(float(rs.mean()),4),
                PF=round(float((r[r>0].sum())/(abs(r[r<=0].sum())+1e-9)),3),WR=round(float((r>0).mean()),3),
                winners_retained=round(float((r>0).sum()/wtot),3),losers_avoided=round(float(1-(r<=0).sum()/ltot),3),
                drop5=round(float(drop5),4),sel_per_year=round(s.sum()/yrs,1),folds_pos=sum(1 for e in foldE[t] if e>0),
                fold_exps=[round(e,4) for e in foldE[t]]))
FR=pd.DataFrame(front); FR.to_csv(OUT+r"\GC_REAL_VOLUME_RETENTION_FRONTIERS.csv",index=False); FR.to_csv(OUT+r"\GC_REAL_VOLUME_WALK_FORWARD.csv",index=False)
cmp=FR[FR.retention==0.6].pivot_table(index="setup",columns="rep",values="sel_exp"); cmp.to_csv(OUT+r"\GC_REAL_VOLUME_REPRESENTATION_COMPARISON.csv")
print("== FRONTIER @60% winner-retention (pooled TEST) ==");
print(FR[FR.retention==0.6][["setup","rep","sel_exp","sel_exp_stress","winners_retained","losers_avoided","sel_N","folds_pos"]].to_string(index=False))
# ---- gates ----
import ast
def at(sid,rep): x=FR[(FR.setup==sid)&(FR.rep==rep)&(FR.retention==0.6)]; return x.iloc[0] if len(x) else None
gate=[]
for sid in J.setup.unique():
    a=at(sid,"A_xau_baseline"); b=at(sid,"B_plus_gc_price"); c=at(sid,"C_plus_gc_volume"); dd=at(sid,"D_plus_gc_price_vol")
    def folds(x): return x.fold_exps if isinstance(x.fold_exps,list) else ast.literal_eval(str(x.fold_exps))
    # GC info: best(C,D) vs A
    bestCD=max([c,dd],key=lambda x:x.sel_exp); dCA=bestCD.sel_exp-a.sel_exp
    fCA=[cc-aa for cc,aa in zip(folds(bestCD),folds(a))]; info=(dCA>=0.05 and sum(1 for x in fCA if x>=0.03)>=2)
    # real-volume specific: best(C,D) vs B
    dCB=bestCD.sel_exp-b.sel_exp; fCB=[cc-bb for cc,bb in zip(folds(bestCD),folds(b))]; rvs=(dCB>=0.03 and sum(1 for x in fCB if x>=0.02)>=2)
    # price-only: B vs A
    dBA=b.sel_exp-a.sel_exp; fBA=[bb-aa for bb,aa in zip(folds(b),folds(a))]; price=(dBA>=0.05 and sum(1 for x in fBA if x>=0.03)>=2)
    gate.append(dict(setup=sid,A60=a.sel_exp,B60=b.sel_exp,C60=c.sel_exp,D60=dd.sel_exp,bestCD=bestCD.rep,
        GC_INFO=info,REAL_VOL_SPECIFIC=rvs,PRICE_ONLY=price,dCA=round(dCA,4),dCB=round(dCB,4),dBA=round(dBA,4)))
GT=pd.DataFrame(gate); GT.to_csv(OUT+r"\GC_REAL_VOLUME_GATES.csv",index=False)
print("\n== GATES @60% =="); print(GT.to_string(index=False))
print("\nGC_INFORMATION_INCREMENTAL_VALUE(any):", bool(GT.GC_INFO.any()))
print("GC_REAL_VOLUME_SPECIFIC_VALUE(any):", bool(GT.REAL_VOL_SPECIFIC.any()))
print("GC_PRICE_ONLY_INCREMENTAL_VALUE(any):", bool(GT.PRICE_ONLY.any()))
