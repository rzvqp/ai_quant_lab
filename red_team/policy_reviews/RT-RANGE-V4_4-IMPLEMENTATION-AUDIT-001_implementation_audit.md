# RED TEAM — RANGE V4.4 IMPLEMENTATION AUDIT
### RT-RANGE-V4_4-IMPLEMENTATION-AUDIT-001 · Auditor: Red Team · 2026-08-20 · frozen artifact `3bb61cf`

Independent static/construction audit — the mandatory gate between V4.4 implementation freeze and fresh blind
validation. No blind execution, no redesign, no recalibration, no parameter selection. Every material claim
reproduced independently, not trusted by assertion.

---

## 0 — VERDICT

```
V4_4_IMPLEMENTATION_AUDIT_PASS_WITH_NONBLOCKING_NOTES
V4_4_FRESH_BLIND_VALIDATION_AUTHORIZED_FOR_CEO_DECISION
```

Commit `3bb61cf` **faithfully implements the frozen, calibrated V4.4 mechanism**: deterministic, causal,
identity-correct, non-vacuously tested, with V4.3 byte-preserved and **zero validation-data contamination**.
The three non-blocking notes are a pre-existing test-portability artifact, one honestly-disclosed
structurally-unreachable branch, and the already-accepted gentle-channel limitation — none is a defect in the
V4.4 implementation. This audit does **not** validate V4.4: no detector was run on any blind evidence and no
performance number is asserted. Trust in V4.4's numbers requires the fresh-blind-batch stage (§30 note).

---

## 1 — AUDIT MATRIX

| Area | VE claim | RT independent finding | PASS/NOTE/BLOCK |
|---|---|---|---|
| Provenance | chain valid, `3bb61cf` HEAD | 9 commits exist; ancestry freeze `c57d103`→protocol `967222a`→calib `898f149`→impl `3bb61cf`; `3bb61cf` parent = `898f149`; HEAD; local=remote ×4; no later semantic change | **PASS** |
| V4.3 preservation | `V4_3_BYTE_UNTOUCHED` | `range_semantic_v4_3.py`/`range_engine_v4_3.py`/`scoring.py` **byte-identical** to `bc6b9dc` across the whole V4.4 chain; `3bb61cf` touched **no** V4.3 file | **PASS** |
| Frozen-design fidelity | T1–T9+T-KILL implemented per `f241698` §3 | Transition map matches; no `SEMANTIC_DRIFT`/`MISSING_RULE`/`EXTRA_RULE`/`PRIORITY_MISMATCH`/`IMPLICIT_TRANSITION` found | **PASS** |
| State machine | 5 states, deterministic | Priorities T-KILL=0 > excursion > discrimination > duration; no accidental sink; WEAKENING bounded | **PASS** |
| Directional gate | ER/traversal/RND hard, alternation supporting, drift diagnostic | Source-confirmed: T3 returns only on ER/traversal/RND+duration; falsified whole-life `normalized_drift>s_max` **not** restored as a MACRO gate; 4 signals distinct | **PASS** |
| Alternation wiring | fixed unwired→wired, kept supporting | T3 appends `INSUFFICIENT_ALTERNATION_EVIDENCE` but never `return`s on it — supporting-only, non-gating | **PASS** — `IMPLEMENTATION_FIX_CONSISTENT_WITH_FROZEN_DESIGN` |
| WEAKENING | bounded, no indefinite limbo | Mutation removing the bound (`WEAKENING_MAX_BARS`→10⁹) is CAUGHT; dual-trigger T4>T5 deterministic; recovery uses strict threshold | **PASS** |
| Restore atomicity | atomic fail-closed | 6 failure modes (wrong config/contract/fingerprint/missing-field/wrong-type/corrupt-nested) all refused with **STATE_BEFORE == STATE_AFTER** | **PASS** |
| StructureV44 restore fidelity | exact type roundtrip | snapshot→restore→snapshot **identical**; VE's `_awaiting_role`-MACRO test in suite | **PASS** |
| Config identity | `config_id = 23d98c07…` | Recomputed independently from `ConfigV44` → `23d98c07488913c1…8969` **MATCH**; all 10 calibrated + 9 V4.3 params match `898f149` exactly | **PASS** |
| Implementation fingerprint | `833aedfd…`/`1371444c…` | Canonical git-blob sha256 = report exactly (67,340 B / 9,599 B); ties unambiguously to frozen files | **PASS** |
| Snapshot/versioning | fail-closed across boundary | Wrong config_id/contract(`v4.3`)/fingerprint/version all refused; no silent V4.3→V4.4 migration | **PASS** |
| Reason codes | 40 (29+11), reachable | `len(REASONS_V44)==40==unique`; all reachable **except** documented `EPISODE_MERGED` | **PASS** |
| Confirmation timing (prefix invariance) | invariant across 96/288/480 | My own 61-bar prefix in 96/288/480 containers → **identical** state chronology; `PREFIX_CONFIRMATION_INVARIANCE_PASS` | **PASS** |
| Causality | no-lookahead/prefix/chunk/replay/snapshot invariance | Independent constructions: truncate@200==full first-200; deterministic replay; chunk/snapshot-restart at splits 20/61/150 all identical | **PASS** |
| Episode identity | MERGE unreachable-by-invariant | Confirmed **A** — single-active-MACRO invariant (`forming_macro = _active_macro is None`, unchanged from V4.3) makes MERGE structurally unreachable; implemented for spec-completeness, disclosed | **PASS** — `STRUCTURALLY_UNREACHABLE_BY_FROZEN_INVARIANT` (non-blocking) |
| INTERNAL parity | zero divergence vs V4.3 | My own 300-bar mixed macro+internal run: **0** INTERNAL-field divergences V4.3 vs V4.4 | **PASS** |
| Adversarial suite | 22/22, pre-registered | 22/22 pass; strong assertions (state chronology + forbidden `OK_RANGE_MACRO`), not "no-exception" | **PASS** |
| Gentle-channel limitation | #21/#22 confirm, disclosed | Tests assert CONFIRM (not force-rejected); no post-calibration change, no special-case detector, no MB3 exception | **PASS** — `KNOWN_LIMITATION_PRESERVED` |
| Test non-vacuity | 76 new, meaningful | 76 V4.4 tests pass; **6/6 independent mutations CAUGHT** (ER/RND/traversal gates, WEAKENING bound, episode IoU, snapshot gate); source restored byte-identical | **PASS** |
| Mutation testing | 6/6 caught | Reproduced independently — every mutation turns the suite red | **PASS** |
| mypy/static | clean | Independent `mypy --strict` on both V4.4 files: **Success, no issues** | **PASS** (see note 1) |
| Complexity/memory | O(1)/bounded | Bounded W-window deque + rolling accumulator, O(1) counters; snapshot state does not grow per-bar; WEAKENING counter bounded (mutation-confirmed) | **PASS** |
| Rollback | V4.3 baseline intact without V4.4 | V4.3 `config_id=24f72a60` unchanged, importable standalone; V4.4 additive/new-namespace; 394 V4.3-baseline tests green | **PASS** |
| Data contamination | no MB3 use | Detector/engine/tests/report/commit contain **no** MB3 window/escrow/label/prediction semantic reference (only governance "not accessed / sealed" strings) | **PASS** — `MB3-001→024 NOT USED FOR IMPLEMENTATION`, `MB3-025→048 SEALED / NOT ACCESSED` |

**No area is BLOCK. No area requires AMENDMENT.**

## 2 — NON-BLOCKING NOTES

1. **mypy-portability test artifact (pre-existing).** `test_range_semantic_v4_3.py::test_mypy_strict_clean_on_all_touched_files`
   fails in a fresh venv because it invokes `subprocess.run(["python", "-m", "mypy", …])` with a hardcoded
   `"python"` rather than `sys.executable` — the same RT-RANGE-0007 #6 artifact, in the **unchanged V4.3
   baseline** test file. Independent `mypy --strict` on the V4.4 files is clean. Not a V4.4 defect; a
   long-standing test-portability nit (fixable by using `sys.executable`).
2. **`EPISODE_MERGED` structurally unreachable.** By the single-active-MACRO invariant (preserved from V4.3),
   no two MACRO candidates are ever concurrently live, so the MERGE branch cannot fire. It is implemented (not
   dead code) against a hypothetical future concurrent-candidate architecture and honestly disclosed. Classified
   **A — `STRUCTURALLY_UNREACHABLE_BY_FROZEN_INVARIANT`**, fully consistent with the frozen design; non-blocking.
3. **Gentle-channel / violent-zigzag known limitation.** Adversarial #21 (slow drifting equilibrium) and #22
   (violent zigzag) confirm as RANGE — the exact, already-accepted, non-blocking risk from calibration
   (`898f149` §7) and design (`236e8e7` §12). The implementation **preserves** it honestly (test asserts
   confirmation, not a forced rejection); there is no hidden retuning. Its real magnitude is a question for the
   fresh-blind-validation stage, not this audit.

*Minor observation (not a note):* the V4.4 implementation fingerprint covers the two V4.4-owned files; V4.4's
behaviour also depends on the imported V4.3 symbols, which are separately pinned (`bc6b9dc`, byte-verified
untouched here). Together they cover all semantically-material files; a fingerprint that additionally embedded
the V4.3 dependency hash would be marginally stronger but is not required.

## 3 — NEXT PHASE (recorded intention only — NOT authorized here, mandate §30)

CEO intends the next validation batch = **14 fresh windows**, genuinely independent of all V4.4 design/
calibration/implementation evidence, selected+frozen before scoring, labeled without detector access,
predictions frozen without label access, scored only after both sides frozen. **This mandate does not
authorize creating/selecting/labeling/decrypting/executing those windows.** `MB3-025→048` remain sealed and
separate. No detector performance number on blind evidence is produced here.

## 4 — SCOPE / PROHIBITIONS

Static/construction audit only. No blind execution (MB3-001→024, MB3-025→048, or any fresh batch), no
redesign/recalibration/parameter selection, no Strategy Catalog/Alpha/AI Trader/LIVE_SHADOW/broker. Frozen
commit `3bb61cf` preserved; V4.3 code/config unmodified; all changes confined to `red_team/`.

---

*Red Team · V4.3/labels/escrow unmodified · changes only in `red_team/` · MB3-025→048 sealed · MB3-001→024 zero-validation-weight · LEDGER E92 (prev E91).*
