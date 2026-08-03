# RED TEAM — CODE RE-ATTACK · F2/F3 remediation of `market_structure.py`
### RT-CODE-A-0002 · Target: the remediation, commit `f4f8fab` (vs the attacked `8edbf99`)
**Date:** 2026-07-25 · **Auditor:** Red Team · **Mandate:** CEO — attack the F2/F3 fix; do not reopen D2/D7; liquidity_mechanics untouched.
**Method:** read the diff `8edbf99 → f4f8fab`, the remediated functions, and the regression tests (`tests/test_detect_breaks_f2_f3.py` 14, `_rearm.py` 5, `_mk01_mk02_independent.py` 12, `test_structure.py` 10). **No data run.**

## 0. WHAT CHANGED (verified from the diff)
- **F2 — no code change.** `detect_breaks`'s consumption loop is **byte-identical** to `8edbf99`. Only the docstring was added, *ratifying* the semantics: *"each confirmed swing produces at most one valid break; a new break comes only from a DISTINCT swing (different index)."* The claim "the Mandate-5.2 upstream `consumed` filter was already correct" is a **re-verification, not a repair.**
- **F3 — real code, well-scoped.** New `_assert_ordering_precondition(swings)` called at the **top of BOTH `label_structure` and `detect_breaks`** (my RT-CODE-A-0001 F3 extension, implemented). It raises `ValueError` on four violations: confirmed_idx < idx; idx not strictly increasing; duplicate idx; confirmed_idx non-monotone.

---

## 1. F2 re-arm fix — **SURVIVES** (verified independently, no new defect)
- **Re-arm is genuinely prevented.** `test_c1_c7` (breakout sustained bars 10–14 over ref idx=7 → **exactly one** BOS_BULL) and `test_c2` (consumed ref not reactivated) confirm the upstream `consumed` filter. I traced the loop: a consumed idx is skipped **before** `live_*` assignment, so the same swing cannot re-fire. ✅
- **Consumed-swing vs later new swing:** `test_c3` — ref7 consumed, a later distinct HH@20 produces its own break, refs distinct. Correct under the ratified "one break per distinct swing." ✅
- **Bull/bear symmetry:** `test_c4` (sustained downward breakout → one BOS_BEAR). The bearish path mirrors the bullish (`live_ll/live_hl`, shared `consumed` keyed by unique idx). Symmetric. ✅
- **No new defect introduced** — the fix is docstring-only, so it cannot regress executable behavior.

## 2. F3 extension to `label_structure` — **SURVIVES** (correctly implemented + tested)
Both consumers now fail-closed (`test_f3_label_structure_temporal_disorder_raises`, `_duplicate_idx_raises`, and the happy path). This directly actions my RT-CODE-A-0001 F3 finding that ordering is load-bearing in `label_structure` too, not only `detect_breaks`. ✅

---

## 3. FINDING — F3 precondition is OVER-STRICT (answers the CEO's question directly)

**Can the precondition reject legitimate inputs? YES.** The guard enforces a **GLOBAL** invariant (`idx` strictly increasing across the *entire* list), but **both consumers only USE a PER-BLOCK ordering** — each segregates by `block_index` (`detect_breaks`: `block_swings = [s for s in swings if s.block_index == b_i]`; `label_structure`: `last_high[b]`/`last_low[b]` keyed by block). Cross-block order is never used.

**Concrete legitimate input that is wrongly rejected:** call `detect_swings` with `blocks` **not** in ascending-start order (nothing in `detect_swings` requires sorted blocks — it processes them independently), or concatenate two `detect_swings` outputs. The result is **per-block idx-sorted but globally interleaved** → the global check raises `ValueError`, even though both consumers would process it **correctly** per block. The `confirmed_idx`-monotone check fails the same way on out-of-order blocks.

**Severity: LOW, but real.** The canonical pipeline (blocks in ascending order) never trips it, and rejecting is fail-closed (safe, not silently wrong) — so it does not threaten current correctness. But it is a genuine case of *a precondition stricter than the consumers require*, which could block a legitimate reordered-/merged-block caller. **Not tested** (all F3 tests are single-block). *Stated as a finding; I do not propose the fix (that would touch the guard's ratified scope).*

## 4. NEW FINDING — cascade break **MIS-TIMING** (within the ratified count-semantics)

The ratified D7 fixes the *count* ("each distinct swing → one break") — I do **not** reopen it. But the **one-break-per-bar** loop structure (per bar, at most one bullish `if/elif` and one bearish) produces a *timing* artifact the ratification does not cover:

> Two stacked unconsumed higher-highs `HH_a=100`, `HH_b=110`, both confirmed, neither broken. A single sustained `close=120`:
> • bar *c* → BOS vs `HH_b` (most recent), consume `HH_b`;
> • bar *c+1* (close still 120) → BOS vs `HH_a`.
> `HH_a` was exceeded at bar *c* (120 > 100) but its break is **recorded at bar *c+1***. With *N* stacked swings, the oldest breaks at bar *c+N−1* — **mis-timed by up to N−1 bars.**

The *existence* of these distinct breaks is ratified; their **timing is not** (D7 ratifies consumption/count, not break-bar assignment). For any downstream that uses break **timing** (spacing, break-to-entry latency, per-bar break density) this is a distortion. **Reachable** (consolidation with several higher-high fractals, then a breakout close above all). **Untested:** no test sustains a close above ≥2 stacked unconsumed same-label swings — `test_c3` separates its two breaks in time, so the cascade is never exercised.

## 5. REGRESSION COVERAGE — "56 pass, but do they cover what's needed?"
| Covered well | Gap |
|---|---|
| Re-arm (single ref → 1 break), consumed-not-reactivated, distinct-later-swing, bull/bear single-ref symmetry, per-block reset, no-lookahead-under-mutation | **Sustained cascade** (one breakout above ≥2 stacked unconsumed same-label swings) — neither its **count** nor its **timing** (§4) is exercised |
| F3 happy path + all four error branches on `detect_breaks` **and** `label_structure` | F3 **global-vs-per-block over-strictness** (§3) — all F3 tests are single-block; the reordered-/merged-block rejection is untested |
| MK-01/MK-02 independence (12), structure (10) | **F4** (simultaneous opposite CHoCH on one bar, RT-CODE-A-0001) — still unaddressed; **out of scope** for this remediation, noted as remaining open |

The suite solidly covers the **re-arm** and **F3 core**; it does **not** cover the **cascade** (existence + timing) nor the **precondition-scope** edge.

---

## 6. VERDICT

**The remediation SURVIVES.** It does exactly what it claims — the F2 re-arm is verified correct (docstring-only, no regression risk), and F3 is correctly extended to both consumers and tested. **No new code defect is introduced.**

Two findings for the ratification decision (neither blocks it):
- **F3 over-strict (LOW):** the precondition enforces global ordering though the consumers need only per-block — it can reject a legitimate reordered-/merged-block input. Fail-closed, so safe, but stricter than required.
- **Cascade mis-timing (NEW, within ratified count-semantics):** older stacked swings' breaks are recorded 1…N−1 bars late; the timing is an unratified consequence of the one-break-per-bar loop; untested.

Plus a coverage note: the sustained-cascade and the per-block-precondition edge are untested; **F4 remains open** (out of scope here).

## 7. HANDOFF → CEO, for the final MK-01 / MK-02 ratification decision.
The fixes are sound. Before ratifying, the CEO should decide: (a) whether the **cascade break timing** is acceptable (it is a *timing* question D7 did not settle) and (b) whether the **global** precondition scope is intended or should match the consumers' **per-block** requirement. Both are stated as findings; Red Team designs no fix and reopens neither D2 nor D7. `liquidity_mechanics.py` untouched by this remediation and not re-attacked.

**Re-attack ends. Nothing modified, nothing run on data.**
