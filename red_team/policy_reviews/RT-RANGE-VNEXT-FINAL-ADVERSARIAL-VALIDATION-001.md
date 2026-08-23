# RED TEAM — RANGE vNEXT FINAL ADVERSARIAL VALIDATION
### RT-RANGE-VNEXT-FINAL-ADVERSARIAL-VALIDATION-001 · Auditor: Red Team · 2026-08-23

Final independent adversarial validation of the remediated RANGE lifecycle vNext multi-candidate architecture
(`fa36324`). Red Team independently constructed the critical gates and attempted to BREAK the candidate. No
implementation change, no retuning, no repair, no P&L.

---

## 0 — VERDICT

```
RANGE_LIFECYCLE_VNEXT_RED_TEAM_PASS
RANGE_LIFECYCLE_VNEXT_RESEARCH_RATIFICATION_READY
```

The remediated multi-candidate RANGE lifecycle is semantically correct, causal, structurally bounded,
deterministic, and safe enough to be presented to CEO as a **research-ratified** market-intelligence candidate.
This is **not** PRODUCTION_READY / NEW_BRAIN_READY / LIVE_READY / AI_TRADER_READY, and nothing here integrates
it anywhere. v4.4 remains the canonical deployed baseline. One known issue (`_dead`/`_awaiting_role` growth) is
correctly a **mandatory pre-production remediation**, not a research blocker (§M).

## 1 — IDENTITY / REPOSITORY INTEGRITY (§3) — gate verified

| check | result |
|---|---|
| `fa36324` identity, parent = `bba6310` | PASS (ancestor verified) |
| HEAD = `fa36324`, branch discovery-mk-matrix-v1, local = remote ×4 | PASS |
| v4.3 / v4.4 semantic+engine untouched by the vNext work | PASS (empty git diff `bba6310~1..HEAD`) |
| semantic diff = only hard-cap + fingerprint | PASS: **22 lines** in `range_semantic_vnext.py` (the cap-check condition + fingerprint bump); everything else = tests + docs |

The single source change replaces `if action == "REPLACEMENT" and len >= cap` with
`frees_a_slot = action == "MERGE" and target_id is not None and target_id in self._active_macros; if not
frees_a_slot and len >= cap: refuse`. No RANGE semantic (tol_cluster/d_macro/IOU_CONTINUE/formation/merge/
supersession/abandonment/arbitration/confirmation) altered. No unrelated drift → not a blocker.

## 2 — PRE-FIX DEFECT REPRODUCED (§4, gate A)

Independent harness drove a forced CONTINUATION-at-capacity through the **real** pre-fix (`bba6310`) insertion
path:

| cap | before | after | refused |
|---|---|---|---|
| 1 | 1 | **2** | no |
| 2 | 2 | **3** | no |
| 3 | 3 | **4** | no |

Repeated forced CONTINUATION at cap=3 → **active reached 14** with zero refusals. `PRE_FIX_CAP_VIOLATION_
DEMONSTRATED` — the harness detects the defect (exact active=34 not required; construction differs, as the
mandate permits). The pre-fix `REPLACEMENT`-only gate lets CONTINUATION bypass the cap without limit.

## 3 — REMEDIATED HARD-CAP INVARIANT (§5, gate B) + NO ALTERNATE INSERTION (§6, gate C)

**§6 write enumeration** (independent grep of all `_active_macros` mutations): exactly **one** runtime net-add
— line 486 `self._active_macros[new_id] = st_macro`, gated by the capacity check at 451. Other mutations are
the empty constructor (216), `.pop` removals (kill/close/supersede), and restore (940, rebuilds from a snapshot
bounded by its own content). **The whole CLASS of "an action-specific branch escapes the gate" is closed**: the
new check is structural (`not frees_a_slot`), so any future action is capacity-checked by default unless it
demonstrably frees a slot.

**§5 adversarial matrix** (forced episode-identity to exercise every action at capacity, which natural bars
cannot reliably force), post-fix `fa36324`:

| cap | REPLACEMENT | CONTINUATION | MERGE (in-registry target) | MERGE (stale target) |
|---|---|---|---|---|
| 1 | refused, active=1 | refused, active=1 | net-zero, active=1 | **refused**, active=1 |
| 2 | refused, active=2 | refused, active=2 | net-zero, active=2 | **refused**, active=2 |
| 3 | refused, active=3 | refused, active=3 | net-zero, active=3 | **refused**, active=3 |

Plus post-snapshot-restore at capacity: a forced CONTINUATION after `restore_state` is refused (active stays at
cap). **ZERO structural cap violations under every tested path.**

## 4 — MERGE NET-ZERO PROVEN (§7, gate D)

Source ordering: cap-check exempts MERGE only when `target_id in _active_macros`; then `_supersede_macro(target_
id)` **pops the target** (line 306) BEFORE the insert (line 486). Sequence is `len=cap → cap−1 → cap` — **no
transient cap+1**. Adversarially confirmed:
- MERGE at capacity keeps occupancy = cap, target is superseded, `EPISODE_MERGED` emitted, not refused.
- **A stale/absent `target_id` cannot bypass the cap**: the guard requires `target_id in _active_macros`, so a
  MERGE claiming a non-existent target is capacity-checked and refused (no failed-supersession-then-insert
  path, no cap+1). This is the exact class the exemption could have leaked and does not.

`MERGE_NET_ZERO_PROVEN`.

## 5 — REFUSAL SEMANTICS (§8, gate E)

At capacity a refused candidate: is not inserted; does **not** evict or mutate any unrelated candidate (same ids
+ same boundaries before/after, verified); emits exactly one `REGISTRY_CAPACITY_REFUSED` with `structure_id =
None` (no ghost id); clears pending; deterministic. No hidden victim-selection or silent replacement.

## 6 — FULL-HISTORY EQUIVALENCE (§9, gate F) + AGE GATE (§11, gate G)

Independent dual-engine replay, full canonical M15 file (**355,696 bars**, N1 `atr14` reference pipeline),
pre-fix vs post-fix in one pass:

| metric | POST-FIX | PRE-FIX | reference | match |
|---|---:|---:|---:|---|
| births | 12,813 | 12,813 | 12,813 | **EXACT** |
| merges | 361 | 361 | 361 | **EXACT** |
| genuine confirmations | 4,092 | 4,092 | 4,092 | **EXACT** |
| capacity refusals | 0 | 0 | 0 | **EXACT** |
| max active | 4 | 4 | 4 | **EXACT** |
| early confirmations (age < d_macro=29) | 0 | 0 | 0 | **EXACT** |
| price abandonments | 4,152 | 4,152 | 4,108 | +44 (1.0%) |

**Decisive result: PRE == POST byte-identical across all 355,696 bars (0 divergence bars) → the remediation is
semantically inert.** This is guaranteed structurally (the changed condition only alters behavior when `len >=
cap`; historical max active = 4 ≪ the measured-run cap of 500, so the new code path never fires) and is now
confirmed empirically at full scale.

**Two secondary aggregates differ from the reference, both explained and neither remediation-induced** (pre ==
post identical): (a) per-year confirmed-*bars* run higher in my harness — since genuine confirmations match
*exactly* (4,092), this is definitionally a tally convention (my counter includes every bar the canonical macro
carries a `confirm_ts`, incl. weakening, vs an `OK_RANGE_MACRO`-reason count); (b) price abandonments +44
(1.0%), marginal `atr_ref`-sensitivity of the distance-based abandonment trigger in an independent atr feed,
with zero effect on any confirmation, birth, merge, or the cap invariant. **§11 age gate: 0 early confirmations
— EXACT** (no genuine confirmation before d_macro=29 under normal/MERGE/CONTINUATION/refusal/restore).

## 7 — CAUSALITY (§12, gate H)

vNext lifecycle decisions use only current/past information: candidate births consume **confirmed (lagged)**
swings (`_detect_confirmed_swings`, the unchanged v4.4 mechanism); merge/supersession/arbitration read current
`_active_macros` state + current close; confirmation is v4.4's own trailing-close gate. No future-bar data,
future-confirmation knowledge, or post-event reconstruction is used in runtime logic; historical matching lives
in offline analysis, separate from `observe()`. **Empirically corroborated by the restart/prefix-invariance
result (§8 below): a future-data leak would break prefix invariance, and none was observed.**

## 8 — RESTART DETERMINISM (§13, gate I) + IDENTITY/SNAPSHOT (§14, gate J)

- **Restart**: continuous replay vs snapshot→restore→resume produced **identical** canonical id / reason /
  boundaries / active-registry / future outputs across the resumed span (real multi-active data). At-capacity
  restore re-enforces the cap (post-restore forced CONTINUATION refused). Zero divergence.
- **Snapshot identity**: `restore_state` checks contract_version + config_id + implementation_fingerprint.
  Behaviorally verified: a **pre-fix snapshot is rejected by the post-fix implementation** and a **post-fix
  snapshot is rejected by the pre-fix implementation** (both `SNAPSHOT_CONTRACT_MISMATCH`); same-version restore
  is accepted. Cross-version snapshots cannot be falsely accepted → not a blocker. The descriptive
  (non-cryptographic) fingerprint is recorded as a **procedural/integrity limitation only** — code identity is
  independently verifiable via git-blob SHA + config_id.

## 9 — MULTI-CANDIDATE SOLVES THE v4.4 SINGLE-SLOT PATHOLOGY (§K)

The diagnosed v4.4 defect (a single candidate occupies the sole slot ~9.7 years, 2016–2024, blocking all RANGE
activity → **0 confirmed bars for nine consecutive years**) is materially resolved: in my independent run vNext
confirms thousands of RANGE bars in every one of 2016–2024 (v4.4 = 0). The multi-slot registry lets spatially
distinct candidates form and confirm concurrently while the same stuck candidate still, on its unchanged T3
merits, never confirms — it simply no longer blocks others. `MULTI_CANDIDATE_SOLVES_SINGLE_SLOT`.

## 10 — NEGATIVE CONTROL / SLOW-STRUCTURE PRESERVATION (§16)

The mechanism this mandate validates — the **capacity refusal** — has a premature-kill rate of **0/187 (0.0%)**:
it never fired historically (max active 4 ≪ cap). So the hard-cap remediation adds **zero** slow-structure-kill
risk. The broader vNext price-abandonment mechanism's defensible premature-kill core is 2.14–6.42% (matcher-
parameter-sensitive, disclosed, not uniquely identified), with placebo discrimination ~+76–90% — materially
better than the rejected v4.5 timeout recovery (36.9% / 12.3%). Defensible conclusion **holds**: vNext preserves
genuine slow structures far better than v4.5, and the remediation itself introduces no additional risk. Stated
with the uncertainty intact — no single premature-kill percentage is claimed as unique.

## 11 — ABANDONMENT / SUPERSESSION SAFETY (§17)

`_retire_price_abandoned_candidates` never fires on the sole active candidate (`len < 2` guard — protects the
isolated slow candidate this program exists for) and fires only when a **different** active candidate is
structurally closer to price (spatial `tol_cluster*atr_ref` distance, an existing quantity — no new threshold).
It is **not a disguised age timeout**: it is triggered by spatial supersession, never by elapsed time — the
precise distinction from the rejected v4.5. Ordering is deterministic (sorted ids). No two spatially distinct
candidates improperly kill one another.

## 12 — CANDIDATE EXPLOSION UNDER HOSTILE SEQUENCES (§18)

The forced-action harness (repeated CONTINUATION/REPLACEMENT at cap 1/2/3, all refused) is a maximally hostile
insertion sequence; the cap held structurally and the engine stayed deterministic and bounded (refusal is O(1),
no pathological loop). Natural full-history occupancy never exceeded 4. The cap is structural under intentional
hostility.

## 13 — TESTS (§19) + REPORTING (§20)

Independent full-suite re-run: **554 passed** (120.9 s) — matches the VE reference exactly; no environmental
failure in this environment (mypy inclusive). Corrected canonical figures confirmed in the diagnostics:
2016–2024 total **62,713** (not 55,713), range **6,429–7,660** (not 6,429–7,704) — both prior summary errors
corrected in the report, per-year data always correct.

## 14 — SNAPSHOT-STATE GROWTH CLASSIFICATION (§15, gate M)

`_dead` / `_awaiting_role` grow with lifetime candidate population (Statistician: `REMEDIATION_REQUIRED_BEFORE_
PRODUCTION`). Red Team independent assessment: this is a **PRODUCTION_HARDENING** concern (unbounded
memory/snapshot growth + restart latency over long live runtime), **not a RESEARCH_CORRECTNESS** defect — it
does not affect the correctness, causality, boundedness of the active registry, or any confirmation/lifecycle
semantic validated above. **Classification: B — may remain a mandatory pre-production remediation; it does NOT
block RESEARCH ratification.** Not repaired here.

## 15 — GATE SUMMARY (§22)

| gate | result |
|---|---|
| A pre-fix defect reproduced | PASS |
| B hard cap structurally unbreakable | PASS |
| C no alternate insertion bypass | PASS |
| D MERGE net-zero proven | PASS |
| E refusal semantics clean | PASS |
| F full-history semantic equivalence | PASS (pre==post zero drift; 6/6 structural totals EXACT; 2 secondary aggregates explained, non-remediation) |
| G age gate intact | PASS (0 early, EXACT) |
| H causality intact | PASS |
| I restart determinism | PASS |
| J identity / snapshot compatibility | PASS |
| K multi-candidate solves single-slot pathology | PASS |
| L no newly-discovered blocker | PASS (none found) |
| M snapshot-growth correctly classified | PASS (pre-production, not research) |

All 13 material gates pass. No blocker found.

---

## 16 — VERDICT & NEXT STEP

```
RANGE_LIFECYCLE_VNEXT_RED_TEAM_PASS
RANGE_LIFECYCLE_VNEXT_RESEARCH_RATIFICATION_READY
```

The candidate may be presented to CEO for **research ratification**. It is **not** authorized for production,
New Brain, live, or AI Trader integration, and is not integrated anywhere by this mandate. The `_dead`/
`_awaiting_role` growth must be remediated before any production step. v4.4 remains the canonical deployed
baseline.

---

*Red Team · independent adversarial construction · no implementation change · no P&L · pre-fix defect
reproduced · post-fix cap proven structural · MERGE net-zero proven · full-history pre==post zero drift ·
LEDGER E100 (prev E99).*
