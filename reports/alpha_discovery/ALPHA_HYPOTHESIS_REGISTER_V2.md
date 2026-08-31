# ALPHA_HYPOTHESIS_REGISTER_V2 — 20 raw → dedup → tested → falsified

Data-driven from the Behavior Atlas + Contrast Miner. §7 cap = 20 raw. §8 dedup by economic mechanism → 3-5 distinct. Each raw
hypothesis screened against ALPHA_NEGATIVE_KNOWLEDGE_BASE_V1 (reject renamed failures / parameter clones / no-causal-mechanism).

## 20 raw hypotheses + dedup verdict
| ID | name | mechanism | dedup verdict |
|---|---|---|---|
| R01 | HTF-aligned breakout continuation | trend-align break | REJECT — VOLTIME-2/module-taxonomy (breakout aligned still net-neg; contrast HTF +0.11 insufficient) |
| R02 | impulsive-break continuation | velocity filter | REJECT — contrast: impulse WORSE (move spent) |
| R03 | fresh-level break | test-count filter | REJECT — contrast: freshness no help |
| R04 | discount-location long break | location filter | REJECT — contrast: discount −0.375 still neg |
| R05 | **failed-break fade to structural mid** | mean-reversion at sweep | **KEEP (H1)** — distinct (fade, not continuation), structural target |
| R06 | **sweep → opposite-break reversal** | liquidity-grab reversal | **KEEP (H2)** — distinct (double-break monetization) |
| R07 | **HTF-aligned break to STRUCTURAL target** | target-space exit (not R-multiple) | **KEEP (H3)** — distinct exit logic (§17E) |
| R08 | reclaim continuation | break-fail-reclaim | REJECT — SF-1/VOLPATH reclaim coinflip |
| R09 | range-edge rejection fade | Asia/London extreme | REJECT — SF-1 coinflip |
| R10 | session ORB (non-NY) | opening-range | REJECT — VOLTIME-4/SF-2 net-neg |
| R11 | CHoCH reversal | structural failure | REJECT — CHoCH EXACT null 0.334 |
| R12 | compression breakout (DXY-filtered) | vol-timing + exo filter | REJECT — DXY-NDX1 tradeability net-neg |
| R13 | straddle around compression | two-sided harvest | REJECT — VOLPATH straddle net −0.375, pays twice |
| R14 | post-classification momentum | delayed breakout | REJECT — VOLPATH REDUNDANT (net −0.519) |
| R15 | target-space (room-to-run) long | structural room | REJECT — contrast: more room WORSE |
| R16 | premium short / discount long (structural MR) | value reversion | REJECT — M04 range/reversion bounded-neg |
| R17 | volatility-onset directional | R26 vol-timing | REJECT — R26 non-directional |
| R18 | prior-day level acceptance/rejection | auction reference | REJECT — M08 auction bounded-neg |
| R19 | multi-session inheritance | Asia→London→NY chain | REJECT — Batch-D S5-redundant / SF-1 |
| R20 | order-block / demand-zone reentry | supply/demand | REJECT — M14 era-split |

## Deduplicated distinct set (3) → TESTED (`factory_falsify.py`, STRESS 0.24, cross-era, best-trade-removed)
- **H1 FAILED_BREAK_FADE_STRUCTURAL** (R05): n=21,379, **netR −0.256** (D/C/O −0.25/−0.26/−0.25), best-trade-removed −0.256. **FALSIFIED.**
- **H2 SWEEP_REVERSE_STRUCTURAL** (R06): n=1,905, **netR −0.259** (D/C/O −0.30/−0.20/−0.25). **FALSIFIED.**
- **H3 STRUCTURAL_TARGET_BREAK** (R07): n=6,188, **netR −0.360** (D/C/O −0.37/−0.43/−0.26). **FALSIFIED.**

All net-negative, cross-era sign-stable-negative, NOT one-trade-dependent (robustly negative). **SURVIVED_INTERNAL_FALSIFICATION = 0.
NEW_STRATEGY_CANDIDATES = 0.** 17 of 20 raw were renamed prior failures (dedup working as intended); the 3 genuinely-distinct mechanisms
(fade, reversal, structural-target) also fail — confirming direction efficiency extends to mean-reversion and structural-target exits.
