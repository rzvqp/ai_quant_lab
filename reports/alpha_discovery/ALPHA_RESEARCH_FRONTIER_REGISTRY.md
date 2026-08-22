# ALPHA_RESEARCH_FRONTIER_REGISTRY

Living registry for `ALPHA-XAUUSD-CONTINUOUS-RESEARCH-LOOP-001` (opened 2026-08-22). Global program status: **ACTIVE**. Each frontier records: economic question, horizon, timeframes, mechanism class, data consumed, hypotheses, dominant failure mode, scientific conclusion, status. No hidden research. Multiple-testing lineage is cumulative across the whole program — a survivor must disclose all prior search (§20).

Data population for this loop unless noted: **gated native-M5 -> M15/H1/H4/D1 causal aggregation, DEV 2021-07-27 -> 2023-12-29** (`edge_research._common.load`, file_sha `cbb6eebe…`, manifest 2.7.94). CALIB 2024-01 -> 2024-06-20 is out-of-selection robustness only. Price-only. No CALIB selection / 2025+ / N4 / V1 / protected-2024 / exogenous.

---

## GRAVEYARD FRONTIERS (prior program — CLOSED, do not re-run without genuinely new info) — §6, §12

| FRONTIER_ID | economic question | horizon | mechanism class | dominant failure mode | status |
|---|---|---|---|---|---|
| GY-INTRADAY-FADE | mean-reversion fade of extremes | intraday | mean-reversion | trend runs the fade over | CLOSED |
| GY-RAW-BREAKOUT | raw N-bar breakout (intraday) | intraday | breakout | whipsaw (class-C 58-72pct) | CLOSED |
| GY-TREND-CONT-M15 | M15 trend-continuation pullback | intraday | trend continuation | 1:1 WR ceiling ~50-60pct | CLOSED (froze weak survivors) |
| GY-HIGHWR-1TO1 | forced 70-80pct WR at 1:1 | intraday | trend continuation | WR ceiling structural | CLOSED |
| GY-SESSION-SWEEP | Asia/London/PDH/PLH sweep + clean-short | intraday | liquidity reversal | AUC collapses under room control | CLOSED (NOT_SUPPORTED) |
| GY-NESTED-MTF-SHORT | nested MTF bearish sequence | intraday | price sequence | adverse-first path | CLOSED |
| GY-PROB-STATE | probabilistic bearish state model | intraday | state model | no robust conditional edge | CLOSED |
| GY-H1H4-TRANSITION | H1/H4 regime transition entry | intraday->H1 | transition | single-year positives | CLOSED |
| GY-PROTREND | H1/generic pro-trend entry | intraday->H1 | trend continuation | tail-carried, best-10pct-rem<0 | CLOSED (froze HR-TU-pb-L) |
| GY-H4-DISP-FOLLOW | H4 displacement + acceptance follow | H4 | displacement continuation | regime-locked LONG | CLOSED (froze MT-H4-dispaccept-L) |
| GY-AUTONOMOUS-6FAM | FAILED_REV/HTF_REACT/SESSION_ACC/MOM_IGN/STRUCT_RECLAIM/VOL_RESET | intraday->H1 | mixed | all falsified, best-10pct-rem<0 | CLOSED (SEARCH_SPACE_EXHAUSTED) |

**Frozen survivors (SEPARATE — not in this loop, §29-31):** S5 (validated), H4-bo-raw-S (in independent validation, 2011-2018 population), HR-TU-pb-L, MT-H4-dispaccept-L (weak LONG trend-beta, regime-dependent). Do not modify, clone, retune, or use their results to optimize new work.

---

## ACTIVE / QUEUED FRONTIERS (this loop)

| FRONTIER_ID | economic question | horizon | TFs | mechanism class | NEW pre-entry info | status |
|---|---|---|---|---|---|---|
| F1-VOL-EXP | after a genuine H4/D1 volatility compression resolves into directional expansion, does favorable swing continuation occur before destructive adverse movement? | multi-day swing | D1 ctx / H4 signal | volatility-regime transition (squeeze -> expansion) | a volatility regime just flipped compressed->expanding | **CLOSED_NO_ROBUST_ALPHA** |
| F2-EXH-REV | after price becomes statistically over-extended from its D1 anchor (distance / consecutive-run), does a swing mean-reversion pay before continuation? | multi-day swing | D1 ctx / H4 signal | exhaustion / over-extension reversal | price is statistically far from anchor (not a generic fade) | **CLOSED_NO_ROBUST_ALPHA** (advFirst 0.80-0.92; MAE>>MFE; wrong-way) |
| F3-TEMPORAL | does the week/day calendar structure (new-week open acceptance, day-of-week drift) shift the forward path distribution? | multi-session swing | D1 / week | temporal / calendar | temporal position (non-price information class) | **CLOSED_NO_ROBUST_ALPHA** (DOW weak; gap-cont best10<0, 2021<0) |
| F4-DRIFT | is there harvestable swing drift per confirmed trend-regime onset under a horizon (time-based) payoff? | multi-day swing | D1 ctx / H4 signal | trend drift, horizon payoff | regime onset + HTF alignment | **CLOSED_NEAR_MISS** (LONG D1-aligned H=24 clean but horizon-fragile, arbitrary stop, = frozen trend-beta) |
| F5-COMPCONT | does an H4 volatility compression inside a confirmed D1 trend mark a low-risk re-entry that continues before it fails? | multi-day swing | D1 ctx / H4 signal | compression-timed trend continuation (structural stop) | volatility contracted inside a confirmed HTF trend | **SURVIVOR (LONG) `COMP-CONT-L-rr2` FROZEN @ 4082c5c -> `PENDING_INDEPENDENT_VALIDATION` (removed from active research, §12 addendum)** ; SHORT closed (regime-locked) |
| F6-CRASHMOM | are gold's fast down-EXPANSION spikes (risk-off, close-near-low, new-low breakdown) a momentum SHORT that continues with a trailing ride? distinct from the 26 structural shorts (fixed-RR) | multi-day swing | H4 signal, no/opt D1 gate | down-expansion momentum + trailing exit | a high-velocity directional down-thrust just printed | **CLOSED_NO_ROBUST_ALPHA** (down-spikes REVERT/get-bought; all years neg incl 2022; best10<0) |
| F7-PDHBREAK | does a prior-day-high breakout continue as a faster, low-overlap LONG (frequency diversification)? | intraday->swing | D1 ctx / H4 signal | daily-structure breakout continuation | first close above the completed daily high in a D1 uptrend | **CLOSED_NO_ROBUST_ALPHA** (DEV avgR<0, best10<0, advFirst 0.73 noise-stopped; CALIB+ but DEV-fail=noise) |
| F-EXT-S2 | (external replication, priority) does a close-based range box + close-beyond breakout produce favorable-before-adverse continuation? | swing | H1/H4 box | external range-breakout | close beyond a consolidation box | **CLOSED_NO_ROBUST_ALPHA** `S2_NOT_SUPPORTED` — false-break dominated (advFirst 0.72-0.89); free-path & volume add negative value |
| F-EXT-S4 | (external replication, priority) does an M5 sweep+reclaim of a >=1-day structural level reverse? incl. trend-aligned "golden pattern" | intraday | D1/H1/H4 level, M5 reclaim | external sweep-reversal | M5 close back inside after sweeping a level | **CLOSED_NO_ROBUST_ALPHA** `S4_NOT_SUPPORTED` + `S4_TREND_ALIGNED_NOT_SUPPORTED` — reclaims fail (advFirst 0.84-0.91); golden pattern is the WORST subfamily |

Selection order = highest information given accumulated evidence: gold 2021-2023 is trend-dominated (fades die, breakouts whipsaw at intraday stops). F1 harnesses the trend but with a genuinely new *volatility-regime* trigger and swing-scale structural stops (where noise/stop ratio is smaller) — the horizon the prior program never converted. F2 tests the opposite (reversion) under strict over-extension conditioning. F3 tests a non-price information class.

**A frontier is CLOSED when its bounded hypothesis budget (default <=6 rules / family, ~10-20 hypotheses) is exhausted without a robust survivor; then the loop pivots automatically (§33, §43). A CLOSED frontier is not a program stop.**
