# ATTRIBUTION_V2_COVERAGE_REPORT — frozen universe, identity, and the scoring-input blocker

Alpha independent execution of STRATEGY_OUTCOME_ATTRIBUTION_EDGE_RESCUE_V2 against the Statistician-frozen package
`ai_quant_lab/statistician/attribution_v2/`. §1 identity gate + §2 coverage accounting. No object omitted.

## §1 Identity verification — ALL PASS (independently recomputed)
```
MANIFEST_HASH           = 433f1cecbbae20e1d27ce9dc47b604d5258e36702881973a0e7f5fa032a440d9   ✓ exact (sha256 COMPLETE_STRATEGY_GRAVEYARD_MANIFEST_V1.csv)
EXECUTION_UNIVERSE_HASH = 78ea539fe2f6731e5a3dc482220591133d9fc06a3585fb998791bb882839f150   ✓ exact (sha256 ATTRIBUTION_V2_EXECUTION_UNIVERSE.csv)
PROTOCOL_PACKAGE_HASH   = 4488f0e89ae8bb079bf51eb74e4a2767f072d4e368ee383bae1d875ac4359b8f   ✓ exact (sha256 over sorted filenames+contents of attribution_v2/)
IDENTITY_VERIFIED = YES
```

## §2 Coverage of all 115 analysis objects (denominators frozen: families 102, objects 115, mechanisms 25)
```
TIER                          objects   trade-regeneration feasibility (Alpha)
T1_LOG_EXISTS                    14     AVAILABLE — Alpha V1 master table (HTF×4, OBEXEC×4, SESS×6)
T1_REGENERATE_SLIB               56     FEASIBLE — mstrat.REGISTRY(20)+mstrat_ext.EXT_REGISTRY(25)=45 grammar families load OK; rep.py maps reps
T2_REGENERATE_EDGERESEARCH       25     LIKELY FEASIBLE — edge_research modules (unverified per-object)
T2_REGENERATE_FACTORY            14     LIKELY FEASIBLE — alpha_discovery factory modules
T2_REGENERATE_FROZEN_SPEC         6     FEASIBLE — frozen specs (incl. L1/P2/V2-4 style)
```
Trade regeneration is largely feasible. **The blocker is not the trades — it is the features.**

## ★ BLOCKER — the blinded feature VALUE matrix is not available to Alpha
The 5,290 stage-1 tests are `115 objects × 46 blinded features (f001..f046)`. The frozen package publishes only the feature **schema**
(`BLINDED_FEATURE_SCHEMA.csv`, `FEATURE_BINNING.csv`, `FEATURE_ELIGIBILITY_TABLE.csv` = BLIND_ID / KIND / CLASS / N_BINS). It does **not**
publish the per-bar/per-trade blinded feature **values**. Per the frozen design (`feat_REDACTED.py`), the executable builder `feat.py`, the
name→id map `feature_map_SECRET.csv`, and `BLIND_KEY` are **deliberately held by the Statistician and released only at unblinding** — precisely
so Alpha cannot see semantics. They exist only in the Statistician's offline hold (a temp dir), which is NOT an authorization to use them.

Consequently Alpha cannot produce the `f001..f046` values needed to score stage 1, because:
- using the held-back secret (`feat.py` / `feature_map_SECRET.csv` / `BLIND_KEY`) during primary scoring would violate §6 ("DO NOT recover
  feature semantics"), §7 ("Do not exploit [partial blinding]"), and §21/§22 (unblind only after freezing) — a blinding breach; and
- reconstructing the 46 features independently is also forbidden by §6 (no semantic recovery) and, even if attempted, could not be assigned the
  frozen `f-ids` (a **keyed** permutation whose key is offline), so results could never be unblinded against the frozen map.

`BLINDING_DISCIPLINE_PRESERVED = YES` — I inspected only the published schema and the directory listing; I did **not** open `feat.py` or
`feature_map_SECRET.csv`, and I recovered no `f-id → market-variable` mapping.

## Resolution required (cross-division handoff)
To execute V2, the Statistician must hand Alpha the **blinded feature MATRIX** — a data artifact of causal feature *values* under the frozen
blind ids (rows = the governed bars/trades, columns = `f001..f046`, no names), committed and hashed — OR run the blind scoring itself. Either
preserves blinding while supplying the missing scoring input. Alpha must not build or infer the features (that is the whole point of the
blind). This is the exact analogue of a data-gate: identities verified, universe inventoried, and a precise missing artifact identified —
stop rather than improvise.
