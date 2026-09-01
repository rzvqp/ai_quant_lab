"""COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1 builder. Provenance only -- no edge search, no attribution."""
import sys, os, re, glob, json, hashlib
import pandas as pd, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
OUT = r"C:\Users\MEDION GAMING\ai_quant_lab\statistician"

# ---------- BLOCK A : Executable Strategy Library S1-S51 ----------
meta_src = open(os.path.join(AA, "code", "strategy_library_metadata.py"), encoding="utf-8").read()
fams = re.findall(r"^ '(S\d+)': dict\(name='([^']+)', klass='([^']+)'", meta_src, re.M)
META = {f: (n, k) for f, n, k in fams}
NOT_IMPL = re.findall(r"^ '(S3[2-7])': '([^']+)'", meta_src, re.M)

core = pd.read_parquet(os.path.join(AA, "results", "FAMILY_RESULTS.parquet"), engine="fastparquet")
ext = pd.read_parquet(os.path.join(AA, "results", "ext_families", "EXT_FAMILY_RESULTS.parquet"), engine="fastparquet")
allres = pd.concat([core, ext], ignore_index=True)
vc = allres.groupby("fam").size().to_dict()
nc = allres.groupby("fam")["n"].sum().to_dict()
best = allres.groupby("fam")["exp"].max().to_dict()
sides = allres.groupby("fam")["side"].apply(lambda s: "BOTH" if s.nunique() > 1 else str(s.iloc[0])).to_dict()

# mechanism taxonomy derived from the library's own klass labels
def mech_of(klass, name):
    k = klass.lower()
    if "liquid" in k or "stop-hunt" in k or "resting" in k: return "M01_LIQUIDITY_SWEEP"
    if "failed-breakout" in k or "contrarian" in k: return "M02_FAILED_BREAKOUT_FADE"
    if "breakout-retest" in k or "participation-gated breakout" in k: return "M03_BREAKOUT_RETEST"
    if "volatility regime" in k or "volatility-regime" in k or "volatility transition" in k or "compression duration" in k or "nr pattern" in k: return "M04_VOLATILITY_COMPRESSION_EXPANSION"
    if "opening-range" in k: return "M05_OPENING_RANGE"
    if "session" in k or "time-of-day" in k or "calendar" in k or "time-window" in k: return "M06_SESSION_TIME"
    if "trend-pullback" in k or "trend continuation" in k or "efficient continuation" in k or "trend acceleration" in k: return "M07_TREND_CONTINUATION"
    if "extension mean-reversion" in k or "exhaustion" in k or "short-term reversal" in k or "overreaction" in k: return "M08_EXTENSION_MEAN_REVERSION"
    if "mtf" in k or "multi" in k: return "M09_MTF_ALIGNMENT"
    if "displacement" in k: return "M10_DISPLACEMENT_CONTINUATION"
    if "structure-break" in k: return "M11_STRUCTURE_BREAK_REVERSAL"
    if "range rotation" in k or "session range position" in k: return "M12_RANGE_ROTATION"
    if "imbalance" in k or "fvg" in k: return "M13_IMBALANCE_FVG"
    if "reference-level" in k or "psychological" in k: return "M14_REFERENCE_LEVEL"
    if "gap" in k: return "M15_GAP"
    if "auction" in k or "value" in k: return "M16_AUCTION_VALUE"
    if "volume" in k or "order-flow" in k: return "M17_VOLUME_PARTICIPATION"
    if "oscillator" in k: return "M18_OSCILLATOR_DIVERGENCE"
    if "sequence" in k or "run-length" in k: return "M19_SEQUENCE_RUNLENGTH"
    if "candlestick" in k: return "M20_CANDLESTICK_PATTERN"
    if "meta" in k or "router" in k or "hybrid" in k or "composite" in k: return "M21_META_ROUTER"
    return "M99_UNCLASSIFIED"

rows = []
INVALID = {"S47": "n<25 (too-rare population; documented INVALID in build_strategy_library.py:318)",
           "S49": "non-selective / non-discrete signal (documented INVALID; NO results parquet exists)"}
for i in range(1, 52):
    f = f"S{i}"
    if f in META:
        name, klass = META[f]
        has_res = f in vc
        if f in INVALID:
            st, elig, defect = "INVALID", "C_CANNOT_REGENERATE", INVALID[f]
        else:
            st, elig, defect = "NEGATIVE", "B_REGENERATE_FROM_FROZEN_SPEC", ""
        rows.append(dict(OBJECT_ID=f, FAMILY_ID=f, MECHANISM_ID=mech_of(klass, name), NAME=name,
                         SOURCE_PROGRAM="Executable Strategy Library (ENGINE v2)",
                         SOURCE_REPORT="results/FAMILY_RESULTS.parquet | results/ext_families/",
                         TIMEFRAME="M15 (HTF context per family)", DIRECTION=sides.get(f, "BOTH"),
                         DATE_RANGE="2011-07-26..2026-07 (research 60/val 20/holdout 20)",
                         VARIANTS=vc.get(f, 0), TRADES=int(nc.get(f, 0)), BEST_VARIANT_EXP=round(float(best.get(f, np.nan)), 4) if has_res else "",
                         STATUS=st, TRADE_LEVEL_DATA_AVAILABLE="NO (summary parquet only)",
                         TRADE_LOG_PATH="", CAN_CAUSALLY_REGENERATE_TRADES="YES" if st != "INVALID" else "NO",
                         REGENERATOR="code/mstrat.py:backtest() / code/mstrat_ext.py + simulate() -> ledger cols R,si,ei",
                         ATTRIBUTION_CLASS=elig, KNOWN_DEFECTS=defect, SUPERSEDES="", SUPERSEDED_BY="", BLOCK="A"))
    else:
        reason = dict(NOT_IMPL).get(f, "not implemented")
        rows.append(dict(OBJECT_ID=f, FAMILY_ID=f, MECHANISM_ID="M22_EXOGENOUS_DATA", NAME=reason.split(" (")[0],
                         SOURCE_PROGRAM="Executable Strategy Library (planned)", SOURCE_REPORT="code/strategy_library_metadata.py:383-388",
                         TIMEFRAME="", DIRECTION="", DATE_RANGE="", VARIANTS=0, TRADES=0, BEST_VARIANT_EXP="",
                         STATUS="NOT_IMPLEMENTED", TRADE_LEVEL_DATA_AVAILABLE="NO", TRADE_LOG_PATH="",
                         CAN_CAUSALLY_REGENERATE_TRADES="NO", REGENERATOR="",
                         ATTRIBUTION_CLASS="C_CANNOT_REGENERATE", KNOWN_DEFECTS="DATA_BLOCKED: requires external data (CEO-gated)",
                         SUPERSEDES="", SUPERSEDED_BY="", BLOCK="A"))

# ---------- BLOCK C : the 14 objects Alpha V1 actually analysed ----------
mt = pd.read_csv(os.path.join(AA, "reports", "alpha_discovery", "STRATEGY_ATTRIBUTION_MASTER_TABLE.csv"))
g14 = mt.groupby("sid").agg(trades=("net", "size"), exp=("net", "mean"), mfe=("mfe", lambda s: int(s.notna().sum())))
GEN = {"HTF_": ("htf_setups.py", "M07_TREND_CONTINUATION"), "OBR_": ("ob_core.py+ob_exec.py", "M14_REFERENCE_LEVEL"),
       "OBEXEC": ("ob_exec.py", "M14_REFERENCE_LEVEL"), "SESS_": ("sess_core.py+sess_scan.py", "M06_SESSION_TIME")}
MECH14 = {"HTF_PBK_TREND": "M07_TREND_CONTINUATION", "HTF_RECLAIM": "M11_STRUCTURE_BREAK_REVERSAL",
          "HTF_RANGE_FADE": "M12_RANGE_ROTATION", "HTF_TGT_BREAK": "M03_BREAKOUT_RETEST",
          "OBR_A_limit": "M14_REFERENCE_LEVEL", "OBEXEC_B": "M14_REFERENCE_LEVEL",
          "OBEXEC_C": "M14_REFERENCE_LEVEL", "OBEXEC_D": "M14_REFERENCE_LEVEL",
          "SESS_A": "M06_SESSION_TIME", "SESS_B": "M06_SESSION_TIME", "SESS_C": "M06_SESSION_TIME",
          "SESS_D": "M06_SESSION_TIME", "SESS_E": "M06_SESSION_TIME", "SESS_Fc": "M06_SESSION_TIME"}
for sid, r in g14.iterrows():
    gen = next((v[0] for k, v in GEN.items() if sid.startswith(k)), "?")
    rows.append(dict(OBJECT_ID=sid, FAMILY_ID=sid.split("_")[0], MECHANISM_ID=MECH14[sid], NAME=sid,
                     SOURCE_PROGRAM="ORDER_BLOCK / SESSION_SPECIALIST / HTF factories (2026)",
                     SOURCE_REPORT="STRATEGY_OUTCOME_ATTRIBUTION_EDGE_RESCUE_V1 (270622a)",
                     TIMEFRAME="M15", DIRECTION="BOTH", DATE_RANGE="2011..2026",
                     VARIANTS=1, TRADES=int(r.trades), BEST_VARIANT_EXP=round(float(r.exp), 4),
                     STATUS="NEGATIVE", TRADE_LEVEL_DATA_AVAILABLE="YES",
                     TRADE_LOG_PATH="reports/alpha_discovery/STRATEGY_ATTRIBUTION_MASTER_TABLE.csv",
                     CAN_CAUSALLY_REGENERATE_TRADES="YES", REGENERATOR=gen,
                     ATTRIBUTION_CLASS="A_VALID_TRADE_LOG_EXISTS",
                     KNOWN_DEFECTS="path (MFE/MAE) absent for OBR/OBEXEC" if r.mfe == 0 else "",
                     SUPERSEDES="OBR fill-artifact version" if sid == "OBR_A_limit" else "",
                     SUPERSEDED_BY="", BLOCK="C"))

# ---------- BLOCK B : post-S51 named factories / frontiers ----------
B = [
 ("OB_RETEST_FACTORY_V1","OBR-BULL-1","427a418","M14_REFERENCE_LEVEL","NEAR_MISS","B_REGENERATE_FROM_FROZEN_SPEC","YES",
  "SURVIVED=1 then FALSIFIED as a same-bar FILL ARTIFACT (934280a / STAT bd2a40e); corrected causal fill -0.067R","","OB_CAUSAL_EXECUTION_FACTORY_V1"),
 ("OB_CAUSAL_EXECUTION_FACTORY_V1","OB causal executions (4 families)","934280a","M14_REFERENCE_LEVEL","NEGATIVE","A_VALID_TRADE_LOG_EXISTS","YES",
  "","OB_RETEST_FACTORY_V1",""),
 ("SESSION_SPECIALIST_FACTORY_V1","Session specialists A-F","29fcb12","M06_SESSION_TIME","NEGATIVE","A_VALID_TRADE_LOG_EXISTS","YES","","",""),
 ("CROSS_MARKET_RELATIVE_RESPONSE_FACTORY_V1","XAU-vs-DXY dislocation residual (5 families)","4dabcda","M23_CROSS_MARKET","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES",
  "different panel (DXY-joined), not on the M15 pool","",""),
 ("M5_EVENT_REVEALED_DIRECTION_FACTORY_V1","M5 Family A-E state machines","fd0c7b7","M24_EVENT_REVEALED_RESPONSE","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES",
  "native-M5 panel (2021+ only); family E outlier-dependent","",""),
 ("LONG_HORIZON_EVENT_REVEALED_DIRECTION_V1","24h event-revealed direction","35b86b3","M24_EVENT_REVEALED_RESPONSE","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES","","",""),
 ("DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1","OCO prior-day-extreme continuation (1/1.5/2R)","078c136","M25_DIRECTION_AGNOSTIC_OCO","NEAR_MISS","B_REGENERATE_FROM_FROZEN_SPEC","YES",
  "STAT 94dff78: reproduces exactly but mechanism refuted (long-drift); gap-through fills; holdout consumed; stress-net<0","",""),
 ("TEMPORAL_SEQUENCE_MINING_V1","Path/order sequence motifs","f5a770e","M19_SEQUENCE_RUNLENGTH","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES","","",""),
 ("H1_H4_SETUP_M5_EXECUTION_V1","HTF setup + M5 execution","bee6aca","M09_MTF_ALIGNMENT","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES","","",""),
 ("ALPHA_DISCOVERY_FACTORY_V2","Contrast miner H1/H2/H3","c77430d","M26_CONTRAST_MINING","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES","","",""),
 ("VOLPATH_FRONTIER","Compression-expansion path (2 phases)","6092c8f","M04_VOLATILITY_COMPRESSION_EXPANSION","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES","","",""),
 ("VOLTIME_FRONTIER","Volatility-timing families 1-5","1a96ce3","M04_VOLATILITY_COMPRESSION_EXPANSION","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES","","",""),
 ("SESSION_FRONTIER_SF1_SF3","Session events / ORB / whipsaw map","adc81b0","M06_SESSION_TIME","INFORMATION_ONLY","B_REGENERATE_FROM_FROZEN_SPEC","YES","SF-3 is a NO_TRADE context asset, no trade population","",""),
 ("DXY_FRONTIER_V1","DXY impulse / NDX1 joint convergence","fbbfb91","M23_CROSS_MARKET","INFORMATION_ONLY","B_REGENERATE_FROM_FROZEN_SPEC","YES","","",""),
 ("CHRONOLOGICAL_MARKET_LEARNING","Walk-forward chrono reader (27 quarters)","92f8ef0","M21_META_ROUTER","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES","","",""),
 ("BLIND_FORWARD_STRUCTURE_DISCOVERY_V1","BFSD1-4 + ASREJ-1","99ed83c","M11_STRUCTURE_BREAK_REVERSAL","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","YES","","",""),
 ("GOLD_ORDER_FLOW_DISCOVERY_V1","GC MBO order flow","c4e2add","M17_VOLUME_PARTICIPATION","DATA_BLOCKED","D_NO_LEGITIMATE_TRADE_POPULATION","NO",
  "2-week sample only; TIER_C for research (STAT af6790c confirms)","",""),
 ("L1_LONDON","L1 diurnal path asymmetry","2fe30fb/d97ed3a","M06_SESSION_TIME","INFORMATION_ONLY","D_NO_LEGITIMATE_TRADE_POPULATION","NO",
  "window statistic, not a trade population; STAT cb6f28c froze the exact spec","",""),
 ("P2_RANGE_LOW","Bottom-of-24h-range effect","8693478","M12_RANGE_ROTATION","INVALID","D_NO_LEGITIMATE_TRADE_POPULATION","NO","OVERLAP ARTIFACT (Alpha's own replication)","",""),
 ("V2_4_COILED","Coiled-range timing state","7d12f26","M04_VOLATILITY_COMPRESSION_EXPANSION","INVALID","D_NO_LEGITIMATE_TRADE_POPULATION","NO","SESSION COMPOSITION CONFOUND (Alpha's own replication)","",""),
 ("D4_ASIA_CLOSE_EDGE","Asia close-at-edge -> next-6h magnitude","74541e7 (STAT)","M06_SESSION_TIME","INFORMATION_ONLY","D_NO_LEGITIMATE_TRADE_POPULATION","NO","magnitude-only, direction z +0.06","",""),
]
for oid, nm, cm, mech, st, cls, regen, defect, sups, supby in B:
    rows.append(dict(OBJECT_ID=oid, FAMILY_ID=oid, MECHANISM_ID=mech, NAME=nm,
                     SOURCE_PROGRAM="post-S51 Alpha factory / frontier", SOURCE_REPORT="reports/alpha_discovery/",
                     TIMEFRAME="varies", DIRECTION="BOTH", DATE_RANGE="varies", VARIANTS="", TRADES="", BEST_VARIANT_EXP="",
                     STATUS=st, TRADE_LEVEL_DATA_AVAILABLE="YES" if cls.startswith("A") else "NO", TRADE_LOG_PATH="",
                     CAN_CAUSALLY_REGENERATE_TRADES=regen, REGENERATOR="reports/alpha_discovery/*.py",
                     ATTRIBUTION_CLASS=cls, KNOWN_DEFECTS=defect, SUPERSEDES=sups, SUPERSEDED_BY=supby,
                     BLOCK="B", SOURCE_COMMIT=cm))

# ---------- BLOCK D : frozen / independently-reviewed candidates ----------
D = [
 ("S5_OPENING_RANGE","Opening-range momentum (the only deployed edge)","M05_OPENING_RANGE","VALIDATED","D_NO_LEGITIMATE_TRADE_POPULATION",
  "PROTECTED -- mandate S18 forbids touching it; excluded from the attribution universe by protection, not by eligibility"),
 ("H4_BO_RAW_S","H4 raw-breakout SHORT (b0/b1 historical)","M03_BREAKOUT_RETEST","NEAR_MISS","B_REGENERATE_FROM_FROZEN_SPEC",
  "STAT 3498069 PACKAGE_AUDIT_PASS but BLOCKED on evidence independence"),
 ("COMP_CONT_L_RR2","Compression-timed LONG continuation","M07_TREND_CONTINUATION","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC","STAT 1fb865d FAIL"),
 ("CRS1_H4DIV_FADE_S","Current-regime H4-divergence fade SHORT","M08_EXTENSION_MEAN_REVERSION","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC",
  "STAT 4163382 FAIL (FDR); VE 91b7415 repaired an H4 lookahead that had collapsed avgR +0.45 -> +0.07"),
 ("HR_TU_PB_L","Frozen weak LONG trend-beta (pullback)","M07_TREND_CONTINUATION","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC",""),
 ("MT_H4_DISPACCEPT_L","Frozen weak LONG displacement-accept","M10_DISPLACEMENT_CONTINUATION","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC",""),
 ("RANGE_LIFECYCLE_V4_4","RANGE detector v4.4 (deployed baseline)","M12_RANGE_ROTATION","VALIDATED","D_NO_LEGITIMATE_TRADE_POPULATION","detector/context, not a trade generator"),
 ("RANGE_LIFECYCLE_VNEXT","RANGE vNext multi-candidate","M12_RANGE_ROTATION","INFORMATION_ONLY","D_NO_LEGITIMATE_TRADE_POPULATION","research baseline only"),
 ("E015_ORDER_BLOCK_REMITIGATION","OB re-mitigation (edge_research)","M14_REFERENCE_LEVEL","NEGATIVE","B_REGENERATE_FROM_FROZEN_SPEC",""),
]
for oid, nm, mech, st, cls, defect in D:
    rows.append(dict(OBJECT_ID=oid, FAMILY_ID=oid, MECHANISM_ID=mech, NAME=nm,
                     SOURCE_PROGRAM="frozen candidate / independently reviewed", SOURCE_REPORT="statistician/ + red_team/",
                     TIMEFRAME="varies", DIRECTION="", DATE_RANGE="", VARIANTS="", TRADES="", BEST_VARIANT_EXP="",
                     STATUS=st, TRADE_LEVEL_DATA_AVAILABLE="NO", TRADE_LOG_PATH="",
                     CAN_CAUSALLY_REGENERATE_TRADES="YES" if cls.startswith("B") else "NO",
                     REGENERATOR="frozen spec", ATTRIBUTION_CLASS=cls, KNOWN_DEFECTS=defect,
                     SUPERSEDES="", SUPERSEDED_BY="", BLOCK="D"))

# ---------- BLOCK E : edge_research e0xx / cand00xx ----------
er = sorted(glob.glob(os.path.join(AA, "edge_research", "e0*.py")) + glob.glob(os.path.join(AA, "edge_research", "cand0*.py")))
seen = set()
for f in er:
    b = os.path.basename(f)[:-3]
    if b.endswith("_clean") or "_dependence" in b or "reconstruct" in b or "_setb" in b: continue
    fid = re.match(r"(e\d+|cand\d+)", b).group(1)
    if fid in seen: continue
    seen.add(fid)
    nm = b.split("_", 1)[1] if "_" in b else b
    rows.append(dict(OBJECT_ID=fid.upper(), FAMILY_ID=fid.upper(), MECHANISM_ID="M27_EDGE_RESEARCH_PATTERN", NAME=nm.replace("_", " "),
                     SOURCE_PROGRAM="edge_research (E-series / candidate series)", SOURCE_REPORT=f"edge_research/{b}.py",
                     TIMEFRAME="M15", DIRECTION="BOTH", DATE_RANGE="pre-holdout split", VARIANTS="", TRADES="", BEST_VARIANT_EXP="",
                     STATUS="NEGATIVE", TRADE_LEVEL_DATA_AVAILABLE="NO", TRADE_LOG_PATH="",
                     CAN_CAUSALLY_REGENERATE_TRADES="YES", REGENERATOR=f"edge_research/{b}.py",
                     ATTRIBUTION_CLASS="B_REGENERATE_FROM_FROZEN_SPEC", KNOWN_DEFECTS="",
                     SUPERSEDES="", SUPERSEDED_BY="", BLOCK="E"))

M = pd.DataFrame(rows)
for c in ("SOURCE_COMMIT",):
    if c not in M.columns: M[c] = ""
M["SOURCE_COMMIT"] = M["SOURCE_COMMIT"].fillna("")
cols = ["OBJECT_ID","FAMILY_ID","MECHANISM_ID","NAME","BLOCK","SOURCE_PROGRAM","SOURCE_REPORT","SOURCE_COMMIT",
        "TIMEFRAME","DIRECTION","DATE_RANGE","VARIANTS","TRADES","BEST_VARIANT_EXP","STATUS",
        "TRADE_LEVEL_DATA_AVAILABLE","TRADE_LOG_PATH","CAN_CAUSALLY_REGENERATE_TRADES","REGENERATOR",
        "ATTRIBUTION_CLASS","KNOWN_DEFECTS","SUPERSEDES","SUPERSEDED_BY"]
M = M[cols].sort_values(["BLOCK","OBJECT_ID"]).reset_index(drop=True)
p = os.path.join(OUT, "COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1.csv")
M.to_csv(p, index=False)
h = hashlib.sha256(open(p, "rb").read()).hexdigest()
print("=" * 110); print("  MANIFEST BUILT"); print("=" * 110)
print(f"  rows {len(M)}   -> {p}")
print(f"  MANIFEST_HASH = {h}")
print(f"\n  by BLOCK:  {M.BLOCK.value_counts().sort_index().to_dict()}")
print(f"  by STATUS: {M.STATUS.value_counts().to_dict()}")
print(f"  by ATTRIBUTION_CLASS: {M.ATTRIBUTION_CLASS.value_counts().to_dict()}")
print(f"\n  DISTINCT_MECHANISMS = {M.MECHANISM_ID.nunique()}")
for m, c in M.MECHANISM_ID.value_counts().sort_index().items(): print(f"    {m:38} {c}")
tot_var = pd.to_numeric(M.VARIANTS, errors="coerce").fillna(0).sum()
print(f"\n  TOTAL_VARIANTS (S-library + 14 objects) = {int(tot_var)}")
json.dump(dict(hash=h, rows=len(M)), open(r"C:\Users\MEDION~1\AppData\Local\Temp\gy\meta.json", "w"))
