# AI_TRADER_NEGATION_LIBRARY_V1

**Mandate:** `AI_TRADER_FAILURE_ENGINEERING_V1`, §8/§12/§17/§25. **RESEARCH ONLY. No runtime
integration. No Market Intelligence changes. No Strategy Router changes. No rule below may be
called VALIDATED under this mandate.** Every candidate arose from a repeated failure mechanism
identified in `AI_TRADER_FAILURE_ENGINEERING_REPORT_V1.md` *before* its counterfactual economic
effect (§ below) was computed — thresholds were not chosen after seeing which one looked best.

---

## NEG-P007-001 — Thin-margin reclaim negation

```
NEGATION_RULE_ID       = NEG-P007-001
NAME                   = Thin-margin PATTERN-007 reclaim negation
FAILURE_MECHANISM      = A PATTERN-007 reclaim (close back above H1 EMA50 confirmed) that clears the
                          EMA by a razor-thin margin appears more prone to an almost-immediate
                          (within 1 bar / ~15min) re-break than a decisive-margin reclaim.
APPLICABLE_SETUP_TYPES = Any hypothetical trade or decision that treats a PATTERN-007 reclaim as a
                          resolved, actionable event (e.g. "reclaim confirmed -> resume WITH-trend
                          bias").
PRECONDITIONS          = A PATTERN-007 instance is in progress (price closed below both a defended
                          structural level and H1 EMA50 confirmed) and a candidate reclaim bar has
                          just closed.
OBSERVABLE_CONDITION   = |close - H1_EMA50_confirmed| at the reclaim bar's close is below
                          approximately 0.2 price points (~2 project pips) — i.e. the reclaim margin
                          is at or near noise level relative to the confirmed EMA value.
TIMEFRAME              = M15 (the reclaim bar itself), against H1-confirmed EMA50.
DECISION_TIME          = At the close of the candidate reclaim bar, before the next bar is revealed.
REASON_FOR_CAUSALITY   = A margin this thin is close to the EMA's own bar-to-bar update noise; a
                          genuine directional reassertion should plausibly clear the level with more
                          conviction. This is a stated hypothesis about margin-as-signal, not a
                          proven mechanism.
EXPECTED_FAILURE_PREVENTED = Acting on a reclaim that is about to immediately re-fail (whipsaw).
KNOWN_COUNTEREXAMPLES  = The 09-30-1159 instance reclaimed on a margin of ~0.06pt (thinner than the
                          0.2pt threshold) and HELD (did not re-break within the observed window) —
                          a direct counterexample to a naive "any thin margin fails" reading.
CONDITIONS_WHERE_RULE_MUST_NOT_APPLY = Instances where the reclaim bar itself carries elevated
                          volume/activity (not systematically tested here — flagged as an open
                          refinement, not resolved).
EVIDENCE_N             = 3 thin-margin reclaim instances observed this quarter (09-24-1759,
                          09-25-0514, 09-30-1159); 2 of 3 re-broke within 1 bar.
INDEPENDENT_EPISODES   = All 3 instances occur within the single 09-24/09-25/09-30 window of the
                          same continuous advancing-trend episode that the entire PATTERN-007 record
                          sits inside — NOT independent episodes in the regime sense.
REGIME_COVERAGE        = Single regime only (same `INDEPENDENCE_LIMITATION` that applies to
                          PATTERN-007 as a whole).
STATUS                 = NEGATION_CANDIDATE_UNVALIDATED
EVIDENCE_GRADE          = C (retrospective hypothesis, weak evidence — n=3, one direct
                          counterexample, single regime, 2 of the 3 supporting instances have a
                          disclosed pre-classification-compromise caveat on their *detection*
                          though not on the underlying market behavior)
```

**Counterfactual application to realized AI Trader trades (§12):** **N/A / TRADES_BLOCKED = 0.** No
Q2 or Q3 trade was entered on a PATTERN-007 reclaim thesis — this candidate has no historical
apprenticeship trade to test against. Its only evidence base is the PATTERN-007 observational record
itself (Corpus Bucket B/E), not the trade record.

---

## NEG-P007-002 — Repeated-test degraded-floor negation

```
NEGATION_RULE_ID       = NEG-P007-002
NAME                   = Repeated structural-floor-breach degradation negation
FAILURE_MECHANISM      = A structural level that has already been breached multiple times within
                          the same advancing episode carries progressively less defended
                          significance — treating a further breach of it as still-meaningful
                          structure risks misreading eroded liquidity as fresh information.
APPLICABLE_SETUP_TYPES = Any decision that uses the 1907.066 structural floor (or, by extension, any
                          level with a similar repeated-breach history) as a defended reference point
                          for a trade thesis.
PRECONDITIONS          = The level in question has already been breached at least twice within the
                          same continuous episode.
OBSERVABLE_CONDITION   = Count of prior close-based breaches of the specific level, within the
                          current continuous episode, is >= 2 at decision time.
TIMEFRAME              = H4/M15 (level defined at H4 structural scale, breach detection at M15
                          close).
DECISION_TIME          = At the moment a new approach toward the level is being evaluated.
REASON_FOR_CAUSALITY   = A commonly-cited market-structure mechanism: each defense of a level
                          consumes some of the resting liquidity/orders that made it "defended" in
                          the first place; repeated tests are consistent with progressive
                          exhaustion. Stated as a working hypothesis, not established causally in
                          this record (identical caveat to PATTERN-007's own `WHY_IT_MAY_EXIST`
                          field in `GOLD_BEHAVIOR_MODEL_V1.md`).
EXPECTED_FAILURE_PREVENTED = Treating a well-worn, no-longer-meaningfully-defended level as if it
                          were still fresh structure.
KNOWN_COUNTEREXAMPLES  = Every breach of the 1907.066 floor observed so far has STILL eventually
                          produced a bounce (no instance has yet resolved as a clean breakdown) —
                          i.e. the floor has degraded in *magnitude of significance*, not (yet) to
                          zero. This rule would currently only ever downgrade confidence, never
                          flip a directional read.
CONDITIONS_WHERE_RULE_MUST_NOT_APPLY = A genuinely new, previously-untested level should not inherit
                          this discount merely by proximity to 1907.066.
EVIDENCE_N             = 5 distinct AMBIGUOUS-instance breaches of the same level (08-10, 08-24,
                          09-07, 09-21, 09-25) plus 7 additional breaches within the single 09-21
                          episode alone (12 total breach events on one level).
INDEPENDENT_EPISODES   = All within the single continuous advancing episode — same
                          `INDEPENDENCE_LIMITATION` caveat as NEG-P007-001.
REGIME_COVERAGE        = Single regime only.
STATUS                 = NEGATION_CANDIDATE_UNVALIDATED
EVIDENCE_GRADE          = C (plausible, repeatedly-observed depth trend, but n at the *episode* level
                          is small [5 distinct episodes] and entirely single-regime; the mechanism
                          itself is a stated hypothesis, not demonstrated causally)
```

**Counterfactual application to realized AI Trader trades (§12):** **N/A / TRADES_BLOCKED = 0.**
Same reasoning as NEG-P007-001 — no realized trade used this level as a thesis input.

---

## NEG-TRD-001 — H1 EMA slope-not-yet-confirmed negation

```
NEGATION_RULE_ID       = NEG-TRD-001
NAME                   = Unconfirmed H1 EMA slope negation
FAILURE_MECHANISM      = An entry taken when the H1 EMA(50) has crossed price but its SLOPE has not
                          yet been independently confirmed in the trade's direction may be accepting
                          a false continuation.
APPLICABLE_SETUP_TYPES = M15 WITH-trend entries relying on an H1 EMA cross as part of the
                          alignment read.
PRECONDITIONS          = H1 EMA(50) has crossed price in the trade's intended direction.
OBSERVABLE_CONDITION   = H1 EMA(50) slope is not yet independently confirmed FALLING (for a short)
                          or RISING (for a long) at entry time — i.e. the cross exists but the slope
                          confirmation field is not yet satisfied.
TIMEFRAME              = H1 (slope), M15 (entry trigger).
DECISION_TIME          = At the moment of entry.
REASON_FOR_CAUSALITY   = A crossed-but-not-yet-sloping EMA is consistent with an EMA lagging a
                          temporary price excursion rather than confirming a genuine change in
                          higher-timeframe character — this is exactly the distinction the Q2-era
                          "Multi-Timeframe Trend Alignment" correction was built to capture.
EXPECTED_FAILURE_PREVENTED = Accepting a false continuation shortly after an H1 EMA cross, before the
                          slope itself confirms.
KNOWN_COUNTEREXAMPLES  = **Q3-002** is a direct, immediate counterexample to this rule's sufficiency
                          — it is the strictest-possible test (slope WAS independently confirmed
                          FALLING, the first such instance of the quarter) and it STILL lost
                          (−1.120R). Requiring slope confirmation does not, on this evidence, make an
                          entry safe — it only removes one specific failure mode (Q3-001's), not
                          losses in general.
CONDITIONS_WHERE_RULE_MUST_NOT_APPLY = Not established — insufficient n to characterize exceptions.
EVIDENCE_N             = 1 supporting instance (Q3-001, slope unconfirmed, lost within 30min) + 1
                          direct contrast instance (Q3-002, slope confirmed, also lost). This is
                          the entire checkable evidence base — the per-trade slope-confirmation
                          sub-field is not separately logged for the Q2 #57-66 trades in the
                          retained record, so this rule cannot currently be evaluated against Q2 at
                          all.
INDEPENDENT_EPISODES   = 2 (both Q3, one week apart, same continuous macro episode as everything
                          else in this apprenticeship).
REGIME_COVERAGE        = Single regime, n=2.
STATUS                 = ANECDOTAL_NEGATION
EVIDENCE_GRADE          = C
```

**Counterfactual application to realized AI Trader trades (§12), among the 2 checkable instances
only (Q2 cannot be evaluated — field not logged):**

```
TRADES_BLOCKED               = 1  (Q3-001 only; Q3-002 had slope confirmed, rule does not fire)
LOSSES_BLOCKED                = 1  (Q3-001, −1.084R)
WINNERS_BLOCKED                = 0
NET_R_REMOVED                  = +1.084R (i.e. removing this loss improves the checkable subset)
NET_PROJECT_PIPS_REMOVED       = +38.00 pips
GOOD_TRADES_WRONGLY_BLOCKED    = 0
MISSED_OPPORTUNITIES_WORSENED  = none identified
NO_TRADE_QUALITY_IMPROVED      = unclear — n=2 is too small to claim an improvement in general
                                  NO_TRADE quality; this only shows the rule did not misfire on its
                                  one contrast case (there was no contrast case to misfire on, since
                                  Q3-002 does not trigger the rule at all).
```

**Per §12, this result is reported without retuning.** The rule is NOT rejected outright (it did
correctly flag its one applicable instance and never wrongly blocked a winner), but it is graded no
higher than C and explicitly NOT proposed for independent falsification (§17 requires Grade B+ for
that) because n=1 supporting instance is not a "repeated mechanism" by any reasonable reading of
§3's requirement, and the Q2 trade set cannot even be checked against it.

---

## NEG-TRD-002 — CONFLICTED MTF alignment negation (reported for completeness, not proposed further)

```
NEGATION_RULE_ID       = NEG-TRD-002
NAME                   = CONFLICTED multi-timeframe alignment negation
FAILURE_MECHANISM      = An entry taken with M15-confirmed direction structurally opposed by H1/H4
                          context (explicitly tagged CONFLICTED at entry) may be fighting a live
                          higher-timeframe process rather than confirming a fade of it.
APPLICABLE_SETUP_TYPES = Any entry where MTF_ALIGNMENT is disclosed as CONFLICTED.
PRECONDITIONS          = M15 structure confirms one direction while H1/H4 context is structurally
                          opposed.
OBSERVABLE_CONDITION   = MTF_ALIGNMENT field = CONFLICTED at entry (already an existing, disclosed
                          category in this apprenticeship's own governance — not a new field).
TIMEFRAME              = H4/H1 vs. M15.
DECISION_TIME          = At entry.
REASON_FOR_CAUSALITY   = The higher timeframe carries more standing liquidity/participation; a
                          disclosed conflict means the trade is betting the lower timeframe
                          overrides the higher one, which is the harder side of that bet on priors.
EXPECTED_FAILURE_PREVENTED = The H1/macro context reasserting against the M15 entry.
KNOWN_COUNTEREXAMPLES  = None observed — but only because n=1 (Q3-005 is the only CONFLICTED-tagged
                          entry in the entire retained trade record).
CONDITIONS_WHERE_RULE_MUST_NOT_APPLY = Not established.
EVIDENCE_N             = 1 (Q3-005).
INDEPENDENT_EPISODES   = 1.
REGIME_COVERAGE        = Single instance, single regime.
STATUS                 = ANECDOTAL_NEGATION
EVIDENCE_GRADE          = C, and explicitly at the floor of even that — n=1 is not evidence of a
                          repeated mechanism, it is a single disclosed, honestly-tagged decision
                          that happened to lose. Included here only because the mandate requires
                          every identified candidate to be reported, not because it clears any
                          meaningful bar.
```

**Counterfactual application:** `TRADES_BLOCKED = 1` (Q3-005), `LOSSES_BLOCKED = 1` (−1.123R),
`WINNERS_BLOCKED = 0`. Reported for completeness; **not carried forward past this document** — n=1
does not meet the bar for further proposal under §17.

---

## Summary

```
NEGATION_RULES_PROPOSED         = 4  (NEG-P007-001, NEG-P007-002, NEG-TRD-001, NEG-TRD-002)
NEGATION_RULES_GRADE_B_OR_HIGHER = 0
NEGATION_RULES_REJECTED          = 0  (none rejected outright — all remain UNVALIDATED/ANECDOTAL,
                                    none disqualified by a counterexample that blocked a winner)
BEST_NEGATION_RULE (best-evidenced, not "best performing") = NEG-P007-002 (repeated-test floor
                                    degradation) — largest event count (12 breach events across 5
                                    episodes) of any candidate, though still Grade C and single-regime
```

**No candidate here clears Grade B.** Per §25 of the mandate, none is prepared as a
`TRADER_NEGATION_CANDIDATE_<ID>` handoff package for Alpha/Statistician — that gate requires
genuinely promising evidence, which this pass did not produce. This is stated plainly rather than
inflating a Grade-C hypothesis into a handoff-worthy candidate to have something to hand off.

See `AI_TRADER_STRATEGY_READINESS_DIAGNOSTIC_V1.md` for what this result implies about where the
apprenticeship's real leverage currently is.
