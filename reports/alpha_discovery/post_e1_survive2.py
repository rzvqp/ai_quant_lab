"""Phase 2: small interpretable P2 model (<=8 feat) + simple <=3-condition rule for CLEAN_REVERSAL among
UNDECIDED-at-P2, DISC->CONF + temporal + remaining distance. Decide READY / WEAK / NONE. NO execution."""
import sys, os, numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import post_e1_survive as PS
recs=PS.recs; feats_at=PS.feats_at; auc=PS.auc
K=2  # landmark P2 (10 min after E1; ~25p remaining; best timeliness/discrimination balance)

# undecided-at-P2 population
und=[r for r in recs if len(r["idx"])>=K and r.get(f"res{K}")=="undecided"]
for r in und:
    F,res,cn,rm=feats_at(r["e"],r["idx"],K); r["F"]=F; r["consumed"]=cn; r["remaining"]=rm
D=[r for r in und if r["split"]=="DISC"]; C=[r for r in und if r["split"]=="CONF"]
baseD=np.mean([r["label"] for r in D]); baseC=np.mean([r["label"] for r in C])
print(f"UNDECIDED-at-P2: n={len(und)} (DISC {len(D)} base_clean={baseD:.3f} | CONF {len(C)} base_clean={baseC:.3f})")
print(f"  median remaining to mid: DISC {np.median([r['remaining'] for r in D]):.1f}p CONF {np.median([r['remaining'] for r in C]):.1f}p")

MF=["net_prog","dist_to_sweep","downside_prog","ratio_dn_up","last_bear_body","consec_lower_close","dist_to_e1hi","failed_extend"]
Xd=np.array([[r["F"][f] for f in MF] for r in D]); yd=np.array([r["label"] for r in D],float)
Xc=np.array([[r["F"][f] for f in MF] for r in C]); yc=np.array([r["label"] for r in C],float)
mu=Xd.mean(0); sd=Xd.std(0)+1e-9
def fit(X,y,l2=3.0,it=50):
    X1=np.column_stack([np.ones(len(X)),X]);w=np.zeros(X1.shape[1]);R=l2*np.eye(X1.shape[1]);R[0,0]=0
    for _ in range(it):
        p=1/(1+np.exp(-np.clip(X1@w,-30,30)));W=np.clip(p*(1-p),1e-6,None)
        try:s=np.linalg.solve(X1.T@(X1*W[:,None])+R,X1.T@(p-y)+R@w)
        except:break
        w-=s
        if np.max(np.abs(s))<1e-7:break
    return w
def pred(w,X):return 1/(1+np.exp(-np.clip(np.column_stack([np.ones(len(X)),X])@w,-30,30)))
w=fit((Xd-mu)/sd,yd); pd_=pred(w,(Xd-mu)/sd); pc_=pred(w,(Xc-mu)/sd)
print(f"\n=== P2 MODEL (8 feat, frozen DISC): DISC AUC={auc(yd,pd_):.3f} | CONF AUC={auc(yc,pc_):.3f} ===")
print("  top |coef|:", {MF[j]:round(w[1+j],2) for j in np.argsort(-np.abs(w[1:]))[:4]})
# high-confidence clean bucket (frozen DISC top-40% prob)
thr=np.quantile(pd_,0.6); mC=pc_>=thr
if mC.sum()>=5:
    print(f"  high-conf clean (p>=DISC-q0.6={thr:.2f}): CONF n={mC.sum()} P(clean)={yc[mC].mean():.3f} (base {baseC:.3f}) medRemain={np.median([C[i]['remaining'] for i in range(len(C)) if mC[i]]):.1f}p")

# ---- simple <=3-condition rule ----
print("\n=== SIMPLE RULE (<=3 conditions) on UNDECIDED-at-P2 ===")
def rule_eval(cond,name):
    for tag,grp,base in (("DISC",D,baseD),("CONF",C,baseC)):
        sel=[r for r in grp if cond(r["F"])]
        if not sel: print(f"  {name:42} {tag}: n0"); continue
        pcl=np.mean([r["label"] for r in sel]); rem=np.median([r["remaining"] for r in sel])
        print(f"  {name:42} {tag}: n{len(sel):2d} P(clean)={pcl:.3f} (base {base:.3f}, lift {pcl-base:+.3f}) medRemain={rem:.1f}p")
medDS=np.median([r["F"]["dist_to_sweep"] for r in D])
rule_eval(lambda F: F["net_prog"]>0 and F["last_bear_body"]>0, "R1: net downside>0 AND bearish P2 body")
rule_eval(lambda F: F["net_prog"]>0 and F["dist_to_sweep"]>=medDS, f"R2: net downside>0 AND dist_to_sweep>={medDS:.0f}p")
rule_eval(lambda F: F["net_prog"]>0, "R3: net downside progress > 0")

# ---- temporal (undecided-at-P2, model high-conf) ----
print("\n=== TEMPORAL (P(clean) by year; undecided-at-P2) ===")
allp=pred(w,(np.array([[r["F"][f] for f in MF] for r in und])-mu)/sd)
yrs=np.array([r["yr"] for r in und]); ylab=np.array([r["label"] for r in und])
for y in (2021,2022,2023):
    m=yrs==y
    if m.sum()>=6:
        hc=m&(allp>=thr)
        print(f"  {y}: undecided n={m.sum()} base_clean={ylab[m].mean():.3f} | high-conf n={hc.sum()} P(clean)={ylab[hc].mean() if hc.sum() else float('nan'):.3f}")

# ---- landmark comparison: does P1 already work? is P3 needed? ----
print("\n=== LANDMARK DISC/CONF AUC of P2-frozen feature set, re-evaluated at P1/P3 (undecided-at-that-Pk) ===")
for k in (1,2,3):
    u=[r for r in recs if len(r["idx"])>=k and r.get(f"res{k}")=="undecided"]
    for r in u: r["Fk"]=feats_at(r["e"],r["idx"],k)[0]
    d=[r for r in u if r["split"]=="DISC"]; c=[r for r in u if r["split"]=="CONF"]
    Xdk=np.array([[r["Fk"][f] for f in MF] for r in d]); Xck=np.array([[r["Fk"][f] for f in MF] for r in c])
    muk=Xdk.mean(0); sdk=Xdk.std(0)+1e-9; wk=fit((Xdk-muk)/sdk,np.array([r["label"] for r in d],float))
    ad=auc([r["label"] for r in d],pred(wk,(Xdk-muk)/sdk)); ac=auc([r["label"] for r in c],pred(wk,(Xck-muk)/sdk))
    rem=np.median([r["remaining"] for r in u if r["split"]=="CONF"]) if c else float('nan')
    print(f"  P{k}: undecided n={len(u)} DISC AUC={ad:.3f} CONF AUC={ac:.3f} medRemain(CONF)={rem:.1f}p")
