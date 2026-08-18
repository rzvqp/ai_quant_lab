# RANGE_STATE SEMANTIC SPEC V2 — contract, defect diagnosis, and remediation (ve_n1_replay 0.3.0)

Implements **STAT-RANGE-SEMANTIC-DIAGNOSIS-V2-v1.0** (Statistician, `@3aac2cc`, manifest v2.7.78 `@18aa2a1`), which
ruled the 0.2.0 detector `SEMANTIC_SPEC_DEFECT` — not an implementation bug. This is a **new contract, not a patch**:
`ve_n1_replay 0.3.0`. **`range_state.py`/`range_engine.py` (0.2.0) are unmodified**, kept for audit (verified: zero git
diff against the last committed state). N1 (0.1.1) stays byte-identical — untouched.

## Pre-implementation verification (per mandate: "signal any contradiction before writing code")

All seven cited sources verified present and correct in Git: `3aac2cc`, `18aa2a1`, 0.2.0 wheel SHA-256
`04b96a8b78b2d09bd8b54bd8044058282c6ab24bf2ac0f2aaec6c1f7a278786f`, build `1dc355b`, delivery `3577026`, Red Team
`RANGE_STATE_HANDOFF_PASS` `898e1b9` (RT-RANGE-0002), N1 `N1_INCREMENTAL_PASS` `6230ee5` (RT-N1-0002). The
Statistician's own document self-flags two contradictions (their `n_generated_total` formula going stale at 363, and
`aec8f07` naming a commit not a content-hash) — neither affects VE's work; `18aa2a1` is cited here correctly as
"manifest commit," not "config hash" or "content hash."

**One genuine gap found and disclosed**: `w` (zone half-width) and `s_max` (slope threshold) are declared
"PRE-ÎNREGISTRATĂ" in the spec but **no literal numeric value appears in the document or the manifest** (verified
against both). Per the mandate's explicit prohibition on selecting these by fitting to results, `RangeConfigV2`
exposes both as configurable parameters with **VE-proposed, Statistician-unratified** defaults (`w_atr=0.25`, reusing
the already-pre-registered v1 grid midpoint as a structural anchor, not re-derived from this construction's own
geometry; `s_max=0.15`, a new V2 parameter with no corpus precedent, chosen small and disclosed, not fit). Per the
Statistician's own blind-verification plan, empirical calibration against the real corpus (P1–P3) is Red Team's task
on RC-06/07/08 — **VE did not load real market data** (`data/market/OANDA_XAUUSD_M15.csv` exists in-repo but was
deliberately not read) to avoid exactly the "select parameters on results" the mandate forbids.

## The defect (Part 4 of the diagnosis, verified independently by VE)

0.2.0's definition contained three mutually-incompatible requirements:
1. `boundary := extremum of CONFIRMED swings in the window` — a **maximum over a growing set**, non-decreasing in
   window length.
2. `touch := close within 0.25×ATR of that boundary`.
3. `duration >= 96 bars`.

Reaching (3) forces the window to grow; growing it raises the boundary via (1); raising the boundary **retroactively
invalidates** the touches counted under (2), which were near the old, lower boundary. The longer the required
duration, the more of its own evidence the detector destroys — an unsatisfiable definition, not a wrong
implementation (which is why Red Team passed the handoff and Alpha reproduced zero-occupancy identically).

## The fix — Part 6 of the diagnosis, implemented exactly

- **`anchor` = MEDIAN** of confirmed swing extremes on that side, over the **bounded active window**
  (`range_window`, same pruning discipline as 0.1.1/0.2.0). Median is not monotone in window length, so it cannot
  self-invalidate; one new extreme does not move it materially.
- **`boundary_zone = [anchor − w, anchor + w]`** — a zone, not a line.
- **`touch`** = any bar whose `[low, high]` interval intersects the zone **as it existed at that bar** — evaluated
  causally, accumulated as a **monotone counter** (`touches_upper`/`touches_lower`, only ever incremented). The
  engine never re-scans history against a later zone, so a causally-confirmed touch cannot vanish retroactively —
  proven directly against 0.2.0 on the identical adversarial fixture (`test_regression_v1_loses_touches_v2_does_not`):
  0.2.0 drops `touches_upper` 8→1 and never regains `CONFIRMED`; 0.3.0 preserves `CONFIRMED` and keeps growing touches
  through the same event.
- **Internal BOS/CHoCH never invalidates.** `structure_events_inside` is a pure descriptor, computed by reusing the
  already-ratified `IncrementalRawAxesBuilder` (0.1.1) as an isolated internal counter (symbol `"V2_INTERNAL"`,
  entirely separate instance, never touching the real N1 engine) — reuse, not reimplementation of break detection.
- **Range vs. channel** — `|slope| × d_min ≤ s_max × ATR` (spec's literal formula; note **`d_min`**, the *fixed*
  duration constant, not the growing episode length — using the growing length was an early implementation mistake
  caught and fixed during this delivery: it made cumulative "drift" grow unboundedly with episode age regardless of
  actual trend, a false-positive channel classification for any long-lived range). Slope is OLS over a **bounded
  trailing window of `d_min_bars` closes** (a fixed-size deque, not the whole episode — an unbounded window grows
  noisier/more phase-sensitive as an episode ages; the trailing window is coherent with the same `d_min` used in the
  drift projection and stays `O(d_min_bars)`/bar, never `O(n)`). `structure_class ∈ {UNCLASSIFIED, RANGE_STATE,
  CHANNEL_UP, CHANNEL_DOWN}`; `consolidation_state=ESTABLISHED` only when `structure_class==RANGE_STATE`.
- **Two duration classes** (`RangeConfigV2.intraday()` d_min=24, `.multiday()` d_min=96) — separate, not merged;
  separate hypotheses if separately tested (multiplicity rule unchanged).
- **`TREND_PAUSE` overlap** unchanged in shape from 0.2.0: `precedence_rule="RANGE_STATE_OVER_TREND_PAUSE"` (hashed
  into `range_spec_id`), N1 direction retained as the `trend_context` attribute, never lost.
- **11 events** (`range-events-v2`): `RANGE_FORMING, RANGE_ESTABLISHED, RANGE_HIGH, RANGE_LOW, RANGE_MID,
  BREAKOUT_CANDIDATE, BREAKOUT_ACCEPTED_LONG, BREAKOUT_ACCEPTED_SHORT, BREAKOUT_RETEST, BREAKOUT_FAILED,
  LIQUIDITY_SWEEP`. `ACCEPTED_LONG`/`ACCEPTED_SHORT`/`FAILED` are mutually exclusive by state-machine construction
  (only one is reachable from `BREAKOUT_CANDIDATE` per episode); `LIQUIDITY_SWEEP` only fires from `ESTABLISHED`/
  `FORMING`, structurally disjoint from the candidate branch — verified zero same-bar collisions (P6).
- **F7 `RANGE_MID_NO_ENTRY` = SAFETY_GUARD**, unchanged in meaning from the CEO's final amendment (`d0d08c1`):
  explicit state, executable refusal (`entry_decision_v2`), separate `n_guards` counter, audited, survives
  snapshot/restart.

## A second bug caught and fixed during this delivery (disclosed per house convention)

The first `RANGE_ESTABLISHED` transition was silently never emitted — `_classify_and_maybe_establish` flipped the
machine state but had no `events` list threaded through to append to. Fixed by threading `events` through
`_maybe_confirm`/`_classify_and_maybe_establish` and appending the event on the `FORMING→ESTABLISHED` transition.
Caught by the reachability test before delivery, not after.

## Version matrix (mandate §6 — full)

| field | value |
|---|---|
| `artifact_version` (`VE_N1_REPLAY_VERSION`) | `0.3.0` |
| `range_state_contract_version` | `range-state-v2` |
| `range_state_schema_version` | `range-state-schema-v2` |
| `range_producer_version` | `range-producer-0.3.0` |
| `range_event_contract_version` | `range-events-v2` |
| `range_state_machine_version` | `range-state-machine-v2` |
| `range_snapshot_schema_version` | `range-state-snapshot-v2` |
| `range_ledger_schema_version` | `range-state-ledger-v2` |
| `range_reason_code_schema_version` | `range-reason-codes-v2` |
| `pkg_n1_contract_version` (package-declared) | `n1-replay-request-v2` — **unchanged from 0.2.0** |
| `pkg_raw_axis_schema_version` | `raw-axis-schema-v2` — **unchanged from 0.2.0** |
| `pkg_router_version` | `router-v2` — **unchanged from 0.2.0** |
| Statistician source commit | `3aac2cc` |
| Statistician manifest commit | `18aa2a1` (manifest v2.7.78) |
| N1 baseline identity | `0.1.1`, `N1_INCREMENTAL_PASS` `@6230ee5` |
| predecessor identity | `0.2.0`, wheel SHA-256 `04b96a8b…786f`, build `1dc355b`, delivery `3577026`, `RANGE_STATE_HANDOFF_PASS` `@898e1b9` |

`config_hash`/`range_spec_id`/`run_hash` are recomputed from the V2 parameter set — a 0.2.0 result is **automatically
non-comparable by type** with a 0.3.0 result (different `range_state_schema_version` string enters the hash).

## Compatibility (mandate §5)

- **N1 (0.1.1) byte-identical**: `RangeStateReplayEngineV2` composes the untouched `N1IncrementalReplayEngine`;
  `output_fingerprint` per bar verified equal to a bare `N1IncrementalReplayEngine` across trend_up/trend_down/
  uncertain/oscillation fixtures (`test_n1_full_parity_with_0_1_1`, 4 parametrized cases).
  `pkg_n1_contract_version`/`pkg_raw_axis_schema_version`/`pkg_router_version` (package-declared) are **identical
  strings** to 0.2.0 — verified by direct equality test — since N1's own contract surface did not change.
- **15 AI + 5 detector modules**: byte-identity untouched (same vendored closure as 0.1.1/0.2.0/0.3.0 — no diff, no
  re-vendor).
- **N3/N4/EV/N6**: not referenced anywhere in `range_state_v2.py`/`range_engine_v2.py` — unchanged, per the RT
  architectural verdict.
- **0.2.0 files**: `git diff` against the last commit is empty for `range_state.py` and `range_engine.py` — byte
  untouched. Both remain importable and functional (`test_0_2_0_module_files_untouched_still_functional`).

## Exact list of new/modified files (mandate §12)

**New** (0.2.0 untouched): `ve_n1_replay/range_state_v2.py`, `ve_n1_replay/range_engine_v2.py`,
`tests/test_range_state_v2.py`, `tools/benchmark_range_v2.py`, `HANDOFF_MANIFEST-0.3.0.json`.
**Modified** (additive only — see diff, no existing 0.1.x/0.2.0 constant changed in meaning):
`ve_n1_replay/version.py` (VE_N1_REPLAY_VERSION bump + new `*_V2` constants), `ve_n1_replay/__init__.py` (new
exports), `pyproject.toml` (version bump), `CHANGELOG.md`, `PROJECT_STATE.md`.

## Test matrix — 28 mandate items, all covered (`tests/test_range_state_v2.py`, 45 tests)

| # | item | test(s) |
|---|---|---|
| 1 | stable anchor on later extreme | `test_anchor_stable_and_touches_survive_new_extreme` |
| 2 | old touches don't vanish retroactively | same (touches sequence asserted non-decreasing) |
| 3 | wick-only touch | `test_wick_only_touch_counts` |
| 4 | non-intersecting bar → no touch | `test_non_intersecting_bar_no_touch` |
| 5 | range neutral bullish/bearish | `test_range_classification_neutral_to_bias_direction` |
| 6 | range inside a larger trend | `test_range_in_larger_trend_boundary_mechanics_unaffected` |
| 7 | internal BOS/CHoCH doesn't destroy outer range | `test_internal_bos_choch_does_not_invalidate` |
| 8 | real outer-structure invalidation | `test_real_outer_invalidation_on_accepted_break` |
| 9 | ascending channel → not range | `test_channel_up_never_range_state` (×4 drift values) |
| 10 | descending channel → not range | `test_channel_down_never_range_state` (×4 drift values) |
| 11 | breakout candidate | `test_breakout_candidate_reachable` |
| 12 | accepted long | `test_breakout_accepted_long` |
| 13 | accepted short | `test_breakout_accepted_short` |
| 14 | retest | `test_breakout_retest` |
| 15 | failed breakout | `test_breakout_failed` |
| 16 | liquidity sweep | `test_liquidity_sweep` |
| 17 | accepted vs failed/sweep exclusivity | `test_accepted_failed_sweep_mutually_exclusive_no_same_bar_collision` |
| 18 | zero-lookahead | `test_zero_lookahead` |
| 19 | structural_start_ts vs confirm_ts | `test_structural_start_vs_confirm_ts_ordering` |
| 20 | chunk invariance | `test_chunk_invariance` (×5 chunkings) |
| 21 | determinism | `test_determinism` |
| 22 | two instances, no shared state | `test_two_instances_no_shared_state` |
| 23 | snapshot/restart bit-identical in every state | `test_snapshot_restart_every_machine_state_incl_mid_breakout` |
| 24 | snapshot mid-breakout | same (cut points sweep through CANDIDATE/ACCEPTED/RETEST) |
| 25 | contract/config/source mismatch → refuse | `test_mismatch_config_refused`, `test_mismatch_n1_identity_refused`, `test_mismatch_predecessor_version_snapshot_refused_both_directions` |
| 26 | F7 explicit + persistent | `test_f7_explicit_persistent_zero_entry` |
| 27 | full N1 0.1.1 parity | `test_n1_full_parity_with_0_1_1` (×4), `test_n1_contract_versions_unchanged_from_0_2_0` |
| 28 | rollback reproducible | packaging-level (empty-venv install/downgrade/upgrade), see delivery report |

Plus the **regression test that fails on the old moving-boundary definition**:
`test_regression_v1_loses_touches_v2_does_not` runs 0.2.0 (unmodified) and 0.3.0 side by side on the identical
adversarial fixture and asserts 0.2.0 *does* lose `CONFIRMED` (proving the defect is real and reproduced) while 0.3.0
does not (proving the fix). Plus reachability (`test_reachability_all_v2_events`, all 11 events + `RANGE_STATE`),
no forbidden imports (`test_no_forbidden_imports_in_source`, inherited pattern), and a direct white-box test of the
classification decision (`test_slope_classification_decision_range_vs_channel`) isolating the branch logic from
whole-engine fixture noise.

## A note on threshold sensitivity (disclosed, not hidden)

On deterministic synthetic oscillations, sustaining `structure_class==RANGE_STATE` at the shipped default `s_max=0.15`
proved sensitive to the exact shape of the price series — a sharp, perfectly-periodic zigzag aliases badly against
any fixed-size trailing regression window (confirmed: the OLS math itself is exactly correct — hand-verified on flat
and linear-ramp inputs — the sensitivity is in achieving literally-zero measured trend on a hand-crafted deterministic
fixture, not a code defect). The mandate's actual gating requirement, **P2 — no negative control ever produces
RANGE_STATE** — holds robustly across every channel/drift variant tried (8 total, deterministic and randomized,
`s_max` from 0.15 to 1.2), with zero exceptions. This threshold-sensitivity finding is exactly the kind of thing VE is
supposed to surface for Statistician/Red Team's ratification of the numeric defaults, not silently paper over by
tuning fixtures until the unratified default looks good.

## Prohibitions honored

No backtest, no PnL, no cost gate, no p-value, no selection on results, no Alpha run, no AI Trader modification, no
LIVE_SHADOW, no `set_authority`/`order_send`/broker, no SEALED/OOS access, no real market data loaded (`range1.pdf`/
`range2.pdf` do not appear anywhere in the resolved corpus manifest and were never referenced). `n_generated_total`,
`m_inference`, tombstones, and existing Alpha verdicts untouched. Status: **`READY_FOR_RANGE_SEMANTIC_REVALIDATION`**
— not self-declared PASS.
