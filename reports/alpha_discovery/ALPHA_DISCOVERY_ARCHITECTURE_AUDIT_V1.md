# ALPHA_DISCOVERY_ARCHITECTURE_AUDIT_V1 — false-negative & search-direction audit

Meta-research only (§18): no new experiment, no optimization, no data acquisition, no engine/NKB changes. Diagnosis of the discovery
PROCESS from existing artifacts. The CEO's question: are repeated SURVIVED=0 results genuine efficiency, or an over-narrow search
architecture? Verified inputs used (this session): TEMPORAL positive-control +0.56 (engines have power); OB level info confirmed but 4
executions + fixed-2R net-neg (corrected fill −0.067); session-state beats matched control +0.05..0.15R but era-trend; cross-market
residual does not beat the simple DXY impulse (−0.069).

## 0. The single most important empirical fact
**Positive-control tests pass** (TEMPORAL future-return motif shifts within-cell P(up) +0.56; GC divergence fwd positive-control
p=.0005). The engines detect information when it exists. Therefore the negatives are **real**, not powerless — but "real" applies to what
was actually tested: **directional prediction with fixed-R exits on M15+**. That is a narrow slice of strategy space.

And the one survivor, **S5**, does NOT predict direction in advance. It waits for the NY opening range to break — letting the market
REVEAL direction via a causal event — then trades continuation. Every falsified frontier tried to FORECAST direction. **S5 is a
conditional-response strategy in a sea of prediction attempts.** This asymmetry is the thread running through the entire audit.

## 3. Frontier-by-frontier classification (WHY, not the report verdict)
| frontier | classification | why |
|---|---|---|
| Modular 56-branch taxonomy | SEARCH_SPACE_EFFECTIVELY_SATURATED (for directional prediction) | every directional primitive → era-trend; broad, positive-control-backed |
| VOLTIME (vol timing) | EXECUTION_FAILED_BUT_INFORMATION_EXISTS + OUTCOME_MODEL_LIMITED | magnitude/expansion predictable & cross-era-stable, but forced into directional fixed-R |
| VOLPATH (path geometry) | OUTCOME_MODEL_LIMITED | whipsaw/expansion geometry is real info; monetized only as directional fixed-R (failed) |
| DXY / DXY-NDX1 | MECHANISM_FALSIFIED (directional) + DATA_LIMITED | DXY→gold regime-inverts; the *driver* (real yields) never tested |
| SESSION_TIMING / SESSION_SPECIALIST | EXECUTION_FAILED_BUT_INFORMATION_EXISTS + REGIME_DEPENDENT_POSSIBLE | session-state beats control +0.05..0.15R but only era-trend cells positive; no causal regime gate tried |
| Contrast Miner V2 | REPRESENTATION_MAY_BE_TOO_WEAK | single static ex-ante price features carry no discriminator; interactions & state-machines untested |
| TEMPORAL_SEQUENCE | MECHANISM_GENUINELY_FALSIFIED (path→direction) | P(up)≈0.50 in all 19 ordered classes; +0.56 positive control ⇒ a true, powered negative for ORDER→direction |
| H1_H4 setup + M5 exec | MECHANISM_FALSIFIED (HTF-selection→direction) + REGIME_DEPENDENT_POSSIBLE | HTF_ON≈HTF_OFF; only positive cell (TGT_BREAK O-era) = R20 era-trend |
| ORDER_BLOCK_RETEST / OB_EXEC | EXECUTION_FAILED_BUT_INFORMATION_EXISTS + OUTCOME_MODEL_LIMITED | OB level info Statistician-confirmed; 4 causal executions + fixed-2R all net-neg; skew/trailing exit never tested |
| CROSS_MARKET_RELATIVE_RESPONSE | MECHANISM_FALSIFIED + DATA_LIMITED | residual doesn't beat the raw impulse; only DXY, 3 blocks, no 2024+, no risk proxy |
| GOLD_ORDER_FLOW | DATA_LIMITED | 2-week MBO sample only; TIER_C for research |

**Pattern:** two frontiers are *genuinely* falsified (TEMPORAL path→direction; cross-market residual). The **majority are
EXECUTION_FAILED / OUTCOME_MODEL_LIMITED / REGIME_DEPENDENT_POSSIBLE** — i.e. information exists but the way we tried to monetize it
(directional prediction, fixed-R, M15-first, unconditional cross-era) suppressed it. That is a search-architecture signal, not pure
efficiency.

## 4. Fixed-R false-negative audit
`COULD_FIXED_R_TESTING_BE_CAUSING_MATERIAL_FALSE_NEGATIVES = YES.` Evidence: (a) the OB level's edge over control GREW with target (≈0 at
1R, +0.24..0.52 at 2R/3R) — payoff structure interacts with the signal; (b) VOLTIME/VOLPATH established that *expansion magnitude* is the
predictable quantity, and a 2R cap **truncates exactly the rare large continuation** the CEO wants (100–300 pip moves); (c) most families
sit at WR 0.42–0.48, just under the 2R break-even (0.413) — a positive-skew exit (trail/structural/partial) could flip several from
break-even to positive without any new signal. `FIXED_R_FALSE_NEGATIVE_RISK = HIGH.`

## 5. Entry false-negative audit
Entry semantics demonstrably matter (the OB +0.154→−0.067 correction). But the executions we DID vary (OBEXEC A/B/C/D) never rescued a
negative baseline, so entry narrowness is real but second-order to target/timeframe. Untested and plausibly material: **breakout-ACCEPTANCE
vs first-break** (S5 is acceptance), state-transition entries, volatility-trigger entries, and native M5 execution. Assessment: MEDIUM.

## 6. Timeframe (M15-first) audit
`M15_FIRST_FALSE_NEGATIVE_RISK = HIGH.` We have ALWAYS aggregated to M15 before inspecting M5, and never ran M5-NATIVE discovery. Sweeps,
reclaims, opening impulses, short-lived imbalances and precise retests are **M5-native phenomena that vanish under M15 aggregation** (a
sweep-and-reclaim inside one M15 bar is invisible). The one M5 test (87% miss) was a *pullback* entry on a *breakout* thesis — structurally
wrong, not evidence M5-native fails. Native M5 exists 2021+ (354k bars, 5 yr) — enough for recent-era discovery. This is the **single
biggest blind spot**.

## 7. Regime-conditional audit
`REGIME_CONDITIONAL_SEARCH_UNDEREXPLORED = YES.` We rejected strategies whose UNCONDITIONAL sign flips across calendar eras (D/C/O) — but a
strategy gated on a **prospectively-observable causal regime** (realized-vol state, ATR percentile, trend-persistence, session-vol) is
legitimate even if its unconditional sign flips. We used the **hindsight era label**, never a **causal regime variable**. Distinguish:
HINDSIGHT ERA LABEL (rejected, correctly) vs PROSPECTIVELY OBSERVABLE REGIME (never built/tested). Several "era-trend" rejections
(TGT_BREAK, session A/D, VOLTIME) may be regime-conditional edges we discarded with too blunt a criterion.

## 8. Static rules vs state machines
`SEQUENTIAL_STATE_SEARCH_UNDEREXPLORED = YES.` Most hypotheses were static "IF A+B+C → enter". TEMPORAL tested ORDER but as a static
classifier of the path, not a true state machine with **failure/acceptance branches** (sweep→displacement→failed-acceptance→reclaim→
continuation, where the trade requires reaching a terminal state *through* intermediate failures). OBR was the closest (OB→displacement→
BOS→retest) and got furthest (SURVIVED=1 pre-artifact) — suggestive that multi-stage structure is where residual signal lives.

## 9. Interactions
`INTERACTION_SEARCH_UNDEREXPLORED = YES.` Hypotheses were hand-designed with 1–3 conditions; the Contrast Miner tested discriminators one
at a time. We never used transparent interaction discovery (small decision trees, rule lists, conditional-probability surfaces) to FIND
which combinations matter — while keeping OOS/control discipline. Caveat: interaction mining raises overfit risk; must stay transparent +
pre-registered.

## 10. Directional prediction may be the wrong target — THE KEY FINDING
`CONDITIONAL_RESPONSE_SEARCH_PRIORITY = HIGH.` Almost all search was "predict UP vs DOWN before the move" — the axis we proved efficient 10
times. The **predictable** quantities (expansion, continuation-conditional-on-a-revealed-move, magnitude, path) were repeatedly confirmed
(VOLTIME, VOLPATH, OB-level, session-state) but forced into directional prediction and discarded. **S5 works because it doesn't forecast
direction — a causal event (OR break) reveals it, then S5 harvests the predictable continuation.** We should search
"CONDITIONAL RESPONSE AFTER THE MARKET REVEALS DIRECTION," not "PREDICT DIRECTION BEFOREHAND." This reframes the whole campaign.

## 11. Frequency / payoff
We implicitly favored many-trades / moderate-R / stable frequency, biasing against low-frequency high-payoff and event-driven plays (tied
to the fixed-R skew truncation). Must still separate LEGITIMATELY-RARE-EVENT from INSUFFICIENT-N. Concern: MEDIUM.

## 12. Data question — marginal value ranking
| data | marginal value | note |
|---|---|---|
| economic-event timestamps | HIGH | direction-REVEALING exogenous events; fits conditional-response; **already captured** by Data-Acq (near-zero cost) |
| real yields (US 10y TIPS) | HIGH | only untested exogenous DIRECTIONAL driver (what DXY reflects); slow/macro; needs acquisition |
| VIX / rates | MEDIUM | regime/vol context; supports regime-conditional search |
| NDX / SPX | MEDIUM | cross-market residual already weak; completes family F |
| GC futures / order-flow | MEDIUM | data-blocked; microstructure |
**Distinct space using CURRENT XAU data alone?** YES — M5-native + conditional-response + regime-conditional + skew-exit are all doable
with existing XAU M5 (2021+) and M15 (2011+). We have NOT exhausted current data correctly.

## 13. Engine strictness — required vs research-choice
SCIENTIFICALLY_REQUIRED (do NOT relax): causal fill, cost model, OOS, no-lookahead, no future HTF candle, same-bar honesty, outlier
analysis, no live promotion, matched-control for incremental-info claims.
RESEARCH_CHOICE (candidates to change WITHOUT adding hindsight):
- **M15-first / no-M5-before-M15-survival** → relax: allow M5-native discovery in the 2021+ window (real data, same OOS/control discipline). ↑power, no hindsight.
- **2R-first** → relax: test PRE-SPECIFIED structural/trailing/time/partial exits (captures skew). ↑power; moderate exit-mining risk → mitigate with pre-registration + OOS.
- **cross-era-sign-stable** → refine: allow PROSPECTIVELY-OBSERVABLE regime-conditional strategies; keep rejecting hindsight-era labels. ↑power, no hindsight if regime is causal.
- **simple-entry** → relax to disciplined state-transition/acceptance entries.
- fixed hypothesis budget, price-only baseline → keep (anti-mining).

## 14. Systematic blind spots (ranked)
1. **M5-native / fast** strategies (M15 aggregation destroys the event).
2. **Positive-skew / rare-large-payoff** strategies (2R cap truncates winners).
3. **Conditional-response / event-revealed-direction** strategies (we predict instead).
4. **Regime-conditional** strategies (unconditional cross-era sign-flip rejects them).
5. **Multi-stage state-machine** strategies (static classifiers miss them).
6. **Interaction-dependent** strategies (single-variable tests miss them).
7. **News/scheduled-event-driven** (calendar captured but never used in Alpha).

## 15. TOP 4 NEXT DIRECTIONS (as a research lead, outside the prior list)
### #1 CONDITIONAL-RESPONSE / EVENT-REVEALED-DIRECTION FACTORY (M5-native)
- MECHANISM: detect a causal direction-REVEALING event (decisive M5 displacement/acceptance/break of a pre-formed M15/H1 level), then
  trade the predictable continuation/expansion in the revealed direction with a skew-capturing exit — never forecasting direction.
- DISTINCT: generalizes S5 (the only winner) beyond the NY-OR; monetizes the proven-predictable axis, not the proven-efficient one.
- WHY PRIOR NEGATIVES DON'T FALSIFY: every prior negative FORECAST direction; this waits for the market to reveal it.
- DATA: existing XAU M5 (2021+) + M15 (levels). TIMEFRAMES: M15/H1 level → M5 event/execution. EVENT COUNT: medium (session-anchored).
- FAILURE MODE: over-fitting the event trigger; costs on M5. WHY EDGE: S5 is a working instance. VALUE=HIGH · OVERFIT=MEDIUM.
### #2 REGIME-CONDITIONAL EXPANSION HARVEST
- MECHANISM: build a CAUSAL, prospectively-observable regime detector (realized-vol / ATR-percentile / trend-persistence), then test the
  info-confirmed-but-non-monetizable signals (OB-level, session-state, VOLTIME magnitude) WITHIN a specific regime.
- DISTINCT: prior rejections used hindsight era labels; this gates on a causal regime. WHY NOT FALSIFIED: never gated prospectively.
- DATA: existing XAU only. TIMEFRAMES: M15/H1. EVENT COUNT: medium. FAILURE MODE: regime-conditioning overfit → strict pre-registration.
- WHY EDGE: several era-trend rejections may be regime edges. VALUE=MEDIUM-HIGH · OVERFIT=MEDIUM-HIGH.
### #3 EXIT / PAYOFF REFRAME ON CONFIRMED-INFORMATION SIGNALS
- MECHANISM: take the already-confirmed signals (OB-level, session-state) and test PRE-SPECIFIED non-fixed-R exits (structural/trailing/
  time/partial/vol-adjusted) for positive-skew monetization; and as a NON-directional S5 sizing/no-trade overlay.
- DISTINCT: reuses confirmed information; changes only payoff. WHY NOT FALSIFIED: only fixed 1R/2R/3R ever tested on these.
- DATA: existing XAU only. TIMEFRAMES: M15. EVENT COUNT: high. FAILURE MODE: exit-mining → pre-register + OOS. VALUE=MEDIUM · OVERFIT=MEDIUM.
### #4 SCHEDULED-EVENT (MACRO) RESPONSE
- MECHANISM: use the already-captured economic-calendar timestamps as direction-revealing events; trade the causal XAU response/continuation
  after a high-impact release (release reveals direction via the initial move).
- DISTINCT: event timing never used in Alpha; exogenous direction-revealer without new market data. WHY NOT FALSIFIED: no prior frontier used it.
- DATA: existing XAU + EXISTING calendar capture (no acquisition). TIMEFRAMES: M5/M15 around events. EVENT COUNT: low-medium (rare, legitimate).
- FAILURE MODE: event-timestamp alignment / survivorship. WHY EDGE: news is a genuine direction-revealer. VALUE=MEDIUM-HIGH · OVERFIT=MEDIUM.

## 16. Forced prioritization
Rank: **#1 Conditional-response M5-native > #2 Regime-conditional > #3 Exit-reframe > #4 Scheduled-event.**
- **IF ONLY ONE MORE PRICE-BASED CYCLE → #1 Conditional-response / event-revealed-direction (M5-native).** WHY: it directly generalizes the
  ONLY strategy that works (S5), exploits the proven-predictable axis instead of fighting the proven-efficient one, uses existing data, and
  its S5 precedent lowers overfit risk. Highest expected value of any remaining price-only cycle.
- **IF NEW DATA ALLOWED → real yields (US 10y TIPS)**, used through the conditional-response frame (regime/direction context), NOT raw
  prediction. WHY: the only genuinely untested exogenous DIRECTIONAL driver; every price/price-cross-market axis is now exhausted.
  (Runner-up: economic-event timestamps — nearly free since captured — if counted as "new to Alpha".)

## 17. Price-only saturation verdict
`PRICE_ONLY_NOT_SATURATED_BUT_CURRENT_REPRESENTATIONS_ARE.` Evidence: directional PREDICTION from price is saturated (10 frontiers +
passing positive controls). But we have NOT tested M5-native representations, conditional-response (post-event) formulation, regime-
conditional gating, or positive-skew exits — and **S5 proves a price-only edge exists in the conditional-response paradigm.** Do not
overstate to "price-only is dead"; the honest verdict is that our *representations and targets* are saturated, not the price data.

## 19. FINAL REPORT
```
ALPHA_DISCOVERY_ARCHITECTURE_AUDIT_COMPLETE = YES
ENGINES_TOO_STRICT = PARTLY (research-choices too narrow; scientific gates correctly strict)
SCIENTIFIC_RIGOR_TOO_STRICT = NO
SEARCH_ARCHITECTURE_TOO_NARROW = YES

M15_FIRST_FALSE_NEGATIVE_RISK = HIGH
FIXED_R_FALSE_NEGATIVE_RISK = HIGH
STATIC_RULE_FALSE_NEGATIVE_RISK = MEDIUM
REGIME_CONDITIONAL_SEARCH_UNDEREXPLORED = YES
INTERACTION_SEARCH_UNDEREXPLORED = YES
SEQUENTIAL_STATE_SEARCH_UNDEREXPLORED = YES
CONDITIONAL_RESPONSE_SEARCH_PRIORITY = HIGH

PRICE_ONLY_VERDICT = PRICE_ONLY_NOT_SATURATED_BUT_CURRENT_REPRESENTATIONS_ARE

TOP_NEXT_DIRECTION_1 = Conditional-response / event-revealed-direction factory (M5-native)
TOP_NEXT_DIRECTION_2 = Regime-conditional expansion harvest (causal regime gate on confirmed signals)
TOP_NEXT_DIRECTION_3 = Exit/payoff reframe on confirmed-information signals (skew-capturing exits + S5 overlay)
TOP_NEXT_DIRECTION_4 = Scheduled-event (macro) response using the existing calendar capture

BEST_NEXT_PRICE_ONLY_CYCLE = Conditional-response / event-revealed-direction (M5-native)
BEST_NEXT_NEW_DATA_CYCLE = Real yields (US 10y TIPS), used in the conditional-response/regime frame

WHAT_WE_ARE_MOST_LIKELY_MISSING = strategies that do NOT predict direction but RESPOND to a causal direction-revealing event and harvest
  the predictable expansion/continuation with a skew-capturing exit — especially M5-native ones destroyed by M15 aggregation
WHAT_WE_SHOULD_STOP_TESTING = any new price-only variable that PREDICTS M15 direction in advance (BOS/OB/pullback/session-breakout/reclaim/
  sweep/cross-market residual as directional predictors), and fixed-2R as the sole payoff on info-bearing signals
CEO_RECOMMENDATION = Reorient Alpha from directional PREDICTION to CONDITIONAL RESPONSE. Next price-only cycle = M5-native conditional-
  response (generalize S5) with pre-specified skew-capturing exits. Keep ALL scientific-integrity gates; relax three research-choices
  (M15-first → allow M5-native; fixed-2R → pre-specified structural/trailing exits; cross-era-sign-stable → prospectively-observable
  regime-conditional). Highest-value data decision = real yields, but only worth it inside the conditional-response frame.
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
