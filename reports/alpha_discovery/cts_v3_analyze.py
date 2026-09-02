"""cts_v3_analyze.py — CTS V3 PHASE 3: incremental-value verdicts (§22 event-relational vs A/B; §25 relation-structure from controls), practical
gate (§23), the §27 CEO pressure-attack concept test (mechanical, post-freeze), the §28 ten market-reasoning answers from winner-loser contrasts
on the event features, motif interpretation, and feasibility. Interpretation only; no retuning.
"""
import os, ast, numpy as np, pandas as pd
OUT=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
FR=pd.read_csv(OUT+r"\CTS_V3_RETENTION_FRONTIER.csv"); NC=pd.read_csv(OUT+r"\CTS_V3_NEGATIVE_CONTROLS.csv")
EL=pd.read_parquet(OUT+r"\CTS_V3_EVENT_LEDGER.parquet"); R=EL.R.to_numpy(); dr=EL.dir.to_numpy()
FR["fold_exps"]=FR["fold_exps"].apply(lambda s: ast.literal_eval(s) if isinstance(s,str) else s)
def at(rep,ret):
    x=FR[(FR.rep==rep)&(FR.retention==ret)]; return x.iloc[0] if len(x) else None

# ---- §22 EVENT_RELATIONAL_INCREMENTAL_VALUE ----
A6=at("A_cts_v2_baseline",0.6); B6=at("B_event_aggregates",0.6); C6=at("C_event_relational",0.6)
pooled_CA=C6.sel_exp-A6.sel_exp; pooled_CB=C6.sel_exp-B6.sel_exp
folds_CA=[c-a for c,a in zip(C6.fold_exps,A6.fold_exps)] if len(C6.fold_exps)==len(A6.fold_exps) else []
eriv = (pooled_CA>=0.08) and (sum(1 for x in folds_CA if x>=0.05)>=2) and (pooled_CB>0)
print(f"== §22 EVENT_RELATIONAL_INCREMENTAL_VALUE ==")
print(f"  C-A pooled@60 = {pooled_CA:+.4f} (need >=+0.08) ; folds C-A = {[round(x,4) for x in folds_CA]} ; C-B pooled = {pooled_CB:+.4f}")
print(f"  EVENT_RELATIONAL_INCREMENTAL_VALUE = {'YES' if eriv else 'NO'}")

# ---- §25 relation-structure + order controls ----
def ctl(name):
    x=NC[NC.control==name]; return x.iloc[0] if len(x) else None
rd=ctl("RELATION_DESTROY"); od=ctl("EVENT_ORDER_DESTROY"); lp=ctl("LABEL_PERM_C"); mr=ctl("MATCHED_RANDOM_C")
rsiv = bool(rd is not None and (rd.real - rd.null_mean)>=0.05)
print(f"\n== §25 controls ==")
for c in (od,rd,lp,mr):
    if c is not None: print(f"  {c.control:18s} real={c.real:+.4f} null={c.null_mean:+.4f} delta={c.real-c.null_mean:+.4f} passes={c.passes}")
print(f"  RELATION_STRUCTURE_INCREMENTAL_VALUE = {'YES' if rsiv else 'NO'}")
ncg = bool((mr is not None and mr.passes) or (lp is not None and lp.passes))
print(f"  NEGATIVE_CONTROL_GATE = {'PASS' if ncg else 'FAIL'} (C beats random/label-perm null?)")

# ---- §23 practical gate ----
prac=FR[(FR.winners_retained>=0.60)&(FR.losers_avoided>=0.55)&(FR.sel_exp>=0.10)&(FR.sel_exp_stress>0)&(FR.folds_pos>=2)&(FR.drop5>0)]
print(f"\n== §23 PRACTICALLY_USEFUL_EVENT_SELECTION = {'YES' if len(prac) else 'NO'} ({len(prac)} qualifying points) ==")

# ---- §28 market-reasoning answers via winner-loser contrasts on event features ----
def corr(feat):
    x=EL[feat].to_numpy(float); ok=np.isfinite(x)
    xr=x[ok]-np.nanmean(x[ok]); rr=R[ok]-R[ok].mean(); return float((xr*rr).sum()/(np.sqrt((xr**2).sum()*(rr**2).sum())+1e-9))
Q={ "1_attack_pressure(attack_size_prog)":"gE_attack_size_prog","2_pullback_shrink":"gE_pullback_shrink",
    "3_attack_participation(attack_vol_prog)":"gE_attack_vol_prog","4_defense_decay(atk_pb_vol_ratio)":"gE_atk_pb_vol_ratio",
    "5_repeated_touch":"gE_touch_count","6_penetration(depth)":"gE_penetration","7_time_near_level":"gE_time_near",
    "8_adverse_structure_break":"gE_adverse_breaks","9_favorable_struct(struct_net)":"gE_struct_net","10_last_attack_strong":"gE_last_attack_strong"}
print("\n== §28 event-feature winner-loser correlations (corr with net_R; |corr|>=0.03 = informative) ==")
info={}
for lab,f in Q.items():
    c=corr(f); info[lab]=c; print(f"  {lab:40s} corr={c:+.4f} {'INFO' if abs(c)>=0.03 else '-'}")

# ---- §27 CEO pressure-attack concept: composite 'attack-against-trade increasing + pullbacks shrinking + participation persistent + defense weakening' ----
# For a trade, adverse pressure = adverse structure breaks + shrinking pullbacks + rising attack participation. Higher -> setup should be WEAKER (lower R).
z=lambda a: (a-np.nanmean(a))/(np.nanstd(a)+1e-9)
adverse_pressure = z(EL.gE_adverse_breaks.to_numpy()) + z(-EL.gE_pullback_shrink.to_numpy()) + z(EL.gE_attack_vol_prog.to_numpy()) + z(EL.gE_closes_through.to_numpy())
cc=np.corrcoef(adverse_pressure, R)[0,1]
# expected: higher adverse pressure -> lower R (concept SUPPORTED if corr negative & |corr|>=0.03)
ceo = "SUPPORTED" if cc<=-0.05 else ("PARTIALLY_SUPPORTED" if cc<=-0.02 else ("NOT_SUPPORTED" if abs(cc)<0.02 else "NOT_SUPPORTED"))
print(f"\n== §27 CEO PRESSURE-ATTACK CONCEPT ==")
print(f"  corr(adverse_attack_pressure, net_R) = {cc:+.4f}  -> CEO_PRESSURE_ATTACK_CONCEPT = {ceo}")

# ---- representation comparison + feasibility ----
cmp=FR.pivot_table(index="retention",columns="rep",values="sel_exp"); cmp.to_csv(OUT+r"\CTS_V3_REPRESENTATION_COMPARISON.csv")
SEC_YR=365.25*86400; yrs=(EL.decision_time.max()-EL.decision_time.min())/SEC_YR
feas=pd.DataFrame([dict(rep=r.rep,retention=r.retention,sel_exp=r.sel_exp,sel_per_year=round(r.sel_N/yrs,1),
    time_to_50_mo=round(50/(r.sel_N/yrs)*12,1)) for _,r in FR.iterrows()]); feas.to_csv(OUT+r"\CTS_V3_PROSPECTIVE_FEASIBILITY.csv",index=False)
import json
json.dump({"EVENT_RELATIONAL_INCREMENTAL_VALUE":"YES" if eriv else "NO","RELATION_STRUCTURE_INCREMENTAL_VALUE":"YES" if rsiv else "NO",
           "NEGATIVE_CONTROL_GATE":"PASS" if ncg else "FAIL","PRACTICALLY_USEFUL":"YES" if len(prac) else "NO","CEO_concept":ceo,
           "info_features":{k:round(v,4) for k,v in info.items()},"C_minus_A_60":round(pooled_CA,4)}, open(OUT+r"\_cts_v3_summary.json","w"),indent=2)
print("\nsaved comparison + feasibility + summary")
