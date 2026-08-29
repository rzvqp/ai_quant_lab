# VOLPATH_INFORMATION_LEDGER — Phase-1 path geometry (information-only, no strategy)

`volpath_phase1.py`, 4,304 deduped mature-compression events (comp_dur≥12, H=48b, ref=close@endpoint, barriers {0.5,1,1.5,2}ATR). Causal.

## A — Expansion timing
Median bars to first excursion: 0.5ATR=1, 1.0ATR=3, 1.5ATR=6, 2.0ATR=10 (2ATR reached 4254/4304). **Max excursion lands LATE:**
median bar-to-max-up=27, max-dn=24 (of 48) — the expansion develops across the whole horizon, not in the first impulse.

## B/C — Two-sided excursion + path ordering
| k (ATR) | P(up) | P(dn) | **P(BOTH)** | ord UP | ord DN | ord BOTH-simul |
|---|---|---|---|---|---|---|
| 0.5 | 0.932 | 0.912 | 0.844 | 0.42 | 0.39 | 0.20 |
| 1.0 | 0.855 | 0.830 | **0.685** | 0.50 | 0.46 | 0.04 |
| 1.5 | 0.778 | 0.746 | 0.524 | 0.50 | 0.48 | 0.02 |
| 2.0 | 0.698 | 0.661 | 0.371 | 0.50 | 0.48 | 0.01 |
Path ordering is **SYMMETRIC** (UP≈DN≈0.50 at every k) — which side is touched first is a coinflip. Both ±1ATR reached 68.5% of events.

## D — Midpoint recross (whipsaw)
Mean recross count **3.10** (median 2); P(0 recross = clean)=**0.255**; P(≥2 recross)=**0.613**; median time-to-first-recross=8b.
→ compression expansions are WHIPSAW-DOMINANT (61% oscillate through the midpoint ≥2×; only 25% are one-directional/clean).

## E/F — First break quality + double-sided break
Break rate 0.989. Classification of the first compression-range break: **CONTINUES 0.154 · WHIPSAW 0.375 · DOUBLE_BREAK 0.470** (break
one side → recross → break the opposite side) · NEITHER 0.001. First-break follow-through median ft1=−0.07/ft2=−0.09/ft4=−0.09 ATR
(NEGATIVE — the raw first break does NOT follow through); fb_MFE=3.19≈fb_MAE=3.09 (symmetric). **The first break is a poor continuation
signal** — confirms VOLTIME-2 at the geometry level; 47% double-break is the crux hazard for any straddle (pays whipsaw twice).
- **H2 conditional (KEY):** an OBSERVED follow-through predicts continuation, cross-era-stable: ft2≥0.3ATR → P(CONTINUES)=**0.395**
  (D/C/O 0.41/0.39/0.38), DOUBLE_BREAK 0.336; ft2<0 → P(CONTINUES)=0.008 (D/C/O 0.01/0.01/0.01). Base 0.154 → 0.395 (2.5×) after
  confirmation. Direction is SUPPLIED by the observed move, not predicted from the endpoint.

## G — Range consumption (does the first impulse consume the expansion?)
Median fraction of the DOMINANT excursion reached within: first 1b=0.061, 2b=0.096, 4b=0.149, **8b=0.244**. → the first impulse consumes
LITTLE; **~76% of the dominant excursion remains after 8 bars.** Post-classification entry preserves most of the opportunity.

## Context (H6)
Path geometry is fairly stable across session/era (P(both±1) 0.67–0.74, recross 2.8–3.3, CONTINUES 0.13–0.21). London mildly cleaner
(CONTINUES 0.21 vs NY 0.13). Extreme compression → slightly more recross (3.31) and more two-sided (0.71). Effects mild.

## Straddle economics proxy
±1ATR: P(both)=0.685, one-sided-only 0.315 → activates both sides most of the time (pays whipsaw). ±2ATR: P(both)=0.371, one-sided-only
**0.617**, neither 0.012 → a WIDE straddle escapes one-sided 62%, but the winner must beat a ~2ATR loser + two-sided spread on the 37%
both-hit. Borderline; hostile at tight barriers.
