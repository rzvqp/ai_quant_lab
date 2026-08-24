# ALPHA_S5_DISCOVERY_LINEAGE_RECONSTRUCTION

**Mandate:** `ALPHA-XAUUSD-BROAD-DISCOVERY-CAMPAIGN-V2-001` §2/§42-A. Mechanical reconstruction from authoritative primary artifacts (NOT chat-memory). Purpose = reverse-engineer the DISCOVERY PROCESS that let S5 emerge, extract `S5_DISCOVERY_PROCESS_PRINCIPLES`, then modernize. **NOT** to copy/retune S5.

## S5 identity (confirmed)
`S5` · historical ID `C_2d587447` · frozen spec `S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3}` · **LONG-only** NY opening-range breakout, stop = opposite OR boundary, target = 3R. Definition: `ai_quant_lab-families/code/mstrat.py:260-278`. Engine: `mstrat.simulate` (`mstrat.py:42-74`).

## The discovery process (7 steps, primary-sourced)
1. **BROAD common-engine campaign.** 20 families S1-S20, **1,972 canonical hypotheses**, ONE shared lookahead-safe simulator + ONE feature set + ONE pipeline. A family supplies only `grammar()` + `setups(d,h)->[{si,ei,dir,stop,exit_kind,exit_param}]`; execution is identical for all (entry@next-open, stop/target/timeout(48)/trailing, stop-floor, sequential non-overlap). `run_full_campaign.py`, `CHANGELOG.md:1870-1874`, `PROJECT_AUDIT.md:80` (1972 gen · 1800 valid · 357 hist-profitable · 130 research-worthy · 1,300,740 trades; holdout SEALED).
2. **FROZEN fast-fail screen ("Discovery Screen V1").** `run_full_campaign.py:31-36`, verbatim: `hist_prof = n>0 & sumR>0 & exp>0 & pf>1.00`; `research_worthy = n>=25 & exp>0 & pf>=1.02 & dd<=25 & (wo1>0 or t1<0.5) & months>=2 & years>=2`; `fragile = exp>0 & (t1>=0.5 or wo1<=0)`. (`wo1`=exp with best trade removed; `t1/t3/t5`=top-1/3/5 trade share of gross profit.) Kills ~93% (1972→130). No tuning-to-profit (§0 protocol: "an edge's job is to survive falsification, not to be made profitable").
3. **DEDUP to economic candidates.** 130 research-worthy clustered by economic mechanism key (S5 key = `[session,side]`) → **17 distinct candidates** (`STRATEGY_DEDUPLICATION_REPORT_S1S20.md`). Cross-strategy overlap measured (signal Jaccard, daily-PnL corr).
4. **ROBUSTNESS ranking.** `knowledge_system.py:92`: `rob = stab + val_exp.clip(-0.3,0.3) + log10(n)/3 - t1 - (dd/25).clip(1) - fragile*0.5` — REWARDS stability (pos-month share), OOS val_exp, log(n); PENALIZES tail-share (t1), drawdown, fragility. **S5 ranked #1/17 (rob 2.14)**, rep_exp +0.166 GROSS, PF 1.48, val_exp +0.179 (positive OOS). Knife-edge gate: reject if <20% of a mechanism's tuning neighbors profitable.
5. **INDEPENDENT A-H validation on a FRESH clean population with RATIFIED cost.** Separate population (clean 52,572-bar block, `STAT_S5_S20_CLEAN_VALIDATION_FREEZE.md`) + ratified execution (TICK 0.01, BASE RT 0.05, STRESS RT 0.24 — explicitly FORBIDDEN from using mstrat.CFG). Gates (`RT_S5_S20_CLEAN_INDEPENDENT_VALIDATION_REPORT.md:79-95`, 295 trades): A sample n≥100 (295); B BASE>0 (+0.2098); C STRESS>0@0.24 (+0.1925); D temporal ≥2/3 thirds>0 none<−0.10 ([0.273,0.153,0.201]); E tail best-1%-removed>0 (+0.1907); F +1-bar exec-delay>0 (+0.1581); G risk maxDD≤15R & maxloss≤2R (−6.44R/−1.03R); H spec fidelity. **S5 = INDEPENDENT_VALIDATION_PASS (A-H all)**, WR 0.549, PF 1.609, non-scalping geometry (SL med $12.44 / TP med $37.32 / 373 pips, 99% TPs ≥100 pips), tail = LEGITIMATE_POSITIVE_SKEW.
6. **What DISTINGUISHED S5 from the ~16 that failed** (the real survivor bar): (a) **legitimate positive skew** — survives best-1%-removed (+0.036) while the S-corpus as a whole was fat-tail-carried (top-5 = 41%); (b) **temporal reproduction on BOTH OOS blocks** (DEV +0.062 AND CALIB +0.080) — competitors reproduced on one, reversed on the other (C-001 DEV +0.088→CALIB −0.030); (c) **cost survival at STRESS**; (d) **regime-agnostic** — positive every regime, NO rescue gate needed (C-001 needed a trend gate); (e) **controlled risk degradation** — maxDD −6.44R vs S20's −23.59R which FAILED gate G despite clearing A-F/H (same RR3, but 32% WR → long losing runs); (f) **non-scalping geometry**.
7. **Multiplicity provenance.** Exact hypothesis count (1972), family universe, selection rank, all failed competitors preserved; sealed 20% holdout never opened (`FINAL_HOLDOUT_ACCESS=0`); frozen-candidate-before-OOS (protocol Stage 3 = the anti-p-hack control).

## Known defects carried forward (do NOT repeat)
- **mstrat.TICK=0.1 is a 10× error** (RT-CODE-A-0007). The discovery screen therefore ran GROSS/near-zero-cost → its 357/130 survivors are **cost-naive**. Ratified cost = TICK 0.01 / STRESS RT 0.24.
- **Analytic normal-approx p-value INVALID in the tail** (S6: 2.1e-54 analytic vs ~0.12 empirical) → retracted; significance left PENDING at discovery. Use empirical/matched-null + cross-era + tail-removal instead.
- **Single-regime corpus** (2022-12→2025-10 = one 131% bull) → every mstrat verdict is `REGIME-LIMITED`, never `VALIDATED`. Cross-era generalization was structurally impossible in that corpus.
- **val_exp leakage**: S5's OOS val_exp entered the robustness score, "consuming" that slice → a FRESH clean population was required for honest A-H. (Counterfactually removing val_exp left S5 rank-1, RR3 — the result was not an artifact of the leak, but the discipline stands.)

## S5_DISCOVERY_PROCESS_PRINCIPLES (RETAINED — §42-B)
- **P1** Broad common-engine search: many economically-distinct mechanisms, ONE lookahead-safe simulator + ONE scorecard; comparability is the deliverable.
- **P2** Frozen objective fast-fail screen BEFORE deepening; kills the bulk cheaply; never tune-to-profit.
- **P3** Dedup to economic candidates + robustness ranking that penalizes tail-dependence / drawdown / fragility and rewards stability + OOS + N.
- **P4** Independent A-H validation on a FRESH population with RATIFIED cost, separate from the screen.
- **P5** The six S5 distinguishers ARE the survivor bar: positive-skew (best-1%-removed>0), temporal reproduction on all OOS blocks, STRESS-cost survival, regime-agnostic (no rescue gate), controlled maxDD, non-scalping geometry.
- **P6** Full multiplicity provenance + sealed holdout + frozen-candidate-before-OOS.

## MODERNIZATIONS (CORRECTED — §42-C)
- **C1 Ratified cost at the SCREEN, not only validation.** Apply STRESS RT 0.24 during screening so cost-fragile ghosts die immediately (the original screen's central blind spot).
- **C2 Multi-era cross-era at the SCREEN.** Score every hypothesis on b0/b1 (2011-2018) + DEV (2021-2023) + CALIB (2024); REQUIRE same-sign behavior (cross-era sign reversal with sufficient N = FAIL, §15). The strongest falsifier; the original corpus could not do it.
- **C3 Strict causal timestamps + mechanism-owned structural stops + event dedup + DISC/CONF + adversarial SESSION-artifact & TAIL checks** (S10 pullback-fill and S4 Asia-session false positives are precedent — strong result ≠ survivor until stress-tested).
- **C4 Fixed engine cost** (TICK 0.01, ratified stop-floor) — `swing_base` already correct; never use mstrat.CFG cost.
- **C5 Market Mode = optional conditioner** (§4), measured for stable incremental value, not a reflexive gate.

## Consequence for the campaign
The broad S1-S51 search already ran (2,432 hyps) but **cost-naive + single-regime**; nothing is validated (only S5 cleared A-H, COMP-CONT-L pending). The genuinely-new, highest-information modern step is to run **the S5 process (P1-P6) on the ratified `swing_base` engine across multiple eras (C1-C5)** as a broad cross-information-class screen — reusing `sb.simulate` (no forked simulator), deepening only survivors against the A-H bar, freezing robust non-redundant ones, and when the named universe is exhausted, generating new mechanisms from the Discovery Radar.
