# ALPHA_STATE_PATH_BOUNDED_CONCLUSION

Mandate `ALPHA-XAUUSD-CAUSAL-STATE-PATH-DISCOVERY-001`. The causal price-only state->path information space has been **systematically mapped** across 5 state families using the outcome-first method (first-passage `P(+X before -Y)`, multi-horizon, LONG/SHORT separate, base-rate lift, per-year + DISC/CONF + **cross-population**). This is the whole-map conclusion the mandate requires (§26) — **not** a claim that price-only alpha is impossible.

## What was mapped (engines: state_path / state_validate / state_transitions / state_pathhist(+xpop) / state_multitf / state_session)
| family | strongest signal | within-DEV stability | cross-population (b0/b1) | verdict |
|---|---|---|---|---|
| static state | trend-extension -> SHORT | +0.081 top-decile, but DISC+ -> CONF- | inverts (~0) | regime-transient KILLED |
| transition A->B | up-efficiency-drop -> LONG-avoidance | -0.069 stable | (negative filter) | filter, not a trade |
| path-history | clean-advance-near-highs -> SHORT | **+0.039, all years + DISC/CONF** | **INVERTS -0.01..-0.05** | regime-conditional KILLED |
| multi-TF | H4-trend -> H1 direction | +0.028 (trend-beta) | ~0 on b0 | weak + REDUNDANT |
| session | London->SHORT / NY->LONG | +0.036 / +0.024 stable | same-sign but +0.002..+0.012 | stable but IMMATERIAL |

## Central finding (evidence-backed)
**Causal price-only state->path relationships on XAUUSD are REGIME-CONDITIONAL, not stationary.** Every *material* state->path lift found in 2021-2023 (trend-extension exhaustion, clean-advance exhaustion) is a property of that macro-regime and **inverts** on 2011-2018 (b0/b1). The only *cross-population-stable* effects are (a) a faint session microstructure (London slightly favors shorts, NY slightly favors longs) that is **economically negligible** (+0.002-0.012 lift, untradeable after cost), and (b) trend-drive presence -> same-direction continuation, which is **already captured by the frozen COMP-CONT-L** (redundant).

**Why this matters:** it explains, at the information level, *why* the whole price-only program (19 named-pattern frontiers + 5 state-path families) produced only **regime-specific** robust edges — COMP-CONT-L (2021-2023-specific LONG) and H4-bo-raw-S (2011-2018-specific SHORT). A price-only state that predicts path in one regime predicts the opposite in another; a single stationary, tradeable, non-redundant price-only edge does not appear in the mapped space.

## Methodological result (reusable)
Within-period stability (per-year + DISC/CONF inside one macro-regime) is **necessary but NOT sufficient** — per-year splits share the regime. **Cross-population (a different era) is the decisive generalization gate.** The path-history SHORT signal passed the entire within-period battery and still inverted cross-population. This gate is now standard for all future state candidates.

## CEO DECISION REQUESTED (the productive next levers are CEO-gated)
No material cross-population-stable non-redundant price-only edge exists in the mapped space. The genuine options:
1. **Re-authorize the EXOGENOUS frontier WITH provisioned data** — the state map shows price-only information is regime-conditional; an *exogenous* driver (DXY/real-yields) is the most likely source of a stationary, uncorrelated signal. Blocked only on data (`ALPHA_EXOGENOUS_DATA_REQUIREMENTS.md`).
2. **Accept the REGIME-SPECIFIC portfolio** — S5 (validated) + COMP-CONT-L-rr2 & H4-bo-raw-S (pending independent validation), explicitly operated as regime-specific edges with a regime-detection overlay (a separate mandate).
3. **Authorize a genuinely different price-only population** (a new era of ratified data) to search for another regime-specific edge.

Per §26 this is a **bounded** conclusion with the full information map attached (`ALPHA_STATE_INFORMATION_MAP.md`, candidate registry, MT ledger), **not** `PRICE_ONLY_ALPHA_IMPOSSIBLE`. Global program ACTIVE; auto-loop paused at this decision point.
