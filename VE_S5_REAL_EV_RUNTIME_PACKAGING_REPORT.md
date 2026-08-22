# VE_S5_REAL_EV_RUNTIME_PACKAGING_REPORT

**Mandate**: `VE-S5-REAL-EV-RUNTIME-PACKAGING-001`
**Repo**: `ai_quant_lab-research-main`, branch `ai-trader-implementation`
**Contract**: [`S5_REAL_EV_RUNTIME_EVIDENCE_CONTRACT.md`](S5_REAL_EV_RUNTIME_EVIDENCE_CONTRACT.md)
**Base commit**: `c30b056` (S5 onboarding COMPLETE: bounded soak clean, 15993 cycles, 0 exceptions)

## 1. Root cause / evidence lineage

S5's `TradeHypothesis.expected_edge` was honestly `None` since `AI-TRADER-S5-CANONICAL-ONBOARDING-001`
(`fb078b5`) because the real 295-trade frozen ledger is sealed, off-git escrow — never readable by this
repository. What became available since is AGGREGATE evidence, extracted from that ledger without opening
it, through a five-commit chain, each independently read in full before this mandate began:

| Commit | Author | What it established |
|---|---|---|
| `633bd5da` | Red Team | `RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001` — S5 `INDEPENDENT_VALIDATION_PASS`, gates A-H, on the frozen 52,572-bar population |
| `e54a2a5` | Statistician | `STAT_S5_CANONICAL_EV_EVIDENCE_REPORT.md` — specified the canonical evidence schema (§11's YAML, which `ValidatedEVEvidence`'s field names are drawn from directly) and proved, arithmetically, that `n_target := round(WR*n)` would falsify `n_target` by **>=3x** (`3.0*T <= 163.458 winner-R => T <= 54.5`, vs. `WR*n = 162`) — the reason this contract requires raw counts, never a scalar WR |
| `8228ded` | Red Team | `RT-S5-EV-ESCROW-AGGREGATE-EXTRACTION-001` — extracted `n=295, n_target=15, n_horizon=196, sum_horizon_r=+102.2125344478 GROSS`; initially `BRACKET_FAIL` (`n_stop=84` outside a `[99,147]` bracket) |
| `9cfcc5f` | Statistician | `STAT_S5_EV_AGGREGATE_RECONCILIATION_REPORT.md` — proved the `n_stop>=99` floor was mis-derived from *total losing trades* (133), not *stop exits* (`n_losers = n_stop + negative-horizon losers = 84 + 49 = 133`); withdrew the floor; independently reconfirmed all values by executing `_decode_probability_inputs` on the real aggregates; **identified the two fail-open defects fixed in this mandate** |
| `b4cb441` | Red Team | `RT-S5-EV-AGGREGATE-RESTAMP-001` — re-stamped `S5_VALIDATED_EV_AGGREGATES_V1` `READY_FOR_RUNTIME_PACKAGING`, values byte-identical, added a stable `evidence_fingerprint` |

All five commits are present, identically, across all four repo mirrors — read directly at their source
paths in `ai_quant_lab` (branch `statistician-foundation`), not paraphrased from the mandate prompt.

## 2. Exact source values (verified against source, not transcribed from the prompt)

| Field | Value | Source line |
|---|---|---|
| `n` | 295 | `RT_S5_EV_AGGREGATE_RESTAMP_REPORT.md`, artifact lineage table |
| `n_target` | 15 | same |
| `n_horizon` | 196 | same |
| `n_stop` (implicit) | 84 | `n - n_target - n_horizon`, never a stored field |
| `sum_horizon_r` | +102.2125344478 (GROSS) | `RT_S5_EV_ESCROW_AGGREGATE_EXTRACTION_REPORT.md` §3 |
| `evidence_fingerprint` | `9ca6e2bd9884389b822518bed2341f7273288018187974c468016b20070593b4` (full 64 hex, verified directly, not the abbreviated form) | restamp report line 104 |
| `source_artifact_fingerprint` | `ff1384a2fba6d37c859613887d89837bdd11a94614ade0a1ed034176653dddd4` (full) | restamp report line 94 |
| `validation_ledger_sha256` | `cd4e8d4aae0104cd1041898cf136917b9ec3194c343ba6840fab0bdb7831e1d7` | matches `s5_opening_range_breakout.py`'s own `VALIDATION_PROVENANCE` string exactly |
| `population_ohlc_sha256` | `bac65b1a8840a0b82a384aa86bfafab9f38f36abb03cd030c6f7afdfbc457ea1` (full — the two source reports this mandate named only show an abbreviated `bac65b1a...`; the full digest was recovered from `statistician/STAT_S5_S20_CLEAN_VALIDATION_FREEZE.md`, cross-referenced) | |
| `population_timeline_sha256` | `4c9ce7b7f245bb9a375edaec42bcf3355a78ba99d2dd2fbf8d897ecf2ed4728a` (full, same recovery) | |
| `cost_model_id` / `round_trip_price` | `AI_TRADER_SHADOW_COST_MODEL_v1` / STRESS `0.24` (BASE `0.05` also ratified; STRESS chosen as the bound scenario — more conservative) | escrow extraction report §8 |

`e_x_h = sum_horizon_r / n_horizon = 102.2125344478 / 196 = 0.521493` — independently reproduced by
`ve_brain.run_ev`'s own internal computation when this evidence is fed through it (section 6 below,
`e_x_h = 0.5214925226928572`), matching the Statistician's own `9cfcc5f`-reported `0.521492` to 5
significant figures. This cross-validation (two independent computations of the same derived quantity
converging) is strong evidence the evidence package is wired correctly, not merely internally consistent.

## 3. Fail-closed hardening (mandate sections 3-4)

Both defects were independently confirmed OPEN by the Statistician (`9cfcc5f` §15) via direct execution
of the pre-mandate `_decode_probability_inputs` — not theoretical:

**Defect A** — `sum_horizon_r=NaN` (with `n=295,n_target=15,n_horizon=196`, the Statistician's own exact
repro) decoded to `ProbabilityInputs VALID`; `NaN` then propagates through `ev_from_terms` to
`EV_R=NaN`. Root cause: `_decode_probability_inputs` (pre-mandate) checked `n < 0 or n_target < 0 or
n_horizon < 0 or not (0.0 < credibility < 1.0)` — never touching `sum_horizon_r`'s own finiteness.

**Defect B** — `{n=10, n_target=8, n_horizon=9, sum_horizon_r=1.0}` (Statistician's own exact repro)
decoded to `ProbabilityInputs VALID`, implied `n_stop=-7`. `ve_brain._ev_core.ev_from_terms`'s own
`if p_s < 0.0: p_s = 0.0` clamp (sealed, unmodifiable, read directly from source) then silently absorbs
the corruption — discarding the entire loss branch and returning a plausible-looking but INFLATED EV.
The Statistician's own words: "the more dangerous of the two: it fails open, quietly, with a number that
looks reasonable."

**Fix** (`real_ev_engine.py`, `_decode_probability_inputs` + new helper `_decode_count`):

```python
if not math.isfinite(sum_horizon_r):        # Defect A -- explicit, not an implicit NaN-comparison trick
    return None
if n_target + n_horizon > n:                # Defect B -- rejects BEFORE ve_brain._ev_core's own p_s clamp
    return None
```

Both reproduced with the Statistician's own exact input values in
`test_decode_rejects_non_finite_sum_horizon_r` (parametrized NaN/+inf/-inf) and
`test_decode_rejects_impossible_count_geometry_matches_statistician_repro`.

**Additionally hardened** (mandate section 5, implied by "do not silently coerce corrupt evidence," not
separately flagged by the Statistician): `bool` values masquerading as counts (`int(True)==1`), fractional
counts silently truncating (`int(294.7)==294`), and a latent crash — pre-hardening, `int(float('inf'))`
raises `OverflowError`, which the old `except (KeyError, TypeError, ValueError)` clause did NOT catch,
meaning a `+inf`/`-inf` value for `n`/`n_target`/`n_horizon` would have CRASHED `decide()` rather than
failing closed. Fixed via a new `_decode_count()` helper checking finiteness before calling `int()`.

## 4. Evidence identity binding (mandate section 9)

`ValidatedEVEvidence.to_expected_edge()` (new module `s5_ev_evidence.py`) renders eight additive,
OPTIONAL keys into `expected_edge` alongside the five pre-existing ones (`edge_schema` unchanged —
`"real-ev-expected-edge-v1"`, not a new schema version). `RealEVDecisionEngine.decide()` gained a new,
GENERIC step, `_verify_evidence_identity()` — when these optional keys are present, they are cross-checked
against `entry: CatalogEntry` (strategy_id/version/implementation_fingerprint/config_fingerprint) and
`self.cost_model` (cost_model_id, and the summed price fields against `evidence_round_trip_price` within
`1e-9`). A mismatch on any strategy-identity field fails closed with the new `rc.EVIDENCE_IDENTITY_
MISMATCH`; a cost mismatch fails closed with the new `rc.EVIDENCE_COST_IDENTITY_MISMATCH`. **No
strategy-specific code was added anywhere** — this is purely a cross-check between the edge dict and two
sources of truth the engine already had in scope; a payload lacking these optional keys (the pre-existing
generic fixture's) is provably unaffected
(`test_evidence_without_identity_keys_is_unaffected_backward_compat`).

## 5. Real audit trail (mandate section 20/23)

`EVDecision` gained a new field, `evidence_fingerprint: str = ""` (empty = no validated evidence package
involved). `ShadowLedgerRecord.ev_decisions` changed from `tuple[tuple[str,str],...]` to
`tuple[tuple[str,str,str],...]` — the third element is that fingerprint, threaded through all 4
post-`ev_engine.decide()` call sites in `pipeline.py`. `_serialize`/`_deserialize` needed no code change
(both are tuple-arity-generic); a ledger row persisted before this field existed would deserialize as a
2-tuple, but nothing in this codebase destructures `ev_decisions` with a fixed-arity unpack, and no
live/production ledger predates this change (`BROKER_ORDER_SUBMISSION` has never been enabled) — disclosed
in `shadow_ledger.py`'s own field comment, not silently glossed over.

## 6. Genuine positive REAL EV proof (mandate section 14 — full transparency, not asserted)

Run against the canonical breakout test fixture (`or_high=2050.00`, `or_low=2040.00`, breakout close
`2052.00`, `atr=5.878571428571441`), S5's own real `evaluate()` (now carrying `S5_REAL_EV_EVIDENCE_V1`),
a genuinely cost-identity-matching `CostModel` (`AI_TRADER_SHADOW_COST_MODEL_v1`, fields summing to
`0.24`), through the real, unmodified `ve_brain.run_ev`:

```
hypothesis geometry: intended_entry=2052.0  invalidation=2039.98  risk=12.02  exit=rr:3.0  max_hold=48

decoded evidence: n=295 n_target=15 n_horizon=196 sum_horizon_R=102.2125344478 credibility=0.8

ve_brain.run_ev outcome (every field, unmodified):
  enter               = True
  reason              = 'enter'
  expected_value_net  = 0.15050088053601787
  expected_reward     = 0.11968324153884277
  expected_loss       = 0.2956988064927022
  estimated_cost      = 0.019966722129783725
  probability_assumptions = {
    p_t_hat: 0.05084745762711865, p_t_lcb: 0.039894413846280924,   # LCB-shrunk, the value actually used
    p_h_hat: 0.6644067796610169, e_x_h: 0.5214925226928572, e_x_h_missing: False,
    credibility: 0.8, rr: 3.0, r: 12.02, cost: 0.24, rr_min: 0.019966722129783725,
  }

DECISION: TRADE_DECISION, reason=REAL_EV_VALIDATED_EDGE, evidence_fingerprint=9ca6e2bd...

independent manual re-derivation (cross-check, not the production path):
  p_t = 15/295 = 0.050847         (matches p_t_hat exactly)
  p_h = 196/295 = 0.664407        (matches p_h_hat exactly)
  E[X|h] = 102.2125344478/196 = 0.521493   (matches e_x_h to 6 s.f.)
```

**This was not forced** (mandate section 13 explicitly: forcing `TRADE_DECISION` is not the objective) —
`enter=True` because `EV_LCB=expected_value_net=0.1505 > 0`, computed genuinely from the geometry S5's own
`evaluate()` produced and the verified evidence, through the unmodified sealed engine. A second fixture
with a materially wider stop (`test_s5_hypothesis_negative_geometry_reaches_honest_no_trade`) is asserted
only to be a *real, non-fabricated* verdict (`TRADE_DECISION` or `NO_TRADE` with a legitimate EV/geometry
reason) — proving the decision genuinely tracks geometry, not a hardcoded strategy id.

## 7. Shadow-pipeline proof (mandate section 22)

`test_s5_hypothesis_reaches_real_ev_authority_with_genuine_evidence` runs the full chain — `MarketState`
→ `StrategyCatalog` → `StrategyRouter` → S5 → `TradeHypothesis` (carrying genuine evidence) →
`RealEVDecisionEngine` (genuine evidence consumed, `TRADE_DECISION`) → Risk (approved) → Execution
(`BLOCKED_AT_GATE:...`) → `ShadowLedger` (`ev_decisions=((STRATEGY_ID, "TRADE_DECISION",
"9ca6e2bd...9ca6e2bd..."),)`, `final_decision="NO_TRADE"` — structurally always, broker disabled). No
mock probability, no synthetic evidence, no broker call (`order_send_calls_total` never incremented,
`BrokerOrderSubmissionGate(enabled=False)` untouched).

## 8. Tests (mandate section 27)

**70 new tests**, full suite **174 passed, 0 failed** (up from the pre-mandate 104/104 — the previously-
disclosed `order_send` substring false-positive was fixed by the prior S5 onboarding mandate, confirmed
still fixed here):

| File | New | Covers |
|---|---|---|
| `test_real_ev_engine.py` | +28 | Hardening (NaN/inf/geometry/fractional/bool, generic — section 16), identity/cost-identity mismatch + positive control (section 9), backward-compat proof |
| `test_s5_ev_evidence.py` (new) | 41 | `ValidatedEVEvidence` construction validation (mirrors `CostModel`'s own pattern), `to_expected_edge()` rendering, tamper tests with HONEST disclosure of the undetectable class (section 17) |
| `test_s5_onboarding_integration.py` | +1 net (1 rewritten, 1 added) | Genuine-evidence shadow-pipeline proof, negative-geometry real-decision proof |
| `test_s5_opening_range_breakout.py` | 0 net (1 assertion updated) | `expected_edge` now asserted equal to `S5_REAL_EV_EVIDENCE_V1.to_expected_edge()`, not `None` |

Also fixed in passing: the pre-existing AST-based "no strategy-specific branch" test only stripped the
MODULE docstring before scanning, not FUNCTION/CLASS docstrings — my own new hardening docstrings
(legitimately naming "S5" in prose, explaining why the mandate exists) tripped a false positive. Fixed by
generalizing the stripper to walk the whole tree (`_strip_all_docstrings`, `ast.NodeTransformer`), which
is a strict improvement matching the test's own already-stated intent ("prose legitimately discusses these
names ... the guard is on executable logic, not prose") — not a scope change to what the test verifies.

### mypy --strict

`0` errors attributable to any file this mandate touched or created (`real_ev_engine.py`,
`s5_ev_evidence.py`, `s5_opening_range_breakout.py`, `ev_engine.py`, `pipeline.py`, `shadow_ledger.py`,
`reason_codes.py`, and all 4 test files). `21` pre-existing `fastjsonschema`/`jsonschema`-stub errors in 7
unrelated files — the same baseline confirmed clean before this mandate (and before the prior one).

## 9. Regression (mandate sections 18-19)

**Generic EV authority** (`VE-AI-TRADER-GENERIC-EV-AUTHORITY-001`): all 48 of its own tests still pass,
unmodified in behavior — the hardening only REJECTS additional cases (finite-check, geometry-check) that
were previously accepted incorrectly; every case the original suite asserted should decode successfully
still does (`test_decode_sane_baseline_still_accepted` uses the exact Statistician-cited baseline as an
anchor). `ve_brain.decide_n6`'s 4 sealed strategies, sealed catalog isolation, and
`StrategyCatalog`'s own fail-closed behavior are byte-for-byte untouched (no diff to `router.py`,
`catalog.py`, `risk_execution_adapter.py`, or any `ve_brain` file).

**S5 onboarding** (`AI-TRADER-S5-CANONICAL-ONBOARDING-001`): the canonical formula (opening-range
construction, NY session window, breakout trigger, `stop=or_low-2*TICK`, `target=entry+3*risk`,
`max_hold=48`) is byte-for-byte unchanged — the only change to `s5_opening_range_breakout.py` is what
`expected_edge` carries. This IS `AI-TRADER-S5-CANONICAL-ONBOARDING-001`'s own explicitly-disclosed
"what this contract does NOT cover" gap being closed (`AI_TRADER_VALIDATED_STRATEGY_ONBOARDING_
CONTRACT.md`'s closing section), not a violation of it — two existing tests that asserted the OLD
`expected_edge is None` behavior were updated to assert the new, correct behavior; this is the mandate's
own explicit section-12 objective, not an unplanned break (see section 8's test table).

## 10. Performance (mandate section 26)

Measured directly (`venv/Scripts/python.exe`, isolated script, warm interpreter), against S5's own real
canonical fixture:

| Operation | n | mean | median | p95 | max |
|---|---|---|---|---|---|
| `ValidatedEVEvidence.to_expected_edge()` | 1000 | 0.00167 ms | 0.00160 ms | 0.00170 ms | 0.01590 ms |
| `_decode_probability_inputs()` (hardened) | 1000 | 0.00864 ms | 0.00820 ms | 0.00920 ms | 0.06160 ms |
| `_verify_evidence_identity()` | 1000 | 0.00326 ms | 0.00320 ms | 0.00330 ms | 0.02680 ms |
| `RealEVDecisionEngine.decide()`, full path (S5, incl. all of the above) | 1000 | 2.21039 ms | 1.91980 ms | 4.44414 ms | 6.29690 ms |

The three new/hardened operations sum to ≈0.0136 ms — **under 1%** of the full `decide()` cost, and both
`decide()` numbers here (S5's own, and the prior mandate's fixture-strategy measurement, 3.1-3.5ms) are
the same order of magnitude, dominated by `ve_brain.DecisionRequest`/fingerprint construction and
`ve_brain.run_ev`'s own LCB computation — not by this mandate's additions. **No optimization performed**
(none required, per the measured numbers and mandate section 26's own "no optimization unless materially
required").

## 11. Rollback

All 11 mandate files (6 modified: `ev_engine.py`, `pipeline.py`, `real_ev_engine.py`, `reason_codes.py`,
`s5_opening_range_breakout.py`, `shadow_ledger.py`; 4 test files modified/added; 1 new production module,
`s5_ev_evidence.py`) were stashed out with `git stash push --include-untracked`, and the full
`strategy_platform` suite re-run against the resulting pre-mandate tree:

```
104 passed in 50.84s
```

— identical to the confirmed pre-mandate baseline (104/104, the exact state at `c30b056`). The stash was
restored (`git stash pop`), and the full suite re-confirmed at `174 passed`. Cleanly, fully reversible;
`ve_brain`'s sealed catalog/`decide_n6` and every other pipeline mechanic are unaffected by this change's
presence or absence.

## 12. Verdict (mandate section 30)

- `S5_REAL_EV_EVIDENCE_PACKAGED`
- `S5_REAL_EV_FAIL_CLOSED_HARDENING_PASS`
- `S5_MISSING_PROBABILITY_INPUTS_BLOCKER_CLOSED`
- `S5_GENUINE_REAL_EV_RUNTIME_PATH_PASS`
- `S5_OPERATIONAL_SHADOW_EVIDENCE_READY`
- `BROKER_ORDER_SUBMISSION_DISABLED` (`order_send_calls_total=0` throughout every new test)
- `READY_FOR_S5_OPERATIONAL_SHADOW_VALIDATION`

No evidence-integrity blocker remains. `REAL_EV_MATH_UNCHANGED` (zero diff to any `ve_brain` file),
`S5_SIGNAL_UNCHANGED` (zero diff to S5's session/OR/breakout/SL/TP/RR formulas),
`GENERIC_EV_AUTHORITY_PRESERVED` (48/48 prior tests unmodified in behavior, AST-verified zero
strategy-specific code). No MT5, no demo order, no live order.
