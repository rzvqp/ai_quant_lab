# Edge Discovery Roadmap

**Program**: 40-Edge Alpha Discovery Program. **Purpose**: recommend an order to run the 40 edges
through `EDGE_RESEARCH_PROTOCOL.md`, and justify it.

## ⚠ CURRENT STATUS (updated 2026-07-21): ACTIVE — E011 Discovery complete, awaiting authorization for E005

E015-SCALP Phase 0/0A/root-cause investigation is CLOSED at EVIDENCE LIMIT REACHED (no feasibility
verdict; see `edge_research/E015-SCALP_protocol_and_pilot.md`). Per explicit CEO priority-shift
instruction, no further Replay investigation time is authorized unless materially new evidence
emerges, and §9 (scalping validation) remains deferred project-wide. The laboratory has returned to
its primary Discovery mission (Protocol §§1-8 only).

**Tier 1 reordered (2026-07-21) per a CEO-approved, pre-committed scoring framework** (see
`NEXT_SESSION_FLOW_A.md` for the full audit) — the historical registration order was NOT assumed
optimal. New authorized order: **E006 → E014 → E008 → E011 → E005 → E027 → E016 → E013** (E016/E013
gated on a cheap definitional-overlap check against E015's/E010's existing detectors before any full
Discovery pass, given their high redundancy risk with already-completed results).

**E006 — Asia Range Expansion Failure: Discovery complete (2026-07-21).** V0 NOT SUPPORTED as an
Asia-specific mechanism — real, replicated session-dependent failure-rate heterogeneity found, but a
structural control shows the same pattern is substantially generic to session timing, not the Asia
range itself. No V1 proposed. Full detail: `edge_research/E006_asia_range_expansion_failure.md`.

**E014 — Inside Bar False Breakout: Discovery complete (2026-07-21).** V0 NOT SUPPORTED as an
inside-bar-SPECIFIC mechanism — but a real, replicated (M15/H1/H4) false-breakout-fade effect (~71-76%,
well above a random/synthetic control) was found, driven by generic range **compression** relative to
volatility rather than the strict "inside bar" containment condition (a compression-only control
matches or exceeds real inside bars on every timeframe). **V1 PROPOSED**: compression-driven
false-breakout fade. A dramatic-looking attempt-1-vs-attempt-2 decay was found and explicitly
falsified as a generic artifact of the attempt-selection mechanism (present identically in a fully
synthetic control) — not proposed as a V1. Full detail:
`edge_research/E014_inside_bar_false_breakout.md`. **E014-V1 frozen as a Discovery Candidate contract
(2026-07-21)** — not validated alpha, not an execution rule; see the same file's own
"Frozen Discovery Candidate Contract" section.

**E008 — Friday Profit Taking Shift: Discovery complete (2026-07-21).** V0 NOT SUPPORTED — no
significant difference between Friday afternoon and the rest of the week in directional persistence
or volatility, on M15 or H1, confirmed null by a placebo/permutation control and a
reversal-of-week's-trend test. No V1 proposed. A real, replicated, but Friday-unrelated day-of-week
volatility pattern (Monday quietest, Wednesday most volatile) was found and disclosed as an
out-of-scope observation only, per the CEC-001 precedent — not studied further. Full detail:
`edge_research/E008_friday_profit_taking_shift.md`.

**E011 — Failed 3 Drive Pattern: Discovery complete (2026-07-21).** V0 NOT SUPPORTED — the first
pattern-family diversification in this program (a swing/leg detector, not OB/FVG/CHoCH/compression or
session-timing). A clean, complete null across the entire predeclared battery on all three timeframes
(M15/H1/H4): failed-3rd-leg reversal rate, completed-3-drive reversal rate, a generic isolated swing
point, and a fully synthetic random point are all statistically indistinguishable from each other and
from a coin flip (~50-57%), at every fractal-k tested (3/5/8) and across every context slice. No V1
proposed — no residual effect anywhere to build one from. Full detail:
`edge_research/E011_failed_3_drive_pattern.md`.
**Awaiting CEO authorization before starting E005.**

<details><summary>Superseded status entries (kept for the record, not current)</summary>

### Original entry (2026-07-22): PAUSED — E015-SCALP Phase 0 (TradingView Replay) verdict: NOT FEASIBLE; awaiting CEO decision

**CEO directive (2026-07-22)**: the research objective shifted from multi-day structural-behavior
Discovery to testing whether each edge is an IMMEDIATELY tradable scalp (TP=2R before SL=1R within
5-60 minutes). `EDGE_RESEARCH_PROTOCOL.md` §9 registers this as Protocol v2. Repository M1/M5 data was
confirmed absent (`data/market/` = D1/H1/H4/M15 only); the CEO then authorized TradingView Bar Replay on
XAUUSD M1 as the execution-validation source and directed a Phase 0 feasibility pilot on **E015-SCALP —
First Order Block Mitigation Immediate Response**.

**E015-SCALP Phase 0 result: NOT FEASIBLE (verdict C)** — a live TradingView CDP connection was
confirmed, the frozen E015 detector was reconstructed (6,919 visit-1 events), a 5-event outcome-blind
pilot sample was selected, and trade rules were frozen before any replay. Two independent replay
attempts (dates ~3.3 years and ~8 weeks back) both showed `replay_start`'s own date-seek failing to
reach the requested historical point — the chart/replay consistently reverted to the live real-time bar.
One attempt additionally surfaced a native TradingView "Data point unavailable" toast (a possible feed
retention limit); the other showed no such toast, isolating a genuine tool-integration defect
independent of retention. Per explicit instruction, no manual/visual workaround was substituted. Full
report, evidence screenshots, and the mandatory per-event record: `edge_research/
E015-SCALP_protocol_and_pilot.md`, `edge_research/e015_scalp_pilot_events.json`.

**E015's own structural result is unchanged** (V0 NOT SUPPORTED as registered; V1 candidate = "first
mitigation only"; both stand exactly as before). **E013 has NOT begun.** All five edges studied under
§§1-8 alone (E017/E009/E010/E012/E015) carry an appended "structural-behavior Discovery, not direct
scalping validation" scope clarification — no V0/verdict/conclusion changed. Awaiting CEO decision on
how to proceed (fix the replay-seek tooling and retry Phase 0 / investigate feed retention / redirect
back to structural-behavior Discovery for now / another path).

**TERMINAL HOLDOUT BREACHED, then REMEDIATED** (`PROJECT_STATE_v2.md` §8.23/§8.24): the five edges
studied in this program's first research session (E025, E026, E028, E029, E032) originally loaded data
from the Research Lab's own sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) — **the
old terminal holdout is CONSUMED / INVALIDATED**, permanently. CEO-authorized remediation (2026-07-21)
implemented centralized holdout-exclusion enforcement (`edge_research/_common.py::load()`, 17 tests
passing) and cleanly reran all five — 4 of 5 CONFIRM their original finding, 1 (E025) partially weakens.
Registry status: `DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE` for those five.

**E017 — Equal Highs / Lows Target — Discovery pass complete, 2026-07-21** (run entirely under the
post-remediation centralized-loader enforcement, no contamination possible). **Result: V0 NOT
supported** — equal-highs/lows show no reach-rate or reversal-magnitude advantage over ordinary
isolated swings, robust across every tolerance (0.10–0.40×ATR) and horizon (1/5/20 trading days) tested;
a random-matched-distance control reaches its target *more* reliably than real swing points, the
opposite of a "magnet" story. No Final Verdict issued. Full detail:
`edge_research/E017_equal_highs_lows.md`.

**E009 — Change of Character Retest — Discovery pass complete, 2026-07-21** (an earlier reference to
"E009 — Previous Day High/Low" was a factual error, verified against the registry and withdrawn by
explicit CEO decision before any research began; this pass studies the registry's own real, frozen E009
only). **Result: V0 NOT supported** — CHoCH shows no retest-rate, continuation-rate, or failure-rate
advantage over an ordinary BOS break (its natural, on-topic, same-mechanism control), at any tested
fractal-k (3/5/8), horizon (1/5/20 trading days), session, or volatility regime; the retest metric
itself was found to be near-saturated (90%+) even for a random, no-structure, distance-matched control,
an important disclosed methodological limit on this pass's own power. No Final Verdict issued. Full
detail: `edge_research/E009_choch_retest.md`.

**CEO authorized (2026-07-22) an "overnight full edge profile" directive**: beyond the binary V0 test,
each edge now also gets a timeframe profile, a 7-horizon/5-ATR-threshold movement profile, a context
profile (session/volatility/trend/day-of-week), controls/falsification, a disciplined V1 search (no
combination-hunting, no retrospective V0 changes), and robustness checks (parameter sensitivity, yearly
stability) — see `edge_research/_profile.py`, the new shared library this requires, and each edge's own
log for the full template. One edge at a time, auto-continuing after each commit, per that
authorization.

**E010 — Breaker Block Snatch — full profile complete, 2026-07-22** (M15 + H1; M1/M5 confirmed
unavailable, per §1's own gap analysis). **Result: V0 NOT supported** — after a breaker flip, price
continuation-in-the-new-direction is a coin flip (~50%) on both timeframes, at every displacement
threshold (1.2×/1.5×/2.0×ATR), session, volatility regime, trend context, day of week, and year tested.
**A large, real, robust directional effect was found instead for the natural unflipped-OB control**
(ordinary, never-violated order blocks respected in their ORIGINAL polarity, ~86-88% continuation,
+1 ATR mean move by 1 bar) — flagged as a possible future, separately-registered edge, not folded into
E010's own V1 (none offered). No Final Verdict issued. Full detail:
`edge_research/E010_breaker_block_snatch.md`.

**E012 — Inverted Fair Value Gap — full profile complete, 2026-07-22** (M15 + H1; M1/M5 unavailable,
same as E010). **Result: V0 NOT supported** — the same qualitative pattern as E010: after an FVG
inverts, continuation in the new direction is a coin flip (~50-53%) on both timeframes, every gap-size
filter, session, volatility regime, trend context, day of week, and year. **The natural un-inverted-FVG
control again shows a large, real, directional continuation effect in the ORIGINAL role** (~86-87%,
mirroring E010's own unflipped-OB finding) — two independent structural concepts now both suggest that
violating/flipping a zone destroys its predictive power rather than reversing it. No V1 candidate
offered. No Final Verdict issued. Full detail: `edge_research/E012_inverted_fvg.md`.

**CEO-directed governance step (2026-07-22)**: before continuing past E010/E012, a registration-only
cross-edge research candidate, **CEC-001**, was recorded in the new `CROSS_EDGE_RESEARCH_CANDIDATES.md`
— NOT part of this 40-edge structure, NOT a numbered edge, no study conducted. It documents the
recurring "unbroken structural zone predicts continuation; broken/flipped one predicts nothing" pattern
(E010's unflipped-OB control, E012's un-inverted-FVG control) alongside a serious risk register
(look-ahead bias in the unbroken/unviolated classification itself, event-definition leakage,
tautological continuation labels, survivorship, unmatched distance/age, dependent samples) explaining
why it is explicitly NOT yet an accepted edge. E010's and E012's own conclusions are unchanged.

**E015 — Order Block Re-Mitigation — full profile complete, 2026-07-22** (M15 + H1; M1/M5 unavailable).
**Result: V0 NOT supported — but not a flat null; a sharp, well-evidenced DECAY.** Reaction is real and
substantial on the FIRST mitigation (~76% continuation, both timeframes, matching the magnitude of
E010's own unflipped-OB/CEC-001 effect) but collapses to a random-matched-control-level coin flip
(~50-54%) by the SECOND mitigation and stays there for the third and later — robust across 3
displacement thresholds, every session, volatility regime, trend context, and year. **A V1 candidate IS
offered** (the first this program): "reaction concentrated in the first mitigation only" — Discovery-
stage, unfrozen, not Frozen Candidate. Deliberately designed to avoid CEC-001's own look-ahead risk
(visit numbering is purely sequential/forward-only, unlike the unbroken/unviolated classification that
risk concerns). No Final Verdict issued. Full detail:
`edge_research/E015_order_block_remitigation.md`.

**Per the CEO's own standing "overnight full profile" authorization, the session auto-continues to the
next eligible edge without stopping for approval between edges** (stopping only for a genuine
governance issue, an unoperationalizable V0, a missing-data blocker, a loader/test failure, a
Flow-B-touching requirement, or an audit-trail risk — none occurred for E010, E012, or E015). ~~**Next:
E013 — Mitigation Block Sniping**, then in order **E016, E011, E014**, then the session-timing edges
**E006, E008, E005, E027**.~~ **Superseded 2026-07-21 by the CEO-approved priority-audit reorder above
— this auto-continue note no longer reflects the authorized sequence.**

</details>

## 1. Data-availability gap analysis (verified against what is actually on disk today)

Before any sequencing decision, the project's real data inventory was checked (read-only, no code run):

| Resource | Status today | Gap vs. what the 40 edges need |
|---|---|---|
| XAUUSD OHLCV history | `data/market/OANDA_XAUUSD_{D1,H4,H1,M15}.csv`, ~2022-12-16 → 2026-07-13 (~3.5-4 years) | Short of the protocol's ~5-6 year requirement (§2 of the protocol); moderate gap, likely closeable by extending the same feed backward/forward, not a new data source |
| Intraday resolution | **M15 is the finest resolution that exists** | No M1 or tick data at all — blocks precise session-boundary edges (E001, E002, E004, E027), most Category 2/3 edges' precision, all tick-dependent edges (E018 as redefined, E019-E021, E023, E030), and every Category 6 news edge (fast reactions need finer than M15) |
| Volume field | Present in all 4 XAUUSD files, but of unconfirmed provenance (likely OTC tick-count proxy, not verified exchange volume) | Affects every edge that leans on volume as a real signal (E019, E020, E021, E022, E023, E031) — these can still be tested, but any Final Verdict must caveat that "volume" here is a proxy, not confirmed order-flow |
| DXY / US10Y / XAGUSD / USDJPY / SPX | **None exist anywhere in this project** | Blocks all four Intermarket edges (E033-E036) and two others (E003 needs XAGUSD, E024 needs SPX) entirely until acquired |
| Economic calendar (NFP/CPI/FOMC/Flash PMI timestamps) | **Does not exist.** A scaffold does: `ai_trader/market_scanner/calendar_engine.py` and a `CalendarEvent` type can *ingest* external events once supplied, but no actual event data file exists | Blocks all four News edges (E037-E040) and two others (E007, and E003's Silver Fix timestamp) entirely until a calendar feed is acquired |

None of these gaps is resolved by this roadmap — they are the reason the sequencing below starts with
what is testable today and defers what needs new data acquisition, which itself would be a separate,
explicitly-authorized future step (data acquisition is not "implementation" of an edge, but it is not
part of this program's current authorization either).

## 2. Sequencing principle

Edges are ordered by **what is testable with today's actual data** first, deferring edges that need a
new data source. Within a data-availability tier, edges are ordered by structural
simplicity/testability — a single, unambiguous, mechanically definable condition is cheaper and more
reliable to run through Discovery than a subjective or compound one. This mirrors the general research
posture already established in this project's own mechanism work
(`MECHANISM_REGISTRY.md`): cheap falsification first, complex/expensive study only once the simple
questions are answered.

## Tier 0 — Prerequisite (blocks nothing below directly, but should run once, early)

Extend the existing `OANDA_XAUUSD_M15` (and D1/H1/H4) history as far back and forward as the same
provider/feed allows, to close the ~3.5-4 → ~5-6 year gap. This is data acquisition, not edge research —
listed here only because every single edge below benefits from it and it is the single highest-leverage
action before the tiers below begin in earnest.

## Tier 1 — Testable today, single instrument, M15-adequate

These need only what already exists on disk (XAUUSD OHLCV, M15 or coarser, no volume dependency, no
external instrument, no calendar). Recommended first because they can start immediately and because a
disproportionate share of them can reuse existing `ai_trader/market_intelligence/` building blocks
(`structure.py`, `volatility.py`, `session_behavior.py`) as candidate components — cutting real
Discovery-stage cost, not just theoretical cost.

1. **E025 — Round Numbers** (simplest possible mechanical definition; pure price-level math)
2. **E026 — ADR Exhaustion** (pure daily-range arithmetic, D1/M15 only)
3. **E029 — Weekly Gap Fill** (pure D1 gap arithmetic)
4. **E032 — Premium Discount Flip** (pure range-midpoint arithmetic)
5. **E028 — Fibonacci OTE** (mechanical retracement measurement)
6. **E017 — Equal Highs / Lows Target** (candidate reuse: `structure.py`)
7. **E009 — Change of Character Retest** (candidate reuse: `structure.py`)
8. **E010 — Breaker Block Snatch** (candidate reuse: `structure.py`)
9. **E012 — Inverted Fair Value Gap**
10. **E015 — Order Block Re-Mitigation**
11. **E013 — Mitigation Block Sniping**
12. **E016 — Propulsion Block Entry**
13. **E011 — Failed 3 Drive Pattern**
14. **E014 — Inside Bar False Breakout**
15. **E006 — Asia Range Expansion Failure** (session boundaries known at daily granularity even without
    M1; some timing precision lost but the core question is testable)
16. **E008 — Friday Profit Taking Shift** (candidate reuse: `session_behavior.py`)
17. **E005 — London Close Reversal**
18. **E027 — Midnight Open Anchor**

Sub-ordering rationale: pure-arithmetic edges (1-5) first because they have zero ambiguity in
definition and the fastest possible Discovery pass; structure-pattern edges (6-14) next because they can
lean on an existing analyzer instead of building pattern-detection logic from scratch; session-behavior
edges with only moderate precision loss from M15 (15-18) last in this tier.

**Remaining-items order superseded 2026-07-21** (items 11-18 above, i.e. everything after E015):
a CEO-approved, pre-committed scoring framework (Novelty, Expected Information Value, Leverage,
Execution Cost, Independence — see `NEXT_SESSION_FLOW_A.md` for the full audit) found E013 and E016
carry the highest redundancy risk in this remaining set (their V0 objects substantially overlap
already-completed E010/E012/E015 findings) rather than being natural next steps. **Authorized order for
the remaining items is now: E006 (done) → E014 (done) → E008 (done) → E011 (done) → E005 → E027 → E016 → E013**
(E016/E013 gated on a cheap definitional-overlap check before any full Discovery pass). The numbered
list above is kept as-is for the historical record; this note is the current authority on sequencing.

## Tier 2 — Testable today but need finer-than-M15 timing to do properly

The core question is answerable with existing data, but the *precision* of the answer is capped by M15
resolution — worth an early, explicitly-caveated Discovery pass now (to see if a signal survives even
at coarse resolution), with a note that Validation/Walk Forward should be re-run at M1 once/if that data
is acquired.

19. **E001 — London Open Liquidity Hunt**
20. **E002 — Frankfurt Pre-Market Trap**
21. **E004 — US Market Open First FVG**
22. **E018 — B-Book Stop Hunt** (also needs the reformulation flagged in the registry before Discovery
    can meaningfully start — a definitional prerequisite, not a data one)
23. **E030 — Tick Speed Acceleration** — **held, not sequenced into an early pass**: this edge's entire
    hypothesis is about tick frequency; there is no coarse-resolution proxy worth testing. Placed last
    in this tier deliberately as a placeholder until tick data exists.

## Tier 3 — Volume-dependent (testable today, but every Final Verdict must caveat the proxy-volume issue)

24. **E022 — VWAP Touch And Go**
25. **E031 — 3 Standard Deviations VWAP**
26. **E023 — High Relative Volume Breakout**
27. **E019 — Volume Climax Exhaustion**
28. **E020 — Delta Divergence** — **held**: needs buy/sell-side delta, not just a volume column; the
    OANDA proxy volume cannot construct this. Placeholder until true order-flow data exists.
29. **E021 — Iceberg Order Absorption** — **held**: same reason as E020, arguably an even stronger
    requirement (needs visibility into repeated absorption at a level, i.e. time-and-sales/order-book
    data). Placeholder.

## Tier 4 — Blocked on a new instrument's data (Intermarket + 2 others)

Cannot meaningfully enter Discovery until the named companion instrument's historical data is acquired.
Recommended acquisition order, if/when authorized, by how directly it's referenced: DXY and XAGUSD are
named by two edges each (counting E003/E035 for silver, E024 doesn't need silver) — actually each
companion instrument below is named by exactly the edges listed next to it:

30. **E033 — DXY Lead** (needs DXY)
31. **E035 — Silver Leading Indicator** (needs XAGUSD)
32. **E003 — NY Silver Fix Momentum** (needs XAGUSD + a fix-timestamp convention)
33. **E034 — US10Y Lead** (needs US10Y yield series)
34. **E036 — USDJPY Inversion** (needs USDJPY)
35. **E024 — SP500 / Gold Delta Shift** (needs SPX)

## Tier 5 — Blocked on an economic calendar (News + 2 others)

Cannot meaningfully enter Discovery until a verified economic-calendar feed with exact release
timestamps is acquired and wired into the existing `calendar_engine.py`/`CalendarEvent` scaffold.

36. **E038 — CPI Initial Reaction Reversal** (single, well-defined monthly event; simplest of this tier)
37. **E040 — Flash PMI Sentiment Flip**
38. **E037 — NFP First Wave Liquidation**
39. **E039 — FOMC Slingshot** (two timestamps per event — statement and press conference — the most
    structurally complex of this tier)
40. **E007 — Central Bank Whisper** (last: requires the calendar *and* a pre-registered definition of
    "before major news," which is currently the vaguest hypothesis in the whole registry and would
    benefit from being defined only after E037-E039 have already established what a "normal" news
    reaction looks like, to have a clean baseline to detect drift against)

## 3. Summary

| Tier | Edges | Blocked by | Ready to start now? |
|---|---|---|---|
| 1 | 18 | Nothing | Yes |
| 2 | 5 | M1/tick resolution (partial pass possible now) | Partially |
| 3 | 6 | Volume/order-flow data quality (4 partially testable; 2 fully held) | Partially |
| 4 | 6 | New instrument data (DXY, US10Y, XAGUSD, USDJPY, SPX) | No |
| 5 | 5 | Economic calendar data | No |

**23 of 40 edges (Tiers 1-2) are startable with the data already on disk today**, 18 of those with no
caveat at all. The remaining 17 (Tiers 3 partial-hold, 4, 5) require a data-acquisition decision that
this roadmap does not make — it only sequences what to do once each acquisition is authorized.

This roadmap recommends starting Tier 1 first, in the order listed, while a separate decision is made
about the Tier 0 history-extension and any Tier 3-5 data acquisitions. No edge in any tier is authorized
to begin Discovery by this document alone — that remains a separate, explicit, per-edge or per-batch CEO
authorization, per the program's own opening instruction.
