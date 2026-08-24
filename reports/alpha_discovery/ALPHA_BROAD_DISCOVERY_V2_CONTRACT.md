# ALPHA_BROAD_DISCOVERY_V2_CONTRACT

**Mandate:** `ALPHA-XAUUSD-BROAD-DISCOVERY-CAMPAIGN-V2-001` (+ ADDENDUM: never idle). The modernized S5 discovery process (see [ALPHA_S5_DISCOVERY_LINEAGE_RECONSTRUCTION.md]) run as a continuous broad→deep→validate engine. Price-only XAUUSD, no exogenous (§26), Market Mode optional conditioner (§4).

## Engine (reuse, do NOT fork — §10)
- **Simulator:** `swing_base.sb.simulate` — next-bar-open entry, stop-wins-ties, mechanism-owned structural stop, event dedup (`sb.dedup_events`), STRESS RT **0.24 USD** cost (ratified TICK 0.01; the mstrat.CFG TICK=0.1 is the known 10× defect — never used).
- **Common screen driver:** `bscreen.py`. A hypothesis = `{name, info_class, side(+1/-1), rr, horizon, cool, signal(frame)->(idx, sl_usd)}`. LONG/SHORT screened separately (§22).
- **Eras (multi-era, the key modernization C2):** b0/b1 = 2011-2018 (`hist_m15_data`), DEV = 2021-2023, CAL = 2024 (`swing_base` gated-M5 firewall). No 2025+, no read_csv, no SEALED/protected regions (§26/§27 clean). b0/b1 give the cross-era falsification the original single-regime corpus could not.

## Uniform scorecard (§12) + fast-fail verdict (§13)
Per hypothesis, per era: N, avgR(STRESS), avgR_gross, PF, WR, medR; pooled: poolN, poolR, best-1%-removed (`best1`, = S5 gate E), best-10%-removed (descriptor), session distribution, cross-era pos-count.
Verdict (exploratory, §37): `ELIM:INSUFFICIENT_N` (poolN<60 or <2 eras with N≥25) · `ELIM:NEG_STRESS` (poolR≤0) · `ELIM:SIGN_REVERSAL` (an era >0 and another <−0.03, both N≥25 — §15) · `ELIM:TAIL_ONLY` (best1≤0) · `ELIM:INCONSISTENT` · `SURVIVOR` (all N≥25 eras >0, poolR>0, best1>0, no reversal; `*` if poolR>0.05) · `SURVIVOR-weak` (all-but-one era >0). `[SESSION_ARTIFACT]` flag if >65% one session (§16 precedent: S4/S10 false positives).
**Calibration:** the screen must reproduce the frozen **S5** (`ORB_NY_L`) as a SURVIVOR; Batch A confirmed it (best1 +0.043, all 4 eras +). The tail gate was corrected best10→best1 against this anchor.

## Tier funnel (§14)
TIER0 HYPOTHESIS → TIER1 SCREEN_SURVIVOR (passes bscreen) → TIER2 DEEPENING_CANDIDATE → TIER3 ROBUST_ALPHA_CANDIDATE → TIER4 FROZEN_PENDING_INDEPENDENT_VALIDATION. A SCREEN_SURVIVOR is not a candidate; most die in deepening.

## Deepening bar for survivors (§15) = S5's A-H gates (P4/P5)
A sample n≥100 · B BASE>0 · C STRESS>0@0.24 · D temporal thirds ≥2/3>0 none<−0.10 · E best-1%-removed>0 · F +1-bar exec-delay>0 · G maxDD≤15R & maxloss≤2R · H spec fidelity. Plus DISC/CONF, neighbor stability, session-artifact, year concentration, MFE/MAE, event-dedup, portfolio overlap vs S5/COMP-CONT-L (§30). Adversarial skepticism mandatory for strong results (§16).

## Anti-overfit (§21/§36/§37)
Small bounded variant sets (§8, ~3-10/mechanism), no grids. Every configuration counted in the multiplicity ledger (`ALPHA_BROAD_SCREEN_RESULTS_BATCH_*.md` rows). Negatives preserved. Batches are intentionally cross-information-class (§32).

## Loop (§34, never idle — ADDENDUM)
batch → screen → record → rank → deepen survivors → freeze robust (FROZEN_PENDING_INDEPENDENT_VALIDATION, continue) → next cross-class batch → … When named S1-S51 exhausted, generate new bounded hypotheses from the Radar (§18). Hard-stop only on the 6 governance/data-integrity blockers (§41).

## Frozen/reference (do NOT modify — §7/§30)
S5 (validated), COMP-CONT-L-rr2 (pending), H4-bo-raw-S (reference/overlap only, validation blocked). New survivors compared against these for redundancy.
