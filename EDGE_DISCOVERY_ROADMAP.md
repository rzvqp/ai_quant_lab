# Edge Discovery Roadmap

**Program**: 40-Edge Alpha Discovery Program. **Purpose**: recommend an order to run the 40 edges
through `EDGE_RESEARCH_PROTOCOL.md`, and justify it.

## ⚠ CURRENT STATUS (updated 2026-07-21): E017 DONE — awaiting CEO approval to resume at E009

**TERMINAL HOLDOUT BREACHED, then REMEDIATED** (`PROJECT_STATE_v2.md` §8.23/§8.24): the five edges
studied in this program's first research session (E025, E026, E028, E029, E032) originally loaded data
from the Research Lab's own sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) — **the
old terminal holdout is CONSUMED / INVALIDATED**, permanently. CEO-authorized remediation (2026-07-21)
implemented centralized holdout-exclusion enforcement (`edge_research/_common.py::load()`, 17 tests
passing) and cleanly reran all five — 4 of 5 CONFIRM their original finding, 1 (E025) partially weakens.
Registry status: `DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE` for those five.

**E017 — Equal Highs / Lows Target — Discovery pass complete, 2026-07-21, CEO-authorized, run entirely
under the post-remediation centralized-loader enforcement from the start** (no contamination possible).
**Result: V0 NOT supported** — equal-highs/lows show no reach-rate or reversal-magnitude advantage over
ordinary isolated swings, robust across every tolerance (0.10–0.40×ATR) and horizon (1/5/20 trading
days) tested; a random-matched-distance control reaches its target *more* reliably than real swing
points, the opposite of a "magnet" story. No Final Verdict issued (below the ~5-6yr horizon). Full
detail: `edge_research/E017_equal_highs_lows.md`.

**The next Flow A action (E009) is NOT yet authorized.** Per the CEO's own E017 authorization ("Do not
begin E009 or any later edge during this authorization... Stop after E017 and await CEO verdict"),
resuming the Tier 1 sequence requires its own separate CEO approval. Once granted, the sequence resumes
at **E009 — Change of Character Retest**, then in order **E010, E012, E015, E013, E016, E011, E014**,
then the session-timing edges **E006, E008, E005, E027**.

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
