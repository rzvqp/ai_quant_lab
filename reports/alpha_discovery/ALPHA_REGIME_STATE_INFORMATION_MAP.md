# ALPHA_REGIME_STATE_INFORMATION_MAP

Within-regime state->path information (mandate `ALPHA-XAUUSD-REGIME-CONDITIONAL-STATE-PATH-DISCOVERY-001`). For each regime, causal states screened for MATERIAL lift over the SAME-REGIME base rate (§2, §17), validated across same-regime occurrences DEV vs b0/b1 (§9). Foundation (taxonomy + baselines) done; per-regime state screens follow.
QUEUED (priority): DOWN-regime SHORT states; QUIET-regime states; then UP/CHOP/TRANSITION. LONG/SHORT separate (§13). No threshold mining (§11).

## DOWN & QUIET regime SHORT screen (`state_regime_discover.py`) — same-regime cross-era gate
DOWN SHORT base: DEV 0.413 / b0 0.439 / b1 0.364. QUIET SHORT base: DEV 0.403 / b0 0.452 / b1 0.372.
| regime | state | DEV lift | DISC/CONF | per-year | same-regime b0/b1 | verdict |
|---|---|---|---|---|---|---|
| DOWN | **falling_vol (vc<0.9)** | **+0.097** | +0.11/+0.08 | all yrs + (0.07/0.08/0.10) | **b0 -0.029 / b1 -0.001** | strong within-DEV, FAILS same-regime cross-era |
| DOWN | rising_vol | -0.060 | -/-consistent | all yrs - | b0 +0.031/b1 +0.008 (inverts) | not stable |
| DOWN | deep_below_ema | +0.024 | +/+ | mixed | b0 +0.005/b1 +0.008 (immaterial) | immaterial |
| QUIET | fresh_down_imp | +0.032 | +/+ | 2021 -0.06 | b0 +0.042/b1 +0.013 (same-sign!) | same-sign cross-era but IMMATERIAL (<0.04) + 2021-inconsistent |
| QUIET | bounced_top / deep_below | -0.046 / -0.066 | mixed | mixed | invert | not stable |
**Verdict:** NO material same-regime-stable SHORT signal in DOWN/QUIET. Key deepening of the meta-finding: **even WITHIN the same causal regime, state->path lifts are era-dependent** — the strongest within-DEV regime-conditional signal (DOWN+falling-vol +0.097, flawless within-period across all years + DISC/CONF) still FAILS same-regime cross-era (b0 -0.029). The only same-sign-cross-era effects (QUIET fresh-down-imp) are economically immaterial (<0.04). Same-regime cross-era is a genuine, strict gate.

## UP & CHOP regime LONG screen
UP LONG base DEV 0.376: no stable positive (rising_vol +0.022 but b1 -0.044 inverts). CHOP LONG base 0.436: falling_vol -0.041 STABLE (b0 -0.022/b1 -0.044) = LONG-AVOIDANCE filter (not a trade); rest flat. No new stable positive LONG in UP/CHOP.
