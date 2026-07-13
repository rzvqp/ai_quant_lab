# VALIDATION_STATUS — what has and has NOT been validated (S1–S51)

Everything in this knowledge base is **EXPLORATORY**. No primitive is validated alpha.

## Pipeline stage status
| stage | status |
|---|---|
| Historical profitability (research segment) | COMPUTED — 375 profitable hypotheses (S1-S40) + S41-S51 additions |
| Discovery Screen V1 (Research-Worthy) | COMPUTED — 143 RW total (130 S1-S20 + 13 S21-S51); FROZEN, development-tuned |
| Out-of-sample (validation 20%) | COMPUTED per hypothesis — separates ~genuine (S5, S2, S1-short, S22, S42) from overfit (calendar) |
| **Matched-null (Test B)** | **ENGINE VALIDATED** (branch matched-null-validation) but **applied to only 10 pre-registered pilots**, NOT the full candidate universe |
| Global-FDR | **NOT RUN** on the full eligible universe |
| Walk-forward | NOT RUN |
| Red Team | NOT RUN |
| Terminal holdout (last 20% M15) | **SEALED — never opened** |

## Explicit statements (per CEO)
- Results in this knowledge base are **EXPLORATORY** — historical and/or OOS-positive, not validated.
- The **matched-null is a VALIDATED ENGINE** (calibration + power + adversarial + parity pass), **but not all
  strategies have been run through it** — only a 10-hypothesis pilot.
- **Global-FDR has NOT been run** over the complete universe; per-hypothesis OOS p's are pre-FDR.
- The **holdout is SEALED**; opening it is a CEO gate.
- **No primitive is validated alpha.** Most positive primitives are long in a 2023-25 gold bull, so timing-alpha
  vs gold-beta is unresolved until a beta/regime-matched null runs over the full set.

## What remains for validation (when the CEO resumes it)
1. Run the validated matched-null over the FULL deduped candidate set (not just the pilot), beta/regime/direction-matched.
2. One dependence-aware GLOBAL-FDR (multiplicity) procedure over the frozen eligible universe.
3. Walk-forward + Red Team on survivors.
4. Only then, a single CEO-gated evaluation on the sealed terminal holdout.
5. Portfolio construction (correlations currently too uncertain — ~26 months — and long-beta-dominated).

## Primitive readiness (exploratory ranking, NOT validation)
- Closest to validation-ready: P003 (opening-range), P002 (failed-breakout fade), P001 (confirmed sweep, short leg),
  P004 (round-number), P006 (short-term overreaction, small-n). All VALIDATION PENDING.
- Mixed / needs work: P005, P007 (redundant/beta), P008, P010.
- Do NOT advance: P011-P019 (repeatedly negative / overfit), the calendar and chasing primitives.
