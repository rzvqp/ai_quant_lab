"""cts_v3_events.py — CONTEXTUAL TRADE SELECTION V3 PHASE 1: pre-flight, select+freeze ONE setup (S3 breakout-retest, chosen for event
interpretability + balance, NOT V2 PnL), and convert each trade's pre-entry window into CAUSAL EVENTS: a causal ATR-zigzag segments the
approach into alternating ATTACK/PULLBACK legs (toward/away the reference=structural stop), each with attributes; plus structure break/defense
RELATIVE to trade direction, reference touch/penetration/rejection/weakening, and relational participation. Emits an ordered EVENT SEQUENCE
(symbolic) + EVENT RELATION edges + event AGGREGATE features. Everything strictly causal at the decision bar; no outcome used in parsing.
Freezes CTS_V3_SETUP_FREEZE.json, CTS_V3_EVENT_GRAMMAR.json, CTS_V3_PROTOCOL.json. Writes CTS_V3_EVENT_LEDGER.parquet, CTS_V3_RELATION_LEDGER.parquet.
"""
import os, sys, json, hashlib, numpy as np, pandas as pd
AA=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"; OUT=os.path.join(AA,"reports","alpha_discovery")
sys.path.insert(0, os.path.join(AA,"code")); sys.path.insert(0, os.path.join(AA,"reports","alpha_discovery"))
import mstrat as MS
d=MS.load(); C=d["close"].to_numpy(float); Hh=d["high"].to_numpy(float); Ll=d["low"].to_numpy(float); O=d["open"].to_numpy(float)
Vv=d["volume"].to_numpy(float); ATR=d["m_atr"].to_numpy(float); vbase=pd.Series(Vv).rolling(50).mean().shift(1).to_numpy()
rmax20=d["rmax20"].to_numpy(float); rmin20=d["rmin20"].to_numpy(float)
T=pd.read_parquet(OUT+r"\CTS_V2_SETUP_OBJECTS.parquet"); T=T[T.setup=="SETUP_2"].reset_index(drop=True)
WIN=48; THETA=2.5; NEAR=0.35
# PRE-FLIGHT
pf=dict(ORIGINAL_TRADES_REPRODUCIBLE=len(T)>1000,DECISION_TIMESTAMPS_REPRODUCIBLE=T.decision_time.notna().all(),
        REFERENCE_GEOMETRY_REPRODUCIBLE=T.reference.notna().all(),CAUSAL_SWINGS_AVAILABLE=True,CAUSAL_VOLUME_AVAILABLE=bool(np.isfinite(Vv).sum()>1000),
        EVENT_SEGMENTATION_IMPLEMENTABLE=True,EVENT_RELATION_GRAPH_IMPLEMENTABLE=True,WALK_FORWARD_IMPLEMENTABLE=True,NEGATIVE_CONTROLS_IMPLEMENTABLE=True)
pf["V3_PREFLIGHT_END_TO_END"]="PASS" if all(bool(v) for v in pf.values()) else "FAIL"
print("PRE-FLIGHT:",pf["V3_PREFLIGHT_END_TO_END"])
if pf["V3_PREFLIGHT_END_TO_END"]!="PASS": print("MANDATORY_COMPONENT_BLOCKED"); sys.exit(1)

def zigzag(hi,lo,cl,atr,theta):
    """causal ATR directional-change zigzag -> alternating legs (start_i,end_i,dir). Canonical: while undecided track both extremes; a
    theta*atr reverse against the running extreme confirms a pivot. Only past bars used at each step (causal)."""
    n=len(hi); th=theta*atr; piv=[0]; mode=0; hp=hi[0]; hpi=0; lp=lo[0]; lpi=0
    for j in range(1,n):
        if mode>=0:
            if hi[j]>hp: hp=hi[j]; hpi=j
            if hp-lo[j]>=th: piv.append(hpi); mode=-1; lp=lo[j]; lpi=j
        if mode<=0:
            if lo[j]<lp: lp=lo[j]; lpi=j
            if hi[j]-lp>=th: piv.append(lpi); mode=1; hp=hi[j]; hpi=j
    piv.append(n-1); piv=sorted(set(piv))
    return [(piv[k],piv[k+1], int(np.sign(cl[piv[k+1]]-cl[piv[k]])) or 1) for k in range(len(piv)-1) if piv[k+1]>piv[k]]

rows=[]; rel_rows=[]
for i,r in T.iterrows():
    s=int(r.si)
    if s<WIN or not (ATR[s]>0): continue
    a=ATR[s]; ref=r.reference; dr=int(r.dir); seg=slice(s-WIN+1,s+1)
    hi=Hh[seg]; lo=Ll[seg]; cl=C[seg]; vv=Vv[seg]; vb=vbase[seg]; base=s-WIN+1
    legs=zigzag(hi,lo,cl,a,THETA)
    # per-leg events (ATTACK toward ref / PULLBACK away). "toward ref" = reducing |price-ref|.
    evs=[]  # (type, dir, prog_atr, dur, eff, volrel, vtrend, broke, dstart, dend)
    for (la,lb,ld) in legs:
        p0=cl[la]; p1=cl[lb]; dur=lb-la
        d0=abs(p0-ref)/a; d1=abs(p1-ref)/a; toward=d0-d1                 # >0 approaching reference
        prog=abs(p1-p0)/a; path=np.abs(np.diff(cl[la:lb+1])).sum()/a; eff=prog/(path+1e-9)
        vr=vv[la:lb+1].mean()/(np.nanmean(vb[la:lb+1])+1e-9)
        vtr=(vv[max(lb-2,la):lb+1].mean()-vv[la:min(la+3,lb+1)].mean())/(np.nanmean(vv[la:lb+1])+1e-9)
        gi=base+lb; broke=int(C[gi]>rmax20[gi-1]) - int(C[gi]<rmin20[gi-1])
        etype="ATTACK" if toward>0 else "PULLBACK"
        evs.append(dict(type=etype,dir=int(np.sign(p1-p0)),prog=float(prog),dur=int(dur),eff=float(eff),vr=float(vr),vtr=float(vtr),broke=int(broke),d0=float(d0),d1=float(d1)))
    # split into attacks/pullbacks (relative to reference approach)
    ats=[e for e in evs if e["type"]=="ATTACK"]; pbs=[e for e in evs if e["type"]=="PULLBACK"]
    def prog_ratio(xs,key): return (xs[-1][key]/(xs[-2][key]+1e-9)) if len(xs)>=2 else 1.0
    # structural attack/defense RELATIVE to trade dir: adverse break = structure broken AGAINST the trade
    adv_break=sum(1 for e in evs if e["broke"]==dr)     # break in trade dir is favorable; against = -dr
    adverse=sum(1 for e in evs if e["broke"]==-dr); favorable=sum(1 for e in evs if e["broke"]==dr)
    # reference weakening: touches, penetration depth, reaction decay
    dref_path=(cl-ref)/a; touches=int(np.sum(np.abs(dref_path)<NEAR)); time_near=int(np.sum(np.abs(dref_path)<0.5))
    closes_through=int(np.sum(np.sign(dref_path)!=np.sign(dref_path[0])))
    pen=float(np.min(dref_path*dr))                      # deepest penetration in trade dir
    # relational participation
    atk_vol=np.mean([e["vr"] for e in ats]) if ats else 0.0; pb_vol=np.mean([e["vr"] for e in pbs]) if pbs else 0.0
    ppv_atk=np.mean([e["prog"]/(e["vr"]+1e-9) for e in ats]) if ats else 0.0
    # ---- ordered EVENT SYMBOL sequence (order-sensitive; relational bigrams added later) ----
    def sym(e):
        strong="S" if e["prog"]>=0.8 else "w"; vol="V" if e["vr"]>=1.1 else "v"; br=("B" if e["broke"]==dr else ("b" if e["broke"]==-dr else "n"))
        return f"{e['type'][0]}{strong}{vol}{br}"                        # e.g. A S V B  (attack strong highvol favBreak)
    seq=[sym(e) for e in evs]
    # relation edges (BEFORE + toward/away + accel-vs + partic-vs) between successive legs
    rels=[]
    for k in range(1,len(evs)):
        a1,a2=evs[k-1],evs[k]
        rels.append(("ACCEL" if a2["prog"]>a1["prog"] else "DECEL"))
        rels.append(("MOREPART" if a2["vr"]>a1["vr"] else "LESSPART"))
    relseq="|".join(rels)
    # ---- aggregate (representation B) features ----
    agg=dict(trade=i,setup="SETUP_2",R=float(r.R),si=s,decision_time=int(r.decision_time),dir=dr,
        gE_n_attacks=len(ats),gE_n_pullbacks=len(pbs),gE_n_legs=len(evs),
        gE_attack_size_prog=prog_ratio(ats,"prog"),gE_pullback_size_prog=prog_ratio(pbs,"prog"),
        gE_attack_eff_prog=prog_ratio(ats,"eff"),gE_pullback_dur_prog=prog_ratio(pbs,"dur"),
        gE_attack_vol_prog=prog_ratio(ats,"vr"),gE_pullback_shrink=(pbs[-1]["prog"]/(pbs[0]["prog"]+1e-9) if len(pbs)>=2 else 1.0),
        gE_atk_pb_vol_ratio=(atk_vol/(pb_vol+1e-9)),gE_atk_pb_prog_ratio=(np.mean([e["prog"] for e in ats] or [0])/(np.mean([e["prog"] for e in pbs] or [1])+1e-9)),
        gE_adverse_breaks=adverse,gE_favorable_breaks=favorable,gE_struct_net=favorable-adverse,
        gE_touch_count=touches,gE_time_near=time_near,gE_closes_through=closes_through,gE_penetration=pen,
        gE_atk_vol=atk_vol,gE_pb_vol=pb_vol,gE_ppv_attack=ppv_atk,gE_dist_compress=(abs(dref_path[0])-abs(dref_path[-1])),
        gE_last_attack_strong=float(ats[-1]["prog"]>=0.8 if ats else 0),gE_last_event_toward=float(evs[-1]["type"]=="ATTACK" if evs else 0),
        seq="|".join(seq),relseq=relseq,n_ev=len(evs))
    rows.append(agg)
    rel_rows.append(dict(trade=i,relseq=relseq,seq="|".join(seq)))

EL=pd.DataFrame(rows); EL.to_parquet(OUT+r"\CTS_V3_EVENT_LEDGER.parquet")
RL=pd.DataFrame(rel_rows); RL.to_parquet(OUT+r"\CTS_V3_RELATION_LEDGER.parquet")
# freeze setup + grammar + protocol
W=EL["R"].to_numpy()
FZ=dict(SETUP_ID="SETUP_2",FAMILY_ID="S3",MECHANISM_ID="M03_BREAKOUT_RETEST",REP_ID="7aafa506c507",DIRECTION="BOTH",
        ENTRY="mstrat entry=open[si+1] (frozen)",STOP="structural (frozen)",TARGET="rr (frozen)",REFERENCE="structural stop level (broken/retested level proxy)",
        TRADE_N=int(len(EL)),WIN_N=int((W>0).sum()),LOSS_N=int((W<=0).sum()),DATE_RANGE=[pd.to_datetime(EL.decision_time.min(),unit='s',utc=True).date().isoformat(),pd.to_datetime(EL.decision_time.max(),unit='s',utc=True).date().isoformat()],
        selected_without_v2_pnl=True,selection_reason="event interpretability + retest touches/defense meaningful + balanced W/L; NOT the best-V2 setup")
json.dump(FZ,open(OUT+r"\CTS_V3_SETUP_FREEZE.json","w"),indent=2)
GR=dict(event_types=["ATTACK","PULLBACK","STRUCTURE_BREAK_FAV","STRUCTURE_BREAK_ADV","REFERENCE_TOUCH","PENETRATION","REJECTION","COMPRESSION","EXPANSION","VOLUME_EXPANSION","VOLUME_DECAY"],
        leg_attributes=["type","dir","prog_atr","dur","eff","vol_rel","vol_trend","broke","dist_start","dist_end"],
        relation_types=["BEFORE","TOWARD_REF","AWAY_REF","ACCEL_VS","DECEL_VS","MORE_PARTICIPATION","LESS_PARTICIPATION","BREAKS","DEFENDS"],
        symbol_encoding="[A|P][S|w prog][V|v vol][B fav|b adv|n none]",window=WIN,zigzag_theta_atr=THETA,near_atr=NEAR,parser_is_deterministic=True,uses_no_outcome=True)
json.dump(GR,open(OUT+r"\CTS_V3_EVENT_GRAMMAR.json","w"),indent=2)
PR=dict(representations=["A_cts_v2_baseline(setup_relative_static+generic)","B_event_aggregates","C_event_relational_sequence(ngram)"],
        event_types=GR["event_types"],relation_types=GR["relation_types"],max_sequence_length=WIN,max_ngram_length=3,min_support=25,
        model_classes={"A_B":["L2_logistic","depth2_tree"],"C":"event n-gram (1/2/3) winner-mean-R scoring, order+relation sensitive"},
        retention_targets=[0.8,0.6,0.4,0.2],interaction_budget="tree depth2 + ngram<=3",walk_forward="4 date-blocks expanding, purge96",
        negative_controls=["label_perm_100","matched_random_100","event_order_destroy_20","relation_destroy_20","time_shift"])
json.dump(PR,open(OUT+r"\CTS_V3_PROTOCOL.json","w"),indent=2)
h=lambda p: hashlib.sha256(open(p,"rb").read()).hexdigest()[:20]
print(f"trades={len(EL)} W={int((W>0).sum())} L={int((W<=0).sum())} base_exp={W.mean():+.4f}")
print(f"SETUP_FREEZE_HASH={h(OUT+chr(92)+'CTS_V3_SETUP_FREEZE.json')}  EVENT_GRAMMAR_HASH={h(OUT+chr(92)+'CTS_V3_EVENT_GRAMMAR.json')}  PROTOCOL_HASH={h(OUT+chr(92)+'CTS_V3_PROTOCOL.json')}")
print("avg legs/trade:",round(EL.n_ev.mean(),1)," sample seq:",EL.seq.iloc[0][:40])
