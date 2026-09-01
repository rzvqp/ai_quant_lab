# LONG_HORIZON_EVENT_REVEALED_DIRECTION_V1_REPORT — final

Discovery cycle: does a causal price EVENT reveal 24h direction AFTER the market begins moving (the paradigm the Statistician's long-horizon
scout recommended, since static advance direction is null)? Native M15 2011-2026 (355,696 bars, 14yr). Horizon 24h = 96 M15 bars. Direction
EVENT-REVEALED, never predicted. Independent-episode discipline (≥96-bar spacing). **SURVIVED = 0.** Code: `lh_scan.py`.

## §13 Positive control — PASS
```
(1) race-winner dir  P(continue)=1.000 (mechanical check ✓)   (2) net-return dir P(continue)=0.831 vs ~0.50 baseline (recovers a large effect)
POSITIVE_CONTROL = PASS — the engine detects directional information when it exists; the negatives below are real.
```

## §2/§14 Data
M15 355,696 bars, 2011-07-26→2026-07-27. Pre-2021 = 224,116 bars (63%), post-2021 = 131,580 (37%). UTC. 24h horizon walks bar index (96
bars). Every family reported PRE_2021 / POST_2021.

## Families & the decisive matched control (independent episodes, P(+100 in revealed dir before −100))
```
CONTROL displacement-alone (|net over 4h| >= 1 ATR, dir=sign)   cont=0.571   PRE 0.601 / POST 0.526   sret +1p   N=3667
A displacement -> acceptance -> continuation                    cont=0.579 (+0.008 vs ctrl)  DEV 0.625/OOS 0.529  PRE 0.608/POST 0.537  drop5%sret -31p
B displacement -> failure/reclaim -> reversal                   cont=0.576 (+0.006)          PRE 0.616/POST 0.511                        drop5%sret -26p
C displacement -> shallow retrace -> renewed expansion          cont=0.556 (-0.014)          PRE 0.584/POST 0.514
E range escape -> persistence outside -> continuation           cont=0.572 (+0.002)          PRE 0.609/POST 0.518  sret +14p            drop5%sret -23p
```
**Every event→response family is within ±0.01 of the displacement-ALONE control.** The acceptance / failure / retracement RESPONSE adds
essentially nothing to what the initial move already contains. `SEQUENTIAL_STATE_INCREMENTAL_INFORMATION_FOUND = NO.`

## §21 Top-5 phenomena (all NOISE or INFORMATION_ONLY)
| # | phenomenon | cont | vs control | pre/post | outlier | class |
|---|---|---|---|---|---|---|
| 1 | displacement-alone → continuation | 0.571 | (baseline) | 0.601/0.526 | drop5% neg | INFORMATION_ONLY (momentum, decaying) |
| 2 | A disp→accept→cont | 0.579 | +0.008 | 0.608/0.537 | top1%=3.7 | INFORMATION_ONLY (≈control) |
| 3 | B disp→fail→reversal | 0.576 | +0.006 | 0.616/0.511 | — | INFORMATION_ONLY (≈control) |
| 4 | E range-escape→persist | 0.572 | +0.002 | 0.609/0.518 | drop5% neg | INFORMATION_ONLY (≈control) |
| 5 | C disp→shallow→renew | 0.556 | −0.014 | 0.584/0.514 | top1%=5.5 | NOISE (worse than control) |
`STRATEGY_HYPOTHESIS_WORTH_TESTING = 0.` No family passes the §15 information gate (matched-control superiority fails; effect era-decaying;
signed returns outlier-carried). No strategy interpretation constructed.

## §23 CEO questions — answered
1. **Does direction become predictable after the market reveals part of the move?** **Only weakly, via the initial move itself** (P(continue@100)=0.571, i.e. simple momentum) — and that is **pre-2021-concentrated and decaying** (0.60→0.53). The subsequent event-RESPONSE reveals **no additional** direction.
2. **Is the remaining 24h move large enough to monetize after waiting for confirmation?** The moves exist (P200 ~0.21, P300 ~0.11 in the revealed dir), but the directional edge is too weak (0.571, ~0.53 recently) and signed returns are tiny (+1..+14p) and **outlier-carried** (drop-best-5% negative). **No — not monetizable.**
3. **Does the sequential event add information beyond the initial move?** **NO** — decisively (families ≈ control, ±0.01).
4. **Does it work pre-2021 as well as post-2021?** It works **better pre-2021** (0.60-0.62) than post (0.51-0.54); the continuation edge **decayed**, it is near-coinflip recently. Not a recent-bull artifact, but not stable.
5. **Is the main barrier still direction, or execution/payoff?** **DIRECTION remains the barrier.** The payoff (large moves) is available; direction after the event is only ~0.571 (decaying to ~0.52). The sequential-response paradigm does **not** solve direction at 24h on M15.

## §22 VERDICT
```
LONG_HORIZON_EVENT_REVEALED_DIRECTION_V1_COMPLETE = YES
POSITIVE_CONTROL = PASS
SEQUENCE_FAMILIES_TESTED = 5 (4 event→response + displacement-alone control) · EFFECTIVE_HYPOTHESES ≈ 5
EVENT_REVEALED_DIRECTION_INFORMATION_FOUND = NO (beyond the trivial, decaying initial-move momentum)
SEQUENTIAL_STATE_INCREMENTAL_INFORMATION_FOUND = NO
STATISTICALLY_MEANINGFUL_PHENOMENA = 1 (displacement→continuation, INFORMATION_ONLY, era-decaying)
STRATEGY_INTERPRETATIONS_TESTED = 0 · STRATEGY_INTERPRETATIONS_SURVIVED = 0
NEW_STRATEGY_CANDIDATE = none
PRE_2021_SUPPORT = YES but INVERSE (stronger pre-2021, decaying post) — not monetizable in either era
READY_FOR_INDEPENDENT_VALIDATION = NO
S5_MECHANISM_CLONED = NO · FAMILY_E_NOT_CLONED = YES (native long-horizon families, different thresholds/horizon)
```

## §24 PROTECTION
S5·Q4·AI_Trader·P007·MGMT004·MT5·StrategyCatalog untouched; L1·P2·V2-4·Scheduled-Events·M5-Family-E NOT reopened; no promotion.

## Honest summary
Tested rigorously — 14 years, independent episodes, a passing positive control, pre/post-2021, matched controls — the event-revealed-
direction paradigm at 24h on M15 does **not** reveal direction beyond the trivial initial-move momentum, and even that momentum is decaying
(0.60 pre-2021 → 0.53 post) and outlier-carried. The sequential response (acceptance/failure/retrace) adds nothing (±0.01 vs the displacement
alone). **Direction remains the barrier**: the market reveals *that* it will move (large 24h excursions are common) but not *which way*, even
after it has already started. This closes the long-horizon event-revealed-direction avenue on price-only M15. S5 remains the sole tradeable
edge; the campaign's consistent finding holds — XAU magnitude/timing is predictable, direction is not.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_INDEPENDENT_VALIDATION = NO
```
