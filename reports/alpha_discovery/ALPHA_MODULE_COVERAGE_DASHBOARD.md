# ALPHA_MODULE_COVERAGE_DASHBOARD — primary Alpha Discovery progress view

Coverage % is MECHANICALLY derived: (materially-covered sub-mechanism branches) / (ratified branch denominator per module).
A branch is "materially covered" ONLY when its major causal hypothesis received info-first AND tradeable/falsification testing.
NOT derived from hypothesis/backtest/commit counts. Denominator = the ratified sub-mechanism branches in ALPHA_STRATEGY_MODULE_
REGISTRY_V1 (4 per module). Updated after every materially-completed branch. Post VE 91b7415 (all causal-verified).

```
M01 TREND          ███████░░░ 75%  (3/4)  survivor:0            → next: persistence-hold sizing
M02 PULLBACK       ███████░░░ 75%  (3/4)  near-miss RESOLVED    → next: Fib/measured retrace
M03 BREAKOUT       ██████████ 100% (4/4)  own-survivor:0 (S5=M07) → complete; S5 uses breakout mechanic (secondary)
M04 RANGE          ██████████ 100% (4/4)  survivor:0  BNEG      → complete (fade/reversion/rotation all fail)
M05 LIQUIDITY      ██░░░░░░░░ 25%  (1/4)  survivor:0  OPEN      → next: strict pool→sweep→reclaim (MK-02)
M06 VOLATILITY     ███████░░░ 75%  (3/4)  info-only non-direc.  → next: vol-regime mean-reversion
M07 SESSION        ███████░░░ 75%  (3/4)  SURVIVOR: S5 (IVAL)   → next: session-transition behavior
M08 AUCTION        █████░░░░░ 50%  (2/4)  survivor:0           → next: value-migration + reclaim (causal)
M09 CROSS-SCALE    ████░░░░░░ 38%  (1.5/4) OPEN (CRS-1 invalid) → next: causal confluence-amplification
M10 TRANSITION     █████░░░░░ 50%  (2/4)  survivor:0  OPEN      → next: MK-01 CHoCH/BOS transition EVENTS
M11 HAZARD         ███████░░░ 75%  (3/4)  survivor:0           → next: survival-without-invalidation
M12 EVENT-SEQUENCE █████░░░░░ 50%  (2/4)  survivor:0           → next: sweep→reclaim→retest (needs pools), multi-leg
M13 IMBALANCE/FVG  █████░░░░░ 50%  (2/4)  survivor:0           → next: BPR + FVG-stack/density
M14 ORDER-BLOCK    █████░░░░░ 50%  (2/4)  survivor:0           → next: OB-mitigation + demand-zone reentry
```

## Machine-readable coverage table
| module | coverage% | confidence | total branches | untested | lightly | subst | bounded_neg | near_miss | survivors | ival | next highest-value open branch |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M01 trend | 75% | HIGH | 4 | 1 | 0 | 3 | 3 | 0 | 0 | 0 | persistence-hold sizing |
| M02 pullback | 75% | HIGH | 4 | 1 | 0 | 3 | 3 | 0(resolved) | 0 | 0 | Fib/measured retrace |
| M03 breakout | 100% | HIGH | 4 | 0 | 0 | 4 | 3 | 0 | 0 | 0 (S5=M07 secondary) | — (complete) |
| M04 range | 100% | HIGH | 4 | 0 | 0 | 4 | 4 | 0 | 0 | 0 | — (complete, BNEG) |
| M05 liquidity | 25% | MED | 4 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | strict pool→sweep→reclaim |
| M06 volatility | 75% | HIGH | 4 | 1 | 0 | 3 | 3(non-dir) | 0 | 0 | 0 | vol-regime mean-reversion |
| M07 session | 75% | HIGH | 4 | 1 | 0 | 3 | 2 | 0 | 1 | **1 (S5)** | session-transition behavior |
| M08 auction | 50% | MED | 4 | 2 | 0 | 2 | 2 | 0 | 0 | 0 | value-migration + reclaim (causal) |
| M09 cross-scale | 38% | MED | 4 | 2 | 1 | 1 | 1 | 0 | 0 | 0 | causal confluence-amplification |
| M10 transition | 50% | MED | 4 | 1 | 1 | 2 | 2 | 0 | 0 | 0 | MK-01 CHoCH/BOS transition events |
| M11 hazard | 75% | HIGH | 4 | 1 | 0 | 3 | 2 | 0 | 0 | 0 | survival-without-invalidation |
| M12 event-seq | 50% | MED | 4 | 2 | 0 | 2 | 1 | 0 | 0 | 0 | sweep→reclaim→retest→hold |
| M13 imbalance/FVG | 50% | MED | 4 | 2 | 0 | 2 | 2 | 0 | 0 | 0 | BPR + FVG-stack/density |
| M14 order-block | 50% | MED | 4 | 2 | 0 | 2 | 2 | 0 | 0 | 0 | OB-mitigation + demand-zone reentry |

**Aggregate:** 14 modules, 56 branches, ~36 materially covered ≈ **64% overall coverage**. Survivors: 1 (S5, IVAL, in M03/M07). No robust survivor found in any other module yet. Highest-value OPEN branches (lowest coverage + distinct primitive + Alpha-unrun): **M05 liquidity (25%), M09 cross-scale (38%), M08/M10/M11/M12/M14 (50%)**. NOTE: all DIRECTIONAL-polarity branches tested (FVG/OB/reference/cross-scale) resolve in the ERA-TREND (R20) — remaining hope is NON-directional/structural branches (hazard-duration, gated sequences, session-transition). No "exhausted" claim is valid without this dashboard (denominator exists, open branches listed).
