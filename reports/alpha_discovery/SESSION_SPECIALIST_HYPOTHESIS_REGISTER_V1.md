# SESSION_SPECIALIST_HYPOTHESIS_REGISTER_V1 — 20 raw → dedup 6 → tested → 0 survived

§5 deliverable. S5 (NY opening-range breakout, long) EXCLUDED from generation. Screened against `ALPHA_NEGATIVE_KNOWLEDGE_BASE_V1`.

## 20 raw → dedup
| ID | concept | dedup |
|---|---|---|
| Z01 | Asia range break → London continuation (long) | KEEP → **A** |
| Z02 | Asia range break → London continuation (short) | → A (direction split) |
| Z03 | Asia compression → London expansion | REJECT — VOLTIME expansion info-only; = A magnitude |
| Z04 | Asia location-in-PDR → London expansion | REJECT — = A + location filter |
| Z05 | Asia false-break up → London reversal | KEEP → **B** |
| Z06 | Asia false-break down → London reversal | → B (mirror) |
| Z07 | Asia sweep of PDH/PDL → London reversal | REJECT — = B (sweep-reversal, NKB negative) |
| Z08 | London overextension (up) → NY fade | KEEP → **C** |
| Z09 | London overextension (down) → NY fade | → C (mirror) |
| Z10 | London took liquidity → NY reversal | REJECT — = C |
| Z11 | London trend up → NY continuation | KEEP → **D** |
| Z12 | London trend down → NY continuation | → D (mirror) |
| Z13 | London range-expansion → NY continuation | REJECT — = D magnitude variant |
| Z14 | NY displacement → second leg (long) | KEEP → **E** |
| Z15 | NY displacement → second leg (short) | → E (mirror) |
| Z16 | NY failed reversal → continuation | REJECT — = E re-acceptance |
| Z17 | late-NY large day → continuation | KEEP → **F** |
| Z18 | late-NY large day → exhaustion/fade | → F (mode split) |
| Z19 | large day → overnight continuation | REJECT — = F horizon variant |
| Z20 | Asia directional close → London same-direction | REJECT — = A/D directional-bias variant |

20 raw → **6 distinct mechanisms** (A expansion, B reversal, C overextension-fade, D trend-continuation, E second-leg, F late-session).

## Results (next-open entry, 2R, conservative same-bar, price-cost)
| family | net-R | matched-control | verdict |
|---|---|---|---|
| A Asia→London expansion | +0.010 (O-only) | beats control +0.13–0.15 | **FALSIFIED** (break-even, era-trend, 7-8/16 yrs) |
| B Asia false-break→London reversal | −0.366 | — | **FALSIFIED** (fades fail; breaks continue) |
| C London overext→NY reversal | −0.279 | — | **FALSIFIED** |
| D London trend→NY continuation | −0.027 (O-only) | beats control +0.05–0.11 | **FALSIFIED** (break-even, era-trend, 4/16 yrs) |
| E NY displacement→second leg | −0.171 | — | **FALSIFIED** |
| F late-NY continuation/exhaustion | negative both modes | — | **FALSIFIED** |

RAW=20 · DEDUPED=6 · TESTED=6 · FALSIFIED=6 · **SURVIVED=0.** `SESSION_INCREMENTAL_INFORMATION_FOUND=YES` (families A/D beat matched
controls) but no family monetizes cross-era. Falsified subfamilies added to the Negative Knowledge Base.

## §11 direction / §6 clone check
Directions tested separately; positive era-cells are era-trend-aligned (long in bull O, short in bear D), confirming directional beta not
session structure. `S5_MECHANISM_CLONED = NO`.
