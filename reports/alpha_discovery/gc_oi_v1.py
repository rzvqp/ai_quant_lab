"""gc_oi_v1.py — GC OPEN INTEREST CONTEXTUAL VALUE V1. Build 5 frozen OI information families (O1 level/regime, O2 change, O3 price x OI,
O4 volume x OI, O5 XAU/GC relative x OI) from the DAILY total-family GC open interest (roll-immune, point-in-time: OI used only after its
ts_event dissemination <= XAU decision). Join to the 3 frozen CTS setups (reusing the GC price+volume features from GC_VOLUME_V1). Seven
representations A..G isolate whether OI adds value over the already-failed GC price/volume. Same L2-logistic, chronological walk-forward,
retention frontier. DAILY OI windows [1,5,10,20,60] (not intraday 4/8/16/32). Freezes inventory+protocol (+hash).
"""
import os, json, hashlib, numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OI=pd.read_parquet(OUT+r"\GC_OI_DAILY.parquet").sort_values("avail_unix").reset_index(drop=True)
oi=OI["total_oi"].to_numpy(float); av=OI["avail_unix"].to_numpy()
ser=pd.Series
# --- causal daily OI features (all use prior/at-availability values) ---
ma20=ser(oi).rolling(20).mean().to_numpy(); ma60=ser(oi).rolling(60).mean().to_numpy()
pct252=ser(oi).rolling(252).apply(lambda x:(x[:-1]<x[-1]).mean(),raw=True).to_numpy()
d1=oi/np.roll(oi,1)-1; d5=oi/np.roll(oi,5)-1; d20=oi/np.roll(oi,20)-1
rise=(np.diff(oi,prepend=oi[0])>0).astype(float)
def streak(a):
    out=np.zeros(len(a));c=0
    for i in range(len(a)): c=c+1 if a[i]>0 else 0; out[i]=c
    return out
OIF={}
OIF["o1_oi_rel_ma20"]=oi/(ma20+1e-9); OIF["o1_oi_dev_ma60"]=(oi-ma60)/(ma60+1e-9); OIF["o1_oi_pct252"]=pct252
OIF["o2_doi_1"]=d1; OIF["o2_doi_5"]=d5; OIF["o2_doi_20"]=d20; OIF["o2_oi_rise_streak"]=streak(rise); OIF["o2_oi_accel_5_20"]=d5-d20
OIdf=pd.DataFrame(OIF); OIdf["av"]=av
# --- join to XAU trades (causal: OI row with av<=decision_time) ---
J=pd.read_parquet(OUT+r"\GC_CTX_JOINED.parquet"); proto0=json.load(open(OUT+r"\GC_REAL_VOLUME_PROTOCOL.json"))
P=[c for c in proto0["price_features"] if c in J.columns]; Vv=[c for c in proto0["volume_features"] if c in J.columns]
A=[c for c in J.columns if c.startswith("gA_") or c.startswith("gB_")]
dt=J["decision_time"].to_numpy(); pos=np.searchsorted(av,dt,side="right")-1
future=int((pos<0).sum())
ok=pos>=0; J=J[ok].reset_index(drop=True); pos=pos[ok]
O1=["o1_oi_rel_ma20","o1_oi_dev_ma60","o1_oi_pct252"]; O2=["o2_doi_1","o2_doi_5","o2_doi_20","o2_oi_rise_streak","o2_oi_accel_5_20"]
for c in O1+O2: J[c]=OIdf[c].to_numpy()[pos]
# O3 price x OI (neutral interactions): GC price displacement sign x OI change; magnitude products
gcret=np.sign(J["p_gc_disp_8"].to_numpy()) if "p_gc_disp_8" in J else np.zeros(len(J))
J["o3_price_x_doi5"]=gcret*np.sign(J["o2_doi_5"]); J["o3_pricemag_x_doi5"]=J.get("p_gc_disp_8",0)*J["o2_doi_5"]
J["o3_pxoi_updn"]=((J.get("p_gc_disp_8",0)>0)&(J["o2_doi_5"]>0)).astype(float)-((J.get("p_gc_disp_8",0)<0)&(J["o2_doi_5"]>0)).astype(float)
# O4 volume x OI
vrel=J["g1_vol_rel_tod"].to_numpy() if "g1_vol_rel_tod" in J else np.ones(len(J))
J["o4_vol_x_doi5"]=vrel*J["o2_doi_5"]; J["o4_highvol_oiup"]=((vrel>1.1)&(J["o2_doi_5"]>0)).astype(float); J["o4_highvol_oidn"]=((vrel>1.1)&(J["o2_doi_5"]<0)).astype(float)
# O5 XAU/GC relative x OI: XAU distance-to-ref x OI regime
xdisp=J["gB_dist_ref_atr"].to_numpy() if "gB_dist_ref_atr" in J else np.zeros(len(J))
J["o5_xau_x_oiregime"]=xdisp*J["o1_oi_rel_ma20"]; J["o5_xau_x_doi5"]=xdisp*J["o2_doi_5"]
O3=["o3_price_x_doi5","o3_pricemag_x_doi5","o3_pxoi_updn"]; O4=["o4_vol_x_doi5","o4_highvol_oiup","o4_highvol_oidn"]; O5=["o5_xau_x_oiregime","o5_xau_x_doi5"]
OIfeat=O1+O2+O3+O4+O5
J.to_parquet(OUT+r"\GC_OI_JOINED.parquet")
print(f"OI causal join: XAU trades={len(J)} future_oi_used={future}")
print("matched per setup:", J.groupby("setup").size().to_dict())
# inventory + protocol freeze
inv=pd.DataFrame([dict(feature=c,family=c.split('_')[0].upper(),kind="OI") for c in OIfeat])
inv.to_csv(OUT+r"\GC_OI_FEATURE_INVENTORY.csv",index=False)
proto=dict(mandate="GC_OI_CONTEXT_V1",oi_source="Databento GLBX.MDP3 statistics GC.FUT stat_type=9 OPEN_INTEREST",
    oi_construction="DAILY total-family GC OI (sum across outrights; roll-immune)",oi_causality="use OI only after ts_event dissemination <= decision (point-in-time)",
    oi_windows_days=[1,5,10,20,60],families=["O1","O2","O3","O4","O5"],oi_features=OIfeat,price_features=P,volume_features=Vv,
    representations={"A":"XAU","B":"A+price","C":"A+volume","D":"A+OI","E":"A+price+OI","F":"A+volume+OI","G":"A+price+volume+OI"},
    model="L2_logistic",walk_forward="4 date-blocks expanding purge96",retention=[0.8,0.6,0.4,0.2])
json.dump(proto,open(OUT+r"\GC_OI_PROTOCOL.json","w"),indent=2,default=str)
fh=hashlib.sha256(open(OUT+r"\GC_OI_FEATURE_INVENTORY.csv","rb").read()).hexdigest()[:20]
ph=hashlib.sha256(open(OUT+r"\GC_OI_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"OI features={len(OIfeat)} GC_OI_FEATURE_HASH={fh} GC_OI_PROTOCOL_HASH={ph}")
# ---- 7 representations walk-forward ----
REPS={"A_xau":A,"B_price":A+P,"C_volume":A+Vv,"D_oi":A+OIfeat,"E_price_oi":A+P+OIfeat,"F_volume_oi":A+Vv+OIfeat,"G_all":A+P+Vv+OIfeat}
for c in set(sum(REPS.values(),[])):
    if c in J: x=J[c].to_numpy(float).copy(); x[~np.isfinite(x)]=np.nan; lo,hi=np.nanpercentile(x,[1,99]); J[c]=np.clip(x,lo,hi)
J["R_stress"]=J["R"]-0.05; RET=[0.8,0.6,0.4,0.2]; PURGE=96; SEC_YR=365.25*86400
def stdz(tr,te):
    mu=np.nanmedian(tr,0); mu=np.where(np.isnan(mu),0,mu); tr=np.where(np.isnan(tr),mu,tr); te=np.where(np.isnan(te),mu,te)
    sd=tr.std(0); sd=np.where(np.isfinite(sd)&(sd>0),sd,1); return np.nan_to_num((tr-mu)/sd),np.nan_to_num((te-mu)/sd)
def logit(X,y,l2=1.,it=250,lr=.3):
    Xb=np.hstack([np.ones((len(X),1)),X]); w=np.zeros(Xb.shape[1])
    for _ in range(it): p=1/(1+np.exp(-np.clip(Xb@w,-30,30))); grd=Xb.T@(p-y)/len(y); grd[1:]+=l2*w[1:]/len(y); w-=lr*grd
    return w
def lpr(w,X): return 1/(1+np.exp(-np.clip(np.hstack([np.ones((len(X),1)),X])@w,-30,30)))
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
            Xtr,Xte=stdz(g[feats].to_numpy()[tr],g[feats].to_numpy()[te]); w=logit(Xtr,(R[tr]>0).astype(float)); str_=lpr(w,Xtr); ste=lpr(w,Xte)
            wtr=str_[R[tr]>0]
            for t in RET:
                thr=np.quantile(wtr,1-t) if len(wtr) else 0; sel=ste>=thr; pooled[t][te]=sel
                st=np.zeros(N,bool); st[te]=sel; foldE[t].append(R[st].mean() if st.sum() else np.nan)
            tested[te]=True
        wtot=(R[tested]>0).sum(); ltot=(R[tested]<=0).sum()
        for t in RET:
            s=pooled[t]&tested
            if s.sum()==0: continue
            r=R[s]; rs=Rs[s]
            front.append(dict(setup=sid,rep=rep,retention=t,sel_N=int(s.sum()),sel_exp=round(float(r.mean()),4),sel_exp_stress=round(float(rs.mean()),4),
                winners_retained=round(float((r>0).sum()/wtot),3),losers_avoided=round(float(1-(r<=0).sum()/ltot),3),drop5=round(float(np.sort(r)[:int(len(r)*0.95)].mean()),4),
                sel_per_year=round(s.sum()/yrs,1),folds_pos=sum(1 for e in foldE[t] if e>0),fold_exps=[round(e,4) for e in foldE[t]]))
FR=pd.DataFrame(front); FR.to_csv(OUT+r"\GC_OI_RETENTION_FRONTIERS.csv",index=False); FR.to_csv(OUT+r"\GC_OI_WALK_FORWARD.csv",index=False)
FR[FR.retention==0.6].pivot_table(index="setup",columns="rep",values="sel_exp").to_csv(OUT+r"\GC_OI_REPRESENTATION_COMPARISON.csv")
print("\n== FRONTIER @60% (pooled TEST) =="); print(FR[FR.retention==0.6][["setup","rep","sel_exp","winners_retained","losers_avoided","folds_pos"]].to_string(index=False))
# gates
import ast
def at(sid,rep): x=FR[(FR.setup==sid)&(FR.rep==rep)&(FR.retention==0.6)]; return x.iloc[0] if len(x) else None
def folds(x): return x.fold_exps if isinstance(x.fold_exps,list) else ast.literal_eval(str(x.fold_exps))
gate=[]
for sid in J.setup.unique():
    reps={r:at(sid,r) for r in REPS}; nonoi=max([reps["A_xau"],reps["B_price"],reps["C_volume"]],key=lambda x:x.sel_exp)
    bestoi=max([reps["D_oi"],reps["E_price_oi"],reps["F_volume_oi"],reps["G_all"]],key=lambda x:x.sel_exp)
    dOI=bestoi.sel_exp-nonoi.sel_exp; fOI=[a-b for a,b in zip(folds(bestoi),folds(nonoi))]
    info=(dOI>=0.05 and sum(1 for x in fOI if x>=0.03)>=2)
    # interaction diagnostics: does E beat B? F beat C? (OI adds over price / volume)
    gate.append(dict(setup=sid,best_nonoi=nonoi.rep,best_oi=bestoi.rep,nonoi60=nonoi.sel_exp,bestoi60=bestoi.sel_exp,dOI=round(dOI,4),GC_OI_INCREMENTAL=info,
        price_x_oi=(reps["E_price_oi"].sel_exp-reps["B_price"].sel_exp),vol_x_oi=(reps["F_volume_oi"].sel_exp-reps["C_volume"].sel_exp)))
GT=pd.DataFrame(gate); GT.to_csv(OUT+r"\GC_OI_GATES.csv",index=False)
print("\n== GATES @60% =="); print(GT.to_string(index=False))
print("\nGC_OI_INCREMENTAL_VALUE_OVERALL:", bool(GT.GC_OI_INCREMENTAL.any()))
