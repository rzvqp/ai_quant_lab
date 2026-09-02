# CONTEXTUAL TRADE SELECTION V1 — winner-vs-loser causal discrimination on 10 base setups

Trade-selection discovery: given a real base setup that sometimes wins and sometimes loses, what PRE-ENTRY context separates the good
instances from the bad? No new strategy factory, no parameter search, no strategy modification. All evidence is **INTERNAL_GENERALIZATION**
(chronological walk-forward on materially-exposed history) — NOT OOS validation. Blind feature IDs were ranked and frozen before unblinding.
Discovery only; nothing promoted; protections intact (S5 / AI-Trader / P007 / MGMT-004 / MT5 / StrategyCatalog untouched; V2 rescue mining not reopened).

## Design (frozen)
- **10 base setups** (register hash `2ad27dae`) — mechanism-diverse S-library families with large balanced winner AND loser populations
  (learning substrates, NOT top expectancy), none is S5: M01 sweep, M02 fade, M03 breakout-retest, M04 compression-expansion, M08 mean-reversion,
  M10 displacement-continuation, M11 structure-break-reversal, M12 range-rotation, M13 imbalance-FVG, M16 auction-value. **125,797 frozen trades**,
  entry/stop/target/cost UNCHANGED; NET_R is the target to be explained.
- **55 strictly-causal context features** (29 sequence descriptors) computed at the DECISION bar `si` using only bars ≤ si — movement path,
  acceleration, path-efficiency, pullback depth, close-location progression, range expansion, overlap/chop, HH/LL structure, volume/participation
  path, volatility path, level distances + approach dynamics, HTF causal state, time/session. Windows 4/8/16/32. Budget frozen (`CTX_SEARCH_BUDGET.json`).
- **Models** (bounded, interpretable, numpy): unfiltered base · L2 logistic (P win) · depth-2 regression tree (one interaction). Nested chronological
  walk-forward (5 expanding folds, purge 96 bars); the TAKE/SKIP threshold is tuned ONLY on train chronology and applied UNCHANGED to the later fold.
- **Negative controls**: label permutation, random-N-matched selection, (time-shift placebo declared). Blind ranking frozen (hash `0c92276e`).

## Result 1 — the discriminator is market STATE, not the arrival PATH (counter to the seeded hypothesis)
Ranking the 55 blind features by |corr with NET_R|, then unblinding: the winner-vs-loser signal lives in **static volatility / participation
STATE**, not in the sequence/path representation the mandate emphasized.

| leading categories | mean \|corr_R\| | trailing categories | mean \|corr_R\| |
|---|---|---|---|
| volume_path · pullback · volatility_path · static_state | 0.024–0.025 | structure (HH/LL) · overlap/chop · path_efficiency | 0.009–0.011 |

**Dynamic/path categories 0.0184 < static/state+time 0.0222** → the elaborate sequence/approach/structure features do NOT lead. Top global
discriminators: `m_volrank`, `atr_vs_atrma`, `compress_flag`, `vol_rel_4/8/16`, `gap_atr`, `hour_utc`. **HOW the market IS at the decision
(volatility regime, participation, compression) matters more than HOW it ARRIVED.**

## Result 2 — one causal state cross-cuts 7 mechanisms (CROSS_SETUP_CONTEXT_FOUND = YES)
The same context separates winners from losers across genuinely distinct mechanisms:

| feature | direction | #setups | #mechanisms |
|---|---|---|---|
| compress_flag | higher (compressed) → **worse** | 7 | 7 |
| m_volrank | higher (participation) → **better** | 6 | 6 |
| atr_vs_atrma | higher (expansion) → better | 5 | 5 |
| vol_rel_8 / vol_rel_4 / vol_rel_16 | higher → better | 4 each | 4 each |
| roc3_atr, ema20_rel_atr | higher → worse | 4 each | 4 each |

**Multiple unrelated setups fail for the same reason: they are taken in LOW-volatility / compressed / low-participation regimes**, and do
better in volatility-expansion / high-volume states. This is a real, controlled, cross-mechanism lesson — and a *state* filter, not the
approach-path/structure/acceptance sequence hypothesized.

## Result 3 — context selects, but the monetizable positive slice is thin
TAKE-ALL vs TAKE-CONTEXT-SELECTED on the pooled INTERNAL_TEST (negative-control gate **PASS**: mean real lift 0.109 vs placebo 0.022):

| class | setups | behaviour |
|---|---|---|
| **PROFITABLE_CONTEXTUAL_SELECTION** | **2** (M11, M12) | selected expectancy turns positive, but thin and aggressive |
| LOSE_LESS_ONLY | 6 | avoids ~83% of losers, stays negative (keeps ~18% of winners) |
| NO_DISCRIMINATION | 2 (M02, M13) | context does not separate |

Best selector — **BASE_SETUP_08 (M12 range-rotation)**: base −0.232R → **selected +0.0127R** (lift +0.244), **93.6% of losers avoided**, N=961,
fires **64/yr** (50 selected in ~9 months), placebo-clean (perm lift −0.008). BASE_SETUP_07 (M11): base −0.058 → +0.0012R (essentially zero).
**But both are achieved by keeping only ~10% of winners, and the selected effect is far too small to power** — 80%-power at 50% shrinkage is
~54,000 months for M12 (effect +0.013R vs R-variance ~1.2). So the information is real; the *validatable positive edge* is not there.

## §31 CEO answers
1. **Which 10 & why?** 10 mechanism-diverse S-library families with large balanced winner+loser counts (learning substrates), not top expectancy; none is S5. 2. **Strongest per-setup differentiator?** Mostly volatility/participation STATE (m_volrank, atr_vs_atrma, vol_rel) + gap + time; see per-setup table. 3. **Approach path?** WEAK — approach/path-efficiency near the bottom (approach_pdh_8 helps only M11/M12). 4. **Structure?** NO — HH/LL structure is the weakest category. 5. **Volume/participation path?** YES — the strongest category; vol_rel recurs across mechanisms (higher→better). 6. **HTF context?** PARTIAL — h4/d1 trend matters for reversal-type setups (M11 fails against H4 trend), not universally. 7. **Time/session after structure?** YES — hour/halfhour persist as discriminators (as in V2). 8. **Any losing setup turned positive?** YES. 9. **How many?** 2 (marginally); 6 lose-less; 2 none. 10. **Loser avoidance?** 90–94% (profitable), ~83% (lose-less). 11. **Winners sacrificed?** HIGH — ~90% (the positive slices are thin). 12. **Setup-specific or cross-mechanism?** BOTH — strong cross-mechanism state recurrence PLUS setup-specific tops. 13. **Human-intuitive feature ranked low?** YES — the CEO's approach-PATH / structure / arrival-sequence ranked LOW; STATE dominated. 14. **Non-obvious discovery?** YES — static volatility/participation STATE cross-cuts 7 mechanisms and beats the sequence/path representation. 15. **Best selector?** BASE_SETUP_08 (M12): fastest, largest lift, placebo-clean — but thin. 16. **Validatable ≤24 months?** NO — effects too small to power despite fast firing.

## §32 FINAL OUTPUT
```
CONTEXTUAL_TRADE_SELECTION_V1_COMPLETE = YES
BASE_SETUPS = 10 · TOTAL_TRADES_ANALYSED = 125797
SETUPS_WITH_PROFITABLE_CONTEXTUAL_SELECTION = 2 · LOSE_LESS_ONLY = 6 · NO_DISCRIMINATION = 2
NEGATIVE_CONTROL_GATE = PASS (mean real lift 0.109 vs placebo 0.022)
APPROACH_PATH_INFORMATION_FOUND = WEAK (present in M11/M12 only; category near the bottom)
STRUCTURE_INFORMATION_FOUND = NO
VOLUME_PATH_INFORMATION_FOUND = YES
HTF_CONTEXT_INFORMATION_FOUND = PARTIAL
CROSS_SETUP_CONTEXT_FOUND = YES (low-volatility/compression/low-participation -> worse, across 5-7 mechanisms)
BEST_CONTEXTUAL_SELECTOR = BASE_SETUP_08 (M12 range-rotation): volatility/participation state + approach_pdh_8 + ema20-location
BEST_BASE_EXPECTANCY = -0.2324R · BEST_SELECTED_EXPECTANCY = +0.0127R · BEST_SELECTED_N = 961
BEST_SELECTED_TRADES_PER_YEAR = 64.1 · BEST_LOSERS_AVOIDED_PERCENT = 93.6% · BEST_WINNERS_RETAINED_PERCENT = 10.2%
NEW_NONOBVIOUS_CONTEXT_DISCOVERY_FOUND = YES (market STATE beats arrival PATH; one volatility/participation state fails 7 mechanisms)
PRACTICALLY_VALIDATABLE_CANDIDATE_EXISTS = NO (selected effects too thin to power; ~54,000 months for the best)
READY_FOR_PROSPECTIVE_FREEZE = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Interpretation for the CEO
Contextual pre-entry information is **real and cross-mechanism** — the negative controls pass, and one causal state (low volatility /
compression / low participation) separates winners from losers across seven distinct mechanisms. But the finding reproduces the campaign's
standing verdict at a new altitude: **the information does not monetize into a validatable positive edge.** Selecting for it either yields a
thin, aggressive positive slice (2/10 setups, +0.001–0.013R, ~10% of winners kept, un-powerable) or a lose-less tilt (6/10). It also
overturns the seeded intuition: the market's STATE at the decision discriminates better than the elaborate sequence/approach/structure
representation. No candidate is ready for a prospective freeze; the honest next step is a genuinely new information source, not a richer
context model over the same price/volume history.
```
CONTEXTUAL_TRADE_SELECTION_V1 = COMPLETE — real cross-mechanism context (compression/participation), but no validatable positive selection
```
