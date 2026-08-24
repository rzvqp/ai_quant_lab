# Current-Regime CR-1..CR-15 — EXACT CAUSAL REPLAY Before/After Ledger

Mandate: CEO ALPHA-EXACT-CAUSAL-REPLAY (2026-08-23) after VE-CURRENT-REGIME-TEMPORAL-CAUSALITY-REPAIR-001 (commit 91b7415,
`CURRENT_REGIME_CAUSAL_INFRASTRUCTURE_PASS`). Every CR frontier re-run EXACTLY (no retuning) on the repaired `cur_screen.like_at`
/ `cur_data.causal_bucket_asof`. Source: `cur_replay_harness.py` → `cur_replay_manifest_output.txt`. Question: WHAT SURVIVES
WHEN EXECUTED CAUSALLY?

## Before/After table (BEFORE = tainted lookahead; AFTER = causal)

| Frontier | BEFORE (tainted) | AFTER (causal) | class |
|---|---|---|---|
| **CR-13 CRS-1** H4-up-fade short | avgR **+0.4507**, PF 1.87, gate PASS (SURVIVOR); info H4-up P(downFirst) 0.600 dn-up +2.25 | avgR **+0.0669**, PF 1.10, gate FAIL (leave-1yr worst min-partition −0.152); info H4-up P(downFirst) 0.515 dn-up +0.94 | **INVALIDATED** |
| **CR-15** M15×H1 confluence (H1-up&H4-up) | subset avgR **+0.498**, all partitions+, OOS +0.81 (strong) | avgR **−0.034**, D +0.03/C −0.27/O −0.02 | **INVALIDATED** |
| **CR-1 first-pass** short-continuation | NEAR_MISS (CONF +0.067 / OOS +0.123) | current-like ALL negative (short-cont −0.26; reversion −0.10) | **INVALIDATED** |
| CR-1 verify wide-short | REJECTED (tail-dep best10rm −0.226, episode-conc) | +0.074 but **best10rm −0.247** → still REJECTED | **SURVIVES** (rejection) |
| CR-2 lower-high | no edge (P(downFirst)~0.51) | dn-up +0.37, P(downFirst) 0.515 | **SURVIVES** (no edge) |
| CR-3 vol-exp-down (8th false-pos) | dn-up +0.95 concentrated but tail-dep (best10rm −0.203) | dn-up +0.50; trade +0.132 all-partitions+ but **best10rm −0.182** → NOT survivor | **SURVIVES/WEAKENS** (concentration weaker, tail-dep rejection holds) |
| CR-4 capitulation-long | FAIL (OOS −1.24) | up-dn −0.21, P(upFirst) 0.493 FAIL | **SURVIVES** (fail) |
| CR-5 retest-failure | dn-up +0.94 but ordering unchanged (P 0.510) | dn-up +0.85, **P(downFirst) 0.494** (ordering still coinflip), frac 0.88 | **SURVIVES** (ordering-not-improved) |
| CR-6 session ordering ceiling | max robust P(downFirst) **0.541**; trade −0.014 FAIL | **0.526**; trade −0.0415 FAIL | **SURVIVES/WEAKENS** (ceiling ~0.53, still too weak) |
| CR-7 episode-age | weak (0.522) | weak | **SURVIVES** |
| CR-8 conjunction | 0.549 < 0.56 bar FAIL | 0.544 FAIL | **SURVIVES** |
| CR-9 coil-breakdown structural | −0.010, WR 0.541 FAIL | −0.022, WR 0.536 FAIL | **SURVIVES** |
| CR-10 PDL/PDH geometry | on ceiling (~0.51) | P(downFirst) 0.494 / 0.469 (weaker) | **SURVIVES** |
| CR-11 two-sided vol-expansion | breakouts fade (WR 0.34) FAIL | negative | **SURVIVES** |
| CR-12 fade coil-breakout | +0.021 one-sided, NOT survivor | +0.027, WR 0.660, NOT survivor | **SURVIVES** |
| CR-14 divergence LONG | −0.093 FAIL | −0.089 FAIL | **SURVIVES** |

**Tally: 3 INVALIDATED (all were the POSITIVE findings — CRS-1, CR-15 confluence, CR-1 near-miss), 12 SURVIVE (all the NEGATIVE/rejection findings). The lookahead created false positives; it did not hide real edges.** CURRENT_REGIME_SURVIVOR = 0 (causally confirmed, stronger than before).

## §4 Knowledge rebuild — which contaminated claims are causally supported
- **Directional/payoff asymmetry**: PARTIALLY SURVIVES as *info only* but WEAKER (down-EXCURSION dn-up still >0: CR-2 +0.37, CR-5 +0.85; CR-3 concentration +0.95→+0.50) and NOT tradeable (tail-dependent everywhere).
- **Path-ordering / ~0.54 ceiling**: SURVIVES, now ~0.50–0.53 (even weaker) → reinforces "no tradeable current-regime direction".
- **Session / episode-age / range-migration conditioning**: SURVIVE as negatives (all too weak / fail).
- **Cross-scale H4×M15 as an EDGE**: INVALIDATED (CRS-1 +0.067). BUT per CEO §6 cross-scale representations remain OPEN — CRS-1's failure invalidates CRS-1, not the class. Do NOT cite "CRS-1 proved cross-scale works".
- **CRS-1 singularity / "CR classes exhausted"**: the *tradeable-edge* exhaustion SURVIVES (no current-regime survivor exists causally); the "singularity" framing is moot (0 survivors).

**Active knowledge base after replay: CURRENT_REGIME_SURVIVOR = 0; the current regime has NO robust tradeable directional edge (down-excursion asymmetry exists as weak info but is tail-dependent/unbracketable). S5 remains the only independently-validated XAUUSD edge. Multi-regime taxonomy (VE-confirmed causal) unaffected: 0 survivors there too.** Tainted numbers retained in the old ledger for provenance only.
