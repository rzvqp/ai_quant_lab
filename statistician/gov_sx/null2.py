"""L3 refacut cu maparea riscului per tranzactie CORECTA (ei -> stop din setup-ul chiar folosit)."""
import os,sys,math,numpy as np,pandas as pd
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; sys.path.insert(0,os.path.join(AA,"code"))
import mstrat, mstrat_ext as ME
from alpha_lab import CFG
mstrat.TICK=0.01
if hasattr(ME,"TICK"): ME.TICK=0.01
def cfg_for(rt):
    c=dict(CFG); c["spread_ticks"]=rt/(2*mstrat.TICK); c["slip_ticks"]=0.0; return c
CB=cfg_for(0.05)
d=mstrat.load(); o=d['open'].values; atr=d['m_atr'].values
T=d["time"].to_numpy(); mon=(pd.to_datetime(T,unit="s",utc=True).year*12+pd.to_datetime(T,unit="s",utc=True).month).to_numpy()
SPEC={}
for N in range(1,52):
    for mod in (mstrat,ME):
        g=getattr(mod,f"s{N}_grammar",None); s=getattr(mod,f"s{N}_setups",None)
        if not(g and s): continue
        for h in g():
            if h['id'] in ("85dfa65a9ce1","047d776a1bcb","601e20753a4a"): SPEC[h['id']]=(f"S{N}",h,s)
        break
def clt(r,cl):
    n=len(r); mu=r.mean(); g=pd.DataFrame({"c":cl,"r":r}).groupby("c")["r"].agg(["sum","count"]); G=len(g)
    res=g["sum"].to_numpy()-g["count"].to_numpy()*mu
    se=math.sqrt(max((res**2).sum()/n**2*(G/max(G-1,1)),1e-18)); return mu,se,mu/se,G
print("="*116); print("  L3 (refacut) — NULL POTRIVIT LONG, risc mapat corect per tranzactie"); print("="*116)
rng=np.random.default_rng(11); B=400
for hid,(fam,h,sfn) in SPEC.items():
    su=sfn(d,h)
    ei2stop={}
    for s in su:
        ei2stop.setdefault(s['ei'], s['stop'])
    dup=len(su)-len(ei2stop)
    real=mstrat.simulate(d,su,CB); ei=real.ei.to_numpy(); rr=real.R.to_numpy()
    risks=np.array([max(abs(o[e]-ei2stop[e]), max(2*CB['spread_ticks']*mstrat.TICK,5*mstrat.TICK,0.10*atr[e-1])) for e in ei])
    mu,se,t,G=clt(rr,mon[ei])
    act=np.unique(mon[ei]); pool={m:np.where(mon==m)[0] for m in act}
    nulls=[]; nn=[]
    for b in range(B):
        syn=[]
        for e,rk in zip(ei,risks):
            cand=pool[mon[e]]; bb=int(rng.choice(cand))
            if bb+1>=len(d)-1 or bb<1: continue
            syn.append(dict(si=bb,ei=bb+1,dir=1,stop=o[bb+1]-rk,exit_kind="rr",exit_param=3.0))
        tn=mstrat.simulate(d,syn,CB)
        if len(tn)>=50: nulls.append(float(tn.R.mean())); nn.append(len(tn))
    nulls=np.array(nulls)
    print(f"\n  {fam:4} {hid}  (setup-uri cu ei duplicat: {dup})")
    print(f"    risc median folosit in null = {np.median(risks):.3f} USD ({np.median(risks)/0.10:.0f} pipi); N real={len(rr)}, N null median={int(np.median(nn))}")
    print(f"    REAL  mean={mu:+.4f}  t_clust={t:+.2f} ({G} luni)")
    print(f"    NULL  mean={nulls.mean():+.4f}  sd={nulls.std():.4f}  [p5 {np.quantile(nulls,.05):+.4f}, p95 {np.quantile(nulls,.95):+.4f}]")
    print(f"    p empiric P(null>=real) = {(nulls>=mu).mean():.4f}   EXCES peste null = {mu-nulls.mean():+.4f} R")
