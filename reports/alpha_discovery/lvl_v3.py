"""lvl_v3.py — LEVEL-TO-LEVEL ACCEPTANCE EXECUTION V3 (bounded hybrid). FINAL frozen execution test. Combines ONLY already-frozen V1/V2
components, NO new parameter. Bind exact V1 universe (asserts 102458/72103/30355). Entry UNCHANGED (open[break+2]). HARD CATASTROPHE STOP = exact
V1 stop (min low / max high over break..acceptance +/- 0.10 ATR, governed floor) -> position-sizing denominator (1R = |entry-hard_stop|), which
REMOVES the V2 entry->L1 degeneracy. NATURAL_RR = |L2-entry|/|entry-hard_stop| >= 1.00 (frozen). TARGET = L2. SOFT exit = V2 acceptance-failure
close (completed M15 close back through L1 -> next open) as an EARLY exit, WITH the hard stop active throughout. Exit priority (causal): intrabar
hard-stop / target first (conservative stop-first on same-bar tie), then completed soft close. Also runs a V1-hard-stop-ONLY pass over the SAME
eligible population for the §14 comparison. NO param search, NO context filter, NO V4. Protocol frozen+hashed before scoring."""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet").reset_index(drop=True)
assert len(EV1)==102458 and int(EV1.accepted.sum())==72103 and int((~EV1.accepted).sum())==30355, "V1 identity gate FAIL"
print("V1_IDENTITY_GATE = PASS (102458 / 72103 / 30355)")
BUF=0.10; BACKSTOP=96; SPREAD_B=0.05; SPREAD_S=0.08; PIP=0.10; MINRR=1.00
proto=dict(mandate="LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3",parents=["V1 hash 2a9f0c09eb50be79f3a0","V2 hash 58c8280847bf794faa84"],timeframe="M15",
    bound_event_universe=dict(raw=102458,accepted=72103,rejected=30355),break_rule="UNCHANGED (V1)",acceptance="UNCHANGED (V1)",L2="UNCHANGED (V1)",entry="UNCHANGED: open[break+2]",
    hard_catastrophe_stop="EXACT V1 stop: long min(low[break..acceptance])-0.10ATR / short max(high)+0.10ATR, governed floor max(struct,2*spread,0.05,0.10ATR)",
    position_sizing="1R = |entry - hard_stop| (bounded); REMOVES V2 entry->L1 degeneracy",
    natural_rr_gate="|L2-entry| / |entry-hard_stop| >= 1.00 (frozen, not mined)",target="L2 (no 2R/runner/partial/extension)",
    soft_exit="V2 acceptance-failure close (completed M15 close back through L1) -> exit NEXT open; EARLY exit, hard stop active throughout",
    exit_priority="intrabar hard_stop/target first (conservative stop-first on same-bar tie), then completed soft close; no future info",
    one_trade_at_a_time=True,backstop_bars=BACKSTOP,cost_base=SPREAD_B,cost_stress=SPREAD_S,min_reward_risk=MINRR,no_param_search=True,no_context_filter=True,final_iteration_no_v4=True)
json.dump(proto,open(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_PROTOCOL.json","w"),indent=2)
PH=hashlib.sha256(open(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"PROTOCOL_HASH={PH}  (frozen before scoring)")
def setup(row):
    b=int(row.b); side=int(row.dir); L1=row.L1; L2=row.L2; a=float(row.atr) if row.atr>0 else 1.0; ei=b+2
    if not row.has_L2 or ei>=n: return None
    entry=O[ei]
    inval=min(L[b:b+2]) if side>0 else max(H[b:b+2])
    stop_raw=inval-BUF*a if side>0 else inval+BUF*a
    risk=max(abs(entry-stop_raw),2*SPREAD_B,0.05,0.10*a); hard_stop=entry-side*risk
    if (side>0 and L2<=entry) or (side<0 and L2>=entry): return None
    rr=abs(L2-entry)/risk
    return dict(b=b,side=side,L1=L1,L2=L2,a=a,ei=ei,entry=entry,risk=risk,hard_stop=hard_stop,rr=rr,
                L1_type=int(row.L1_type),L2_type=int(row.L2_type),dtime=int(row.dtime),year=int(row.year),accepted=bool(row.accepted))
def sim(s, soft):
    side=s["side"]; entry=s["entry"]; L1=s["L1"]; L2=s["L2"]; hs_p=s["hard_stop"]; risk=s["risk"]; ei=s["ei"]
    end=min(ei+BACKSTOP,n-1); R=None; exit_i=end; reason="timeout"; amb=False
    for k in range(ei,end+1):
        hs=(L[k]<=hs_p) if side>0 else (H[k]>=hs_p); tg=(H[k]>=L2) if side>0 else (L[k]<=L2)
        if hs and tg: R=-1.0; exit_i=k; reason="hard_stop"; amb=True; break     # conservative stop-first
        if hs: R=-1.0; exit_i=k; reason="hard_stop"; break
        if tg: R=abs(L2-entry)/risk; exit_i=k; reason="target"; break
        if soft:
            fail=(C[k]<L1) if side>0 else (C[k]>L1)
            if fail: xo=O[k+1] if k+1<n else C[k]; R=side*(xo-entry)/risk; exit_i=(k+1 if k+1<n else k); reason="soft"; break
    if R is None: R=side*(C[end]-entry)/risk; exit_i=end; reason="timeout"
    return R, exit_i, reason, amb
# funnel
elig=[]; rr_lt1=0
for row in EV1.itertuples():
    s=setup(row)
    if s is None: continue
    if not s["accepted"]: continue
    if s["rr"]>=MINRR: elig.append(s)
    else: rr_lt1+=1
RR_GE1=len(elig)
# V3 pass (hard+soft) and V1E pass (hard only), each one-at-a-time
def run(soft):
    tr=[]; open_until=-1
    for s in elig:
        if s["b"]<=open_until: continue
        R,exit_i,reason,amb=sim(s,soft)
        net=R-SPREAD_B/s["risk"]; net_s=R-SPREAD_S/s["risk"]
        later={};
        if net<=0:
            for w in (4,8,16,32):
                hit=False
                for k in range(exit_i+1,min(exit_i+1+w,n)):
                    if (H[k]>=s["L2"]) if s["side"]>0 else (L[k]<=s["L2"]): hit=True; break
                later[w]=hit
        favbi=float(max(H[s["ei"]:exit_i+1])-s["entry"]) if s["side"]>0 else float(s["entry"]-min(L[s["ei"]:exit_i+1]))
        tr.append(dict(b=s["b"],ei=s["ei"],dir=s["side"],entry=s["entry"],L1=s["L1"],L2=s["L2"],hard_stop=s["hard_stop"],risk=s["risk"],
            natRR=s["rr"],R=R,net_R=net,net_R_stress=net_s,exit_i=exit_i,exit_reason=reason,ambiguous=amb,
            later4=later.get(4,False),later8=later.get(8,False),later16=later.get(16,False),later32=later.get(32,False),
            L1_type=s["L1_type"],L2_type=s["L2_type"],dtime=s["dtime"],year=s["year"],fav_usd=favbi))
        open_until=exit_i
    return pd.DataFrame(tr)
TR=run(True); V1E=run(False)
TR.to_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V3_TRADES.parquet")
yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400)
r=TR.net_R.to_numpy()
print(f"FUNNEL: accepted=72103 RR<1_rejected={rr_lt1} RR>=1_eligible={RR_GE1} | V3_trades={len(TR)} ({len(TR)/yrs:.0f}/yr)  V1E_trades={len(V1E)}")
print(f"natRR: med={np.median(TR.natRR):.2f} P25={np.percentile(TR.natRR,25):.2f} P75={np.percentile(TR.natRR,75):.2f} P90={np.percentile(TR.natRR,90):.2f}")
print(f"exit mix V3: {TR.exit_reason.value_counts().to_dict()}")
print(f"BASE={r.mean():+.4f} STRESS={TR.net_R_stress.mean():+.4f} WR={(r>0).mean():.3f} PF={r[r>0].sum()/(abs(r[r<=0].sum())+1e-9):.3f}")
los=-r[r<=0]; print(f"realized-loss R: P95={np.percentile(los,95):.2f} P99={np.percentile(los,99):.2f} MAX={los.max():.2f}")
# save V1E summary for §14
V1E.to_parquet(OUT+r"\_lvl_v3_v1e.parquet")
print(f"§14 avg_loss V1E={V1E.net_R[V1E.net_R<=0].mean():+.3f} vs V3={r[r<=0].mean():+.3f}")
