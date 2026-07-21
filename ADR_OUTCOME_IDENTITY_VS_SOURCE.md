# ADR — Outcome Identity vs. Outcome Source

**Status: PURE ARCHITECTURE REVIEW. No code, no contract changes, no schema changes.** Companion to
`LEARNING_RESEARCH_FEEDBACK_DESIGN.md` (commit `5752640`) and its Addendum (commit `4905ff4`), both
ACCEPTED. This ADR does not modify either document — it is a standalone review answering one further
question the CEO raised before authorizing implementation. Nothing here is adopted until its own
explicit CEO approval.

---

## Problem statement

The Addendum proposes distinguishing Strategy Outcome ("how did the strategy itself perform," Shadow-
sourced) from Portfolio Outcome ("what actually happened in the live AI Trader," real-ledger-sourced)
using a single field, `Outcome.source_type`, adding one new `SourceType` enum member
(`SHADOW_EVIDENCE_ADAPTER` already exists; a new member such as `REAL_PORTFOLIO_LEDGER` would be added).
Under this scheme, `SourceType` answers two questions at once: *what does this outcome represent* and
*where did the evidence come from*. The CEO asked whether these should instead be modeled as two
independent enums — `OutcomeKind` (STRATEGY | PORTFOLIO) answering "what," `SourceType` (SHADOW_EVIDENCE_
ADAPTER | REAL_PORTFOLIO_LEDGER | ...) answering "where from" — before this is locked into a schema.

---

## Alternatives considered

**Option A — single `SourceType` enum, semantics inferred from source.** One field on `Outcome`. Each
enum member's own name is expected to carry both meanings (e.g. `REAL_PORTFOLIO_LEDGER` is read as both
"this is a Portfolio-kind outcome" and "computed from the real ledger").

**Option B — two orthogonal fields, `OutcomeKind` and `SourceType`.** `OutcomeKind` (a small, closed set:
`STRATEGY`, `PORTFOLIO`) answers what the outcome represents; `SourceType` (an open, growing set)
answers where the evidence came from. A given `Outcome` row carries both.

---

## Analysis

### 1. Semantic clarity

**A**: a consumer must know, by convention or documentation, which `SourceType` values mean "Strategy"
and which mean "Portfolio" — the mapping lives outside the schema, in institutional knowledge.
**B**: the schema itself states the meaning directly (`outcome_kind == STRATEGY`), with no external
mapping required. **B is clearer.**

### 2. Future extensibility

**A**: every new evidence source must independently re-encode its own kind in its own name, and any code
that needs to group by kind must maintain an external, hand-written `SourceType → kind` mapping table,
duplicated wherever needed, silently vulnerable to drift as new sources are added.
**B**: a new source for an *already-existing* kind is a single new `SourceType` member; `OutcomeKind`
itself does not need to change. This is not a hypothetical concern — this project's own roadmap already
names a near-certain future case: **MT5 Live (roadmap step 6/6)** would introduce a live-broker-execution
evidence source that answers the exact same question as today's simulated `trade_ledger` ("what actually
happened") — i.e. a second `SourceType` for the *same* `OutcomeKind.PORTFOLIO`. Under Option A, this
would force a new enum member whose own name has to independently signal "this is still Portfolio-kind,"
with nothing in the type system enforcing that consumers classify it correctly. **B is materially more
extensible, and this is grounded in the project's own stated roadmap, not speculation.**

### 3. Contract stability

**A** mixes two concerns with different rates of change in one flat enum: `OutcomeKind` is a small,
essentially closed set (arguably just `{STRATEGY, PORTFOLIO}` for the foreseeable future, since these are
the two fundamental questions the CEO's own framing already established); `SourceType` is open-ended and
will grow as new evidence-computation methods are added (already at 2 members before this ADR, headed to
3+). Mixing a stable axis with a growing one in a single enumeration is a well-known source of long-term
churn. **B separates them, keeping the stable axis stable independent of how much the growing axis
grows.**

### 4. Risk of ambiguity

**A**: a genuinely new or hybrid evidence source (e.g. one that partially uses Shadow data and partially
uses real fills) has no way to express itself — a single enum value must pre-decide, permanently and by
name alone, which kind it belongs to, with no room for "this source can serve either kind depending on
context." **B**: kind and source are specified independently per row, so this ambiguity cannot arise —
each `Outcome` states its own kind explicitly regardless of how many sources exist. **B has materially
lower ambiguity risk.**

### 5. Long-term maintenance

**A** requires every consumer that needs to group or filter by kind (most obviously `evidence.py`'s own
future statistics, which the Addendum already requires to "group by source_type before computing any
statistic" — itself a slightly imprecise instruction once this ambiguity is surfaced, since grouping by
kind is conceptually what's actually wanted) to carry its own hardcoded source→kind table. **B** makes
this a single-field query with no external table to maintain or drift. **B is lower-maintenance.**

### 6. Backward compatibility

Neither option breaks anything *today* — Context Memory has zero real callers and zero real data
(confirmed directly: every `Observation`/`Outcome` construction in the codebase is test-fixture-only).
But this symmetry is exactly why the decision matters now rather than later: if Option A is shipped and
real data starts accumulating, and this same ambiguity is discovered later, correcting it would require
a real data migration (re-tagging every existing `Outcome` row with an inferred `OutcomeKind`) — a
nontrivial, backward-incompatible schema change once real data exists. Choosing Option B now, before any
row has ever been written, costs nothing. **B is safer for backward compatibility, precisely because
this is the cheapest possible moment to make the choice — before any migration burden exists.**

### 7. Alignment with existing Context Memory contracts

`ContextSnapshot` itself is the strongest evidence in the package's own existing design: it already uses
**eight separate, orthogonal enums** (`ContextTrendDirection`, `ContextStructureState`,
`ContextMomentumState`, `ContextVolatilityRegime`, `ContextLiquidityState`, `ContextExpansionState`,
`ContextAgreementLevel`, `ContextDataQualityState`) rather than one conflated "market state" enum — the
package's own architects already demonstrated, repeatedly, a preference for "one enum per question" over
"one enum answering several questions at once." `Outcome`'s own existing `SourceType` member `PRICE_ONLY`
is itself informative: its name is oriented entirely around *how the value was computed*, not around
*what it represents* — suggesting the original design already implicitly treats `SourceType` as a
"how/where" axis, not a "what" axis, even though it was never given an explicit partner field. **B is
the option consistent with the package's own already-demonstrated architecture; A would be the first
place in this package where a single enum is asked to carry two independent meanings at once.**

---

## Advantages / disadvantages summary

| | Option A | Option B |
|---|---|---|
| **Advantages** | Fewer schema elements; simplest possible shape; structurally prevents nonsensical kind/source combinations by construction (a single value can only ever mean one thing) | Explicit, self-documenting; extensible without growing a second concern into the same enum; matches existing package convention; zero migration risk since adopted before any real data exists; independently queryable by either axis |
| **Disadvantages** | Implicit, undocumented mapping burden on every consumer; conflates a stable concern with a growing one; cannot express a genuinely new/hybrid source without ambiguity; first departure from the package's own established one-enum-per-question convention | Introduces a Cartesian product that can, in principle, represent combinations that are not currently meaningful (e.g. `(PORTFOLIO, SHADOW_EVIDENCE_ADAPTER)`) unless explicitly constrained |

**On Option B's own disadvantage**: this is real but fully mitigable using a pattern the package already
uses elsewhere — `Outcome.__post_init__` already enforces cross-field invariants today (e.g. `RESOLVED`
requires `normalized_result` to be set, `contracts.py:371-398`). A future implementation would add one
more such rule (which `SourceType` values are valid for which `OutcomeKind` today), giving Option B the
same structural safety Option A gets "for free," via a technique this package already relies on rather
than a novel one.

---

## Recommendation

**Option B**, with an explicit kind/source compatibility invariant enforced at construction time
(mirroring `Outcome`'s own existing `__post_init__` validation pattern) to close its one real
disadvantage. This is not proposed as a schema change here — it is a recommendation for whatever
document eventually specifies the implementation, subject to its own separate CEO authorization.

## Justification

All seven dimensions favor Option B, and none of them rest on abstract preference alone:
extensibility is grounded in this project's own stated roadmap (MT5 Live implies a second, real,
near-certain `SourceType` for the existing `PORTFOLIO` kind); backward-compatibility risk is asymmetric
in Option B's favor specifically because Context Memory has zero real data today, making this the
lowest-cost possible moment to decide correctly; and alignment with existing convention is not a
stylistic argument but a direct structural observation — `ContextSnapshot` already uses eight orthogonal
enums rather than one conflated one, and `PRICE_ONLY`'s own existing name already reads as a "how," not
a "what." Option A's only genuine advantage (structural prevention of nonsensical combinations) is fully
recoverable in Option B via a validation invariant the package already knows how to write.

---

## Verdict

## **APPROVE OPTION B**

Technical justification, in one sentence: separating *what an outcome represents* (a small, stable,
closed set) from *where its evidence came from* (an open, growing set that this project's own roadmap
already guarantees will grow — MT5 Live) avoids conflating two concerns with different rates of change,
matches this exact package's own already-demonstrated architectural convention of one enum per question,
and costs nothing to adopt today specifically because no real data yet exists to migrate.

---

## Governance confirmation

No code was written or modified. No contract or schema was changed. No `ai_trader/` file was touched.
This ADR is a standalone review; it does not edit `LEARNING_RESEARCH_FEEDBACK_DESIGN.md` or its Addendum
— if approved, incorporating this verdict into that design is its own next step, not taken here. Zero
diff confirmed against every frozen module, Flow A, and Context Memory's own existing package.
