# ALPHA_DISCOVERY_CHECKPOINTS

Rolling research checkpoints for `ALPHA-XAUUSD-CONTINUOUS-RESEARCH-LOOP-001`. A checkpoint is NOT a stop (§32).

---

## CHECKPOINT #1 — 2026-08-22 — `NEW_ROBUST_STRATEGY_CANDIDATE_FOUND`
**Frontiers this cycle:** 5 (F1-VOL-EXP, F2-EXH-REV, F3-TEMPORAL, F4-DRIFT, F5-COMPCONT). **Hypotheses:** 14 (H01–H14). **Candidates:** 1 survivor. **Parameter variants:** F5 full W×H×cd×rr grid + CALIB.
**Data consumed:** gated M5 -> M15/H1/H4/D1 causal, DEV 2021-07-27..2023-12-29 (selection), CALIB 2024-01..2024-06 (robustness only). Price-only. No 2025+/N4/V1/protected-2024/exogenous. loader sha `cbb6eebe…`, manifest 2.7.94.

**Failures & lessons:**
- Reversion (F2) and neutral breakout (F1) confirmed dead at the SWING horizon too — extends the intraday lesson upward.
- Temporal/calendar (F3) — a genuinely new non-price information class — is too weak/tail-carried on 2.5y.
- Time-based drift (F4) is real but fragile and = the frozen LONG trend-beta (near-miss, not new).
- **Positive lesson:** volatility-compression × confirmed-HTF-trend is the productive interaction (F5).

**Survivor:** `COMP-CONT-L-rr2` (LONG, D1-uptrend regime-specific). STRESS avgR +0.443, PF 1.94, best-10%-removed +0.246, DISC +0.52/CONF +0.33, all 3 years positive, CALIB 2024 +0.223. Full package: `ALPHA_XAUUSD_COMP_CONT_L_CANDIDATE_REPORT.md`, `COMP_CONT_L_STRATEGY_SPEC.md`, `comp_cont_L_package.json`. impl_fp `c60357cb…`, ledger_fp `98a8b906…`.

**Action:** per §35 active search STOPS on this first robust candidate; handed to Statistician for independent validation. Global program remains **ACTIVE**.

**Next frontiers queued (for after validation, if CEO restarts the loop):**
1. **Overlap quantification** of COMP-CONT-L vs the actual frozen LONG ledgers (needs those ledgers) — decide if it adds real portfolio opportunity or is redundant beta.
2. **Compression × other HTF states** (compression at a D1 structural level; compression after a D1 transition) — extend the ONE productive interaction, bounded budget.
3. **Portfolio SHORT gap** — repeatedly unfilled on this population (regime-locked). Candidate flag: `EXOGENOUS_FRONTIER_REQUIRES_CEO_AUTHORIZATION` OR a different (range-bound / older) price-only population — both need CEO authorization (§18, §36). Recorded, loop NOT stopped for it.
4. **Vol-state as a filter on the frozen trend-beta** (research-only, no frozen-strategy change) — does compression-timing lift the frozen survivors' robustness? (analysis, not retune).

---

## CHECKPOINT #2 — 2026-08-22 — post-survivor resume (CEO addendum: freeze + continue)
**Action on prior survivor:** `COMP-CONT-L-rr2` registered **`FROZEN_PENDING_INDEPENDENT_VALIDATION`** at commit `4082c5c` — removed from active research; no retune/retest/clone (§2 addendum). Global loop **CONTINUED immediately** (did NOT stop on the survivor, §1/§12 addendum).
**Frontiers this cycle:** 2 new (F6-CRASHMOM, F7-PDHBREAK). **Hypotheses:** H15–H18. Both **CLOSED_NO_ROBUST_ALPHA**.
**Data consumed:** same gated M5 -> H4/D1 DEV population; CALIB used ONLY as robustness readout (never selection). Firewall intact; no 2025+/N4/V1/protected-2024/exogenous.

**Diversification targets attacked (per addendum §7) and outcomes:**
- **SHORT (most-wanted):** F6 crash-momentum short = DEAD. This is the **7th** falsified SHORT mechanism class (after short-specialist ×26, transition-S, range-S, F4-S, F5-S). Down-spikes revert; even 2022 negative. **Bounded conclusion (§37): no robust price-only SHORT exists on the 2021–2023 DEV population** — the market is structurally bid. NOT a universal-impossibility claim.
- **FREQUENCY / low-overlap LONG:** F7 PDH-breakout = DEAD on DEV (noise-stopped, advFirst 0.73). Faster LONG events revert to the tight-stop trap; only the swing-scale wide-stop LONG survives. Frequency cannot be bought by shrinking the stop.

**Standing scientific state (2 turns + full graveyard, ~18 loop hyps + 60+ prior):** the ONLY robust price-only edge on this population is **swing-scale LONG trend-continuation with wide (~190p) structural stops**, now **saturated** (COMP-CONT-L frozen this loop + prior TR-rng2trend-L / HR-TU-pb-L / MT-dispaccept-L). SHORT/RANGE/reversion/temporal/faster-LONG are comprehensively falsified. Cloning LONG-beta is forbidden (§9).

**DECISION POINT (not a global stop — loop remains ACTIVE):** the non-redundant, robust, *diversifying* frontiers the CEO most values (SHORT, uncorrelated, different-state) are **proven absent in the authorized 2021–2023 price-only DEV population**. The genuine highest-value next frontiers require a **CEO data-governance decision**, recorded as authorization-gated (NOT self-authorized):
1. `DIFFERENT_PRICE_ONLY_POPULATION_REQUIRES_CEO_AUTHORIZATION` — a genuinely range-bound / older / bearish price-only population where SHORT and mean-reversion could live (cf. H4-bo-raw-S found its SHORT edge on 2011–2018). Would open real diversification without exogenous data.
2. `EXOGENOUS_FRONTIER_REQUIRES_CEO_AUTHORIZATION` (§18) — macro/DXY/yields/positioning, repeatedly identified as gold's likely true driver; strictly outside the current price-only firewall.

**What I did NOT do (anti-overfit, §4/§11):** did not mine thresholds after mechanism failure; did not manufacture a SHORT or a frequency edge; did not promote the CALIB-positive-but-DEV-negative F7 (that would be CALIB-fishing); did not clone LONG trend-beta.

**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`. Frozen pending-validation: `COMP-CONT-L-rr2`. Next productive frontier is CEO-authorization-gated per the two options above; awaiting a data-scope decision to continue with a non-redundant prior, rather than spend search budget on near-zero-prior price-only tests on the exhausted population.

---

## CHECKPOINT #3 — 2026-08-22 — external S2/S4 priority replication (both NOT_SUPPORTED)
**Priority frontier:** independently formalize + falsify two externally-supplied strategies (S2 range breakout, S4 sweep reversal). External win-rates (52%/67%/"9/9") treated as non-evidence; rules FROZEN in `EXTERNAL_RULE_MAPPING.md` before results.
**Hypotheses:** H19–H28 (10). **Verdicts:** `S2_NOT_SUPPORTED`, `S4_NOT_SUPPORTED`, `S4_TREND_ALIGNED_SUBFAMILY_NOT_SUPPORTED`.
**Key findings:** S2 gold false-breaks close-based boxes (advFirst 0.72-0.89), free-path & volume increments make it WORSE; S4 reclaims fail (advFirst 0.84-0.91), tight stops noise-stopped, overlays don't rescue; the predeclared "golden pattern" trend-aligned subfamily is the WORST cell. Full report: `ALPHA_EXTERNAL_S2_S4_INDEPENDENT_TEST_REPORT.md`.
**Data:** gated M5 -> M15/H1/H4/D1 DEV; causal (next-bar-open, close_time HTF, shifted levels); no non-causal D1/H4 merge; M1/news excluded; CALIB untouched (nothing reached robustness). Deliverables: `s2_test.py`, `s4_test.py`, `external_common.py`, `EXTERNAL_RULE_MAPPING.md`.
**Action (§38):** both graveyarded with lessons; no freeze (no survivor); continuous loop CONTINUES. No parameter rescue / reinterpretation. Frozen pending-validation remains `COMP-CONT-L-rr2`. The standing data-scope decision point (Checkpoint #2: DIFFERENT_PRICE_ONLY_POPULATION or EXOGENOUS, both CEO-authorization-gated) is unchanged — the external replication did not open a new authorized price-only frontier with a positive prior.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #4 — 2026-08-22 — DIFFERENT_PRICE_ONLY_POPULATION authorized; historical b0/b1 opened
**Authorization:** CEO opened `DIFFERENT_PRICE_ONLY_POPULATION` (exogenous still closed). Resumed native /loop immediately.
**Setup (governance-first):** mechanically inventoried historical XAUUSD; wrote `ALPHA_EVIDENCE_CONSUMPTION_MAP.md` classifying every region; built a **separately-versioned CAUSAL loader `hist_data.py`** (HTF usable only after its bar fully closes; FEATURE_AVAILABLE_AT<=DECISION_TIME; asserted) — the legacy non-causal D1->H4 merge is NOT used; 2024+ PROTECTED excluded by assertion. Discovery territory = b0(2011-2013 incl 2013 bear)+b1(2016-2018), DISCOVERY_CONSUMED -> new-mechanism discovery only, NOT validation (§4).
**Frontiers this cycle:** HF1 (compression-timed SHORT continuation in D1 downtrend), HF2 (range mean-reversion in real range). **Hypotheses:** H29, H30. Both **CLOSED_NO_ROBUST_ALPHA**.
**Findings:** HF1 — bearish regime makes SHORT *less-dead* (2013 +0.52 @rr3) but NOT robust (tail-carried best10<0, block-inconsistent b0+/b1-, RR-fragile). HF2 — range-fade DEAD even in a genuine range (MAE>>MFE, best10<0). Failure-map lessons #14-15.
**Action (§16, §23):** both graveyarded with lessons; no freeze; loop CONTINUES immediately. Frozen pending-validation still COMP-CONT-L-rr2. Reporting/commit/telemetry are not terminal.
**Telemetry:** `ALPHA_LOOP_TELEMETRY.md`. NEXT_FRONTIER = HF3 (bearish breakdown-momentum trailing / downtrend pullback-short, distinct from H4-bo-raw-S & HF1) — runs next cycle.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.
