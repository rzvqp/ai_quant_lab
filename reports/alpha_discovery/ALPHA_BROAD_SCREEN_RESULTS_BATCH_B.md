# ALPHA_BROAD_SCREEN_RESULTS — BATCH B (untested information classes)

Engine `bscreen.py` (sb.simulate, STRESS 0.24, eras b0/b1/DEV/CAL, event-deduped, cross-era). Ledger (§36): 13 hyps, all counted.

| # | hypothesis | info class | side | poolN | poolR | best1 | b0 | b1 | DEV | CAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | SB_break_L (Donchian/BOS) | structure-break | L | 5273 | **−0.015** | −0.036 | −0.070 | +0.017 | −0.005 | +0.040 | ELIM NEG (near-breakeven) |
| B2 | SB_break_S | structure-break | S | 5066 | −0.067 | −0.088 | −0.001 | −0.081 | −0.121 | −0.117 | ELIM NEG_STRESS |
| B3 | RANGE_fade_L | range-rotation | L | 1855 | −0.259 | −0.282 | −0.195 | −0.321 | −0.293 | −0.064 | ELIM NEG (51% Asia) |
| B4 | RANGE_fade_S | range-rotation | S | 2215 | −0.338 | −0.362 | −0.222 | −0.416 | −0.400 | −0.207 | ELIM NEG (52% Asia) |
| B5 | HOLDdisp_L (R6) | momentum/hold-disp | L | 6232 | −0.215 | −0.238 | −0.218 | −0.241 | −0.214 | −0.102 | ELIM NEG_STRESS |
| B6 | HOLDdisp_S (R6) | momentum/hold-disp | S | 6059 | −0.327 | −0.350 | −0.208 | −0.493 | −0.343 | −0.089 | ELIM NEG_STRESS |
| B7 | MTF_align_L | multi-timeframe | L | 2404 | **−0.026** | −0.047 | −0.127 | +0.080 | −0.053 | −0.003 | ELIM NEG (near-breakeven) |
| B8 | STREAKfade_S | exhaustion | S | 7807 | −2.635 | −2.681 | −2.215 | −3.865 | −1.854 | ELIM (catastrophic) |
| B9 | STREAKfade_L | exhaustion | L | 7733 | −2.522 | −2.567 | −1.893 | −3.761 | −1.912 | ELIM (catastrophic) |
| B10 | VOLonset_L | volatility-onset | L | 1879 | −0.072 | −0.093 | −0.114 | +0.035 | −0.172 | ELIM NEG_STRESS |
| B11 | VOLonset_S | volatility-onset | S | 1869 | −0.030 | −0.051 | +0.071 | −0.072 | −0.059 | ELIM NEG (near-breakeven) |
| B12 | NR_break_L | narrow-range breakout | L | 6014 | −0.221 | −0.243 | −0.231 | −0.273 | −0.194 | ELIM NEG_STRESS |
| B13 | NR_break_S | narrow-range breakout | S | 5995 | −0.261 | −0.284 | −0.253 | −0.309 | −0.229 | ELIM NEG_STRESS |

## Findings
1. **0/13 survivors.** Structure-break, range-rotation, HOLD-displacement, MTF-alignment, exhaustion, volatility-onset, narrow-range breakout all NEG_STRESS cross-era.
2. **Counter-momentum is catastrophic.** STREAK-fade −2.6R (both sides) — fading momentum in XAUUSD gets run over; strongest confirmation that the edge (if any) is WITH momentum (R4).
3. **The near-breakeven cluster is momentum/breakout-CONTINUATION.** SB_break_L −0.015, MTF_align_L −0.026, VOLonset_S −0.030 — all continuation-flavored, all just under breakeven after STRESS cost. The residual XAUUSD price signal is continuation, but M15 cost-drag keeps it sub-breakeven — except the specific S5 session-open structure.
4. **R6 info ≠ expectancy (reconfirmed).** HOLD-displacement (real path information) is −0.22 as a tradeable rr2 entry — matches S10 BOUNDED_NEGATIVE.
5. **Range-fade is Asia-concentrated** (~52%) and negative — range mechanisms live in the illiquid session (echoes R11).

## Implication → Batch C
The continuation cluster sits at breakeven because the 0.24 USD round-trip cost is large relative to an M15 move. The untested lever (§23, timeframe ownership) is to run the same continuation/breakout mechanisms at **H1/H4**, where the same cost is negligible against much larger moves — the most plausible place a residual continuation edge becomes net-positive. Batch C = timeframe study.
