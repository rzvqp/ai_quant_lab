# AI_TRADER_FAILURE_ENGINEERING_REPORT_V1

**Mandate:** `AI_TRADER_FAILURE_ENGINEERING_V1`, §§6-13. Builds on `AI_TRADER_FAILURE_CORPUS_V1.md`.
Taxonomy first, thresholds/economics never chosen after seeing which one looks best. Q1/Q2/Q3
checkpoints not modified; Q4 not touched; S5/MI/ve_brain not touched.

---

## 1. Bad trade vs. normal loss — every realized loss, individually classified

Per §9 of the mandate: a losing trade is `BAD_TRADE` only if the *pre-entry observable state*
already contained evidence that should reasonably have caused abstention. Otherwise it is
`GOOD_TRADE_NORMAL_LOSS`. No Negation Rule is proposed for category B losses.

| ID | Classification | Failure taxonomy tag(s) | Reasoning |
|---|---|---|---|
| Q2 #57 | `GOOD_TRADE_NORMAL_LOSS` | `NORMAL_STATISTICAL_LOSS` | FULLY_ALIGNED, countertrend-spike-exhaustion thesis reasoned and disclosed at entry; no pre-entry disqualifying condition found |
| Q2 #59 | `GOOD_TRADE_NORMAL_LOSS` | `MANAGEMENT_FAILURE` (not entry) | Entry FULLY_ALIGNED; the loss originates from a discretionary trail-flip *after* entry, not from anything observable before entry |
| Q2 #60 | `GOOD_TRADE_NORMAL_LOSS` | `NORMAL_STATISTICAL_LOSS` | FULLY_ALIGNED; stop hit with a real 2.458pt overshoot on the bar's own extension — ordinary variance |
| Q2 #61 | `GOOD_TRADE_NORMAL_LOSS` | `NORMAL_STATISTICAL_LOSS` | FULLY_ALIGNED; stop survived 4 separate tests over 4 bars before triggering — the thesis was contested, not obviously wrong at entry |
| Q2 #62 | `GOOD_TRADE_NORMAL_LOSS` | `NORMAL_STATISTICAL_LOSS` | FULLY_ALIGNED; stop wick-pierced 3x before closing through — same reasoning as #61 |
| Q2 #65 | `GOOD_TRADE_NORMAL_LOSS` | `NORMAL_STATISTICAL_LOSS` | FULLY_ALIGNED, first fixed-SL/TP trade; no disclosed pre-entry defect |
| Q2 #66 | `GOOD_TRADE_NORMAL_LOSS` | `MANAGEMENT_FAILURE` (not entry) | PARTIALLY_ALIGNED at entry but the defining event is a 0.006pt-from-TP reversal — a management/no-partial-capture story, not a pre-entry read failure; the near-miss stop-crossing controversy was correctly *not* used to alter the frozen stop |
| Q3-001 | **`BAD_TRADE`** | `FALSE_BREAK_ACCEPTED_AS_REAL`, `PREMATURE_CONFIRMATION` | PARTIALLY_ALIGNED — H1 EMA had crossed price but its **slope was not yet confirmed FALLING**. This is a pre-entry-observable condition (the slope field existed and was checked, just not required). Reclaimed within 2 bars (30min) — the fastest, cleanest possible disconfirmation of the thesis. This is the corpus's clearest `BAD_TRADE` candidate. |
| Q3-002 | `GOOD_TRADE_NORMAL_LOSS` | `NORMAL_STATISTICAL_LOSS` | The strictest-criteria entry of the quarter (FULLY_ALIGNED, slope confirmed FALLING, 2-bar real-volume confirmation, rejection wick explicitly watched-not-entered-on) — no pre-entry condition available then would have flagged this. Directly falsifies "full alignment ⇒ safe" as a universal rule (see §2 below). |
| Q3-003 | `GOOD_TRADE_NORMAL_LOSS` | `MANAGEMENT_FAILURE` (not entry) | PARTIALLY_ALIGNED, sustained high-volume breakout, retest-and-hold confirmed before entry; wicked to within 0.36pt of TP1 — a no-partial-capture story, not an entry-read failure |
| Q3-004 | `GOOD_TRADE_NORMAL_LOSS` | `MANAGEMENT_FAILURE` (not entry) | PARTIALLY_ALIGNED, independently confirmed by a real ICT displacement pivot; reached ~3.16R unrealized before round-tripping — again a management-structure story (`TARGET_MODE=TP1_ONLY`, no second real level for a partial), not a pre-entry defect |
| Q3-005 | **`BAD_TRADE`** (weak case, disclosed at the time) | `HTF_LTF_CONFLICT`, `LOCAL_PHASE_OPPOSES_HTF_LABEL` | `MTF_ALIGNMENT` was explicitly logged as `CONFLICTED` at entry — M15 confirmed bearish break vs. H1 EMA(50) far below price and macro structurally bullish. The conflict was *known and disclosed*, not undiscovered, but it was a pre-entry-observable condition available to cause abstention and the trade was still taken. Weak case: n=1, and the honest alternative reading is that CONFLICTED trades were never tested as a category to abstain from — see §2. |

**Tally: 12 losses total — 2 candidate `BAD_TRADE` (Q3-001, Q3-005), 10 `GOOD_TRADE_NORMAL_LOSS`.**
Of the 10 normal losses, 4 (Q2 #59, #66, Q3-003, Q3-004) trace to a **management**, not entry,
failure mode — see §3.

---

## 2. Common-denominator analysis (§7 of the mandate)

For every proposed factor, both directions are tested — a factor is not "useful" merely because it
recurs in losses; it must also be checked against winners and correct no-trades.

| Factor | FAILURES_WITH | FAILURES_WITHOUT | WINNERS_WITH | CORRECT_NO_TRADES_WITH | Verdict |
|---|---|---|---|---|---|
| `FULLY_ALIGNED` at entry | 6 of 12 (Q2 #57,59,60,61,62,65) | 6 of 12 | 1 of 3 (Q2 #58) | N/A (no-trades have no entry tag) | **Inverted from the naive hypothesis.** FULLY_ALIGNED is *more* common among losses than among wins in this sample (6/12 vs. 1/3) — directly consistent with the Q2 checkpoint's own disclosed, counterintuitive finding (FULLY_ALIGNED trades had the *worst* win rate, 1W/6L). **Do not build a negation rule that treats FULLY_ALIGNED as protective — the realized evidence points the other way, on a small sample.** |
| `PARTIALLY_ALIGNED` at entry | 5 of 12 (Q2 #66, Q3-001,003,004 + Q2 uses this tag once more is not present — recount: Q2 #66, Q3-001, Q3-003, Q3-004 = 4) | 8 of 12 | 1 of 3 (Q2 #64) | N/A | Present in both losses and the one clearest `BAD_TRADE` (Q3-001) but also in 2 `GOOD_TRADE_NORMAL_LOSS` management-story losses and 1 winner — **not discriminating on its own.** |
| `CONFLICTED` alignment | 1 of 12 (Q3-005) | 11 of 12 | 0 of 3 | N/A | n=1 — cannot support any rule; the only instance was a loss, but this is not "repeated" evidence per the mandate's own §3 requirement |
| H1 EMA slope not-yet-confirmed at entry | 1 of 12 (Q3-001) | 11 of 12 (including Q3-002, which explicitly required and had slope confirmation, and still lost) | 0 of 3 confirmed-present in the checkpoint text | N/A | n=1 present, and its natural contrast case (Q3-002, slope confirmed) still lost — **weak, not zero, evidence; see NEG-TRD-001 in the Negation Library, graded C** |
| MFE ≥ 0.6R without being banked (MFE-giveback) | **7 of 10** fully-evidenced Q2 losses/wins-with-giveback + **3 of 5** Q3 losses reached meaningful MFE before reversing | small remainder | **also present in ALL 3 Q2 wins to some degree** (58: 3.743R MFE, 66% captured; 63: 3.163R, 73% captured; 64: 2.467R, 58% captured) — i.e. even winners under this methodology give back a portion | N/A (no-trades never reach MFE) | **This is the single most repeated, most cross-population pattern in the entire realized-trade corpus** — but it is a **post-entry management** condition, not observable before entry, so it cannot become a Negation Rule under this mandate's own definition (§3: "causally observable PRE-ENTRY condition"). Reported instead as the primary Strategy-Readiness blocker (§18 diagnostic doc). |

**Conclusion of the common-denominator pass:** across n=12 realized losses, **no pre-entry-observable
factor recurs with both (a) meaningful frequency and (b) a genuinely one-sided distribution between
losses and winners.** The two most tempting-looking candidates (full/partial alignment) either point
the *wrong* direction (FULLY_ALIGNED) or are evenly spread across losses, wins, and the one
management-driven loss (PARTIALLY_ALIGNED). The one factor that IS strongly, repeatedly, and
consistently present across both losses and wins is a **post-entry** one (MFE giveback under
no-trailing methodology) and is therefore explicitly excluded from Negation Rule candidacy by the
mandate's own rules, not smoothed into one anyway.

**This is reported as a genuine, if modest, finding: the entry-side realized-trade sample (n=12) does
not currently support any Grade-B-or-higher entry Negation Rule.** Manufacturing one from n=1-2
subsets would violate §16's hard anti-overfitting rules.

---

## 3. Failure taxonomy tallies

| Tag | Count | Trades |
|---|---|---|
| `NORMAL_STATISTICAL_LOSS` | 6 | Q2 #57, #60, #61, #62, #65, Q3-002 |
| `MANAGEMENT_FAILURE` (post-entry, not a negation candidate) | 4 | Q2 #59, #66, Q3-003, Q3-004 |
| `FALSE_BREAK_ACCEPTED_AS_REAL` / `PREMATURE_CONFIRMATION` | 1 | Q3-001 |
| `HTF_LTF_CONFLICT` / `LOCAL_PHASE_OPPOSES_HTF_LABEL` | 1 | Q3-005 |

No loss was forced into a preventable category merely to produce a tidier table — 6 of 12 remain
`GOOD_TRADE_NORMAL_LOSS` / `NORMAL_STATISTICAL_LOSS`, exactly per §6/§9's instruction.

---

## 4. PATTERN-007 failure engineering (§10-11 of the mandate)

**Using the strict-prospective population (n=23: 15/1/7) as primary evidence**, per the mandate.

**Can a discriminator be determined before outcome?** Re-confirmed: **NO** —
`PATTERN_007_DISCRIMINATOR_INSUFFICIENT_EVIDENCE`, unchanged from
`AI_TRADER_Q2_VS_Q3_FORENSIC_REVIEW.md` §14. Most of the CEO-mandated candidate variables
(`BREAK_DEPTH_ATR`, `BREAK_VELOCITY`, `BODY_ATR`, `WICK_BODY_RATIO`, 1/2/4-bar follow-through,
`ACTIVITY_TREND` vs. `ACTIVITY_MAGNITUDE`, `PRICE_PROGRESS_PER_ACTIVITY`, `EXPANSION_STATE`) were
**not systematically captured** at the time each instance was logged in the durable record.
Retroactively computing them now from raw OHLCV, after already knowing every instance's outcome,
would itself be a hindsight-informed reconstruction — explicitly declined, consistent with
`ACTIVE_FALSIFICATION_V1` and the mandate's own §16 ("no same-data discovery and validation").

**What genuinely IS available and repeatedly observed, without needing new computation:**

1. **`TIME_BEYOND_LEVEL` (active-market duration) is continuous, not bimodal** — MIN=0.25h to
   MAX=77.25h with no natural gap (§`AI_TRADER_FAILURE_CORPUS_V1.md` Bucket E). This rules out
   duration-bucket-based rules of the "fast vs. slow" form as a discriminator, since the buckets
   don't naturally separate.
2. **Structural-floor breach count degrades a level's defended significance** — the 1907.066 floor
   was breached across at least 5 distinct AMBIGUOUS instances (08-10, 08-24, 09-07, 09-21, 09-25),
   plus 7 times within the single 09-21 episode alone, and its practical significance visibly eroded
   over the quarter. This is a genuine, repeated, causally-plausible mechanism (repeated tests
   exhaust the level's remaining defended liquidity) — candidate `NEG-P007-002` in the Negation
   Library.
3. **Reclaim-margin thinness and immediate re-failure** — of the 3 sub-~0.2pt-margin reclaims
   observed this quarter (09-24-1759, 09-25-0514, 09-30-1015/0859 cluster — see Corpus Bucket B),
   **2 of 3 re-broke within 1 bar (~15min)** of reclaiming. n=3 is small and 2 of the 3 instances are
   themselves flagged as pre-classification-compromised in `AI_TRADER_Q3_INTEGRITY_AUDIT.md` §3 —
   but the underlying *market behavior* (not the detection method) is real and dated. Candidate
   `NEG-P007-001` in the Negation Library.

**`PATTERN_007_NEW_DISCRIMINATOR_FOUND = NO`. `PATTERN_007_STATUS_CHANGED = NO`** — the pattern
remains `DEVELOPING_PATTERN`, behaviorally real, not tradeable, playbook-not-ready. What changed is
narrower: two specific, evidence-grounded (not manufactured) *negation* hypotheses are now formally
proposed, neither of which is a discriminator for the pattern's SUPPORT/AMBIGUOUS/COUNTEREXAMPLE
classification itself — they are cautionary conditions for *acting on* a reclaim once one occurs.

---

## 5. Alpha negative-evidence cross-check (§13 of the mandate)

**Does the same failure mechanism appear independently in a second, unrelated research mode?**

**YES — whipsaw / double-break / immediate-reversal is independently confirmed.** Alpha's VOLPATH
Phase-1 finding (`SOURCE: -alpha-automation, VOLPATH_PHASE1_REPORT.md, 6092c8f`), derived entirely
independently from AI Trader's own PATTERN-007 work (different data window, different methodology,
different research team/track), states: *"compression→expansion whipsaw-dominant+symmetric (61%
recross≥2, 47% double-break, straddle pays twice)."* This is the same class of behavior — a level
gets crossed, reverses, and re-crosses — that PATTERN-007's thin-margin whipsaw cluster shows at the
individual-instance level. **`CROSS_ALPHA_FAILURE_MECHANISM_CONFIRMED = YES`, for the
whipsaw/double-break mechanism specifically.** Per the mandate's own instruction, this raises
confidence in the *behavioral mechanism being real*, not automatically in any trade rule — neither
AI Trader's nor Alpha's evidence proposes a monetization path for it (VOLPATH's own candidates were
subsequently falsified in Phase-2; PATTERN-007's negation candidates are explicitly cautionary, not
entry signals).

**Secondary, weaker corroboration:** RANGE's own validation history independently and repeatedly
surfaces the same theme — `RANGE_V2_BLIND_PROTOCOL_COMPROMISED` (whipsaw-adjacent protocol failure)
and `MACRO_GENERALIZATION_NOT_SUPPORTED` on the MB3 blind batch — a third, independent research
track (VE/Statistician's RANGE detector) repeatedly failing to generalize cleanly on reclaim/
regime-transition-shaped structures. Not as directly comparable as VOLPATH (different object of
study — a detector's generalization, not a market-behavior claim), so weighted lower, but consistent
in direction.

**No cross-check evidence was found** connecting AI Trader's specific `HTF_LTF_CONFLICT` /
`FALSE_BREAK_ACCEPTED_AS_REAL` entry-side taxonomy tags to any Alpha-committed finding — those
remain apprenticeship-only observations at this evidence density (n=1 each).

---

## 6. What this report does NOT claim

- It does not claim any Negation Rule is validated (none may be, per §8/§16).
- It does not claim the entry-side n=12 sample is large enough to rule out an entry-side
  discriminator existing — only that none is currently evidenced without overfitting.
- It does not claim PATTERN-007 generalizes beyond the single continuous advancing episode it was
  observed in — the `INDEPENDENCE_LIMITATION` from the Q3 forensic review stands unchanged.
- It does not merge Alpha and AI Trader evidence into one combined statistic anywhere — §5's
  cross-check is a mechanism-confidence statement only, per the mandate's explicit instruction.

See `AI_TRADER_NEGATION_LIBRARY_V1.md` for the formal candidate specifications and counterfactual
test results, and `AI_TRADER_STRATEGY_READINESS_DIAGNOSTIC_V1.md` for the blocker assessment and
CEO-facing recommendation.
