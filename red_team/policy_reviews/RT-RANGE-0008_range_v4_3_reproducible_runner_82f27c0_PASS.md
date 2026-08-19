# RED TEAM — RANGE V4.3 REPRODUCIBLE RUNNER AUDIT
### RT-RANGE-0008 · **`RANGE_V4_3_REPRODUCIBLE_RUNNER_AUDIT_PASS`**
**Date:** 2026-08-19 · **Auditor:** Red Team · **Target:** VE's reproducible run package, frozen `runner_commit = 82f27c0` over `prototype_commit = f224e7d`, `contract_version = range-hierarchical-v4.3`, `config_id 24f72a60…`. Direct response to RT-RANGE-0007 (`b7c6fa8`) verdict B (`CONSTRUCTION_RESULT_NOT_REPRODUCED`) + finding #1 (freeze-fail).

**Audits only the runner, scorer, synthetic reproduction, and anti-leakage separation. No real sealed bars accessed, no SEALED/OOS/escrow/PnL/broker/LIVE_SHADOW. Nothing modified; nothing repaired. Changes only in `red_team/`.**

---

# VERDICT — **`RANGE_V4_3_REPRODUCIBLE_RUNNER_AUDIT_PASS`**

VE committed exactly what RT-RANGE-0007 found missing. From a **clean Git-only checkout** I installed and ran the package and **reproduced all 12 construction figures byte-identically**; the frozen detector is byte-identical to `f224e7d` and is invoked unchanged; inference and scoring are two isolated stages (inference never reads labels, scoring never runs the detector — confirmed both statically and by dynamic file-access instrumentation); and the predictions are cryptographically frozen (SHA-256 + read-only) so they cannot be modified after labels are read. None of the FAIL conditions (uncommitted dependency, leakage, hash difference, non-reproducibility, post-label prediction modification) is present.

| sub-verdict | result |
|---|---|
| `CLEAN_CHECKOUT_REPRODUCIBILITY` | **PASS** |
| `HISTORICAL_SYNTHETIC_RESULT` | **REPRODUCED** (+ `CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY` / `CIRCULAR_LABEL_DERIVED_BARS` / `ZERO_VALIDATION_WEIGHT`) |
| `INFERENCE_LABEL_ISOLATION` | **PASS** |
| `SCORER_DETECTOR_ISOLATION` | **PASS** |
| `RUNNER_PRE_BLIND_FREEZE_PROTOCOL` | **PASS** |

**This PASS authorizes ONLY `RANGE_V4_3_INDEPENDENT_BLIND_EXECUTION_MANDATE_PREPARATION`** — it does not run the blind validation, modify the detector, or authorize a wheel, Strategy Catalog, Alpha, AI-Trader, LIVE_SHADOW, broker, trades, or the 6-hour regression. The synthetic construction result remains circular and carries **zero validation weight**; the only real accuracy measure is the separate blind mandate on the sealed bars.

**Two non-blocking findings** (below): the anti-leakage AST tests catch only 6/12 injected mutations, and the mypy in-suite test still hardcodes `"python"` (RT-RANGE-0007 #6, unchanged in the frozen prototype).

---

## PASS/FAIL matrix

| § | Check | Result |
|---|-------|--------|
| 1 | Sources + local=remote + 25 files + no uncommitted deps | **PASS** |
| 2 | Clean-checkout reproducibility (decisive) | **PASS** |
| 4 | Prototype frozen byte-identical | **PASS** |
| 5 | Historical synthetic reproduction (12 figures) | **REPRODUCED** |
| 6 | Inference/scoring separation | **PASS** |
| 7 | Anti-leakage tests non-vacuous (mutation) | **PARTIAL** (6/12; no real path) |
| 8 | Dynamic file-access audit | **PASS** |
| 9 | Input schema fail-closed | **PASS** |
| 10 | Output schema (no leakage fields) | **PASS** |
| 11 | Open-at-end structures fix | **PASS** |
| 12 | Freeze + tamper detection | **PASS** |
| 13 | Determinism | **PASS** |
| 14 | Scorer + denominators | **PASS** |
| 15 | 426 tests + mypy | **PASS** (425 real + mypy clean; 1 portability artifact) |
| 16 | Freeze order | **PASS** |

## §1 — Sources · PASS
`82f27c0` is HEAD (branch `discovery-mk-matrix-v1`), descends from `f224e7d`, **local = remote OK on all 4 mirrors**, and adds exactly **25 files** (delivery report + `blind_runner/` 10 + `construction_reproduction/` 13 + PROJECT_STATE). `code/run_production_pipeline.py` is modified but **not referenced** by the runner (grep over `blind_runner/`+`construction_reproduction/` is empty) — it is neither imported, read, nor needed. `82f27c0` touched **no** detector or historical test file vs `f224e7d` (empty `git diff`); the runner is purely additive.

## §2 — Clean-checkout reproducibility · PASS
I built the audit environment **exclusively from Git** (`git archive 82f27c0 ve_n1_replay | tar -x` into a fresh dir; a fresh venv with `ve_n1_replay` installed from the archive plus the external pinned `ve_brain 0.1.3` + numpy). The package installed and the reproduction ran **entirely from committed content** — no worktree caches, scratch files, local results, or env vars. `CLEAN_CHECKOUT_REPRODUCIBILITY = PASS`.

## §4 — Prototype frozen · PASS
Git blob SHAs of `range_semantic_v4_3.py`, `range_engine_v4_3.py`, `version.py`, and the semantic test file are **byte-identical** between `82f27c0` and `f224e7d`. `inference.py` re-hashes the two detector files at runtime against pinned `FROZEN_HASHES` and refuses fail-closed on any mismatch, and asserts `ConfigV43().config_id() == FROZEN_CONFIG_ID (24f72a60…)`. The runner invokes exactly the `f224e7d` detector; no modified copy, wrapper, or substitution.

## §5 — Historical synthetic reproduction · REPRODUCED
Running `construction_reproduction/run_construction.py` from the clean checkout reproduced **every figure exactly**:

| figure | committed | Red Team | Δ |
|---|---:|---:|---:|
| MACRO matched / GT | 57 / 88 | **57 / 88** | 0 |
| MACRO recall | 0.648 | **0.648** | 0 |
| INTERNAL matched / GT | 2 / 12 | **2 / 12** | 0 |
| INTERNAL recall | 0.167 | **0.167** | 0 |
| SWEEP_CONFIRMED | 209 | **209** | 0 |
| BREAKOUT_ACCEPTED | 112 | **112** | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 21 | **21** | 0 |
| IS_TREND_MACRO (promotion) | 94 | **94** | 0 |
| funnel total | 725 | **725** | 0 |
| funnel MACRO / INTERNAL / partial-overlap | 151 / 16 / 558 | **151 / 16 / 558** | 0 |

The regenerated `construction_run_results.json` is **byte-identical (LF-normalized, `62a8fa9c…`)** to the committed one — the only raw-byte difference was CRLF vs LF (a Windows file-write artifact; content identical). The committed result carries the mandatory tags `CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY`, `CIRCULAR_LABEL_DERIVED_BARS`, `ZERO_VALIDATION_WEIGHT`, and `historical_reproduction.status = HISTORICAL_SYNTHETIC_RESULT_REPRODUCED` with zero mismatches. **Fixture provenance:** the label fixtures are committed self-contained in `construction_reproduction/fixtures/` (no cross-branch runtime reads); the addendum sets the corrected windows **BLIND-046=288, BLIND-047=96, BLIND-048=480**. **This remains construction-only, circular (bars synthesized from the labels they are scored against), with zero validation weight.**

## §6 — Inference / scoring separation · PASS
**Static:** `inference.py` imports only `schemas`, `ve_n1_replay` (Bar/ConfigV43/Engine/version) — no labels, no scoring. `scoring.py` imports only `hashlib`/`json`/`statistics`/`pathlib` — no detector, no inference, no importlib. **`INFERENCE_LABEL_ISOLATION = PASS`, `SCORER_DETECTOR_ISOLATION = PASS`** (corroborated dynamically in §8).

## §7 — Anti-leakage tests non-vacuous · PARTIAL (no real contamination path)
Mutation testing (12 forbidden patterns injected into temp copies): the delivered AST tests **catch 6/12** — direct `import labels`, `open('LEVEL_MAPPING…')`, `read_text('…LOCKED_LABELS…')`, `import scoring`, `import range_semantic_v4_3`, `importlib` in scoring. They **miss 6/12**: `__import__(...)`, `exec`/`eval`, `subprocess.run(['python','inference.py'])`, `from ve_n1_replay import range_semantic_v4_3 as _alias` (the import check records only the `from`-module, not the imported submodule name), `getattr(dynamic_module,'RangeSemanticEngineV43')`, and a **neutral-name file path** (`open('./data/aux.json')`). **This is a real test-robustness limitation** (the AST guard is not a complete leakage barrier). **But there is no real contamination path:** the delivered code contains none of these patterns (§6), the dynamic audit shows no actual label/detector access (§8), and the cryptographic freeze blocks any post-label prediction change (§12). *Recommended hardening:* add `__import__`/`eval`/`exec`/`subprocess` to the forbidden-call set, record `ImportFrom` imported names (not just the module), and flag any `open`/`read_text` on a path not in an explicit allow-list.

## §8 — Dynamic file-access audit · PASS
Instrumenting `open`/`read_text`/`read_bytes`/`subprocess`/`socket` while running the **actual** stages: **inference** read only the **input file** (`input.json`) — zero label-ish files, zero subprocess, zero network; it wrote `predictions.json` + `predictions.sha256`. **Scoring** read only `predictions.json` + `predictions.sha256` (labels passed in-memory) — zero detector files, zero subprocess, zero network. Empirically, inference never touches labels and scoring never runs the detector.

## §9 — Input schema · PASS
`validate_and_normalize_input` accepts a valid window and refuses fail-closed on `NaN`, `inf`, `high < low`, missing OHLC field, empty window, and duplicate window-id (independent probes). (VE's `test_schemas` covers the remaining cases — timestamp order/duplicate, wrong timeframe, corrupt/truncated manifest, extra bar after hash, and normalization invariance — all passing.)

## §10 — Output schema · PASS
The prediction records carry `structure_id`/`parent_structure_id`/`predecessor_id`, `depth`, `start_ts`/`end_ts`/`confirm_ts`, `boundary_lower`/`upper`, `role`/`role_known_ts`, plus per-window `run_hash`, `n_bars`, opaque `window_id`; the manifest carries `prototype_commit`/`config_id`/frozen hashes/input+normalized hashes and `zero_labels_access=True`. No real calendar timestamp, window period, local path, username, secret, label, mapping, or PnL appears (VE's `test_zero_real_calendar_timestamp_in_output`, `test_zero_local_paths_zero_secrets_in_output`, `test_manifest_declares_zero_labels_access` pass).

## §11 — Open-at-end structures · PASS
The prediction output **includes** a confirmed-but-still-open structure (observed `start_ts=3, end_ts=None, confirm_ts=32`), closing the RT-RANGE-0007-era gap where such structures were dropped. VE's `test_still_open_structure_at_window_end_is_included` and the scorer's open-structure handling (span to the observable limit `n_bars`, never into the future) pass; the indexing convention is respected (no extension past the last observed bar).

## §12 — Freeze + tamper detection · PASS
`predictions.json` is written **read-only**, hashed to `predictions.sha256`; `load_frozen_predictions` recomputes the hash and refuses on mismatch, and separately refuses on `config_id`/`prototype_commit` mismatch. My independent tamper tests (on writable copies): a **one-bit flip** in predictions → refused; a **tampered `.sha256`** → refused; a **re-hashed predictions with wrong `config_id`** → refused; **wrong `prototype_commit`** → refused. **This is the control that prevents predictions generated after reading labels from being used in the blind run:** inference (which never sees labels) produces the predictions and freezes them by hash before scoring runs; any re-generation would need a new hash, and the scorer additionally binds `config_id` + `prototype_commit`.

## §13 — Determinism · PASS
The strongest evidence is §5: two independent runs (VE's committed run and my clean-checkout run) produced a **byte-identical** results file (LF-normalized) — proving the whole pipeline, including the scorer's matching and **tie-breaking**, is fully deterministic. VE's `test_same_input_byte_identical_output`, `test_window_order_independent_per_window_result`, `test_two_processes_no_shared_state`, `test_chunk_invariance_bar_by_bar_matches_single_batch`, and `test_snapshot_restart_mid_window_identical_continuation` pass.

## §14 — Scorer + denominators · PASS
48 windows / 13 824 bars; **88 MACRO + 26 UNRESOLVED = 114** level-1 + **12 INTERNAL** separate — confirmed in the committed results (`macro_gt_count=88`, `internal_gt_count=12`, `unresolved_gt_count=26`). MACRO recall uses 88 (57/88), INTERNAL uses 12 (2/12), UNRESOLVED is reported separately and never scored, INTERNAL is not double-counted; corrected window lengths applied. The matching/tie-breaking is deterministic (byte-identical reproduction). VE's `test_scoring` oracle (perfect match, zero match, partial overlap, two predictions for one label, one prediction intersecting two labels, open structure, boundary error, start/end/single-bar segments, tie) passes.

## §15 — Tests + mypy · PASS (1 portability artifact)
**425/426 tests pass** from the clean checkout. The single "failure" is again `test_mypy_strict_clean_on_all_touched_files` — the **frozen** V4.3 test still runs `subprocess.run(["python","-m","mypy",…])` against the base interpreter (no mypy there), the exact RT-RANGE-0007 finding #6, unchanged because the prototype is byte-frozen; VE added no portable runner-level mypy test. **The actual `mypy --strict` is clean** — Success, 0 issues, on `inference.py`, `scoring.py`, `schemas.py` (and the V4.3 modules). Per-group: historical/incremental + V4.3 detector tests (the 370-suite) + `blind_runner/tests` (schemas, inference, scoring, anti-leakage-AST, tamper/determinism) + `construction_reproduction/tests` — all pass except the one portability artifact.

## §16 — Freeze order · PASS
The delivery report §9 documents the correct order this time — **tests + fingerprints computed BEFORE the commit**, then commit → push → local=remote → declare `RANGE_V4_3_RUNNER_PRE_BLIND_FROZEN` — explicitly contrasting `f224e7d` (where the run preceded the commit). The declared artifact fingerprints (`synth.py`, `inference.py`, `scoring.py`) **match the committed files**. No real sealed bars were run in this stage (the construction is synthetic; `blind_runner` uses `dev_fixtures`, not real bars). `RUNNER_PRE_BLIND_FREEZE_PROTOCOL = PASS`.

## CONSOLIDATED FINDING LIST (both non-blocking)
1. **Anti-leakage AST tests are incomplete** — catch 6/12 injected mutations, miss `__import__` / `exec`/`eval` / `subprocess` / aliased-submodule import / `getattr`-on-dynamic-module / neutral-name file path. No real contamination path exists in the delivered runner (clean code + dynamic isolation + cryptographic freeze), but the AST guard should be hardened before it is relied on as a barrier for future changes. *Fix:* extend the forbidden-call set, record `ImportFrom` imported names, and enforce an allow-list on file opens.
2. **mypy in-suite test not portable** — still hardcodes `"python"` (frozen V4.3 test, RT-RANGE-0007 #6, unchanged); VE added no portable runner-level mypy test. Actual `mypy --strict` is clean. *Fix:* add a runner-level mypy test using `sys.executable`.

## What I re-verified independently vs. did not run
- **Independently this session (clean Git-only checkout + fresh venv):** §1 sources/local=remote/25-files; §2 install+run from archive; §4 blob byte-identity; §5 all 12 figures + byte-identical results JSON; §6 static isolation; §7 12-mutation testing; §8 dynamic file/subprocess/network instrumentation of both stages; §9 input fail-closed probes; §11 open-structure in output; §12 four tamper attacks; §14 denominators from committed results; §15 425/426 run + `mypy --strict` clean on the runner; §16 fingerprint match.
- **Not run:** real sealed bars, SEALED/OOS, escrow, PnL, broker, LIVE_SHADOW, the blind validation itself (all out of scope by mandate).

## Disposition
`RANGE_V4_3_REPRODUCIBLE_RUNNER_AUDIT_PASS` authorizes **only** `RANGE_V4_3_INDEPENDENT_BLIND_EXECUTION_MANDATE_PREPARATION` — preparing the separate mandate in which Red Team runs the frozen `f224e7d` detector, via this runner, on the **real sealed bars**, freezes the predictions by hash, and only then scores them against the labels. It does not authorize running the blind validation now, modifying the detector, a wheel, the Strategy Catalog, Alpha, AI-Trader integration, LIVE_SHADOW cutover, the broker, trades, or the 6-hour regression. The two findings should be addressed but do not block. Red Team modified no VE/Statistician code and changed nothing outside `red_team/`.
