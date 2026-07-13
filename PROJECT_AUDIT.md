# PROJECT_AUDIT — open defects, debts, method validity (2026-07-13)

## A. Confirmed defects
| id | severity | description | status |
|---|---|---|---|
| D1 | HIGH | Analytic normal-approx p-value invalid in extreme tail (heavy-tailed R) → spurious tiny p / false FDR passes. Proven: S6 analytic 2.14e-54 vs empirical bootstrap ~0.12. | retracted from verdict role; needs official empirical engine |
| D2 | HIGH | R-normalization / tiny-stop explosion: structure stops (prev_ext/beyond_sweep/structural) can be ~0 from entry → R=pnl/risk explodes (S6 R up to +166; top-5=71% profit; maxDD 89.8R v1 → 85R v2). | partially mitigated by v2 stop-floor; INVALID-EXECUTION not wired |
| D3 | HIGH | Matched-null (Test B, PRIMARY alpha test) miscalibrated: p≈0 on synthetic-null (construction/scale mismatch). | must fix + validate on synthetic PRICE series before official use |
| D4 | MED | Discovery Screen V1 thresholds calibrated on S1-S10 results = DEVELOPMENT-TUNED (selection-bias). | frozen; S11-S20 = prospective test |
| D5 | LOW | run_full_campaign.py %-profitable display bug (÷valid=0 → 400% for S19). Counts correct. | cosmetic |
| D6 | MED | Top-by-expectancy / top-by-profit-DD lists dominated by low-n flukes (S1 n=3-5, PF≈99). | use RESEARCH_WORTHY + monthly-stability lists |
| D7 | INFRA | Lab code+data were only in ephemeral Temp scratchpad. | fixed: copied to durable ai_quant_lab/; GC MBO raw (data2) still Temp-only (re-downloadable) |

## B. Method validity status (ALL under validation)
- Analytic p-value: INVALID for verdicts (diagnostic only).
- IID bootstrap (Test A robustness): H0-centering proven correct; METHOD UNDER VALIDATION.
- Block bootstrap (Test A robustness): well-calibrated on 2 synthetic controls; METHOD UNDER VALIDATION (needs full battery).
- Matched-null (Test B, primary): MISCALIBRATED; fix required.
- Global-FDR: NOT yet run with a valid p-value. Universe = full eligible valid (m=1552; 1704 conservative diagnostic).

## C. Retracted conclusions (audit trail)
1. "S1 = mostly long-bias/drift" — REFUTED (drift_core.py: random-long baseline −0.087R; S1 excess +0.31R).
2. "S1/S5/S9 decorrelated" — RETRACTED (single unstable monthly-R point estimate; no CI/stability/canonical representative).
3. "No Research Candidate significant" — RETRACTED (only S1-rep + S6 tested under pilot; reformulated to those two only).
4. S1-standalone "6 Discovery Candidates" (s1.py) — SUPERSEDED (family-favorable ATR-null + per-family FDR; not a candidate under mstrat.py unified engine + global FDR).

## D. Frozen decisions (do not change without CEO gate)
- Primary statistic = mean expectancy R/trade, one-sided (H0: mean≤0).
- Discovery Screen V1 = n≥25 & exp_research>0 & PF≥1.02 & maxDD≤25R & research-only (no OOS).
- Stop-floor formula = max(2×spread, 5×tick, 0.10×ATR) (pre-registered).
- Data splits research 60% / validation 20% / terminal holdout 20% SEALED (never opened).

## E. Governance
- Holdout terminal: SEALED, never opened this session. Opening = CEO gate only.
- No live trading. No candidate optimization. No REJECTED verdicts while p-engine invalidated.
