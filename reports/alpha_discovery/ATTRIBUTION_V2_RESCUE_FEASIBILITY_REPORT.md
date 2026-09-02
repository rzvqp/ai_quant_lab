# V2 RESCUE PROSPECTIVE-VALIDATION FEASIBILITY AUDIT — 22 frozen rescues

Prioritization / arithmetic / provenance audit ONLY. No new search, no new bins, no combined conditions, no retuning, no future-outcome
inspection, no strategy modification. The 22 credible rescues are bound verbatim from the FINAL_83 frozen result; every condition, N,
expectancy and gate status is carried as-frozen. Protections intact (S5 / AI-Trader / P007 / MGMT-004 / MT5 / StrategyCatalog untouched).

## The structural finding — rescue STRENGTH and FIRING RATE are inversely related
The audit's central result is not a single winner but a wall: **the scientifically strong rescues fire rarely, and the rescues that fire
often are weak.** There is no credible rescue in the fast-firing corner.

| tier | examples | discovery strength | independent firing rate | time to 100 indep |
|---|---|---|---|---|
| **strong & rare** | S6, S31, S23, S46, CAND0004, CAND0006, S14 | HIGH / MEDIUM (lift +0.48 … +0.93R) | **3–6 / yr** | **100 – 320 months** |
| **frequent & weak** | DIRECTION_AGNOSTIC, SESS_D, S17, S39, S9 | LOW / MEDIUM (exp +0.055 … +0.34R) | 23 – 51 / yr | 24 – 52 months |

## Feasibility gate — NONE powered within 24 months (full OR shrunk effect)
For every rescue, the future sample for a properly-powered test (80% power, two-sided α=0.05, positive-expectancy) was computed on the
**independent-day** mean/variance, at full discovery effect and at the mandated **50% shrinkage**:

- `powered @ full-effect ≤ 24 months`: **0 / 22**
- `powered @ 50%-shrunk effect ≤ 24 months`: **0 / 22**

The fastest-firing credible, S5-independent rescue (**S17**, +0.339R, 27 indep/yr) needs **≈38 months at full effect** and **≈152 months at 50%
shrinkage** for 80% power — the *shortest powered horizon of any credible rescue*, and still well beyond 24 months. The absolutely fastest
firer (DIRECTION_AGNOSTIC, 51/yr) reaches 100 independent trades in ~24 months but is LOW strength (+0.055R) and would itself need >200 months
to power. So no candidate is simultaneously strong enough and frequent enough.

## Two rankings (kept separate per §10)
**RANKING A — scientific strength** (frozen evidence only): S6 (HIGH, lift +0.808) · S31 (HIGH, +0.416R, lift +0.766) · S23 (HIGH, +0.359R) ·
S46 (HIGH, +0.434R) · CAND0004 (MEDIUM, highest raw exp +0.682R, lift +0.927) · CAND0006 (MEDIUM, +0.663R).
**RANKING B — validation feasibility** (time to 100 independent trades): DIRECTION_AGNOSTIC 23.5mo (LOW) · SESS_D 40mo (MEDIUM, PARTIAL) ·
S17 44mo (MEDIUM, YES) · S39 47mo (MEDIUM, YES) · S9 52mo (MEDIUM, YES) · S5 80mo (NO — S5 itself).

**CEO_STRATEGY2_PRIORITY (balanced: causal + S5-independent + strength + speed):** the single best-balanced candidate is **S17::3cf289079abb —
`vol_rel_20 = 4` (M14_REFERENCE_LEVEL, BOTH)**: MEDIUM strength (+0.339R, lift +0.56, N=113, chrono all-thirds positive, S5-independent), and
the fastest-to-power of any credible independent rescue. It is the least-blocked path — but it is *still not near-term validatable* (a powered
test remains 38+ months out even at full effect). SESS_D fires marginally faster but is only PARTIAL-independent and much weaker-to-power.

## S14 benchmark (§11) — confirmed from the frozen ledger
S14::25e44853ad0f `dist_prev_sess_high_atr=0`: N=65, subset +0.4926R, remainder −0.1881R, **≈3.7 independent trades/yr** → ~50 in **~13 years**,
~100 in **~27 years** (consistent with the CEO's 4.3/yr → 12/23-year framing). STRONG discovery, IMPRACTICAL validation. Its scientific rank
stays high; its practical-validation rank is at the bottom.

## Post-2026-07-27 expected qualifying events (rate only — no outcomes inspected)
Fastest credible: S17 ≈ 2.3 / month (27/yr); SESS_D ≈ 2.5 / month; the strong-but-rare cohort (S14, CAND0004/6, S46, S23) ≈ 0.3 / month each
(~3–4 / year). Over 24 months: S17 ~55, SESS_D ~60, S14 ~7.

## §16 REQUIRED FINAL OUTPUT
```
V2_RESCUE_VALIDATION_FEASIBILITY_AUDIT_COMPLETE = YES
FROZEN_RESCUES_TOTAL = 22
CAUSAL_RESCUES = 22 (all conditions available AT/BEFORE the original decision; f029 excluded upstream)
S5_INDEPENDENT_RESCUES = 17 YES + 4 PARTIAL (M06 session-time) + 1 NO (S5 itself)
FAST_VALIDATION_RESCUES = 0            (horizon = months to a reasonable ~100 independent-trade sample)
MEDIUM_VALIDATION_RESCUES = 1 (DIRECTION_AGNOSTIC, but LOW discovery strength)
SLOW_VALIDATION_RESCUES = 4 (SESS_D, S17, S39, S9 — all MEDIUM strength)
IMPRACTICAL_VALIDATION_RESCUES = 17 (incl. every HIGH-strength rescue: S6, S31, S23, S46, and S14, CAND0004/6)
TOP_SCIENTIFIC_RESCUE = S6::7199b701458a (dist_or_low_atr=4, HIGH, lift +0.808R)  [highest raw expectancy: CAND0004 +0.682R]
TOP_VALIDATION_FEASIBILITY_RESCUE = DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1 (compress_flag=0, 51 indep/yr) [LOW strength]
                                    fastest CREDIBLE = S17::3cf289079abb (vol_rel_20=4)
TOP_PRIORITY_RESCUE = S17::3cf289079abb  (vol_rel_20=4, M14_REFERENCE_LEVEL, BOTH)
TOP_PRIORITY_DISCOVERY_N = 113
TOP_PRIORITY_EXPECTANCY = +0.3385R (remainder -0.2238R, lift +0.5623R)
TOP_PRIORITY_EXPECTED_TRADES_PER_YEAR = ~27 (raw)  ·  TOP_PRIORITY_EFFECTIVE_TRADES_PER_YEAR = 27.4 (independent-day)
TOP_PRIORITY_TIME_TO_30 = ~13 months  ·  TIME_TO_50 = ~22 months  ·  TIME_TO_100 = ~44 months
   (powered@80%: ~38 months full-effect / ~152 months at 50% shrinkage)
PRACTICALLY_VALIDATABLE_RESCUE_EXISTS = NO
   (no rescue meets causal + S5-independent + HIGH/MEDIUM strength + powered prospective horizon <= 24 months, at full OR shrunk effect)
V2_RESCUE_ROUTE_NEAR_TERM_BLOCKED = YES
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Recommendation for the CEO decision
The V2 rescue route is **structurally blocked as a near-term Strategy #2 path**: the effect-rich rescues are rare events (multi-decade sample
accrual, like S14) and the frequent rescues are too weak to power in a near-term window. This is not a fixable engineering gap — it is the
shape of the frozen evidence. Two options: (a) **redirect discovery to genuinely new information sources** (the mandate's own contingency), or
(b) if a *first-look, explicitly underpowered* prospective read is acceptable, **S17 (`vol_rel_20=4`)** is the fastest credible, S5-independent
candidate (~30 independent trades in ~13 months) — with the standing caveat that 30–50 trades cannot confirm a +0.34R edge, only fail to
falsify it. No validation was performed and no rescue was modified.
```
V2_RESCUE_ROUTE = NEAR_TERM_BLOCKED (structural strength-vs-frequency wall); least-blocked credible candidate = S17 vol_rel_20=4
```
