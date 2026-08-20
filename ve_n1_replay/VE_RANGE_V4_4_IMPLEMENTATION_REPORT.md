# VE RANGE V4.4 — Implementation delivery report

**Mandate**: `VE-RANGE-V4_4-IMPLEMENTATION-001`. **Date**: 2026-08-20. **Division**: Validation Engine (VE).
**Directive constraints honored**: `IMPLEMENT_FROZEN_DESIGN_ONLY`, `NO_NEW_RESEARCH`, `NO_RECALIBRATION`,
`NO_PARAMETER_CHANGES`, `NO_MB3_ACCESS`, `NO_FRESH_BLIND_EXECUTION`, `PRESERVE_V4_3`,
`FREEZE_IMPLEMENTATION_BEFORE_RED_TEAM`.

Structured against the mandate's own §24 (25 required items), in order.

---

## 1 — Authoritative source chain

Every commit below was independently re-verified this mandate (existence via `git cat-file -t`, local=remote
on `discovery-mk-matrix-v1` across all 4 mirrors) before being used as a source of truth:

| Commit | Content |
|---|---|
| `071fbd7` | VE diagnostic (V3→V4.3 defect catalogue) |
| `3be88a1` | Red Team diagnostic audit |
| `236e8e7` | VE V4.4 design (`VE_RANGE_V4_4_DESIGN_AND_PREREGISTRATION.md`) |
| `f241698` | VE convergence (`VE_RANGE_V4_4_CONVERGENCE_AND_REVIEW_PACKAGE.md`) |
| `ca550d4` | Red Team V4.4 design audit |
| `c57d103` | V4.4 mechanism freeze (`VE_RANGE_V4_4_DESIGN_FREEZE.md`) |
| `967222a` | V4.4 pre-registered calibration protocol |
| `898f149` | V4.4 calibration results, final parameter registry, verdict `V4_4_CALIBRATION_PASS_WITH_NONBLOCKING_NOTES` — **HEAD at implementation start, verified** |

No document outside this chain was treated as normative. `bc6b9dc` (F1-only remediation) is cited only for its
implementation-fingerprint *procedure* precedent (item 6 below), not as part of the V4.4 design chain itself.

---

## 2 — Exact files added / changed

**Added (8 files, zero pre-existing files modified):**

| File | Bytes | Role |
|---|---|---|
| `ve_n1_replay/ve_n1_replay/range_semantic_v4_4.py` | 67,340 | Core V4.4 state machine, config, pure signal functions |
| `ve_n1_replay/ve_n1_replay/range_engine_v4_4.py` | 9,599 | N1-composing engine wrapper (mirrors `range_engine_v4_3.py`) |
| `ve_n1_replay/tests/test_v4_4_internal_parity.py` | — | INTERNAL-depth byte-identity proof vs V4.3 |
| `ve_n1_replay/tests/test_v4_4_transitions.py` | — | T1–T9+T-KILL, episode identity, WEAKENING, gate priority |
| `ve_n1_replay/tests/test_v4_4_causality.py` | — | §8/§14 causality invariants |
| `ve_n1_replay/tests/test_v4_4_snapshot_robustness.py` | — | §11 snapshot/restore fail-closed matrix |
| `ve_n1_replay/tests/test_v4_4_reason_code_reachability.py` | — | §13 mechanical reachability, all 11 new codes |
| `ve_n1_replay/tests/test_v4_4_adversarial_suite.py` | — | §16, all 22 pre-registered scenarios |
| `ve_n1_replay/VE_RANGE_V4_4_IMPLEMENTATION_REPORT.md` | — | This document |

**Changed:** none. `range_semantic_v4_3.py` and `range_engine_v4_3.py` are byte-identical to HEAD (`898f149`)
— see item 3.

---

## 3 — V4.3 byte-preservation proof

```
$ git diff --stat HEAD -- ve_n1_replay/ve_n1_replay/range_semantic_v4_3.py ve_n1_replay/ve_n1_replay/range_engine_v4_3.py
(no output, exit code 0)
$ git diff HEAD -- ve_n1_replay/ve_n1_replay/range_semantic_v4_3.py ve_n1_replay/ve_n1_replay/range_engine_v4_3.py | wc -l
0
```
Zero lines changed. `V4_3_BYTE_UNTOUCHED` holds. Every V4.3 symbol reused by V4.4 (`Cluster`, `Excursion`,
`Registry`, `Structure`, `Depth`, `MacroState`, `InternalState`, `ROLES_V43`, `RangeEventV43`,
`ContractErrorV43`, `ConfigNotRatifiedErrorV43`, `SNAPSHOT_CONTRACT_MISMATCH`, `REASONS_V43`,
`degeneracy_check`, `evaluate_candidate_with_n_touch`, `offer_swing`, `assign_level`, `promotion_check`,
`sweep_reversal_confirmed`, ~20 reason-code constants) is **imported**, never copy-pasted-and-modified.

The one unavoidable type-boundary friction — V4.3's pure functions are typed `cfg: ConfigV43`, and `ConfigV44`
deliberately does not subclass `ConfigV43` (§4 below) — is resolved on the **V4.4 side only**, via a local
`_as_v43_cfg()` cast helper in `range_semantic_v4_4.py`. No V4.3 signature changed.

---

## 4 — Final parameter registry

Reproduced exactly from `898f149` §16, verified field-for-field against `ConfigV44`'s defaults:

| Field | Value | Status |
|---|---|---|
| `ER_max` | 0.5 | anchor |
| `RND_max` | 1.0 | anchor |
| `ALT_MIN` | 0.5 | ratified reuse (unchanged from design phase) |
| `W` | 29 | derived (`= d_macro`) |
| `MIN_TRAVERSALS` | 1 | derived |
| `ER_weakening` | 0.75 | derived |
| `RND_weakening` | 2.0 | derived |
| `WEAKENING_MAX_BARS` | 22 | derived (`= K_reentry`) |
| `IOU_CONTINUE` | 0.5 | derived |
| `GAP_MAX` | 12 | derived (`= d_internal`) |

Plus the 9 unchanged V4.3 fields (`d_macro=29, d_internal=12, n_touch=2, K_reentry=22, N_accept=3, K_struct=2,
n_external_swings=2, atr_window=14, w_atr=0.80`) and unchanged ATR provenance strings. No value substituted,
rounded, or defaulted differently from `898f149`.

---

## 5 — `config_id()`

```
computed:  23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969
frozen (898f149 §16): 23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969
match: True
```
Recomputed independently from the actual `ConfigV44` implementation (not copy-pasted), using the identical
formula to `ConfigV43.config_id()` (sha256 over sorted dataclass fields + 5 derived properties, JSON
`sort_keys=True`, compact separators). **No `V4_4_CONFIG_ID_MISMATCH`.** Re-verified after every subsequent
edit this mandate, most recently post-freeze (item 24).

---

## 6 — Implementation fingerprint

Procedure identical to the `RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT` precedent (`bc6b9dc`, F1-only
remediation): compute `sha256` of the finalized source bytes; the fingerprint **constant** embedded in code is
a human-readable label (V4.3's own precedent is `"f1-only-f5-deferred-2026-08-20"`, not a raw digest), chosen
at freeze time.

```
range_semantic_v4_4.py   67,340 bytes  sha256=833aedfd835e6f95b62d61784de1d865cf0dd8f6dfc5edc100eb6fe7d94a09db
range_engine_v4_4.py      9,599 bytes  sha256=1371444c98f1dc1fc9e057d0c8a666a82d51f21bf3d54cb5805bc93a6222de97
combined (concatenated, semantic_then_engine order)
                                       sha256=b799ec6f5ec077c55e38ae17d8fa469a8eb82cc6fbaeb75db3b8d74015f85e23
```

`RANGE_HIERARCHICAL_V4_4_IMPLEMENTATION_FINGERPRINT = "v4-4-implementation-freeze-2026-08-20"` — distinct from
V4.3's label, embedded in `snapshot_state()`/`restore_state()`, checked on every restore (fail-closed).

---

## 7 — Contract / snapshot / reason-code identities

- `contract_version = "range-hierarchical-v4.4"` (`RANGE_HIERARCHICAL_V4_4_CONTRACT_VERSION`)
- `config_id` — item 5
- `implementation_fingerprint` — item 6
- `REASONS_V44` = `REASONS_V43` (29, unrenumbered) + 11 new = **40**, asserted at import time for exact count
  and uniqueness (`assert len(REASONS_V44) == 40`, `assert len(set(REASONS_V44)) == 40`)
- New codes: `INSUFFICIENT_EFFICIENCY`, `INSUFFICIENT_TRAVERSAL`, `INSUFFICIENT_ALTERNATION_EVIDENCE`,
  `EXCESSIVE_NET_DISPLACEMENT`, `RANGE_CANDIDATE_PRESENT`, `RANGE_WEAKENING`, `WEAKENING_RECOVERED`,
  `WEAKENING_PERSISTENCE_TERMINATED`, `EPISODE_CONTINUATION`, `EPISODE_MERGED`, `EPISODE_REPLACEMENT`

---

## 8 — State-machine implementation mapping

5-state MACRO lifecycle (`CANDIDATE→FORMING→CONFIRMED→WEAKENING→TERMINATED`), reported via the new
`_macro_state_label()` (INTERNAL keeps V4.3's own `MacroState`/`InternalState` labeling, untouched — see item
14). Transition table (`f241698` §3) implemented in `_evaluate_macro_formation()` (T1–T3) and `_step_macro()`
(T-KILL, T4–T9):

| Row | Trigger | Implementation |
|---|---|---|
| T-KILL | `degeneracy_check` (priority 0, checked before everything) | `_step_macro` top, → `_kill_macro` |
| T1 | entry to CANDIDATE | swing detection → `StructureV44` construction |
| T2 | width+touch → FORMING, `RANGE_CANDIDATE_PRESENT` once | `_evaluate_macro_formation`, `_candidate_present_emitted` flag |
| T3 | duration + 4-signal gate → CONFIRMED, `OK_RANGE_MACRO` | `_evaluate_macro_formation`, fixed ER→traversal→RND priority |
| T4 | excursion opens → WEAKENING(`EXCURSION_PENDING`), priority 4a | `_step_macro`, unconditional label override |
| T5 | trailing ER/RND past looser ceiling → WEAKENING(`TRAILING_DEGRADATION`), priority 4b | `_step_macro`, only when T4 false |
| T6 | reentry/`SWEEP_CONFIRMED` → CONFIRMED, `WEAKENING_RECOVERED` | `_step_macro`, excursion resolution branch |
| T7 | ER/RND recover to strict ceiling → CONFIRMED, `WEAKENING_RECOVERED` | `_step_macro`, trailing-degradation branch |
| T8 | `BREAKOUT_ACCEPTED` → TERMINATED (absolute priority) | `_close_macro_via_breakout` |
| T9 | `WEAKENING_MAX_BARS` exceeded → TERMINATED, `WEAKENING_PERSISTENCE_TERMINATED` | `_terminate_macro_weakening_persistence` |

Episode identity (`f241698` §6, priority MERGE>CONTINUATION>REPLACEMENT) in
`_episode_identity_for_new_macro()`, invoked from `_offer_swing_everywhere()` at new-MACRO-candidate
formation.

---

## 9 — Transition test matrix

`tests/test_v4_4_transitions.py`, 27 tests: T-KILL (degenerate via ATR spike on confirmed structure;
inverted, direct construction) · T1→T2 (`RANGE_CANDIDATE_PRESENT` emitted exactly once) · T2→T3 (genuine
oscillator confirms) · T3 rejects a shallow channel that satisfies width/touch/duration · T3 gate priority (3
numerically-verified fixtures: all-three-fail→ER wins, ER-passes→traversal wins, only-RND-fails→RND) ·
alternation supporting-only (3 cases) · T4→T6 · T4→T8 · T8 leaves no stale confirmed range · T5 entry · T7
recovery (both thresholds) · T9 persistence · **the WEAKENING indefinite-holding-state regression test**
(counter increments unconditionally in the ER∈(0.5,0.75] middle zone, 22/22 bars asserted) · dual-trigger
T4-over-T5 (label override + counter pause) · episode identity ×5 (replacement/continuation/forced-
replacement/gap-exceeded/merge-forced-reachable) · `test_episode_merge_is_structurally_unreachable` (4-cycle
mixed scenario, `EPISODE_MERGED` absent, `EPISODE_REPLACEMENT`/`EPISODE_CONTINUATION` present) · 2 forbidden-
transition tests (WEAKENING never silently reverts; terminated id never reused).

---

## 10 — Directional-gate tests

ER/traversal/RND individually and combined, deterministic priority (item 9), plus adversarial #4/#5 (shallow
channel up/down), #6/#7 (strong trend), #8 (stair-step), #12 (temporarily-fitting directional move), #13
(slow boundary migration exceeds `RND_max`), #14 (one-sided touch concentration, alternation non-gating).

---

## 11 — Confirmation-timing invariance

`tests/test_v4_4_causality.py::test_confirmation_timing_invariant_across_96_288_480_bar_containers`: a shared
61-bar causal prefix (itself exercising `TOO_SHORT_MACRO→OK_RANGE_MACRO`) embedded in 96/288/480-bar
containers with **three different, verified-divergent tails**; per-bar `(macro_id, macro_reason, macro_state,
macro_weakening_reason, internal_reason, internal_state, events)` asserted identical through the shared
prefix across all three. Plus: `NO_LOOKAHEAD` (truncated vs full replay), `PREFIX_INVARIANCE` (9 truncation
points), `CHUNK_INVARIANCE`/`SNAPSHOT_RESTART_INVARIANCE` (3 arbitrary split points with snapshot/restore
between), `DETERMINISTIC_REPLAY` (two independent runs, identical output), `CONFIG_ID_SENSITIVITY` and
`IMPLEMENTATION_ID_SENSITIVITY` (mismatched snapshots refused, engine left unchanged). 7 tests total, all
passing.

---

## 12 — WEAKENING tests

Both entry paths (T4 excursion, T5 trailing) individually proven; dual-trigger priority (T4 unconditionally
overrides, counter pauses not resets) proven; max persistence (`WEAKENING_MAX_BARS=22`) proven to terminate;
recovery proven to require the **strict** threshold (`ER_max`/`RND_max`), not the looser entry threshold;
genuine directional continuation proven to terminate via T9; accepted breakout proven to leave no stale
confirmed range; snapshot/restart preserves WEAKENING state exactly (covered by the general snapshot
round-trip plus the chunk-invariance test, which crosses a WEAKENING-adjacent window). **No silent fallback to
V4.3 persistence behavior** — V4.3 has no WEAKENING state at all; this is new, additive behavior gated
entirely behind `reached_confirmed` structures, INTERNAL depth untouched (item 14).

---

## 13 — Episode-identity tests

All 6 mandate-required scenarios: (1) one long range with internal rotations does not explode into repeated
macro episodes (adversarial #18, `len(macro_history) <= 1`) · (2) two genuinely independent adjacent ranges
do not merge into one eternal episode (adversarial #17, distinct structure ids, `EPISODE_REPLACEMENT`) · (3)
boundary migration (adversarial #13) · (4) temporary breakout+re-entry (adversarial #11, #19 — same identity
preserved through `WEAKENING_RECOVERED`) · (5) overlapping candidates (`test_episode_identity_continuation_
when_non_breakout_termination_overlaps_within_gap`) · (6) replacement behavior (default, gap-exceeded,
forced-after-breakout — 3 dedicated tests). No scoring-based merge heuristic invented; priority is the exact
MERGE>CONTINUATION>REPLACEMENT order from `f241698` §6.

---

## 14 — Known-risk behavior

INTERNAL/F4 untouched (mandate §19 of the original design mandate, reaffirmed here): `_step_internal`, the
INTERNAL branches of `_offer_swing_everywhere`, `_kill_internal`, `_close_internal_via_breakout`, and
`_channel_or_state_label` are direct, line-for-line copies of V4.3's own orchestration for that depth.
**Empirically proven**, not just asserted by code inspection — `tests/test_v4_4_internal_parity.py` (5 tests)
runs identical bars through `RangeSemanticProducerV43` and `RangeSemanticProducerV44` in parallel (matched
configs) and diffs every INTERNAL field bar-by-bar, across a mixed macro+internal-rotation fixture, a
15-cycle oscillator, a pure-directional fixture, 4 ATR values, and a snapshot-restart-at-bar-20 fixture. Zero
divergence in all 5.

---

## 15 — Adversarial suite results

`tests/test_v4_4_adversarial_suite.py`, all 22 pre-registered scenarios (`VE_RANGE_V4_4_DESIGN_AND_
PREREGISTRATION.md` §10, items 1–20, plus §12's two self-falsification counterexamples as 21/22) — **22/22
pass against the pre-registered expected chronology**, not post-hoc-invented expectations:

- #1–3, #9–11, #17–20: confirm/reconfirm/recover/preserve-identity as designed.
- #4–8, #12–14: never confirm (directional discrimination gate), or confirm without alternation blocking it
  (#14, supporting-only by design).
- #15–16: `start_ts` anchors to first-detectable swing (unchanged V4.3 limitation, not solved here, not
  claimed solved); truncated-at-window-end never fabricates a confirmation.
- **#21 (slow drifting equilibrium) and #22 (violent zigzag): both CONFIRM.** This is not a new finding — it
  is the exact, already-disclosed, non-blocking risk from `898f149` §7 (shallow-channel/gentle-drift
  ambiguity) and `236e8e7` §12 (zigzag "quality" dimension explicitly out of scope, "not solved, not claimed
  solved"). Recorded honestly per mandate §10, **not** silently hidden and **not** "fixed" via undisclosed
  recalibration (`NO_RECALIBRATION`/`NO_PARAMETER_CHANGES` honored).

---

## 16 — V4.3 regression results

Rollback test (item 22) is the authoritative evidence: with both V4.4 files and all 6 V4.4 test files
physically removed from the tree, the remaining suite — **394 tests, 100% unmodified V4.3 + pre-existing
repository tests** — passes with **zero failures, zero collection errors**. `git diff` confirms zero bytes of
V4.3 changed (item 3). No reduction in historical coverage; no test deleted or weakened to obtain green
status.

---

## 17 — Full repository test results

With V4.4 restored: **470 passed**, 0 failed, 0 errors (`python -m pytest tests/ -q`, 118.08s), reproduced
twice independently after the fingerprint freeze (item 24). 394 V4.3-baseline + 76 V4.4-new (internal parity
5, transitions 27, causality 7, snapshot robustness 14, reason-code reachability 2, adversarial suite 22 incl.
the count-check — see per-file collect counts in the raw session log).

---

## 18 — mypy --strict results

```
$ python -m mypy --strict ve_n1_replay/range_semantic_v4_4.py ve_n1_replay/range_engine_v4_4.py
Success: no issues found in 2 source files
```
Clean after resolving 25 initial findings: an explicit `__all__` (matching V4.3's own `--no-implicit-reexport`
convention), a local `_as_v43_cfg()` cast helper for the deliberate `ConfigV44`/`ConfigV43` structural (not
nominal) compatibility, a `_iou` tuple-narrowing fix, and a `_offer_swing_everywhere` restructure (separate
MACRO/INTERNAL branches instead of a heterogeneously-typed loop — behavior-preserving, reverified against the
full suite after the change). V4.3 files reconfirmed clean and untouched.

---

## 19 — Mutation-test results

All 6 named mutations applied via scripted source-text patch, one at a time, against a byte-verified backup:

| # | Mutation | Result |
|---|---|---|
| 1 | Disable ER hard gate | `test_t3_gate_priority_all_three_fail_reports_efficiency_first` FAILS as expected |
| 2 | Remove WEAKENING timeout | `test_t9_persistence_terminates_after_weakening_max_bars` + the indefinite-holding-state regression test FAIL |
| 3 | Reverse T3 gate-check priority | the same gate-priority test FAILS (reports `INSUFFICIENT_TRAVERSAL` instead of `INSUFFICIENT_EFFICIENCY`) |
| 4 | Disable merge logic | `test_episode_merge_logic_itself_is_correct_when_precondition_is_forced` FAILS |
| 5 | Break confirmation timing (absolute vs relative-to-`start_ts` duration) | 2 adversarial-suite tests (#16, #21) FAIL — full-suite run used to catch it, since the dedicated 96/288/480 test starts its shared structure at bar 0 and does not distinguish absolute-from-relative timing by construction |
| 6 | Accept wrong config/contract/fingerprint snapshot | 5 tests FAIL across `test_v4_4_snapshot_robustness.py` and `test_v4_4_causality.py` |

After each mutation, the file was restored from the pre-mutation backup and byte-diffed
(`diff -q` confirmed identical) before proceeding to the next. Final restoration re-verified: mypy clean, full
470-test suite green.

---

## 20 — Complexity / memory results

Empirical, wall-clock measurement over a 1,440-bar varied replay (oscillating macro ranges with periodic
forced episode churn), measured in 200-bar chunks:

- **Per-chunk wall time**: flat at ≈0.006s/chunk from bar 200 through bar 1,400 — no growth trend, no O(n)
  or O(n²) accumulation.
- **Snapshot size**: flat at ≈2,000–2,100 JSON bytes throughout the same replay — bounded, not growing with
  replay length.
- **Bounded-deque enforcement**, directly verified (not inferred from code reading alone): `_macro_history`/
  `_internal_history` (`maxlen=64`) — 100 direct appends → exactly 64 retained, oldest-first eviction
  confirmed (ids 36–99 retained after 100 appends of ids 0–99). `_trailing_closes` (`maxlen=W=29`),
  `_touch_tags` (`maxlen=64`) — confirmed by construction and by the gate functions operating correctly on
  windows that never exceed these sizes.
- ER/traversal/RND are computed by re-scanning the bounded `W`-length window each bar — O(W)=O(29) per bar,
  not streaming-incremental, but genuinely bounded (never grows with structure lifetime), consistent with the
  project's established bounded-vs-unbounded standard (the 0.4.1/RT-RANGE-0004 precedent).
- No V4.4-owned unbounded deque/list exists. INTERNAL-depth memory is entirely V4.3's own, untouched.

---

## 21 — Snapshot robustness tests

`tests/test_v4_4_snapshot_robustness.py`, 14 tests, producer-level (`restore_state`) and engine-level
(`RangeSemanticEngineV44.restore`): round-trip sanity baselines (2, proving the refusal tests are non-vacuous)
· missing field · wrong contract_version · wrong config_id · wrong implementation_fingerprint · V4.3-snapshot-
shape refused · wrong-typed field · foreign snapshot type refused (engine) · real `RangeSnapshotV43` object
refused by the V4.4 engine · corrupted `range_state`, engine left unchanged · mismatched config_id at engine
level · construction refuses without `acknowledge_construction_only=True` · construction refuses on
`config_id()` mismatch (mandate §4 enforcement, live).

**A real, genuine bug was found and fixed here**: the original `restore_state()` mutated `self` field-by-field
in place, so a failure partway through (missing/wrong-typed field) left the producer in a mixed old/new state
— violating "no partial state mutation on failed restore." Confirmed as an **inherited** V4.3 weakness too
(reproduced identically against `RangeSemanticProducerV43.restore_state()`), not something newly introduced.
Fixed **only in the V4.4 file** (V4.3 remains byte-untouched, item 3) by building the entire restored state
into a fresh scratch instance and swapping `self.__dict__` only after every field succeeds — the same
isolate-then-commit discipline `RangeSemanticEngineV44.restore()` already used at the engine level, now also
holding at the producer level. All 14 tests pass post-fix; 2 of them (missing field, wrong-typed field) were
the tests that originally caught the bug.

---

## 22 — Rollback proof

Procedure: moved both V4.4 implementation files and all 6 V4.4 test files out of the tree
(`ve_n1_replay/ve_n1_replay/range_semantic_v4_4.py`, `range_engine_v4_4.py`, `tests/test_v4_4_*.py`) to a
scratch location. Confirmed `ve_n1_replay/__init__.py` has zero references to any V4.4 symbol (fully additive,
no wiring dependency). Ran `python -m pytest tests/ -q`: **394 passed, 0 failed, 0 errors** — the exact V4.3 +
pre-existing baseline, completely unaffected by V4.4's absence. Moved all 8 files back; re-ran the full suite:
**470 passed**, confirming clean restoration with no residual effect from the rollback exercise itself.

---

## 23 — MB3 preservation proof

Zero MB3 files were read, referenced, imported, or executed against at any point in this implementation
mandate. Every fixture used in every test file is synthetic, constructed via the pre-existing `legs_bars`/
`osc_bars`/`mk` helpers already established in `tests/test_range_semantic_v4_3.py`, or via direct, explicit
`StructureV44`/`ConfigV44` construction with hand-specified numeric values (verified numerically via standalone
probes before being written into assertions — see items 9–15). No MB3-001→024 scoring, no MB3-025→048
inspection, no tuning informed by any MB3 outcome. `MB3_025_048_SEALED` honored throughout.

---

## 24 — Implementation-freeze proof

Order of operations, in the sequence actually executed: (1) all semantic code changes completed and verified
(mutation testing, item 19) *before* the fingerprint was set; (2) `RANGE_HIERARCHICAL_V4_4_IMPLEMENTATION_
FINGERPRINT` changed from the `"PENDING_FREEZE"` placeholder to `"v4-4-implementation-freeze-2026-08-20"` —
the **only** edit made after mutation-testing concluded; (3) mypy --strict reconfirmed clean; (4) `config_id()`
reconfirmed to match the frozen calibration value; (5) full suite reconfirmed green **twice**, independently
(470 passed both times, 118.08s and prior). No semantic change occurs after this point. Recorded:
`V4_4_IMPLEMENTATION_FROZEN_FOR_RED_TEAM`.

---

## 25 — Exact remaining risks

1. **Shallow-channel / slow-drifting-equilibrium false-accept** (adversarial #21) — already disclosed in
   `898f149` §7, re-confirmed here, not solved (mandate explicitly forbids recalibrating to chase it).
   Non-blocking per the pre-registered calibration criteria.
2. **Violent-zigzag quality/volatility dimension** (adversarial #22) — disclosed in `236e8e7` §12 as
   explicitly out of scope for this mechanism ("not solved, not claimed solved"). A genuinely different
   signal dimension (path "quality," not directional bias) that no signal in this design addresses.
3. **INTERNAL parity rests on this mandate's own test proof**, not an independent Red Team re-derivation —
   the line-for-line-copy claim is empirically strong (5/5 tests, 4 ATR values, a snapshot-restart case) but
   has not been adversarially attacked by a party other than its author.
4. **Mutation testing covered exactly the 6 named mutation classes**, applied as targeted, hand-authored
   source patches — not exhaustive line/branch/operator mutation coverage via an automated framework. Each
   mutation was caught by at least one, usually several, tests; absence of a caught mutation for an
   *un-named* mutation class was not checked.
5. **Complexity measurement is empirical wall-clock**, environment-dependent (this machine, this run) rather
   than a formal asymptotic proof — the flat trend across 1,440 bars and the direct 100-append deque-cap check
   are strong, but not a mathematical guarantee against a pathological input class not exercised here.
6. **Two implementation-detail resolutions were made during coding**, disclosed in the module docstring and
   this report: the RND trailing-window-vs-`c0` reference (the calibration's own numeric values take
   precedence over an earlier, less-precise implementation-plan sketch), and the alternation-evidence wiring
   (found genuinely unwired during construction, fixed to be reachable-but-still-non-gating). Both are
   additive/corrective, not redesigns, but neither was independently re-ratified by Red Team before this
   delivery — that ratification is exactly what `RT-RANGE-V4_4-IMPLEMENTATION-AUDIT` (item 26) is for.
7. **`_awaiting_role` type-fidelity bug and the `restore_state` non-atomicity bug** (items 21) were both found
   and fixed during this mandate's own construction/testing phase, not by an external reviewer — the fixes are
   tested, but, as with (5), independent confirmation is Red Team's role next, not self-certified here.

---

## Verdict

**`V4_4_IMPLEMENTATION_READY_FOR_RED_TEAM_AUDIT`**

Not `V4_4_VALIDATED`, not `BLIND_PASS`, not `ALPHA_READY`, not `AI_TRADER_READY` — none of these are
self-declared here, consistent with mandate §25.

**Next owner**: Red Team. **Required next step**: `RT-RANGE-V4_4-IMPLEMENTATION-AUDIT` — verifying code
faithfully implements the frozen design; all identities (config/contract/snapshot/reason-code/fingerprint);
non-vacuity of the test suite; causality; snapshot behavior across the V4.3/V4.4 boundary; zero MB3
contamination; and the honesty of the disclosed construction results (items 25.1–25.6 above). Only after a
Red Team PASS may a fresh, independent blind batch be consumed against this detector — not authorized by this
document.

**Not authorized by this mandate** (§27, restated): Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker,
order submission, or live trading of any kind.
