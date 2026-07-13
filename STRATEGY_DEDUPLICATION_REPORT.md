# STRATEGY_DEDUPLICATION_REPORT (S1-S40)

## A. FACTS — result
- **139 Research-Worthy hypotheses → 22 distinct economic candidates** (117 collapsed as duplicates).
- Collapse dominated by S1 (90 RW → 5 mechanisms) and S5 (12 RW → 1; a dead grammar dim removed earlier).
- Machine outputs: `kb_dedup.json` (clusters + members + representative), `kb_correlations.json` (pairwise
  monthly-return correlations with bootstrap CIs), `STRATEGY_REGISTRY.parquet`.

## B. Method (Claude, reconciled with Codex TASK-2 inline design)
Primary clustering = **economic mechanism key** per family (direction + reference/level/mode), collapsing all
tuning dims (RR/exit, lookback, confirmation window, stop variant, entry type, neighbor thresholds). I then
**validated** the clustering with actual monthly-return correlations (to catch under-/over-clustering), which
is Codex's ledger-level check. Codex's proposed quantitative thresholds are adopted as the standard:

- **Exact duplicate:** identical normalized ledger (entry/exit times, side, R within 1e-6).
- **Execution duplicate:** trade Jaccard ≥95%, R-corr ≥0.98, monthly-corr ≥0.98, trade-count diff ≤5%.
- **Parametric (neighbor) duplicate:** Gower parameter distance ≤0.20, entry overlap ≥75%, monthly-corr ≥0.85.
- **Economic duplicate (cross-family):** matching causal signature AND (overlap ≥70% & monthly-corr ≥0.80).
  Different reference pools, opposite sides, or reversal-vs-continuation stay SEPARATE even if correlated.
- **Representative:** cluster medoid, tie-broken by a robustness score (val_exp, median, trim5, wo1,
  positive-month rate, years, low t1/t3/t5, low DD), prefer simpler params then larger n — **NOT expectancy** (Codex).

## C. CLAUDE INTERPRETATION — correlation-validated economic de-redundancy
Beyond the 22 mechanism-key clusters, the monthly-return correlations reveal a **second-order economic
duplicate group** (CI excludes 0):
- **Long-momentum cluster:** S9-any ↔ S9-align **r=.88**; S20-breakout ↔ S9 **r=.75**; S17-pwhigh-break ↔ S39 **r=.60**;
  S17-pwhigh-break ↔ S9 **r=.52**. These are **ONE economic bet** (HTF-aligned bullish continuation) — do NOT
  count as independent confirmations. Collapse to ONE representative for validation (Codex agrees, TASK 4/5).
- S5 ↔ S6-ny-breakout **r=.53** (both NY-session long momentum) — related but distinct trigger; kept separate, flagged.
- Most other pairs have wide CIs crossing 0 (only ~26 common months) → low-correlation ≠ decorrelation
  (repairs the earlier retracted "S1/S5/S9 decorrelated" claim).

## D. Cluster table (22 distinct; representative metrics)
Each row = one distinct candidate: `cluster_id`, member count, representative id, and rep metrics are in
`kb_dedup.json`. Direction/pool/mode distinctions kept (e.g., S1 low/pdh long ≠ S1 high/pdh short; S17
pw_high-break ≠ pw_low-reject). Keep/drop recommendations are in TOP_STRATEGIES_SHORTLIST.md.

## E. Over-/under-clustering checks (Codex TASK-2 diagnostics)
- **Under-clustering guard:** the correlation pass found the momentum cluster that mechanism-keys alone kept
  separate → flagged for collapse (prevents inflated multiple-testing confidence).
- **Over-clustering guard:** within-cluster members share side, holding, and ≥0.85 monthly-corr; no cluster
  mixes opposite sides or reversal/continuation. Representative selection is robustness-ranked, not peak-picked.
- **Sensitivity:** distinct count is stable at ~22 by mechanism-key; collapsing the momentum cluster → ~18
  truly independent economic bets. Report both (base 22 / economic-independent ~18) as the range.

## D-note (Codex filesystem). CODEX FILESYSTEM REVIEW PENDING — Codex validated the dedup METHOD inline (TASK 2)
but could not read the Tier-B result files (stale sandbox), so its ledger-level thresholds were not executed by
Codex on this data; I applied the correlation validation myself.
