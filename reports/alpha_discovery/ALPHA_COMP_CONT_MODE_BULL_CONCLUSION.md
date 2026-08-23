# COMP-CONT-L-MODE-BULL-v1 — COMP_CONT_MODE_BULL_BOUNDED_NEGATIVE

Mandate `ALPHA-COMP-CONT-MODE-BULL-V1-001`. NEW research identity `COMP-CONT-L-MODE-BULL-v1` — inherits NOTHING from the independently-failed `COMP-CONT-L-rr2` (that failure remains authoritative/final). Question: does gating H4 compression→continuation LONG on the FROZEN `MARKET_OPERATING_MODE_V1 == PRIMARY_BULL_IMPULSE` (replacing the old D1-uptrend regime) make it robust? Information-first, frozen mode untouched, no post-hoc regime rescue (only PRIMARY_BULL tested). Impl: `comp_cont_mode.py`. H4 compression (box<0.7·box_ma & atr/atr_ma<0.9 over NB=8) → up-continuation (close>box_hi & range>1.3·atr); forward 12 H4 bars (2 days); structural stop = compression low; STRESS 0.24.

## Information-first (§3) — does PRIMARY_BULL add stable information?
| era | comp-cont GLOBAL P70 L/S | inside PRIMARY_BULL P70 L/S | Δasym(L−S) global→PB | tradeR (structSL, STRESS) |
|---|---|---|---|---|
| b0 (2011-13) | L0.34/S0.49 (−0.15) | L0.40/S0.44 (−0.04) | +0.11 (nudges long) | **−0.036** (n25) |
| b1 (2016-18) | L0.45/S0.35 (+0.10) | L0.46/S0.29 (+0.17) | +0.07 (nudges long) | **+0.196** (n24) |
| DEV (2021-23) | L0.33/S0.30 | **thin (<20)** | — | thin |
| CAL (2024) | thin | thin | — | thin |

PRIMARY_BULL **does** add a mild, consistent LONG nudge (asymmetry improves toward long in both eras). But the resulting comp-cont-long still **SIGN-REVERSES** across the two populated same-mode eras: short-leaning & negative in b0 (bear era), long-leaning & positive in b1. Pooled N=49, avgR +0.077, DISC +0.027 / CONF +0.151 — the pooled positive hides the b0/b1 sign split; pos-eras 1/2.

## Verdict — BOUNDED_NEGATIVE (§9)
1. **Same-mode cross-era sign reversal** (b0 avgR −0.036 / short-lean vs b1 +0.196 / long-lean) — the explicit §9 FAIL trigger.
2. **Inadequate N**: only ~25 PRIMARY_BULL comp-cont events per dense era; **thin (<20) in DEV and CAL** — the mechanism cannot even be established in the 2021-2024 block.
3. Works in exactly one era (b1) — fails §10 (cross-era consistency + adequate N).
4. Confirmed across framings: my prior M15-native S4 test showed the identical reversal (PRIMARY_BULL comp-cont-long b0 −0.14 / b1 +0.21).

**PRIMARY_BULL is NOT a materially sufficient regime definition to rescue compression-continuation** — it nudges direction but does not deliver cross-era stability or adequate frequency. The old D1-uptrend failure is not converted to a PASS. Closing the mechanism. No rescue (§5: not cycling to BULL_CORRECTION / session / vol buckets; §9: do not rescue). No S5-independence test (nothing survived). `COMP-CONT-L-rr2` and MARKET_OPERATING_MODE_V1 untouched.

## Radar R25
Frozen PRIMARY_BULL mode adds a mild consistent LONG nudge to H4 compression-continuation but does NOT make it cross-era-stable: comp-cont-long sign-reverses b0(−)/b1(+) and is thin in DEV/CAL. Mode-conditioning (even the frozen causal PRIMARY_BULL) cannot fix the era-trend dependence (R20) of a directional continuation mechanism. COMP_CONT_MODE_BULL closed.
