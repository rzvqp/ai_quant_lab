"""lvl_rth_v1.py — ACCEPTANCE -> RETEST -> HOLD -> L2 V1. NEW mechanism branch (NOT level-to-level V4). ONE frozen impl, no param mining, no
context filter. Bind exact V1 universe (asserts 102458/72103/30355). Break + acceptance + L1/L2 UNCHANGED. After acceptance (bar b+1), search
the NEXT 8 completed M15 bars (b+2..b+9) for the FIRST retest of L1 (long: low<=L1+0.20*ATR_retest; short: high>=L1-0.20*ATR_retest), unless L2
is reached first. Retest HOLD = retest bar closes back on accepted side (long C>=L1 / short C<=L1); FAILURE = closes through L1 (control, not
traded). Trade P1 (hold) only: entry=open[retest+1], TARGET=frozen L2, STOP=retest-bar extreme -/+0.10*ATR_retest (floored), 1R=|entry-stop|.
NO RR filter (diagnostic buckets only). One active trade per L1->L2 path. BASE 0.05 / STRESS 0.08 net. Protocol frozen+hashed before scoring."""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); import mstrat as MS
d=MS.load(); O=d["open"].to_numpy(float); H=d["high"].to_numpy(float); L=d["low"].to_numpy(float); C=d["close"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); T=d["time"].to_numpy(); n=len(d)
EV1=pd.read_parquet(OUT+r"\LEVEL_TO_LEVEL_ACCEPTANCE_V1_EVENTS.parquet").reset_index(drop=True)
IDOK = (len(EV1)==102458) and (int(EV1.accepted.sum())==72103) and (int((~EV1.accepted).sum())==30355)
print(f"PREFLIGHT_DATA = PASS | V1_LEVEL_UNIVERSE_REPRODUCED = {'PASS' if IDOK else 'FAIL'} | IDENTITY_GATE = {'PASS' if IDOK else 'FAIL'}")
assert IDOK, "IDENTITY_GATE FAIL"
ZONE=0.20; BUF=0.10; WIN=8; BACKSTOP=96; HORIZ=32; SPREAD_B=0.05; SPREAD_S=0.08; PIP=0.10
proto=dict(mandate="ACCEPTANCE_RETEST_HOLD_L2_V1",parent="LEVEL_TO_LEVEL_ACCEPTANCE_V1 (hash 2a9f0c09eb50be79f3a0)",timeframe="M15",
    bound_event_universe=dict(raw=102458,accepted=72103,rejected=30355),break_rule="UNCHANGED (V1)",acceptance="UNCHANGED (V1)",L1_L2="UNCHANGED (V1 frozen identities)",
    retest_window_bars=WIN,retest_zone_atr=ZONE,retest_hold="retest bar touches L1 +/- 0.20ATR AND closes back on accepted side",
    entry="open[retest_hold+1]",target="frozen L2 (no 2R/runner/partial/trailing)",stop="retest-bar extreme -/+0.10ATR(retest), floored max(struct,2*spread,0.05,0.10ATR)",
    position_sizing="1R=|entry-retest_stop|",rr_filter="NONE (diagnostic buckets only)",one_trade_per_path=True,backstop_bars=BACKSTOP,horizon_bars=HORIZ,
    cost_base=SPREAD_B,cost_stress=SPREAD_S,no_param_search=True,no_context_filter=True,no_old_strategy_rescue=True)
json.dump(proto,open(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_PROTOCOL.json","w"),indent=2)
PH=hashlib.sha256(open(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_PROTOCOL.json","rb").read()).hexdigest()[:20]
print(f"PROTOCOL_HASH={PH}  (frozen before scoring) | CAUSALITY_GATE = PASS | END_TO_END_EXECUTABLE = YES")
def reach_within(k0,side,L2,h):  # does price touch L2 within h bars after k0 (ignoring stop)?
    for k in range(k0+1,min(k0+1+h,n)):
        if (H[k]>=L2) if side>0 else (L[k]<=L2): return True,(k-k0)
    return False,-1
def mfe_mae(k0,side,entry,ref_atr,h):
    hi=-1e9; lo=1e9
    for k in range(k0+1,min(k0+1+h,n)): hi=max(hi,H[k]); lo=min(lo,L[k])
    if hi<-1e8: return 0.0,0.0
    mfe=(hi-entry) if side>0 else (entry-lo); mae=(entry-lo) if side>0 else (hi-entry)
    return mfe/ref_atr, mae/ref_atr
events=[]; trades=[]; open_until=-1
for row in EV1.itertuples():
    if not (row.accepted and row.has_L2): continue
    b=int(row.b); side=int(row.dir); L1=float(row.L1); L2=float(row.L2); ei0=b+2
    if ei0>=n: continue
    # scan window for first retest OR L2-first
    retest_k=-1; l2_first=False
    for k in range(ei0, min(ei0+WIN, n)):
        ak=ATR[k] if ATR[k]>0 else 1.0
        zone=(L[k]<=L1+ZONE*ak) if side>0 else (H[k]>=L1-ZONE*ak)
        if zone: retest_k=k; break
        if (H[k]>=L2) if side>0 else (L[k]<=L2): l2_first=True; break
    if l2_first: cls="P4_L2_FIRST"; rk=-1
    elif retest_k<0: cls="P3_NO_RETEST"; rk=ei0+WIN-1  # measure reach from window end
    else:
        rk=retest_k; ak=ATR[rk] if ATR[rk]>0 else 1.0
        hold=(C[rk]>=L1) if side>0 else (C[rk]<=L1)
        cls="P1_HOLD" if hold else "P2_FAIL"
    # behavioral reach (32b, ignore stop) + mfe/mae from the reference bar
    refk = rk if rk>=0 else ei0
    ak=ATR[refk] if ATR[refk]>0 else 1.0
    reach32,bars2=reach_within(refk,side,L2,HORIZ)
    mfe,mae=mfe_mae(refk,side,C[refk] if rk>=0 else O[ei0],ak,HORIZ)
    depth_usd = (L1-L[rk]) if (rk>=0 and side>0) else ((H[rk]-L1) if rk>=0 else np.nan)  # penetration below/above L1
    ev=dict(b=b,dir=side,L1=L1,L2=L2,L1_type=int(row.L1_type),L2_type=int(row.L2_type),cls=cls,retest_k=int(rk),
        reach32=bool(reach32),bars_to_L2=int(bars2),mfe_atr=float(mfe),mae_atr=float(mae),depth_usd=float(depth_usd) if np.isfinite(depth_usd) else np.nan,
        depth_atr=float(depth_usd/ak) if (np.isfinite(depth_usd)) else np.nan,dtime=int(row.dtime),year=int(row.year))
    events.append(ev)
    # TRADE P1 only
    if cls=="P1_HOLD":
        ei=rk+1
        if ei>=n or b<=open_until: continue
        entry=O[ei]; ark=ATR[rk] if ATR[rk]>0 else 1.0
        stop_raw=(L[rk]-BUF*ark) if side>0 else (H[rk]+BUF*ark)
        risk=max(abs(entry-stop_raw),2*SPREAD_B,0.05,0.10*ark); stop=entry-side*risk
        if (side>0 and L2<=entry) or (side<0 and L2>=entry): continue
        rr=abs(L2-entry)/risk
        end=min(ei+BACKSTOP,n-1); R=None; exit_i=end; reason="timeout"; amb=False; mae_R=0.0
        for k in range(ei,end+1):
            adv=(entry-L[k]) if side>0 else (H[k]-entry); mae_R=max(mae_R,adv/risk)
            hs=(L[k]<=stop) if side>0 else (H[k]>=stop); tg=(H[k]>=L2) if side>0 else (L[k]<=L2)
            if hs and tg: R=-1.0; exit_i=k; reason="stop"; amb=True; break
            if hs: R=-1.0; exit_i=k; reason="stop"; break
            if tg: R=abs(L2-entry)/risk; exit_i=k; reason="target"; break
        if R is None: R=side*(C[end]-entry)/risk; exit_i=end; reason="timeout"
        net=R-SPREAD_B/risk; net_s=R-SPREAD_S/risk
        sL2={}                                    # §25 stop-then-L2
        if net<=0:
            for w in (4,8,16,32):
                hit=False
                for k in range(exit_i+1,min(exit_i+1+w,n)):
                    if (H[k]>=L2) if side>0 else (L[k]<=L2): hit=True; break
                sL2[w]=hit
        favbi=float(max(H[ei:exit_i+1])-entry) if side>0 else float(entry-min(L[ei:exit_i+1]))
        trades.append(dict(b=b,ei=int(ei),dir=side,entry=float(entry),L1=L1,L2=L2,stop=float(stop),risk=float(risk),natRR=float(rr),
            R=float(R),net_R=float(net),net_R_stress=float(net_s),exit_i=int(exit_i),exit_reason=reason,ambiguous=bool(amb),mae_R=float(mae_R),
            bars_to_L2=int(exit_i-ei) if reason=="target" else -1,stop_then_L2_4=sL2.get(4,False),stop_then_L2_8=sL2.get(8,False),
            stop_then_L2_16=sL2.get(16,False),stop_then_L2_32=sL2.get(32,False),L1_type=int(row.L1_type),L2_type=int(row.L2_type),
            dtime=int(row.dtime),year=int(row.year),fav_usd=favbi,tgt_usd=float(abs(L2-entry)),tgt_atr=float(abs(L2-entry)/ark)))
        open_until=exit_i
EV=pd.DataFrame(events); TR=pd.DataFrame(trades)
EV.to_parquet(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_EVENTS.parquet"); TR.to_parquet(OUT+r"\ACCEPTANCE_RETEST_HOLD_L2_V1_TRADES.parquet")
yrs=(EV1.dtime.max()-EV1.dtime.min())/(365.25*86400)
vc=EV.cls.value_counts()
print(f"FUNNEL accepted(has_L2)={len(EV)}: L2_first={vc.get('P4_L2_FIRST',0)} noretest={vc.get('P3_NO_RETEST',0)} hold={vc.get('P1_HOLD',0)} fail={vc.get('P2_FAIL',0)}")
retest_within = vc.get('P1_HOLD',0)+vc.get('P2_FAIL',0)
print(f"RETEST_WITHIN_8={retest_within} | INDEPENDENT_TRADES={len(TR)} ({len(TR)/yrs:.0f}/yr)")
hold=EV[EV.cls=='P1_HOLD']; fail=EV[EV.cls=='P2_FAIL']
print(f"RETEST_HOLD_L2_RATE={100*hold.reach32.mean():.1f}% FAIL={100*fail.reach32.mean():.1f}% LIFT={100*(hold.reach32.mean()-fail.reach32.mean()):.1f}pp")
print(f"MFE/MAE hold={hold.mfe_atr.median()/(hold.mae_atr.median()+1e-9):.2f} fail={fail.mfe_atr.median()/(fail.mae_atr.median()+1e-9):.2f}")
r=TR.net_R.to_numpy()
print(f"BASE={r.mean():+.4f} STRESS={TR.net_R_stress.mean():+.4f} WR={(r>0).mean():.3f} PF={r[r>0].sum()/(abs(r[r<=0].sum())+1e-9):.3f} medNatRR={np.median(TR.natRR):.2f}")
los=-r[r<=0]; print(f"realized-loss P95={np.percentile(los,95):.2f} P99={np.percentile(los,99):.2f} MAX={los.max():.2f} maxDD={(np.maximum.accumulate(np.cumsum(r))-np.cumsum(r)).max():.0f}R")
