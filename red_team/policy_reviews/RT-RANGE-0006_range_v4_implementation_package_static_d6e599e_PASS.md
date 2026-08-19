# RED TEAM — RANGE V4 IMPLEMENTATION PACKAGE STATIC REVIEW
### RT-RANGE-0006 · **RANGE_V4_IMPLEMENTATION_PACKAGE_STATIC_PASS**
**Date:** 2026-08-19 · **Auditor:** Red Team · **Target:** Statistician's `range-hierarchical-v4.3` implementation package. Consolidated package commit `d6e599e`; manifest v2.7.94 `14d4c22`; fingerprint `a5d69e2d0150d7ca2cf750df49f65cfc55b91fa89d13568fa42f81a48f4ee565`. Prior contract V4.2 `5a9d5ec`; parameter sheet `4684e66`; construction config `b8cf2a7`.

**Static, Git-only review + independent run of the contractual harness. No detector implemented, no VE engine modified, no blind corpus run, no wheel/Strategy-Catalog/Alpha/AI-Trader/LIVE_SHADOW/broker authorized. `SEALED/OOS_ACCESS = 0`. Nothing changed outside `red_team/`.**

---

# VERDICT — **RANGE_V4_IMPLEMENTATION_PACKAGE_STATIC_PASS**

**The package is complete and unambiguous enough for VE to build the prototype without inventing any rule, formula, priority, constant, or boundary behavior.** Every mandatory field has a numeric definition, an input, an availability moment, a formula, an output, a reason code, and a positive+negative test; the confirmation conjunction is a single function with a fixed normative priority order; the 29-code set is closed; and the executable oracle is mypy-clean and passes 79/79. The three real contract defects VE would otherwise have had to invent around — `LIQUIDITY_SWEEP_REVERSAL` had no defined window (C13), `DEPTH_LIMIT_EXCEEDED` was declared but unemittable (C14), and the confirmation conjunction existed only as prose (C15) — are all closed and independently confirmed reachable.

**This PASS authorizes ONLY the separate VE-prototype mandate.** It does not authorize a wheel, the Strategy Catalog, Alpha, AI-Trader integration, LIVE_SHADOW cutover, the broker, or trades, and it does not validate that the detector recognizes ranges.

**Three non-blocking blemishes** (consolidated at the end) should be corrected by the Statistician but are **not implementable gaps**: a stale "V4_2" review-status string / harness filename against the normative `contract_version="range-hierarchical-v4.3"`; a doc count of "12" non-vacuity gates where the harness actually runs 13; and a "mypy --strict: 0 erori" claim that holds for the harness but not for the adversarial-test file (9 benign `Optional`-narrowing errors). None changes any contract rule, and VE implements the harness/contract, not the test file.

---

## PASS/FAIL matrix

| § | Check | Result |
|---|-------|--------|
| 1 | Sources + local=remote + fingerprint | **PASS** |
| 2 | Version contradiction (decisive) | **PASS** (normative = v4.3; blemish noted) |
| 3 | VE_CAN_IMPLEMENT_WITHOUT_INVENTION | **PASS** |
| 4 | CEO configuration | **PASS** |
| 5 | Boundaries + circularity | **PASS** |
| 6 | Hierarchy | **PASS** |
| 7 | Sweep / breakout / promotion | **PASS** |
| 8 | Confirmation + priority (C13–C17) | **PASS** |
| 9 | Reason codes (exactly 29, closed) | **PASS** |
| 10 | Non-vacuity + harness (79/79, mypy, gates) | **PASS** (mypy-claim blemish) |
| 11 | Lookahead / snapshot / identity | **PASS** |
| 12 | Configuration domain | **PASS** |

## §1 — Sources · PASS
Branch HEAD **is** `d6e599e` ("range-hierarchical-v4.3 implementation package"); **local = remote OK on all 4 mirrors** (alpha1/discovery/lab/trader). Package `d6e599e` adds exactly three files: the V4.3 package doc (314 lines), `statistician/harness/range_v42_contract_harness.py` (409), `statistician/harness/test_range_v42_adversarial.py` (329). Manifest v2.7.94 `14d4c22` carries fingerprint `a5d69e2d…` (exact). Prior contract `5a9d5ec`, parameter sheet `4684e66`, construction config `b8cf2a7` all exist.

## §2 — Version contradiction · PASS (normative = v4.3)
- **Normative contract version: `range-hierarchical-v4.3`** — stated in the doc §2 and hard-coded in the harness (`contract_version = "range-hierarchical-v4.3"`, line 37).
- **Supersession:** `v4.3 = v4.2 (5a9d5ec) + the 17 corrections`; unchanged norms remain in the v4.2 doc, v4.3 governs the changed/added parts. §10 authorizes **only** `range-hierarchical-v4.3` under `config_id 24f72a60…`.
- **Schema/snapshot version:** there is a single version identity — the snapshot/restore fail-closed check keys on `contract_version` **and** `config_id` (no separate, conflicting schema/snapshot version string exists to create ambiguity).
- **Config version:** `config_id = 24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da` (provisional under `w_atr=0.80`, which the CEO fixed).
- **Reason-code set version:** the 29 closed codes, part of v4.3.
- **VE must implement:** `range-hierarchical-v4.3`.

**Decisive test — can VE choose V4.2?** No. `contract_version` is a single normative field ("v4.3"); the executable oracle encodes v4.3 (it tests C13/C14/C15); §10 authorizes only v4.3; and "v4.2" appears **only** in the non-normative review-status string and the harness *filename*. There is no field offering v4.2 as an alternative → no implementable ambiguity. (The stale "V4_2" labels are a naming blemish — see the consolidated list.)

## §3 — VE_CAN_IMPLEMENT_WITHOUT_INVENTION · PASS
The doc §4 matrix maps 25 requirements each to formula → input → output → reason code → test. I confirmed independently that every emitting function is present and numeric: `confirmed_swings` (swing at `j+K_struct`), `offer_swing`/`Cluster` (membership, median center), `degeneracy_check` (KILL geometry), `evaluate_candidate` (the confirmation conjunction), `Excursion.observe` (sweep/breakout race), `sweep_reversal_confirmed` (reversal), `promotion_check` (P1–P4), `assign_level` (R1/R2/R3 + depth), `snapshot`/`restore`, `guard_timestamp`, `Registry` (dead-id). No rule is left as prose or "conform geometriei". The three ex-prose/undefined items (C13/C14/C15) are now numeric and tested. VE's remaining work is per-bar orchestration, not rule invention.

## §4 — CEO configuration · PASS
All values are dataclass **fields** (`ConfigV43`): `d_macro=29`, `d_internal=12`, `n_touch=2`, `K_reentry=22`, `N_accept=3`, `K_struct=2` (bars), `n_external_swings=2` (swings — a **separate** field with different units), `atr_window=14`, `w_atr=0.80`; canonical ATR pinned by `atr_source="…vendor_bridge.atr14"` **and** `atr_provenance_wheel_sha256="39673910…"` (the ratified 0.4.1 wheel). `w_atr` raw = 0.788051 → operational 0.80 (CEO-fixed). `tol_cluster` and `s_max` are **properties** (`= 2×w_atr = 1.60`), never stored; `w_atr_sanity_ceiling` is a property `= 1.3952`. `config_id` is a SHA-256 over **all fields plus the derived values plus the ATR provenance** — changing any value (including `w_atr`, which drives the derived ones and the ATR source) changes the identity. No value is hidden in a bare literal. `validate()` enforces `0<w_atr<1.3952`, `d_internal<d_macro`, `n_touch≥2`, positive structural params.

## §5 — Boundaries + circularity · PASS
Swing confirmed at `j+K_struct` (`confirmed_swings`, `high[j]=max(high[j−K..j+K])`, unique). Upper/lower **clusters are separate** objects (`st.up`/`st.dn`); center = **median** (even count → mean of the two central). Degeneracy is **KILL, not DELAY**, evaluated **before** the duration gate inside the conjunction. **Circularity is broken by type:** membership is pre-confirmation (`Cluster.offer`), touch is post-confirmation, and `confirm_ts` under the KILL reading depends only on `w_atr`-independent conditions; `evaluate_candidate` reads none of its own confirmation outputs. The old ceiling `0.495` is retained historically but declared inapplicable (transplant from the 512-bar-median anchor); the new ceiling `1.3952` has the correct formula/units (`< 2.790/2` ATR, ATR-multiple). **Disjointness inequality:** requirement 6 is `separation > 2×w_atr×ATR_ref`; at **equality** `degeneracy_check` returns `ZONES_DEGENERATE` (the `<=` is inclusive → equality is KILL) — exact behavior specified.

## §6 — Hierarchy · PASS
Exactly two depths (`Depth {MACRO=0, INTERNAL=1}`); **MICRO is unrepresentable** (no enum member). `assign_level` gives INTERNAL a MACRO parent (`parent.structure_id`), never kills the parent; a candidate contained under an **INTERNAL** parent → `DEPTH_LIMIT_EXCEEDED` (C14 enforced, not merely written); partial overlap without containment → `PARTIAL_OVERLAP_NO_CONTAINMENT`; no containment/overlap → `LEVEL_ASSIGNMENT_UNRESOLVED`; a rejected candidate returns no depth and does not continue with an ID. Mapping (`BLIND_BATCH_02_LEVEL_MAPPING`): **88 MACRO + 26 UNRESOLVED = 114** (exact partition of level 1); the **12 INTERNAL are a separate population** (level 2), not double-counted (126 rows total).

## §7 — Sweep / breakout / promotion · PASS
`Excursion.observe`: `N_accept=3` consecutive outside closes → `BREAKOUT_ACCEPTED`; a re-entry **resets the counter to 0**; re-entry within `K_reentry=22` → `SWEEP_CONFIRMED`; otherwise `NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT`. `LIQUIDITY_SWEEP_REVERSAL` has a **calculable window = the episode's life** (C13, no new constant): confirmed when close breaks the last opposite swing formed **before** `open_bar`; `REVERSAL_WINDOW_EXPIRED` past `episode_end_ts`; `REVERSAL_REFERENCE_UNAVAILABLE` if absent; a reference confirmed **after** `open_bar` → `FUTURE_TIMESTAMP_REFUSED` (no lookahead). `K_struct=2` is the fractal radius (bars); `n_external_swings=2` is a swing count; `promotion_check` requires P1∧P2∧P3∧P4 in order — **promotion needs the second confirmed external swing (P3)**; slope alone cannot promote. Accepted breakouts are not retro-erased (the excursion state is monotone). HBL-20 is causal (test 14b: bar 52 = "info doesn't exist yet"; sweep confirmed at re-entry bar 56).

## §8 — Confirmation + priority · PASS
`evaluate_candidate()` is the **single** function for the confirmation conjunction (C15), returning **exactly one** reason code in the fixed normative order: (1) absent/closed → `BETWEEN_EPISODES`; (2) `ATR_UNAVAILABLE` (fail-closed); (3) `ESTABLISHING_FEW_SWINGS`; (4) `ZONES_INVERTED` (KILL); (5) `ZONES_DEGENERATE` (KILL); (6) `TOO_SHORT_MACRO|_INTERNAL`; (7) `OK_RANGE_MACRO|_INTERNAL`. The rationale is substantive and correct: input-missing and KILL states precede the duration gate, so **`TOO_SHORT_*` ("not yet") can never mask an already-dead candidate** (which would be a false statement). Corrections **C13–C17** are all present in the corrections table (C13 reversal window; C14 depth enforcement; C15 the conjunction function; C16 `PROMOTION_REFUSED_PRECONDITION_P1..P4` full naming; C17 `OK_RANGE_INTERNAL` added to symmetrize).

## §9 — Reason codes · PASS
The closed `REASONS` tuple contains **exactly 29** unique codes (independently counted). **I independently drove every declared code to actually emit through the public API** (`rt6_reachability.py`): **29/29 reachable, 0 missing, 0 extra** — including `DEPTH_LIMIT_EXCEEDED`, `LIQUIDITY_SWEEP_REVERSAL`, and `TOO_SHORT_MACRO/INTERNAL`. This is a mechanical reachability proof, stronger than the harness's own list-vs-list closure test (20a–20c). `SLOPE_UNAVAILABLE` was correctly **retracted** (C5, unreachable by construction). No comment/formatting removes a code (the Statistician's own C17 self-caught incident, where a mid-line comment silently dropped `TOO_SHORT_*` to 27, was caught by test 20 and fixed before delivery — confirming the coverage test works).

## §10 — Non-vacuity + harness · PASS (mypy-claim blemish)
Ran independently: **79 PASS · 0 FAIL** (exit 0) — the 16 adversarial cases + the 4 added groups (17 reversal, 18 depth, 19 conjunction+promotion, 20 coverage) + the non-vacuity gates. **Every non-vacuity gate shows `trece=True esueaza-corect=True`** (passes AND fails correctly). The harness actually runs **13** such gates (durata MACRO, durata INTERNAL, degenerare, inversare, sweep, breakout, cluster, INTERNAL level, UNRESOLVED level, channel classification, retrospective role, reversal, depth limit) — the doc says "12" (blemish; more coverage than claimed). **mypy `--strict`: the harness (`range_v42_contract_harness.py`) is CLEAN (Success, 0 issues)** — this is the oracle VE implements against. The adversarial-test file has **9 benign errors** (all `Optional`-narrowing in test assertions/f-strings, e.g. `boundary_upper − boundary_lower` on `float|None` properties whose clusters are non-empty at the call site); the tests still run 79/0. The Statistician's "mypy --strict: 0 erori" claim is therefore accurate for the harness but overstated for the test file (blemish).

## §11 — Lookahead / snapshot / identity · PASS
`guard_timestamp` refuses `ts > as_of` → `FUTURE_TIMESTAMP_REFUSED` (`ts == as_of` admitted). `role_known_ts ≥ confirm_ts` and role assertion on an open episode → `ROLE_ASSERTED_BEFORE_CONFIRMATION` / `ROLE_KNOWN_BEFORE_CONFIRM`. ATR is available only causally (`atr_ref` frozen at the contractual moment). Swings confirm only after the right-hand bars (`j+K_struct`). `snapshot`/`restore` refuse on `contract_version` **or** `config_id` mismatch → `SNAPSHOT_CONTRACT_MISMATCH`, and carry the excursion state, not just boundaries (C9). The harness functions are pure/deterministic (no shared module state), so determinism, chunk-invariance, and two-instance isolation hold by construction. `config_id` is a full fingerprint over scalars + derived relations + ATR-wheel SHA (C10).

## §12 — Configuration domain · PASS
Confirmed from `b8cf2a7`: **50 contributions from 25 segments**; **93 exclusions** (positive vs negative frontier examples); dispersion **0.24–3.93** (min BLIND-013 0.2405, max BLIND-019 3.9258); **78 labeled segments lack a numeric band on both frontiers**; `w_atr=0.80` is **construction-only** (raw 0.788051, CEO-fixed, provisional `config_id`). The doc §10 states plainly: no BLIND PASS, no semantic PASS, no PnL, `SEALED/OOS_ACCESS = 0`, detector never run. Invariants declared untouched: `n_generated_total=363`, `m_inference=26`, tombstones, Alpha registry, verdicts, F1–F6, F7 `SAFETY_GUARD`, LIVE_SHADOW, broker gate.

---

## CONSOLIDATED DEFECT LIST (all non-blocking — no implementable gap)
1. **Version naming inconsistency.** The normative `contract_version="range-hierarchical-v4.3"` is singular and unambiguous, but the review-status string (`RANGE_V4_2_IMPLEMENTATION_PACKAGE_READY_…`) and the harness filename (`range_v42_contract_harness.py`) still say "v4.2". *Fix:* rename the status label and harness file to v4.3. *Not blocking:* no field offers v4.2 as an implementable alternative; VE binds `contract_version` (v4.3) and the oracle enforces v4.3.
2. **Non-vacuity gate count.** Doc §6/§D say "12" (Douăsprezece) gates; the harness runs **13**. *Fix:* correct the count to 13. *Not blocking:* more coverage than claimed; every gate passes and fails correctly.
3. **mypy claim scope.** Doc §6 states "mypy --strict: Success, 0 erori"; true for the harness, but the adversarial-test file has 9 benign `Optional`-narrowing errors. *Fix:* scope the claim to the harness or tighten the test file's Optional handling. *Not blocking:* test code, not contract; harness is clean; tests pass 79/0.

## What I re-verified independently vs. did not run
- **Independently this session:** §1 commits/local=remote/fingerprint; §2 version fields from doc + harness source; §3 emitter presence; §4 config fields/properties/`config_id`; §5/§6/§7/§8/§11 from harness source; §9 **all 29 reason codes driven to emit through the public API** (0 missing/0 extra); §10 harness run (79/0) + mypy `--strict` (harness clean, test file 9 benign) + non-vacuity gates each pass+fail; §12 config-domain numbers from `b8cf2a7`.
- **Did not / could not:** implement the detector, run the blind corpus, validate range semantics, or run PnL/SEALED — all out of scope by mandate.

## Disposition
`RANGE_V4_IMPLEMENTATION_PACKAGE_STATIC_PASS` authorizes **only** the separate VE-prototype mandate (implement `range-hierarchical-v4.3` under `config_id 24f72a60…`, verified against the §6 harness), followed by a further Red Team static review. It does **not** validate that the detector recognizes ranges, and it does **not** authorize a wheel, the Strategy Catalog, Alpha, AI-Trader integration, LIVE_SHADOW cutover, the broker, or trades. The Statistician should correct the three non-blocking blemishes above. Red Team modified nothing outside `red_team/`.
