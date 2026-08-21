# ALPHA COMBINED DISCOVERY WAVE — RANGE + BREAKOUT + FAILED + SWEEP + TREND_DOWN/SHORT

**Status:** `ALPHA_COMBINED_DISCOVERY_COMPLETE_AWAITING_STATISTICIAN_REVIEW`
**Authorization:** Red Team `RANGE_STATE_HANDOFF_PASS` (RT-RANGE-0002, `898e1b9`); Statistician FINAL `d0d08c1`; manifest v2.7.77 / config `aec8f07`.
**Diagnostic screening — no statistical significance declared. No RATIFIED / PROMOTED / LIVE. LIVE_SHADOW & broker untouched.**

## Headline result
Under the **ratified RANGE primary rule** (`n_touch=2, tol_atr=0.25, er_max=0.40, d_min=96 bars, n_acceptance=2, width_filter=off, RANGE_STATE_OVER_TREND_PAUSE`),
**XAUUSD M15 almost never forms a qualifying range over its entire 355,696-bar history (2011→2026).** The
longitudinal layer is correct and reachable, but the tradeable events are vanishingly rare on this instrument,
so **no RANGE or breakout family can be screened** — an honest negative result. TREND_UP long remains the only
regime with survivors; TREND_DOWN short has none.

---

## 1. Installed version + SHA proof
`ve_n1_replay 0.2.0`, wheel SHA-256 `04b96a8b78b2d09bd8b54bd8044058282c6ab24bf2ac0f2aaec6c1f7a278786f` (physically
re-hashed, exact match), delivery `3577026`/build `1dc355b`. Installed from `site-packages` in isolated venv
`.alpha_n1_venv`; ve_brain `0.1.3` (`edd208ad…`) pin intact; detector `61cbd58`; ve_tower NOT importable; AI Trader
main/tower venvs untouched; **bidirectional rollback 0.1.1↔0.2.0 demonstrated**.

## 2. Registry before/after
Before: 355 records. After: **361** (+6 F1–F6 families registered; 44 breakout records relabeled in place, not duplicated).

## 3. n_generated_total before/after
**357 → 363** (+6 for the six genuinely-new RANGE economic mechanisms F1–F6, monotonic, once). `m_inference`
**untouched at 26** (Statistician's; reported for ruling, not self-assigned). `n_guards` separate = 118.

## 4. Hypothesis count vs evaluation-run count
Hypotheses (economic): 363. Evaluation-runs this wave: 44 breakout remaps (new `evaluation_run_hash`, HSF preserved)
+ 6 F-family registrations = 50 new run identities; the 355 canonical NET runs from the prior wave are unchanged.

## 5. Mapping of the 44 breakout (longitudinal remap)
All 44 `BREAKOUT_TRANSITION` hypotheses (28 `bos` + 16 `bos_retest`) remapped to the longitudinal events:
`bos → BREAKOUT_ACCEPTED`, `bos_retest → BREAKOUT_RETEST`. **HSF preserved**, new `evaluation_run_hash` (economic rule
realized exactly by the new event → no new ID, per §3 of the mandate). Prior label `REGIME_UNREACHABLE` (static
BREAKOUT_TRANSITION = 0 bars) → **`EVENT_REACHABLE_BUT_TOO_RARE`**: BREAKOUT_ACCEPTED and BREAKOUT_RETEST each fire
**exactly 1 time in 355,696 bars** → n=1 ≪ 30, cannot screen. Full mapping in `combined_wave_records.json`.

## 6. Duplicate tombstones / supersedări
16 duplicate tombstones unchanged. No new supersedes (breakout HSF preserved; F1–F6 are new, not supersedes).

## 7. Configurations evaluated
44 breakout remaps + 6 F-families + F7 audit = 51 wave records. (RANGE grid is sensitivity-only and was NOT
expanded into independent p-values, per the mandate.)

## 8. Distinct economic mechanisms
This wave adds **6** distinct RANGE mechanisms (F1–F6) + the breakout-longitudinal cluster (2 sub-clusters:
accepted, retest). All disjoint from the trend mechanisms.

## 9. Results on the four ratified blocks
The RANGE events are so sparse (see §11) that no per-block screening is possible for RANGE/breakout. Trend results
(per block) are the prior canonical rerun's (`reports/n1_rerun/`), unchanged.

## 10. Survival per variant/cluster
RANGE/breakout: **0 surviving variants** (all EVENT_TOO_RARE). Trend clusters (unchanged from canonical rerun):
TREND_UP|pullback 34/57, |continuation 22/35, |momentum 16/35 survive; TREND_DOWN/COMPRESSION/BREAKOUT 0.

## 11. RANGE occupancy + event counts (full 355,696-bar history)
`replay_batch` ran **twice, byte-identical** (2068 s, 5.8 ms/bar, O(n)); zero-lookahead OK.

| metric | value |
|---|---|
| ESTABLISHED bars | **23** / 355,696 (0.0065%) |
| FORMING bars | ~355,673 |
| RANGE_MID (F7 guard) | 118 |
| BREAKOUT_CANDIDATE | 1 |
| BREAKOUT_ACCEPTED | 1 |
| BREAKOUT_RETEST | 1 |
| RANGE_HIGH_REJECTION | **0** |
| RANGE_LOW_REJECTION | **0** |
| FAILED_BREAKOUT | **0** |
| LIQUIDITY_SWEEP_REVERSAL | **0** |

**Genuine, not a bug** — verified across three independent eras (fresh engines): 2011-12 → 23 ESTABLISHED; 2017-18 →
0 ESTABLISHED (a few singletons); 2024 → 1 ESTABLISHED. Gold trends; the strict efficiency+duration+touch rule is
almost never satisfied on M15.

## 12. ACCEPTED vs FAILED disjoint populations
`accepted & failed on the same bar = 0` (verified) — the machine's mutual exclusion holds: BREAKOUT_ACCEPTED and
FAILED_BREAKOUT are disjoint by construction. (FAILED_BREAKOUT count itself = 0 here.)

## 13. F7 / n_guards audit
`RANGE_MID_NO_ENTRY` emitted **118** times; `entry_decision.permitted = False` (refusal by construction); zero
entry / zero candidate / zero p-value / zero broker reach; **not** in `m_inference`; counted in the separate
`n_guards` register; survives snapshot/restart. F7 is a SAFETY_GUARD, not a strategy or hypothesis.

## 14. TREND_DOWN / SHORT results
The SHORT mechanisms (pullback/continuation/momentum SHORT) already exist in the registry (127 TREND_DOWN
hypotheses) and were evaluated canonically. Result: **no survivor** — 106 `NET_STRUCTURALLY_NEGATIVE_GROSS` + 21
`ARCHIVE_INSUFFICIENT`. No SHORT edge on XAUUSD M15 under canonical N1. No new clones generated (would double-count).

## 15. Comparison with G0037 / G0184 / G0059 (TREND_UP long)
Unchanged (canonical rerun): G0037 pullback `CANONICAL_PROVISIONAL_SURVIVOR` NET_BASE +0.271; G0184 continuation
`CANONICAL_PROVISIONAL_SURVIVOR` +0.129; G0059 momentum `RECENT_REGIME_NET_PROVISIONAL` +0.116. These remain the
only survivors across the entire program; the RANGE/breakout/short wave adds none.

## 16. GROSS survivors (this wave)
None — every RANGE/breakout family is EVENT_TOO_RARE (n ≤ 1), below any screening threshold.

## 17. NET survivors
None this wave. (Official cost model `AI_TRADER_SHADOW_COST_MODEL_v1` RATIFIED and ready, but there is nothing with
enough events to compute NET on.)

## 18. AWAITING_COST_QUEUE
Unchanged from prior wave (the 62 gross survivors already received canonical NET in the prior rerun). No new
AWAITING_COST entries — the wave produced no gross survivor.

## 19. OOS access count
**0.** SEALED 2025-11+ never loaded (official pre-holdout loader). Range ledger built on the full ratified
discovery population only.

## 20. Restart / dedup / checkpoint evidence
Range ledger built via the O(n) incremental engine; `replay_batch` reproduced identical results across two runs
(determinism). Singleton enforced (all duplicate builder processes killed before each authoritative run). Wave
finalizer is idempotent. F7 guard verified to survive snapshot/restart (contract `test_range_state.py`, 34 tests).

## 21. Complete list of surviving mechanisms (not a top-N)
**Program-wide surviving mechanisms (all PROVISIONAL, PENDING Statistician + Red Team):**
1. TREND_UP | pullback — rep G0037, NET_BASE +0.271 (34/57 variants survive)
2. TREND_UP | continuation — rep G0184, +0.129 (22/35)
3. TREND_UP | momentum — rep G0059, +0.116 (16/35)

**This wave contributes ZERO new surviving mechanisms.** RANGE (F1–F6), breakout-longitudinal, TREND_DOWN/SHORT,
COMPRESSION: no survivor. Executive shortlist ≤1 rep/mechanism; the full surviving set is exactly the three above.

---

**Multiplicity (reported to Statistician, not self-ruled):** +6 new economic mechanisms (F1–F6) → n_generated_total
363; `m_inference` stays 26 (Statistician's); F7 in `n_guards`=118, never in `m_inference`. This wave is diagnostic;
no p-value, no significance, no edge declared. Nothing sent to VE Strategy Catalog; no AI Trader integration
requested. Statistician verifies results; Red Team verifies pipeline & integrity.
