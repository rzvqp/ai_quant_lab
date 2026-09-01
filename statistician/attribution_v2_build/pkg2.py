import sys, os, json, hashlib
import pandas as pd, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = r"C:\Users\MEDION~1\AppData\Local\Temp\v2"
OUT = r"C:\Users\MEDION GAMING\ai_quant_lab\statistician\attribution_v2"
M = pd.read_csv(r"C:\Users\MEDION GAMING\ai_quant_lab\statistician\COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1.csv")
O = pd.read_csv(os.path.join(OUT, "ATTRIBUTION_UNIVERSE_V2.csv"))
SEC = pd.read_csv(os.path.join(T, "feature_map_SECRET.csv"))

# ---------- MECHANISM MAP : completes M27 from each module's own frozen hypothesis text ----------
ER = {
 "E005":"M06_SESSION_TIME","E006":"M02_FAILED_BREAKOUT_FADE","E008":"M06_SESSION_TIME",
 "E009":"M11_STRUCTURE_BREAK_REVERSAL","E010":"M14_REFERENCE_LEVEL","E011":"M08_EXTENSION_MEAN_REVERSION",
 "E012":"M13_IMBALANCE_FVG","E014":"M02_FAILED_BREAKOUT_FADE","E015":"M14_REFERENCE_LEVEL",
 "E017":"M01_LIQUIDITY_SWEEP","E025":"M14_REFERENCE_LEVEL","E026":"M08_EXTENSION_MEAN_REVERSION",
 "E027":"M14_REFERENCE_LEVEL","E028":"M07_TREND_CONTINUATION","E029":"M15_GAP",
 "E032":"M16_AUCTION_VALUE","CAND0001":"M14_REFERENCE_LEVEL","CAND0002":"M04_VOLATILITY_COMPRESSION_EXPANSION",
 "CAND0004":"M13_IMBALANCE_FVG","CAND0005":"M13_IMBALANCE_FVG","CAND0006":"M14_REFERENCE_LEVEL",
 "CAND0009":"M03_BREAKOUT_RETEST","CAND0027":"M06_SESSION_TIME","CAND0037":"M03_BREAKOUT_RETEST",
 "CAND0038":"M10_DISPLACEMENT_CONTINUATION"}
fam2mech = dict(zip(M.OBJECT_ID, M.MECHANISM_ID))
rows = []
for _, r in O.iterrows():
    oid = r.OBJECT_ID
    base = oid.split("::")[0]
    mech = ER.get(base) or fam2mech.get(base) or fam2mech.get(oid) or "M99_UNCLASSIFIED"
    rows.append(dict(OBJECT_ID=oid, FAMILY_ID=base, MECHANISM_ID=mech, TIER=r.TIER))
MM = pd.DataFrame(rows)
unk = MM[MM.MECHANISM_ID.isin(["M99_UNCLASSIFIED", "M27_EDGE_RESEARCH_PATTERN"])]
print(f"  mechanism map: {len(MM)} objects, {MM.MECHANISM_ID.nunique()} distinct mechanisms")
print(f"  UNKNOWN_MECHANISM objects = {len(unk)}  {'-> MECHANISM_MAPPING_COMPLETE = YES' if len(unk)==0 else list(unk.OBJECT_ID)}")
print(f"\n  objects per mechanism:")
for m, c in MM.MECHANISM_ID.value_counts().sort_index().items(): print(f"    {m:38} {c}")
MM.to_csv(os.path.join(OUT, "MECHANISM_MAP.csv"), index=False)

# ---------- FEATURE ELIGIBILITY TABLE ----------
POST = ["mfe_R","mae_R","time_to_mfe","time_to_mae","adverse_first","exit_kind","bars_held","final_R"]
BAD  = ["swing_high_confirmed_later","future_session_range","eventual_exit_price","zigzag_pivot_unconfirmed",
        "forward_atr","session_range_completed","next_bar_open"]
fe = [dict(FEATURE=r.BLIND_ID, CLASS="ELIGIBLE_PRE_ENTRY", KIND=r.KIND) for _, r in SEC.iterrows()]
fe += [dict(FEATURE=p, CLASS="POST_ENTRY_ONLY", KIND="numeric") for p in POST]
fe += [dict(FEATURE=b, CLASS="INVALID_LOOKAHEAD", KIND="excluded") for b in BAD]
FE = pd.DataFrame(fe); FE.to_csv(os.path.join(OUT, "FEATURE_ELIGIBILITY_TABLE.csv"), index=False)
print(f"\n  feature eligibility: {FE.CLASS.value_counts().to_dict()}")
print(f"  NOT_AVAILABLE_FOR_FAMILY is assigned at runtime per object and MUST be reported per (object,feature),")
print(f"  never silently dropped -- a feature absent for a family is a recorded absence, not a missing test.")

# ---------- POLICIES ----------
json.dump(dict(
  multiplicity_method="hierarchical: BH-FDR q=0.05 on stage 1 (5,290 per-object x per-feature omnibus tests); "
                      "Bonferroni m=46 on stage 2 (cross-family recurrence); Bonferroni m=20 on stage 3 (interactions)",
  total_declared_tests=5356,
  reference_bound="Bonferroni over all 5,356 would require |z| > 4.43; reported alongside every stage-2 survivor",
  frozen_before_outcomes=True,
  rule="the correction is fixed here and may not be revised after results are seen"),
  open(os.path.join(OUT, "MULTIPLICITY_POLICY.json"), "w"), indent=1)

json.dump(dict(
  placebo_1=dict(name="OUTCOME_SHUFFLE_WITHIN_BLOCK",
    method="permute the per-trade outcome within (object x calendar-month) blocks, preserving the feature "
           "panel and the trade timestamps; rerun the FULL stage-1 pipeline",
    replicates=200,
    pass_criterion="the BH-FDR discovery rate under the null must be <= q (0.05) +/- Monte-Carlo error; "
                   "if the pipeline routinely manufactures 'rescue' cells under shuffled outcomes, V2 STOPS"),
  placebo_2=dict(name="FEATURE_ASSIGNMENT_SHUFFLE",
    method="permute the feature-vector-to-trade assignment within each object; any condition that survives "
           "is a property of the payoff shape, not of the feature", replicates=200),
  placebo_3=dict(name="SYNTHETIC_POSITIVE_CONTROL",
    method="inject a known conditional effect (+0.3R on one randomly chosen blinded feature's top bin) and "
           "confirm the pipeline recovers it at the declared power", replicates=50),
  rule="all three run BEFORE any real result is interpreted"),
  open(os.path.join(OUT, "PLACEBO_PROTOCOL.json"), "w"), indent=1)

json.dump(dict(
  attribution_discovery_range="2011-07-26 .. 2026-07-27 (the entire governed XAU M15 record)",
  untouched_validation_range="NONE",
  historical_reuse_status="MATERIALLY_EXPOSED",
  evidence=[
    "RESEARCH_HOLDOUT_CUTOFF_UTC = 2025-10-23 was the program escrow; it has been consumed - "
    "Alpha's DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1 ran to 2026-07-27 with no truncation (STAT 94dff78: "
    "213 episodes inside the holdout at +0.2374R vs +0.0442R outside)",
    "Alpha's own attribution V1 trade objects span 2011..2026, i.e. include the escrow window",
    "the S1-S51 campaign declared its own research/val/holdout split (50491/16830/16831) and that split's "
    "holdout has been reported on in prior campaign artifacts"],
  consequence="No clean out-of-sample range exists for this universe. A clean OOS is NOT manufactured. "
              "EVERY V2 finding is HYPOTHESIS_GENERATION ONLY and may not be described as validated, "
              "confirmed, or out-of-sample. Chronological thirds are used for STABILITY description only, "
              "never as independent validation.",
  future="a genuinely clean validation requires either new forward data accrued after this freeze date, "
         "or a newly escrowed range that no division has consulted"),
  open(os.path.join(OUT, "HISTORICAL_REUSE_POLICY.json"), "w"), indent=1)

files = sorted(os.listdir(OUT))
h = hashlib.sha256()
for f in files:
    h.update(f.encode()); h.update(open(os.path.join(OUT, f), "rb").read())
PKG = h.hexdigest()
print(f"\n  package files ({len(files)}): {files}")
print(f"\n  PROTOCOL_PACKAGE_HASH = {PKG}")
json.dump(dict(pkg=PKG), open(os.path.join(T, "pkg2.json"), "w"))
