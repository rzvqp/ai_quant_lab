# RED TEAM — RANGE V4.4.1 STALE-CANDIDATE FOCUSED DESIGN AUDIT
### RT-RANGE-V4_4_1-STALE-DESIGN-AUDIT-001 · Auditor: Red Team · 2026-08-21

Focused adversarial audit of the **T-STALE** stale-candidate correction design (`9aba9b7`,
`VE_RANGE_V4_4_1_STALE_CANDIDATE_DESIGN.md`), the VE response to the FB14 TP-preservation failure
(RT-RANGE-V4_4-FRESH-BLIND14-VALIDATION-001, E93). Design-only. No redesign, no calibration, no
implementation, no fresh-blind run, no MB3-025→048 access.

---

## 0 — VERDICTS

```
V4_4_1_STALE_DESIGN_AUDIT_PASS_WITH_NONBLOCKING_NOTES
V4_4_1_DESIGN_FREEZE_AND_CALIBRATION_AUTHORIZED_FOR_CEO_DECISION
```

The T-STALE design is coherent, minimal, lifecycle-local, and **calibration-ready**. It correctly targets the
root cause diagnosed in `b1dcf92` (a never-confirmed MACRO candidate permanently occupying the single active
slot, of which `INSUFFICIENT_TRAVERSAL` is a downstream symptom) rather than the traversal gate that merely
reported the symptom. It preserves the V4.4 directional gains by construction, its anti-churn safeguard is
structural (not a tuned cooldown), it protects slow/quiet ranges, and every numeric item is correctly left
UNRESOLVED. Four non-blocking notes (§8) — all self-disclosed by VE — are recorded for the calibration mandate;
none blocks the freeze. No churn risk and no slow-range risk was found that would trip `FAIL_CLOSED_ON_CHURN_
OR_SLOW_RANGE_RISK`.

Not authorized by anything here: implementation, calibration, parameter selection, fresh-blind validation,
Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, live trading, V4.4 promotion.

---

## 1 — PROVENANCE & INTEGRITY (§5/§6)

| gate | result |
|---|---|
| commits exist: diagnostic `b1dcf92`, design `9aba9b7`, FB14 verdict `dfebe8f` | PASS |
| ancestry `3bb61cf`(V4.4 impl) → `b1dcf92`(traversal diag) → `9aba9b7`(stale design); `9aba9b7`=HEAD | PASS |
| `9aba9b7` local = remote ×4 (alpha1/discovery/lab/trader), branch discovery-mk-matrix-v1 | PASS |
| design is **docs-only**: `9aba9b7` touches exactly `VE_RANGE_V4_4_1_STALE_CANDIDATE_DESIGN.md` (+ diag `b1dcf92`) — no `.py` change | PASS |
| V4.4 detector byte-untouched: `range_semantic_v4_4.py` blob `833aedfd`, `range_engine_v4_4.py` blob `1371444c` identical to `3bb61cf` | PASS |
| no parameter chosen/ranked/swept in either doc; FB14 = DIAGNOSTIC_ONLY; MB3-025→048 sealed | PASS |
| MB3 references in both docs = only `MB3-001`/`MB3-025` boundary markers in "→024"/"→048" preservation phrases — zero individual sealed-window semantics | PASS |

## 2 — ROOT-CAUSE CONFIRMATION (§7) — the design targets the correct defect

The diagnostic `b1dcf92` (474 lines) is re-verified as the foundation. My own FB14 audit (E93) attributed the
3 lost TP to `INSUFFICIENT_TRAVERSAL` at the traversal gate. VE's diagnostic goes one layer deeper and I
**confirm** it: in each lost-TP span a **single never-confirmed candidate persists throughout**, anchored to a
**stale boundary with 0.000 price-IoU vs the CEO true zone** (FB14-003 id=2 `[1687,1720]` vs CEO `[1724,1742]`;
FB14-012 id=7 `[2514,2526]` vs CEO `[2474,2506]`), while **38 and 66 genuine alternating swings are detected
and rejected** by `offer_swing`. The single-active-MACRO slot is thus blocked; traversal never fails because a
correctly-anchored fresh candidate is never allowed to form and be measured. **`INSUFFICIENT_TRAVERSAL` is a
symptom; the stale-slot occupancy is the cause.** Fixing traversal (my E93 tentative next-step) would have
loosened a working directional gate to compensate for an unrelated lifecycle defect — the design correctly
rejects that path. **ROOT_CAUSE_CONFIRMED.**

## 3 — MECHANISM AUDIT (17 areas, all independently checked)

| # | area | finding | verdict |
|---|---|---|---|
| 1 | provenance / design-only | §1 | PASS |
| 2 | root cause targeted | stale-slot, not traversal (§2) | PASS |
| 3 | scope lifecycle-local (§4) | touches only pre-confirmation candidate lifecycle; ER/RND/traversal/WEAKENING/`offer_swing`/INTERNAL/scorer untouched | PASS |
| 4 | staleness semantics (§5 design) | SEMANTIC = rejected + **alternating** swings; NOT age/timeout, NOT touch-scarcity, NOT price-distance-alone; age is a gating floor only | PASS |
| 5 | anti-churn (§10) | the alternation requirement **is** the safeguard: one-directional trends produce one-sided rejections → never qualify → no reform loop; no tuned cooldown introduced | ANTI_CHURN_SUPPORTED |
| 6 | slow-range protection (§6 design) | accepted touches never count as staleness evidence; silence/quiet never triggers; scenarios 1/2/3/9/12/14 protected | PASS |
| 7 | next-bar replacement (§9, decision B) | **verified in code**: `_offer_swing_everywhere` runs before `_step_macro` in `observe()`, so the triggering swing is offered-and-consumed before T-STALE fires — no double-use, no lookahead; matches every existing slot-freeing path | NEXT_BAR_REPLACEMENT_VALID |
| 8 | directional protection (§12) | a post-T-STALE candidate must independently pass the **unchanged** `_evaluate_macro_formation` (ER/traversal/RND/duration/touch); "changes WHO is evaluated, never HOW" — no bypass path | DIRECTIONAL_PROTECTION_PRESERVED |
| 9 | traversal frozen (§11) | `MIN_TRAVERSALS`/`W`/band-thirds/definition untouched; fix does not make a bad candidate confirm easier | PASS |
| 10 | ER/RND frozen (§12) | thresholds + semantics unchanged, no bypass | PASS |
| 11 | insertion point (§8) | **verified in code**: inserts in `_step_macro`'s `zones is None` (pre-confirmed) branch, after T-KILL, before T2/T3; disjoint from WEAKENING via `reached_confirmed` | PASS |
| 12 | reuse of kill + episode-identity (§8) | **verified in code**: `_kill_macro` (609) already calls `_record_macro_termination_for_episode_identity` (645); T-STALE reuses both — no new episode-identity rule | EPISODE_IDENTITY_REUSE_VALID |
| 13 | state minimality (§7 design) | exactly ONE new bounded deque (rejected-touch records); zone-overlap%/ATR-distance/age-field/running-counters explicitly rejected as unnecessary | PASS |
| 14 | snapshot / versioning (§16) | new `v441_*` field pair, `ConfigV441.config_id()` (same sha formula), `REASONS_V441` = 41 additive/unrenumbered, `contract_version="range-hierarchical-v4.4.1"`, fail-closed cross-version restore via existing mechanism | PASS |
| 15 | parameter inventory (§14) | 4 params, **none chosen**: window-length (RATIFIED_REUSE hypothesis W=29), min-rejection-count (CALIBRATED), min-alternation-count (DERIVED-floor candidate), min-candidate-age (DERIVED candidate); no hidden 5th | ALL UNRESOLVED_PARAMETER |
| 16 | self-falsification (§13) | 16 scenarios; abandonment expected only in 8/15/16, protected in 1-7/9/11-14; no counterexample reintroduces directional false-accept or unbounded churn; weak points disclosed | PASS |
| 17 | test plan (§17) | STALE-1..10 (reachability proven not asserted; slow-range regression; trend no-churn; snapshot at/before/after; prefix/chunk; INTERNAL byte-parity) **plus** a mutation test proving the alternation requirement is load-bearing | PASS |

**17/17 PASS. 0 amendment-required, 0 blocking.**

## 4 — DIRECTIONAL-GAIN PRESERVATION (mandate PRESERVE_V4_4_DIRECTIONAL_GAINS)

The E93 gains (directional FP 13→7, over-seg FP 6→3, precision 0.441→0.545) live entirely in
`_evaluate_macro_formation` (ER/traversal/RND). T-STALE never enters that function — it only frees the single
slot so a fresh candidate can *reach* it. On a genuine continuing trend/channel the freed slot's next occupant
still fails T3 exactly as today. There is **no code path by which T-STALE causes a directional structure to
confirm**. Preservation is structural, not empirical-hopeful. **PRESERVED.**

## 5 — CHURN / SLOW-RANGE FAIL-CLOSED CHECK (mandate FAIL_CLOSED_ON_CHURN_OR_SLOW_RANGE_RISK)

- **Churn:** abandonment requires two-sided *alternating* rejected evidence. A trend's rejections are one-sided
  → the threshold is never met → the stale candidate is not repeatedly killed/reformed (it simply stays, which
  costs nothing during a genuine trend since no real RANGE TP exists there). Bounded by construction; STALE-4 +
  the mutation test enforce it. **No churn risk found.**
- **Slow range:** a slow/quiet genuine range accumulates *accepted* touches, which are explicitly excluded from
  staleness evidence; it is never abandoned (scenarios 1/2/3/9/12/14; STALE-3). **No slow-range risk found.**

Neither fail-closed trip condition is met. The one residual is a **calibration** question (§8 note 1), not a
design defect.

## 6 — CALIBRATION READINESS (§15/§16 mandate)

The mechanism is specified precisely enough to calibrate without reopening design: each of the 4 parameters has
a stated semantic role, unit, and family; the calibration plan (§15 design) mirrors the already-successful
`967222a`/`898f149` protocol (pre-register before results; synthetic construction + ratified-reuse; **not**
FB14, **not** MB3-001→024, **not** MB3-025→048; **dual-sided** acceptance bar — a value must *both* release a
genuinely stale candidate *and* leave slow/quiet ranges undisturbed, no averaging; neighborhood sensitivity
sweep with honest `PARAMETER_FRAGILITY_FLAG`; output a frozen `ConfigV441` with `config_id()`). **CALIBRATION_
READY.**

## 7 — INDEPENDENCE / SEALED-EVIDENCE (§3/§4 mandate)

I authored nothing in this design (Red Team ≠ author of what it audits, §17 governance). No detector/scorer/
runner/escrow file modified; all changes in `red_team/`. FB14 used only to re-confirm the mechanism (zero
calibration weight). MB3-001→024 appears only as diagnostic history; MB3-025→048 not decrypted, not labelled,
not run, not referenced semantically. No Alpha/wheel/catalog/LIVE_SHADOW/broker touched.

## 8 — NON-BLOCKING NOTES (recorded for the future calibration mandate; none blocks the freeze)

1. **Dual-sided calibratability is unproven (VE §20.3).** The acceptance bar requires one parameter set to both
   recover stale-blocked TP (scenarios 8/16) *and* protect slow/quiet ranges (1/2/3/9). VE honestly flags that
   no single value may cleanly satisfy both across all 16 scenarios. This is the **principal residual risk** and
   is correctly a calibration question — the calibration mandate must *prove* dual-sided satisfaction or disclose
   the trade honestly (shallow-channel precedent), never force a value. It does **not** undermine the design's
   coherence.
2. **Minimum-age floor not derived (VE §20.2).** Flagged as structurally necessary but its interaction with
   `d_macro`/`n_touch` is not derived — left as an UNRESOLVED (DERIVED-candidate) parameter. Acceptable at design
   stage.
3. **Episode-identity interaction argued, not tested (VE §20.4).** The "stale zone does not IoU-overlap its
   replacement" claim rests on the two traced 0.000-IoU cases, not a proven general property. STALE-2/STALE-9
   must include an explicit IoU-continuation check at implementation. Non-blocking (grounded in evidence + reuses
   the unmodified episode-identity logic).
4. **Adjacent forced-`EPISODE_REPLACEMENT`-after-`BREAKOUT_ACCEPTED` over-fragmentation (VE §20.5 / `b1dcf92` §8)
   remains out of scope.** A distinct potential over-fragmentation of a CEO-continuous range, correctly not
   addressed here; recorded so it is not lost.

## 9 — WHAT WOULD HAVE MADE THIS AMENDMENT_REQUIRED OR BLOCKED (none occurred)

- A staleness trigger keyed to age/timeout/touch-scarcity/price-distance → would risk slow-range false-abandon →
  **not present** (semantic, alternation-gated).
- Any relaxation of ER/RND/traversal to "help" TP recovery → would erode E93 gains → **not present** (all frozen).
- Same-bar reuse of the triggering swing as replacement evidence → lookahead/double-use → **not present**
  (next-bar B, verified against `observe()` ordering).
- A tuned cooldown parameter introduced to suppress churn → mandate prohibition + fragility → **not present**
  (anti-churn is the alternation requirement itself).
- Any chosen numeric value → **not present** (all 4 UNRESOLVED).
- Any V4.4 code change or MB3-025→048 access → **not present**.

---

## 10 — NEXT CEO ACTION

Authorize a **separate, future calibration mandate** for the four §14 parameters, following the §15 plan, that
must inherit this design's scope boundary and its two non-loosenable structural constraints (rejection-count-
based never touch-scarcity-based; alternation-gated anti-churn), and must prove or honestly disclose the
dual-sided acceptance bar (Note 1) — **before** any implementation mandate. Then implementation, then a fresh
blind re-validation against evidence never used to calibrate (never FB14, never MB3). Whether to pursue this,
accept the E93 precision/recall trade, or hold V4.3 remains a CEO decision.

---

*Red Team · design-only audit · detectors/labels/scorer/escrow unmodified · changes only in `red_team/` ·
FB14 zero-calibration-weight · MB3-025→048 sealed · MB3-001→024 diagnostic-history-only · LEDGER E94 (prev E93).*
