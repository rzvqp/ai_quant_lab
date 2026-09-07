# TRADER-READ EXECUTION GEOMETRY FORENSIC AUDIT V1

Diagnoses WHY the five frozen Trader-Read strategies lose — directional idea vs execution geometry (stop / entry / target / intrabar accounting).
Every original trade stays frozen (`PROTOCOL_HASH ae566fd9`, `FAMILY_SPECS_HASH 3c4a417e`); all alternatives are `COUNTERFACTUAL_DIAGNOSTIC_ONLY`.
No optimization, no new strategy, no parameter search. `ORIGINAL_TRADE_IDENTITY_GATE = PASS` (A=3,274 · B=220 · C=313 · D=5,855 · E=100 = 9,762).

## The answer: losses are substantially EXECUTION GEOMETRY, not (only) wrong direction
`EXECUTION_GEOMETRY_PROBLEM_FOUND = YES`. Two geometry defects dominate, entry and intrabar accounting are clean.

### Stop geometry is too tight (wick-outs + post-stop recovery)
| family | losers | stop-then-2R% | stop-then-1.5R% | stop hit but structure STILL VALID % | post-stop MFE median | reach 2R after stop % |
|---|---|---|---|---|---|---|
| A sweep | 2,079 | 10.6 | 14.0 | 49.3 | 0.02R | 14.5 |
| B breakout | 135 | 16.3 | 19.3 | 51.1 | 0.29R | 21.2 |
| **C attack-decay** | 208 | **32.2** | **39.9** | 34.6 | **0.91R** | **34.5** |
| D disp-fail-rev | 3,730 | 23.3 | 29.4 | 39.9 | 0.56R | 27.2 |
| E compression | 60 | 20.0 | 25.0 | 46.7 | 0.07R | 24.0 |

**35–51% of losing stops are wick-outs** — price hit the stop intrabar but closed back on the correct side (structure still valid). And **10–32% of
losers later reach the original 2R target after being stopped** (C 32%, D 23%, E 20%). Median stop overshoot is only **0.29–0.67 ATR** — the stop is
typically exceeded by less than an ATR before recovery. Winner MAE confirms it: winners retrace a **median 30–44% of the stop distance** and reach
within 20% of the stop in 9–21% of cases — winners need breathing room the current stop barely provides.

### Target geometry is disconnected from structure (2R sits beyond the next level)
| family | % with causal next level | reaches next level % | median level dist (R) | **2R target BEYOND next level %** |
|---|---|---|---|---|
| A | 94.8 | 51.8 | 0.82 | 79.7 |
| **B** | 76.8 | **79.9** | **0.18** | **98.2** |
| C | 83.7 | 68.7 | 0.49 | 80.2 |
| **D** | 99.9 | **78.2** | 0.27 | **94.9** |
| E | 55.0 | 65.5 | 0.89 | 70.9 |

The market reaches the next causally-known structural level **52–80%** of the time, but the fixed 2R target is set **beyond** that level in **71–98%**
of trades. So price often travels to its natural structural destination (the next level) and then the fixed 2R — placed past it — is never reached and
the trade reverses. This is a **target–structure mismatch**, strongest in B (reaches level 80%, target beyond 98%, level only 0.18R away).

### Entry and intrabar accounting are NOT the problem
Next-M15-open entry worsens location by >0.25 ATR in only 0–1% of trades (`ENTRY_GEOMETRY_PROBLEM_FOUND = NO`). M15 same-bar SL/TP ambiguity totals
**29 trades (<0.5%)**; M5 (2021+ coverage) resolves them TP-first 2 / SL-first 5 / still-ambiguous 9 — immaterial (`INTRABAR_ACCOUNTING_PROBLEM_FOUND = NO`).

### Directional quality (independent of stop/target)
MFE/MAE ratio over 32 bars: A 0.98 · B 0.98 · **C 1.21** · D 1.05 · E 1.02 — **C has the strongest standalone directional edge**; A/B/E are near-symmetric
(weak raw direction). Favorable 100-pip ($10) moves occur in 14–25% of trades, 200-pip in 3–10%. Family-E rarity is from the **expansion + structural-break
gates**, not compression (8,406 compression states → ~101 triggers → 100 independent trades).

## §29 CEO answers
1–5. **% losers reaching 2R after stop:** A 10.6 · B 16.3 · **C 32.2** · D 23.3 · E 20.0. 6. **≥+1.5R after stop:** A 14 · B 19 · C 40 · D 29 · E 25.
7. **Winner MAE (median, frac of stop):** A 0.36 · B 0.40 · C 0.44 · D 0.37 · E 0.30 (P90 0.77–0.88). 8. **Winners near the stop?** YES — 9–21% come
within 20% of the stop. 9. **How far beyond stop do stop-then-winner trades travel?** median overshoot 0.29–0.67 ATR (small). 10. **M15 same-bar
ambiguous:** 29 (<0.5%). 11. **M5 resolution:** TP-first 2, SL-first 5 (immaterial). 12. **Next-open degrading entry?** NO (0–1% > 0.25 ATR). 13.
**Favorable 100-pip moves?** 14–25% of trades. 14. **Reach next causal level?** 52–80%. 15. **Breakout+acceptance improve next-level reach?** YES —
B reaches the next level 80% with the level only 0.18R away. 16. **Fixed 2R disconnected from next level?** YES — beyond the level in 71–98%. 17.
**Family-E rarity:** the expansion/structural-break gates (compression itself is common). 18. **Strongest directional idea:** C (MFE/MAE 1.21,
34.5% reach 2R after stop). 19. **Most execution-not-alpha:** C (32% stop-then-2R) for stops; B (98% target-beyond-level) for targets. 20. **Level-to-level justified?** YES.

## §30 FINAL OUTPUT
```
TRADER_READ_EXECUTION_FORENSICS_V1_COMPLETE = YES
ORIGINAL_TRADE_IDENTITY_GATE = PASS
FAMILIES_AUDITED = 5 · TOTAL_TRADES_AUDITED = 9762
FAMILY_A_STOP_THEN_2R_PERCENT = 10.6 · FAMILY_B = 16.3 · FAMILY_C = 32.2 · FAMILY_D = 23.3 · FAMILY_E = 20.0
FAMILY_A_STOP_THEN_1_5R_PERCENT = 14.0 · FAMILY_B = 19.3 · FAMILY_C = 39.9 · FAMILY_D = 29.4 · FAMILY_E = 25.0
M15_SAME_BAR_AMBIGUOUS_TOTAL = 29 · M5_RESOLVED_TP_FIRST = 2 · M5_RESOLVED_SL_FIRST = 5
ENTRY_GEOMETRY_PROBLEM_FOUND = NO
STOP_GEOMETRY_PROBLEM_FOUND = YES (35-51% wick-out stops; 10-32% reach 2R after stop; overshoot 0.3-0.7 ATR)
TARGET_GEOMETRY_PROBLEM_FOUND = YES (2R beyond next causal level in 71-98%; market reaches level 52-80%)
INTRABAR_ACCOUNTING_PROBLEM_FOUND = NO (<0.5% ambiguous)
LEVEL_TO_LEVEL_BEHAVIOR_PRESENT = YES
BREAKOUT_ACCEPTANCE_NEXT_LEVEL_VALUE = YES
FAMILY_A_CLASSIFICATION = STOP_GEOMETRY_SUSPECT (wick-outs high; raw direction also weak)
FAMILY_B_CLASSIFICATION = TARGET_GEOMETRY_SUSPECT (2R beyond a near next-level; reaches level 80%)
FAMILY_C_CLASSIFICATION = STOP_GEOMETRY_SUSPECT (idea strongest, 32% reach 2R after stop)
FAMILY_D_CLASSIFICATION = MULTIPLE_EXECUTION_GEOMETRY_ISSUES (stop wick-outs + target beyond level)
FAMILY_E_CLASSIFICATION = MECHANISM_QUALITY_HIGH_BUT_RARE (plus stop-geometry; rarity from expansion/structural-break gates)
STRONGEST_DIRECTIONAL_FAMILY = C_attack_decay_break
STRONGEST_EXECUTION_PROBLEM_FAMILY = C (stops) / B (targets)
EXECUTION_GEOMETRY_PROBLEM_FOUND = YES
LEVEL_TO_LEVEL_RESEARCH_JUSTIFIED = YES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Counterfactual note (diagnostic only, §18/§19)
Because median stop overshoot is 0.3–0.7 ATR and 10–32% of losers reach 2R after the stop, a structural stop with a small buffer (S1/S2) would
retain a material fraction of the stop-then-2R losers — but at larger initial *price* risk, which for constant *account* R means smaller size, not
more risk. This is `COUNTERFACTUAL_DIAGNOSTIC_ONLY`; no expectancy was scored and no stop was changed. The evidence points to two testable,
structurally-motivated directions (structural stop; level-to-level target) — decisions reserved for the CEO.
```
TRADER_READ_EXECUTION_FORENSICS_V1 = COMPLETE — losses are substantially STOP + TARGET geometry (not entry/intrabar); C's idea strongest; level-to-level justified
```
