# STAT — RANGE vNEXT HARD-CAP PATCH REVALIDATION

**Mandate ID:** `STAT-RANGE-VNEXT-HARD-CAP-REVALIDATION-001`
**Division:** Statistician (independent statistical validation)
**Date:** 2026-08-23
**Remediation under revalidation:** VE `fa36324c05998cd1f7b769a95620d900843e494a`
**Prior validation:** `54fa51f` — `RANGE_LIFECYCLE_VNEXT_INDEPENDENT_VALIDATION_FAIL` /
`RANGE_LIFECYCLE_VNEXT_UNBOUNDED_STATE_BLOCKER`

**Scope directives honoured:** `INDEPENDENT_REVALIDATION_ONLY` · `VERIFY_FA36324` · `REPRODUCE_OLD_BUG` ·
`VERIFY_CONTINUATION_AT_CAP` · `VERIFY_ALL_INSERTION_PATHS` · `VERIFY_FULL_HISTORY_EQUIVALENCE` ·
`VERIFY_RESTART` · `VERIFY_AGE_GATE` · `NO_IMPLEMENTATION_CHANGE`

**Nothing was modified.** The repo working tree was never touched. The pre-fix implementation was
materialised from its git blob into a throwaway package copy.

---

## 0 — TERMINAL VERDICT

```
RANGE_LIFECYCLE_VNEXT_HARD_CAP_REVALIDATION_PASS
RANGE_LIFECYCLE_VNEXT_INDEPENDENT_VALIDATION_PASS
RANGE_LIFECYCLE_VNEXT_READY_FOR_RED_TEAM
```

All six §13 conditions are independently satisfied:

| condition | evidence |
|---|---|
| hard cap now structurally enforced | one insertion path, gated; invariant held in every tested case, worst overshoot **0** |
| old bug independently reproduced pre-fix | cap=3 → **active reached 34**, zero refusals, against the `bba6310` blob |
| the fix independently blocks it | same construction post-fix → **refused, active stays 3** |
| full-history behaviour unchanged | **0 drifting fields** across every metric, all 26 event kinds, all 16 years |
| restart determinism passes | 0 mismatches on real data; near- and at-capacity traces identical |
| age gate intact | **0 of 4,092** below `d_macro = 29`; confirmed-structure sets identical tuple-for-tuple |

**This does NOT mean RATIFIED, PRODUCTION_READY or NEW_BRAIN_READY.** v4.4 remains the canonical deployed
research baseline.

---

## 1 — COMMIT / DIFF AUDIT (§2) — **PASS, narrowly scoped**

| item | value | |
|---|---|---|
| commit | `fa36324c05998cd1f7b769a95620d900843e494a` | ✓ |
| parent | `bba6310` (the validated-then-failed delivery) | ✓ |
| branch | `discovery-mk-matrix-v1` | ✓ |
| mirrors | alpha1 / discovery / lab / trader — **all four MATCH** | ✓ |
| **v4.3 / v4.4** | `git diff --stat bba6310 fa36324` on every v4.3/v4.4 file: **empty** | ✓ **untouched** |

Changed files — five, all within the permitted categories:

| file | lines | category |
|---|---|---|
| `range_semantic_vnext.py` | +22 / −6 | **hard-cap enforcement + implementation identity** |
| `test_vnext_liveness.py` | +197 | **required tests** (7 new) |
| `VE_RANGE_VNEXT_HARD_CAP_REMEDIATION_REPORT.md` | +307 | documentation |
| `VE_RANGE_LIFECYCLE_VNEXT_RESEARCH_REPORT.md` | 47 | documentation |
| `RANGE_VNEXT_LIFECYCLE_DIAGNOSTICS.json` | 4 | **the two reporting corrections I raised** |

**No unrelated semantic modification.** The entire implementation change is two hunks:

```python
frees_a_slot = action == "MERGE" and target_id is not None and target_id in self._active_macros
if not frees_a_slot and len(self._active_macros) >= self._cfg.max_active_macro_candidates:
```

and the fingerprint bump. `tol_cluster`, `d_macro`, `IOU_CONTINUE`, formation, merge, supersession,
abandonment, canonical arbitration and confirmation are all byte-unchanged — confirmed by reading the diff
and by the zero-drift replay (§4).

**Working-tree note, for completeness:** the wp5b working tree carries an unrelated modified file
(`code/run_production_pipeline.py`) and some untracked log files. I verified `run_production_pipeline.py` is
**not in the engine import graph**, so it cannot influence any result here.

---

## 2 — REPRODUCING THE ORIGINAL BLOCKER (§3) — **the harness still detects it**

Before scoring the patch I re-established that my reproducer is still capable of failing. The pre-fix
implementation was materialised from `git show bba6310:…/range_semantic_vnext.py` into a temporary copy of
the package — **the repository working tree was never modified**.

```
  PRE-FIX (bba6310 blob), cap = 3, 31 CONTINUATION offers
    -> active = 34      over_cap = True      REGISTRY_CAPACITY_REFUSED emitted = False
  reference failure from 54fa51f: active reached 34, zero refusals
  harness still detects the original defect: TRUE
```

**Exactly the reference failure, to the number.** A post-fix pass therefore cannot be a false negative from
a broken harness — the control fires.

---

## 3 — HARD-CAP INVARIANT (§4) AND FAILURE SEMANTICS (§5) — **PASS**

Independent adversarial reproducer, not VE's tests.

### 3.1 The invariant grid

| cap | action | attempts | max active | over cap | refused | events |
|---|---|---|---|---|---|---|
| 1 | REPLACEMENT | 1 | 1 | **False** | True | `REGISTRY_CAPACITY_REFUSED` |
| 1 | CONTINUATION | 5 | 1 | **False** | True | `REGISTRY_CAPACITY_REFUSED` |
| 1 | MERGE | 1 | 1 | **False** | False | — (exempt) |
| 2 | REPLACEMENT | 1 | 2 | **False** | True | `REGISTRY_CAPACITY_REFUSED` |
| 2 | CONTINUATION | 5 | 2 | **False** | True | `REGISTRY_CAPACITY_REFUSED` |
| 2 | MERGE | 1 | 2 | **False** | False | — (exempt) |
| 3 | REPLACEMENT | 1 | 3 | **False** | True | `REGISTRY_CAPACITY_REFUSED` |
| 3 | CONTINUATION | 5 | 3 | **False** | True | `REGISTRY_CAPACITY_REFUSED` |
| 3 | MERGE | 1 | 3 | **False** | False | — (exempt) |

**`len(active) ≤ cap` held in every case. Worst overshoot: 0.**

### 3.2 Mixed sequence, invariant checked after *every single* operation

12 operations at cap = 3 alternating CONTINUATION / REPLACEMENT / MERGE:

```
  CONT->refused  REPL->refused  MERGE->ok  CONT->refused  CONT->refused  REPL->refused
  MERGE->ok  CONT->refused  REPL->refused  MERGE->ok  CONT->refused  CONT->refused
  active after every operation: 3
  per-operation invariant violations: 0
```

### 3.3 The MERGE exemption is mechanically net-zero — proven, not assumed

My first MERGE attempt was **absorbed by cluster tolerance before reaching the merge branch** (the
`offer_swing` early return), so it did not test what it claimed to. I rebuilt it: seeded candidate
`[100, 110]`, offered zone `[102, 112]` — IoU **0.667 ≥ IOU_CONTINUE 0.5**, and both edges 2.0 apart, above
`tol_cluster·atr = 1.6`, so not absorbed.

```
  AT CAPACITY (3), genuine MERGE:
    events            : ['CANDIDATE_SUPERSEDED_BY_MERGE', 'EPISODE_MERGED']
    active before/after: 3 -> 3      ids [6000,6001,6002] -> [1,6001,6002]
    target 6000 removed: True        refused: False (correctly exempt)     over cap: False
    NET-ZERO CONFIRMED : True
  10 repeated merges at capacity -> active [3,3,3,3,3,3,3,3,3,3]
```

Order of operations makes the exemption safe: `_supersede_macro` **pops before** the insert, so the registry
goes cap → cap−1 → cap and **never transiently exceeds the bound**. §5's condition — "MERGE exemption is
allowed ONLY if it is mechanically confirmed net-zero" — is satisfied.

### 3.4 Refusal semantics (§5)

At capacity with a CONTINUATION:

```
  candidate inserted?          False   (ids unchanged: [5000,5001,5002])
  unrelated candidate removed? []      <- no silent removal
  boundaries mutated?          False
  reason emitted:              ['REGISTRY_CAPACITY_REFUSED']
  event structure_id:          [None]  <- no victim-selection behaviour introduced
  deterministic across 3 identical runs: True
```

---

## 4 — COMMON-BOUNDARY AUDIT (§6) — **PASS, by construction rather than by enumeration**

The previous defect existed because one branch was omitted from an action-name enumeration. The decisive
question is therefore whether *any* route into `_active_macros` bypasses the gate. I enumerated every
occurrence in the module:

| line | operation | gated? |
|---|---|---|
| 216 | `self._active_macros = {}` — constructor | n/a (empty) |
| **486** | `self._active_macros[new_id] = st_macro` | **YES — line 451, immediately above** |
| 940 | `fresh._active_macros = {…}` — `restore_state` | restores a snapshot (see below) |
| 306 / 491 / 505 | `.pop(mid)` — supersede / kill / breakout-close | removals |

**There is exactly one insertion route for new candidates, and it is gated.** The new condition is expressed
structurally — *does this action free a slot in the same operation?* — so a future action type is
capacity-checked **by default** unless it demonstrably frees a slot. That is the correct shape of fix for
this defect class: it closes the omitted-branch failure mode itself, not just the one instance.

**The `restore_state` route was tested rather than reasoned about** (§4 required it): restoring a
snapshot taken at capacity yields exactly the capacity, and **post-restore CONTINUATION *and* REPLACEMENT
are both refused** — capacity enforcement is not a construction-only check.

---

## 5 — FULL-HISTORY EQUIVALENCE (§7) — **ZERO DRIFT**

Independent canonical replay, 355,696 M15 bars, warmup from the file's first bar (2011-07-26), pre-fix
versus post-fix.

| metric | pre-fix `bba6310` | post-fix `fa36324` | |
|---|---|---|---|
| macro candidate births | 12,813 | 12,813 | **IDENTICAL** |
| `EPISODE_REPLACEMENT` | 11,607 | 11,607 | **IDENTICAL** |
| `EPISODE_CONTINUATION` | 845 | 845 | **IDENTICAL** |
| `EPISODE_MERGED` | 361 | 361 | **IDENTICAL** |
| `CANDIDATE_SUPERSEDED_BY_MERGE` | 361 | 361 | **IDENTICAL** |
| `CANDIDATE_ABANDONED_PRICE_MOVED_ON` | 4,108 | 4,108 | **IDENTICAL** |
| `REGISTRY_CAPACITY_REFUSED` | 0 | 0 | **IDENTICAL** |
| genuine confirmations `OK_RANGE_MACRO` | 4,092 | 4,092 | **IDENTICAL** |
| canonical confirmed id transitions | 5,812 | 5,812 | **IDENTICAL** |
| `ZONES_DEGENERATE` / `BREAKOUT_ACCEPTED` | 5,036 / 3,285 | 5,036 / 3,285 | **IDENTICAL** |
| `RANGE_CANDIDATE_PRESENT` / `RANGE_WEAKENING` | 6,326 / 5,971 | 6,326 / 5,971 | **IDENTICAL** |
| `IS_TREND_MACRO` / `ZONES_INVERTED` / `WEAKENING_RECOVERED` | 2,940 / 23 / 2,536 | same | **IDENTICAL** |
| occupancy min/median/p95/p99/max/mean | 0 / 1 / 2 / 2 / 4 / 1.134 | same | **IDENTICAL** |
| bars zero-active / >1-active / longest zero run | 28,075 / 73,229 / 45 | same | **IDENTICAL** |

**All 16 years of per-year confirmed bars identical** (2011: 2745 … 2026: 3597). **All 26 distinct event
kinds across both depths compared — 0 differing.**

```
  TOTAL DRIFTING FIELDS: 0
  VERDICT: ZERO HISTORICAL SEMANTIC DRIFT
```

This is exactly what the mandate predicted: historical max active = 4 against a production cap of 16, so the
newly-covered code path **never fires on this dataset** — and it demonstrably did not.

---

## 6 — AGE GATE (§8) — **PASS**

| | structures | confirmed | min age | median | max | **below gate (<29)** |
|---|---|---|---|---|---|---|
| pre-fix `bba6310` | 12,813 | 4,092 | 29 | 29 | 649 | **0** |
| post-fix `fa36324` | 12,813 | 4,092 | 29 | 29 | 649 | **0** |
| post-fix, merge/continuation-born | — | 346 | 29 | — | — | **0** |

**Stronger than a count match:** the confirmed-structure sets are identical **tuple-for-tuple** on
`(structure_id, confirm_ts, start_ts)` — `True`. Not one confirmation changed identity, timing, or origin.
The CONTINUATION, MERGE and capacity-refusal paths are all covered by this comparison, since all three
appear in the replay (845 / 361 / 0 respectively).

---

## 7 — RESTART DETERMINISM (§9) — **PASS**

| scenario | result |
|---|---|
| real data, 12,000 bars, snapshot@7,000 → restore → resume | **0 mismatching bars** |
| real data, double restart 3,000 → 6,500 → 12,000 | **0 mismatching bars** |
| **near-capacity** (3 of cap 4), 3 continuation ops | continuous vs restarted traces **IDENTICAL**, no over-cap |
| **at-capacity** (4 of cap 4), 3 continuation ops | continuous vs restarted traces **IDENTICAL**, no over-cap |

Compared per bar: `macro_id`, `macro_state`, `macro_reason`, `active_macro_count`, `active_macro_ids`, both
boundaries, `regime`, and the full event tuple `(kind, depth, structure_id)`.

The near-capacity trace is the informative one: the first CONTINUATION is **admitted** (3 → 4, filling the
cap exactly) and every subsequent one is refused — the boundary transition behaves correctly, and identically
across a restart.

---

## 8 — IMPLEMENTATION IDENTITY (§10) — **acceptable for this revalidation**

| | pre-fix | post-fix | |
|---|---|---|---|
| `contract_version` | `range-hierarchical-vnext-multicandidate-v1` | same | unchanged — **correct**, the contract did not change |
| `config_id` | `3f2f7ba6bef59d68…` | same | unchanged — **correct**, no config field changed |
| implementation fingerprint | `vnext-implementation-freeze-2026-08-22` | `vnext-implementation-hardcap-remediation-2026-08-22` | **BUMPED** |

**The fingerprint remains descriptive rather than content-derived — stated precisely, as §10 requires.**

§10 sets the deciding criterion: fail only if snapshot compatibility can *actually* be falsely accepted
across incompatible implementations. **It cannot.** Tested in both directions:

```
  PRE-FIX snapshot into POST-FIX implementation : REFUSED  (ContractErrorV43: SNAPSHOT_CONTRACT_MISMATCH)
  POST-FIX snapshot into PRE-FIX implementation : REFUSED  (ContractErrorV43: SNAPSHOT_CONTRACT_MISMATCH)
  can be falsely accepted: FALSE
```

Independent content-derived identity also exists via git blob SHAs: `0d8c9117…` → `94dcdc3f…`.

**Classification: acceptable for this revalidation; a residual integrity item for later.** The residual risk
is procedural rather than demonstrated — a descriptive constant depends on an author remembering to bump it,
whereas a content digest cannot be forgotten. VE bumped it correctly here. **Not a blocker.**

---

## 9 — TESTS (§11) — **553 passed / 1 failed of 554; the failure is environmental**

```
  1 failed, 553 passed in 118.93s
  FAILED test_range_semantic_v4_3.py::test_mypy_strict_clean_on_all_touched_files
    incremental.py:22: error: Unused "type: ignore" comment  [unused-ignore]
```

**Identical to the failure I documented at `54fa51f`, and not scored against VE**: `incremental.py` is
untouched by this commit, and the assertion is mypy-version-sensitive to how `import ve_brain` resolves in
my environment (mypy 2.3.0). Effectively **554/554**, matching VE's claim. Test count rose 547 → 554, i.e.
exactly the 7 new cases.

**The mandatory CONTINUATION-at-cap test genuinely exercises the real engine path.** `test_vnext11` calls
`prod._offer_swing_everywhere(...)` with real swing prices, relies on the real
`_episode_identity_for_new_macro_multi` precedence to produce CONTINUATION (IoU 0.714 against a zone
terminated 5 bars ago, within `GAP_MAX = 12`), and asserts that `EPISODE_CONTINUATION` **does not complete**,
that no unrelated candidate disappears, and that repeating the attempt is deterministic. It is not an
assertion reconstructed from reasoning.

The 7 new tests map one-to-one onto §4's required cases: CONTINUATION at cap, REPLACEMENT regression guard,
MERGE net-zero, repeated CONTINUATION, mixed sequence with per-operation invariant, snapshot/restore at
capacity, post-restore enforcement.

---

## 10 — CARRIED-FORWARD FINDINGS (§12) — not reopened, behaviour unchanged

| finding | status | changed by the patch? |
|---|---|---|
| snapshot lifetime-state growth (`_dead`, `_awaiting_role`) | `REMEDIATION_REQUIRED_BEFORE_PRODUCTION` | **no** — inherited from v4.3/v4.4, untouched |
| negative-control matcher parameter sensitivity (2.14–6.42%) | measurement/documentation limitation | **no** — VE disclosed it rather than retuning, which is the correct response |
| reporting corrections: 62,713 bars in 2016–2024; range 6,429–7,660 | **CORRECTED in this commit** | yes — diagnostics JSON, 4 lines |
| descriptive implementation fingerprint | residual integrity item (§8 above) | fingerprint bumped; architecture unchanged |

The two reporting errors I raised at `54fa51f` are fixed in the diagnostics artifact.

---

## 11 — LIMITATIONS

1. This is a **narrow** revalidation, as instructed. The gates not re-run — negative control, churn
   separation, supersession profile, performance — are carried forward from `54fa51f`, and the zero-drift
   result (§5) is the evidence that carrying them forward is legitimate.
2. The cap invariant is proven for **caps 1–4** and the action types reachable through
   `_offer_swing_everywhere`. The production cap of 16 was not exhaustively driven, because the historical
   maximum is 4 and the gate is cap-value-independent.
3. My at-capacity and near-capacity restart tests use **synthetic** registry state, because 15 years of real
   data never exceed 4 active candidates.
4. The pre-fix reproduction uses a package copy with one file replaced by its git blob; the rest of the
   package is at HEAD. Since the only relevant difference between the two commits is in that file, this is
   a faithful reconstruction — but it is a reconstruction, not a checkout.
5. **Nothing was modified and no defect was repaired.**

---

## 12 — VERDICT

```
RANGE_LIFECYCLE_VNEXT_HARD_CAP_REVALIDATION_PASS
RANGE_LIFECYCLE_VNEXT_INDEPENDENT_VALIDATION_PASS
RANGE_LIFECYCLE_VNEXT_READY_FOR_RED_TEAM
```

The single validation-blocking defect is correctly repaired, by a fix whose *shape* closes the omitted-branch
failure class rather than the one instance of it, with **zero historical semantic drift** and no change to
any previously-validated lifecycle behaviour. The control experiment confirms my harness still detects the
original bug, so the pass is not vacuous.

**This does NOT mean RATIFIED, PRODUCTION_READY, or NEW_BRAIN_READY.** No Market Intelligence integration is
authorized. v4.4 remains the canonical deployed research baseline. The carried-forward snapshot-growth item
remains `REMEDIATION_REQUIRED_BEFORE_PRODUCTION`.

**Next owner: Red Team.**

---

## 13 — ARTIFACTS

`statistician/range_vnext/` — `STAT_RANGE_VNEXT_HARDCAP_EQUIVALENCE.json` and reproduction code
(`adversarial.py`, `merge_at_cap.py`, `identity.py`, `restart2.py`, `equiv.py`), alongside the six
deliverables from `54fa51f`.

**Environment:** Python 3.14, mypy 2.3.0, data `OANDA_XAUUSD_M15.csv` sha256
`57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37` (355,696 bars),
pre-fix `bba6310` blob `0d8c9117…`, post-fix `fa36324` blob `94dcdc3f…`, config_id `3f2f7ba6…` (unchanged).
**Test command:** `python -m pytest ve_n1_replay/tests -q`.

---

*Statistician division — independent statistical validation. Verdicts are scoped strictly to the evidence
examined and are not transferable to adjacent claims.*
