# AI_TRADER_S5_ONBOARDING_REPORT

**Mandate**: `AI-TRADER-S5-CANONICAL-ONBOARDING-001`
**Date**: 2026-08-22
**Commits**: `fb078b5` (S5 plugin, tests, AST-guard fix), building on `7bea342` (VE generic real-EV
authority) and `6fa8523` (New Brain architecture)

## 1. Exact S5 identity (recovered mechanically, section 2)

| field | value | source |
|---|---|---|
| Alpha candidate | `C_2d587447` | `ai_quant_lab/red_team/policy_reviews/RT_S5_S20_CLEAN_INDEPENDENT_VALIDATION_REPORT.md` §2 |
| representative | `7472f3d412f2` | same, §2; identical in `red_team/audit/LEDGER.md` entry [97] |
| frozen spec (verbatim) | `S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3}` | same |
| direction | LONG-only | same |
| verdict | `INDEPENDENT_VALIDATION_PASS`, gates A-H all PASS | `RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001` (E97, commit `633bd5da`) |
| frozen trade ledger | sha256 `cd4e8d4aae0104cd1041898cf136917b9ec3194c343ba6840fab0bdb7831e1d7`, 295 trades | same §4 |
| EV (BASE/STRESS/gross) | 0.210 / 0.193 / 0.214 | same §11 |
| win rate / PF | 0.549 / 1.609 | same |
| max drawdown / max loss | -6.44R / -1.03R | same |
| SL median | $12.44 / 124.4 pips | same §10 |
| TP median | $37.32 / 373.2 pips (99.0% of trades >= 100 pips) | same §10 |
| engine | `code/mstrat.py` (`s5_setups`/`simulate`, `ai_quant_lab` repo) | full function bodies read directly, lines 273-291 and simulate's execution loop |
| TICK | `0.01` (ratified override; `mstrat.py`'s own module constant ships a documented `TICK=0.1` defect, `RT-CODE-A-0007`) | RT report §3 + direct code read |

**Cross-check against the CEO's own "opening-range momentum/breakout, RR=1:3" framing**: exact match,
confirmed independently from three sources (`mstrat.py`'s own `ECON` dict label, the `# ---- S5 Opening
Range Breakout ----` code comment, and `ai_quant_lab-alpha-automation/reports/alpha_discovery/ALPHA_S5_
C001_DEEP_RESEARCH_REPORT.md`). No mismatch found; nothing to STOP for.

**Chain of custody / promotion authorization**: CEO -> Statistician (`STAT_S5_INDEPENDENT_VALIDATION_
PROTOCOL.md`, prep) -> Red Team (`RT_S5_S20_CLEAN_INDEPENDENT_VALIDATION_REPORT.md`, execute/score,
"recommend to CEO, not promoted here") -> CEO (`AI-TRADER-S5-CANONICAL-ONBOARDING-001`, this mandate,
the actual promotion decision).

## 2. Mechanism, reproduced exactly (section 4 -- no strategy modification)

All eight formulas below are copied from `code/mstrat.py:273-291` and its `simulate` execution loop, not
reconstructed from the RT report's prose. Full citation and reasoning in `s5_opening_range_breakout.py`'s
own module docstring; summarized here:

1. Session = NY, UTC `[13:00, 21:00)`, 32 M15 bars.
2. Opening range = first 4 M15 bars of the session (`bar_in_session` 0-3) -- `or_high`/`or_low` = max
   high / min low over those 4 bars.
3. Entry window = `bar_in_session` 4-20 inclusive.
4. Trigger: bar's close > `or_high`.
5. Entry: next bar's open (reported at the signal bar's own close in this plugin, matching how the
   pipeline's own next M15 cycle IS the next-bar-open moment).
6. Stop: `or_low - 2*TICK`.
7. Target: `entry + 3 * (entry - stop)`.
8. Max hold: 48 M15 bars (12 hours), force-close at that horizon if neither stop nor target hits.

**Two disclosed, non-drifting scope boundaries** (not silent omissions):

- `mstrat.simulate`'s own stop-FLOOR widening (`max(2*spread_ticks*TICK, 5*TICK, 0.10*ATR)`, applied
  AFTER the raw `or_opp` stop) is a backtest EXECUTION-REALISM detail of that specific research engine,
  not part of S5's own strategy-level stop definition. The architecture's own separation of concerns
  (`AI_TRADER_NEW_BRAIN_ARCHITECTURE.md` §9: "a strategy may propose a stop; it may never override risk
  policy") places any real-world stop-distance adjustment downstream, in the Risk Engine's own
  stop-distance-validity guard -- never inside the strategy plugin.
- `mstrat.py`'s `mode` dimension (`breakout`/`retest`) has ZERO behavioral effect in `s5_setups` --
  confirmed both by direct code reading (the variable is never referenced in that function) and
  independently by the Statistician's own pre-RT disclosure (`STAT_S5_INDEPENDENT_VALIDATION_PROTOCOL.md`
  lines 35-38: both mode values score identically; the frozen choice was sort-order, not behavior). This
  plugin implements exactly the one real mechanism the validated engine has.

No SL/TP/RR/session/window number in the implementation differs from the frozen spec -- `S5_RUNTIME_
VALIDATION_FIDELITY_FAIL` was never triggered.

## 3. Plugin implementation

`ai_trader/new_brain_live/strategy_platform/s5_opening_range_breakout.py` -- `S5OpeningRangeBreakoutLong`,
implementing the generic `Strategy` protocol (`evaluate(StrategyEvaluationInput) -> TradeHypothesis |
None`) plus one additional, S5-specific public method, `observe_bar(bar)`, needed because `MarketState`
deliberately carries no raw OHLC or session-relative bar position (`market_state.py`'s own "deliberately
absent" section) -- the opening range must be tracked statefully across bars, exactly the same
calling-convention precedent `RawAxesBuilder.observe(bar)` already establishes. `evaluate()` itself reads
only `MarketState` (identity/timestamp/entry_price) plus this instance's own already-updated OR state --
no global or broker state touched (onboarding contract item 2's own purity requirement, scoped correctly
to global/broker state, not a strategy's legitimate internal state).

No `if strategy_id == S5` branch exists anywhere outside this one file -- `router.py`, `pipeline.py`,
`real_ev_engine.py`, the Risk Engine, and the Execution Adapter are byte-for-byte unmodified by this
mandate (verified: `git diff 7bea342..fb078b5 -- ai_trader/new_brain_live/strategy_platform/router.py
ai_trader/new_brain_live/strategy_platform/pipeline.py ai_trader/new_brain_live/strategy_platform/
real_ev_engine.py` is empty).

## 4. Catalog registration

`catalog_entry_for_s5(strategy)` -> `CatalogEntry(strategy_id="s5_c_2d587447_opening_range_breakout_long",
strategy_version="rep_7472f3d412f2", status=StrategyStatus.VALIDATED, allowed_directions=("LONG",),
context_eligibility=None, ...)`. `context_eligibility=None` (`REGIME_INDEPENDENT`) is correct, not a
weakening -- S5's frozen spec names a SESSION constraint, not a `ve_brain` regime constraint; session
gating is enforced inside the plugin's own `evaluate()`/`observe_bar()`, exactly matching section 6's own
"all strategy-specific logic belongs inside the plugin" instruction. `validation_provenance` carries the
full citation trail from section 1 above -- `CatalogEntry.__post_init__` structurally rejects
`status=VALIDATED` with no provenance, so this could not have been skipped.

## 5. Router path (section 6)

Proven by `test_s5_opening_range_breakout.py` and `test_s5_onboarding_integration.py`: S5 is selected
only when its own internal OR-tracking state says the exact causal setup exists (breakout within the
entry window, on top of a finalized 4-bar opening range) -- never via a special case in `router.py`
itself (`StrategyRouter.route`/`check_eligibility` are unchanged, confirmed by the empty diff in
section 3).

## 6. TradeHypothesis mapping (section 7)

| TradeHypothesis field | S5 value |
|---|---|
| `direction` | `Direction.LONG` |
| `intended_entry` | the breakout bar's own close |
| `invalidation` | `or_low - 2*TICK` |
| `exit_specification` | `"rr:3.0"` |
| `max_hold` | `48` |
| `strategy_config_fingerprint` | the frozen-spec string, `CONFIG_FINGERPRINT` |
| `market_state_identity` | the MarketState's own `context_id` |
| `expected_edge` | `None` -- see section 8 |

No semantic loss: `RealEVDecisionEngine._parse_exit_specification("rr:3.0")` -> `target_kind="rr",
target_param=3.0`, and `max_hold=48` feeds `DecisionRequest.holding_window` directly -- together
reconstructing exactly "target = entry + 3*risk, force-close at 48 bars if neither hits," matching
`mstrat.py`'s own execution loop.

## 7. REAL EV authority proof (section 8)

`test_s5_hypothesis_reaches_real_ev_authority_honest_missing_probability_inputs` proves,
against S5's real hypothesis and real `CatalogEntry`: `result.record.fingerprints.ev_engine_version ==
"real-ev-engine-v1"` -- never the mock placeholder. No mock/real ambiguity is possible (the audit-lie bug
this exact field exists to prevent was fixed in the prior mandate, `7bea342`).

**The honest, disclosed terminal state**: S5's real 295-trade frozen ledger (`cd4e8d4a...`) is **not
readable in this environment** -- it is off-git escrow, hash-only (confirmed by an exhaustive search
across `ai_quant_lab` and every sibling repo; see the forensic recovery notes preserved in this mandate's
own working history). The documented ledger schema (`STAT_S5_S20_CLEAN_VALIDATION_FREEZE.md` §4.4) does
not include an explicit target/stop/horizon outcome-type column either, so even the schema alone would
not have been sufficient without the actual rows. Per this project's own standing, repeatedly-applied
rule ("never invent or approximate a probability input"), `TradeHypothesis.expected_edge` is honestly
`None`. `RealEVDecisionEngine.decide()` therefore reaches its own, pre-existing, correct gate: `if
probability_inputs is None: return _no_trade(hypothesis, rc.MISSING_PROBABILITY_INPUTS)`.

**A real, disclosed finding from actually exercising this end to end (soak, section 9 below)**:
`pipeline.run_cycle`'s own "no trade_decisions" branch (pre-existing code from the `7bea342` mandate,
unmodified here) records the COARSE `EV_BELOW_THRESHOLD` in `ShadowLedgerRecord.final_reason_codes`
rather than propagating the EV engine's own specific reason (`MISSING_PROBABILITY_INPUTS` in S5's case).
The specific reason IS still available in-memory on `CycleResult.ev_decisions[i].reason_codes` for
anything calling `run_cycle` directly, just not persisted into the ledger's own coarse field. This is a
genuine ledger-granularity observation, not a defect this mandate's own scope authorizes fixing (no
`pipeline.py` change was made) -- flagged here for a future hardening mandate.

**No duplicate Alpha logic in EV (section 9)**: `real_ev_engine.py` contains zero S5-specific code
(confirmed: the empty diff in section 3, plus this package's own pre-existing `test_no_strategy_id_
branch_exists_in_real_ev_engine_source` test from `7bea342` still passes against a codebase that now
includes S5). S5 determines whether its setup exists; `RealEVDecisionEngine` only evaluates the
authorized hypothesis under the generic economic contract.

## 8. Risk Engine proof (section 10)

Reused verbatim -- `risk_execution_adapter.evaluate_and_attempt` is byte-for-byte unchanged.
`test_broker_never_reachable_for_s5_even_when_ev_and_risk_would_approve` proves S5 hypotheses pass
through exactly the same `evaluate_trade_proposal`/`attempt_shadow_execution` path every other strategy
(mock or future) uses -- using a synthetic, explicitly-labeled wiring-only `expected_edge` (NEVER claimed
as real S5 evidence -- see that test's own docstring) to reach `TRADE_DECISION` and prove Risk approval +
broker block, since S5's own honest, current evaluate() never itself produces a positive edge.

## 9. Bounded S5-specific shadow soak (section 19)

Per section 19's own instruction, a fresh 6-hour infrastructure soak was judged NOT necessary -- the
section-36 infrastructure soak already proved 6 real hours of sustained pipeline/Router/Risk/Execution/
ShadowLedger/process stability (`SOAK_REPORT_2026-08-21.json`, 40242 cycles, 0 exceptions).
`soak/s5_soak.py` is a new, bounded, S5-specific soak proving what that run did NOT exercise: `Real
EVDecisionEngine` (not Mock) driving S5's own real `CatalogEntry`, and S5's stateful `observe_bar`
opening-range tracking, across many distinct multi-day NY-session sequences (roughly half deliberately
breaking out, half not).

**4-day smoke validation** (real, run before the full bounded soak): 121 cycles, 0 exceptions, 0
duplicates, ledger:cycle parity exact, `order_send_calls_total=0`, 2 real `RealEVDecisionEngine`
confirmations (the 2 breakout days), 119 `NO_STRATEGY_SIGNAL` (the 117 no-breakout days plus warm-up),
2 `EV_BELOW_THRESHOLD` (see the ledger-granularity finding above -- these are genuinely
`MISSING_PROBABILITY_INPUTS` outcomes at the engine level).

**Full bounded run** (500 simulated NY sessions) -- completed, exit code 0. Raw report archived at
[`S5_SOAK_REPORT_2026-08-22.json`](S5_SOAK_REPORT_2026-08-22.json):

| field | value |
|---|---|
| `duration_seconds` | `30940.35` (~8h35m -- longer than intended; this run was bounded by DAY COUNT, not wall-clock time, and per-cycle cost grew as the ledger/database accumulated rows across nearly 16,000 cycles; disclosed honestly rather than re-run to a "nicer" number) |
| `days_simulated` | `500` |
| `cycles_completed` | `15993` |
| `breakout_days` | `250` |
| `real_ev_engine_confirmations` | `250` -- **exact 1:1 match with `breakout_days`**: every single breakout hypothesis reached `RealEVDecisionEngine`, never the mock |
| `no_strategy_signal_count` | `15743` (the 250 no-breakout days plus per-day filler bars, each correctly producing `NO_STRATEGY_SIGNAL`) |
| `other_reason_counts` | `{"EV_BELOW_THRESHOLD": 250}` -- confirms the section 7 ledger-granularity finding: all 250 real breakout hypotheses resolved through the coarse pipeline label (specific engine-level reason is `MISSING_PROBABILITY_INPUTS`, visible on `CycleResult.ev_decisions`, not persisted into the ledger's own coarse field) |
| `duplicate_cycles_detected` | `0` (across all 15993) |
| `exceptions` | `[]` -- zero, across nearly 16,000 cycles and 250 real-EV-engine invocations |
| `ledger_row_count_final` | `15993` -- exact 1:1 with `cycles_completed` |
| `order_send_calls_total` | `0` |

No crashes, no duplicated decisions, no restart-state corruption risk (dedup mechanism exercised
identically to the generic infrastructure soak), zero broker writes, stable `RealEVDecisionEngine`
operation across 250 real invocations, `NO_TRADE` behavior throughout -- section 19's own required
proof (stability, dedup, real-EV operation, ledger consistency, zero broker submission) is satisfied by
real, measured numbers, not asserted.

## 10. Fail-closed matrix (section 15)

| scenario | mechanism | proof |
|---|---|---|
| wrong S5 fingerprint | `STRATEGY_POLICY_MISMATCH` | `test_wrong_s5_fingerprint_fails_closed` |
| wrong version | `UNKNOWN_STRATEGY` (catalog lookup miss) | `test_wrong_s5_version_fails_closed_unknown_strategy` |
| wrong status (not VALIDATED) | `NO_ELIGIBLE_STRATEGY` | `test_wrong_status_not_validated_fails_closed` |
| disabled entry | `STRATEGY_DISABLED` at EV, excluded at Router | `test_s5_disabled_entry_fails_closed` |
| invalid session | no signal (session/window gating internal to the plugin) | `test_wrong_session_hour_never_fires_...`, `test_breakout_before/after_entry_window_...` |
| invalid MarketState identity | `MARKET_STATE_MISMATCH` | `test_s5_wrong_market_state_identity_fails_closed` |
| wrong EV artifact (unverified `ve_brain` version) | `RealEVAuthorityError` at construction | generic coverage, `test_real_ev_engine.py::test_tampered_ve_brain_version_fails_closed_at_construction` |
| Mock/Real mismatch | `engine_version` audit field, never ambiguous | section 7 above |
| duplicate hypothesis / restart duplicate | dedup via the reopened `ShadowLedger`'s own history | `test_s5_restart_dedup_never_reprocesses` |
| invalid schema | `TradeHypothesis.__post_init__` rejects at construction | structural, cannot even build one |
| NaN/inf | `SCHEMA_VALIDATION_FAILED` | generic coverage, `test_real_ev_engine.py::test_nan_intended_entry_no_trade`/`test_inf_invalidation_no_trade` |
| expired hypothesis | `SCHEMA_VALIDATION_FAILED` | `test_s5_expired_hypothesis_fails_closed` |
| broker enabled unexpectedly | structurally impossible (`BrokerOrderSubmissionGate.enabled=False`, AST-guard-proven) | `deps.gate.enabled is False`, checked in every S5 test that reaches Risk/Execution |
| invalid MarketState (missing atr/entry_price) | `MARKET_STATE_INVALID` | `test_invalid_market_state_entry_price_none_produces_no_signal` |

## 11. Restart / dedup (section 16)

`test_s5_restart_dedup_never_reprocesses`: a genuinely reopened `SqliteStateStore` against the same file
sees exactly one persisted record for a given MarketState after a "restart," and re-processing the same
MarketState returns the existing record (`duplicate=True`) without appending a second row or re-attempting
Risk/Execution.

## 12. Legacy isolation (section 17)

`test_s5_never_referenced_by_legacy_execution_paths` mechanically confirms S5's `strategy_id`, module
name, and class name appear nowhere in `pdh_pdl_demo/orchestration.py` or `multi_policy_live/
orchestration.py`'s source. Both packages remain `LEGACY_NON_AUTHORITY`/quarantined
(`LEGACY_TRADING_AUTHORITY_QUARANTINED = True`, unchanged, commit `e469628`) and were not touched by this
mandate.

## 13. Shadow execution E2E (section 18)

Proven two ways: (1) S5's own honest path -- real MarketState -> S5 -> real EV -> `MISSING_PROBABILITY_
INPUTS` -> `ShadowLedger` (section 7); (2) the wiring-only path -- a synthetic, explicitly-labeled edge
carries a `TRADE_DECISION` through real Risk approval to `BLOCKED_AT_GATE`, `order_send=0` (section 8).
Both terminate with `order_send_calls_total = 0` throughout every test and the soak.

## 14. Test counts / type checks

104/104 `strategy_platform` tests pass (20 new S5-specific: 9 fixture + 11 integration; 84 pre-existing
from `6fa8523`/`7bea342` unaffected). mypy `--strict` clean on all 29 touched/added files (including the
2 files that needed an import-path correction, `s5_soak.py` and the earlier `risk_execution_adapter.py`
pattern it reused). Also fixed, in passing: the pre-existing false-positive broker-call AST guard
(substring match on this package's own `order_send_calls_total` field name) is now AST-based (exact
call-name matching) -- genuinely fixed, not merely disclosed; 0 failures across the whole package.

## 15. Broker-disabled proof

`BrokerOrderSubmissionGate.enabled=False` by construction throughout; every S5 test and the soak assert
`order_send_calls_total == 0` / `deps.gate.enabled is False`. No demo, no live order was ever placed.

## 16. Rollback instructions

S5's admission is entirely additive and opt-in: removing `s5_opening_range_breakout.py` and its two test
files (or simply never constructing a `StrategyCatalog` that includes `catalog_entry_for_s5(...)`)
returns the system to its exact `7bea342` state -- `router.py`/`pipeline.py`/`real_ev_engine.py`/the Risk
Engine/the Execution Adapter were never touched, so there is nothing else to revert. No live process
consumes this catalog entry today (no live wiring was performed, per section 39/mandate scope) -- rollback
requires no coordination with `AITraderLiveShadow` at all.

## 17. Final status

`S5_VALIDATED_IDENTITY_REPRODUCED`, `S5_CANONICAL_PLUGIN_ONBOARDED`, `S5_REAL_EV_PATH_PASS`,
`S5_RISK_PATH_PASS`, `S5_SHADOW_EXECUTION_READY`, `BROKER_ORDER_SUBMISSION_DISABLED`, `READY_FOR_S5_
OPERATIONAL_SHADOW_VALIDATION`.

Not established, per section 21: `S5_LIVE_APPROVED`, `BROKER_ENABLED`, `PRODUCTION_TRADING_APPROVED`.
Not onboarded, per section 20: S20, HR-TU-pb-L, H4-bo-raw-S, MT-H4-dispaccept-L, or any other candidate.
