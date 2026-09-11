# FFR — SECOND-ORDER TRAP (Failed-Failure Re-acceptance) — QUICK-KILL

Alpha/Research-executor quick-kill. Mechanism tested: `BREAK → FAILED ACCEPTANCE → RE-ACCEPTANCE → CONTINUATION to L2`. Cheapest correct
falsification: **reuses the FROZEN failed-acceptance universe** (`FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_EVENTS`, bound to `LEVEL_TO_LEVEL_ACCEPTANCE_V1`
102458/72103/30355) — no new level discovery. All params governed/reused (re-acceptance window 8 bars = RTH retest window; stop buffer 0.10 ATR;
backstop 96; spread BASE 0.05 / STRESS 0.08; target = frozen L2). No grid search, no param invention, no lookahead. `PROTOCOL_HASH = 50707cfaf0fadea0c1c4`.

## VERDICT: **KILL** (over-determined — 5 independent triggers)

### Stage 1 dedup ruling
NOT a strict name-duplicate (re-acceptance-as-trigger never run as its own ledger) → proceeded to quick-kill. But three material priors pre-constrained it and are now confirmed: (a) **FAILED_ACCEPTANCE_V1** — after a failure, continuation-to-L2 is only the *minority* outcome (L2-first 25.0% vs L0-reversal 70.8%); (b) **P007 reclaim** — the reclaim/round-trip component is the weakest, near-circular (AUC 0.691 inverted); (c) the **L1→L2 execution arc** (V1/V2/V3/RETEST/STRUCTURAL-REACTION) already showed late re-entry into this move is non-monetizable.

### Funnel (of 26,646 frozen failed-acceptance events with valid L0 & L2)
| branch | n | share |
|---|---|---|
| fade won (reversed to L0 first) | 14,743 | **55.3%** |
| pre-continued (L2 first, no re-accept needed) | 2,866 | 10.8% |
| no re-acceptance within 8 bars (expiry) | 793 | 3.0% |
| **re-accepted → FFR trigger** | 8,244 | 30.9% → **6,101 independent trades (407/yr)** |

The trap fires at practical frequency — but the fade "wins" (price reverses to the prior level) **55%** of the time, so the trap→continuation is structurally the minority path, exactly as FAILED_ACCEPTANCE_V1 predicted.

### Economics — negative, era-unstable, R:R < 1
| metric | value |
|---|---|
| N (long / short) | 6,101 (2,828 / 3,273) · WR 51.4% |
| avg win / avg loss | +0.837R / −1.028R · **realized R:R 0.81** · medNatRR **0.87** |
| **BASE / STRESS** | **−0.070R / −0.088R** · PF 0.860 · maxDD 463R |
| chronological eras (BASE) | −0.062 / −0.072 / −0.075 → **0/3 positive** |
| 2025–2026 | −0.082R (n 679) — negative in current regime |
| top-5% contribution | −2.08 (NOT outlier-carried; broadly negative) |
| by direction | long −0.038R · short −0.097R (**both negative** — not a long-beta artifact) |
| by level type | **PDH/PDL −0.161** (worst) · session/Asia −0.066 · swing −0.071 · range −0.054 |
| **comparator — PRIMARY ACCEPTANCE (V1)** | BASE −0.065R, PF 0.857 → **FFR is marginally WORSE** |

### Kill triggers (any one suffices; five fired)
1. **STRESS ≤ 0** (−0.088R).
2. **Does not beat primary acceptance** (−0.070R vs −0.065R — slightly worse).
3. **Sign unstable** — 0/3 eras positive, negative in 2025–26.
4. **R:R < 1** — medNatRR 0.87, realized 0.81: the second impulse to L2 is *closer than the trap-swing stop* — the identical shallow-move-vs-noise geometry that killed V1 (0.71), structural-reaction (0.60), and the whole L1→L2 arc.
5. **Relevant levels do not beat generic** — the CEO-named PDH/PDL are the **worst** type (−0.161R), not better than session/swing/range.

Not outlier-dependent (top-5% contribution negative), not salvageable one-sided (both long and short negative).

## FINAL BLOCK
```
FFR_SECOND_ORDER_TRAP_QUICK_KILL_V1_COMPLETE = YES · PROTOCOL_HASH = 50707cfaf0fadea0c1c4
DEDUP = NOT_STRICT_DUPLICATE (proceeded); mechanism pre-constrained by FAILED_ACCEPTANCE_V1 + P007 + L1→L2 arc
FROZEN_FAILED_EVENTS = 26646 · RE_ACCEPTED = 8244 · INDEPENDENT_TRADES = 6101 · TRADES_PER_YEAR = 407
N_LONG = 2828 · N_SHORT = 3273 · WIN_RATE = 0.514
AVG_WIN_R = +0.837 · AVG_LOSS_R = -1.028 · REALIZED_RR = 0.81 · MEDIAN_R = +0.083 · MEDIAN_NAT_RR = 0.87
BASE_EXPECTANCY_R = -0.0697 · STRESS_EXPECTANCY_R = -0.0875 · PROFIT_FACTOR = 0.860 · MAX_DRAWDOWN_R = 463
ERAS_BASE = [-0.062, -0.072, -0.075] (0/3 positive) · 2025_26 = -0.082
TOP5_CONTRIB = -2.08 (not outlier-carried) · LONG = -0.038 / SHORT = -0.097 (both negative)
BY_LEVEL: PDH/PDL -0.161 (worst) · session/Asia -0.066 · swing -0.071 · range -0.054
FFR_vs_PRIMARY_ACCEPTANCE = WORSE (-0.070 vs -0.065)
FFR_VERDICT = KILL
FAILURE_MODE = POOR_RR_CONTINUATION (medNatRR 0.87, target closer than trap stop) + NEGATIVE_EXPECTANCY + ERA_UNSTABLE (0/3, incl 2025-26) + DOES_NOT_BEAT_PRIMARY_ACCEPTANCE + RELEVANT_LEVELS_DONT_BEAT_GENERIC (PDH/PDL worst)
ALPHA_SURVIVOR = NO · READY_FOR_STATISTICIAN = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

Per the mandate KILL clause: no optimization, no threshold changes, no alternate stop attempted — FFR closed. The second-order-trap thesis (trapped faders' stops feed a second continuation impulse) does not survive: the fade reverses to the prior level 55% of the time, and when re-acceptance does occur the continuation to L2 is shorter than the trap-swing invalidation (R:R 0.81), so expectancy is negative, era-unstable, and worse than plain primary acceptance. No Statistician/Red Team started; no strategy promoted; protections intact. S5 remains the sole validated tradeable XAUUSD edge.
```
FFR_SECOND_ORDER_TRAP_V1 = KILL — fade reverses 55%; re-acceptance continuation R:R 0.81 (<1), STRESS -0.088, 0/3 eras, worse than primary acceptance; PDH/PDL worst
```
