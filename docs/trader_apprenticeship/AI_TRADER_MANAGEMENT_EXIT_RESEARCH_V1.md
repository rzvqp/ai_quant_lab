# AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1

**Mandate:** `AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1`, §5-20. Built entirely from
`AI_TRADER_TRADE_PATH_DATASET_V1.md`. Q4 sealed throughout. Entries, directions, initial stops, and
structural targets are unchanged from the original record — only the post-entry management layer is
studied. No policy threshold below was chosen after seeing which one performed best.

---

## 1. Describe the problem without a strategy (§5)

**Primary population (n=12), MFE/MAE/giveback distributions:**

```
MFE_R:       min=0.138  median=1.377  mean=1.492  max=3.743
MAE_R:       min=0.109  median=1.103  mean=0.955  max=1.586
Giveback (MFE_R − RESULT_R):  min=0.857  median=1.701  mean=1.779  max=3.024
```

**Every one of the 12 primary trades gave back at least 0.857R from its own peak** — including all
3 winners. This is the rawest, strategy-agnostic statement of the pathology: under the current
no-trailing / no-genuine-target-reached methodology, giveback is universal in this sample, not a
property of the losing trades alone.

**Conditional-loss probabilities:**

```
P(final loss | MFE >= 0.5R) = 0.70  (n=10)
P(final loss | MFE >= 1.0R) = 0.571 (n=7)
P(final loss | MFE >= 1.5R) = 0.50  (n=6)
P(final loss | MFE >= 2.0R) = 0.00  (n=3)
```

**A genuinely important, non-obvious finding:** the probability of an eventual loss drops to
**exactly zero** once a trade has reached 2.0R favorable — all 3 trades that ever reached 2.0R (#58,
#63, #64) were winners. **The giveback problem, in this sample, is concentrated entirely in the
0.5R-1.5R band** — trades that get some way toward favorable but not decisively far never round-trip
back to a loss once they clear 2.0R. This directly shapes which policy threshold is defensible to
pre-register (§2 below).

**`P(return to entry | MFE >= X)`** — using the derived proxy (`RESULT_R <= 0`, since a net
non-positive close after positive MFE requires price to have retraced through entry): identical to
the loss probabilities above, since every loss in this sample closed at a genuine negative R (no
trade closed at exactly breakeven from a stop-triggered exit) — `P(return-to-entry-or-worse |
MFE>=1.0R) = 0.571`, `P(...>=1.5R) = 0.50`, `P(...>=2.0R) = 0.00`.

**Q2 vs Q3 split:** Q2 (n=10) carries essentially the entire giveback total (17.703R of the
population's cumulative 21.345R giveback); Q3's 2 primary trades (Q3-001, Q3-002) contribute 3.642R
of giveback but **both have MFE below 1.0R**, meaning Q3 offers no trade in this primary sample that
ever reached the range where the loss probability is most differentiated (0.5-1.5R). **This
concentration is disclosed explicitly and carried through the rest of this report — the strongest
policy evidence below is Q2-only.**

**`MFE_GIVEBACK_PROBLEM_CONFIRMED = YES`** — genuinely large, not a marginal effect: 10 of 12 trades
reached at least 0.5R favorable, and 70% of those eventually closed at a loss anyway.

---

## 2. Pre-registered policy set (§6, frozen before any P&L evaluation)

```
POLICY-0 — ORIGINAL STATIC BASELINE. No management change. RESULT_R as recorded.

POLICY-1 — TP1 BANK (40%) + BREAKEVEN. Bank 40% at a genuine, already-frozen TP1; move remaining
           stop to BE only after TP1 is actually reached; preserve remaining structural targets.

POLICY-2 — TP1 BANK (40%) + STRUCTURAL TRAIL. Same TP1 trigger as POLICY-1; remaining 60% uses a
           causal structural trail, no arbitrary fixed-pip trailing.

POLICY-3 — TP1 (40%) + TP2 (30%) + FINAL STRUCTURAL (30%). The full 40/30/30 framework, where
           genuine TP1/TP2 levels existed.

POLICY-4 — MFE-GIVEBACK PROTECTION: move the stop to breakeven (entry price) the first time price
           reaches +1.0R favorable excursion; if price subsequently retraces to breakeven, exit
           there instead of riding to the original stop. 1.0R is used because it is the single most
           standard, textbook breakeven-trigger convention in discretionary risk management — chosen
           for that reason, before this dataset's P&L was computed, not because it was tested against
           several candidate thresholds and 1.0R happened to look best. No fifth structurally
           distinct policy concept was identified beyond this — none manufactured to reach 5.
```

**Immediate, mechanical finding that determines the rest of this section:** per
`AI_TRADER_TRADE_PATH_DATASET_V1.md` §2, **8 of the 12 primary trades had no fixed target of any
kind**, and **zero of the 12 primary trades — including the 3 that did have a genuine frozen target
(#65, #66, Q3-002) — ever reached that target** (`TP1 touched = NO` for every single trade with a
target, per the dataset's §3 table). This extends to the secondary population too: Q3-003's TP1 was
also never reached (0.36pt/0.364pt short by wick), and Q3-004's TP1 was never banked either (~5 pips
short, per its own OUTCOME_NOTES).

**Consequence: POLICY-1, POLICY-2, and POLICY-3 are structurally identical to POLICY-0 on this
entire dataset** — not because the frameworks are good or bad, but because their trigger condition
(reaching TP1) **never fires for a single trade in the whole Q1-Q3 record**. This is reported
plainly rather than fabricating a counterfactual TP1-touch that did not happen (forbidden by §7 of
the mandate). See §6 below (the 40/30/30 audit) for what this means for that framework specifically.

**POLICY-4 is therefore the only policy in the pre-registered set with any differentiated effect on
this dataset**, and its results are reported in full below.

---

## 3. POLICY-4 — primary metrics (§9)

```
N (trades touched by the policy)      = 4  (of 12 primary; all 4 are Q2 SHORT losses with MFE>=1.0R)
ORIGINAL_TOTAL_R (POLICY-0, n=12)     = -3.446
POLICY-4_TOTAL_R (n=12)               = +0.118
DELTA_R                                = +3.564
```

| Metric | POLICY-0 | POLICY-4 |
|---|---|---|
| TOTAL_R | −3.446 | +0.118 |
| AVG_R | −0.287 | +0.010 |
| MEDIAN_R | −1.140 | −0.523 |
| WR | 25.0% (3/12) | 25.0% (3/12 winners unchanged; 4 additional trades moved to exactly 0R, neither win nor loss) |
| MAX_WIN | +2.463 (#58) | +2.463 (#58, unchanged) |
| MAX_LOSS | −1.398 (#66) | −1.379 (#60, since #66 is converted to 0R) |
| AVG_WIN (positive-R trades only) | +2.071 (n=3) | +2.071 (n=3, unchanged — POLICY-4 never touches winners) |
| AVG_LOSS (negative-R trades only) | −1.075 (n=9) | −1.140 (n=5, the 4 converted trades are removed from the loss set entirely) |

**`MFE_CAPTURE_RATIO`**: for the 4 converted trades, POLICY-0 captured 0% of MFE (all 4 closed
negative despite positive MFE); POLICY-4 captures the breakeven point (0R) of each — a partial, not
full, capture (the policy does not attempt to bank any of the MFE profit itself, only to stop the
bleed at 0). **`R_GIVEN_BACK_AFTER_PEAK`** for these 4 trades under POLICY-4 = MFE_R itself (0.046R
to 1.626R) — POLICY-4 does not solve full giveback, only prevents the giveback from crossing into
loss territory.

```
LOSSES_CONVERTED_TO_BREAKEVEN   = 4  (#59, #62, #65, #66)
LOSSES_CONVERTED_TO_SMALL_WIN   = 0  (POLICY-4 as specified only moves to breakeven, not a small
                                       locked-in profit — a stricter/looser variant was not tested,
                                       per the no-threshold-mining rule)
WINNERS_TRUNCATED                = 0
LARGE_WINNERS_PRESERVED          = YES (all 3 winners — #58, #63, #64 — completely untouched)
TOTAL_EXTRA_EXIT_ACTIONS         = 0  (POLICY-4 is a single full-position stop adjustment, not a
                                       partial exit — no additional transaction beyond the original
                                       single entry+exit)
NET_COST_IMPACT                  = 0  (no incremental transaction; GROSS = NET for this policy — see
                                       §5 below)
```

---

## 4. Winner-destruction test (§10)

```
R_SAVED_ON_LOSERS       = +3.564R  (the 4 converted trades: 0.046+1.001+1.119+1.398)
R_LOST_ON_WINNERS       = 0R  (no winner's realized path ever returned to breakeven in this sample,
                                so POLICY-4's trigger condition for intervention never applies to a
                                winner — confirmed directly, not assumed: #58/#63/#64 all closed
                                solidly positive, well above 0R)
INCREMENTAL_COST         = 0R  (§3 above)
NET_MANAGEMENT_VALUE     = R_SAVED_ON_LOSERS - R_LOST_ON_WINNERS - INCREMENTAL_COST = +3.564R
```

**This policy passes the winner-destruction test cleanly on the available evidence** — it is
mechanically incapable of truncating a winner in this dataset, because it only ever intervenes when
price has already retraced to breakeven, and no realized winner ever did that.

---

## 5. Cost model (§8)

No canonical, separately-documented spread/slippage cost model was identified as read this pass in
this repository specific to the apprenticeship's XAUUSD trade-management research (the apprenticeship
throughout uses a **close-based fill convention** — every original RESULT_R already embeds real
overshoot/undershoot from the nominal stop/target level, e.g. #60's 2.458pt close-based stop
overshoot, #62's four wick-tests before the eventual 0.009pt-margin triggering close — i.e. the
GROSS figures above are not idealized frictionless fills, they already carry the project's own
standing execution realism). **`POLICY-4` introduces zero additional transactions** (it is a single
stop-level change on the same one position, not a partial exit), so **GROSS = NET_OF_COSTS for this
policy specifically** — there is no incremental spread/slippage to model beyond what the original
close-based-fill convention already captures. This limitation (no separate formal cost model
identified) would matter more for POLICY-1/2/3 (which do add partial-exit transactions) — moot here
since those policies never trigger on this dataset (§2).

---

## 6. 40/30/30 audit (§16)

```
40_30_30_VERDICT = 40_30_30_INSUFFICIENT_EVIDENCE
```

**Not `SUPPORTED` and not `NOT_SUPPORTED`** — genuinely `INSUFFICIENT_EVIDENCE`, because the
framework was never actually put to a test in this record. Mechanically: **the 40/30/30 framework
by name (40% TP1 / 30% TP2 / 30% final) is specified exactly once in the entire Q1-Q3 record**
(Q3-005's entry tags — excluded from this study's populations for lack of MFE/MAE evidence — Q3-005
stopped out in 2h15m before ever approaching TP1). Every other trade with any target structure used
either no target (#57-64), a single non-split TP (#65, #66), or a 2-way 50/50 split (Q3-002, not
40/30/30). **No trade in the entire retained record has ever banked a TP1 of any kind, at any
split.** The 40/30/30 framework cannot be credited or blamed for anything that has actually happened
to a real trade yet — this is reported as the honest, mechanically-derived answer, not softened into
a default "supported" reading just because it is the currently-preferred framework.

---

## 7. Entry failure vs. management failure (§11)

| Category | Trades | n |
|---|---|---|
| `ENTRY_FAILED_BEFORE_MEANINGFUL_MFE` (MFE < 0.5R) | #57, #60 | 2 |
| `ENTRY_WAS_DIRECTIONALLY_USEFUL_BUT_MANAGEMENT_GAVE_BACK_VALUE` (MFE >= 0.5R, RESULT_R <= 0) | #59, #61, #62, #65, #66, Q3-001, Q3-002 | 7 |
| `NORMAL_WINNER` | #58, #63, #64 | 3 |
| `AMBIGUOUS` | none | 0 |

**Only 2 of 9 losing trades (22%) had entries that failed before generating any meaningful favorable
move — management genuinely cannot be expected to fix these.** The remaining 7 of 9 losses (78%) had
real, meaningful favorable excursion that was subsequently given back. **This does not mean
management could have saved all 7** — POLICY-4 (at its pre-registered, non-mined 1.0R threshold)
only reaches 4 of the 7 (the other 3 — #61 at 0.695R, Q3-001 at 0.686R, Q3-002 at 0.752R — never
crossed the chosen threshold). This is stated as a real limit on what this specific, non-mined policy
can claim credit for, not exaggerated into "management fixes the strategy."

---

## 8. Robustness (§13) and leave-one-out (§14)

**Q2 vs Q3:** DELTA_R is **+3.564R from Q2 alone, +0.000R from Q3** (neither of Q3's 2 primary trades
ever reached the 1.0R trigger). **Q3 does not contradict the policy (it never had the chance to),
but it also supplies zero confirming evidence** — this is disclosed as a real concentration limit,
not glossed over as "both quarters support it."

**Wins vs. losses:** by construction, POLICY-4 only ever affects losses (0 winners touched, §4).

**Long vs. short:** **all 4 converted trades are SHORT.** The primary population's only LONG trade
(#63) is a winner, untouched by the policy. **POLICY-4 has zero LONG-trade loss evidence in this
sample** — `INSUFFICIENT_EVIDENCE` for direction-specific generalization, disclosed as a further
concentration caveat alongside the quarter concentration above.

**Session/context groups:** the 4 converted trades span PRE_US, NY_US_CASH, and LONDON sessions (per
the path dataset's §5) — not concentrated in a single session, a mild positive robustness signal, but
n=4 is too small to support a real per-session breakdown (`INSUFFICIENT_EVIDENCE` for anything finer
than "not obviously single-session").

**Leave-one-out** (removing each of the 4 converted trades individually from the DELTA_R
calculation):

```
remove #59: remaining delta = +3.518R  (still positive)
remove #62: remaining delta = +2.563R  (still positive)
remove #65: remaining delta = +2.445R  (still positive)
remove #66: remaining delta = +2.166R  (still positive)
```

**The sign of the improvement never flips under leave-one-out — `TAIL_DEPENDENT / FRAGILE` does NOT
apply.** The result is not one-trade-driven in the sign-flip sense, though it remains
quarter-and-direction-concentrated as noted above (a distinct caveat from single-trade fragility).

```
ONE_TRADE_DEPENDENT = NO  (sign never flips on any single-trade removal)
```

---

## 9. Key counterfactual (§15)

```
ORIGINAL_TOTAL_R    = -3.446   (primary population, n=12)
COUNTERFACTUAL_TOTAL_R (POLICY-4) = +0.118
DELTA_R              = +3.564

DELTA_FROM_LOSS_REDUCTION   = +3.564R  (all of it — 4 losses converted to exact breakeven)
DELTA_FROM_WINNER_TRUNCATION = 0R      (no winner touched)
DELTA_FROM_COSTS             = 0R      (no incremental transaction, §5)
```

**Had this policy existed prospectively before Q2/Q3, the primary population's total result would
have moved from solidly negative (−3.446R) to roughly flat (+0.118R) — entirely from loss reduction,
with no winner sacrificed and no additional cost.** This is a materially different outcome achieved
with the *exact same entries* — direct, mechanical evidence that at least part of the apprenticeship's
poor Q1-Q3 P&L is a management-layer property, not purely an entry-quality property. **This is not
claimed to make the underlying entries "good" — see §7's honest 2-of-9 entry-failure floor.**

---

## 10. Should management depend on context? (§17)

```
UNIVERSAL_MANAGEMENT_PLAUSIBLE      = YES (on current evidence — POLICY-4 fired across 3 different
                                       sessions with a uniformly positive, non-flipping effect; no
                                       evidence yet suggests a universal BE-at-1R rule needs
                                       session/regime branching)
CONTEXT_DEPENDENT_MANAGEMENT_PLAUSIBLE = UNKNOWN — the sample (n=4 affected trades) is too small to
                                       rule out context-dependence, and the entire supporting sample
                                       is Q2-only, SHORT-only, single-regime (H4-BEARISH standing tag,
                                       same INDEPENDENCE_LIMITATION that applies to PATTERN-007) —
                                       genuinely unknown, not asserted either way, and specifically
                                       NOT explored further this pass per the mandate's own
                                       instruction not to mine context-specific policies without
                                       sufficient evidence.
```

---

## 11. Strategy-readiness reassessment (§19)

```
PRIMARY_STRATEGY_BLOCKER (before this research)   = INSUFFICIENT_REGIME_DIVERSITY / INDEPENDENCE_LIMITATION
SECONDARY_STRATEGY_BLOCKER (before this research)  = MFE-giveback / management-exit problem

PRIMARY_STRATEGY_BLOCKER (now)   = INSUFFICIENT_REGIME_DIVERSITY / INDEPENDENCE_LIMITATION — UNCHANGED.
                                    Nothing in this management research touches regime diversity; it
                                    was never in scope (§1 of the mandate explicitly forbids new
                                    entries/regimes).
SECONDARY_STRATEGY_BLOCKER (now)  = MFE-giveback / management-exit problem — MATERIALLY REDUCED, NOT
                                    ELIMINATED. A concrete, evidence-grounded, non-overfit candidate
                                    (POLICY-4) now exists with a well-specified prospective test
                                    protocol (§`AI_TRADER_Q4_MANAGEMENT_PROSPECTIVE_PROTOCOL_V1.md`).
                                    It remains UNVALIDATED and its supporting evidence is
                                    Q2-only/SHORT-only/single-regime — it has NOT eliminated the
                                    secondary blocker, it has produced the first concrete, testable
                                    step toward addressing it.
```

**Did management research materially reduce the secondary blocker?** Yes, in the sense that a
specific, well-specified, evidence-consistent candidate now exists where before there was only a
diagnosed problem with no proposed fix. It has not been eliminated — POLICY-4 is UNVALIDATED and
untested on Q3/LONG/any regime other than the standing one.

**Does regime diversity remain the primary blocker?** Yes, unambiguously — nothing in this mandate's
scope could have changed that (it explicitly excludes new entries, new regimes, and Q4 data).

**Should Q4 now begin?** See the final CEO report — the recommendation is that Q4 CAN now
meaningfully test both blockers simultaneously (regime diversity via ordinary forward replay, and the
management candidate via the frozen prospective protocol applied to any new Q4 trades), **without
contaminating the apprenticeship**, because the protocol (§`AI_TRADER_Q4_MANAGEMENT_PROSPECTIVE_PROTOCOL_V1.md`)
is fully frozen *before* any Q4 bar is revealed, uses only entry-time-available information, and does
not alter entry/direction/setup logic in any way — it is a pure post-entry management overlay, fully
separable from the entry-discovery mission Q4 will otherwise conduct.

---

## 12. Success gate (§20)

Checking POLICY-4 against all 8 conditions:

```
1. causal and fully specified                                    -> YES
2. no threshold mining                                            -> YES (1.0R pre-registered by
                                                                     convention, not fit to this data)
3. positive net improvement after costs                           -> YES (+3.564R, NET=GROSS)
4. improvement not entirely one-trade driven                      -> YES (leave-one-out stays
                                                                     positive on every single removal)
5. does not destroy the large-winner tail                         -> YES (0 winners touched)
6. mechanism understandable                                       -> YES (standard risk-management
                                                                     rationale, not a black box)
7. both Q2 and Q3 evidence do not directly contradict it          -> PARTIAL — Q2 supports it, Q3 is
                                                                     silent (0 applicable trades), not
                                                                     contradicting but not confirming
                                                                     either; disclosed as the weakest
                                                                     of the 8 conditions
8. exact prospective Q4 protocol can be frozen                    -> YES, see the dedicated protocol
                                                                     document
```

**7 of 8 conditions cleanly met; condition 7 is met in the weak "no contradiction" sense only, not
the strong "both quarters confirm" sense.** Given the mandate's own instruction that "no result may
become validated here" and that the gate produces `MANAGEMENT_CANDIDATE_UNVALIDATED` rather than
anything stronger, this is judged sufficient to clear that specific (unvalidated) status — see
`AI_TRADER_MANAGEMENT_POLICY_LIBRARY_V1.md` for the formal specification and status assignment.

---

*See `AI_TRADER_MANAGEMENT_POLICY_LIBRARY_V1.md` for the formal immutable specification and
`AI_TRADER_Q4_MANAGEMENT_PROSPECTIVE_PROTOCOL_V1.md` for the frozen (not yet authorized) forward-test
protocol.*
