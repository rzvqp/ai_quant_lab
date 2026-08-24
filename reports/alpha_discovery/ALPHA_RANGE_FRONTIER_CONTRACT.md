# ALPHA_RANGE_FRONTIER_CONTRACT — RANGE vNext lifecycle information frontier (PREDECLARED)

Mandate: investigate whether the newly RESEARCH-RATIFIED RANGE LIFECYCLE vNext exposes forward-path information that is causal, cross-era, cost-material, and INDEPENDENT of S5. Information-first; RANGE vNext used **read-only, unmodified**. Pre-registered BEFORE inspecting forward paths.

## Ratified identity (exact, guarded)
- Package `ve_n1_replay` (source-only), commit `fa36324` (`ai_quant_lab-wp5b`, branch `discovery-mk-matrix-v1`).
- `RANGE_HIERARCHICAL_VNEXT_CONTRACT_VERSION = "range-hierarchical-vnext-multicandidate-v1"`; config_id `3f2f7ba6bef59d689f96424424e3f0378ffe10ff6f64ecd6bd3ec40e53322c22` (asserted at runtime; constructor fails closed on mismatch). Status: `RANGE_LIFECYCLE_VNEXT_RESEARCH_RATIFIED` (research only; NOT production). Canonical timeframe **M15** (only). Zero-lookahead (architecture §12). Disclosed caveat: price-abandonment premature-kill 2.14-6.42% (used as a descriptor, not relied on).

## Data (authorized, price-only)
RANGE vNext fed MY authorized M15 frames per contiguous era-slice (fresh engine each, gap-safe): b0 (2011-2013) + b1 (2016-2018) via hist_m15_data; DEV (2021-2023) + CAL (2024) via swing_base gated-M5. No 2025+, no exogenous. Forward path measured on the SAME bars (first-passage, `state_path_m15.passage_m15`).

## Events → predeclared implied direction (event-time causal; NOT chosen from outcomes)
- `BREAKOUT_ACCEPTED` upper → **LONG** (accepted escape up = release/continuation up); lower → **SHORT**.
- `SWEEP_CONFIRMED` upper (failed escape at upper) → **SHORT** (rotation back down); lower → **LONG**.
- `LIQUIDITY_SWEEP_REVERSAL` upper → **SHORT** (reversal after upper sweep); lower → **LONG**.
- `IS_TREND_MACRO` with regime TREND_UP → **LONG**; TREND_DOWN → **SHORT** (post-range trend promotion).
- Neutral (measure both L/S, expect rotation/symmetry): `OK_RANGE_MACRO` (confirmation), `EPISODE_REPLACEMENT` (birth), `EPISODE_MERGED`, `EPISODE_CONTINUATION`, `CANDIDATE_ABANDONED_PRICE_MOVED_ON`.

## Phase 2 labels (predeclared, USD project-pips; 10p=$1)
P(+50/−50), P(+70/−50), P(+100/−70), P(+100/−100), P(+150/−75), LONG & SHORT; plus MFE/MAE, cross-era. Primary horizon Hbars=48 (12h). Metric of interest = **directional asymmetry** asym = P(+70/−50, implied dir) − P(+70/−50, opposite).

## Phase 3/5 PROMOTION CRITERIA (predeclared)
An event class becomes a strategy candidate ONLY if ALL hold:
1. **Material asymmetry**: asym70 ≥ +0.05 in the implied direction (or a neutral event shows a stable directional tilt ≥0.05).
2. **Cross-era stable**: same-sign asymmetry in every era with N≥25 (no sign reversal, §15) — the S5 bar.
3. **Adequate N**: pooled effective N ≥ 60; ≥2 eras with N≥25.
4. **Not tail/era-concentrated**: best-1%-removed of the eventual R stays positive; survives best-era removal (checked at strategy stage via bscreen).
5. **Causal + not a data artifact**: event is event-time observable (given); session distribution not pathologically concentrated (checked, but not auto-disqualifying — S5 itself is NY-only).
Then convert to a bounded executable strategy (event=entry trigger; direction=implied; structural invalidation=the range boundary that defines the event; target/horizon; dedup=one per event) and screen on the SAME ratified sb engine (STRESS 0.24), then deepen.

## S5-INDEPENDENCE GATE (mandatory for any positive)
Compare vs frozen S5 (ORB_NY_L): same-day overlap, same-event overlap, session overlap, direction overlap, return correlation, and **performance on NON-S5 days**. If the edge disappears off S5 days → REDUNDANT_EXISTING_ALPHA (Batch D precedent). Record and continue.

## Null outcome
If no lifecycle event shows material cross-era forward-path asymmetry → record the RANGE frontier BOUNDED_NEGATIVE (the lifecycle adds no independent directional information beyond what price already exposes) and move to the next novel-event frontier. Do NOT rescue.
