# TEMPORAL_SEQUENCE_HYPOTHESIS_REGISTER_V1 — 15 raw → dedup 5 → tested → falsified

TEMPORAL_SEQUENCE_MINING_V1 §10/§11 deliverable. Each raw hypothesis screened against `ALPHA_NEGATIVE_KNOWLEDGE_BASE_V1` (reject
renamed static failures) and required to depend **materially on ORDER / DURATION / TRANSITION / PATH**, not merely the final state
(§5). §7 cap = 15 raw → dedup by mechanism → 5 distinct tested.

## 15 raw hypotheses + dedup verdict
| ID | sequence name | order-dependence | dedup verdict |
|---|---|---|---|
| T01 | monotone impulse → range-edge → continuation | directness of approach | KEEP → **M-C** |
| T02 | whippy/choppy approach → range-edge → reversal | sign-change count | KEEP → **M-C** |
| T03 | early-energy (front-loaded) → break → fade | 1st-half>2nd-half move | KEEP → **M-A** |
| T04 | late-energy (back-loaded) → break → continuation | 2nd-half>1st-half move | KEEP → **M-A** |
| T05 | recent-high late in window → continuation up | argH location-in-time | KEEP → **M-B** |
| T06 | recent-low late in window → continuation down | argL location-in-time | KEEP → **M-B** |
| T07 | shallow pullback into anchor → continuation | pullback depth | KEEP → **M-C** |
| T08 | deep pullback into anchor → reversal | pullback depth | REJECT — clone of T07 (same feature, opposite tail) |
| T09 | large net approach magnitude → continuation | net_r graded | KEEP → **M-D** |
| T10 | 3-seg ordered [+,+,−] vs [−,+,+] net-matched | pure ordered sign | KEEP → **M-E** |
| T11 | compression→sweep→reclaim (V-shape) → continuation | ordered transition | REJECT — reduces to sweep-reversal (NKB: SWR-1 net-neg) + captured by M-E V-class |
| T12 | impulse→pause→continuation | ordered transition | REJECT — = M-A late-energy + M-C directness (no new mechanism) |
| T13 | repeated test → weakening progress → failure | progress-per-vol trend | REJECT — VOLPATH REDUNDANT (NKB) + = M-A energy decay |
| T14 | recross-heavy path → range-edge → reversal | recross count | KEEP → **M-C** (path complexity) |
| T15 | trend → shallow correction → renewed acceptance | ordered transition | REJECT — = WUZ-1 pullback-to-zone (NKB FAIL −0.167) |

10 of 15 kept, collapsing to **5 mechanistically distinct** hypotheses (T08/T11/T12/T13/T15 rejected as clones or NKB-falsified statics).

## 5 deduplicated distinct mechanisms — §10 fields + result
Every mechanism was run through the information test (within-cell spread, positive-control-validated) and the monetized falsification
battery (2R:1R, cost 0.24, L∈{8,16,32,64}, 2 anchors, DEV/OOS, era D/C/O, best-episode removal, independent episodes).

### M-A — ENERGY-ORDER (early vs late composition)
MECHANISM: same net move; does energy arriving *late* (fresh) vs *early* (spent) predict continuation? · START_STATE: pre-anchor window ·
TRANSITIONS: 1st-half vs 2nd-half \|move\| · DECISION_SURFACE: range-edge / vol-transition · WHY_ORDER_MATTERS: "spent vs fresh" momentum ·
SESSION/REGIME/DIRECTION: all · ENTRY: continuation in path dir · INVALIDATION: 1R structural · TARGET: 2R · HOLD: ≤32 bars ·
RELATED_FAILED: Contrast-Miner break_velocity (spent-move) · WHY_DIFFERENT: order of energy, not its magnitude at the break ·
FALSIFIER: net-R ≤ null after cost / era-unstable. **RESULT: FALSIFIED** — info spread −0.009 (era-sign-unstable); monetized net-R
−0.67 (worse than null). Late-energy tercile actively loses.

### M-B — EXTREME-RECENCY (where the high/low sits in time)
MECHANISM: a window whose extreme formed *recently* vs *early* implies different exhaustion. · TRANSITIONS: argH/argL location-in-time ·
WHY_ORDER_MATTERS: recency of the extreme = freshness of the level · WHY_DIFFERENT: pure time-position, not price level.
**RESULT: FALSIFIED** — best single flag (VOL_TRANS argH +0.042 in-sample) appeared at one L only, monetized net-R −0.28 (≈ null),
degrades with L (−0.26→−0.31); argL_continue net-R −1.1 (catastrophic).

### M-C — APPROACH DIRECTNESS / CLEANLINESS
MECHANISM: a clean, direct, shallow-pullback, low-recross approach implies control → continuation. · TRANSITIONS: eff / sc / pull / rc ·
WHY_DIFFERENT: shape of the path, not the endpoint. **RESULT: FALSIFIED** — monetized net-R −0.68…−0.75 on both anchors, **worse than
null**: a directionally-clean approach selects already-spent moves (Contrast-Miner "impressive = spent", re-confirmed via path).

### M-D — NET-MAGNITUDE-PATH (graded approach size)
MECHANISM: larger causal approach magnitude predicts up/down. · WHY_DIFFERENT: graded, path-integrated (not the break bar alone).
**RESULT: FALSIFIED** — info spread −0.007 (unstable); monetized net-R −0.23 ≈ driftless null. No edge.

### M-E — ORDERED-SIGN TRAJECTORY (pure order)
MECHANISM: 3-segment ordered sign; net-matched reversals differ only in ORDER. · WHY_DIFFERENT: the definitive isolation of order.
**RESULT: FALSIFIED** — P(up) ≈ 0.50 in all 19 populated classes; 0 cost-surviving; net-matched order reversals identical.

## Summary
RAW=15 · DEDUPED=5 · TESTED=5 · **FALSIFIED=5** · INFORMATIONAL_ONLY=0 · INSUFFICIENT=0 · SURVIVED=0. No hypothesis reached even the
*information* gate with cross-era stability, let alone the cost/monetization gate. The temporal-path axis reproduces the meta-finding:
XAUUSD M15 direction is efficient — and it is efficient with respect to trajectory ORDER, not only static state.
