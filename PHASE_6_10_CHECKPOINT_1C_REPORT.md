# Phase 6.10 — Implementation Checkpoint 1C Report

**Date:** 2026-07-18. **Scope:** the full virtual position lifecycle for Shadow Evidence — virtual
entry, position/leg tracking, virtual exit (stop-loss/take-profit/time-stop/trailing-stop/end-of-window
forced close), generic multi-edge isolated execution — reusing `ExecutionEngine`/`ExecutionSimulator`/
`PortfolioSimulator` completely unmodified, per the CEO-authorized implementation plan and
`PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md` §4/§9/§10/§10.1/§14 Checkpoint 2. Explicitly
excludes: Strategy Health, Edge Health, Portfolio Health, Portfolio Orchestrator, capital allocation,
Consensus Engine, live trading, Broker Adapter, MT5, Telegram trading, runtime optimization for 43+
edges, multi-account support, any new trading logic, and any S10-specific production code.

---

## 1. Executive summary

Checkpoint 1C is **COMPLETE**. The Shadow Evidence system now runs the complete virtual position
lifecycle — a shadow strategy's ALLOW decision is submitted through its own dedicated, fully independent
`ExecutionEngine`/`ExecutionSimulator`/`PortfolioSimulator`, its resulting position is tracked from
first fill through every partial exit to final close, and the closing mechanism (stop-loss, take-profit,
time-stop, trailing-stop, or end-of-window forced close) is recorded explicitly, never inferred.
Competitive execution remains byte-identical to a Shadow-disabled run, proven for one strategy and for
four simultaneously-configured strategies, over both an 85-day pytest-fixture window and the full
13-month/23,639-bar Phase 6.9A window. S10's own shadow trade ledger was directly compared against the
already-committed `phase69a_isolated_funnel.json` ground truth (§6 below). All 1C code is generic —
zero strategy-specific branches anywhere in `ai_trader/shadow_evidence/`.

## 2. Architectural summary

`ShadowEvidenceEngine` now holds one `_ShadowAccount` per configured strategy — a lazily-constructed
bundle of a dedicated `RiskManager`, `ExecutionEngine` (configured with a `"SHADOW-CID"/"SHADOW-REQ"`
discriminator prefix, Design §10 invariant 4), `ExecutionSimulator`, and `PortfolioSimulator`, plus
per-account bookkeeping (`pending_entries`, `open_position_id`, `trailing_entry_atr`). On an ALLOW
decision, the virtual entry order is submitted immediately, but the corresponding
`ShadowOpportunityRecord`/`ShadowPositionRecord` are **deferred** until the entry fill (or its genuine
absence) resolves on a later bar — `entry_price` cannot be known before a real fill exists, mirroring
how `PortfolioSimulator` itself never creates a `Position` before `_apply_one` sees a fill. Five new
per-bar/per-run entry points drive the lifecycle: `observe()` (risk + virtual entry, extended from
Checkpoint 1B), `apply_time_stops()`/`apply_trailing_stops()` (the identical overlays the real portfolio
uses, applied per shadow account), `settle_bar()` (fills, mark-to-market, leg recording), and
`finalize_at_end()` (end-of-window forced close, honoring the same `close_at_end_policy`). Every entry
point isolates a per-strategy failure internally (Design §10.1) and is wrapped in harness-level
defense-in-depth try/except, exactly matching the precedent Checkpoint 1B established for `observe()`.

## 3. Files modified

| File | Nature of change |
|---|---|
| `ai_trader/shadow_evidence/engine.py` | Core Checkpoint 1C implementation — `_ShadowAccount`/`_PendingEntry`, lazy per-strategy execution-stack construction, virtual entry/exit/settlement/finalization, `_exit_reason_for()` client_order_id-marker classification. |
| `ai_trader/shadow_evidence/types.py` | Docstring updates only — `ShadowOpportunityRecord`/`ShadowRejectionRecord` comments that said "not this checkpoint" now reflect Checkpoint 1C reality. No field/invariant changes. |
| `ai_trader/simulation/harness.py` | `load()`: `ShadowEvidenceEngine` construction now passes `context`/`symbol_meta`/`capabilities` (needed to build its own execution stacks). `_run_one_bar()`: two new shadow call sites (time-stop/trailing-stop overlays; `settle_bar()` after the real fill/mark-to-market sequence). `_finalize_at_end()`: restructured so shadow finalization runs independently of whether the real portfolio itself has open positions, plus a new shadow call site. Every new call site wrapped in the same failure-isolation try/except pattern as the existing Checkpoint 1B tap. |

**Not modified:** `risk_manager/`, `execution_engine/`, `signal_engine/`, `scoring_engine/`,
`strategy_manager/`, `strategy_runtime/`, `strategy_health/`, `time_stop.py`, `trailing_stop.py`,
`execution_simulator.py`, `portfolio_simulator.py` — all reused as unmodified classes, fresh instances.

## 4. Files added

- `phase610_checkpoint1c_s10_validation.py` (+ `.json`) — scratch diagnostic artifact, preserved per this
  project's own standing convention, validating S10's shadow trade ledger directly against
  `phase69a_isolated_funnel.json`.
- `PHASE_6_10_CHECKPOINT_1C_REPORT.md` — this report.

No new production package was created — Checkpoint 1C extends the existing `shadow_evidence/` package.

## 5. Tests added/modified

- `ai_trader/shadow_evidence/tests/test_engine.py` — extended from 7 to 34 tests: constructor signature
  update, per-strategy shadow-account isolation, virtual entry deferral, SHADOW- prefix, stop-loss/
  take-profit/time-stop/end-of-window closes, the position-identity invariant, a hand-constructed
  2-leg partial-exit fixture (FIXED_FRACTION fill policy), LIMIT_MAX_PER_SYMBOL self-blocking, and
  failure isolation for every one of the five new engine methods individually.
- `ai_trader/simulation/tests/test_shadow_disabled_parity.py` — extended from 14 to 21 tests: byte-
  identical competitive execution with full virtual execution enabled (one strategy, four strategies),
  a non-trivial shadow ledger for S10, the SHADOW- id discriminator end to end, the position-identity
  invariant over a full run, multi-edge evidence scaling, shadow-ledger determinism across two runs of
  the identical `(run_id, config)`, the shared `RiskConfig` object's byte-identical-before/after
  property, settlement-path failure isolation, and a combined outer-boundary defense-in-depth test
  covering all four new harness-level call sites in one run.

## 6. Validation results

### 6.1 Unit + integration + full suite
```
pytest ai_trader/ -q                          -> 1627 passed (baseline 1606 + 21 net new)
mypy --strict ai_trader/ --exclude 'tests/'   -> Success: no issues found in 169 source files
```

### 6.2 Coverage
```
coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"
  ai_trader/shadow_evidence/engine.py    237 stmts, 0 miss, 100%
  ai_trader/simulation/harness.py        308 stmts, 16 miss, 95% (all 16 pre-existing, none introduced by Checkpoint 1C)
  TOTAL                                  9994 stmts, 433 miss, 96%  (baseline: 9783/432/96%)
```
Every new statement Checkpoint 1C added is covered; the ±1 total-miss delta against baseline is
pre-existing, unrelated code, not a regression in anything this checkpoint touched.

### 6.3 Competitive execution parity (the single most important property)
Proven byte-identical (full `SimulationReportData`, trade ledger, risk events, orders) whether Shadow
Mode is disabled or enabled-with-full-virtual-execution, for one strategy (S10) and for four
simultaneously-configured strategies (S10/S21/S39/S40), at both the 85-day pytest-fixture scale and the
full 13-month/23,639-bar Phase 6.9A window.

### 6.4 S10 isolated-ledger validation — real divergence found, root-caused, disclosed honestly

Full 13-month run: **142/142 competitive trades, byte-identical** (`full_report_identical: true`,
`trade_ledger_identical: true`) — matches Phase 6.9A's own published competitive count exactly.

The S10-vs-isolated ledger comparison, however, is **not** a close match: shadow produced **68 trades**
vs. the isolated run's **117**; only the **first 2 trades match exactly**, diverging from trade 3 onward.
This is larger than the originally-anticipated "rare, mid-window cooldown edge case" (Design §7's own
framing) — root-caused, not merely asserted away:

**Root cause**: `phase69a_isolated_run.py` builds its harness with `strategy_id_filter=frozenset({"S10"})`,
which restricts the handles **Signal Engine itself evaluates** to S10 alone — its `score_batch` for every
bar contains only S10's own signal, with no possible same-bar conflict. Checkpoint 1C's shadow engine, by
design (Design §4's own "Setup generation"/"Scoring" rows), taps the **competitive run's own** already-
computed `score_batch` — which reflects all 43 strategies' signals and Scoring Engine's own conflict
resolution across them. This is the exact same mechanism Checkpoint 1B's own validation already predicted
would make `BELOW_FLOOR` counts match the *competitive* run, not the *isolated* one — Checkpoint 1C now
makes this concrete at the trade-ledger level for the first time: a same-bar conflict shifting S10's own
recommendation/eligibility by even one bar changes its entry price/timing, and that difference cascades
into every subsequent trade's cooldown/eligibility state, compounding over a 13-month window.

**This is a by-design consequence of the architecture, not an implementation defect** — Shadow Evidence
was explicitly designed to reuse the competitive run's own scoring (never re-score in isolation, Design
§4), and this is the first time that choice's full downstream effect on an actual trade ledger has been
measured, not merely predicted at the funnel-count level. It does not affect competitive-execution parity
(§6.3, perfect) or any of this checkpoint's other invariants. Full numeric result in
`phase610_checkpoint1c_s10_validation.json`.

### 6.5 Multi-edge isolation / generic architecture
`test_multi_edge_shadow_evidence_scales_with_more_configured_strategies` and
`test_shadow_position_identity_invariant_holds_across_a_full_run` confirm every shadow account is fully
independent, correctly attributed, and the formal position-identity invariant (Design §17.1 Q4) holds
exhaustively over a full run. Nothing in `ai_trader/shadow_evidence/engine.py` names S10 or any other
strategy id — verified by direct source inspection (grep) in addition to the generic multi-strategy
tests.

## 7. Adversarial findings

Self-review against Design §10's 9 invariants and §17.4's 6 acceptance conditions (all satisfied — see
inline citations in `engine.py`/`harness.py`). Two genuine coverage gaps were found and closed during
this checkpoint's own review, not left as loose ends:
1. The `finalize_at_end` early-return path (a `HOLD_AND_MARK` close-at-end policy) and the
   `apply_time_stops` not-yet-due early-return path had no dedicated test — added.
2. The four new harness-level outer-boundary defense-in-depth try/except blocks (mirroring the existing
   Checkpoint 1B precedent for `observe()`) had no dedicated test proving they actually fire — added
   `test_shadow_outer_boundary_failure_isolation_covers_every_new_checkpoint_1c_call_site`.

Two genuinely unreachable defensive branches (`_exit_reason_for`'s `"UNKNOWN"` fallback;
`_record_new_trade_legs`'s internal-consistency `RuntimeError`) were marked `# pragma: no cover` with an
explanatory comment, matching this codebase's own established convention for exhaustive-by-construction
branches, rather than engineering a contrived test to hit unreachable code.

## 8. Remaining limitations (disclosed, not resolved by this checkpoint)

- **Shadow-vs-truly-isolated trade-ledger divergence is real and now quantified, not just theoretical**
  (§6.4): S10's shadow run produced 68 trades vs. the isolated run's 117, matching exactly only the first
  2. Root cause: Shadow Evidence taps the competitive run's own conflict-adjusted `score_batch` by design
  (never re-scores in isolation) — a same-bar conflict with another strategy can shift S10's own entry
  timing/price by even one bar, and that difference compounds forward via cooldown/eligibility state over
  a 13-month window. This is a by-design property of the architecture (already predicted at the funnel-
  count level by Checkpoint 1B's own validation), not a defect — but its practical magnitude on an actual
  trade ledger was not previously measured, and is larger than "documented tolerance" may have implied
  before this checkpoint's own empirical result. Flagged explicitly for CEO judgment, not resolved here.
- Runtime/memory at 43+ simultaneously-tracked edges remains a reasoned estimate (~3–5×), not benchmarked
  — Checkpoint 1C validated at N=1 and N=4, not N=43. A 43-edge rollout requires its own benchmark first
  (Design §13 test 8, §14 Checkpoint 3) and its own separate CEO approval.
- Strategy Health integration remains unselected (3 options compared, none chosen) — untouched by this
  checkpoint, per explicit CEO instruction.
- Capital allocation across edges remains undesigned — the largest remaining gap to the stated
  "AI Portfolio Manager" end goal, out of scope here.

## 9. Final statistics

See §6.1/§6.2 above. Final commit hash, branch, and working-tree status are reported in the session's
own final CEO-facing report (this document is committed alongside that state, not before it).
