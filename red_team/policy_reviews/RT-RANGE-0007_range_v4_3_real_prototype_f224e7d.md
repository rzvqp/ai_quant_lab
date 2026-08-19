# RED TEAM — RANGE V4.3 REAL-PROTOTYPE AUDIT
### RT-RANGE-0007 · **A: `RANGE_V4_3_PROTOTYPE_IMPLEMENTATION_PASS`** · **B: `RANGE_V4_3_CONSTRUCTION_RESULT_NOT_REPRODUCED`**
**Date:** 2026-08-19 · **Auditor:** Red Team · **Target:** VE's real RANGE Hierarchical V4.3 prototype, frozen commit `f224e7d` (initial prototype `119a0cc`; delivery report `RANGE_V4_3_REAL_PROTOTYPE_DELIVERY_REPORT.md`). Authorized by RT-RANGE-0006 `2c113ef` (`RANGE_V4_IMPLEMENTATION_PACKAGE_STATIC_PASS`, E81) on Statistician package `d6e599e`.

**Static + dynamic Git-only audit. Prototype not modified, defects not repaired, no wheel produced, no blind corpus run, no SEALED/OOS access, no PnL. Nothing changed outside `red_team/`.**

---

# VERDICTS (two, separate)

## A — Implementation: **`RANGE_V4_3_PROTOTYPE_IMPLEMENTATION_PASS`**
The prototype faithfully implements `range-hierarchical-v4.3` through a real bar-by-bar loop. Config identity is byte-exact (`config_id 24f72a60…`); the confirmation conjunction, hierarchy, sweep/breakout/promotion, and reason codes run through `RangeSemanticProducerV43.observe()`; the C13 reversal bug (below) was found and correctly fixed so `LIQUIDITY_SWEEP_REVERSAL` is now emittable via `observe()`; prefix-invariance/zero-lookahead holds; snapshot/restore is fail-closed and atomic; mypy `--strict` is clean on both modules; 369/370 real tests pass. No semantic, causal, structural, snapshot, or identity deviation found. Minor hardening nits (listed) do not affect contract fidelity.

## B — Construction result: **`RANGE_V4_3_CONSTRUCTION_RESULT_NOT_REPRODUCED`**
The detector produces **non-empty** structures and events (the real improvement over V3's zero — I confirmed independently by running the frozen detector on labels-derived bars), and the denominators are correct (88 MACRO / 12 INTERNAL / 26 UNRESOLVED-separate). **But VE's numbers cannot be independently reproduced from the frozen commit:** the synthesis (`synth.py`) and run (`run_construction.py`) scripts and `construction_run_results.json` are **not committed** (VE §9 states so), so the metrics depend on uncommitted local files (§1 forbids this), and the corpus is **circular** — synthesized from the same labels it is scored against (VE calls it "circulară"), so recall/precision/IoU are a self-consistency sanity check, not a detection-accuracy measure. Non-empty ≠ reproduced.

## PRE_RUN_FREEZE_PROTOCOL = **FAIL**
The mandate's freeze order is code → fingerprint → commit+push → declare `PROTOTYPE_PRE_RUN_FROZEN` → then run. VE §9 openly states the opposite order: *"rularea corpusului s-a făcut DUPĂ fix, ÎNAINTE de commit"* — the run preceded the commit, and `PROTOTYPE_PRE_RUN_FROZEN` was declared **at** `f224e7d`, the commit that already contains the results. The pre-registration discipline was not followed. VE did **not** hide it (disclosed in §8/§9). Per the mandate, `f224e7d` is nonetheless the pre-declared frozen target for my reproduction; this procedural finding stands separately and is not erased by the reproduction.

**Neither verdict is `SEMANTIC_PASS` or `BLIND_PASS`.** IMPLEMENTATION_PASS authorizes **only** `NEW_INDEPENDENT_BLIND_VALIDATION_PREPARATION` — Red Team running the frozen detector on the **real sealed** bars (the separate blind mandate), which is where real accuracy is measured. It does not authorize a wheel, Strategy Catalog, Alpha, AI-Trader, LIVE_SHADOW, broker, trades, or the 6-hour regression.

---

## PASS/FAIL matrix

| § | Check | Result |
|---|-------|--------|
| 1 | Sources + local=remote + frozen target | **PASS** |
| 3 | Identity (contract_version + config_id) | **PASS** |
| 4 | Pre-run freeze protocol | **FAIL** (procedural, disclosed) |
| 5 | CEO configuration in real code | **PASS** |
| 6 | Contract → code → runtime (real loop) | **PASS** |
| 7 | Reversal-watch bug fix | **PASS** |
| 8 | HBL-20 causal timing | **PASS** (late-actionability caveat) |
| 9 | Real hierarchy | **PASS** |
| 10 | Boundaries + lookahead | **PASS** |
| 11 | Sweep / breakout / promotion | **PASS** |
| 12 | Reason-code real reachability | **PASS** |
| 13 | Snapshot / restore fail-closed | **PASS** (2 hardening nits) |
| 14 | VE's tests (370) + mypy | **PASS** (369 real + mypy clean; 1 test-portability artifact) |
| 15 | Construction denominators | **PASS** |
| 16 | Independent metric reproduction | **NOT REPRODUCIBLE** (synth/run uncommitted; circular) |

## §1 — Sources · PASS
Branch HEAD **is** `f224e7d` (branch `discovery-mk-matrix-v1`); **local = remote OK on all 4 mirrors**. `f224e7d` (2026-08-19 20:54:09) = rigor pass over `119a0cc` (20:00:39). `range_semantic_v4_3.py` = **1143 lines** (created `119a0cc`, +64 at `f224e7d`), `range_engine_v4_3.py` = 217 lines. 0.4.1 and prior generations byte-untouched (V4.3 is additive, source-only, no wheel). Frozen target = `f224e7d`; later changes not audited.

## §3 — Identity · PASS
`contract_version = "range-hierarchical-v4.3"` (module + config); `ConfigV43.config_id()` = `24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da` — byte-identical to normative. The engine refuses construction if `config_id() != NORMATIVE_CONFIG_ID` (build-time guard). Changing any parameter (e.g. `w_atr`) changes `config_id`. Snapshot/restore is fail-closed on `contract_version` **and** `config_id` **and** N1 identity fingerprint. **VE's claim that `schema_version`/`snapshot_version`/`config_version`/`reason_code_set_version` do not exist as separate literals is TRUE** (verified in the harness, package, and manifest); VE correctly did not invent them. Within the frozen artifact, `contract_version + config_id` fully protect config, contract, and reason-code set; the internal snapshot *schema* has no separate version (a disclosed limitation — see the reversal_watch nit in §13), but no two incompatible states within `f224e7d` can share an identity and corrupt: missing/wrong-type fields are caught and refused.

## §4 — Pre-run freeze · FAIL (procedural, disclosed)
See the verdict block. `119a0cc` committed code **and** initial results together ("results ready for CEO review", 0 reversals pre-fix); VE then fixed the reversal bug, **re-ran** the corpus (21 reversals), and committed `f224e7d` with the results, declaring the freeze at that commit. The run therefore preceded the freeze declaration. Disclosed by VE, not hidden.

## §5 — CEO configuration · PASS
In the real `ConfigV43`: `d_macro=29, d_internal=12, n_touch=2, K_reentry=22, N_accept=3, K_struct=2, n_external_swings=2, atr_window=14, w_atr=0.80`; `tol_cluster=s_max=1.60` and `w_atr_sanity_ceiling=1.3952` are **computed properties** (never stored); canonical ATR pinned (`atr_source=…vendor_bridge.atr14`). No value hidden in a bare literal; degeneracy is KILL (inclusive `<=` at equality); legacy/incomplete configs refused (`ConfigNotRatifiedErrorV43`).

## §6 — Contract → code → runtime · PASS
`observe(ts_close, open_, high, low, close, atr, …)` is the real loop: detect confirmed swings → offer to clusters → `push_close` → `_step_depth(MACRO)` → `_step_depth(INTERNAL)` → `_check_reversal_watch(MACRO)` → `_check_reversal_watch(INTERNAL)` → build result. Every contract clause maps to a production symbol reached through this loop (matrix in the report body): `evaluate_candidate_with_n_touch`, `assign_level` (R1/R2/R3 + C14 depth), `Excursion`, `promotion_check`, `_maybe_promote`, `Structure.assign_role`, `snapshot_state`/`restore_state`. No function is orphaned from the loop after the C13 fix.

## §7 — Reversal-watch bug fix · PASS
**The bug VE found is real:** `sweep_reversal_confirmed` (C13) was a faithfully-ported, directly-tested pure function that **was never called from the per-bar loop**, so `LIQUIDITY_SWEEP_REVERSAL` was unreachable via `observe()`. The fix — a `_macro/_internal_reversal_watch` opened at `SWEEP_CONFIRMED` (with the opposite-side reference swing and `ref_confirm_ts`, the active excursion slot cleared), checked each bar in `_check_reversal_watch` (calling the unchanged pure function), `episode_end_ts` resolved **dynamically**, persisted in snapshot — is correct. **I independently confirmed reachability through `observe()` only** (my own driver, not VE's test): `LIQUIDITY_SWEEP_REVERSAL` is emitted bar-by-bar; it is created only after a confirmed sweep, tied to the correct structure, requires the opposite-swing break (not every sweep becomes a reversal), and no lookahead (`sweep_reversal_confirmed` raises `FUTURE_TIMESTAMP_REFUSED` if the reference formed after the excursion opened).

## §8 — HBL-20 causal timing · PASS (with a caveat)
Bar-by-bar on VE's HBL-20 fixture: **`SWEEP_CONFIRMED` @ bar 49** (the reentry), **`LIQUIDITY_SWEEP_REVERSAL` @ bar 75**, `BREAKOUT_ACCEPTED` @ 77. These are **distinct sequential events**: the sweep confirms at reentry; the reversal confirms only when a close first breaks the **opposite** swing (close 135 > upper ~120 at bar 75). Bar 75 is the **earliest causal bar** for the reversal — it is **contract-required, not an implementation delay**. The mandate's apparent contradiction (sweep ~56 vs reversal 75) conflates two different events; `SWEEP_CONFIRMED` ≠ `LIQUIDITY_SWEEP_REVERSAL`. **Caveat:** the reversal fires late (~15 pts into the opposite move, adjacent to the breakout), so as an entry signal it is largely post-move — an actionability limitation inherent to the contract's reversal definition, faithfully implemented, not a code defect.

## §9 — Real hierarchy · PASS
`Depth` enum has exactly two members (MACRO=0, INTERNAL=1) → MICRO is unrepresentable. `assign_level` gives INTERNAL a valid MACRO parent, never kills MACRO; a third level → `DEPTH_LIMIT_EXCEEDED`; a rejected candidate returns no ID; level shift creates a new episode linked by `predecessor_id`; `macro_history` retains closed episodes; no ID recycled. VE's e2e tests (`test_e2e_macro_with_channel_up/down_internal`, `_with_subrange_internal`) and harness `1c/2b` (INTERNAL doesn't kill MACRO) pass; the delivery report cites 8 windows with simultaneous MACRO+INTERNAL. (My HBL-20 fixture didn't exercise nesting — fixture-specific, not a defect.)

## §10 — Boundaries + lookahead · PASS
**Prefix-invariance holds** (my independent test): the output for bar *t* is identical whether or not bars after *t* are supplied. Swings confirm at `j+K_struct`; clusters upper/lower separate; center = median; `atr_ref` fixed causally; boundaries frozen at confirmation; degeneracy KILL.

## §11 — Sweep / breakout / promotion · PASS
Through `observe()`: `N_accept=3` consecutive outside closes → breakout; reentry resets the counter; `K_reentry=22`; `NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT`; `SWEEP_CONFIRMED`; `LIQUIDITY_SWEEP_REVERSAL`; closed episode retained; `K_struct=2` fractal radius; `n_external_swings=2`; promotion via the 4-precondition conjunction (slope alone cannot promote). Exact boundary cases pass in the 369-test suite.

## §12 — Reason-code real reachability · PASS
The set is closed at 29 (`REASONS_V43`, asserted). VE's `test_all_29_reason_codes_reachable_via_public_api` + AST test pass; the module reuses the same emitting functions I already drove to emit all 29 in RT-RANGE-0006 (0 missing/0 extra), now wired into `observe()` (the C13 fix closed the last real gap). `DEPTH_LIMIT_EXCEEDED`, `LIQUIDITY_SWEEP_REVERSAL`, `TOO_SHORT_MACRO/INTERNAL` all reachable.

## §13 — Snapshot / restore · PASS (2 hardening nits)
Restore is **atomic and fail-closed**: wrong type, `contract_version`/`config_id`/N1-identity mismatch → `RangeSnapshotErrorV43`; a fresh producer is restored and only swapped on success (a failed restore leaves the engine unchanged — verified). Missing core fields (`n`, `wh`, `macro_history`) and wrong-type structural values are refused. **Two nits:** (1) a list-typed field corrupted to a **string** (`wh="CORRUPT"`) is accepted, because `deque(str)` iterates chars rather than raising — a narrow type-validation gap that would fail on first numeric use; (2) missing `macro_reversal_watch` is `.get`-defaulted to `None` (the field added at `f224e7d`), so a `119a0cc`-schema snapshot restores as a valid-but-watch-less state. Neither corrupts normal operation nor breaks identity within the frozen artifact.

## §14 — Tests + mypy · PASS (1 portability artifact)
**369/370 tests pass.** The single "failure", `test_mypy_strict_clean_on_all_touched_files`, invokes `subprocess.run(["python","-m","mypy",…])` against the **base** interpreter (which lacks mypy in an isolated venv) instead of `sys.executable` — a test-portability blemish, not a type error: my direct `mypy --strict` on both V4.3 modules returns **Success, 0 issues**. The 79 harness tests reconcile as **39 adversarial + 27 groups + 13 non-vacuity = 79** (I re-ran them: 79/0). Determinism, chunk-invariance, two-instance isolation, zero-lookahead all pass.

## §15 — Construction denominators · PASS
`BLIND_BATCH_02_LEVEL_MAPPING`: 88 MACRO + 26 UNRESOLVED = 114 level-1 + 12 INTERNAL (level-2, separate) = 126 rows. **MACRO recall base = 88** (VE 57/88 = 0.648 ✓); **INTERNAL recall base = 12** (VE 2/12 = 0.167 ✓); the 26 UNRESOLVED are reported separately and **never scored**; the 12 INTERNAL are not double-counted. The corrected window lengths (addendum: **BLIND-046=288, BLIND-047=96, BLIND-048=480**) are the ones used (13 824 = 16×(96+288+480)); no old/contradictory JSON detected in the committed labels.

## §16 — Independent reproduction · NOT REPRODUCIBLE
I reran the **committed detector** (`f224e7d`) on labels-derived synthetic bars: it **confirms MACRO ranges and emits `BREAKOUT_ACCEPTED`/sweeps** — non-empty, unlike V3's zero. **But VE's specific figures are structurally non-reproducible from the frozen commit**, because the label→bar synthesis (`synth.py`) and `run_construction.py` are **not committed** and the prose methodology (leg lengths, amplitudes, bridges) does not fully determine the bars; different synthesis yields different structures/matches. VE's declared numbers (MACRO recall 0.648 / precision 0.445 / IoU median 0.770; 57/88 matched; SWEEP 209 / BREAKOUT 112 / REVERSAL 21 / promotion 94; funnel 725→151 MACRO/16 INTERNAL/558 partial-overlap) therefore **cannot be independently confirmed**, and — being computed on a corpus synthesized from the very labels they are scored against — are a self-consistency sanity check, not a detection-accuracy measure. **VE vs Red Team:** VE declared the above; Red Team confirms only *non-emptiness and correct denominators*, and cannot reproduce the point figures (synth uncommitted).

## §18 — Interpretation (CEO language)
On documented shapes the detector **does now see ranges** (V4.3 fixed V3's "zero segments confirmed"): it forms and confirms MACRO ranges, marks sweeps and breakouts, and — after the C13 fix — emits liquidity-sweep reversals. It confirms a MACRO range no faster than the contract's `d_macro=29` gate allows (median confirm delay = 29). It keeps the big MACRO range alive while internal structures appear (INTERNAL never kills MACRO). **Weaknesses:** it detects internal structure poorly (VE's own figure: 2 of 12, recall 0.167); the liquidity-sweep-reversal fires **late** (after the opposite move is largely consumed); and — decisively — **none of these numbers can be independently reproduced** because the run/synth harness is uncommitted and the corpus is circular. **This does not justify skipping blind validation.** The only meaningful accuracy measure remains the separate Red Team blind mandate on the real sealed bars.

## CONSOLIDATED DEFECT / FINDING LIST
1. **PRE_RUN_FREEZE_PROTOCOL = FAIL** — corpus run preceded the freeze declaration; the freeze commit contains the results (VE disclosed). *Fix:* commit + freeze the code before any official run.
2. **Construction results not reproducible** — `synth.py`/`run_construction.py`/`construction_run_results.json` uncommitted; results depend on local files (§1). *Fix:* commit the deterministic run harness so the figures derive from committed artifacts alone.
3. **Corpus circularity** — bars synthesized from the labels they are scored against; recall/precision/IoU are construction-only sanity, not accuracy. (VE transparent; inherent to construction-only.)
4. **Late reversal actionability** — `LIQUIDITY_SWEEP_REVERSAL` fires only on the opposite-swing break, near the breakout (bar 75 vs sweep 49); largely post-move as an entry signal. (Contract-inherent, faithfully implemented.)
5. **Snapshot type-validation nits** — a string-corrupted list field is accepted (`deque(str)` quirk); missing `macro_reversal_watch` is `.get`-defaulted. *Fix:* validate field types; bump a snapshot-schema version when the state shape changes.
6. **mypy in-suite test not portable** — hardcoded `"python"` subprocess instead of `sys.executable`; fails where the base interpreter lacks mypy. (Actual mypy `--strict` is clean.)
7. **Weak INTERNAL detection** — 2/12 (recall 0.167); a construction-result observation, not an implementation defect.

## What I re-verified independently vs. did not run
- **Independently this session:** §1 commits/local=remote/frozen target; §3 config identity + `config_id`; §5 config; §6/§7 real-loop wiring + reversal reachability via `observe()` only; §8 HBL-20 bar-by-bar trace; §10 prefix-invariance; §13 snapshot fail-closed/atomic/corruption; §14 mypy `--strict` (clean) + full 369/370 run + 79-harness reconciliation; §15 denominators from committed labels; §16 detector-non-emptiness on labels-derived bars.
- **NOT reproducible / not run:** VE's exact construction figures (synth/run uncommitted); real-bar blind validation (separate mandate); no wheel, no PnL, no SEALED/OOS.

## Disposition
**A: IMPLEMENTATION_PASS. B: CONSTRUCTION_RESULT_NOT_REPRODUCED. PRE_RUN_FREEZE_PROTOCOL: FAIL.** The faithful implementation authorizes **only** `NEW_INDEPENDENT_BLIND_VALIDATION_PREPARATION` (Red Team running the frozen `f224e7d` detector on real sealed bars), on the conditions that VE commit the deterministic run/synth harness (finding 2) and that the construction figures carry **no** validation weight (findings 2–3). No `SEMANTIC_PASS`, no `BLIND_PASS`. Not authorized: wheel, Strategy Catalog, Alpha, AI-Trader integration, LIVE_SHADOW cutover, broker, trades, 6-hour regression. Red Team modified no VE/Statistician code and changed nothing outside `red_team/`.
