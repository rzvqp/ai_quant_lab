"""cts_v3b.py — CTS V3B TRANSPORT TEST: apply the FROZEN V3 event-relational architecture UNCHANGED (verbatim parser, theta=2.5, window=48,
event grammar, n-gram model, walk-forward, controls, thresholds) to the other two CTS V2 setups (SETUP_1 liquidity-sweep, SETUP_3 auction-value).
NO redesign / NO theta recalibration / NO model change / NO threshold change. Writes CTS_V3B_* artifacts (does not overwrite V3). Reports
parser diagnostics, the retention frontier, controls, incremental-value verdicts, market-reasoning correlations, and the cross-setup summary.
"""
import os, sys, numpy as np, pandas as pd
from collections import defaultdict
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, OUT); import mstrat as MS
d=MS.load(); C=d["close"].to_numpy(float); Hh=d["high"].to_numpy(float); Ll=d["low"].to_numpy(float); O=d["open"].to_numpy(float)
Vv=d["volume"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); vbase=pd.Series(Vv).rolling(50).mean().shift(1).to_numpy()
rmax20=d["rmax20"].to_numpy(float); rmin20=d["rmin20"].to_numpy(float)
WIN=48; THETA=2.5; NEAR=0.35; PURGE=96; RET=[0.8,0.6,0.4,0.2]; COST=0.419; MINSUP=25; SEC_YR=365.25*86400
# ---------- FROZEN V3 PARSER (verbatim) ----------
def zigzag(hi,lo,cl,atr,theta):
    n=len(hi); th=theta*atr; piv=[0]; mode=0; hp=hi[0]; hpi=0; lp=lo[0]; lpi=0
    for j in range(1,n):
        if mode>=0:
            if hi[j]>hp: hp=hi[j]; hpi=j
            if hp-lo[j]>=th: piv.append(hpi); mode=-1; lp=lo[j]; lpi=j
        if mode<=0:
            if lo[j]<lp: lp=lo[j]; lpi=j
            if hi[j]-lp>=th: piv.append(lpi); mode=1; hp=hi[j]; hpi=j
    piv.append(n-1); piv=sorted(set(piv))
    return [(piv[k],piv[k+1], int(np.sign(cl[piv[k+1]]-cl[piv[k]])) or 1) for k in range(len(piv)-1) if piv[k+1]>piv[k]]
def build_events(T):
    rows=[]
    for i,r in T.iterrows():
        s=int(r.si)
        if s<WIN or not (ATR[s]>0): continue
        a=ATR[s]; ref=r.reference; dr=int(r.dir); seg=slice(s-WIN+1,s+1)
        hi=Hh[seg]; lo=Ll[seg]; cl=C[seg]; vv=Vv[seg]; vb=vbase[seg]; base=s-WIN+1
        legs=zigzag(hi,lo,cl,a,THETA); evs=[]
        for (la,lb,ld) in legs:
            p0=cl[la]; p1=cl[lb]; dur=lb-la; d0=abs(p0-ref)/a; d1=abs(p1-ref)/a; toward=d0-d1
            prog=abs(p1-p0)/a; path=np.abs(np.diff(cl[la:lb+1])).sum()/a; eff=prog/(path+1e-9)
            vr=vv[la:lb+1].mean()/(np.nanmean(vb[la:lb+1])+1e-9); gi=base+lb; broke=int(C[gi]>rmax20[gi-1])-int(C[gi]<rmin20[gi-1])
            etype="ATTACK" if toward>0 else "PULLBACK"
            evs.append(dict(type=etype,prog=float(prog),dur=int(dur),eff=float(eff),vr=float(vr),broke=int(broke),d0=float(d0),d1=float(d1)))
        ats=[e for e in evs if e["type"]=="ATTACK"]; pbs=[e for e in evs if e["type"]=="PULLBACK"]
        def pr(xs,key): return (xs[-1][key]/(xs[-2][key]+1e-9)) if len(xs)>=2 else 1.0
        adverse=sum(1 for e in evs if e["broke"]==-dr); favorable=sum(1 for e in evs if e["broke"]==dr)
        dref_path=(cl-ref)/a; touches=int(np.sum(np.abs(dref_path)<NEAR)); time_near=int(np.sum(np.abs(dref_path)<0.5))
        closes_through=int(np.sum(np.sign(dref_path)!=np.sign(dref_path[0]))); pen=float(np.min(dref_path*dr))
        atk_vol=np.mean([e["vr"] for e in ats]) if ats else 0.0; pb_vol=np.mean([e["vr"] for e in pbs]) if pbs else 0.0
        ppv_atk=np.mean([e["prog"]/(e["vr"]+1e-9) for e in ats]) if ats else 0.0
        def sym(e):
            strong="S" if e["prog"]>=0.8 else "w"; vol="V" if e["vr"]>=1.1 else "v"; br=("B" if e["broke"]==dr else ("b" if e["broke"]==-dr else "n"))
            return f"{e['type'][0]}{strong}{vol}{br}"
        seq=[sym(e) for e in evs]; rels=[]
        for k in range(1,len(evs)):
            a1,a2=evs[k-1],evs[k]; rels.append("ACCEL" if a2["prog"]>a1["prog"] else "DECEL"); rels.append("MOREPART" if a2["vr"]>a1["vr"] else "LESSPART")
        net_toward=(dref_path[0]-dref_path[-1])*np.sign(dref_path[0]) if abs(dref_path[0])>abs(dref_path[-1]) else -(abs(dref_path[-1])-abs(dref_path[0]))
        rows.append(dict(trade=i,setup=r.setup,R=float(r.R),si=s,decision_time=int(r.decision_time),dir=dr,
            gE_n_attacks=len(ats),gE_n_pullbacks=len(pbs),gE_n_legs=len(evs),gE_attack_size_prog=pr(ats,"prog"),gE_pullback_size_prog=pr(pbs,"prog"),
            gE_attack_eff_prog=pr(ats,"eff"),gE_pullback_dur_prog=pr(pbs,"dur"),gE_attack_vol_prog=pr(ats,"vr"),
            gE_pullback_shrink=(pbs[-1]["prog"]/(pbs[0]["prog"]+1e-9) if len(pbs)>=2 else 1.0),gE_atk_pb_vol_ratio=(atk_vol/(pb_vol+1e-9)),
            gE_atk_pb_prog_ratio=(np.mean([e["prog"] for e in ats] or [0])/(np.mean([e["prog"] for e in pbs] or [1])+1e-9)),
            gE_adverse_breaks=adverse,gE_favorable_breaks=favorable,gE_struct_net=favorable-adverse,gE_touch_count=touches,gE_time_near=time_near,
            gE_closes_through=closes_through,gE_penetration=pen,gE_atk_vol=atk_vol,gE_pb_vol=pb_vol,gE_ppv_attack=ppv_atk,
            gE_dist_compress=(abs(dref_path[0])-abs(dref_path[-1])),gE_last_attack_strong=float(ats[-1]["prog"]>=0.8 if ats else 0),
            gE_last_event_toward=float(evs[-1]["type"]=="ATTACK" if evs else 0),seq="|".join(seq),relseq="|".join(rels),n_ev=len(evs)))
    return pd.DataFrame(rows)
# ---------- FROZEN V3 model + walk-forward (verbatim) ----------
def stdz(tr,te):
    mu=np.nanmedian(tr,0); mu=np.where(np.isnan(mu),0,mu); tr=np.where(np.isnan(tr),mu,tr); te=np.where(np.isnan(te),mu,te)
    sd=tr.std(0); sd=np.where(np.isfinite(sd)&(sd>0),sd,1); return np.nan_to_num((tr-mu)/sd),np.nan_to_num((te-mu)/sd)
def logit(X,y,l2=1.,it=250,lr=.3):
    Xb=np.hstack([np.ones((len(X),1)),X]); w=np.zeros(Xb.shape[1])
    for _ in range(it): p=1/(1+np.exp(-np.clip(Xb@w,-30,30))); g=Xb.T@(p-y)/len(y); g[1:]+=l2*w[1:]/len(y); w-=lr*g
    return w
def lp(w,X): return 1/(1+np.exp(-np.clip(np.hstack([np.ones((len(X),1)),X])@w,-30,30)))
def toks_of(seq,relseq,ev_over=None,rl_over=None):
    ev=(ev_over if ev_over is not None else (seq.split("|") if seq else [])); rl=(rl_over if rl_over is not None else (relseq.split("|") if relseq else [])); out=[]
    for i,e in enumerate(ev):
        out.append(e)
        if 2*i+1<len(rl): out.append("R:"+rl[2*i]+rl[2*i+1])
    return out

def run_setup(sid, Araw, EL):
    M=EL.merge(Araw,on="si",how="left").reset_index(drop=True)
    Afeat=[c for c in Araw.columns if c!="si"]; Bfeat=[c for c in EL.columns if c.startswith("gE_")]
    for c in Afeat+Bfeat:
        x=M[c].to_numpy(float).copy(); x[~np.isfinite(x)]=np.nan
        lo,hi=np.nanpercentile(x,[1,99]); M[c]=np.clip(x,lo,hi)
    N=len(M); R=M["R"].to_numpy(); si=M["si"].to_numpy()
    stopd=np.abs(M["gB_stop_dist_atr"].to_numpy()) if "gB_stop_dist_atr" in M else np.ones(N)
    Rs=R-COST/np.maximum(stopd*1.0,1e-6)
    days=M["decision_time"].to_numpy()//86400; ud=np.unique(days); cuts=[ud[int(len(ud)*k/4)] for k in range(1,4)]; blk=np.digitize(days,cuts)
    FOLDS=[([0],1),([0,1],2),([0,1,2],3)]; yrs=(M.decision_time.max()-M.decision_time.min())/SEC_YR
    EVs=[(s.split("|") if isinstance(s,str) and s else []) for s in M.seq]; RLs=[(s.split("|") if isinstance(s,str) and s else []) for s in M.relseq]
    def grams_of(k,od=False,rd=False,rng=None):
        ev=EVs[k]; rl=RLs[k]
        if od and ev: ev=ev[:]; rng.shuffle(ev)
        if rd and rl: rl=rl[:]; rng.shuffle(rl)
        t=toks_of(None,None,ev,rl); gr=set()
        for nn in (1,2,3):
            for i in range(len(t)-nn+1): gr.add(tuple(t[i:i+nn]))
        return gr
    base_grams=[grams_of(k) for k in range(N)]
    def ngram(idx_tr,idx_te,Ry,gr_tr=None,gr_te=None):
        gt=gr_tr or [base_grams[k] for k in idx_tr]; ge=gr_te or [base_grams[k] for k in idx_te]
        tab=defaultdict(lambda:[0.,0])
        for g,k in zip(gt,idx_tr):
            for gm in g: tab[gm][0]+=Ry[k]; tab[gm][1]+=1
        T={g:s/ct for g,(s,ct) in tab.items() if ct>=MINSUP}
        sc=lambda gs:[np.mean([T[g] for g in gr if g in T]) if any(g in T for g in gr) else 0.0 for gr in gs]
        return np.array(sc(gt)),np.array(sc(ge))
    def frontier(kind,feats=None,Ry=None,od=False,rd=False,seed=0):
        Ry=R if Ry is None else Ry; pooled={t:np.zeros(N,bool) for t in RET}; tested=np.zeros(N,bool); foldE={t:[] for t in RET}
        rng=np.random.RandomState(seed)
        for trb,teb in FOLDS:
            tr=np.where(np.isin(blk,trb))[0]; te=np.where(blk==teb)[0]; te=te[si[te]>si[tr].max()+PURGE]
            if len(tr)<400 or len(te)<80: continue
            if kind=="ngram":
                if od or rd:
                    gtr=[grams_of(k,od,rd,rng) for k in tr]; gte=[grams_of(k,od,rd,rng) for k in te]; str_,ste=ngram(tr,te,Ry,gtr,gte)
                else: str_,ste=ngram(tr,te,Ry)
            else:
                Xtr,Xte=stdz(M[feats].to_numpy()[tr],M[feats].to_numpy()[te]); w=logit(Xtr,(Ry[tr]>0).astype(float)); str_=lp(w,Xtr); ste=lp(w,Xte)
            wtr=str_[Ry[tr]>0]
            for t in RET:
                thr=np.quantile(wtr,1-t) if len(wtr) else 0.; sel=ste>=thr; pooled[t][te]=sel;
                st=np.zeros(N,bool); st[te]=sel; foldE[t].append(R[st].mean() if st.sum() else np.nan)
            tested[te]=True
        rows=[]
        for t in RET:
            s=pooled[t]&tested
            if s.sum()==0: continue
            r=R[s]; rs=Rs[s]; wtot=(R[tested]>0).sum(); ltot=(R[tested]<=0).sum()
            rows.append(dict(rep=kind,retention=t,sel_N=int(s.sum()),sel_exp=float(r.mean()),sel_exp_stress=float(rs.mean()),
                PF=float((r[r>0].sum())/(abs(r[r<=0].sum())+1e-9)),WR=float((r>0).mean()),winners_retained=float((r>0).sum()/wtot),
                losers_avoided=float(1-(r<=0).sum()/ltot),drop5=float(np.sort(r)[:int(len(r)*0.95)].mean()),
                sel_per_year=round(s.sum()/yrs,1),folds_pos=sum(1 for e in foldE[t] if e>0),fold_exps=[round(e,4) for e in foldE[t]]))
        return rows
    FA=frontier("logit",feats=Afeat); FB=frontier("logit",feats=Bfeat); FC=frontier("ngram")
    for r in FA: r["rep"]="A_cts_v2_baseline"
    for r in FB: r["rep"]="B_event_aggregates"
    for r in FC: r["rep"]="C_event_relational"
    FR=pd.DataFrame(FA+FB+FC); FR["setup"]=sid
    # controls at 60% (fast: precomputed base grams for perm/random; recompute for destructions)
    realC=[r for r in FC if r["retention"]==0.6][0]["sel_exp"]
    od=[frontier("ngram",od=True,seed=s) for s in range(20)]; od60=np.nanmean([[x for x in rr if x["retention"]==0.6][0]["sel_exp"] for rr in od if [x for x in rr if x["retention"]==0.6]])
    rd=[frontier("ngram",rd=True,seed=100+s) for s in range(20)]; rd60=np.nanmean([[x for x in rr if x["retention"]==0.6][0]["sel_exp"] for rr in rd if [x for x in rr if x["retention"]==0.6]])
    def wf60(Ry):
        sel=np.zeros(N,bool); tested=np.zeros(N,bool)
        for trb,teb in FOLDS:
            tr=np.where(np.isin(blk,trb))[0]; te=np.where(blk==teb)[0]; te=te[si[te]>si[tr].max()+PURGE]
            if len(tr)<400 or len(te)<80: continue
            str_,ste=ngram(tr,te,Ry); thr=np.quantile(str_[Ry[tr]>0],0.4); sel[te]=ste>=thr; tested[te]=True
        return sel,tested
    selR,tst=wf60(R); realE=R[selR&tst].mean(); kk=int((selR&tst).sum())
    perm=[]
    for s in range(100): rp=R.copy(); np.random.RandomState(300+s).shuffle(rp); se,tt=wf60(rp); perm.append(R[se&tt].mean() if (se&tt).sum() else np.nan)
    perm=np.array(perm); rnd=[R[tst][np.random.RandomState(7+i).choice(int(tst.sum()),kk,replace=False)].mean() for i in range(100)]
    NC=pd.DataFrame([
        dict(setup=sid,control="EVENT_ORDER_DESTROY",real=round(realC,4),null_mean=round(float(od60),4),n=20,passes=bool(realC>od60+0.05)),
        dict(setup=sid,control="RELATION_DESTROY",real=round(realC,4),null_mean=round(float(rd60),4),n=20,passes=bool(realC>rd60+0.05)),
        dict(setup=sid,control="LABEL_PERM_C",real=round(float(realE),4),null_mean=round(float(np.nanmean(perm)),4),n=100,passes=bool(realE>np.nanpercentile(perm,95))),
        dict(setup=sid,control="MATCHED_RANDOM_C",real=round(float(realE),4),null_mean=round(float(np.mean(rnd)),4),n=100,passes=bool(realE>np.percentile(rnd,95)))])
    # market reasoning corr + CEO concept
    def corr(f): x=M[f].to_numpy(float); ok=np.isfinite(x); xr=x[ok]-np.nanmean(x[ok]); rr=R[ok]-R[ok].mean(); return float((xr*rr).sum()/(np.sqrt((xr**2).sum()*(rr**2).sum())+1e-9))
    Q={"attack_pressure":"gE_attack_size_prog","pullback_shrink":"gE_pullback_shrink","attack_participation":"gE_attack_vol_prog","defense_decay":"gE_atk_pb_vol_ratio",
       "repeated_touch":"gE_touch_count","penetration":"gE_penetration","time_near":"gE_time_near","adverse_break":"gE_adverse_breaks","favorable_struct":"gE_struct_net","last_attack_strong":"gE_last_attack_strong"}
    MR=pd.DataFrame([dict(setup=sid,question=k,feature=v,corr_R=round(corr(v),4),informative=abs(corr(v))>=0.03) for k,v in Q.items()])
    z=lambda a:(a-np.nanmean(a))/(np.nanstd(a)+1e-9)
    ap=z(M.gE_adverse_breaks.to_numpy())+z(-M.gE_pullback_shrink.to_numpy())+z(M.gE_attack_vol_prog.to_numpy())+z(M.gE_closes_through.to_numpy())
    ccc=float(np.corrcoef(ap,R)[0,1]); ceo="SUPPORTED" if ccc<=-0.05 else ("PARTIALLY_SUPPORTED" if ccc<=-0.02 else "NOT_SUPPORTED")
    diag=dict(setup=sid,mean_legs=round(EL.n_ev.mean(),2),median_legs=int(EL.n_ev.median()),pct_3_10=round(float(((EL.n_ev>=3)&(EL.n_ev<=10)).mean()),3),pct_single=round(float((EL.n_ev<=1).mean()),3))
    return FR,NC,MR,diag,ceo,ccc,realC,realE
# ================= run both setups =================
V2O=pd.read_parquet(OUT+r"\CTS_V2_SETUP_OBJECTS.parquet"); V2F=pd.read_parquet(OUT+r"\CTS_V2_SETUP_RELATIVE_FEATURES.parquet")
Acols=["si"]+[c for c in V2F.columns if c.startswith("gA_") or c.startswith("gB_")]
allFR=[]; allNC=[]; allMR=[]; diags=[]; reg=[]; summ={}
for sid,label in [("SETUP_1","M01_LIQUIDITY_SWEEP"),("SETUP_3","M16_AUCTION_VALUE")]:
    T=V2O[V2O.setup==sid].reset_index(drop=True); EL=build_events(T)
    Araw=V2F[V2F.setup==sid][Acols].drop_duplicates("si")
    FR,NC,MR,diag,ceo,ccc,realC,realE=run_setup(sid,Araw,EL)
    allFR.append(FR); allNC.append(NC); allMR.append(MR); diags.append(diag)
    A6=FR[(FR.rep=="A_cts_v2_baseline")&(FR.retention==0.6)].iloc[0]; B6=FR[(FR.rep=="B_event_aggregates")&(FR.retention==0.6)].iloc[0]; C6=FR[(FR.rep=="C_event_relational")&(FR.retention==0.6)].iloc[0]
    import ast
    fA=A6.fold_exps if isinstance(A6.fold_exps,list) else ast.literal_eval(str(A6.fold_exps)); fC=C6.fold_exps if isinstance(C6.fold_exps,list) else ast.literal_eval(str(C6.fold_exps))
    dCA=C6.sel_exp-A6.sel_exp; foldsCA=[c-a for c,a in zip(fC,fA)]
    eriv=bool(dCA>=0.08 and sum(1 for x in foldsCA if x>=0.05)>=2 and (C6.sel_exp-B6.sel_exp)>0)
    ncmap={r.control:r for _,r in NC.iterrows()}
    rsiv=bool(realC>ncmap["RELATION_DESTROY"].null_mean+0.05); oiv=bool(realC>ncmap["EVENT_ORDER_DESTROY"].null_mean+0.05)
    prac=FR[(FR.winners_retained>=0.6)&(FR.losers_avoided>=0.55)&(FR.sel_exp>=0.10)&(FR.sel_exp_stress>0)&(FR.folds_pos>=2)&(FR.drop5>0)]
    ncg=bool(ncmap["MATCHED_RANDOM_C"].passes or ncmap["LABEL_PERM_C"].passes)
    summ[sid]=dict(mechanism=label,trades=int(len(EL)),eriv=eriv,rsiv=rsiv,oiv=oiv,practical=(len(prac)>0 and ncg),
        base=round(float(EL.R.mean()),4),C60=round(float(C6.sel_exp),4),A60=round(float(A6.sel_exp),4),B60=round(float(B6.sel_exp),4),
        stress60=round(float(C6.sel_exp_stress),4),wret=round(float(C6.winners_retained),3),lavd=round(float(C6.losers_avoided),3),ceo=ceo,ceo_corr=round(ccc,4),dCA=round(dCA,4))
    reg.append(dict(SETUP_ID=sid,MECHANISM=label,TRADE_N=int(len(EL)),WIN_N=int((EL.R>0).sum()),LOSS_N=int((EL.R<=0).sum()),base_exp=round(float(EL.R.mean()),4)))
    print(f"{sid} {label}: legs~{diag['mean_legs']} | C60={C6.sel_exp:+.4f} A60={A6.sel_exp:+.4f} dCA={dCA:+.4f} ERIV={eriv} RSIV={rsiv} OIV={oiv} PRACTICAL={summ[sid]['practical']} CEO={ceo}({ccc:+.3f})")
pd.concat(allFR).to_csv(OUT+r"\CTS_V3B_RETENTION_FRONTIERS.csv",index=False); pd.concat(allFR).to_csv(OUT+r"\CTS_V3B_WALK_FORWARD.csv",index=False)
pd.concat(allNC).to_csv(OUT+r"\CTS_V3B_NEGATIVE_CONTROLS.csv",index=False); pd.concat(allMR).to_csv(OUT+r"\CTS_V3B_MARKET_REASONING_INTERPRETATION.csv",index=False)
pd.DataFrame(diags).to_csv(OUT+r"\CTS_V3B_PARSER_DIAGNOSTICS.csv",index=False); pd.DataFrame(reg).to_csv(OUT+r"\CTS_V3B_SETUP_REGISTER.csv",index=False)
cmp=pd.concat(allFR); cmp[cmp.retention==0.6].pivot_table(index="setup",columns="rep",values="sel_exp").to_csv(OUT+r"\CTS_V3B_REPRESENTATION_COMPARISON.csv")
# cross-setup summary incl V3 S3 (ERIV NO, RSIV NO, OIV NO, practical NO)
erc=sum(summ[s]["eriv"] for s in summ)+0; ric=sum(summ[s]["rsiv"] for s in summ)+0; oic=sum(summ[s]["oiv"] for s in summ)+0; pec=sum(summ[s]["practical"] for s in summ)+0
cls="EVENT_RELATIONAL_ARCHITECTURE_SUPPORTED" if (erc>=2 and pec>=1) else ("EVENT_RELATIONAL_INFORMATION_SETUP_SPECIFIC" if erc==1 else "EVENT_RELATIONAL_ARCHITECTURE_NOT_SUPPORTED_ON_CTS3")
CS=pd.DataFrame([dict(metric="EVENT_RELATIONAL_SUCCESS_COUNT",value=f"{erc}/3"),dict(metric="RELATION_INCREMENTAL_COUNT",value=f"{ric}/3"),
    dict(metric="ORDER_INCREMENTAL_COUNT",value=f"{oic}/3"),dict(metric="PRACTICAL_EVENT_EDGE_COUNT",value=f"{pec}/3"),dict(metric="FINAL_ARCHITECTURE_CLASSIFICATION",value=cls)])
CS.to_csv(OUT+r"\CTS_V3B_CROSS_SETUP_SUMMARY.csv",index=False)
print("\n== CROSS-SETUP (incl V3 S3) =="); print(CS.to_string(index=False))
import json; json.dump(summ,open(OUT+r"\_cts_v3b_summary.json","w"),indent=2)
