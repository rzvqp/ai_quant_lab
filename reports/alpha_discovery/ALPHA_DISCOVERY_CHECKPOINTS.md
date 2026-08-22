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
