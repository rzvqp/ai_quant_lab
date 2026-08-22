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

---

## CHECKPOINT #5 — 2026-08-22 — historical b0/b1 bearish frontiers (HF3/HF4); HF4 robust-but-REDUNDANT
**Frontiers:** HF3 (pullback-EMA short + breakdown-momentum trailing), HF4 (transition-onset short + full vet). **Hypotheses:** H31-H34.
**HF3:** A pullback-EMA short = NEAR-MISS (both blocks+ @rr2 but best10<0, 2012/2017<0); B breakdown-momentum = DEAD.
**HF4 transition-onset short:** clears ALL internal gates — avgR +0.270 STRESS, PF 1.62, best5 +0.177, **best10 +0.075**, both blocks+ (b0 +0.09/b1 +0.57), DISC +0.16/CONF +0.44, allYr+ @rr3, maxDD -4.1R, favorable path (advF 0.47), neighborhood STABLE (all-positive grid), survives +1bar (+0.10). BUT **overlap vs frozen H4-bo-raw-S = 85% within 3d (same-day 53%)** -> `REDUNDANT_WITH_H4_BO_RAW_S`. Per §9/§30 NOT frozen (would duplicate the frozen candidate). Also CALIB-flat (+0.005) + delay-sensitive.
**Lessons (failure-map #16-17):** bearish-short on b0/b1 is SATURATED by the frozen H4-bo-raw-S event (multiple triggers converge on the same down-legs); a signal can pass every robustness gate yet be non-alpha (redundant) — independence needs the overlap check, not just the gates.
**Action:** HF3 graveyarded; HF4 recorded REDUNDANT (not frozen); loop CONTINUES. Frozen pending-validation still COMP-CONT-L-rr2. NEXT_FRONTIER = HF5 (counter-trend long-reversion after capitulation / high-vol event alpha — genuinely different, low prior). 
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #6 — 2026-08-22 — HF5 dead; b0/b1 bounded near-exhaustion assessment
**Frontier:** HF5 (counter-trend LONG reversion: capitulation-bounce + down-spike-fade). **Hypotheses:** H35, H36. Both **CLOSED_NO_ROBUST_ALPHA**.
**Finding:** mean-reversion dead on b0/b1 in both directions; down-spike reversion is a 2021-23 bid-market artifact (continues on b0/b1). 
**Bounded assessment (§37, NOT universal impossibility):** across 5 historical SWING frontiers (HF1-HF5) covering bearish-short (compression/pullback/breakdown/transition), range mean-reversion, and counter-trend long-reversion, **the ONLY robust price-only edge on b0/b1 is the already-frozen H4-bo-raw-S short event** (new bearish-short triggers are redundant with it; long-trend-onset is redundant with TR-rng2trend-L). No NEW non-redundant robust price-only alpha emerged.
**Authorized price-only discovery territory remaining:** 2021-23 native (exhausted); b0/b1 (major SWING classes now explored); 2014-15/2019 MISSING; 2020-21 CALIB readout-only; 2024-25 PROTECTED. Genuinely-distinct untested price-only angles on b0/b1 are thin (temporal/gap, position-horizon) and low-prior; further same-class variants would be mining (forbidden §17).
**Action:** loop CONTINUES (mandate: negatives are not blockers). NEXT_FRONTIER = HF6 (D1 overnight/gap directional on b0/b1 — a genuinely different temporal-structural class, low prior). If HF6 also fails, the honest signal to CEO is that the authorized price-only space is exhausted of new non-redundant robust alpha and the **exogenous frontier (CEO-gated) is the productive next lever** — surfaced for a CEO data-scope decision, loop still ACTIVE.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #7 — 2026-08-22 — HF6 closed; AUTHORIZED PRICE-ONLY SPACE EXHAUSTED -> CEO DATA-SCOPE DECISION POINT (auto-loop PAUSED, program ACTIVE)
**Frontier:** HF6 (D1 gap NOT_TESTABLE — synthesized D1 has no gaps; day-after-big-day continuation near-miss best10<0/2018<0). **Hypotheses:** H37, H38.
**Bounded exhaustion (§37, NOT universal impossibility):** across the FULL authorized price-only space —
  - **2021-2023 native (M5->M15/H1/H4/D1):** 11 frontiers (F1-F7 + external S2/S4) -> ONE new robust survivor `COMP-CONT-L-rr2` (LONG); SHORT/range/reversion/temporal/faster-LONG dead.
  - **historical b0/b1 (H1/H4/D1 causal):** 6 frontiers (HF1-HF6) covering bearish-short (compression/pullback/breakdown/transition), range-fade, counter-trend long-reversion (capitulation/spike), temporal/gap, day-after-big-day -> NO new non-redundant robust alpha; the only robust bearish edge is the frozen H4-bo-raw-S (new triggers redundant with it, HF4 85%-within-3d); long-trend-onset redundant with TR-rng2trend-L.
  **Total: 17 frontiers / 38 hypotheses / ~250 configs this loop; 1 new independent survivor (COMP-CONT-L-rr2).**
**Remaining price-only options (all require a CEO data-scope decision — I will not self-authorize):**
  1. `INTRADAY_HISTORICAL_M15` on b0/b1 — AVAILABLE (raw M15 ~52k bars each) but GOVERNANCE-UNRESOLVED (raw M15 vs ratified `_from_M15_v2`; file bleeds into PROTECTED 2024+); LOW prior (intraday exhausted on 2021-2023).
  2. A genuinely different authorized price-only population — none obviously available in the repo beyond the above.
  3. `EXOGENOUS_FRONTIER` (DXY/yields/positioning/news) — repeatedly identified as gold's likely true driver; **the highest-prior productive lever for NEW diversifying alpha**, but CEO-authorization-gated (§22).
**Decision (§36 governance-gated, mandate-authorized pause):** continuing on the authorized price-only space would be mining low-prior b0/b1 variants (forbidden §17) or launching the governance-unresolved M15-intraday sub-program without authorization. So the auto-loop is **PAUSED at this decision point**; the **global program remains ACTIVE** for CEO redirection. Not a claim of impossibility — a bounded statement that the *authorized price-only* space is exhausted of NEW non-redundant robust alpha.
**CEO decision requested:** (a) authorize `EXOGENOUS_FRONTIER`; (b) authorize `INTRADAY_HISTORICAL_M15` for b0/b1 discovery (resolve the raw-M15 governance question); (c) point Alpha at another authorized price-only population; or (d) accept the portfolio as-is (S5 validated + COMP-CONT-L-rr2 & H4-bo-raw-S pending independent validation) and hold. On any of (a)-(c) the loop resumes immediately.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE` (auto-loop paused, awaiting data-scope decision).

---

## CHECKPOINT #8 — 2026-08-22 — INTRADAY_HISTORICAL_M15 authorized; loader governance-proven; M15-F1 closed
**Authorization:** CEO authorized `INTRADAY_HISTORICAL_M15` on b0/b1 (exogenous still prohibited). Loop resumed immediately.
**Governance-first (§2-§4):** built `hist_m15_data.py` — reads RAW M15 but SLICES b0+b1 BEFORE features; **governance boundary PROVEN** (105,255 rows: b0 52,404 + b1 52,851; 2011-07-26..2018-04-06; ZERO protected/CALIB/gap/outside rows, asserted -> else DATA_GOVERNANCE_BLOCKER). Causal H1/H4/D1 aggregated from the same slice (close_time<=decision_time; coverage 1.0). Legacy merge NOT used.
**Frontier:** M15-F1 displacement->first-pullback->resumption (both sides, H4-regime-gated). **Hypotheses:** H39, H40. **CLOSED_NO_ROBUST_ALPHA.**
**Finding:** high-frequency (~16/mo) but LONG dead (WRt 0.16) and SHORT marginal-but-fails-gate (best10<0, CONF<0, block-inconsistent, 2013-bear-driven ~ redundant). **Intraday tight stops (47-52p) are noise-stopped even in b0/b1's trending regimes -> the 2021-23 intraday exhaustion is a STRUCTURAL noise/stop property, not regime-specific (answers §5's regime-dependence question: intraday continuation is NOT regime-rescued).** Failure-map #20.
**Action:** loop CONTINUES. NEXT_FRONTIER = M15-F2 (session-based: session impulse->reset->second leg, §7E — b0/b1 session behavior untested; a genuinely different intraday structure). Frozen pending-validation still COMP-CONT-L-rr2.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #9 — 2026-08-22 — HISTORICAL_M15_PRICE_ONLY_FRONTIER_EXHAUSTED -> CEO decision point (auto-loop PAUSED, program ACTIVE)
**Frontiers:** M15-F2 (session impulse->reset->second-leg, London/NY), M15-F3 (break->acceptance->first-retest). **Hypotheses:** H41, H42. Both **CLOSED_NO_ROBUST_ALPHA**.
**M15 frontier summary (3 genuinely-distinct classes, all NOT robust):** F1 displacement-pullback (WRt 0.16, tight 47p noise-stopped), F2 session-2nd-leg (WRt 0.02-0.16, 39-54p stop noise-stopped), F3 break-accept-retest (WRt 0.03-0.06, 19-20p stop noise-stopped). Same signature across all: intraday tight stops noise-stopped, best10<0, regime-independent.
**Decisive structural conclusion (§23, NOT universal impossibility):** `HISTORICAL_M15_PRICE_ONLY_FRONTIER_EXHAUSTED`. Any M15 mechanism uses TIGHT intraday stops (noise-stopped -> dead) OR WIDE swing stops (-> REDUNDANT with the frozen H4 edges COMP-CONT-L / H4-bo-raw-S). Intraday alpha is NOT regime-dependent in the way hoped (§5 answered: the 2021-23 intraday exhaustion is structural noise/stop, confirmed on b0/b1). No NEW non-redundant robust price-only alpha on M15.
**Full authorized price-only space now covered:** 2021-23 native (11 frontiers -> COMP-CONT-L-rr2), historical b0/b1 SWING (HF1-HF6 -> none new; only frozen H4-bo-raw-S robust), historical b0/b1 INTRADAY M15 (F1-F3 -> none, structural noise wall). **19 frontiers / 42 hypotheses this loop; 1 new independent survivor (COMP-CONT-L-rr2).**
**`EXOGENOUS_FRONTIER_REMAINS_NEXT_HIGH_PRIORITY_OPTION`** — repeatedly identified as gold's likely true driver and the natural home for an uncorrelated strategy; CEO-authorization-gated (§22/§23).
**CEO decision requested:** (a) authorize `EXOGENOUS_FRONTIER`; (b) point Alpha at another genuinely-different authorized price-only population/data object; (c) accept portfolio as-is (S5 validated + COMP-CONT-L-rr2 & H4-bo-raw-S pending independent validation) and hold. Loop resumes on (a)/(b).
**Per §23, auto-loop PAUSED at this governance-gated decision point; global program ACTIVE.** No mining of M15 variants (structural wall makes them near-zero-prior); no self-authorized exogenous use.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE` (auto-loop paused, awaiting decision).

---

## CHECKPOINT #10 — 2026-08-22 — EXOGENOUS_FRONTIER authorized; DXY gate FAILED -> EXOGENOUS_DATA_GOVERNANCE_BLOCKER (auto-loop paused, program ACTIVE)
**Authorization:** CEO authorized `EXOGENOUS_FRONTIER` (new mandate `ALPHA-XAUUSD-EXOGENOUS-CONTINUOUS-LOOP-001`). Addendum: DXY DATA AVAILABILITY GATE before any DXY hypothesis.
**Gate result (mechanical inventory of the entire authorized data environment):** `DXY_DATA_NOT_AVAILABLE`. No DXY / yields / real-yields / curve / rate-expectations / COT / fund-flow data exists anywhere. Only exogenous data present = `ff_calendar_2026-W32` (99 rows, 2026) + `NEWS_LEDGER.csv` (506 rows, ~2026-08) -> 2026 protected-future, quarantined/unratified, ZERO overlap with any authorized XAUUSD research period. Double-blocked.
**Verdict:** `EXOGENOUS_DATA_GOVERNANCE_BLOCKER` (§27 genuine blocker) — no authorized exogenous research can be performed without fabricating/substituting data (forbidden §3/§4/addendum) or using protected+quarantined+non-overlapping data. NOT a claim that exogenous alpha is impossible; the DATA to test it does not yet exist in the authorized environment.
**Constructive deliverables:** `ALPHA_EXOGENOUS_EVIDENCE_MAP.md` (class-by-class), `ALPHA_EXOGENOUS_DATA_REQUIREMENTS.md` (exact datasets + coverage/timestamp/vintage spec, priority-ranked; minimal viable = one ratified DXY H1 series over b0/b1 unblocks X1/X3/X4), `ALPHA_EXOGENOUS_FRONTIER_REGISTRY.md` (X1-X6 frozen, BLOCKED_NO_DATA), `ALPHA_EXOGENOUS_HYPOTHESIS_REGISTRY.md` (0 tested).
**CEO action requested:** provision (via Data Acquisition, ratified) at least one historical exogenous series covering b0/b1 (or 2021-2023) per the requirements spec — a ratified DXY H1 series is the highest-leverage single unblock. Loop resumes immediately on provisioning.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE` (auto-loop paused at genuine data blocker).

---

## CHECKPOINT #11 — 2026-08-22 — state-path method (new mandate); Stage-A univariate information map
**Authorization:** CEO paused DXY/exogenous; issued `ALPHA-XAUUSD-CAUSAL-STATE-PATH-DISCOVERY-001` — change discovery METHOD to outcome-first state->future-path information mapping (price-only). Loop resumed.
**Built `state_path.py`:** causal first-passage engine P(+X before -Y) per bar + MFE/MAE, multi-horizon, LONG/SHORT separate, on 2021-2023 native H1 DEV (N=10,168). Raw causal price-state features only (excludes untrusted canonical RANGE/N1-N6 MI). Baselines recorded (`ALPHA_PATH_BASELINES.md`).
**Stage-A univariate map (`ALPHA_STATE_INFORMATION_MAP.md`):** 10 state vars x 2 sides x 2 horizons on headline P(+100/-70).
**Key finding:** `trend`=(EMA20-EMA50)/ATR is the dominant causal state — strongly-extended-up = EXHAUSTION: LONG P(+100/-70) drops to 0.313 (-0.105 vs base 0.418) and SHORT P rises to 0.472 (+0.081 vs base 0.391, +21pct, monotone, both horizons). Secondary: vol_ratio/vol_change (high vol favors trend-continuation), effic (monotone SHORT gate). `ST-TREND-EXH` registered PROMISING_UNIVARIATE (potential SHORT diversifier + LONG-avoidance filter; counter to LONG trend-beta so not obviously redundant).
**Discipline:** promising != confirmed — NOT yet per-year/DISC/CONF-validated (the SHORT lift may be 2022-concentrated). No strategy geometry imposed (§3). No thresholds mined (continuous decile response). MT ledger updated (~40 univariate screens; winner selected by cross-consistency).
**NEXT:** stability of ST-TREND-EXH (per-year + DISC/CONF + neighboring-region + cross-population b0/b1) + multi-horizon response curve + small interaction (extension x vol/efficiency). Only if it survives -> Stage-C strategy conversion + overlap-vs-frozen.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #12 — 2026-08-22 — ST-TREND-EXH validated -> KILLED (stability firewall); pivot to transitions
**Rigorous validation of the Stage-A univariate winner** (`state_validate.py`): per-year, DISC/CONF, multi-horizon, neighboring thresholds, cross-population b0/b1, interactions.
**Verdict: `INFO_UNSTABLE_KILLED`.** DISC lift +0.081 -> **CONF lift -0.076** (SHORT information INVERTS out-of-sample; decisive §14 kill). Per-year 2021 +0.074 / 2022 +0.122 / **2023 -0.029** (2021-22 transient). Cross-pop b0 -0.001 / b1 -0.032 (no generalization). DEV-wide lift small (+0.022); the "0.472" was the extreme top decile; interactions sharpen the same in-sample effect.
**Interpretation:** the single most-informative STATIC univariate causal price-state on 2021-2023 H1 carries only a 2021-22 regime-transient, not stable path information. The METHOD worked (flag -> validate -> reject); the stability firewall did its job. No strategy built (info-first gate not passed, §16/§13).
**NEXT:** state-TRANSITION family (§8) — build A(t-k)->B(t) transition screens with the first-passage path outcome AND DISC/CONF + cross-population FROM THE OUTSET (test stability early to avoid another in-sample-only candidate). Also map baselines on b0/b1 for cross-pop context.
**Not a blocker (§26):** the causal-state information space is still being mapped; this is one static-state family closed.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #13 — 2026-08-22 — state-TRANSITION family screened (stability built-in); no positive tradeable edge
**Screen:** 9 causal transitions A(t-6)->B(t) x 2 sides on 2021-2023 H1 DEV, headline P(+100/-70) H48, with per-year + DISC/CONF stability evaluated IN the screen (`state_transitions.py`) — applying the ST-TREND-EXH lesson to avoid another in-sample-only candidate.
**Result:** the ONLY stable transition is `T3 up-efficiency->drop` = a LONG-AVOIDANCE FILTER (lift -0.069, DISC -0.088/CONF -0.041, per-year negative) — a stable negative signal, NOT a standalone tradeable edge, and it re-encodes trend-drive presence (COMP-CONT-L territory). Every apparent POSITIVE edge (T9-S trend-weaken, T5-L accept-up, T3-S) is a regime transient (DISC->CONF inversion or single-year); T8-S promising both-halves-positive but N=91, 2023-only (insufficient).
**Conclusion:** no stable POSITIVE tradeable path-lift from static states (ST-TREND-EXH) or transitions on 2021-2023 H1. The stable price-only state information reduces to "trend-drive presence" (already exploited by COMP-CONT-L). NOT price-only-impossible (§26) — 2 of several state families mapped.
**NEXT:** PATH-HISTORY states (causal MFE/MAE-so-far, recent realized asymmetry before decision) — a genuinely different information class (§5 "MFE/MAE history available before decision"); then multi-TF / session-conditioned states. Cross-population b0/b1 for any stable positive.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #14 — 2026-08-22 — path-history family: first stable-positive DEV signal -> KILLED by cross-population; REGIME-CONDITIONAL meta-finding
**Screen:** 10 causal path-history states (realized-eff, pullback-depth, MFE/MAE-so-far, asymmetry, time-since-new-extreme) x 2 sides on 2021-2023 H1 DEV, headline P(+100/-70) H48, per-year + DISC/CONF stability in-screen (`state_pathhist.py`).
**Found:** the "clean recent advance near highs -> exhaustion" family is within-DEV STABLE — clean_up/shallowPB_up SHORT +0.035/+0.039 (all years + DISC/CONF), LONG-avoidance -0.156. **First stable POSITIVE tradeable lift in the whole state program.**
**Cross-population (b0/b1) — DECISIVE KILL (`state_pathhist_xpop.py`):** lift INVERTS (b0 -0.009/-0.026; b1 -0.044/-0.052). The signal is a 2021-2023 bid-market-regime property, not general.
**META-FINDING:** causal price-state->path relationships on XAUUSD are **REGIME-CONDITIONAL, not stationary**. A signal can pass the full within-period gate (per-year + DISC/CONF) yet INVERT cross-regime. Within-period per-year splits share the macro-regime -> within-period stability is necessary but NOT sufficient; **cross-population is the decisive generalization test.** Explains why general price-only alpha is elusive and why the frozen survivors are regime-specific. This is the honest map (§26).
**NEXT:** multi-TF state family (H4/D1 causal state conditioning H1 path) + session-conditioned states — with cross-population as a first-class gate from the outset. After that the causal-state information space is substantially mapped; a bounded, evidence-backed conclusion (regime-conditional non-stationarity) can be presented to CEO.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #15 — 2026-08-22 — state-path map COMPLETE (5 families); bounded regime-conditional conclusion -> CEO decision (auto-loop paused, program ACTIVE)
**Completed:** multi-TF (HTF state -> H1 path: no cross-stable edge; trend-beta ~0 on b0) + session-conditioned (London-SHORT/NY-LONG stable but IMMATERIAL, +0.002..0.012 cross-pop). Full state-path map now spans 5 families (static / transition / path-history / multi-TF / session).
**Central finding:** causal price-only state->path relationships on XAUUSD are REGIME-CONDITIONAL, not stationary. Material DEV lifts (trend-extension, clean-advance exhaustion) INVERT cross-population; the only cross-pop-stable effects are a faint untradeable session microstructure + trend-drive presence (redundant with frozen COMP-CONT-L). No material cross-population-stable non-redundant positive price-only state->path edge exists in the mapped space.
**Methodological result:** within-period stability is necessary but NOT sufficient (per-year splits share the macro-regime); CROSS-POPULATION is the decisive generalization gate. Now standard for all future candidates.
**Deliverable:** `ALPHA_STATE_PATH_BOUNDED_CONCLUSION.md` (whole map + method result + CEO options). Per §26 this is a BOUNDED conclusion with the full information map attached — NOT PRICE_ONLY_ALPHA_IMPOSSIBLE.
**CEO decision requested:** (1) re-authorize EXOGENOUS with provisioned data (most likely source of a stationary uncorrelated signal; blocked only on data); (2) accept the regime-specific portfolio (S5 + COMP-CONT-L-rr2 + H4-bo-raw-S) with a regime-detection overlay (separate mandate); (3) authorize a genuinely different ratified price-only population. Loop resumes on any.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE` (auto-loop paused at decision point).

---

## CHECKPOINT #16 — 2026-08-22 — NEW mandate: regime-conditional method; causal regime taxonomy FROZEN + reproducible + baselines
**Authorization:** CEO accepted the regime-conditional finding; issued `ALPHA-XAUUSD-REGIME-CONDITIONAL-STATE-PATH-DISCOVERY-001`. Generalization gate CHANGED: same-regime cross-era (not same-sign across different regimes). DXY/exogenous stays PAUSED (ignore acquisition_staging/dxy). Loop resumed.
**Foundation (Stage 1) done:** built + FROZE a causal price-only regime taxonomy (`state_regime.py`): UP/DOWN/QUIET/CHOP/TRANSITION from eff/trend/vr (all causal; QUIET is research-local, NOT canonical RANGE; no MI retuning). **Reproducibility EXCELLENT** — every regime occurs 8-34% in EVERY era (2021/2022/2023 + b0/b1), near-identical frequencies; DOWN recurs in all eras (b0 11.9%/b1 11.6%) enabling same-regime cross-era SHORT validation. Regime-conditional path baselines established (`ALPHA_REGIME_PATH_BASELINES.md`): regime BASE rates are stable across eras (DOWN-SHORT ~0.40-0.41 both eras; QUIET-SHORT ~0.40-0.41) — unlike the raw state->path lifts that inverted.
**Status corrections recorded:** H4-bo-raw-S = INDEPENDENT_VALIDATION_BLOCKED (non-causal legacy D1 filter) -> reference/overlap only. Clean frozen = S5 (validated) + COMP-CONT-L-rr2 (pending).
**Artifacts:** ALPHA_CAUSAL_REGIME_MAP, ALPHA_REGIME_PATH_BASELINES, ALPHA_REGIME_STATE_INFORMATION_MAP, ALPHA_REGIME_TRANSITION_MAP, ALPHA_REGIME_STRATEGY_REGISTRY.
**NEXT:** within-regime state discovery — priority DOWN & QUIET regimes (SHORT), where cross-era base rates are most consistent: find causal states lifting SHORT materially above the same-regime base, validate DEV vs b0/b1 same-regime. Then regime transitions (§27). LONG/SHORT separate; material lift + sample honesty + DISC/CONF.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #17 — 2026-08-22 — within-regime SHORT discovery (DOWN, QUIET): no material same-regime-stable edge
**Screen:** 8 causal states x 2 priority regimes (DOWN, QUIET) SHORT, DEV lift over same-regime base + within-regime DISC/CONF + per-year + SAME-REGIME cross-era b0/b1 (`state_regime_discover.py`).
**Result:** strongest = DOWN + falling-vol -> SHORT +0.097 DEV (all 3 years positive, DISC +0.11/CONF +0.08 — flawless within-period) BUT same-regime cross-era FAILS (b0 -0.029, b1 -0.001). QUIET fresh-down-impulse same-sign across all eras (+0.032/+0.042/+0.013) but IMMATERIAL (<0.04) + 2021-inconsistent. No material same-regime-stable SHORT candidate.
**Deepened meta-finding:** state->path lifts are era-dependent EVEN WITHIN a fixed causal regime. Same-regime cross-era is a strict, genuine generalization gate; within-period stability (even flawless across all years + DISC/CONF) remains insufficient.
**NEXT (do not stop, §30):** UP/CHOP regimes LONG + regime-TRANSITION family (§27, boundary A->B — may hold more path info than persistent states). Same-regime / same-transition cross-era gate throughout.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #18 — 2026-08-22 — regime + transition sweep COMPLETE; only stable edge = the frozen COMP-CONT-L (re-discovered) -> CEO decision (auto-loop paused, program ACTIVE)
**Completed:** UP/CHOP LONG within-regime + 8-transition family (§27). **Only same-transition-cross-era-STABLE positive = QUIET->UP LONG (+0.099 DEV/+0.048 b0b1)** — but tiny N (40/72, §16) AND REDUNDANT with COMP-CONT-L (compression->uptrend thesis). Every other regime/transition signal is regime-transient (fails same-regime cross-era), a stable avoidance filter, immaterial, or insufficient-N.
**Central conclusion (bounded, §26):** NO new non-redundant material same-regime(-transition)-stable price-only edge. The one stable positive is the already-frozen COMP-CONT-L edge -> the regime-conditional method INDEPENDENTLY CONFIRMS COMP-CONT-L as a genuine QUIET->UP regime-transition LONG. Deeper result: price-only state->path is era-dependent EVEN WITHIN a fixed causal regime (a regime label is insufficient for portability). NOT price-only-impossible.
**Deliverable:** `ALPHA_REGIME_CONDITIONAL_BOUNDED_CONCLUSION.md` (method + findings + CEO options).
**CEO decision requested:** (1) send COMP-CONT-L-rr2 to independent validation (now doubly-confirmed); (2) re-authorize exogenous with provisioned data (DXY staging appeared); (3) accept regime-specific portfolio + regime-router overlay. Loop resumes on any.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE` (auto-loop paused at decision point).

---

## CHECKPOINT #19 — 2026-08-22 — NEW M15 mandate; Stage-1 M15 path baselines (engine + foundation)
**Authorization:** CEO issued `ALPHA-XAUUSD-M15-CAUSAL-STATE-PATH-DISCOVERY-001` — apply the information-first state->path method to M15 (H1 map bounded; M15 only ever tested via named patterns). DXY stays PAUSED. Loop resumed.
**Stage 1 done:** built causal M15 first-passage engine (`state_path_m15.py`, sorted-threshold pointer) + unconditional path baselines (`ALPHA_M15_PATH_BASELINES.md`) on 2021-2023 gated M15 (N=40,649) + historical b0/b1 M15 (52k each; governance-proven, 2024+ excluded). Findings: M15 LONG/SHORT base rates near-SYMMETRIC (unlike H1 long-bias); natural excursion MFE/MAE med ~44-52p (b0/2021-23), ~31p (b1) -> structural M15 stop ~50-70p, NOT tight (§19); base rates strongly era-dependent (b1 much quieter) -> same-regime-conditional baselines required.
**NEXT:** M15 univariate state info map (efficiency/displacement/vol/compression/pullback/path-cleanliness/MFE-MAE-asymmetry) for P(+70/-50) & P(+100/-70) lift over regime-conditional base + same-regime cross-era + event-dedup; then M15 TRANSITIONS (§8 priority: low-vol->expansion, inefficient->directional, etc.); H1/H4 causal context conditioning; session-conditioned (vs session base). LONG/SHORT separate. No named patterns, no tight-stop forcing.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #20 — 2026-08-22 — M15 state info map: FIRST cross-era-stable signal (high-vol -> M15 SHORT bias)
**Screen:** 16 causal M15 states x 2 sides -> P(+70/-50) 8h lift, event-deduped (raw vs effective-N), per-year + DISC/CONF + cross-era b0/b1 (`state_m15_discover.py`).
**BREAKTHROUGH:** the FIRST cross-era-stable signals in the entire H1+M15 program — all VOLATILITY-based. The directional one: **high/rising M15 volatility (ATR>1.3x norm, vc>1.2) -> M15 SHORT bias** (P(+70/-50) lift +0.058/+0.050, same-sign across 2021/2022/2023 + b0 + b1, DISC+CONF; vol_hi does NOT lift LONG -> genuine directional asymmetry, consistent with gold down-moves being faster in high-vol/risk-off). Other vol signals (vol_lo/vc_fall/compress) are symmetric quiet->avoidance filters. Registered ST-M15-HIGHVOL-SHORT = STABLE_INFO_TRADEABILITY_TBD.
**Honest caveat:** lift is stable but MODEST — high-vol SHORT P(+70/-50)=0.32 < 0.417 breakeven for that label. Stable INFORMATION; tradeability not yet established.
**NEXT:** characterize high/rising-vol SHORT expectancy across RR/targets (find net-positive geometry after STRESS cost, §18-19), effective-N/opportunities, same-regime recurrence, overlap vs frozen; sharpen via M15 transitions (low-vol->expansion) + H1/H4 context (does high-vol-short concentrate in a parent regime?) + session. If no RR is net-positive -> STABLE_INFO_NOT_TRADEABLE + continue. Do NOT force geometry.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #21 — 2026-08-22 — ST-M15-HIGHVOL-SHORT: univariate NOT tradeable; DOWN-parent-regime LEAD (+0.102 DEV)
**Characterization (`state_m15_highvol.py`, STRESS, event-deduped):** fixed brackets + structural ATR stops on DEV+b0+b1.
**Univariate = STABLE_INFO_NOT_TRADEABLE:** no geometry net-positive cross-era (DEV all neg, b1 all neg, b0 marginal +0.03). The stable +0.058 lift is sub-breakeven (P 0.32).
**LEAD:** high-vol-short CONDITIONED on H1 DOWN parent regime = +0.102 avgR DEV (WR .48, N=239, best10 -0.048 slightly tail-carried); UP/QUIET/CHOP/TRANSITION parents negative; raw down-disp interaction doesn't help. Economically high-vol confirms downtrend. `ST-M15-HIGHVOL-SHORT-DOWNPARENT` = LEAD_CROSS_ERA_TBD.
**NEXT:** DECISIVE same-regime cross-era check — DOWN-parent high-vol-short on b0/b1 (b0 has 2013 bear DOWN; b1 has little DOWN -> possibly INSUFFICIENT_SAME_REGIME_EVIDENCE). If material + cross-era-stable + non-redundant + sample-honest -> Stage-C freeze (REGIME-SPECIFIC SHORT candidate); else record honestly and continue to M15 transitions + other M15 states. Guarded: H1 DOWN shorts were era-unstable.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #22 — 2026-08-22 — DOWN-parent high-vol-short FAILS same-regime cross-era (b1 contradicts) -> not frozen
**Decisive check (`state_m15_downparent.py`):** DOWN-parent high-vol M15 short, STRESS, event-deduped.
- DEV (N=293): positive, best 2.0ATR rr1.0 avgR +0.112 WR .56 best10 +0.015 (14.7 tpm). b0 (N=469): sign-confirmed (+0.03..+0.13) but best10<0. **b1 (N=392): CONTRADICTS (all neg -0.11..-0.15).**
**Verdict: REGIME_SPECIFIC_INFO_NOT_CROSS_ERA_STABLE** — fails same-regime cross-era (§9). High-vol-short works when DOWN = genuine downtrend (DEV/b0 2013 bear) but fails when DOWN = correction in uptrend (b1). Consistent with the program-wide finding that price-only shorts are genuine-downtrend-specific. NOT frozen (b1 contradicts + b0 tail-carried). A sharper causal genuine-downtrend regime def MIGHT rescue it but would be P&L-fitting if defined post-hoc (§28) -> not pursued.
**NEXT (do not stop, §29):** M15 TRANSITIONS (§8: low-vol->expansion, inefficient->directional, extension->loss-of-continuation, pullback->renewed-efficiency) + deeper M15 states (displacement/pullback/path-cleanliness) + session-conditioned, all event-deduped + same-era cross-population gate.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #23 — 2026-08-22 — M15 transition family: no positive tradeable transition (only highvol->stab LONG-avoidance)
**Screen (`state_m15_transitions.py`):** 10 causal M15 transitions A(t-8)->B(t) -> P(+70/-50) lift, event-deduped, per-year + DISC/CONF + cross-era b0/b1.
**Result:** only CROSS_STABLE = highvol->stabilization -> LONG -0.068 (avoidance filter, not a trade). Every apparent positive transition fails cross-era (extUp->pullback S +0.039 but b0/b1 invert) or immaterial. No material cross-era-stable positive tradeable M15 transition.
**M15 map status:** volatility is the only cross-era-stable M15 information (high-vol -> down-bias; quiet -> targets unreached; highvol-stab -> avoid long) but none converts to tradeable positive alpha (univariate not tradeable; DOWN-parent short fails b1; transitions only avoidance). Deeper states (displacement/pullback/path-cleanliness/wick) were covered in the univariate map (only vol cross-stable). SESSION-conditioned = last untested family.
**NEXT:** session-conditioned M15 (state lift vs SESSION base, §13, cross-era + event-dedup); then present a BOUNDED M15 conclusion (whole M15 map) + CEO decision, §27 (NOT before session done).
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #24 — 2026-08-22 — Session-conditioned M15 (§13): NY-session high-vol->SHORT survives b1 (first directional cross-era-stable M15 candidate)
**Screen (`state_m15_session.py`):** session structural bias + session-open burst + high-vol-short concentration, all vs SESSION base, event-deduped, cross-era b0/b1.
**Findings:** (1) London bilateral +0.086L/+0.126S cross-stable = range-expansion (small consistent short tilt); Off 21-24 bilateral depression = stable avoidance filter. (2) NY-open first hour +0.173L/+0.162S cross-stable = volatility-timing burst. (3) **NY-session high-vol->SHORT +0.070 (b0+0.08/b1+0.05) = S_CROSS_STABLE — the FIRST directional M15 signal to survive the b1 gate**, because SESSION conditioning captures the mechanism where DOWN-parent conditioning failed b1.
**Registered:** ST-M15-NY-HIGHVOL-SHORT (CANDIDATE_PENDING_TRADEABILITY). Opposite direction to frozen COMP-CONT-L -> non-redundant.
**NEXT (decisive):** tradeability characterization of NY-session high-vol->SHORT — any geometry (fixed brackets / structural ATR stop, §19) net-positive STRESS expectancy cross-era (DEV+b0+b1), event-deduped? If yes -> Stage-C freeze (REGIME/STATE_SPECIFIC_FROZEN_PENDING_INDEPENDENT_VALIDATION) + notify CEO. If no -> bounded M15 conclusion + CEO decision (§27).
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #25 — 2026-08-22 — NY-session high-vol-short NOT tradeable -> BOUNDED M15 CONCLUSION (CEO decision requested)
**Decisive tradeability (`state_m15_ny_hvshort.py`):** NY-session high-vol M15 SHORT across 4 fixed brackets + 9 structural ATR stops x 3 eras (DEV/b0/b1), STRESS, event-deduped. ALL net-NEGATIVE (best DEV avgR -0.034 w/ losing 2022 -0.16; b0 -0.021; b1 -0.088); best10 -0.15..-0.38 everywhere -> carried by outliers, no robust core. The +0.070 cross-era-stable P-lift is REAL info but does NOT convert to tradeable expectancy. ST-M15-NY-HIGHVOL-SHORT = INFO_CONFIRMED_CROSS_ERA_NOT_TRADEABLE (not frozen).
**M15 frontier status:** baselines + univariate states + transitions + session ALL systematically completed (§27). No tradeable cross-era-stable non-redundant standalone M15 edge exists. => BOUNDED M15 CONCLUSION written (`ALPHA_M15_BOUNDED_CONCLUSION.md`): the only cross-era-stable M15 information is volatility (timing/filter), which does NOT convert to standalone directional alpha; M15's evidenced role is a causal TRIGGER under a frozen HTF edge (COMP-CONT-L / S5), matching the CEO economic-profile directive.
**CEO DECISION REQUESTED (A/B/C):** A(rec)=pivot M15 to trigger-under-HTF-edge (test M15 vol-timing improving frozen HTF LONG entry); B=extend M15 to path-SHAPE/H4-conditioned axis; C=accept bounded negative, return to HTF/trigger track. Loop paused at this genuine decision point.
**Global status:** `ALPHA_M15_STANDALONE_FRONTIER_BOUNDED` — awaiting CEO A/B/C.

---

## CHECKPOINT #26 — 2026-08-22 — NEW MANDATE (Decision B): H4 parent-state taxonomy FROZEN + per-state M15 base rates
**Mandate:** ALPHA-XAUUSD-H4-M15-PATH-SHAPE-DISCOVERY-001. §3-4 foundation.
**Done (`h4_parent.py`):** froze causal H4 parent-state taxonomy (reused frozen regime() on the causal H4 frame; QUIET = research-local neutral, NOT canonical RANGE, §4); aligned H4 state to M15 causally (last-closed H4 bar); established per-H4-state M15 first-passage BASE RATES (P(+50/-50,+70/-50,+100/-70,+100/-100) L/S + adverse-first + MFE/MAE med/P75/P90), DEV/b0/b1, event-deduped with RAW/EffN/unique-days/independent-H4-episodes. Contract frozen in `ALPHA_H4_PARENT_STATE_CONTRACT.md`.
**Key facts locked in:** (1) all 5 H4 states have EffN>=500 in every era -> same-H4-state cross-era gate (§10) viable for all; (2) absolute base rates strongly era-dependent (b1 low-vol compresses all P + MFE/MAE) -> only WITHIN-state/era LIFTS are comparable (§8); (3) instantaneous H4 state alone = era-dependent directional bias (UP DEV short-favor/b1 long; DOWN DEV long/b0 short; QUIET symmetric) -> NOT standalone cross-era alpha. The open question: does M15 PATH-SHAPE conditional on H4 add cross-era-stable lift over these baselines?
**NEXT:** first M15 path-shape family (directional run-length / persistence-vs-alternation, window 4/8) conditional on each H4 state, lift vs per-state/era base rate, L/S separate, event-deduped, cross-era gate.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE` (new frontier).

---

## CHECKPOINT #27 — 2026-08-22 — Family 1 (run-length/persistence): no cross-era-stable positive lift over H4-state base
**Screen (`h4m15_runlen.py`):** M15 signed run-length + path-persistence (pe8/pe4) conditional on each H4 state; P(+70/-50 & +100/-70) lift vs same-H4-state deduped base, L/S separate, DEV DISC/CONF + per-year + b0 + b1, event-deduped.
**Result:** NO cross-era-stable positive tradeable lift. Only CROSS_STABLE = QUIET x runUp>=4 short -0.055 (a NEGATIVE short-avoidance signal, + within-DEV per-year sign flip -> weak). Strongest positive = DOWN x persistDn short +100/-70 +0.059 (D/C/b0 positive) but b1 ~0 -> era-conditional continuation, fails cross-era. "Pullback-in-uptrend -> LONG" NOT supported (UP x runDn LONG negative). Continuation shorts era-conditional (fail b1 low-vol), consistent with program-wide finding.
**NEXT:** Family 2 = impulse -> retracement geometry (recent impulse magnitude + retracement depth relative to it) conditional on H4 state; then recovery-after-adverse & MFE/MAE-asymmetry families.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #28 — 2026-08-22 — Family 2 (impulse->retracement geometry): FIRST cross-era-stable candidate (DOWN-H4 down-impulse-shallow -> SHORT)
**Screen (`h4m15_impretr.py`):** M15 impulse magnitude (W=8/16, ATR-norm) x retracement depth (shallow=continuation / deep=reversal) conditional on H4 state; P(+70/-50 & +100/-70) lift vs same-H4-state base, L/S separate, DISC/CONF+per-year+b0+b1, event-deduped.
**Result:** FIRST cross-era-stable positive candidate of the mandate. **DOWN x impDn8&shallow -> SHORT +70/-50 = +0.055** (DISC +0.03/CONF +0.08; b0 +0.04/b1 +0.03 — survives incl b1 low-vol era; per-yr 2021 +0.12/2023 +0.05; +100/-70 & W=16 neighbor also +; coherent mirror). Registered ST-H4DN-M15DNIMP-SHALLOW-SHORT (INFO_CROSS_STABLE_PENDING_CHARACTERIZATION). Note: the research-bracket lift is INFORMATION, not yet tradeable expectancy. Other cells fail (QUIET impUp16 short reverses on b0/b1 = era-transient).
**NEXT (characterization):** §8 full outcome distribution; §14-15 STRUCTURAL-STOP strategy (recent M15 swing high / ATR from observed MAE, NO forced RR), net STRESS expectancy cross-era DEV/b0/b1 event-deduped; §16 frequency; §17 independence vs S5/COMP-CONT-L. If net-positive + non-redundant -> Stage-C freeze + notify CEO; else record + continue path-shape families.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #29 — 2026-08-22 — ST-H4DN-M15DNIMP-SHALLOW-SHORT characterized: NOT a tradeable survivor (expectancy era-conditional)
**Characterization (`h4m15_dnimp_char.py`, §8/§14/§15/§16/§17):** structural stop = recent 8-bar M15 swing high (med 42/62/30p DEV/b0/b1 — genuine, not tight); net STRESS expectancy cross-era, event-deduped, predeclared rr set (no mining).
**Result:** tradeable ONLY in b0 (strong-downtrend high-vol: avgR +0.089..+0.200, best10 ~0); DEV breakeven-negative (best rr3.0 -0.015, DISC -0.047/CONF +0.032 disagree, losing 2022); b1 negative (-0.02..-0.05, best10 -0.15..-0.35). The cross-era-stable RELATIVE info lift does NOT convert to cross-era-stable EXPECTANCY — DOWN-state base rate + follow-through scale with era volatility (b1 MFE med 32p vs b0 59p). Fails robust-survivor bar (§22); NOT frozen; NOT rescued by vol-sub-cutting DOWN (would re-tune frozen H4 taxonomy, §3). Independence vs COMP-CONT-L: 4/72 shared-days, opposite direction (non-redundant, moot).
**Central lesson (recorded):** cross-era-stable relative INFORMATION != cross-era-stable tradeable EXPECTANCY; absolute expectancy is gated by era volatility/follow-through even when the relative lift is stable.
**NEXT:** Family 3 = recovery-after-adverse-excursion / successive MFE-MAE asymmetry / volatility-expansion->controlled-retracement, conditional on H4 state.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #30 — 2026-08-22 — Family 3 (recovery/asymmetry/vol-exp-calm): no cross-era-stable candidate
**Screen (`h4m15_recovery.py`):** M15 dip-recover/pop-fade + intrabar MFE-MAE asymmetry + vol-expansion->calm conditional on H4 state; P(+70/-50 & +100/-70) lift vs same-H4-state base, L/S separate, DISC/CONF+per-year+b0+b1, event-deduped.
**Result:** NO cross-era-stable candidate. Strongest = UP x dipRecovUp -> LONG +0.059 (absorption; DEV-robust all-years + DISC +0.06/CONF +0.06 + coherent mirror) but b0 +0.02 marginal / b1 -0.01 -> era-conditional, fails. DOWN x asymDn short +0.047 fails b1 (flat). Meta-pattern F1-F3: continuation edges work high-vol/trend eras & fail b1; reversal/absorption edges work DEV & fail hist. Binding constraint = b1 low-vol lacks follow-through.
**NEXT:** Family 4 = HH/HL vs LH/LL structural swing-sequence + wick/body sequence asymmetry (microstructure) conditional on H4 state.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #31 — 2026-08-22 — Family 4 (swing-sequence + wick): only vol-structure cross-era-stable (non-directional); convergence with standalone-M15
**Screen (`h4m15_swingwick.py`):** M15 HH/HL block structure + wick asymmetry conditional on H4 state; P(+70/-50 & +100/-70) lift vs same-H4-state base, L/S separate, DISC/CONF+per-year+b0+b1, event-deduped.
**Result:** 2 CROSS_STABLE flags but both non-directional: (1) CHOP x HH_LL(expand) short +0.049 = BILATERAL range-expansion (long side also +0.041; CHOP has no directional H4 thesis for §15) = VOL_TIMING_NOT_DIRECTIONAL; (2) UP x uwDom short -0.061 = negative avoidance. Pattern: HH_LL expansion lifts BOTH sides in every state (vol-structure); LH_HL contraction lowers BOTH sides (avoidance). Directional structure (DOWN x LH_LL short +0.050) era-conditional (b1 flat). NO new directional cross-era-stable tradeable candidate.
**Convergence:** H4-conditioned path-shape REPRODUCES the standalone-M15 bounded conclusion — the only cross-era-stable M15 information is VOLATILITY-STRUCTURE (expansion/contraction), which is non-directional; directional path-edges remain era-conditional.
**NEXT:** Family 5 = time-since-local-extreme + recent path curvature/acceleration (last univariate path-shape class); then present a BOUNDED INTERIM CONCLUSION on the H4-M15 path-shape frontier for CEO review.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #32 — 2026-08-22 — Family 5 (fresh-extreme + curvature): 2nd cross-era-stable candidate (DOWN x decelDn short, same family as F2)
**Screen (`h4m15_curvature.py`):** M15 fresh 8-bar extreme (momentum) + 4-bar velocity accel/decel conditional on H4 state; P(+70/-50 & +100/-70) lift vs same-H4-state base, L/S separate, DISC/CONF+per-year+b0+b1, event-deduped.
**Result:** momentum-extreme signals fail cross-era (b1~0). ONE cross-era-stable candidate: **DOWN x decelDn -> SHORT +0.050/+0.059** (DISC+0.05/CONF+0.05, b0+0.06/b1+0.04 — survives incl b1; coherent mirrors). BUT it is the SAME DOWN-H4-short-continuation MECHANISM as the F2 candidate ST-H4DN-M15DNIMP-SHALLOW-SHORT (different trigger). Registered ST-H4DN-M15-DECELDN-SHORT (pending characterization).
**NEXT:** characterize ST-H4DN-M15-DECELDN-SHORT (§14-15 structural-stop net STRESS cross-era + §17 redundancy: event-day overlap vs F2). Prior from F2: expectancy era-conditional (tradeable b0, neg b1) + likely redundant -> expect not-a-survivor; verify not assume. THEN present BOUNDED INTERIM CONCLUSION on the H4-M15 path-shape frontier for CEO review.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #33 — 2026-08-22 — ST-H4DN-M15-DECELDN-SHORT: NOT tradeable + REDUNDANT with F2 (not frozen)
**Characterization (`h4m15_deceldn_char.py`, §14/§15/§17):** structural stop = recent 8-bar swing high (med 47/64/30p DEV/b0/b1); net STRESS cross-era + event-overlap vs F2.
**Result:** tradeable ONLY in b0 (+0.019..+0.161); DEV net-negative (best -0.010, 2022 -0.35); b1 marginal (+0.009..-0.011) -> era-conditional, same as F2. **§17 redundancy: 100% DEV day-overlap with F2 (62/62 days, 36 shared bars)** -> same DOWN-H4 short-continuation events = REDUNDANT_EXISTING_ALPHA. NOT frozen on two independent grounds.
**Interpretation:** the DOWN-H4 short-continuation family has era-conditional EXPECTANCY (tradeable high-vol/trend eras only) AND its distinct triggers (impulse-shallow F2, decel F5) are MUTUALLY REDUNDANT (fire on the same days) -> not multiple distinct strategies, one era-conditional mechanism.
**NEXT:** complete §21 budget — bounded M15 path-shape TRANSITION/sequence map + a small number of interpretable INTERACTIONS conditional on H4 — then present a BOUNDED INTERIM CONCLUSION on the H4-M15 path-shape frontier for CEO review.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #34 — 2026-08-22 — §21 budget complete -> BOUNDED H4-M15 CONCLUSION (CEO decision A/B/C/D requested)
**§21 completion (`h4m15_trans_interact.py`):** M15 path-shape transitions (squeeze->release, pullback->resume) + interactions conditional on H4. squeeze-release UP->L +0.107 but thin(EffN 72)/CONF-na/b1-flat; DOWN->S b1-negative; pullback-resume zero-info; interactions marginal EXCEPT LH_LL&decel@DOWN->S +0.055 cross-stable = 3rd trigger of the SAME DOWN-H4-short mechanism (not independent, §18 no-cloning). NO new candidate.
**Frontier bounded:** univariate 5 families + transition map + interactions ALL completed. NO robust non-redundant cross-era-tradeable NEW price-only strategy emerged.
**Central result:** only cross-era-stable M15 info = VOLATILITY-STRUCTURE (non-directional); the one cross-era-stable-INFO directional mechanism (DOWN-H4 short continuation) has era-conditional EXPECTANCY (tradeable b0 only) + mutually-redundant triggers -> one era-conditional mechanism, not a strategy. Binding constraint = b1 low-vol lacks follow-through. Convergent across THREE methods (standalone M15, regime state-path, H4-M15 path-shape): cross-era-stable price-only INFO is non-directional; cross-era-stable directional EXPECTANCY does not exist price-only. `ALPHA_H4M15_BOUNDED_CONCLUSION.md` written.
**CEO DECISION A/B/C/D:** A(rec)=open EXOGENOUS axis (authorize bounded DXY causal study); B=deploy DOWN-H4 short as regime-gated module (non-stationary); C=M15 as trigger under frozen HTF edge; D=non-directional vol-timing study. Loop paused at decision point.
**Global status:** `ALPHA_H4M15_PATHSHAPE_FRONTIER_BOUNDED` — awaiting CEO A/B/C/D.

---

## CHECKPOINT #35 — 2026-08-22 — NEW MANDATE (Decision A): DXY causal aligner FROZEN + coverage verified
**Mandate:** ALPHA-XAUUSD-DXY-CAUSAL-INCREMENTAL-INFORMATION-001. Exogenous DXY axis, information-first.
**Done (`dxy_data.py`):** causal loader/aligner for the RATIFIED ICE DXY H1 (governed slices) joined to XAUUSD H1 (_from_M15_v2 = DXY coverage reference). Enforces the ratified timestamp contract (merge_asof backward on dxy_close=dxy.time+3600 vs XAUUSD decision=time+3600; causal assertion passes). Per-slice DXY features (governed, no between-block continuous). Predeclared feature set (8) + lag set {0,1,2,4}H. Coverage verified == ratified report: b0 97.4% / b1 97.8% / y2123 99.9% same-hour. Contract frozen in `ALPHA_DXY_ALIGNER_CONTRACT.md`.
**Foundation finding:** corr(past DXY 4h return, XAUUSD forward 24h return) ~= 0 in every era (b0 -0.027/b1 -0.000/y2123 +0.004) -> the DXY<->gold inverse relationship is CONTEMPORANEOUS (shared-driver, simultaneous), NOT predictive from past DXY to future gold. The mandate's real question (does causal/lagged DXY add INCREMENTAL info about future XAUUSD path) is thus non-trivial; naive lagged DXY-return alone carries no edge.
**NEXT:** Stage A DXY information map — DXY state (impulse/accel/efficiency/vol/dist) -> XAUUSD P(+50/-50,+70/-50,+100/-70,+100/-100) path lift vs XAUUSD parent-state base, L/S separate, lag curve {0,1,2,4}, cross-era, event-deduped; then §7 incremental-over-price-only test.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE` (DXY frontier).

---

## CHECKPOINT #36 — 2026-08-22 — Stage A DXY univariate map: no cross-era-stable info; DXY<->gold relationship INVERTS in 2021-2023
**Screen (`dxy_infomap.py`):** DXY state (impulse/accel/efficiency) -> XAUUSD P(+70/-50 & +100/-70) path lift vs era-global XAUUSD base, directed side (§13), lag {0,1,2,4}H, cross-era b0/b1/y2123, event-deduped (6h), H=24h.
**Result:** NO cross-era-stable univariate DXY directional information. Lifts small (<=0.04, consistent w/ ~0 linear corr). Most coherent signal = persistent DXY efficiency -> inverse XAUUSD path: +0.02..+0.03 in b0/b1 (classic inverse) but **REVERSES to -0.02..-0.04 in 2021-2023** (inflation/safe-haven regime where gold & USD rose together). DXY's directional link to gold is REGIME-CONDITIONAL, not stationary. Lag curve decays from lag0 (no better lag).
**NEXT:** X3 divergence (XAUUSD NOT reacting to DXY as expected -> continuation/reversal info?) + §7 incremental-over-XAUUSD-parent test + small XAUUSD-state x DXY-state interactions, before the bounded DXY conclusion. Do NOT conclude DXY_INCREMENTAL_INFORMATION_NOT_SUPPORTED until X3 + incremental + interactions done (§20).
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #37 — 2026-08-22 — DXY X3 divergence + §7 incremental: incremental info REAL but regime-conditional (inverts 2021-2023)
**Screen (`dxy_divergence_incremental.py`):** X3 divergence (gold not reacting to material DXY move, DXY threshold from DISC only) + §7 incremental (persistent DXY direction OVER XAUUSD parent regime), cross-era, deduped, H=24h.
**Result:** X3 divergence flips sign across eras (div_bull L +0.029 b0 / -0.053 b1; div_bear S -0.046 b0 / +0.050 b1) -> not stable. §7 incremental (CRITICAL gate): DXY direction adds SMALL POSITIVE increment over XAUUSD parent in b0/b1 (+0.02..+0.06, so NOT purely redundant with XAUUSD trend) but INVERTS in 2021-2023 (dxyEffDn->L UP -0.034/TRANSITION -0.061). The only cross-era-coherent piece (DXY-strength-in-XAUUSD-UP -> shorts worse) is an XAUUSD-trend effect, not new DXY info.
**Decisive:** DXY carries GENUINE (non-redundant) incremental info about XAUUSD path in 2011-2018, but it is REGIME-CONDITIONAL and INVERTS in the 2021-2023 inflation/safe-haven regime -> fails the MATERIAL+STABLE requirement (§1/§15). Same non-stationarity the whole program found, now on the exogenous axis.
**NEXT:** bounded DXY transitions (DXY accel->decel / reversal sequences) to complete the §20 order; then present the BOUNDED DXY CONCLUSION (likely DXY_INCREMENTAL_INFORMATION_NOT_SUPPORTED as a STABLE edge) + CEO decision.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #38 — 2026-08-22 — DXY transitions -> §20 complete -> BOUNDED DXY CONCLUSION (CEO decision A/B/C/D)
**DXY transitions (`dxy_transitions.py`):** USD impulse-exhaustion + reversal -> XAUUSD path lift, cross-era. NO cross-era-stable transition (usdUpExhaust->L +0.037/+0.044 b1/y2123 but ~0 b0; usdRevDn->L flips b0 vs b1). §20 order complete.
**BOUNDED DXY CONCLUSION (`ALPHA_DXY_BOUNDED_CONCLUSION.md`):** DXY carries GENUINE non-redundant incremental info about XAUUSD path in 2011-2018 (§7: +0.02..+0.06 over parent, NOT redundant) but it INVERTS in 2021-2023 (inflation/safe-haven regime; classic inverse DXY<->gold flipped). Univariate/divergence/transitions all confirm no cross-era-stable sign. => `DXY_INCREMENTAL_INFORMATION_NOT_SUPPORTED` as a STABLE/tradeable edge (not "uninformative" — real but non-stationary; recent regime carries inverted sign). Mechanism: DXY is an endogenous output of the real-yield/monetary regime, not the primitive driver -> cannot be cross-era-stable alone. Exogenous-axis confirmation of the program-wide result.
**CEO DECISION A/B/C/D:** A(rec) accept the bounded DXY negative; C(rec next) authorize REAL-YIELDS axis (mandate deferred yields "until DXY determined" — now determined; 2021-2023 inversion is a real-yield signature); B regime-gated DXY (rejected — recent regime inverted, no stable gate); D price-only M15-trigger-under-HTF-edge fallback. Loop paused at decision point.
**Global status:** `ALPHA_DXY_FRONTIER_BOUNDED` — awaiting CEO A/B/C/D.

---

## CHECKPOINT #39 — 2026-08-22 — ARCHITECTURE RESET (Decision): MARKET_OPERATING_MODE_V1 FROZEN
**Mandate:** ALPHA-XAUUSD-HIERARCHICAL-MODE-STRUCTURAL-EVENT-DISCOVERY-001. Paradigm: mode -> structural event -> specialist strategy (regime-specific specialists, not one universal strategy).
**Done (`market_mode.py`, §3-8):** froze MARKET_OPERATING_MODE_V1 — price-only, causal, H4, 6 modes via a two-scale view (PRIMARY backbone pdisp over P=30 H4 bars vs IMMEDIATE idisp over I=6): PRIMARY_BULL_IMPULSE / BULL_CORRECTION / PRIMARY_BEAR_IMPULSE / BEAR_CORRECTION / NEUTRAL_ROTATION / TRANSITION. Solves §4 (separates genuine PRIMARY_BEAR from bearish CORRECTION-inside-bull). Vol/extension = attribute tags (no combinatorial explosion). NEUTRAL_ROTATION != canonical RANGE. Thresholds frozen from price-structure reasoning (PRIM_T=1.0/IMM_T=0.3/EFF_T=0.25), NOT P&L. Contract `ALPHA_MARKET_OPERATING_MODE_V1_CONTRACT.md`.
**Population/validity:** stable distribution across all 5 eras (b0/b1/2021/2022/2023), every mode sufficient N + episodes (cross-era gate viable); corrections shorter-duration than primary impulses; transition matrix shows sticky primary backbone (BULL_CORRECTION returns to PRIMARY_BULL, rarely flips to bear) -> §4 confirmed.
**NEXT (§10):** FIRST structural-event family ONLY — LIQUIDITY EVENT -> RECLAIM/FAILURE -> DISPLACEMENT -> FUTURE PATH — M15 events conditioned on the frozen H4 mode, information-first, mandatory decomposition (mode base -> +event -> +reclaim -> +displacement), L/S separate, event-deduped, cross-era within same mode.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE` (mode->event architecture).

---

## CHECKPOINT #40 — 2026-08-22 — Liquidity-event family first cut: DISPLACEMENT is the informative component; 2 mode-conditional cross-era leads
**Screen (`liquidity_event.py`):** mechanical M15 liquidity event (sweep recent 20-bar swing -> reclaim -> displacement) conditioned on the FROZEN H4 mode; mandatory decomposition MODE base -> +evt -> +rcl -> +disp, P(+70/-50) 8h, directed side (sell->L/buy->S), event-deduped, per era (b0/b1/2021/2022/2023).
**Key finding (validates §13/§14):** the DISPLACEMENT component carries the information, NOT the raw sweep — +evt lifts ~0/inconsistent, +disp adds the most across cells. The CEO's core hypothesis (edge is in the post-event response) is supported.
**Two mode-conditional cross-era-consistent leads (b0+b1 same sign, disp-driven):** BEAR_CORRECTION + sell-sweep+reclaim+disp -> LONG (+0.144 b0 / +0.045 b1); BULL_CORRECTION + buy-sweep+reclaim+disp -> SHORT (+0.064 b0 / +0.046 b1). Both = "sweep + displacement continues the correction" — specialist (mode-conditional) signals. Counter-trend cells (PRIMARY_BULL buy->S) fail 2023. Disp-N small (31-44/era); b1 low-vol base. LEADS not survivors.
**NEXT:** deepen the 2 correction leads — more eras (relaxed-N 2023) + +100/-70 label + explicit winner-vs-loser (reclaim vs no-reclaim) + event-N honesty (unique days/H4 episodes) + tradeability with structural stop.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.

---

## CHECKPOINT #41 — 2026-08-22 — Two single-bar liquidity leads FAIL deepening (rare + tight-stop + not cross-era-robust)
**Deepening (`liquidity_deepen.py`, §14/§18/§20/§21/§22):** winner-vs-loser + full labels + event-N honesty + tradeability with structural stop (swept swing extreme).
**Result:** BOTH leads fail. Lead A (BEAR_CORRECTION sweep->L): b0 rr1.0 +0.136 but SL only 23p (tight), b1 NEGATIVE -> not cross-era-robust. Lead B (BULL_CORRECTION sweep->S): b0 NEGATIVE (-0.21..-0.29) despite P-lift (reversal short run over by bull primary), b1 marginal. Both ~2 eff/mo (too rare for a desirable specialist §25). Winner-loser non-monotonic (reclaim-only often < base) -> first-cut disp lift was small-N noise. Structural stop = swept extreme is TOO TIGHT (16-30p) when sweep+reclaim+displacement forced onto ONE M15 bar (§21 tight-stop fragility).
**Root cause:** event FORMULATION, not necessarily the hypothesis — the CEO sequence (sweep->reclaim->DISPLACEMENT->path) is inherently MULTI-BAR; the single-bar collapse made it rare + tight-stopped.
**NEXT (one predeclared reformulation, §12-13, NOT mining):** multi-bar liquidity SEQUENCE — sweep+reclaim on bar t, displacement over next K bars, entry after displacement confirms, structural stop at swept extreme (with room); re-test the mode-conditional decomposition + winner-loser + tradeability cross-era. If still no robust specialist -> bounded liquidity-family conclusion.
**Global status:** `ALPHA_CONTINUOUS_RESEARCH_ACTIVE`.
