# Edge Research Protocol

**Program**: 40-Edge Alpha Discovery Program. **Applies to**: every edge in
`EDGE_DISCOVERY_REGISTRY_v1.md`, without exception. **Protocol version: v2 (updated 2026-07-22)** — §9
adds the Immediate Scalping Response Protocol (CEO directive) as an additional, later-stage check
alongside §§1-8's own structural-behavior Discovery pipeline; see §9.1 for how the two relate. §9's own
tests are currently BLOCKED project-wide — no M1/M5/tick data exists (§9.6).

## 0. Purpose and philosophy

The 40 entries in the registry are raw research hypotheses, not strategies. This protocol exists so
that all 40 are studied under one identical, disciplined procedure — so results are comparable across
edges and so no edge is quietly implemented, adjusted, or declared "true" without having earned it
through the same gates as every other edge.

Two rules govern everything that follows, restated here because they are the ones most likely to be
violated by accident under normal research pressure:

1. **The goal is discovery, not confirmation.** An edge's initial description (however it is worded in
   the registry, however confidently the CEO or anyone else states it) is a starting hypothesis, not a
   fact. If the CEO says "it only works on Tuesday," the correct response is to test whether that is
   true — not to encode it as a filter and move on. The research may discover the real condition is
   different (only Tuesday *and* Wednesday; only after the Asia range; only in low volatility; only
   without news nearby) — or that no real condition exists and the edge should be refuted outright.
2. **An edge's job in this program is to survive falsification, not to be made profitable.** No edge may
   be tuned, filtered, or parameter-searched until it "works." If the raw hypothesis loses money, that
   is a valid, complete, and useful result — not a reason to keep adjusting until it doesn't.

## 1. Mandatory permanent record — kept for every edge, forever

For every edge, from the moment it enters Discovery, the following must exist and must never be
deleted, overwritten, or retroactively rewritten:

- **V0** — the original hypothesis exactly as registered in `EDGE_DISCOVERY_REGISTRY_v1.md`. Frozen at
  registration. Never edited.
- **All observations** — every data point/finding produced during Discovery, whether it supports,
  contradicts, or is neutral to the hypothesis. Negative and null observations are recorded with the
  same weight as positive ones and are never removed once recorded, at any later stage.
- **All discovered conditions** — every condition found to matter (day, session, volatility regime, news
  proximity, filter, instrument state, etc.), including conditions that *reduce* the edge's apparent
  value, not only ones that improve it.
- **All exceptions** — specific instances where the edge behaved unlike the general pattern, kept as
  data even if they cannot yet be explained.
- **All falsifications** — every test, control comparison, or out-of-sample check that failed to
  confirm the edge, recorded with the same rigor as a successful test. A falsification is not evidence
  to be argued away; it stands as part of the edge's permanent record.
- **All successive versions** — V1, V2, V3, … each one a new, dated, appended entry representing a
  refinement of the hypothesis based on what Discovery found (e.g. V0 "works on Tuesday" → V1 "works
  Tuesday and Wednesday, conditional on low ADR consumption"). A new version is *added*, never a
  replacement that erases what came before.
- **Final Verdict** — the terminal classification once (and only once) the edge completes every stage
  below (§3).

This record lives in a per-edge, append-only research log. This protocol defines the requirement; the
log files themselves are created only when an edge actually enters Discovery (not created by this
protocol document itself — see §6).

## 2. Required study horizon

Every edge must be studied across **approximately 5-6 years of history** before a Final Verdict may be
issued. A shorter window may be used for an early Discovery pass (to cheaply check whether an edge is
even worth the full study), but no Frozen Candidate, Validation, or Walk Forward stage may complete, and
no Final Verdict may be issued, on less than the full ~5-6 year horizon. This is a materially longer
window than any prior study in this project (all prior Strategy/Root-Cause/Atlas work used a single
fixed 1-year window) — the data-acquisition implications of this are addressed as a prerequisite in
`EDGE_DISCOVERY_ROADMAP.md`, not resolved here.

## 3. The six mandatory stages

Every edge must pass through these stages, in this order, with no stage skipped and no stage re-entered
after a Final Verdict is issued (a refuted or inconclusive edge does not get silently re-tried under a
new hypothesis without registering that as a new, separate V-version with its own visible history).

### Stage 1 — V0 (Registration)

The raw hypothesis as written in the registry. No data has been examined yet. Entry condition: the edge
exists in `EDGE_DISCOVERY_REGISTRY_v1.md`. Exit condition: a Discovery study is authorized to begin.

### Stage 2 — Discovery

An open-ended, exploratory pass across the available history, answering — for this specific edge — all
nine questions in §4 below. Discovery is where the hypothesis is allowed to change shape: the edge may
turn out to work under a narrower, wider, or entirely different condition than V0 stated. Every such
finding is recorded as a new version per §1, with the evidence that produced it.

Discovery ends in one of two ways:
- **Promotion to Frozen Candidate** — a specific, precisely-worded version of the hypothesis (which
  condition, which filter, which regime) is written down, based only on the data examined so far.
- **Early Refutation** — Discovery itself can be enough to issue a Final Verdict of REFUTED if the edge
  shows no signal whatsoever across a reasonably thorough look, without needing to proceed through
  Frozen Candidate/Validation/Walk Forward. This is explicitly allowed so that a clearly dead edge is
  not dragged through unnecessary later stages — but the same permanent-record requirements (§1) still
  apply, and REFUTED is still a Final Verdict subject to §3 Stage 6's own rules.

### Stage 3 — Frozen Candidate

The specific hypothesis version selected at the end of Discovery is **frozen**: its exact wording,
conditions, and parameters are written down and locked before any further data is examined. This is the
control against p-hacking — once frozen, the candidate's definition cannot be adjusted based on how
Validation or Walk Forward results come out. If Validation fails, the correct response is a Final
Verdict reflecting that failure (or, if warranted, a **new**, separately-versioned candidate re-entering
Discovery) — never a silent edit to the frozen definition.

#### Discovery Identity (added 2026-07-21, CEO governance directive — applies to every V1 candidate
frozen from this point forward; does not retroactively reopen any already-frozen candidate)

Every frozen V1/Discovery Candidate contract must open with a short **Discovery Identity** block,
immediately before its own numbered contract items, containing:

1. **Edge ID** and **V1 candidate name** (short, descriptive label, e.g. "E014-V1 — Compression-Driven
   False-Breakout Fade").
2. **Parent V0** — the frozen, verbatim registry hypothesis this candidate descends from.
3. **Date frozen** and **freezing commit hash** (the commit that closed the contract, once known).
4. **Discovery classification** — per Protocol v2 §9's own labeling convention, e.g.
   "structural-behavior Discovery, not scalping-validated."
5. **Status**: always "Discovery Candidate" at this point in the pipeline — explicitly not validated
   alpha, not a production signal, not an execution rule, not a trading strategy, until it clears
   Stages 4-6.
6. **Authorizing decision reference** — the CEO decision (by date/topic) that accepted the candidate.

This is a documentation-format enhancement only — it does not change any scientific verdict, does not
require rerunning any already-frozen candidate, and does not reopen E014-V1 or any other
already-closed contract.

### Stage 4 — Validation

The frozen candidate is tested against the remaining, previously-unexamined portion of the ~5-6 year
history (data not used to shape the Discovery-stage findings). This is the first point at which the
frozen, specific version of the hypothesis is checked against data it was not built from.

### Stage 5 — Walk Forward

The frozen candidate is tested in a rolling, sequential fashion across the full history (train-on-past,
test-on-next-unseen-slice, repeated forward through time) — checking not just "does it work once
out-of-sample" but "does it keep working as time moves forward," and whether performance is stable or
decaying/regime-dependent.

### Stage 6 — Final Verdict

One terminal classification, chosen from the taxonomy in §5, written with the same numeric/evidentiary
rigor already established as house convention in this project (see `MECHANISM_REGISTRY.md` for the
existing style this program's verdicts should match). A Final Verdict is not the end of the permanent
record (§1 continues to apply — the full V0→verdict history stays attached to the edge forever) — it is
the end of *this* research cycle for *this* version of the edge.

## 4. The nine questions every edge's Discovery stage must answer

Regardless of category, Discovery must produce an explicit, evidenced answer to each of the following
for that specific edge — "not enough data to tell" is an acceptable answer to any of these, but it must
be stated, not left implicit:

1. Does the edge exist at all (any signal distinguishable from noise)?
2. How often does it occur (frequency)?
3. On which days does it work?
4. On which days does it fail?
5. In which sessions does it work?
6. In which volatility regimes does it work?
7. Are there filters that improve it?
8. Are there conditions that invalidate it?
9. Does it survive out-of-sample testing?

These questions are deliberately open (§0.1) — e.g. question 3/4 do not presume "Tuesday" or any other
specific day is either the answer or excluded; the answer is whatever Discovery finds, including "no day
dependency detected" or "a day dependency exists but disappears once [X] is controlled for."

## 5. Final Verdict taxonomy

A dedicated taxonomy for this program (distinct from, but modeled after, the existing
`MECHANISM_REGISTRY.md` taxonomy already in use in this repository, for consistency of house style):

| Verdict | Meaning |
|---|---|
| **CONFIRMED-ROBUST** | Survives Validation and Walk Forward across the full history with a stable, well-characterized condition set; no material regime-dependence found |
| **CONFIRMED-CONDITIONAL** | Real signal exists, but only under specific, precisely-stated conditions discovered during research (a narrower or different condition than V0) |
| **INCONCLUSIVE** | Data insufficient, contradictory, or too thin to support any of the other verdicts |
| **OVERFIT-IN-SAMPLE-ONLY** | Appeared to work during Discovery/Frozen Candidate definition but failed Validation and/or Walk Forward |
| **REFUTED** | No signal found; the hypothesis, in every version tested, does not distinguish from noise/cost drag |

None of these five verdicts is itself authorization to implement anything. Per the CEO's explicit
instruction opening this program, moving from a Final Verdict to actual implementation is a separate,
future, separately-authorized decision — not an automatic next step of this protocol.

## 6. Where future research artifacts will live (not created by this document)

This protocol only defines the procedure. The per-edge, append-only research logs required by §1 do not
exist yet — none will be created until an edge is actually authorized to enter Discovery. When that
happens, the expected convention (for consistency, not yet enforced by any code or tooling) is one
file per edge, e.g. `edge_research/E0XX_<slug>.md`, containing that edge's full V0→verdict history in
one place. No such file, or `edge_research/` directory, has been created as part of this protocol
document.

## 7. Explicit prohibitions (restated verbatim from the CEO's own program directive)

- No edge may be optimized until it becomes profitable.
- No negative examples/observations may be removed from an edge's record, at any stage.
- The hypothesis may not be modified retroactively after seeing results — refinements are new, appended
  versions (§1), never edits to a prior version.
- No edge may skip a stage in §3.
- A Final Verdict does not authorize implementation, strategy creation, or any code change — that
  requires a separate, future, explicitly-authorized decision.

## 8. Mandatory holdout exclusion (added 2026-07-21, following the TERMINAL HOLDOUT BREACH incident —
`PROJECT_STATE_v2.md` §8.23)

**Background**: on 2026-07-21 it was confirmed that all five edges studied in this program's first
research session (E025, E026, E028, E029, E032) had loaded and analyzed data from the Research Lab's
own sealed terminal holdout (2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC), because the shared Flow A
data loader applied no date cutoff at all. **The old terminal holdout is CONSUMED / INVALIDATED** as a
result. This section is the resulting mandatory rule.

**Implementation status (updated 2026-07-21, CEO-authorized remediation)**: the loader-level
enforcement described below is now implemented, in `edge_research/_common.py::load()` — the module's
only data-reading entry point. `load(tf, *, data_split_id, cutoff)` requires both arguments (no
defaults; a missing/empty/unparseable value raises `HoldoutConfigError` or `TypeError`, fail-closed —
it never silently falls back to loading the full, unfiltered file); the cutoff is applied as an
exclusive upper bound on the UTC `dt` column BEFORE any indicator is computed; every successful call
returns an auditable metadata dict (`data_split_id`, `holdout_cutoff`, `holdout_excluded`,
`min_date_used`, `max_date_used`, `n_bars_used`, `n_bars_before_cutoff`, `n_bars_excluded_by_cutoff`,
`loader_version`, `timeframe`) satisfying every item required below. `edge_research/test_loader.py`
(17 tests) verifies exact-boundary behavior, fail-closed configuration handling, metadata correctness,
and that no edge script bypasses this loader. The approved cutoff for the current remediation batch is
`2025-10-23T09:15:00+00:00` (`_common.RESEARCH_HOLDOUT_CUTOFF_UTC`); the split identifier is
`pre_holdout_2025-10-23T09-15-00Z_v1` (`_common.PRE_HOLDOUT_SPLIT_ID`). This does not restore the old
sealed holdout — it produces a holdout-clean rerun only; a new, separately-designated holdout (if the
CEO chooses to define one) is a distinct, future, unmade decision.

- **Alpha Discovery may not read, load, aggregate, or otherwise use data from a sealed holdout period,
  under any circumstance.** This applies to every stage and every kind of analysis without exception:
  Discovery, negative controls, falsification checks, parameter exploration, and every analysis script,
  regardless of whether the holdout data would appear to support or refute the hypothesis under study.
- **The temporal limit must be enforced centrally, in the shared loader(s)**, not left to each analysis
  script to remember individually — the exact failure mode that produced this incident (a shared loader
  with no cutoff, silently trusted by five independent scripts).
- **Every result produced from this point forward must record, alongside its findings**:
  - the minimum date actually used;
  - the maximum date actually used;
  - the number of bars used;
  - the data-split identifier the run claims to respect (e.g. "research" vs. "validation-OOS" vs.
    "holdout" — see the Research Lab's own `PROJECT_STATE_v1.0.md`/`PROJECT_AUDIT.md` §D split);
  - an explicit `holdout_excluded=true` confirmation.
- **The absence of this evidence invalidates the run.** A result that does not carry all five items
  above is not a valid Discovery-stage (or any later-stage) result under this protocol, regardless of
  what its own findings say.
- **Accidental holdout access must be reported as an incident, in the open, in the affected edge's own
  permanent research log and in the project's own official state documents — it can never be repaired
  retroactively by silently dropping the offending bars and re-presenting the same run as clean.** A
  contaminated run stays contaminated; the only remedy is a fresh, clean rerun that itself satisfies the
  five requirements above from the start.

## 9. Immediate Scalping Response Protocol — PROTOCOL v2 (added 2026-07-22, CEO directive)

**Scope change, explicit and non-retroactive**: §§1-8 above define what this document now calls
**structural-behavior Discovery** — does a market-structure concept produce a statistically
distinguishable directional signal at all, tested over multi-bar/multi-day horizons. This section adds
a **second, separate, additional** research question that a structural-behavior Discovery result does
**NOT** by itself answer:

> After the event is confirmed, does a mechanically defined trade initiated immediately or on the first
> valid retest reach TP = 2R before SL = 1R within a short, session-relevant time horizon?

**Every edge studied to date under §§1-8 alone (E017, E009, E010, E012, E015) is a structural-behavior
Discovery result ONLY, not a direct scalping validation** — this label is retroactively attached to
those five edges' own permanent logs (as an appended scope clarification, not a change to any V0,
verdict, or conclusion) and applies to every edge studied under §§1-8 alone going forward, unless and
until that edge separately passes the extension defined below.

### 9.1 Relationship to §§1-8

This is an **additional, later-stage check**, not a replacement for Stage 2 (Discovery) under §3. An
edge must still complete a structural-behavior Discovery pass (or already have one) before an
Immediate Scalping Response study is meaningful — there is no market-structure signal to test the
speed/tradability of otherwise. Passing this section's own tests does **not** by itself authorize
implementation (§7's own standing rule continues to apply in full) — it only tells the CEO whether a
structural-behavior finding is *additionally* a candidate for closer, cost-aware, execution-level study,
which itself would still require its own separate Frozen Candidate → Validation → Walk Forward →
Final Verdict pipeline under §§3-6 before any real-world consideration.

### 9.2 Mandatory data resolution — NOT NEGOTIABLE

- **M1 is the required execution-resolution dataset.** M5 may be used for setup confirmation where the
  edge's own concept calls for it. M15/H1 may be used for higher-timeframe context only, never as a
  substitute for M1 execution.
- **Approximating a 5/10/15/30/60-minute scalp using M15 or coarser bars is explicitly prohibited.** An
  M15 bar cannot resolve which of a 2R target or a 1R stop was hit first within a 15-minute window, nor
  can it establish sub-15-minute latency between event confirmation and threshold-touch — attempting to
  approximate this from M15 closes/highs/lows would silently manufacture a result the data cannot
  support.
- **If M1 (or credible tick-level) data is not available for the instrument/period in question, this
  section's own tests may not be run at all** — not with a caveat, not "as an approximation," not scaled
  down to whatever resolution happens to exist. The correct action is to stop, report the exact gap
  (§9.6), and await a separate, explicit data-acquisition decision — mirroring this project's own
  standing rule for the Tier-0 history-extension gap (`EDGE_DISCOVERY_ROADMAP.md` §1).

### 9.3 Required time horizons

5, 10, 15, 30, and 60 minutes, plus "until session end" where session structure is relevant to the
edge's own concept. These are fixed, disclosed checkpoints — not searched for a favorable one.

### 9.4 Mandatory trade simulation — per event, mechanically defined in advance

1. Event confirmation time (from the edge's own structural-behavior definition, unchanged).
2. Earliest valid entry time (immediate, or first valid retest — defined per edge, disclosed, not
   tuned to the outcome).
3. Entry price.
4. Stop-loss rule (structural, e.g. beyond the zone/level that defines the event).
5. Risk distance (entry to stop).
6. TP = 2 × risk distance (fixed 1:2 RR, per this section's own standing convention).
7. Maximum holding time (one of §9.3's horizons).
8. Tie-breaking rule for a bar that touches both TP and SL (must be pre-registered per edge — e.g.
   "assume the worse outcome," "use sub-bar path reconstruction from M1 if available," disclosed before
   any result is examined).
9. Spread (disclosed, instrument-appropriate).
10. Slippage (disclosed, instrument-appropriate).
11. Transaction costs (disclosed, instrument-appropriate).

**Every event must be classified** as: TP hit first / SL hit first / timeout / invalid setup /
ambiguous intrabar path (and the ambiguous-path rate itself must be reported, not silently resolved by
assumption unless item 8's own pre-registered tie-break rule genuinely resolves it).

**Required reported metrics**: win rate, loss rate, timeout rate, invalid rate, expectancy in R, profit
factor, average and median holding time, MFE in R, MAE in R, maximum losing streak, sample size, a
confidence interval, and the result net of costs. **For a 1:2 RR trade, the relevant comparison is the
approximate break-even win rate after costs (≈33-35% depending on the exact cost model), not 50%** —
comparisons against 50% are a category error for an asymmetric-RR trade and must not be used.

### 9.5 Context discovery — staged, not an unrestricted search

- **Stage A**: test the edge alone (no context conditioning).
- **Stage B**: test each context variable individually (first-vs-repeated occurrence, session, HTF
  direction, trend/range, volatility regime, displacement strength, sweep presence, acceptance/
  rejection, position within session/daily range, proximity to session open, fresh-vs-aged level, and
  any other variable the specific edge's own concept motivates — not an arbitrary list).
- **Stage C**: test only a small number of interactions, and only ones justified by Stage B's own
  results plus market logic — never an unrestricted combination search.
- **Stage D**: any improved variant is registered as a new, separately-versioned V1 candidate — never a
  retroactive edit of V0 or of an already-issued Stage-A/B/C result.
- **Multiple-testing correction and a minimum sample-size threshold are mandatory** at every stage;
  results below the threshold, or unadjusted for the number of comparisons made, may not be reported as
  confirmatory.

### 9.6 Data-resolution audit — required before any edge enters this section's own testing

Before running ANY Immediate Scalping Response study, the exact raw timeframes physically present in
`data/market/` must be (re-)verified and reported: as of 2026-07-22, this is
**D1, H1, H4, M15 only — no M1, no M5, no tick-level data exists anywhere in this project**
(re-confirmed by direct filesystem audit this session; consistent with `EDGE_DISCOVERY_ROADMAP.md` §1's
own prior finding, not a new discovery). **This means Section 9's own tests cannot currently be run for
any edge, on any instrument, in this project.** Any future session must re-verify this audit before
assuming it still holds, and must not proceed past this check by substituting coarser data.

### 9.7 Standing rule

No edge's structural-behavior Discovery result (§§1-8) may be described, in this project's own
documentation, as a validated scalp opportunity, a tradable setup, or evidence of tradability, until it
has separately passed this section's own tests. The correct standing description for every edge studied
under §§1-8 alone is: **"structural-behavior Discovery, not direct scalping validation."**
