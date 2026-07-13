# EXPERIMENT_REGISTRY — from 54 hypotheses to a 10-experiment plan

Read-only planning. No implementation, no backtest, no engine/strategy change, holdout SEALED. Machine copy of
the full tagged 54: `EXPERIMENT_REGISTRY.jsonl`. Frozen specs: `WAVE_{1,2,3}_SPEC.md`.

## Funnel (ETAPA 1–5)
- **54** HGv1 hypotheses → **54 STRUCTURALLY VALID** (all have claim/mechanism/falsifier/difference, ≤2 added
  ingredients, T0-implementable, lookahead-safe, no holdout use, no new primitive).
- **→ 52 after semantic dedup** (2 redundant collapsed) → **all 52 implementable on T0 data**.
- Valid representatives by type: A alpha 36 · B mechanism 2 · C contradiction 4 · D beta 2 · E placebo 3 · F scope 5.
- **→ 10 selected** (≤12 cap): 2 mechanism (B), 2 contradiction (C), 2 beta (D), 2 placebo (E), 2 alpha (A).
  (Only 2 mechanism experiments exist, so B=2 < the 3 cap; F scope-tests documented but not selected into the plan.)

## The 10 selected experiments
| exp | type | wave | hypothesis | question (one line) | resolves |
|---|---|---|---|---|---|
| EXP-01 | B mechanism | 1 | HGv1-042 | does confirmation carry the S1 sweep edge? (confirmed vs raw, paired) | C1 |
| EXP-02 | B mechanism | 1 | HGv1-043 | does the efficiency gate carry S39's edge? (gate on/off) | C2 |
| EXP-03 | D beta | 1 | HGv1-048 | is the sweep edge alpha or gold beta? (beta/regime-matched, long+short) | I7 |
| EXP-04 | D beta | 1 | HGv1-049 | is opening-range alpha or beta? | I7 |
| EXP-05 | E placebo | 1 | HGv1-050 | does the sweep LEVEL matter? (level-label shuffle) | I8 |
| EXP-06 | E placebo | 1 | HGv1-051 | does the prior-day level matter for the fade? | I8 |
| EXP-07 | C contradiction | 2 | HGv1-044+004 | round-number vs breakout (2×2 factorial) | C4 |
| EXP-08 | C contradiction | 2 | HGv1-045 | return-ranked vs value-referenced reversion | C5 |
| EXP-09 | A alpha | 3 | HGv1-002 | does confirmation/structure rescue value-reaction? | C8 |
| EXP-10 | A alpha | 3 | HGv1-005 | does an efficiency gate rescue the always-on router? | C10 |

## Structural-status legend (applied to all 54 in the jsonl)
STRUCTURALLY VALID · DUPLICATE · SEMANTICALLY REDUNDANT · NOT IMPLEMENTABLE · NEEDS EXTERNAL DATA · TOO COMPLEX ·
INVALID CLAIM. In HGv1 none were NEEDS-EXTERNAL-DATA / TOO-COMPLEX / INVALID (the generator's novelty gate + ≤2-
ingredient rule kept them clean); 2 were SEMANTICALLY REDUNDANT.

## Guardrails
Every experiment reuses EXISTING S1–S51 setups (no new primitive), includes an explicit control/ablation arm
(Codex requirement), and runs on a shared matched-null + label-shuffle harness. Treated as ONE hierarchical
family-wise plan (see PRIORITY_MATRIX), not 10 independent significance chances. Nothing runs without a new CEO gate.
