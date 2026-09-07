"""lvl_v2.py — LEVEL-TO-LEVEL ACCEPTANCE EXECUTION V2. ONE frozen implementation, direct follow-up to V1. Binds the EXACT V1 event
universe (LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet; asserts 102458/72103/30355). Break + acceptance + L2 UNCHANGED. The ONLY changes:
(1) NATURAL_GEOMETRY_GATE before entry: trade only if NATURAL_REWARD_RISK = |L2-entry| / |entry-L1|(floored) >= 1.00 (frozen, not mined);
(2) invalidation = ACCEPTANCE-FAILURE CLOSE (a completed M15 candle closes back through L1), exit at NEXT M15 OPEN (no same-bar hindsight);
NO distant structural stop as primary exit. Realized loss NOT forced to -1R (full tail measured). NO parameter search, NO second variant.
Writes TRADES.parquet + PROTOCOL.json (frozen+hashed before scoring). BASE 0.05 / STRESS 0.08 net, per planned-R."""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet")
# --- BIND EXACT V1 EVENT UNIVERSE (identity gate) ---
assert len(EV1)==102458, f"RAW_BREAK_EVENTS {len(EV1)}!=102458"
assert int(EV1.accepted.sum())==72103, f"ACCEPTED {int(EV1.accepted.sum())}!=72103"
assert int((~EV1.accepted).sum())==30355, f"REJECTED {int((~EV1.accepted).sum())}!=30355"
print("V1_IDENTITY_GATE = PASS (102458 / 72103 / 30355)")
# --- frozen V2 parameters ---
CLUST=0.20; BACKSTOP=96; SPREAD_B=0.05; SPREAD_S=0.08; PIP=0.10; MINRR=1.00
def floorrisk(x,a): return max(abs(x),2*SPREAD_B,0.05,0.10*(a if a>0 else 1.0))
# --- FREEZE + HASH PROTOCOL BEFORE SCORING ---
proto=dict(mandate="LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2",parent="LEVEL_TO_LEVEL_ACCEPTANCE_V1 (hash 2a9f0c09eb50be79f3a0)",timeframe="M15",
    bound_event_universe=dict(raw=102458,accepted=72103,rejected=30355),
    break_rule="UNCHANGED: completed M15 close beyond known L1",acceptance="UNCHANGED: next completed M15 bar closes on breakout side (long>=L1, short<=L1)",
    L2="UNCHANGED: nearest causally-known level in breakout direction (cluster 0.20 ATR), known before entry",target="L2 (no 2R, runner, partial, extension)",
    entry="UNCHANGED: open[break+2] if NATURAL_REWARD_RISK>=1.00",
    natural_geometry_gate="NATURAL_REWARD_RISK = |L2-entry| / PLANNED_RISK_DISTANCE >= 1.00 (frozen minimal economic condition, NOT PnL-optimized)",
    planned_risk_distance="max(|entry-L1|, 2*spread, 0.05, 0.10*ATR)",
    invalidation="ACCEPTANCE-FAILURE CLOSE: first completed M15 candle closing back through L1 (long C<L1, short C>L1); EXIT at NEXT M15 OPEN",
    realized_loss="NOT forced to -1R; full tail measured; distant structural extreme retained as DIAGNOSTIC ONLY, not a stop",
    one_trade_at_a_time=True,backstop_bars=BACKSTOP,cost_base=SPREAD_B,cost_stress=SPREAD_S,min_reward_risk=MINRR,
    no_param_search=True,no_second_variant=True,no_context_filter=True)
json.dump(proto,open(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_PROTOCOL.json","w"),indent=2)
PH=hashlib.sha256(open(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"PROTOCOL_HASH={PH}  (frozen before scoring)")
# --- geometry eligibility for ALL events with L2 (control + eligibility), hypothetical entry=O[b+2] ---
def geom(row):
    b=int(row.b); side=int(row.dir); L2=row.L2; L1=row.L1; a=row.atr; ei=b+2
    if not row.has_L2 or ei>=n: return None
    entry=O[ei]
    if (side>0 and L2<=entry) or (side<0 and L2>=entry): return None  # L2 must be beyond entry
    pr=floorrisk(entry-L1,a); rr=abs(L2-entry)/pr
    return entry,pr,rr,ei
EV1=EV1.reset_index(drop=True)
# --- V2 SIMULATION over the bound universe (row order = V1 processing order) ---
trades=[]; open_until=-1; elig_acc=0; elig_rej=0; acc_geo_reach=[]; rej_geo_reach=[]
for row in EV1.itertuples():
    g=geom(row)
    if g is None: continue
    entry,pr,rr,ei=g; side=int(row.dir); L1=row.L1; L2=row.L2; a=float(row.atr); geo_ok=rr>=MINRR
    # descriptive control: eligibility + reach among geometry-eligible accepted vs rejected (event-level reach from V1)
    if geo_ok:
        if row.accepted: elig_acc+=1; acc_geo_reach.append(bool(row.reached_L2))
        else: elig_rej+=1; rej_geo_reach.append(bool(row.reached_L2))
    if not (row.accepted and geo_ok): continue
    b=int(row.b)
    if b<=open_until: continue
    end=min(ei+BACKSTOP,n-1); R=None; exit_i=end; reason="timeout"; same_bar=False
    for k in range(ei,end+1):
        tgt=(H[k]>=L2) if side>0 else (L[k]<=L2)
        fail=(C[k]<L1) if side>0 else (C[k]>L1)          # completed close back through L1
        if tgt:                                           # resting target fills on the wick -> win takes precedence
            R=abs(L2-entry)/pr; exit_i=k; reason="target"; same_bar=bool(fail); break
        if fail:                                          # acceptance failed at close k -> exit next open
            xo=O[k+1] if k+1<n else C[k]; R=side*(xo-entry)/pr; exit_i=(k+1 if k+1<n else k); reason="accept_fail"; break
    if R is None: R=side*(C[end]-entry)/pr; exit_i=end; reason="timeout"
    net=R-SPREAD_B/pr; net_s=R-SPREAD_S/pr
    later=False                                           # §26: after exit, does L2 reach within 32 bars?
    for k in range(exit_i+1,min(exit_i+33,n)):
        if (H[k]>=L2) if side>0 else (L[k]<=L2): later=True; break
    favbi=float(max(H[ei:exit_i+1])-entry) if side>0 else float(entry-min(L[ei:exit_i+1]))
    trades.append(dict(b=b,ei=int(ei),dir=side,entry=float(entry),L1=float(L1),L2=float(L2),atr=a,planned_risk=float(pr),
        planned_risk_atr=float(pr/a) if a>0 else np.nan,natRR=float(rr),R=float(R),net_R=float(net),net_R_stress=float(net_s),
        exit_i=int(exit_i),exit_reason=reason,same_bar=bool(same_bar),later_L2=bool(later),
        L1_type=int(row.L1_type),L2_type=int(row.L2_type),dtime=int(row.dtime),year=int(row.year),fav_usd=favbi))
    open_until=exit_i
TR=pd.DataFrame(trades); TR.to_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_TRADES.parquet")
# descriptive control frame
pd.DataFrame([dict(group="accepted_geo_eligible",n=elig_acc,reach=float(np.mean(acc_geo_reach)) if acc_geo_reach else np.nan),
    dict(group="rejected_geo_eligible",n=elig_rej,reach=float(np.mean(rej_geo_reach)) if rej_geo_reach else np.nan)]).to_csv(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_CONTROL.csv",index=False)
yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400)
r=TR.net_R.to_numpy()
print(f"V2_GEOMETRY_ELIGIBLE_EVENTS(accepted)={elig_acc}  rejected_eligible={elig_rej}")
print(f"V2_INDEPENDENT_TRADES={len(TR)}  TPY={len(TR)/yrs:.0f}")
print(f"exit mix: {TR.exit_reason.value_counts().to_dict()}")
print(f"BASE={r.mean():+.4f} STRESS={TR.net_R_stress.mean():+.4f} WR={(r>0).mean():.3f} PF={r[r>0].sum()/(abs(r[r<=0].sum())+1e-9):.3f} medNatRR={np.median(TR.natRR):.2f}")
los=-r[r<=0]; print(f"realized-loss R: P90={np.percentile(los,90):.2f} P95={np.percentile(los,95):.2f} P99={np.percentile(los,99):.2f} MAX={los.max():.2f}")
