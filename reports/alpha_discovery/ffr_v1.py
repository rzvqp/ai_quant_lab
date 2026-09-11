"""ffr_v1.py — FFR SECOND-ORDER TRAP QUICK-KILL. Mechanism: BREAK -> FAILED ACCEPTANCE -> RE-ACCEPTANCE -> CONTINUATION to L2. Alpha/Research
executor: cheapest causal falsification. REUSES the FROZEN failed-acceptance universe (FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_EVENTS, itself bound to
LEVEL_TO_LEVEL_ACCEPTANCE_V1: 102458/72103/30355) — no new level discovery. All params governed/reused (re-acceptance window 8 bars = RTH retest
window; stop buffer 0.10 ATR; backstop 96; spread BASE 0.05 / STRESS 0.08; target=L2). NO grid search, NO param invention, NO lookahead. Comparator =
PRIMARY ACCEPTANCE (LEVEL_TO_LEVEL_ACCEPTANCE_V1: BASE -0.065R, PF 0.857, medRR 0.71)."""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
FA=pd.read_parquet(OUT+r"\FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_EVENTS.parquet")
fail=FA[(~FA.accepted) & FA.has_L0 & FA.L2.notna()].reset_index(drop=True)
print(f"IDENTITY: failed-acceptance events (frozen) = {len(fail)}  (bound to LEVEL_TO_LEVEL 30355 rejected; has_L0 & L2)")
WIN=8; BUF=0.10; BACKSTOP=96; SB=0.05; SS=0.08; PIP=0.10
proto=dict(mandate="FFR_SECOND_ORDER_TRAP_QUICK_KILL_V1",parent="FAILED_ACCEPTANCE_PRIOR_LEVEL_V1 (ffc5e8e0) / LEVEL_TO_LEVEL_ACCEPTANCE_V1 (2a9f0c09)",
    mechanism="BREAK -> FAILED ACCEPTANCE -> RE-ACCEPTANCE (close back on breakout side within 8 bars) -> entry next open -> target L2",
    reacceptance_window_bars=WIN,stop="trap-swing extreme (break..reaccept) -/+0.10ATR floored",target="L2 (frozen)",backstop=BACKSTOP,cost_base=SB,cost_stress=SS,
    abstain="fade_won (L0 reached first) / pre_continued (L2 first) / no_reacceptance (expiry)",comparator="PRIMARY ACCEPTANCE = LEVEL_TO_LEVEL_ACCEPTANCE_V1",
    no_grid_search=True,no_param_invention=True,causal=True)
json.dump(proto,open(OUT+r"\FFR_SECOND_ORDER_TRAP_V1_PROTOCOL.json","w"),indent=2)
PH=hashlib.sha256(open(OUT+r"\FFR_SECOND_ORDER_TRAP_V1_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"PROTOCOL_HASH={PH} (frozen before scoring)")
trades=[]; funnel={"fade_won":0,"pre_continued":0,"no_reacceptance":0,"reaccepted":0}; open_until=-1
for r in fail.itertuples():
    b=int(r.b); side=int(r.dir); L1=float(r.L1); L0=float(r.L0); L2=float(r.L2)
    reaccept=-1; stop_scan=b
    for k in range(b+2, min(b+2+WIN, n)):
        # fade wins (reversal to L0) first -> no trap
        if (L[k]<=L0) if side>0 else (H[k]>=L0): funnel["fade_won"]+=1; reaccept=-2; break
        # continuation to L2 before any re-acceptance close (subsumes crossing L1)
        if (H[k]>=L2) if side>0 else (L[k]<=L2): funnel["pre_continued"]+=1; reaccept=-3; break
        # re-acceptance: completed close back on breakout side of L1
        if (C[k]>=L1) if side>0 else (C[k]<=L1): reaccept=k; break
    if reaccept<0:
        if reaccept==-1: funnel["no_reacceptance"]+=1
        continue
    funnel["reaccepted"]+=1
    ei=reaccept+1
    if ei>=n or b<=open_until: continue
    a=ATR[reaccept] if ATR[reaccept]>0 else 1.0; entry=O[ei]
    inval=min(L[b:reaccept+1]) if side>0 else max(H[b:reaccept+1])
    stop_raw=(inval-BUF*a) if side>0 else (inval+BUF*a); risk=max(abs(entry-stop_raw),2*SB,0.05,0.10*a); stop=entry-side*risk
    if (side>0 and L2<=entry) or (side<0 and L2>=entry): continue
    rr=abs(L2-entry)/risk
    end=min(ei+BACKSTOP,n-1); R=None; exit_i=end; reason="timeout"
    for k in range(ei,end+1):
        hs=(L[k]<=stop) if side>0 else (H[k]>=stop); tg=(H[k]>=L2) if side>0 else (L[k]<=L2)
        if hs and tg: R=-1.0; exit_i=k; reason="stop"; break
        if hs: R=-1.0; exit_i=k; reason="stop"; break
        if tg: R=abs(L2-entry)/risk; exit_i=k; reason="target"; break
    if R is None: R=side*(C[end]-entry)/risk; exit_i=end; reason="timeout"
    trades.append(dict(b=b,ei=int(ei),dir=side,entry=float(entry),L1=L1,L2=L2,risk=float(risk),natRR=float(rr),
        R=float(R),net_R=float(R-SB/risk),net_R_stress=float(R-SS/risk),exit_reason=reason,L1_type=int(r.L1_type),dtime=int(r.dtime),year=int(r.year)))
    open_until=exit_i
TR=pd.DataFrame(trades); TR.to_parquet(OUT+r"\FFR_SECOND_ORDER_TRAP_V1_TRADES.parquet")
yrs=(FA.dtime.max()-FA.dtime.min())/(365.25*86400)
print(f"FUNNEL (of {len(fail)} failed): {funnel} | INDEPENDENT_TRADES={len(TR)} ({len(TR)/yrs:.0f}/yr)")
if not len(TR): print("NO TRADES"); sys.exit()
r=TR.net_R.to_numpy(); rs=TR.net_R_stress.to_numpy(); N=len(TR)
wins=r[r>0]; losses=r[r<=0]; pf=wins.sum()/(abs(losses.sum())+1e-9); eq=np.cumsum(r); dd=float((np.maximum.accumulate(eq)-eq).max())
S=np.sort(r)[::-1]; k5=max(1,int(N*0.05)); top5=float(S[:k5].sum()/(r.sum()+1e-9)) if r.sum()!=0 else np.nan
srt=TR.sort_values("dtime"); th=np.array_split(srt.net_R.to_numpy(),3); eras=[round(float(x.mean()),4) for x in th]; era_pos=sum(1 for x in th if x.mean()>0)
recent=TR[TR.year>=2025].net_R
print(f"N={N} long={int((TR.dir>0).sum())} short={int((TR.dir<0).sum())} WR={(r>0).mean():.3f}")
print(f"avg_win={wins.mean():+.3f} avg_loss={losses.mean():+.3f} realizedRR={wins.mean()/(abs(losses.mean())+1e-9):.2f} medR={np.median(r):+.3f} medNatRR={np.median(TR.natRR):.2f}")
print(f"BASE={r.mean():+.4f} STRESS={rs.mean():+.4f} PF={pf:.3f} maxDD={dd:.0f}R top5%contrib={top5:.2f}")
print(f"eras(BASE)={eras} pos={era_pos}/3 | 2025-26: n={len(recent)} exp={recent.mean() if len(recent) else float('nan'):+.4f}")
byt={1:"PDH/PDL",2:"session/Asia",3:"swing",4:"range"}
lt=TR.groupby("L1_type").agg(n=("net_R","size"),exp=("net_R","mean"),wr=("net_R",lambda x:(x>0).mean()))
print("by L1_type:"); print(lt.round(4).to_string())
byd=TR.groupby("dir").agg(n=("net_R","size"),exp=("net_R","mean")); print("by dir (long=+1/short=-1):"); print(byd.round(4).to_string())
pd.DataFrame([dict(metric="N",v=N),dict(metric="N_long",v=int((TR.dir>0).sum())),dict(metric="N_short",v=int((TR.dir<0).sum())),dict(metric="WR",v=round((r>0).mean(),3)),
    dict(metric="avg_win",v=round(float(wins.mean()),3)),dict(metric="avg_loss",v=round(float(losses.mean()),3)),dict(metric="realizedRR",v=round(float(wins.mean()/(abs(losses.mean())+1e-9)),2)),
    dict(metric="BASE",v=round(r.mean(),4)),dict(metric="STRESS",v=round(rs.mean(),4)),dict(metric="PF",v=round(pf,3)),dict(metric="maxDD",v=round(dd,1)),
    dict(metric="medR",v=round(float(np.median(r)),3)),dict(metric="top5_contrib",v=round(top5,2)),dict(metric="era1",v=eras[0]),dict(metric="era2",v=eras[1]),dict(metric="era3",v=eras[2]),
    dict(metric="recent2025_26",v=round(float(recent.mean()),4) if len(recent) else None),dict(metric="tpy",v=round(N/yrs,0))]).to_csv(OUT+r"\FFR_SECOND_ORDER_TRAP_V1_RESULTS.csv",index=False)
srt.groupby("year").agg(n=("net_R","size"),exp=("net_R","mean"),total=("net_R","sum")).to_csv(OUT+r"\FFR_SECOND_ORDER_TRAP_V1_YEARLY.csv")
lt.to_csv(OUT+r"\FFR_SECOND_ORDER_TRAP_V1_LEVEL_TYPES.csv")
# KILL evaluation
prim_base=-0.0652; prim_pf=0.857
kill=[]
if rs.mean()<=0: kill.append("STRESS<=0")
if r.mean()<=prim_base: kill.append("does_not_beat_primary_acceptance(BASE)")
if era_pos<2: kill.append("sign_unstable_<2of3_eras")
if (TR[TR.dir>0].net_R.mean()>0 and TR[TR.dir<0].net_R.mean()<=0): kill.append("only_LONG_positive")
if top5>0.60: kill.append("outlier_dominated_top5>60pct")
print(f"\nPRIMARY_ACCEPTANCE_COMPARATOR: BASE {prim_base:+.4f} PF {prim_pf}")
print(f"FFR_VERDICT = {'KILL' if kill else 'ALPHA_SURVIVOR_CANDIDATE'} | kill_flags={kill}")
