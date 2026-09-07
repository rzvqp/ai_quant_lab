"""lvl_v1.py — LEVEL-TO-LEVEL ACCEPTANCE STRATEGY V1. Frozen causal mechanism: known level L1 -> M15 close-break -> acceptance (next bar
closes on breakout side) -> entry next open -> target = next causally-known level L2 -> stop = structural invalidation (break..acceptance extreme
+/- 0.10 ATR, floored). Trade every accepted occurrence, one active trade at a time. Rejected breaks kept as control. Level classes 1-4 (prev-day
H/L, prev/curr session H/L, causal swing H/L, 20-bar range boundary); cluster 0.20 ATR; L2 = nearest cluster beyond current price. NO param mining,
NO context filter. BASE 0.05 / STRESS 0.08 net. Writes LEVELS/EVENTS/TRADES parquet + all metrics. Protocol frozen+hashed before scoring.
"""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
pdh=d["pdh"].to_numpy(float); pdl=d["pdl"].to_numpy(float); psh=d["prev_sess_high"].to_numpy(float); psl=d["prev_sess_low"].to_numpy(float)
sh=d["sess_high"].to_numpy(float); sl=d["sess_low"].to_numpy(float)
rhi=pd.Series(H).rolling(20).max().shift(1).to_numpy(); rlo=pd.Series(L).rolling(20).min().shift(1).to_numpy()
# causal swing engine (theta=1.0 ATR, frozen) -> last confirmed swing high/low as-of each bar
def swings(theta=1.0):
    swh=np.full(n,np.nan); swl=np.full(n,np.nan); mode=0; hp=H[0]; hpi=0; lp=L[0]; lpi=0; csh=np.nan; csl=np.nan
    for j in range(1,n):
        th=theta*(ATR[j] if ATR[j]>0 else 1.0)
        if mode>=0:
            if H[j]>hp: hp=H[j]; hpi=j
            if hp-L[j]>=th: csh=hp; mode=-1; lp=L[j]; lpi=j
        if mode<=0:
            if L[j]<lp: lp=L[j]; lpi=j
            if H[j]-lp>=th: csl=lp; mode=1; hp=H[j]; hpi=j
        swh[j]=csh; swl[j]=csl
    return swh,swl
SWH,SWL=swings(1.0)
CLUST=0.20; BUF=0.10; BACKSTOP=96; SPREAD_B=0.05; SPREAD_S=0.08; PIP=0.10
LTYPE={"pdh":1,"pdl":1,"psh":2,"psl":2,"sh":2,"sl":2,"SWH":3,"SWL":3,"rhi":4,"rlo":4}
def levels_at(b):
    cand=[("pdh",pdh[b]),("pdl",pdl[b]),("psh",psh[b]),("psl",psl[b]),("sh",sh[b]),("sl",sl[b]),("SWH",SWH[b]),("SWL",SWL[b]),("rhi",rhi[b]),("rlo",rlo[b])]
    cand=[(nm,p) for nm,p in cand if np.isfinite(p)]; cand.sort(key=lambda x:x[1])
    a=ATR[b] if ATR[b]>0 else 1.0; out=[]
    for nm,p in cand:
        if out and abs(p-out[-1][1])<CLUST*a: continue   # cluster: keep first (deterministic)
        out.append((nm,p))
    return out   # sorted (name,price)

def reach_before_return(b0, entry_bar, L1, L2, dr):
    """from entry_bar, does price reach L2 before closing materially back through L1? (for control + trade path)."""
    end=min(entry_bar+BACKSTOP,n-1)
    for k in range(entry_bar,end+1):
        if dr>0:
            if H[k]>=L2: return k
            if C[k]<L1-0.1*(ATR[k] if ATR[k]>0 else 1): return -1
        else:
            if L[k]<=L2: return k
            if C[k]>L1+0.1*(ATR[k] if ATR[k]>0 else 1): return -1
    return -1

events=[]; trades=[]; open_until=-1
for b in range(60,n-2):
    a=ATR[b]
    if not (a>0) or not np.isfinite(C[b-1]): continue
    levs=levels_at(b); prices=[p for _,p in levs]
    # UP break: close[b] crosses above a level that close[b-1] was at/below
    up=[(nm,p) for nm,p in levs if C[b-1]<=p<C[b]]
    dn=[(nm,p) for nm,p in levs if C[b-1]>=p>C[b]]
    for side,cr in ((+1,up),(-1,dn)):
        if not cr: continue
        L1nm,L1=(min(cr,key=lambda x:x[1]) if side>0 else max(cr,key=lambda x:x[1]))
        # L2 = nearest level beyond current price in break direction
        if side>0: above=[p for _,p in levs if p>C[b]+CLUST*a]; L2=min(above) if above else np.nan; L2nm=next((nm for nm,p in levs if p==L2),"") if above else ""
        else: below=[p for _,p in levs if p<C[b]-CLUST*a]; L2=max(below) if below else np.nan; L2nm=next((nm for nm,p in levs if p==L2),"") if below else ""
        # acceptance: next completed bar b+1 closes on breakout side of L1
        if b+2>=n: continue
        accepted = (C[b+1]>=L1) if side>0 else (C[b+1]<=L1)
        ev=dict(b=int(b),dir=int(side),L1=float(L1),L1_type=LTYPE[L1nm],L2=(float(L2) if np.isfinite(L2) else np.nan),L2_type=(LTYPE.get(L2nm,0)),
                accepted=bool(accepted),has_L2=bool(np.isfinite(L2)),dtime=int(T[b]),year=int(pd.to_datetime(T[b],unit="s",utc=True).year),atr=float(a))
        # control: does price reach L2 (measured from acceptance bar b+1)?
        if np.isfinite(L2):
            rk=reach_before_return(b, b+1, L1, L2, side); ev["reached_L2"]=bool(rk>=0); ev["bars_to_L2"]=int(rk-(b+1)) if rk>=0 else -1
        else: ev["reached_L2"]=False; ev["bars_to_L2"]=-1
        events.append(ev)
        # TRADE only accepted breaks with valid L2
        if accepted and np.isfinite(L2):
            ei=b+2
            if b<=open_until or ei>=n: continue
            entry=O[ei]
            inval=(min(L[b:b+2])) if side>0 else (max(H[b:b+2])); stop=(inval-BUF*a) if side>0 else (inval+BUF*a)
            risk=max(abs(entry-stop),2*SPREAD_B,0.05,0.10*a); stp=entry-side*risk
            # target must be beyond entry in dir
            if (L2<=entry and side>0) or (L2>=entry and side<0): continue
            end=min(ei+BACKSTOP,n-1); R=None; exit_i=end; same_bar=False; stop_hit_bar=-1
            for k in range(ei,end+1):
                ht=(H[k]>=L2) if side>0 else (L[k]<=L2); hs=(L[k]<=stp) if side>0 else (H[k]>=stp)
                if ht and hs: same_bar=True; R=-1.0; exit_i=k; stop_hit_bar=k; break
                if hs: R=-1.0; exit_i=k; stop_hit_bar=k; break
                if ht: R=(abs(L2-entry)/risk); exit_i=k; break
            if R is None: R=side*(C[end]-entry)/risk
            ltr=abs(L2-entry)/risk  # level-target-R
            # post-stop: if stopped, does L2 reach within 32 bars after?
            stop_then_L2=False
            if stop_hit_bar>=0:
                for k in range(stop_hit_bar+1,min(stop_hit_bar+32,n)):
                    if (H[k]>=L2) if side>0 else (L[k]<=L2): stop_then_L2=True; break
            net=R - (SPREAD_B/risk); net_s=R - (SPREAD_S/risk)
            favbi=float(max(H[ei:exit_i+1])-entry) if side>0 else float(entry-min(L[ei:exit_i+1]))
            trades.append(dict(b=int(b),ei=int(ei),dir=int(side),entry=float(entry),stop=float(stp),L2=float(L2),risk=float(risk),
                R=float(R),net_R=float(net),net_R_stress=float(net_s),level_target_R=float(ltr),exit_i=int(exit_i),same_bar=bool(same_bar),
                stop_hit=bool(stop_hit_bar>=0),stop_then_L2=bool(stop_then_L2),L1_type=LTYPE[L1nm],L2_type=LTYPE.get(L2nm,0),
                dtime=int(T[b]),year=int(pd.to_datetime(T[b],unit="s",utc=True).year),fav_before_inval=favbi))
            open_until=exit_i
EV=pd.DataFrame(events); TR=pd.DataFrame(trades)
EV.to_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet"); TR.to_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_TRADES.parquet")
pd.DataFrame([{"note":"levels built per-bar from LTYPE1-4, cluster 0.20 ATR"}]).to_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_LEVELS.parquet")
proto=dict(mandate="LEVEL_TO_LEVEL_ACCEPTANCE_V1",timeframe="M15",level_classes={1:"prev-day H/L",2:"session H/L",3:"causal swing H/L",4:"20-bar range boundary"},
    cluster_atr=CLUST,break_rule="M15 close beyond L1",acceptance="next completed bar closes on breakout side",entry="open[break+2]",
    stop="structural invalidation (break..acceptance extreme) +/- 0.10 ATR, floored max(struct,2*spread,0.05,0.10ATR)",target="next causal level L2 beyond price",
    swing_theta_atr=1.0,one_trade_at_a_time=True,cost_base=SPREAD_B,cost_stress=SPREAD_S,backstop_bars=BACKSTOP,no_context_filter=True,no_param_mining=True)
json.dump(proto,open(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_PROTOCOL.json","w"),indent=2)
ph=hashlib.sha256(open(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_PROTOCOL.json","rb").read()).hexdigest()[:20]
yrs=(EV.dtime.max()-EV.dtime.min())/(365.25*86400)
print(f"PROTOCOL_HASH={ph}")
print(f"RAW_BREAK_EVENTS={len(EV)} ACCEPTED={int(EV.accepted.sum())} REJECTED={int((~EV.accepted).sum())} | INDEPENDENT_TRADES={len(TR)} ({len(TR)/yrs:.1f}/yr)")
acc=EV[EV.accepted & EV.has_L2]; rej=EV[(~EV.accepted) & EV.has_L2]
ar=acc.reached_L2.mean()*100; rr=rej.reached_L2.mean()*100
print(f"ACCEPTED_BREAK_NEXT_LEVEL_RATE={ar:.1f}% REJECTED={rr:.1f}% LIFT={ar-rr:.1f}pp")
r=TR.net_R.to_numpy(); rs=TR.net_R_stress.to_numpy()
print(f"BASE_EXP={r.mean():+.4f} STRESS_EXP={rs.mean():+.4f} WR={(r>0).mean():.3f} PF={r[r>0].sum()/(abs(r[r<=0].sum())+1e-9):.3f} medR={np.median(r):+.3f}")
eq=np.cumsum(r); dd=(np.maximum.accumulate(eq)-eq).max(); print(f"maxDD={dd:.1f}R medLevelTargetR={np.median(TR.level_target_R):.2f} stop_then_L2%={100*TR[TR.stop_hit].stop_then_L2.mean() if TR.stop_hit.any() else 0:.1f}")
