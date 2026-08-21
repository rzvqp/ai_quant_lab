# VE RANGE V4.4 — Research baseline freeze + V4.4.1 closure report

**Mandate**: `VE-RANGE-V4_4-RESEARCH-BASELINE-CLOSE-001`. **Date**: 2026-08-21. **Division**: Validation Engine (VE).
**CEO Directive**: `AUTHORIZE_VE_RANGE_V4_4_RESEARCH_BASELINE_CLOSE_AND_HANDOFF`. **Constraints honored**:
`V4_4_COMMIT_3bb61cf_FIXED`, `NO_RANGE_RETUNING`, `NO_ALPHA_RESEARCH_BY_VE`, `NO_STRATEGY_DESIGN`, `V4_4_1_CLOSED`,
`MB3_025_048_SEALED`, `BROKER_ORDER_SUBMISSION_DISABLED`, `NO_LIVE`.

This mandate authorizes **freeze/document/preserve/handoff only** — no code touched V4.4, V4.4.1, or any
detector file. No Alpha hypothesis, strategy, or backtest was produced.

Structured against the mandate's own 9 sections, in order.

---

## §1 — Authoritative source chain (independently re-verified)

| Commit | Content | Verified |
|---|---|---|
| `3bb61cf` | V4.4 frozen implementation | exists, `git cat-file -t` |
| `4ed4eb4` | V4.4.1 frozen implementation (T-STALE, params 29/4/3/12) | exists, HEAD of `discovery-mk-matrix-v1`, local=remote ×4 |
| `6adef91` | Red Team implementation audit — `V4_4_1_IMPLEMENTATION_AUDIT_PASS_WITH_NONBLOCKING_NOTES` | exists (branch `statistician-foundation`) |
| `4af8ea9`→`2ad5cab`→`778778d` | F441 fresh-blind protocol precommit → label selection/freeze → predictions frozen before label access | exists, chain order confirmed |
| `8e550ae` | Red Team final fresh-blind validation — `V4_4_1_FRESH_BLIND14_GENERALIZATION_NOT_SUPPORTED` (E96) | exists (branch `statistician-foundation`), full report read in full this mandate, not summarized from memory |

`8e550ae` lives on `statistician-foundation` (Red Team's own audit branch), not `discovery-mk-matrix-v1` — this
is the established multi-branch division structure, not an anomaly. Its full report
(`red_team/policy_reviews/RT-RANGE-V4_4_1-FRESH-BLIND14-VALIDATION-001.md`) was read in full before writing this
document; every number below is reproduced from that source, not from the mandate text alone.

**F441 result** (26 CEO RANGE ground truth, ratified scorer, ×4 ISO-verified chain, `MB3-025→048` sealed,
`FB14`/`MB3-001→024` not reused):

| Metric | V4.4 (`3bb61cf`) | V4.4.1 (`4ed4eb4`) | Gate |
|---|---:|---:|---|
| TP | 15 | 21 | H3 PASS |
| **total FP** | **8** | **16** | **H2 FAIL (HARD)** |
| **directional FP** | **4** | **5** | **H1 FAIL (HARD)** |
| recall | 0.577 | 0.808 | H4 PASS |
| precision | 0.682 | 0.568 | — |
| F1 | 0.625 | 0.667 | — |

**H1 and H2 (both HARD, both pre-registered `4af8ea9` before any run) FAIL → `GENERALIZATION_NOT_SUPPORTED`.**
Under the CEO's prospectively-frozen priority — **false RANGE is more dangerous than missed RANGE** — a
recall/F1 gain cannot compensate a hard-gate failure. Mechanism: T-STALE's diagnosis was correct (it recovers
9 genuine stale-blocked RANGE, recall +0.231) but the cure over-fires — 32 firings, 9 beneficial / **17
harmful** / 6 neutral, doubling false RANGE via RANGE-context over-segmentation (FP 4→11 inside genuine ranges)
and destroying 3 V4.4 true positives via harmful abandonment. **Every one of the 32 firings occurred at
alternation=3 exactly** — the value this program's own calibration (`9116c2b`) classified `FRAGILE` and both
prior Red Team audits flagged as the residual risk. That risk is now **confirmed material on fresh evidence**,
not theoretical.

This report does not re-litigate `8e550ae`'s verdict — it is treated as authoritative per the CEO directive.

---

## §2 — V4.4 research baseline: frozen identity (re-verified directly against the code this mandate, not recalled)

```
RANGE_RESEARCH_BASELINE = V4.4
STATUS = FROZEN_CONSERVATIVE_RESEARCH_BASELINE
```

| Identity | Value |
|---|---|
| Commit | `3bb61cf` |
| `contract_version` | `range-hierarchical-v4.4` |
| `config_id` (recomputed, matches normative constant) | `23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969` |
| Implementation fingerprint | `v4-4-implementation-freeze-2026-08-20` |
| Reason codes | 40 total (29 from V4.3 + 11 new) |
| F441 prediction hash (this batch) | `2830a712…` |

Full parameter registry (21 fields, `ConfigV44`, values as committed at `3bb61cf`, unchanged by this mandate):

`d_macro=29, d_internal=12, n_touch=2, K_reentry=22, N_accept=3, K_struct=2, n_external_swings=2, atr_window=14,
w_atr=0.8, atr_source=ai_trader.structural_observer.vendor_bridge.atr14,
atr_provenance_wheel_sha256=39673910…f8281f4, contract_version=range-hierarchical-v4.4, ER_max=0.5, RND_max=1.0,
ALT_MIN=0.5, MIN_TRAVERSALS=1, W=29, ER_weakening=0.75, RND_weakening=2.0, WEAKENING_MAX_BARS=22,
IOU_CONTINUE=0.5, GAP_MAX=12`.

No semantic change. No new threshold. No new parameter. Rollback identity: this is the exact same `3bb61cf`
already independently rollback-tested during the V4.4 implementation mandate and again during V4.4.1's own
rollback proof (removing V4.4.1 restores V4.4's 470/470 baseline exactly) — no new rollback test was needed or
performed, since nothing about V4.4 itself changed.

---

## §3 — Explicit known behavior

**STRENGTH**: V4.4 is false-RANGE-averse relative to every alternative tested to date (V4.3's weaker gate,
V4.4.1's T-STALE correction) — lowest directional-FP and total-FP profile of the three.

**KNOWN LIMITATION**: V4.4 can miss genuine RANGE structures. Mechanism (independently diagnosed,
`b1dcf92`, and now confirmed again on fresh evidence via V4.4.1's 9 recovered TP): a never-confirmed MACRO
candidate can occupy the single active-MACRO slot indefinitely once V4.4's discrimination gate (T3) correctly
rejects it as directional, with no staleness-based release — blocking a fresh, better-anchored candidate from
ever forming. This is real and reproducible, not a hypothetical edge case.

**CEO's accepted trade-off**: V4.4 is retained **despite** this known limitation because, under the
prospectively-frozen error-cost priority (**false RANGE > missed RANGE**), the cost of the false-RANGE
alternative (V4.4.1, confirmed on fresh blind evidence to double false RANGE and add a directional FP) is
judged higher than the cost of missing some genuine RANGE. This is a deliberate, evidence-based trade-off, not
an oversight.

**V4.4 does NOT perfectly reproduce CEO semantics.** It is a conservative research baseline with a documented
directional bias (under-detection of RANGE, particularly of the stale-candidate-blocked kind), not a validated
ground-truth reproduction. Epistemic status is exactly:

```
V4_4_FROZEN_CONSERVATIVE_RESEARCH_BASELINE
```
NOT `FULLY_VALIDATED`, NOT `GENERALIZATION_PASS`, NOT `LIVE_READY`. This mandate does not retroactively change
V4.4's own historical blind-validation verdict (its own prior fresh-blind result stands as it was recorded);
it only changes V4.4's *program status* — from "candidate under active development" to "frozen baseline
selected by CEO cost-priority decision."

---

## §4 — V4.4.1 closure

```
V4_4_1_ACTIVE_DEVELOPMENT_CLOSED
V4_4_1_NOT_SUPPORTED_ON_F441
```

**Nothing was deleted.** All V4.4.1 artifacts remain in git history and on disk, preserved for reproducibility:

| Artifact | Location |
|---|---|
| Traversal diagnostic | `ve_n1_replay/VE_RANGE_V4_4_TRAVERSAL_DIAGNOSTIC.md` (`b1dcf92`) |
| T-STALE design | `ve_n1_replay/VE_RANGE_V4_4_1_STALE_CANDIDATE_DESIGN.md` (`9aba9b7`) |
| Design freeze | `ve_n1_replay/VE_RANGE_V4_4_1_T_STALE_DESIGN_FREEZE.md` (`e2b65bf`) |
| Calibration protocol + results | `ve_n1_replay/VE_RANGE_V4_4_1_STALE_CALIBRATION_PROTOCOL.md` + `_RESULTS.md` (`8605cb2`, `9116c2b`) |
| Implementation | `ve_n1_replay/ve_n1_replay/range_semantic_v4_4_1.py` + `range_engine_v4_4_1.py` (`4ed4eb4`) |
| Implementation report + test suite | `ve_n1_replay/VE_RANGE_V4_4_1_STALE_IMPLEMENTATION_REPORT.md` + `ve_n1_replay/tests/test_v4_4_1_stale.py` (`4ed4eb4`) |
| Red Team design audit | `eeb082e` (branch `discovery-mk-matrix-v1`) |
| Red Team implementation audit | `6adef91` (branch `statistician-foundation`) |
| Red Team fresh-blind validation | `red_team/policy_reviews/RT-RANGE-V4_4_1-FRESH-BLIND14-VALIDATION-001.md` (`8e550ae`) |

No further T-STALE tuning without a new CEO mandate. Red Team's own report (§14) recorded three CEO options —
hold V4.4 (recommended, chosen), authorize a future separate re-examination of T-STALE's firing stringency on
evidence never used here, or abandon T-STALE outright. This mandate implements the first; the second remains
available to a future, separately-authorized mandate; this report takes no position on which.

---

## §5 — Research-only boundary

The V4.4 freeze authorizes use as **RESEARCH CONTEXT / FEATURE SOURCE ONLY**. It does NOT authorize Strategy
Catalog, AI Trader, LIVE_SHADOW, broker, orders, or live trading. `BROKER_ORDER_SUBMISSION` remains DISABLED.
This boundary is restated explicitly in the Alpha handoff artifact (§7 below) as a forbidden-interpretation
item, not left implicit.

---

## §6 — Evidence protection

| Evidence class | Status |
|---|---|
| FB14 (13,511 bars, `dfebe8f`/E8) | Consumed detector-validation evidence — do not reuse for Alpha tuning |
| F441 (14 windows, `8e550ae`/E96) | Consumed detector-validation evidence — do not reuse for Alpha tuning |
| MB3-001→024 | Diagnostic history — informational only |
| MB3-025→048 | **SEALED / UNTOUCHED** throughout this entire RANGE program, confirmed again this mandate |

Alpha Discovery must not use CEO labels from FB14/F441 to tune Alpha strategies — those labels validated the
*detector*, not any downstream trading hypothesis, and reusing them for Alpha-side tuning would contaminate
Alpha's own future validation evidence. Restated explicitly in the handoff.

---

## §7 — Alpha handoff artifact

Produced: [`RANGE_V4_4_ALPHA_DISCOVERY_HANDOFF.md`](RANGE_V4_4_ALPHA_DISCOVERY_HANDOFF.md) — canonical detector
identity, import/API path (source-only, not in any built wheel — see handoff §2), config identity, causal
input requirements, output schema (21-field `RangeSemanticResultV44`), state semantics, permitted RANGE
consumption patterns for Alpha research, known limitations, forbidden interpretations, evidence exclusions,
rollback reference. Written to let Alpha Discovery use V4.4 without reopening detector design.

---

## §8 — Project state update

`PROJECT_STATE.md` updated (prepend-only) to record:
```
RANGE ACTIVE DEVELOPMENT: CLOSED
RANGE RESEARCH BASELINE: V4.4 / 3bb61cf
RANGE STATUS: FROZEN_CONSERVATIVE_RESEARCH_BASELINE
V4.4.1: NOT_SUPPORTED / ACTIVE DEVELOPMENT CLOSED
NEXT PROGRAM OWNER: ALPHA DISCOVERY DEPARTMENT
```
Alpha Discovery itself is recorded only as *next owner* — not marked started or completed by VE, per mandate
§8's explicit instruction.

---

## §9 — Final VE status

```
RANGE_V4_4_RESEARCH_BASELINE_FROZEN
V4_4_1_ACTIVE_DEVELOPMENT_CLOSED
RANGE_ALPHA_HANDOFF_READY
```

No Alpha hypothesis, strategy, or backtest was produced by VE. No RANGE code was modified. VE stops here per
mandate §9.
