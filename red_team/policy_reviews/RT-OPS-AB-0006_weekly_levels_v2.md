# RED TEAM — OPERATIONAL MODE, PHASE A + B · RT-OPS-AB-0006
### CAND-0006 reformulated — Prior-Week High/Low (PWH/PWL) v2.0, Route 3
**Date:** 2026-07-27 · **Auditor:** Red Team · **Policy @ commit `b636f29`, `POLICY_WEEKLY_LEVELS_v2.md`.**
Part A + Part B in one pass. **No data run · policy not modified · no remedy.** Verification = frozen policy + `git show | sha256sum` + reading `institutional_levels.py@bf02dd2` (weekly funcs).

**What changed:** v1.0 was NOT_CURRENTLY_TESTABLE. The Statistician (v2.7.40, `e68e0cd`) proved the block was **the thesis, not the detector**: 572 weekly levels → 275 touched geometrically (48.1 %, healthy) → 6 bias-aligned (2.2 %, collapse). v2.0 = **Route 3: remove the bias stage; direction from level kind** (WEEKLY_HIGH→short, WEEKLY_LOW→long). Population returns to 275.

## 1. GROUNDING — VERIFIED
- **Hash MATCH:** `institutional_levels.py @ bf02dd2 = c284fa2c` ✅ (identical at `0000225`, file unchanged across the session-levels commit — confirmed).
- **Feed-alignment:** weekly levels use `derive_week_index` from the 17:00-NY `day_ordinal` (weekend gap), NOT `session_of` fixed-UTC-hours — so the session feed-alignment warning does **not** transfer verbatim; the weekly window is a calendar-day/weekend construct, more feed-robust. (Day-boundary family, like PDH/PDL.)

## 2. TARGET 3 — THE COMPOSED WEEKLY TOUCH: composition CORRECT, lookahead-free
`detect_level_touches` **verified to skip weekly** — `if lv.kind not in (PDH, PDL): continue`; its window is same-day only. So no ratified function returns weekly touches; Alpha composed it (same discipline as the session sweep, CAND-0026).
- **Penetration + D7 mirrored:** WEEKLY_HIGH `high[j]≥price` / WEEKLY_LOW `low[j]≤price`, consumed once — identical to `detect_level_touches`' semantics. ✅
- **Window from `derive_week_index`:** `[available_idx, last bar of the current week]`, the weekly analog of the daily function's same-day window. Verified against `compute_prior_week_levels`: `available_idx = weeks[k][0]` (first bar of the *current* week), level = `max/min` over the *prior* week `weeks[k-1]` → **level known before it is used, no lookahead.** ✅
- **D3_bis:** `range(1, len(weeks))` per block → first week of each block UNCLASSIFIED, no cross-block window. ✅
- **Composition is faithful.** Optional (policy offers it): ratify `detect_weekly_level_touches` to replace the composition 1:1 — a hygiene improvement, not a correctness fix.

## 3. TARGET 4 — PARTIAL WEEKS: correctly gated; exclusion is legitimate, disclose the conditioning
- **COMPLETE-only via the ratified flag — verified.** `completeness = "COMPLETE" if n_days>=5 else "PARTIAL"` is computed **inside** ratified `compute_prior_week_levels` (`n_days` = distinct `day_index` over the source week); the policy only *gates* on it. **No invented threshold**, and **no lookahead** (n_days is a property of the fully-past source week). ✅
- **Statistician's flag — is exclusion another bias?** A partial (holiday) week's H/L is computed over fewer days → narrower range → the level sits closer to price → **touched more often.** Excluding partials therefore shifts the traded population toward **wider, less-frequently-touched** levels.
  - **It is a LEGITIMATE population definition, not a performance bias:** the criterion (`n_days≥5`) is **structural and pre-data**, not chosen on outcomes, and a <5-day "week" is genuinely not a weekly structure (thin holiday liquidity).
  - **BUT it is NOT frequency-neutral, and must be DISCLOSED as a conditioning:** the edge is measured on the COMPLETE subpopulation only — partials are touched more and are removed, so trigger counts and any touch-rate statistic are **conditioned on completeness**, not representative of "all weekly levels." Direction of its effect on measured edge is unknown (could flatter or penalize) — which is exactly why, being pre-registered and structural, it is not p-hacking. **Recommend the Statistician report the COMPLETE-only conditioning and, as a robustness check, measure partial-week touch/reversion separately.** Not a defect.

## 4. TARGET 5 — HORIZON: week boundary, live-valid; NOT the 460-bar survey window
- Part B time-stop = **the week boundary** (last bar of the current week, from `week_index`) — the weekly-native analog of the PDH/PDL day-boundary time-stop. **Live-valid** (the week end is calendar/weekend-derivable, not stale). ✅
- **The 460-bar survey window is NOT used as a horizon** — correctly. That figure was a *measurement* of how long weekly levels stay relevant, not a trade rule; using it as a time-stop would be a survey artifact. The policy uses the native week boundary instead. ✅
- **No Finding H′:** the week boundary is live-valid (unlike the persistent-B stale source session). A level touched late in its week has a short remaining horizon — same property as PDH/PDL, consistent with the family.

## 5. TARGET 2 — DIRECTION FROM KIND: an assumption; the CAND-0028 inverse-test requirement APPLIES, and is DECISIVE here
WEEKLY_HIGH→short is the **fade** assumption — not a measured fact. At CAND-0028 I required the direction rule be tested against its inverse. **The same requirement applies here** — with one difference and one amplifier:
- **Difference from 0028:** a Mid is *directionless* (approach-side was a bare assumption); a weekly HIGH/LOW *is* a resistance/support, so fade is the **inherited grammar of the screening-POSITIVE level-fade family** (CAND-0001 daily, CAND-0027 session). So there is a real prior — this is a *transfer* test to the weekly period, not a coin-flip.
- **Amplifier (why it is decisive, not a formality):** the very anti-correlation that collapsed the bias version — a HIGH is reached by rallying up, and we short it — is a structural reason to doubt that fade transfers cleanly to the weekly period, where a larger structural level may more often be reached by momentum that **continues**. **The inverse (continuation/breakout = Route 2) is the live alternative Alpha declined**, so it must be the null the fade is tested against. Requirement: test WEEKLY_HIGH→short **against** WEEKLY_HIGH→long, exactly as CAND-0028.

## 6. TARGET 1 — WHAT REMOVING BIAS LOSES  (and: does the reformulation remove the problem or move it?)
These two CEO questions converge on one answer.
- **The bias filter did two things:** (a) it *contradicted* the touch geometry (short demands bias-down, but a high is reached by rising) — the pathology, **correctly deleted**; (b) in principle it could also have *filtered* the touches that will break through rather than revert. **We cannot say whether (b) was useful or merely blocking** — the bias-aligned population was n=6, never enough to measure reversion-vs-continuation. So removing bias **loses whatever reversion discrimination bias might have carried, of unknown value.**
- **Route 3 does not RESOLVE that — it SIDESTEPS it** by adopting the family default (no filter) and betting the level-fade edge (proven at daily/session) transfers to weekly.
- **So: the reformulation REMOVES the bias-collapse *mechanism* but MOVES the underlying tension into the fade direction itself**, where it is now **measurable rather than blocking.** The anti-correlation ("reached by momentum, faded against it") is *still present* — it is no longer a funnel that zeroes the population; it is now the **risk of the fade**. This is genuine progress (untestable → testable), but it means the direction assumption (Target 2) carries the whole bet.

## 7. CROSS-BATCH PREDICTION — does the reformulation escape the weekly-structure problem?
**No — it relocates it, consistent with my period-length prediction.** I predicted the structural conflict is minimal at session, moderate at daily, **maximal at persistent (oldest).** Weekly sits **between daily and persistent** in age.
- The **bias-collapse** (275→6) is session-exempt (the policy's cross-check is correct: 0026-0031 have no bias stage, so that specific mechanism cannot fire) — **but that is a different thing from the anti-correlation.**
- The **anti-correlation as fade-risk** is family-wide: I already signalled it on the session batch (RT-OPS-AB-0004) as milder-at-session, and WORST for persistent-B (RT-OPS-AB-0005). **Weekly should sit between daily and persistent-B in severity.** So Route 3 does not remove the anti-correlation; it converts it from a blocking funnel into a measurable directional risk whose expected severity at the weekly period is intermediate. **The inverse-direction test (Target 2) is where this gets measured.**

## 8. STANDARD TARGETS + PART B
- **Lookahead — PASS** (level from prior week, used from current week; stop=raw OHLC at j; target=ratified opposite weekly level; time-stop=week boundary; direction from kind — all causal).
- **Circularity — PASS** (level selection vs forward measurement disjoint).
- **Duplicate/subset — NOT a subset.** PWH/PWL is the WEEKLY member of the level-fade family; period population **disjoint** from CAND-0001 (daily) and CAND-0027 (session) — distinct level-generating primitive (prior WEEK). No W-incr obligation. **The Statistician may group {0001, 0027, 0006} as one level-fade family for FDR** (shared grammar/mechanism) — a defensible family choice, not a subset correction.
- **Falsifiability — INTACT without a density filter.** 275 touches over the survey is naturally sparse (far below the Primitive-B saturation that forced the ATR filter); each touch is a discrete falsifiable event with defined stop/target/time-stop. ✅
- **S1 (intrabar order):** unspecified → existing DEMO worst-case convention. Carry.
- **S2 (arbitrarily-small stop):** stop = touch-bar extreme beyond the weekly level — same profile as CAND-0001/0027; **exposed → bind `min_executable_risk` floor.**
- **Hidden optimization — PASS.** No tunable numeric parameters (completeness `≥5` is the ratified D-WEEK flag, not a policy free-parameter; window from `week_index`; direction from kind). The only choice is Route 3 vs Routes 1/2 — a **thesis** choice pre-registered with reasons **before** results, not per-candidate numeric tuning.

## 9. VERDICT — **SURVIVED_RED_TEAM_A — Part B CONDITIONAL**
Reformulation is **correct and disciplined**: it deletes the bias-vs-geometry contradiction at the root, stays live-valid, and rejoins the screening-positive level-fade family. Composition verified lookahead-free; completeness-gate correct; horizon live-valid (no Finding H′); falsifiability intact without a density filter. Part B conditional on the existing DEMO gate (S1 worst-case + `min_executable_risk` floor). **Not a rejection.**

**The decisive open item is the direction assumption (Target 2):** Route 3 concentrates the entire weekly-structure tension into WEEKLY_HIGH→short, and everything the pipeline has measured predicts the fade edge is weaker at the weekly period than at daily. **The reformulation makes the problem testable; it does not solve it.**

## 10. HANDOFF → Statistician, for protocol & DEMO criteria
1. **Test the fade direction against its inverse** (WEEKLY_HIGH→short vs →long / continuation) — the CAND-0028 requirement, **decisive here**; the declined Route 2 is the null.
2. **Disclose the COMPLETE-only conditioning** (partials are touched more, removed by a pre-data structural criterion — legitimate, but the edge is conditioned on completeness); optional robustness: measure partial-week touch/reversion separately.
3. **FDR family:** {CAND-0001, CAND-0027, CAND-0006} is a defensible level-fade family; period populations are disjoint (distinct tests, not subsets).
4. **Weekly-structure severity is intermediate** (between daily and persistent-B) — the anti-correlation is relocated into the fade, not removed; measure it at the weekly period.
5. **DEMO gate:** existing S1 worst-case + `min_executable_risk` floor (touch-bar-extreme stop, S2-exposed).
6. Optional hygiene: ratify `detect_weekly_level_touches` to replace the composed trigger 1:1.

Multiple-testing family grows. Nothing modified, nothing run on data; no risk method proposed.
