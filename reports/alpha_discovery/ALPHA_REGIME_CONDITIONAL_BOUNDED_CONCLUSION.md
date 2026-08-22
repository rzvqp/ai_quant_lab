# ALPHA_REGIME_CONDITIONAL_BOUNDED_CONCLUSION

Mandate `ALPHA-XAUUSD-REGIME-CONDITIONAL-STATE-PATH-DISCOVERY-001`. The regime-conditional method has been applied end-to-end: a causal regime taxonomy was frozen first, regime-conditional baselines established, and within-regime states + regime transitions screened with the **same-regime / same-transition cross-era** generalization gate. This is the bounded conclusion (§26) — NOT `PRICE_ONLY_ALPHA_IMPOSSIBLE`.

## Method executed
1. **Frozen causal taxonomy** (`state_regime.py`): UP/DOWN/QUIET/CHOP/TRANSITION from eff/trend/vol. **Reproducible** — each regime 8-34% in EVERY era (2021/2022/2023 + b0/b1); recurs, not "year 2022".
2. **Regime-conditional baselines** established (`ALPHA_REGIME_PATH_BASELINES.md`) — stable across eras (unlike raw lifts).
3. **Within-regime state discovery:** DOWN & QUIET (SHORT), UP & CHOP (LONG) — ~8 causal states each, lift over same-regime base, within-regime DISC/CONF + per-year + same-regime cross-era.
4. **Regime-transition family (§27):** 8 onsets A->B, forward path lift vs destination-regime base, same-transition cross-era.

## Findings
| result | evidence |
|---|---|
| **Only same-transition-cross-era-STABLE positive = QUIET->UP LONG** | +0.099 DEV / +0.048 b0b1 — but tiny N (40/72) AND **REDUNDANT with COMP-CONT-L** (compression->uptrend). The method independently re-discovered the already-frozen edge. |
| Strongest within-regime signal (DOWN+falling-vol SHORT +0.097, flawless within-period) | FAILS same-regime cross-era (b0 -0.029). State->path is era-dependent EVEN WITHIN a fixed regime. |
| Stable filters (not trades) | DOWN rising-vol, CHOP falling-vol -> LONG/SHORT avoidance; re-encode trend-drive presence. |
| Everything else | regime-transient (fails same-regime cross-era), immaterial (<0.04), or INSUFFICIENT_SAME_REGIME_EVIDENCE. |

## Central conclusion (bounded, evidence-backed)
**No NEW non-redundant, material, same-regime(-transition)-stable price-only edge exists in the mapped regimes/transitions.** The single same-transition-cross-era-stable POSITIVE signal is the compression->uptrend LONG **already frozen as COMP-CONT-L** — so the regime-conditional method **confirms COMP-CONT-L is a genuine regime-transition edge** and finds no additional independent one. The deeper result: price-only state->path relationships are era-dependent **even within a fixed causal regime** — a regime *label* is not sufficient to make a price-only edge portable across eras. This is the strongest possible internal validation of the one edge we have, and a clear boundary on price-only discovery.

## Portfolio status
- **S5** — frozen, independently validated (benchmark).
- **COMP-CONT-L-rr2** — FROZEN_PENDING_INDEPENDENT_VALIDATION; now independently corroborated as a genuine QUIET->UP (compression->uptrend) regime-transition LONG edge.
- **H4-bo-raw-S** — INDEPENDENT_VALIDATION_BLOCKED (non-causal legacy D1 filter); reference only.

## CEO decision requested
1. **Send COMP-CONT-L-rr2 to independent validation** — it is now confirmed by two independent methods (original swing discovery + regime-conditional re-discovery). Highest-value next step for the portfolio.
2. **Re-authorize the exogenous frontier with provisioned data** — the price-only ceiling is now well-characterized (era-dependent even within regimes); an exogenous, potentially-stationary driver is the most likely source of a NEW independent edge. (`acquisition_staging/dxy` appeared; provisioning may be underway — still requires explicit CEO authorization.)
3. **Accept the regime-specific portfolio** and build a causal regime-router overlay (separate mandate).

Auto-loop paused at this decision point; global program ACTIVE.
