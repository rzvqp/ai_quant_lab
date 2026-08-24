# ALPHA_BROAD_SCREEN_RESULTS — BATCH D (session-range inheritance) + §30 independence

New mechanism (§18): prior session's full range = coil; next session breaks it directionally. Engine `bscreen.py`, STRESS 0.24, eras b0/b1/DEV/CAL. Ledger (§36): 8 hyps.

## First-pass screen
| hypothesis | side | poolN | poolR | best1 | b0 | b1 | DEV | CAL | first-pass |
|---|---|---|---|---|---|---|---|---|---|
| ASIArange_LONbreak_L | L | 1545 | −0.019 | −0.040 | −0.008 | +0.016 | −0.121 | +0.147 | ELIM NEG_STRESS |
| ASIArange_LONbreak_S | S | 1571 | −0.003 | −0.023 | +0.076 | −0.025 | −0.035 | −0.239 | ELIM NEG_STRESS |
| **LONrange_NYbreak_L** | L | 2096 | **+0.059** | +0.039 | +0.045 | +0.066 | +0.086 | −0.007 | SURVIVOR-weak |
| LONrange_NYbreak_S | S | 2193 | −0.034 | −0.055 | +0.016 | −0.041 | −0.060 | −0.139 | ELIM NEG_STRESS |
| **ASIArange_NYbreak_L** | L | 2754 | **+0.041** | +0.021 | +0.042 | +0.024 | +0.053 | +0.076 | SURVIVOR (all eras +) |
| ASIArange_NYbreak_S | S | 2747 | −0.036 | −0.057 | +0.018 | −0.057 | −0.048 | −0.177 | ELIM NEG_STRESS |
| ASIArange_LONbreak_L_acc | L | 1262 | −0.020 | −0.040 | −0.028 | +0.024 | −0.111 | +0.147 | ELIM NEG_STRESS |
| **LONrange_NYbreak_L_acc** | L | 1832 | **+0.059** | +0.039 | +0.035 | +0.070 | +0.088 | +0.006 | SURVIVOR* |

3 first-pass survivors — ALL LONG, ALL resolving in the NY session, ALL SHORT-side variants negative (S5's asymmetry). Positive across b0(2011-13 bear)+b1(2016-18 chop)+DEV+CAL → NOT era-trend leakage (unlike Batch C). Genuinely positive signal — so the decisive test is independence vs S5.

## §30 PORTFOLIO INDEPENDENCE vs frozen S5 (ORB_NY_L; `deepen_d.py`) — ALL REDUNDANT
| candidate | DISC/CONF | w/o-best-block | **% trade-days overlapping an S5 NY-long day** | **independent (non-S5-day) trades** |
|---|---|---|---|---|
| ASIArange_NYbreak_L | +0.020/+0.074 | +0.038 | **64%** | n=828, **avgR −0.188** (~10/mo, LOSING) |
| LONrange_NYbreak_L | +0.058/+0.060 | +0.048 | **76%** | n=367, **avgR −0.256** |
| LONrange_NYbreak_L_acc | +0.054/+0.068 | +0.048 | **78%** | n=289, **avgR −0.208** |

**Verdict: REDUNDANT_EXISTING_ALPHA.** The entire positive expectancy comes from days that overlap S5's NY-long signal; on the days S5 does NOT fire, every candidate is net-NEGATIVE. These are noisier proxies for the same economic episode (NY-session long momentum), not independent edges. Incremental independent opportunities/month = **0** (the non-overlapping trades lose money). Not frozen, not candidates.

## Decisive campaign finding (R18)
Across Batches A-D (~40 hypotheses, ~15 information classes, M15/H1/H4) + the prior S1-S51 corpus, the **XAUUSD price-only edge is essentially SINGULAR**: opening-range (S5), Asia-range-break, and London-range-break all rediscover the *same* NY-session long-momentum episode; every other class is modern-negative or era-leakage. No mechanism tested adds INDEPENDENT positive expectancy beyond S5. Implication for §31 (40-60 independent opportunities/month): the price-only universe does not supply a diverse specialist portfolio — it supplies ~one robust edge (S5). Growing the portfolio independently would require either a genuinely novel price mechanism not yet conceived, or (CEO-gated §26) exogenous information (DXY/yields/news). This is flagged to CEO as evidence, not a stop — discovery continues (new-mechanism generation).
