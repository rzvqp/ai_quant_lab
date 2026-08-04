# RED TEAM — CODE ATTACK · Session reference levels (MK-04)
### RT-CODE-A-0004 · Target: `code/session_levels.py`, commit `bf02dd2`
**Date:** 2026-07-25 · **Auditor:** Red Team · **Mandate:** CEO — attack session levels (lookahead, D3_bis, D7, ambiguity; + Mid, primitive-B saturation, straddle, backtest↔live).
**Method:** read the frozen module + `session_of`/`_runs` + tests (`tests/test_session_levels.py`, 7). **No data run · module not modified · no remedy.**

## 0. CONTEXT & CONTAMINATION
Two primitives: **A** `compute_prior_session_levels` (expires after the next session, 2–3 active) and **B** `compute_persistent_session_levels` (persists to first touch/D7, accumulates). Three levels per closed session (High/Low/Mid) + touch detectors. Reuses `institutional_levels._runs` and `market_state.session_of`. **Imports: only `Block` (inert), `session_of`, `_runs` — no MK-01/MK-02 defective logic (F1/F2 do not reach here).** `session_of` = **fixed UTC-hour buckets** (asia<8, london<13, ny<21, late).

## 1. STANDARD TARGETS

**Lookahead — PASS (verified per field, not just the declaration).**
- The level is the closed session's `max(high)`/`min(low)`/mid over `[p0,p1]`, and `available_idx` = the first bar of the **next** session (A) or the next session start (B) — i.e. **after** `p1`. The session max/min is only knowable at `p1`; it is used from a later bar. ✅
- Touch scans run `range(available_idx, expiry_idx+1)` forward; consumed once. ✅
- Confirmed by `test_prior_no_lookahead_level_uses_only_completed_session`: mutating **future** bars leaves the levels unchanged. ✅

**D3_bis — PASS.** Both primitives compute sessions **per block** (`_runs(session_index, block.start, block.end)`). Primitive A skips the block's first session (`range(1, …)` → UNCLASSIFIED, no cross-block borrow); primitive B caps every level's `expiry_idx = block.end-1` and never emits the block's last session (`range(0, len-1)`), so no window crosses a block boundary. ✅ (`test_…_first_session_unclassified` asserts no `available_idx == 0`.)

**D7 — PASS.** Both touch detectors `break` at the first touch; `count_active_persistent_levels` deactivates a level at `min(first_touch, expiry)`. Consistent one-shot consumption. ✅

## 2. TARGET 1 — MID as a different object: **SURVIVES**, one degenerate edge
- **Containment correctly implemented:** `low[j] <= Mid <= high[j]` (`detect_session_mid_touches`), separate from High/Low (`detect_session_level_touches` skips Mid). The three are never reported together. ✅
- **"Covers Mid but doesn't trade it?" — cannot happen for a real bar.** A bar's `[low,high]` is its traded range; if `low[j] ≤ Mid ≤ high[j]`, price *did* traverse Mid within the bar. Containment is therefore a **sound** proxy for "price reached Mid." No defect.
- **Degenerate (zero-range) session — flag.** If a session's `max(high) == min(low)` (a flat/single-price session), then `Mid = High = Low`. A bar containing that price then satisfies **all three** tests (`high≥High`, `low≤Low`, `low≤Mid≤high`) → the module emits **three coincident levels** and up to three touches **at the same price**. Each is individually correct, but the "three distinct objects" collapse to one and are **not deduped**; a downstream aggregating levels would triple-count a flat session's single price. Rare, but reachable; **not exercised by the tests** (fixtures use distinct H/L). Minor edge, flagged.

## 3. TARGET 2 — Primitive B saturation: **stated directly — do NOT use B without a filter**
Measured: **median ~89, max 188 active levels simultaneously.** At that density the level set **saturates the price range** — price is essentially *always* adjacent to some session level, so **"price reacts at a session level" carries no information**: any reaction is attributable to the nearest of ~89 levels, and the hypothesis becomes **unfalsifiable by saturation.** This is precisely the pattern the CEO cites as the project's worst losers (DZ×FVG 18,275 / −\$2,432; CAND-0020 34,006 / −15,409R; CAND-0024 18,852 / −2,605R) — **high-volume, unfiltered zone/level exposure that dilutes any edge below cost.**

**Direct answer:** primitive **B, used without a selection filter, is guaranteed to dilute** — it is not a usable trigger on its own. The module **itself** flags this and ships `count_active_persistent_levels` as a **hard precondition** ("măsurat înainte de a construi ceva pe B"). So:
- **Primitive A** (2–3 active) — **SURVIVES clean**, exactly mirroring PDH/PDL.
- **Primitive B** — **SURVIVES as a primitive** (correct, lookahead-safe, D7), **but carries a HARD condition: no candidate may be built on B without a filter that bounds the active-level count to a small, decidable set.** Unfiltered, it repeats the DZ×FVG / CAND-0020 / CAND-0024 loss. Stated directly, as instructed.

## 4. TARGET 3 — Straddle (8.32% of sessions cross a day boundary): **SPECIFIED, not ambiguous**
Sessions are segmented by **`session_index`** (from `session_of` on the UTC hour), **not** by `day_index`. A session that crosses the 17:00-NY day boundary remains **one `session_index` run** (same `session_of` label → no increment), so its High/Low/Mid come from the **whole session run**, assigned to **that session**, and are **never split** by the day. The "old day vs new day" question **does not arise** — session levels do not use day assignment at all. This is **specified** (via `session_index`), not ambiguous; **no defect.** (Contrast: PDH/PDL uses `day_index`; the two segmentations are deliberately different objects.)

## 5. TARGET 4 — Backtest↔live alignment: **a transferability (correctness-of-transfer) risk, not mere interpretation**
`session_of` maps a timestamp → session by **fixed UTC hours** (boundaries at 08/13/21 UTC). The **21 UTC (ny→late) boundary sits right at the OANDA maintenance pause (20–21 UTC)**; MT5's clock differs by ~3h with a weekend close at 23:45. The **UTC-hour label is feed-independent** (a pure function of the timestamp), **but the BARS that fall in each session differ by feed** (different pause/weekend structure). So the **same session** (same UTC label) contains a **different bar set** on OANDA vs MT5 → a **different** `max(high)`/`min(low)`/Mid.

**Assessment — correctness-of-transfer, not interpretation.** The module is internally correct (a pure function of its input bars). But its **output is feed-dependent**: a session-levels edge validated on the OANDA backtest can produce **different session levels live on MT5** because the session's bar set — especially near the 20–21 UTC boundary and the weekend — is not the same. So backtest and live are **not aligned**, and a validated candidate may **not reproduce live**. This is **not a module defect** and cannot be fixed inside `session_of` (it consumes caller-side session indices); it is a **standing transferability constraint on every session-levels candidate.**

**Which candidate is affected?** **None yet** — this primitive precedes its candidates (handoff: "Alpha builds candidates"). But **every future session-levels candidate inherits this risk**, most acutely any whose sessions abut the 21 UTC / weekend boundary. It must be attached at candidate creation (analogous to the earlier feed-provenance warnings).

## 6. TEST COVERAGE (7 tests) — sufficient?
Covered: A emit/HLM/D3_bis/expiry; A no-lookahead (future-mutation invariance); B accumulation + `expiry=block end` + `count_active`; A-expires-vs-B-persists; High/Low touch-by-exceedance + D7 + Mid-excluded; Mid containment. **Solid on the core semantics + lookahead + D3_bis + D7.**
**Not exercised:** the **degenerate zero-range session** (High=Low=Mid coincidence, §2); the **saturation scale** (89–188 active — a measurement, not a unit-testable property); the **backtest↔live feed-alignment** (§5 — cross-feed, not unit-testable). The first is a real untested edge; the latter two are design/transferability concerns outside a unit test.

---

## 7. VERDICT

**The module SURVIVES** — lookahead-safe (verified per field), D3_bis and D7 correct, Mid containment sound, and the straddle is specified (not ambiguous). Primitive A mirrors PDH/PDL cleanly.

**Two conditions the CEO must carry (neither is a module defect):**
1. **Primitive B — do NOT use without a filter.** At 89–188 active levels, unfiltered B is *guaranteed to dilute* (the DZ×FVG / CAND-0020 / CAND-0024 loss pattern); `count_active_persistent_levels` exists precisely so any B-candidate must first bound its active-level count. **A candidate on B without such a filter should not be built.**
2. **Session-levels candidates carry a backtest↔live transferability risk** — fixed-UTC-hour session boundaries (21 UTC at the OANDA pause; MT5 +3h / 23:45 weekend) make session levels **feed-dependent**; an OANDA-validated edge may not reproduce on MT5. A correctness-of-transfer constraint, attached at candidate creation.

Plus a minor edge: **degenerate zero-range sessions** collapse High=Low=Mid into three coincident, un-deduped levels (untested).

## 8. HANDOFF → CEO, then Alpha builds candidates.
Ratify the module (sound). Bind, at candidate creation: (1) **primitive B requires an active-level filter** — reject any B-candidate without one; (2) the **feed-alignment transferability warning** on every session-levels candidate. Consider a test for the degenerate coincidence. Red Team designs no fix; reopens nothing. Nothing modified, nothing run on data.
