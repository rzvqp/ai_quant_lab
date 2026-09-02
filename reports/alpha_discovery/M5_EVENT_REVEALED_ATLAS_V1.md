# M5_EVENT_REVEALED_ATLAS_V1 — native-M5 conditional-response state-machine census

Code: `m5_core.py`, `m5_families.py`. Native XAUUSD M5 (354,669 bars, 2021-07-27→2026-07-27), no aggregation. Direction EVENT-REVEALED;
conservative same-bar; entries next-M5-open after the state completes.

## State machines (dedup 20 raw → 5 distinct; direction from the event, never forecast)
| id | STATE_0 → STATE_1 → STATE_2 → ENTRY_READY | direction source | invalidation |
|---|---|---|---|
| A | balance → displacement ≥1.5ATR/6bar → acceptance (3 closes beyond ref) → pullback then continuation close | sign(displacement) | pullback extreme |
| B | range → sweep of 20-bar extreme → reclaim close back inside → acceptance | reclaim direction | swept extreme |
| C | range → close-break of 20-bar extreme → return back through level (≤3 bars) → opposite | OPPOSITE of break | failed-break extreme |
| D | compression (atr12/atr50<0.7) → expansion bar >1.5ATR → bounded pause → continuation | sign(expansion bar) | pause extreme |
| E | balance → impulse ≥1.5ATR/6bar (d1) → rejection close through impulse origin → opposite-acceptance (d2) | OPPOSITE (d2=−d1) | impulse extreme |

All states complete by entry-bar−1 close (causal). Cooldown 6 bars; event-level dedup (gap 48 bars ≈ 4h) for independent episodes.

## Raw-path census (2R baseline)
| family | N | ind-ep | net-R | P(+100p) | P(+200p) | P(+300p) | median stop |
|---|---|---|---|---|---|---|---|
| A displacement→accept | 19,902 | 6,068 | −1.72 | 0.05 | 0.015 | 0.006 | 11 pip |
| B sweep→reclaim | 20,259 | 5,750 | −0.41 | 0.071 | 0.020 | 0.008 | 15 pip |
| C failed-break→opposite | 14,721 | 5,377 | −0.31 | 0.089 | 0.027 | 0.010 | 19 pip |
| D compression→2nd-leg | 1,263 | 1,142 | −2.22 | 0.031 | 0.011 | 0.006 | 7 pip |
| **E impulse→reject→opposite** | 3,636 | 2,618 | −0.12 | **0.216** | **0.081** | **0.043** | **44 pip** |

E is the standout: wide structural stops (44 pips → cheap cost) and by far the highest large-move reach (22% reach +100 pips). A and D are
killed by tight-stop cost (0.38-0.60R/trade). Detailed analysis in the contrast report and the final report.
