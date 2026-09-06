# AI Trader — General Observer Shadow Apprenticeship — Operating Protocol V1

Read-only learning phase. No broker execution, no autonomous trade signals, no strategy promotion,
no S5 modification. Governs how the already-implemented, Red-Team-passed General Observer V1.1
(`GENERAL_OBSERVER_V1_1_FINAL = PASS`, commit `a2637e0`, 191/191 real-MT5 tests) is actually operated
day to day. Does not modify code, does not touch S5, does not change any already-frozen event,
scorecard, lesson, or missed-move semantic (`AI_TRADER_GENERAL_OBSERVATION_DESIGN_V1_1_DEFINITIONAL_
LOCK.md`, Sections 1–19, unchanged).

Verified before writing this document (not assumed): `git show --stat` on `a2637e0`, `1e099aa`,
`256fb81`; `VE_AI_TRADER_GENERAL_OBSERVER_V1_1_RT_BLOCKER_FIX_REPORT.md` in full;
`main_general_observer.py`; `AITraderApprenticeshipV2_task.xml`; a live check of currently-registered
Windows Scheduled Tasks (`AITraderApprenticeshipV2`, `AITraderLiveShadow`, `AITraderS5MT5DemoSoak` —
all `Running`; **no `AITraderGeneralObserverV1_1` task exists yet**); a live check of
`ai_trader/apprenticeship_v2/general_observer/` and `AITraderApprenticeshipV2_task.xml` for a
matching task file (none exists) and of the live-state directory for any general-observer artifact
(none exists — this subsystem has never been run outside of tests).

---

## 1. What General Observer collects each day

Two layers, deliberately kept separate — mechanical (continuous, automatic, already running the
moment the process starts) and qualitative (periodic, requires deliberate LLM/CEO-reviewer time):

**Mechanical (continuous, zero daily action required):**
- Every `SWEEP_REJECTION` / `STRUCTURAL_BREAK` / `DISPLACEMENT` / `SESSION_TRANSITION_REVERSAL`
  episode the 4 frozen detectors fire, as a `PENDING_LLM_REVIEW` shell (frozen snapshot, hash,
  `underlying_move_id`, reference levels) — `general_observer/episode_builder.py`, wired into
  `tick.py`'s own 60s loop.
- Every H1 missed-move audit candidate and cluster (`general_observer/missed_move_audit.py`),
  including `UNCOVERED`/`COVERED`/`UNSCORABLE_ATR_UNAVAILABLE` determinations.
- Per-horizon mechanical scorecard rows (`H1`/`H2`/`H4`/`H8`) for every episode whose BEFORE
  qualitative pass has already set a real `ai_trader_expectation` — and `STRUCTURAL_FINAL` rows,
  independently, per `general_observer/structural_resolution.py`.
- Checkpoints (`general_observer_checkpoint_due()`, its own cadence/keys, disjoint from S5's).

**Qualitative (requires a deliberate, periodic LLM review pass — not automatic, not yet scheduled by
anything):**
- BEFORE fill for every episode still `PENDING_LLM_REVIEW`: `h4_context`/`h1_context`/`m15_context`/
  `m5_context`, `market_structure_state`, `pressure_state`, `pullback_state`, `participation_state`,
  `acceptance_rejection_state`, `level_defense_weakening_state`, `liquidity_context`,
  `supporting_evidence`/`conflicting_evidence`, `what_to_watch_next`, `ai_trader_expectation`,
  `confidence`, `expected_confirmation_behavior`/`expected_invalidation_behavior` — read **only** the
  frozen snapshot, never later bars — then `before_review.complete_before_review()`, which now also
  mechanically enforces the ordering guard (forces `prospective_eligibility=NO` if any scorecard row
  already exists with an earlier `scored_at_utc`).
- AFTER interpretation for resolved scorecard rows: `after_market_interpretation`/
  `lesson_candidate_effect` — qualitative only, can never alter the already-computed
  `expectation_correct`.
- New `LessonHypothesis` creation, when (and only when) a genuinely recurring pattern is noticed
  across multiple already-reviewed episodes sharing one expressible, prospectively-available
  `hypothesis_eligibility_definition` — never manufactured on a schedule, never backdated.

**BEFORE cadence — mechanically correct requirement, not a daily-batching recommendation** (CEO
prospective-learning safety patch, superseding this section's prior "at least once per trading day"
text): every new episode intended for prospective learning must receive its qualitative BEFORE review
before its own H1 outcome boundary (`frozen_at_bar_ts + 60 minutes` — the same frozen horizon
`before_review.evaluate_before_deadline_eligibility` now mechanically enforces; a review completed
after that boundary is forced `prospective_eligibility = NO` and can never vote, regardless of intent
or reporting cadence). Daily batching is acceptable ONLY for reporting/AFTER summaries and for
retrospective/diagnostic reading of already-late episodes — never for the creation of a prospective
BEFORE prediction itself, since a once-daily pass would arrive well past the H1 boundary for most of
the day's episodes and mechanically forfeit them as evidence before the reviewer ever opens the queue.

Review resolved scorecard rows for AFTER-interpretation at least weekly (horizons take up to 8h to
resolve, so daily AFTER review would mostly find nothing new); revisit hypothesis creation whenever a
review pass notices a repeat, not on a fixed schedule. Both remain operating recommendations, not new
semantic thresholds — only the BEFORE-creation cadence above is now a mechanically enforced boundary.

## 2. BEFORE → AFTER → scorecard → lesson evidence accumulation

The full, already-built pipeline, restated as an operating sequence (nothing new):

1. Detector fires → mechanical shell, `PENDING_LLM_REVIEW` (automatic).
2. LLM BEFORE pass → qualitative fields + `ai_trader_expectation`/`confidence` →
   `complete_before_review()` → `prospective_eligibility` becomes authoritative, including the
   RT-fixed ordering guard (automatic once invoked; invocation itself is the daily human/LLM step).
3. Mechanical per-horizon scoring, `H1`→`H2`→`H4`→`H8`(+`STRUCTURAL_FINAL`), each independently gated
   on enough causal forward bars existing, append-only, never revised (automatic).
4. LLM AFTER interpretation on resolved rows (periodic step above).
5. Lesson hypothesis creation (judgment call, per above) — `hypothesis_eligibility_definition` +
   `lesson_evaluation_horizon` frozen at creation, never altered.
6. Vote tally: canonical episode per `underlying_move_id` (earliest prospectively-eligible match) →
   exactly one scorecard row consulted (the hypothesis's own frozen horizon) → `SUPPORT`/
   `COUNTEREXAMPLE`/non-voting → `N_VOTING_INDEPENDENT_MOVES`, `support_ratio` (automatic, already
   implemented, already tested against every CEO worked example).
7. Lesson status recomputed fresh every time from current totals (no ratchet — deterioration and
   recovery both fall out for free) against the **unchanged** frozen minimums:
   `MIN_INDEPENDENT_UNDERLYING_MOVES = 10`, `MIN_SUPPORT_RATIO_FOR_PROSPECTIVELY_SUPPORTED = 0.70`.

## 3. Metrics for genuine learning vs. mere observation-generation

Explicitly **not** PnL. Track instead:

- **Review-queue health**: age of the oldest still-`PENDING_LLM_REVIEW` episode. A queue that never
  gets reviewed means the apprenticeship is only accumulating raw data, not learning anything —
  regardless of how many episodes exist.
- **Hypothesis-ladder movement**: are any `NEW_HYPOTHESIS`/`REPEATED_OBSERVATION` entries actually
  advancing (toward `PROSPECTIVELY_SUPPORTED` *or* `WEAKENED`/`REJECTED` — movement in either
  direction is a sign the evidence is doing something; permanent stasis at `N<2` for a long window is
  not).
- **Calibration trend** (Section 4) over rolling cohorts of reviewed episodes — is it improving,
  flat, or degrading over time.
- **Missed-move coverage stability**: fraction of H1-material 4-hour moves that were `COVERED` by an
  existing prospective episode vs. `UNCOVERED` (a cluster). This is a *diagnostic* on the 4 frozen
  detectors' own reach, not a target to chase — per explicit instruction, detectors are not to be
  optimized off this number. Track it to know what the observer structurally cannot see, not to tune
  it.
- **Reasoning distinctness** (qualitative, human-checked, not automatable): are BEFORE write-ups
  genuinely episode-specific, or template/boilerplate repeats — a spot-check item for the CEO health
  report, not a computed metric.

None of these is optimized against; they are read, not steered.

## 4. Confidence calibration

Bucket every prospectively-eligible, non-`NOT_SCORABLE` scorecard row by its episode's own
`confidence` (`HIGH`/`MEDIUM`/`LOW` — the already-frozen enum, unchanged) at a single, fixed reporting
horizon (recommend `H4` for the health report specifically — 4 hours, a middle horizon giving each
episode a real chance to resolve without waiting the full 8h `H8`; this is a *reporting* choice, not a
new lesson-evaluation-horizon rule — each hypothesis's own frozen `lesson_evaluation_horizon` is
untouched by this). Compute the empirical `expectation_correct=YES` rate per bucket.

**Well-calibrated**: `HIGH` hit-rate ≥ `MEDIUM` ≥ `LOW`, monotonically, once each bucket has reached
the same `≥10`-independent-move floor already established for lesson evidence (reused, not a new
number, for exactly the same reason: fewer than 10 observations is not yet a real signal).
**Miscalibrated**: no such ordering, and especially **inverted** (`HIGH` confidence showing a *worse*
hit rate than `LOW`) — a specific, named warning sign (overconfidence), always called out explicitly
in the health report, never averaged away.

## 5. Performance breakdowns

All of the following are already-available cross-tabs — no new field, no new computation:

- **Event class**: `episode_type` ∈ the 4 frozen classes — already on every episode row.
- **Direction**: `directional_hypothesis` ∈ `{BULLISH, BEARISH}` — already on every row.
- **Session**: derived mechanically from `frozen_at_bar_ts` via the project's own already-established
  `session_for_ts`/`hh<8→ASIA, hh<13→LONDON, hh<21→NY, else→LATE` convention — no new logic.
- **Timeframe/context**: `trigger_timeframe` (always `"M15"` today — not itself discriminating, since
  every trigger is M15 by design) combined with the *qualitative* `h4_context`/`h1_context` text once
  BEFORE review has filled it — read as prose, not yet a structured cross-tab field.
- **Market regime, "where already available"**: **honestly, not available as a structured field
  today.** `h4_context`/`h1_context` are free-text qualitative descriptions, not a discrete regime
  label — there is no `regime` column anywhere in the schema. A regime breakdown is possible only by
  manually reading `h4_context` text across episodes; it cannot be an automatic cross-tab until (if
  ever) a structured regime field is added — which is not authorized by this mandate (no new
  detector/metric invention) and is flagged here as an honest gap, not silently faked with a
  freetext-parsing heuristic.

## 6. Useful learning vs. neutral vs. systematic misunderstanding

- **Useful learning**: a hypothesis reaches `REPEATED_OBSERVATION` or beyond with a support ratio
  trending toward/above `0.70`, backed by a coherent, re-statable causal story in its own
  `hypothesis_eligibility_definition`/reviewed episodes' reasoning — not a coincidental label match.
- **Neutral / inconclusive**: `N < 10` for an extended period (genuinely data-starved — not yet
  decidable), or a ratio sitting close to the `0.5` majority midpoint (already established, Section
  19.7) with no clear drift either way.
- **Systematic misunderstanding**: a hypothesis reaching `N ≥ 10` with a ratio persistently `< 0.5`
  (`PROSPECTIVELY_REJECTED`) — and, more importantly, the *same underlying reasoning pattern*
  recurring across multiple independently-rejected hypotheses. That second case is the one worth
  surfacing prominently: it means AI Trader holds a specific, identifiable, wrong prior about a class
  of setups — a corrected belief, not just a quiet rejection — and belongs at the top of the health
  report, not buried in a table.

## 7. Minimum evidence before influencing Trade Decision research

Unchanged, reused verbatim from the already-frozen Alpha Handoff Rule (Section 14): only a lesson at
`PROSPECTIVELY_SUPPORTED` (`N ≥ 10` independent underlying moves, `support_ratio ≥ 0.70`) may be
handed off, in the existing field format (`HYPOTHESIS_ID, MARKET_BEHAVIOR,
CAUSAL_INFORMATION_AVAILABLE_AT, APPLICABLE_EPISODES_N, SUPPORTING_N, COUNTEREXAMPLES_N,
EFFECT_SIZE_OR_BEHAVIORAL_DIFFERENCE, WHY_IT_MAY_MATTER, KNOWN_CONFOUNDS, WHY_IT_IS_NOT_YET_TRADEABLE`),
labeled only `RESEARCH_HYPOTHESIS_FOR_INDEPENDENT_TEST`, never `TRADEABLE_EDGE`, never a promotion
recommendation. Nothing below `PROSPECTIVELY_SUPPORTED` may be cited to Trade Decision research at
all, even informally.

## 8. Apprenticeship Health Report — template

Concise, trading-language-first, one page. Populated from real data only once the apprenticeship has
actually run — the mock values below are illustrative placeholders (`[N]`), not real observations,
since nothing has been started yet.

```
AI TRADER — GENERAL OBSERVER HEALTH REPORT
Period: [start date] – [end date]

1. WHAT WAS OBSERVED
   [N] episodes ([N] SWEEP_REJECTION, [N] STRUCTURAL_BREAK, [N] DISPLACEMENT,
   [N] SESSION_TRANSITION_REVERSAL) across [N] trading days. [N] missed-move
   clusters (uncovered material H1 moves). Review queue: [N] pending, oldest [N]h old.

2. WHAT IT PREDICTED CORRECTLY
   [1-2 named examples: episode, expectation, horizon, outcome]

3. WHAT IT MISUNDERSTOOD
   [1-2 named examples, same shape — named, not averaged away]

4. EMERGING LESSON(S)
   [hypothesis name] — [lesson_status], N=[n_voting], support=[ratio]
   (repeat per active hypothesis; explicitly say "none yet" if true)

5. IS CONFIDENCE CALIBRATED?
   HIGH: [n]/[n] ([%])   MEDIUM: [n]/[n] ([%])   LOW: [n]/[n] ([%])
   Verdict: [calibrated / miscalibrated / inverted — inverted always called out by name]

6. MISSED MOVES OF NOTE
   [any cluster whose canonical magnitude is unusually large — described plainly, no threshold math]

7. IS THE OBSERVER IMPROVING?
   [one paragraph, referencing Section 3's metrics: queue health, ladder movement,
   calibration trend — never PnL]

RUNTIME: APPRENTICESHIP_ACTIVE=[Y/N]  MT5_CONNECTED=[Y/N]  LAST_TICK=[timestamp]
```

## 9. Graduation — Group 3 (Learning/Calibration) → Group 5 (General Trade Decision)

Graduation authorizes using learned context as a **research input**, never autonomous trading.
Mandatory gate (reused, not new): at least one lesson at `PROSPECTIVELY_SUPPORTED`
(`N≥10`/`ratio≥0.70`, unchanged) with a coherent, re-statable `hypothesis_eligibility_definition`.
Additional, derived (not new-numbered) conditions: confidence calibration (Section 4) must **not** be
inverted at the time of graduation review; the graduating hypothesis's own canonical episodes must
span more than one `episode_type`/session combination (evidence of a genuine pattern, not one
narrow, repeatedly-observed corner case). If the CEO additionally wants a minimum elapsed-calendar-
time or minimum-total-episode-count floor on top of these, that is a policy choice for the CEO to set
explicitly — not invented here, since it is not derivable from anything already frozen.

## 10. Readiness — is everything needed already built?

**`ADDITIONAL_ENGINEERING_REQUIRED_BEFORE_START = NO`.** The mechanical layer (detectors, dedup,
snapshot/hash, missed-move audit + coverage + cluster dedup, scorecard classifier, lesson voting,
checkpoint scheduling, causal-truncation and idempotency fixes) is complete, Red-Team-audited, and
verified against a live MT5 terminal (191/191, 4 consecutive runs, mypy clean). Nothing in Sections
1–9 above requires new code — only the operating cadence (Section 1's qualitative review) this
document itself defines.

**Exact start procedure** (mirrors `AITraderApprenticeshipV2_task.xml`'s own already-working pattern
exactly, pointed at the separate entrypoint):

1. Create `ai_trader/apprenticeship_v2/general_observer/AITraderGeneralObserverV1_1_task.xml`,
   identical in shape to `AITraderApprenticeshipV2_task.xml`, with:
   `<Arguments>-m ai_trader.apprenticeship_v2.general_observer.main_general_observer</Arguments>`
   (same `venv\Scripts\python.exe`, same working directory, same Boot/Logon triggers, same
   `RestartOnFailure`).
2. Register it: `Register-ScheduledTask -Xml (Get-Content '<path>' -Raw) -TaskName
   "AITraderGeneralObserverV1_1"` (elevated PowerShell). **Disclosed honestly**: my own shell has
   previously lacked the privilege to register a new Scheduled Task at all (the same blocker hit and
   resolved by the CEO directly during the original apprenticeship_v2 rollout) — this may recur and,
   if so, needs the same resolution (CEO runs the registration with elevated privileges, or I run
   `main_general_observer.py` as a session-scoped background process in the interim).
3. Verify independently after starting: `Get-ScheduledTaskInfo`/`Get-CimInstance Win32_Process`
   (parent PID = the Task Scheduler service host, not an interactive shell) and
   `new_brain_live_state/apprenticeship_v2/heartbeat_general_observer.json` updating every ~60s with
   `mt5_connected=true`.
4. Begin the daily BEFORE-review cadence (Section 1) — this is the one step that is genuinely a new
   *operating* commitment, not new engineering: nothing currently invokes the qualitative review pass
   on any schedule, so real lesson evidence will not accumulate until it is performed.

---

## Required Final Block

```
GENERAL_OBSERVER_IMPLEMENTATION_PHASE = CLOSED

SHADOW_APPRENTICESHIP_PROTOCOL_DEFINED = YES

READY_TO_START_PROSPECTIVE_COLLECTION = YES

ADDITIONAL_ENGINEERING_REQUIRED_BEFORE_START = NO
IF_YES_ENGINEERING_REQUIRED = NONE

BROKER_EXECUTION_REQUIRED = NO
S5_CHANGED = NO
OBSERVER_SEMANTICS_CHANGED = NO

MINIMUM_PROSPECTIVE_EVIDENCE_PRESERVED = YES
GRADUATION_CRITERIA_DEFINED = YES

NEXT_OWNER = CEO (to authorize starting the Scheduled Task per Section 10) -- then AI_TRADER (for the daily qualitative review cadence, Section 1) -- VE has no further build work authorized by this mandate

NEXT_AUTHORIZED_ACTION = CEO decides whether to start the AITraderGeneralObserverV1_1 Scheduled Task per Section 10's exact procedure; no code, runtime, or broker action is authorized by this document itself

STOP.
```
