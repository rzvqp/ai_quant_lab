# TRADER-READ → MECHANICAL STRATEGY TRANSLATION V1

Five human-interpretable XAUUSD behaviors mechanized as frozen causal M15 rules, every qualifying occurrence traded, no context filtering, no
parameter mining. Specs frozen + hashed before scoring (`PROTOCOL_HASH = ae566fd9…`, `FAMILY_SPECS_HASH = 3c4a417e…`). Common payoff:
structural stop + 2R (primary) / 3R (diagnostic); entry = next-M15-open; BASE spread 0.05 / STRESS 0.08, net; one trade at a time per family.
INTERNAL_GENERALIZATION only (history materially exposed). Protections intact. Pre-flight PASS (355,696 M15 bars, 2011–2026).

## Result — no family passes the full candidate gate
`BASE_MECHANICAL_EDGE_FOUND = NO` · `FAMILIES_PASSING_PRIMARY_GATE = 0`.

| family | trader read | trades | /yr | WR | BASE 2R | STRESS 2R | PF | maxDD (R) | drop-best-5% | era | gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | sweep→reclaim→displacement→cont | 3,274 | 218 | 0.367 | +0.014 | +0.006 | 1.02 | 77.6 | −0.090 | ONE_ERA | FAIL |
| B | breakout→acceptance→shallow-pullback→cont | 220 | 14.8 | 0.386 | +0.063 | +0.054 | 1.10 | 14.2 | −0.039 | MIXED | FAIL |
| C | repeated-attack→defense-decay→breakout | 313 | 20.9 | 0.335 | **−0.018** | −0.034 | 0.97 | 50.9 | −0.119 | EARLY | FAIL |
| D | displacement→fail-to-accept→reversal | 5,855 | 390 | 0.364 | +0.041 | +0.028 | 1.06 | 102.4 | −0.062 | EARLY | FAIL |
| **E** | **compression→expansion→continuation** | 100 | 6.8 | 0.400 | **+0.108** | **+0.098** | **1.18** | **12.2** | **+0.009** | MIXED | FAIL (frequency only) |

**Family E is the one high-quality mechanism** — it passes every quality gate (expectancy ≥+0.10R, STRESS >0, PF ≥1.15, maxDD ≤15R, 2/3
chronological thirds positive, **drop-best-5% still positive**, top-1% only 18% of PnL — not tail-carried). It fails the gate **only** on
frequency: 100 trades / 6.8 per year, and its yearly record is **8 positive / 8 negative years (1–12 trades/yr)** — so the full-history edge is
driven by a few good years on tiny samples and cannot be distinguished from noise. The compression→expansion read is real but too rare to trust.
The frequent families (A 218/yr, D 390/yr) are the opposite: small positive means (+0.014 / +0.041R) that are tail-dependent (A's mean is more
than fully carried by its top 1%), one/early-era, and carry very large drawdowns (78R / 102R). C (defense-decay) is outright negative.

**3R diagnostic:** all five improve at 3R (positive skew) — B → +0.166R, C → +0.085R, E → +0.118R — but none of the frequent families reaches
the candidate gate, and 3R does not rescue frequency. §35: `3R_DIAGNOSTIC = positive-skew present`, not an auto-candidate.

## Cross-family overlap
A and D share ~78% of trading days (both frequent reaction-type mechanisms — not two independent strategies). B, C, E are more distinct but
sparse. E overlaps ~67–75% of its few days with A/D.

## §47 CEO answers
1. **Trades per family?** A 3,274 · B 220 · C 313 · D 5,855 · E 100. 2. **Most frequent?** D (390/yr). 3. **Best BASE expectancy?** E (+0.108R).
4. **Best STRESS?** E (+0.098R). 5. **Best PF?** E (1.18). 6. **Lowest maxDD?** E (12.2R). 7. **Sweep→reclaim→displacement (A)?** frequent but
thin, tail-dependent, one-era → no. 8. **Breakout→pullback (B)?** decent quality but too rare (14.8/yr), drop-5% negative → no. 9. **Repeated-
attack→decay→breakout (C)?** NEGATIVE → no. 10. **Failed-displacement→reversal (D)?** small positive but low PF, huge DD, early-era, tail →
no. 11. **Compression→expansion (E)?** best quality, but 6.8/yr and 8/8 pos/neg years → not trustworthy. 12. **Positive after drop-best-5%?**
only E (+0.009). 13. **Positive in ≥2/3 chronology?** B, C, D, E (2/3); A only 1/3. 14. **Cross-era stable?** none (0/5 are 3/3 thirds). 15.
**Materially one-sided?** E is long-driven (long +0.137 vs short −0.022); C short-only-positive; D short-stronger. 16. **3R vs 2R?** 3R better
for all (positive skew), materially for B. 17. **Most faithful mechanization?** A, D, E = HIGH fidelity; B = MEDIUM-HIGH; C = MEDIUM (defense-
decay is the hardest to mechanize and the mechanical version is negative). 18. **Most common winner-vs-loser difference?** diagnostic only
(HTF alignment and ATR-state show small differences) — `FOLLOW_UP_HYPOTHESIS_ONLY`, not used to repair. 19. **Any family passes the gate?** No.
20. **Which to falsify next?** none strictly qualifies; E is the closest on quality but fails frequency, so it is NOT ready.

## §48 FINAL OUTPUT
```
TRADER_READ_MECHANICAL_V1_COMPLETE = YES
PROTOCOL_HASH = ae566fd9d4bbda4d0813 · FAMILY_SPECS_HASH = 3c4a417ee17eef45ccce
FAMILIES_TESTED = 5

FAMILY_A_TRADES = 3274 · BASE_EXP_2R = +0.0140 · STRESS_EXP_2R = +0.0060 · PF_2R = 1.023 · MAXDD = 77.6R · STATUS = FAIL (thin/tail-dependent/one-era/high-DD)
FAMILY_B_TRADES = 220  · BASE_EXP_2R = +0.0628 · STRESS_EXP_2R = +0.0535 · PF_2R = 1.103 · MAXDD = 14.2R · STATUS = FAIL (low-frequency/N; drop5<0)
FAMILY_C_TRADES = 313  · BASE_EXP_2R = -0.0179 · STRESS_EXP_2R = -0.0340 · PF_2R = 0.974 · MAXDD = 50.9R · STATUS = FAIL (negative expectancy)
FAMILY_D_TRADES = 5855 · BASE_EXP_2R = +0.0406 · STRESS_EXP_2R = +0.0279 · PF_2R = 1.063 · MAXDD = 102.4R · STATUS = FAIL (below-threshold/high-DD/tail/early-era)
FAMILY_E_TRADES = 100  · BASE_EXP_2R = +0.1082 · STRESS_EXP_2R = +0.0977 · PF_2R = 1.180 · MAXDD = 12.2R · STATUS = FAIL (low-frequency/N only; all quality gates pass)

BEST_BASE_FAMILY = E_compress_expand · BEST_BASE_EXPECTANCY = +0.1082R · BEST_STRESS_EXPECTANCY = +0.0977R
BEST_TRADES_PER_YEAR = 390.3 (D) · BEST_MAX_DRAWDOWN = 12.2R (E)
FAMILIES_PASSING_PRIMARY_GATE = 0
BASE_MECHANICAL_EDGE_FOUND = NO
PRIMARY_FAILURE_MODES = LOW_FREQUENCY (E,B) · NEGATIVE/below-threshold EXPECTANCY (C,A,D) · TAIL_DEPENDENCE (A,D) · EXCESSIVE_DRAWDOWN (A,D) · ERA_INSTABILITY (A,C,D)
READY_FOR_INDEPENDENT_FALSIFICATION = NO
NEXT_FAMILY_FOR_FALSIFICATION = NONE (E is closest on quality but fails the frequency/N gate; not ready)
BROADER_PRICE_ACTION_FAILURE_CLAIM_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Authorized scope (§44)
The five specified trader-read mechanical families did NOT produce a robust base edge under the frozen implementation: the one high-quality
mechanism (compression→expansion) is too infrequent to trust, and the frequent mechanisms are thin, tail-dependent, and high-drawdown. No
broader claim — that price action has no edge, trader reasoning is useless, or XAU cannot be traded mechanically — is made or supported.
```
TRADER_READ_MECHANICAL_V1 = COMPLETE — 0/5 pass the candidate gate; compression→expansion has real per-trade quality but insufficient frequency
```
