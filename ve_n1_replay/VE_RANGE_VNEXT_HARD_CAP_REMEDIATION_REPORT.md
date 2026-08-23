# VE_RANGE_VNEXT_HARD_CAP_REMEDIATION_REPORT

> **STATUS UPDATE (2026-08-23): this remediation has since been independently revalidated and CEO-ratified.**
> See [`RANGE_VNEXT_RESEARCH_RATIFICATION_AND_HANDOFF.md`](RANGE_VNEXT_RESEARCH_RATIFICATION_AND_HANDOFF.md)
> for the full chain (Statistician `90b572e` → Red Team `986cba8` → `RANGE_LIFECYCLE_VNEXT_RESEARCH_RATIFIED`)
> and current consumption guidance. This report is preserved unmodified below as the original record of the
> remediation itself.

**Mandate**: `VE-RANGE-VNEXT-HARD-CAP-REMEDIATION-001`
**Repo**: `ai_quant_lab-wp5b`, branch `discovery-mk-matrix-v1`
**Source audit**: Statistician independent validation, commit `54fa51f` — verdict
`RANGE_LIFECYCLE_VNEXT_INDEPENDENT_VALIDATION_FAIL` / `RANGE_LIFECYCLE_VNEXT_UNBOUNDED_STATE_BLOCKER`
**Old (candidate under remediation) commit**: `bba6310`
**New commit**: this file's own delivery commit — a commit cannot contain its own hash; see `git log` on
`discovery-mk-matrix-v1`, the delivery Telegram notification, or memory topic
`ve-range-vnext-multi-candidate` for the recorded value.

> **VERDICT: `RANGE_LIFECYCLE_VNEXT_HARD_CAP_REMEDIATED` / `RANGE_LIFECYCLE_VNEXT_READY_FOR_INDEPENDENT_REVALIDATION`**
> — see section 14 for the full gate-by-gate evidence. NOT `RATIFIED`/`PRODUCTION_READY`/`NEW_BRAIN_READY`;
> independent revalidation comes next.

## 1. The blocker, confirmed by direct code inspection before any fix was written

Statistician reproduced: `max_active_macro_candidates=3`, active candidates reached 34, zero
`REGISTRY_CAPACITY_REFUSED` events. Read directly at `range_semantic_vnext.py` (delivered commit
`bba6310`, line 442):

```python
action, target_id = self._episode_identity_for_new_macro_multi((cand_lo, cand_hi), i)
if action == "REPLACEMENT" and len(self._active_macros) >= self._cfg.max_active_macro_candidates:
    events.append(RangeEventV43(kind=REGISTRY_CAPACITY_REFUSED, ...))
    self._clear_pending()
    return
```

The capacity check gated ONLY `action == "REPLACEMENT"`. `_episode_identity_for_new_macro_multi` can
return three actions — `MERGE`, `CONTINUATION`, `REPLACEMENT` — and the single common insertion point
(`self._active_macros[new_id] = st_macro`, confirmed via `grep` to be the *only* assignment into that
dict) is reached unconditionally by all three. Of the three:

- **MERGE** is net-zero: `_supersede_macro(target_id, ...)` removes the target from `_active_macros`
  *before* the new entry is inserted, so registry size is unchanged.
- **CONTINUATION** and **REPLACEMENT** (the `else` branch) are both net **+1**: their predecessor is
  already absent from `_active_macros` (terminated earlier, tracked only as a scalar
  `_last_terminated_macro_id`/`_last_terminated_macro_zone`), so nothing is removed when the new candidate
  is added.

Gating the check on `action == "REPLACEMENT"` therefore left CONTINUATION completely unchecked — every
CONTINUATION-eligible swing pair was admitted regardless of registry size, exactly matching the
Statistician's reproduction (repeated CONTINUATION growing the registry to 34 candidates against a cap of
3).

## 2. Fix

Minimal, single-condition change, no other line touched:

```python
frees_a_slot = action == "MERGE" and target_id is not None and target_id in self._active_macros
if not frees_a_slot and len(self._active_macros) >= self._cfg.max_active_macro_candidates:
    ...
```

Deliberately expressed as "does this action free a slot" rather than as an enumeration of action names
that must be capacity-checked (mandate's own preference: "prefer enforcing the invariant at the narrowest
common registry insertion boundary"). A future fourth action type is capacity-checked **by default**
unless it demonstrably frees a slot the same way MERGE does — the invariant does not depend on anyone
remembering to add a new action string to an allow-list. The check still runs *before* any mutating side
effect (`_registry.new_id()`, `offer_swing`, `_supersede_macro`), so a refusal:

- consumes no registry id (matches the pre-existing REPLACEMENT-refusal precedent),
- discards no swing data (a later bar can still succeed once room exists — architecture's existing
  refused-candidate philosophy, unchanged),
- and, critically, **never partially executes a MERGE** — if `frees_a_slot` were computed *after*
  `_supersede_macro` ran, a refusal could strand the operation having already evicted the merge target
  with no replacement inserted (a real regression the mandate explicitly forbids: "do not silently evict
  another candidate"). Checking `target_id in self._active_macros` *before* superseding avoids this.

**Exact diff** (`ve_n1_replay/ve_n1_replay/range_semantic_vnext.py`):

```diff
@@ -439,7 +439,16 @@ class RangeSemanticProducerVNext:

         # not contained by any active macro's own INTERNAL slot -- try forming a NEW MACRO candidate
         action, target_id = self._episode_identity_for_new_macro_multi((cand_lo, cand_hi), i)
-        if action == "REPLACEMENT" and len(self._active_macros) >= self._cfg.max_active_macro_candidates:
+        # Structural cap invariant (remediation VE-RANGE-VNEXT-HARD-CAP-REMEDIATION-001): the check must
+        # cover every action that nets a NEW entry into `_active_macros`, not just REPLACEMENT. MERGE is
+        # the only action that frees a slot in the SAME operation (`_supersede_macro` below removes
+        # `target_id`), so it alone is exempt -- checked here, structurally, rather than by enumerating
+        # action names, so a future action type is capacity-checked by default unless it demonstrably
+        # frees a slot the same way. CONTINUATION and REPLACEMENT both add a net-new entry with nothing
+        # removed (their predecessor is already absent from `_active_macros`, having terminated earlier),
+        # so both must be refused at capacity exactly like REPLACEMENT always was.
+        frees_a_slot = action == "MERGE" and target_id is not None and target_id in self._active_macros
+        if not frees_a_slot and len(self._active_macros) >= self._cfg.max_active_macro_candidates:
             events.append(RangeEventV43(kind=REGISTRY_CAPACITY_REFUSED, bar_index=i, structure_id=None,
                                         depth=Depth.MACRO.name, reason_codes=(REGISTRY_CAPACITY_REFUSED,),
                                         not_yet_available=()))
```

**No other file, semantic, threshold, or config value was touched.** `tol_cluster`, `d_macro`,
`IOU_CONTINUE`, formation/merge/supersession/abandonment/canonical-arbitration/confirmation semantics, and
RANGE boundary logic are byte-identical to `bba6310`. `range_semantic_v4_3.py` and `range_semantic_v4_4.py`
remain untouched (confirmed: `git diff --stat` empty on both, same as every prior RANGE mandate in this
lineage).

## 3. Internal-depth registry — confirmed structurally safe, no analogous fix needed

`_active_internals` has exactly one insertion point (`self._active_internals[mid] = st_internal`), and
`mid` is always drawn from `sorted(self._active_macros)` — an internal can only be keyed by an id that is
already a key in `_active_macros`. `len(_active_internals) <= len(_active_macros) <= cap` holds by
construction; no second cap or second fix is needed at INTERNAL depth.

## 4. Mandatory regression test (mandate section 5)

`test_vnext11_mandatory_continuation_at_capacity_is_refused_not_admitted` — cap=3, three spatially distinct
macros seeded to fill the registry, a CONTINUATION-eligible swing pair constructed via direct scalar setup
of `_last_terminated_macro_zone`/`_end_ts`/`_id`/`_end_reason` (the same established direct-construction
convention `seeded_macro` itself already uses) satisfying the real
`_episode_identity_for_new_macro_multi`'s own CONTINUATION precedence (IoU ≥ `IOU_CONTINUE` against the
terminated zone, within `GAP_MAX` bars, non-breakout end reason), exercised through the REAL
`_offer_swing_everywhere` registry-mutating path — not the isolated identity function alone. Asserts:
active count stays exactly 3, `REGISTRY_CAPACITY_REFUSED` is emitted, no `EPISODE_CONTINUATION` event
occurs, no unrelated candidate (1/2/3) disappears, and a repeated identical attempt changes nothing.

**Empirically verified to catch the exact original bug**: the fix condition was temporarily reverted to
`action != "REPLACEMENT"` (a faithful reproduction of the original gate — CONTINUATION and MERGE both
bypass, only REPLACEMENT is checked) and the suite re-run. Exactly the three tests that exercise
CONTINUATION-at-capacity failed (`test_vnext11`, `test_vnext11d`, `test_vnext11e`); the four that don't
(REPLACEMENT regression guard, MERGE success, snapshot/restore) still passed. The real fix was then
restored and the full suite re-verified green. This is not asserted from reasoning alone — it was run.

## 5. Adversarial cap tests (mandate section 6)

All in `tests/test_vnext_liveness.py`, section `VNEXT-11`:

| Case | Test | Result |
|---|---|---|
| REPLACEMENT at capacity | `test_vnext11b` (explicit regression guard alongside the pre-existing `test_vnext4`) | refused, registry unchanged |
| CONTINUATION at capacity | `test_vnext11` (mandatory test) | refused, registry unchanged |
| MERGE at capacity | `test_vnext11c` | **succeeds** — net-zero, registry stays at cap, target properly superseded (not left dangling) |
| Repeated CONTINUATION attempts | `test_vnext11d` (3 separate attempts, separate bars) | all refused identically |
| Mixed REPLACEMENT / CONTINUATION / MERGE sequence | `test_vnext11e` | `len <= cap` asserted after **every** operation, not just at the end; a real termination correctly re-opens a slot for a subsequent REPLACEMENT |
| Snapshot → restore at capacity | `test_vnext11f` | restored registry has the exact same 3 ids and boundaries |
| Post-restore capacity enforcement | `test_vnext11g` | a restored producer refuses an over-cap admission exactly like a freshly-constructed one |

`len(active_candidates) <= cap` was asserted after every single operation in `test_vnext11e`, not only at
the end, per the mandate's own explicit requirement.

## 6. Full-history equivalence (mandate section 7)

Full canonical-history (2011-07-26 warmup, 355,696 M15 bars) dual-engine (v4.4 vs vNext) replay re-run
post-fix. Every figure is **byte-for-byte identical** to the pre-fix reference:

| Metric | Pre-fix reference | Post-fix (this remediation) |
|---|---|---|
| Births | 12,813 | 12,813 |
| Merges / supersessions | 361 / 361 | 361 / 361 |
| Abandonments | 4,108 | 4,108 |
| Genuine confirmations | 4,092 | 4,092 |
| Capacity refusals | 0 | 0 |
| Historical max active | 4 | 4 |
| Registry size (min/median/p95/p99/max) | 0/1/2/2/4 | 0/1/2/2/4 |
| Bars with 0 active | 28,075 (7.89%) | 28,075 (7.89%) |
| Bars with >1 active | 73,229 (20.59%) | 73,229 (20.59%) |
| Longest continuous zero-active | 45 bars (0.47d) | 45 bars (0.47d) |
| Episode comparison (preserved/changed/lost/new) | 93/48/46/4,116 | 93/48/46/4,116 |
| vNext confirmed bars, all 16 years (2011-2026) | (see research report §7) | identical, digit-for-digit, in every single year |
| v4.4 confirmed bars, all years | (unchanged, untouched engine) | identical |

**Zero divergence of any kind.** This confirms the mandate's own explicit prediction: because the
production default `max_active_macro_candidates=16` was never approached historically (measured max
concurrent = 4), the newly-covered CONTINUATION-at-capacity code path never actually fired during this
replay in either version — `capacity_refused=0` both before and after — so the fix had no opportunity to
change behavior on this exact dataset. The fix only changes behavior when the registry is already at/near
cap, a condition this 15-year history never reached; §4-5's adversarial unit tests are what demonstrate
the fix's actual effect, since the full-history replay structurally cannot exercise it at the production
cap.

## 7. Age gate (mandate section 8)

Verified by direct logical consequence of section 6's demonstrated identical outputs, not by re-running
the expensive unbounded per-structure history extraction a second time (disclosed methodology, not
silently assumed): `capacity_refused=0` in **both** the pre-fix and post-fix full-history runs means the
fix never once altered an admission decision on this dataset — every structure that was created,
offered swings, and reached confirmation follows an *identical* code path in both versions (the only
changed code is the admission gate's condition, which structurally cannot have fired differently when its
own refusal counter is 0 in both runs). Since `confirmations_any=4,092` in both runs too, the SET of
confirmed structures and each one's own `start_ts` (hence its own age at confirmation) is provably
unchanged. The pre-fix measurement (research report §9.4) already found 4,090/4,092 (99.95%) confirm at or
above the frozen `d_macro=29` gate, with the 2 exceptions being a 1-bar fencepost artifact of logic
byte-identical to v4.4's own — that finding is unchanged by this remediation. Capacity enforcement did not
create an age-gate bypass: the two code paths (registry admission, age gate) are structurally independent
(different methods, `_offer_swing_everywhere` vs. `_evaluate_macro_formation`), and the admission gate's
own behavior is confirmed identical to before.

## 8. Restart determinism (mandate section 9)

The four pre-existing `VNEXT-6` determinism/restart tests (continuous vs. snapshot→restore, cross-version
fail-closed refusal, registry round-trip) were re-run after the fix: **4/4 still pass, unchanged**. Two
NEW tests specifically exercise restart **at capacity** (section 5 table above, rows 6-7):
`test_vnext11f`/`test_vnext11g` — snapshot/restore preserves the exact at-cap registry, and a restored
producer still refuses a subsequent over-cap admission. Zero divergence in all cases tested.

The mandate's broader "continuous replay vs. snapshot→restore→resume" comparison is deliberately verified
via direct-construction unit tests rather than a full 355,696-bar-scale split-run, for a concrete reason:
section 6 shows the real 15-year history never approaches the production cap (max concurrent observed =
4, against a cap of 16) — there is no natural point in that replay where the registry is genuinely "at
capacity," so a full-history-scale restart test could not exercise the AT-CAPACITY scenario the mandate is
specifically concerned with even if run. Direct construction (`test_vnext11f`/`g`, cap=3 with exactly 3
seeded candidates) is the only way to genuinely test this condition, and is what was used. General
(not-at-capacity) full-history restart equivalence is unaffected by this remediation's own change (the fix
touches only the registry-admission condition, not `snapshot_state`/`restore_state` themselves, both
byte-unchanged) and was already established for this architecture by the prior mandate's own `VNEXT-6`
suite, re-confirmed passing here.

## 9. Implementation identity (mandate section 10)

`RANGE_HIERARCHICAL_VNEXT_IMPLEMENTATION_FINGERPRINT` changed from `"vnext-implementation-freeze-2026-08-22"`
to `"vnext-implementation-hardcap-remediation-2026-08-22"`. A snapshot taken under the old implementation
is fail-closed refused by the new one (`SNAPSHOT_CONTRACT_MISMATCH`, unchanged mechanism, exercised by the
pre-existing `test_vnext6c`-style cross-version guard). Descriptive label, not a content digest — this
project's own established convention (v4.3/v4.4 fingerprint precedent, already independently audited and
accepted): code identity is verified via git-blob SHA + `config_id()`, not the fingerprint string itself.
`config_id()` itself is unchanged (no `ConfigVNext` field was added, removed, or given a different default
value by this remediation — `max_active_macro_candidates` stays 16, set by the prior mandate).

## 10. Snapshot-growth finding (mandate section 11) — recorded unchanged, not redesigned

Statistician's independent validation confirmed the inherited `_dead`/`_awaiting_role` lifetime-state
growth (already disclosed in the prior mandate's own research report, section 12 / section 14 item 7) and
classified it **`REMEDIATION_REQUIRED_BEFORE_PRODUCTION`**. Recorded here verbatim, unchanged. Per this
mandate's own explicit instruction, that subsystem is **not** touched, redesigned, or otherwise addressed
by this remediation — it remains a separate, disclosed, future production-hardening item, tracked in the
research report's disclosed-limitations list (item 7, updated to cite this exact classification).

## 11. Negative-control matcher (mandate section 12) — documentation only

Added research report §9.6: the reported true premature-kill rate depends on unregistered matching
parameters (e.g. the 50-bar coarse start-time-proximity threshold used to select which 46 episodes warrant
refined investigation), with plausible values in a 2.14%–6.42% range depending on configuration — while
remaining, under every parameterization Statistician tested, an order of magnitude below v4.5's own rates.
No matching parameter, threshold, or RANGE lifecycle semantic was changed in response to this finding, per
the mandate's own explicit instruction that this is a measurement/documentation issue, not grounds for
retuning.

## 12. Reporting corrections (mandate section 13) — documentation only, no data changed

Both were derivation errors in already-correct per-year data, confirmed by direct recomputation:

| | Originally reported | Corrected |
|---|---|---|
| 2016–2024 confirmed-bar total | 55,713 | **62,713** (sum of the nine unchanged per-year values) |
| 2016–2024 range | 6,429–7,704 | **6,429–7,660** (7,704 is 2014's own value, outside this window and correct on its own row; 7,660 is 2018's, the true in-window max) |

Fixed in `VE_RANGE_LIFECYCLE_VNEXT_RESEARCH_REPORT.md` (§7, §14) and
`RANGE_VNEXT_LIFECYCLE_DIAGNOSTICS.json` (`pathological_period_2016_2024`), with an explicit correction
note left in place at both locations rather than silently overwritten. The underlying
`vnext_canonical_confirmed_bars_by_year` per-year figures were always correct and are unchanged.

## 13. Test suite (mandate section 14)

New: **7 tests** (`VNEXT-11` section, `tests/test_vnext_liveness.py`), all attributable to this
remediation, all passing, one (the mandatory test, section 4 above) empirically verified to fail against
the original bug before the fix and pass after. `mypy --strict`: clean on both touched implementation
files (`range_semantic_vnext.py`, `range_engine_vnext.py`); the test file shows only the pre-existing,
expected `sys.path`-based import-not-found note shared by every RANGE test file in this project (not
introduced by this remediation).

Full repository suite (`pytest tests/`): **554 passed, 0 failed** (547 pre-remediation + 7 new, section 4-5
above). 100% green in VE's own test environment — the environmental mypy failure Statistician's own run
showed (546/547) did not reproduce here. Investigated rather than ignored: the only mypy-in-pytest
integration test in this suite is `test_mypy_strict_clean_on_all_touched_files`
(`tests/test_range_semantic_v4_3.py`), which subprocess-invokes `mypy --strict` on exactly
`range_semantic_v4_3.py`/`range_engine_v4_3.py` — neither touched by this remediation, and it passed in
this run. A repo-wide `mypy --strict ve_n1_replay/` (not part of any pytest test, run separately as a
direct check) does show 23 pre-existing `import-not-found` errors, all in the vendored `_ai`/`_det`
subtree (e.g. `ai_trader.n1_replay.engine`, `market_state`, `order_block_void`) — bare cross-module
imports that resolve only at runtime via this project's own bootstrap, not under static mypy analysis run
directly against the file tree. This is a pre-existing characteristic of the vendored subtree, not
introduced by this remediation (which touches none of those files), and is the most plausible source of
what Statistician's own environment reported as a test failure (likely a difference in mypy/Python version
or invocation between the two environments) — disclosed here rather than either silently dismissed or
falsely claimed fixed, since this remediation did not touch, and was not asked to touch, that subtree.
**Zero test failures are attributable to this remediation.**

## 14. Verdict (mandate section 16)

Per the mandate's own explicit gate, checked independently, none waived because another looks good:

| Requirement | Status | Evidence |
|---|---|---|
| Hard cap structurally enforced | **PASS** | §2 (fix), §4 (mandatory test, empirically proven to catch the exact original bug), §5 (7 adversarial cases: REPLACEMENT/CONTINUATION/MERGE at capacity, repeated attempts, mixed sequence with per-operation invariant checks, snapshot/restore at capacity, post-restore enforcement) |
| Canonical historical behavior unchanged | **PASS** | §6: every figure byte-for-byte identical to the pre-fix reference — births, merges, abandonments, confirmations, capacity refusals, registry distribution, all 16 years of per-year confirmed bars, episode comparison |
| Restart determinism passes | **PASS** | §8: pre-existing `VNEXT-6` suite (4/4) unchanged; new at-capacity restart cases (`test_vnext11f`/`g`) pass; full-history-scale restart is not meaningfully constructible at capacity for this dataset (§8 explains why), and general restart equivalence is unaffected since `snapshot_state`/`restore_state` themselves are byte-unchanged |
| Age gate remains intact | **PASS** | §7: provable by direct consequence of §6's identical `capacity_refused`/`confirmations_any` counts — the set of confirmed structures and their own ages is unchanged, so the pre-fix 99.95% (4,090/4,092) age-gate compliance finding is unchanged |

**All four conditions are satisfied. Verdict: `RANGE_LIFECYCLE_VNEXT_HARD_CAP_REMEDIATED` /
`RANGE_LIFECYCLE_VNEXT_READY_FOR_INDEPENDENT_REVALIDATION`.**

Per the mandate's own explicit prohibition, this is **not** `RATIFIED`, not `PRODUCTION_READY`, and not
`NEW_BRAIN_READY` — independent revalidation (Statistician and/or Red Team) is the required next step.
v4.4 (`3bb61cf`) remains the sole deployed baseline until that revalidation completes.

## 15. Known remaining limitations (carried forward, unchanged by this remediation)

All limitations disclosed in `VE_RANGE_LIFECYCLE_VNEXT_RESEARCH_REPORT.md` §14 remain as stated there,
updated only where this remediation's own findings bear directly (items 7, 8, 9 in that document, added or
amended by this mandate). This remediation fixes exactly one structural defect (registry-capacity
enforcement) and corrects two reporting errors; it does not resolve, and was explicitly instructed not to
attempt to resolve, the `_dead`/`_awaiting_role` growth finding, the matcher parameter sensitivity, or any
RANGE semantic question. v4.4 (`3bb61cf`) remains the sole deployed baseline pending independent
revalidation of this remediation.
