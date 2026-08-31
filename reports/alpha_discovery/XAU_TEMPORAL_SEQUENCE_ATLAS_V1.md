# XAU_TEMPORAL_SEQUENCE_ATLAS_V1 — causal pre-decision trajectory vocabulary & census

TEMPORAL_SEQUENCE_MINING_V1 §22 deliverable. Governed OANDA XAUUSD M15 UTC (355,696 bars, 2011-07-26 → 2026-07-27), existing infra
(`cur_data`, `tsm_core.py`). Everything causal: sequence features use bars ≤ anchor t; outcome uses bars > t only.

## 1. Core research unit
`CAUSAL_SEQUENCE_t` = ordered history of the last **L ∈ {8,16,32,64}** M15 bars ending at decision time t. HTF context (H1≈EMA80,
H4≈EMA320 on M15; era; session with DST via hour-of-day UTC buckets) attached causally. These are bounded research scales, not
optimization targets.

## 2. CURRENT-STATE vocabulary (the baseline the path must beat)
The static "final state" the mandate requires the path to add information *beyond* — the same class Factory V2 falsified as standalone
discriminators: `range_pos` (position within rolling-20 range, premium/discount), `vol_state` (atr/atr_ma bucket), `htf_align`
(EMA80 vs EMA320), `session` (AS/LN/NY/LT, DST-correct), `anchor_dir`, `dist-from-structure` (rolling-20 swing extremes). State CELL =
(range-third × vol-third × htf × session × path-net-dir) — the matched-contrast strata.

## 3. PATH-MOTIF vocabulary (order-sensitive; NOT reducible to the final state)
| motif | definition | what makes it ORDER-dependent |
|---|---|---|
| `eff` | \|net displacement\| / Σ\|bar moves\| over L | directness of the approach |
| `sc` | # sign-changes of bar returns | whipsaw of the path |
| `energy_late` | (Σ\|moves\| 2nd-half − 1st-half)/sum | **early vs late energy** — same net, different order |
| `argH`,`argL` | time-location (0=old,1=recent) of window high/low | **where in time** the extreme sits |
| `pull` | deepest retrace of the dominant move (in ATR) | pullback depth into the anchor |
| `rc` | recross count of window mid-price | path complexity |
| `net_r` | net window move in ATR | graded magnitude of the approach |
| 3-seg ordered-sign | sign of returns in thirds → 27 ordered classes | **pure order**: [+,+,−] ≠ [−,+,+] at equal net |

## 4. Anchor families (causal decision surfaces, §7 — deliberately NOT limited to the falsified structural-break population)
| anchor | definition | raw N | independent episodes (H=32) |
|---|---|---|---|
| **RANGE_EDGE** | fresh arrival into top/bottom 15% of rolling-20 range (continue-vs-reverse surface) | 38,200 | 8,756 |
| **VOL_TRANS** | compression (atr10/atr50<0.85) → expansion onset (bar range >1.5×atr_ma) | 6,906 | 4,485 |

Independent-episode ratio 0.23 / 0.65 — overlap is real and is controlled for (episode net-R ≈ raw net-R throughout).

## 5. Trajectory-class census — 3-segment ordered-sign motif (L=32, RANGE_EDGE, N=38,200)
19 of 27 ordered classes populated (≥150). **The census is the headline finding of the atlas:** P(up-first) is pinned at ~0.50 in
*every* class; the net-R spread is pure barrier geometry, not directional information.

| ordered motif | N | net-R (2R:1R, cost.24) | P(continue) | **P(up)** |
|---|---|---|---|---|
| (1,1,1) monotone-up | 5,366 | −0.241 | 0.504 | 0.504 |
| (−1,1,1) dip-then-up | 5,555 | −0.397 | 0.513 | 0.500 |
| (1,1,−1) up-then-fade | 4,295 | −0.614 | 0.524 | 0.519 |
| (1,−1,1) up-dip-up | 4,582 | −0.289 | 0.507 | 0.512 |
| (1,−1,−1) up-then-down | 5,234 | −1.047 | 0.499 | 0.504 |
| (−1,−1,1) down-then-up | 4,358 | −0.833 | 0.505 | 0.509 |
| (−1,1,−1) down-up-down | 4,201 | −1.154 | 0.492 | 0.522 |
| (−1,−1,−1) monotone-down | 4,586 | −1.240 | 0.501 | 0.499 |

**Net-matched order reversals are statistically identical:** (1,1,−1) vs (−1,1,1) → P(up) 0.519 vs 0.500; (1,−1,−1) vs (−1,−1,1) →
0.504 vs 0.509. The order of the sub-moves does not move the directional outcome. The net-R differences track only how *extended* the
path is (a monotone move sits farther from its 2R target and nearer its 1R stop) — a geometry artifact, not predictability.

## 6. Interpretation
The atlas establishes the state-space in which the contrast test operates: a rich, well-populated causal trajectory vocabulary
(motifs + 19 ordered shape classes) over two distinct decision surfaces, with directional outcome invariant (~0.50) across all of it.
Whether any of this vocabulary carries *incremental* information beyond the final state is answered in
`TEMPORAL_SEQUENCE_CONTRAST_REPORT_V1.md`.
