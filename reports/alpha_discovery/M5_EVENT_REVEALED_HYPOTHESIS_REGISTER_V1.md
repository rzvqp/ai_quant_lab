# M5_EVENT_REVEALED_HYPOTHESIS_REGISTER_V1 — 20 raw → dedup 5 → tested → 0 survived

§6 deliverable. Direction EVENT-REVEALED (never forecast). S5 (NY-OR breakout) excluded. Screened vs `ALPHA_NEGATIVE_KNOWLEDGE_BASE_V1`.

## 20 raw → dedup 5
| ID | concept | dedup |
|---|---|---|
| M01 | displacement→acceptance→continuation | KEEP → **A** |
| M02-M04 | accept variants (bar count / ref) | → A |
| M05 | sweep→reclaim→continuation | KEEP → **B** |
| M06-M07 | sweep depth / reclaim-close variants | → B |
| M08 | break→failed-acceptance→opposite | KEEP → **C** |
| M09-M10 | failed-break window / level variants | → C |
| M11 | compression→expansion→second-leg | KEEP → **D** |
| M12 | volatility-state transition → continuation | → D (folds into compression→expansion) |
| M13-M14 | expansion magnitude / pause-depth variants | → D |
| M15 | impulse→rejection→opposite-acceptance | KEEP → **E** |
| M16-M17 | rejection depth / acceptance variants | → E |
| M18 | opening impulse second-leg | REJECT — S5-adjacent (opening range) |
| M19 | reclaim continuation w/o sweep | REJECT — = B without STATE_1 |
| M20 | micro-BOS chain | REJECT — static BOS (NKB), not a revealed-direction sequence |

20 raw → **5 distinct** sequential state machines (A displacement-accept, B sweep-reclaim, C failed-break-opposite, D compression-2ndleg,
E impulse-reject-opposite).

## Results
| family | net-R (2R) | verdict |
|---|---|---|
| A | −1.72 | FALSIFIED (tight-stop cost) |
| B | −0.41 | FALSIFIED |
| C | −0.31 | FALSIFIED |
| D | −2.22 | FALSIFIED (tight-stop cost) |
| E | −0.12 (best cell +0.117, DEV −0.013, outlier-dependent) | FALSIFIED as tradeable; **information CONFIRMED** |

RAW=20 · DEDUPED=5 · TESTED=5 · FALSIFIED=5 · **SURVIVED=0.** `SEQUENTIAL_EVENT_INCREMENTAL_INFORMATION_FOUND=YES` (E). `S5_MECHANISM_CLONED=NO`.
`FIXED_R_ONLY=NO` (2R/struct/trail/time tested). Falsified subfamilies + the E information finding added to the Negative Knowledge Base.
