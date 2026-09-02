# AI_TRADER_Q4_FINAL_APPRENTICESHIP_AUDIT

**READ-ONLY SYNTHESIS.** No replay was performed to produce this document. No P007/S5/MGMT-004
definitions were changed. All figures below are drawn from the frozen ledgers
(`AI_TRADER_Q4_PATTERN_LEDGER.md`, `AI_TRADER_Q4_TRADE_EVIDENCE_LOG.md`,
`AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md`) as they stood at Q4 completion (bar 5932).

Learning-audit cutoff: **bar 3057 = Q4-P007-035**. Everything at or before Q4-P007-035 is
PREDECLARED_LEARNING. Q4-P007-036 through Q4-P007-089 (54 entries) is FUTURE_TEST_EVIDENCE.

---

## 1-2. Objective and cutoff

Population sizes, verified by independent re-derivation from the frozen ledger (not merely trusted
from the CEO's frozen totals):

```
PRE-3058 (Q4-P007-001..035):    35 entries -- 11 SUPPORT / 24 REJECTED (2 entries, -004/-007, had no
                                 pre-resolution PRE-CLASSIFICATION section and are excluded from
                                 calibration counts, not from status counts)
POST-3057 (Q4-P007-036..089):   54 entries -- 13 SUPPORT / 41 REJECTED
TOTAL:                          89 entries -- 24 SUPPORT / 65 REJECTED
```

11+13=24 and 24+41=65 -- matches the CEO's frozen `P007_SUPPORT=24` / `P007_REJECTED=65` exactly.
This independent cross-check is reported because it is the first evidence in this audit that the
underlying ledger is internally consistent, not because it was assumed.

The three predeclared lessons, stated exactly as given:
1. **partial-vs-full round-trip / retracement-shortfall**
2. **sustained multi-bar volume vs isolated trigger-bar spike**
3. **fresh-extreme evidence as an additional discriminator**

---

## 3-4. Round-trip lesson -- full audit

Claim under test: partial retracement continues to distinguish SUPPORT; near-complete/full/overshoot
round-trip continues to distinguish REJECTED.

Every one of the 54 post-3057 entries was classified using its own resolution-section retracement
figure (or the qualitative equivalent where no percentage was given) against its final STATUS.

```
APPLICABLE_CASES   = 53   (1 entry, Q4-P007-036, had no stated retracement figure -- NOT_APPLICABLE)
CONFIRMATIONS       = 46
COUNTEREXAMPLES     = 7
AMBIGUOUS           = 0   (the 7 counterexamples below are called counterexamples, not ambiguous,
                            because the lesson's own directional claim was violated cleanly, not
                            merely unclear)
```

**Every true counterexample, not hidden:**

| Entry | Retracement | Status | Why it violates the lesson |
|---|---|---|---|
| Q4-P007-045 | ~89% | SUPPORT | Near-complete retracement (the "should be REJECTED" band per the lesson's own logic), yet resolved SUPPORT -- fresh extreme arrived on the very next bar and the reclaim margin was thin, not weak. |
| Q4-P007-055 | ~73% | REJECTED | A genuinely partial retracement (well inside the "should be SUPPORT" range) still resolved REJECTED -- every other component (gap depth, volume, decline magnitude) was thin, and the entry's own resolution reasoning explicitly says this was REJECTED "on overall weakness," not any single dominant signal. |
| Q4-P007-056 | 86% | SUPPORT | High retracement, SUPPORT anyway -- decided by 75-bar duration and chain-continuation context (third consecutive record-low in the -052→053→056 decline), not retracement completeness. |
| Q4-P007-059 | 88% | SUPPORT | Same high-retracement-but-SUPPORT pattern as -045/-056 -- decided by volume sustained across all 15 bars, not the retracement figure. |
| Q4-P007-070 | 87% | SUPPORT | Same %-band, same direction of surprise -- decided by volume landing exactly at the deepest low. |
| Q4-P007-077 | ~37% (LOW) | REJECTED | The CEO's explicitly-flagged "low retracement but weak reclaim" case: retracement was the lowest of the whole post-3057 population (should strongly favor SUPPORT per the lesson) but the reclaim itself barely cleared the causal EMA50 (+0.023pt margin, the thinnest recorded all quarter) and no fresh extreme was present -- a low retracement number alone did not carry the day. |
| Q4-P007-086 | 60% | REJECTED | A genuinely partial (60%) retracement still resolved REJECTED because there was no fresh extreme at all -- partial retracement was necessary-context but not sufficient on its own. |

**Dramatic fresh extreme + full round-trip (explicitly requested, not hidden):** Q4-P007-082 is the
single hardest test case in the entire post-3057 population. It combined the **deepest fresh
extreme of the whole 12-episode defended-floor stretch** (1871.868, 2.47pt below the prior floor)
with the **heaviest and most cleanly-placed volume of that entire stretch** (1937, landing exactly
on the low bar, with a second bar of real follow-through volume before tapering) -- by every other
component this was the single most credible SUPPORT candidate observed all quarter. It still
resolved REJECTED, because the retracement completed to ~100% within 4 bars. This is a
**CONFIRMATION**, not a counterexample, of the round-trip lesson -- but it is the confirmation that
should worry a research department most, because it shows the round-trip signal overriding the
single strongest possible reading of every other signal simultaneously.

**Overshoot cases (>100% retracement, i.e. reclaiming past the pre-episode level):** Q4-P007-042,
044, 047, 051, 054, 060, 063, 066, 067, 068, 073, 074, 076, 079, 081, 084, 085, 087, 088, 089 -- 20
episodes. **All 20 resolved REJECTED, zero exceptions.** This is the single cleanest, most
unambiguous sub-finding of the whole audit.

**A genuine "dead zone" discovered by this audit, not predeclared:** retracements in the
approximate 85-90% band (Q4-P007-045, 046, 056, 059, 070, 071, 072, 075, 083) split roughly evenly
between SUPPORT and REJECTED (045✓SUPPORT, 046✗REJECTED, 056✓SUPPORT, 059✓SUPPORT, 070✓SUPPORT,
071✗REJECTED, 072✗REJECTED, 075✗REJECTED, 083✗REJECTED -- 4 SUPPORT / 5 REJECTED). Outside that
band the lesson is extremely strong (near-100%+ is REJECTED with essentially no exceptions found;
well-under-80% leans SUPPORT far more often than not, subject to the -055/-077/-086 counterexamples
above). The lesson holds as a strong prior, weakens sharply in the 85-90% band, and is never alone
sufficient.

**Marginal reclaim durability** (a question the CEO's own bar-3057-era episode, Q4-P007-040, raised
and which Q4-P007-041 partially answered): -040's own resolution explicitly flagged its reclaim
margin (+0.48pt) as the thinnest of any SUPPORT instance to that point. -041, one instance later,
showed that decline continuing to a deeper low -- the marginal reclaim did not hold as a durable
level shift, it was simply where the *next* P007 instance's own gate origin sat. This question was
raised prospectively but was never independently re-tested a third time with the same explicit
framing anywhere in the remaining 48 post-041 episodes, so per the instructions in Section 7 it is
classified **RETROSPECTIVE_HYPOTHESIS_ONLY**, not confirmed learning.

---

## 5. Volume-persistence lesson

Claim under test: sustained multi-bar volume is more informative than an isolated trigger-bar spike.

This lesson was **only cleanly testable in a small number of the 54 post-3057 episodes** -- most
REJECTED calls in this population were decided by round-trip completeness or fresh-extreme absence,
not by volume character specifically. Reporting only the cases where the entry's own language
cleanly isolates sustained-vs-isolated volume as the deciding or contrasting factor:

**The canonical contrast pair, exactly as the CEO asked for ("massive isolated volume failed" vs
"sustained heavy volume supported a genuine structural episode"):**

- **Q4-P007-058 (REJECTED)**: "MASSIVE, among the heaviest single-bar volumes in the entire Q4
  replay" -- an isolated spike with no fresh extreme, ~97% reabsorbed in 3 bars. Volume magnitude
  alone, decoupled from persistence or a fresh extreme, was insufficient.
- **Q4-P007-059 (SUPPORT)**: the entry's own text explicitly contrasts itself with -058 -- "volume
  stayed sustained and dramatically elevated across the ENTIRE 15-bar episode (not a single
  spike)." 88% partial retracement.

These two episodes fired four bars apart on the calendar (bars 5014 and 5254) and are the cleanest,
most deliberate real-world A/B test of this lesson available in the whole ledger.

**Q4-P007-078 (REJECTED)**: reinforces -058's side of the contrast -- the heaviest volume of the
entire defended-floor stretch (1182) at the origin bar, but it "collapsed immediately and
completely (243, then 316)" with zero follow-through -- an isolated spike, REJECTED.

**Counterexample, not hidden:** **Q4-P007-040 (SUPPORT)** is a genuine complication. Its trigger was
an isolated, violent capitulation spike (7296 volume) followed by an extremely long, slow,
**low-volume** grind -- the opposite of "sustained multi-bar volume" -- yet it resolved SUPPORT
(with the thinnest reclaim margin of any SUPPORT instance to that point, +0.48pt). As discussed
above, -041 showed that marginal reclaim did not hold as a durable structural shift, which
partially -- but not cleanly -- rescues the lesson: the reclaim event itself technically satisfied
SUPPORT's definition, but the underlying volume story does not fit "sustained volume predicts
SUPPORT" at all.

```
VOLUME_LESSON_CLEANLY_APPLICABLE_CASES = 4  (058, 059, 078 confirming; 040 counterexample)
CONFIRMATIONS   = 3
COUNTEREXAMPLES = 1
```

Given the small clean-test count, this lesson is judged **directionally supported but narrower in
scope than originally stated** -- see Section 8.

---

## 6. Fresh-extreme component -- incremental value

**Necessity test:** every one of the 13 post-3057 SUPPORT instances (038, 039, 040, 041, 045, 052,
053, 056, 057, 059, 064, 065, 070) had *some* form of fresh extreme established by resolution time
-- 13/13, 100%. In four of those (045, 064, 065, 070) the fresh extreme was **not obvious at
pre-classification time** -- it only became apparent as the episode developed, which is itself an
important finding: fresh-extreme evidence is a resolution-time concept the system had to learn to
wait for, not something reliably visible at the trigger bar.

**Sufficiency test -- counterexamples, explicitly requested and not hidden:** a fresh extreme was
present but the episode still resolved REJECTED in at least 7 post-3057 cases: **046, 050, 051, 073,
078, 082, 089**. Q4-P007-051 (a near-record fresh extreme) and Q4-P007-082 (the deepest fresh
extreme of the whole defended-floor stretch) are the two most dramatic of these -- direct evidence
that fresh-extreme evidence, however strong, does not override round-trip completeness. (This count
of 7 should be read as a lower bound: resolution-time fresh-extreme status was tracked with full
rigor for entries 062-089, drawn from this session's own live reasoning, but was extracted less
exhaustively for entries 036-061 by a research pass focused primarily on pre-classification
language -- so additional REJECTED-despite-fresh-extreme cases in that middle range may exist and
were not exhaustively counted. Disclosed rather than papered over, per the instruction not to
fabricate precision the ledger does not cleanly support.)

```
FRESH_EXTREME_INCREMENTAL_VALUE = WEAK
```

Necessary (no SUPPORT occurred without one) but far from sufficient (a material fraction of
fresh-extreme cases, including the single most dramatic one in the dataset, still resolved
REJECTED once round-trip completeness dominated). It is real, reusable information -- but strictly
subordinate to the round-trip signal, not an independent co-equal discriminator.

---

## 7. Discriminator evolution

**A. Known by bar 3057 (PREDECLARED_LEARNING):** the three lessons as stated in Section 2.

**B. Genuinely new lessons discovered after bar 3057**, each checked against the "at least one later
independent prospective test" bar:

| New lesson | First crystallized | Later independent prospective test(s) | Verdict |
|---|---|---|---|
| Round-trip completeness overrides even the strongest fresh-extreme + volume evidence | Q4-P007-051 | 073, 076, 078, 080, 081, 082, 089 (7 independent later re-tests, explicitly citing the rule by name) | **PROSPECTIVELY_CONFIRMED** -- the single best-evidenced new lesson in the whole dataset |
| Magnitude of a favorable component matters, not just its direction/presence | Q4-P007-046 | 049, 054 (explicitly cite -046) | PROSPECTIVELY_CONFIRMED |
| "Fresh" must be judged against the most recent *comparable episode*, not just the all-time Q4 record | Q4-P007-071 | 072 through 089 -- ~18 consecutive later episodes applied this framing | PROSPECTIVELY_CONFIRMED, extremely well-tested |
| A trivial/quiet trigger bar is a poor predictor of the eventual episode's character, and this cuts *both* ways | Q4-P007-064/065 (both escalated dramatically from quiet triggers) | Q4-P007-066 (fired immediately after, did *not* escalate, explicitly noted as confirming the "cuts both ways" reading) | PROSPECTIVELY_CONFIRMED via a genuine three-episode balanced test |
| Volume placement (which bar it lands on), not merely volume growth across an episode, is what matters | Q4-P007-036 | 044, 054, 072 (each independently notes volume landing off the decisive point despite being real/growing) | PROSPECTIVELY_CONFIRMED |
| Chain-continuation context (consecutive episodes each setting a deeper record low in the same decline) carries real interpretive weight | Q4-P007-052/053 | 056, 057 (explicitly built on the -052→053→056 chain) | PROSPECTIVELY_CONFIRMED, though the re-tests are within the same continuous decline rather than fully independent later episodes -- weaker form of confirmation than the others in this table |
| A low retracement percentage alone is necessary but not sufficient without a decisive (not marginal) reclaim margin | Q4-P007-077 | No later episode explicitly re-tested this exact framing with the same clarity; -086 is thematically related (partial retracement, REJECTED) but for a different stated reason (no fresh extreme) | **RETROSPECTIVE_HYPOTHESIS_ONLY** -- raised once, never cleanly re-tested |
| Marginal reclaim durability (does a thin reclaim margin hold?) | Q4-P007-040, touched again at 041 | No third independent test with the same explicit framing | **RETROSPECTIVE_HYPOTHESIS_ONLY** |

---

## 8. Failed beliefs -- did the model change its mind under disagreeing evidence?

```
CONFIRMED  : Lesson 1 (round-trip / retracement-shortfall) -- 46/53 applicable confirmations,
             survived its single hardest stress test (-082) without being weakened or rationalized
             away.
WEAKENED   : Lesson 2 (volume persistence) -- directionally right on its two cleanest tests
             (-058/-059) but narrower in applicable scope than implied, plus one real counterexample
             (-040) that was disclosed rather than explained away.
REFINED    : Lesson 3 (fresh extreme) -- downgraded from "an additional discriminator" to
             "necessary but weak/insufficient on its own," and its own operational definition was
             sharpened mid-quarter (-071's "vs most recent comparable episode" refinement).
REJECTED   : none of the three predeclared lessons was rejected outright.
```

Evidence the system *did* revise its stance under disagreement, not merely accumulate confirmations:
Q4-P007-045's own resolution explicitly states the pre-classification's "isolation" framing (volume
without a confirming fresh extreme) "didn't hold once the next bar's evidence arrived" -- language
that names the prior read and states it was wrong, rather than silently moving on. Q4-P007-066's
resolution explicitly notes it "confirms not every thin trigger bar escalates," directly qualifying
the more dramatic -064/065 pattern rather than assuming it would generalize. Q4-P007-082's own
observational note treats the round-trip lesson surviving its hardest test as a genuinely open,
notable result ("this support level looks unusually robust") rather than a foregone conclusion.

---

## 9. Preclassification accuracy

Buckets: LEAN_SUPPORT (an unhedged directional lean toward SUPPORT, including "leaning toward
taking this seriously"), LEAN_REJECTED (an unhedged directional lean toward REJECTED), AMBIGUOUS
(any entry whose own language opens with "genuinely ambiguous," "genuinely uncertain," or
"genuinely watching," including hedged "leaning slightly X" framings inside such an entry -- these
are kept in AMBIGUOUS rather than folded into a weak-lean bucket, because that is how the ledger
itself frames them). Q4-P007-004 and -007 (pre-3058, no pre-resolution language recorded) are
excluded from calibration.

**PRE-3058 (33 classifiable entries):**
```
LEAN_SUPPORT  -> SUPPORT   7/8    (87.5%)
LEAN_REJECTED -> REJECTED  18/18  (100%)
AMBIGUOUS     -> SUPPORT   2/7 (28.6%) | -> REJECTED  5/7 (71.4%)
```

**POST-3057 (54 classifiable entries):**
```
LEAN_SUPPORT  -> SUPPORT   1/3    (33.3%)
LEAN_REJECTED -> REJECTED  29/37  (78.4%)
AMBIGUOUS     -> SUPPORT   4/14 (28.6%) | -> REJECTED  10/14 (71.4%)
```

**WHOLE Q4 (87 classifiable entries):**
```
LEAN_SUPPORT  -> SUPPORT   8/11   (72.7%)
LEAN_REJECTED -> REJECTED  47/55  (85.5%)
AMBIGUOUS     -> SUPPORT   6/21 (28.6%) | -> REJECTED  15/21 (71.4%)
```

Note the AMBIGUOUS bucket's SUPPORT rate (28.6%) is nearly identical in both halves of the quarter
and sits close to the population's own overall SUPPORT base rate (24/89 = 27.0%) -- when the system
genuinely says it does not know, its calls track the base rate rather than adding discriminating
information, in both periods equally. This is an honest, non-flattering, but real finding.

LEAN_REJECTED calibration *declined* from 100% pre-3058 to 78.4% post-3057 -- entirely because of
eight genuine escalation surprises (038, 039, 052, 053, 056, 057, 064, 065), each a quiet trigger
bar that grew into a real structural episode. See Section 10 for why this is not read as a
reasoning regression.

---

## 10. Learning curve

Divided into three roughly equal, non-optimized thirds by entry count: EARLY (001-030), MIDDLE
(031-060), LATE (061-089).

**EARLY:** Preclassification language is largely a single binary lean ("leaning REJECTED" /
"leaning toward taking this seriously") without much explicit decomposition into separately-tracked
components. Uncertainty is preserved formally ("not pre-committing") but with comparatively little
explanation of *why* a call is uncertain. Reliance on a smaller number of dominant cues (volume
magnitude, gap size) is more common than fully multi-factor weighing.

**MIDDLE:** The three-way "genuinely uncertain, leaning slightly X" hedge language emerges and
becomes standard -- a materially richer uncertainty vocabulary than early Q4's plain binary lean.
The first systematic cross-episode OBSERVATIONAL NOTEs appear, explicitly naming and building on
specific prior entries by number (-036 built on by -044; -046 built on by -049/-054; -051
crystallizing the round-trip-dominance rule for the first time). Chain-continuation reasoning
(-052/053/056/057) is a genuinely new analytical move not present early.

**LATE:** Reasoning becomes explicitly cumulative and citation-heavy -- resolutions routinely name
multiple specific prior entries by number as precedent ("consistent with the established priority
of round-trip completeness over volume placement (-058/-073)"). The "-071 fresh-vs-recent-episode"
refinement is applied with unbroken discipline across roughly 18 consecutive episodes in the
defended-floor stretch. Q4-P007-082 shows the system stress-testing its own strongest rule against
its single most unfavorable case rather than looking for reasons to make an exception.

**DID REASONING QUALITY IMPROVE, separated from market conditions?** Yes, on richness and
consistency of multi-factor reasoning and cumulative citation -- this is visible in the text itself,
not inferred from outcomes. Raw LEAN_REJECTED hit-rate, however, *declined* late (100% → 78.4%),
which at first glance looks like the opposite. Read against market conditions this is not a
contradiction: pre-3058 Q4 contained several of the quarter's largest, most unambiguous moves
(bars 1782-1980, 2528-2812, 2988-2996 -- three of the largest episodes of the entire quarter, all
in the first 30 entries), which are comparatively easy calls once one component (usually record
volume) dominates. The defended-floor stretch (070-089, entirely late-Q4) was a genuinely
lower-signal, choppier regime -- 14 consecutive thin, mostly-REJECTED episodes with the eight
escalation surprises scattered through the middle segment. A fair reading is that late Q4 was a
*harder* market regime, and the calibration dip reflects that, not a reasoning failure -- especially
since a quiet-trigger-bar-escalates outcome is, by the pre-classification's own stated methodology
("not pre-committing," "watching for real continuation"), explicitly disclaimed as unknowable from
the trigger bar alone.

---

## 11. Information rate

Given early rate: **6.3 meaningful learning events / 1000 bars** for bars 1632→3057 (1425 bars,
implying ~9 events by the given rate's own arithmetic).

For 3058→5932 (2874 bars), using the 8 genuinely-new, independently-prospectively-retested lessons
identified in Section 7's table (excluding the 2 classified RETROSPECTIVE_HYPOTHESIS_ONLY, since
those do not meet the same "used prospectively before resolution" bar the earlier audit's own rate
must have applied):

```
LATE_RATE_PER_1000 = 8 / 2874 * 1000 ~= 2.8
```

**Important methodology disclosure:** the exact criteria the bar-3057 audit used to count a
"meaningful learning event" were not given to this audit, only the resulting rate. The 2.8 figure
above is this audit's own reasonable reconstruction (a genuinely new, reusable analytical concept,
crystallized in one entry, independently re-applied in at least one later entry) applied
consistently to the post-3057 population -- it is not a verified apples-to-apples match to whatever
exact rule produced 6.3. The *direction* of the finding (a real decline, not a rounding artifact --
6.3 vs 2.8 is more than a 2x difference) is judged more robust than the exact ratio.

**Did learning saturate?** Directionally, yes -- most of the foundational discriminator components
(round-trip primacy, fresh-extreme necessity-not-sufficiency, volume-placement-matters) were already
present in some form by bar 3057 or crystallized very early in the post-3057 window (-036 through
-051, i.e., the first ~15 post-cutoff entries). The remainder of the post-3057 population (~39
further entries) mostly *applied and re-tested* those components rather than generating comparably
many brand-new ones -- which is real, valuable prospective confirmation (Section 3-4's 46
confirmations happened during this stretch), just not the same kind of event as discovering a new
primitive.

---

## 12. P007 final scientific status / research handoff

Standing governance is **not** overridden:
```
BEHAVIORALLY_REAL = YES
TRADEABLE = NO
DISCRIMINATOR = INSUFFICIENT_EVIDENCE
PLAYBOOK_READY = NO
```

Independent question: is there now a sufficiently precise *observational* discriminator to hand to
a separate research department for formalization/testing?

```
P007_RESEARCH_HANDOFF_READY = YES
```

**Minimum qualitative hypothesis (no numeric thresholds, not backtested):** a PATTERN-007 candidate
is more likely to resolve as a genuine structural SUPPORT event, rather than a REJECTED false
signal, when (a) the post-break retracement is genuinely partial rather than near-complete or
overshooting -- this is the single strongest observed discriminator, confirmed in 46 of 53
applicable post-3057 cases including its single hardest stress test; (b) the episode's low
represents a fresh extreme relative to the *most recent comparable prior episode*, not merely the
all-time record -- necessary in every confirmed SUPPORT case, but not sufficient on its own; (c) the
heaviest volume of the episode is concentrated at or very near the deepest point of the decline,
rather than diffuse or concentrated on the reclaim/recovery leg; and (d) elevated volume persists
across multiple bars of the episode rather than appearing as a single isolated spike with no
follow-through. No one of these four is independently sufficient -- round-trip completeness in
particular has repeatedly overridden even the single most favorable simultaneous reading of the
other three (Q4-P007-082) -- so any formal test should treat this as a joint/composite condition,
not four thresholds to be optimized separately.

---

## 13. MGMT-004 final audit

All 7 prospective triggers, in order:

| Trade | Trigger bar / R at trigger | CONTROL_RESULT_R | SHADOW_RESULT_R | DELTA_R |
|---|---|---|---|---|
| #1  | bar 636, +1.05R | +0.651 (MAX_HOLD) | 0.000 (STOP at breakeven) | **-0.651** |
| #4  | bar 1297, +1.10R | +0.929 (MAX_HOLD) | +0.929 (MAX_HOLD) | 0.000 |
| #12 | bar 2357, +1.53R | +3.000 (TARGET) | +3.000 (TARGET) | 0.000 |
| #25 | bar 4122, +1.08R | +0.9486 (MAX_HOLD) | +0.9486 (MAX_HOLD) | 0.000 |
| #26 | bar 4351, +1.89R | +3.000 (TARGET) | +3.000 (TARGET) | 0.000 |
| #32 | bar 4862, +1.01R | +1.6973 (MAX_HOLD) | +1.6973 (MAX_HOLD) | 0.000 |
| #36 | bar 5565, +2.32R | +3.000 (TARGET) | +3.000 (TARGET) | 0.000 |

```
MGMT004_TOTAL_DELTA_R = -0.651
MGMT004_HELPED_N = 0
MGMT004_HURT_N   = 1   (TRADE #1)
MGMT004_SAME_N   = 6

MGMT004_EVIDENCE = ADVERSE
```

Reasoning for ADVERSE rather than INSUFFICIENT: across all 7 Q4 trials, MGMT-004 never once
produced a better outcome than the control, produced an identical outcome in 6/7, and produced a
strictly worse outcome in the remaining 1/7 -- zero wins in seven tries is a real, if small-sample,
signal, and it is consistent with the ledger's own note that this Q4 evidence "joins the n=4 Q1-Q3
discovery-stage evidence," i.e. it is not being evaluated in isolation. The small-sample caveat is
real and is disclosed here rather than smoothed over -- a different reviewer could reasonably prefer
INSUFFICIENT at n=7 -- but ADVERSE is the more decision-relevant, less-hedged answer the accumulated
evidence actually supports. The management rule itself is not modified by this finding.

---

## 14. S5 -- pure monitoring, not learning

```
S5_Q4_TRADES = 40
S5_Q4_NET_R (control basis) = -3.5526R

EXIT_REASON breakdown (all 40 trades, grepped directly from the trade log):
  STOP      = 16
  TARGET    = 3
  MAX_HOLD  = 21
```

Arithmetic cross-check: 3 TARGET hits contribute a fixed +9.000R (3 x +3R by construction); 16 STOP
hits contribute a fixed -16.000R (16 x -1R by construction); the remaining 21 MAX_HOLD trades
therefore collectively contributed **+3.4474R** net (-3.5526 - 9.000 - (-16.000)). This is reported
purely as monitoring/bookkeeping -- it is not evidence of AI Trader "learning" anything, and S5's
independent validation from its own earlier Q4 segment is not questioned or revisited here.

---

## 15. Operational self-correction (OPERATIONAL_LEARNING, not MARKET_LEARNING)

Distinct category, explicitly not counted anywhere above as market/pattern learning:

- A trade-ledger insertion-ordering bug (TRADE #26 landing before TRADE #25) was self-caught via
  cross-referencing grep before a checkpoint, not discovered by the user.
- A gap-classification timestamp-labeling convention was corrected mid-quarter (`gap_start` is a
  bar's `ts_open`, not `ts_close`, 15 minutes earlier than earlier prose implied) -- disclosed as a
  labeling nuance after verifying no actual MAINTENANCE/UNEXPECTED classification had been wrong.
- A live EMA-tracker re-seeding bug (missing bars 386-388 during a mid-quarter restart) was found,
  corrected, and every affected decision independently re-verified against the corrected trajectory
  before Q4-P007-003's resolution was finalized.
- A retroactive documentation gap (TRADE #12's MGMT-004 trigger, already committed to durable state
  but never written up in the MGMT-004 ledger) was filled using only already-known, already-frozen
  facts, not new judgment.
- A hard boundary check (`MAX_Q4_BAR_INDEX=5932`, refusing to reveal bar 5933+) was added this
  session once it became clear the underlying multi-year source CSV has no natural Q4 stopping
  point -- verified working on its first live test at the actual boundary.

None of these improved P007/S5/MGMT-004 pattern knowledge. They improved the reliability of the
process that records that knowledge.

---

## 16. Central CEO question

**IF WE RESET AI TRADER TO ITS BAR-0 KNOWLEDGE, WOULD THE VERSION AT BAR 5932 MAKE BETTER
PRE-OUTCOME JUDGMENTS ABOUT P007 THAN THE VERSION AT THE START OF Q4?**

**YES.** At bar 0, PATTERN-007 had zero field-captured instances; the only available prior was "the
pattern's own standing expectation of eventual reclaim," with no way to discriminate a genuine
structural event from noise before the fact. The bar-5932 version has demonstrably reusable
components that were exercised prospectively, not narrated after the fact: round-trip completeness
as the dominant discriminator (46/53 post-3057 confirmations, surviving its single hardest test at
-082); fresh-extreme necessity (13/13 SUPPORT cases); and the fresh-vs-most-recent-episode
refinement (used consistently across ~18 consecutive episodes). A bar-0 system could not have told
Q4-P007-082 (dramatic fresh extreme + heaviest volume, REJECTED) apart from Q4-P007-065 (comparable
fresh extreme + concentrated volume, SUPPORT) -- the bar-5932 system correctly separated them
*before* either resolved, using a rule (round-trip completeness) that did not exist at bar 0.

---

## 17. Second central question

Highest level of learning supported by the evidence, among {A. market vocabulary only,
B. descriptive pattern recognition, C. genuinely reusable prospective discrimination,
D. tradeable decision rules}:

```
C. GENUINELY REUSABLE PROSPECTIVE DISCRIMINATION
```

A and B are clearly exceeded throughout the whole ledger. D is explicitly not supported: no numeric
thresholds were ever set, nothing was backtested, and this audit deliberately does not override the
standing TRADEABLE=NO / DISCRIMINATOR=INSUFFICIENT_EVIDENCE governance. C is supported because the
round-trip-completeness rule, the fresh-extreme necessity condition, and the fresh-vs-recent-episode
refinement were each stated *before* resolution and reapplied prospectively across multiple
independent later episodes with real, above-hindsight discriminating power -- not merely described
after the fact.

---

## 18. Required final verdict

See the chat response delivered alongside this document for the CEO's exact required flag-format
output (Section 18 of the mandate). The figures there are drawn directly from this document and are
not restated with different values here.
