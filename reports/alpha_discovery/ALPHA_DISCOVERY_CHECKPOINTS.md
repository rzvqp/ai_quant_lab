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
