# ORDER_BLOCK_RETEST_HYPOTHESIS_REGISTER_V1 — 20 raw → dedup 6 → tested → 1 survived

§25 deliverable. Raw hypotheses screened against `ALPHA_NEGATIVE_KNOWLEDGE_BASE_V1`; deduped by mechanism to 6 distinct; concept
diversity over threshold mining.

## 20 raw → dedup
| ID | concept | dedup verdict |
|---|---|---|
| O01 | last-bearish-candle OB + close-BOS + fresh first retest (FULL_RANGE) | KEEP → **H1** |
| O02 | OB body-only representation | REJECT — representation variant of O01 (FULL_RANGE tested) |
| O03 | OB open-to-extreme representation | REJECT — representation variant |
| O04 | OB + displacement>=1.5 ATR gate | KEEP → **H2** (displacement quality) |
| O05 | OB + target-space >=2R | KEEP → **H3** (target space) |
| O06 | sweep-origin OB (liquidity grab before displacement) | REJECT — overlaps NKB sweep-reverse; folded into O01 origin |
| O07 | session-specialized OB (LN/NY retest) | KEEP → **H4** |
| O08 | deep 50-75% mitigation vs shallow touch | KEEP → **H5** (depth) → proven HINDSIGHT (see below) |
| O09 | H4-aligned OB first retest | KEEP → **H6** (HTF) |
| O10 | wick-BOS vs close-BOS | REJECT — BOS-quality variant; close-BOS used |
| O11 | second/third retest | REJECT — §10 primary is first-retest only (later = diagnostic) |
| O12 | OB + EMA-trend filter | REJECT — HTF-selection (prior negative) = H6 |
| O13 | OB mid vs edge entry | REJECT — entry-level variant of O01 |
| O14 | fixed-1R vs 2R vs 3R target | REJECT — target variant (tested across H1–H4) |
| O15 | OB with volume-expansion origin | REJECT — no governed volume-quality edge (VOLTIME info-only) |
| O16 | counter-trend OB fade | REJECT — = range-fade (NKB negative) |
| O17 | OB + prior-day-level confluence | REJECT — auction confluence (NKB bounded-neg) |
| O18 | OB retest close-rejection entry | REJECT — close-entry proven negative (hindsight depth) = H5 |
| O19 | multi-timeframe OB (H1 block) | REJECT — timeframe variant; M15 primary |
| O20 | OB + M5 micro-confirmation execution | KEEP as EXECUTION layer (§24), tested on survivor only |

20 raw → **6 distinct** (H1 first-retest, H2 displacement, H3 target-space, H4 session, H5 depth/mitigation, H6 HTF) + M5 execution layer.

## 6 distinct — result
| H | mechanism | result |
|---|---|---|
| **H1** | fresh first-retest of causal OB (close-BOS), limit entry | ~break-even (−0.006 bull) — **information present** (beats controls) but not monetizable alone |
| **H2** | + displacement ≥1.5 ATR | **MONETIZES** — monotone dose-response; the core of the survivor |
| **H3** | + target-space ≥2R | WEAK — room alone mildly positive, not decisive |
| **H4** | + LN/NY session | **MONETIZES** — LN+NY lifts net-R; NY strongest; combined with H2 = survivor |
| **H5** | depth/mitigation (shallow vs deep) | **FALSIFIED as hindsight** — the +0.28 shallow-depth cell is a limit-fill intrabar artifact; causal close-entry is negative |
| **H6** | H4-aligned OB retest | FALSIFIED — HTF alignment adds nothing on top of H2+H4 (consistent with prior HTF negative) |
| M5 | stop-tighten to M5 swing-low (native 2021+) | **VALUE_ADD** on native window (+0.23→+0.93R; needs Statistician R-accounting scrutiny) |

## Outcome
RAW=20 · DEDUPED=6 · TESTED=6 · FALSIFIED=4 (H3 weak, H5 hindsight, H6, + the un-gated H1) · **SURVIVED=1** (H2×H4 = OBR-BULL-1;
OBR-BEAR-1 secondary/weaker). The order block **does** add cross-era information beyond ordinary pullbacks — the first positive discovery
of the campaign. Falsified subfamilies (H5 depth-hindsight, H6 HTF, generic-pullback controls) added to the Negative Knowledge Base.
