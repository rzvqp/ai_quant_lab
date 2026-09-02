# OB_CAUSAL_EXECUTION_COMPARISON_V1 — §20 primary comparison

Structure frozen from OBR (unchanged): bullish last-bearish-candle OB + close-BOS of causal 20-bar swing high + displacement ≥1.5 ATR +
fresh first retest + LN/NY. Only the EXECUTION changes. Stop = block_low−0.1ATR (floored ≥0.5ATR risk); target = 2R. **Same-bar ordering
is CONSERVATIVE** (any bar reaching both stop and target → counted as STOP/loss). Cost = price-cost $0.419/risk; harsh = +0.15R extra.
Code: `ob_exec.py`, `ob_exec_compare.py`. Regression test: `test_ob_exec_fill.py`.

## Old fill artifact (reproduced + frozen)
```
OLD_BUGGY_FILL  net=+0.1536  N=2122   <- resting limit cancelled when the SAME bar closed below block_low (dropped same-bar losers)
EXEC_A corrected net=-0.0673 N=2486   <- keeps those 364 same-bar filled-then-closed-below LOSSES; matches Statistician -0.067 exactly
OLD_FILL_ARTIFACT_REPRODUCED = YES · OLD_OBR_BULL_1_REMAINS_FALSIFIED = YES
```

## §20 primary comparison table (bull, disp≥1.5, LN+NY, 2R)
| EXECUTION | N | NET_R | WR | PF | MAX_DD | D | C | O | DEV | OOS | BEST1%_RM | CTRL_NET_R | OB−CTRL | HARSH_COST | VERDICT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **EXEC-A** true resting limit | 2486 | **−0.067** | 0.412 | 1.40 | 239R | −0.092 | −0.081 | +0.003 | −0.092 | −0.041 | −0.087 | −0.122 | +0.055 | −0.154 | **FALSIFIED** |
| **EXEC-B** retest close→next open | 2160 | **−0.266** | 0.329 | 0.97 | 596R | −0.310 | −0.252 | −0.182 | −0.310 | −0.219 | −0.288 | −0.260 | −0.006 | −0.409 | **FALSIFIED** |
| **EXEC-C** rejection close→next open | 1896 | **−0.206** | 0.329 | 0.97 | 402R | −0.262 | −0.184 | −0.103 | −0.262 | −0.146 | −0.227 | −0.177 | −0.029 | −0.412 | **FALSIFIED** |
| **EXEC-D** penetration+reclaim→next open | 955 | **−0.185** | 0.335 | 1.00 | 224R | −0.261 | −0.303 | +0.133 | −0.261 | −0.108 | −0.206 | −0.192 | +0.007 | −0.392 | **FALSIFIED** |

## §7 same-bar ordering (specified before testing; conservative worst-case)
```
EXEC-A: ENTRY_TS = fill instant (first bar low≤block_high); STOP_ACTIVE_FROM = fill bar; TARGET_ACTIVE_FROM = fill bar
        SAME_BAR_AMBIGUOUS_TRADES = 440 / 2486 (18%) -> ALL assigned STOP (loss). This is exactly where the artifact lived.
EXEC-B/C/D: ENTRY_TS = next-bar OPEN after signal-bar close; STOP/TARGET_ACTIVE_FROM = entry bar; ambiguous 57 / 13 / 4 -> STOP.
SAME_BAR_CONSERVATIVE_OUTCOME_POLICY = ambiguous → stop-first (never infer favorable intrabar order from OHLC).
```

## Reading
- **EXEC-A** (corrected canonical) reproduces the Statistician's −0.067R — the sanity baseline is negative, as expected.
- **EXEC-B/C/D** (next-bar-open variants) are *worse* (−0.18 to −0.27): giving up the block-edge fill price and entering at the next open
  pays away the level advantage; PF ≈ 1.0 (coinflip on 2R:1R after cost). Only EXEC-D shows an O-era positive (+0.133) = the R20 era-trend
  again, negative in D/C.
- **Matched timing-controls:** OB−CTRL is +0.055 (A), −0.006 (B), −0.029 (C), +0.007 (D). The OB level's edge over a height-matched
  shifted level is small and does not survive into positive net-R under any execution. `OB_EXECUTION_INCREMENTAL_INFORMATION_FOUND = NO`.
- Max drawdowns (224–596R) are alone disqualifying.

## Conclusion
No causal execution converts the (independently-confirmed) OB level information into positive net expectancy.
**ORDER_BLOCK_LEVEL_INFORMATION_CONFIRMED_BUT_NOT_CURRENTLY_MONETIZABLE.**
