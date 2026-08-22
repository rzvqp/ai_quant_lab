# ALPHA_GRAVEYARD

Falsified mechanisms — **do not re-run without genuinely new information (§4, §6, §12).** "Reopening the same dead mechanism under a new name" is forbidden. Repository records control.

## This loop (ALPHA-XAUUSD-CONTINUOUS-RESEARCH-LOOP-001)
- **F1 volatility compression -> expansion breakout** (swing, H4): symmetric path (MFE≈MAE), best-10%-removed<0, shorts negative, 300p structural stops, N tiny. DEAD both sides.
- **F2 exhaustion / over-extension reversion** (ATR-extension E{2.5,3.0}; D1 consecutive-run K{4,5}): decisively wrong-way — median MAE >> MFE, adverse-first 0.80–0.92. Fading over-extension in trend-dominated gold = getting run over. DEAD both sides.
- **F3 temporal/calendar** (day-of-week drift; weekly-open gap continuation & fade): DOW too weak (upRate≈0.5); gap-continuation best-10%-removed<0 and 2021<0. DEAD.
- **F5 SHORT** (compression continuation in D1-downtrend): regime-locked, best-10%-removed<0, DISC<0. NOT_SUPPORTED. (LONG side survived — see candidate.)
- **F4** is NOT graveyard: it is a documented **near-miss that maps onto the already-frozen LONG trend-beta** (kept as evidence, not a new strategy).
- **F6 down-expansion crash-momentum SHORT** (trailing ride, both un-gated and D1-down-gated): DEAD — gold's fast down-spikes **REVERT (get bought)**, not continue; posRate 0.29, all years negative incl 2022, best-10%-removed<0. The mirror confirmation of the structurally-bid market. Adds a 7th falsified SHORT mechanism class.
- **F7 prior-day-high breakout continuation LONG** (frequency-diversifier attempt): DEAD on DEV — tight 56p stop noise-stopped (advFirst 0.73), avgR<0, best10<0, all years<0. Faster/higher-frequency LONG events revert to the intraday tight-stop failure mode; only the SWING-scale wide-structural-stop LONG survives. (CALIB-positive but DEV-negative = noise, not selected.)

## Prior program (pre-existing reports in reports/alpha_discovery/ — CLOSED)
- Intraday **mean-reversion fades** of extremes — trend runs them over.
- Intraday **raw N-bar breakouts** — whipsaw (class-C 58–72%).
- **M15 / high-WR 1:1 trend-continuation** — WR ceiling ~50–60%; froze only weak survivors.
- **Session/liquidity sweeps** (Asia-High, London-PLH, PDH clean-short; Frankfurt/London false-drive; early-session trap) — AUC collapses under room/position control; several proven **tautological or proxy-contaminated** (London-PLH audit).
- **Nested-MTF bearish sequences**, **probabilistic bearish state models**, **post-E1 clean-path** — adverse-first path, no robust conditional edge.
- **H1/H4 regime transition**, **H1/generic protrend**, **H4 displacement-followthrough** — single-year positives / tail-carried; froze weak LONG trend-beta (HR-TU-pb-L, MT-H4-dispaccept-L).
- **RANGE families** (generic fade/breakout, failed-break/rotation, M15-structure/M5-entry) — no robust local-structure edge; RANGE detector (v4.4) frozen upstream.
- **Autonomous 6-family loop** (FAILED_REV, HTF_REACT, SESSION_ACC, MOM_IGN, STRUCT_RECLAIM, VOL_RESET) — all falsified; `SEARCH_SPACE_EXHAUSTED` for the intraday frontier.

## Standing structural lesson (why these die)
2021–2023 XAUUSD is **trend-dominated with high intraday noise**. Reversion/fade mechanisms get run over; neutral breakouts whipsaw; tight intraday stops are noise-stopped; SHORTs are regime-locked (2022). The **only** surviving edge class is **LONG trend-continuation** (now: generic beta = frozen; compression-timed re-entry = COMP-CONT-L candidate). See `ALPHA_FAILURE_MODE_MAP.md`.

## External-replication priority mandate (S2/S4, faithful frozen formalization — CLOSED)
- **S2 RANGE BREAKOUT** (`S2_NOT_SUPPORTED`): H1/H4 close-based boxes (body-envelope / close-extremes / close-IQR) + close-beyond breakout, entry-A (breakout) and entry-B (retest), no-chase $4, structural opposite-side SL. Gold **false-breaks** these boxes (adverse-first 0.72-0.89, P(+1R<-1R)~0.45); best-10%-removed<0, never all-years-positive. The external increments **hurt**: free-path (>=100p clear) and 1.3x volume both make it WORSE. Confirms/extends the prior RANGE-breakout graveyard on the specific external formalization.
- **S4 SWEEP REVERSAL** (`S4_NOT_SUPPORTED`): M5 sweep+reclaim of >=1-day levels (PDH/PDL, H4-swing, H1-24hi/lo), SL beyond sweep+$0.50. Reclaims **fail** (adverse-first 0.84-0.91); tight ~15p stops noise-stopped; best-5/10%-removed<0; DISC/CONF<0. `+quality`/anti-fade/invalidation overlays do not rescue; `+1-bar delay` degrades all.
- **S4 TREND-ALIGNED "golden pattern"** (`S4_TREND_ALIGNED_SUBFAMILY_NOT_SUPPORTED`): the predeclared strongest external form is the **WORST** subfamily in every level variant (rr1 -0.15 to -0.29). External "9/9" not reproducible; ignored as evidence per mandate. **Do NOT reopen S2/S4 under new names.**

## Historical different-population frontiers (b0 2011-2013 + b1 2016-2018, causal) — CLOSED
- **HF1 compression-timed SHORT continuation in D1 downtrend**: the bearish regime is *less dead* than 2021-2023 (2013 +0.52 @ rr3) but NOT robust — positive only in the single 2013 crash leg at high RR, best-10%-removed<0 (tail-carried), block-inconsistent (b0 +0.22 / b1 -0.27), RR-fragile (only rr3). The robust bearish edge on this population is H4-bo-raw-S (raw breakout) — compression-timing does not replicate it. Do NOT reopen.
- **HF2 range mean-reversion (fade extremes)**: DEAD even where a GENUINE range exists (2011-2012). Fading the top/bottom gets run over (MAE>>MFE, advF 0.75-0.80), best10<0, both blocks negative. Range boundaries not respected enough at H4 with structural stops. Extends the range/mean-reversion graveyard to the historical range regime. Do NOT reopen.

## Historical b0/b1 bearish frontiers (HF3/HF4) — CLOSED
- **HF3-A pullback-to-falling-EMA short**: NEAR-MISS (both blocks positive @rr2, avgR +0.109) but tail-carried (best10<0) and year-inconsistent (2012/2017<0). Not robust.
- **HF3-B breakdown-momentum trailing short**: DEAD (avgR<0, best10<0).
- **HF4 transition-onset short**: ROBUST on internal gates but **REDUNDANT_WITH_H4_BO_RAW_S** — 85% of trades within 3 days of a frozen H4-bo-raw-S entry (same-day 53%). Two triggers (20-bar-low breakdown vs TREND_DOWN transition-onset) capture the SAME bearish episodes in b0/b1. NOT frozen (would duplicate the frozen candidate, §9/§30). Also CALIB-flat + delay-sensitive. **Do NOT reopen bearish-short trigger variants on b0/b1 — the frontier is saturated by the frozen H4-bo-raw-S event.**

## Historical b0/b1 counter-trend LONG reversion (HF5) — CLOSED
- **HF5-A capitulation LONG** (oversold flush + up-close): DEAD (advF 0.78-0.83, MAE>>MFE, best10<0, b1 badly neg). Buying oversold flushes in the bear gets run over; the tiny positive cells are n=3 (2011).
- **HF5-B down-spike reversion LONG** (fade big down bar): DEAD (N=221, advF 0.87, best10<0, maxDD -62R). **Regime-dependent finding: down-spikes REVERT in the 2021-23 structurally-bid market (F6) but CONTINUE on b0/b1** — the reversion edge is a property of the 2021-23 bid, not universal. Mean-reversion is now dead on b0/b1 in BOTH directions (HF2 fade + HF5).

## Historical b0/b1 temporal (HF6) — CLOSED
- **HF6 D1 gap**: `NOT_TESTABLE` — the `_from_M15_v2` D1 bars are continuously synthesized (open == prior close), so there are no overnight gaps to trade. Honest data-structural note.
- **HF6 day-after-big-day continuation**: NEAR-MISS (rr1.5 avgR +0.132, both blocks+) but best-10%-removed<0 and 2018 negative -> fails gate. Fade weak. Not robust.

## Historical INTRADAY M15 frontiers — CLOSED
- **M15-F1 displacement->first-pullback->resume** (both sides, H4-regime-gated): LONG dead (WRt 0.16, intraday pullback rarely reaches 1R, tight 47p stop noise-stopped); SHORT marginal-but-fails-gate (best10<0, CONF<0, block-inconsistent, positivity concentrated in 2013 bear = H4-bo-raw-S episode). **Intraday tight stops are noise-stopped even in b0/b1's trending regimes -> the regime shift does NOT rescue intraday continuation (the 2021-23 intraday exhaustion is structural, not regime-specific).** Do NOT reopen displacement-pullback on M15.
