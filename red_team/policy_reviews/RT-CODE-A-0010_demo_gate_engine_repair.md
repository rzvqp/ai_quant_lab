# RED TEAM — CODE RE-ATTACK · DEMO gate engine repair
### RT-CODE-A-0010 · Target: `demo_gate_engine/` @ `06e4e00` — the D1/D2/R1/R2 fixes from RT-CODE-A-0005
**Date:** 2026-08-03 · **Auditor:** Red Team · **Gates live wiring** (four policies waiting on zero trades). Checklist only: lookahead, leakage, circularity, ambiguity, overfitting, hidden params, reproducibility. **No data run · nothing modified · no remedy.** Numeric re-verification on synthetic bars (engine imported read-only), incl. the exact fixture that exposed D1.

## VERDICT — **PASS_WITH_LIMITATIONS.**
All four defects (D1, D2, R1, R2) are genuinely fixed and **independently re-verified** — the D1 fix is confirmed on the very fixture that exposed it, long/short symmetric; D2's naming collision is gone with no stale consumer; R1's subsumption argument is sound; R2's F3 assert works and makes the dynamic `open_[j+1]` bounds-safe. The corrected fixture now asserts the **right result**, not "not-INVALID". 29 tests pass. The residual **limitations are caller-contract preconditions the pure function cannot enforce** — not engine-logic bugs.

---

## D1 — S1 on the ENTRY BAR at all trades — **FIXED, VERIFIED, SYMMETRIC.**
New logic (both engines): after the entry guards, `entry_bar_hitS = low[ei]≤exec_stop (long) / high[ei]≥exec_stop (short)`; if breached → **STOP at `ei`** for non-floored (the fix), **INVALID** for floored (unchanged narrow case).
- **Re-verified on the exposing fixture** (long, `open=100`, `stop=99.0` non-floored, entry-bar `low=98.9`, next bar `high=105`): the engine now returns **`STOP`, `exit_idx=1`, `exit_price=99.0`, `net_R=−1.000`, `stop_at_entry_bar`** — a **loss**, where before the fix it returned `TARGET` (win). ✅
- **Long/short symmetry (the CEO's specific target) — PASS.** Constructed a breaching entry bar on each side: long → STOP@1 px 99.0 net_R −1; short (`stop=101`, entry-bar `high=101.2`) → STOP@1 px 101.0 net_R −1. **Identical reason/order/idx/sign.** Boundary-inclusive (`low==exec_stop` → STOP, worst-case). No asymmetry.
- **No new false-stop:** a non-breaching entry bar proceeds normally to the scan (verified: stop lands at the real later bar, not spuriously at entry). The entry-bar **target** is still ignored (S3, conservative) — no optimism introduced.
- **New-defect hunt — none found.** The entry-bar stop fills at `exec_stop_price` (a wick to the stop; a gap-open beyond the stop is pre-empted by the NO_TRADE structural-stop guard for non-floored, and by the floored-gap INVALID for floored). The order of checks (INVALID → NO_TRADE → entry-bar stop → scan) is worst-case-correct on every branch.

## D2 — `day_end_idx` → `time_stop_idx` — **naming separation COMPLETE; value live-validity is now a caller contract.**
- The field is renamed to `time_stop_idx` with **one meaning** ("last scan bar = force-close limit; the caller decides what it represents"). Both engines use it consistently; **grep confirms no consumer uses the old `day_end_idx`** (it survives only in explanatory comments).
- **But the rename fixes the NAME collision, not the VALUE's live-validity.** The dynamic engine's docstring makes the caller responsible ("granița de bloc, orizont de N bare etc."). **If the CAND-0002 caller passes a BLOCK boundary, Finding H′ returns** — a block is a discovery-data construct, so a block-boundary force-close never fires on a live forward account. The engine cannot detect this. **So for live wiring, the caller MUST pass a live-valid `time_stop_idx` (a real forward N-bar horizon or day boundary), not a block boundary.** The engine is now *honest* about the contract; it does not *enforce* it. (Limitation, not a defect.)

## R1 — the third INVALID condition — **DECLARED SUBSUMED, and the argument is VALID.**
- The literal clause-(3) guard (`"ambiguous_same_bar_fill"`, `entry ≤ exec_stop` for long) is **tautologically false**: `exec_stop = entry − d·dist` with `dist>0`, so `entry ≤ exec_stop` can never hold. It is a **fail-closed no-op** for a malformed signal — verified it never fires on valid inputs.
- **The real same-bar ambiguous case is resolved WORST-CASE, not marked INVALID** — and that is the sound subsumption. On the entry bar the engine checks **only the stop** (D1, stop-first) and **ignores the entry-bar target** (S3); a same-bar stop→**STOP** (a loss), the target never credited. So the prereg's "entry/exit inside the same bar with ambiguous fill" is **resolved to a STOP (conservative)** rather than excluded. Resolving worst-case is **at least as conservative** as marking INVALID → the argument holds. There is **no unresolved same-bar ambiguity** (checked: stop∧target on the entry bar → STOP). ✅ *(Minor: the dead clause-(3) is labeled as if it does something; harmless, fail-closed.)*

## R2 — F3 precondition — **FIXED, VERIFIED; also closes the dynamic `open_[j+1]` risk.**
- `if not (0 ≤ entry_idx ≤ time_stop_idx ≤ n−1): raise ValueError` present in **both** engines. Verified: `entry_idx>time_stop_idx`, `time_stop_idx>n−1`, `entry_idx<0` all **raise** (fail-closed, not a silent bad trade or IndexError).
- The dynamic engine's `open_[j+1]` (RT-CODE-A-0005 R7) is now **bounds-safe by construction**: the `boundary` (j==scan_end) branch returns before the `opposing` branch, so `opposing` only fires at `j<scan_end` → `j+1 ≤ scan_end = time_stop_idx ≤ n−1` (guaranteed by the F3 assert). Verified in bounds. ✅

## CORRECTED FIXTURE — **asserts the CORRECT result, not merely "another".**
`test_same_entry_bar_breach_unfloored_is_STOP_not_invalid` now asserts `exit_reason==STOP`, `exit_idx==1`, `exit_price==99.0`, **`net_R<0`** (a loss) and `stop_at_entry_bar` — explicitly noting the old test "verifica doar `!= INVALID` și codifica eroarea D1". Plus new dedicated D1 tests (unfloored-STOP, short-symmetry, no-breach-proceeds). **The masking is removed.** ✅

## CHECKLIST
- **Lookahead — PASS.** The per-trade evaluator reads only bars `[ei, time_stop_idx]`; `open[ei]` is the first tick, so `low/high[ei]` are post-entry; scan strict from `ei+1`; F3 caps at `n−1`. No future beyond the trade window.
- **Leakage — PASS.** Pure per-trade function; no cross-trade state (`simulate_demo_trades` maps independently).
- **Circularity — N/A** (execution evaluator; no probability/selection feedback).
- **Ambiguity — minor.** The tautologically-dead clause-(3) carries an "ambiguous_same_bar_fill" label though it never fires (harmless).
- **Overfitting — N/A** (no fitted parameters).
- **Hidden params — one carried (U1).** `K_SPREAD=2 / K_TICK=5 / K_ATR=0.10` are still hardcoded copies of `MIN_STOP_FLOOR_PREREG` (RT-CODE-A-0005 U1) — a silent-divergence hazard if the prereg changes. **Tick is correctly a PARAMETER** (`tick_size` passed in) — the engine does not hardcode 0.1; but the caller must pass the **correct 0.01** (RT-CODE-A-0007), else the S2 floor is 10× off. Caller contract.
- **Reproducible — PASS.** Deterministic pure function; 29 tests (22 pdh + 7 dynamic) pass; mypy clean; all my numeric checks reproduce.

## LIMITATIONS (all caller-contract; none an engine-logic bug)
- 🟠 **DR-L1 · `time_stop_idx` live-validity is unenforced** — a block-boundary value re-introduces Finding H′ (never fires live). **Critical for CAND-0002 live wiring:** the caller must pass a live-valid horizon.
- 🟠 **DR-L2 · `tick_size` correctness is unenforced** — the engine parameterizes the tick (good), but the caller must pass 0.01 (per RT-CODE-A-0007), not the research 0.1, or the S2 floor is 10× too wide.
- 🟡 **DR-U1 · `K_SPREAD/K_TICK/K_ATR` hardcoded copies** of the prereg (carried from RT-CODE-A-0005 U1) — divergence hazard.
- 🟡 **DR-U2 · Clause-(3) INVALID guard is tautologically dead** (fail-closed no-op) — harmless but misleadingly labeled.

## VERDICT — **PASS_WITH_LIMITATIONS.** The engine's own four defects are fixed and verified; live wiring may proceed **provided the caller honors two contracts the engine cannot enforce: a live-valid `time_stop_idx` (not a block boundary — else Finding H′ returns, esp. CAND-0002) and the correct `tick_size=0.01` (else the S2 floor is 10× off).** With those honored, S1 (entry bar + all collisions), S2, S3, the three INVALID conditions, and F3 are all correct. The masking fixture is repaired.

## HANDOFF → CEO (unblock decision)
1. **DR-L1 (highest):** before wiring CAND-0002 (dynamic exit), confirm its caller passes a **live-valid `time_stop_idx`**, not a block boundary — otherwise the force-close never fires live.
2. **DR-L2:** confirm every caller passes **`tick_size=0.01`** (the RT-CODE-A-0007 correction), not 0.1.
3. **DR-U1/U2:** collapse the hardcoded prereg constants to one source; drop or relabel the dead clause-(3).
4. With DR-L1/L2 confirmed, the gate engine is safe to wire — the four RT-CODE-A-0005 defects are closed.

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
