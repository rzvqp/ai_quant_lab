# AI_TRADER_MANAGEMENT_POLICY_LIBRARY_V1

**Mandate:** `AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1`, §6/§12/§20. **RESEARCH ONLY. No runtime
integration. No live/demo execution change. No status below may be called VALIDATED.** Built from
`AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md`.

---

## POLICY-0 — Original static baseline

```
STATUS = N/A (not a candidate, the reference point every other policy is measured against)
```

---

## POLICY-1 — TP1 bank (40%) + breakeven

```
POLICY_ID          = POLICY-1
NAME                = TP1 bank + breakeven
MECHANISM           = Bank 40% of position size at a genuine, already-frozen TP1; move remaining
                       stop to breakeven only after TP1 is actually reached; preserve remaining
                       structural targets unchanged.
APPLICABLE_TRADES   = Only trades with a genuine, already-frozen TP1 level (#65, #66, Q3-002 in the
                       primary population; Q3-003, Q3-004 in the secondary population).
TRIGGER_CONDITION   = Price closes at or through the frozen TP1 level.
OBSERVED_TRIGGERS   = 0 of 5 applicable trades ever reached TP1 (verified individually — #65 closest
                       8.296pts short; #66 closest 0.006pt short per the checkpoint account, or
                       "never meaningfully favorable" per the conflicting log account, either way
                       never closed through; Q3-002 MFE 0.752R vs. TP1 at 5.434R; Q3-003 wick 0.36pt
                       short, never closed through; Q3-004 ~5 pips short).
STATUS              = MANAGEMENT_NOT_SUPPORTED — not because the mechanism is flawed, but because it
                       has zero observed triggers in the entire retained Q1-Q3 record. There is no
                       evidence either for or against this policy's economic effect; there is only
                       evidence that it would have changed nothing so far.
EVIDENCE_N          = 0 triggered instances (5 applicable trades, 0 activations)
```

---

## POLICY-2 — TP1 bank (40%) + structural trail

```
POLICY_ID          = POLICY-2
NAME                = TP1 bank + structural trail
MECHANISM           = Same TP1 trigger as POLICY-1; remaining 60% managed via a causal structural
                       trail (no arbitrary fixed-pip trailing) rather than a static breakeven stop.
APPLICABLE_TRADES   = Same 5 trades as POLICY-1.
TRIGGER_CONDITION   = Same as POLICY-1 (TP1 reached) — this policy only differs from POLICY-1 in what
                       happens to the remaining 60% AFTER that trigger, so it inherits the same
                       zero-trigger outcome.
OBSERVED_TRIGGERS   = 0 of 5 applicable trades.
STATUS              = MANAGEMENT_NOT_SUPPORTED (identical reasoning to POLICY-1 — no trigger, no
                       evidence either direction)
EVIDENCE_N          = 0
```

---

## POLICY-3 — TP1 (40%) + TP2 (30%) + final structural (30%)

```
POLICY_ID          = POLICY-3
NAME                = Full 40/30/30 framework
MECHANISM           = 40% at TP1, 30% at TP2, 30% trailing/final structural target — the framework
                       currently preferred by this apprenticeship's own standing methodology.
APPLICABLE_TRADES   = Trades with a genuine TP1 AND TP2 (only Q3-002 in the primary population has a
                       genuine 2-way split, though 50/50 not 40/30/30; Q3-005 is the sole trade in
                       the ENTIRE retained record specified as literal 40/30/30, and it is excluded
                       from this study for lack of MFE/MAE evidence).
TRIGGER_CONDITION   = TP1 reached (first stage).
OBSERVED_TRIGGERS   = 0 (same reasoning as POLICY-1/2 — TP1 was never reached in any applicable
                       trade; Q3-005, the only literal 40/30/30 specification anywhere in the record,
                       stopped out before ever approaching TP1).
STATUS              = MANAGEMENT_NOT_SUPPORTED — with the important caveat that this verdict means
                       "not supported by any observed trigger yet," not "refuted." See
                       `AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md` §6 for the full 40/30/30 audit —
                       the honest verdict there is `INSUFFICIENT_EVIDENCE` for the framework as a
                       whole (it has simply never been tested by a live trade reaching TP1), while
                       this specific counterfactual-application pass is `MANAGEMENT_NOT_SUPPORTED`
                       in the narrower sense of "produced zero differentiated effect on this Q1-Q3
                       dataset."
EVIDENCE_N          = 0
```

---

## POLICY-4 — MFE-giveback protection (breakeven-move at +1.0R)

```
NEGATION/MANAGEMENT_RULE_ID = MGMT-004
NAME                = MFE-giveback breakeven protection
FAILURE_MECHANISM   = A trade that reaches +1.0R favorable excursion and then retraces to breakeven
                       is, in this sample, allowed to continue all the way to the original stop
                       under the current no-management-change methodology, converting a genuinely
                       useful entry into a full-size realized loss.
APPLICABLE_SETUP_TYPES = Any trade under the current fixed-SL / no-partial-capture methodology (both
                       the "no fixed target, hold-or-trail" style of #57-64 and the "single frozen
                       TP" style of #65/#66 — this policy does not require a TP1 to exist at all,
                       unlike POLICY-1/2/3).
PRECONDITIONS       = A position is open with a defined initial stop and entry price (R is
                       computable).
OBSERVABLE_CONDITION = Price first closes at or beyond +1.0R favorable excursion from entry.
TRIGGER             = The first M15 close at or beyond +1.0R.
DECISION_TIME       = At that bar's close.
STOP_CHANGE          = Move the stop to exactly the entry price (breakeven, 0R). No partial exit, no
                       change to any remaining structural target.
REASON_FOR_CAUSALITY = 1.0R is the single most standard, textbook breakeven-trigger convention in
                       discretionary risk management, independent of this dataset — pre-registered
                       for that reason, not fit to the data.
EXPECTED_FAILURE_PREVENTED = A trade that has already proven the entry thesis directionally correct
                       (by reaching 1.0R) fully round-tripping into a realized loss.
KNOWN_COUNTEREXAMPLES = None within the primary population that would REVERSE the policy's net
                       effect — no winner is ever touched (§`AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md`
                       §4). The weakest point is evidentiary concentration, not a counterexample: all
                       4 supporting instances are Q2, SHORT-only, single-regime.
CONDITIONS_WHERE_RULE_MUST_NOT_APPLY = Not established from current evidence — no LONG-trade or
                       Q3-trade instance exists to test whether the rule behaves differently there.
EVIDENCE_N           = 4 triggered instances (of 12 primary trades), all converted from a realized
                       loss to exactly breakeven.
INDEPENDENT_EPISODES = 4, but NOT independent in the regime sense — all 4 sit inside the same
                       continuous single H4-BEARISH-tagged episode as every other piece of evidence
                       in this apprenticeship (the same `INDEPENDENCE_LIMITATION` that applies to
                       PATTERN-007).
REGIME_COVERAGE      = Single regime, SHORT-direction only, Q2-quarter only.
ROBUSTNESS           = Leave-one-out: sign never flips on any single-trade removal (§`AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md`
                       §8). Session spread: 3 distinct sessions among the 4 triggers (not
                       single-session-concentrated).
STATUS               = MANAGEMENT_CANDIDATE_UNVALIDATED
EVIDENCE_GRADE        = B — historical, repeated mechanism (n=4, non-sign-flipping under
                       leave-one-out) with a clear ex-ante observable (a standard convention, not
                       mined from this data) — not independently validated (no Q3, LONG, or
                       out-of-regime confirming instance exists). This clears Grade B specifically
                       because, unlike every Grade-C entry-side candidate in
                       `AI_TRADER_NEGATION_LIBRARY_V1.md`, it satisfies all 8 of the mandate's own
                       §20 success-gate conditions (7 fully, 1 partially — see the research report).
```

**`MANAGEMENT_CANDIDATE_READY_FOR_Q4_FORWARD_TEST = YES`** — this is the ONE candidate from either
Failure Engineering V1 or this mandate that clears enough of its own evidentiary bar to warrant a
frozen prospective protocol. It remains **UNVALIDATED** — clearing the discovery-stage gate is not
validation, and Q4 forward evidence (once separately authorized) is required before any stronger
status could ever be considered.

---

## Summary

```
POLICIES_TESTED                    = 5 (POLICY-0 baseline + POLICY-1/2/3/4)
POLICIES_WITH_ZERO_OBSERVED_TRIGGER = 3 (POLICY-1, POLICY-2, POLICY-3 — all MANAGEMENT_NOT_SUPPORTED
                                      for lack of any trigger, not for a negative economic result)
POLICIES_WITH_A_TESTABLE_EFFECT     = 1 (POLICY-4)
BEST_POLICY                         = POLICY-4 / MGMT-004
BEST_POLICY_STATUS                  = MANAGEMENT_CANDIDATE_UNVALIDATED
```

See `AI_TRADER_Q4_MANAGEMENT_PROSPECTIVE_PROTOCOL_V1.md` for the frozen, not-yet-authorized forward
test of POLICY-4/MGMT-004.
