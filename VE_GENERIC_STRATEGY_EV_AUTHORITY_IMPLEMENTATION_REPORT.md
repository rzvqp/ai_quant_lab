# VE_GENERIC_STRATEGY_EV_AUTHORITY_IMPLEMENTATION_REPORT

**Mandate**: `VE-AI-TRADER-GENERIC-EV-AUTHORITY-001`
**Repo**: `ai_quant_lab-research-main`, branch `ai-trader-implementation`
**Architecture record**: [`VE_GENERIC_STRATEGY_EV_AUTHORITY_ARCHITECTURE.md`](VE_GENERIC_STRATEGY_EV_AUTHORITY_ARCHITECTURE.md)
**Base commit**: `6fa8523` (Section 36 soak COMPLETE: 40242 cycles, 6h00m, 0 exceptions)

## 1. Exact code changes

### 1.1 New files

| File | Lines | Purpose |
|---|---|---|
| `ai_trader/new_brain_live/strategy_platform/real_ev_engine.py` | 295 | The generic `RealEVDecisionEngine` — admission gate + `ve_brain.run_ev` composition |
| `ai_trader/new_brain_live/strategy_platform/future_strategy_fixture.py` | 122 | Mandate section 13 fixture: two synthetic strategies (`FIXTURE_FUTURE_VALIDATED_STRATEGY_POSITIVE`/`_NEGATIVE`) proving generic admission without hardcoding S5 |
| `ai_trader/new_brain_live/strategy_platform/tests/test_real_ev_engine.py` | 511 | 48 tests (section 2 below) |

### 1.2 Modified files (all additive; no existing line removed except direct predecessors of a changed line)

| File | Diff | Change |
|---|---|---|
| `ev_engine.py` | +18/−0 | `MOCK_EV_ENGINE_VERSION` constant; `EVDecisionEngine.engine_version` added to the `Protocol` as a read-only `@property`; `MockEVDecisionEngine.engine_version` class attribute |
| `pipeline.py` | +30/−8 | `_fingerprints()` gains a keyword-only `ev_engine_version` param (default = Mock placeholder); the 4 call sites *after* `ev_engine.decide()` has run pass `ev_engine.engine_version` explicitly; the 2 call sites with no engine in scope (`_no_trade_record`, and the pre-decide "no eligible strategy" branch inside `run_cycle`) keep the default |
| `reason_codes.py` | +19/−0 | 10 new additive reason-code constants + `ALL_REASON_CODES` extended (original 11 codes byte-unchanged) |

Full `pipeline.py` diff (representative — confirms exactly 2 default call sites vs. 4 explicit ones):

```diff
-EV_ENGINE_VERSION = "mock-ev-engine-v1"
+EV_ENGINE_VERSION = MOCK_EV_ENGINE_VERSION   # fallback only for the no-EV-engine-in-scope paths

-def _fingerprints(market_state: MarketState) -> StrategyPlatformFingerprints:
+def _fingerprints(market_state: MarketState, *, ev_engine_version: str = EV_ENGINE_VERSION) -> StrategyPlatformFingerprints:
     return StrategyPlatformFingerprints(
         ...
-        ev_engine_version=EV_ENGINE_VERSION, ...
+        ev_engine_version=ev_engine_version, ...
     )

 def _no_trade_record(market_state, *, reason):           # line 71 -- no ev_engine in scope, keeps default
     ... fingerprints=_fingerprints(market_state), ...

 def run_cycle(...):
     ...
     if <no eligible strategy / no hypotheses>:            # line 120 -- BEFORE ev_engine.decide(), keeps default
         ... fingerprints=_fingerprints(market_state), ...
     ev_decisions = tuple(ev_engine.decide(h) for h in outcome.hypotheses)   # line 125
     if <conflict>:                                        # line 137 -- AFTER decide(), explicit
         ... fingerprints=_fingerprints(market_state, ev_engine_version=ev_engine.engine_version), ...
     ... (3 more explicit sites: 150, 168, 184)
```

## 2. Root-cause bug found and fixed during implementation (not hypothetical)

`pipeline._fingerprints()` stamped **every** `ShadowLedgerRecord.fingerprints.ev_engine_version` with a
hardcoded module constant, `"mock-ev-engine-v1"`, regardless of which engine instance actually ran.
Reproduced empirically with a smoke test (`RealEVDecisionEngine` run through `pipeline.run_cycle`; ledger
recorded `"mock-ev-engine-v1"` even though the real engine decided). This would have made the audit trail
misattribute every real decision to the mock engine — a direct violation of mandate section 10's "no
ambiguity" requirement. Fixed as described in section 1.2/1.1 above. Verified fixed by
`test_full_shadow_pipeline_real_trade_decision_blocked_at_broker_gate`'s own assertion:
`result.record.fingerprints.ev_engine_version == REAL_EV_ENGINE_VERSION`.

A second, smaller defect was caught before it ever ran against real data: an initial draft compared
`ve_brain`'s EV-infeasibility reason against the literal string `"NO_TRADE_EV_LCB"`; a direct read of
`ve_brain/_ev_core.py`'s `Reason` enum showed the actual `.value` is lowercase snake_case,
`"no_trade_ev_lcb_not_positive"` — fixed before the first test run, not discovered by a failing test.

## 3. Tests (mandate section 19)

**48 new tests**, `test_real_ev_engine.py`, covering every category mandate section 14/19 requires:

| Category | Count | Representative names |
|---|---|---|
| Unit / schema / artifact identity | 6 | `test_cost_model_rejects_empty_id`, `test_engine_version_identity_distinct_from_mock`, `test_parse_exit_specification`, `test_decode_probability_inputs_well_formed` |
| Fail-closed: admission | 8 | `test_unknown_strategy_no_trade`, `test_wrong_strategy_fingerprint_no_trade`, `test_wrong_strategy_version_no_trade`, 5× parametrized non-`VALIDATED` statuses, `test_strategy_disabled_no_trade` |
| Fail-closed: MarketState / N1 contract | 4 | missing atr/entry_price, wrong `market_state_identity`, `INCOMPATIBLE_N1_CONTRACT` |
| Fail-closed: hypothesis schema / geometry | 8 | NaN/inf entry/invalidation, invalid SL/TP at construction (via `TradeHypothesis.__post_init__`), expired hypothesis, missing probability inputs, invalid `target_kind`, duplicate hypothesis |
| Fail-closed: EV-authority installation | 5 | tampered `ve_brain.VE_BRAIN_VERSION`, `None` version (uninstalled), Mock/Real never collide, `RealEVAuthorityError` at construction |
| Positive/negative EV through the real engine | 2 | `_POSITIVE_EDGE` → `TRADE_DECISION`; `_NEGATIVE_EDGE` → `NO_TRADE`/`NEGATIVE_EXPECTED_VALUE`, both via genuine `ve_brain.run_ev` computation |
| No-strategy-specific-code mechanical proof | 2 | AST-based: no forbidden strategy-name token anywhere in `real_ev_engine.py`'s **code** (docstring excluded); no reference to `ve_brain.decide_n6` anywhere in the module |
| Old-strategy regression (section 12) | 4 | `ve_brain.decide_n6`'s 4 sealed strategies (`trend_pullback`, `range_fade`, `trend_shadow`, `trend_experimental`), parametrized, decisions byte-identical to pre-mandate behavior |
| Full shadow-pipeline integration (section 16) | 2 | positive-edge → Risk approved → Execution `BLOCKED_AT_GATE:` → ShadowLedger; negative-edge → `NO_TRADE` end-to-end |
| Restart / dedup (section 17) | 2 | replay never reprocesses across a fresh `SqliteStateStore` handle; `dedup_key` deterministic across identical inputs |
| Performance (section 18) | 1 | `decide()` averages under 5ms/call over 200 calls |
| Cost-model / probability-decoding edge cases | 4 | malformed `expected_edge` parametrized (`None`, `{}`, wrong schema version, non-numeric, out-of-range credibility, a Mock-shaped edge) |

**Result**: `48 passed` in isolation; `83 passed, 1 failed` across the full `strategy_platform` suite (84
collected total). The 1 failure (`test_no_strategy_platform_module_references_broker_calls_directly`) is
confirmed pre-existing and unrelated (section 5, rollback proof) — `harness.py`/`run_soak_cli.py` mention
the substring `"order_send"` in their own reporting/docstrings, tripping a naive AST-adjacent substring
scanner; nothing this mandate touched.

### mypy --strict

`0` errors attributable to any file this mandate created or modified
(`real_ev_engine.py`, `future_strategy_fixture.py`, `reason_codes.py`, `ev_engine.py`, `pipeline.py`,
`tests/test_real_ev_engine.py`). Running `mypy --strict` across the whole `strategy_platform` package
reports `21 errors in 7 files` — all `fastjsonschema`/`jsonschema` stub-availability noise in unrelated
pre-existing modules, matching the baseline already confirmed clean before this mandate began (verified by
running the same command against `test_pipeline.py`/`_fixtures.py` in isolation: identical 21-error
baseline, 0 attributable to those files either).

## 4. Compatibility / regression (mandate section 12)

`ve_brain.decide_n6`'s 4 sealed strategies are asserted, individually, to reach the exact decision they
reached before this mandate (`test_ve_brain_decide_n6_four_strategies_unchanged`, parametrized):

| `strategy_id` | Decision (unchanged) | Reason (unchanged) |
|---|---|---|
| `trend_pullback` | `NO_TRADE` | `MISSING_PROBABILITY_INPUTS` |
| `range_fade` | `NO_TRADE` | `TRUE_RANGE_NOT_IDENTIFIABLE` |
| `trend_shadow` | `NO_TRADE` | `MISSING_PROBABILITY_INPUTS` |
| `trend_experimental` | `NO_TRADE` | `NO_ELIGIBLE_STRATEGY` |

(Missing `probability_inputs` is deliberate in this probe — it isolates catalog/range-block/eligibility
resolution, the part this mandate could plausibly have disturbed, from EV math specifics, which it never
touches.) Old inputs → identical decisions, confirmed.

**Rollback proof** (mandate section 11's "no silent mutation" + general delivery discipline): all 6
mandate files (3 new, 3 modified) were stashed out with `git stash push --include-untracked`, and the full
`strategy_platform` suite re-run against the resulting pre-mandate tree:

```
1 failed, 35 passed in 25.40s
```

— identical to the known pre-mandate baseline (36 tests, same single unrelated failure). The stash was
then restored (`git stash pop`), and the full suite re-confirmed at `1 failed, 83 passed`. This proves the
change is fully, cleanly reversible and that `ve_brain`'s own sealed catalog/`decide_n6` and every other
pipeline mechanic are completely unaffected by its presence or absence.

## 5. Versioning

See architecture doc section 3 for the full identity table. Artifact identity for this delivery is the
git commit that lands these 6 files (recorded in the handoff doc and this repo's
`AI_TRADER_PROJECT_STATE.md` once committed) — following this repo's own convention (no
date-stamped "implementation fingerprint" label; that convention belongs to the sibling `ve_n1_replay`/
RANGE work, not to `ve_brain` or `strategy_platform`, confirmed via a full read of `ve_brain`'s own
version/manifest modules).

## 6. Performance (mandate section 18)

Measured directly (`venv/Scripts/python.exe`, isolated scripts, warm interpreter, Windows), reusing one
`MarketState`/`RealEVDecisionEngine`/hypothesis across N calls so each number isolates exactly one
operation:

| Operation | n | mean | median | p95 | max |
|---|---|---|---|---|---|
| `RealEVDecisionEngine.__init__` | 500 | 0.0011 ms | 0.0011 ms | 0.0016 ms | 0.0096 ms |
| `Strategy.evaluate()` (fixture strategy) | 500 | 0.0072 ms | 0.0072 ms | 0.0080 ms | 0.0425 ms |
| `RealEVDecisionEngine.decide()` | 500 | 3.4721 ms | 3.1801 ms | 4.8930 ms | 5.9923 ms |
| `RealEVDecisionEngine.decide()` (2nd independent run) | 2000 | 3.1682 ms | 3.0834 ms | 3.5833 ms (p95) / 4.3980 ms (p99) | 9.1235 ms |
| `pipeline.run_cycle()`, cold (first cycle, no dedup hit) | 1 | 4.7258 ms | — | — | — |
| `pipeline.run_cycle()`, dedup-hit fast path (same `market_state` replayed) | 99 | 0.0021 ms (median) | 0.0021 ms | — | — |
| Retained memory per `RealEVDecisionEngine` instance (`tracemalloc`, instances kept alive) | 20–300 | ≈318 bytes/instance, no growth trend across sample sizes | | | |

`decide()` cost is dominated by building `ve_brain.DecisionRequest`, computing `data_identity`/
`regime_fingerprint`/`decision_fingerprint`, `validate_request()`, and `ve_brain.run_ev()`'s own LCB
computation — all genuine, necessary, ratified work, not overhead specific to this mandate's admission
gate (engine construction and strategy evaluation are both sub-0.01ms, i.e. noise next to `decide()`
itself).

**Is a new 6-hour soak warranted? No** — stated with reasoning, per mandate section 18's own instruction:

1. The change is additive and isolated: when `MockEVDecisionEngine` is used (the soaked pipeline's own
   configuration), behavior is provably unchanged (section 4). The already-completed 6-hour soak
   (`6fa8523`: 40242 cycles, 0 exceptions, 0 duplicate cycles) remains valid evidence for that
   configuration; nothing this mandate did invalidates it.
2. `RealEVDecisionEngine` and `CostModel` are frozen, immutable dataclasses with no state accumulated
   across calls — there is no drift/leak mechanism a multi-hour soak is positioned to catch that unit,
   fail-closed, restart/dedup, and full shadow-pipeline integration tests do not already exercise directly.
3. Decision latency (~3–5 ms) is negligible against the pipeline's own natural cadence — the 6-hour soak
   averaged one cycle per ≈0.54 s (40242 cycles / 21600 s); an extra ~3–5 ms is <1% of one cycle's budget
   even in the worst observed case (5.99 ms).
4. The only genuinely new *runtime* participant is `RealEVDecisionEngine` itself, and it is exercised by
   48 tests including two full shadow-pipeline integration runs and two restart/dedup runs against a real
   `SqliteStateStore` — the specific failure modes a soak exists to catch (exceptions surfacing only after
   many cycles, duplicate trade events across restarts, slow memory growth) are covered by the restart/
   dedup tests and the memory measurement above, not left to chance.

If, after a first real validated strategy is onboarded (a separate future mandate, section 22), the
production configuration actually runs `RealEVDecisionEngine` continuously for the first time, a soak at
*that* point — of the real onboarded strategy under real market data — would be the correct gate, not a
synthetic-fixture soak now.

## 7. Verdict (mandate section 23)

- `GENERIC_VALIDATED_STRATEGY_EV_AUTHORITY_IMPLEMENTED`
- `REAL_EV_PLUGIN_PATH_READY`
- `AI_TRADER_REAL_STRATEGY_DECISION_HANDOFF_READY`
- `READY_FOR_FIRST_VALIDATED_STRATEGY_ONBOARDING`

No blocker. S5 was not implemented or onboarded; no strategy was promoted; broker submission remains
disabled; no demo/live trade was placed (mandate section 22, all verified in sections 3/4/6 above).

See [`VE_GENERIC_STRATEGY_EV_AUTHORITY_HANDOFF.md`](VE_GENERIC_STRATEGY_EV_AUTHORITY_HANDOFF.md) for the
exact onboarding sequence a future validated strategy follows through this new authority.
