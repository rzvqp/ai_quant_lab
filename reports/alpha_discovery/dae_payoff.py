"""dae_payoff.py — §15 payoff geometry test on the info-gate survivor (B.priorday OCO continuation). Stop = opposite prior-day extreme
(risk = PDH-PDL). Target multiple in {1.0, 1.5, 2.0}x risk + time-expiry variant. Report net/WR/DEV/OOS/PRE/POST + drop-best-1%/5% + top1%.
Native M15, independent daily episodes, conservative same-bar, cost 0.419. No optimization beyond the 3 pre-declared payoffs.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import dae_scan as DS
COST=0.419; H=96

def run(M, starts, pdh, pdl, tgtmult, label, time_expiry=False):
    h=M["h"];l=M["l"];c=M["c"];n=M["n"]; rows=[]; s_used=[]
    for s,ua,da in zip(starts,pdh,pdl):
        risk=ua-da
        if risk<=0: continue
        end=min(s+H,n-1); trig=None
        for j in range(s+1,end+1):
            up=h[j]>=ua; dn=l[j]<=da
            if up and dn: trig="skip"; break
            if up: trig=(j,+1,ua); break
            if dn: trig=(j,-1,da); break
        if trig is None or trig=="skip": continue
        j,d,entry=trig; stop=da if d>0 else ua; tgt=entry+d*tgtmult*risk; res=None
        for k in range(j,end+1):
            ht=(h[k]>=tgt) if d>0 else (l[k]<=tgt); hs=(l[k]<=stop) if d>0 else (h[k]>=stop)
            if ht and hs: res=-1.0;break
            if hs: res=-1.0;break
            if ht: res=float(tgtmult);break
        if res is None: res=d*(c[end]-entry)/risk
        rows.append(res-COST/risk); s_used.append(s)
    net=np.array(rows); starts_a=np.array(s_used); yE=M["yr"][starts_a]; dev=yE<=2019; pre=yE<2021
    d1=np.sort(net)[:int(len(net)*0.99)].mean(); d5=np.sort(net)[:int(len(net)*0.95)].mean()
    top1=np.sort(net)[-max(1,len(net)//100):].sum()/net.sum() if net.sum()>0 else float('nan')
    print(f"{label:26s} N={len(net):4d} net={net.mean():+.3f} WR={(net>0).mean():.3f} DEV={net[dev].mean():+.3f} OOS={net[~dev].mean():+.3f} "
          f"PRE={net[pre].mean():+.3f} POST={net[~pre].mean():+.3f} dropBest1%={d1:+.3f} dropBest5%={d5:+.3f} top1%PnL={top1:.2f}")

def main():
    M=DS.load(); starts,pdh,pdl=DS.day_starts(M)
    pdr=pdh-pdl; ok=(pdr>0)&np.isfinite(pdr); starts,pdh,pdl=starts[ok],pdh[ok],pdl[ok]
    print("B.priorday OCO continuation — payoff geometry (stop=opposite extreme, risk=PDR):")
    for m in (1.0,1.5,2.0):
        run(M,starts,pdh,pdl,m,f"  target {m}R")

if __name__=="__main__":
    main()
