# RED TEAM — RANGE V4.4 FOCUSED DESIGN AUDIT
### RT-RANGE-V4_4-DESIGN-AUDIT-001 · Auditor: Red Team · 2026-08-20

Independent focused audit of the RANGE V4.4 design before implementation or freeze. Not a redesign, not an
implementation, no threshold selection. Targets: VE design `236e8e7` + convergence package `f241698`, against
diagnostic `071fbd7` and my audit `3be88a1`.

---

## 0 — DISPOSITION

```
V4_4_DESIGN_AUDIT_PASS_WITH_NONBLOCKING_NOTES
V4_4_DESIGN_FREEZE_AUTHORIZED_FOR_CEO_DECISION
```

The V4.4 design is **coherent, causal, deterministic, complete as a mechanism, and non-overfit.** It correctly
rejects the falsified naive drift gate, keeps the directional-discrimination fix separate from the
over-segmentation fix, bounds every new state, and — most importantly — is **honest about what it has not
proven**: it presents its central FP-reduction gate as a falsifiable hypothesis whose true-positive
preservation is *not yet empirically cleared*, and defers every uncertain parameter to a pre-registered
calibration mandate on untouched evidence rather than fishing a value. No fatal flaw, internal contradiction,
non-deterministic rule, unsatisfiable invariant, or MB3-fitted constant was found.

The freeze this authorizes locks the **mechanism/specification** so the next steps can proceed; it does **not**
authorize implementation, parameter selection, or any trust in the detector's numbers — those follow the
sequence in §3 below. The non-blocking notes are preconditions on that sequence, not design defects.

---

## 1 — PROVENANCE (mandate §1) — PASS

| check | result |
|---|---|
| all 4 commits exist (`071fbd7`/`3be88a1`/`236e8e7`/`f241698`) | PASS |
| local=remote ×4 mirrors (design branch `discovery-mk-matrix-v1` @ `f241698`) | PASS |
| V4.3 reference code/config untouched (`bc6b9dc..f241698` diff on `ve_n1_replay/ve_n1_replay/`) | PASS — empty |
| V4.4 work is design-only (two `.md` docs, zero code) | PASS |
| MB3-025→048 untouched/sealed | PASS — the design references only MB3-007/015/020/021/024 (within 001-024, diagnostic, zero-validation-weight); every MB3-025→048 mention is a "sealed / not accessed" statement, no semantic content; no escrow/payload/label opened by the design or by this audit |

---

## 2 — AUDIT MATRIX (mandate §19)

| # | Audit area | VE design | RT finding | PASS/AMEND/BLOCK | Material note |
|---|---|---|---|---|---|
| 1 | State machine | `CANDIDATE→FORMING→CONFIRMED→WEAKENING→TERMINATED`; full transition table T1–T9 + T-KILL (convergence §3) | Every legal transition explicit; priorities deterministic (T-KILL=0 highest; T4>T5; AND-for-recovery/OR-for-termination); WEAKENING cannot persist (T9 `WEAKENING_MAX_BARS`); recovery uses the *same* gates as confirmation (no weaker path); no reachable permanent sink | **PASS** | A persistently-directional `FORMING` candidate has no explicit abandon-path beyond `ZONES_DEGENERATE`/window-end — it lingers as `FORMING` (correctly never `CONFIRMED`); worth an implementation clarification, not a defect |
| 2 | Directional gate | 4 signals over a bounded window: ER (hard), traversal (hard), RND (hard), alternation (supporting); drift demoted to diagnostic | ER is a genuinely different construction from the falsified whole-life `normalized_drift` (self-normalized, raw path length, no ATR); the falsified naive gate is **not** reintroduced; alternation stays supporting (matches VE's own self-falsification); all signals causal/prefix-computable/O(1); not a disguised single threshold (ER & RND share the net-displacement numerator but differ in denominator; traversal independent) | **PASS** | ER/RND sharing the numerator means a low-net-displacement structure passes both trivially — correct for ranges, and the source of the disclosed violent-zigzag risk (note 4 below) |
| 3 | Confirmation timing | Evidence-gated, not time-gated; `RANGE_CANDIDATE_PRESENT` distinguishes RANGE-PRESENT from FIRST-CONFIRMED; new acceptance test (convergence §5) | The acceptance test — identical price-path shape must confirm at the **same relative bar-since-start regardless of window length** — directly operationalizes "recognition must not depend on window length" as a falsifiable regression; addresses `MORE_TIME_TO_FIRE` at the mechanism level | **PASS** | "Range already underway at window start" is honestly disclosed as **not solved** (needs cross-window context, out of scope for a per-window detector) — a real residual limitation, correctly out-of-scope |
| 4 | WEAKENING | Entry T4 (excursion, reuses unchanged `Excursion`) / T5 (trailing degradation); recovery T6/T7; termination T8/T9 | Bounded (T9); does not preserve stale RANGE through a directional shift (invariant "no stale RANGE after termination"); interaction with accepted/failed breakout, displacement, migration all specified; dual-trigger priority resolved deterministically | **PASS** | `ER_weakening`/`RND_weakening`/`WEAKENING_MAX_BARS` UNRESOLVED — fail-closed (too-short bound → over-termination → under-recall, never unsafe) |
| 5 | Episode identity | CONTINUATION/MERGE/REPLACEMENT (priority MERGE>CONTINUATION>REPLACEMENT); NESTING unchanged | Kept **separate** from the directional gate (§4), exactly as my audit required (a directional gate "would not fix these and could over-suppress genuine ranges"); over-merge bounded by forced REPLACEMENT after `BREAKOUT_ACCEPTED` | **PASS** | `IOU_CONTINUE`/`GAP_MAX` UNRESOLVED; over-merge risk disclosed with fail-closed + named test |
| 6 | Parameters | Full registry; ER_max=0.5 / RND_max=1.0 / ALT_MIN=0.5 DERIVED; 7 UNRESOLVED; V4.3 gates RATIFIED | No parameter carries `CHOSEN_BECAUSE_MB3_SCORE_IMPROVED`; RND_max=1.0 near-tautological (strong), ER_max=0.5 a principled scale-midpoint (VE flags it as a candidate for calibration); no hidden constants; `config_id` correctly **not** computed | **PASS** | Design is **not runnable** until the 7 UNRESOLVED params are resolved + the 2 anchors validated via a pre-registered calibration mandate on untouched evidence (note 1) |
| 7 | TP preservation | Matrix per correction; honest disclosure | **The central concern, correctly handled:** the ER/traversal/RND gate's TP-preservation is a *construction hypothesis* (bounded-window ≠ the whole-life measure that overlapped), explicitly **not** empirically cleared (cannot be, on MB3, without fishing) | **PASS** (design) | Note 2: the core claim — reduce the 30 directional FP **without** the naive gate's 13/23 TP loss — is UNVALIDATED and must be proven on a fresh independent blind batch (never MB3) before the detector is trusted |
| 8 | Open risks | 3-risk register (slow-drift, zigzag, over-merge) | Each is documented, bounded, fail-closed, has a named test, and cannot silently invalidate the main claim — meeting the mandate's own "acceptable known risk" bar | **PASS** | None blocks freeze; note 4 |
| 9 | Adversarial suite | 20 scenarios with chronology/events/forbidden/rule | Covers ranges/noisy/drifting/channels/trends/stair-step/breakout/failed-breakout/displacement/migration/one-sided-touch/truncation/consecutive/long-range-rotations; no new failure mode from my audit → no scenario added (correct, per "do not inflate") | **PASS** | Suite is a specification; executable after params resolved (e.g. #20 depends on `W`) |
| 10 | Causality/determinism | No-lookahead, prefix/chunk/snapshot invariance, deterministic reason-code priority, no contradictory terminal events, bounded memory | All new computations causal (≤t) and O(1)/bounded-window; priority order prevents simultaneous contradictory terminals; carries over V4.3's invariants in kind | **PASS** | — |
| 11 | Snapshot/versioning | contract `range-hierarchical-v4.4`; config_id after params; new snapshot schema; 11 additive reason codes; fingerprint **procedure** | V4.4 cannot silently restore V4.3 state (fail-closed across the boundary); implementation-fingerprint is a computed-after-implementation procedure, **not** a faked placeholder (matches mandate §15); identity-compatibility statement explicit | **PASS** | — |
| 12 | Implementation readiness | Files/fields/functions/transition-order/snapshot-policy/tests/rollback specified | Another engineer could implement the **mechanism** from the spec without reopening research | **PASS** (mechanism) | A **runnable, validated** detector additionally requires the pre-registered calibration mandate (params) then blind validation (TP-preservation) — a planned next step, not "reopening research" (note 1/2) |

**No area is BLOCK. No area requires AMENDMENT.** Every open item is a correctly-deferred precondition, not a
design defect. The convergence package (`f241698`) resolved the three under-specified details its own re-review
found (dual-WEAKENING interaction, episode-identity priority, fingerprint procedure) — I confirm all three are
now deterministic and complete.

## 3 — NON-BLOCKING NOTES (preconditions on the sequence, not defects)

1. **Parameter resolution before running.** Seven `UNRESOLVED_PARAMETER`s (`W`, `MIN_TRAVERSALS` exact,
   `ER_weakening`, `RND_weakening`, `WEAKENING_MAX_BARS`, `IOU_CONTINUE`, `GAP_MAX`) and the two principled
   anchors (`ER_max`, `RND_max`) must be resolved/validated via a **pre-registered calibration mandate on
   evidence never used to derive them** (never MB3-001→024). `config_id` is correctly uncomputable until then.
   The *code* can be implemented; a *runnable/trusted* config cannot.
2. **TP-preservation is unvalidated by design.** The design's core value — fixing the 30 directional FP
   without the naive gate's 13/23 TP loss — is a falsifiable hypothesis, not a demonstrated result. It **must**
   be validated on a fresh independent blind batch (never MB3) before the detector is trusted. This is the same
   discipline that caught the F5-MACRO-leak; the design honestly claims only a hypothesis.
3. **Two disclosed residual limitations** — a range already underway at window start (unfixable per-window),
   and a violent zero-net-displacement zigzag that could pass the gates — are out-of-scope, fail-closed, and
   documented. Acceptable known risks, not blockers.
4. **Minor implementation clarification** — specify the intended handling of a `FORMING` candidate that is
   persistently directional but whose zones never degenerate (currently lingers as `FORMING`, correctly never
   confirmed).

## 4 — REQUIRED SEQUENCE (unchanged from VE's own plan; Red Team endorses)

```
CEO design-freeze decision (this audit authorizes it)
  → pre-registered calibration mandate (resolve UNRESOLVED params + validate anchors on untouched evidence)
  → implement additive range_semantic_v4_4.py / range_engine_v4_4.py (V4.3 byte-untouched)
  → Red Team static + construction-only audit
  → fresh independent blind batch validation (never MB3) — where TP-preservation is finally proven or refuted
  → CEO promotion decision
```

No step may be skipped; in particular, freeze does not authorize implementation, and implementation does not
authorize trust in the numbers until the fresh-blind-batch stage.

## 5 — SCOPE / PROHIBITIONS

Focused design audit only. No redesign, no implementation, no threshold selection, no parameter values, no
blind execution, no Strategy Catalog/Alpha/AI Trader/LIVE_SHADOW/broker. `MB3-025→048` remain
`SEALED_FUTURE_CONFIRMATION_BATCH` — not accessed by the design or this audit. `MB3-001→024` carry
`ZERO_VALIDATION_WEIGHT` (diagnostic only). V4.3 code/config unmodified; all changes confined to `red_team/`.

---

*Red Team · design-doc audit only; escrow/labels/detector unmodified · changes only in `red_team/` · MB3-025→048 sealed · LEDGER E91 (prev E90).*
