"""m5_profileB.py — the economic-profile directive's actual proposal: TIGHT M5 structural stop + LARGE fixed target (70-80 pip = $7-8),
HTF-aligned, profile-B (low WR / high RR). Tests whether the large target rescues M5-entry where rr2/rr3 failed. Real cost STRESS 0.24. + null."""
import sys, numpy as np, pandas as pd
from numpy.random import default_rng
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import m5_panel
P=m5_panel.build(); O=P["o"];H=P["h"];L=P["l"];C=P["c"];ATR=P["atr"];T=P["t"];n=P["n"];yr=P["yr"];sess=P["sess"];bis=P["bis"]
h4t=P["h4t"];d1t=P["d1t"];orh=P["orh"];orl=P["orl"];rmax20=P["rmax20"];rmin20=P["rmin20"];pdh=P["pdh"];pdl=P["pdl"]
month=pd.to_datetime(T,unit="s",utc=True).to_period("M").astype(str).to_numpy()
h4up=(h4t==1);h4dn=(h4t==0);d1up=(d1t==1);d1dn=(d1t==0); insess=(sess=="london")|(sess=="ny")
def xup(lvl):
    o=np.zeros(n,bool)
    for i in range(1,n):
        if np.isfinite(lvl[i]) and C[i-1]<=lvl[i]<C[i]: o[i]=True
    return o
def xdn(lvl):
    o=np.zeros(n,bool)
    for i in range(1,n):
        if np.isfinite(lvl[i]) and C[i-1]>=lvl[i]>C[i]: o[i]=True
    return o
def sim_fixed(el,es,stop_atr,target_usd,cost):
    sig=np.where(el,1,np.where(es,-1,0)); tr=[]; ou=-1
    for i in range(60,n-2):
        s=sig[i]
        if s==0 or i<=ou: continue
        a=ATR[i]
        if not (a>0): continue
        ei=i+1; entry=O[ei]; risk=max(stop_atr*a,2*cost,0.05); stop=entry-s*risk; tgt=entry+s*target_usd
        end=min(ei+288,n-1); R=None; xi=end   # 288 M5 = 24h horizon for a big target
        for k in range(ei,end+1):
            hs=(L[k]<=stop) if s>0 else (H[k]>=stop); ht=(H[k]>=tgt) if s>0 else (L[k]<=tgt)
            if hs and ht: R=-1.0;xi=k;break
            if hs: R=-1.0;xi=k;break
            if ht: R=target_usd/risk;xi=k;break
        if R is None: R=s*(C[end]-entry)/risk
        tr.append((i,s,R-cost/risk,risk)); ou=xi
    return pd.DataFrame(tr,columns=["i","dir","net","risk"]) if tr else None
def mnull(tr,cost,tgt_usd,reps=200,seed=7):
    if tr is None or len(tr)<120: return None
    real=float(tr.net.mean()); ii=tr.i.to_numpy(); dr=tr.dir.to_numpy(); rk=tr.risk.to_numpy()
    mb={}
    for i in range(60,n-300): mb.setdefault(month[i],[]).append(i)
    rng=default_rng(seed); nm=[]
    for _ in range(reps):
        rs=[]
        for a in range(len(ii)):
            cand=mb.get(month[ii[a]])
            if not cand: continue
            j=int(rng.choice(cand)); s=int(dr[a]); risk=rk[a]; ei=j+1
            if ei>=n-1: continue
            entry=O[ei]; stop=entry-s*risk; tgt=entry+s*tgt_usd; end=min(ei+288,n-1); R=None
            for k in range(ei,end+1):
                hs=(L[k]<=stop) if s>0 else (H[k]>=stop); ht=(H[k]>=tgt) if s>0 else (L[k]<=tgt)
                if hs and ht: R=-1.0;break
                if hs: R=-1.0;break
                if ht: R=tgt_usd/risk;break
            if R is None: R=s*(C[end]-entry)/risk
            rs.append(R-cost/risk)
        if rs: nm.append(float(np.mean(rs)))
    nm=np.array(nm); return dict(real=round(real,4),null=round(float(nm.mean()),4),excess=round(real-float(nm.mean()),4),capt=round(100*float(nm.mean())/(real+1e-9),0),p=round(float((nm>=real).mean()),4))
fams={
 "ORB_h4d1": (insess&(bis>=12)&(bis<=48)&xup(orh)&h4up&d1up, insess&(bis>=12)&(bis<=48)&xdn(orl)&h4dn&d1dn),
 "pdh_h4d1": (xup(pdh)&h4up&d1up, xdn(pdl)&h4dn&d1dn),
 "don20_h4d1": (xup(rmax20)&h4up&d1up, xdn(rmin20)&h4dn&d1dn),
}
print("profile-B: tight M5 stop (0.5 ATR) + fixed target, HTF-aligned, STRESS 0.24 cost")
for tgt in (7.0,):   # 70 pip
    for st in (0.5,):
        for name,(el,es) in fams.items():
            tr=sim_fixed(el,es,st,tgt,0.12)
            if tr is None or len(tr)<120: print(f"{name} tgt${tgt} stop{st}ATR: thin"); continue
            rs=tr.net.to_numpy(); y=yr[tr.i.to_numpy()]; pf=rs[rs>0].sum()/(abs(rs[rs<=0].sum())+1e-9)
            m=mnull(tr,0.12,tgt,reps=150)
            v="EDGE" if (m and m['p']<0.05 and m['excess']>0 and rs.mean()>0) else "no-edge"
            print(f"{name} tgt${tgt} stop{st}ATR: N={len(tr)} WR={(rs>0).mean():.3f} STRESS={rs.mean():+.4f} PF={pf:.2f} | null_capt={m['capt'] if m else '?'}% p={m['p'] if m else '?'} -> {v}")
