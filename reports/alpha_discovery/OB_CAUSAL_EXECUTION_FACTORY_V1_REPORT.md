# OB_CAUSAL_EXECUTION_FACTORY_V1_REPORT — final

Narrow follow-up cycle: can a pre-specified, fully causal EXECUTION monetize the (Statistician-confirmed) order-block level information,
after OBR-BULL-1's fill artifact was falsified? Structure frozen; only execution varied; 4 families; conservative same-bar ordering;
matched timing-controls; **no M5** (§15). **SURVIVED = 0.** Code: `ob_exec.py`, `ob_exec_compare.py`, `test_ob_exec_fill.py`.
Docs: comparison, hypothesis register, this report.

## The artifact (§3) — reproduced and frozen as a regression test
The falsified execution treated a resting BUY limit at `block_high` as *not filled* when the same bar closed below `block_low` — dropping
same-bar filled-then-invalidated LOSSES. Corrected: a touched limit is filled; a same-bar close cannot cancel it; conservative same-bar
ordering thereafter.
```
OLD_BUGGY_FILL net = +0.1536 (N 2122)   CORRECTED EXEC-A net = -0.0673 (N 2486, +364 recovered same-bar losers)
OLD_FILL_ARTIFACT_REPRODUCED = YES   OLD_OBR_BULL_1_REMAINS_FALSIFIED = YES   (matches Statistician -0.067 exactly)
```
Permanent regression test `test_ob_exec_fill.py` asserts: buggy − corrected > 0.15, corrected ≤ 0, corrected keeps more trades,
corrected ≈ −0.067. PASS.

## §23 SCOREBOARD
```
OB_CAUSAL_EXECUTION_FACTORY_V1_COMPLETE = YES
STRUCTURAL_OB_DEFINITION_FROZEN = YES
OLD_FILL_ARTIFACT_REPRODUCED = YES
OLD_OBR_BULL_1_REMAINS_FALSIFIED = YES

EXECUTION_HYPOTHESES_RAW = 4
EXECUTION_HYPOTHESES_TESTED = 4
EXECUTION_HYPOTHESES_FALSIFIED = 4
EXECUTION_HYPOTHESES_SURVIVED = 0

EXEC_A_NET_R = -0.067   (true resting limit, corrected; = Statistician)
EXEC_B_NET_R = -0.266   (retest close → next open)
EXEC_C_NET_R = -0.206   (rejection close → next open)
EXEC_D_NET_R = -0.185   (penetration + reclaim → next open)

OB_EXECUTION_INCREMENTAL_INFORMATION_FOUND = NO   (OB−control +0.055 at best, still net-negative; not monetized)
CROSS_ERA_STABLE_SURVIVOR = NO
M5_REFINEMENT_RUN = NO   (§15 — not authorized; no M15 survivor)
NEW_STRATEGY_CANDIDATES = 0
READY_FOR_STATISTICIAN_REVIEW = NO
```

## §22 interpretation — the correct conclusion
EXEC-A negative, EXEC-B/C/D negative, yet the OB level still (marginally) beats matched controls and was independently confirmed
informative by the Statistician. Therefore:
> **ORDER_BLOCK_LEVEL_INFORMATION_CONFIRMED_BUT_NOT_CURRENTLY_MONETIZABLE.**

The information exists in the *level*; the four natural causal executions (resting limit / next-open on validity / next-open on rejection
/ next-open on reclaim) each pay away more than the level is worth — via same-bar loss realization (limit) or giving up the entry price
(next-open). We do **not** keep inventing executions until one turns positive (§22). No M5 was run (§15).

## §25 PROTECTION
```
S5_UNTOUCHED=YES · Q4_UNTOUCHED=YES · AI_TRADER_UNTOUCHED=YES · P007_UNTOUCHED=YES · MGMT004_UNTOUCHED=YES · MT5_UNTOUCHED=YES
EXECUTION_UNTOUCHED=YES · STRATEGY_CATALOG_UNTOUCHED=YES · NO_M5_SYNTHESIS=YES · NO_LIVE_PROMOTION=YES
```

## §26 close + next-space ranking (NOT started)
SURVIVED = 0 → cycle closed; OBR-BULL-1 remains FALSIFIED as a tradeable strategy (NKB updated). The OB-level information finding is
preserved as knowledge, not a strategy. Remaining genuinely-distinct spaces, ranked:
1. **SESSION_SPECIALIST_FACTORY** — S5 is the only validated edge and is a session+structure specialist; the most plausible price-only
   avenue. (The OB work suggests level-identity matters even if this exact monetization failed — a session-anchored level specialist may
   combine both.)
2. **EXOGENOUS real yields** — the only plausible stable *directional* signal; CEO-scoped-out to date.
3. CROSS_MARKET_RELATIVE_RESPONSE · 4. GC_FUTURES_WITH_PROPER_DATA (blocked on data).

## Honest note
This cycle did its job: it confirmed the Statistician's falsification mechanically (to the digit), froze the artifact as a permanent
regression test, and tested four disciplined causal executions — none monetize. The right lesson is not "OB is worthless" (its level
information is real and independently confirmed) but "this level information is too small to survive realistic execution frictions in
these four natural forms." That is a legitimate, honest negative.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_STATISTICIAN_REVIEW = NO
```
