# Mandate 4.1 — Transactional evaluation of E001/E002/E004. NUMBERS ONLY.

FROZEN V1 structural events (`V1_OPERATIONALIZED_CONTRACTS.md`) run through the PATCHED §9.4.1 execution
contract (`ai_quant_lab` `statistician-foundation` @ `3ef47b7`, read integrally). No V1 parameter
adjusted, optimized, or reformulated. Script `edge_research/mandate41_eval.py`, raw
`edge_research/mandate41_eval_results.json`. Order-block family (E010/E013/E015/E016) untouched. **No
viability conclusion — numbers only.**

**Data (official loader v5, discovery half only):** `M15_v2`, **130,491 bars**, 2011-07-26 → 2021-09-03,
manifest v2.2.0, hash/status-gated. **3 regimes** (bear / bull / correction). **Regime 4 (2022-10→2026-02
bull +223.3%) is NOT in M15_v2's delivered discovery** — it is M15 legacy and **SAME-WINDOW-RESAMPLED**
(the window that informed V1 parametrization), so it is **excluded from this confirmation run**, per the
manifest's `same_window_resampled_predicate`. Sealed halves untouched.

**Execution (patched §9.4.1):** entry@next-open — E001 after the sweep bar (inverse of break), E002 at
the 08:00 bar after an aggressive Frankfurt move (opposite the move), E004 after FVG formation (FVG
polarity) + separate `fill` binary. Stop $4.00 official / $5.00 sensitivity. RR 1:1 (target=1×stop) and
1:2 (target=2×stop), separate. Cost $0.40 round-trip, net-of-cost R. Tie-break worst-case (stop-first)
with best-case bracket. ≤1 entry/day/edge.

## Per edge × regime × RR (official stop $4.00) — no aggregation

R = net-of-cost. `E_worst` uses stop-first on undetermined bars; `E_best` = target-first bracket.
Concentration (best/sumR, top-3, top-5) is **N/A wherever net sumR ≤ 0** (all cells here). `NRM15` =
NOT-RESOLVABLE-AT-M15 (undetermined fraction > 25%).

### E001 — Asia-range sweep, inverse
| Regime | RR | n | timeout | undet% | winrate | E_worst (R) | E_best (R) | net sumR | wo1>0 | NRM15 |
|---|---|---|---|---|---|---|---|---|---|---|
| bear (-42.0%) | 1:1 | 465 | 0 | 0.65% | 0.4710 | −0.158 | −0.145 | −73.5 | no | no |
| bear | 1:2 | 465 | 0 | 0.22% | 0.2989 | −0.203 | −0.197 | −94.5 | no | no |
| bull (+86.3%) | 1:1 | 454 | 0 | 0.66% | 0.4758 | −0.149 | −0.135 | −67.4 | no | no |
| bull | 1:2 | 454 | 0 | 0.44% | 0.2996 | −0.201 | −0.188 | −91.4 | no | no |
| corr (-17.4%) | 1:1 | 218 | 0 | 0.46% | 0.4954 | −0.109 | −0.100 | −23.8 | no | no |
| corr | 1:2 | 218 | 0 | 0.46% | 0.3394 | −0.082 | −0.068 | −17.8 | no | no |

### E002 — Frankfurt aggressive move, reversal
| Regime | RR | n | timeout | undet% | winrate | E_worst | E_best | net sumR | wo1>0 | NRM15 |
|---|---|---|---|---|---|---|---|---|---|---|
| bear | 1:1 | 317 | 0 | 0.63% | 0.4416 | −0.217 | −0.204 | −68.7 | no | no |
| bear | 1:2 | 317 | 0 | 0.00% | 0.2997 | −0.201 | −0.201 | −63.7 | no | no |
| bull | 1:1 | 288 | 0 | 0.69% | 0.4792 | −0.142 | −0.128 | −40.8 | no | no |
| bull | 1:2 | 288 | 0 | 0.35% | 0.3160 | −0.152 | −0.142 | −43.8 | no | no |
| corr | 1:1 | 129 | 0 | 0.00% | 0.5194 | −0.061 | −0.061 | −7.9 | no | no |
| corr | 1:2 | 129 | 0 | 0.00% | 0.3566 | −0.030 | −0.030 | −3.9 | no | no |

### E004 — First post-US-open FVG, polarity
| Regime | RR | n | timeout | undet% | winrate | E_worst | E_best | net sumR | wo1>0 | NRM15 |
|---|---|---|---|---|---|---|---|---|---|---|
| bear | 1:1 | 464 | 0 | 0.22% | 0.4914 | −0.117 | −0.113 | −54.4 | no | no |
| bear | 1:2 | 464 | 0 | 0.22% | 0.3211 | −0.137 | −0.130 | −63.4 | no | no |
| bull | 1:1 | 478 | 0 | 0.84% | 0.4791 | −0.142 | −0.125 | −67.8 | no | no |
| bull | 1:2 | 478 | 0 | 0.63% | 0.3222 | −0.134 | −0.115 | −63.8 | no | no |
| corr | 1:1 | 221 | 1 | 0.45% | 0.5158 | −0.068 | −0.059 | −15.1 | no | no |
| corr | 1:2 | 221 | 1 | 0.00% | 0.3122 | −0.163 | −0.163 | −36.1 | no | no |

**E004 `fill` rate (separate binary, per regime):** bear 0.718, bull 0.736, correction 0.662.

## BH-FDR — family of 6 (3 edges × 2 RR, official stop $4, pooled across regimes)

Per §6. One-sided binomial vs the cost-adjusted break-even winrate `w* = (1+0.4/S)/(RR+1)` (§9.4
break-even convention). BH at α=0.05.

| Test | n | winrate | break-even | p (one-sided) | BH crit | passes |
|---|---|---|---|---|---|---|
| E001 RR1 | 1137 | 0.4776 | 0.5500 | 1.000 | 0.05000 | no |
| E001 RR2 | 1137 | 0.3069 | 0.3667 | 1.000 | 0.03333 | no |
| E002 RR1 | 734 | 0.4700 | 0.5500 | 1.000 | 0.04167 | no |
| E002 RR2 | 734 | 0.3161 | 0.3667 | 0.998 | 0.00833 | no |
| E004 RR1 | 1163 | 0.4910 | 0.5500 | 1.000 | 0.02500 | no |
| E004 RR2 | 1163 | 0.3199 | 0.3667 | 1.000 | 0.01667 | no |

**Passing: NONE.**

## Sensitivity — stop $5.00 (not in the family)

Pooled winrate vs break-even (all below): E001 RR1 0.464/0.540, RR2 0.302/0.360; E002 RR1 0.477/0.540,
RR2 0.319/0.360; E004 RR1 0.486/0.540, RR2 0.314/0.360. Full per-regime cells in the JSON.

## Facts (no interpretation)

- Undetermined fraction < 1% in every cell → all combinations resolvable at M15 (well under the 25%
  `NOT-RESOLVABLE-AT-M5` gate); the worst/best bracket is stable (Part 1's rare-indeterminacy prediction
  holds empirically). Timeouts: 0–1 per cell.
- Net sumR ≤ 0 in every cell → concentration metrics (best/sumR, top-3, top-5) are N/A and wo1 is not
  positive anywhere.
- No viability conclusion drawn; no winrate targeted. The Statistician/CEO decide what these numbers mean.
