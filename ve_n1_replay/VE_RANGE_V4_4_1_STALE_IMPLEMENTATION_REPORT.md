# VE RANGE V4.4.1 — T-STALE implementation delivery report

**Mandate**: `VE-RANGE-V4_4_1-STALE-IMPLEMENTATION-001`. **Date**: 2026-08-21. **Division**: Validation Engine (VE).
**Directive constraints honored**: `IMPLEMENT_FROZEN_CALIBRATED_DESIGN_ONLY`, `PARAMETERS_29_4_12_3_FIXED`,
`NO_RECALIBRATION`, `NO_TRAVERSAL_CHANGE`, `NO_ER_RND_CHANGE`, `NO_FB14_SCORING`, `NO_MB3_ACCESS`, `NO_FRESH_BLIND`,
`PRESERVE_V4_4`, `TRACK_MIN_ALTERNATION_FRAGILITY`, `FREEZE_BEFORE_RED_TEAM`.

Structured against the mandate's own §26 (24 required items), in order.

---

## 1 — Authoritative source chain

Every commit below was independently re-verified this mandate (existence via `git cat-file -t`, local=remote on
`discovery-mk-matrix-v1` across all 4 mirrors, HEAD confirmed = `9116c2b`, clean working tree apart from
pre-existing unrelated dirty files) before being used as a source of truth:

| Commit | Content |
|---|---|
| `3bb61cf` | VE V4.4 implementation (frozen, byte-untouched by this mandate) |
| `dfebe8f` | Red Team V4.4 implementation audit |
| `b1dcf92` | VE traversal-failure diagnostic (`VE_RANGE_V4_4_TRAVERSAL_DIAGNOSTIC.md`) |
| `9aba9b7` | VE T-STALE design (`VE_RANGE_V4_4_1_STALE_CANDIDATE_DESIGN.md`) |
| `eeb082e` | Red Team design audit |
| `e2b65bf` | T-STALE mechanism freeze (`VE_RANGE_V4_4_1_T_STALE_DESIGN_FREEZE.md`) |
| `8605cb2` | Pre-registered calibration protocol |
| `9116c2b` | Calibration results, final parameter registry, verdict `V4_4_1_CALIBRATION_PASS_WITH_NONBLOCKING_NOTES` — **HEAD at implementation start, verified** |

No document outside this chain was treated as normative.

---

## 2 — Exact files added / changed

**Added (4 files, zero pre-existing files modified):**

| File | Bytes | Role |
|---|---|---|
| `ve_n1_replay/ve_n1_replay/range_semantic_v4_4_1.py` | 30,718 | `ConfigV441`/`StructureV441`/`RangeSemanticProducerV441` — T-STALE mechanism |
| `ve_n1_replay/ve_n1_replay/range_engine_v4_4_1.py` | 10,036 | N1-composing engine wrapper (mirrors `range_engine_v4_4.py`) |
| `ve_n1_replay/tests/test_v4_4_1_stale.py` | 30,706 | STALE-1..15 + 2 supplementary protection tests (18 total) |
| `ve_n1_replay/VE_RANGE_V4_4_1_STALE_IMPLEMENTATION_REPORT.md` | — | This document |

**Changed:** none. `range_semantic_v4_4.py`, `range_engine_v4_4.py`, and `range_semantic_v4_3.py` are byte-identical
to HEAD (`9116c2b`) — see item 3.

---

## 3 — V4.4 byte-preservation proof

```
$ git diff --stat HEAD -- ve_n1_replay/ve_n1_replay/range_semantic_v4_4.py ve_n1_replay/ve_n1_replay/range_engine_v4_4.py ve_n1_replay/ve_n1_replay/range_semantic_v4_3.py
(no output, exit code 0)
$ git diff HEAD -- <same three files> | wc -l
0
```
Zero lines changed. `V4_4_BYTE_UNTOUCHED` holds (and transitively `V4_3_BYTE_UNTOUCHED`). Every V4.4/V4.3 symbol
reused by V4.4.1 (`ConfigV44`, `StructureV44`, `RangeSemanticProducerV44`, `RangeSemanticResultV44`,
`EPISODE_CONTINUATION`/`EPISODE_MERGED`/`EPISODE_REPLACEMENT`, `RANGE_WEAKENING`, `WEAKENING_RECOVERED`,
`WEAKENING_PERSISTENCE_TERMINATED`, `REASONS_V44`, `_as_v43_cfg`, `efficiency_ratio`, `relative_net_displacement`,
plus V4.3's `Depth`, `Structure`, `Registry`, `Excursion`, `ContractErrorV43`, `RangeEventV43`,
`SNAPSHOT_CONTRACT_MISMATCH`, `offer_swing`, `assign_level`, `degeneracy_check`,
`NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT`, `OK_RANGE_MACRO`, `SWING_OUTSIDE_CLUSTER`, `BETWEEN_EPISODES`,
`BREAKOUT_ACCEPTED`, `SWEEP_CONFIRMED`, `ZONES_DEGENERATE`, `ZONES_INVERTED`) is **imported**, never
copy-pasted-and-modified. V4.3-native constants (`NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT`, `OK_RANGE_MACRO`,
`ContractErrorV43`, `RangeEventV43`, `SNAPSHOT_CONTRACT_MISMATCH`) are imported directly from
`range_semantic_v4_3` (their point of definition) rather than through `range_semantic_v4_4`'s re-export, avoiding
a `--no-implicit-reexport` mypy error class already encountered and fixed the same way during the original V4.4
implementation.

Architecture, disclosed in full in the module docstring: unlike V4.4's own relationship to V4.3 (a fresh,
non-subclassing producer), V4.4.1 is a **true subclass** at all three levels (`ConfigV441(ConfigV44)`,
`StructureV441(StructureV44)`, `RangeSemanticProducerV441(RangeSemanticProducerV44)`) — verified safe on this
Python version (3.14.6) via standalone probes before committing to the shape (frozen-slotted-dataclass
inheritance, subclass-attribute-narrowing, and classmethod `super()`+`cast()` restore-chaining were each tested
in isolation first). ~23 methods on the producer are inherited completely unmodified; exactly 5 are overridden
(`__init__`, `_offer_swing_everywhere`, `_step_macro`, `snapshot_state`, `restore_state`), plus one new method
(`_t_stale_should_fire`). The `snapshot_state`/`restore_state` overrides were not originally scoped as
needing changes — found while re-reading the frozen V4.4 source line-by-line before writing any V4.4.1 code:
both reference `RANGE_HIERARCHICAL_V4_4_IMPLEMENTATION_FINGERPRINT` and construct
`RangeSemanticProducerV44`/`StructureV44` by literal name inside their own bodies (module-global references,
not `self.`-based), which Python's scoping rules mean would silently embed the wrong identity if inherited
unmodified. Recorded as a disclosed implementation finding, not a design-freeze gap — the freeze's own
snapshot/versioning plan (`e2b65bf` §13) already anticipated new identities were needed.

---

## 4 — Final parameter registry (exactly the 4 frozen values, no substitution)

Reproduced exactly from `9116c2b`, verified field-for-field against `ConfigV441`'s defaults:

| Field | Value | Status (from calibration) |
|---|---|---|
| `STALE_WINDOW` | 29 | `RATIFIED_REUSE` (= `W`; sensitivity honestly disclosed as untested — item 24) |
| `STALE_MIN_REJECTIONS` | 4 | `DERIVED` (= `min_alternation` + 1, the mathematical floor) |
| `STALE_MIN_ALTERNATION` | 3 | `CALIBRATED` / **`FRAGILE`** — escalated 1→2→3 during calibration; ±1 fails one side of the dual-sided acceptance bar each direction (item 17/24) |
| `STALE_MIN_AGE` | 12 | `DERIVED` (= `d_internal`) / `STABLE` |

`ConfigV441.validate()` enforces the floor relationship mechanically (`STALE_MIN_REJECTIONS >=
STALE_MIN_ALTERNATION + 1`), raising `ContractErrorV43` if violated — confirmed to fire automatically at
construction time via `ConfigV44.__post_init__` (discovered empirically during mutation testing, item 17).

---

## 5 — config_id

```
ConfigV441().config_id() == "d7b6c0670fbafe2583d49c0ed14046cc2ccb49a7068ffbb349a35962779a1f03"
```
Matches the illustrative preview computed during calibration (`9116c2b`) **exactly** — confirmed by direct
comparison against the real `ConfigV441` dataclass (not re-derived). `config_id()` is **inherited unchanged**
from `ConfigV44`: `self.__dataclass_fields__` on a `ConfigV441` instance dynamically includes all 31 fields
(27 inherited + 4 new), verified empirically before relying on it, so the existing formula covers the complete
V4.4.1 field set with zero override needed.
`RANGE_HIERARCHICAL_V4_4_1_NORMATIVE_CONFIG_ID` (module-level constant) matches this value exactly.

---

## 6 — Implementation fingerprint

```
RANGE_HIERARCHICAL_V4_4_1_IMPLEMENTATION_FINGERPRINT = "v4-4-1-implementation-freeze-2026-08-21"
```
Same convention as V4.4's own `"v4-4-implementation-freeze-2026-08-20"` — a human-readable, date-stamped label,
not a raw digest, consistent with the precedent in `range_semantic_v4_4.py`/`range_semantic_v4_3.py`. Set only
after all code was finalized and the full test suite (item 18) was green, per the standing
"never compute the fingerprint before the code exists" discipline.

Reference sha256 digests of the finalized source (recorded for independent re-verification, not stored as the
fingerprint value itself):

| File | sha256 |
|---|---|
| `range_semantic_v4_4_1.py` | `2065198da9632acf9a9d5e2f0e57e4f4d83cfaa60cc4a1b87e945e39a77e6017` |
| `range_engine_v4_4_1.py` | `30384a4bb3dbb1ee77932103b6ef4cc87641d906b9e2ab708b4a63d4a9134a0d` |

---

## 7 — Snapshot / contract / reason identities

| Identity | Value |
|---|---|
| `contract_version` | `"range-hierarchical-v4.4.1"` |
| `REASONS_V441` | `REASONS_V44 + (STALE_CANDIDATE_ABANDONED,)` = 41 total (40 unchanged + 1 new), uniqueness asserted at import time |
| New snapshot key (`StructureV441.snapshot()`) | `v441_rejected_touches` — bounded list, `[[bar_index, "H"\|"L"], ...]` |
| New snapshot keys (`RangeSemanticProducerV441.snapshot_state()`) | `contract_version`/`config_id`/`implementation_fingerprint` overwritten with V4.4.1-correct values on top of the inherited V4.4 payload |
| `restore_state` guard | Refuses fail-closed on any of the 3 identity keys mismatching (mutation-tested, item 17) |

---

## 8 — T-STALE transition mapping

Inserted in `_step_macro`, inside the existing `if zones is None:` branch (the same branch that already guards
T2/T3 formation-evaluation, structurally guaranteeing T-STALE only ever evaluates **never-confirmed** candidates
— item 12), immediately after T-KILL (`degeneracy_check`) and before falling through to
`_evaluate_macro_formation`:

```
kill = degeneracy_check(...)          # T-KILL — unchanged, highest priority
if kill in (ZONES_INVERTED, ZONES_DEGENERATE): ...

zones = st.zones(...) if st.reached_confirmed else None
if zones is None:
    if self._t_stale_should_fire(st, i):      # ← T-STALE, new, second priority
        self._kill_macro(st, i, STALE_CANDIDATE_ABANDONED, events)
        return STALE_CANDIDATE_ABANDONED
    return self._evaluate_macro_formation(st, i, events)   # T2/T3 — unchanged, falls through only if T-STALE doesn't fire
```

Termination reuses `_kill_macro` **completely unmodified** (already generic on `reason: str`) — a simplification
found while implementing: the design doc sketched a dedicated `_abandon_macro_stale` method, but `_kill_macro`'s
existing body (end_ts/end_reason, registry kill, history append, event emission, episode-identity bookkeeping,
slot release) already does everything needed with zero new termination-mechanics code.

---

## 9 — Rejected-evidence implementation

`StructureV441` adds exactly one new bounded field: `_rejected_touches: deque[tuple[int, str]]` (`maxlen=64`,
same convention/value as `StructureV44`'s own `_touch_tags`), kept structurally **separate** from `_touch_tags`
so as not to corrupt the existing `SUPPORTING_ONLY` alternation signal.

Populated in the `_offer_swing_everywhere` override — the **only** semantic change in that method versus V4.4:
captures `offer_swing`'s second return value (`reason_macro`, previously discarded) and records a rejection only
when `reason_macro == SWING_OUTSIDE_CLUSTER` — deliberately **not** for `ATR_UNAVAILABLE`, since that is a
transitory no-ATR-yet state, not genuine price-based staleness evidence (freeze `e2b65bf` §4).

`rejected_touches_in_window(as_of_bar, window)` recomputes the trailing subsequence on demand
(`b > as_of_bar - window`, strict), mirroring the calibration harness's own convention exactly — verified
against it directly (item 20 for the boundary-exactness proof).

---

## 10 — Alternation implementation

```python
flips = sum(1 for a, b in zip(in_window, in_window[1:]) if a != b)
return flips >= self._cfg.STALE_MIN_ALTERNATION
```
Pairwise adjacent-comparison flip-counting, identical in shape to `alternation_rate`'s own convention elsewhere
in the codebase and to the calibration harness's `t_stale_would_fire` function it was ported from. Reproduces
the calibration's own P1–P3/N1–N10 scenario battery (13/13) when run against the real `_t_stale_should_fire`
directly (smoke-tested before the formal suite was written).

---

## 11 — Anti-churn results

`STALE-4` (200-bar stress, one-sided rejections with a rare isolated flip every 50 bars — the N7/N8 shape from
calibration, extended and now against real code): **0 false fires across 200 bars**, checked at every bar from
age 12 through 200.

---

## 12 — Slow-range-protection results

`STALE-3` (N1-shape: zero rejections ever, candidate aged out to 300 bars): **never fires**, checked at every
bar. Structural protection independently confirmed by the dedicated
`test_stale_confirmed_structure_immune_even_with_qualifying_rejection_evidence` test: a **confirmed** structure
carrying rejection evidence that would independently satisfy `_t_stale_should_fire` in isolation is nonetheless
never killed through the real `_step_macro` orchestration, because the outer `zones is None` gate excludes it
structurally (T-STALE applies only to never-confirmed MACRO — mandate requirement, not merely a design
intention).

---

## 13 — Positive stale-release results

`STALE-1` (two-part reachability proof): (a) direct construction + `_step_macro` reproduces calibration's P1
scenario exactly, returns `STALE_CANDIDATE_ABANDONED`, event emitted, slot freed; (b) a **separate** targeted
test drives the real `_offer_swing_everywhere` with genuinely out-of-tolerance prices (not the
`record_rejected_touch_v441` shortcut used elsewhere for sequence control) and confirms the new rejection-
recording line fires on a real `SWING_OUTSIDE_CLUSTER` return.

`STALE-5` (no confirmation bypass): after abandonment, a freshly-formed replacement candidate fed the same
`INSUFFICIENT_EFFICIENCY` fixture already numerically verified in `test_v4_4_reason_code_reachability.py` is
correctly **rejected** at gate T3, not auto-confirmed — `reached_confirmed` stays `False`.

`STALE-2` (organic re-formation): after abandonment, real bars through the public `observe()` API produce a
**new**, independently-confirming candidate (`EPISODE_REPLACEMENT` → `RANGE_CANDIDATE_PRESENT` →
`OK_RANGE_MACRO`), proving the freed slot is fully functional, not just non-null.

---

## 14 — Next-bar replacement tests

`STALE-6`: immediately after the abandoning `_step_macro` call returns, in the *same* bar, `_active_macro`,
`_pending_up`, and `_pending_dn` are all confirmed `None` — nothing synchronously repopulates the slot inside
`_step_macro` itself. Formation of a new candidate exclusively requires `_offer_swing_everywhere`, which
`observe()` only calls on the **next** bar.

---

## 15 — Snapshot/restart tests

`STALE-7`: a dedicated deterministic construction (rejection evidence pre-loaded so T-STALE fires at *exactly*
bar 12, verified empirically before being written into the test) is split at bars 11, 12, and 13 — immediately
before, exactly at, and immediately after the firing bar — with a real `snapshot_state`/`restore_state` round
trip at each split point. All three match the continuous run bar-for-bar, including the abandonment event
itself.

`STALE-8`: prefix invariance (growing the container from 10→40 bars never rewrites earlier results) confirmed
on a fixture with rejection evidence actively accumulating in the background.

Producer-level identity refusal (`test_stale_restore_state_refuses_mismatched_identity_at_producer_level`):
wrong `contract_version`/`config_id`/`implementation_fingerprint` each independently refused fail-closed, with
no partial state mutation on the refusing producer — mirrors `test_v4_4_snapshot_robustness.py`'s own
methodology, raised to V4.4.1.

---

## 16 — Boundary tests for 29 / 4 / 12 / 3

| Test | Boundary | Result |
|---|---|---|
| `STALE-13` | window: rejection at exactly `as_of - 29` excluded (strict `>`), at `as_of - 28` included | confirmed both sides |
| `STALE-14` | age: 11 blocks, 12 fires | confirmed both sides |
| `STALE-15` | count: 3 rejections never satisfy (max 2 flips possible from 3 elements — structurally coupled to the alternation floor, not a test artifact), 4 rejections with 3 flips satisfy | confirmed both sides, coupling documented explicitly |

---

## 17 — Fragility mutation results (STALE-11/STALE-12) and the 8 named source mutations

**STALE-11/STALE-12** (`CONSTRUCTION_ONLY_ZERO_VALIDATION_WEIGHT`, disclosed, not repaired): `min_alternation=2`
fires on the N8 shallow-channel-with-one-pullback fixture that the frozen registry (`=3`) correctly rejects;
`min_alternation=4` misses a genuine 3-flip positive case that the frozen registry correctly accepts. Both
confirmed against real code, both directions of the fragility kept explicit per mandate §17 rather than tuned
away.

**8 named source-code mutations** (mandate §23) — each applied directly to the frozen file, full suite run, then
restored byte-exact (sha256-verified after every restore) before the next mutation:

| # | Mutation | Result |
|---|---|---|
| 1 | Remove alternation requirement | 3 tests fail (STALE-4, STALE-11, STALE-12) |
| 2 | `min_alternation` default → 2 | 3 tests fail (STALE-4, STALE-11, STALE-15) |
| 3 | `min_alternation` default → 4 | **Collection error** — `ConfigV441()` raises `ContractErrorV43` at import time via the validate()-enforced floor (`4 < 4+1`), caught automatically by `ConfigV44.__post_init__` |
| 4 | Reduce `min_rejections` default → 3 | **Collection error** — same floor mechanism (`3 < 3+1`) |
| 5 | Remove age gate | 2 tests fail (STALE-7, STALE-14) |
| 6 | Allow same-bar replacement (pre-seed pending state at the abandonment bar) | 2 tests fail (STALE-2, STALE-6) |
| 7 | Allow T-STALE on confirmed structure (move check outside the `zones is None` gate) | 2 tests fail (STALE-9, dedicated confirmed-immunity test) |
| 8 | Disable snapshot identity gate | 1 test fails (dedicated `restore_state` identity test) |

All 8 caused a meaningful failure (an assertion failure or, for #3/#4, an even earlier and stronger
construction-time `ContractErrorV43`). Source file hash after every single restore matched the pre-mutation
baseline (`0dec7c9...b27c2e0`) exactly. Two genuine test-suite gaps were found and closed *during* this
exercise, before running mutations #7 and #8 (a confirmed-structure-immunity test and a producer-level
`restore_state` identity-refusal test) — both now part of the permanent suite (item 2).

---

## 18 — Full regression results

```
470 pre-existing baseline tests (V4.3/V4.4/N1/incremental/etc, unchanged, unweakened, unskipped)
+ 18 new V4.4.1 tests (15 named STALE-1..15 + 1 extra STALE-1 sub-test + 2 supplementary protection tests)
= 488 passed, 0 failed, 0 skipped
```
Confirmed both before and after the mutation-testing/rollback exercises (which necessarily perturbed the
source/file layout temporarily) — 488/488 green in the final state.

---

## 19 — mypy --strict results

`range_semantic_v4_4_1.py` + `range_engine_v4_4_1.py`: **`Success: no issues found in 2 source files`**.

`test_v4_4_1_stale.py` (with `MYPYPATH=tests`, matching how the existing `test_v4_4_*.py` files resolve their
sibling `test_range_semantic_v4_3` import): **`Success: no issues found in 1 source file`** — cleaner than the
existing precedent file `test_v4_4_transitions.py`, which under the identical invocation still carries 3
pre-existing, out-of-scope errors (2 reexport, 1 comparison-overlap) that predate this mandate and were not
touched.

Whole-package `mypy --strict ve_n1_replay/`: 23 pre-existing errors, all in unrelated vendored `_ai`/`_det`
import trees with unresolvable cross-package imports — confirmed **zero** of these 23 mention
`range_semantic_v4_4_1`/`range_engine_v4_4_1` (`grep -c` check).

---

## 20 — Complexity / memory results

- `_rejected_touches` deque strictly bounded at `maxlen=64` regardless of rejection count fed (verified with
  5,000 rejections fed → length stays 64).
- Snapshot payload (`v441_rejected_touches`) bounded identically (64 entries max) — does not grow indefinitely
  over a long replay.
- `rejected_touches_in_window`: 100,000 calls in 0.234s (≈2.34 µs/call) — a bounded linear scan over a
  constant-size (≤64) structure, not proportional to total replay length.
- 20,000-bar stress test (rejections fed continuously): first-half vs second-half wall-clock ratio = **1.02x**
  — flat, no evidence of any hidden O(n²) accumulation path.

---

## 21 — Rollback proof

All 3 new files moved aside; full suite re-run: **470/470 pass** (the exact pre-existing baseline count),
confirming nothing else in the repository silently depends on V4.4.1's presence. `mypy --strict` on the 3 core
V4.3/V4.4 files: clean. Files restored; sha256 verified byte-identical to the pre-removal state; full suite
re-run: **488/488 pass** again.

---

## 22 — FB14 / MB3 preservation proof

No FB14 bars/labels, and no MB3-001..048 (any range) data, were read, imported, referenced, or scored anywhere
in `range_semantic_v4_4_1.py`, `range_engine_v4_4_1.py`, or `test_v4_4_1_stale.py`. All 18 new tests are
construction-only, built from hand-specified synthetic fixtures (direct `StructureV441` construction,
`legs_bars`-style synthetic oscillators) — the same fixture discipline already established throughout
`test_v4_4_*.py`. No fresh blind execution was performed, per `NO_FRESH_BLIND`.

---

## 23 — Implementation-freeze proof

`RANGE_HIERARCHICAL_V4_4_1_IMPLEMENTATION_FINGERPRINT` set to its final value (item 6) only after items 1–22
above were all complete and green — no semantic change to either implementation file after that point. This
report, the implementation files, and the test file are committed together in a single commit; local=remote
hash equality is verified across all 4 mirrors (alpha1/discovery/lab/trader) as the concluding step of this
delivery, per `FREEZE_BEFORE_RED_TEAM`.

---

## 24 — Remaining known risks (carried forward, not resolved by this mandate)

- **`min_alternation=3` fragility** (`TRACK_MIN_ALTERNATION_FRAGILITY`): deliberately not tuned away — see
  item 17. Neighboring values each fail one side of calibration's dual-sided acceptance bar.
- **Window-length (`STALE_WINDOW=29`) sensitivity**: reused from `W` by ratification, not independently
  swept during calibration — disclosed as an untested gap in `9116c2b`, carried forward unresolved here too
  (boundary-exactness at 29 is tested — item 16 — but that is a different claim from *29 being the right
  value*).
- **MB3-025→048**: still completely untouched throughout this entire V4.4.1 line of work, as in every prior
  phase.
- **No semantic/fresh-blind validation performed or claimed** — this mandate is implementation-only; the
  verdict below makes no claim about real-market generalization, matching `V4_4_1_FRESH_BLIND14_...`-style
  validation being explicitly out of scope here.
- Snapshot/restore correctness for V4.4.1 has been proven only on the scenarios in this suite (organic
  oscillators, direct-construction never-confirmed/confirmed candidates); it has not been exercised against a
  long, organically-diverse multi-thousand-bar replay the way V4.4's own causality suite does at 96/288/480
  bars — a reasonable next-phase addition, not a defect found here.

---

## Verdict

**`V4_4_1_IMPLEMENTATION_READY_FOR_RED_TEAM_AUDIT`**

No semantic validation is claimed. Next owner: Red Team, mandate `RT-RANGE-V4_4_1-IMPLEMENTATION-AUDIT-001`.
No promotion (Strategy Catalog / Alpha / AI Trader / LIVE_SHADOW / broker / live trading) is authorized by this
mandate or this report.
