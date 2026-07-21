# PORTFOLIO_ARCHITECT_POLICY_RESEARCH.md — Policy Research (Flow B roadmap step 2/6)

**Status: RESEARCH ONLY. No code, no harness changes, no new `ArchitectMode`, no new calibration run, no
Flow A contact.** Produced per explicit CEO directive following the Phase 2A verdict (`STRATEGY_
CONCENTRATION_REORDER` REJECTED — evidence-sparsity, `PORTFOLIO_ARCHITECT_PHASE2A_CALIBRATION_REPORT.md`,
commit `64e7401`). This is a genuinely new research pass, starting from first principles, per the CEO's
own explicit instruction: not a recalibration, not a rescue attempt, not a parameter search. Candidate
ideas only — none is proposed for implementation; none is ranked by profitability.

**The single most important lesson carried forward, explicitly, from Phase 2A**: any candidate whose
evidence source is the real competitive Risk-Manager-ALLOW stream inherits the exact sparsity failure
already demonstrated (19 events over 85 days, 43 strategies — never crossing a 25-event floor). Every
candidate below was screened against this specific failure mode, and its own evidence source is stated
explicitly, so the reader can judge independently whether it repeats the mistake.

---

## Method

Search restricted to decisions that (1) sit strictly between Strategy Health's `health_eligible_ids`
filter and `risk_manager.evaluate()` — the only lifecycle placement the CEO's own governance permits;
(2) are expressible as a `rank` reassignment or an equivalently narrow, auditable transform of the
opportunity sequence, never an ALLOW/DENY/sizing verdict; (3) are provably non-duplicative of Signal
Engine, Scoring Engine (including its own `conflict_penalty` mechanism, read directly from
`ai_trader/scoring_engine/conflict.py` for this research, not assumed), Strategy Health, or Risk Manager.
Each candidate is evaluated against all 10 of the CEO's own constraints; candidates failing any one are
either rejected outright (§3) or flagged as unresolved (§2, where noted).

**A direct architectural finding used throughout**: Scoring Engine's own `conflict_penalty`
(`conflict.py:34-81`) already penalizes exactly two things — (a) `CONFLICT_OPPOSING`: an opposing-
direction signal of higher pre-conflict quality exists in the same batch; (b) `CONFLICT_CORRELATED`: one
or more OTHER same-direction, **same `contract.klass`** signals exist in the same batch (capped at 0.4).
It does **not** penalize same-direction agreement **across different klasses** — this gap is real, not
assumed, and is the basis for Candidate 1 below.

---

## Candidates

### Candidate 1 — Cross-Klass Directional Consensus Tie-Break

**Problem solved**: when multiple actionable opportunities from *different* `contract.klass` groups
agree on the same direction in the same bar, Scoring Engine's own conflict penalty does not see them as
related (it only penalizes same-klass correlation) — yet from a portfolio perspective, five independently
-labeled strategies from five different klasses all going LONG on the same bar is a genuine
concentration-of-directional-bet event that no existing module recognizes at all.

**Why existing components cannot solve it**: Scoring Engine's `compute_conflict_penalties` is explicitly
klass-scoped (`conflict.py:60-71`) — cross-klass agreement is structurally invisible to it. Strategy
Health has no notion of direction or symbol at all. Risk Manager's `LIMIT_MAX_CORRELATED` is driven by
`RiskConfig.correlation_groups`, a static, empty-by-default, operator-declared mapping — unrelated to a
same-bar directional read.

**Required inputs**: the current bar's own already-scored candidate batch only — `strategy_id`,
`direction`, and (via the already-available `component_scores`/`trade_context` or a parallel read of
`contract.identity.klass`, if exposed to Portfolio Architect) each candidate's own klass label.
**No historical data of any kind.**

**Forbidden inputs**: any data outside the current bar; any competitive/Shadow trade-ledger history;
Strategy Health's own internal scoring; Risk Manager's own config or decision state.

**Deterministic decision**: among candidates in the same `(symbol, as_of)` batch, count how many
*distinct klasses* (not counting one's own) share the same direction; apply a small, bounded down-rank
(near-tie adjustment only — never crossing a materially higher-scored candidate, mirroring the Phase 2
design's own §5 discipline) proportional to that count, capped.

**Failure modes**: klass labels may be sparse/undeclared for some strategies (`contract.klass` can be
`None`, per `conflict.py:60`) — must degrade to neutral, never penalize missing metadata; a policy that
is too aggressive could still, in principle, be gamed by a batch where every candidate is a distinct
klass (no effect at all) — a plausible, self-limiting failure mode, not a defect.

**Negative controls**: a batch with only one klass represented → no-op; a batch with zero cross-klass
agreement → no-op; klass metadata missing for all candidates → no-op (matches Q9's own missing-data-
neutral convention from the Phase 2 design).

**Invariants**: same as the Phase 2 design's own §13 (permutation-only output, only `rank` changes,
deterministic, no look-ahead — trivially satisfied since this uses zero historical data).

**Implementation complexity**: Low — pure same-bar computation, no new evidence-accumulation
infrastructure, no rolling window, no minimum-evidence floor to calibrate.

**Expected benefit**: Unknown/unmeasured by design (this is ideation, not calibration) — but structurally
promising because it needs no historical accumulation and therefore cannot repeat Phase 2A's own failure
mode. The genuine open question is how OFTEN cross-klass same-direction batches actually occur in this
strategy universe — not evaluated here.

**Confidence**: Medium — architecturally clean and non-duplicative, but its real-world frequency and
therefore its practical relevance are unknown and would need their own dedicated, freshly-predeclared
evidence pass (not this document, not a recalibration of the rejected policy).

---

### Candidate 2 — Genuine-Tie Round-Robin Fairness

**Problem solved**: Scoring Engine's own Ranker (`scoring_engine/ranker.py:13-26`) breaks ties, as its
own last resort, by `strategy_id` ascending — a completely static ordering. When two or more candidates'
`total_score` (an `int` field — genuine exact ties are structurally possible, not just a float-precision
curiosity), `historical_confidence`, and `signal_strength` are ALL exactly equal, the SAME
alphabetically-earlier strategy wins, every single time, forever, with zero portfolio memory. This is a
real, provable structural bias with no expiry and no fairness mechanism anywhere in the current pipeline.

**Why existing components cannot solve it**: Scoring Engine's own tie-break is static by design and
explicitly documented as such — it is not meant to, and structurally cannot, remember past outcomes
across bars. Risk Manager processes whatever order it is handed and has no concept of "whose turn it is."
Strategy Health has no bar-level or opportunity-level granularity at all.

**Required inputs**: the current bar's candidate batch (to detect a genuine tie — `total_score`,
`historical_confidence`, `signal_strength` all equal), plus a **small, portfolio-owned rotation counter**
per tied-strategy-set — the one candidate in this document that needs ANY state beyond the current bar,
and even then only a simple, self-generated round-robin pointer, never external market/evidence data.

**Forbidden inputs**: any competitive-ALLOW-count history (the exact input that failed in Phase 2A); any
Strategy Health internals; any Risk Manager config.

**Deterministic decision**: among candidates that are in an EXACT tie on every field Scoring Engine's own
Ranker itself uses, break the tie by which candidate was LEAST RECENTLY given priority in a prior genuine
tie of this same kind — a simple round-robin, not a score-based judgment (Scoring Engine already declared
these candidates equal; this only resolves what Scoring Engine left unresolved, never overrides a
preference Scoring Engine actually expressed).

**Failure modes**: genuine 3-way-or-more ties are rarer than 2-way ties — the rotation state needs a
well-defined key (e.g., the tied SET of strategy_ids, not just a pairwise history) to remain coherent as
group composition changes bar to bar; if genuine ties are rare in practice, this candidate is
architecturally clean but low-impact (an honest possibility, not hidden).

**Negative controls**: no tie exists → no-op (must be provably true: any near-tie, not an exact tie,
must NOT trigger this mechanism — this is the sharpest possible falsification test, directly checkable
by comparing `total_score`/`historical_confidence`/`signal_strength` bit-for-bit); a tie of exactly one
candidate (i.e., not actually a tie) → no-op; the SAME strategy set tied on consecutive occurrences →
priority must visibly rotate, not repeat.

**Invariants**: same permutation-only/rank-only invariants as Candidate 1; additionally, the rotation
state itself must be a pure function of the sequence of PAST genuine ties only — no look-ahead, fully
reproducible from a replay of the same run.

**Implementation complexity**: Low-Medium — the computation itself is trivial; the ONE piece of new
infrastructure is a small, portfolio-owned, deterministic rotation counter, a genuine (small) departure
from Phase 1/2's fully stateless design, worth flagging as its own open architectural question rather
than assuming it is automatically acceptable.

**Expected benefit**: Structural fairness only, not a performance claim — this candidate exists to
correct a proven bias (alphabetical dominance in exact ties), not to improve returns.

**Confidence**: Medium-High on architectural soundness (the clearest non-duplication argument of any
candidate here: it activates ONLY where Scoring Engine's own ranking is provably indifferent); low
confidence on practical FREQUENCY (how often exact, multi-field ties actually occur) — unmeasured, would
need its own dedicated, freshly-predeclared evidence pass before implementation.

---

### Candidate 3 — Denial-Stream-Based Starvation Fairness (evidence source deliberately chosen to be
### ABUNDANT, not sparse)

**Problem solved**: when a strategy's own opportunity is repeatedly denied `LIMIT_MAX_PER_SYMBOL` bar
after bar because a different, but not necessarily better-suited, strategy keeps winning the shared slot
first, is there a portfolio-level "how long has this candidate effectively been waiting" signal worth
using in prioritization? Unlike Phase 2A's rejected policy, this uses **denial events**, not ALLOW
events, as its evidence source — and the Root-Cause Report already established `LIMIT_MAX_PER_SYMBOL` is
the DOMINANT denial reason for the majority of strategies in this universe, meaning this evidence stream
is abundant, not sparse, by the very evidence that killed Candidate 1's predecessor in Phase 2A.

**Why existing components cannot solve it**: Risk Manager's own cooldowns (`cooldowns.after_loss_bars`,
`consecutive_loss_count`) govern a SINGLE strategy's own re-entry pacing after an adverse event — they
have no concept of fairness RELATIVE TO OTHER, unrelated, competing strategies. Strategy Health's
eligibility is a coarser, slower-moving classification, not a per-bar queueing concept. Scoring Engine
has no memory of prior bars at all.

**Required inputs**: **this is the one candidate here that requires an input contract beyond what
Phase 1/2 currently define** — either (a) read access to the run's own accumulated `RiskEventRecord`
stream (already produced by the Portfolio Simulator, `simulation/types.py:232-251`), filtered to
`LIMIT_MAX_PER_SYMBOL` denials, or (b) Portfolio Architect tracking, in its own state, how many
consecutive bars each strategy_id has appeared as an ACTIONABLE candidate without a corresponding
`portfolio_state.recent_closed_positions`/open-position entry for it. Either shape is a genuine, disclosed
departure from the current stateless, narrowly-scoped input contract.

**Forbidden inputs**: any real competitive-ALLOW-count-based share metric (the exact rejected input);
any look-ahead into future denial/allow events.

**Deterministic decision**: among candidates competing for the same scarce resource this bar, give a
small, bounded priority boost to the candidate with the longest current streak of consecutive
`LIMIT_MAX_PER_SYMBOL` denials — an aging/anti-starvation mechanism, conceptually identical to fairness
scheduling in operating systems, applied here to slot contention.

**Failure modes**: could interact with Candidate 2's own tie-break rotation in non-obvious ways if both
were ever implemented together (a reason to treat them as independent, separately-evaluated candidates,
not bundle them); a strategy that is CORRECTLY excluded most of the time by Scoring Engine's own
opposing-direction/correlated penalty (i.e., its own signal quality is genuinely weaker, not merely
unlucky) would still accumulate an aging boost under a naive implementation — this must be bounded
tightly enough that it can only break NEAR-ties, never override a materially higher-quality competing
candidate (the same discipline as every other candidate here).

**Negative controls**: a strategy with a fresh (zero-length) denial streak → no boost; a strategy whose
denial streak resets the moment it IS finally allowed → boost must reset to zero, never persist past a
successful allocation; an artificially short streak length (e.g., 1 bar) must produce negligible effect
relative to a genuinely long streak.

**Invariants**: bounded displacement (near-tie only, same as every candidate here); the aging signal must
be entirely derived from PAST, already-recorded denial events — never a prediction of future denial
likelihood.

**Implementation complexity**: Medium — the mechanism itself is simple, but formalizing the NEW input
contract (state or expanded read access) is real design work not yet done, and interacts with the
"stateless" design principle established in Phase 1/2 — this document does not resolve that tension,
only surfaces it.

**Expected benefit**: Directly targets the Root-Cause Report's own dominant finding (shared-slot
contention denying the same few strategies repeatedly) — the clearest LINE OF SIGHT to the original
problem statement of any candidate in this document, though still unmeasured.

**Confidence**: Medium — strong problem-fit and a deliberately abundant evidence source (unlike the
rejected policy), but the new input-contract requirement is a real, unresolved design question, not a
minor detail.

---

## Candidates explicitly considered and rejected (shown for rigor, per the CEO's own stated preference
## for honest negative results)

### Rejected — Strategy Health recency-of-eligibility boost/penalty

*Idea*: give a freshly-re-admitted strategy (just transitioned out of PROBATION/NEW) different priority
than a long-standing ACTIVE strategy. **Rejected**: this requires reading Strategy Health's own
classification HISTORY/transition timing and using it to second-guess an eligibility judgment Strategy
Health has ALREADY made — Strategy Health decided this strategy is eligible NOW; adjusting its priority
based on HOW RECENTLY that became true is functionally re-litigating Strategy Health's own decision,
violating "never duplicate Strategy Health" (constraint 4) even though it is not, technically, an
eligibility override.

### Rejected — Position-sizing-aware reordering (favor smaller-footprint opportunities to fit more into
### the same risk budget)

*Idea*: prioritize opportunities whose eventual sizing would consume less of the exposure/leverage
budget, to fit more trades into the same risk envelope. **Rejected**: sizing and exposure budgeting are
Risk Manager's exclusive, frozen domain (`risk_manager/sizing.py`, `RiskConfig.portfolio_limits`) — any
reasoning about "how much budget would this consume" necessarily anticipates or reimplements Risk
Manager's own sizing computation, violating constraint 5 directly. This was already excluded in the
Phase 2 design's own responsibility matrix (§4 there) and remains excluded here.

### Rejected — Regime-tag-aware concentration cap

*Idea*: use a market-regime classification (e.g. from Market Intelligence) to cap concentration in one
regime-correlated cluster. **Not rejected outright, but deferred, not proposed here**: this was already
flagged in the original Phase 2 design (§7 option (c)) and requires either a genuine Market Intelligence
integration (out of scope for this research pass's own time budget, per the same limitation disclosed in
the Phase 2A report) or a coarse, ad-hoc proxy (already shown, in Phase 2A's own calendar-half-split, to
be too low-signal to draw conclusions from at this data scale). Not included as a numbered candidate
because it is not yet a fully-specified, evaluable idea — it is a placeholder for future work, disclosed
honestly rather than dressed up as a candidate.

---

## Summary ranking, by architectural value (NOT profitability)

1. **Candidate 2 (genuine-tie round-robin fairness)** — cleanest non-duplication argument of any
   candidate (activates only where Scoring Engine is provably indifferent), needs no historical
   competitive-evidence stream, smallest new-state footprint.
2. **Candidate 1 (cross-klass directional consensus)** — equally clean evidence-sparsity profile (same-
   bar only, zero history needed), targets a genuine, confirmed gap in Scoring Engine's own conflict
   logic, no new state required at all.
3. **Candidate 3 (denial-stream starvation fairness)** — strongest problem-fit to the ORIGINAL Root-Cause
   Report finding, deliberately uses an abundant (not sparse) evidence source, but requires a real,
   unresolved expansion to Portfolio Architect's own input contract — the least "ready" of the three,
   architecturally sound but incompletely specified.

**Honest caveat applying to all three**: none has been measured against real data in this pass, per the
CEO's own explicit instruction that this is ideation only, not a new calibration. Every "expected
benefit"/"confidence" note above reflects architectural reasoning, not evidence. A genuinely useful
Portfolio Architect may still turn out to be Candidate 2 or 1 alone, some combination, or none of these —
that determination is intentionally left open, not decided here.

---

## Governance confirmation

No code was written or modified. No `ArchitectMode` was added. No harness change. Zero diff confirmed
against every frozen module and every Flow A artifact — verified directly via `git status`/`git diff
--stat` before this document's own commit.
