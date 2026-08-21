# ALPHA_HISTORICAL_CANDIDATE_INVENTORY

**Mandate:** `ALPHA-HISTORICAL-CANDIDATE-INVENTORY-001` · **Date:** 2026-08-21 · **Type:** DOCUMENTATION ONLY.
No backtest, no retune, no VALIDATION/FINAL-HOLDOUT access, no promotion. Reconstructed **exclusively from repository evidence** (not chat memory).

---

## 1. Source / provenance audit
| Source | Repo / path | Role |
|---|---|---|
| `CANDIDATE_STATUS_REGISTER_v1.6.md` (CEO-REGISTER-v1.6, 2026-07-25) | `ai_quant_lab` | **Authoritative consolidated status** of all 28 discovery candidates + validation machinery. Only-CEO-writable single source of truth. |
| `discovery_candidates/DISCOVERY_CANDIDATE_INDEX.md` | `ai_quant_lab-wp5b` | Authoritative lifecycle index (titles, origin, date frozen) for DC-0001…DC-0026. |
| `STRATEGY_CANDIDATE_REGISTRY.parquet` (17 rows × 34 cols) | `ai_quant_lab-alpha-automation` | Formal S-family (S1–S20) strategy-candidate registry with backtest metrics + classification. |
| `results/FAMILY_RESULTS.parquet` (1,972 rows) | (Flow C / Research Lab) | Underlying systematic backtest corpus behind the S-family registry (verified in v1.6 §E). |
| `MECHANISM_REGISTRY.*`, `EDGE_DISCOVERY_REGISTRY_v1.md`, `STRATEGY_PROFILES.md`, `SESSION_CLOSE_ALPHA_DISCOVERY_WINDOW_2025-10-23.md` | alpha-automation / wp5b | Supporting mechanism/profile evidence. |

**Verification:** all IDs and statuses below are transcribed from the above; nothing invented. Where no formal ID exists, `NO_FORMAL_ID` is used.

## 2. Chronological Alpha history before RANGE V4.x
1. **~2026-07-13 — Research Lab / systematic S1–S20 family campaign.** 1,972 hypotheses backtested (GROSS, no ratified cost model, no OOS at the time). Produced the **17 formal S-family strategy candidates** (`STRATEGY_CANDIDATE_REGISTRY`). Classified A_profitable_but_fragile / B_research_candidate.
2. **2026-07-21 → 07-25 — Discovery / observation-journaling era (Alpha #1 & #2).** Discretionary + autonomous replay produced **28 discovery candidates** (DC-0001…DC-0026 = Alpha #1; AP2-DC-0001/0002 = Alpha #2). Red-Team triaged; 3 to Statistician; 1 (DC-0004) executed by Validation Engine.
3. **2026-07-25 — v1.6 consolidation.** Alpha #1 & #2 **CLOSED**; inventory frozen. **0 promoted to Knowledge Base, 0 reached AI Trader.**
4. *(bridge, ~2026-07→08, contemporaneous-with-RANGE, kept separate below)* — Flow-B economic-screening / `flowb` detached service (`CAND-00xx` / `G-series`, incl. G0037), and the RANGE V3→V4.4 program. These are **not strictly "before RANGE"** and are listed only as §Bridge for completeness.

---

## 3–6. Complete candidate table + status + failure-vs-pause + regime/timeframe classification

### Population A — Systematic S-family strategy candidates (17, `STRATEGY_CANDIDATE_REGISTRY`, M15 + HTF context, all LONG unless noted)
| ID | Mechanism | Dir | rep_n | rep_exp (GROSS) | PF | val_exp | robustness | classification | Current status | Failure vs pause | Likely regime relationship |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C_2d587447 | S5 opening-range momentum | long | 287 | +0.166 | 1.48 | +0.179 | 2.14 | B_research_candidate | **INCONCLUSIVE** (best; never validated) | **PAUSE (infra)** | REGIME_INDEPENDENT / session |
| C_0bb5095b | S9 MTF-trend momentum | long | 545 | +0.068 | 1.15 | +0.100 | 1.76 | B_research_candidate | INCONCLUSIVE | PAUSE (infra) | TREND_UP |
| C_d008e0a4 | S9 MTF-trend momentum | long | 512 | +0.063 | 1.12 | +0.250 | 1.51 | B_research_candidate | INCONCLUSIVE | PAUSE (infra) | TREND_UP |
| C_09d2245b | S20 hybrid sweep+MTF | long | 456 | +0.075 | 1.10 | +0.087 | 1.34 | B_research_candidate | INCONCLUSIVE | PAUSE (infra) | MULTI_REGIME |
| C_11418358 | S17 weekly levels breakout | long | 171 | +0.287 | 1.43 | **−0.086** | 1.34 | B_research_candidate | INCONCLUSIVE (⚠ val_exp<0) | PAUSE (infra) w/ cost flag | REGIME_INDEPENDENT / level |
| C_954698b1 | S1 liquidity-sweep MR | long | 193 | +0.071 | 1.17 | +0.004 | 1.26 | B_research_candidate | INCONCLUSIVE | PAUSE (infra) | RANGE_DEPENDENT |
| C_dca5629f | S1 liquidity-sweep MR | long | 399 | +0.032 | 1.05 | −0.061 | 1.22 | B_research_candidate | INCONCLUSIVE (⚠ val_exp<0) | PAUSE (infra) | RANGE_DEPENDENT |
| C_204a973a | S2 failed-breakout fade | long | 268 | +0.060 | 1.08 | +0.256 | 1.18 | B_research_candidate | INCONCLUSIVE | PAUSE (infra) | RANGE / TRANSITION |
| C_227d3ef2 | S6 session-transition momentum | long | 140 | +0.025 | 1.04 | +0.120 | 1.16 | B_research_candidate | INCONCLUSIVE | PAUSE (infra) | REGIME_INDEPENDENT / session |
| C_9214b37b | S1 liquidity-sweep MR | short | 241 | +0.017 | 1.03 | +0.346 | 1.06 | B_research_candidate | INCONCLUSIVE | PAUSE (infra) | RANGE_DEPENDENT |
| C_5ae92203 | S8 extension mean-reversion | long | 302 | +0.017 | 1.03 | +0.109 | 0.78 | B_research_candidate | INCONCLUSIVE (weak) | PAUSE (infra) | TREND (reversion) |
| C_3c96bb23 | S14 momentum exhaustion | short | 118 | +0.035 | 1.06 | **−0.137** | 1.05 | A_profitable_but_fragile | **REJECTED-fragile** | SCIENTIFIC (fragile/val<0) | TREND-reversal |
| C_46f00099 | S1 liquidity-sweep MR | short | 28 | +0.014 | 1.43 | NaN | 1.01 | A_profitable_but_fragile | **REJECTED-fragile** (n=28, knife-edge) | SCIENTIFIC (sparse/fragile) | RANGE_DEPENDENT |
| C_e6081c5b | S6 session-transition | long | 395 | +0.017 | 1.03 | +0.160 | 1.01 | A_profitable_but_fragile | **REJECTED-fragile** | SCIENTIFIC (fragile) | REGIME_INDEPENDENT |
| C_a55d34d8 | S17 weekly levels reject | short | 137 | +0.142 | 1.21 | +0.077 | 0.59 | A_profitable_but_fragile | **REJECTED-fragile** (knife-edge) | SCIENTIFIC (fragile) | REGIME_INDEPENDENT / level |
| C_38a4ea2c | S17 weekly levels reject | short | 187 | +0.057 | 1.08 | +0.031 | 0.56 | A_profitable_but_fragile | **REJECTED-fragile** (knife-edge) | SCIENTIFIC (fragile) | REGIME_INDEPENDENT / level |
| C_ff1d4063 | S1 liquidity-sweep MR | long | 326 | +0.020 | 1.04 | +0.064 | 0.56 | A_profitable_but_fragile | **REJECTED-fragile** (knife-edge, wo1<0) | SCIENTIFIC (fragile) | RANGE_DEPENDENT |

**Caveat (v1.6 §E):** the whole S-corpus shows the *opposite* of the lab's stated target — profitability carried by a few large trades (top-5 = 41% of contribution), median winner −0.231 R, win-rate <50%, 30.5% collapse without their best trade. All S-family metrics are GROSS/in-sample; none passed a validated cost model or OOS. Treat "classification" as research-worthiness, **not validation**.

### Population B — Discovery candidates (28; DC-0001…0026 Alpha #1 + AP2-DC-0001/0002 Alpha #2; M1/M15 microstructure events)
Red-Team verdicts (v1.6 §1–§2): 🟢 SURVIVED · 🟡 NEEDS-MORE-EVIDENCE · 🔴 REJECTED (archived, ID reserved). All lifecycle = `FROZEN` in the index; v1.6 is authoritative for the triage.

| ID | Title (mechanism) | RT | Current status | Failure vs pause | Regime relationship (now) |
|---|---|---|---|---|---|
| DC-0003 | Scale inversion — micro coils vs HTF compressions resolve oppositely | 🟢 | **FROZEN_CANDIDATE** (→ Stat Phase 2 authorized) | PAUSE (division closed mid-analysis) | TRANSITION / MULTI_REGIME |
| DC-0004 | NY prior-day-high sweep-reject → reversion | 🟢 | **INCONCLUSIVE** — matched-null p=0.021 sign-stable, but fails Bonferroni + **holdout consumed** by discretionary observation → capped `TESTABLE_BUT_INSUFFICIENT_EVIDENCE` | PAUSE (governance/contamination), NOT scientific failure | RANGE / REGIME_INDEPENDENT (session) |
| DC-0008 | Large M15 candle from sustained multi-minute volume (vs single-minute) | 🟢 | **FROZEN_CANDIDATE** (→ Stat Phase 2, bimodality test) | PAUSE (division closed) | TRANSITION |
| DC-0026 | Thin-liquidity daily-rollover parabolic spike fully reverses | 🟡 | FROZEN_CANDIDATE ("most solid of new batch") | PAUSE (infra) | TRANSITION / RANGE |
| DC-0001,0002,0005,0007,0009,0011,0012,0014,0016,0018,0019,0020,0021,0023 | velocity outlier / HTF compression→expansion (H4 bias) / third-test / equal-lows sweep-reclaim / 7-touch band / single-min sweep-reclaim / absorption / V-reversal / expansion-reversal / extreme-vol high-failure / weekend-gap / 18:00 sweep / decline-absorption / 8h choppy | 🟡 | FROZEN_CANDIDATE (NEEDS-MORE-EVIDENCE) | PAUSE (infra) | mixed: TRANSITION / RANGE / REGIME_INDEP |
| DC-0013 | NY large sustained 4-candle directional expansion (family container ~12 instances) | 🟡 | FROZEN_CANDIDATE (family) | PAUSE (infra) | TREND / TRANSITION |
| AP2-DC-0001 | (variant of DC-0018) extreme-vol fresh-high failure → decline | 🟡 | FROZEN_CANDIDATE (independent replication) | PAUSE | TRANSITION |
| AP2-DC-0002 | (variant of DC-0023) 8h choppy extreme-volume episode | 🟡 | FROZEN_CANDIDATE | PAUSE | TRANSITION |
| DC-0006 | Extreme-volume candle fails to extend | 🔴 | **REJECTED** (archived) | SCIENTIFIC | — |
| DC-0010 | Quiet-hour early-Asia volume break | 🔴 | **REJECTED** | SCIENTIFIC | — |
| DC-0015 | NY prolonged 11-candle expansion (~2h45m) | 🔴 | **REJECTED** (single-instance record) | SCIENTIFIC (non-generalizable) | — |
| DC-0017 | 12:30 UTC NFP-scale impulse holds | 🔴 | **REJECTED** (event-specific) | SCIENTIFIC | — |
| DC-0022 | NY-afternoon record duration/magnitude expansion | 🔴 | **REJECTED** (single-instance; magnitude claim superseded by DC-0024) | SCIENTIFIC | — |
| DC-0024 | London-morning record magnitude decline (125.7pt / 514.165pt addendum) | 🔴 | **REJECTED** (single-instance record) | SCIENTIFIC | — |
| DC-0025 | Two-candle escalating-volume waterfall, record volume | 🔴 | **REJECTED** (single-instance record) | SCIENTIFIC | — |

**Machinery note (not strategies):** `matched_null@v1` and `bonferroni@v1` are validation *methods* that reached `VALIDATED` (2/15) — they are NOT Alpha candidates and are excluded from the candidate counts.

---

## 5. Scientific failure vs infrastructure pause (the critical distinction)
- **B — paused because infrastructure was incomplete (NOT failed):** all 11 S-family B_research_candidates (paused for lack of a validated p-engine, ratified cost model, and OOS protocol at the time); DC-0003 & DC-0008 (SURVIVED Red Team, paused when Alpha #1 closed mid-Statistician-Phase-2); DC-0026 and the ~16 🟡 DC (frozen awaiting evidence). **DC-0004 is a special pause:** a real signal (p=0.021) whose decisive test was lost to **holdout contamination**, i.e. a governance/data pause — *its Bonferroni failure predates contamination, but it was never scientifically falsified on the merits.*
- **A — scientific failure:** the 6 A_profitable_but_fragile S-family (knife-edge / negative val_exp / n=28) and the 7 🔴 DC (single-instance descriptive records with no demonstrated repeatability).

## 7. Comparison with current ALPHA_CANDIDATE-001 (kept SEPARATE — not merged)
`ALPHA_CANDIDATE-001` = displacement + acceptance, **trend-conditioned continuation**, TRANSITION→TREND, M15, STRESS-positive but fat-tail-dependent (this-session discovery). Economic nearest-neighbours in the historical set: **S9 MTF-trend momentum** (trend continuation), **DC-0002 / DC-0013** (HTF compression→expansion / sustained directional expansion), **S6 session-transition momentum**. It is a **distinct, newly-registered mechanism** (N1 displacement + acceptance) not previously in either historical population. **Not merged, not promoted.**

- **HISTORICAL_CANDIDATE_COUNT = 45** (17 S-family + 28 discovery).
- **CURRENT_STAGE1_CANDIDATE_COUNT = 1** (ALPHA_CANDIDATE-001).
- **TOTAL_KNOWN_NON_REJECTED_CANDIDATES = 33** (historical non-rejected = 11 S-family B + 21 DC not-🔴 [incl. DC-0003/0004/0008/0026 + 15 🟡 + 2 AP2] = 32) **+ 1 current = 33.** (The 6 fragile S-family + 7 🔴 DC = 13 are excluded as rejected.)

## 8. HISTORICAL_CANDIDATES_WORTH_REVIEWING_NOW
Not falsified, meaningful positive evidence, paused mainly for infrastructure, and plausibly served by the now-available regime architecture (TREND_UP/DOWN, RANGE V4.4, TRANSITION, REGIME_INDEPENDENT):
1. **C_2d587447 — S5 opening-range momentum** (robustness 2.14, val_exp +0.179) — strongest historical; REGIME_INDEPENDENT/session; directly re-evaluable.
2. **C_0bb5095b / C_d008e0a4 — S9 MTF-trend momentum** (robustness 1.76 / 1.51) — TREND_UP; now has a real N1 trend gate (which we showed *adds value* for trend continuation).
3. **C_09d2245b — S20 hybrid sweep+MTF** (1.34) — MULTI_REGIME; testable across N1 regimes.
4. **DC-0003 — scale inversion** (SURVIVED Red Team) — compression-resolution; now measurable via N1 compression/displacement.
5. **DC-0008 — sustained-volume M15 candle** (SURVIVED Red Team; bimodality) — TRANSITION; aligns with the displacement family that just produced ALPHA_CANDIDATE-001.
6. **DC-0004 — NY sweep-reject reversion** (real p=0.021) — worth re-review **only on genuinely uncontaminated data**; its original holdout is burned, so it needs a fresh causal window and the regime architecture. Flag the contamination explicitly.
7. **C_954698b1 / C_9214b37b — S1 liquidity-sweep mean-reversion** — RANGE_DEPENDENT; now testable *as a feature-gated hypothesis* against V4.4 CONFIRMED (measure whether the detector adds value; do not assume it).

*Reason common to all:* positive in-sample evidence + a plausible causal mechanism + a regime-context tool that did not exist when they were paused. **Do not execute this review under this mandate.**

## 9. HISTORICAL_CANDIDATES_DO_NOT_REOPEN
| Candidate | Reason |
|---|---|
| DC-0006, DC-0010, DC-0015, DC-0017, DC-0022, DC-0024, DC-0025 | 🔴 Red Team REJECTED — single-instance descriptive records / event-specific, no demonstrated repeatability (superseded/non-generalizable) |
| C_3c96bb23 (S14 exhaustion) | negative val_exp (−0.137), A_fragile |
| C_46f00099 (S1 short) | n=28, knife-edge, val_exp NaN |
| C_a55d34d8, C_38a4ea2c (S17 short) | knife-edge, robustness <0.6 |
| C_ff1d4063 (S1 long) | knife-edge, wo1<0 |
| C_e6081c5b (S6) | A_fragile |
| C_11418358 (S17 breakout) | ⚠ re-open only with care: high in-sample exp but **val_exp −0.086** (out-of-sample/cost failure signal) — treat as cost-failure evidence unless a new causal rationale emerges |
*Rationale:* prevent Alpha from spending compute rediscovering already-falsified or non-repeatable ideas.

## §Bridge — contemporaneous-with-RANGE (NOT counted as "before RANGE")
The `flowb` economic-screening / detached-service `CAND-00xx` / `G-series` (incl. G0037 TREND_UP pullback, the canonical-rerun `CANONICAL_PROVISIONAL_SURVIVOR`) ran ~2026-07→08, overlapping the RANGE program. Listed for completeness only; **not** part of the pre-RANGE historical count, and kept separate from ALPHA_CANDIDATE-001.

## 10. Recommendation to CEO
1. **Portfolio has three separate tiers:** (a) 1 current Stage-1 candidate (ALPHA_CANDIDATE-001, fat-tail caveat) awaiting Statistician/Red Team; (b) ~7 historical candidates worth re-review (§8) — none falsified, all paused for infrastructure now available; (c) 13 do-not-reopen (§9).
2. **Highest-value historical re-reviews:** S5 opening-range momentum and S9 MTF-trend momentum — both have the strongest in-sample robustness and map cleanly onto the now-frozen regime architecture; S9 in particular is adjacent to the displacement/trend-continuation mechanism that just survived Wave 1.
3. **DC-0004 requires a governance decision** before any re-review (its holdout is burned; a fresh uncontaminated window would be needed).
4. **Do not treat the paused S-family/DC as rejected** — the pivot to RANGE/Market-Intelligence, not scientific failure, is why they stopped.
5. **No action taken under this mandate** beyond documentation. Recommend the CEO decide (a) proceed with ALPHA_CANDIDATE-001 Phase 2, and/or (b) authorize a *separate* historical-candidate re-review wave under the current architecture — as a new mandate, since this one is inventory-only.

---
**Status:** `ALPHA_HISTORICAL_CANDIDATE_INVENTORY_COMPLETE` · `READY_FOR_CEO_CANDIDATE_PORTFOLIO_REVIEW`.
Documentation only — no backtest, no retune, no VALIDATION/FINAL-HOLDOUT access (FINAL_HOLDOUT_ACCESS=0), no promotion, no AI Trader, no LIVE. STOP.
