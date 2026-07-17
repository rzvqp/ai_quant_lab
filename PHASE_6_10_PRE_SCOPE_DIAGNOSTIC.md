# Phase 6.10 Pre-Scope Diagnostic — Same-Bar Competition, Persistent Blocking, Holding-Period
# Structure, Signal Redundancy, and Independent-Evidence Estimate

**Date:** 2026-07-17. **Scope: a diagnostic measurement pass only, requested by the CEO before any
Phase 6.10 architecture is selected.** No strategy, parameter, Scoring Engine, Risk Manager, Execution
Engine, Strategy Health methodology, Research Lab, or sealed-holdout logic was touched, executed, or
re-simulated. This document does not begin Phase 6.10, does not select a governance architecture, and
does not change the official phase status (Phase 6.10 remains NOT STARTED / NOT SCOPED after this
document, per `PROJECT_STATE_v2.md` §3 and `NEXT_SESSION.md` §A).

**Method**: 100% of the figures below are derived by a new, read-only script,
`phase610_prescope_analysis.py` (committed alongside this report, output in
`phase610_prescope_analysis.json`), that loads the two existing Phase 6.9A JSON artifacts
(`phase69a_competitive_funnel.json`, `phase69a_isolated_funnel.json`) and computes everything from
them. **No `ai_trader/` source file is imported or executed by this script, no simulation is re-run, no
new backtest was performed.** This satisfies the CEO's "use existing artifacts first" instruction in
full for four of the five requested measurement areas; the one area that could not be answered from
existing data (stop/target-level signal similarity) is stated explicitly in §6 and §8, with the smallest
additive instrumentation that would be needed — not implemented.

Window (unchanged from Phase 6.9A, for direct comparability): **2024-10-23 → 2025-10-23** (365 days,
23,639 M15 bars). Same $2,000 capital, 5% risk/trade, cost model, `run_seed=1`, execution model, market
data as every prior phase.

---

## 1. Executive conclusion

**A data-quality correction, found while building this diagnostic, changes the unit of account slightly
from Phase 6.9A's own headline numbers — disclosed immediately, not buried.** `TradeRecord` is
documented as "one closed trade (**or partial exit**)" (`portfolio_simulator.py` line 51). Direct
inspection found that 65 of the 823 isolated-run trade rows (25 of the 142 competitive rows) are actually
a SECOND leg of a single scaled-exit position (identical strategy, entry bar, entry price, and
direction; only the exit differs) — not a second, independent opportunity. Every measurement in this
document below therefore operates on **logical positions** (partial-exit legs collapsed): **758
isolated positions** (not 823 trade-legs) and **117 competitive positions** (not 142 trade-legs). The
823/142 trade-leg counts and the 5.8× headline ratio from Phase 6.9A's own report remain correct AS
TRADE-LEG counts and are not being revised — this is a finer unit of account for THIS diagnostic's own
opportunity-counting questions, not a contradiction of that report. Full detail in §2.

**On the five questions the CEO asked this diagnostic to resolve:**

1. **Persistent blocking is present far more often than same-bar conflict, and the two frequently
   overlap rather than being separate causes — a correction to this diagnostic's own first-draft
   framing, found and fixed during the CEO-requested consistency check (§4.1).** Of the 691 isolated
   positions that do not have a matching competitive-run realization: persistent blocking is present
   (alone or combined with same-bar conflict) in **90.4% (625)**, while same-bar conflict is present
   (alone or combined) in only **45.7% (316)**. Critically, these are **not disjoint categories**: **273
   of the 691 (39.5%) exhibit BOTH mechanisms simultaneously** — the position both shares its entry bar
   with another strategy's isolated entry AND falls inside a third strategy's already-open isolated
   position. Only **43 (6.2%) are same-bar-conflicted with no persistent blocking also present**;
   **352 (50.9%) are persistent-blocked with no same-bar conflict also present**; **23 (3.3%)** show
   neither. An earlier draft of this document reported a clean 45.7%/50.9%/3.3% three-way split as if it
   were a natural partition; that split is only reproducible by applying an arbitrary priority rule
   (classify same-bar first) to the 273 dual-mechanism cases — it does not reflect two cleanly separable
   causes. Full breakdown and reproduction method in §4.1. **The corrected picture argues persistent
   blocking is the more foundational mechanism** (present in 90.4% of the gap vs. same-bar's 45.7%, and
   "pure" same-bar-only conflict is rare at 6.2%), which sharpens rather than reverses this document's
   final recommendation (§10).
2. **Persistent blocking is heavily concentrated in three strategies**: S46, S39, and S40 together
   account for **57% (1,134 of 1,978) of all measured blocking relationships** (§5) — this is a sharper,
   more actionable finding than the prep document had, and argues for considering a targeted remedy
   aimed at these three specifically, not only a portfolio-wide redesign.
3. **A small number of long-held positions dominate occupied slot-time**, confirming the prep document's
   Open Question 5 directly: the longest-held **10% of isolated positions account for 69.4% of all
   occupied slot-time**; in the competitive run the same figure is 50.7% (§5, §6). Time-stop exits are a
   small minority of both trade count (5–10%) and slot-time consumed (0.7–2.7%) — **the long tail is
   overwhelmingly stop-loss and take-profit exits that ran a long time before resolving, not time-stop-
   capped trades** (§6).
4. **Most same-bar conflicts are agreement, not direction conflict** — 81.25% of same-bar conflict
   groups have every competing strategy signaling the SAME direction; only 18.75% are a genuine BUY-vs-
   SELL clash (§3, §7). This means a meaningful share of the measured "lost opportunity" is duplicated,
   correlated signal, not independent edge — but even after the strictest available deduplication, an
   estimated **~74% of isolated positions remain economically distinct** (§7), so the finding that
   independent slots would produce genuinely new evidence, not merely restated evidence, still stands,
   just at a discounted magnitude from the raw 5.8× headline.
5. **Stop/target-level signal similarity cannot be measured from existing artifacts** — `TradeRecord`
   carries no stop-loss/take-profit price fields, only entry/exit price and MFE/MAE. Answering this
   fully would require new, CEO-gated instrumentation and two new backtest runs (§6, §8) — not
   implemented here.

**Recommendation (per §9–§10 below, using the letter scheme in the CEO's own diagnostic request)**: scope
**A — shadow-mode evidence accumulation** as the first concrete Phase 6.10 design target, because it is
the only option that addresses both the same-bar and the persistent-blocking mechanism simultaneously,
requires no new capital risk, and directly targets the specific chronic victims this diagnostic
identifies (S10, S48, S25, S44, S13). Scope two smaller, parallel, lower-cost follow-on investigations
alongside it: a **targeted holding-period/slot-release look at S46/S39/S40 specifically** (closest to
option **E**), and a **strategy-clustering study of the S39↔S40 redundancy** (option **F**). This is a
recommendation for what to investigate/design next, not an implementation, and not a final architecture
selection — no option is selected today.

---

## 2. Measurement definitions

- **Trade-leg**: one `TradeRecord` row as already persisted in `phase69a_competitive_funnel.json`/
  `phase69a_isolated_funnel.json` (Phase 6.9A's own unit; 823 isolated / 142 competitive).
- **Logical position** (this diagnostic's own unit, used throughout §3–§7): trade-legs sharing
  `(strategy_id, entry_as_of)` collapsed into one record, with `full_exit_as_of` = the MAX `exit_as_of`
  across its legs (the symbol slot is not fully free until the last leg closes) and `holding_bars_full`
  = the holding-bars value of whichever leg produced that final exit. Verified: every one of the 65
  (isolated) / 25 (competitive) multi-leg groups has exactly 2 legs, identical `entry_price` and
  `direction` across both legs — consistent with a scaled (partial) take-profit/exit design, not a data
  error. Isolated: 823 legs → **758 positions**. Competitive: 142 legs → **117 positions**.
- **Same-bar conflict**: an `entry_as_of` bar shared by ≥2 *different-strategy* isolated positions (a
  single strategy cannot conflict with itself; this diagnostic explicitly excludes that case, which a
  naive per-bar grouping would not).
- **Persistent blocking**: isolated position X's `entry_as_of` falls strictly inside another
  (different-strategy) isolated position Y's own open interval `[entry_as_of, full_exit_as_of)`. This is
  a **counterfactual overlay** — it assumes all 43 strategies' isolated positions coexist "as if real,"
  which only one shared XAUUSD slot could ever actually allow historically. It is an upper-bound proxy
  for blocking *pressure*, not an exact reconstruction of which specific position would have held the
  slot at each moment (see §8).
- **Gap decomposition**: for each of the 758 isolated positions, check whether a competitive-run
  position exists at the identical `(strategy_id, entry_as_of)`. If yes, the position is "matched"
  (realized in both runs). If not, it is part of "the gap," classified same-bar-conflicted first, else
  persistent-blocked, else unexplained.
- **Economically distinct opportunity count**: two bounds, both computed over logical positions —
  a strict **lower bound** (dedup only exact-same-bar entries into one event) and a loose **upper
  bound** (connected components of the full temporal-overlap graph, same-bar OR persistent-block edges).
  The upper bound is reported but flagged as degenerate (§7, §8).
- **Exit reason** (stop-loss / take-profit / time-stop / trailing-stop / forced liquidation): derived
  from each trade-leg's own `client_order_id` string, verified directly against source: `builder.py`
  derives `client_order_id = f"{prefix}-{decision_id}"`; `time_stop.py`/`trailing_stop.py` build
  `decision_id` as `"TIMESTOP-{strategy}-{symbol}-{as_of}"` / `"TRAILSTOP-{strategy}-{symbol}-{as_of}"`;
  a normal OCO bracket exit's fill carries the sibling order's own id, suffixed `-SL`/`-TP`
  (`execution_simulator.py` lines 464/473); a forced end-of-window close uses
  `"LIQUIDATION-{symbol}-{as_of}"` (`portfolio_simulator.py` line 324). A small residual (10 isolated
  legs, 3 competitive legs — 1.2%/2.1%) matched none of these patterns and is reported as
  "unclassified"; immaterial to every conclusion below given its size.

---

## 3. Same-bar competition analysis

| | Isolated positions (758) |
|---|---|
| Distinct entry bars used | 564 |
| Bars with ≥2 competing strategies | **144** |
| Positions involved in a same-bar conflict | **338 (44.6%)** |
| Conflict groups, all same direction | 117 (81.25%) |
| Conflict groups, mixed (BUY vs SELL) direction | 27 (18.75%) |
| Mean entry-price spread within a conflict group | 0.68 (points) |
| Max entry-price spread within a conflict group | 28.07 (points) |

**Nearly half (44.6%) of all isolated-slot positions occur on a bar where at least one other strategy
also has an isolated position.** Of those conflicts, the overwhelming majority (81.25%) are strategies
agreeing on direction, not fighting over it — genuine BUY-vs-SELL same-bar arbitration is a minority case
(18.75% of conflict groups). Entry-price spread within a conflict group is small on average (0.68
points on a ~2,600–2,800 instrument) but not always negligible (max 28.07) — a reminder that "same bar"
does not always mean "identical fill," since different evaluators can reference slightly different
intra-bar price points.

**Participation is concentrated, not diffuse**: S40 (66 conflict-bar appearances) and S39 (61) are far
ahead of the rest (S4: 23, S44: 19, S26: 17). The single largest same-direction pair is **S39↔S40, co-
occurring 61 times** — this is essentially the entirety of both strategies' own conflict participation,
a strong signal that S39 and S40 fire on substantially the same underlying market condition (§6). Cross-
referencing against the competitive run: of the 117 competitive-position entry bars, **22 were also an
isolated-run conflict bar** — i.e., roughly a fifth of realized competitive trades occurred on a bar
where the isolated data shows another strategy also wanted in.

---

## 4. Persistent blocking analysis

| | Isolated positions (758) |
|---|---|
| Total blocking relationships measured (ordered blocker→victim pairs) | **1,978** |
| Distinct positions blocked at least once | **678 (89.4%)** |
| Median holding-bars of the blocking position | 99 |
| Mean holding-bars of the blocking position | 426.8 |

**Persistent blocking is pervasive** — 89.4% of all isolated positions have their own entry bar falling
inside at least one other strategy's already-open isolated position. But it is **not diffuse across all
43 strategies as blockers** — it is dominated by three:

| Blocker | Blocking events caused | (for context, from Phase 6.9A's own table: competitive / isolated trade-legs) |
|---|---|---|
| S46 | 439 | 47 / 79 |
| S39 | 354 | 36 / 66 |
| S40 | 341 | 3 / 69 |

**These three strategies alone account for 1,134 of 1,978 blocking relationships (57.3%).** All three
are strategies that hold positions unusually long relative to their peers (median blocking-position
holding time across the whole dataset is 99 bars — roughly a full trading day on M15 — but S46/S39/S40's
own typical holds run considerably longer; see §5). The most-blocked ("victim") strategies are:

| Victim | Times blocked |
|---|---|
| S10 | 293 |
| S48 | 185 |
| S25 | 151 |
| S44 | 146 |
| S13 | 121 |

This directly corroborates Phase 6.9A's own per-strategy finding that S10 is the single most
slot-starved strategy (1 competitive trade vs. 117 isolated) — the top three blocker↔victim pairs are
**S39→S10 (77), S40→S10 (76), S46→S10 (76)** — S10 is blocked at nearly identical rates by all three of
the dominant blockers, not by one specific antagonist.

### 4.1 Gap decomposition: same-bar conflict vs. persistent blocking — the honest overlap

This subsection directly answers `PHASE_6_10_PREPARATION.md`'s Open Question 3 ("how much of the gap is
same-bar conflict vs. persistent-position blocking?") and documents a correction found and fixed during
the CEO-requested consistency check (see instruction context): **an earlier draft of this document
classified each unmatched isolated position into same-bar-conflict OR persistent-blocked using a
priority rule (same-bar checked first), which silently forced a clean partition and hid the fact that
the two conditions frequently co-occur.** This subsection reports the honest, non-prioritized breakdown.

**Setup**: of the 758 isolated positions, only **67 match** a competitive-run position at the identical
`(strategy_id, entry_as_of)` — these are "realized both ways." The remaining **691 are "the gap"** (a
different number from the raw leg-level 823−142=681 in Phase 6.9A's own report, because this diagnostic
uses logical positions, not trade-legs — see §2). Each of the 691 gap positions was checked against BOTH
conditions independently, with no priority rule:

| Category | Count | % of the 691-position gap |
|---|---|---|
| Same-bar conflict present, persistent blocking NOT present ("same-bar only") | **43** | 6.2% |
| Persistent blocking present, same-bar conflict NOT present ("persistent only") | **352** | 50.9% |
| **BOTH present simultaneously** | **273** | **39.5%** |
| Neither present (unexplained residual) | 23 | 3.3% |
| *Same-bar present at all (only + both)* | *316* | *45.7%* |
| *Persistent blocking present at all (only + both)* | *625* | *90.4%* |

**Reading this correctly**: same-bar conflict and persistent blocking are not two alternative
explanations for different subsets of the gap — for the 273 positions in the "BOTH" row, the position
lost its bid for the slot on the SAME bar another strategy also entered, AND a third (or the same)
strategy's older position was independently already occupying the slot at that moment. It is not possible
to say from this data alone which of the two conditions was the "true" proximate cause for those 273 —
both were present. Only the 43 "same-bar only" positions can be attributed cleanly to same-bar
arbitration with no persistent-blocking confound, and only the 352 "persistent only" positions can be
attributed cleanly to an already-open position with no same-bar confound.

**This changes the interpretation from this document's own first draft**: reporting "45.7% vs. 50.9%,
roughly co-equal" (the forced-partition view) implied two comparably-sized, independent causes. The
honest view shows persistent blocking is present in the large majority of the gap (90.4%, whether alone
or combined) while "pure" same-bar-only conflict — the ONLY case a same-bar-specific remedy (e.g.
consensus aggregation, ranked arbitration) would cleanly address without also needing a persistent-
blocking remedy — is a small minority (6.2%, 43 positions). This is reflected in the sharpened
recommendation in §10, and the raw `phase610_prescope_analysis.json` retains both the forced-partition
figures (`forced_partition_*` keys, for continuity with anything already derived from the first draft)
and this honest breakdown (`honest_gap_*` / `pct_gap_*_present` keys) side by side.

---

## 5. Holding-period analysis

| | Legs (matches Phase 6.9A headline units) | | Logical positions (this diagnostic's own unit) | |
|---|---|---|---|---|
| | Competitive (142) | Isolated (823) | Competitive (117) | Isolated (758) |
| Median holding (bars) | 73.5 | 19.0 | 73.0 | 17.5 |
| Mean holding (bars) | 160.7 | 87.8 | 169.4 | 83.4 |
| P90 holding (bars) | 374.0 | 261.0 | 400.4 | 241.6 |
| Max holding (bars) | 2,358 | 4,717 | 2,358 | 4,717 |
| Total slot-bars occupied | 22,816 | 72,224 | 19,817 | 63,209 |
| Top 10% of trades' share of total occupied time | 47.6% | 67.8% | 50.7% | 69.4% |

**A small number of long-held positions dominate occupied slot-time** — confirming `PHASE_6_10_
PREPARATION.md` Open Question 5 directly. In the isolated data, the longest-held 10% of positions (76
of 758) account for **69.4%** of all slot-time ever occupied across the whole 43-strategy population.
The competitive run shows the same pattern at a smaller magnitude (50.7%), consistent with the
competitive run simply having fewer total positions to spread the same underlying market's long-holding
tendency across.

**Exit-reason contribution** (isolated, all 758 positions' worth of legs, 823 legs):

| Exit reason | Trade-legs | % of trades | Median holding (bars) | % of total slot-time |
|---|---|---|---|---|
| Stop-loss | 380 | 46.2% | 19.0 | 52.8% |
| Take-profit | 170 | 20.7% | 82.0 | 43.0% |
| Trailing-stop | 182 | 22.1% | 2.5 | 1.0% |
| Time-stop | 81 | 9.8% | 24.0 | 2.7% |
| Unclassified | 10 | 1.2% | 1.0 | 0.5% |

**Time-stop exits are NOT the driver of the long tail** — they are capped by construction (median 24
bars, matching e.g. S13's own documented `TIME_STOP_BARS = 24`) and contribute only 2.7% of total
occupied slot-time despite being 9.8% of trade count. **The long tail is overwhelmingly stop-loss and
take-profit exits that simply ran a long time before resolving** (a median take-profit exit alone holds
82 bars, and together stop-loss + take-profit account for 95.8% of occupied slot-time). This means a
holding-period-focused remedy (Phase 6.10 option **E**) would need to target *when a still-open,
undecided position releases the slot*, not the existing time-stop mechanism, which is already doing its
narrow job and is not the bottleneck.

---

## 6. Signal redundancy analysis

**What is measurable from existing artifacts:**
- **Direction agreement**: 81.25% of same-bar conflict groups have every strategy agreeing on direction
  (§3) — most competing signals are not fighting, they are duplicating.
- **Entry similarity**: same-bar conflict groups show a small mean entry-price spread (0.68 points),
  consistent with genuinely near-identical fills, though not universally tight (max spread 28.07 points
  — see §3's caveat on differing intra-bar price references across evaluators).
- **Overlapping holding horizon**: covered directly by §4's persistent-blocking measurement — 89.4% of
  isolated positions overlap in time with at least one other strategy's position.
- **Candidate strategy clusters (co-occurrence only, no elimination)**: the clearest candidate pair is
  **S39↔S40** (61 same-direction same-bar co-occurrences — essentially all of either strategy's own
  conflict participation). Secondary candidates: S26↔S43 (12), S4↔S48 (8), S13↔S44 (6), S26↔S4 (6),
  S4↔S40 (6). These are **co-occurrence observations only** — nothing about any strategy's contract,
  parameters, or Health status was changed or should be inferred as a recommendation to change.

**What is NOT measurable from existing artifacts** (stated per the CEO's required protocol):
- **Similar stop, similar target**: `TradeRecord` (the only per-trade granular data captured) carries
  `entry_price`, `exit_price`, `mfe`, `mae` — but no stop-loss or take-profit PRICE LEVEL field. The
  actual stop/target levels each strategy set at signal time are not persisted anywhere the Phase 6.9A
  instrumentation captured (the `FunnelRecorder` only counts signal/scoring/risk OUTCOMES, not the
  `RiskDecision.constraints`/`Sizing` values that would carry stop-distance information).
  - **Missing information, precisely**: the stop-loss and take-profit PRICE LEVELS (or ATR-based stop
    distance) attached to each actionable signal/`RiskDecision`, tagged by `(strategy_id, entry_as_of)`,
    for both the competitive and isolated runs.
  - **Smallest additive instrumentation that would close this gap**: extend
    `phase69a_funnel_recorder.py`'s existing `record_decision_batch()` tap (already monkey-patching
    `harness._risk_manager.evaluate`, already reading `RiskDecision` objects) to ALSO persist, per
    ALLOWED and DENIED decision, the already-computed `decision.constraints` (carries `max_slippage`,
    derived from entry price and `max_slippage_pct`) and `decision.sizing` fields, keyed by
    `(strategy_id, as_of)` in an event-level list rather than the current monthly-aggregate counters.
    This is additive (a new field on an already-read object, same technique already CEO-approved in
    Phase 6.9A §1.1), touches no production file, but is NOT retroactively computable from the JSON
    already on disk — it requires **two new instrumented backtest runs** (competitive + all-43-isolated,
    identical window/config) to actually populate the finer-grained log, since the existing artifacts
    were captured with the current aggregate-only recorder. **Not implemented here — would need its own
    separate CEO approval**, per the CEO's explicit instruction.

**Net assessment**: signal redundancy is real and measurable in direction/timing terms (§3's 81.25%
same-direction figure, plus the S39↔S40 finding), but a *precise* redundancy measure (would two
"agreeing" signals actually have produced near-identical trades, or merely similar direction with
different risk/target) cannot be finished without the additive instrumentation above.

---

## 7. Independent-evidence estimate

| Stage | Count |
|---|---|
| Raw setup detections (portfolio-wide, recomputed directly from `signal_counts`) | 31,409 |
| Signals reaching Risk Manager (ALLOW + DENY) | 1,016,477 (145 ALLOW + 1,016,332 DENY) |
| Executable opportunity count — isolated, no slot contention (trade-legs) | 823 |
| Executable opportunity count — isolated, no slot contention (logical positions) | **758** |
| Economically distinct opportunity count — **lower bound** (strict same-bar dedup) | **564** |
| Economically distinct opportunity count — **upper bound** (temporal-overlap connected components) | 52 (flagged degenerate, see below) |
| Completed trades, competitive (realized evidence, positions) | 117 |

**The lower-bound estimate (564) is the defensible one**: deduplicating only exact-same-bar entries
still finds **~74% of isolated positions (564 of 758) are economically distinct events** — i.e., even
after removing the cleanest, least-ambiguous form of duplication, the large majority of the "5.8×"
headline opportunity gap is not simply the same signal counted 43 times.

**The upper-bound estimate (52) is reported but must be treated as degenerate, not a real estimate**:
because 89.4% of positions overlap something (§4), a connected-components clustering criterion chains
transitively through a handful of very long-duration positions (chiefly S46/S39/S40's own multi-month
holds) and merges large numbers of temporally-distant, almost certainly economically UNRELATED
opportunities into the same "cluster" simply because they both happened to overlap the SAME long-held
position at different times. This is a genuine methodological finding in its own right: **pure temporal
overlap is too coarse a redundancy criterion on its own** — it would need to be combined with the
direction/price/stop-target similarity data flagged as missing in §6 to produce a trustworthy upper
bound. Until that instrumentation exists, **564 (the lower bound) — not 52 — is the number that should
inform Phase 6.10 scoping.**

---

## 8. Limitations and unresolved questions

1. **Opportunity proxy, not the full signal population**: same-bar and persistent-blocking analysis (§3,
   §4) uses the 758 ISOLATED-RUN LOGICAL POSITIONS as the unit of "an opportunity" — i.e., signals that
   already survived Signal Engine → Scoring Engine → Risk Manager → Execution in isolation. The true
   full population (30,239 actionable signals, or 31,409 raw setups) cannot be analyzed this way, because
   `signal_counts` in the existing artifacts is a monthly aggregate with no bar timestamp or direction
   retained per signal. This diagnostic's same-bar/persistent-blocking figures are therefore a
   **conservative, downstream-filtered view** of contention — the true signal-level contention rate is
   almost certainly higher, not lower, than what §3/§4 measure.
2. **The persistent-blocking overlay is a counterfactual, not a historical reconstruction**: it assumes
   all 43 strategies' isolated positions coexist simultaneously, which the real single-slot architecture
   never allowed. The true historical sequence would have resolved each contention event to a single
   winner (via Scoring Engine ranking) whose own OWN presence would then have blocked or not blocked
   later entrants differently than this overlay assumes. This is the same caveat already disclosed in
   the Phase 6.9A report (§2 of `PHASE_6_10_PREPARATION.md`) regarding cooldown-dynamics asymmetry —
   this diagnostic quantifies it more precisely (§4's 1,978 "relationships measured" is an upper-bound
   pressure measure) but does not resolve it.
3. **A materially large, unexplained residual exists between the two runs independent of slot
   contention**: only 67 of the 117 competitive positions (57%) match an isolated position at the exact
   same `(strategy_id, entry_as_of)`; the other **50 (43%) have no isolated counterpart at all** — meaning
   the competitive run produced a position that strategy would NOT have taken alone, at that bar, under
   the current instrumentation's granularity. This is very likely a cooldown-after-loss or other
   shared-account-state divergence between the isolated and competitive runs (an account-level, not
   strategy-level, mechanism — the same caveat Phase 6.9A itself flagged for the 823-vs-142 gap as a
   whole). It was NOT specifically requested by the CEO's five measurement areas, but it is large enough
   (43% of realized competitive positions) that it deserves its own follow-up before treating the
   isolated-vs-competitive comparison as a clean slot-contention-only measurement.
4. **Stop/target-level signal similarity is not measurable from existing data** — see §6's full
   treatment and proposed (not implemented) additive instrumentation.
5. **The upper-bound "economically distinct" estimate (52) is degenerate** — see §7. Only the lower
   bound (564) should be used.
6. **Exit-reason classification relies on a `client_order_id` string-matching heuristic**, verified
   against the actual source construction logic (not guessed), but with a small (1.2%/2.1%)
   "unclassified" residual where no known pattern matched. Immaterial to every conclusion above given its
   size, but not zero.
7. **Window scope unchanged**: identical to Phase 6.9A's own approved, non-holdout window
   (2024-10-23→2025-10-23). Nothing about whether these findings hold in a different regime or a longer
   window was tested — that remains `PHASE_6_10_PREPARATION.md`'s own Open Question 2, still open.
8. **No new simulation was run to produce this document** — every number above is a re-derivation from
   the two existing Phase 6.9A JSON artifacts. The sealed holdout was not opened; no strategy, Scoring
   Engine, Risk Manager, Execution Engine, or Strategy Health code was executed or modified.

---

## 9. Comparison of the Phase 6.10 options (A–I, `PHASE_6_10_PREPARATION.md` §4) against the measured findings

| Option (prep doc's own letter) | Prep doc's one-line note | What THIS diagnostic adds |
|---|---|---|
| A. ACTIVE+WATCHLIST differentiated risk (soft gate) | Would increase slot contention unless paired with a slot-level change | Confirmed: contention is already severe (89.4% of isolated positions get blocked); adding more live-trading strategies without addressing slot contention would make §4's findings worse, not better. |
| B. Hierarchical/Bayesian pooling of evidence | Addresses Health System's own sparsity, orthogonal to slot contention | Unchanged — this diagnostic measured the slot-contention mechanism specifically (§3–§5), which B does not touch. |
| C. Longer evidence windows | Same as B | Unchanged — a longer window does not change same-bar or persistent-blocking dynamics measured here. |
| D. Minimum exploration allocation | Guarantees some slot time to non-ACTIVE strategies | Directly relevant to the §4 finding that 3 strategies (S46/S39/S40) dominate slot occupancy — a guaranteed allocation for victim strategies (S10, S48, S25, S44, S13) would directly counteract the measured blocking concentration, at the cost of displacing the same 3 strategies' own trades. |
| E. Portfolio-level Health scoring | Sidesteps per-strategy attribution | Relevant to the §3 finding that 81.25% of same-bar conflicts are same-direction agreement, but §4.1's honest breakdown shows "pure" same-bar-only conflict (no persistent blocking also present) is only 6.2% of the gap (43 of 691 positions) — this option would cleanly help a small minority of the gap and does nothing for the 90.4%-of-gap persistent-blocking mechanism (§4.1), which is not a same-bar attribution problem. |
| F. Shadow-mode evidence accumulation | Most directly responsive to Phase 6.9A's finding | **Confirmed as the most broadly responsive option by this diagnostic**: it is agnostic to WHICH mechanism (same-bar, persistent, or — per §4.1 — both simultaneously in 39.5% of the gap) caused a given opportunity to be denied; either way, a shadow-tracked hypothetical trade recovers the evidence. The §7 finding that ~74% of isolated positions remain economically distinct even after strict dedup means shadow-tracking would produce genuinely new evidence, not mostly restated duplicates. |
| G. Regime-conditioned evidence | Orthogonal to slot-contention finding | Unchanged — not addressed by this diagnostic. |
| H. Incumbency-until-negative-evidence | Reduces churn, doesn't help fresh strategies | Unchanged — does not address the §4 concentration finding or the §3 same-bar finding. |
| I. Multiple independent slots / multi-symbol expansion | The only option changing the measured bottleneck directly; CEO has explicitly barred implementing it now | This diagnostic's §7 lower-bound finding (74% of isolated positions are economically distinct) means independent slots would likely surface genuinely new evidence, not just noise — but Open Question 1 (would it be net PROFITABLE) remains completely untested by this diagnostic, exactly as `PHASE_6_10_PREPARATION.md` already disclosed. Still not to be implemented. |

---

## 10. Recommended option or recommended experiment

Using the CEO's own lettering for this diagnostic's recommendation (distinct from §9's prep-document
lettering, to avoid conflating the two menus):

> A. Shadow evidence only · B. multi-slot simulation · C. consensus aggregation · D. ranked arbitration ·
> E. holding-period or slot-release redesign · F. strategy clustering · G. another explicitly defined
> option · H. no architectural change

**H (no architectural change) is not supported by the evidence.** The measured gap is large (641 raw
positions, ~74% of it estimated economically distinct even after dedup), dominated by persistent
blocking (present in 90.4% of the gap, §4.1) with a further 39.5% showing both mechanisms entangled, and
concentrated enough (3 strategies causing 57% of blocking) to be addressable without guesswork.

**Primary recommendation: scope A (shadow evidence only) as the first concrete Phase 6.10 design
target.** This diagnostic's own measurements strengthen, rather than merely repeat, `PHASE_6_10_
PREPARATION.md`'s prior leaning toward this option — and the §4.1 correction makes the case for A
*stronger*, not weaker: because 39.5% of the gap shows same-bar conflict and persistent blocking
entangled in the SAME position (not two cleanly separable populations), no mechanism-SPECIFIC remedy
(same-bar-only fix or persistent-blocking-only fix) could cleanly address most of the gap on its own —
only a mechanism-AGNOSTIC remedy like shadow-mode evidence accumulation helps regardless of which
condition (or both) applied to a given denied opportunity. It also targets the specific, now-identified
chronic victims (S10, S48, S25, S44, S13), requires no new capital risk, and the §7 finding that a large
majority of the "lost" opportunity is economically distinct (not mere duplication) means shadow-tracking
it would generate real information rather than noise.

**Two smaller, parallel, lower-cost follow-on investigations are also justified by the evidence
(neither is a substitute for scoping A; both are cheaper next steps, not architecture selections):**

- **Closest to E (holding-period or slot-release redesign), narrowly scoped**: §4/§4.1/§5 together show
  persistent blocking is both the dominant gap mechanism (present in 90.4% of the gap) AND dominated by 3
  specific strategies (S46/S39/S40, causing 57% of all blocking relationships) whose own long holds
  (median 99 bars for the blocking position, top-10%-of-positions consuming ~69.4% of total slot-time) —
  NOT by time-stop-capped trades, which are already working as designed. A targeted look at whether a
  slot-release rule specific to these 3 chronic holders (not a portfolio-wide holding-period change)
  would relieve a large share of the blocking is worth scoping as a narrow follow-on experiment, separate
  from and smaller than a full architectural redesign — and, given persistent blocking's now-confirmed
  dominance, this follow-on is better-justified than a same-bar-specific remedy (see C/D below).
- **Closest to F (strategy clustering)**: the S39↔S40 co-occurrence finding (§3, §6 — 61 same-direction
  same-bar co-occurrences, effectively all of either strategy's own conflict participation) is strong
  enough to justify a dedicated clustering study of which strategy pairs/groups are substantially
  redundant, PURELY AS RESEARCH — no strategy contract, parameter, or Health status is implicated or
  should be changed as a result of this document.

**C (consensus aggregation) and D (ranked arbitration) are weakly supported, more weakly than this
document's own first draft suggested**: both would only cleanly help the "same-bar-only" slice of the
gap — 6.2% (43 positions, §4.1), not the 45.7% headline figure a naive same-bar/persistent split implies
— since the other 39.5% of the gap where same-bar conflict is ALSO present is entangled with persistent
blocking and would not be fixed by a same-bar remedy alone. Neither C nor D addresses the 90.4%-of-gap
persistent-blocking mechanism (§4.1). Materially less broadly responsive than A.

**B (multi-slot simulation)** remains explicitly barred from live/production implementation by prior CEO
instruction (`PHASE_6_10_PREPARATION.md` §6, reaffirmed by this document); a SIMULATION-ONLY exploration
of it (to finally test Open Question 1 — would the additional evidence be net profitable) is a
legitimate, low-risk next research question, but is a separate decision from anything recommended above
and is not being proposed as an immediate next step here.

**No option is selected. No implementation follows this document.** This is a recommendation for what to
scope and investigate next, consistent with `PHASE_6_10_PREPARATION.md`'s own standing instruction that
Phase 6.10 itself "deliberately stops short of designing any single option in detail."

---

## 11. Protected-area confirmation

- No `ai_trader/` source file was read for execution purposes beyond static inspection (confirming
  `client_order_id` construction logic, `TradeRecord` fields, `time_stop.py`/`trailing_stop.py` decision-
  id formats) — nothing was imported or run.
- No simulation was executed. No new backtest, isolated or competitive, was run. The sealed terminal
  holdout was not opened.
- No strategy, its parameters, or its contract was touched. No Scoring Engine, Risk Manager, Execution
  Engine, or Strategy Health scoring/methodology file was modified.
- The only new files created are diagnostic artifacts, following the same preserved-scratch-script
  precedent as `phase69_*.py`/`relevance12m_*.py`/`phase69a_*.py`: `phase610_prescope_analysis.py` (this
  document's own analysis script, reads only) and `phase610_prescope_analysis.json` (its output).
- Official phase status is unchanged: **Phase 6.10 remains NOT STARTED, NOT SCOPED.** This document is
  pre-scope diagnostic material only, per the CEO's own explicit instruction not to update phase status.

**Waiting for CEO review. No further action will be taken until then.**
