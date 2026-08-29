# TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2

**STATUS: FINAL.** Supersedes both the original `PROVISIONAL_PREMATURE_BOUNDARY` version (stopped
2020-06-30 00:00:00 UTC) and the intermediate `PROVISIONAL_INCOMPLETE_BOUNDARY` version (stopped
2020-06-30 19:15:00 UTC after a CEO STOP that was itself later corrected). Neither prior version is
deleted, per standing governance; both are retained for the record, and this version's content
fully absorbs and extends them.

**`FINAL_Q2_LAST_BAR = 2020-06-30 23:45:00 UTC`** (O1784.436/H1784.436/L1784.436/C1784.436,
V34.75). This is the true, complete calendar-Q2 boundary. Replay processed every M15 bar from
2020-04-01 00:00:00 UTC through this bar, one-step-one-read, and stopped with `current_date =
1593561599` (2020-06-30 23:59:59 UTC, one second before the first Q3 bar). The first Q3 bar
(2020-07-01 00:00:00 UTC) was never revealed at any point across all three versions of this
checkpoint — confirmed via explicit python3 timestamp verification before the replay engine was
allowed to advance further. `Q3_FIRST_BAR_ALREADY_VISIBLE` does not apply.

**Explicit trade-count limitation (per direct CEO instruction):**

```
TOTAL_APPRENTICESHIP_TRADES      = 66
STRUCTURED_COMPARABLE_TRADES     = 17   (#48, #51-#56 backfilled + #57-#66 fully evidenced)
NOT_STRUCTURED_COMPARABLE        = 49   (#1-#47 excl. #48, #49, #50 — RESULT_R/points not
                                          reconstructable without hindsight; deferred per
                                          EVIDENCE_UPGRADE_METHODOLOGY_V1.md §2)
```

**No claim anywhere in this report — win-rate, expectancy, "best playbook," "most robust,"
regime performance, or otherwise — extends beyond the 17 `STRUCTURED_COMPARABLE_TRADES`.** The
other 49 trades cannot be prospectively classified without hindsight (their entry-time context
tags, MFE/MAE, and in most cases even precise RESULT_R were never captured before Evidence
Upgrade V1 existed), so they are excluded from every statistic below, not estimated into them.
Any reference to "this window," "this checkpoint's trades," or a specific N always means a subset
of the 17, explicitly stated at each table.

Prepared: 2020-06-30 23:45:00 UTC (replay clock) / finalized under direct CEO correction
(real-time) that superseded an earlier, premature CEO STOP, under standing CEO mandate
`AI_TRADER_MARKET_APPRENTICESHIP_V1`, Lane A (`HISTORICAL_MARKET_APPRENTICESHIP`),
`AI_TRADER_APPRENTICESHIP_V2` architecture.

**See also: [`TRADER_Q2_FORENSIC_REVIEW_2020.md`](./TRADER_Q2_FORENSIC_REVIEW_2020.md)** — a
separate, much deeper companion document (produced under a later CEO mandate, real-time) covering
trade-by-trade reasoning, why each loss/win happened, playbook/regime/MTF-alignment forensics,
management forensics (actual vs. static-baseline), rejected hypotheses, and the full Q3 TP1/TP2/TP3
management recommendation. This checkpoint remains the authoritative statistical record; the
forensic review is the authoritative narrative/causal record. Neither overwrites the other.

**Scope note:** built directly from this apprenticeship's governance files —
`TRADE_EVIDENCE_LOG.md`, `STRATEGY_EVIDENCE_DENOMINATOR.md`, `TRADER_STRATEGY_CANDIDATES.md`,
`REPLAY_DATA_GAP_LEDGER.md`, `2020_Q2_H4_LOG.md`, `AI_TRADER_REGIME_STRATEGY_MATRIX.md`, and the
frozen `checkpoints/TRADER_KNOWLEDGE_CHECKPOINT_2020_Q1.md`. All R/points/win-rate/expectancy
figures below were recomputed directly from the governance files' own recorded numbers (explicit
arithmetic, not narrative approximation) — see §21 for which fields are genuinely recoverable and
which are not.

---

## 1. Exact Q2 terminal replay state

- **current_date (replay engine):** 1593561599 (2020-06-30 23:59:59 UTC)
- **FINAL_Q2_LAST_BAR:** 2020-06-30 23:45:00 UTC — O1784.436 / H1784.436 / L1784.436 / C1784.436,
  V34.75 (flat, very thin)
- **Position at close of quarter:** FLAT. No open trade. Trade #66 (the only position open at the
  first provisional checkpoint) closed for real at 2020-06-30 15:00:00 UTC, 8h45m before the true
  quarter close (see §2).
- **Q3 leakage check:** no bar at or after 2020-07-01 00:00:00 UTC was ever revealed by
  `data_get_ohlcv` or `replay_step`, at any point across this checkpoint's three drafting passes.
  `Q3_FIRST_BAR_ALREADY_VISIBLE` does not apply.
- **Chart state:** the native `short_position` visualization for Trade #66 is frozen at its exact
  close time/price (entity `yGFKq9`, point2.time=1593529200). No further chart drawing occurred
  after the trade closed (FLAT for the remainder of the quarter, including the 19:15–23:45 UTC
  stretch processed after the CEO correction).
- **New data-integrity event in the final stretch:** GAP-084, a standard 75-minute daily-rollover
  gap (2020-06-30 20:45→22:00 UTC), logged in `REPLAY_DATA_GAP_LEDGER.md`. No apprenticeship
  impact — FLAT at the time. Gap count for the full file is now **39** (was 38 in the prior two
  drafts).

---

## 2. Final status of Trade #66

**CLOSED, LOSS.**

| Field | Value |
|---|---|
| Direction | SHORT |
| Entry | 1766.952 (2020-06-24 12:45:00 UTC) |
| Frozen SL | 1778.874 (HIT) |
| Frozen TP | 1747.566 (never reached — closest approach 0.006pts, 2020-06-26 14:15 UTC) |
| Exit fill | 1783.614 (close-based, bar close, 2020-06-30 15:00:00 UTC) |
| GROSS | −16.662pts |
| RESULT_R | **−1.398R** (risk 11.922pts) |
| MFE | 19.38pts / +1.626R (2020-06-26 14:15 UTC, near-full-TP approach) |
| MAE | 17.488pts / −1.467R (the triggering bar's own high, 1784.44, 2020-06-30 15:00 UTC) |
| Duration | 146.25 hours / 585 M15 bars |
| Static baseline | RESOLVED_VIA_ORIGINAL_STOP, identical to actual (no trailing/discretionary
management occurred — fixed-SL/TP methodology). ACTUAL_VS_STATIC = 0.000. |

**The 14:30 UTC near-miss (for the record, since it drove a direct user request this session):**
high 1778.278 (0.596pts below the frozen SL), close 1777.897 (0.977pts clear), on heavy real volume
(V1264). Under the standing close-based execution convention — a level triggers only on a bar's own
CLOSE crossing it; wicks never trigger, applied symmetrically in both directions across this entire
apprenticeship (e.g. trade #62's three wick-piercings that still didn't trigger, trade #59's
trail-flip) — this bar did not close the trade. The user asked twice, in real time, for this
near-miss to be retroactively scored a WIN; both requests were declined on the grounds that
altering #66 alone, after the fact, would break the same symmetric rule that has protected every
other trade in both directions. Thirty minutes later the trade closed for real, adversely, on its
own close, under the unmodified frozen SL. Trade #66's FROZEN_SL/FROZEN_TP were never altered.

**Structural TP Execution Buffer V1** was installed prospectively during this trade's life
(real-time CEO decision) and explicitly does **not** apply to #66 — its FROZEN_TP remained the bare
structural target (1747.566) throughout, with no buffer. It governs trades opened from this point
forward; none has opened yet.

Full detail: `TRADE_EVIDENCE_LOG.md` ("TRADE #66 — EVIDENCE CLOSE"), `2020_Q2_H4_LOG.md`
(2020-06-30 MATERIAL_EVENT entries).

---

## 3. Complete Q2 trade statistics

Two tiers of evidence, per standing governance — never blended without saying so:

- **Fully evidenced (#57–#66, n=10):** R, MFE, MAE, multi-timeframe alignment, and static-baseline
  comparison all recorded at entry/close, no hindsight.
- **Backfilled (#48, #51–#56, n=7):** RESULT_R and RESULT_PTS only (computed from entry/stop/exit
  values logged in real time before outcome was known); MFE/MAE/static-baseline are
  `NOT_RECOVERABLE_WITHOUT_HINDSIGHT` / `DEFERRED` and are not estimated.
- Combined dataset this checkpoint can speak to: **n=17** (#48, #51–#66). Trades #1–#47 (excl.
  #48), #49, #50 remain out of scope entirely — not included in any statistic below.

### 3.1 Fully evidenced trades (#57–#66)

| # | Dir | Entry | Result (pts) | Result R | Alignment | Playbook | Notes |
|---|---|---|---|---|---|---|---|
| 57 | SHORT | 1706.11 | −6.192 | −1.361 | FULLY_ALIGNED | A (pre) | Countertrend-spike exhaustion |
| 58 | SHORT | 1740.327 | +12.259 | +2.463 | FULLY_ALIGNED | A (pre) | Largest MFE (+3.743R); trailed result underperformed static baseline by 15.233pts / 3.061R |
| 59 | SHORT | 1712.008 | −0.654 | −0.046 | FULLY_ALIGNED | A (pre) | Trail-flip; underperformed static baseline by 31.459pts / 2.225R |
| 60 | SHORT | 1707.01 | −8.948 | −1.379 | FULLY_ALIGNED | A (pre) | Close-based fill overshot nominal stop by 2.458pts |
| 61 | SHORT | 1707.856 | −12.237 | −1.150 | FULLY_ALIGNED | A (pre) | Stop tested 4x over 4 bars (0.27–1.63pts margins) |
| 62 | SHORT | 1680.167 | −8.342 | −1.001 | FULLY_ALIGNED | A (pre) | Stop wick-pierced 3x (closest 0.147pts); closed almost exactly −1.0R |
| 63 | LONG | 1695.555 | +23.187 | +2.306 | TRANSITIONAL | B | Underperformed static-horizon baseline by 7.406pts / 0.737R; avoided −0.506R MAE a static hold would have carried |
| 64 | SHORT | 1740.496 | +6.382 | +1.443 | PARTIALLY_ALIGNED | A-prime | First WITH-trend SHORT to pass the corrected rule; static baseline never resolved (STILL_OPEN at trade close) |
| 65 | SHORT | 1724.903 | −8.211 | −1.119 | FULLY_ALIGNED | A-prime | First trade closed under fixed-SL/TP methodology |
| 66 | SHORT | 1766.952 | −16.662 | −1.398 | PARTIALLY_ALIGNED | A-prime | Closed this window — see §2 |

**Net, #57–#66 (n=10): −0.156R** (3 wins: #58 +2.463, #63 +2.306, #64 +1.443 = +6.212; 7 losses:
#57 −1.361, #59 −0.046, #60 −1.379, #61 −1.150, #62 −1.001, #65 −1.119, #66 −1.398 = −7.454; net =
6.212 − 7.454 = **−1.242R**). *(Correction from the provisional checkpoint: that version reported
+0.156R across #57–#65 only, before #66's resolution flipped the window's fully-evidenced net to
−1.242R.)*

### 3.2 Backfilled trades (RESULT_R/RESULT_PTS only, pre-Evidence-Upgrade)

| Trade | Dir | Result (pts) | RESULT_R |
|---|---|---|---|
| #48 | LONG | −1.416 | −0.182 |
| #51 | SHORT | +22.386 | +6.120 |
| #52 | SHORT | −1.743 | −0.718 |
| #53 | LONG | −0.747 | −0.110 |
| #54 | SHORT | −7.834 | −1.006 |
| #55 | SHORT | +3.256 | +0.447 |
| #56 | SHORT | +5.857 | +0.616 |

### 3.3 Combined ledger (n=17: #48, #51–#66) — recomputed directly from §3.1+§3.2

| Group | N | Wins | Losses | Win rate | Net R | Net pts | Avg R/trade | Median R | Profit factor | Max DD (R, sequential) |
|---|---|---|---|---|---|---|---|---|---|---|
| **ALL** | 17 | 6 | 11 | 35.3% | +3.925R | +0.341pts | +0.231R | −0.182R | 1.414 | 3.576R |

Net R (+3.925) and net points (+0.341) diverge sharply because risk sizes (INITIAL_RISK_POINTS)
varied a lot across trades (2.427pts to 14.138pts) — R-normalization and raw points tell different
stories on the same 17 trades. Both are reported; neither is hidden in favor of the other. This
divergence recurs at the playbook level (§8) and is itself one of this window's more important
honest findings, not a rounding artifact.

---

## 4. Wins / losses / open-at-boundary

- **Wins (n=17 combined):** 6 — #51 (+6.120R), #58 (+2.463R), #63 (+2.306R), #55 (+0.447R), #64
  (+1.443R), #56 (+0.616R).
- **Losses (n=17 combined):** 11 — #48, #52, #53, #54, #57, #59, #60, #61, #62, #65, #66.
- **Open at boundary:** none. FLAT since Trade #66 closed at 2020-06-30 15:00:00 UTC, 8h45m before
  the true quarter close (2020-06-30 23:45:00 UTC).

---

## 5. Net result

- **Combined (n=17), R-normalized: +3.925R.**
- **Combined (n=17), raw points: +0.341pts.**
- **Fully evidenced only (n=10, #57–#66): −1.242R** (this is the set with genuine MFE/MAE/alignment
  detail; the sign is negative here specifically because #66 flipped the small provisional +0.156R
  into a net loss).
- No claim of a validated edge is made from either figure — see §21.

---

## 6. Result_R distribution (n=17 combined)

```
+6.120  ################################################## #51
+2.463  ####################                                #58
+2.306  ###################                                 #63
+1.443  ############                                        #64
+0.616  #####                                                #56
+0.447  ####                                                 #55
-0.046  ▏                                                    #59
-0.110  ▉                                                    #53
-0.182  █▍                                                   #48
-0.718  █████▊                                               #52
-1.001  ████████                                             #62
-1.006  ████████                                             #54
-1.119  █████████                                            #65
-1.150  █████████▎                                           #61
-1.361  ███████████                                          #57
-1.379  ███████████                                          #60
-1.398  ███████████▏                                         #66
```

Median R across all 17 is **−0.182R** (below zero) while the mean is **+0.231R** — the distribution
is right-skewed: most trades lose a modest amount, and the net-positive R figure is carried by one
outsized win (#51, +6.120R) plus two solid wins (#58, #63). Remove #51 alone and net R across the
remaining 16 drops to **−2.195R** — this single trade is doing more work than any playbook or rule.
This fragility is stated plainly, not smoothed over.

---

## 7. MFE / MAE evidence (fully evidenced trades only, n=10 — not recoverable for the 7 backfilled trades)

| # | MFE (R) | MAE (R) | Result R | MFE captured? |
|---|---|---|---|---|
| 57 | 0.138 | 1.586 | −1.361 | No — MFE was trivial, MAE dwarfed it |
| 58 | 3.743 | 0.109 | +2.463 | Partially — 66% of MFE captured |
| 59 | 1.586 | 0.267 | −0.046 | No — trail-flip erased a 1.586R favorable excursion |
| 60 | 0.223 | 1.497 | −1.379 | No |
| 61 | 0.695 | 1.280 | −1.150 | No |
| 62 | 1.168 | 1.058 | −1.001 | No |
| 63 | 3.163 | 0.506 | +2.306 | Partially — 73% of MFE captured |
| 64 | 2.467 | 0.209 | +1.443 | Partially — 58% of MFE captured |
| 65 | 1.652 | 1.119 | −1.119 | No — 1.652R favorable excursion fully given back |
| 66 | 1.626 | 1.467 | −1.398 | No — came within 0.006pts of full TP, gave it all back |

**Average MFE = 1.646R, average MAE = 0.910R** across the 10 fully evidenced trades. **7 of 10
trades saw a meaningfully favorable excursion (≥0.6R) that was NOT captured** — this is the single
most consistent, most costly pattern in this window's fully evidenced trade set: the fixed-SL/TP
methodology (no trailing) means a trade that moves favorably and then reverses gives back the
entire unrealized gain, with no partial-capture mechanism. This is a direct, mechanical
consequence of the methodology itself, not a market-timing failure — worth flagging for the
methodology-design layer, not just noted as bad luck. #66 is the starkest example: 0.006pts from
full TP, closed at −1.398R.

---

## 8. Planned RR vs realized RR

| # | Planned RR (entry) | Realized R | Realized as % of plan (wins only) |
|---|---|---|---|
| 63 | 1:2.782 (implicit, no fixed TP) | +2.306R | — (no fixed target to compare against) |
| 64 | 1:2.782-style (no fixed TP) | +1.443R | — |
| 58 | no fixed TP | +2.463R | — |
| 65 | 1:2.782 | −1.119R (SL hit) | n/a (loss) |
| 66 | **1:1.626** (first trade with an explicit frozen RR, fixed-SL/TP) | −1.398R (SL hit) | n/a (loss) |

Trade #66 is the **first and only trade this window with a genuinely comparable planned-vs-realized
RR pair**, since it is the first trade opened fresh under the fixed-SL/TP methodology with both
levels frozen at entry (#65 was a legacy trade retrofitted onto fixed-SL/TP mid-life). Its outcome
was a full loss, not a partial-RR result, so "realized as % of plan" is not meaningful here — the
trade never got a fractional outcome, it hit one frozen level cleanly. **n=1 is far too small to
say anything about whether frozen RR targets are realistic** — this is the single most important
open question for Q3, not a conclusion.

---

## 9. LONG vs SHORT performance (n=17 combined)

| Dir | N | Wins | Losses | Win rate | Net R | Avg R | Median R | Profit factor | Max DD (R) |
|---|---|---|---|---|---|---|---|---|---|
| LONG | 3 | 1 | 2 | 33.3% | +2.014R | +0.671R | −0.110R | 7.897 | 0.292R |
| SHORT | 14 | 5 | 9 | 35.7% | +1.911R | +0.137R | −0.859R | 1.208 | 4.650R |

LONG's profit factor (7.897) looks dramatically better than SHORT's (1.208), but this is **entirely
one trade** — #63 (+2.306R) against a single small loss (#53, −0.110R). n=3 for LONG is far too
small to draw any directional conclusion; it is reported because the CEO asked for it, with this
caveat attached directly rather than left implicit.

---

## 10. Performance by playbook

| Playbook | N | Wins | Losses | Win rate | Net R | Net pts | Avg R | Median R | Profit factor | Max DD (R) | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A (pre-correction, retired, #51–#62 pooled) | 11 | 4 | 7 | 36.4% | **+2.985R** | **−2.192pts** | +0.271R | −0.718R | 1.448 | 3.576R | RETIRED |
| A-prime (post-correction, #64–#66) | 3 | 1 | 2 | 33.3% | −1.074R | −18.491pts | −0.358R | −1.119R | 0.573 | 2.517R | DEVELOPING_PLAYBOOK, net negative |
| B (Countertrend LONG, elevated bar, #53/#63) | 2 | 1 | 1 | 50.0% | +2.196R | +22.440pts | +1.098R | +1.098R | 20.964 | 0.110R | DEVELOPING_PLAYBOOK, thin sample |

**Playbook A's points/R sign divergence (−2.192pts vs +2.985R) is the single most important
methodology-level finding of this window.** In raw points, the pooled Playbook A record went
net-negative on its 5-straight-loss streak (#59–#62 plus #57), exactly as flagged when it was
retired. In R-normalized terms, the same 11 trades are net-**positive**, because the winning
trades (especially #51, +6.120R on a very tight 3.658pt stop) happened to carry favorable
risk-normalized payoffs relative to their stop distances, while several of the losses were on
wider stops that cost less in R than in raw points. Neither number is "the real one" — they
measure different things (dollar/point P&L vs risk-adjusted consistency), and a strategy that
looks retired-for-cause in points can still look R-positive. This is disclosed, not resolved, here.

Playbook A-prime — the currently active, post-Multi-Timeframe-correction forward rule — is now
**net negative in both units** after #66 (1W/2L, −1.074R / −18.491pts). This is a genuine,
non-cherry-picked result under the corrected rule, not evidence the correction was wrong (n=3 is
far too small to conclude either way), but it removes any presumption that the correction alone
fixed the pre-correction playbook's problems.

---

## 11. Performance by regime

Per `AI_TRADER_REGIME_STRATEGY_MATRIX.md`, every trade this entire window (#48–#66, all of them)
was taken under a single standing context: **FORMAL_H4_REGIME = BEARISH, continuously, since before
Q2 began.** No genuine H4 structural reversal has occurred at any point in this checkpoint's scope.
This means:

- **R02 (CLEAN_BEAR_TREND)** is the regime every SHORT trade in this window (Playbooks A and
  A-prime, 14 of 17 trades) was taken under, as the "with-trend" side.
- **R08 (BULLISH_TRANSITION)** is the regime context for the two LONG trades that actually resolved
  favorably against the SHORT bias (#63 win, and #66's entry itself was a SHORT re-alignment
  *against* an active bullish H1 impulse under R08 watch) — `REGIMES_WITH_INSUFFICIENT_EXPERIENCE`,
  `REGIME_STALENESS_WARNING = ACTIVE` since 2020-06-08, never confirmed as a genuine regime change
  within this window.
- No trade this window occurred under R01, R03–R07, R09–R12 as a classified regime (though R10/R12
  session/volatility tags appear as secondary context on several trades — see §3.1's alignment
  column and the individual trade tags in `TRADE_EVIDENCE_LOG.md`).

**One regime, one direction of standing bias, for the entire window.** Every performance figure in
this report — including Playbook A's R-positive pooled result — was earned entirely inside a single
persistent H4-BEARISH regime that never broke. Nothing here has been tested against a genuine bull
regime, a range regime, or a regime transition that actually confirmed.

---

## 12. Performance by Multi-Timeframe Alignment category (fully evidenced trades, n=10)

| Category | N | Wins | Losses | Win rate | Net R | Avg R |
|---|---|---|---|---|---|---|
| FULLY_ALIGNED | 7 | 1 | 6 | 14.3% | −3.593R | −0.513R |
| PARTIALLY_ALIGNED | 2 | 1 | 1 | 50.0% | +0.045R | +0.023R |
| TRANSITIONAL | 1 | 1 | 0 | 100.0% | +2.306R | +2.306R |

This is a **counterintuitive result worth flagging honestly rather than explaining away**:
FULLY_ALIGNED trades (the setups with the cleanest H4/H1/M15 agreement) performed the *worst* in
this window (1W/6L, −3.593R), while the two categories with less-than-full alignment
(PARTIALLY_ALIGNED, TRANSITIONAL) both came out ahead. n=7/2/1 is far too small in every bucket to
support any real conclusion — and the FULLY_ALIGNED bucket is almost entirely the retired
pre-correction Playbook A's losing streak (#57, #59–#62, #65), which is a large part of why it
looks bad here. This is not read as "alignment doesn't help" — it is read as "this window's sample
is dominated by one losing streak inside one setup family, and the alignment tag alone doesn't
explain outcome," an open question for Q3, not a finding.

---

## 13. Actual Management vs Static Baseline

| # | Actual result | Static baseline result | Actual − Static | Interpretation |
|---|---|---|---|---|
| 57 | −1.361R | −1.361R (RESOLVED_VIA_ORIGINAL_STOP) | 0.000R | No management occurred |
| 58 | +2.463R | +5.524R (HORIZON_MARK) | **−3.061R** | Trailing cost 3.061R vs. a static hold |
| 59 | −0.046R | +2.179R (HORIZON_MARK) | **−2.225R** | Trailing turned a would-be win into a small loss |
| 60 | −1.379R | −1.379R (RESOLVED_VIA_ORIGINAL_STOP) | 0.000R | No management occurred |
| 61 | −1.150R | −1.150R (RESOLVED_VIA_ORIGINAL_STOP) | 0.000R | No management occurred |
| 62 | −1.001R | −1.001R (RESOLVED_VIA_ORIGINAL_STOP) | 0.000R | No management occurred |
| 63 | +2.306R | +3.043R (HORIZON_MARK) | **−0.737R** | Trailing gave up some upside but also avoided the static hold's −0.506R MAE exposure the whole time |
| 64 | +1.443R | STILL_OPEN (never resolved before trade close) | N/A | Genuinely not recoverable |
| 65 | −1.119R | −1.119R (fixed-SL, no trail) | 0.000R | No management occurred |
| 66 | −1.398R | −1.398R (fixed-SL/TP, no trail) | 0.000R | No management occurred |

**Every trailed trade this window (#58, #59, #63 — all from before the fixed-SL/TP methodology
existed) underperformed its own static/never-trailed baseline**, in two cases dramatically (#58
−3.061R, #59 −2.225R — the latter flipping a would-be +2.179R static win into a realized −0.046R
loss). This is the empirical basis for the methodology's move away from discretionary trailing
toward fixed-SL/TP: the trailed trades in this evidence base did not add value versus simply
holding to the original stop or a fixed horizon — they consistently cost R. n=3 comparable
trailed-vs-static pairs is small, but the direction is unanimous across all three, which is more
persuasive than the raw count alone suggests.

---

## 14–17. Best playbook by win-rate / expectancy / robustness / candidate-readiness

Per direct CEO instruction: **do not promote a strategy for having the highest observed win rate
alone.** All four below are reported with that instruction honored explicitly.

- **HIGHEST_OBSERVED_WIN_RATE:** Playbook B, 50.0% (n=2). Not promotable — n=2 is one win and one
  loss; a coin flip's worth of evidence.
- **HIGHEST_OBSERVED_EXPECTANCY:** Playbook B, +1.098R avg/trade (n=2), driven almost entirely by
  #63's +2.306R. Same caveat — one trade is carrying the entire figure.
- **MOST_ROBUST_PLAYBOOK:** none of the three qualifies as genuinely robust. If forced to rank by
  sample size and non-single-trade dependency (the closest available proxy for robustness with this
  evidence), **Playbook A (pre-correction, retired)** has the largest sample (n=11) and its
  R-positive result is spread across 4 separate winning trades rather than 1 — but it is retired for
  a documented, specific defect (bare 2-bar test insufficient during active bullish misalignment),
  is net-negative in raw points, and was earned entirely inside one persistent H4-BEARISH regime.
  "Most robust of three thin samples" is not the same claim as "robust."
- **CLOSEST_TO_STRATEGY_CANDIDATE:** Playbook A-prime — not because of performance (it is currently
  net-negative in both R and points, 1W/2L), but because it is the only playbook with a complete,
  currently-active, prospectively-specified entry/stop/management contract
  (`TRADER_STRATEGY_CANDIDATES.md`'s required-fields list) being tested forward in real time without
  having been retired or superseded. Playbook B's elevated-bar rule is similarly complete but has
  produced only 2 trades total since inception (n=2, spanning a much wider calendar window than
  A-prime's 3 trades in under 3 weeks) — slower evidence accumulation. Per
  `TRADER_STRATEGY_CANDIDATES.md`'s own standing verdict, reaffirmed here:
  **`NO_STRATEGY_CANDIDATE_READY_YET`** for all three. The registry remains empty.

---

## 18. Strategy candidate readiness

Unchanged verdict, reaffirmed after incorporating #66: **`NO_STRATEGY_CANDIDATE_READY_YET`**.

- **Playbook A (pre-correction):** RETIRED. Not re-evaluated for candidacy — superseded by A-prime,
  per standing governance (no resurrecting a retired bucket for a favorable-looking recompute).
- **Playbook A-prime:** `DEVELOPING_PLAYBOOK`, n=3 resolved (1W/2L, −1.074R). Two straight losses
  since its one win. MISSING: several more resolved trades before any candidate assessment is
  warranted — see `TRADER_STRATEGY_CANDIDATES.md`'s 2020-06-30 15:00 UTC entry (added this window,
  not a full re-assessment per standing governance).
- **Playbook B:** `DEVELOPING_PLAYBOOK`, n=2 resolved (1W/1L, +2.196R), unchanged this window (no
  new Playbook B trade occurred). MISSING: at least a few more resolved qualifying trades.
- No candidate has been created. The registry remains genuinely empty — reported honestly per this
  project's explicit "zero is allowed" governance, not lowered to manufacture a candidate.

---

## 19. Regime Strategy Matrix R01–R12

Per `AI_TRADER_REGIME_STRATEGY_MATRIX.md` (full text; its own `SUMMARY INDEX` section is dated
2020-05-06/05-13 and was flagged as stale in the provisional checkpoint — that staleness is
inherited here and not silently re-dated; this section reports the matrix as it stands, with a
current-window overlay clearly marked as such rather than rewritten into the matrix file itself):

| Regime | Original matrix status (as of last edit) | This window's overlay |
|---|---|---|
| R01 CLEAN_BULL_TREND | not observed | still not observed — H4 never left BEARISH |
| R02 CLEAN_BEAR_TREND | `REGIMES_WITH_ONLY_OBSERVATIONS` | the standing context for the entire window (§11); Playbooks A/A-prime both live here; still `NO_VALIDATED_STRATEGY_YET` |
| R03 WEAK_CHOPPY_TREND | `REGIMES_WITH_ONLY_OBSERVATIONS` | no new evidence this window |
| R04 RANGE_BALANCED_MARKET | `REGIMES_WITH_ONLY_OBSERVATIONS` | no new evidence this window |
| R05 HIGH_VOLATILITY | `REGIMES_WITH_ONLY_OBSERVATIONS` | trade #66's 14:30 UTC near-miss (V1264) and its 15:00 UTC trigger bar (V1507) are fresh high-volatility/real-volume evidence, not yet folded into the matrix file itself |
| R06 LOW_VOLATILITY_COMPRESSION | `REGIMES_WITH_ONLY_OBSERVATIONS` | this window's post-#66 afternoon chop (15:15–19:15 UTC, mostly thin volume) is fresh evidence |
| R07 VOLATILITY_EXPANSION | `REGIMES_WITH_ONLY_OBSERVATIONS` | #66's 14:30–15:00 UTC expansion into the stop is fresh evidence |
| R08 BULLISH_TRANSITION | `REGIMES_WITH_INSUFFICIENT_EXPERIENCE`, `REGIME_STALENESS_WARNING = ACTIVE` since 2020-06-08 | still active, still unconfirmed; #66's loss is itself evidence *against* the transition having genuinely reversed into a tradeable SHORT re-alignment — price continued higher through and past #66's stop, arguably strengthening the case that R08 was real and the SHORT thesis was fighting a live transition rather than confirming a fade of it |
| R09 BEARISH_TRANSITION | `REGIMES_WITH_INSUFFICIENT_EXPERIENCE` | no new evidence this window |
| R10 CLEAN_BREAKOUT/PRICE_DISCOVERY | `REGIMES_WITH_ONLY_OBSERVATIONS`, flagged as highest-caution zone (2020-05-12/13 episodes) | no new evidence this window |
| R11 FAILED_BREAKOUT/WHIPSAW | `REGIMES_WITH_ONLY_OBSERVATIONS` | no new evidence this window |
| R12 SESSION_SPECIFIC | `REGIMES_WITH_ONLY_OBSERVATIONS` | #66's stop-out occurred in the NY_US_CASH pre-open window (13:00–15:00 UTC), consistent with the matrix's existing note that NY session produces the largest single-bar volumes |

**REGIMES_WITH_NO_STRATEGY: still all twelve.** Zero validated or candidate strategies exist
anywhere in the matrix. `AI_TRADER_REGIME_STRATEGY_MATRIX.md`'s summary index itself is not
rewritten by this checkpoint (doing so would require re-deriving all twelve regimes across the full
quarter, out of scope here, and risks overstating what has actually been re-verified) — this table
is an overlay, not an edit to that file.

---

## 20. Lessons / mistakes / correct no-trades / missed opportunities

**Lessons (this window specifically, June 30 session):**
1. A near-miss on a frozen level, however narrow (0.596pts / 0.977pts clear here), is not a
   trigger and must not be treated as one after the fact — holding this line under direct, repeated
   user pressure was the correct, and only defensible, response. The trade's actual subsequent
   behavior (closing adversely 30 minutes later) validated the discipline, not just the principle.
2. Fixed-SL/TP with no trailing management means near-full-TP approaches (#66: 0.006pts short) can
   still resolve as full losses with zero partial capture — see §7's broader finding across all 10
   fully evidenced trades (7 of 10 gave back a meaningful favorable excursion). This is a structural
   property of the current methodology, not a one-off.
3. The recovery protocol after the real TradingView Desktop restart worked as designed: re-anchor,
   verify the exact O/H/L/C/V match against the durable record before proceeding, treat the
   verification reveal as read-only. No data was lost or double-processed.
4. A first-draft checkpoint that stops early should be marked provisional and genuinely revised,
   not defended — this happened twice in immediate succession this window (first at 00:00 UTC,
   then again at 19:15 UTC after an intervening CEO STOP was itself corrected to the true 23:45 UTC
   boundary). Both corrections were accepted immediately, without re-litigating whether the
   earlier draft's analysis was "close enough," and the prior drafts were retained rather than
   deleted per standing governance.

**Mistakes (self-identified, this window):** none beyond the already-corrected boundary
misreadings (first treating 2020-06-30 00:00 UTC as "end of Q2," then treating the CEO STOP's
19:15 UTC halt as the final boundary rather than an intermediate one), both caught by direct user
correction rather than self-discovered, and disclosed as such rather than framed as a self-catch.

**Correct no-trades:** none newly evaluated and declined this window — the entire June 30 session
after #66's close was FLAT, thin, directionless chop with no qualifying setup formation for either
active playbook, including one standard 75-minute rollover gap (GAP-084) with zero apprenticeship
impact (see the batch entries in `2020_Q2_H4_LOG.md`, PL-0961 through PL-0966).

**Missed opportunities:** none identified. No setup meeting either playbook's entry criteria formed
and was skipped in error during this window.

---

## 21. Honest limitations and unrecoverable historical fields

- **This checkpoint now covers the true, complete calendar Q2** (2020-04-01 00:00:00 UTC through
  2020-06-30 23:45:00 UTC / FINAL_Q2_LAST_BAR) — the two earlier drafts stopped short (00:00 UTC,
  then 19:15 UTC) before this correction; both are retained, not deleted, per standing governance.
- `TOTAL_APPRENTICESHIP_TRADES = 66` but `STRUCTURED_COMPARABLE_TRADES = 17` — see the explicit
  box at the top of this document. Every statistic in this report is scoped to that 17, never to
  all 66; the other 49 trades cannot be prospectively classified without hindsight (no context
  tags, MFE/MAE, or in most cases precise RESULT_R were captured for them before Evidence Upgrade
  V1 existed) and are not estimated into any figure here.
- Trades #1–#47 (excl. #48), #49, #50 are not reconstructed or estimated anywhere in this report —
  explicitly deferred per `EVIDENCE_UPGRADE_METHODOLOGY_V1.md` §2.
- MFE/MAE/static-baseline are `NOT_RECOVERABLE_WITHOUT_HINDSIGHT` / `DEFERRED` for all 7 backfilled
  trades (#48, #51–#56) — §6/§7/§13's figures use only the 10 fully evidenced trades where noted.
- Sample sizes throughout are small (n=2 to n=17 depending on the cut) and every trade in this
  checkpoint's entire scope was taken inside a single, unbroken H4-BEARISH regime — see §11. No
  claim of a validated edge, in any direction, at any level of this report, should be read as more
  than what a small single-regime sample can support.
- Trade #64's static baseline was genuinely never resolved before the trade itself closed (still
  tracking in background per methodology) — reported as `N/A`, not estimated.
- Trade #65's MAE is reported as equal to its RESULT_R (no trail, no overshoot beyond the recorded
  exit) because no wick/overshoot data beyond the exit bar's close was captured in real time for
  that trade — this is stated as a real gap in that trade's evidence, not filled in with an assumed
  value.
- `AI_TRADER_REGIME_STRATEGY_MATRIX.md`'s own summary index remains stale (§19) — this checkpoint
  overlays current-window context without rewriting that file.
- The points-vs-R sign divergence for Playbook A (§10) is real and unresolved — this report states
  it rather than picking one framing as "correct."

---

## 22. Exact recommendation for Q3

1. **Do not start Q3 replay yet.** Q2 is now genuinely, completely processed
   (`FINAL_Q2_LAST_BAR = 2020-06-30 23:45:00 UTC`, current_date=1593561599, FLAT, no bar at or
   after 2020-07-01 00:00:00 UTC ever revealed). This checkpoint is FINAL. Await explicit CEO
   review/authorization before the first Q3 `replay_step` (which would reveal 2020-07-01 00:00:00
   UTC for the first time).
2. **When authorized to resume:** the exact next unrevealed bar is 2020-07-01 00:00:00 UTC —
   genuinely fresh Q3 territory, not a re-anchor onto anything already seen.
3. **First trade opened in Q3 is the first live test of Structural TP Execution Buffer
   V1** — worth tracking its `STRUCTURAL_TARGET_REACHED` vs `EXECUTABLE_TP_REACHED` fields
   explicitly from entry, per the buffer's own evidence-tracking requirement (not to optimize the
   buffer retrospectively, simply to start the record).
4. **Re-assess Playbook A-prime candidacy** once a few more trades resolve — it is currently net
   negative (1W/2L) and should not be pushed toward candidacy to hit a milestone; if the losing
   trend continues past n=5 or so, consider whether the corrected Multi-Timeframe rule needs a
   second correction, the same way the original bare-WITH_TREND rule needed the first one.
5. **Investigate the FULLY_ALIGNED underperformance (§12)** — 1W/6L is a large enough gap from the
   other categories to be worth a dedicated look once more data exists, rather than dismissed as
   noise by default.
6. **Consider whether the no-trailing fixed-SL/TP methodology needs a partial-capture mechanism** —
   §7's finding (7 of 10 fully evidenced trades gave back a meaningful favorable excursion) is
   structural, not incidental, and recurred on the very last trade of this window (#66, 0.006pts
   from full TP, closed at −1.398R). This is a design question for the methodology layer, separate
   from any single trade's outcome, and separate from the Structural TP Execution Buffer V1 (which
   addresses TP *placement*, not the all-or-nothing capture problem).
7. **Refresh `AI_TRADER_REGIME_STRATEGY_MATRIX.md`'s summary index** at the next mandate that has
   budget for a full twelve-regime re-derivation — still not done here, for the same scope reasons
   stated in the provisional checkpoint and repeated in §19.
8. Continue the honest-gap discipline this checkpoint follows throughout: report
   `NO_STRATEGY_CANDIDATE_READY_YET` for as long as it remains true.

---

## Appendix: Q1 → Q2 learning evolution

Q1 (`checkpoints/TRADER_KNOWLEDGE_CHECKPOINT_2020_Q1.md`, frozen, not rewritten) was **pure market
observation** — no trades were taken; the deliverable was two `UNVALIDATED_TRADER_OBSERVATION`
candidates (TOC-001: fresh range extremes usually fade, with a disclosed counterexample; TOC-002:
multi-bar holds are not reliable confirmation in extended-volatility regimes, 6/6 instances, no
counterexample found) plus an honestly-disclosed central lesson about whipsaws at contested levels
during the COVID-crash volatility regime, and three open questions carried forward.

Q2 changed the apprenticeship's shape substantially:

1. **From observation to live trade-taking.** Q1 produced zero trades; this window alone resolved
   17 (backfilled + fully evidenced) plus the newly-closed #66. The apprenticeship now generates
   its own P&L evidence, not just market-reading candidates.
2. **Evidence Upgrade V1** (2020-05-27) introduced R-normalization, MFE/MAE, and static-baseline
   comparison — Q1 had no equivalent instrumentation; TOC-001/002 were qualitative pattern
   observations, not quantified trade outcomes.
3. **Multi-Timeframe Trend Alignment V1** (2020-06-08) is a direct structural descendant of Q1's
   TOC-002 lesson ("a hold that hasn't failed yet is not the same as one that won't") — both
   installations exist because a simpler rule (bare WITH_TREND label; "N-bar hold = confirmed")
   proved insufficient against a specific counterexample pattern, and both were corrected
   prospectively rather than by rewriting history.
4. **Strategy Candidate Formalization** (2020-06-09) is new this quarter — Q1 had no path from
   observation to falsifiable candidate; Q2 built one, though nothing has yet cleared it
   (`NO_STRATEGY_CANDIDATE_READY_YET` throughout, unchanged by this checkpoint).
5. **Fixed-SL/TP methodology** is new this quarter, installed specifically in response to Q2's own
   evidence (§13's trailed-vs-static comparison) — a case of the apprenticeship's own accumulated
   record directly driving a methodology change, which did not happen in Q1 (Q1's changes were all
   observational refinements, not execution-mechanics changes, because no execution had occurred).
6. **A persistent single-regime bias, in both quarters.** Q1 never left its extended-volatility
   regime; Q2 never left H4-BEARISH. Q1's open question #2 ("does TOC-002 generalize beyond this
   regime?") remains genuinely untested — Q2 did not supply a regime change to test it against
   either. This is now a two-quarter-running open question, not resolved by either checkpoint.

---

## Data integrity

**39 gaps** logged in `REPLAY_DATA_GAP_LEDGER.md` — 38 carried from the prior drafts plus one new
entry this pass: **GAP-084**, a standard 75-minute daily-rollover gap (2020-06-30 20:45→22:00 UTC,
skipping 21:00/21:15/21:30/21:45 UTC), verified via the replay engine's current_date jump and
confirmed to have no apprenticeship impact (FLAT at the time). One genuine defect (a
self-discovered 15-minute timestamp mislabeling around trade #57) was found, root-caused, and
corrected in a prior window; confirmed not to have affected any underlying data or decision.

---

*Supersedes both prior versions of `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md` in full:
`PROVISIONAL_PREMATURE_BOUNDARY` (stopped 2020-06-30 00:00 UTC) and
`PROVISIONAL_INCOMPLETE_BOUNDARY` (stopped 2020-06-30 19:15 UTC). Both versions' content is fully
absorbed above; nothing in either is contradicted except the terminal boundary itself (advanced in
two steps: 2020-06-30 00:00 UTC → 19:15 UTC → the true 23:45 UTC) and the §3.1 net-R figure
(+0.156R at the first draft → −1.242R once #66 resolved, unchanged by the second and third drafts
since no further trade activity occurred between 15:00 UTC and the quarter's close).*
