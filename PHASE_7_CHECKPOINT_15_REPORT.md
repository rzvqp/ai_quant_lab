# Phase 7 — Checkpoint 15: Decision Intelligence v1 vs v2 Falsification Study

**Validation label: TARGETED VALIDATION PASSED.** Per the CEO's own Checkpoints 14–15 batch policy,
only the new `decision_comparison` package's own tests, `mypy --strict` scoped to it, and targeted
coverage were run at this checkpoint's own close. The combined Context Memory + Decision Intelligence
validation and the full-repository run happen next, per the batch's own closing rules (§8 below).

## 1. Mission

Build the complete comparison framework between Decision Intelligence v1 and v2, per the CEO's own
explicit rule: **the goal is falsification, not confirmation** — "nu presupune ca v2 este mai bun." This
checkpoint neither modifies v1, v2, nor Context Memory; `ai_trader/decision_comparison/` reads their
already-produced outputs only (verified by the same import-independence/write-detection static scan
used at every prior checkpoint's own close).

## 2. The Central, Disclosed Structural Fact This Study Is Built Around

Checkpoint 14's own architecture makes `DecisionReportV2.recommended_strategy_id` construction-time-
enforced to equal `v1_report.recommended_strategy_id` — Context Memory was explicitly forbidden from
influencing eligibility, ranking, scoring, Risk, Position Sizing, or Execution at that stage. This means
several of the CEO's own named comparison dimensions — **final recommendation, NO TRADE frequency, edge
selection, expectancy, win rate, drawdown, false positives, false negatives, and regime robustness (as
measured by the recommendation stream)** — are all downstream FUNCTIONS of "which strategy_id, if any,
was recommended on a given bar." Since that stream is provably identical between v1 and v2, these
metrics are provably identical too — this is a logical consequence of Checkpoint 14's own design, not an
assumption this study makes for convenience. `trade_outcome_proof.py` states this proof explicitly and
computes `equivalence_holds` by DIRECTLY comparing the paired recommendation stream (never by assuming
it) — a genuine divergence, if one ever occurred, would be caught and reported, not silently hidden.

**This checkpoint deliberately did NOT re-run an expensive multi-hour backtest to "confirm" P&L metrics
that are already provably identical by construction** — doing so would be a purposeless computation
producing a foregone conclusion, contrary to this project's own established discipline against
purposeless work. The proof itself (backed by a direct pairwise comparison over real market data, §5) is
the rigorous artifact; a second backtest would add nothing but wall-clock cost.

## 3. What CAN Genuinely Differ — Confidence Calibration and Explanation Quality

Two of the CEO's own named dimensions are NOT downstream of the recommendation stream and were measured
for real:

- **Explanation quality** (`explanation_quality.py`): a deterministic completeness checklist — whether
  each candidate's Context Memory attachment discloses why the context was found, what evidence exists,
  what limitations apply (when any exist), and why the evidence status is what it is. v1 has ZERO
  Context-Memory-derived content on any candidate; whenever v2 attaches evidence to even one candidate,
  it strictly adds explanatory content v1 could never have produced — `v2_strictly_more_explanatory_content`
  reports this directly, never a subjective score.
- **Confidence calibration** (`calibration.py`): whether Context Memory's own point estimate
  (`mean_normalized_result`) carries measured predictive skill against REAL realized outcomes — sign
  agreement rate and Pearson correlation, pure stdlib machinery. **`n_samples == 0` is the honest,
  first-class result today**: Context Memory's repository holds no real AI Trader historical
  observations yet (Checkpoint 14's own disclosed limitation), so this dimension cannot be measured for
  real in this checkpoint — only its measurement machinery is built and tested (7 tests, synthetic data:
  perfect/zero sign agreement, missing predictions excluded correctly, Pearson correlation on perfect
  positive correlation and on zero-variance/single-sample degenerate inputs).

## 4. Framework Coverage of Every CEO-Named Dimension

| CEO dimension | Where covered | Status this checkpoint |
|---|---|---|
| Final recommendation | `recommendation.py::compare_recommendations` | Measured directly; 0 divergences over real data |
| NO TRADE frequency | same | Measured directly (identical v1/v2 by construction) |
| Edge selection | same | Measured directly (identical v1/v2 by construction) |
| Expectancy / win rate / drawdown | `trade_outcome_proof.py` | Provably identical (proof, not re-simulated) |
| False positives / false negatives | same | Provably identical (same proof) |
| Stability / regime robustness (recommendation-level) | same | Provably identical (same proof) |
| Confidence calibration | `calibration.py` | Machinery built + tested; `n_samples=0` on real data (disclosed) |
| Explanation quality | `explanation_quality.py` | Measured directly; v2 strictly richer whenever evidence attaches |

No dimension was silently skipped or omitted — every one has real, tested code, and every one's current
result is disclosed exactly as measured, including the ones that are provably trivial under the current
architecture.

## 5. Real-Data Proof

`test_falsification_study_over_real_market_data_yields_v1_remains_active` drives 20 real XAUUSD bars
through `make_decision()` and `make_decision_v2()` (with a populated synthetic Context Memory index for
strategy S1), runs `run_falsification_study()` over the paired output, and confirms: 20/20 compared, 0
divergences, `trade_outcome_equivalence.equivalence_holds is True`, verdict `V1_REMAINS_ACTIVE`.

## 6. Falsification Verdict

**`V1_REMAINS_ACTIVE`.** No measured or measurable trade-outcome benefit exists for v2 over v1 under the
current integration architecture — their recommendation streams are provably identical, so every
P&L-relevant metric is identical too. v2's only measured difference from v1 is additional, genuinely
richer explanatory content per candidate; its potential predictive value (confidence calibration) is
unmeasurable today for lack of real historical Context Memory data. **Per the CEO's own explicit rule —
absent proof of a v2 benefit, v1 remains the active system.** This is not a default choice; it is the
measured, structurally-proven result of this study, reached the same way regardless of which pair of
real reports is examined (proven, not merely observed, by `DecisionReportV2`'s own construction-time
invariant).

`FalsificationVerdict.V2_SUPERIOR_CONFIRMED` exists in the type vocabulary but is **not reachable** by
`run_falsification_study()` under the current architecture — reaching it would require a future,
separately-authorized checkpoint that lets Context Memory's evidence actually influence a decision,
which this project has not authorized and this checkpoint does not propose.

## 7. Tests / Targeted Coverage / mypy Result

24 tests: recommendation comparison (empty input, full agreement, genuine-divergence detection via a
deliberately-bypassed invariant), trade-outcome-equivalence proof (both branches), explanation-quality
completeness (no evidence, failed-retrieval-with-no-report, fully-populated-SUFFICIENT-evidence),
calibration machinery (7 tests covering both branches of every code path), falsification orchestration
(no divergence, divergence, empty input), a 4-test import-independence/write-detection/harness-reference
static scan, and one real-data end-to-end integration test.

```
coverage report (--source=ai_trader.decision_comparison, --omit tests/):
    __init__.py                 8 stmts   0 miss   100%
    calibration.py              34 stmts   0 miss   100%
    explanation_quality.py      30 stmts   0 miss   100%
    falsification.py            20 stmts   0 miss   100%
    recommendation.py           26 stmts   0 miss   100%
    trade_outcome_proof.py       8 stmts   0 miss   100%
    types.py                    53 stmts   0 miss   100%
    TOTAL                      179 stmts   0 miss   100%

mypy --strict ai_trader/decision_comparison/ --exclude 'tests/'
    -> Success: no issues found in 7 source files
```

## 8. Protected-Path Verification

`git diff --stat 0346e07 HEAD -- ai_trader/decision_intelligence/` empty (v1 untouched since Checkpoint
7). `git diff --stat dbcdb66 HEAD -- ai_trader/decision_intelligence_v2/` empty (v2 untouched since
Checkpoint 14's own close). `git diff --stat 2445785 HEAD -- ai_trader/context_memory/` empty (Context
Memory untouched since Checkpoint 13's own close). `git status --porcelain` before staging showed only
`ai_trader/decision_comparison/` (new) plus this report.

## 9. Files Changed / Commit Hash / Working Tree Status

New: `ai_trader/decision_comparison/__init__.py`, `types.py`, `recommendation.py`,
`trade_outcome_proof.py`, `explanation_quality.py`, `calibration.py`, `falsification.py`, and `tests/`
(8 files: `__init__.py`, `test_recommendation.py`, `test_trade_outcome_proof.py`,
`test_explanation_quality.py`, `test_calibration.py`, `test_falsification.py`,
`test_import_independence.py`, `test_integration.py`) — 15 files total.

- Branch: `ai-trader-implementation`
- Parent commit: `dbcdb66` (Checkpoint 14)
- This checkpoint's commit hash: recorded after commit, see final session output.
- Working tree: clean after commit, verified before the post-Checkpoint-15 combined validation begins.
