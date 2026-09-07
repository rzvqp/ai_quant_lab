"""gc_cot_v1.py — CFTC COT POSITIONING CONTEXT V1. Build 5 frozen COT families (C1 level, C2 change, C3 extreme, C4 cross-participant
disagreement, C5 price x positioning) from the weekly COMEX-Gold Disaggregated Futures-Only COT, point-in-time (each report usable only after
its Friday public release; XAU trade uses the most recent released report). Join to the 3 frozen CTS setups (reusing GC price+volume+OI features).
Seven representations A..G isolate whether COT adds value beyond the null GC channels. Same L2-logistic, walk-forward, retention frontier. Weekly
windows 1/2/4/8 only. Freezes inventory+protocol (+hash). NO daily interpolation (latest released report carried as current state; age recorded).
"""
import os, json, hashlib, numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
C=pd.read_parquet(OUT+r"\CFTC_COT_GOLD.parquet").sort_values("release_unix").reset_index(drop=True)
oi=C.oi.to_numpy(float)
mm_net=(C.mm_l-C.mm_s).to_numpy(); pm_net=(C.pm_l-C.pm_s).to_numpy(); sw_net=(C.sw_l-C.sw_s).to_numpy(); or_net=(C.or_l-C.or_s).to_numpy()
spec_net=mm_net+or_net; comm_net=pm_net+sw_net; ser=pd.Series
def pct104(a): return ser(a).rolling(104).apply(lambda x:(x[:-1]<x[-1]).mean(),raw=True).to_numpy()
def zt(a,w=104): m=ser(a).rolling(w).mean().to_numpy(); s=ser(a).rolling(w).std().to_numpy(); return (a-m)/(s+1e-9)
CF={}
# C1 level (net share of OI)
CF["c1_mm_net_oi"]=mm_net/(oi+1e-9); CF["c1_pm_net_oi"]=pm_net/(oi+1e-9); CF["c1_sw_net_oi"]=sw_net/(oi+1e-9); CF["c1_or_net_oi"]=or_net/(oi+1e-9)
CF["c1_mm_long_oi"]=C.mm_l.to_numpy()/(oi+1e-9); CF["c1_mm_short_oi"]=C.mm_s.to_numpy()/(oi+1e-9)
# C2 change (weekly windows 1/2/4/8)
for w in (1,2,4,8):
    CF[f"c2_dmm_net_{w}"]=(mm_net-np.roll(mm_net,w))/(oi+1e-9); CF[f"c2_dpm_net_{w}"]=(pm_net-np.roll(pm_net,w))/(oi+1e-9)
CF["c2_dmm_long_1"]=(C.mm_l.to_numpy()-np.roll(C.mm_l.to_numpy(),1))/(oi+1e-9); CF["c2_dmm_short_1"]=(C.mm_s.to_numpy()-np.roll(C.mm_s.to_numpy(),1))/(oi+1e-9)
# C3 extreme (causal percentile / z / dist-from-median)
CF["c3_mm_pct104"]=pct104(mm_net); CF["c3_mm_z104"]=zt(mm_net); CF["c3_pm_pct104"]=pct104(pm_net)
CF["c3_mm_dist_median"]=(mm_net-ser(mm_net).rolling(104).median().to_numpy())/(oi+1e-9)
# C4 cross-participant disagreement
CF["c4_mm_vs_pm"]=(mm_net-pm_net)/(oi+1e-9); CF["c4_spec_vs_comm"]=(spec_net-comm_net)/(oi+1e-9)
CF["c4_dmm_vs_dsw_4"]=((mm_net-np.roll(mm_net,4))-(sw_net-np.roll(sw_net,4)))/(oi+1e-9)
COT_L=list(CF.keys()); COTdf=pd.DataFrame(CF); COTdf["rel"]=C.release_unix.to_numpy()
rel=C.release_unix.to_numpy()
# ---- join to XAU trades ----
J=pd.read_parquet(OUT+r"\GC_OI_JOINED.parquet"); proto0=json.load(open(OUT+r"\GC_OI_PROTOCOL.json")); proto0v=json.load(open(OUT+r"\GC_REAL_VOLUME_PROTOCOL.json"))
A=[c for c in J.columns if c.startswith("gA_") or c.startswith("gB_")]; P=[c for c in proto0v["price_features"] if c in J]; Vv=[c for c in proto0v["volume_features"] if c in J]; OIf=[c for c in proto0["oi_features"] if c in J]
dt=J["decision_time"].to_numpy(); pos=np.searchsorted(rel,dt,side="right")-1; future=int((pos<0).sum())
ok=pos>=0; J=J[ok].reset_index(drop=True); pos=pos[ok]
for c in COT_L: J[c]=COTdf[c].to_numpy()[pos]
J["cot_age_days"]=(J["decision_time"].to_numpy()-rel[pos])/86400.0
# C5 price x positioning (interactions)
gcret=np.sign(J["p_gc_disp_8"].to_numpy()) if "p_gc_disp_8" in J else np.zeros(len(J))
J["c5_price_x_dmm4"]=gcret*J["c2_dmm_net_4"]; J["c5_price_x_mmextreme"]=gcret*J["c3_mm_z104"]
J["c5_xau_x_mmnet"]=(J["gB_dist_ref_atr"].to_numpy() if "gB_dist_ref_atr" in J else 0.0)*J["c1_mm_net_oi"]
COT_L=COT_L+["c5_price_x_dmm4","c5_price_x_mmextreme","c5_xau_x_mmnet"]
J.to_parquet(OUT+r"\GC_COT_JOINED.parquet")
print(f"COT causal join: XAU trades={len(J)} future_cot_used={future} | median cot_age_days={J.cot_age_days.median():.1f}")
print("matched per setup:", J.groupby("setup").size().to_dict())
inv=pd.DataFrame([dict(feature=c,family=c.split('_')[0].upper(),kind="COT") for c in COT_L]); inv.to_csv(OUT+r"\CFTC_COT_FEATURE_INVENTORY.csv",index=False)
proto=dict(mandate="CFTC_COT_CONTEXT_V1",cot_market="COMEX GOLD",cot_code="088691",cot_report="Disaggregated Futures-Only",
    cot_causality="each report usable only after Friday public release (ref Tue + 3d @20:00 UTC); most-recent-released used; no daily interpolation",
    revision_note="historical CFTC files hold current (possibly minor-revised) values; strict original-release archive unavailable -> disclosed point-in-time approximation",
    weekly_windows=[1,2,4,8],families=["C1","C2","C3","C4","C5"],cot_features=COT_L,price_features=P,volume_features=Vv,oi_features=OIf,
    representations={"A":"XAU","B":"A+price","C":"A+volume","D":"A+OI","E":"A+COT","F":"A+price+COT","G":"A+volume+OI+COT"},model="L2_logistic")
json.dump(proto,open(OUT+r"\CFTC_COT_PROTOCOL.json","w"),indent=2,default=str)
fh=hashlib.sha256(open(OUT+r"\CFTC_COT_FEATURE_INVENTORY.csv","rb").read()).hexdigest()[:20]; ph=hashlib.sha256(open(OUT+r"\CFTC_COT_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"COT features={len(COT_L)} COT_FEATURE_HASH={fh} COT_PROTOCOL_HASH={ph}")
# ---- 7 representations ----
REPS={"A_xau":A,"B_price":A+P,"C_volume":A+Vv,"D_oi":A+OIf,"E_cot":A+COT_L,"F_price_cot":A+P+COT_L,"G_vol_oi_cot":A+Vv+OIf+COT_L}
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
FR=pd.DataFrame(front); FR.to_csv(OUT+r"\CFTC_COT_RETENTION_FRONTIERS.csv",index=False); FR.to_csv(OUT+r"\CFTC_COT_WALK_FORWARD.csv",index=False)
FR[FR.retention==0.6].pivot_table(index="setup",columns="rep",values="sel_exp").to_csv(OUT+r"\CFTC_COT_REPRESENTATION_COMPARISON.csv")
print("\n== FRONTIER @60% =="); print(FR[FR.retention==0.6][["setup","rep","sel_exp","winners_retained","losers_avoided","folds_pos"]].to_string(index=False))
import ast
def at(sid,rep): x=FR[(FR.setup==sid)&(FR.rep==rep)&(FR.retention==0.6)]; return x.iloc[0] if len(x) else None
def folds(x): return x.fold_exps if isinstance(x.fold_exps,list) else ast.literal_eval(str(x.fold_exps))
gate=[]
for sid in J.setup.unique():
    reps={r:at(sid,r) for r in REPS}; nonc=max([reps["A_xau"],reps["B_price"],reps["C_volume"],reps["D_oi"]],key=lambda x:x.sel_exp)
    bestc=max([reps["E_cot"],reps["F_price_cot"],reps["G_vol_oi_cot"]],key=lambda x:x.sel_exp)
    dC=bestc.sel_exp-nonc.sel_exp; fC=[a-b for a,b in zip(folds(bestc),folds(nonc))]
    info=(dC>=0.05 and sum(1 for x in fC if x>=0.03)>=2)
    gate.append(dict(setup=sid,best_nonCOT=nonc.rep,best_COT=bestc.rep,nonc60=nonc.sel_exp,bestc60=bestc.sel_exp,dCOT=round(dC,4),COT_INCREMENTAL=info))
GT=pd.DataFrame(gate); GT.to_csv(OUT+r"\CFTC_COT_GATES.csv",index=False)
print("\n== GATES @60% =="); print(GT.to_string(index=False)); print("\nCOT_INCREMENTAL_VALUE_OVERALL:", bool(GT.COT_INCREMENTAL.any()))
