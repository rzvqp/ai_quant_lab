# AI_TRADER_MARKET_READING_LIBRARY_V1

- **CREATED**: 2026-08-25
- **STATUS**: ACTIVE
- **SCOPE**: A structured OBSERVATION / INTERPRETATION library for the AI Trader apprenticeship. This is
  NOT a strategy library, NOT a BUY/SELL voting engine, and NOT an Alpha signal integration. It does NOT
  retune Market Intelligence and is not wired into any decision path.
- **FITS INTO**: `docs/trader_apprenticeship/README.md`'s existing artifact set (ledger, checkpoints,
  observation candidates) as a fourth, reference-only artifact — the vocabulary the apprenticeship reads
  *with*, not a new lane, not a new handoff mechanism, not a replacement for anything already governed
  there.

---

## Governance (read first)

- **Alpha stays independent.** Nothing in this library imports an Alpha division conclusion as an AI
  Trader belief, and nothing here promotes a failed or unvalidated Alpha hypothesis into AI Trader's
  vocabulary. Where an Alpha-division finding is mentioned at all (M08), it is mentioned only as context
  for why a concept has no live implementation — never restated as AI Trader's own conclusion.
- **S5, StrategyCatalog, and live execution are untouched and out of scope.** This library does not
  modify, extend, or reference the internals of `s5_opening_range_breakout.py`, its MT5 demo runtime, or
  any StrategyCatalog/live-execution code path. Where S5 or a StrategyCatalog entry is the only existing
  runtime evidence for a module (M03's breakout detector, M02's placeholder catalog entry), that is noted
  as a *fact about what exists*, never as something this library calls, extends, or trades against.
- **This is downstream documentation only.** It is not imported by any runtime module and does not alter
  Market Intelligence, `ve_brain` routing, or any live signal path. Writing this file changes nothing
  about what the running system does.
- **Nothing here is a validated edge.** AI Trader may LEARN observations from this library the same way
  it learns anything else in the apprenticeship. Any frozen observation candidate this later produces
  still requires an independent Alpha audit before being treated as an edge — the same rule
  `observation_candidates/TOC-001.md` already lives under (`STATUS: UNVALIDATED_TRADER_OBSERVATION`).
  This library does not shortcut that gate for anything it helps produce.
- **Read-only, forward-only integration.** This library becomes available to the apprenticeship starting
  now. It does NOT retroactively apply to anything already recorded in
  `lane_a_historical/2020_Q1_H4_LOG.md` — no prior entry, reading, or interpretation in that log is
  rewritten, reinterpreted, or reframed by this document. Knowledge from this library is available only
  to observations made from this integration point forward.

---

## How to use this library

Do **not** mechanically evaluate all 14 modules against every M15 candle. At true M15 density a full
14-module pass per bar would collapse replay throughput for no corresponding gain in learning quality —
most ordinary bars are, honestly, just drift or chop with nothing structurally new to read.

Instead, read with **attention-based** discipline: most bars get the same compact market-state update the
walk already uses (price, volatility texture, WATCH/no-entry, one-line reading). Only when something
*materially develops* does a bar earn a stop to consult the relevant module's lens. Concretely:

- Compression appears → consult **M06** (is this genuine tightening, or just a quiet stretch?).
- An important prior high/low is attacked → consult **M05** (probe, sweep, or genuine break developing?).
- A break occurs → consult **M03** (is this accepted or does it look like a probe?).
- Market behavior changes character (trend → chop, chop → impulse) → consult **M10**.
- A fair value gap appears after a displacement move → consult **M13**, purely as context — never as a
  trigger (per M13's own observation-only design, below).
- Price stalls for several bars at exactly the same level repeatedly tested before → consult **M05** or
  **M14** (is this level actually being defended, or is that just recency bias?).
- A scheduled session opens, or the walk enters a window already known from SF-3 to be historically
  low-opportunity → consult **M07** before reading anything else into the quiet.
- H4, H1, and M15 stop agreeing on direction at the same moment → consult **M09** (cross-scale conflict is
  itself the signal to slow down, not to pick a side).

The goal of this library is to increase the **QUALITY** of attention, not the **QUANTITY** of narration.
A module lens is a tool to reach for when something changed — not a checklist to run every bar.

---

## The 14 modules

### M01 — Trend

**RUNTIME_STATUS**: RUNTIME-BACKED (YES). Live in `ve_brain/regime_routing.py` (external installed
package) via `ai_trader/new_brain_bridge/raw_axes_builder.py`; also computed in
`ai_trader/market_scanner/features.py` (`h1_trend_up`/`h4_trend_up`/`d1_trend_up`); a dormant, unused copy
also exists in `ai_trader/market_intelligence/trend.py`.

1. **WHAT IT MEANS**: A trend is a sustained directional bias where price makes a series of higher
   structural points (uptrend) or lower structural points (downtrend) over a timeframe-appropriate
   window, rather than oscillating around a fixed center. It describes *what already happened*, not a
   prediction of continuation.
2. **WHAT TO OBSERVE**:
   - A sequence of higher highs/higher lows (or lower lows/lower highs) across multiple structural swings.
   - Pullbacks that stay shallow relative to the prior impulse, rather than fully round-tripping it.
   - Volume/participation that doesn't collapse on each new impulse leg.
3. **WHAT IT DOES NOT MEAN**:
   - A trend is not a guarantee of continuation — every trend ends, usually without advance warning.
   - A single strong impulsive bar is not by itself a trend; it can be a spike, a liquidation event, or a
     probe (see M11, M06).
   - "Trending on H4" does not mean every lower timeframe is also trending at the same moment (see M09).
4. **FORMING STATE**: Two or three structural swings in the same direction, each pullback still shallow;
   not yet enough history to call it more than "a directional stretch."
5. **CONFIRMED STATE**: Multiple consecutive higher-high/higher-low (or inverse) swings, spanning enough
   time and range that a single pullback wouldn't erase the structure, with the move accepted (not
   immediately reversed) at each new extreme.
6. **FAILURE / INVALIDATION**: A pullback that exceeds the depth of prior pullbacks and takes out the
   most recent higher low (or lower high); a sustained multi-bar move against the prior direction that
   doesn't get reclaimed.
7. **RELATION TO H4 / H1 / M15 / M5**: H4/D1 is the natural home for identifying that a trend exists at
   all — it is a structural, multi-swing concept and gets noisy at very short horizons. H1/M15 refine
   *where inside* an established H4 trend price currently sits. M5 is not a natural home for trend
   identification on its own; at M5 resolution what looks like "trend" is usually a leg of a higher
   timeframe's structure, not an independent trend to be read in isolation.
8. **RELATION TO OTHER MODULES**: Trend + Pullback (M02) — is the current retracement shallow enough to
   stay inside the trend, or deep enough to question it? Trend + Volatility (M06) — is a trend leg
   expanding (real participation) or just drifting? Trend + Transition (M10) — the most important trend
   question is usually "has this stopped being true," which is M10's job to flag. Trend + Cross-scale
   (M09) — does the H1/M15 read agree with the H4 trend, or are they in conflict?
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): the Feb19+ 2020 uptrend is the clearest trend episode logged so far —
     `lane_a_historical/2020_Q1_H4_LOG.md` records it extending from roughly the 1590 level (Feb19) to
     roughly 1686 (Feb24), described in the log as "the longest, largest single move of the entire pilot
     by far," with the ledger separately noting it reached a "blow-off top (~1689 high)" before reversing
     on 2/24. Both are genuine walk observations, not fabricated for this document.
   - VALIDATED EDGE (none claimed): no claim is made that this trend, or trend structure generally, was
     tradeable or profitable — only that it was observed and logged as WATCH throughout, per the mandate's
     discipline.
10. **APPRENTICESHIP QUESTIONS**: Is price still making higher highs and higher lows, or has that pattern
    stopped? How deep was the last pullback compared to the ones before it? Would the most recent
    structural point being taken out change the read? Does the H1/M15 picture agree with what H4 is
    showing? What would the first honest sign of exhaustion look like here? Am I calling this a trend
    because of real structure, or because the last few bars moved in one direction?

---

### M02 — Pullback

**RUNTIME_STATUS**: PARTIAL. `ve_brain`'s catalog carries a "trend_pullback" entry, but its rule fields
are literal placeholder strings, not real pullback-depth logic. `ai_trader/strategy_runtime/families/
s07_*.py` and `s38_*.py` implement pullback-family logic but are batch-only, not reachable from the live
path.

1. **WHAT IT MEANS**: A pullback is a temporary, shallower counter-move against a prevailing trend, after
   which price resumes the original direction. It is defined by *not* invalidating the trend it interrupts.
2. **WHAT TO OBSERVE**:
   - A retracement against the trend that stays shallower than the impulse that preceded it.
   - The retracement stalling or reversing near a prior structural point (prior swing low in an uptrend,
     for example), rather than accelerating through it.
   - Reduced participation/volume on the pullback itself relative to the trend impulse.
3. **WHAT IT DOES NOT MEAN**:
   - Not every counter-move is a pullback — a deep enough retracement is evidence the trend itself may be
     ending (see M01 failure, M10).
   - A pullback is not defined by time (how long it lasts) but by depth and structure; a long, shallow
     pullback and a short, deep one are read very differently.
   - A pullback "holding" once does not guarantee it holds on a second test.
4. **FORMING STATE**: Price has turned against the trend direction for one or more bars; not yet clear
   whether this stays shallow or becomes something deeper.
5. **CONFIRMED STATE**: The retracement stalls or reverses while still shallower than the preceding
   impulse, and price resumes in the original trend direction with real follow-through.
6. **FAILURE / INVALIDATION**: The retracement exceeds the depth of the prior impulse, or takes out the
   trend's most recent defining structural point — at that point it should be read as a possible trend
   failure (M01) or transition (M10), not a pullback.
7. **RELATION TO H4 / H1 / M15 / M5**: H4/H1 typically defines the trend a pullback is measured against;
   M15 is the natural home for watching a pullback actually develop and resolve bar by bar; M5 can refine
   exactly where a pullback stalls, but only in the context of an M15/H1-defined trend — M5 alone cannot
   establish that a pullback (versus a new trend) is even the right frame.
8. **RELATION TO OTHER MODULES**: Pullback + Trend (M01) — the core pairing; a pullback is only meaningful
   relative to an established trend. Pullback + Liquidity (M05) — does the pullback stall exactly at a
   prior swing point or session extreme, or blow through it? Pullback + Volatility (M06) — a low-volume,
   orderly pullback reads differently from a high-volume, violent one.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): no walk entry in `2020_Q1_H4_LOG.md` is explicitly framed and logged as
     a "pullback" episode as such; the log's own vocabulary so far leans on "reclaim," "consolidation," and
     "give-back" for similar behavior (e.g. the Feb13-14 compression-and-edge-up sequence). Rather than
     force-fit one of those into a pullback label retroactively, this module is being introduced without a
     confirmed walk example — the honest state is that no on-topic example exists yet.
   - VALIDATED EDGE (none claimed): none.
10. **APPRENTICESHIP QUESTIONS**: Is this retracement shallower than the move that came before it? Where
    is it stalling, if it's stalling at all? Has the trend's last defining structural point been touched or
    broken? Is participation on this counter-move lighter than on the trend itself? Would a second, deeper
    test of the same low change my read?

---

### M03 — Breakout

**RUNTIME_STATUS**: RUNTIME-BACKED (YES) via S5 (`ai_trader/new_brain_live/strategy_platform/
s5_opening_range_breakout.py`) — S5 itself is FROZEN and is cited here only as a fact about what exists in
the codebase, never as something this library references, extends, or draws logic from. Separately, and
independently of S5, a real BOS (break-of-structure) detector (vendored `market_structure.py`) genuinely
feeds the live `BREAKOUT_TRANSITION` regime axis.

1. **WHAT IT MEANS**: A breakout is price moving decisively beyond a previously respected boundary (a
   range edge, a prior high/low, a well-tested level) rather than reversing at it as it has before.
2. **WHAT TO OBSERVE**:
   - Price closes beyond the prior boundary, not just wicks through it.
   - Follow-through on subsequent bars in the same direction, rather than an immediate round-trip.
   - Volume or range expansion accompanying the move through the level.
3. **WHAT IT DOES NOT MEAN**:
   - A single bar closing beyond a level is not proof of a genuine breakout — see M03's own failure mode
     below and TOC-001's entire finding.
   - A breakout is not the same as acceptance; price can trade beyond a level and still fail to hold it.
   - High volume on the breakout bar does not by itself guarantee follow-through (compare the walk's 2/25
     and 2/28 spikes, which did not hold, against 3/2, which did).
4. **FORMING STATE**: Price is testing or has just closed beyond a prior boundary; not yet known whether
   subsequent bars extend the move or fade it.
5. **CONFIRMED STATE**: Multiple bars past the level without a full round-trip back through it, ideally
   with the level itself later acting as support/resistance rather than a magnet for reversal.
6. **FAILURE / INVALIDATION**: Price gives back the new extension and closes back inside the prior
   boundary within a small number of bars — this is a rejection, not a breakout, and is the exact pattern
   `observation_candidates/TOC-001.md` describes for XAUUSD's Jan-Feb 2020 range.
7. **RELATION TO H4 / H1 / M15 / M5**: H4 typically defines the boundary being broken (a range edge, a
   multi-week high/low); M15 is where the break itself and its immediate follow-through are best watched
   bar by bar; M5 is the natural home for refining entry timing around an already-confirmed break, not for
   deciding whether the break is real in the first place.
8. **RELATION TO OTHER MODULES**: Breakout + Acceptance/Volatility (M06) — is the break happening on
   expanding participation or a thin, low-conviction poke? Breakout + Liquidity (M05) — is this a break of
   a level with real resting interest behind it (sweep-then-break) or an isolated print? Breakout +
   Transition (M10) — a confirmed breakout is often the clearest evidence a regime transition is underway.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): `observation_candidates/TOC-001.md` is real, governed project evidence
     directly on-topic for this module — its `FROZEN_OBSERVATION_DEFINITION` is literally "a fresh extreme
     is not held," logged from four confirming instances in the Jan-Feb 2020 range. Its own
     `COUNTEREXAMPLE_TIMESTAMPS` field records a breakout beginning at bar close 1582038900 that held for
     44 consecutive M15 candles without reverting — a real disconfirming instance in the same document.
     Separately, `2020_Q1_H4_LOG.md`'s 2020-03-02 entry (record-volume candle 1583247600) is logged as
     "acceptance rather than rejection of a fresh extreme," explicitly flagged there as "the opposite of
     what TOC-001 would predict."
   - VALIDATED EDGE (none claimed): TOC-001 remains `UNVALIDATED_TRADER_OBSERVATION`; the 3/2 event is
     logged only as a candidate counterexample-class event for the Q1 checkpoint, not as evidence for or
     against any tradeable edge.
10. **APPRENTICESHIP QUESTIONS**: Did price close beyond the level, or only wick through it? Is the next
    bar extending the move or immediately giving it back? Is this level being broken with expanding
    participation or on thin volume? Have I seen this exact level tested and rejected before — does that
    raise or lower my confidence this time? What would prove this break was real rather than a probe?

---

### M04 — Range

**RUNTIME_STATUS**: PARTIAL / blocked-by-design. `RANGE_STRATEGY_ROUTING="DISABLED"` in `ve_brain` is a
deliberate, permanent CEO fail-closed decision, not a bug or an oversight. No live range detector exists,
on purpose.

1. **WHAT IT MEANS**: A range is a period where price oscillates between a relatively stable upper and
   lower boundary without establishing a new sustained directional trend — the opposite structural state
   from a trend (M01).
2. **WHAT TO OBSERVE**:
   - Repeated tests of a similar high and a similar low over multiple swings, without a durable break of
     either.
   - Momentum/impulse fading as price approaches either boundary.
   - Multiple failed breakout attempts at the same edges (directly related to M03's failure mode).
3. **WHAT IT DOES NOT MEAN**:
   - A range does not mean price cannot move — a wide, violent range (see the walk's post-2/24 1625-1660
     episode) can have large intra-range swings without ever being a trend.
   - Two touches of similar highs/lows is not yet enough to call a range; it can be coincidence or the
     start of a trend's early consolidation.
   - A range holding through several tests does not guarantee it holds on the next one (the walk's 1625
     floor held three times, then broke on the fourth).
4. **FORMING STATE**: Price has reversed at a similar level twice from two different directions, but the
   boundaries aren't yet well-established or repeatedly tested.
5. **CONFIRMED STATE**: Multiple (three or more) tests of both the upper and lower boundary, each followed
   by a reversal back toward the range's interior, with no sustained close beyond either edge.
6. **FAILURE / INVALIDATION**: A close beyond either boundary that holds for multiple bars without
   reverting — at that point the frame shifts to M03 (breakout) or M10 (transition), not range.
7. **RELATION TO H4 / H1 / M15 / M5**: H4 is the natural home for identifying that a range exists at all,
   since its boundaries are usually multi-day/multi-week structures; M15 is useful for watching how price
   behaves *inside* an H4-defined range (drift vs. edge tests); M5 is not a natural home for establishing
   range boundaries — at that resolution, apparent "ranges" are usually just noise inside a single M15 bar.
8. **RELATION TO OTHER MODULES**: Range + Liquidity (M05) — range edges are exactly where resting
   liquidity tends to accumulate, making sweep/reclaim behavior (M05) the natural companion read. Range +
   Breakout (M03) — every range eventually resolves into a breakout or a deeper range; the two modules
   describe the same structure from before/after the resolution. Range + Volatility (M06) — compression
   inside a range (M06) is often the tell that a resolution is approaching.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): `observation_candidates/TOC-001.md`'s `MARKET_CONTEXT` field explicitly
     names the Jan 1 – Feb 19, 2020 XAUUSD regime as "range-bound... roughly 1517-1593 since a Jan 1-2
     breakout" — real, governed project evidence of a multi-week range being read and logged as such.
   - VALIDATED EDGE (none claimed): TOC-001's fade-the-extreme behavior inside that range remains
     `UNVALIDATED_TRADER_OBSERVATION`; no claim is made that ranges are tradeable structures.
10. **APPRENTICESHIP QUESTIONS**: How many distinct times has each boundary actually been tested? Is
    momentum fading as price nears an edge, or accelerating through it? Would I call this a range, or am I
    imposing a range frame on what's really just two coincidental touches? Is the range widening,
    narrowing, or stable over successive tests? What would the first real breakout out of this range look
    like, versus another failed probe?

---

### M05 — Liquidity

**RUNTIME_STATUS**: PARTIAL / blocked. A real pool/sweep detector (`liquidity_mechanics.py`) exists but is
blocked pending an unresolved day/week-boundary derivation issue. Only a volume-thinness proxy is
live-adjacent (`ai_trader/market_intelligence/liquidity.py`, part of a dormant chain). This module is
built here as pure observation vocabulary — pools, prior highs/lows, equal highs/lows, session extremes,
sweep, failed sweep, reclaim, displacement away, acceptance beyond liquidity, repeated probing — without
activating or referencing the blocked detector logic in any way.

1. **WHAT IT MEANS**: Liquidity, in the observational sense used here, refers to price levels where
   resting orders are likely to have accumulated (prior highs/lows, equal highs/lows, session extremes)
   and the characteristic ways price interacts with those levels — probing them, sweeping through them
   briefly, or accepting beyond them.
2. **WHAT TO OBSERVE**:
   - Equal or near-equal highs/lows across multiple swings (a level tested more than once at almost the
     same price).
   - A brief spike through such a level followed by a fast reversal back inside (a sweep).
   - A level that, once swept, is then reclaimed and traded back through in the opposite direction.
   - Repeated probing of the same level without a clean resolution either way.
3. **WHAT IT DOES NOT MEAN**:
   - A sweep is not automatically bullish or bearish just because it happened — the reversal afterward has
     to actually materialize and hold.
   - Equal highs/lows are not proof of "stops sitting there" — this is an observational pattern, not a
     verified mechanism (no live detector exists to confirm order placement).
   - A level being defended once, or even several times, does not guarantee it holds the next time (see
     M04's own caution and the walk's 1625-floor example below).
4. **FORMING STATE**: Price approaches a prior high/low or equal-level cluster; not yet clear whether it
   will sweep through, stall short, or accept beyond it.
5. **CONFIRMED STATE**: A clean sweep-and-reverse (brief excursion beyond the level, fast reclaim, real
   follow-through the other way) or, on the opposite side, clean acceptance beyond the level with no
   immediate reversion.
6. **FAILURE / INVALIDATION**: What looked like a sweep instead becomes sustained acceptance beyond the
   level (the "reversal" never comes), or a level defended multiple times finally breaks cleanly with real
   follow-through.
7. **RELATION TO H4 / H1 / M15 / M5**: H4/H1 typically defines which prior highs/lows are structurally
   significant enough to matter; M15 is the natural home for watching a sweep or probe actually develop
   bar by bar; M5 is where entry refinement around a confirmed reclaim would happen, but M5 alone cannot
   establish that a level is significant in the first place.
8. **RELATION TO OTHER MODULES**: Liquidity + Range (M04) — range edges are natural liquidity locations.
   Sweep + Reclaim is itself the core liquidity pairing (probe beyond a level, then a decisive move back
   through it). Liquidity + Breakout (M03) — is a break of a level a genuine breakout, or a sweep that's
   about to reclaim? Liquidity + Order Block (M14) — a swept level and a nearby order block are often
   discussed together in practitioner vocabulary, though neither is machine-confirmed against the other
   here.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): the ~1625 floor in late February 2020 is real, logged, on-topic
     evidence — `2020_Q1_H4_LOG.md` records three distinct tests of the same zone (2/25 spike low
     1625.017, a 2/25-2/26 double-test at 1625.263/1626.862, and a 2/27-2/28 third test at
     1626.799/1626.994), each followed by a real multi-bar bounce, before a fourth test finally broke
     cleanly through to a fresh low (1621.292). This is repeated-probing/level-defense behavior in the
     sense this module describes, observed and logged honestly including its eventual failure — it was
     never machine-tagged as a "liquidity pool" by any detector, since none is live.
   - VALIDATED EDGE (none claimed): no claim is made that defended levels are tradeable; the walk's own
     entry treats the level's eventual break as a lesson that "a level holding 3 times does not by itself
     predict it holds a 4th," not as a confirmed pattern.
10. **APPRENTICESHIP QUESTIONS**: Is this a genuine equal-high/low cluster, or am I pattern-matching two
    unrelated touches? Did price sweep through and reverse fast, or is it accepting beyond the level? Who
    looks trapped right now — those who bought/sold the level, or those who faded the probe? How many
    times has this exact zone already been tested, and does that raise or lower my confidence in it
    holding again? What would prove this was never a real liquidity level at all?

---

### M06 — Volatility

**RUNTIME_STATUS**: RUNTIME-BACKED (YES). Compression/expansion axes (vendored `market_state.py`)
genuinely live-gate `ve_brain`'s regime routing via `is_compressed`/`is_displacement`.

1. **WHAT IT MEANS**: Volatility describes how much price is moving relative to its recent own history —
   compressing into a tighter range, or expanding/displacing into a wider one. It is a texture of price
   action, not a direction.
2. **WHAT TO OBSERVE**:
   - A stretch of bars with meaningfully narrower ranges than the recent average (compression).
   - A sudden, large single-bar or multi-bar range/volume expansion relative to the recent average.
   - How long an expansion sustains versus how quickly it normalizes back to prior levels.
3. **WHAT IT DOES NOT MEAN**:
   - Compression does not predict direction, only that a resolution (in either direction) may be more
     likely — the mandate's own framing is "mature compression → elevated expansion probability," not
     "compression → up" or "compression → down."
   - A volatility spike is not automatically a trend start or a reversal — it can be a single-bar event
     that fully normalizes within a few bars.
   - High volume does not always mean high volatility, and vice versa — they should be read together, not
     assumed to move in lockstep.
4. **FORMING STATE**: Range/volume is visibly narrowing (or widening) relative to the recent stretch, but
   not yet extreme enough to call it a clear compression or expansion regime.
5. **CONFIRMED STATE**: A clearly, persistently tighter (or wider) multi-bar range than the walk's own
   recent baseline, ideally with volume confirming the same read.
6. **FAILURE / INVALIDATION**: An apparent compression that never resolves into anything (just stays quiet
   indefinitely, no information gained); an apparent expansion spike that fully normalizes within one or
   two bars with no lasting effect on structure.
7. **RELATION TO H4 / H1 / M15 / M5**: H4 is useful for spotting multi-day compression/expansion regimes;
   M15 is the natural home for watching a compression phase tighten or an expansion spike unfold bar by
   bar; M5 can sharpen the exact bar a displacement starts, but the broader compression/expansion *regime*
   is best read at H4/M15, not assembled from M5 alone.
8. **RELATION TO OTHER MODULES**: Compression + Breakout (M03) — the walk's own most direct pairing:
   compression tightening, then resolving into a directional move. Volatility + Hazard (M11) — a violent,
   unexplained spike is exactly where the hazard lens (news/liquidation risk) belongs. Volatility + Session
   (M07) — some sessions are structurally quieter or louder than others, independent of any single event.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): `2020_Q1_H4_LOG.md` logs a genuine multi-candle compression phase around
     2020-02-12 to 02-14 ("volatility has been compressing over the last ~10 candles... a genuine, real
     compression phase forming"), which tightened further before "edging up out of it" toward 1583 — read
     explicitly against the mandate's own compression-to-expansion framing. Separately, the ledger logs
     several real expansion spikes at record volume: the 2/25 single-candle ~21-point move (volume 4316,
     then-record), the 2/28 liquidation crash (volume 8946, roughly double the prior record, during the
     documented COVID-19 panic window), and the 3/2 record-volume breakout (volume 9475).
   - VALIDATED EDGE (none claimed): none of these episodes are claimed as tradeable; several are logged
     explicitly as WATCH-only, with the 2/28 event specifically flagged as a different mechanism
     (liquidation) from the walk's probe-and-reject pattern and not to be conflated with it.
10. **APPRENTICESHIP QUESTIONS**: Is the range genuinely tightening over several bars, or is this one quiet
    bar in an otherwise normal stretch? Is this expansion sustaining into follow-through, or already
    normalizing back down? Is this move accompanied by proportional volume, or is range moving without
    volume (or the reverse)? Have I seen a compression phase like this resolve before, and how did it
    resolve? Is this volatility expanding, or only spiking?

---

### M07 — Session

**RUNTIME_STATUS**: RUNTIME-BACKED (YES). A real `SessionEngine` (`ai_trader/market_scanner/session.py`)
is live. S5's session window is load-bearing for S5's own (frozen) logic — cited here only as a fact that
session boundaries are real, load-bearing runtime concepts in this codebase; S5's trading logic itself is
not referenced further.

1. **WHAT IT MEANS**: A trading session is a recurring time-of-day window (Asia, London, New York, and
   their overlaps) with characteristic participation and volatility patterns that repeat across different
   trading days.
2. **WHAT TO OBSERVE**:
   - Which named session window the current bar falls in, in UTC.
   - Whether current volatility/volume is typical for that session, or unusually high/low for it.
   - Behavior right at session opens/closes and overlaps, where participation often shifts abruptly.
3. **WHAT IT DOES NOT MEAN**:
   - A session being historically "low-opportunity" does not mean nothing important can happen in it — it
     means the base rate of structural development is lower, not zero.
   - Session identity alone does not determine direction; it conditions *how much* is likely to happen,
     not *which way*.
   - A quiet session is not itself evidence of an upcoming breakout — quiet can just mean quiet.
4. **FORMING STATE**: N/A in the usual sense — a session is a clock-defined window, not a developing
   structure. The relevant "forming" question is whether the session's *behavior* (quiet vs. active) is
   still matching its historical pattern as it unfolds.
5. **CONFIRMED STATE**: The session's observed behavior (quiet drift, or active development) matches what
   would be expected for that named window, based on prior observation within the walk.
6. **FAILURE / INVALIDATION**: A session behaves meaningfully differently than its historical pattern would
   suggest (an unusually active print inside a normally quiet window, or vice versa) — worth noting rather
   than dismissing, since it may indicate a broader regime or event overriding the normal session texture.
7. **RELATION TO H4 / H1 / M15 / M5**: Session is inherently a shorter-horizon lens — M15 is its natural
   home for reading real-time session texture, with M5 useful for refining exactly where inside a session
   a resolving move develops. H4/D1 are not the natural home for this module; session identity mostly
   washes out at that resolution.
8. **RELATION TO OTHER MODULES**: Session + Volatility (M06) — is the current bar's volatility normal or
   abnormal for its session? Session + Hazard (M11) — an unscheduled, session-inconsistent spike is a
   candidate for the hazard lens. Session + Cross-scale (M09) — a quiet session on M15 can still sit inside
   an active H4 trend; the two reads are not in conflict.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): `2020_Q1_H4_LOG.md` cites SF-3 by name at least twice as real, logged
     session-texture context — once for a genuine round-trip/consolidation M15 session ("matches SF-3's
     own finding from the closed session-timing frontier: this UTC window sits in a historically
     lower-opportunity phase") and again for a very quiet overnight stretch ("matches SF-3's own finding —
     this is the pre-London/Asian-late session, historically the lowest-opportunity window"). Both citations
     used SF-3 correctly as read-only context for interpreting quiet, not as a signal.
   - VALIDATED EDGE (none claimed): SF-3 itself is a bounded information asset (see the Information Assets
     section below), not a tradeable signal, and is not claimed as one here.
10. **APPRENTICESHIP QUESTIONS**: What named session window is this bar in? Is the current level of activity
    typical or atypical for this window? Am I about to misread ordinary session quiet as a lack of
    structure, or genuine quiet as something more meaningful? Is this near a session open/close/overlap
    where behavior often shifts? Would this same price action look different in a different session?

---

### M08 — Auction

`CONCEPTUAL_OBSERVATION_ONLY — no governed implementation exists.`

**RUNTIME_STATUS**: Zero implementation anywhere in AI Trader or `ve_brain`. Only a VWAP±σ proxy exists,
and only in the separate Alpha division's own research, where it was found bounded-negative in Alpha's own
work — that finding belongs to Alpha, is not restated here as an AI Trader conclusion, and is noted only to
explain why this concept has no live footing in this codebase. Real point-of-control/value-area logic would
require volume-profile data AI Trader does not currently have access to.

1. **WHAT IT MEANS**: The auction framework reads price as a continuous two-sided negotiation between
   buyers and sellers, organized around where the most trading actually occurred (value/point of control)
   versus where price merely passed through with little acceptance.
2. **WHAT TO OBSERVE**:
   - Where price spends the most time/volume over a session (would-be value area) versus where it barely
     touches and moves on.
   - Price returning repeatedly to a prior area of heavy trading (value) versus rejecting away from it.
   - Single-print or thin areas (would-be low-volume nodes) that price moves through quickly.
3. **WHAT IT DOES NOT MEAN**:
   - Auction concepts are not the same as simple support/resistance — value is about *where trading
     concentrated*, not just where price reversed.
   - A price level being visited often is not the same as a level being "accepted" in the auction sense
     without genuine volume-at-price data to confirm it.
   - This module should not be treated as equivalent to M05 (liquidity) — liquidity concerns resting
     orders at extremes; auction concerns where trade actually occurred throughout a session.
4. **FORMING STATE**: N/A in a machine-verifiable sense here — without volume-profile data, "forming"
   auction structure can only be estimated visually from price dwell time, which is a much weaker
   observation than a real volume-at-price read.
5. **CONFIRMED STATE**: N/A — no governed data source exists in this codebase to confirm a value area or
   point of control with any rigor.
6. **FAILURE / INVALIDATION**: N/A for the same reason — without a real detector, there is no defensible
   basis to call an auction read "invalidated" versus simply "never confirmed in the first place."
7. **RELATION TO H4 / H1 / M15 / M5**: In principle, auction concepts are typically read intraday (M15/M5)
   against a single session's volume profile; H4/D1 is not this module's natural home. In practice, none
   of this can currently be observed with real data at any timeframe in this codebase.
8. **RELATION TO OTHER MODULES**: Auction + Session (M07) — auction structure is normally read per session,
   making the two closely linked in principle. Auction + Range (M04) — a well-developed value area often
   resembles a range in shape, though the two concepts are not identical. Auction + Volatility (M06) — thin,
   low-volume-node areas are natural places for fast expansion moves.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): none. No walk entry in `2020_Q1_H4_LOG.md` reads price in auction/value
     terms, and no real data exists in this codebase to support doing so credibly. Stated honestly rather
     than inventing an example.
   - VALIDATED EDGE (none claimed): none.
10. **APPRENTICESHIP QUESTIONS**: If I had real volume-at-price data here, where would I guess value
    concentrated? Is price spending time at this level or just passing through it? Am I substituting a
    support/resistance read for an auction read because I don't actually have volume-profile data? What
    would I need to see to trust an auction-style read at all in this codebase? Is this level being
    revisited because of value, or for reasons this module can't actually distinguish yet?

---

### M09 — Cross-scale

**RUNTIME_STATUS**: PARTIAL. `mtf.py`/`agreement.py` exist in the dormant orchestrator chain; the live
chain's actual N2-N4 "tower" cross-scale logic runs in an opaque subprocess that isn't independently
readable from this codebase. Separately — and this is a genuine strength worth stating plainly — the
apprenticeship's own manual H4→H1→M15→M5 top-down hierarchy, mandated by the CEO and actively used
throughout the walk, is itself a real, working practice of this exact module, even though the automated
runtime version is unverified.

1. **WHAT IT MEANS**: Cross-scale reading means deliberately checking whether the structural picture at
   one timeframe agrees with, contradicts, or simply doesn't yet resolve the picture at another — using
   higher timeframes for context, and lower timeframes for detail, without letting either overrule the
   other blindly.
2. **WHAT TO OBSERVE**:
   - Whether H4 trend/range context and M15 price action are pointing the same direction or in conflict.
   - Whether a break that looks significant on M15 is actually still inside H4 noise.
   - Whether H1 provides a genuinely different read from what H4 alone would suggest.
3. **WHAT IT DOES NOT MEAN**:
   - Agreement across timeframes is not proof of anything by itself — timeframes can coincidentally align.
   - A lower timeframe "confirming" a higher timeframe read does not make the higher timeframe read more
     statistically valid — it is still the same underlying market, viewed at different resolutions.
   - Disagreement between timeframes is not automatically resolved in favor of the higher one; sometimes
     the lower timeframe is showing the first real evidence the higher-timeframe read is becoming stale.
4. **FORMING STATE**: The picture at one timeframe has just started to diverge from another (e.g., M15
   makes a new local high while H4 context is still "range-bound"); not yet clear whether this resolves
   into agreement or genuine conflict.
5. **CONFIRMED STATE**: Multiple timeframes give a consistent, mutually reinforcing read (H4 context, H1
   structure, M15 development all pointing the same way), or a clearly identified, named conflict between
   them worth tracking explicitly rather than silently picking one.
6. **FAILURE / INVALIDATION**: What looked like cross-scale agreement turns out to have been coincidental
   — the higher-timeframe context changes and the lower-timeframe read that seemed to confirm it no longer
   makes sense in the new context.
7. **RELATION TO H4 / H1 / M15 / M5**: This module is defined *by* the relationship between all four —
   there is no single natural home. H4 typically supplies context, H1 supplies intermediate structure, M15
   supplies setup development, and M5 supplies entry refinement; the module's whole point is checking that
   this chain is actually consistent rather than assuming it.
8. **RELATION TO OTHER MODULES**: Cross-scale conflict is the connective tissue for nearly every other
   module — Trend (M01) agreement/disagreement across timeframes, Transition (M10) showing up first on a
   lower timeframe before the higher one catches up, Range (M04) on H4 while M15 shows a directional
   push inside it. It is best treated as a lens applied *to* another module's read, not a standalone
   observation.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): the apprenticeship's own methodology is the real example here.
     `2020_Q1_H4_LOG.md`'s "METHODOLOGY SHIFT" entry (M15 becomes the sole replay clock) explicitly
     describes carrying H4 context forward unchanged ("H4 context carries forward unchanged... rather than
     being re-derived") while walking M15 in full detail — a genuine, working practice of checking M15
     development against a held H4 frame, exactly this module's core idea, done manually rather than by any
     automated tower.
   - VALIDATED EDGE (none claimed): the automated N2-N4 cross-scale logic in `ve_brain`'s live chain is
     explicitly unverified from this codebase and is not claimed as working; only the apprenticeship's own
     manual practice is cited as a genuine, observed strength.
10. **APPRENTICESHIP QUESTIONS**: Does what I'm seeing on M15 actually agree with the H4 context I'm
    carrying forward, or have I stopped checking? If H1 and M15 disagree right now, which one has more
    recent, more relevant information? Is this M15 development big enough to matter at H4 scale, or still
    inside H4 noise? Am I updating my higher-timeframe read when lower-timeframe evidence genuinely
    warrants it, or clinging to a stale frame?

---

### M10 — Transition

**RUNTIME_STATUS**: RUNTIME-BACKED (YES). `BREAKOUT_TRANSITION` is a real, live regime axis in `ve_brain`.

1. **WHAT IT MEANS**: A transition is the market moving from one structural regime into another — trend
   into range, range into trend, compression into expansion, or one directional trend into its opposite.
   It is fundamentally a "the rules that applied a moment ago may no longer apply" read.
2. **WHAT TO OBSERVE**:
   - A change in the *character* of price action (e.g., a market that was ranging suddenly makes a
     sustained directional push, or a trending market suddenly starts round-tripping).
   - A previously reliable level or pattern stops working the way it had been (a range floor finally
     breaking, a pullback that doesn't hold).
   - The magnitude/volume signature of the change relative to the regime it's exiting.
3. **WHAT IT DOES NOT MEAN**:
   - A single anomalous bar is not automatically a transition — it can be a spike that fully normalizes
     (see M06).
   - A transition being underway does not mean the new regime's boundaries are already known; that
     usually only becomes clear well after the fact.
   - "This feels different" is not sufficient evidence — a transition read needs the same structural
     confirmation any other module needs (see Confirmed State below).
4. **FORMING STATE**: A regime's usual behavior stops repeating (a range's edges stop holding, a trend's
   pullbacks stop staying shallow) but it's not yet clear whether this is a genuine shift or a temporary
   deviation.
5. **CONFIRMED STATE**: The new behavior sustains across multiple bars/swings and the old regime's rules
   (its range edges, its trend's pullback depth) are decisively no longer being respected.
6. **FAILURE / INVALIDATION**: What looked like a transition reverts — price returns to and re-respects the
   old regime's boundaries or pattern, meaning the apparent shift was a temporary deviation, not a genuine
   one.
7. **RELATION TO H4 / H1 / M15 / M5**: H4 is generally where a transition's significance is ultimately
   judged (did the multi-day/week regime actually change); M15 is where a transition is often first
   noticed developing, frequently well before H4 context is formally updated (see M09). M5 is not a
   natural home for judging regime transitions on its own.
8. **RELATION TO OTHER MODULES**: Transition + Hazard (M11) — an unexplained, violent transition is exactly
   where the hazard lens belongs, to ask whether this is organic regime change or an external shock.
   Transition + Trend (M01) — a trend's failure (M01's own Failure/Invalidation) is one specific case of a
   transition. Transition + Volatility (M06) — regime transitions are very often, though not always,
   accompanied by a volatility expansion.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): the entire post-Feb19-top episode logged in `2020_Q1_H4_LOG.md` and the
     ledger is real, on-topic transition evidence — the Feb19+ uptrend's blow-off top gave way to a sharp
     2/24 impulsive breakdown (explicitly logged as "the first genuinely large, fast, heavy-volume reversal
     move observed against the dominant trend all pilot"), followed by the 2/25 record spike, a 2/26
     large-scale rejection of a fresh high, three tests of a ~1625 floor, that floor's eventual break on
     2/28, and the same-day COVID-panic liquidation crash — a documented sequence of a trending regime
     giving way to a violent, range-and-break regime. The 2020-03-02 record-volume breakout that held (not
     rejected) is separately flagged in the ledger as a possible further transition signal, not yet
     resolved.
   - VALIDATED EDGE (none claimed): none of this sequence is claimed as a tradeable transition signal; it
     is logged throughout as WATCH-only and explicitly earmarked for the Q1 checkpoint discussion rather
     than any live decision.
10. **APPRENTICESHIP QUESTIONS**: Is the market still behaving the way it was a day ago, or has that
    changed? Is this still the same regime? What previously reliable pattern just stopped working? Is this
    change sustaining, or could it still be a single anomalous bar? What would the old regime need to do to
    prove it's still intact?

---

### M11 — Hazard

`CONCEPTUAL_OBSERVATION_ONLY — no governed implementation exists.`

**RUNTIME_STATUS**: Zero implementation anywhere across AI Trader, VE, or Alpha, company-wide. A genuine,
complete gap.

1. **WHAT IT MEANS**: Hazard reads price action for the possibility that an observed move is driven by an
   external shock (scheduled news, an unscheduled event, forced liquidation, thin-liquidity gaps) rather
   than organic structural development — a caution lens, not a detection system.
2. **WHAT TO OBSERVE**:
   - Sudden, large moves with no apparent structural buildup (no compression, no prior level being tested).
   - Volume/range far outside anything else seen in the recent walk.
   - Behavior inconsistent with the prevailing session's normal texture (see M07).
   - Gaps, especially weekend gaps or gaps with no clear preceding structural cause.
3. **WHAT IT DOES NOT MEAN**:
   - An unexplained move is not automatically a hazard event — it may simply be a structural move whose
     cause isn't visible from price alone.
   - A hazard-flagged move is not inherently untradeable forever — it means added caution is warranted
     while its cause and resolution are unclear, not that no future analysis is possible.
   - Hazard is not a synonym for volatility (M06) — an expansion can be organic; a hazard read specifically
     asks whether the *cause* looks external and possibly non-repeating.
4. **FORMING STATE**: A move begins that has no visible structural precedent (no compression flagged, no
   level being tested) and is unusually large or fast for its context.
5. **CONFIRMED STATE**: There is no live detector to confirm this against, so "confirmed" here can only
   mean the move remains inconsistent with any other module's explanation after review — a negative
   finding, not a positive one.
6. **FAILURE / INVALIDATION**: A later, better explanation emerges that fits another module cleanly (it
   was actually a clean M03 breakout, or an M06 compression release) — at that point the hazard framing
   should be dropped rather than kept as a residual label.
7. **RELATION TO H4 / H1 / M15 / M5**: Hazard events are usually first visible at M15 or M5 resolution
   (a single anomalous bar), with H4/H1 useful afterward for judging how much lasting structural impact the
   event had. No timeframe can predict a hazard event in advance from this codebase's data.
8. **RELATION TO OTHER MODULES**: Hazard + Volatility (M06) — the most natural pairing; an unexplained
   expansion spike is the primary hazard trigger. Hazard + Transition (M10) — a genuine external shock can
   trigger a real regime transition, but the two should be reasoned about separately (cause vs. structural
   consequence). Hazard + Event Sequence (M12) — a hazard event is often the anchor point a later event
   sequence gets built around.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): two real, logged episodes fit this module honestly, neither machine-
     detected. `2020_Q1_H4_LOG.md` logs a weekend gap-up to 1681.3 ("largest single-bar move + volume of
     the entire walk"), explicitly tagged `WEEKEND-001` and reasoned about as "expected/normal weekend gap,
     distinct from the 4 unexplained intraday gaps" — itself a hazard-style judgment call made by hand. The
     ledger's 2020-02-28 entry for the extreme liquidation crash (volume 8946, then again 6694) explicitly
     names the real-world COVID-19 panic window as context and reasons, by hand, that the mechanism (forced
     liquidation) is different from the walk's ordinary probe-and-reject pattern and "should not be
     conflated with it" — a genuine hazard-style read, done manually, well before this module existed as a
     named concept.
   - VALIDATED EDGE (none claimed): neither episode is claimed as a detected or predicted hazard event —
     both were recognized only in hindsight, by hand, and logged as WATCH-only.
10. **APPRENTICESHIP QUESTIONS**: Is there any structural buildup that would explain this move, or does it
    look genuinely external? Is this consistent with the session it's happening in? Have I seen anything
    like this magnitude before in the walk? Would a scheduled-news or forced-liquidation explanation fit
    better than a structural one? Should I be reasoning about this move differently than an ordinary
    breakout or expansion?

---

### M12 — Event Sequence

`CONCEPTUAL_OBSERVATION_ONLY — no governed implementation exists.`

**RUNTIME_STATUS**: Zero implementation anywhere.

1. **WHAT IT MEANS**: An event sequence reads a stretch of the market as a connected chain of structural
   events (a breakout, followed by a spike, followed by a reversal, followed by a re-test) rather than as
   isolated, unrelated bars — asking what story the sequence as a whole tells, not just what any single
   event means alone.
2. **WHAT TO OBSERVE**:
   - Multiple structurally distinct events occurring within a compressed window, in a way that seems
     connected rather than coincidental.
   - Whether each subsequent event is consistent with, or a reversal of, the one before it.
   - Whether the sequence, read end to end, resolves into a clear before/after regime change (see M10) or
     remains an unresolved, still-open chain.
3. **WHAT IT DOES NOT MEAN**:
   - A sequence of events happening close together in time is not proof they share a single cause.
   - Naming a sequence after the fact ("this was the top-to-crash episode") is a narrative convenience for
     review, not a claim that the sequence was predictable as it unfolded.
   - A sequence remaining open (not yet resolved) is not itself informative — many sequences simply take
     time to play out and should not be forced into a premature conclusion.
4. **FORMING STATE**: Two or three connected events have occurred, but it's too early to say whether they
   form a coherent chain or are separate, unrelated developments.
5. **CONFIRMED STATE**: A chain of events that, reviewed together, tells a coherent structural story
   (buildup → resolution → aftermath) worth treating as a single episode for review purposes (e.g., in a
   quarterly checkpoint), even without claiming predictive value.
6. **FAILURE / INVALIDATION**: What looked like a connected sequence turns out, on later review, to be
   unrelated events that happened to cluster in time with no coherent through-line.
7. **RELATION TO H4 / H1 / M15 / M5**: Event sequences are naturally read across H4 context (for the
   sequence's overall shape) and M15 detail (for each individual event within it); this is inherently a
   multi-timeframe, retrospective-review concept rather than something read live at M5.
8. **RELATION TO OTHER MODULES**: Event Sequence is largely a container for the others — it strings
   together Volatility (M06) spikes, Transition (M10) moments, and Liquidity (M05) tests into a single
   narrative for review. Event Sequence + Hazard (M11) — a hazard event is often the anchor a sequence gets
   built around.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): the late-February 2020 episode logged across `2020_Q1_H4_LOG.md` and the
     ledger is real, on-topic evidence — the sequence runs from the Feb19+ uptrend's blow-off top, through
     the 2/24 impulsive breakdown, the 2/25 record-volume spike, the 2/26 large-scale rejection of a fresh
     high, three tests of the ~1625 floor (2/25-2/28), the floor's break on 2/28, and the same-day
     liquidation crash — explicitly described in the ledger as "the single richest structural episode of
     the pilot so far" and flagged to "anchor a major section of the Q1 checkpoint," i.e. already being
     treated, in practice, as a single connected sequence for review.
   - VALIDATED EDGE (none claimed): the sequence is logged as a set of individually-WATCH-only events; no
     claim is made that the sequence as a whole was predictable or tradeable.
10. **APPRENTICESHIP QUESTIONS**: Does this event connect to something that happened recently, or is it
    isolated? If I string the last several notable events together, what story do they tell? Is this
    sequence still open, or has it resolved into a clear before/after? Am I forcing a narrative onto
    unrelated events, or is there a genuine through-line? What would this sequence look like described to
    someone who hadn't watched it unfold?

---

### M13 — FVG (Fair Value Gap)

**RUNTIME_STATUS**: RUNTIME-BACKED (YES), OBSERVATION-ONLY BY DESIGN. A real detector runs live against
real MT5 ticks via `ai_trader/structural_observer/` and `ai_trader/live_observation/entrypoint.py`
(vendored `imbalance_mechanics.py`) — but by explicit CEO instruction elsewhere in this codebase, it
records only and never evaluates for a decision. This module's job is to expose that existing observation
capability's output (`FVG_FORMED`/`FVG_REACTION` event types) to the apprenticeship's reading vocabulary
as pure context — never as a signal.

1. **WHAT IT MEANS**: A fair value gap is a three-candle imbalance where the middle candle's range moves
   fast enough that the first and third candles' ranges don't overlap, leaving a price gap that wasn't
   fully traded through — commonly read as a zone of imbalanced, fast-moving order flow.
2. **WHAT TO OBSERVE**:
   - A displacement move (see M06) fast enough to leave a genuine three-candle imbalance.
   - Whether and how price later returns to that gap (partially or fully filling it) versus leaving it
     untouched.
   - The reaction at the gap when price does return to it — acceptance through it, or rejection from it.
3. **WHAT IT DOES NOT MEAN**:
   - An FVG existing is not itself a trade signal — per this codebase's own explicit design, the live
     detector *records*, it does not evaluate or recommend action.
   - A gap being filled does not mean the move that created it is invalidated; gaps fill for many reasons
     unrelated to the original displacement's validity.
   - Not every fast move leaves a meaningful FVG, and not every FVG gets revisited within any useful
     timeframe.
4. **FORMING STATE**: A displacement move is underway; whether it will leave a genuine three-candle
   imbalance isn't yet resolved until the third candle closes.
5. **CONFIRMED STATE**: A clean, real three-candle gap has formed (an `FVG_FORMED` event, per the live
   detector's own vocabulary), and is available as context for later observation.
6. **FAILURE / INVALIDATION**: N/A as a "wrong" outcome in the usual sense — an FVG is a structural fact
   once formed, not a prediction. The relevant later observation is simply how price reacts if and when it
   returns (an `FVG_REACTION` event), not whether the gap itself was "right."
7. **RELATION TO H4 / H1 / M15 / M5**: FVGs are inherently a shorter-horizon, entry-refinement concept —
   M15 and M5 are their natural home, since the live detector reads real tick-level MT5 data. H4/H1 are not
   natural homes for this module; an FVG visible at H4 resolution is a much rarer, much larger-scale event
   than the ones this detector is built to catch.
8. **RELATION TO OTHER MODULES**: FVG + Volatility/Displacement (M06) — an FVG is essentially a byproduct
   of a genuine displacement move; the two are closely linked by definition. FVG + Order Block (M14) — both
   are output by the same `structural_observer`/`live_observation` path and are often discussed together in
   practitioner vocabulary, though neither confirms the other here. FVG + Liquidity (M05) — an unfilled gap
   near a liquidity level is a common practitioner pairing, though not one this codebase currently
   cross-references automatically.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): none yet. The 2026-08-25 coverage audit recorded in the ledger explicitly
     notes that this detector's real, live output does not currently reach the apprenticeship (a separate,
     manual process) — no walk entry in `2020_Q1_H4_LOG.md` references an FVG by name, and none should be
     invented here. The honest state is: the capability is real and live, but not yet observed *by the
     apprenticeship* in any logged walk entry.
   - VALIDATED EDGE (none claimed): none, and by this codebase's own explicit design, none should ever be
     claimed for this detector's raw output — it records, it does not evaluate.
10. **APPRENTICESHIP QUESTIONS**: Did the move that just happened leave a genuine three-candle imbalance,
    or was it too gradual? Has price returned to this gap yet, and if so, how did it react? Am I treating
    this gap as pure context, or am I quietly starting to treat it as a signal? Is this gap forming inside a
    displacement I'd already flagged under M06? What would I expect to see if this gap turns out to be
    structurally unimportant?

---

### M14 — Order Block

**RUNTIME_STATUS**: RUNTIME-BACKED (YES), OBSERVATION-ONLY BY DESIGN, same shape as M13. A real vendored
detector (`order_flow.py`/`order_block_void.py`) runs live via the same `structural_observer`/
`live_observation` path (`ORDER_BLOCK_FORMED`/`BREAKER`/`MITIGATION`/`REJECTION` event types) — records
only, never evaluates.

1. **WHAT IT MEANS**: An order block, in the vocabulary this detector uses, is the last opposing-direction
   candle (or small cluster of candles) immediately before a genuine displacement move — commonly read as a
   zone where the order flow that fueled the subsequent move may have originated.
2. **WHAT TO OBSERVE**:
   - The last down-close candle before a strong up-displacement (or the last up-close candle before a
     strong down-displacement).
   - Whether and how price later returns to that zone.
   - The specific reaction type when it does — mitigation (a controlled retest that holds), rejection
     (a fast reversal away), or a breaker (the zone being violated and flipping role).
3. **WHAT IT DOES NOT MEAN**:
   - An order block existing is not a trade signal — same design rule as M13: this detector records, it
     does not evaluate.
   - Not every candle before a fast move is a meaningful order block; the concept is only useful when
     genuinely paired with a real displacement (see M06/M13).
   - A "mitigation" event does not guarantee continuation, and a "rejection" event does not guarantee
     reversal — these are observed reaction types, not outcomes with known reliability in this codebase.
4. **FORMING STATE**: A displacement move has just occurred; the candle(s) immediately preceding it are
   candidates for an order block, but the label only becomes meaningful once the detector actually flags
   an `ORDER_BLOCK_FORMED` event.
5. **CONFIRMED STATE**: A genuine `ORDER_BLOCK_FORMED` event tied to a real displacement, available as
   context for a later `MITIGATION`/`BREAKER`/`REJECTION` observation if and when price returns to it.
6. **FAILURE / INVALIDATION**: N/A as a "wrong" outcome in the usual sense, same as M13 — the structural
   fact of the block having formed doesn't get invalidated; only the later reaction (mitigation vs.
   rejection vs. breaker) is the thing actually worth observing and recording.
7. **RELATION TO H4 / H1 / M15 / M5**: Same as M13 — inherently a shorter-horizon, tick-adjacent concept;
   M15/M5 are its natural home given the live detector reads real MT5 tick data. H4/H1 are not natural
   homes for this specific detector's granularity.
8. **RELATION TO OTHER MODULES**: Order Block + Structural Location (M05/M04) — an order block's
   significance is usually read in the context of where it sits relative to a broader range or liquidity
   level, not in isolation. Order Block + FVG (M13) — both come from the same detector path and often
   co-occur around the same displacement. Order Block + Transition (M10) — a breaker-type reaction (the
   zone's role flipping) is itself a small-scale transition event.
9. **EXAMPLES AND COUNTEREXAMPLES**:
   - OBSERVATION (from the walk): none yet, for the same honest reason as M13 — the ledger's 2026-08-25
     audit entry confirms this detector's real live output does not currently reach the apprenticeship's
     manual process, and no walk entry in `2020_Q1_H4_LOG.md` references an order block by name. Stated
     plainly rather than inventing an example.
   - VALIDATED EDGE (none claimed): none, and none should be claimed for this detector's raw output by
     this codebase's own explicit design.
10. **APPRENTICESHIP QUESTIONS**: What was the last opposing candle before this displacement — is it a
    plausible order block? Has price returned to that zone, and if so, was the reaction mitigation,
    rejection, or a breaker? Am I keeping this as pure context, or letting it quietly become a trigger? Does
    this order block sit at a structurally meaningful location (a range edge, a liquidity level), or in the
    middle of nowhere? What would tell me this zone's role has actually flipped?

---

## Information assets (read-only context, not signals)

Three frozen information assets exist upstream of AI Trader, as documented in this repo's own
`docs/trader_apprenticeship/README.md`: "DXY-NDX1, VOLTIME-1, SF-3 — usable only as READ-ONLY context
inputs to a `MARKET_ARMED`-style state, never as direct BUY/SELL signals... never retuned." Their specific
statistical derivations belong to the separate Alpha division's own research and are not restated here;
only their bounded, read-only role in this codebase is described.

- **VOLTIME-1** — movement/expansion likelihood information only. Bears on *whether* volatility may be
  about to expand, not on which direction any resulting move would go.
- **DXY-NDX1** — magnitude-conditioning information only. Bears on the potential *size* of an expansion
  once one is underway, not on its direction.
- **SF-3** — session-phase opportunity/whipsaw context only. Bears on whether the current session window
  is historically higher- or lower-opportunity, and on whipsaw risk within it, not on direction.

**NONE of these three may determine LONG/SHORT direction.** This is stated once, prominently, and applies
without exception.

SF-3 has already been correctly used this way, twice, in the walk — both citations in
`lane_a_historical/2020_Q1_H4_LOG.md` use it purely to interpret session-level quiet, not to signal a
trade: once for a genuine round-trip/consolidation M15 session ("matches SF-3's own finding from the
closed session-timing frontier: this UTC window sits in a historically lower-opportunity phase"), and once
for a very quiet overnight stretch ("matches SF-3's own finding — this is the pre-London/Asian-late
session, historically the lowest-opportunity window"). VOLTIME-1 and DXY-NDX1 are documented in this
repo's governance but, per the ledger's 2026-08-25 coverage-audit entry, have not yet been cited by name
anywhere in the walk.

---

*End of `AI_TRADER_MARKET_READING_LIBRARY_V1`. Read-only, forward-only, per the Governance section above.*
