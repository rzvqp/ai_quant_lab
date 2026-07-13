# TIER B REPORTS + CONSOLIDATED S21–S40 (branch family-implementation-s21-s40)

Companion to `S21_S40_IMPLEMENTATION_REPORTS.md` (Tier A). Same frozen engine/screen/metrics. Research 60% /
validation (OOS) 20% / holdout SEALED. Cost drag ≈ 0.027 R/trade (engine 2×cost = 0.4 price round-trip ÷ ~15
price typical 1.5·ATR risk) — the SAME order as the small edges, so high-frequency families are cost-dominated.
Two definitional corrections were made BEFORE seeing PnL (per family): S22 breakout-crossing bug + step
selectivity; S28 anchor selectivity. No PnL-driven tuning.

## S22 — Round-number magnet / rejection  →  POSITIVE — KEEP (1 RW)
- Mechanism: psychological $ levels ($50/$100 on gold) cluster limit orders/stops.
- Definition: nearest round level step in {50,100}. reject = high/low tags level, close rejected back → fade;
  breakout = floor(close/step) changes between bars (crossed a level) → follow. Entry next open; stop 1.5·ATR
  or beyond level; exit rr2/rr3/time. (step 10/25 dropped: <0.6% of price, non-selective. breakout logic fixed
  from a circular-comparison bug. Both pre-PnL definitional fixes.)
- Grammar 24 · valid 24 · profitable 6 · RW 1. bestExp +0.121, bestPF 1.18.
- RW `46c7c98c262b` (step=100 breakout, atr, rr3): n=223, exp=0.082, PF=1.12, maxDD 22.5R, win 34%, 15/25 pos
  months, 4 yr, t1=0.02, OOS +0.147. Several step=50 breakouts profitable (+OOS) but maxDD>25 → not RW.
- Finding: ONLY breakout profits, not reject → round numbers act as MOMENTUM triggers, not reversal levels.
  New mechanism (round-number momentum), distinct from all S1–S20. Verdict: POSITIVE — KEEP.

## S24 — Overnight variance / session carry  →  EXPLORATORY
- Prior session's close-in-range conditions the next session; carry/fade at target session start.
- Grammar 24 · profitable 2 · RW 0. Best (ny/fade/bar1/time): n=551, exp=0.081, PF=1.11, but maxDD 33.4R (>25)
  and OOS −0.075. Signal exists (NY session mean-reversion) but fails robustness + OOS. New axis, not validated.

## S25 — Volatility-regime onset  →  NEGATIVE — CLOSED
- Grammar 12 · profitable 0 · bestExp −0.080. Trading the vol-regime transition (expand→momentum /
  contract→revert) has no edge; distinct from S23 but also negative.

## S27 — VWAP reclaim in trend  →  NEGATIVE — CLOSED
- Grammar 24 · profitable 0 · bestExp −0.064 · n=2267–4364 (very high → cost-dominated). Reclaim fires too
  often; cost drag buries any edge.

## S28 — Anchored-VWAP reaction  →  NEGATIVE — CLOSED
- Grammar 12 (anchors week/month; day/swing/impulse dropped pre-PnL — reset too fast to form a stable cost
  basis / non-selective). profitable 0 · bestExp −0.040. Finding: intraday anchors reset too often on M15 to
  be meaningful institutional cost bases.

## S29 — Day-of-week effect  →  EXPLORATORY (data-mining / overfit suspect)
- Grammar 20 (5 weekdays × 2 sides — bounded but multiple-testing). profitable 6 · screen-RW 4.
  In-sample strong (Thursday-long exp +0.419, PF 1.59) BUT 3 of 4 RW have NEGATIVE OOS (Thu-long OOS −0.299,
  Fri-long −0.261); only Fri-long/time is OOS-positive (+0.199).
- Finding: textbook seasonality OVERFIT to the bull-market sample. The screen (no OOS) flags them; OOS refutes
  them. Verdict: EXPLORATORY, NOT positive. Must be FDR-controlled + OOS-validated before any belief.

## S30 — Kill-zone / time-window effect  →  NEGATIVE — CLOSED
- Grammar 12 · profitable 0 · bestExp −0.016. London/NY kill-zone breakout/reversal has no edge.

## S31 — Month-end / month-start effect  →  EXPLORATORY (overfit suspect)
- Grammar 12 · profitable 2 · screen-RW 2 (month_start short). But n=38 (tiny) and OOS −0.42/−0.44.
  Small-sample calendar artifact. Verdict: EXPLORATORY, NOT positive.

---

# CONSOLIDATED TABLE — S21–S40 implemented so far (14 families, Tier A + B)

| Family | Mechanism | Hyps | Prof | RW | BestExp | PF | repTrades | MaxDD | OOS(rep) | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| S21 | equal-highs/lows liq raid | 48 | 0 | 0 | −0.092 | 0.91 | 1592 | 262R | −0.09 | NEGATIVE — closed |
| S22 | round-number momentum | 24 | 6 | 1 | +0.121 | 1.18 | 223 | 22R | +0.15 | POSITIVE — keep |
| S23 | squeeze breakout + HTF | 32 | 0 | 0 | −0.091 | 0.88 | 624 | 74R | +0.08 | NEGATIVE — closed |
| S24 | overnight/session carry | 24 | 2 | 0 | +0.081 | 1.11 | 551 | 33R | −0.08 | EXPLORATORY |
| S25 | vol-regime onset | 12 | 0 | 0 | −0.080 | 0.89 | 854 | 73R | −0.10 | NEGATIVE — closed |
| S26 | value-area reject/accept | 32 | 0 | 0 | −0.123 | 0.85 | 941 | 129R | −0.25 | NEGATIVE — closed |
| S27 | VWAP reclaim in trend | 24 | 0 | 0 | −0.064 | 0.92 | 2267 | 205R | +0.13 | NEGATIVE — closed |
| S28 | anchored-VWAP reaction | 12 | 0 | 0 | −0.040 | 0.94 | 553 | 47R | +0.03 | NEGATIVE — closed |
| S29 | day-of-week effect | 20 | 6 | 4 | +0.419 | 1.59 | 112 | 22R | −0.30 | EXPLORATORY (overfit) |
| S30 | kill-zone window | 12 | 0 | 0 | −0.016 | 0.98 | 946 | 123R | +0.20 | NEGATIVE — closed |
| S31 | month-end/start | 12 | 2 | 2 | +0.178 | 1.26 | 38 | 9R | −0.42 | EXPLORATORY (overfit) |
| S38 | patient pullback cont. | 36 | 0 | 0 | −0.098 | 0.88 | 1363 | 158R | +0.03 | NEGATIVE — closed |
| S39 | trend-efficiency cont. | 24 | 2 | 2 | +0.031 | 1.09 | 314 | 12R | +0.02 | POSITIVE — keep |
| S40 | regime router | 16 | 0 | 0 | −0.118 | 0.83 | 2079 | 301R | −0.12 | NEGATIVE — closed |
| Σ | | 328 | 26 | 10 | | | | | | 2 KEEP, 3 EXPLORATORY, 9 closed |

## Answers to the CEO's Tier-B closing questions
1. **Positive among S21–S31 (Tier A+B):** genuine (RW + OOS-supported) = **1: S22**. Screen-RW-but-OOS-refuted:
   S29, S31 (overfit). (S39 is Tier-A, also positive.)
2. **Research-Worthy:** the screen counts 10 across the 14 families, but only **3 are OOS-supported**
   (S22×1, S39×2). The other 6 (S29×4, S31×2) fail OOS = data-mining artifacts.
3. **Mechanisms that FAILED:** sweep-without-confirmation (S21); squeeze/breakout chasing (S23); value-area
   σ-proxy (S26); VWAP reclaim (S27); anchored-VWAP (S28); vol-regime onset (S25); kill-zone (S30); patient
   pullback continuation (S38); naive always-on router (S40). Theme: breakout/continuation chasing and broad
   high-frequency signals lose to cost drag; counter-trend fades lose in the bull sample.
4. **Mechanisms that PRODUCED signal:** (a) round-number MOMENTUM (S22) — genuine, +OOS; (b) trend-efficiency
   continuation (S39) — genuine, +OOS; (c) NY session-carry MR (S24) — weak, no OOS; (d) calendar/seasonality
   (S29/S31) — strong in-sample, REFUTED OOS.
5. **Economic duplicates?** S22-breakout vs S39 are both momentum-flavoured but mechanistically distinct
   (psychological-level break vs efficient-trend continuation) — not duplicates. S23/S27/S30 overlap the
   "breakout-chasing" negative cluster; S29/S31 share the same overfit failure mode.
6. **What goes to matched-null later:** the 2 OOS-supported KEEP families **S22** and **S39**, joining S1–S20's
   shortlist for the eventual CEO-gated matched-null → global-FDR pass. S24 optionally as an exploratory probe.
   NOT S29/S31 (overfit).
7. **Is external data (S32–S37) still justified?** YES — arguably more so. The T0 universe is now largely
   exhausted: of 14 T0 families only 2 carry a real edge, and both are momentum in a bull trend (drift-suspect).
   The lab lacks direction-symmetric, drift-independent factors; the intermarket/positioning families (DXY,
   real yields, risk-regime, COT) are precisely the missing axis. The T0 results strengthen the Tier-C case
   (still CEO-gated; no acquisition performed).

## Guarantees
Engine frozen (`mstrat.py`/`s1.py`/`mtf.py`/`run_full_campaign.py`/screen/stop-floor/matched-null/holdout all
untouched — new code only in `code/mstrat_ext.py`). No verdicts issued. No optimization (definitional fixes
only, pre-PnL). No holdout, no global-FDR. Artifacts: `results/ext_families/*_results.parquet` +
`EXT_FAMILY_RESULTS.parquet`.
