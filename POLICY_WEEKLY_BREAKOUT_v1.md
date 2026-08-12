# POLICY — Weekly-Level Breakout / Continuation — **v1.0 (Part A + Part B)**

# 🟢 PROMISING — SURVIVES FAT-TAIL CHECK · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0037.** The **first candidate in the project with a robust economic edge** — survives the
fat-tail check (single-best-trade share + top-1%-trimmed avg_R) AND is stable across years. Produced by
the Flow-B economic-screening flow (IDEA → POLICY → QUICK BACKTEST → SCREEN). Route 2 (breakout), the
opposite of the eliminated level-FADE class.

## WHY THIS EXISTS (the finding chain)

The level-FADE class (CAND-0001 PDH/PDL, CAND-0027 session, CAND-0006 weekly, CAND-0005 BPR) was proven
to have NO robust edge — every positive total was a tiny-stop fat-tail (best trade 20–78% of total;
top-1%-trimmed avg_R negative). Root cause: the touch-bar-extreme stop is microscopic, so the rare
survivor that reaches a far target prints a 100–1400R fluke. **The fix (pre-registered): trade the
BREAKOUT with a STRUCTURAL, non-microscopic stop.** Screened on all three level populations:

| population | n | win% | avg_R | median_R | best-share | top-1%-trimmed avg_R | years+ | verdict |
|---|---|---|---|---|---|---|---|---|
| PDH/PDL break | 1204 | 46.4% | +0.005 | −0.04 | 0.62 | −0.023 | 5/8 | flat, no edge |
| session break | 4543 | 44.4% | +0.007 | −0.07 | 0.22 | −0.039 | 4/8 | flat, no edge |
| **weekly break** | **246** | **50.8%** | **+0.062** | **+0.013** | **0.17** | **+0.043 (PF 1.21)** | **7/8** | **🟢 PROMISING** |

Also confirmed on the same run: **CAND-0009 (level break + displacement, SMALL "broken-level" stop):
ELIMINATED** — avg_R −0.084, PF 0.88, 3/8 years, trims to −0.26 (its pre-repair +146R was an engine
artifact). **The structural stop is the decisive difference** — weekly-break (opposite-level stop,
≈ full range) survives; CAND-0009 (broken-level stop, small) dies. The edge is **specific to the WEEKLY
timeframe** — daily and session breakouts are flat noise.

## PART A — ENTRY MECHANISM — **DEFINED**

Mechanism: a prior-week extreme that the market CLOSES THROUGH is a genuine range expansion; price
continues in the break direction.

| field | value · reason |
|---|---|
| **family** | `weekly_level_breakout_continuation` (MK-04) |
| **timeframes_used** | execution TF + prior-week H/L; `week_index` from 17:00-NY `day_index` (`derive_week_index`). |
| **activation** | `compute_prior_week_levels` (RATIFIED): PWH/PWL of the prior week, active during the current week (`available_idx` = first bar of the current week, Q4 no-lookahead). |
| **trigger** | the **first bar in the current week whose CLOSE closes THROUGH the level** in the break direction: WEEKLY_HIGH → `close[j] > price` (break up); WEEKLY_LOW → `close[j] < price` (break down). Consumed once. Close-through known at `j` → no lookahead. |
| **entry** | `next-open` after `j`. Direction = **WITH the break**: WEEKLY_HIGH break → **LONG**; WEEKLY_LOW break → **SHORT**. |
| **invalidation** | price falls back to the opposite prior-week level (see Part B). |
| **no_trade_rules** | one break per level (D7); block reset (D3_bis). No trade if `next-open` already beyond the stop. |
| **expiry** | the break must occur within the current week; else the level expires unbroken. |

## PART B — RISK MANAGEMENT — **COMPLETED (single structural variant, chosen BEFORE results)**

Family = range breakout. The OPPOSITE prior-week level is the structural (non-microscopic) invalidation —
this is the whole point: it removes the tiny-stop fat-tail that killed the fade.

| field | method · reason |
|---|---|
| **stop_loss** | **The OPPOSITE prior-week level** — long (WEEKLY_HIGH break) → `WEEKLY_LOW`; short → `WEEKLY_HIGH`. **Reason:** a genuine breakout does not return through the entire prior-week range; the far side is the structural, non-microscopic invalidation. ≈ full-week-range 1R → spread-in-R is negligible → cost-robust. |
| **exit** | **Week-boundary live time-stop** (bars until `week_index` changes). **Reason:** a weekly breakout's natural horizon is the current week; the level was defined for it. No fixed target (no invented R:R). |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized to `entry − opposite level`. |
| **min_trades** | **Deferred to the Statistician** (n=246 over 10 yr ≈ 25/yr). |

**Validity guard:** no trade if `next-open` already beyond the opposite-level stop. No lookahead. **Runnable:**
`edge_research/cand_level_breakout.py` (weekly_break case).

## ECONOMIC SCREEN (Flow B, GROSS R, holdout sealed, worst-case intrabar)

n=246 · win 50.8% · avg_R +0.062 · median +0.013 · PF 1.302 · best-trade share 17.4% ·
**top-1%-trimmed avg_R +0.043 / PF 1.205 (SURVIVES)** · **7/8 years positive** (only 2020 negative).
Cost note: the full-week-range stop dwarfs spread → the gross edge is essentially intact after costs
(unlike a tight-stop strategy). **Verdict: PROMISING → route to Red Team / Statistician / formal validation.**

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `5443077a62ed574a4316327f04822bbc0cdffa97` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_prior_week_levels`, `derive_week_index`, `LevelKind.WEEKLY_HIGH/LOW` | `code/institutional_levels.py` | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |

*17:00-NY `day_index` = the verbatim caller-side convention (`obdz002_population._day_index`), supplied
by `edge_research/_screen.py:day_index_ny17`. Verify the hash, don't assume it.*

## Verdict — **PROMISING (survives fat-tail + year-stable)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
→ **Red Team / Statistician / formal validation** (the first candidate to earn the expensive pipeline).
