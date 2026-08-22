# ALPHA_HYPOTHESIS_REGISTRY

Cumulative hypothesis log for `ALPHA-XAUUSD-CONTINUOUS-RESEARCH-LOOP-001`. Every materially-distinct rule tested, with side, key params, N, verdict. Parameter *variants* (RR/horizon/threshold neighborhoods) are counted as robustness checks of one hypothesis, not as separate hypotheses (§20, §33). Population: gated M5 -> H4/D1, DEV 2021-07-27..2023-12-29, STRESS cost.

## Loop hypotheses (this mandate)
| # | frontier | hypothesis | side | key params | N | verdict |
|---|---|---|---|---|---|---|
| H01 | F1 | compression -> up-release breakout continues | L | W20, box+atr comp, RR{1.5,2,3}, H{42,60} | 25 | FALSIFIED (MFE≈MAE; best10<0; DISC<0) |
| H02 | F1 | compression -> down-release breakout continues | S | as H01 | 17 | FALSIFIED (avgR<0; DISC−0.52) |
| H03 | F1 | + D1-alignment filter improves the break | L/S | D1 EMA20>50 subset | 13/7 | FALSIFIED (worse/too few) |
| H04 | F2 | ATR-extension (ext>E) reverts (short the extended-up) | S | E{2.5,3.0}, RR{1,1.5,2} | 40–52 | FALSIFIED (advFirst 0.80–0.87; avgR<0) |
| H05 | F2 | ATR-extension reverts (long the extended-down) | L | E{2.5,3.0} | 27–41 | FALSIFIED (best10<0; 2023<0) |
| H06 | F2 | D1 consecutive-run (>=K days) reverts | L/S | K{4,5} | 5–13 | FALSIFIED (advFirst 0.85–0.92; avgR<0) |
| H07 | F3 | day-of-week directional drift | both | UTC weekday means | 444d | FALSIFIED (upRate≈0.5; weak) |
| H08 | F3 | weekly-open gap continuation | dir | ATR stop, RR{1,1.5} | 89 | FALSIFIED (best10−0.07; 2021<0) |
| H09 | F3 | weekly-open gap fade | dir | as H08 | 89 | FALSIFIED (avgR<0 all) |
| H10 | F4 | trend-drift per regime onset, horizon payoff | L | H{12,24,42}, 3ATR safety | 65 | NEAR-MISS (H24 clean but fragile; = trend-beta) |
| H11 | F4 | same, D1-aligned | L | H24 sweet-spot | 38 | NEAR-MISS (posRate .55, allYrs+, but horizon-fragile) |
| H12 | F4 | trend-drift SHORT per down-regime onset | S | H{12,24,42} | 21–49 | FALSIFIED (regime-locked, best10<0) |
| **H13** | **F5** | **compression = low-risk re-entry WITH the D1 trend, structural stop** | **L** | **W20,H42,cd20,rr2** | **53** | **SURVIVOR -> READY_FOR_INDEPENDENT_VALIDATION** |
| H14 | F5 | same, SHORT in D1-downtrend | S | W20,H42,rr{1.5,2,3} | 36 | NOT_SUPPORTED (best10<0; DISC−0.26) |
| H15 | F6 | down-expansion crash-bar momentum continues (trailing ride) | S | N10, tr>1.3atr, close<0.33, trail{2,3}ATR | 69 | FALSIFIED (down-spikes REVERT; all yrs<0 incl 2022; best10<0) |
| H16 | F6 | same, gated to D1-downtrend | S | trail{2,3}ATR | 29 | FALSIFIED (avgR<0; 2022 −0.69/−0.95) |
| H17 | F7 | prior-day-high breakout continuation (frequency LONG) | L | first close>PDH, D1-up, rr{1.5,2} | 74 | FALSIFIED (DEV avgR<0, best10<0, advFirst 0.73 noise-stopped) |
| H18 | F7 | overlap of H17 vs frozen COMP-CONT-L | L | trade-day Jaccard | — | 0.19 (low) but moot — H17 not robust |

**Note on H17/CALIB:** CALIB 2024 was +0.33 for H17 but **DEV is negative** — a positive robustness-population number on a DEV-failing rule is noise, NOT an edge. Selection gate = DEV-robust first; H17 fails it. Recorded to prevent CALIB-fishing.

## External-replication hypotheses (priority mandate ALPHA-XAUUSD-EXTERNAL-S2-S4-INDEPENDENT-TEST-001)
Rules FROZEN in `EXTERNAL_RULE_MAPPING.md` before results. External win-rates are non-evidence.
| # | family | hypothesis | side | key params (frozen) | N range | verdict |
|---|---|---|---|---|---|---|
| H19 | S2 | close-based box + close-beyond breakout continues (entry A) | L/S | H1/H4, W5, 3 box defs, no-chase $4 | 82–1095 | FALSIFIED (advFirst 0.72-0.89; best10<0; yr+ never) |
| H20 | S2 | + first-retest entry (B) improves | L/S | retest window 20 | 66–869 | FALSIFIED (less-bad, still <0; lowers freq only) |
| H21 | S2 | + free-path (>=100p clear) increment | L/S | prior swing obstacle | subset | FALSIFIED (WORSE than base) |
| H22 | S2 | + 1.3x volume increment | L/S | aggregated-M5 vol | subset | FALSIFIED (WORSE than base) |
| H23 | S4 | M5 sweep+reclaim of >=1-day level reverses (BASE) | L/S | PDH/PDL, H4-swing, H1-24, SL sweep+/-$0.50 | 433–688 | FALSIFIED (advFirst 0.84-0.91; best5/10<0) |
| H24 | S4 | + reclaim quality (upper/lower third) | L/S | closepos>=0.66 | 276–428 | FALSIFIED (marginal, gate-fail; delay-fragile) |
| H25 | S4 | + anti-fade (exclude pre-sweep pressure) | L/S | 12-bar approach slope | 111–235 | FALSIFIED (pressure-sweeps ARE worse, but no positive edge) |
| H26 | S4 | TREND-ALIGNED "golden pattern" (causal D1) | L/S | D1 EMA20/50 via close_time | 236–341 | FALSIFIED — the WORST subfamily; "9/9" not reproducible |
| H27 | S4 | +1-bar delay degradation | L/S | entry+1 | — | degrades every cell (no base edge to protect) |
| H28 | S4 | invalidation exit (M5 close beyond sweep extreme) | L/S | thesis-negation | — | does not rescue (all <0) |

**Robustness checks on H13 (not separate hypotheses):** W∈{14,20,28}×H∈{30,42,60}×cd∈{12,20}×rr∈{1.5,2.0} full grid (reported in `frontier5_vet.py` output); CALIB 2024 out-of-selection; DISC/CONF 60/40; best-1/5/10%-removed; per-year; overlap-vs-protrend proxy.

## Prior-program lineage (summary — full detail in ALPHA_GRAVEYARD.md)
60+ materially-distinct hypotheses across ~20 mandates already falsified (intraday fades/breakouts, session/sweep shorts, nested-MTF sequences, probabilistic states, H1/H4 transition, protrend, disp-followthrough, RANGE families, and the 6-family autonomous loop). The survivor H13 must be read against this cumulative search (§20).

## Historical different-population hypotheses (CEO auth DIFFERENT_PRICE_ONLY_POPULATION)
Causal `hist_data.py`, b0+b1 DISCOVERY_CONSUMED (NOT validation).
| # | frontier | hypothesis | side | key params | N | verdict |
|---|---|---|---|---|---|---|
| H29 | HF1 | compression-timed continuation in confirmed D1 downtrend | S | W20,H42,rr{1.5,2,3}, D1 EMA20<50 causal | 107 | FALSIFIED (2013-only @rr3, best10<0, b0+/b1-, RR-fragile) |
| H30 | HF2 | fade range extremes in causal RANGE regime (real range) | L/S | WB30, touch 0.1*height, stop beyond boundary | 75/81 | FALSIFIED (MAE>>MFE, best10<0, both blocks neg) |
