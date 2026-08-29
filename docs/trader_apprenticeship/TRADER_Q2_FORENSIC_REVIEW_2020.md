# TRADER Q2 2020 FORENSIC REVIEW

Prepared under direct CEO mandate, real-time, following `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md`
(`STATUS: FINAL`). Objective: a complete, evidence-grounded account of what the AI Trader actually
experienced and learned during Q2 — not only P&L. Built from the durable apprenticeship record
through the end of Q2: `TRADE_EVIDENCE_LOG.md`, `STRATEGY_EVIDENCE_DENOMINATOR.md`,
`TRADER_STRATEGY_CANDIDATES.md`, `AI_TRADER_REGIME_STRATEGY_MATRIX.md`,
`AI_TRADER_MARKET_READING_LIBRARY_V1.md`, `AI_TRADER_EXPERIENCE_LEDGER.md`,
`AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md`, `REGIME_TRANSITION_WATCH.md`,
`EVIDENCE_GRADE_CLASSIFICATION.md`, `EVIDENCE_UPGRADE_METHODOLOGY_V1.md`, `Q2_TRADE_PLAN_CONTRACT.md`,
`2020_Q2_H4_LOG.md`, and `checkpoints/TRADER_KNOWLEDGE_CHECKPOINT_2020_Q1.md`.

**No Q3 outcome informs this report.** Four Q3 bars (2020-07-01 00:00–01:00 UTC) were causally read
before this mandate arrived, FLAT throughout, zero trades taken — retained, not erased, but never
used below to revise any Q2 conclusion (per §22 governance).

**Evidence-tier discipline used throughout:** every claim below is tagged, explicitly or by
section-level note, as `RECORDED FACT` (directly in a governance file), `SUPPORTED INFERENCE`
(a reasonable reading of recorded facts, not itself directly written down), or
`NOT_RECOVERABLE_WITHOUT_HINDSIGHT` / `NOT_RECOVERABLE_WITHIN_THIS_REVIEW'S_RESEARCH_BUDGET`. Q2
trade *outcomes* are never used to relabel entry-time reasoning; where a source document itself
performed such an audit (e.g. the Multi-Timeframe Alignment tagging of trades #58–62), that is
reported as what it is — a forward-methodology annotation on frozen entry-time tags, not a
result-informed relabeling.

A critical scope finding surfaced during this review's research, stated once here and referenced
throughout rather than repeated per-section: **the canonical top-level `2020_Q2_H4_LOG.md` begins
mid-trade, already inside Trade #59's management** — it contains no entry-level narrative for
trades #48 or #51–58. Their `RESULT_R`/`RESULT_PTS` are securely recorded in `TRADE_EVIDENCE_LOG.md`
(the official structured backfill), but the *reasoning* behind them is not in the canonical files.
A separate `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md` does carry narrative for trades #47–#53 and
beyond, but its per-trade RESULT figures for #47/#49/#50 were **never promoted** into
`TRADE_EVIDENCE_LOG.md`'s official structured set — a real, previously undocumented gap, reported
honestly in §20 rather than papered over by treating those figures as equally authoritative.

---

## 1. Q2 executive summary

```
Q2_TOTAL_TRADES               = 66
Q2_STRUCTURED_COMPARABLE_TRADES = 17   (#48, #51-#56 backfilled + #57-#66 fully evidenced)
```

| Metric | Combined (n=17) | Fully evidenced only (n=10, #57-#66) |
|---|---|---|
| WINS | 6 | 3 |
| LOSSES | 11 | 7 |
| BREAKEVEN | 0 | 0 |
| WIN_RATE | 35.3% | 30.0% |
| NET_R | +3.925R | −1.242R |
| NET_PIPS (points) | +0.341pts | −69.65pts |
| AVG_R_PER_TRADE | +0.231R | −0.124R |
| MEDIAN_R | −0.182R | −1.079R |
| PROFIT_FACTOR | 1.414 | 0.630 |
| MAX_DRAWDOWN (sequential, R) | 3.576R | 3.576R |

*(NET_PIPS for the fully-evidenced set is the same figure as NET_R's underlying points sum,
converted at 10 pips/point per the new Q3 pip standard — Q2 itself was reported in raw points, not
retroactively rebranded; see `AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1.md` §4 for why this conversion
is display-only here.)*

- **LONG vs SHORT (n=17):** LONG 3 trades, 1W/2L, +2.014R, profit factor 7.897 (one trade, #63,
  responsible for nearly the entire figure — n=3 far too small to read as a directional edge).
  SHORT 14 trades, 5W/9L, +1.911R, profit factor 1.208.
- **Best period:** the #63/#64 stretch (2020-06-08 to 06-15) — first-ever qualifying countertrend
  LONG win under an elevated evidence bar, immediately followed by the first WITH-trend SHORT to
  pass the corrected Multi-Timeframe rule. Two structurally different playbooks both validated
  their *newest, most-scrutinized* version in immediate succession.
- **Worst period:** the #59–#62 stretch (2020-06-03 to 06-08), four losses in five trading days,
  the stretch that pushed the pooled Playbook A pool into points-negative territory and directly
  triggered the Multi-Timeframe Trend Alignment V1 correction and the `REGIME_STALENESS_WARNING`.
- **Best observed playbook (by the numbers, heavily caveated):** Playbook B (Countertrend LONG,
  elevated bar) — 50% win rate, +1.098R avg/trade, n=2. See §12 — not promotable from this alone.
- **Worst observed playbook:** Playbook A-prime (post-correction WITH-trend SHORT) — 1W/2L,
  −1.074R net, n=3 — the playbook installed specifically to *fix* Playbook A's problems, currently
  net negative in both R and points.
- **Best observed regime:** N/A in the comparative sense — Q2 occurred entirely inside one
  unbroken H4-BEARISH regime (`RECORDED FACT`, `AI_TRADER_REGIME_STRATEGY_MATRIX.md` /
  `2020_Q2_H4_LOG.md`, never once broken across all 66 trades). There is no second regime to
  compare it against.
- **Worst observed regime:** same reasoning — only one regime existed. The closest analog is the
  *sub-regime* stress-test: the extreme multi-bar whipsaw episodes (five/four-bar
  alternating-massive-volume stretches before trades #62 and various Playbook B declines) were the
  most difficult market texture encountered, and discipline held (correctly declined) every time.
- **Most important thing learned in Q2 (SUPPORTED INFERENCE, synthesizing §5/§10/§14):** a trade's
  entry-time context tag (FULLY_ALIGNED, WITH_TREND) is not a durable property — it can go stale
  mid-trade as a higher timeframe's real-time behavior diverges from its last formal label, and the
  apprenticeship's own worst stretch (#59–62) happened almost entirely under tags that were
  technically correct at entry but arguably already going stale by the time of resolution.
- **Largest remaining weakness (SUPPORTED INFERENCE):** the fixed-SL/TP methodology's total absence
  of a partial-capture mechanism — 7 of the 10 fully evidenced trades gave back a meaningful
  favorable excursion (≥0.6R) with zero capture, most starkly Trade #66 (0.006pts from full TP,
  closed a full loss). This is the direct evidentiary basis for the newly-installed Multi-Target
  System V1 (§11), though that system itself carries zero Q2 trades yet.

---

## 2. What the trader was actually watching

Source: `AI_TRADER_MARKET_READING_LIBRARY_V1.md` (14 modules, M01–M14), cross-checked against
which modules actually appear cited by name in `2020_Q1_H4_LOG.md`/`2020_Q2_H4_LOG.md`. The
library itself states it is "read-only, forward-only" reference vocabulary, not a decision engine,
and explicitly instructs **against** mechanically evaluating every module on every bar — a module
is consulted only when something material develops (compression appearing, a prior high/low being
attacked, a break occurring, a character change, price stalling repeatedly at one level). This
attention-based discipline is itself a documented, deliberate practice, not a gap.

| Module | What it looks for | Why it matters | When it helped | When it failed | Confidence |
|---|---|---|---|---|---|
| **M01 Trend** | Sustained HH/HL or LL/LH sequences, shallow pullbacks, non-collapsing volume on new legs | Establishes whether a directional bias genuinely exists vs. is assumed | Correctly identified the Feb19+ Q1 uptrend, the apprenticeship's clearest trend episode | Never claimed predictive of continuation ("every trend ends, usually without warning") — self-limiting by design | Moderate — real, RUNTIME-BACKED, but explicitly not a guarantee |
| **M02 Pullback** | Shallower counter-move than the preceding impulse, stalling near a prior structural point | Distinguishes a healthy retracement from a trend failure | **No confirmed on-topic example found in the walk log** — the log's own vocabulary leans on "reclaim"/"consolidation" instead | N/A — essentially unused vocabulary in practice | Low — conceptually defined, not yet operationally applied |
| **M03 Breakout** | Close beyond a boundary + follow-through + volume/range expansion | Core mechanism behind every WITH-trend entry taken this quarter | Correctly framed trades #57–#66's entry logic (2 consecutive real-volume closes beyond a level) | TOC-001 (Q1) is literally this module's failure mode, formally tracked | High for the mechanism; explicitly caveated that a single closing bar is never proof |
| **M04 Range** | Multiple tests of stable upper/lower boundaries without a durable break | Frames when NOT to expect trend-style continuation | Q1's Jan–Feb 1517–1593 range (TOC-001's home regime) | The ~1625 floor (Q1) held 3 tests then broke on the 4th — explicit lesson: holding N times ≠ N+1th holds | Moderate |
| **M05 Liquidity** | Prior highs/lows, equal highs/lows, sweeps, failed sweeps, reclaims | Frames where a stop-run or reversal is structurally likely | The ~1625 floor's three defended tests (Q1) | Explicitly "an observational pattern, not a verified mechanism — no live detector exists" | Low-moderate — pure observation, unconfirmed by any live tool |
| **M06 Volatility** | Compression (narrowing range) vs. expansion (sudden wide range/volume) | Frames when a resolution is more likely, not which way | RUNTIME-BACKED — genuinely gates `ve_brain`'s live regime routing; correctly flagged multiple record-volume episodes | Never claims direction — "compression → up" is explicitly disclaimed | High for the mechanism, by design silent on direction |
| **M07 Session** | Named UTC windows (Asia/London/NY) with characteristic participation | Frames *how much* can be expected to develop, not which way | SF-3 (a frozen, bounded information asset) correctly used twice in Q1 to interpret session-level quiet, never as a signal | N/A — used correctly within its stated scope both times | Moderate — RUNTIME-BACKED, correctly bounded to context-only use |
| **M08 Auction** | Value area / point-of-control (where trading concentrated, not just where price reversed) | Deeper read of order-flow acceptance | **Zero implementation, zero example in the walk log** — no volume-profile data exists in this codebase | N/A | None — `CONCEPTUAL_OBSERVATION_ONLY`, honestly stated as unusable here |
| **M09 Cross-scale** | Whether H4/H1/M15 structural pictures agree, conflict, or don't yet resolve | The connective tissue for nearly every trade's entry reasoning | The apprenticeship's own manual H4→H1→M15 hierarchy is a genuine, working practice of this module | The entire #59–62 stretch is arguably a cross-scale-conflict episode that wasn't formally flagged as such until the 2020-06-08 audit | High for the manual practice; the automated tower version is explicitly unverified |
| **M10 Transition** | Trend↔range, compression↔expansion, one trend flipping to its opposite | Signals "the rules that applied a moment ago may no longer apply" | Correctly framed the Feb19-top→crash episode (Q1) | The whole R08 BULLISH_TRANSITION watch (Q2) is a live, still-unresolved test of this module — "forming" for the entire quarter, never reaching "confirmed" | Moderate — real regime axis, but genuinely hard to call in real time |
| **M11 Hazard** | External-shock caution lens (news, forced liquidation, thin-liquidity gaps) vs. organic structure | Prevents treating a shock-driven move as a repeatable structural signal | Correctly distinguished the 2020-02-28 COVID liquidation crash from ordinary probe-and-reject | Zero implementation anywhere company-wide; "recognized only in hindsight, by hand" both times it mattered | Low — conceptually sound, structurally unsupported |
| **M12 Event Sequence** | Reading a stretch as a connected chain of events, not isolated bars | Frames a whole episode (buildup→resolution→aftermath) for review | The Feb19-top-to-crash episode is explicitly treated this way, informing the Q1 checkpoint | Zero implementation; inherently retrospective-review only | Low-moderate — useful for review, not real-time decisions |
| **M13 FVG** | Three-candle imbalance from a displacement move | Zone of fast, imbalanced order flow | RUNTIME-BACKED live detector exists (real MT5 ticks) — but **never once reaches the apprenticeship's own reasoning**, "by explicit CEO instruction, records only, never evaluates" | N/A — no walk entry references an FVG by name | None observed — capability real, never surfaced |
| **M14 Order Block** | Last opposing candle before a genuine displacement | Zone where the order flow fueling a move may have originated | Same status as M13 — live detector, never surfaced to the apprenticeship | N/A — no walk entry references an order block by name | None observed — capability real, never surfaced |

**Three bounded information assets** (VOLTIME-1, DXY-NDX1, SF-3) exist as read-only context —
explicitly, in the library's own words, "NONE of these three may determine LONG/SHORT direction."
SF-3 is the only one actually cited in the walk log, both times correctly (context, not signal).
VOLTIME-1 and DXY-NDX1 have never been cited by name in the apprenticeship as of the last coverage
audit (2026-08-25, real-time).

**Concepts on the CEO's list without a dedicated module** (`RECORDED FACT`, confirmed by direct
search of the library): support/resistance, swing structure, failed breakouts, reclaims,
acceptance/rejection, regime identification, momentum/lack-of-progress each exist only as
*vocabulary threaded through* other modules (M03/M04/M05/M09/M10/M01), not as standalone entries —
reported honestly rather than inventing standalone confidence levels for concepts the library
itself doesn't isolate.

---

## 3. Complete recurring observation inventory

Genuinely complete extraction of every discretely-tracked recurring observation found across
`AI_TRADER_EXPERIENCE_LEDGER.md` and `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md`. Q1-origin items
noted as such; all remained active/referenced into Q2.

### TOC-001 — "a fresh multi-week range extreme gets rejected within 1-2 bars" *(Q1-origin, carried forward)*
- FIRST_SEEN 2020-01-03 / LAST_SEEN 2020-02-19 (confirming instances) — SUPPORTING_OCCURRENCES 4
  (Jan3, Jan8, Feb3, Feb19) — COUNTEREXAMPLES 1 confirmed (Feb19 breakout held 44+ consecutive M15
  bars). REGIME: R04 range-bound (1517–1593). CONFIRMATION grade note (`EVIDENCE_GRADE_CLASSIFICATION.md`):
  3 of 4 confirmations are lower-rigor EARLY_PILOT grade; the 1 STRICT_M15_APPRENTICESHIP confirmation
  and the 1 counterexample fall on the *same day* — under primary evidence grade the record is
  effectively 1-vs-1, materially weaker than the raw 4-vs-1 count implies. STATUS: `UNVALIDATED_TRADER_OBSERVATION`,
  scope flagged too narrow, never resolved within Q1/Q2.

### TOC-002 — "a multi-bar M15 hold does not reliably predict a durable move, in this extended-volatility regime" *(Q1-origin, carried forward, active in early Q2)*
- SUPPORTING_OCCURRENCES: 7 STRICT_M15_APPRENTICESHIP-grade instances by Q1 close (2020-03-10
  through 04-01), growing to "8th reinforcing instance" by early Q2 (per
  `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md` PL-0001/PL-0002). COUNTEREXAMPLES: 0 found at any
  point. **Notable self-discipline**: at PL-0024 (2020-04-02) a 3-instance cluster within one
  continuous leg was explicitly declined as reinforcement, "per TOC-002's own precedent, this needs
  to be observed OUTSIDE a single continuous leg before it means anything structurally" — same-leg
  repeats don't count as independent confirmation. WHAT_INVALIDATES: a hold that genuinely sticks
  — never observed in either quarter. STATUS: `UNVALIDATED_TRADER_OBSERVATION`, methodologically
  the strongest-grade candidate in the file (100% STRICT_M15_APPRENTICESHIP evidence).

### TOC-003 — "after a heavily-defended level finally breaks, the first 1-2 bars (immediate continuation vs. stall) predict the outcome" *(Q2-origin)*
- FIRST_SEEN 2020-04-22 (trade #37 zone) / LAST_SEEN 2020-05-12. SUPPORTING_OCCURRENCES: 6 at the
  point of last explicit count (2W/4L split — stall signature preceded losses, immediate
  continuation preceded wins). COUNTEREXAMPLES: one "role-reversal instance" (tagged R02, not
  TOC-003 itself) logged honestly as a disclosed complication, matrix update flagged pending. WHY:
  not stated beyond the descriptive pattern — `NOT_RECOVERABLE_WITHOUT_HINDSIGHT` for deeper
  mechanism. STATUS: actively monitored, definition being refined, never formally promoted or
  rejected within available files.

### TRADER_LESSON_021 / "1685.883-class heavily-defended-level breaks" *(Q2-origin — likely the same underlying phenomenon as TOC-003, tracked under a separate label)*
- Explicit instance-by-instance tally in the source: trade #28 LOSS (1st) → #30 LOSS (2nd) → #32
  WIN (3rd, "first to work," 1W/2L) → #33-area LOSS (4th, 1W/3L) → #35-area LOSS (5th, 1W/4L) → #36
  WIN (6th, confirms the stall-vs-continuation distinguishing feature, final tally **2W/4L**).
  WHAT_USUALLY_HAPPENED_NEXT: same stall-vs-continuation signature as TOC-003. STATED CONFIDENCE:
  qualitative but graduated — "elevated-uncertainty flag" escalating to "max-strength caution" as
  the zone got more heavily defended across instances 3–5.
  **Cross-reference gap, flagged honestly**: TOC-003 and TRADER_LESSON_021 describe what appears to
  be the identical market phenomenon but are never explicitly merged or cross-referenced in any
  file this review accessed — a genuine open item for Q3, not resolved here (see §19).

### The "Countertrend LONG" saga *(Q2-origin, unnamed for most of its life, formally named only at trade #63)*
- The richest, most rigorously self-scrutinized thread in the whole record. SUPPORTING SEQUENCE
  (`RECORDED FACT`, `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md`): trade #47 LOSS −4.232pts → #48
  LOSS −1.416pts → #49 LOSS −5.439pts ("widest-margin loss of the 3 countertrend attempts") → #50
  (initially profitable, final resolution not located within this review's research budget — see
  §20) → #53 LOSS −0.747pts, explicitly the **5th straight countertrend loss**, logged at that
  point as "Countertrend n=5: ALL FIVE have now lost, though magnitudes have shrunk with stronger
  confirmation/management." Contrast: WITH-trend trade #51 in the same window = **+22.386pts, the
  single largest winning trade of the apprenticeship**. Between #53 and #63 (2020-05-19 to 06-08),
  at least 8 further countertrend LONG candidates were correctly declined against #53's own
  elevated 3544/5373-volume benchmark, held even against structurally similar-looking setups. Trade
  #63 (2020-06-08) finally cleared the benchmark on both legs — first countertrend LONG win of the
  apprenticeship, **+2.306R**, immediately formalized as "Countertrend LONG playbook" under the new
  Multi-Timeframe Alignment V1 framework. STATUS: went from ANECDOTE (n=1, #47) through a 5-loss
  DEVELOPING_PATTERN, to REPEATED-and-escalated evidence bar, to a single confirming win under a
  formally reformalized system — functionally the clearest OBSERVATION → DEVELOPING_PLAYBOOK arc in
  the record, even though no file uses those exact status words for it.

### Close-based stop-execution slippage *(Q2-origin, execution-mechanics not market-structure)*
- At least 3 named instances (trades #24, an unnamed instance near #24-28, #28) where a fast/
  high-volume reversal bar's own close landed beyond the stop level, producing a realized loss
  worse than nominal planned risk. Distinct in kind from the market-structure observations above —
  an accepted structural feature of close-based execution interacting with volatility, reinforced
  repeatedly through Q2 on trades #60 (overshoot +2.458pts past nominal), #61, and #62 (closed
  0.009pts past the level — the narrowest margin of the apprenticeship).

### "Hold through target when no exhaustion signal" pattern (TRADER_LESSON_014) *(Q2-origin)*
- 3 confirmed instances: trade #17 LONG +13.458pts ("largest single-trade gain" at the time) →
  trade #26 LONG +15.991pts (new record) → trade #29 SHORT +12.73pts (first SHORT instance,
  directionally generalized). TRIGGER: price reaches the target zone with no exhaustion/stall
  signal — specifically a close-at-high on the trade's largest-volume bar. WHY (stated inline, not
  inferred): a strong-volume close at the extreme reads as absence of exhaustion, implying the move
  isn't finished. COUNTEREXAMPLES: `NOT_RECOVERABLE_WITHOUT_HINDSIGHT` within this review's read
  window. STATUS: DEVELOPING_PATTERN, reinforced 3x, directionally generalized by the 3rd instance.

### CORRECT_NO_TRADE_003/004/005 — "failed confirmation bar immediately after a clean trigger" *(Q2-origin, converges with TOC-003)*
- 3 instances over 2020-05-04/05-05, one explicitly "second such failed trigger today." A clean
  trigger fires on real volume, but the very next bar stalls/reverses on lighter volume — trade
  correctly declined each time; the apparent break subsequently proved false. Filed under a
  different ID family (no-trade discipline) rather than merged into TOC-003 — a second, smaller
  instance of the same cross-reference gap noted above.

### Rejected/degraded ideas
See §16 for the full, dedicated treatment (6 distinct rejected hypotheses, 2 from Q1, 4 from Q2).

---

## 4. Every recorded trade — trade-level audit

**Evidence tiers used below**: `FULL` = rich entry-to-close narrative recovered (trades #59–#66,
from the canonical `2020_Q2_H4_LOG.md`); `STRUCTURED_ONLY` = RESULT_R/points recorded in
`TRADE_EVIDENCE_LOG.md` but no entry-time narrative recovered from canonical files (#48, #51, #52,
#54, #55, #56); `PARTIAL_UNPROMOTED` = narrative found in `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md`
but result never promoted to the official structured backfill (#47, #49, #50, and partially #53).

### FULL tier

**#59** — SHORT, entry 1712.008 (Playbook A pre-correction, WITH-trend). H4 BEARISH / decisive
fresh-low breakdown / 2 consecutive real-volume down-closes (3365, 4993). Confirmation: real-volume
reversal off a fresh local high. Invalidation: close beyond 1726.146. **What happened after entry**:
one real-volume adverse retest correctly not trailed on first rejection; a decisive 7,713-volume
continuation bar triggered the first trail (1726.146→1711.9, marginally profit-locking). Then a
long thin-volume consolidation and adverse drift; closed when a thin-volume (475) bar's close
(1712.662) pierced both the trail and entry. MFE 1.586R / MAE 0.267R (an MFE mislabeling was
self-caught and corrected — no decision affected). RESULT: −0.046R (LOSS). Management action: 1
trail, later shown to have converted a would-be small win into a small loss.

**#60** — SHORT, entry 1707.01 (Playbook A pre-correction). WITH-trend, 2 real-volume down-closes
(2700, 2912) breaking a 19-hour compression. Invalidation: close beyond 1713.5. **After entry**: a
single decisive 7,566-volume reversal bar closed at 1715.958, well past the stop — no trail had yet
been set. MFE 0.223R / MAE 1.497R. RESULT: −1.379R (LOSS), 0.379R worse than nominal, "the mirror-
image risk" of trail-overshoot on an untrailed stop.

**#61** — SHORT, entry 1707.856 (Playbook A pre-correction). WITH-trend resumption after #60, 2
real-volume down-closes (4558, 2585) on a wide-range bar. Invalidation: close beyond 1718.5.
**After entry**: three consecutive wicks pierced to within 0.27–1.63pts of the stop and closed back
below each time (close-based-fill demonstration); a fourth test closed beyond (1720.093). MFE
0.695R / MAE 1.280R. RESULT: −1.150R (LOSS).

**#62** — SHORT, entry 1680.167 (Playbook A pre-correction). Entered only after correctly declining
through the apprenticeship's most extreme whipsaw episode (5 consecutive massive-volume bars,
10603/5946/8498/5480/6299, alternating direction, no valid same-direction pair). Entry triggered on
bars 6–7 (6299, 7431 real-volume down/down), confirmed by a descending-high staircase. Invalidation:
close beyond 1688.5. **After entry**: the 1687–1689 zone tested repeatedly — three separate wicks
pierced the stop outright (closest survival 0.147pts) before the eventual triggering close crossed
by just 0.009pts, the narrowest margin of the apprenticeship. MFE 1.168R / MAE 1.058R. RESULT:
−1.001R (LOSS), remarkably close to nominal despite the drama.

**#63** — LONG, entry 1695.555 (Playbook B, first countertrend win). First trade under the newly-
installed Multi-Timeframe Trend Alignment V1, classified TRANSITIONAL. Three consecutive massive
real-volume bars (7315/5674/6544) following a real-volume test-and-defend of 1688.5 — the first
sequence all quarter to clear trade #53's elevated 3544/5373 benchmark on both legs. Invalidation:
close beyond 1685.5. **After entry**: four disciplined trails (1685.5→1692.9→1696.394→1706.478→
1721.134), each gated by a real-volume-fresh-high-then-real-volume-pullback pattern and a
TRADER_MISTAKE_004 pre-check; survived multiple wick-tests including a 0.252pts closest-survival
margin on the 4th trail. **Closed** on a 6,491-volume reversal bar (largest of the trade's life)
through the 4th trail. MFE 3.163R / MAE 0.506R. RESULT: +2.306R (WIN). STATIC_BASELINE would have
captured +3.043R at the 48h horizon — trailing "cost" upside but avoided the −0.506R MAE exposure
the whole time. **Immediately after this close, a MISSED_OPPORTUNITY was logged** — see §9.

**#64** — SHORT, entry 1740.496 (Playbook A-prime, first WITH-trend SHORT under the corrected
rule). Real-volume (7023/4241) rejection at a **twice-tested** resistance zone (1743–1745), the
first entry explicitly classified GENUINE_LOCAL_BEARISH_RE-ALIGNMENT (not a bare 2-bar test) —
directly contrasted against a materially weaker bare-2-bar signal correctly declined 3 days
earlier. Invalidation: close beyond 1744.918. **After entry**: three trails (1744.918→1736.066→
1735.232→1733.254), each off a confirmed pause/rejection at resistance; survived nine distinct
wick-tests including a 0.031pt margin (narrowest of the apprenticeship at that point); first trade
carried through a weekend gap. MFE 2.467R / MAE 0.209R. RESULT: +1.443R (WIN).

**#65** — SHORT, entry 1724.903 (Playbook A-prime). WITH-trend resumption of the bearish drift
after a wide choppy range (H1 directionless, not actively fighting the SHORT) — FULLY_ALIGNED.
Invalidation: close beyond 1732.242. **After entry**: one trail after a 10-bar down-sequence broke
the post-entry chop range; the **fixed-SL/TP methodology was installed mid-trade** here (a
retroactive structural TP frozen alongside the SL, made operative going forward). A visualization
tick-conversion bug (10x error) was found and fixed mid-trade; the underlying trade computation
(done in raw price points) was confirmed unaffected. RESULT: −1.119R (LOSS) — frozen SL hit, TP
never approached (closest 8.3pts short).

**#66** — SHORT, entry 1766.952 (Playbook A-prime, final Q2 trade). First trade under the fully-
installed fixed-SL/TP methodology. WITH-trend, real-volume acceptance lower on two consecutive
fresh-low closes off an impulse-top reversal — PARTIALLY_ALIGNED (H1 in an active bullish impulse
just broken). Invalidation: close beyond 1778.874. **After entry**: unrealized reached +10.1pts
before a sharp bounce erased most of it; four consecutive real-volume pushes drove the trade to
within 0.006pts of TP (1747.566) before a violent reversal erased the gain back to near-breakeven —
direct motivation for the Structural TP Execution Buffer V1. A TradingView Desktop restart
mid-trade required a verified read-only recovery (no post-restart data used); the Q2 boundary was
corrected twice before finalization. A near-miss on the SL (0.977pts clear) survived the close-based
rule; two bars later a decisive real-volume close (1783.614) triggered it cleanly (entire bar range
above the stop). MFE 1.626R / MAE 1.467R. RESULT: −1.398R (LOSS).

### STRUCTURED_ONLY tier (#48, #51, #52, #54, #55, #56)

| # | Dir | Entry | Exit | Result pts | RESULT_R | Narrative recoverable? |
|---|---|---|---|---|---|---|
| 48 | LONG | 1731.446 | 1730.03 | −1.416 | −0.182 | Partial — see PARTIAL_UNPROMOTED note below |
| 51 | SHORT | 1754.79 | 1732.404 | +22.386 | +6.120 | No — largest win of the apprenticeship, mechanism not recovered here |
| 52 | SHORT | 1733.911 | 1735.654 | −1.743 | −0.718 | No |
| 54 | SHORT | 1744.494 | 1752.328 | −7.834 | −1.006 | No — TRADE_EVIDENCE_LOG.md notes it was "never trailed... exited a hair past its original stop" |
| 55 | SHORT | 1728.586 | 1725.33 | +3.256 | +0.447 | No |
| 56 | SHORT | 1718.845 | 1712.988 | +5.857 | +0.616 | No |

MFE, MAE, market regime detail, thesis reasoning, and management actions for these six trades are
`NOT_RECOVERABLE_WITHOUT_HINDSIGHT` — genuinely absent from any file this review accessed, not
merely unsearched (per `TRADE_EVIDENCE_LOG.md`'s own backfill note: "MFE/MAE NOT_RECOVERABLE_WITHOUT_HINDSIGHT
in this first pass... a deferred, separately-schedulable task, not a refusal").

### PARTIAL_UNPROMOTED tier (#47, #48, #49, #50, #53)

Narrative found in `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md`, all part of the Countertrend LONG
saga (§3): #47 LOSS −4.232pts, #48 LOSS −1.416pts (matches the structured figure above — the one
point of overlap), #49 LOSS −5.439pts ("widest-margin loss"), #50 initially profitable /
final resolution not located, #53 LOSS −0.747pts (matches `TRADE_EVIDENCE_LOG.md`'s backfilled
figure exactly). **#47, #49, #50's RESULT figures as narrated in the Thesis Ledger were never
promoted into `TRADE_EVIDENCE_LOG.md`'s official 17-trade structured set** — flagged in §20 as a
genuine, actionable gap, not treated as authoritative here since it sits outside the officially
reconciled structured backfill.

### Trades #1–#46 (excl. #48), #49 [narrative only], #50 [narrative only]

Genuinely `NOT_RECOVERABLE_WITHOUT_HINDSIGHT` for structured fields, per standing
`EVIDENCE_UPGRADE_METHODOLOGY_V1.md` §2 scope. This review does not reconstruct or estimate them.

---

## 5. Why each losing trade lost

Covers every FULL-tier and STRUCTURED_ONLY-tier loss with recoverable classification basis. Losses
in the PARTIAL_UNPROMOTED tier (#47, #49) are given a best-effort classification flagged as
lower-confidence, since their full frozen entry-time context wasn't recoverable within this review.

| # | PRIMARY_CAUSE | SECONDARY_CAUSE | Thesis reasonable? | Execution good? | Management good? | Avoidable w/o hindsight? |
|---|---|---|---|---|---|---|
| 48 | INSUFFICIENT_CONFIRMATION | COUNTERTREND_ERROR | UNCLEAR (pre-escalation-bar era) | UNCLEAR | NOT_RECOVERABLE | UNCLEAR |
| 49 | INSUFFICIENT_CONFIRMATION | COUNTERTREND_ERROR | UNCLEAR | UNCLEAR | NOT_RECOVERABLE | UNCLEAR |
| 52 | GOOD_TRADE_NORMAL_LOSS | — | YES | YES | NOT_RECOVERABLE | NO |
| 53 | GAVE_BACK_MFE (small) | MANAGEMENT_ERROR (minor) | YES | YES | UNCLEAR — "2nd instance of profit-locking trail still producing a loss" | UNCLEAR |
| 54 | GOOD_TRADE_NORMAL_LOSS | — | YES | YES | N/A (never trailed) | NO |
| 57 | GOOD_TRADE_NORMAL_LOSS | — | YES | YES | N/A (never trailed) | NO |
| 59 | MANAGEMENT_ERROR | GAVE_BACK_MFE | YES | YES | **NO** — trail level too tight relative to volatility, converted +1.586R MFE into a realized loss | **YES** — a wider or delayed trail, or accepting the risk of staying at original stop longer, was a genuinely available prospective choice |
| 60 | GOOD_TRADE_NORMAL_LOSS | STOP_OVERSHOT (close-based mechanics) | YES | YES | N/A (untrailed) | NO — overshoot is a structural feature of close-based fill, not a rule violation |
| 61 | GOOD_TRADE_NORMAL_LOSS | — | YES | YES | N/A (untrailed) | NO |
| 62 | GOOD_TRADE_NORMAL_LOSS | — | YES | YES | N/A (untrailed) | NO — textbook demonstration of correctly-functioning close-based discipline despite dramatic wick action |
| 65 | GOOD_TRADE_NORMAL_LOSS | — | YES | YES | N/A (fixed-SL/TP) | NO — thesis reasonable, TP never approached |
| 66 | GAVE_BACK_MFE (methodology-level, not discretionary) | NO_PARTIAL_CAPTURE_MECHANISM | YES — real-volume breakdown off a documented impulse top, fully aligned tags | YES — close-based SL correctly triggered, no rule violation | **N/A by design** — fixed-SL/TP had zero discretion to exercise; the "failure" is structural (no partial-take existed), not an execution/discretion error | **NO** for the SL trigger itself; **the broader structural gap (no partial capture) is the direct evidentiary basis for Multi-Target System V1**, i.e. it *was* prospectively addressable at the methodology-design level, just not within this trade's own frozen rules |

**Do NOT read every loss as a mistake.** 8 of the 12 classified losses above are
`GOOD_TRADE_NORMAL_LOSS` — a reasonable thesis, correct execution, and no management error; the
market simply resolved against a well-formed trade. This is the honest, expected shape of a
directional trading process and is stated plainly rather than searched for hidden fault. Two losses
(#59, #66) point to genuine, actionable process findings — one a discretionary management error
(§10), one a structural methodology gap now being addressed prospectively (§11), never
retroactively.

---

## 6. Why winning trades won

| # | What was read correctly | Timeframes agreeing | Confirming behavior | Regime | Entry characteristic | Win source |
|---|---|---|---|---|---|---|
| 51 | WITH-trend alignment with the dominant, unbroken H4 bear regime | H4 (context) + entry-level M15 confirmation | Not narratively recovered — `PARTIAL` | R02 CLEAN_BEAR_TREND | Tight initial risk (3.658pts) relative to eventual move (+22.386pts) | **Favorable regime alignment + large asymmetric opportunity** |
| 55/56 | WITH-trend, smaller real-volume confirmations | H4/M15 | Not narratively recovered | R02 | — | Favorable regime alignment |
| 58 | WITH-trend, fresh-high rejection | H4/M15 | 2 real-volume closes lower | R02 | — | Good direction + good timing, but trailing **underperformed** its own static baseline by 15.233pts/3.061R — a win, achieved despite suboptimal management, not because of it |
| 63 | First genuine countertrend re-alignment to clear the elevated benchmark on **both legs** | H4 (context, stale-flagged) + H1 (confirmed real-volume recovery) + M15 (3 massive-volume bars) | 3 consecutive massive-volume closes, real-volume test-and-defend precursor | TRANSITIONAL (R08 watch, unconfirmed) | Unusually rare/strong confirmation vs. a persistent trend; large structural room (48.5h hold) | **Good timing (rare, disciplined confirmation) + disciplined 4-stage management** — the clearest case in Q2 where entry selectivity AND management both genuinely contributed |
| 64 | Genuine local bearish re-alignment at a twice-tested resistance zone, explicitly distinguished from a materially weaker bare-signal declined 3 days earlier | H4/H1(TRANSITIONAL)/M15 all independently tagged | Real-volume rejection (7023/4241) | R02 with active R08 watch context | Entry at a *twice*-tested level, not a first test | **Good direction + good timing (selective entry) + disciplined 3-stage management surviving 9 wick-tests** |

**Common characteristics of winners**: (1) real/elevated volume at the confirming bars (shared with
several losers too — not a clean discriminator alone, see §7); (2) for SHORT wins, simple alignment
with the persistent H4 regime; (3) for the single LONG win, an unusually high, newly-cleared
confirmation bar rather than a bare pattern match; (4) where trailing was used (#58, #63, #64), the
management was disciplined and gated by explicit re-confirmation at each step, even where it
nominally "cost" some upside vs. a static hold. **No win in this dataset is attributable to pure
luck/noise** in the sense of contradicting its own entry thesis — every FULL-tier win's eventual
resolution was consistent with the reasoning stated at entry.

---

## 7. Winners vs. losers

**What most clearly distinguished winners from losers** (evidence-grounded, variables the trader
was actually observing):

1. **Confirmation-bar strength for countertrend LONG entries.** The clearest, most directly
   evidenced discriminator in the whole record: 5 straight countertrend losses (#47–#53) at
   progressively-but-still-insufficient confirmation, followed by the first win (#63) only once the
   evidence bar was cleared on *both* legs for the first time. This is a genuine, prospectively-
   observable, escalating discipline that produced a real result.
2. **Immediate continuation vs. stall in the 1–2 bars after a defended-level break** (TOC-003 /
   TRADER_LESSON_021, §3) — the clearest within-playbook discriminator found for WITH-trend
   breakout-style entries specifically, 2W/4L split tracking that exact signature.

**What looked important but did NOT actually distinguish winners from losers:**

1. **Multi-Timeframe Alignment tag at entry.** Counterintuitively, per the Q2 checkpoint's own
   fully-evidenced-trade analysis, `FULLY_ALIGNED` trades performed *worst* (1W/6L, −3.593R) while
   `PARTIALLY_ALIGNED` (1W/1L) and `TRANSITIONAL` (1W/0L) both came out ahead. This is a genuinely
   surprising finding, addressed in depth in §14 — the tag itself, as a static entry-time label,
   did not predict outcome in this sample.
2. **Real volume presence at the confirming bars.** Both winners (#58, #63, #64) and several losers
   (#60, #61, #62) had genuine, elevated real volume at entry — volume-presence alone does not
   discriminate; what mattered more (per point 2 above) was the market's *reaction* in the bars
   immediately following, not the volume of the trigger itself.
3. **Wick-test survival count during the trade's life.** Both the largest win (#63, surviving
   multiple wick-tests down to a 0.252pts margin) and several losses (#61, #62, surviving 3–4
   wick-tests before eventually triggering) show similar intrabar drama — the number of close
   survivals a trade racks up before its eventual resolution does not itself predict which way that
   resolution goes.
4. **Nominal H4 direction alone.** Every trade in Q2 shared the same H4-BEARISH context; it cannot,
   by construction, discriminate within-quarter outcomes (see §11 in the regime-forensics sense).

---

## 8. No-trade decisions

`CORRECT_NO_TRADE` decisions in Q2 were extensive and, on the evidence, effective:

- **The countertrend LONG evidence-bar discipline** (§3, §7): at least 8+ candidates correctly
  declined between #53 and #63 against a benchmark that was never lowered, even when a later
  setup structurally resembled a prior qualifying one ("correctly held to the same standard, not
  lowered because the pattern looks similar," 2020-06-15/06-23 entries).
- **The first live test of the Multi-Timeframe forward SHORT rule** (2020-06-11 14:00–14:30 UTC): a
  bare 2-consecutive-real-volume down-close pair technically formed but was trivial in magnitude
  (−0.533pts, −0.017pts) and lacked genuine local re-alignment — correctly declined, explicitly
  logged as the rule's first real test, and it worked as intended.
- **Two extreme multi-bar whipsaw episodes** (a 5-bar alternating-massive-volume stretch before
  #62; a separate 4-bar whipsaw battle, 2739–6281 volume, before a Playbook B candidate) — both
  correctly declined through, despite dramatic price action, explicitly logged as "discipline
  holds" and "a textbook illustration of why the standing same-direction-pair discipline matters."
- **CORRECT_NO_TRADE_003/004/005** (§3): three failed-confirmation-bar declines over 2 days,
  correctly avoiding false breaks.

**Is the trader becoming more selective?** `SUPPORTED INFERENCE`, yes — the countertrend evidence
bar was raised once (after #53) and never subsequently lowered despite repeated pressure from
similar-looking setups; the Multi-Timeframe correction added an entirely new, stricter forward
SHORT-entry requirement mid-quarter (genuine local re-alignment, not a bare 2-bar count).

**Was NO_TRADE ever too conservative?** Only one documented instance — see §9. The overwhelming
pattern in the available record is NO_TRADE decisions being subsequently validated by the market
continuing to behave as the decline predicted, not regretted.

---

## 9. Missed opportunities

**Exactly one explicitly documented instance** (`RECORDED FACT`, `2020_Q2_H4_LOG.md`,
2020-06-10, immediately after trade #63's close): the two bars that closed #63 and immediately
followed formed a clean, qualifying WITH-trend SHORT sequence under Playbook A criteria. It was
never evaluated in real time because attention was on managing #63's close; by the time the gap
was noticed, a further bar had already been read, so per standing no-hindsight governance **no
retroactive entry was taken**. Logged explicitly as `MISSED_OPPORTUNITY` for `STRATEGY_EVIDENCE_DENOMINATOR.md`.

**Classification**: `ATTENTION / EXECUTION ISSUE` — not `GOOD_DISCIPLINE`, not `PROCESS_FAILURE`,
not `TOO_STRICT_FILTER`. This was a genuine, honestly-disclosed attention gap during a fast-moving
transition between managing one position and evaluating the next setup, not a filter or rule
problem. No other missed opportunity is documented anywhere in the files this review accessed —
this review does **not** invent hypothetical missed trades from chart hindsight, per the mandate.

---

## 10. Management forensics

**ACTUAL_MANAGEMENT vs. COUNTERFACTUAL_MANAGEMENT_RESEARCH, kept strictly separate** (per
`EVIDENCE_UPGRADE_METHODOLOGY_V1.md` §1 — STATIC_BASELINE never influences a live trade and is
never mixed into actual Q2 statistics; §1's own executive-summary and §3 numbers above are all
ACTUAL_MANAGEMENT figures):

| Trade | ACTUAL result | STATIC_BASELINE (counterfactual, never-trailed) | Actual − Static |
|---|---|---|---|
| 58 | +2.463R | +5.524R (HORIZON_MARK) | **−3.061R** |
| 59 | −0.046R | +2.179R (HORIZON_MARK) | **−2.225R** — trailing flipped a would-be win into a realized loss |
| 63 | +2.306R | +3.043R (HORIZON_MARK) | **−0.737R**, but avoided the static hold's −0.506R MAE exposure the entire time |

**Did fixed SL/TP protect or damage expectancy?** For trades #57, 60, 61, 62, 65, 66 — no discretionary
management occurred at all (ACTUAL = STATIC exactly, 0.000 diff in every case), so this specific
question doesn't apply to them; a *different* management question applies instead — see below.

**When did trailing help?** #63 is the one clean case: despite giving back nominal R vs. the
horizon snapshot, the 4-stage trail demonstrably avoided real, sustained adverse exposure (−0.506R
MAE) that a pure static hold would have carried the entire ~48.5-hour life of the trade. This is
genuine downside-protection value, even though the upside comparison looks unfavorable in isolation.

**When did trailing cut winners short or hurt?** #58 and, most starkly, #59 — the latter converting
a would-be +2.179R static win into a realized −0.046R loss. **Every trailed trade in this dataset
underperformed its own static baseline**, unanimously across all 3 comparable pairs — a small
sample, but a unanimous direction, and the direct empirical basis for the fixed-SL/TP methodology's
adoption mid-quarter.

**How often was meaningful MFE later surrendered?** 7 of the 10 FULL-tier trades (#57, 59, 60, 61,
62, 65, 66) saw a favorable excursion of ≥0.6R **not captured at all** by the close. Average MFE
across the 10 was 1.646R; average MAE 0.910R — the gap between what was available and what was
realized is the single largest recurring pattern in the fully-evidenced Q2 record.

**How often did price approach target and reverse?** Twice, dramatically: #66 (0.006pts from full
TP, reversed to a full loss) and #63 (reached its true MFE the same bar as its own 48h horizon mark
before a sharp reversal 30 minutes later).

**When would breakeven have helped / hurt?** `TRADER_MISTAKE_004` (trade #42, pre-Q2-window per
`AI_TRADER_EXPERIENCE_LEDGER.md`) is directly instructive: a reactive breakeven stop was set at a
level the *very bar that triggered the reassessment* had already traded through — a stop cannot
protect against a move that already happened before it's set. The prospective fix (explicitly check
whether the reacting bar's own close has already passed the proposed new level before freezing it)
was applied cleanly on every subsequent trade through #45 with no recurrence found. This is the
single most concrete, actionable management-mechanics lesson in the entire record and directly
informs the AFTER_TP1_STOP_RULE recommendation in §11.

**Trade #66 used only as evidence, never as grounds to rewrite the historical result** — its
−1.398R LOSS stands unmodified; it appears above solely as the starkest illustration of the
no-partial-capture structural gap.

---

## 11. TP1/TP2/TP3 management recommendation (RESEARCH ONLY — nothing installed)

The 40/30/30 split installed in `AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1.md` is explicitly
provisional. **No Q2 trade was ever run under a real multi-target system** — Q2 used either no
target at all (trailing-only, pre-#65) or a single all-or-nothing fixed TP (#65, #66). Everything
below is therefore evidence-*informed* reasoning about what the available Q2 evidence suggests,
not a measured optimum from actual multi-target trades. That distinction is kept explicit
throughout.

- **RECOMMENDED_TP1_PERCENT = 40%** — `KEEP`. No Q2 evidence contradicts this default; it cannot,
  since no trade tested any split. Retained as a reasonable starting hypothesis.
- **RECOMMENDED_TP2_PERCENT = 30%** — `KEEP`.
- **RECOMMENDED_TP3_PERCENT = 30%** — `KEEP`.
- **AFTER_TP1_STOP_RULE**: move to breakeven once TP1 is **genuinely banked** (the partial exit has
  actually executed, not merely approached). Directly targets the #59/#66 failure mode — both gave
  back 100% of a substantial favorable excursion with zero capture; a banked TP1 makes that specific
  outcome structurally impossible for the position as a whole. Must respect the `TRADER_MISTAKE_004`
  lesson: verify the reacting bar's own close hasn't already invalidated the proposed breakeven
  level before freezing it.
- **AFTER_TP2_STOP_RULE**: trail to the structural level that defined the TP1→TP2 leg (e.g., the
  swing point the leg broke from), not a fixed distance — consistent with the apprenticeship's
  structural-first target-selection principle (§7 of the new mandate) applied to stop placement too.
- **TP3_MANAGEMENT_RULE**: structural trailing preferred over a hard fixed cap. Evidence: #58's
  STATIC_BASELINE showed +27.492pts genuinely available vs. +12.259pts captured — XAUUSD
  demonstrably continued well past what looked like a "reasonable" objective at the time, more than
  once in this small sample (#63 similarly reached its true MFE at almost the exact moment of its
  own 48h horizon mark). A fixed TP3 cap would have foreclosed exactly this upside in both cases.
- **Should TP3 remain fixed or become structural trailing?** Structural trailing, per the above.
- **When should breakeven be used?** After a real partial exit has banked genuine profit — never
  purely reactively on an in-progress adverse move (the exact TRADER_MISTAKE_004 pattern).
- **When should it NOT be used?** On trades with very tight initial risk (a handful of points),
  where normal M15 noise could stop out a still-valid thesis at breakeven prematurely. This is
  `LOW_CONFIDENCE` reasoning — a plausible inference, not evidence-proven in Q2, since no small-risk
  trade's breakeven behavior was specifically studied here.
- **Should part of the final position be allowed to run beyond TP3 in exceptional price-discovery
  conditions?** **Yes**, as a *pre-declared* possibility only — never invented after the fact.
  `AI_TRADER_REGIME_STRATEGY_MATRIX.md`'s own R10 (CLEAN_BREAKOUT/PRICE_DISCOVERY) is already
  flagged as the apprenticeship's highest-caution zone from two extraordinary, unresolved
  record-volume episodes in Q1/Q2 — genuine large-expansion conditions are real and documented, not
  hypothetical, but must be recognized and declared in the frozen management plan before entry,
  exactly as §14 of the new operating standard requires.

**Overall verdict: `KEEP_40_30_30`**, with the stop-management refinements above layered on top as
the actual substance of the recommendation — the split itself is the least evidence-constrained
part of this system; the *stop rules around it* are where Q2's real, hard-won lessons apply.

---

## 12. Playbook forensics

| Playbook | Setup logic (as currently understood) | Regime | N | W | L | Win rate | Net R | Avg R | MFE/MAE character | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** (pre-correction WITH-trend SHORT, #51–62 pooled) | Bare 2 consecutive real-volume down-closes, H4 BEARISH, no MTF alignment check | R02 CLEAN_BEAR_TREND | 11 | 4 | 7 | 36.4% | **+2.985R** / **−2.192pts** (sign diverges by unit — see Q2 checkpoint §10) | +0.271R | Not systematically tracked pre-Evidence-Upgrade | RETIRED |
| **A-prime** (post-correction WITH-trend SHORT, #64–66) | 2 real-volume closes + genuine local bearish re-alignment (not bare count), H4/H1/M15 tags frozen independently | R02 w/ R08 watch context | 3 | 1 | 2 | 33.3% | −1.074R | −0.358R | avg MFE 1.582R, avg MAE 0.629R across its 3 trades | DEVELOPING_PLAYBOOK, net negative |
| **B** (Countertrend LONG, elevated evidence bar) | 2 consecutive real-volume closes clearing #53's 3544/5373 benchmark on both legs, against dominant H4 | TRANSITIONAL (R08 watch) | 2 | 1 | 1 | 50.0% | +2.196R | +1.098R | #63: MFE 3.163R / MAE 0.506R; #53: not recovered | DEVELOPING_PLAYBOOK, thin sample |

- **HIGHEST_OBSERVED_WIN_RATE**: Playbook B, 50% — n=2, not promotable from this alone.
- **HIGHEST_OBSERVED_EXPECTANCY**: Playbook B, +1.098R/trade — same caveat, driven almost entirely
  by one trade.
- **MOST_CONSISTENT**: none genuinely qualifies. Closest: Playbook A (pre) has the largest N (11)
  and its positive R figure isn't single-trade-dependent (4 separate wins), though it's retired for
  a documented defect and net-negative in raw points.
- **MOST_REGIME_DEPENDENT**: all three, equally — 100% of Q2 occurred in one H4-BEARISH regime.
  Playbook A/A-prime particularly so, since their entire premise is alignment WITH that regime.
- **MOST_PROMISING**: the underlying countertrend-LONG *mechanism* (escalating evidence-bar
  discipline across #47→#53→#63) — not for its raw numbers (n=2), but because it shows the clearest
  documented arc of genuine prospective learning culminating in a real result.
- **MOST_DISAPPOINTING**: Playbook A-prime — installed specifically to fix Playbook A's problems,
  currently net negative in both R and points after its first 3 trades.
- **CLOSEST_TO_STRATEGY_CANDIDATE**: Playbook A-prime, by specification-completeness (the only
  currently-active, fully-specified, prospectively-tested forward rule) — explicitly **not** by
  performance, per the standing instruction not to promote from Q2 results alone.

`TRADER_STRATEGY_CANDIDATES.md`'s verdict stands, reaffirmed: **`NO_STRATEGY_CANDIDATE_READY_YET`**.

---

## 13. Regime forensics

Q2 occurred entirely inside **one unbroken H4-BEARISH regime** — `RECORDED FACT`, never once
broken across all 66 trades, per `AI_TRADER_REGIME_STRATEGY_MATRIX.md` and every trade's own
frozen H4_REGIME tag. This has one direct consequence for this section: there is no genuine
CLEAN_TREND(bull)/RANGE/confirmed-TRANSITION regime diversity to compare within Q2 — only
sub-textures inside the single standing regime.

- **R02 CLEAN_BEAR_TREND**: the standing context for the entire quarter. Trade performance: all 17
  structured trades. Reading quality: generally sound (8 of 12 classified losses were
  `GOOD_TRADE_NORMAL_LOSS`, not misreads). Common mistake: treating the formal H4 tag as durable
  without checking whether H1/M15 behavior had already begun diverging from it (§14). Successful
  behavior: WITH-trend entries requiring genuine real-volume confirmation, not bare pattern counts.
  Candidate specialist logic: Playbook A-prime, currently unproven (§12).
- **R08 BULLISH_TRANSITION**: `REGIMES_WITH_INSUFFICIENT_EXPERIENCE`, watched continuously from
  2020-06-08 (`REGIME_STALENESS_WARNING = ACTIVE`) through the end of Q2, **never formally
  confirmed**. This is arguably the single most consequential open regime question of the quarter —
  price continued higher through and past trade #66's own SL, which if anything strengthens the
  case that R08 was a real, live phenomenon the formal H4 label never caught up to.
- **R10 CLEAN_BREAKOUT/PRICE_DISCOVERY**: flagged as the apprenticeship's highest-caution zone —
  two extraordinary real-volume episodes (Q1: 1709.7–1713.73 zone) each failed to cleanly resolve
  despite record/record-duration volume. Open question, never answered: whether this reflects
  something genuinely anomalous about that specific zone, or illustrates that extreme volume alone
  never guarantees resolution.
- **Failed-breakout/whipsaw texture**: repeatedly encountered and repeatedly handled correctly (§8)
  — the 5-bar and 4-bar extreme alternating-volume episodes are the clearest evidence the trader can
  reliably decline through genuinely chaotic conditions without forcing a trade.
- **R12 SESSION_SPECIFIC**: Asia consistently thinnest; London consistently where real-volume
  expansion begins; NY_US_CASH produced the largest single-bar volumes recorded (including trade
  #66's own stop-out, which occurred in the NY pre-open window).
- **No genuine CLEAN_TREND(bull), RANGE, or confirmed TRANSITION regime was ever traded in Q2** —
  this is itself the central, honestly-disclosed regime-forensics finding: everything the trader
  has learned this quarter about "what works" was learned entirely against a bearish backdrop that
  never let up.

---

## 14. Multi-Timeframe Alignment review

The Q2 checkpoint's finding stands, reaffirmed here with the deeper evidence this review gathered:
`FULLY_ALIGNED` trades performed the *worst* in the fully-evidenced set (1W/6L, −3.593R), while
`PARTIALLY_ALIGNED` (1W/1L, +0.045R) and `TRANSITIONAL` (1W/0L, +2.306R) both came out ahead. n=7/2/1
is far too small in every bucket to support a real conclusion, and this is stated as such, not as a
finding to explain away.

**Why FULLY_ALIGNED trades performed poorly, evidence-supported reasoning (not proven):**

1. **H4 context did go stale**, on the record. `REGIME_TRANSITION_WATCH.md` documents
   `REGIME_STALENESS_WARNING = ACTIVE` set 2020-06-08 — precisely because a persistent H1 bullish
   recovery had been developing for days beforehand while H4 remained formally, unbrokenly
   BEARISH. Six of the seven FULLY_ALIGNED losing trades (#57, 59–62, 65) were entered **before**
   this correction, under the old bare-WITH_TREND label, during exactly the stretch the correction
   was later installed to address.
2. **H1/M15 local structure carried more real-time information than the formal H4 label** —
   this is the explicit rationale the CEO gave for installing Multi-Timeframe Trend Alignment V1
   in the first place, and it is directly supported by the fact that the two post-correction
   categories (PARTIALLY_ALIGNED, TRANSITIONAL) outperformed the pre-correction FULLY_ALIGNED
   bucket in this sample.
3. **Transition periods were, on this evidence, under-classified rather than misclassified** — R08
   sat at `INSUFFICIENT_EXPERIENCE`/`ACTIVE_WARNING` status for the back half of the quarter without
   ever resolving to CONFIRMED, meaning trades taken during this stretch had no clean regime label
   available at all, not merely a wrong one.
4. **Formal H4 direction was, on the balance of this evidence, over-weighted** in the pre-correction
   framework — precisely the defect the correction targeted, and precisely why "FULLY_ALIGNED"
   (which in the old framework was largely synonymous with "matches the never-changing H4 tag")
   ended up correlating with the worst-performing bucket rather than the best.

**What this review does NOT do**: change the Multi-Timeframe Alignment model because of these
results. Per explicit instruction, this is stated as evidence and uncertainty, not acted on. n=3
resolved trades under the corrected model (Playbook A-prime) is nowhere near enough to judge
whether the correction itself actually fixes the problem it was designed to address — Playbook
A-prime is, after all, currently net negative too (§12). The honest state is: the correction has a
sound, evidence-grounded rationale, but has not yet demonstrated a fix.

---

## 15. Trader mistakes

Genuinely complete list from `AI_TRADER_EXPERIENCE_LEDGER.md` (through trade #45) and
`2020_Q2_H4_LOG.md` (trades #59–66 and this session's own record):

| ID | What happened | Why | Affected a trade? | What changed prospectively | Repeated? |
|---|---|---|---|---|---|
| **TRADER_MISTAKE_001** (2020-04-01, trade #1) | Reached +11.7pts favorable, no exit/management plan existed, fully round-tripped to a net loss | No MANAGEMENT_PLAN field existed in the entry contract at all | YES — converted a winner into a loss | Six-field `Q2_TRADE_PLAN_CONTRACT.md` installed (ENTRY/STRUCTURAL_INVALIDATION/INITIAL_STOP/TARGET/MANAGEMENT_PLAN/REASSESSMENT_TRIGGER) | No — never recurred in this specific shape after the contract's installation |
| **JUDGMENT_OVERRIDE_001 / TRADER_MISTAKE_002** (2020-04-02) | A frozen `SHORT_IF` condition fired outright; the trader then introduced a new, previously-unfrozen requirement to justify not entering — a post-trigger goalpost move | Discretion applied *after* a rule had already been satisfied, not before | No trade entered (prevented, not corrupted) — a counterfactual shadow trade was tracked separately, never entering P&L | CEO ratified: a frozen condition may only fire/fail/not-yet-trigger, never be redefined after satisfaction; `TRIGGER_FIRED` formally distinguished from `TRADE_PLAN_COMPLETE` | No confirmed second instance of a *post-trigger* goalpost move found in the reviewed record |
| **TRADER_MISTAKE_004** (2020-05-04, trade #42) | A reactive breakeven stop was set at a level the very reacting bar's own close had already passed | No check existed for "has the current bar already invalidated this new level" | Affected how the loss was recorded (attribution), not whether the trade would have closed anyway | Explicit pre-check adopted, applied and confirmed clean on every subsequent trade through #45 | No |
| **CEO audit — stop-fill convention reversion** (trades #43/#44) | The post-pilot architecture silently reverted to intrabar-touch triggering with fill at the nominal stop, breaking the established close-based convention | Not self-caught — surfaced only by a direct CEO check | **YES, materially** — #43's recorded loss grew by 3.4pts on correction; **#44 flipped from a recorded WIN to a LOSS**; the running 44-trade net P&L was corrected down from +17.375pts to +8.579pts | Corrected convention reapplied and confirmed working "under real pressure in both directions" by trade #45 | Not found to repeat after correction |
| **TRADER_LESSON_017** (technique-transfer caution, trades #18–20) | A "raise the bar" technique validated at one zone (1617–1624) was reapplied to a different zone and failed on first application, despite meeting the letter of the pre-declared standard | Applying a validated technique a second time without re-deriving *why* it worked the first time | Contributed to a loss at the new zone | Named explicitly as the boundary between legitimate discipline and disguised goalpost drift — a standing caution, not a rule change | Not independently re-tested within the reviewed record |
| **ERRATUM** (self-discovered, ~trade #57) | A 15-minute timestamp mislabeling across three consecutive material writes | Incrementing a mental clock instead of re-verifying via python3 timestamp checks | No — confirmed zero impact on any trading decision | Reinforced the zero-exceptions python3-verification discipline already standing | No |
| **Visualization tick-conversion bug** (trade #65) | A 10x error in stopLevel/profitLevel tick conversion rendered chart boxes at 1/10th intended distance for the whole session | Tick size (0.001) vs. an assumed 0.01 | No — underlying trade computation (done directly in price points) confirmed unaffected; visualization only | Corrected; tick size 0.001 now explicit standing knowledge | No |
| **This session's own error** (Q3-PL-0002 batch, real-time) | Four Q3 bars' OHLCV data were shifted one row against their timestamps when writing a log batch, with one bar's true data dropped and replaced by a garbled duplicate | A composition/copy slip while writing the narrative entry, not a data-retrieval error | No — FLAT throughout, no trade decision affected; underlying `data_get_ohlcv`/timestamp-verification calls were all individually correct | Immediate self-discovery and ERRATUM correction logged in `2020_Q3_H4_LOG.md`, per this project's own standing precedent | Not yet re-observed |

**RULE_DRIFT / GOALPOST_MOVE, as a category**: the single explicitly-named instance is
JUDGMENT_OVERRIDE_001 above. TRADER_LESSON_017 interrogates the *risk* of drift (technique transfer
without re-derivation) without itself being a confirmed rule violation. No other instance found.

---

## 16. What was rejected

| Idea | Why it looked promising | What contradicted it | Why degraded/rejected |
|---|---|---|---|
| "Compression-resolution reclaims are more durable than sweep-reclaims" *(Q1)* | An initial reclaim-out-of-compression looked structurally cleaner than an earlier fast-sweep reclaim that had failed | The compression-reclaim also failed one entry later (fresh low made below the original breakdown) | Both reclaim signatures observed in Q1 failed — dropped, not revisited as a named candidate |
| "1625 is a durable floor" *(Q1)* | Held three separate real-volume tests, called "the single most consistent structural feature of the episode" | Broke cleanly on the 4th test to a fresh low | Explicitly self-falsified in the very next log entry — generalized into the standing lesson "a level holding N times does not predict an N+1th hold" |
| Premature TOC-002-counterexample lean (1504.8, 16-bar hold) *(Q1)* | A hold far exceeding TOC-002's original 5–6 bar failure threshold looked like the first genuine counterexample | The hold failed after all, ~20 minutes later in replay time | Self-corrected explicitly — actually *reinforced* TOC-002 (extending its scope to longer holds) rather than weakening it; lesson: never call a counterexample while a hold is still in progress |
| "Widen the stop to fix single-bar whipsaw losses" *(implicit, Q2, trade #7)* | Reduced whipsaw-triggered losses | Produced the largest single-trade loss up to that point via a *different* failure mode (slow grind-through) | Explicitly corrected — risk-sizing is a genuine trade-off, not a solvable problem |
| "Clean trigger + real volume → reliable" *(Q2, trades #11/12/17)* | 3-for-3 wins on real-volume, clean triggers | The largest-volume trigger of the whole set (trade #18) still whipsawed in one bar | Downgraded from "reliable" to "describes entry-signal quality, not a guarantee of follow-through" |
| "With-trend setups are inherently safer than countertrend" *(implicit, Q2, trade #14)* | Seemed obviously true a priori | The first genuine with-H4-trend SHORT whipsawed immediately while 3 prior countertrend longs had all won | Explicitly walked back as likely oversimplified; reframed into the untested hypothesis "trading against the most recent few hours of momentum is costly regardless of nominal H4 alignment" — never re-tested, remains open (§19) |
| "A heavily-defended level breaking is inherently a more reliable trigger" *(Q2, naive framing, trades #28–36)* | Intuitive — more tests "should" mean more conviction on the eventual break | Found the opposite at first (1W/4L at n=5) | Not simply rejected — refined into the stall-vs-continuation distinguishing feature that became TOC-003/TRADER_LESSON_021 |
| "A level surviving N tests makes the N+1th more likely to hold" *(Q2, trade #41 area)* | Intuitive extrapolation from repeated successful defenses | Two successful real-volume defenses explicitly did not make a third more likely; generalized from the Q1 "1625 floor" lesson | Explicitly rejected as a standing caution against that entire reasoning pattern, regardless of N |

---

## 17. What the AI Trader now believes about XAUUSD

*Evidence-grounded practitioner synthesis, Q1+Q2 combined.*

**How it trends**: genuine multi-swing trends exist and are identifiable (M01), but every one
observed so far has ended, "usually without advance warning" — the Feb19+ Q1 uptrend's blow-off top
is the clearest example. A trend's *failure* looks like a pullback exceeding prior depth and taking
out the most recent swing point, not a single anomalous bar.

**How it transitions**: transitions are frequently first visible on a lower timeframe well before
the formal higher-timeframe context catches up — R08's entire Q2 arc (watched from 2020-06-08,
never confirmed, price still pushing higher through Q2's close) is a live, ongoing demonstration of
exactly this. A transition should never be called from a single bar, however violent.

**How it traps**: extremely common, even on record volume. The most extreme documented episode (a
5-bar, alternating-direction, 10,000+-volume whipsaw before trade #62) shows real volume does not
guarantee directional resolution. A defended level surviving repeated tests does not make the next
test more likely to hold — this was independently discovered and confirmed twice, in two different
quarters, against two different levels.

**How it behaves around structural levels**: multiply-defended levels can and do break, often
cleanly once they finally go (trade #62's own eventual stop-trigger, and the "1625 floor" both
broke decisively on their 4th real test). The *reaction in the first 1–2 bars* after a break —
immediate continuation vs. stall — is the single most reliable prospectively-observed discriminator
found in either quarter (TOC-003/TRADER_LESSON_021), though still only n=6 and unformalized.

**How confirmation behaves**: 2 consecutive real-volume closes is a real, recurring signal, but a
bare bar-count alone is insufficient during an active cross-timeframe conflict (the entire
motivation for Multi-Timeframe Trend Alignment V1). Close-based fill genuinely overshoots nominal
levels in both directions under fast/high-volume conditions — this is a structural property of the
market's own bar-close mechanics under real volatility, not a flaw in the execution rule.

**When momentum is trustworthy**: when a break is followed by immediate continuation without stall,
and when a "hold through target" decision is backed by a close-at-high on the trade's largest-volume
bar with no exhaustion signal (TRADER_LESSON_014, 3-for-3 across both directions).

**When a move is likely to fail**: stall/thin-volume follow-through immediately after a break;
countertrend entries against a still-active, persistent higher-timeframe trend without exceptional,
both-legs-clearing confirmation (5 straight countertrend losses before the first win).

**When NO_TRADE is preferable**: extreme multi-bar whipsaws with no clean same-direction pair; bare
pattern/bar-count triggers occurring during an active, unresolved cross-timeframe conflict.

**Which timeframes matter most**: H4 for context, but its formal label can go stale mid-quarter
without external correction — this is the single largest lesson of Q2 (§14). M15 is the primary
executable read. H1 is, on this evidence, the layer most likely to reveal staleness first.

**What makes a high-quality opportunity**: multi-timeframe agreement that has been *recently
re-verified*, not merely formally labeled; real/elevated volume at the trigger; genuine local
structural re-alignment rather than a bare pattern count; and, for countertrend entries
specifically, confirmation clearing a bar meaningfully higher than whatever has failed before it.

---

## 18. What the trader will watch in Q3

- **Observations needing more evidence**: TOC-003/TRADER_LESSON_021's stall-vs-continuation
  signature (n=6, and the two labels need reconciling); the reframed "recent momentum > nominal H4
  alignment" hypothesis (proposed, never re-tested); the "hold through target on no exhaustion"
  pattern (n=3, all favorable so far, needs a genuine counterexample test).
- **Playbooks needing more examples**: Playbook A-prime (n=3, currently net negative, needs many
  more resolved trades in both directions before any real read is possible); Playbook B (n=2 across
  the *entire* apprenticeship — a genuinely rare, high-bar setup).
- **Failure modes requiring attention**: the GAVE_BACK_MFE / no-partial-capture pattern (7 of 10
  fully-evidenced trades); trail-flip converting favorable unrealized into a realized loss (#59);
  reactive-breakeven-on-an-already-passed-level (TRADER_MISTAKE_004's exact shape, guard against
  recurrence under the new multi-target system's AFTER_TP1_STOP_RULE); technique-transfer drift
  when reapplying a validated pattern to a structurally different zone (TRADER_LESSON_017).
- **Regime questions remaining open**: does R08 ever formally confirm, or does the H4-BEARISH
  regime eventually reassert itself; does TOC-002's multi-bar-hold-unreliability finding generalize
  beyond extended-volatility regimes (untested across two full quarters now).
- **Management questions needing prospective evidence**: does the new TP Execution Buffer + Multi-
  Target System actually improve realized expectancy over the all-or-nothing single-TP pattern that
  cost #66 its near-full-TP excursion, without giving back the close-based discipline's other
  strengths; does moving to breakeven after a genuinely banked TP1 protect trades without
  prematurely stopping out still-valid theses.
- **What could become a strategy candidate**: Playbook A-prime, if it stabilizes net positive over
  a larger sample; the TOC-003/TRADER_LESSON_021 stall-vs-continuation signature, if formalized with
  explicit entry/stop/target/management/no-trade specification.

---

## 19. Q2 → Q3 learning transfer

**HIGH_CONFIDENCE_LESSONS**
- Close-based execution (never wick-based) works as designed, demonstrated repeatedly and
  symmetrically in both directions (trades #59, #60, #61, #62, #66's near-miss).
- A level surviving N defended tests does not predict an N+1th hold — independently confirmed twice,
  across two different quarters and two different levels.
- Post-trigger goalpost-moving (redefining a rule after it has already fired) is a real, named
  failure mode, formally guarded against since JUDGMENT_OVERRIDE_001.
- Reactive stop-adjustment must check whether the current bar has already passed the proposed new
  level before freezing it (TRADER_MISTAKE_004).

**MODERATE_CONFIDENCE_LESSONS**
- Trailing management, as practiced in Q2, underperformed static/hold baselines in a small but
  unanimous sample (3-for-3 negative) — direct basis for the fixed-SL/TP methodology.
- A `FULLY_ALIGNED`-at-entry tag can go stale mid-trade during an active, developing regime
  transition not yet reflected in the formal H4 label.
- Countertrend entries need a materially higher confirmation bar than with-trend entries during a
  persistent single-direction regime.
- Immediate continuation vs. stall in the 1–2 bars after a defended-level break is a real
  distinguishing signature (TOC-003/TRADER_LESSON_021), though still thin (n=6).

**LOW_CONFIDENCE_HYPOTHESES**
- "Trading against the most recent few hours of momentum is costly, regardless of nominal H4
  alignment" — proposed, never re-tested.
- Multi-target/partial-exit management will outperform the all-or-nothing single-TP pattern —
  plausible given the GAVE_BACK_MFE evidence, but zero trades have actually run under it.
- Breakeven should be withheld on very tight-initial-risk trades — inferred, not directly evidenced.

**REJECTED_IDEAS** — full list in §16 (7 distinct items: compression-vs-sweep reclaim durability;
"1625 durable floor"; the premature TOC-002-counterexample call; "widen the stop"; "clean trigger +
volume = reliable"; "with-trend inherently safer"; "N-time-defended level breaking = inherently more
reliable trigger" naive framing, later refined not simply discarded).

**UNRESOLVED_QUESTIONS**
- Does R08 BULLISH_TRANSITION ever formally confirm, or does H4-BEARISH reassert?
- Does TOC-002 generalize beyond extended-volatility regimes — untested across two full quarters.
- Are TOC-003 and TRADER_LESSON_021 the same underlying phenomenon? Never formally reconciled in
  any file this review accessed.
- What were trades #38, #40, and #50's exact resolutions? Not located within this review's research
  budget (flagged by the research agent as likely present in `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md`
  at specific unread line ranges) — a genuine open research task, not a data gap.
- Were trades #47/#49/#50's RESULT_R/points figures ever meant to be promoted into
  `TRADE_EVIDENCE_LOG.md`'s official structured backfill? Currently sitting in an unreconciled
  middle state (§20).

---

## 20. Honest limitations

```
TOTAL_APPRENTICESHIP_TRADES = 66
```
Only a subset carries structured, comparable evidence. This report does not pretend all 66 have
fields that were never frozen.

**RECOVERABLE**: all 17 officially structured-comparable trades' direction/RESULT_R/RESULT_pts; the
full FULL-tier narrative for trades #59–66; the complete `AI_TRADER_MARKET_READING_LIBRARY_V1.md`
14-module reference; the complete `REGIME_TRANSITION_WATCH.md` log; `EVIDENCE_GRADE_CLASSIFICATION.md`
in full; TOC-002/TOC-003 and the countertrend-LONG saga's overall shape and running tallies.

**PARTIALLY_RECOVERABLE**: trades #47, #49, #50's narrative and approximate result figures (found
in `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md`, never promoted into the official structured
backfill — a genuine reconciliation gap, not previously documented); trade #53's narrative (partial);
the precise line-by-line resolution of trades #38, #40 (located to within ~100-line ranges, not
individually confirmed within this review's research budget).

**NOT_RECOVERABLE_WITHOUT_HINDSIGHT**: MFE/MAE for all 7 officially-backfilled trades (#48, 51–56);
any entry-time narrative or context tags for trades #1–46 (excl. nothing new — the canonical
top-level log genuinely begins mid-trade-#59, so even #59's own entry narrative sits outside this
review's reach); the deeper causal "why" behind TOC-002 and TOC-003 beyond their descriptive pattern
shape (never stated in any file this review accessed, as distinct from simply not being searched
for).

**Research-budget note, stated once, for transparency**: this review deployed parallel research
agents against the largest source files (`AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md`, 16,010 lines;
`2020_Q2_H4_LOG.md`, 8,313 lines) using targeted search rather than exhaustive line-by-line reading
for the largest file. Both agents explicitly reported their exact coverage and flagged specific
unread ranges (documented above) rather than silently extrapolating — this review inherits and
preserves those honest coverage disclosures rather than smoothing them into false completeness.

---

## 21. Output

This document: `TRADER_Q2_FORENSIC_REVIEW_2020.md`. Linked from
`TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md` (added as a reference pointer; no raw historical evidence
in the checkpoint or any underlying governance file was overwritten to produce this report — this
is a synthesis document only).

### Concise executive summary for the CEO

```
TOP_5_Q2_LESSONS
1. Fully-aligned entry tags can go stale mid-trade -- H4 label lagged real H1 behavior for weeks.
2. Trailing management underperformed static/hold baselines 3-for-3 in the comparable sample.
3. Close-based execution (no wick triggers) works correctly and symmetrically, repeatedly proven.
4. A level surviving N defended tests never predicts an N+1th hold -- confirmed twice, two quarters.
5. Countertrend entries need a materially higher, never-lowered confirmation bar than with-trend.

TOP_5_Q2_FAILURE_MODES
1. No-partial-capture (fixed all-or-nothing TP) gave back MFE on 7/10 fully-evidenced trades.
2. Trail-flip converted a would-be win into a realized loss (#59).
3. Reactive breakeven set on a level the reacting bar had already passed (TRADER_MISTAKE_004).
4. Post-trigger goalpost-moving (redefining a rule after it fired) -- caught once, guarded since.
5. Silent reversion to an abandoned execution convention (#43/#44), surfaced only by CEO audit.

TOP_5_RECURRING_MARKET_BEHAVIORS
1. Multiply-defended levels can and do break, often decisively on the break.
2. Immediate continuation vs. stall in the first 1-2 post-break bars predicts outcome (n=6).
3. Extreme multi-bar whipsaws occur repeatedly even on record volume, with no clean resolution.
4. Regime transitions (R08) develop slowly on lower timeframes well before H4 confirms.
5. Real-volume 2-consecutive-close breaks are a genuine signal but insufficient alone during
   active cross-timeframe conflict.

BEST_OBSERVED_PLAYBOOK = Playbook B (Countertrend LONG, elevated bar) -- by the numbers only
  (50% WR, +1.098R avg), n=2, explicitly not promotable from this alone.
WORST_OBSERVED_PLAYBOOK = Playbook A-prime -- net negative in both R and points after 3 trades,
  the playbook installed specifically to fix Playbook A's problems.
MOST_PROMISING_DEVELOPING_PLAYBOOK = the countertrend-LONG escalating-evidence-bar mechanism
  (#47->#53->#63 arc) -- promising for its demonstrated learning process, not its thin sample.
BIGGEST_MANAGEMENT_PROBLEM = no partial-capture mechanism under fixed-SL/TP -- direct cause of
  the #66 near-full-TP-to-full-loss outcome and 6 similar cases.
BIGGEST_MARKET_READING_PROBLEM = over-weighting the formal H4 label without checking whether
  H1/M15 behavior had already begun diverging from it -- the FULLY_ALIGNED-underperformance finding.
RECOMMENDED_TP_ALLOCATION = KEEP_40_30_30, with AFTER_TP1_STOP_RULE=breakeven-once-banked and
  TP3=structural-trailing-not-fixed-cap as the substantive additions (see full §11).

Q3_TOP_PRIORITIES
1. Accumulate resolved Playbook A-prime trades (both directions) before any candidacy re-assessment.
2. Track STRUCTURAL_TARGET_REACHED vs EXECUTABLE_TARGET_REACHED under the new TP buffer -- do not
   recalibrate from fewer than several examples.
3. Reconcile TOC-003 / TRADER_LESSON_021 into one tracked observation.
4. Watch for R08's eventual resolution (confirm or reassert-BEARISH) -- the single largest open
   regime question carried from Q2.
5. Apply the AFTER_TP1_STOP_RULE / TP3-trailing recommendation as designed, honestly tracking
   whether it actually reduces the GAVE_BACK_MFE pattern rather than assuming it will.
```

---

## 22. Governance / Q3

No unseen Q3 market outcome was used anywhere in this review. Four Q3 bars (2020-07-01 00:00–01:00
UTC) were causally read before this mandate arrived and are retained, unerased, in `2020_Q3_H4_LOG.md`
— but their content was never referenced above to revise any Q2 conclusion. Zero Q3 trades have
been entered. This report and the TP management recommendation in §11 are now presented to the
CEO, per instruction, before any Q3 trade may be entered.

**STOP. Awaiting CEO review.**
