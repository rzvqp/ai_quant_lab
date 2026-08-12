# RED TEAM — TARGETED RE-ATTACK · wp5b bus fixes (E2E-L1 / E2E-L2 / E2E-U1)
### RT-CODE-A-0016 · Diff `d782401 → ad8b586` only (RT-AUDIT-CHAIN-0002 remediation)
**Date:** 2026-08-10 · **Auditor:** Red Team · Prior verdict RT-AUDIT-CHAIN-0002 = PASS_WITH_LIMITATIONS; contract/cascade/identity/audit/lookahead already verified clean — **not re-run.** Only the three fixes. **No real-data run; verified on synthetic + the repo's own tests + a monkey-patched reintroduction; nothing modified; no remedy.**

## VERDICT — **PASS_WITH_LIMITATIONS** (nothing blocks Shadow; two minor disclosures).
The blocking item **E2E-L1 is completely closed and — crucially — GUARDED by a regression test that I proved actually fails when N4 is reintroduced.** E2E-L2's guards fire on the production path. S2 is wired 3/3. The residuals are minor: the S2 recognizer is a filler with a mismatched label (the CEO's suspicion, confirmed), the E2E-L2 guards are procedural (bypassable via direct construction), and the premium+short quadrant has no policy.

---

## TARGET 1 — is E2E-L1 completely closed, or does N4 still reach the decision? **COMPLETELY CLOSED (every path checked).**
- **Every recognizer reads only N1/N2/N3.** `policy_pdl_sweep_reversal`, `policy_pdl_failed_break_fade`, `policy_pd_close_breakout` all use `_nearest_zone` (N3) + `_bias_direction` (N2) — **grep-verified none touches `confirmations`/`_first_confirmation`** (`_first_confirmation` was deleted). ✅
- **`inputs_hash` covers only N1/N2/N3.** `_inputs_hash_n1n2n3` hashes `regime/bias/zones` schema (or `U:reason` for Unavailable) — **verified it references no `confirmation`/N4** and does reference regime+bias+zones. ✅
- **`decide()` computes the outcome from `matches` (N1/N2/N3) + edge**, then packs N4 into `EvidenceRecord` only; the `DecisionRecord` carries `decided_at = zone_hit`, `inputs_hash` (N1/N2/N3). N4 is type-isolated in the evidence branch. ✅
- **Numeric invariance (verified):** same N1/N2/N3 with N4 ∈ {ACCEPTANCE, UNDETERMINED, Unavailable} → **1 distinct decision, 1 distinct inputs_hash**, `decided_at=5 (zone_hit)`, `attached_at=9 (i0+W+1)`. The 5 E2E-L1 regression tests pass. **No path from N4 to the decision.**

## TARGET 5 (the one that matters most) — is there a test that FAILS if N4 is reintroduced? **YES — PROVEN a real guard.**
`test_e2e_l1_decision_and_inputs_hash_exclude_n4` asserts `len({decision})==1` and `len({inputs_hash})==1` across the three N4 variants; `test_e2e_l1_validated_edge_trade_is_also_independent_of_n4` proves it on the **TRADE** path too. **I monkey-patched `_inputs_hash_n1n2n3` to reintroduce N4** and re-ran the guard test: it **FAILED with an AssertionError** (unpatched it passes). So the regression test is a **real guard, not decorative** — a future edit that lets N4 back into the decision is caught at test time. **This closes the CEO's central concern: the defect cannot be silently reintroduced.** ✅

## TARGET 2 — did moving to zone_hit introduce another defect? Is the new (zone.attribute + bias) recognition a faithful generalization? **No defect; the shift is necessary and coherent for S1/S16.**
The recognizers now key on `zone.attribute` (discount/premium, N3) + `bias direction` (N2) — **forced** by the decision-clock fix (N4 isn't observable at zone_hit). The mappings are economically coherent: **S1** = discount(support)+LONG → reversal up; **S16** = premium(resistance)+LONG → breakout up. **No double-match** is possible (bias direction is single-valued, so discount can't be both LONG and SHORT). The **semantic shifted** from *confirmed* (N4 absorption/acceptance) to *predicted* (bias+location) recognition — but that shift is **required** to decide at zone_hit, and is the correct direction. **Coverage gap (not a defect):** the **premium+SHORT** quadrant has **no policy** → such a setup always NO_MATCH → NO_TRADE (an incomplete library, not a bug).

## TARGET 4 — is the S2 recognizer faithful to the S2 reclaim family, or a filler? **A FILLER with a mismatched label (the suspicion is correct).**
`policy_pdl_failed_break_fade` = **discount + SHORT**. The classic **S2 "reclaim"** is: a level is falsely broken, the break fails, price **reclaims** → trade in the reclaim direction. A failed break of **support** (discount) reclaims **UP (long)** — which is already S1. So **discount+SHORT is not the reclaim setup**; it is the leftover (discount, SHORT) quadrant, occupied to reach 3/3, with a "fade the failed break, short" rationale that **does not match** a support reclaim (a support reclaim is bullish). The state itself (discount + short bias = bearish continuation through support) is coherent, but **the S2-reclaim label is inaccurate** — it is a partition-filler, not a faithful S2 generalization. **Low severity** (edge=False → no trade; and it reads only N1/N2/N3, so it does not threaten E2E-L1), but the CEO's read is right. (E2E-U1.)

## TARGET 3 — are `_assert_cut` / `_require_valid` enforced on ALL paths, or just the main one? **Fire on the production path (verified), but procedural — bypassable via direct construction.**
- **`_assert_cut`** is called for **all four timeframes** at the top of `build_market_state`; **verified it raises** on a future bar (`t[-1]=999 > as_of=5`). Not decorative. ✅
- **`_require_valid`** is called for **N1/N2/N3** (regime/bias/zones); **verified it raises** on a stale level (`valid_until 3 < as_of 5`). ✅ **Not applied to N4** (evidence-only — defensible).
- **Bypass:** both live in `build_market_state` (the intended assembly entry), **not in the `MarketState` constructor** — so a caller that constructs `MarketState` directly (as the unit tests do) **bypasses** them. The guards protect the **production path** but are **procedural, not structural** — a direct-construction path is unguarded. Since `build_market_state` is the only intended entry, this protects real use, but the enforcement is not type-level. (E2E-L2 residual.)

## SEVERITY
- 🟡 **E2E-U1 · S2 recognizer is a filler** — `discount+SHORT` labeled as an "S2 reclaim/fade" it is not (reclaim is bullish); occupies the leftover quadrant to reach 3/3. Low severity (edge=False; reads only N1/N2/N3).
- 🟡 **E2E-L2 residual · guards are procedural** — `_assert_cut`/`_require_valid` fire in `build_market_state` (verified) but are bypassable via direct `MarketState` construction; `_require_valid` not applied to N4.
- 🟡 **Coverage · premium+SHORT quadrant has no policy** — such setups always NO_TRADE (incomplete library, not a bug).

## WHAT SURVIVES (verified)
**E2E-L1 completely closed:** all three recognizers + `inputs_hash` + `decide()` exclude N4 (grep + numeric); decision/inputs_hash invariant to N4; `decided_at=zone_hit`, `attached_at=i0+W+1`; **the regression guard PROVEN to fail on N4 reintroduction.** **E2E-L2:** `_assert_cut` raises on future bars, `_require_valid` raises on stale levels (both verified). **E2E-U1:** S2 wired (3/3 policies). The 89-test suite passes; the 5 targeted regression tests pass.

## VERDICT — **PASS_WITH_LIMITATIONS.** The three fixes achieve their purpose and the one that matters — E2E-L1 — is **fully closed with a working, proven regression guard**, so the defect cannot be silently reintroduced. **Nothing blocks Shadow.** The disclosures are minor: the S2 recognizer is a partition-filler with an inaccurate "reclaim" label (not a faithful S2), the E2E-L2 guards are procedural (bypassable off the `build_market_state` path), and the premium+short quadrant is uncovered.

## HANDOFF → CEO / Statistician (before/with Shadow)
1. **E2E-L1 is closed and guarded** — proceed; the guard test protects against silent reintroduction.
2. **E2E-U1:** relabel S2 (`discount+SHORT` is a bearish continuation, not a reclaim) or replace it with a genuine reclaim recognizer; note the premium+short coverage gap.
3. **E2E-L2:** if strictness matters, move `_assert_cut`/`_require_valid` into the `MarketState` construction (structural, not just in `build_market_state`), and consider validating N4's window too.
4. All three fixes verified firing; the DoD + Shadow-readiness on the decision-clock axis hold.

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
