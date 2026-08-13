# RED TEAM — VE HANDOFF RE-VALIDATION · `ve_brain` v0.1.1 @ `c111d82`
### RT-HANDOFF-0002 · the eight points · forged-eligibility attack · complete-path break attempts
**Date:** 2026-08-13 · **Auditor:** Red Team · **Target:** `ve_brain/` v0.1.1 @ `c111d82` (FAIL-1/2/4 + A5 corrective, 25 tests, mypy clean). **No engine modified; no repair; no real data.** Verified on imported source @`c111d82` + executed fixtures + VE's 25 tests re-run (25 passed).

# VERDICT — **VE_HANDOFF_CONDITIONAL**
**Seven of eight points pass and the real N1→Router→EligibilityDecision→EV→N6 path is demonstrably correct** — my prior FAIL-1/FAIL-2/FAIL-4 and the A5 gaps are genuinely closed. **One CEO-named invariant is not structurally guaranteed:** a **matching-ID forged `EligibilityDecision(eligible=True)`** for a RANGE strategy makes N6 emit **TRADE** — because N6 trusts the forgeable `eligibility.reason_codes` and the candidate carries **no independent range marker** (`requires_true_range`/`strategy_family`). This is the **fourth instance** of the bypassable-guard pattern (the CEO asked me to find it). One well-scoped fix stands between CONDITIONAL and PASS; **Mandate 2 is not yet authorized.**

## THE EIGHT POINTS — scorecard
| # | point | result |
|---|---|---|
| 1 | router cannot be bypassed | ⚠ real path yes; **forged matching-ID eligibility bypasses** (defect below) |
| 2 | a RANGE strategy cannot produce TRADE | 🔴 **violated** via forged eligibility → TRADE |
| 3 | N6 requires a VALID EligibilityDecision | ⚠ requires one + checks **identity**, but cannot verify it is genuine (forged matching-ID passes) |
| 4 | compression & displacement axes stay INDEPENDENT | ✅ `RawAxes.is_compressed`/`is_displacement`, non-mutual-exclusive |
| 5 | simultaneity survives to the Router | ✅ `{COMPRESSION, BREAKOUT_TRANSITION}` both present (fixture) |
| 6 | A5 carries COMPLETE data identity | ✅ `data_identity` = symbol/timeframe/block_start/**block_end**/segment_id/manifest_hash; fingerprint covers data·config·strategy·engine·contract·N1·router·eligibility |
| 7 | comparability imposed on ALL internal paths | ✅ **by absence** (verified: no internal comparison/leaderboard/aggregation) |
| 8 | 12 handoff deliverables complete | ✅ appear present |

## THE ONE BLOCKING DEFECT (enumerated)
- **defect:** N6's range block is not structural. Step 2 fires only on `TRUE_RANGE_NOT_IDENTIFIABLE ∈ eligibility.reason_codes` (a consumer-constructible, forgeable field), and `_eligibility_valid` checks only **identity consistency** (ids/fingerprint/router_version/eligible=True). The candidate (`DecisionRequest`) carries **no** `requires_true_range`/`strategy_family`/`allowed_regimes`, so N6 has **no independent way** to know the strategy requires RANGE. A forged eligibility with **matching** ids + `eligible=True` + reason_codes omitting the range code defeats the block.
- **file · line:** `ve_brain/n6.py::decide_n6` step 2 (`if _RANGE_REASON in eligibility.reason_codes`) + `_eligibility_valid`; `ve_brain/contracts.py::DecisionRequest` (no range marker).
- **fixture (reproducible):** candidate = range strategy, RATIFIED, EV-positive, all ids set; `eligibility = EligibilityDecision(strategy_id/strategy_version/market_event_id/regime_fingerprint = candidate's, router_version=ROUTER_VERSION, eligible=True, reason_codes=("ROUTER_ELIGIBLE",))` → `decide_n6(candidate, eligibility)`.
- **observed:** `decision = TRADE`, `reason = TRADE_VALIDATED_EDGE`. A range strategy trades.
- **required:** `NO_TRADE` / `TRUE_RANGE_NOT_IDENTIFIABLE`. N6 must fail-closed on the strategy's **own** range requirement, independent of the eligibility object.
- **required fix:** carry `requires_true_range` (or `strategy_family`/`allowed_regimes`) on `DecisionRequest`, bind it into the `regime_fingerprint`/schema so it cannot be silently omitted or altered, and have N6 emit `TRUE_RANGE_NOT_IDENTIFIABLE` whenever the candidate declares range — since RANGE is never producible, this is a pure structural fail-closed.
- **owner:** VE.
- **why VE's 25 tests miss it:** every F1 test derives its eligibility from the **real router** (`_elig` runs `StrategyRouter`), which never emits `eligible=True` for range; the forgery tests (f1_03–06) use **wrong-id** eligibilities (caught by identity check). **No test constructs a matching-id `eligible=True` eligibility for a range strategy** — exactly the surface the CEO named ("strategy_family / requires_true_range poate fi omis").

## WHAT IS GENUINELY FIXED (verified — so CONDITIONAL is precise, not grudging)
- **FAIL-1 real path CLOSED + guarded.** `decide_n6(candidate, eligibility)` — `eligibility` is a mandatory positional (no permissive legacy signature); `None` → `MISSING_OR_INVALID_ELIGIBILITY` (test_f1_02/09). The complete real path (N1 `RawAxes` → `StrategyRouter` → `EligibilityDecision` → N6) blocks a range strategy: router → `eligible=False, TRUE_RANGE_NOT_IDENTIFIABLE`; N6 → `NO_TRADE, TRUE_RANGE_NOT_IDENTIFIABLE` (reproduced). Identity forgeries with wrong ids are rejected (f1_03–06). My original bug (test_f1_01) is exactly reproduced and now yields NO_TRADE.
- **FAIL-2 CLOSED.** `applicable_regimes(RawAxes)` reads `is_compressed` and `is_displacement` **independently**; the mandatory fixture (`is_compressed=T ∧ is_displacement=T ∧ structure=range`) → **`{COMPRESSION, BREAKOUT_TRANSITION}` both present**. `volatility_state` is present but **used nowhere** for eligibility (grep-verified: only its declaration/docstring) — no mutual-exclusive enum is recomposed downstream. The `.state` partition is eliminated, not relocated.
- **A5 CLOSED (point 6).** `data_identity` includes **block_end** (fixture: same strategy, block_end 100 vs 200 → different fingerprint); S1 vs S3 differ; engine/contract/N1/router/eligibility are separate dimensions. My eleventh (block_end omitted) is closed **at the ve_brain fingerprint** (the measurement-layer `run_hash` is a separate track).
- **Point 7 CLOSED by absence (verified VE's claim).** No internal comparison/leaderboard/selection/aggregation exists in `ve_brain`: the only `sorted(` is an intra-decision regime-name sort; `max/min` in `_ev_core`/`ev_engine` are EV arithmetic; `compare_decisions` (raises) is the sole comparison entrypoint and is never called internally. The package produces decisions, it does not compare them — so require_comparable has nothing internal to guard. **VE's claim is true.**
- **FAIL-4:** re-pin acknowledged (`c111d82` message + strict-geometry INVALID_EXECUTION reason); the measurement contract version/commit is the canonical-evaluator track, verified separately.

## (e) TENTH DIVERGENCE — honest status
Active hunting in **this** artifact (the EV/routing brain) surfaced the **forged-eligibility structural hole** above, not a new numeric measurement divergence. The measurement divergences (6th entry-bar-target, 9th gap-open, the `.state` lead) live on the **canonical_evaluator** track; no new tenth measurement divergence was found here — I will not manufacture one. The structural finding is the fourth instance of the bypassable-guard pattern.

## VERDICT — **VE_HANDOFF_CONDITIONAL** → PASS blocked on one fix
The real path, FAIL-2, A5, point 7, and points 4/5/6/8 all pass; the corrections are real. **PASS requires all eight** — point 2's invariant ("a RANGE strategy cannot produce TRADE") is violable via a matching-id forged `EligibilityDecision`. Close the one defect (carry + bind `requires_true_range` on the candidate; N6 fail-closed independent of the eligibility object) and re-submit; I will re-verify the forged-eligibility fixture and the complete path. **Mandate 2 to AI Trader remains NOT authorized.** A2 and the canonical contract remain independent (my extended suite + zero unexplained divergences + CEO approval).

## HANDOFF → CEO / VE
1. **Blocking:** add `requires_true_range` (or `strategy_family`/`allowed_regimes`) to `DecisionRequest`, bind it into the schema + `regime_fingerprint` (so it cannot be omitted/forged), and make N6 fail-closed on it independent of `eligibility.reason_codes`.
2. **Add the missing test:** matching-id `EligibilityDecision(eligible=True, reason omits range)` for a range strategy → assert `NO_TRADE / TRUE_RANGE_NOT_IDENTIFIABLE`.
3. Re-submit for handoff re-verification; CONDITIONAL holds until then.

Red Team designed no remedy, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
