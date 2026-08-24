# ALPHA_M15_TRANSITION_MAP

Mandate `ALPHA-XAUUSD-M15-CAUSAL-STATE-PATH-DISCOVERY-001`, §8. Causal M15 transitions A(t-8)->B(t) -> P(+70/-50) 8h lift, event-deduped, per-year + DISC/CONF + cross-era b0/b1 gate (`state_m15_transitions.py`). DEV base L 0.276 / S 0.265.

| transition | side | DEV lift | DISC/CONF | per-year | b0 / b1 | verdict |
|---|---|---|---|---|---|---|
| **highvol->stab** | L | -0.068 | -0.05/-0.09 | all neg | -0.025/-0.023 | **CROSS_STABLE (LONG-avoidance filter, not a trade)** |
| highvol->stab | S | -0.103 | -0.12/-0.07 | all neg | -0.107/-0.014 | dev-stable avoidance (b1 marginal) |
| extUp->pullback | S | +0.039 | +0.03/+0.06 | 2022 -0.03 | -0.014/-0.011 (invert) | not cross-stable |
| lowvol->exp | S | +0.031 | | 2021 -0.05 | +0.045/+0.012 | immaterial/inconsistent |
| ineff->dirDn | S | +0.025 | | | +0.030/-0.002 | immaterial, b1 inverts |
| ineff->dirUp / dirUp->collapse / dirDn->collapse / extDn->pullback | L/S | <0.02 | mixed | mixed | mixed | no info |
**Verdict:** NO material cross-era-stable POSITIVE tradeable M15 transition. The only cross-stable signal is highvol->stabilization -> LONG-avoidance (a filter). Every apparent positive transition fails the cross-era gate (b0/b1 invert) or is immaterial. Consistent with the M15 finding: the only cross-era-stable M15 information is volatility-based and non-tradeable.
