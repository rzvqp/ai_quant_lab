# RED TEAM — SUITE EXTENDED TO 18 + RE-ATTACK PREP + FOUR-BLOCK COMPLETENESS
### RT-AUDIT-MEAS-0004 · Test 18 (gap-open), the tenth divergence, and the surviving three-block paths
**Date:** 2026-08-13 · **Auditor:** Red Team · **Mandate:** CEO — extend the suite to 18 and prepare the re-attack. Add **Test 18** (entry gaps through stop / through target); verify whether the Statistician's spec (*open beyond TP → exit at entry price, never nominal TP*) **closes** the gap or only **moves** it. **Hunt the tenth.** Verify the **four-block population correction** is complete — *or whether a path still reads three*. Re-attack proper waits for VE's three fixes (MEAS-9, T17, four-block). **No engine modified; no repair; no real data.** Verified on synthetic fixtures + imported source + the live manifest v2.7.65 + the block-consuming code.

## VERDICT — **prep complete; two blocking items stand, plus a tenth divergence and an INCOMPLETE four-block correction.**
1. **Test 18 added** and encoded as canonical expectations (`test_18_gap_open.py`). The Statistician's spec, **as quoted, only covers the TARGET side** → it **MOVES** the gap: the target-gap is fixed, but the economically worse case (a **WIN booked from a gapped-through stop, +0.95R**) **survives**. The spec must be made symmetric (exit-at-entry / no-trade for the **stop** gap too).
2. **Tenth divergence (novel) — MEAS-14:** the R3 **rejection is scenario-invariant** — decided once, outside the scenario loop, from `sig.spread_price` — so BASE and STRESS share **one** rejection population; the CEO's per-scenario R3 components (BASE 0.05 / STRESS 0.08) require **different** floors → **different populations**, which the evaluator's architecture cannot express.
3. **The four-block correction is NOT complete.** **Three** code paths still read three (or fifteen), and the 4th operative block (2022-12→2025-10) is **structurally sealed** by the fail-closed reader. A manifest-internal contradiction remains (the m4 finding says the overlap **is** the 4th discovery block; the reader's contract says the overlap is "**never delivered**").

---

## 1 · CEO DECISIONS REGISTERED (both close prior Red Team flags)
- **`spread_price` = FULL bid-ask.** BASE 0.05 → R3 component 0.05; STRESS 0.08 → R3 component 0.08. **This closes the T12/T13 full-vs-half contradiction I raised** (RT-AUDIT-MEAS-0001/0002). The Statistician's proof — frozen constant `COST = 2 × EFF_SPREAD` — confirms the *old* `effective_spread` was a **half**; the new `spread_price` is the full round-trip. The evaluator's **cost** (R4 = spread + entry_slip + exit_slip, spread once) is consistent with this. ✅
- **Canonical population = FOUR blocks** (2011, 2016, 2020, **2022-12→2025-10**). Results over 3 or 15 blocks are **NON-COMPARABLE**. Registered; the completeness check is §4.
- **Consequence for the CEO's own note:** the full-spread decision means R3's floor term is now **1× spread** (0.05 / 0.08), but the evaluator computes **2× spread** (0.10 / 0.16). This is the manifest's own MATERIAL item ("*~18% R3 rate measured against DOUBLE thresholds — re-measure*") — see §3; my earlier T2/floor flag is thereby **confirmed by the ratified decision**, not merely suspected.

## 2 · TEST 18 (gap-open) — does the spec CLOSE the gap or MOVE it? **It MOVES it.**
Encoded in `red_team/policy_reviews/test_18_gap_open.py` (canonical expectations; runs against any engine).

| case | Statistician spec (as quoted) | current evaluator @82acad9 | canonical-correct |
|---|---|---|---|
| **18A target-gap** (long, open 105 > TP 102) | **covered:** exit at ENTRY 105, net = −cost | exit at nominal TP 102 → **−0.436R** (wrong fill) | exit at entry, net = −cost |
| **18B stop-gap** (long, open 97 < stop 98) | **NOT covered** (quote is TP-only) | immediate "stop" at 98 → **+0.95R (a WIN)** | NO-TRADE / exit-at-entry, **never > 0** |
**Finding:** the quoted rule ("*open beyond TP → exit at entry price*") fixes **18A** but is silent on **18B**. The worse defect — a **positive R credited to a trade that gapped straight through its stop** — is untouched. **So the spec MOVES the gap (closes the target side, leaves the stop side open).** To CLOSE it, the principle must be stated **symmetrically**: *when the open is beyond ANY level (stop or target), you cannot be filled at that level* → for the stop gap, no-trade or exit-at-entry, never a nominal-stop credit. This is the exact condition Test 18B guards.

## 3 · THE TENTH DIVERGENCE — MEAS-14 (novel): the R3 rejection is scenario-invariant
Verified from imported source: the floor is computed **once** (`ms = minimum_stop_distance(sig.spread_price, sig.atr)`) and the `Rejection` returns **before** the `for sc in scenarios` loop. So:
- A signal is rejected **for all scenarios or none** — the eligible population is **identical** across BASE and STRESS.
- The floor uses **`sig.spread_price`** (one context value), **not** the scenario spread. Under the CEO's decision (BASE 0.05 / STRESS 0.08 as the R3 component), a signal with stop-distance **0.065** should be **executed in BASE** (floor 0.05) and **rejected in STRESS** (floor 0.08) → **different populations per scenario.** The evaluator returns **one** outcome for both and **cannot express** this.

This is distinct from — and **not** — the R3 `2×spread` magnitude, which the manifest **already** flags as MATERIAL ("*~18% R3 rate measured against DOUBLE thresholds — re-measure*"). **In fairness I record that the 2× double-count is corroboration of a known open item, not a new discovery.** MEAS-14 (rejection cannot vary by scenario at all) is the novel structural point the manifest does not raise. Both must be fixed for BASE/STRESS to be honest, separable populations.

## 4 · FOUR-BLOCK CORRECTION — **INCOMPLETE. Three surviving paths + a manifest contradiction.**
The manifest v2.7.65 **declares** four operative discovery blocks (`context_derived_htf.m15_v2_discovery_blocks`, and `m4_block_count.finding` = "*the manifest's OPERATIVE list holds FOUR discovery blocks, not three*"). But the 4th (2022-12→2025-10) is inherited via `overlap_with_M15`, **not** a `regime_segments` discovery_range. The consuming code was checked directly:

| code path | what it delivers | why |
|---|---|---|
| `edge_research/split_manifest.py :: segmentation_plan` | **3** discovery ranges | builds `discovery` only from `regime_segments` with a `discovery_range` (bear/bull/correction). Its own docstring: "**the M15_v2 overlap … SEALED by default … never delivered.**" The 4th block is sealed by design. |
| `code/run_four_regime.py` | **3** regimes | line 74 iterates `regime_segments` minus `TOO_SHORT_FULLY_SEALED`; `expected` bar-counts are exactly `{bear, bull, correction}`; the leaderboard is "**3** regimes"; the line-80 assert would **fail** if a 4th were added. Named "four_regime", computes three. |
| `edge_research/_screen.py :: derive_blocks` | **~15** | gap-based (>72h), **manifest-blind** — the CEO's "15". |

**Enumerated regime_segments (verified):** seg0 bear 2011-07→2013-09, seg1 bull 2016-01→2018-04, seg2 correction 2020-08→2021-09 (three with a discovery_range); seg3 `bull_partial` = `TOO_SHORT_FULLY_SEALED` (no discovery_range). The 4th operative block **2022-12→2025-10 is not among them** — it is the `overlap_with_M15` range (2022-12→2026-07), and `segmentation_plan` seals it.

**Manifest-internal contradiction (blocking):** `m4_block_count.provenance_of_the_fourth` = "*overlap_with_M15 … Inherits M15's discovery/embargo/sealed classification VERBATIM*" (i.e. the overlap **is** the 4th discovery block); `segmentation_plan`'s contract = the overlap is "**never delivered**." **Both cannot hold.** Until the reader is changed to compute the overlap's inherited M15-discovery sub-range, no code path delivers four — and `run_four_regime`'s hardcoded three-regime bar-accounting will actively reject a fourth.

**Consequence:** every persistence/leaderboard number produced by `run_four_regime` (including **CAND-0037**'s per-regime persistence) is on a **THREE-block** population that discards the newest, largest ~3 years — **non-comparable** to a four-block figure by the CEO's own rule. The freeze is correctly holding these as non-final.

## 5 · RE-ATTACK CHECKLIST (armed; fires when VE delivers the three fixes)
When VE lands MEAS-9, T17, and the four-block population, I will verify — not trust — each:
1. **MEAS-9 (gap guard):** run Test 18A **and 18B**; confirm the stop-gap is no longer a win (no-trade or exit-at-entry) **and** the target-gap exits at entry, not nominal TP. Confirm the guard is symmetric (both levels, both directions), and add a monkey-patch reintroduction to prove the test actually fails if the guard is removed.
2. **T17:** confirm (a) a comparison function **raises** on config_id mismatch (not just a comment), and (b) config_id payload now includes **symbol + date range + block-manifest id** (today it is data-blind). Re-run the data-blindness probe.
3. **Four-block population:** confirm `segmentation_plan` delivers **four** (the overlap's inherited discovery sub-range is materialised), `run_four_regime`'s `expected`/leaderboard move to four with correct bar-accounting, and **no** path (`derive_blocks` included) silently reads three or fifteen. Re-report every `n` and flag any figure still on 3/15 as non-comparable.
4. **MEAS-14 + R3 1×:** confirm the floor uses **1× the scenario spread** and that rejection is evaluated **per scenario**, so BASE/STRESS are separable populations; re-measure the R3 rate against the corrected single thresholds.
5. **Suite = 18** against **every** engine (SCREEN/MSTRAT/DEMO/canonical_evaluator) with matching provenance before any ratification.

## 6 · FREEZE
**Holds.** No leaderboard, no economic elimination, and **no S3 flip** is definitive until every engine passes the **18** with matching provenance **and** the population is genuinely four blocks. CAND-0037's three-block persistence and any BASE-only S3 number are explicitly **non-final** under this freeze.

## HANDOFF → CEO / Statistician
1. **Make the gap spec symmetric (blocking):** "*open beyond any level → cannot fill at that level*" — the stop-gap must not book a win (Test 18B). As quoted, the fix is TP-only.
2. **Four-block (blocking):** resolve the manifest contradiction — either `segmentation_plan` materialises the overlap's inherited discovery sub-range (→4) or the m4 finding is wrong; **and** re-point `run_four_regime` off its hardcoded three regimes. Verify `_screen.derive_blocks` (gap-based, 15) is reconciled to the manifest or explicitly quarantined.
3. **R3 (blocking with the above):** 1× the (full) spread **and** per-scenario evaluation (MEAS-14), then re-measure the ~18% rate against corrected thresholds.
4. **T17:** enforce comparison-on-match and extend config_id to symbol/period/block.
5. **Keep the freeze;** re-attack is armed for the moment VE delivers.

Red Team designed no remedy, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
