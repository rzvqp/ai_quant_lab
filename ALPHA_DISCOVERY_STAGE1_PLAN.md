# ALPHA DISCOVERY — STAGE 1 RESEARCH ARCHITECTURE + HYPOTHESIS PORTFOLIO

**Mandate:** `ALPHA-DISCOVERY-STAGE1-PLANNING-001` · **Date:** 2026-08-21 · **Status:** `ALPHA_DISCOVERY_STAGE_1_PLAN_READY`
**This is a PLAN. No experiment, backtest, PnL, cost gate, OOS access, or multi-day loop was executed.**

---

## 1. Confirmation — VE handoff consumed
Read `ai_quant_lab-wp5b/ve_n1_replay/RANGE_V4_4_ALPHA_DISCOVERY_HANDOFF.md` in full. Verified from Git (not from the mandate text):
- VE closure `6120b5d` ("freeze V4.4, close V4.4.1") ✓; V4.4 implementation `3bb61cf` ✓; my prior Alpha report `cbc576c` in history ✓.
- V4.4 source files (`range_semantic_v4_4.py`, `range_engine_v4_4.py`) are **byte-identical** between `3bb61cf` and current wp5b HEAD `6120b5d` (empty diff) — frozen intact.
- `ConfigV44().config_id()` = `23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969` — **matches the handoff exactly.**

## 2. Exact V4.4 research identity (frozen, do not modify)
| Field | Value |
|---|---|
| Commit | `3bb61cf` (repo `ai_quant_lab-wp5b`, branch `discovery-mk-matrix-v1`) |
| contract_version | `range-hierarchical-v4.4` |
| config_id | `23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969` |
| impl fingerprint | `v4-4-implementation-freeze-2026-08-20` |
| Import (source-only, NOT in any wheel) | `from ve_n1_replay.range_engine_v4_4 import RangeSemanticEngineV44` (+ `ConfigV44`) |
| Construction | `RangeSemanticEngineV44(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=<N1 commit>, range_config=ConfigV44(), acknowledge_construction_only=True)` |
| Confirmed RANGE (research def) | `macro_state == "CONFIRMED"` (`macro_confirm_ts is not None`) — CANDIDATE/FORMING is NOT a detection |
| Status string (mandatory in downstream reports) | `V4_4_FROZEN_CONSERVATIVE_RESEARCH_BASELINE` |
| Known limitation (must always report) | one-directional under-detection: a rejected candidate can hold the single active-MACRO slot and block a fresh candidate (§8 of handoff). Accepted, NOT to be fixed. |

**Consumption rule:** V4.4 is a **feature/context input to be tested, never ground truth or a recall-complete RANGE oracle.** Any hypothesis whose validity needs V4.4 recall to be high stands on a known-false assumption. V4.4 config is NOT `ConfigV44()`-overridable (config_id guard is fail-closed). Config note for calibration: V4.4 is **more permissive** than the retired `ve_n1_replay 0.2.0` range engine (ER_max 0.5 vs 0.4, hierarchical MACRO/INTERNAL, K_reentry=22), so its real CONFIRMED occupancy on XAUUSD M15 is **unknown and must be measured empirically in Wave 1** — it is NOT the 0.2.0 "23 ESTABLISHED bars" result, which used a different detector.

## 3. Regime coverage architecture
Full market-state space, no forced equality; a regime with zero surviving Alpha is an acceptable result. Every hypothesis declares one `PRIMARY_REGIME_RELATIONSHIP` ∈ {TREND_UP_DEPENDENT, TREND_DOWN_DEPENDENT, RANGE_DEPENDENT, TRANSITION_DEPENDENT, MULTI_REGIME, REGIME_INDEPENDENT}. Regime classifier = **canonical N1** (`ve_n1_replay` incremental, `n1-additive-raw-axes-v1`, byte-identical across 0.1.1/0.2.0) for TREND/UNCERTAIN; **V4.4 CONFIRMED** for RANGE context. Market Intelligence gating must **earn** its value empirically (items 20–21): every regime-conditioned hypothesis is compared against its unconditional form.

## 4. Data partitions (frozen before any material search)
Ratified discovery population = the 4 blocks (2011-07→2013-09, 2016-01→2018-04, 2020-08→2021-09, 2022-12→2025-10), M15, 197,094 pre-holdout bars via the official loader.

| Partition | Period | Reuse rule |
|---|---|---|
| **DEVELOPMENT** | Blocks 1–2 (2011-07→2018-04) | repeatedly explorable — mechanism discovery, feature construction, cheap falsification |
| **CALIBRATION** | Block 3 (2020-08→2021-09) | limited — parameter neighborhoods only; not for go/no-go |
| **VALIDATION** | Block 4 recent (2022-12→2025-10) | **used once per survivor** (OOS-like); never for tuning |
| **FINAL HOLDOUT** | 2025-10-23 → present | **SEALED / UNTOUCHED** — never exploratory; CEO-release only |

FINAL HOLDOUT must never become exploratory evidence. VALIDATION is spent on first contact per hypothesis-version. FB14/F441/MB3 are excluded from all Alpha tuning (§15).

## 5. Execution / cost contract (verified against repo; differences reported — no silent substitution)
Canonical evaluator = `mstrat.simulate` (wp5b reconciled, `RT-CODE-A-0007`, **TICK=0.01**). Verified mechanics:
- **Entry:** next-bar open (`ei = signal_idx + 1`, entry `= open[ei]`). ✓ matches mandate.
- **Min stop floor:** `max(2·spread_price, 5·TICK=0.05, 0.10·ATR)`. ✓ matches mandate `max(2×spread, 0.05, 10%ATR)`.
- **Cost:** applied as `2·cost` in the R numerator; full bid-ask treatment. ✓
- **Cost model:** `AI_TRADER_SHADOW_COST_MODEL_v1`, calibration **RATIFIED**, config-fp `b7bb9a9aed17a1c8`, content_hash `1341f228…`, SE **UNAVAILABLE**.

**⚠ DIFFERENCE TO RESOLVE BEFORE WAVE 1 (reported, not substituted):** the mandate says "BASE spread 0.05, STRESS spread 0.08". The RATIFIED manifest gives **BASE round-trip 0.05** (spread 0.05, zero slippage) and **STRESS round-trip 0.24** (spread **0.08** + entry-slip 0.08 + exit-slip 0.08; slippage itself `COST_MODEL_UNAVAILABLE` — zero real fills). So the **spread** components match (0.05 / 0.08) but the STRESS **round-trip** is 0.24 in the ratified model vs a spread-only 0.08 in the mandate wording. Proposed resolution: use the RATIFIED manifest (BASE 0.05, STRESS 0.24) as authoritative for NET, and additionally report a "STRESS-spread-only 0.08" scenario for continuity with the mandate. **Awaiting CEO ruling on which STRESS definition is authoritative before any NET decision.**

## 6–9. Hypothesis portfolio (17 distinct causal mechanisms) + taxonomy + regime classification + cheap falsification
Schema per item 12. `PP` = PARAMETER_PROVENANCE, `DEV/VAL` = data required, `CC` = COMPUTE_COST (L/M/H). All parameters are **pre-registered from causal reasoning or literature defaults**, never from a profitability scan.

### TREND_UP_DEPENDENT
**H01 · TREND_UP pullback-continuation (baseline anchor)** — FAMILY pullback. MECHANISM: in a confirmed uptrend, a shallow counter-move into prior demand is absorbed and the trend resumes. WHY: liquidity replenishment + trend-followers re-entering. FEATURES: N1 TREND_UP, pullback depth (bars of lower-high/lower-low), close reclaiming prior high. SIGNAL: pullbackN reclaim. DIR long. ENTRY next-open. INVALIDATION: close below pullback low. STOP: 2.5·ATR. EXIT: time-40 / opposite structure. MAXHOLD 40 bars. FAILURE MODE: trend already exhausted → pullback becomes reversal. REL-V4.4: none (TREND). FALSIFICATION: forward-return after pullback-reclaim > 0 net of BASE on DEVELOPMENT; else archive. MIN SAMPLE 200 events. PP: literal (existing survivor G0037). DEV blocks1-2; VAL block4. CC L. *Established provisional survivor — carried as the reference baseline, not re-discovered.*

**H02 · Failed bearish counter-move** — FAMILY failed-counter. MECHANISM: inside TREND_UP, a bearish reversal *attempt* (a down-close breaking a minor swing low) that **fails to follow through within k bars** signals trapped shorts → sharp resumption up. WHY: stop-run of trapped sellers. FEATURES: N1 TREND_UP, minor-swing-low break, no continuation in k=3 bars, reclaim. SIGNAL: reclaim after failed breakdown. DIR long. ENTRY next-open. INVALIDATION: sustained close below the swing low. STOP: below the failed low. EXIT: time / RR-2. MAXHOLD 30. FAILURE: genuine trend change (the breakdown was real). REL-V4.4 none. FALSIFICATION: conditional fwd-return | failed-breakdown vs unconditional TREND_UP baseline shows positive shift; else archive. MIN 150. PP causal (k=3 pre-set). DEV; VAL. CC M. **Distinct from H01** (trap/stop-run, not dip-buying).

**H03 · Acceleration after compression (vol-conditioned continuation)** — FAMILY compression-expansion. MECHANISM: a volatility contraction *inside* an uptrend (ATR falling below its own MA) resolves upward with an expansion bar → continuation with better R:R. WHY: coiled positioning, breakout of a micro-balance in trend direction. FEATURES: N1 TREND_UP, ATR14 < 0.8·ATR-MA(50) for ≥m bars, expansion bar up. SIGNAL: first up-expansion out of compression. DIR long. ENTRY next-open. INVALIDATION: expansion fails (close back inside). STOP: compression low. EXIT: measured-move / time. MAXHOLD 40. FAILURE: false expansion / whipsaw. REL-V4.4 none. FALSIFICATION: expansion-conditioned fwd-return > unconditioned; disappears after BASE → archive. MIN 100. PP causal (0.8, 50 literal). DEV; VAL. CC M.

**H04 · TREND_UP exhaustion / reversal (counter-trend, separate mechanism)** — FAMILY exhaustion. MECHANISM: late-trend climax (accelerating range + volume + failure to make a new high) marks buyer exhaustion → mean-reverting short. WHY: last-buyer exhaustion, profit-taking. FEATURES: N1 TREND_UP, consecutive expanding up-bars then a failed new high / bearish engulf. SIGNAL: exhaustion pattern. DIR **short** (counter-trend). ENTRY next-open. INVALIDATION: new high. STOP: above the high. EXIT: RR-1.5 / fast time. MAXHOLD 20. FAILURE: trend simply continues (exhaustion is the hardest to time). REL-V4.4 none. FALSIFICATION: short fwd-return after exhaustion signal > 0 net BASE; **expected to be hard** — cheap kill likely. MIN 120. PP causal. DEV; VAL. CC M. **Tests the mandate's "do not assume LONG is always correct in TREND_UP".**

### TREND_DOWN_DEPENDENT
**H05 · Breakdown acceptance (short continuation)** — FAMILY breakdown-acceptance. MECHANISM: a break below a defended level followed by **acceptance** (n closes below without reclaim) confirms distribution → short continuation. WHY: supply overwhelms, longs capitulate. FEATURES: N1 TREND_DOWN, level break, N_accept closes below, no reclaim. SIGNAL: acceptance confirmed. DIR short. ENTRY next-open. INVALIDATION: reclaim above the level. STOP: above the broken level. EXIT: measured-move / time. MAXHOLD 40. FAILURE: bear trap (fast reclaim). REL-V4.4 none. FALSIFICATION: acceptance-conditioned short return > naive break-and-short (which the canonical rerun showed fails); if no lift → archive short entirely. MIN 150. PP causal (N_accept=2 pre-set). DEV; VAL. CC M. **Directly tests why the prior swing-based shorts failed — is *acceptance* the missing ingredient?**

**H06 · Failed bullish counter-move (short)** — mirror of H02 in TREND_DOWN. MECHANISM: a failed up-break in a downtrend traps longs → resumption down. DIR short. Same structure as H02, opposite direction. FAILURE: real bottom. FALSIFICATION: conditional fwd-return shift; else archive. MIN 150. CC M.

**H07 · TREND_DOWN exhaustion / reversal (long)** — mirror of H04. MECHANISM: capitulation climax (panic expansion + failure to make new low) → mean-revert long. DIR **long** (counter-trend). FAILURE: downtrend continues. FALSIFICATION: cheap kill likely. MIN 120. CC M.

### RANGE_DEPENDENT (V4.4 CONFIRMED as feature — measure its value, don't assume it)
**H08 · Boundary-rejection mean-reversion** — FAMILY boundary-fade. MECHANISM: inside a V4.4-CONFIRMED MACRO range, price tagging a boundary (within tol) and rejecting reverts toward `range_mid`. WHY: responsive liquidity at tested boundaries. FEATURES: `macro_state=="CONFIRMED"`, price within tol of `macro_boundary_upper/lower`, rejection close. SIGNAL: boundary rejection. DIR: short at upper / long at lower. ENTRY next-open. INVALIDATION: close beyond boundary (breakout). STOP: beyond the boundary + buffer. EXIT: `range_mid` or opposite boundary / time. MAXHOLD 96. FAILURE: boundary breaks (range ends); V4.4 under-detection means many real ranges are missing → small sample. REL-V4.4: **primary** (needs CONFIRMED spans). FALSIFICATION: (a) measure CONFIRMED occupancy first; (b) rejection→mid fwd-return > 0 net BASE. If occupancy ≈ 0 (as 0.2.0 suggested, but V4.4 may differ) → `EVENT_TOO_RARE`, report and archive. MIN 100 events. PP causal (tol from ATR). DEV; VAL. CC M.

**H09 · Genuine RANGE breakout: displacement + acceptance out of CONFIRMED range** — FAMILY range-breakout. MECHANISM: a displacement bar exiting a V4.4-CONFIRMED range **with acceptance** (closes hold outside) initiates a new directional leg. WHY: range resolution / imbalance. FEATURES: CONFIRMED range end via breakout + N_accept closes outside. SIGNAL: accepted breakout. DIR: break direction. ENTRY next-open. INVALIDATION: re-entry into the range. STOP: back inside the range. EXIT: range-width projection / time. MAXHOLD 60. FAILURE: false breakout (→ H10). REL-V4.4 primary. FALSIFICATION: accepted-breakout return > 0 net BASE; disjoint from H10 by construction. MIN 60. CC M.

**H10 · Failed-breakout re-entry (range fade)** — FAMILY failed-breakout. MECHANISM: a breakout from a CONFIRMED range that **fails and re-enters** traps breakout traders → fade back toward mid. DIR: opposite the failed break. Disjoint population from H09 (accepted XOR failed). INVALIDATION: re-break in the original direction with acceptance. FAILURE: it wasn't a real failure. REL-V4.4 primary. FALSIFICATION: failed-re-entry return > 0 net BASE. MIN 60. CC M.

### TRANSITION_DEPENDENT
**H11 · Displacement + acceptance regime escape** — FAMILY displacement-acceptance. MECHANISM: a large displacement bar (≥w·ATR net move) followed by **acceptance** (closes hold in the displacement direction) marks a genuine structural change → trade continuation of the *new* regime. WHY: repricing event; acceptance separates real change from a wick/sweep. FEATURES: displacement magnitude, N_accept confirming closes, N1 direction flip. SIGNAL: accepted displacement. DIR: displacement direction. ENTRY next-open (only from `confirm_ts`, never `structural_start_ts`). INVALIDATION: reversion through the displacement origin. STOP: displacement origin. EXIT: measured / time. MAXHOLD 48. FAILURE: displacement is a one-bar spike that reverts. REL-V4.4 none (uses N1 + displacement). FALSIFICATION: **displacement+acceptance vs single-sweep/wick** — does acceptance discriminate forward continuation? (Uses the qualitative finding only as hypothesis-generation, NOT proof.) MIN 120. PP causal (w, N_accept pre-set). DEV; VAL. CC M.

**H12 · Volatility-expansion breakout from a low-vol base** — FAMILY vol-expansion. MECHANISM: a regime-agnostic ATR expansion from a multi-day low-vol base resolves directionally and trends briefly. WHY: volatility clustering / regime ignition. FEATURES: ATR percentile low → expansion bar. SIGNAL: first expansion. DIR: expansion direction. ENTRY next-open. INVALIDATION: reversion inside the base. STOP: base extreme. EXIT: time / trailing. MAXHOLD 40. FAILURE: expansion whipsaw. REL-V4.4 none. FALSIFICATION: expansion-direction fwd-return > 0 net BASE. MIN 120. CC M.

**H13 · Structural reversal (confirmed CHoCH)** — FAMILY structural-reversal. MECHANISM: a confirmed change-of-character (break of the last opposing swing) marks trend reversal → trade the new direction. WHY: structural break of prior trend. FEATURES: N1 structure/direction flip (BOS/CHoCH), confirmed. SIGNAL: CHoCH confirm. DIR: new direction. ENTRY next-open. INVALIDATION: failure swing reclaims. STOP: prior extreme. EXIT: measured / time. MAXHOLD 48. FAILURE: false reversal in a range. REL-V4.4: gate by "not inside a CONFIRMED range" (comparison test). FALSIFICATION: CHoCH fwd-return > 0 net BASE; compare with/without range gate. MIN 120. CC M.

### REGIME_INDEPENDENT (no Market-Intelligence gate — MI must earn its value)
**H14 · Session / time-of-day effect** — FAMILY session. MECHANISM: XAUUSD exhibits session-structured behavior (London/NY momentum vs Asia mean-reversion). WHY: participant composition, liquidity windows. FEATURES: NY-anchored session bucket (`day_index_ny17`), bar-of-session. SIGNAL: session-conditioned directional bias. DIR: per-session (pre-registered from causal reasoning, not fitted). ENTRY next-open. INVALIDATION: session end. STOP: ATR. EXIT: session close / time. MAXHOLD ≤ 1 session. FAILURE: effect is spurious / arbitraged away. REL-V4.4 none. FALSIFICATION: conditional fwd-return by session shows a *stable, pre-declared-sign* shift across DEVELOPMENT sub-periods; else archive. MIN 300. PP: session boundaries deterministic. DEV; VAL. CC **L** (cheapest — high info gain). **Tests whether alpha exists without any regime classification.**

**H15 · Volatility asymmetry** — FAMILY vol-asymmetry. MECHANISM: gold's up-vol vs down-vol asymmetry (or realized-vol sign dependence) predicts short-horizon return skew. WHY: safe-haven demand asymmetry. FEATURES: signed realized vol / up-down range ratio. SIGNAL: asymmetry threshold. DIR: per-sign. ENTRY next-open. INVALIDATION: horizon end. STOP ATR. EXIT time. MAXHOLD 16. FAILURE: no exploitable asymmetry net of cost. REL-V4.4 none. FALSIFICATION: monotone relationship between asymmetry feature and fwd-return; disappears after BASE → archive. MIN 300. CC L.

**H16 · Conditional momentum (vol-regime-conditioned)** — FAMILY conditional-momentum. MECHANISM: short-horizon momentum works only in a specific realized-vol band (too calm = noise, too wild = reversal). WHY: signal-to-noise varies with vol. FEATURES: k-bar return sign × realized-vol band. SIGNAL: momentum within the band. DIR: momentum direction. ENTRY next-open. INVALIDATION: horizon end. STOP ATR. EXIT time. MAXHOLD 24. FAILURE: momentum is a cost-eaten mirage on M15. REL-V4.4 none. FALSIFICATION: momentum EV positive only in the pre-declared vol band, net BASE. MIN 250. CC M.

**H17 · Overnight/weekend gap & return-path structure** — FAMILY gap. MECHANISM: session/weekend gaps show continuation or fade with a stable sign. WHY: information accumulation while closed. FEATURES: gap size vs ATR at session open. SIGNAL: gap classification. DIR: pre-declared per gap-type. ENTRY next-open. INVALIDATION: gap fill / horizon. STOP ATR. EXIT time / fill. MAXHOLD ≤ 1 session. FAILURE: gaps too rare / no stable sign on XAUUSD M15. REL-V4.4 none. FALSIFICATION: gap-conditioned fwd-return stable-signed net BASE; sparse → archive. MIN 150. CC L.

**Distinctness note:** these are 17 *mechanisms*, not threshold variants — pullback vs failed-counter vs compression-expansion vs exhaustion are causally different; LONG and SHORT are distinct directions in the fingerprint; accepted-breakout and failed-breakout are disjoint populations; regime-independent hypotheses carry no MI gate by design.

## 10. Minimum-sample rules
Each hypothesis declares `MINIMUM_SAMPLE_REQUIREMENT` (events, above). Below it → `SAMPLE_TOO_SPARSE`, archived, **not rescued with filters**. Episode-primary counting (regime episodes, not calendar) for regime-dependent hypotheses; event counting for regime-independent. No screening verdict below min sample.

## 11. Prioritization matrix (ranked BEFORE any large experiment, no profitability input)
Scored 1–5 on: causal plausibility, measurability, falsifiability, cost realism, data availability, independence, expected information gain, compute efficiency. Ranking is deliberately blind to any result.

| Rank | H | Σ (info-gain × cheapness weighted) | Note |
|---|---|---|---|
| 1 | H14 session | highest — cheapest, regime-independent, high info gain | tests "alpha without MI" |
| 2 | H05 breakdown-acceptance | high — resolves the failed-short puzzle | is *acceptance* the missing ingredient? |
| 3 | H11 displacement+acceptance | high — tests the key qualitative finding | transition core |
| 4 | H02 failed-bearish-counter | high — cheap, distinct TREND_UP mechanism | trap/stop-run |
| 5 | H08 boundary-rejection | medium-high — directly measures V4.4 value | occupancy-gated |
| 6 | H15 vol-asymmetry | medium-high — cheap, independent | |
| 7–17 | H03,H12,H16,H13,H09,H10,H06,H07,H04,H17,H01 | medium / baseline | H01 is the carried survivor |

## 12. Recommended Wave 1 (4–6 hypotheses; distinct families; high info gain, low evidence consumption)
**Wave 1 = {H14 (session, REGIME_INDEPENDENT), H05 (breakdown-acceptance, TREND_DOWN), H11 (displacement+acceptance, TRANSITION), H02 (failed-bearish-counter, TREND_UP), H08 (boundary-rejection, RANGE)}** — five distinct families, one per regime class. Each runs its single cheapest falsification test on **DEVELOPMENT only** (blocks 1–2). H08 first measures V4.4 CONFIRMED occupancy; if ≈0 it is archived as `EVENT_TOO_RARE` without consuming VALIDATION. Optional 6th: H15 (vol-asymmetry) if compute budget allows. **Do NOT run the full campaign.**

## 13. Robustness path (survivors only)
Cheap-falsification PASS → parameter-neighborhood stability on CALIBRATION (no re-tuning, just sensitivity) → walk-forward within DEVELOPMENT → cost sensitivity (GROSS vs BASE vs STRESS) → fat-tail / concentration checks (best-trade share, best-episode share, top-1%-trimmed) → **only then** one VALIDATION pass.

## 14. OOS protection
VALIDATION (block 4) is consumed **once per hypothesis-version**, after robustness, never for tuning. FINAL HOLDOUT (2025-10-23+) stays SEALED; OOS access counter must remain observable and is 0 until CEO releases it. Any accidental VALIDATION reuse voids the hypothesis-version → new ID required.

## 15. Anti-overfitting controls
Every material variant → new `HYPOTHESIS_ID`/version. Forbidden: tune-until-profitable, reuse VALIDATION as DEVELOPMENT, cherry-pick periods, post-hoc trade removal, post-hoc cost changes, silent filter additions. **Complete graveyard** of failed hypotheses retained (failed research is evidence). No FB14/F441/MB3 labels as Alpha optimization targets (§ handoff 10); MB3-025→048 SEALED.

## 16. Autonomous multi-day loop (DESIGNED, NOT LAUNCHED)
`GENERATOR → FORMALIZER → PRE-REGISTRATION → FAST_FALSIFICATION → {FAIL→GRAVEYARD | PASS→SURVIVOR_QUEUE} → ROBUSTNESS → OOS → INDEPENDENT_REVIEW → CANDIDATE_ALPHA`. Generator keeps producing while survivors advance. Detached service (singleton, heartbeat, watchdog, checkpoint-per-hypothesis, restart-resume, niced below AI Trader, bounded batches) — reuses the proven `alpha_service` pattern. **Not started; awaits separate CEO authorization.**

## 17. Checkpoint policy (for the future loop)
Checkpoint every 25 hypotheses OR per mechanism-family completion. Each records: generated / tested / failed / survived / current best candidates / data consumed / VALIDATION untouched / compute consumed / anomalies / next queue. Once the autonomous campaign is separately authorized, individual failed hypotheses do NOT need per-item CEO approval.

## 18. Research / compute / evidence budgets (proposal)
- **Research budget:** ≤ 200 distinct hypotheses/versions for the first campaign.
- **Compute budget:** a fixed wall-clock/CPU cap (niced below AI Trader); e.g. ≤ N CPU-hours/day, hard stop.
- **Evidence budget:** DEVELOPMENT unlimited-reuse; CALIBRATION limited; VALIDATION one-pass-per-survivor (finite, tracked); FINAL HOLDOUT zero.
- **Stop condition:** campaign ends at whichever comes first — hypothesis cap, compute cap, or VALIDATION-budget exhaustion. **The campaign is a success even if ZERO strategies survive.** It must never be instructed "keep searching until profitable."

## 19. Future promotion gates (no shortcut)
`ALPHA_CANDIDATE` is the most Alpha Discovery may produce. Chain: `FAST_FALSIFICATION_PASS → ROBUSTNESS_PASS → OUT_OF_SAMPLE_PASS → STATISTICAL_REVIEW → RED_TEAM → CEO_DECISION → STRATEGY_CATALOG_CANDIDATE`. No independent promotion to Strategy Catalog / AI Trader / LIVE_SHADOW / LIVE. `BROKER_ORDER_SUBMISSION = DISABLED`.

## 20. Unresolved research risks
1. **STRESS cost definition** (§5) — ruling needed before any NET decision.
2. **V4.4 CONFIRMED occupancy on XAUUSD M15 is unknown** — H08/H09/H10 may be `EVENT_TOO_RARE`; V4.4's under-detection bias (§8) is one-directional and must be reported on every RANGE result.
3. **Short-side alpha may not exist** — the canonical rerun found no TREND_DOWN survivor; H05/H06 test whether *acceptance* changes this, but a null result is likely and acceptable.
4. **M15 cost drag** — momentum/vol-asymmetry (H15/H16) may be real gross but cost-eaten; BASE/STRESS sensitivity is the gate.
5. **Multiple-testing** across 17+ hypotheses — multiplicity accounting belongs to the Statistician; Alpha reports counts, never self-declares significance.
6. **N1 implementation_commit** for V4.4's engine wrapper must be pinned and recorded in every `evaluation_run_hash`.

---

### State
`ALPHA_DISCOVERY_STAGE_1_OPEN` · `ALPHA_DISCOVERY_STAGE_1_PLAN_READY` · `READY_FOR_CEO_ALPHA_WAVE_1_AND_AUTONOMOUS_LOOP_DECISION`.
No experiment executed. Broker disabled, LIVE untouched, no AI Trader integration, no Strategy Catalog promotion, SEALED data untouched, FB14/F441/MB3 excluded. **STOP — awaiting CEO decision on Wave 1 + autonomous loop.**
