# Alpha Configuration Discovery Protocol

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Status**: DESIGN DOCUMENT ONLY — authorized
2026-07-21 by explicit CEO decision, following E027's closure. **This document defines process; it
performs no research, runs no backtests, generates no new edge candidates, and changes no prior
scientific verdict.** Nothing in `EDGE_DISCOVERY_REGISTRY_v1.md`, `EDGE_DISCOVERY_ROADMAP.md`, or any
individual edge's `.md` log is altered by this document. E016 and E013 remain not started. No
implementation of anything described below has occurred.

**Why this document exists**: the program has now completed six full Discovery passes (E006, E014,
E008, E011, E005, E027) plus the earlier E009/E010/E012/E015/E017 batch. Several of these found real,
replicated statistical properties of the market (session-dependent heterogeneity, compression-driven
fade behavior, swing-point/anchor-level non-magnetism). None of these is automatically a tradable
strategy. This protocol defines, precisely and in advance, how the laboratory will go from an isolated
statistical primitive to a fully specified, cost-aware, executable trade configuration — and how it
will resist overfitting while doing so.

---

## 1. Definitions

Every term below is fixed for all future work under this protocol. None may be silently redefined by
a future session; a redefinition requires a new, dated, appended version of this document, exactly
like every edge's own append-only research log.

**Market primitive.** A single, independently observable, mechanically-defined property of price
action — e.g. a session boundary, a liquidity sweep, a range-compression state, a displacement bar, a
zone-acceptance event, a failed pattern, a volatility regime, an anchor level, a trend state. A
primitive is a *measurement*, not a *trade*. A primitive may be statistically real (survive controls,
replicate across timeframes) without being independently tradable — this is the central distinction
this protocol exists to enforce.

**Context condition.** A higher-timeframe or slower-moving state that must hold for a configuration to
be considered active (e.g. D1/H4 trend direction, a volatility regime, a day-of-week/week-of-month
flag). Context conditions narrow *when* a configuration is eligible; they do not themselves generate
entries.

**Location condition.** A specific price-structural place where a setup is evaluated (e.g. inside a
compression zone, at a session boundary, at an anchor level, at a swing extreme). Location answers
*where* on the chart the configuration looks.

**Trigger.** The specific, mechanically defined event that fires the setup once context and location
are satisfied (e.g. a close beyond a level, a confirmed swing point, a session transition). A trigger
is binary and timestamped — it either fires at a bar or it does not.

**Entry.** The exact, deterministic rule mapping a trigger to an executable price and timestamp (e.g.
"market entry at the trigger bar's own close," "limit entry at a specific retracement level"). Entry
must be specifiable without reference to any bar after the entry bar.

**Invalidation.** The condition under which a configuration is abandoned *before* triggering, or a
live setup is cancelled without being taken as a trade (e.g. price closes back inside a range before a
breakout confirms). Invalidation is distinct from a stop-loss: invalidation cancels a *setup*; a stop
loss exits an already-*entered* trade.

**Stop loss.** The deterministic, pre-specified adverse-price level at which an entered trade is
closed for a loss. Must be statable in price terms at the moment of entry, not adjusted afterward
(no "moving the stop" as a matter of course — see §4, prohibition on post-hoc stop placement).

**Take profit.** The deterministic, pre-specified favorable-price level at which an entered trade is
closed for a gain, statable at the moment of entry.

**Holding horizon.** The maximum time (in bars or wall-clock duration) a trade may remain open before
being force-closed at market if neither the stop nor the target has been hit. Every configuration must
declare one; "hold indefinitely" is not a valid holding horizon.

**Executable edge configuration.** The complete tuple: *context + location + trigger + entry +
invalidation + stop loss + take profit + holding horizon + transaction-cost model*. A market primitive
is not an executable edge configuration; it becomes one only once every element in this tuple is
specified, deterministic, and frozen before evaluation.

**Positive expectancy.** The average R-multiple return per trade, after transaction costs, is greater
than zero: `E[R] = win_rate × avg_win_R − loss_rate × avg_loss_R − cost_R > 0`. **Win rate above 50% is
neither necessary nor sufficient for positive expectancy** — see the worked example in §"Important
constraints" below (reproduced from the CEO's own authorization message): at RR = 1:2, a 40% win rate
with average win = +2R and average loss = −1R yields `0.40×2 − 0.60×1 = +0.20R` per trade before
costs, a clearly positive-expectancy configuration despite losing on 60% of trades. Conversely, a
55% win rate at 1:2 with poor loss control could still be negative after costs. **Expectancy in R,
after costs, is the primary evaluation criterion throughout this protocol — never win rate alone.**

For a fixed target RR of 1:2, the theoretical **gross** (before-cost) break-even win rate is
`1 / (1 + 2) = 33.3%`. After deducting spread, slippage, and commission (each expressed in R units for
the configuration's own typical stop distance), the **required** break-even win rate is higher than
33.3% by exactly the cost's own R-equivalent — e.g. a cost of 0.15R raises the required win rate from
33.3% to roughly 36-38% depending on the loss-rate distribution; the exact figure must be computed per
configuration from its own disclosed cost model (§2), never assumed.

**Robustness.** A configuration's expectancy, sign, and rough magnitude persist across: (a) a
plausible neighborhood of its own parameters (§7 "Stage 5"), (b) a temporal split it was not built on
(§7 "Stage 3"), (c) a rolling walk-forward re-estimation (§7 "Stage 4"), and (d) more than one
volatility/trend regime (§7 "Stage 7"). A result that only holds at one exact parameter value, on one
time slice, in one regime, is not robust regardless of its point-estimate expectancy.

**Discovery candidate.** Any market primitive or configuration that has completed Stage 0-1 (§7) but
no further validation stage. Carries no claim of tradability.

**Validated edge.** A configuration that has completed all eight validation stages (§7) with positive,
robust, cost-adjusted expectancy at every stage it was evaluated on, and has been explicitly promoted
via the states in §9. Nothing in the program has reached this status as of this document's authoring.

---

## 2. Configuration schema

Every future configuration (from its very first Discovery-stage description onward) is recorded in
this single, canonical, machine-readable schema — no edge invents its own ad hoc fields for this
purpose. Fields marked **(required)** must be present and non-null before a configuration may leave
Stage 0.

```json
{
  "configuration_id": "string, e.g. E014-CFG-001",
  "derived_from": ["edge_id or V1 candidate id this configuration is built from"],
  "date_registered": "ISO date, before any evaluation",
  "higher_timeframe_context": {
    "timeframe": "e.g. D1/H4",
    "condition": "disclosed, mechanical definition",
    "rationale": "independent mechanism hypothesis, stated before evaluation"
  },
  "market_regime": {
    "volatility_regime": "low/mid/high tercile, or 'any' if not conditioned",
    "trend_regime": "bull/bear/range, or 'any' if not conditioned"
  },
  "session_or_time_window": "UTC session/hour condition, or 'any' if not conditioned",
  "structural_location": "the location condition, disclosed construction",
  "setup_condition": "context+location combined pre-trigger state",
  "trigger_condition": "exact, timestampable firing rule",
  "entry_price_rule": "deterministic mapping from trigger to entry price/time",
  "stop_loss_rule": "deterministic price rule, statable at entry",
  "take_profit_rule": "deterministic price rule, statable at entry",
  "target_rr": "default 1:2 unless justified (see below)",
  "maximum_holding_time_bars": "integer, required",
  "cancellation_conditions": "invalidation rule(s), pre-trigger only",
  "transaction_cost_model": {
    "spread": "disclosed estimate, instrument-specific",
    "slippage": "disclosed estimate",
    "commission": "disclosed estimate, 0 if genuinely absent for the instrument",
    "same_bar_ambiguity_policy": "how simultaneous stop+target touches on one bar are resolved",
    "gap_policy": "how a gap through stop/target is resolved"
  },
  "overlapping_trade_policy": "how concurrent signals on the same instrument are handled",
  "status": "one of the §9 promotion states",
  "validation_stage_reached": "0-8, per §7"
}
```

**Default target RR = 1:2**, matching this program's own standing Protocol v2 convention. A different
target RR may be used only with a stated, disclosed, *pre-registered* scientific justification (e.g.
the underlying primitive's own measured typical excursion ratio) — never selected after seeing which
RR produces a better backtest.

---

## 3. Primitive roles — classification of existing Discovery results

This is a classification of *already-completed, unchanged* Discovery results into the six roles below.
No verdict is altered; this is a relabeling for configuration-design purposes only.

| Edge / finding | Role | Basis |
|---|---|---|
| E006 (Asia range breakout, real-Asia-specific claim) | **Unsupported primitive** | Failed against a structural control; heterogeneity is generic to session timing, not Asia |
| E006 (session-dependent breakout-failure heterogeneity itself, generic form) | **Descriptive primitive** | Real, replicated (M15+H1), but not attributable to any single named mechanism yet |
| E008 (Friday-specific mechanism) | **Unsupported primitive** | Failed primary test + placebo + reversal test |
| E008 (Monday-quiet/Wednesday-volatile day-of-week pattern) | **Descriptive primitive** | Real, replicated, disclosed as out-of-scope for E008; not yet independently motivated as a conditioning variable — would need a fresh, pre-registered rationale before reuse (§4) |
| E011 (failed 3-drive pattern) | **Unsupported primitive** | Clean null across the entire battery, all three timeframes |
| E005 (London-close-specific reversal) | **Unsupported primitive** | Indistinguishable from another real boundary and a random hour |
| E017 (equal-highs/lows as magnet) | **Unsupported primitive** | Random-matched-distance control outperforms real levels |
| E027 (midnight-open as magnet) | **Unsupported primitive** | Same refutation signature as E017, independently replicated on a second level-type |
| E017 + E027 jointly ("reference levels are not magnets, on this instrument/resolution") | **Descriptive primitive** | Two independent, structurally-different level-types agree; not yet a registered cross-edge candidate (would need its own CEO-authorized registration, per the CEC-001 precedent) |
| E009 (CHoCH retest) | **Unsupported primitive** | No advantage over BOS control; retest metric near-saturated even for random control |
| E010 (breaker block) | **Unsupported primitive** | Coin-flip vs. its own natural control |
| E010's own control (unflipped OB, ~86-88% continuation) | **Candidate conditioning variable** | Real, large effect — but only as a *component*, per CEC-001's own registration and risk log, not a standalone edge |
| E012 (inverted FVG) | **Unsupported primitive** | Coin-flip vs. its own natural control |
| E012's own control (un-inverted FVG, ~86-87% continuation) | **Candidate conditioning variable** | Mirrors E010's control; also CEC-001-registered |
| **CEC-001** (unbroken-zone continuation, cross-edge observation) | **Candidate conditioning variable** | Explicitly registered as observation-only per its own document; look-ahead-bias and other risks not yet resolved; may not be used as a configuration input until those risks are addressed and it is separately promoted |
| E015 V0 (2nd+ mitigation reacts) | **Unsupported primitive** | Refuted; reaction concentrated in visit-1 only |
| E015's own "unfrozen V1 candidate" note (visit-1-only reaction) | **Descriptive primitive** (not yet a V1 Discovery Candidate under this protocol) | E015's own file records this as an *unfrozen* candidate, predating this protocol's stricter Discovery-Identity/freezing convention (cf. `EDGE_RESEARCH_PROTOCOL.md`'s Discovery Identity addition). Per explicit CEO statement, **E014 remains the only current V1 Discovery Candidate** — E015's note is not elevated by this document. |
| **E014-V1 (Compression-Driven False-Breakout Fade)** | **V1 Discovery Candidate** | Frozen contract exists (`E014_inside_bar_false_breakout.md`), replicated 3/3 timeframes, survived a 4-way control ladder — the program's only current V1 Discovery Candidate |
| E014's attempt-1-vs-attempt-2 decay | **Known mechanical artifact** | Identical collapse in a fully synthetic control with no market structure — explicitly not market knowledge |
| E027's apparent late-session effect | **Known mechanical artifact** | Attributed to the day-bounded horizon leaving unequal remaining time, not a genuine session effect |
| UTC 21:00 bar-coverage gap (OANDA_XAUUSD_M15) | **Dataset limitation** | Recorded in `NEXT_SESSION_FLOW_A.md` §"Data quality notes"; not imputed, not reinterpreted as market behavior |
| E025/E026/E028/E029/E032 (clean-rerun-confirmed mathematical edges) | **Descriptive primitive** | Statistically confirmed patterns; none has yet been run through this protocol's configuration schema |

**A rejected standalone primitive may only re-enter the program as a conditioning variable inside a
future configuration if there is an independent, pre-specified reason to test it** — stated and
registered *before* any configuration using it is evaluated, never introduced because it happens to
improve a backtest already in progress (§4).

---

## 4. Configuration generation rules

**Allowed sources for a new configuration proposal:**
- An existing, frozen **V1 Discovery Candidate** (currently: E014-V1 only).
- A mechanism that has **survived its own predeclared controls** in a completed Discovery pass (i.e.
  the primary result, not a control that merely revealed a *different* generic pattern — see §3's
  distinction between "unsupported primitive" and "candidate conditioning variable").
- **Independently motivated market structure** with a stated mechanism hypothesis, registered before
  any data is examined for that specific configuration.
- **Observations already logged in the registry** (`EDGE_DISCOVERY_REGISTRY_v1.md`,
  `CROSS_EDGE_RESEARCH_CANDIDATES.md`), used only for the role classification §3 already assigns them.
- **Explicit hypotheses derived before examining outcomes** — the same Discovery-stage discipline
  already standing in `EDGE_RESEARCH_PROTOCOL.md` §1, extended to configurations.

**Explicitly prohibited, without exception:**
- Unrestricted combinatorial search across contexts, locations, triggers, or filters.
- Selecting a condition, threshold, or filter *because* it improves historical profit or win rate.
- Repeatedly changing a threshold after seeing results and re-running (this is the single most common
  form of overfitting and is banned even when framed as "robustness checking").
- Testing large numbers of configurations and reporting only the winners (this protocol's §8 requires
  every attempted configuration to be logged, win or lose, before any is reported).
- Silently dropping a regime, time window, or subsample that performs poorly without disclosing it was
  tried and removed.
- Post-hoc entry or stop placement — i.e. choosing where the "entry" or "stop" would have been after
  seeing how the trade played out. Entry and stop rules must be statable from information available
  strictly before or at the entry bar.

---

## 5. Minimal configuration principle

Every candidate configuration **begins with the smallest defensible combination** consistent with its
own source primitive's frozen definition — typically just the primitive itself plus the single trigger
that converts it into a directional prediction (e.g. for E014-V1: *compression event + breakout
trigger*, nothing else).

```
Primitive A + Trigger B                     <- START HERE

Primitive A + Trigger B + Session C
Primitive A + Trigger B + Regime D
Primitive A + Trigger B + Indicator E
Primitive A + Trigger B + Filter F           <- ONLY reached by satisfying the gate below
```

An additional condition (context, session, regime, indicator, or filter) may be added on top of the
minimal configuration **only when all three hold simultaneously**:
1. The simpler configuration was evaluated and **failed in a clearly diagnosed way** (not merely
   "underperformed slightly" — the diagnosis must identify *why*, e.g. "expectancy is negative
   specifically because losing trades cluster in high-volatility regimes").
2. The proposed new condition has an **independent mechanism hypothesis** — a reason it should matter,
   stated without reference to the specific historical trades that motivated adding it.
3. The addition is **registered in the configuration schema (§2) before evaluation**, not adjusted
   afterward.

Violating any one of the three turns the exercise into a search for a profitable filter, which §4
explicitly prohibits.

---

## 6. Trading evaluation (direct trade simulation)

Every candidate configuration, once specified via the §2 schema, must be evaluated by direct,
deterministic trade simulation with all of the following made explicit **before** the simulation is
run:

- Deterministic entry (§1).
- Deterministic stop (§1).
- Deterministic 2R target (or the justified alternative RR, §2).
- Spread, commission, and slippage assumptions (disclosed estimates, not fit to the sample).
- Same-bar ambiguity policy (if one bar's range touches both stop and target, the same
  tie-break-to-AMBIGUOUS convention already standing in `E015-SCALP_protocol_and_pilot.md` applies by
  default unless a configuration states a different, equally disclosed policy).
- Gap policy (how a price gap through the stop or target level, if the data resolution can show one,
  is resolved — worst-reasonable-fill by default, disclosed if otherwise).
- Maximum holding horizon (§1).
- Overlapping-trade policy (whether a new signal while a position is open is skipped, queued, or
  allowed to pyramid — skip-while-open is the default unless justified otherwise).

**Required minimum report for every simulated candidate** (win or lose, always reported in full,
never selectively):
- Number of trades attempted; wins; losses; unresolved (timeout/ambiguous/data-unavailable) trades.
- Win rate.
- Average R and median R (separately — median guards against a single outsized win dominating the
  average).
- **Expectancy in R** (the primary criterion, per §1).
- Profit factor (gross win R / gross loss R).
- Maximum drawdown (in R, over the trade sequence).
- Longest losing streak (count of consecutive losing trades).
- **Percentage of total profit dependent on the single best trade**, and **expectancy recomputed with
  the best trade removed** — a configuration whose entire positive expectancy depends on one outsized
  trade is not robust regardless of its headline number.
- Annual and regime-conditional expectancy distribution (does expectancy hold up year-by-year and
  across volatility/trend regimes, or is it concentrated in one period/regime).

---

## 7. Validation ladder

Distinct, ordered stages. **No configuration may be described as validated, tradable, or reliable
before completing every stage required for its current claim.** A configuration may be reported at
any intermediate stage, but only with that stage's own (limited) status attached.

| Stage | Name | What happens | Exit criterion to advance |
|---|---|---|---|
| 0 | Hypothesis registration | Configuration fully specified via §2 schema, registered, dated, before any data touches it | Schema complete, no required field null |
| 1 | In-sample discovery | Direct trade simulation (§6) on the same clean split used for the source primitive's own Discovery pass | Positive cost-adjusted expectancy; full §6 report produced |
| 2 | Matched and synthetic controls | The same trade simulation re-run against the primitive's own already-established controls (generic/random-matched), converted into trade outcomes rather than raw rates | Real configuration's expectancy exceeds every control's own expectancy, not just its raw event rate |
| 3 | Temporal holdout | Re-run on a time slice not used to shape the Stage 0-2 design — **this requires a fresh, explicit decision on what data serves as this holdout, since the program's existing clean split was already used in the source primitive's own Discovery pass** (see §11's own flagged open question) | Expectancy sign and rough magnitude persist on genuinely unseen data |
| 4 | Walk-forward validation | Rolling train-on-past/test-on-next-slice re-estimation across the full history | Expectancy does not decay or reverse sign as time moves forward |
| 5 | Parameter-neighborhood stability | Re-run at a small number of predeclared, non-optimized neighboring parameter values (e.g. the compression threshold ±5 percentile points) | Expectancy sign is stable across the neighborhood, not a knife-edge at one exact value |
| 6 | Cost and execution stress | Re-run under deliberately worse cost assumptions (wider spread, higher slippage) than the base case | Expectancy remains positive, or the exact cost sensitivity is disclosed if it does not |
| 7 | Cross-regime replication | Re-run separately across volatility and trend regimes already defined by shared infrastructure (`_common.vol_regime`, trend tagging) | Expectancy is not concentrated in a single regime |
| 8 | Shadow / paper-trading validation | Forward, non-live tracking against genuinely new, not-yet-seen data as it arrives | Expectancy holds prospectively, not merely retrospectively |

---

## 8. Multiple-testing control

- **Hypothesis registry before execution**: every configuration is entered into the schema (§2) and
  dated *before* Stage 1 is run — mirroring the same discipline this program already applies to V0
  hypotheses.
- **Fixed number of candidate configurations per batch**: a batch's size is stated in advance (e.g.
  "this batch will evaluate the 3 configurations registered today") before any of them is run — no
  open-ended "keep trying variants until one works."
- **Complete reporting of all tested candidates**: every configuration in a batch is reported per §6,
  including the ones that fail — no selective reporting of winners only.
- **Family-wise or false-discovery-rate correction** applied across a batch's own p-values/expectancy
  significance tests where a formal significance claim is made, exactly as already flagged as an open
  gap in this program's own Discovery-stage p-values (`NEXT_SESSION_FLOW_A.md`).
- **Holdout data untouched during configuration generation**: whatever data is designated the Stage 3
  temporal holdout (§7) is not inspected, summarized, or used to shape any configuration decision
  before Stage 3 is formally reached.
- **No repeated reuse of the same holdout**: once a holdout has been used for a Stage 3 test, it is
  considered spent for that configuration family — a failed Stage 3 does not license trying the same
  holdout again with a tweaked configuration (that configuration must restart at Stage 0 as a new,
  separately-versioned candidate, per this program's own standing "no silent edits to a frozen
  candidate" rule).
- **Separate discovery and confirmation datasets**: Stage 1-2 use the discovery split; Stage 3+ use a
  disjoint confirmation split, never the same rows.

---

## 9. Candidate promotion states

Exact, ordered states. A configuration's `status` field (§2 schema) must always be one of:

1. **REJECTED** — failed Stage 1 or Stage 2 (negative expectancy in-sample, or fails to beat its own
   controls). Terminal for this exact configuration; a materially different configuration is a new,
   separately-registered candidate.
2. **DESCRIPTIVE ONLY** — the underlying primitive is real (per §3) but no configuration built from it
   has yet reached positive Stage 1-2 expectancy, or the finding is explicitly a conditioning-variable
   role, not intended as a standalone trade.
3. **CONFIGURATION DISCOVERY CANDIDATE** — passed Stage 0-2 (positive in-sample expectancy, beats its
   own controls). No claim beyond "worth carrying to Stage 3."
4. **V1 CONFIGURATION CANDIDATE** — passed Stage 0-2 with the same disciplined, non-cherry-picked
   criteria this program's existing V1 candidates require (replication, not explained by controls,
   pre-declared not post-hoc).
5. **VALIDATION CANDIDATE** — passed Stage 3-5 (temporal holdout, walk-forward, parameter-neighborhood
   stability). Still not tradable.
6. **VALIDATED EDGE** — passed Stage 6-8 (cost stress, cross-regime replication, shadow/paper
   validation). Only a VALIDATED EDGE may be discussed as an input to Flow B (`ai_trader/`) — and even
   then, per the two-flow separation, that handoff is itself a separate, explicit governance decision,
   not automatic.

**A high in-sample win rate is insufficient for any promotion beyond CONFIGURATION DISCOVERY
CANDIDATE.** Promotion past that state requires positive cost-adjusted expectancy (§1) *and*
robustness (§1) demonstrated at the corresponding stage — not point-estimate profitability alone.

---

## 10. Relationship with existing Alpha work

- **E005, E006, E008, E011, and E027 remain closed.** Their V0 NOT SUPPORTED verdicts are not
  reversed, reopened, or reinterpreted by this document.
- **E014 remains the only current V1 Discovery Candidate** in the program, per explicit CEO
  confirmation. E015's own "unfrozen V1 candidate" note predates this protocol's stricter
  freezing/Discovery-Identity convention and is not elevated by this document (see §3's classification
  table).
- **Existing null findings are retained as negative knowledge** — they inform which primitives are
  *not* eligible configuration sources (§4) and are never silently repackaged as a positive setup.
- **This protocol changes future research design only.** It adds no new requirement to, and removes no
  standing requirement from, any already-closed edge's own governance record.

---

## 11. First pilot recommendation (proposal only — NOT executed, NOT tested)

**Configuration ID (proposed)**: `E014-CFG-001`. **Status**: Stage 0 (hypothesis registration) only,
by this document. No simulation has been run.

This is offered as the single most-justified starting point for configuration construction, precisely
*because* E014-V1 is the program's only frozen V1 Discovery Candidate — not because it is expected to
succeed. **E014 is not yet a tradable edge. This proposal does not change that.**

| Schema field | Proposed value (unevaluated) |
|---|---|
| Derived from | E014-V1 (Compression-Driven False-Breakout Fade), frozen contract in `E014_inside_bar_false_breakout.md` |
| Higher-timeframe context | None in this first, minimal version — per §5's minimal-configuration principle, no HTF filter is added until the unconditioned version has been evaluated and diagnosed |
| Market regime | Unconditioned ("any") in this first version, for the same reason |
| Session/time window | Unconditioned ("any") — E014's own Discovery pass found no robust session dependency to justify one |
| Structural location (compression event) | Exactly E014-V1's own frozen definition: a bar in the lowest tercile of (range / same-bar ATR14), using the already-frozen thresholds (M15 ≤0.7356, H1 ≤0.6911, H4 ≤0.6929) — reused verbatim, not re-derived |
| Trigger | A close beyond the compression bar's own range (breakout), exactly E014's own frozen breakout definition |
| Entry | Market entry in the FADE direction (opposite the breakout) at the breakout bar's own close — the standard "fade the false breakout" construction, directly justified by what E014-V1 actually measured (a subsequent close back through the opposite boundary), rather than waiting for that confirmation to occur (which would forgo most of the move) |
| Stop loss | Beyond the breakout bar's own extreme (the far side of its wick), plus a small disclosed buffer in the same style as `E015-SCALP_protocol_and_pilot.md`'s own convention (`max(2×spread, 0.05%×entry_price)`) |
| Take profit | Entry ± 2R (target RR = 1:2, the protocol default; no justification yet exists for a different ratio) |
| Maximum holding time | 50 bars — reused directly from E014-V1's own frozen response horizon, for continuity with the primitive it is built from |
| Cancellation conditions | None beyond the stop/target/horizon themselves in this minimal version |
| Controls (Stage 2) | The same three controls E014-V1 was itself tested against (generic single-bar, generic-bar-vs-random baseline already ruled out at the primitive level, and the random-matched synthetic baseline), each converted into the identical trade structure above and simulated the same way |
| Validation sequence proposed | Stage 0 (this table) → Stage 1 (in-sample simulation on the same clean split E014's Discovery pass used) → Stage 2 (control comparison, trade-outcome form) → Stage 3 (temporal holdout — **flagged as an open question below**) → Stages 4-8 only if Stage 3 is passed |

**Unresolved decision, flagged explicitly, not decided by this document**: E014's own Discovery pass
already used the entire pre-holdout-cutoff clean dataset (2022-12-16 to 2025-10-23) in-sample. A
genuine Stage 3 temporal holdout for this configuration therefore has no untouched data available
under the current split — advancing this configuration past Stage 2 requires either (a) a fresh,
CEO-authorized decision on how to carve out a genuine confirmation split from the existing clean data
(at the cost of shrinking the Stage 1-2 discovery sample), or (b) waiting for new data to accrue past
the current cutoff, or (c) some other resolution the CEO specifies. **This document does not propose
an answer — it surfaces the question because Stage 3 cannot proceed without one.**

---

## 12. Decision gates

At each evaluation point, exactly one of the following actions is taken — never an ad hoc mixture:

- **Reject** the configuration outright when: Stage 1 expectancy is negative and clearly not an
  artifact of an obviously mis-specified cost assumption, or Stage 2 shows the configuration performs
  no better than its own random-matched control.
- **Simplify** the configuration (strip a condition back out) when: a more complex version
  underperforms a simpler version already in the validation ladder, and no independent mechanism
  hypothesis justified the removed condition in the first place.
- **Add exactly one condition** when: the current configuration failed in a *clearly diagnosed* way
  (§5), a new condition has an independent, pre-registered mechanism hypothesis, and the addition is
  logged in the schema before re-evaluation — never more than one condition added per iteration, so
  the effect of each addition can be attributed.
- **Stop the family entirely** when: two or three independently-motivated simplifications/additions in
  a row all fail to produce positive Stage 1 expectancy, indicating the underlying primitive likely
  does not convert into a tradable configuration at all (distinct from "needs one more filter").
- **Advance to the next validation stage** when: the current stage's own exit criterion (§7 table) is
  met in full, not partially.
- **Return to primitive discovery** when: the configuration-construction process itself surfaces a
  *new*, previously-unstudied primitive (e.g. a conditioning variable that looks structurally
  interesting on its own) — that primitive is spun out as its own, separately-registered Discovery-stage
  question under `EDGE_RESEARCH_PROTOCOL.md`, not folded into the configuration under construction.

---

## Important constraints (restated from the authorizing CEO decision, binding)

- **Do not optimize for a win rate above 50%.** At RR = 1:2, positive expectancy after costs is the
  target, not a majority win rate.
- **Do not assume every primitive must win more often than it loses.** The worked example: 40% wins,
  60% losses, average win +2R, average loss −1R → gross expectancy `0.40×2 − 0.60×1 = +0.20R` per
  trade, positive despite losing most trades. Expectancy, not win rate, is the criterion throughout
  this protocol.
- No implementation has occurred. No configuration search has been run. No new edge candidate has been
  generated. E016 and E013 have not been started. No prior scientific verdict has changed.
