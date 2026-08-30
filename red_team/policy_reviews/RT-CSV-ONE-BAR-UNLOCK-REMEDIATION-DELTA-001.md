# RED TEAM — DELTA REVIEW · CSV ONE-BAR UNLOCK REMEDIATION · FINAL AUTONOMOUS-Q4 GATE
### RT-CSV-ONE-BAR-UNLOCK-REMEDIATION-DELTA-001 · Auditor: Red Team · 2026-08-30

Delta review of the remediation `a87f42d → 7241b17` addressing the single blocking finding of E104
(`ONE_BAR_UNLOCK_ENFORCED=FAIL`, `SAFE_FOR_AUTONOMOUS_SEQUENTIAL_Q4=NO`). Delta only; prior passed adapter
findings not reopened. Bar 380 not exposed; no real bar-380 materialization; Q4 not resumed; source not
modified; synthetic ≤-boundary data only for adversarial testing.

---

## 0 — FINAL DECISION

**Can AI Trader now safely continue from bar 380 through the remainder of Q4 under autonomous sequential
causal replay without CEO authorization for every bar? → YES** (conditional on the one wiring note in §8).

```
RED_TEAM_DELTA_REVIEW_COMPLETE = YES
REMEDIATION_COMMIT = 7241b1763ce38861423a918473e7c19f4a30e989
REMEDIATION_IDENTITY_VERIFIED = YES
SCOPE_CLEAN = YES

ONE_BAR_UNLOCK_ENFORCED = PASS
ARBITRARY_RUNTIME_BOUNDARY_REACHABLE = NO

DURABLE_STATE_GATED_EXTENSION = PASS
PENDING_DECISION_GATE = PASS
COMMIT_BEFORE_EXTEND = PASS
POINTER_CONSISTENCY_GATE = PASS
FAIL_CLOSED = PASS

FIXTURE_OVERWRITE_PROTECTION = PASS
RESTART_RESUME_EXACT = PASS
AUTONOMOUS_ONE_BAR_LOOP = PASS

ATOMIC_LOCK_WHILE_P007_OPEN = PASS
P007_H1_EMA_SEMANTIC_PRESERVED = PASS

BAR_380_ACCESSED = NO
TESTS = 63 (50 existing + 13 new) reproduced + 12 independent RT synthetic checks, all pass

BLOCKING_FINDINGS = NONE
NONBLOCKING_FINDINGS = 2 (autonomous-wiring requirement; per-extension full-source re-hash + fixture accretion)

SAFE_FOR_AUTONOMOUS_SEQUENTIAL_Q4 = YES (conditional on §8 note 1)
RED_TEAM_VERDICT = PASS_WITH_NONBLOCKING_NOTES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## 1 — IDENTITY & SCOPE (§2)

`7241b17` ("fix: fail-closed one-bar autonomous extension gate (Red Team E104)") is HEAD, a descendant of
`a87f42d`, changing **exactly 3 files**: `fixtures/autonomous_extend.py` (new, 138), `fixtures/
materialize_sealed_fixture.py` (+31/−6), `tests/test_autonomous_extend.py` (new, 202). `engine.py`,
`sealed_reader.py`, `ema.py`, `persistence.py`, and both `Q4_SEALED_1_378/379.csv` fixtures are **byte-
unchanged** (empty diff `a87f42d..7241b17`). No MT5/S5/P007/MGMT-004/runtime change.
**REMEDIATION_IDENTITY_VERIFIED = YES · SCOPE_CLEAN = YES.**

## 2 — ORIGINAL BLOCKER RE-TESTED (§3) — closed

The E104 vulnerability was that the extension boundary was caller-controlled and arbitrary. The new
`autonomous_extend.extend_next_bar(*, store, source_path, output_dir)` is the **only** autonomous entrypoint
and takes **no boundary parameter** — it derives `TARGET = durable_state.source_identity.sealed_through_bar_
index + 1` **internally**. Independently verified (`inspect.signature`): the sole non-infrastructure params are
`store`/`source_path`/`output_dir`; there is **no** path to request `+2`, `+10`, or arbitrary `N`.
**ONE_BAR_UNLOCK_ENFORCED = PASS · ARBITRARY_RUNTIME_BOUNDARY_REACHABLE = NO.**

The arbitrary `materialize()`/`--max-bar` CLI **remains** (unchanged) for CEO-authorized manual/research use;
nothing in `autonomous_extend.py` or `engine.py` calls it. This is exactly the §4 `TECHNICAL_CAPABILITY` vs
`AUTHORIZED_RUNTIME_PATH` distinction, cleanly realized.

## 3 — COMMIT-BEFORE-EXTEND + POINTER CONSISTENCY (§4) — PASS

`extend_next_bar` fail-closes (`OneBarUnlockRefusedError`, **no fixture written, no state touched**) unless
**all** hold:
- `pending_decision is None` (**PENDING_DECISION_GATE / COMMIT_BEFORE_EXTEND**);
- the current sealed fixture named in durable state **exists** and its **content hash matches** the recorded
  hash (tamper/since-modified protection);
- `last_committed_timestamp` is present and, **looked up in the fixture's own rows**, maps to Q4 bar index ==
  `sealed_through_bar_index` — i.e. it does **not** trust the state file's arithmetic; a state file with a
  correct-looking `next_bar` but a tampered/earlier `last_committed_timestamp` is caught here
  (**POINTER_CONSISTENCY_GATE**, the strongest gate);
- `next_bar == sealed_through_bar_index + 1` exactly;
- the target `Q4_SEALED_1_{target}.csv` does **not** already exist (**FIXTURE_OVERWRITE_PROTECTION**).

Only then is `materialize(target = sealed+1)` called. **DURABLE_STATE_GATED_EXTENSION = PASS ·
PENDING_DECISION_GATE = PASS · COMMIT_BEFORE_EXTEND = PASS · POINTER_CONSISTENCY_GATE = PASS.**

## 4 — FAIL-CLOSED / NO FUTURE EXPOSURE (§5) — PASS

Every refusal path raises **before** `materialize()` is reached, so no future OHLCV is parsed, returned,
logged, or written to a fixture; my probe confirmed **no `Q4_SEALED_1_6.csv` is written** on every refused
case (skip, pending, tampered pointer, hash mismatch). Even on the success path, `materialize` uses the same
`SealedReader` (boundary error at `target+1` **before** its OHLCV parse), and `_bar_index_for_timestamp` reads
only the already-sealed fixture bounded at its own claimed boundary (never the unsealed source). **FAIL_CLOSED
= PASS · UNAUTHORIZED_FUTURE_SEMANTIC_EXPOSURE = NO.**

## 5 — FIXTURE SAFETY (§6) — PASS

`Q4_SEALED_1_378.csv` and `Q4_SEALED_1_379.csv` are **byte-unchanged** by `7241b17`; each boundary
materializes to its own separately-named file, and `extend_next_bar` refuses if the target already exists (no
overwrite). Bar 380 is not present in any fixture and was not accessed. **FIXTURE_OVERWRITE_PROTECTION = PASS ·
CHECKPOINT_378_UNCHANGED = YES · CHECKPOINT_379_UNCHANGED = YES · BAR_380_ACCESSED = NO.**

## 6 — RESTART / AUTONOMOUS LOOP (§7) — PASS (independently reproduced on synthetic data)

Independent RT probe (synthetic source bars 1–12, `close=1000+N`, in a tmp dir — **never the real Q4 source,
never real bar 380**) drove the real `extend_next_bar` through: valid +1 (materializes exactly the next bar,
not the one after); `+2` skip refused; pending refused; tampered-pointer refused (via fixture-content lookup);
hash-mismatch refused; duplicate refused; and a **4-iteration autonomous loop** `extend → (simulated
reveal+commit advancing durable state) → reload state.json (simulated restart) → extend`, which advanced
**exactly +1 each step (6→7→8→9)**, materialized no bar beyond the current boundary, and recovered its pointer
from `state.json` alone each iteration. **RESTART_RESUME_EXACT = PASS · AUTONOMOUS_ONE_BAR_LOOP = PASS.** No
per-bar human approval is technically required once the loop is wired to `extend_next_bar` and CEO authorizes
the run.

## 7 — P007 / ATOMIC / EMA (§8) — preserved

`engine.py` and `ema.py` are byte-unchanged, so the E103/E104 guarantees carry unmodified:
**ATOMIC_LOCK_WHILE_P007_OPEN = PASS** (HYBRID `run_until_gate` is mechanically unreachable while
`Q4-P007-003` is OPEN; only `step()` advances until a `P007_RESOLUTION` commit) and
**P007_H1_EMA_SEMANTIC_PRESERVED = PASS** (the causal **H1** EMA-50 remains the P007 reference — the Q4 log's
bar-379 bridge note adopting the E103 correction is intact; the M15 `ema.py` helper remains test-only). The
remediation did not weaken either contract.

## 8 — FINDINGS

**BLOCKING: NONE.** The E104 single blocker is fully remediated: the autonomous extension path is fail-closed,
one-bar-only, durable-state-derived, commit-gated, pointer-consistency-checked, tamper/hash-guarded, and
overwrite-protected.

**NONBLOCKING (2):**
1. **Autonomous-wiring requirement.** Safety depends on the autonomous Q4-continuation runtime being wired
   **exclusively** to `extend_next_bar()`; the arbitrary-`N` `materialize()`/`--max-bar` CLI still exists (by
   design, for CEO manual use) and would bulk-expose if an autonomous loop called it directly. The design and
   docstrings make this explicit; the CEO/integrator must ensure the autonomous loop never calls
   `materialize()`/CLI, only `extend_next_bar()`. (Not a defect — the required distinction is correctly built —
   but the operational condition for autonomy.)
2. **Per-extension full-source re-hash + fixture accretion (operational).** Each `extend_next_bar` re-hashes
   the full multi-year source (`hash_file(source_path)` — a disclosed provenance read, no semantic exposure,
   per E103) and writes a new `~2,380-row` fixture; over ~5,500 remaining Q4 bars this is ~5,500 full-file
   hashes and ~5,500 fixture files (disk growth). Purely operational; no causal or scientific impact.
   Optional: prune superseded fixtures or cache the source hash across a run.

(The E104 cosmetic `source_identity.symbol="UNKNOWN"` note is unrelated to this remediation and unchanged.)

## 9 — CONCLUSION

The remediation `7241b17` closes the E104 blocker cleanly and minimally. The autonomous extension is
fail-closed and one-bar-only by construction (no boundary parameter, target derived from durable state),
gated on commit + pointer consistency (verified against fixture content, not just state arithmetic) + fixture
hash + no-overwrite, and I reproduced all of it — plus a restart-safe +1 loop — on synthetic data without ever
touching real bar 380. The engine's ATOMIC-lock and the causal-H1-EMA P007 semantic are preserved. **AI Trader
can now safely continue autonomously from bar 380 through the remainder of Q4, one bar at a time, provided the
autonomous loop is wired exclusively to `extend_next_bar()`** (§8 note 1).

```
RED_TEAM_VERDICT = PASS_WITH_NONBLOCKING_NOTES
SAFE_FOR_AUTONOMOUS_SEQUENTIAL_Q4 = YES (conditional on §8 note 1)
BAR_380_ACCESSED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

Bar 380 not exposed, no real bar-380 materialization, Q4 not resumed, source/MT5/S5/P007/MGMT-004 not modified.
Control returned to CEO.

---

*Red Team · delta review · remediation identity + scope verified · E104 blocker closed · one-bar gate proven
fail-closed on synthetic data · autonomous +1 loop restart-safe · bar 380 not accessed · 63 tests + 12
independent RT checks · LEDGER E105 (prev E104).*
