# WAVE1_HANDOFF — everything a NEW chat needs to start Wave 1

This file is self-contained: a new session can begin Wave 1 from the official artifacts WITHOUT the prior
conversation. **Wave 1 is PLANNED, FROZEN, NOT STARTED. Do not implement or run anything without a new CEO gate.**

## Official state
- Branch: **research-main** · close commit recorded in PROJECT_STATE_v1.0.md · engine **mstrat.py v2** (FROZEN).
- Data: XAUUSD M15 84,152 bars (+H1/H4/D1), portable path `code/mtf.py D = Path(__file__).parents[1]/data/market`.
- Matched-null = VALIDATED ENGINE (Verdict A), applied only to a 10-hyp pilot. Global-FDR NOT run. Holdout SEALED.

## Why Wave 1
S1–S51 produced a knowledge base of 19 behavioral primitives, an ontology (9 invariants, knowledge graph),
Hypothesis Generator v1 (54 candidates) and Experiment Planner v1 (a 10-experiment plan). Wave 1 is the first,
highest-information batch: controls + beta diagnostics + mechanism experiments that UPDATE the most Knowledge-
Graph edges and build the two reusable harnesses (matched-null control + level-label shuffle). Full spec:
`knowledge/experiments/WAVE_1_SPEC.md` (+ WAVE_2/3 for later).

## The six Wave-1 experiments
| exp | type | hypothesis | research question | H0 | H1 | primary contrast |
|---|---|---|---|---|---|---|
| EXP-01 | mechanism | HGv1-042 | does confirmation carry the S1 sweep edge? | confirmed ≤ raw (same events) | confirmed > raw by margin | confirmed-vs-raw, paired identical sample |
| EXP-02 | mechanism | HGv1-043 | does the efficiency gate carry S39's edge? | gated ≤ gate-off | gated > gate-off | gate-ON vs gate-OFF, same signals |
| EXP-03 | beta | HGv1-048 | sweep: timing-alpha or gold beta? | expectancy ≤ beta/regime-matched null | > matched null | observed vs beta/regime/direction-matched null |
| EXP-04 | beta | HGv1-049 | opening-range: alpha or beta? | ≤ matched null | > matched null | observed vs matched null |
| EXP-05 | placebo | HGv1-050 | does the sweep LEVEL matter? | shuffled-labels ≈ real | real ≫ shuffled | real vs level-label-shuffled |
| EXP-06 | placebo | HGv1-051 | does the prior-day level matter for the fade? | shuffled ≈ real | real ≫ shuffled | real vs shuffled |

- **Primary metric:** mean expectancy (R/trade). **Secondary:** PF, maxDD(R), pos-month share, top-1 share, OOS expectancy.
- **Matched-null:** reuse the VALIDATED engine `code/matched_null.py` (`matched_null_p`), unstratified ATR-scaled config.
- **Multiplicity plan:** ONE predeclared primary contrast per experiment; a SINGLE global family-wise correction
  across all 10 plan experiments (not per-experiment); no promotion on a secondary/exploratory result.
- **Minimum trades:** 30 per arm (UNRESOLVED if a matched-null p CI straddles the pre-set margin).
- **Stopping rule:** fixed Monte-Carlo B per the matched-null spec; report p + Wilson CI; never p=0.

## Files a Wave-1 implementation will need to CREATE (not yet created)
- `code/wave1_harness.py` — generic matched-null + beta/regime-matching + label-shuffle harness (built once, reused).
- `code/run_wave1.py` — driver executing EXP-01..06, writing `results/wave1/EXP-0X_result.parquet` + a summary.
- `knowledge/experiments/WAVE_1_RESULTS.md` — outcomes + which KG nodes/edges updated (written AFTER the run).
All reuse EXISTING S1/S2/S5/S21/S39 setups via `mstrat`/`mstrat_ext`; **no new primitive, no engine change.**

## Hard restrictions (unchanged)
Do NOT modify mstrat.py / s1.py / mtf.py / mstrat_ext.py / S1–S51 / the screen / stop-floor / matched-null.
Do NOT open the holdout. Do NOT run global-FDR. Do NOT generate new hypotheses. Do NOT reinterpret post-hoc —
all rules/metrics/margins are frozen in WAVE_1_SPEC.md before any result is read.

## Success criteria (Wave 1)
Each experiment returns an INTERPRETABLE result (positive OR negative) for its primary contrast, updates the named
Knowledge-Graph nodes/edges, and (for placebos/beta) validates or refutes the control. Success is information gain,
not profitability. Alpha (Wave 3) may only be considered after Wave-1 placebo/beta context is clean.

## Forbidden-before-run results
No expectancy, PF, p-value, or "edge confirmed/refuted" claim may be stated before the frozen run executes.

## Roles
- **Claude:** methodology guardian — build the harness/driver, prevent over-claiming, enforce the multiplicity plan.
- **Codex:** semantic-equivalence checks, feasibility, code review of the harness (inline if its filesystem is stale).

## Recommended first prompt for the new chat
> "Reconstruct the lab state from the official docs in this folder (PROJECT_STATE_v1.0.md, NEXT_SESSION.md,
>  knowledge/experiments/WAVE_1_SPEC.md). Confirm the official branch research-main and the close commit. Read
>  WAVE_1_SPEC.md and confirm EXP-01..EXP-06. Do NOT modify anything. Then STOP and ask me (CEO) to approve
>  implementing the Wave-1 harness and running EXP-01..EXP-06."

## Needs CEO approval before proceeding
Building `wave1_harness.py`/`run_wave1.py` and RUNNING any experiment. Nothing runs until the CEO says go.
