# AI_TRADER_S5_OPERATIONAL_SHADOW_VALIDATION_REPORT

**Mandate**: `AI-TRADER-S5-OPERATIONAL-SHADOW-VALIDATION-001`
**Scope**: operational correctness of the ALREADY-BUILT S5 real-evidence pipeline under realistic repeated
operation. No strategy/EV/threshold/risk-policy change was made or is proposed here.

## 1. Lineage (mechanically verified, not reconstructed from the mandate prompt)

All commit hashes below were independently confirmed to exist (`git cat-file -t` + `git log --oneline -1`)
in their respective repos, with subject lines matching the citation chain already embedded in
`s5_ev_evidence.py`'s own module docstring:

| Commit | Repo | Verdict |
|---|---|---|
| `633bd5da` | `ai_quant_lab` | `RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001` = `INDEPENDENT_VALIDATION_PASS` |
| `8228ded` | `ai_quant_lab` | `RT-S5-EV-ESCROW-AGGREGATE-EXTRACTION-001` = `EXTRACTED + BRACKET_FAIL` (E98) |
| `9cfcc5f` | `ai_quant_lab` | `STAT-S5-EV-AGGREGATE-RECONCILIATION-001` = reconciliation PASS; withdrew the erroneous `n_stop>=99` floor |
| `b4cb441` | `ai_quant_lab` | `RT-S5-EV-AGGREGATE-RESTAMP-001` = `VERIFIED + READY_FOR_RUNTIME_PACKAGING` (E99) |
| `1e2af14` | `ai_quant_lab-research-main` | `VE-S5-REAL-EV-RUNTIME-PACKAGING-001` -- packages the above into the runtime |
| `c30b056`, `fb078b5` | `ai_quant_lab-research-main` | `AI-TRADER-S5-CANONICAL-ONBOARDING-001` -- S5 strategy plugin onboarding (predates `1e2af14`) |

**Reconciliation math (read directly from `9cfcc5f`/`b4cb441`/`8228ded`'s own commit messages, not
assumed)**: the escrow extraction (`8228ded`) found aggregates `n=295, n_target=15, n_horizon=196,
n_stop=84, sum_horizon_r=+102.2125` (GROSS, since `ve_brain._ev_core` subtracts round-trip cost once,
separately) and flagged `BRACKET_FAIL` because `n_stop=84 not in [99,147]`. The Statistician
(`9cfcc5f`) found the `>=99` floor was its OWN mis-derivation -- the inequality actually bounds
`n_LOSERS >= 99` (133 total losers = 84 stop-outs + 49 negative-horizon exits), not `n_stop` specifically
-- and formally withdrew the floor. Independent cross-checks in that same commit: gross avg R
`63.2125/295=0.214280` vs. published `0.214`; WR `162/295=0.549153` vs. published `0.549`; gross pinned
to the ratified BASE/STRESS cost ratio within `0.034%`. Red Team then re-stamped
(`b4cb441`) the artifact `VERIFIED + READY_FOR_RUNTIME_PACKAGING`, values byte-identical (fingerprint
changed `fe6eaf9f`->`ff1384a2` for status/reconciliation metadata only -- the economic values did not
move).

**`s5_ev_evidence.py`'s `S5_REAL_EV_EVIDENCE_V1` constant, read in full and cross-checked field-by-field
against the above**: matches exactly (`n=295, n_target=15, n_horizon=196` -> derived `n_stop=84`,
`sum_horizon_r=102.2125344478`, `credibility=0.80`, `evidence_fingerprint=9ca6e2bd...`,
`source_artifact_fingerprint=ff1384a2...`). No discrepancy found.

## 2. Runtime identities

- `RealEVDecisionEngine.engine_version = "real-ev-engine-v1"` (`REAL_EV_ENGINE_VERSION`)
- Verified against `ve_brain` version `0.1.3` only (`_VERIFIED_VE_BRAIN_VERSIONS`); construction fails
  closed (`RealEVAuthorityError`) on any other installed version.
- S5 identity: `strategy_id="s5_c_2d587447_opening_range_breakout_long"`,
  `strategy_version="rep_7472f3d412f2"`, `config_fingerprint="S5-frozen-spec:session=ny,mode=breakout,
  side=up,stop=or_opp,exit=rr3;tick=0.01;or_bars=4;entry_window_bis=4-20;hold_bars=48;rr=3.0"`.
- Cost model used in this validation run: `CostModel(cost_model_id="AI_TRADER_SHADOW_COST_MODEL_v1",
  full_spread_price=0.0, entry_slippage_price=0.12, exit_slippage_price=0.12)` -- sums to `0.24`, exactly
  matching `S5_REAL_EV_EVIDENCE_V1.round_trip_price` (STRESS scenario), so the evidence's own
  `evidence_cost_model_id`/`evidence_round_trip_price` identity-binding check passes genuinely, not by
  coincidence.

**Finding (not a defect, a discovered scope gap in a PRIOR artifact)**: the S5-specific soak from the
prior onboarding mandate (`soak/s5_soak.py`) used its own ad hoc `CostModel(cost_model_id="s5-soak-cost-
v1", ...)`, which predates `1e2af14` and does NOT match `S5_REAL_EV_EVIDENCE_V1`'s declared identity --
running that script unmodified today would trip `EVIDENCE_COST_IDENTITY_MISMATCH` on every cycle rather
than reaching a genuine EV computation. `s5_soak.py` is left untouched (out of this mandate's scope to
modify prior-mandate deliverables); this mandate's own replay script
(`soak/s5_operational_replay.py`, NEW) uses the correct, evidence-matching cost model instead.

## 3. Environment

- `venv\Scripts\python.exe` (main repo venv), `ve_brain==0.1.3` installed.
- `AITraderLiveShadow` Scheduled Task: untouched throughout (never stopped, restarted, or reconfigured);
  running on its own old, unrelated commit as before.
- `BROKER_ORDER_SUBMISSION` / `BrokerOrderSubmissionGate.enabled`: `False` throughout, asserted as a
  precondition at the start of every replay run.

## 4. Dataset / replay (section 10)

Synthetic-but-mechanically-faithful multi-day NY-session bar sequences (same formulas
`s5_opening_range_breakout.py`/`s5_soak.py`/the onboarding test fixtures already use and cite -- the
real, 295-trade validation ledger remains sealed escrow and was never touched). Alternating
breakout/non-breakout days (day parity), never engineered to avoid either outcome.

- **Synthetic date range**: epoch-anchored `1970-01-01 14:45 UTC` -> `1970-02-09 20:45 UTC` (first/last
  `market_timestamp` = `53100` / `3444300` raw seconds) -- 40 consecutive synthetic NY sessions. These are
  disclosed synthetic timestamps (epoch-day-indexed, same convention as this codebase's own test
  fixtures), not real historical dates -- the real dataset is the sealed 295-trade ledger, inaccessible
  per every prior mandate's own disclosure.
- **Sessions**: 40 (20 breakout, 20 non-breakout), 32 M15 bars/session = 1280 bars total.
- **Cycles completed** (bars with a valid ATR, i.e. a real pipeline evaluation, excluding the ~14-bar
  warmup and excluding exact restart-duplicates): 1273.
- **S5 hypotheses produced**: 20 (one per breakout day -- the strategy only ever emits a hypothesis on
  its own qualifying breakout bar, exactly its own `evaluate()` logic, never once per cycle).
- **EV evaluations**: 20 (one per hypothesis; `RealEVDecisionEngine.decide()` invoked genuinely each
  time, never mocked, never skipped).
- **TRADE_DECISION**: 20 / 20 hypotheses (100% of this run's canonical-geometry breakouts).
- **NO_TRADE**: 1253, distribution: `NO_STRATEGY_SIGNAL=1253` (no breakout signal that cycle -- honest
  absence, not a rejected hypothesis), plus the 20 TRADE_DECISION cycles themselves resolve
  `final_decision=NO_TRADE` too (reason `BROKER_DISABLED`) since broker submission is structurally
  disabled -- see section 8. No cherry-picking: every one of the 40 sessions is included; the 50/50
  breakout split is the generator's own fixed rule, not a post-hoc filter.

This run deliberately did NOT attempt a much larger day count: a 250-day run of the same replay was
started and killed after several minutes of pure CPU-bound growth (a 40-day run itself took ~5m04s, up
from ~3.4s for an 8-day pilot -- a markedly superlinear cost as accumulated in-process bar history grows,
most likely in `RawAxesBuilder`'s own incremental axis computation, not in `strategy_platform` code this
mandate is scoped to touch). Per section 11's own explicit instruction ("do not create an unnecessarily
multi-hour day-count-bounded test if an equivalent deterministic replay can cover the operational cases
more efficiently"), this 40-day/1273-cycle replay was judged sufficient -- it already contains repeated,
independent instances of every required case (signal-free cycles, valid setups, TRADE_DECISION,
restart boundary) rather than one of each. The scaling behavior itself is recorded here as a genuine
operational finding/limitation (section 17 below), not silently worked around.

## 5. MISSING_PROBABILITY_INPUTS regression (section 5)

**Zero occurrences** across all 1273 cycles of this replay. `S5OpeningRangeBreakoutLong.evaluate()` now
always attaches `S5_REAL_EV_EVIDENCE_V1.to_expected_edge()` on every hypothesis it produces (confirmed by
direct source read of `s5_opening_range_breakout.py` lines 180-192, and independently by
`test_s5_hypothesis_reaches_real_ev_authority_with_genuine_evidence` in
`test_s5_onboarding_integration.py`), so a correctly-identified S5 hypothesis can never again decode to
`probability_inputs=None`. The 20 EV evaluations in this replay all had genuine, non-`None`
`probability_inputs`; the reason distribution above contains no `MISSING_PROBABILITY_INPUTS` entry.
Fail-closed coverage for a deliberately MALFORMED/missing evidence payload (never naturally produced by
S5 itself) is exhaustively exercised by the existing unit suite -- section 8 below.

## 6. Genuine REAL EV path proof (section 6)

- `ev_engine_version_confirmed = "real-ev-engine-v1"` on every one of the 20 TRADE_DECISION records --
  `MockEVDecisionEngine` was never constructed or reachable anywhere in this replay's code path.
- Sample ledger record (first of the 20, verbatim from the persisted `ShadowLedgerRecord`):
  ```
  market_timestamp: 57600
  ev_decisions: [["s5_c_2d587447_opening_range_breakout_long", "TRADE_DECISION",
                  "9ca6e2bd9884389b822518bed2341f7273288018187974c468016b20070593b4"]]
  hypothetical_order_intent: "s5_c_2d587447_opening_range_breakout_long|XAUUSD|LONG|2008.0|1994.98"
  broker_submission_state: "BLOCKED_AT_GATE:BrokerOrderSubmissionGate: order submission is DISABLED --
                             Mandate 2 integration not yet ratified by Red Team -- default-closed"
  ```
  The `evidence_fingerprint` (`9ca6e2bd...`) is byte-identical to `S5_REAL_EV_EVIDENCE_V1.
  evidence_fingerprint` in all 20 records -- the genuine evidence package, never a synthetic stand-in.
- The decision was **not forced**: `test_s5_hypothesis_negative_geometry_reaches_honest_no_trade`
  (pre-existing, re-run clean) proves the same real evidence + real engine genuinely computes a
  *different* result for a materially different (much wider) risk geometry -- the outcome depends on the
  geometry the strategy itself produces, not on a hardcoded strategy_id branch. This replay's 20/20
  TRADE_DECISION rate reflects that this generator's canonical breakout geometry is IDENTICAL every
  time (fixed OR width, fixed +3 breakout offset, per the frozen `config_fingerprint`), not that the
  engine was rigged to always approve.

## 7. Decision distribution (section 10/18)

| Reason | Count | Meaning |
|---|---:|---|
| `NO_STRATEGY_SIGNAL` | 1253 | no S5 breakout on this cycle -- genuine, most-common, honest NO_TRADE |
| `BROKER_DISABLED` | 20 | EV=TRADE_DECISION, Risk approved, execution attempted, blocked at the disabled broker gate |

No `RISK_REJECTED`, `MISSING_PROBABILITY_INPUTS`, `EVIDENCE_IDENTITY_MISMATCH`, or
`EVIDENCE_COST_IDENTITY_MISMATCH` occurred naturally in this replay (all 20 valid setups passed Risk
under the fixed, generous `RiskExecutionDeps` fixture used; the cost/identity bindings were correct by
construction -- section 2). This is disclosed, not hidden: the fail-closed paths for each of these are
independently proven by the pre-existing unit suite (section 8), not fabricated into this replay just to
tick a box.

## 8. Fail-closed evidence regression (section 7) -- pre-existing, independently re-run, not modified here

All in `test_real_ev_engine.py` (232 lines added by `1e2af14`, re-run clean as part of the 174):

- Missing evidence -> `test_missing_probability_inputs_no_trade`
- Non-finite `sum_horizon_r` -> `test_decode_rejects_non_finite_sum_horizon_r` (NaN/+inf/-inf, parametrized)
- Impossible count geometry (`n_target+n_horizon>n`) -> `test_decode_rejects_impossible_count_geometry_matches_statistician_repro`, `test_decode_rejects_n_target_plus_n_horizon_exactly_one_over_n`, `test_decode_rejects_single_count_exceeding_n`
- Evidence/strategy identity mismatch -> `test_evidence_identity_mismatch_fails_closed` (parametrized over all 4 identity fields)
- Evidence/cost identity mismatch -> `test_evidence_cost_identity_mismatch_fails_closed`
- Fractional/boolean/negative counts -> `test_decode_rejects_fractional_counts`, `test_decode_rejects_boolean_masquerading_as_count`, `test_decode_rejects_negative_counts`

Every one of these resolves to a `NO_TRADE` before any Risk/Execution call is ever reached (verified by
each test's own assertions, not merely by this report's claim) -- no broker call occurs after any
rejection, structurally (Risk/Execution is only ever invoked from `pipeline.py` after a `TRADE_DECISION`,
line 159 `risk_execution_adapter.evaluate_and_attempt`, which itself never runs for these).

## 9. Cost semantics (section 8)

Verified by direct source inspection of `real_ev_engine.py` (not re-derived from `ve_brain`'s sealed
internals, which are out of this mandate's scope): `_decode_probability_inputs` places
`expected_edge["sum_horizon_r"]` into `ve_brain.OutcomeCell.sum_horizon_R` completely unmodified (no
subtraction, no scaling) -- this stays GROSS, exactly as `9cfcc5f`'s own reconciliation confirmed the
evidence itself already is. Cost is supplied as three SEPARATE fields
(`full_spread_price`/`entry_slippage_price`/`exit_slippage_price`) on the `DecisionRequest`, applied
exactly once, downstream, inside the sealed, already-ratified `ve_brain.run_ev`/`_ev_core` -- AI-Trader
code never pre-subtracts cost from `sum_horizon_r` before that call. No cost-model retuning was made or
proposed.

## 10. Risk path (section 9)

`RiskExecutionDeps` fixture used throughout (identical shape to the pre-existing
`test_s5_onboarding_integration.py`/`s5_soak.py` fixtures -- not reinvented): `$200,000` demo account,
`XAUUSD` instrument spec, a permissive `RiskConfig` with `reference_spread`/`liquidity_floor`/
`point_value` set for `XAUUSD`. All 20 TRADE_DECISION hypotheses passed `evaluate_trade_proposal`
(`risk_decision.approved=True` in every one) and reached `attempt_shadow_execution`, which then blocked
at `BrokerOrderSubmissionGate` (disabled) before any broker call. No future MT5-DEMO 5%-equity policy was
imposed or referenced -- none exists in this codebase as an isolated, disabled config, so none was
invented here.

## 11. ShadowLedger (section 14)

1273 records written across the primary replay (`ledger_row_count=1273`, exactly matching
`cycles_completed`) -- one record per evaluation cycle, none skipped, none batched. Every
`TradeHypothesis` that reached `TRADE_DECISION` has its shadow-execution intent fully recorded:
side (`LONG`), entry, invalidation (SL), strategy identity, `evidence_fingerprint`, decision
(`TRADE_DECISION`), and `broker_submission_state` explicitly naming the disabled gate and its reason
string -- see section 6's sample record. No order was ever submitted to a broker (section 13).

## 12. Dedup (section 12)

`duplicate_hypotheses=0`, `duplicate_decisions=0`, `duplicate_shadow_orders=0` for the full 1273-row
primary replay -- every `hypothesis_dedup_key` and every `hypothetical_order_intent` string recorded is
unique across the run (verified by set-cardinality comparison against the raw list lengths, not merely
asserted).

## 13. Restart determinism (section 13)

Phase 2 reopened the SAME on-disk ledger (fresh `SqliteStateStore`/`ShadowLedger` instances) and replayed
the IDENTICAL 1280-bar sequence through FRESH `RawAxesBuilder`/`S5OpeningRangeBreakoutLong`/
`RealEVDecisionEngine` instances (simulating a process restart). Result: `cycles_completed=0` new records,
`duplicates_detected=1273` (exactly the primary run's row count), `ledger_row_count_after_replay=1273`
(unchanged from before the restart replay began). No duplicate trade identity or ShadowLedger record was
created; the evidence identity (`evidence_fingerprint`) in the unchanged, pre-existing rows is of course
identical, since nothing was re-written. Zero exceptions during the restart phase.

## 14. Exceptions / error-handling accounting (section 16)

| | Primary | Restart |
|---|---:|---:|
| Total exceptions | 0 | 0 |
| Handled (caught, logged, cycle skipped) | 0 | 0 |
| Fatal (escaped the run) | 0 | 0 |
| Rejected evidence (this replay) | 0 (see section 8 for the exhaustive unit-level rejection matrix) | -- |
| Risk rejections | 0 | -- |
| Execution-disabled events | 20 | -- |

## 15. Broker hard boundary (section 15)

- `deps.gate.enabled is False` asserted as a precondition before the replay begins.
- `order_send_calls_total = 0`, both structurally (no code path in `strategy_platform`,
  `risk_execution_adapter`, or this replay script imports or calls any `order_send`-shaped function --
  re-confirmed by the pre-existing, AST-based `test_strategies_never_reach_broker.py`, re-run clean) and
  empirically (0 counted across 1273 + 1273 cycles).
- No MT5 order, no demo order, no live order, at any point in either phase.

## 16. Performance (section 22)

Full per-cycle latency (primary replay, real Sqlite I/O + real EV, N=1273): mean **5.24ms**, median
**7.67ms**, p95 **8.34ms**, max **30.48ms**. Component microbenchmark (200 fixed-fixture iterations, no
ledger I/O): `strategy.evaluate()` mean **0.012ms**; `RealEVDecisionEngine.decide()` (the real
`ve_brain.run_ev` call) mean **1.94ms**, p95 **2.16ms** -- the dominant cost of the decision path;
`evaluate_and_attempt` (Risk + shadow execution) mean **0.11ms**. No material operational blocker found;
no optimization attempted (section 22's own instruction: only optimize if a material blocker is found --
sub-10ms median full-cycle latency is not one).

**Separately noted, NOT optimized (out of scope)**: the standalone superlinear scaling finding from
section 4 (40 days taking ~5m04s vs. an 8-day pilot's 3.4s) is a property of sustained multi-day,
single-process bar accumulation, not of a single cycle's latency -- flagged in section 17 as a limitation
for whoever designs a real always-on live loop, not fixed here.

## 17. Limitations

- **Superlinear multi-day scaling** (see section 4): running this replay for hundreds of synthetic days
  in one process becomes CPU-bound and slow, most likely due to `RawAxesBuilder`'s incremental axis
  computation cost growing with total accumulated bar history rather than staying bounded. This did not
  block this mandate (a 40-day/1273-cycle bounded replay was sufficient and is reported honestly as
  such), but is a genuine open question for whoever eventually designs a real, long-running live loop
  (a process that runs for months would need this characterized and, if confirmed, addressed --
  out of this mandate's scope, no `RawAxesBuilder`/N1 code was touched or is proposed to be touched here).
- **Fixed canonical geometry**: this replay's synthetic breakout days all share the identical OR
  width/breakout offset (per the frozen `config_fingerprint`), so all 20 hypotheses evaluate to the same
  TRADE_DECISION outcome -- genuine geometry-sensitivity (a case that resolves NO_TRADE via
  `NEGATIVE_EXPECTED_VALUE`/`INFEASIBLE_GEOMETRY`) is proven separately, at the unit level, by the
  pre-existing `test_s5_hypothesis_negative_geometry_reaches_honest_no_trade` -- not re-derived here to
  avoid duplicating already-proven coverage.
- **Synthetic, not real, market data**: as in every prior S5 mandate, the real 295-trade validation ledger
  remains sealed escrow; this replay (like the strategy's own unit tests) uses synthetic-but-mechanically-
  faithful bar sequences reproducing the strategy's real entry/exit formulas, never the real historical
  outcomes. This is the same, already-disclosed limitation carried forward from
  `AI_TRADER_S5_ONBOARDING_REPORT.md` -- not new to this mandate.

## 18. Rollback

Unchanged from `AI_TRADER_VALIDATED_STRATEGY_ONBOARDING_CONTRACT.md` item 10 / Addendum 2/3: S5's
`CatalogEntry` can be omitted from the next `StrategyCatalog` build, or `enabled=False`/`status=DISABLED`
set, to remove it from production authority instantly (the catalog is an immutable snapshot, never
mutated in place). This mandate added exactly one new file
(`ai_trader/new_brain_live/strategy_platform/soak/s5_operational_replay.py`) and this report; no existing
platform, strategy, EV, or risk code was modified, so there is nothing else to roll back.

## Regression tests (section 20)

`pytest ai_trader/new_brain_live/strategy_platform/ -q` -> **174 passed** (unchanged from `1e2af14`'s own
reported count -- independently re-run, not assumed).

## Static checks (section 21)

`mypy --strict ai_trader/new_brain_live/strategy_platform/` -> **Success: no issues found in 33 source
files** (32 pre-existing + this mandate's 1 new file). No new static errors introduced.

## Final verdict

- `S5_OPERATIONAL_SHADOW_VALIDATION_PASS`
- `S5_GENUINE_EVIDENCE_OPERATIONAL_PASS`
- `S5_REAL_EV_OPERATIONAL_PASS`
- `S5_RISK_OPERATIONAL_PASS`
- `S5_RESTART_DEDUP_PASS`
- `S5_BROKER_DISABLED_PROOF_PASS`
- `BROKER_ORDER_SUBMISSION_DISABLED`
- `READY_FOR_S5_MT5_DEMO_EXECUTION_INTEGRATION`

Per the CEO's own final directive: STOP here. No S20, no second strategy, no live/demo order, no broker
enable, without a new, separate mandate.
