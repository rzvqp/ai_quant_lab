# ALPHA_RANGE_FRONTIER_CONCLUSION — RANGE vNext lifecycle information frontier = BOUNDED_NEGATIVE

Mandate: does the RESEARCH-RATIFIED RANGE LIFECYCLE vNext (multi-candidate) expose forward-path information that is causal, cross-era, cost-material, and INDEPENDENT of S5? Information-first; RANGE vNext used **read-only, unmodified** (`ve_n1_replay` @ `fa36324`, config_id `3f2f7ba6…` runtime-guarded, M15-only, zero-lookahead). Evaluated against the PREDECLARED criteria in `ALPHA_RANGE_FRONTIER_CONTRACT.md` (fixed before any forward path was seen). Atlas: `range_extract.py` (per-era read-only extraction) + `range_atlas2.py`. Populations: b0(2011-13)/b1(2016-18)/DEV(2021-23)/CAL(2024) M15, authorized, gap-safe.

## Phase 1 — atlas (well-populated, causal)
Events fired at healthy rates across all eras (per era: OK_RANGE_MACRO ~130-610, BREAKOUT_ACCEPTED ~50-290/side, SWEEP_CONFIRMED ~80-540/side, EPISODE birth ~390-1740; up to 3-4 concurrent candidates). vNext multi-candidate machinery is active and real. `LIQUIDITY_SWEEP_REVERSAL` with an `upper` boundary never fired (SWEEP_REV_up n=0) — the reversal channel is sparse.

## Phase 2/3 — forward-path directional asymmetry (asym70 = P(+70/-50 implied dir) − P(+70/-50 opposite))
| event | implied | b0 | b1 | DEV | CAL | verdict vs predeclared bar |
|---|---|---|---|---|---|---|
| BREAKOUT_ACCEPTED upper | L | +0.03 | +0.01 | +0.03 | +0.07 | sign-stable but **IMMATERIAL** (<0.05 in 3/4); = gold long-bias, Asia-heavy |
| BREAKOUT_ACCEPTED lower | S | −0.12 | −0.02 | −0.01 | −0.02 | material only b0 (bear) → era-dependent |
| SWEEP_CONFIRMED upper | S | −0.12 | −0.21 | **+0.13** | +0.07 | **SIGN REVERSAL** (short 2011-18 → long 2021-24) = era-trend leakage |
| SWEEP_CONFIRMED lower | L | −0.15 | +0.01 | −0.00 | +0.11 | sign-flips, opposite implied in b0 |
| LIQ_SWEEP_REVERSAL lower | L | −0.17 | +0.04 | +0.00 | thin | sign-flips |
| OK_RANGE_MACRO (neutral) | — | −0.07 | −0.01 | +0.04 | **+0.20** | era-trend (bear-lean → bull-lean) |
| EPISODE birth (neutral) | — | −0.03 | +0.03 | +0.02 | — | ~0, no information |

## Verdict — BOUNDED_NEGATIVE
**No RANGE vNext lifecycle event meets the predeclared bar** (material ≥0.05 asymmetry, same-sign across all eras). The events' directional asymmetry **amplifies the era's secular trend** (short-lean in the 2011-2018 bear-ish eras, long-lean/flip in the 2021-2024 bull) rather than creating its own cross-era-stable direction — the exact R20 root-cause signature, now reproduced through the richer multi-candidate lifecycle. The clearest case, SWEEP_CONFIRMED-upper, is a clean sign reversal (−0.21 b1 → +0.13 DEV). The only sign-stable event (BREAKOUT_ACCEPTED-upper → long) is immaterial and reflects gold's long bias (Asia-heavy, not S5's NY channel).

**Consequences (predeclared null clause honored):**
- The RANGE lifecycle adds **no independent cross-era directional information** beyond what raw price already exposes; it inherits/amplifies era-trend. Do NOT rescue (per contract + CEO).
- **Phase 4 (Market Mode) not pursued**: the failure mode is era-trend *dependence* (a cross-era phenomenon); MARKET_OPERATING_MODE_V1 is a within-era conditioner and cannot repair cross-era sign reversal. Adding it would be a rescue, forbidden.
- **Phase 5 / S5-independence not reached**: nothing cleared the information bar, so there is no candidate to convert or to test for S5-redundancy.
- Value retained: RANGE lifecycle STATE (CONFIRMED vs WEAKENING vs trend) remains a potential non-directional structural CONTEXT/filter, but it is not a standalone directional edge — consistent with R12 (structure/vol = timing, not direction).

## Radar R23
RANGE vNext lifecycle events carry only era-trend-dependent directional asymmetry (SWEEP_up short 2011-18 → long 2021-24; OK_MACRO bear-lean → bull-lean); the richer multi-candidate structure does NOT escape the R20 limitation. RANGE frontier BOUNDED_NEGATIVE at the information level. The one sign-stable event (accepted-upside-escape → mild long) is immaterial (gold long-bias). Next: continue novel-event discovery.
