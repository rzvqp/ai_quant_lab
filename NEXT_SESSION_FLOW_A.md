# NEXT_SESSION_FLOW_A.md — Alpha Discovery Laboratory (Flow A)

**Scope of this document**: Flow A ONLY — the 40-Edge Alpha Discovery Program. Split out of the
former single `NEXT_SESSION.md` on 2026-07-20, per explicit CEO instruction, so Flow A and Flow B each
have their own operational document. Do not write Flow B (AI Trader Development) content here — see
`NEXT_SESSION_FLOW_B.md` for that. See `NEXT_SESSION.md` for the short, common orientation pointer.

---

## Current state

**Status: EVIDENCE LIMIT REACHED (2026-07-21) — E015-SCALP Phase 0 root-cause investigation CLOSED,
no feasibility verdict issued. A previously-reported "Verdict A — manual replay start works" finding
was RETRACTED as not reproducible under rigorous re-testing (10+ clean attempts across multiple
healthy chart tabs, no successes). A CEO-directed root-cause investigation across 11 candidate
categories (modal state, layout, renderer/session state, timing, coordinates, toolbar state, Pine
overlays, lazy-load/viewport positioning, tab/WebContents identity, CDP target attachment,
cross-tab shared state) could not identify the cause with certainty. Recorded conclusion (verbatim):
"Current evidence most strongly supports Category C (stale/pre-existing replay state), but this
remains an unproven hypothesis due to the lack of an independent manual confirmation." No
implementation or workaround was attempted. Normal 4H chart scrolling and historical data
reachability back through 2023 ARE confirmed sound; the specific unresolved blocker is replay-start
candle *selection* via click. Full detail, falsification table, and what evidence would upgrade or
falsify the conclusion: `edge_research/E015-SCALP_protocol_and_pilot.md` §"Phase 0 — Root-Cause
Investigation of the Non-Reproducible Result (2026-07-21) — CLOSED, EVIDENCE LIMIT REACHED".
**Investigation closed — do not resume without explicit CEO reauthorization. Do not begin E013. Do
not resume E015-SCALP formal validation. Awaiting next assignment.**

**Phase 0A update (supersedes the Phase 0 "NOT FEASIBLE" framing below with a more precise
diagnosis)**: root-caused and fixed a real tooling defect (a "success" report that silently landed
on the wrong date) in the separate `tradingview-mcp` repo's `replay_start` — commit `c839e91`, 45/45
tests passing, live-verified. The fix makes every failure explicit and correctly classified
(`DATA_UNAVAILABLE`/`MODAL_BLOCKED`/`TIMESTAMP_MISMATCH`/`TOOLING_FAILURE`) instead of silently
succeeding on a substituted date — a genuine improvement. **It did not unlock historical replay** via
that API path: every date tested via `replay_start(date=...)` is rejected identically with a native
"Data point unavailable" toast. The 2026-07-21 manual-navigation retry (above) subsequently disproved
the broader "plan/subscription-level restriction" theory this had been assessed as — normal chart
scrolling reaches all 5 frozen pilot dates without issue — but did not find a working alternative to
`replay_start(date=...)` for actually selecting a replay start point.

**What changed**: the CEO redirected the research objective from multi-day structural-behavior
Discovery to testing whether each edge produces an IMMEDIATELY tradable scalp (a mechanically defined
entry/stop/TP=2R trade, resolved within 5-60 minutes at M1 execution resolution) —
`EDGE_RESEARCH_PROTOCOL.md` §9, Protocol v2. Before continuing to E013, or running the requested
E015-SCALP extension, a data-resolution audit was required.

**Data audit result (re-confirmed by direct filesystem check this session)**: `data/market/` contains
**only** `OANDA_XAUUSD_{D1,H4,H1,M15}.csv` — 84,152 M15 bars, 20,833 H1 bars, 5,451 H4 bars, 910 D1 bars.
**No M1, no M5, no tick-level data exists anywhere in this project** — a repo-wide search for M1/M5/tick
CSV files found none (only unrelated matches inside third-party test fixtures in `venv/`). This is the
same gap `EDGE_DISCOVERY_ROADMAP.md` §1 already identified for the Tier-0 history extension, now
independently re-confirmed for this different purpose. **Per the CEO's own explicit instruction ("do
not approximate a 5-minute scalp using H1 bars"), no attempt was made to approximate §9's tests from
M15/H1 data.** §9's own tests, and the requested E015-SCALP extension specifically, cannot be run.

**Governance actions taken at this point** (documentation only, no code/data change beyond the audit
itself): `EDGE_RESEARCH_PROTOCOL.md` §9 registers Protocol v2 in full (the new primary research
question, required horizons, the 11-field mandatory trade simulation, the required outcome
classifications and metrics, the staged A→B→C→D context-discovery process, and this data-resolution
audit requirement itself). Each of E017/E009/E010/E012/E015's own permanent logs (append-only) carries a
"Scope clarification (2026-07-22, Protocol v2)" section stating **"structural-behavior Discovery, not
direct scalping validation"** — none of their V0 results, verdicts, or statuses were changed.

## E015-SCALP Phase 0 — TradingView Replay feasibility pilot (2026-07-22) — VERDICT: NOT FEASIBLE

The CEO subsequently authorized **TradingView Bar Replay on XAUUSD M1** as the execution-validation
source (repository M1 data being absent), and directed a Phase 0 feasibility pilot specifically on
**E015-SCALP — First Order Block Mitigation Immediate Response**, before resuming E013.

**What was done**: confirmed a live CDP connection to TradingView Desktop; reconstructed E015's own
frozen detector to recover real timestamps for all 6,919 visit-1 ("first mitigation") events
(`edge_research/e015_scalp_all_visit1_events.json`); selected a 5-event, outcome-blind pilot sample via
a pre-registered rule (`edge_research/e015_scalp_pilot_sample.json`); froze the confirmation/entry/
stop/TP=2R/timeout/tie-break/cost rules before any replay
(`edge_research/E015-SCALP_protocol_and_pilot.md`); switched the chart to `OANDA:XAUUSD` (matching the
repo's own data provenance) at M1; then attempted to replay to 2 of the 5 pilot events' historical
dates.

**Result**: `replay_start`'s own date-seeking did not work in either test (~3.3 years back, and ~8 weeks
back) — the chart/replay consistently reverted to the live real-time bar instead of the requested
historical date. One attempt surfaced a native TradingView "Data point unavailable" toast (a possible
feed-retention limit); the other showed no such toast, isolating a genuine tool-integration defect
independent of retention (candle-by-candle stepping itself was confirmed precise — `replay_step`
advanced exactly 1 minute once replay was active). Per explicit instruction, no manual/visual workaround
was substituted; the remaining 3 pilot events were not attempted once the blocker was reproduced twice.

**Verdict: C — NOT FEASIBLE**, specifically for automated historical-date seeking with the current
tooling — not a judgment on E015's own structural finding (unchanged) and not a judgment on whether
TradingView Replay could work via a fixed tool or manual operation. Full report, screenshots, and the
complete 5-event mandatory record: `edge_research/E015-SCALP_protocol_and_pilot.md`,
`edge_research/e015_scalp_pilot_events.json`, `edge_research/e015_scalp_evidence/`.

**What would need to change before retrying**: (1) diagnose/fix `replay_start`'s date-seek (or use a
UI-click-based date-picker interaction instead of the parameterized call); (2) separately establish this
feed's actual M1 replay retention window via manual (non-automated) testing. See the full report for
detail.

## Proposed minimal data-ingestion plan (for CEO decision — not started)

To make Protocol v2 (§9) and the E015-SCALP extension runnable at all, this project would need, at
minimum:
1. **XAUUSD M1 OHLCV** (OANDA or an equivalent, methodologically consistent source) covering at least
   the existing clean-research window (2022-12-16 → 2025-10-23, i.e. matching `PRE_HOLDOUT_SPLIT_ID`) —
   ideally the same feed/provider as the existing D1/H1/H4/M15 files, to avoid introducing a
   cross-provider data-quality confound into the comparison.
2. **M5 OHLCV for the same window**, if not trivially derivable from M1 by resampling (M5 can likely be
   built by resampling M1 once M1 exists, avoiding a separate ingestion step).
3. A **disclosed, spread/slippage/cost model** appropriate to M1-resolution XAUUSD execution (the
   existing M15-scale cost conventions used elsewhere in this project's `code/` engine may not directly
   transfer to a 1-minute holding-time trade and should be re-examined, not assumed, once real M1 data
   exists).
4. Confirmation of the **new data's own provenance and volume-field meaning** (the existing M15/H1/H4/D1
   `volume` column is already flagged elsewhere in this project as an unconfirmed OTC/CFD proxy, not
   verified exchange volume — the same caveat would need re-checking for any new M1 feed).
5. **This is a data-acquisition decision, not an edge-research action** — consistent with this
   project's own standing treatment of the Tier-0 history-extension gap (`EDGE_DISCOVERY_ROADMAP.md`
   §1: "data acquisition... is not part of this program's current authorization"). No fetch, download,
   or vendor engagement was attempted or should be attempted without a separate, explicit CEO decision
   on source, cost, and provider.
Following the TERMINAL HOLDOUT BREACH (identified 2026-07-21: all 5 edges studied first — E025, E026,
E028, E029, E032 — had loaded and analyzed data from the Research Lab's own sealed terminal holdout,
2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC; **the old terminal holdout is CONSUMED / INVALIDATED**,
full incident record `PROJECT_STATE_v2.md` §8.23), the CEO authorized and this session completed
holdout remediation: (1) centralized holdout-cutoff enforcement in `edge_research/_common.py::load()`,
with a 17-test suite (`edge_research/test_loader.py`, all passing); (2) a clean rerun of all five
contaminated edges (`e0XX_..._clean.py`); (3) documentation of both the original (contaminated,
preserved verbatim) and clean results in each edge's own permanent log. **Registry status for these 5:
`DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE`.** The CEO then separately authorized **E017 — Equal
Highs / Lows Target** (V0 NOT supported — see below) and, after resolving a factual mismatch (an
earlier reference to "E009 — Previous Day High/Low" did not exist in the registry and was withdrawn),
**E009 — Change of Character Retest** (also V0 NOT supported — see below), both run entirely under the
post-remediation centralized-loader enforcement from the start (no contamination possible). The CEO then
authorized an **"overnight full edge profile" directive (2026-07-22)**: each edge now also gets a
timeframe profile, a 7-horizon/5-ATR-threshold movement profile, a context profile, controls/
falsification, a disciplined V1 search, and robustness checks — see `edge_research/_profile.py`, the
new shared library this required. **E010 — Breaker Block Snatch**, **E012 — Inverted Fair Value Gap**,
and **E015 — Order Block Re-Mitigation** were completed under this directive (all V0 NOT supported as
registered — see below; E010/E012 independently surfaced the same "unbroken zone predicts continuation,
broken/flipped one predicts nothing" pattern via their own natural controls, now registered — CEO
decision — as **CEC-001** in the new `CROSS_EDGE_RESEARCH_CANDIDATES.md`, not a numbered edge, no study
conducted; E015 additionally produced this program's first V1 candidate). Per the same authorization,
this session auto-continues to the next eligible edge without stopping for approval between edges
unless a governance issue arises. The remaining edges are
unaffected and still `UNSTUDIED`/`V0`.

**Governing documents**: `EDGE_DISCOVERY_REGISTRY_v1.md` (the 40-edge backlog), `EDGE_RESEARCH_PROTOCOL.md`
(the six-stage pipeline, the permanent-record rules, and — new as of this incident — §8's mandatory
holdout-exclusion rule), and `EDGE_DISCOVERY_ROADMAP.md` (recommended sequencing, data-availability-
driven; its own top section now records the same pause and remediation-first next action). **New
(2026-07-22)**: `CROSS_EDGE_RESEARCH_CANDIDATES.md` — a registration-only log (not part of the 40-edge
registry, not a Discovery-stage study) for the recurring "unbroken structural zone retains directional
information; broken/flipped one loses it" observation surfaced independently by E010's and E012's own
control groups. CEC-001 there records the exact observations, sample sizes, control definitions,
p-values, and — most importantly — the specific look-ahead/tautology/survivorship risks that make this
NOT yet an accepted edge. Does not change E010's or E012's own conclusions.

## Last Flow A commits

```
eed1634  Flow A: first Alpha Discovery session — Discovery pass on E025/E026/E029/E032/E028
411a04b  docs: record holdout breach and quarantine affected edge research
360a410  Flow A: holdout remediation — centralized cutoff enforcement + clean rerun of 5 edges
be0e8d3  Flow A: E017 Discovery pass — Equal Highs/Lows Target (V0 not supported)
58338d7  Flow A: E009 Discovery pass — Change of Character Retest (V0 not supported)
8b1bcc7  Flow A: E010 full-profile pass — Breaker Block Snatch (V0 not supported)
192f0d2  Flow A: E012 full-profile pass — Inverted Fair Value Gap (V0 not supported)
d43fd93  Flow A: register cross-edge research candidate CEC-001 (governance step, no study conducted)
<pending this session's own commit — E015 full-profile pass — see the E015 report for the exact hash>
```

Re-verify live before trusting this — `git log -1`, `git branch --show-current`, `git status
--porcelain` — do not assume it is still the current HEAD in any future session. This work now lives on
its own dedicated worktree/branch: `C:\Users\MEDION GAMING\ai_quant_lab-alpha-discovery`, branch
`alpha-discovery` (separated from Flow B's own `ai_quant_lab-research-main` / `ai-trader-implementation`
worktree, per CEO decision 2026-07-21).

## Edges studied

**2026-07-20 session, first Discovery-stage pass (later found holdout-contaminated, then remediated
2026-07-21)**: **E025 (Round Numbers) → E026 (ADR Exhaustion) → E029 (Weekly Gap Fill) → E032 (Premium
Discount Flip) → E028 (Fibonacci OTE)**.

**2026-07-21/22 session, run entirely under the post-remediation centralized-loader enforcement (no
contamination possible)**: **E017 (Equal Highs / Lows Target) → E009 (Change of Character Retest) →
E010 (Breaker Block Snatch) → E012 (Inverted Fair Value Gap) → E015 (Order Block Re-Mitigation)** — the
latter three under the "overnight full profile" directive.

Full per-edge evidence, method disclosure, and answers to all 9 mandatory Discovery questions live in
`edge_research/E0XX_<slug>.md` (one file per edge, permanent, append-only), alongside each edge's own
analysis script and JSON/CSV output (also in `edge_research/`, committed). Every studied edge's registry
`Status` field was updated from `UNSTUDIED` to `DISCOVERY_IN_PROGRESS`; every `V0` hypothesis wording is
unedited (per protocol §1) — any informal, unfrozen "V1 candidate" framing suggested by a session's own
evidence lives only in the per-edge logs, never in the registry itself (none of E017's, E009's, or
E010's own logs offer a V1 candidate — see each log for why).

**No Final Verdict was issued on any edge.**

## Results — ORIGINAL (contaminated) vs. CLEAN RERUN (holdout-excluded, 2026-07-21)

**The original results below were HOLDOUT-CONTAMINATED** (see "Current state" above and
`PROJECT_STATE_v2.md` §8.23) — preserved verbatim as an audit trail, per the protocol's own
permanent-record rule; they never supported and still do not support promotion to Frozen Candidate,
Validation, or a Final Verdict. **The clean-rerun column is the one to rely on going forward.** Full
detail, including per-slice/per-session breakdowns, is in each edge's own `edge_research/E0XX_*.md` log.

| Edge | Original (contaminated) headline | Clean rerun (holdout-excluded) headline | Outcome |
|---|---|---|---|
| **E025 Round Numbers** | $50: round vs control p=0.0022 (4h horizon); approach-from-above p=0.0059 | $50 reaction_4 (~1h) CONFIRMS (p=0.00011); reaction_16 (~4h) and approach-from-above subslice no longer clear p<0.05 (p=0.072, p=0.121) | **PARTIALLY WEAKENED** |
| **E026 ADR Exhaustion** | Upside: Spearman r=−0.137, p=2.4e-6; downside null; Asia-only session significance | Upside: r=−0.171, **p=8.4e-8** (stronger); downside null unchanged; Asia-only pattern replicates identically | **CONFIRMED** (strengthened) |
| **E029 Weekly Gap Fill** | Fill rate 88.9%; large-tercile 77.8%, median TTF 11.0h; 43% artifact rate | Fill rate 91.3%; large-tercile 78.3% (CONFIRMS), median TTF 1.875h (**CHANGED**, small-n-sensitive); ~45% artifact rate (CONFIRMS) | **RATE PATTERN CONFIRMED; TTF FIGURE CHANGED** |
| **E032 Premium Discount Flip** | Daily-range Spearman r=0.527, p≈4e-299; weekly r=0.039, p=0.0049 | Daily r=0.522, p≈6.5e-235; weekly r=0.039, p=0.012 | **CONFIRMED** (near-identical, most robust of the five) |
| **E028 Fibonacci OTE** | Shallow 64.6% vs OTE 57.3% continuation rate, χ²=9.28, p=0.0023 | Shallow 63.0% vs OTE 57.0%, χ²=4.89, **p=0.027** (weaker test, same rates) | **CONFIRMED** |

**Open questions carried forward unresolved by the clean rerun** (identical in both runs): E026's
upside effect may still be a session-composition confound (only individually significant in Asia); E029
still lacks a matched intraday-revisitation control; E032 still lacks an overextension-confound control;
E028 still hasn't tested a coarser fractal `k`. None of these are resolved by holdout removal alone.

## Result — E017 Equal Highs / Lows Target (2026-07-21, clean-from-the-start)

**V0 NOT supported — REFUTED-leaning evidence, both sides, robust to every sensitivity check run:**
- **Reach rate, equal vs. isolated control**: no meaningful difference at any of 4 tolerances
  (0.10/0.15/0.25/0.40×ATR) × 3 horizons (1/5/20 trading days) — e.g. primary config (0.15×ATR, 5
  days): highs 93.2% vs 92.6% (p=0.826); lows 87.1% vs 86.2% (p=0.765).
- **Reach rate, equal vs. a random-matched-distance control** (no real swing structure, same distance
  profile): the RANDOM control reaches its target *more* reliably and far faster than real equal-highs/
  lows — highs 98.2% (median 1 bar) vs 93.2% (16 bars), p=0.0067; lows 92.8% (2 bars) vs 87.1% (13
  bars), p=0.043. The opposite direction from a "magnet" story.
- **Reversal magnitude after reach**: no boost from being "equal" — high side even trends the wrong
  direction (equal *less* reversing than isolated, p=0.056 borderline); low side n.s. either way.
- **Distance-quantile-matched comparison and session/volatility slices**: no effect recovered anywhere.
- **No V1 candidate offered** — the distinguishing "equal" property was tested directly and repeatedly
  found to add nothing; see `edge_research/E017_equal_highs_lows.md` for the full analysis, including a
  flagged open question (relevant to E009/E010/E012/E015/E013/E016/E011/E014, the other structure-
  pattern edges) about whether swing points in general carry the "liquidity magnet" property commonly
  claimed for them.

**No Final Verdict issued** (below the ~5-6yr horizon, same as every other edge studied so far).

## Result — E009 Change of Character Retest (2026-07-21, clean-from-the-start)

**V0 NOT supported.** An earlier reference in this session to "E009 — Previous Day High/Low" was
verified against the registry, found not to exist anywhere in it, and withdrawn by explicit CEO decision
before any research began — this pass studies the registry's own real, frozen E009.

- **CHoCH vs. its natural on-topic control, BOS** (both are real structural breaks; the only difference
  is whether the break agrees with (BOS) or contradicts (CHoCH) the preceding trend): no significant
  retest-rate, continuation-rate, or failure-rate difference at the primary config (k=5, 5-day horizon)
  — low-break p=0.516/0.220, high-break p=0.648/0.586 — nor at any of 3 fractal-k values (3/5/8) or 3
  horizons (1/5/20 trading days), nor in any session or volatility slice.
- **Important disclosed methodological finding**: the retest metric itself is close to saturated
  (90-99%) for CHoCH, BOS, **and** a random, no-structure, distance-matched control alike — at this
  swing scale, "does price touch a nearby recently-broken level again" is close to a foregone conclusion
  regardless of structural meaning, limiting how much this dimension alone could have discriminated a
  true effect even if one existed. The continuation and compound-outcome dimensions (86-94%, less
  saturated) told the same null story independently.
- **No V1 candidate offered** — CHoCH's defining property was tested directly against BOS and found to
  add nothing; see `edge_research/E009_choch_retest.md` for the full analysis, including a flagged
  concern (relevant to E010/E012/E015/E013/E016/E011/E014) about retest-metric saturation at this swing
  scale for any future "retest"-flavored edge.

**No Final Verdict issued** (below the ~5-6yr horizon, same as every other edge studied so far).

## Result — E010 Breaker Block Snatch (2026-07-22, full profile, clean-from-the-start)

**V0 NOT supported — one of the cleanest nulls found this program.** Tested on M15 (5,833 breaker
events) and H1 (1,550) — M1/M5 confirmed unavailable anywhere in this project's data.
- **After a breaker flip, continuation in the NEW direction is a coin flip**: 49.9% (M15) / 51.4% (H1),
  with MFE≈MAE at every horizon (1/3/5/10/20/50 bars) and every ATR threshold (0.25-2.0×) — the clearest
  possible signature of non-directional noise. Stable across 3 displacement thresholds (1.2/1.5/2.0×
  ATR), every session, volatility regime, trend context, day of week, and year in the sample.
- **Its own natural control — unflipped (never-violated) order blocks — shows a large, real,
  directional continuation effect instead**: 88.0% (M15) / 86.2% (H1) continuation in their ORIGINAL
  polarity, +1 ATR mean move within 1 bar. The gap between breaker (49.9%) and unflipped (88.0%)
  continuation is enormous (p=5.9e-119, M15) — this control also proves the methodology CAN detect a
  real effect when one exists, sharpening rather than undermining the breaker null.
- **No V1 candidate offered.** The unflipped-OB effect is flagged as a strong candidate for a future,
  separately-registered edge (not folded into E010, which would improperly substitute a different claim
  for V0's own).
- New shared library `edge_research/_profile.py` (movement/context/robustness helpers) built this pass,
  reusable for all edges going forward under the CEO's "full profile" directive.

**No Final Verdict issued** (below the ~5-6yr horizon, same as every other edge studied so far).

## Result — E012 Inverted Fair Value Gap (2026-07-22, full profile, clean-from-the-start)

**V0 NOT supported — the same pattern as E010, found independently.** Tested on M15 (12,433 inverted
FVGs) and H1 (2,898) — M1/M5 unavailable, same as E010.
- **After an FVG inverts, continuation in the NEW direction is a coin flip**: 50.0% (M15) / 52.9% (H1),
  MFE≈MAE at every horizon/threshold. Stable across 3 gap-size filters, every session, volatility
  regime, trend context, day of week, and year.
- **Its own natural control — un-inverted (never-violated) FVGs — shows a large, real, directional
  continuation effect instead**: 86.8% (M15) / 86.2% (H1) in their ORIGINAL role, +0.48 ATR by 1 bar
  (p=4.4e-80, M15). **This is the SECOND independent structural concept this session (after E010's
  unflipped-OB) to show the same qualitative pattern**: an unbroken zone predicts continuation; a
  broken/flipped one predicts nothing — the opposite of what both V0s claim.
- **No V1 candidate offered** — same reasoning as E010.

**No Final Verdict issued** (below the ~5-6yr horizon, same as every other edge studied so far).

## CEC-001 registered (2026-07-22) — before continuing to E015

`CROSS_EDGE_RESEARCH_CANDIDATES.md` created per explicit CEO decision: a registration-only entry for
the E010/E012 pattern above (unbroken zone predicts continuation; broken one predicts nothing) — NOT a
numbered edge, NOT subject to the protocol's stage pipeline, no study conducted. Documents the exact
observations, sample sizes, control definitions, p-values, and (its real content) a serious risk
register — look-ahead bias in the unbroken/unviolated classification itself (it's defined using the
same future window the outcome is measured over), event-definition leakage, tautological continuation
labels, event/outcome window overlap, survivorship, unmatched distance/age between groups, dependent/
repeated samples from the same structural episode — explaining exactly why this is NOT yet an accepted
edge, plus what independent falsification would require. E010's and E012's own conclusions are
unchanged.

## Result — E015 Order Block Re-Mitigation (2026-07-22, full profile, clean-from-the-start)

**V0 NOT supported — but not a flat null; a sharp, well-evidenced DECAY, and this program's first V1
candidate.** Tested on M15 (6,929 order blocks) and H1 (1,875) — M1/M5 unavailable.
- **Reaction is real and large on the FIRST mitigation** (~76% continuation both timeframes, matching
  the magnitude of E010's/CEC-001's own unflipped-OB effect — unsurprising, similar population) **but
  collapses to a random-matched-control-level coin flip (~50-54%) by the SECOND mitigation and stays
  there for the third-plus** — robust across 3 displacement thresholds, every session, volatility
  regime, trend context, and year (visit-1 vs visit-2 χ² p=3.1e-123, M15; p=1.2e-35, H1).
- **Random-matched control confirms this is OB-specific, not generic**: it starts near 50% at "visit 1"
  already (pure noise) and stays flat — unlike the real OB group, which starts high and decays down to
  that floor.
- **V1 candidate (unfrozen, Discovery-stage)**: "An order block's reaction is concentrated in its FIRST
  mitigation; the second and later mitigations show no directional edge over a random-matched control" —
  meets the CEO's own 7 V1 criteria (economic logic, large n, consistent effect, beats control,
  parameter-insensitive, stable across segments/years, not yet cost-tested). Deliberately designed to
  avoid CEC-001's own look-ahead risk — visit numbering is purely sequential/forward-only, not dependent
  on the OB's more-distant future.

**No Final Verdict issued** (below the ~5-6yr horizon, same as every other edge studied so far).

## Limitations (must be respected on any revisit)

- **No Final Verdict is possible yet on any edge studied so far.** The M15/H1/H4/D1 data on disk
  (~3.6 years, 2022-12-16→2026-07-13) is short of `EDGE_RESEARCH_PROTOCOL.md` §2's own ~5-6 year
  requirement for any Final Verdict (including an early REFUTED verdict). Every edge studied so far
  remains in **Stage 2 — Discovery, first pass complete** — not Frozen, not Validated, not
  Walk-Forwarded.
- **Recurring open question across this session's edges, worth closing before further "reversion-
  flavored" edges are studied**: several of the "significant" patterns found (E026 upside, E032
  daily-range) may be restatements of a single, generic, already-known market property — large/
  stretched recent moves partially mean-revert — rather than edge-specific mechanisms. No edge studied
  this session has yet been checked against that generic-reversion control. **E031 (3-SD VWAP) is a
  likely future candidate for the same confound** — worth building the control before or alongside
  studying it.
- No multiple-comparison correction has been applied to any of the above p-values — they are
  Discovery-stage screening signals, not confirmed findings.

## Next step: PAUSED — awaiting CEO decision after E015-SCALP Phase 0A's own verdict C (standing
auto-continue authorization suspended by this specific blocker)

**Per explicit CEO instruction, this session stops after the Phase 0A remediation, its verdict, and
clean commits — no formal E015-SCALP validation, no E013, no other edge, no rule optimization, no
AI Trader implementation.** The replay tooling itself is now fixed (deterministic, correctly
classified failures — `tradingview-mcp` commit `c839e91`); the remaining blocker is data/plan
availability, not code. Options for the CEO to choose from:
1. **Confirm the TradingView plan/subscription tier** for this connection and whether it includes
   extended intraday Bar Replay history — a billing/account question. If it does and something else
   is misconfigured, retry Phase 0 against the same frozen 5-event pilot sample with no code changes
   needed (the remediation is orthogonal to this question).
2. **Acquire repository M1 data** (the originally proposed ingestion plan, still valid, see the git
   history of this section for its full detail) as an alternative to TradingView Replay entirely.
3. **Redirect back to structural-behavior Discovery for now** — resume the Tier 1 sequence at
   **E013 — Mitigation Block Sniping**, then in order **E016, E011, E014**, then the session-timing
   edges **E006, E008, E005, E027** — unchanged, only paused — with every future result continuing to
   carry the "structural-behavior Discovery, not direct scalping validation" label until Stage 2 is
   separately passed for that edge.

## Resume instructions

1. Re-verify git state live: `git branch --show-current`, `git log -1`, `git status --porcelain`.
2. Read, in this order:
   - **This document** — current state, summarized above.
   - **`EDGE_DISCOVERY_ROADMAP.md`** — full data-availability gap analysis (M15 is the finest
     resolution that exists; no tick/M1 data; no DXY/US10Y/XAGUSD/USDJPY/SPX data; no economic
     calendar — 17 of 40 edges are blocked on a data-acquisition decision not yet made) and the
     complete tier ordering.
   - **`EDGE_RESEARCH_PROTOCOL.md`** — the mandatory six-stage pipeline, the permanent-record rules
     (nothing ever deleted or retroactively edited), the 9 mandatory Discovery questions, and the
     5-verdict taxonomy.
   - **`EDGE_DISCOVERY_REGISTRY_v1.md`** — look up the specific edge(s) to continue with: V0
     hypothesis, category, required data/timeframes/instruments/observable variables/measured outcome.
   - **`PROJECT_STATE_v2.md` §1.1/§8.19/§8.20** — how Flow A relates to the rest of the project
     (context only, not required to continue research).
3. **Under the standing "overnight full profile" authorization, new-edge Discovery may continue
   automatically** (one edge at a time, per commit) — stop only for a genuine governance issue (see
   "Next step" above for the exact stop conditions). Verify `git status --porcelain` is clean, and
   confirm `EDGE_RESEARCH_PROTOCOL.md` §8's enforcement is actually present in
   `edge_research/_common.py::load()` (it should require `data_split_id`/`cutoff` and raise if either
   is missing) before relying on any run's own `holdout_excluded=true` claim.
4. If resuming a fresh session (not a direct continuation), report the reconstructed state back to the
   CEO once before proceeding — the standing authorization covers continuing within an already-briefed
   session, not silently skipping the report on a brand-new one.

## Warnings relevant to research

- **`EDGE_RESEARCH_PROTOCOL.md` §9, Protocol v2 (new, 2026-07-22) — BLOCKED, no M1/M5/tick data
  exists.** Do not describe any structural-behavior Discovery result (§§1-8, i.e. every edge studied to
  date) as scalp-tradable or implementable — the correct standing description is "structural-behavior
  Discovery, not direct scalping validation." Do not attempt to approximate a 5/10/15/30/60-minute scalp
  test using M15 or H1 bars under any circumstance — re-verify the data audit above before assuming this
  has changed in a future session.
- **TERMINAL HOLDOUT BREACHED, CONSUMED / INVALIDATED (2026-07-21)** — the old sealed period
  (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC) can no longer be treated as unseen. Do not describe it
  as "intact." Do not describe a future cutoff-enforced rerun as "restoring" it — it does not; only a
  new, separately-designated holdout (not yet decided) would give the project a genuinely unseen period
  again, and that decision has not been made.
- **`EDGE_RESEARCH_PROTOCOL.md` §8 (new, 2026-07-21; enforcement live as of this remediation)**: Alpha
  Discovery may not read, load, aggregate, or use data from a sealed holdout period, under any
  circumstance or research stage. Every future result must record its own min/max date used, bar count,
  data-split identifier, and an explicit `holdout_excluded=true` confirmation — absent evidence
  invalidates the run. Enforced centrally by `edge_research/_common.py::load()` — the module's only
  data-reading entry point; it takes no default split/cutoff and fails closed if either is missing.
- **No edge may be optimized until it becomes profitable.**
- **No negative observation/exception/falsification may ever be removed** from an edge's own permanent
  record, at any stage.
- **No hypothesis may be edited retroactively after seeing results** — refinements are new, appended
  versions (V1, V2, …), never edits to a prior version. V0 itself is frozen forever.
- **No protocol stage may be skipped.**
- **A Final Verdict never itself authorizes implementation** — turning a studied edge into an actual
  strategy requires its own separate, explicit, future CEO decision.
- **Naming**: Flow A's "Alpha Edge" / "Edge" (E001–E040) is a completely different, unrelated concept
  from Phase 6.10's "Edge Portfolio" or Phase 7's "Edge Intelligence" (both `ai_trader/`-internal,
  Flow B concepts). Flow A's "Edge" means a raw, unimplemented research hypothesis in
  `EDGE_DISCOVERY_REGISTRY_v1.md` — never a registered `strategy_id`/`RuntimeEvaluator`. Do not conflate
  the two vocabularies.
- **Flow A does not import `ai_trader` code** — any candidate reuse of an `ai_trader/market_intelligence/`
  concept (e.g. `structure.py`'s swing/BOS/CHoCH logic) is built from scratch, analogous in spirit only,
  never imported directly, per the two-flow separation (`PROJECT_STATE_v2.md` §1.1).
- **Branch/worktree separation now exists (CEO decision, 2026-07-21)**: Flow A's official location is
  `C:\Users\MEDION GAMING\ai_quant_lab-alpha-discovery`, branch `alpha-discovery` — a dedicated git
  worktree, separate from Flow B's own `C:\Users\MEDION GAMING\ai_quant_lab-research-main`
  (`ai-trader-implementation` branch). Do not access or modify the `ai_quant_lab-research-main` worktree
  from a Flow A session, and do not modify `NEXT_SESSION_FLOW_B.md`,
  `STRATEGY_HEALTH_INTEGRATION_POLICY_DESIGN.md`, `ai_trader/`, or any Flow B report/implementation from
  here. Still verify git state live (`git branch --show-current`, `git log -1`, `git status
  --porcelain`) before assuming any prior session's described state still holds — other sessions may
  land commits on this branch too.
