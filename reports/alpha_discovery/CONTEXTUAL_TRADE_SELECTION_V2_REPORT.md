# CONTEXTUAL TRADE SELECTION V2 — setup-relative winner-vs-loser discrimination

Binding execution spec. The exact question — *why does the same frozen setup win in some pre-decision market contexts and lose in others, and
can a causal context model keep a useful fraction of winners while disproportionately removing losers?* — was answered with the mandated
representations (setup-relative coordinates, preserved ordered 8/16/32-bar sequences, an order-sensitive sequence model) under a strict
chronological walk-forward. No proxy substitution; no strategy modified; no exhaustion claim. INTERNAL_GENERALIZATION only (history materially
exposed). Protections intact (S5 / AI-Trader / P007 / MGMT-004 / MT5 / StrategyCatalog / V2 rescue register untouched). 3 setups only; no auto-scale.

## What V2 corrects about V1
V1's "STATE beats PATH, so arrival path doesn't matter" was **not** a licensed conclusion. V2 tested the materially different setup-relative
representation and finds: **`SETUP_RELATIVE_INCREMENTAL_VALUE = YES`** — setup-relative geometry (B) beats generic state (A) by **+0.067R
(SETUP_2)** and **+0.063R (SETUP_3)** at 60% winner-retention, in ≥2/3 TEST folds AND pooled. So setup-relative context genuinely carries
winner-vs-loser information beyond generic market state. The V1 claim is retracted; the correct statement is that the *setup-relative static
position* (distance/penetration relative to the reference), not the arrival-path aggregates or ordered sequence, is what adds the value.

## The decisive result — real, controlled, cross-mechanism context, but no practical positive edge
Under the mandated walk-forward (4 date-blocks, expanding folds, purge 96) at the practically-useful **60% winner-retention** target, **every
representation on every setup is negative** (best −0.072R), with **0/3 folds positive** anywhere. The winner-retention frontier never yields a
≥60%-retention point with ≥+0.10R base expectancy → **`PRACTICALLY_USEFUL_CONTEXT_SELECTION = NO`** (`§24` standard met by 0 points).

| setup | mechanism | base exp | best rep @60% | best sel exp @60% | losers avoided | class |
|---|---|---|---|---|---|---|
| SETUP_1 | liquidity sweep | −0.314 | B setup-static | −0.268 | 42% | LOSE_LESS_ONLY |
| SETUP_2 | breakout-retest | −0.374 | B setup-static | −0.266 | 43% | LOSE_LESS_ONLY |
| SETUP_3 | auction-value | −0.176 | B setup-static | **−0.072** | 64% | POSITIVE_BUT_IMPRACTICAL |

The selection is **not a null artifact** — it beats matched-random-N selection in 3/3 setups and label-permutation in 2/3 (`NEGATIVE_CONTROL_GATE
= PASS`). It captures a real, coherent, cross-mechanism signal (`CROSS_SETUP_CONTEXT_FOUND = YES`): setups fired into a **compressed /
low-participation** state resolve worse; genuine participation/volatility-expansion resolves better. But the signal is *necessary-not-sufficient*
— it lowers losses without removing the base strategies' negative edge.

## Sequence order and idea ranks
- **`SEQUENCE_ORDER_INCREMENTAL_VALUE = NO`** — the order-sensitive model beats its bar-order-destroyed control by only +0.006 / +0.006 /
  +0.035R (max 0.035 < the +0.05 bar). Order is not noise (all three positive) but its incremental value is sub-threshold.
- **Idea-class ranks (§32, mean |corr| across setups):** VOLUME-RELATIVE-TO-IMPULSE = **HIGH** (0.0326 — the CEO's "participation attacking a
  level" intuition ranks high and partly validates); LEVEL-WEAKENING (bearish-block-style pressure) = **MEDIUM**; APPROACH-GEOMETRY = **MEDIUM**;
  STRUCTURAL-PRESSURE (HH/LL) = **LOW**. Generic volatility/participation state remains marginally top.

## §40 CEO answers
1. **Which 3?** SETUP_1 S21 liquidity-sweep (M01), SETUP_2 S3 breakout-retest (M03), SETUP_3 S27 auction-value (M16). 2. **Why (not via V1 context result)?** causal validity + large balanced winner/loser populations + clear reconstructable reference geometry + mechanism diversity — selection used none of V1's contextual performance. 3. **Original identity reproduced?** YES — regenerated via the canonical engine, entry/stop/target/cost unchanged, decision bars `si` reproduced (freeze hash `f154f171…`). 4. **Setup-relative beat generic?** YES (+0.06–0.07R, 2/3 setups). 5. **Ordered sequence add info?** marginally (+0.006…+0.035R), below threshold → NO by the §26 bar. 6. **Did destroying order hurt?** slightly (all 3 positive deltas), not materially. 7–9. **Winner-vs-loser drivers (S1 sweep / S2 breakout / S3 auction)?** all three: participation/volatility STATE (volrank↑, atr-vs-MA↑, compress↓ → better) + relative participation (persistent toward-volume↑, progress-per-volume↓ → better); plus setup-relative distance/penetration for S2/S3. 10. **Approach pressure?** MEDIUM (some, sub-dominant). 11. **Pullback progression?** weak. 12. **Level weakening/defense?** MEDIUM (penetration/distance help for level setups). 13. **Causal structure (HH/LL)?** NO (weakest). 14. **Volume relative to attack/pullback?** YES — HIGH. 15. **Generic volatility still dominant after setup-relative added?** roughly co-equal — generic state is marginally top, but setup-relative static adds a real +0.06R increment. 16. **At 80% retention, losers avoided?** ~20–35% (little). 17. **At 60%?** 42–64%. 18. **Any subset ≥+0.10R base?** NO at ≥60% retention. 19. **Stayed >0 under STRESS?** N/A (none positive). 20. **Positive in ≥2/3 folds?** NO (0/3). 21. **drop-best-5% positive?** NO. 22. **Independent trades/yr?** high (340–750/yr) but the selection is negative. 23. **50 future obs in ≤24 months?** the firing supports it, but there is nothing positive to validate. 24. **Coherent unseeded behavior?** YES — participation-behind-the-move (compression/low-volume → failure) recurs across mechanisms. 25. **Human idea ranked low?** YES — HH/LL structural pressure (LOW); order/sequence sub-threshold. 26. **Strongest justified conclusion?** setup-relative + participation context genuinely separates winners from losers across these 3 mechanisms and beats generic state, but does not reach a practically-useful positive selection at ≥60% winner retention. 27. **Not justified?** any claim that price/context/path is exhausted, or that arrival-path never matters.

## §41 FINAL VERDICT
```
CONTEXTUAL_TRADE_SELECTION_V2_COMPLETE = YES
PREFLIGHT_END_TO_END_EXECUTABLE = YES
BASE_SETUPS = 3 · BASE_SETUP_IDS = [SETUP_1 S21::M01_sweep, SETUP_2 S3::M03_breakout_retest, SETUP_3 S27::M16_auction_value]
BASE_SETUP_FREEZE_HASH = f154f1717c74811603def9f6 · CTS_V2_PROTOCOL_HASH = 17cb1e66c6d324ba83f22582
TOTAL_TRADES = 50268
GENERIC_STATE_BASELINE_RESULT = negative at every retention (best SETUP_3 A@60 = -0.135R)
SETUP_RELATIVE_INCREMENTAL_VALUE = YES (B beats A by +0.067R S2 / +0.063R S3, >=2/3 folds + pooled)
SEQUENCE_ORDER_INCREMENTAL_VALUE = NO (max delta +0.035R < +0.05)
SETUP_1_CLASSIFICATION = LOSE_LESS_ONLY
SETUP_2_CLASSIFICATION = LOSE_LESS_ONLY
SETUP_3_CLASSIFICATION = POSITIVE_BUT_IMPRACTICAL
SETUPS_WITH_PRACTICALLY_USEFUL_CONTEXT_EDGE = 0 · POSITIVE_BUT_IMPRACTICAL = 1 · LOSE_LESS_ONLY = 2 · NO_INCREMENTAL_CONTEXT_INFORMATION = 0
BEST_SETUP = SETUP_3 (auction-value) · BEST_REPRESENTATION_CLASS = B_setup_relative_static
BEST_BASE_EXPECTANCY = -0.176R · BEST_SELECTED_EXPECTANCY_BASE = -0.072R · BEST_SELECTED_EXPECTANCY_STRESS = -0.353R
BEST_WINNER_RETENTION = 58% · BEST_LOSER_AVOIDANCE = 64% · BEST_SELECTED_N = 8908 · BEST_EFFECTIVE_TRADES_PER_YEAR = ~594 (but negative)
APPROACH_PRESSURE_INFORMATION = YES (weak/medium) · PULLBACK_PROGRESSION_INFORMATION = NO
LEVEL_WEAKENING_INFORMATION = YES (medium) · STRUCTURE_INFORMATION = NO · RELATIVE_PARTICIPATION_INFORMATION = YES (high)
SEQUENCE_DESTRUCTION_CONTROL = order carries sub-threshold info (real > destroyed by <=0.035R) · NEGATIVE_CONTROL_GATE = PASS
HUMAN_COHERENT_MARKET_REASONING_FOUND = YES (participation-behind-the-move; compression/low-volume -> failure)
NEW_NONOBVIOUS_CONTEXT_DISCOVERY = YES (setup-relative static geometry adds real increment over generic state; participation>structure)
CROSS_SETUP_CONTEXT_FOUND = YES
PRACTICALLY_USEFUL_CONTEXT_SELECTION = NO
PRACTICALLY_VALIDATABLE_WITHIN_24_MONTHS = NO (nothing positive to validate)
READY_TO_SCALE_TO_REMAINING_7_SETUPS = NO
BROADER_PRICE_CONTEXT_EXHAUSTION_CLAIM_AUTHORIZED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Authorized scope of conclusion (§35)
The specified CTS V2 setup-relative representations did NOT produce a practically useful contextual edge on these three setups. They DID show
that setup-relative context carries real, cross-mechanism winner-vs-loser information that beats generic state and beats random/permutation
nulls — but it only reduces losses, and ordered-sequence structure adds sub-threshold value on these mechanisms. No broader claim (price
exhausted, context exhausted, arrival path never matters, new data mathematically required) is made or supported by this experiment.
```
CTS_V2 = COMPLETE — setup-relative context is real and beats generic state, but no practically-useful positive selection on these 3 setups
```
