# PORTFOLIO_ARCHITECT_PHASE2A_CALIBRATION_REPORT.md — Calibration Design and Evidence Generation (Flow B roadmap step 2/6)

**Status: ANALYSIS ONLY. No production code written or modified.** Produced per explicit CEO
authorization following the ACCEPTED verdict on Portfolio Architect Phase 2 policy design
(`PORTFOLIO_ARCHITECT_PHASE2_DESIGN.md`, commit `c0fb366`). This report determines whether the Phase 2
design's candidate `STRATEGY_CONCENTRATION_REORDER` policy (design doc §5) has a defensible,
deterministic, non-optimized calibration, using one offline, deterministic, zero-production-diff
instrumented simulation. **Final verdict: C. NOT CALIBRATABLE, for the specific predeclared grid tested.**

---

## 1. Mandatory first step — preconditions reconstructed and confirmed

- Portfolio Architect Phase 1 is CLOSED (CEO verdict, commits `bf41d5e`/`c1b0fd2`) — confirmed.
- Phase 2 design is ACCEPTED (commit `c0fb366`) — confirmed.
- `ArchitectMode.PASSTHROUGH` is the only mode in `ai_trader/portfolio_architect/types.py` — confirmed
  by direct grep (`class ArchitectMode` shows exactly one member); zero other `ArchitectMode.*`
  references exist anywhere in `ai_trader/`.
- No Phase 2 runtime policy exists — confirmed (no code changed by this report).
- Working tree was clean before this work began — confirmed (`git status --porcelain` empty at HEAD
  `c0fb366`).
- Flow A was zero-diff before this work began — confirmed.

All items TRUE. Proceeded per the CEO's own instruction.

---

## 2. Data-source inventory

- **No pre-existing persisted historical simulation output, Shadow Evidence record set, or
  allocation/admission record covering the AI Trader's own 43-strategy universe was found** in the
  repository (checked: no `*shadow*.json`/`.csv` outputs, `results/` contains only Research-Lab
  artifacts unrelated to `ai_trader/`, the prior `ceo_strategy_constraint_root_cause_study.py`
  preserved its own captured event data only for the six A-Candidate strategies at signal/score/decision
  level, not Shadow Evidence trade-leg data, and did not persist a reusable JSON either).
- **Generated fresh, this report**: one new, offline, deterministic, zero-production-diff instrumented
  simulation (`portfolio_architect_phase2a_calibration.py`, repo root) — reuses the EXACT proven
  43-strategy configuration already established by `ai_trader/simulation/tests/
  test_shadow_disabled_parity.py::test_all_43_production_strategies_execute_concurrently_with_
  byte_identical_competitive_execution` (`all_registered_strategies()`, `ManagerConfig(
  auto_admit_min_maturity="EXPLORATORY")`, `use_strategy_runtime=True`, `enable_time_stops=True`,
  `enable_trailing_stops=True`, Shadow Evidence enabled for all 43 strategies).
- **Window used**: `DateRange(1_672_617_600, 1_680_000_000)` — the same bounded, already-validated
  85-day window this project's own 43-strategy tests use, **not** the fuller multi-year non-holdout
  history (e.g. the CEO-approved 2024-10-23→2025-10-23 window `phase69a_funnel_run.py` established for
  the Root-Cause Study). This is a **scope/time limitation, disclosed here, not hidden** — see §8.
- **No live trading results were used or exist in this repository.** No new trading strategy was
  created. No strategy signal, scoring, Strategy Health, Risk Manager, or execution logic was altered.

---

## 3. Predeclared candidate calibration grid (fixed before any result was inspected)

Per CEO Calibration Question 6 (hidden-optimization prevention), the following was fixed in the
analysis script's own docstring **before the instrumented run was executed**, and never revised after
seeing results:

- **Denominator (Question 1)**: total Risk Manager ALLOW decisions (the "admitted" event stream) — the
  design doc's own §9.1 recommended option, and the literal reading of the CEO's own phrasing ("last N
  admitted trades") in Calibration Question 2.
- **Rolling windows (Question 2)**: {10, 25, 50, 100} admitted events — exactly the CEO's own predeclared
  set, no others tested.
- **Minimum-evidence floor (Question 3)**: 25 (reused from Strategy Health's own `MIN_EVIDENCE_TRADES`,
  per design doc §9.7's provisional recommendation) — a strategy's own share is `INSUFFICIENT_EVIDENCE`
  until the window contains at least 25 total ALLOW events (from ANY strategy).
- **Concentration state categories (Question 4)**: 4 states — `INSUFFICIENT_EVIDENCE`, `NEUTRAL`
  (share ≤ 1.5× the window's own "fair share" = 1/N distinct strategies observed), `MODERATELY_
  CONCENTRATED` (≤ 3× fair share), `HIGHLY_CONCENTRATED` (> 3× fair share) — thresholds are relative to
  a principled reference point (fair share), not fit to any outcome.
- **This script never reads, ranks by, or is influenced by net PnL/profitability at any point.**

---

## 4. Analysis methodology

Zero-file-diff instrumentation, identical precedent to `phase69a_funnel_recorder.py`/
`ceo_strategy_constraint_root_cause_study.py`: `harness._scoring_engine.score_batch` and
`harness._risk_manager.evaluate` are monkey-patched, post-`load()`, on the already-constructed instance
only — each wrapper calls the original implementation, returns its result unchanged, and additionally
records it. **Zero lines changed in any `ai_trader/` source file**; the exact same compiled decision
logic ran.

- **A. Distribution analysis**: per-strategy opportunity/eligible/ALLOW/filled/Shadow-isolated-ALLOW
  counts, sparse-history flag (< 25 total ALLOWs).
- **B. Concentration analysis**: for each predeclared window, rolling share/state sequence over the
  global ALLOW event stream; top-strategy turnover; a disclosed, simple ATR-independent calendar-half
  split as a **coarse proxy** for regime sensitivity (explicitly NOT a call into
  `ai_trader.market_intelligence`'s own frozen regime classifier — flagged as a limitation, §8).
- **C. Counterfactual reorder analysis (shadow evaluation only)**: for every bar with ≥2 same-symbol
  candidate opportunities, computed the Phase 2 design's §5 formula's counterfactual order using only
  data strictly before that bar's `as_of`; for bars where the top-ranked candidate would change, replayed
  the reordered candidate list through a **freshly-constructed, separate `RiskManager` instance** (same
  `RiskConfig`, captured `risk_context`/`portfolio_state` snapshots) to determine whether the actual
  ALLOWed strategy would differ — this never touched or fed back into the real harness run, which had
  already completed.
- **D. Stability analysis**: sensitivity of max observed share across the 4 predeclared windows;
  boundary sensitivity (window = 24 vs. 25 vs. 26 — one observation entering/leaving); determinism
  (identical recomputation from the same captured stream, twice).
- **E. Negative controls**: the CEO's own 7 required controls, run directly against the captured data.

---

## 5. Results

**Run scale**: 5,752 bars processed (200-bar warmup + 5,552 scored bars), 238,736 score events,
238,736 decision events, 43 strategies, single symbol (XAUUSD).

### 5.1 Distribution analysis (§A)

- Every strategy was evaluated (scored) on all 5,552 post-warmup bars — `opportunity_count`/
  `eligible_count` = 5,552 for all 43 strategies. **This denominator is uninformative for concentration**:
  it counts every per-bar SCORING pass, not actionable signals or admissions, so it cannot distinguish
  strategies by trading intent — noted as a finding in its own right (§8).
- **Total real (competitive) Risk Manager ALLOW events across the ENTIRE run, all 43 strategies
  combined: 19.** Only 3 of 43 strategies ever received a real ALLOW at all: S46 (11), S39 (7), S10 (1).
  The other 40 strategies received **zero** real allocations in this 85-day window.
- **Total Shadow-isolated ALLOW events (Shadow's own per-strategy risk evaluation, immune to real
  competitive contention) across all 43 strategies: 88.** Richer than the real stream, but still sparse
  per strategy — the highest is S40 (14), followed by S10 (12), S39 (11), S1 (10); 22 of 43 strategies
  have **zero** Shadow-isolated ALLOWs in this window either.
- Every single strategy is flagged `sparse_history: true` (< 25 total ALLOWs) — **all 43, without
  exception**, under the predeclared minimum-evidence floor.

### 5.2 Concentration analysis (§B)

For **every one of the 4 predeclared windows** (10/25/50/100), the concentration-state distribution over
the full run is **100% `INSUFFICIENT_EVIDENCE`** (19/19 ALLOW events, `n_events_with_evidence: 0` in
every window). **No `NEUTRAL`, `MODERATELY_CONCENTRATED`, or `HIGHLY_CONCENTRATED` state was ever
reached, for any window, at any point in the run.** The global ALLOW stream (19 events total) never
accumulates the predeclared 25-event minimum-evidence floor at all — the floor is never crossed even
once across the entire 85-day window.

Top-strategy turnover rate (computed over whatever partial-evidence prior windows existed, pre-floor):
0.059 (roughly 1 change per 17 admissions) — low-confidence given the tiny N.

Calendar-half split (coarse regime proxy, §4): first-half top-strategy share = 0.556, second-half =
0.600 — both computed from ~9–10 events per half, too few to draw a regime-sensitivity conclusion from.

### 5.3 Counterfactual reorder analysis (§C)

- 5,552 bars had ≥2 same-symbol candidate opportunities (multi-candidate bars exist in abundance — this
  is NOT the limiting factor).
- **0 of those bars produced a changed order** under the §5 formula, because every share computation
  returned `None` (insufficient evidence) for the entire run — with all shares undefined, every
  candidate's priority key falls through entirely to the Scoring-Engine `rank` tie-break, which is
  identical to the original order by construction.
- **0 bars required a Risk Manager replay** (none were candidates, since no reorder ever occurred).
- **Total actual ALLOW count under the tested policy: 19 — identical to PASSTHROUGH's own 19**, trivially
  (aggregate-capacity-neutrality invariant holds, but vacuously, since the policy never activates).

### 5.4 Stability analysis (§D)

- Max-share-by-window: `null` for all 4 windows (no window ever had a defined share).
- Boundary sensitivity (24/25/26): `null` for all three (same reason).
- **Determinism**: confirmed — recomputing the full concentration-state sequence twice from the same
  captured stream produced byte-identical results.

### 5.5 Negative controls (§E)

| Control | Result |
|---|---|
| 1. Random strategy-ID permutation must not create an apparent benefit | `null` vs `null` — **not evaluable**: with zero defined shares, there is nothing for a permutation to show a spurious benefit against. Not a pass in any meaningful sense; the control could not run under real conditions. |
| 2. Equal shares reproduce original order | **PASS** — confirmed for all 5,552 multi-candidate bars. |
| 3. Missing evidence reproduces original order | **PASS** — mechanically identical to control 2 in this run, since ALL evidence was missing throughout. |
| 4. Single-opportunity batch unchanged | **PASS** (structurally guaranteed by construction; 0 single-opportunity batches occurred in this particular run to exercise it empirically, noted honestly). |
| 5. Health-ineligible strategies never reappear | **NOT APPLICABLE** — this baseline run had no Strategy Health `health_eligible_ids` filter active (matching Phase 1's own PASSTHROUGH-equivalent baseline convention); this control needs its own dedicated run with a filter active to be meaningfully exercised. |
| 6. Risk Manager ALLOW-count identical | **PASS**, vacuously (§5.3). |
| 7. Only `rank` field ever changes | **Guaranteed by design** (`dataclasses.replace(o, rank=...)`, §5 of the design doc) — a structural property of the specification, not independently re-derivable from this data capture alone. |

**Controls 1 and 5 did not run under real, exercising conditions** — this is itself evidence of the same
sparsity problem, not a clean pass. Disclosed plainly rather than reported as "7/7 passed."

---

## 6. Key finding — evidence sparsity, not absence of concentration

The real competitive ALLOW stream (19 events over 85 days, 43 strategies) is **too sparse for the
predeclared minimum-evidence floor (25) to ever be reached within the tested window**, using the tested
denominator. This is not a case of "no concentration exists" — the 19 real ALLOWs that DID occur are, if
anything, sharply concentrated (S46 alone: 11/19 = 58%; S46+S39: 18/19 = 95%; 40 of 43 strategies: 0%) —
but there are simply too few of them, too infrequently, for a rolling-count-based evidence floor to ever
authorize the policy to act before the window itself has mostly rolled past.

This mirrors, structurally, the exact lesson already learned and encoded in Strategy Health's own
`shadow_gate.py` design: gating a mechanism's own evidence on a resource that is itself scarce (there,
competitive trades for Strategy Health; here, competitive ALLOWs for Portfolio Architect's own
concentration metric) risks the mechanism never having enough evidence to function — the same shared-
slot scarcity the Root-Cause Report originally diagnosed as the reason Portfolio Architect is needed at
all is *also* the reason its own most natural calibration input starves.

---

## 7. Required verdict

## **C. NOT CALIBRATABLE**

for the specific predeclared grid tested: denominator = real Risk Manager ALLOW count, windows =
{10, 25, 50, 100} admitted events, minimum-evidence floor = 25, over the 85-day/43-strategy window. The
available evidence does not justify authorizing this concentration-aware reorder policy as calibrated —
it would be a permanent, silent no-op (always `INSUFFICIENT_EVIDENCE`, always PASSTHROUGH-equivalent
behavior) for the entire tested evidence base, which is itself a form of failure against the CEO's own
acceptance criteria (a calibration that can never activate is not "usable with limitations" — it is
simply unexercised).

**This is not a profitability verdict** and does not claim the underlying concept (portfolio-level
concentration awareness) is wrong — only that the specific, predeclared calibration input tested here
does not have enough real-ALLOW evidence, at this window scale, to support it.

No frozen candidate specification is provided, per the CEO's own instruction ("IF VERDICT A OR B" —
this is verdict C).

---

## 8. Unresolved limitations (explicit, not silently resolved)

- **Window scope**: only the bounded 85-day test window was used, not the fuller, already-CEO-approved
  non-holdout window (2024-10-23→2025-10-23, `phase69a_funnel_run.py`'s own established precedent) or
  the full multi-year non-holdout history. A longer window would very likely accumulate more real ALLOW
  events and could reach the evidence floor — this is **plausible but UNTESTED**, not verified here, and
  would require its own fresh, separately-predeclared Phase 2A-2 pass (not a retroactive substitution
  within this verdict).
- **Denominator alternative, observed but not formally tested**: the Shadow-isolated ALLOW stream (88
  events aggregate vs. 19 real) is richer but still sparse per strategy in this same window (only 4 of 43
  strategies exceed 10 events; none reach 25) — noted as a supplementary, exploratory observation from
  data already captured, explicitly NOT a second formal test against the predeclared grid, and not itself
  sufficient evidence that this alternative would calibrate either. It also changes what "concentration"
  conceptually measures (isolated per-strategy signal frequency, not real competitive/capital dominance)
  — a genuine architectural tradeoff, not just a data-availability fix.
- **"Total eligible opportunities" as a denominator (Question 1's first candidate) is empirically
  uninformative** in this run — every strategy trivially scores 5,552 (one per bar), since Signal
  Engine produces a signal for every strategy every bar regardless of actionability. This candidate
  denominator was analytically weak by design (§9.1 of the Phase 2 design doc already anticipated related
  concerns) and this run's own numbers confirm it empirically.
- **Regime-sensitivity analysis used a coarse calendar-half-split proxy**, not `ai_trader.
  market_intelligence`'s own frozen regime classifier — a genuine Market Intelligence integration was out
  of scope for this pass's own time/effort budget; the coarse proxy itself was too low-N (≈9-10 events
  per half) to draw any conclusion regardless.
- **Negative controls 1 and 5 did not run under real, exercising conditions** (§5.5) — both need either
  more real evidence (control 1) or a dedicated Strategy-Health-filtered run (control 5) to be
  meaningfully re-tested.
- **No profitability signal was examined at any point**, per the CEO's own explicit prohibition — this
  report cannot and does not speak to whether the underlying strategies are "good," only to whether the
  specific calibration input has enough evidence to drive a reorder policy.

---

## 9. Final calibration verdict (restated)

**C. NOT CALIBRATABLE**, for the predeclared grid as tested. The evidence-sparsity failure mode is
concrete, measured, and matches one of the CEO's own explicitly anticipated falsification conditions
("concentration does not persist [long enough for evidence to accumulate before the policy could act]").
A longer window and/or an alternative denominator remain plausible, untested avenues for a future,
separately-authorized, freshly-predeclared calibration attempt — not decided or implicitly endorsed here.

---

## 10–13. Governance confirmation

- **Focused commit hash**: reported after this report and the calibration script/data are committed
  together (see final message to CEO — commit created immediately following this document).
- **Working tree status**: confirmed clean immediately before commit (verified via `git status
  --porcelain`).
- **Flow A zero-diff**: confirmed — `git status --porcelain -- NEXT_SESSION_FLOW_A.md edge_research
  EDGE_DISCOVERY_REGISTRY_v1.md EDGE_RESEARCH_PROTOCOL.md EDGE_DISCOVERY_ROADMAP.md` returns empty.
- **PASSTHROUGH remains the only active runtime behavior**: confirmed — no `ArchitectMode` beyond
  `PASSTHROUGH` exists in `ai_trader/portfolio_architect/types.py`; the calibration script
  (`portfolio_architect_phase2a_calibration.py`) lives entirely outside `ai_trader/`, is deterministic,
  never imports or activates any new mode, and never touched Risk Manager, Strategy Health, Signal
  Engine, Scoring Engine, Shadow Evidence semantics, Execution Engine, production harness behavior, or
  Flow A.
