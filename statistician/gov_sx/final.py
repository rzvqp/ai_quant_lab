import os,sys,math,numpy as np,pandas as pd
from statistics import NormalDist
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
ND=NormalDist()
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; sys.path.insert(0,os.path.join(AA,"code"))
R=pd.read_csv("fwer_all.csv")
print("="*112); print("  BH-FDR — sensibilitate la contaminarea cu artefacte demonstrate"); print("="*112)
art=R.family.isin(["S49","S51"])
print(f"  ipoteze totale {len(R)}; din familii cu artefact demonstrat (S49 stop=bar / S51): {int(art.sum())}")
for lbl,sub in (("toate", R), ("fara S49/S51", R[~art])):
    p=np.sort(sub.p_one.to_numpy()); m=len(p); crit=np.arange(1,m+1)/m*0.05
    k=np.where(p<=crit)[0]; thr=p[k.max()] if len(k) else 0.0
    print(f"  {lbl:14} m={m:5d}  descoperiri BH={len(k):4d}  p-prag={thr:.3e}  (t>{ND.inv_cdf(1-thr):.2f})" if thr>0 else f"  {lbl:14} m={m:5d}  0 descoperiri")
    for hid in ("85dfa65a9ce1","047d776a1bcb","601e20753a4a"):
        r=sub[sub.id==hid]
        if len(r): print(f"       {hid}: p={r.p_one.iloc[0]:.2e} -> {'TRECE' if r.p_one.iloc[0]<=thr else 'PICA'}")

print("\n"+"="*112); print("  S1 — NULL POTRIVIT LONG pe PANOUL CU CONTEXT ISTORIC (exista informatie de intrare inainte de 2023?)"); print("="*112)
import mstrat, mstrat_ext as ME, htf_context_historical as HH
from alpha_lab import CFG
mstrat.TICK=0.01
if hasattr(ME,"TICK"): ME.TICK=0.01
def cfg_for(rt):
    c=dict(CFG); c["spread_ticks"]=rt/(2*mstrat.TICK); c["slip_ticks"]=0.0; return c
CB=cfg_for(0.05)
dh=HH.load_mstrat_historical(); o=dh['open'].values; atr=dh['m_atr'].values
Th=dh["time"].to_numpy(); yrh=pd.to_datetime(Th,unit="s",utc=True).year.to_numpy()
monh=(pd.to_datetime(Th,unit="s",utc=True).year*12+pd.to_datetime(Th,unit="s",utc=True).month).to_numpy()
def clt(r,cl):
    n=len(r); mu=r.mean(); g=pd.DataFrame({"c":cl,"r":r}).groupby("c")["r"].agg(["sum","count"]); G=len(g)
    res=g["sum"].to_numpy()-g["count"].to_numpy()*mu
    se=math.sqrt(max((res**2).sum()/n**2*(G/max(G-1,1)),1e-18)); return mu,se,mu/se,G
SPEC={}
for N in range(1,52):
    for mod in (mstrat,ME):
        g=getattr(mod,f"s{N}_grammar",None); s=getattr(mod,f"s{N}_setups",None)
        if not(g and s): continue
        for h in g():
            if h['id'] in ("85dfa65a9ce1","047d776a1bcb","601e20753a4a"): SPEC[h['id']]=(f"S{N}",h,s)
        break
rng=np.random.default_rng(23); B=400
for hid,(fam,h,sfn) in SPEC.items():
    su=sfn(dh,h); e2s={}
    for s in su: e2s.setdefault(s['ei'],s['stop'])
    real=mstrat.simulate(dh,su,CB); ei=real.ei.to_numpy(); rr=real.R.to_numpy()
    risks=np.array([max(abs(o[e]-e2s[e]), max(2*CB['spread_ticks']*mstrat.TICK,5*mstrat.TICK,0.10*atr[e-1])) for e in ei])
    mu,se,t,G=clt(rr,monh[ei])
    pool={m:np.where(monh==m)[0] for m in np.unique(monh[ei])}
    nulls=[]
    for b in range(B):
        syn=[]
        for e,rk in zip(ei,risks):
            bb=int(rng.choice(pool[monh[e]]))
            if bb+1>=len(dh)-1 or bb<1: continue
            syn.append(dict(si=bb,ei=bb+1,dir=1,stop=o[bb+1]-rk,exit_kind="rr",exit_param=3.0))
        tn=mstrat.simulate(dh,syn,CB)
        if len(tn)>=50: nulls.append(float(tn.R.mean()))
    nulls=np.array(nulls)
    pre=yrh[ei]<2023
    print(f"\n  {fam:4} {hid} pe panoul istoric: N={len(rr)} (din care pre-2023: {int(pre.sum())})")
    print(f"    REAL mean={mu:+.4f} t_clust={t:+.2f} | NULL mean={nulls.mean():+.4f} sd={nulls.std():.4f}")
    print(f"    p empiric = {(nulls>=mu).mean():.4f}   EXCES = {mu-nulls.mean():+.4f} R")
    if pre.sum()>=50:
        mp,sp,tp,Gp=clt(rr[pre],monh[ei][pre])
        print(f"    DOAR pre-2023: N={int(pre.sum())} mean={mp:+.4f} t_clust={tp:+.2f}")
