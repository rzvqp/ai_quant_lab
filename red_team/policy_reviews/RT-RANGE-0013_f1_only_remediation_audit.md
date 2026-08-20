# RED TEAM — RANGE V4 F1-ONLY REMEDIATION AUDIT / FINAL PRE-BLIND FREEZE GATE
### RT-RANGE-0013 · Auditor: Red Team · 2026-08-20 · audited build `bc6b9dc`

---

## 0 — VERDICT

```
RANGE_V4_F1_ONLY_REMEDIATION_AUDIT_PASS
MACRO_INDEPENDENT_BLIND_PREPARATION_AUTHORIZED = TRUE

F5_PRODUCTION_BEHAVIOR_DEFERRED = TRUE          (DEFERRED_RESEARCH_ONLY_NON_BLOCKING)
F1_OHLC_BYTE_IDENTITY = TRUE
F1_ONLY_PATCHED_PREDICTIONS_MATCH_FREEZE = TRUE
MACRO_REAL_BAR_BEHAVIORAL_DIFFERENCES = 0
MACRO frozen score restored: 62/88 · recall 0.705 · precision 0.534 · F1 0.608 · IoU-median 0.439
INDEPENDENT_SEMANTIC_BLIND = FALSE · VALIDATION_WEIGHT = ZERO
WHEEL/STRATEGY-CATALOG/ALPHA/AI-TRADER/LIVE_SHADOW/BROKER = NOT AUTHORIZED
```

`bc6b9dc` (branch `discovery-mk-matrix-v1`, parent `69af414`, i.e. the rejected F1+F5 build with F5 reverted
on top) **correctly preserves the validated F1 fix and fully removes the F5→MACRO behavioral leak.** The
frozen pre-F5 MACRO behavior is restored **exactly** on real bars. All commits verified from Git with
`local=remote` on all four mirrors; `bc6b9dc` audited directly. Nothing modified to force any result; changes
only in `red_team/`. **This PASS authorizes only preparation/sealing of the new independent MACRO blind batch
— not the final RANGE semantic PASS, and not Wheel/Alpha/AI-Trader/broker.**

---

## Diff classification (82f27c0 → bc6b9dc), independently verified

| production hunk | classification |
|---|---|
| `schemas.py` (+129) | **F1** validator — **byte-identical to the RT-0012-audited `69af414`** (0-line diff) |
| `inference.py` (+36) | **F1 integration** + identity: `FROZEN_PROTOTYPE_COMMIT="f224e7d+F1"`, detector hash `098fa144`, fingerprint `f1-only-f5-deferred-2026-08-20` |
| `range_semantic_v4_3.py` (net +37) | **F5 revert** (line back to pre-F5 `abs(price-boundary) <= self._cfg.tol_cluster`) + **implementation fingerprint** + **snapshot/restore gating** |
| `scoring.py` (+6) | **scoring identity-only** — `prototype_commit → f224e7d+F1` + fingerprint check; **no scoring logic** |
| tests/docs | F1 tests, new non-vacuous multi-ATR MACRO-identity test, F5 test suite deleted, reports, PROJECT_STATE |

AST executable-code diff (comments/docstrings stripped) of the detector, pre-F5 vs `bc6b9dc`: **exactly 4
changes** — the fingerprint constant, its `__all__` entry, and the two snapshot/restore lines. **The entire
`observe()` / candidate-formation path (including the boundary-retest line) is executable-identical to
pre-F5.** No unauthorized production behavior change.

---

## GATE A — F5 must actually be gone · **PASS** → `F5_PRODUCTION_BEHAVIOR_DEFERRED = TRUE`

The rejected F5 line (`... <= self._cfg.tol_cluster * atr_ref`) is **absent**; the source is the pre-F5
`82f27c0` form. Not accepted on comments alone: (a) the AST executable-code diff shows no change on the
boundary-retest path; (b) running the `bc6b9dc` detector on the 48 real windows reproduces the pre-F5 freeze
`46a9576` **fully, 48/48, including structure-ids** (§Gate C/D) — so the INTERNAL boundary-retest behavior is
executably restored to pre-F5. F5 stays `DEFERRED_RESEARCH_ONLY_NON_BLOCKING`. Not repaired by Red Team.

## GATE B — F1 must remain exactly valid · **PASS** → `F1_OHLC_BYTE_IDENTITY = TRUE`

`schemas.py` is **byte-identical** to the F1 validator fully audited in RT-RANGE-0012. Independently
re-confirmed on the real corpus with the `bc6b9dc` validator:
- `min_tick=0.01` (XAUUSD, from symbol metadata); `epsilon = min_tick/2 = 0.005`; unknown symbol →
  `UNKNOWN_SYMBOL_MIN_TICK` fail-closed.
- Value-vs-shifted-boundary: `high+eps` tolerated / `+1 ULP` rejected; `low-eps` tolerated / `-1 ULP` rejected.
- **13/13,824 tolerated bars, all on `close`, 9 above high / 4 below low, per length 96:1 / 288:6 / 480:6.**
- `INPUT_OHLC_SUBTICK_TOLERATED` remains a quality event on a separate `input_quality_events` channel, outside
  the 29 reason codes; **OHLC values are byte-identical after validation** (never modified).

## GATE C — decisive F1-only freeze match (real ATR) · **PASS** → `F1_ONLY_PATCHED_PREDICTIONS_MATCH_FREEZE = TRUE`

Executed the `bc6b9dc` candidate (F1 validator + F5-reverted detector, engine path with **real ATR**) on the
48 real sealed windows. Full semantic projection (records + macro_structures + internal_structures, including
structure-ids) is **identical to the frozen pre-F5 baseline `46a9576` on 48/48 windows**; projection hash
`63ef7551…` equal. Quality events are a separate channel and do not enter the semantic identity. No synthetic
fixtures, no `atr=1.0` used as the identity proof.

## GATE D — MACRO behavioral identity on real bars · **PASS** → `MACRO_REAL_BAR_BEHAVIORAL_DIFFERENCES = 0`

Same comparison class that exposed the RT-0012 leak, `bc6b9dc` vs verified pre-F5 baseline, 48 real windows,
real ATR, compared independently of structure-id renumbering (start/confirm/end/boundaries/reason/role/event
kinds/timing/promotions/sweeps/breakouts/reversals):

| | rejected F1+F5 (`69af414`) | **`bc6b9dc`** |
|---|---|---|
| MACRO geometry diffs (excl id) | 12 / 48 | **0 / 48** |
| MACRO event diffs (excl id) | 12 / 48 | **0 / 48** |
| MACRO sweeps / breakouts / reversals / promotions | 59 / 93 / 6 / 89 | **67 / 96 / 7 / 90** (= freeze) |

Zero differences — including full structure-id identity, so even the shared-counter renumbering is gone.

## GATE E — frozen MACRO score · **PASS**

Audited scorer on the `bc6b9dc` real-bar predictions (same labels/isolation as before):
**MACRO 62/88 · recall 0.705 · precision 0.534 · F1 0.608 · IoU-median 0.439.** Exactly the frozen baseline;
does **not** reproduce the rejected `58/88 (0.659)`. INTERNAL 1/12 (unchanged, RESEARCH_ONLY, non-blocking).

## GATE F — implementation identity / snapshot · **PASS**

Fingerprint `"f1-only-f5-deferred-2026-08-20"` — an honest label of the actual behavior (F1-only, F5 deferred;
neither the bare `f224e7d` nor the rejected `f1-f5-conformance`). `config_id` (`24f72a60…`) and
`contract_version` (`range-hierarchical-v4.3`) unchanged. Refusal matrix verified:

```
correct F1-only snapshot            → accepted
bare pre-identity (no fingerprint)  → REFUSED
rejected F1+F5 fingerprint          → REFUSED   (no silent compatibility with rejected state)
corrupt fingerprint                 → REFUSED
wrong config_id                     → REFUSED
wrong contract_version              → REFUSED
```

## GATE G — scorer integrity · **PASS**

`scoring.py` changes are identity/version gates only (`prototype_commit → f224e7d+F1` + fingerprint check,
which also refuses the rejected `f1-f5-conformance` tag). **No** scoring-formula, denominator, threshold,
label-interpretation, or metric change.

## GATE H — tests / static / negative · **PASS**

Active suites **99/99 pass**; `mypy --strict` clean on all four touched production files; the F5 test suite is
**deleted** (F5 deferred); construction_reproduction (pinned to `f224e7d`) **refuses** the `bc6b9dc` detector
fail-closed with the correct byte-identity error (historical pin intact, not masking a regression). VE's **new
multi-ATR regression** is non-vacuous: it byte-compares the guard line to pre-F5 source, asserts no `atr_ref`
on that line, and exercises the retest guard at **five distinct ATR values (0.65/1.0/1.85/3.2/10.0)** spanning
the real median — a test the deferred F5, if present, would fail. This does **not** repeat the RT-0012
`atr=1.0`-only mistake; the decisive real-bar/real-ATR confirmation was performed by Red Team (Gates C–E).

---

## MATRIX

| Gate | Verdict |
|---|---|
| Sources & local=remote (4 mirrors) | PASS |
| Diff classification / no unauthorized change | PASS |
| A — F5 production behavior gone | PASS |
| B — F1 exactly valid + OHLC byte identity | PASS |
| C — F1-only freeze match (real ATR) | PASS |
| D — MACRO real-bar behavioral differences = 0 | PASS |
| E — frozen MACRO score 62/88 recall 0.705 | PASS |
| F — implementation identity / snapshot refusal matrix | PASS |
| G — scorer integrity (identity-only) | PASS |
| H — tests / mypy / construction pin / non-vacuous multi-ATR | PASS |

## CONSOLIDATED FINDINGS

- **No material defect.** F5's MACRO leak is fully removed; F1 is preserved exactly; the frozen MACRO baseline
  is restored bit-for-bit on real bars.
- **Non-blocking (representational):** the detector's *file hash* differs from pre-F5 (`098fa144` vs
  `2aba333c`) because the fingerprint constant + snapshot-gating lines were added. This is **purely
  representational and score/semantics-invariant** — proven by the 48/48 full real-bar semantic identity
  (Gate C/D) and the identical 62/88 score (Gate E). The mandate explicitly permits such a representational
  identity change. It correctly forces construction_reproduction (pinned to `f224e7d`) to treat `bc6b9dc` as a
  new artifact and refuse it.
- **INTERNAL** remains `RESEARCH_ONLY_NOT_VALIDATED`, 1/12, non-blocking — F5 deferred, no INTERNAL change made.

## SCOPE

`INDEPENDENT_SEMANTIC_BLIND = FALSE`, `VALIDATION_WEIGHT = ZERO`. The 48 windows were used only for
reproduction/regression/identity. **A PASS authorizes ONLY preparation and sealing of the new independent
MACRO blind batch** — it is not the final RANGE semantic/blind PASS and does not authorize Wheel, Strategy
Catalog, Alpha, AI Trader, LIVE_SHADOW, or broker execution. Red Team does not prepare the blind batch under
this mandate. **Next owner: Statistician / designated blind-batch preparation role, under a separate mandate.**

---

*Red Team · VE/Statistician/scorer/escrow/labels/ve_brain unmodified · changes only in `red_team/` · LEDGER E88 (prev E87).*
