# ALPHA_BROAD_SCREEN_RESULTS — BATCH C (timeframe study, H1/H4)

Hypothesis: the near-breakeven M15 continuation cluster (Batch B) becomes net-positive at H1/H4 where the fixed 0.24 USD cost is negligible vs larger moves (§23). Engine `bscreen.py`, STRESS 0.24, eras b0/b1/DEV/CAL. Ledger (§36): 12 hyps (6 mechanisms × 2 TFs), all counted.

## First-pass screen
| hypothesis | TF | side | poolN | poolR | best1 | b0 | b1 | DEV | CAL | first-pass |
|---|---|---|---|---|---|---|---|---|---|---|
| TREND_break_S | H4 | S | 271 | +0.111 | +0.090 | +0.250 | +0.015 | +0.064 | −0.114 | SURVIVOR (flagged) |
| SB_break_L | H4 | L | 565 | +0.033 | +0.012 | −0.010 | +0.110 | −0.017 | +0.046 | ELIM INCONSISTENT |
| SB_break_S | H4 | S | 489 | +0.017 | −0.003 | +0.128 | −0.045 | −0.052 | +0.085 | ELIM SIGN_REVERSAL |
| TREND_break_L | H4 | L | 356 | +0.024 | +0.001 | −0.006 | +0.079 | −0.089 | +0.324 | ELIM SIGN_REVERSAL |
| VOLonset_L | H4 | L | 280 | +0.037 | +0.016 | −0.072 | +0.223 | −0.009 | −0.153 | ELIM SIGN_REVERSAL |
| VOLonset_S | H4 | S | 269 | −0.036 | — | +0.101 | +0.019 | −0.167 | −0.440 | ELIM NEG_STRESS |
| SB_break_L | H1 | L | 1702 | +0.021 | +0.000 | −0.009 | +0.015 | +0.028 | +0.156 | ELIM IMMATERIAL |
| SB_break_S | H1 | S | 1578 | −0.041 | — | +0.063 | −0.079 | −0.088 | −0.184 | ELIM NEG_STRESS |
| TREND_break_L | H1 | L | 1006 | +0.037 | +0.015 | −0.018 | +0.122 | −0.035 | +0.119 | ELIM SIGN_REVERSAL |
| TREND_break_S | H1 | S | 876 | −0.026 | — | +0.119 | −0.078 | −0.072 | −0.292 | ELIM NEG_STRESS |
| VOLonset_L | H1 | L | 724 | +0.051 | +0.029 | +0.066 | −0.010 | +0.076 | +0.204 | SURVIVOR-weak (72% NY flag) |
| VOLonset_S | H1 | S | 783 | −0.050 | — | +0.068 | −0.119 | −0.100 | −0.134 | ELIM NEG_STRESS |

## Deepening / adversarial (§15/§16) — all first-pass survivors KILLED (`deepen_c.py`)
- **TREND_break_S@H4 → ERA-TREND LEAKAGE.** Concentrated in the 2011-2013 gold BEAR (2011 +0.578, 2013 +0.294); CONF (recent 40%) = **+0.012 ≈ 0**; 2024 **−0.114**; pooled-without-b0 = +0.025. A short-continuation that "works" because gold fell in its best block — sign tracks era trend (§11/§15). NOT robust.
- **SB_break_L@H1 → BREAKEVEN / RECENT-ONLY.** best1 = **+0.000**; DISC = **−0.007** (negative); positive only via 2024 (+0.156); remove that block → +0.010. Auto-eliminated IMMATERIAL by the tightened screen.
- **VOLonset_L@H1 → NY-SESSION ARTIFACT.** **72% NY**-concentrated, b1 block **−0.010**, volatile years (2016 −0.11, 2018 −0.27); "vol-onset" = NY-session vol expansion (echoes R11/R12). NOT a clean directional edge.

## Verdict
**Batch C = 0 robust survivors.** The timeframe lever surfaced thin/era-concentrated/session-artifact positives, all killed by the skepticism gate (3rd/4th/5th false positives this campaign — after S10, S4). SIGN_REVERSAL is pervasive at H1/H4: continuation direction flips with the era's trend (era-trend leakage is the dominant failure mode for directional continuation). Screen tightened with two principled checks learned here: **best-1%-removed materiality (>0.02)** and **best-era-removal (era-concentration)**; S5 still survives, `SB_break_L@H1` now auto-eliminated.

## Screen-calibration note
SESSION_ARTIFACT and era-leakage remain flags, not auto-eliminators, because S5 itself is 100% NY-session — auto-killing session-concentrated cases would reject the one validated edge. The funnel (screen flags → deepening kills) is the correct division of labor (§14).
