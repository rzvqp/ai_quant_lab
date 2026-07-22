# Learning/Research Feedback — Architectural Decision Package

**No implementation was performed to produce this document.** No file under `ai_trader/learning_feedback/`
was modified. `ai_trader/simulation/harness.py` is byte-identical to its state before this review began.
No Phase F wiring was selected or written. This document recommends; it does not decide or implement —
every "Recommend" below is a proposal awaiting explicit CEO authorization, exactly as requested.

This package builds directly on, and does not repeat verbatim, `LEARNING_FEEDBACK_PHASE_F_INTEGRATION_
DESIGN.md` and `LEARNING_FEEDBACK_LIFECYCLE_SPECIFICATION.md` (both already CEO-accepted). Every new claim
here is either a fresh, cited source read performed for this document, or an explicit inference from the
already-accepted Lifecycle Specification, marked as such.

---

## 1. Confirmed current-state facts (new to this document, beyond the Lifecycle Specification)

- `ai_trader/risk_manager/config.py:41`: `max_per_symbol: int = 1` — the actual configured default,
  resolving the Lifecycle Specification's own `[UNVERIFIED]` flag on this point.
- `check_max_per_symbol` (`risk_manager/limits.py:46-51`) gates only **opening** decisions. No file in
  `risk_manager/` re-checks a *closing* (`reduce_only` or opposite-direction) decision's own `strategy_id`
  against the position's current owner — the cross-strategy-close/flip risk the Lifecycle Specification
  flagged remains live and is not resolved by this limit.
- `ai_trader/market_intelligence/engine.py:1-16,32-49` (`build_market_intelligence`): confirmed, by
  direct read of its own docstring and body, to be a **pure, stateless function of `MarketContext` alone**
  — "Deliberately not wired into any live per-bar loop... calling it changes nothing about how the market
  context was produced or how any other module behaves." Every analyzer it calls (`analyze_trend`,
  `analyze_volatility`, etc.) is itself pure. No I/O, no network, no hidden state.
- `ai_trader/edge_intelligence/engine.py:1-40` (`evaluate_edges`): also pure/read-only, and **already
  internally calls `build_market_intelligence(context)` itself** (`:39`, `snapshot =
  build_market_intelligence(context)`). This means calling both `build_market_intelligence` and
  `evaluate_edges` independently from a new call site would compute Market Intelligence **twice** per
  symbol per bar — a real, avoidable inefficiency, not a correctness risk. **[UNVERIFIED]**: whether
  `EdgeIntelligenceSnapshot` (`evaluate_edges`'s return type) exposes the `MarketIntelligenceSnapshot` it
  computed internally, or discards it — not confirmed in this review; material to Decision 4's
  implementation, not to the decision itself.
- `simulation/portfolio_simulator.py:157-226` (`_apply_one`) re-read in full for this document: confirmed
  precisely, line by line, the flip mechanics used throughout Decision 2 below (quoted inline).
- `simulation/portfolio_simulator.py:299-329` (`_liquidate`) re-read in full: confirmed liquidation is
  **always** a full close to flat — `del acct.positions[symbol]` (`:329`) with no remainder/reopen branch
  anywhere in the function. A flip can never be liquidation-driven.
- `execution_simulator.py:456-480` (`_activate_bracket_children`, already partly cited in the Lifecycle
  Specification): both bracket children are built with `reduce_only=True` (`:469,478`) explicitly. Combined
  with `_apply_one:220` (`if remainder > 1e-9 and not fill.reduce_only:`), this proves a bracket TP/SL fill
  can **never** cause a flip — the `reduce_only=True` flag structurally forecloses the remainder-reopens
  branch.
- `ai_trader/simulation/types.py:71-75` (`CloseAtEndPolicy`): confirms the two end-of-run dispositions —
  `CLOSE_AT_LAST` (forces closure, already covered by `_finalize_at_end`) and `HOLD_AND_MARK` (positions
  are marked but never closed — genuinely, permanently unresolved for that run).
- `ai_trader/learning_feedback/adapters.py` (re-confirmed, already read in earlier phases): both
  `build_strategy_outcome`/`build_portfolio_outcome` take exactly **one** `TradeRecord`/`ShadowPositionRecord`
  pairing and produce exactly **one** `Outcome`. Neither adapter aggregates across multiple `TradeRecord`s
  for the same position today — this is material to Decision 3.
- `context_memory/contracts.py:462-468` (`OperationalMetadata`'s own module comment, already read in
  earlier phases): the exact, already-shipped precedent for "a separate, optional, diagnostic-only
  companion type, structurally excluded from `evidence.py`/`retrieval.py`, never a learning target" — this
  precedent is the direct model for Decision 3's recommendation.

---

## 2. Decision 1 — Real Position Identity

### Alternatives considered

| | **A. Add `position_id` to `Position`** | **B. External lifecycle registry (event-replay)** | **C. Derive from opening execution data** | **D. External snapshot-diff registry (recommended)** |
|---|---|---|---|---|
| Ownership | Portfolio Simulator | `learning_feedback` | `learning_feedback` | `learning_feedback` |
| Birth point | `Position.__init__` at open (`:174`) and at flip-reopen (`:222`) | when the registry's own replayed open/scale/reduce/flip classification (mirroring `_apply_one:171,181,188`) detects a new position | at the moment the opening fill's own data is available — **but this data is not retained on `Position` today**, so C cannot be built without first doing (part of) A | when a per-bar diff of `portfolio_simulator.account.positions` (or `to_portfolio_state().open_positions`) shows a symbol key that is either new, or whose `opened_as_of` changed |
| Persistence | new field on `Position` + `TradeRecord` | own dict, symbol-keyed, mirroring Shadow's `open_position_id` | n/a — collapses into A | own dict, symbol-keyed, refreshed once per bar from ground truth |
| Mutation rules | constant while `size>0`, replaced wholesale on flip | constant while registry's own replayed size>0, replaced on detected flip | n/a | constant while a bar-over-bar symbol key's `opened_as_of` is unchanged; replaced when it changes |
| Terminal rule | `del acct.positions[symbol]` (already the real terminal rule) | registry's own replayed size reaches ~0 | n/a | symbol key absent from the current bar's snapshot |
| Flip behavior | naturally correct — new `Position()` already constructed at the exact same site | must independently detect flip from replayed fill classification | n/a | detected via `opened_as_of` change at a still-present key |
| Replay determinism | fully deterministic (same inputs, same call site) | fully deterministic PROVIDED the replay logic never diverges from `_apply_one`'s own | n/a | fully deterministic — reads already-computed ground truth, never re-derives it |
| Files changed | `simulation/portfolio_simulator.py` (`Position`, `TradeRecord`, 3 construction sites) — a frozen, independently-tested production module | `ai_trader/learning_feedback/` only, plus one new harness.py read of the fills tuple | n/a | `ai_trader/learning_feedback/` only, plus one new harness.py read of `account.positions` (a pattern harness.py already uses today, e.g. `harness.py:353`) |
| Migration impact | touches a currently-stable file outside `learning_feedback`'s own package boundary; requires re-running/updating Portfolio Simulator's OWN existing test suite | none to existing files | n/a | none to existing files |
| Failure modes | a missed construction site (e.g. `_liquidate`'s own synthetic `TradeRecord`, `:323-328`, has no `Position` object to source an id from) silently produces an unidentified close | independent replay of open/scale/reduce/flip **quantity** bookkeeping can silently drift from Portfolio Simulator's own arithmetic over time as that module evolves | n/a | blind to a same-bar close-then-reopen-then-close chain at the SAME symbol (bar-granularity only) — a real but rare, disclosed limitation |
| Advantages | single source of truth; available to any future consumer, not just `learning_feedback` | contained entirely within `learning_feedback`; matches Shadow's own already-proven pattern | n/a | contained entirely within `learning_feedback`; **no duplicated bookkeeping logic at all** — reads already-authoritative state instead of re-deriving it; self-healing every bar (cannot silently drift over a long run) |
| Disadvantages | violates the ownership boundary already established in the Lifecycle Specification §2 (Context Memory's own correlation need should not force a change to a frozen, independently-owned simulation core module); widens Phase F's blast radius beyond its declared scope | duplicates open/scale/reduce/flip **classification** logic that must be kept in permanent lockstep with Portfolio Simulator's own — an ongoing maintenance coupling risk | not independently viable | one bar of latency between an intra-bar `Position` mutation and `learning_feedback`'s own observation of it (immaterial for an append-only diagnostic system that never gates trading behavior); cannot distinguish a same-bar open+close+reopen sequence |

**Option C is not independently viable**: `Position` (`portfolio_simulator.py:29-46`) has no field
retaining the opening fill's own `client_order_id` or any other opening-fill provenance. Deriving an id
from "opening execution data" at close time requires that data to already be retained somewhere — which
either means modifying `Position` to retain it (making C a strict subset of A, with no independent
benefit) or reconstructing it externally from the original fill stream (making C a restatement of B).
Listed per the CEO's own instruction, rejected on inspection.

### Recommendation: **Option D**

Read-only, bar-level diff of `portfolio_simulator.account.positions` (already the authoritative,
already-computed state), keyed by `symbol`, minting a new id
`f"{run_id}:{symbol}:{position.opened_as_of}:{position.direction.value}"` whenever a symbol key appears
that was either absent or carried a different `opened_as_of` on the prior bar, and retiring it when the
symbol key disappears entirely. This is deterministic, requires zero changes to any frozen module (respects
the ownership boundary the Lifecycle Specification already established), and avoids re-implementing any of
Portfolio Simulator's own open/scale/reduce/flip quantity-tracking logic — the one property Option B
cannot offer and Option A can only offer by crossing the ownership boundary.

**Explicitly proven against the CEO's own required properties**:
- unique within a run: yes — `run_id` is part of the string, and `opened_as_of` disambiguates successive
  positions at the same symbol.
- survives partial fills (entry side, scale-in): yes — scale-in never changes `opened_as_of` (`:184-185`
  mutate `avg_entry`/`size` only), so the diff sees no change, the id is stable.
- survives partial exits: yes — a partial reduce mutates `size` only (`:216`), `opened_as_of` unchanged,
  id stable, PROVIDED (per Decision 3) retirement is driven by symbol-key absence, not by any single
  `TradeRecord`.
- remains stable while the same economic position remains open: yes, by construction.
- terminates when the position reaches zero: yes — symbol-key absence is exactly `size<=1e-9` (`:217-218`).
- creates a new identity after a flat-to-open transition: yes — the symbol key reappears with a fresh
  `opened_as_of`, triggering a new id.
- correctly handles long-to-short and short-to-long flips: yes — `direction` is part of the id and
  `opened_as_of` changes at the exact flip bar (proven in Decision 2 below).
- does not depend on `strategy_id`: correct by construction — deliberately excluded per the Lifecycle
  Specification's own I3 finding.
- does not depend on `client_order_id`: correct by construction.
- does not reuse identity merely because the symbol is the same: correct — `opened_as_of` (and,
  transitively, `direction`) disambiguate successive, distinct lifecycles at the same symbol.
- deterministic: yes — pure function of already-deterministic `Position` state.
- auditable: yes — the id is a plain, human-readable string encoding exactly the facts that produced it.

---

## 3. Decision 2 — Flip Semantics

Worked using the CEO's own example: existing position `+10`, incoming fill `-15`, against the confirmed,
unmodified logic in `_apply_one` (`portfolio_simulator.py:164-226`, quoted precisely):

```
close_qty = min(fill.qty, existing.size)        # min(15, 10) = 10
...
acct.trade_ledger.append(TradeRecord(client_order_id=fill.client_order_id, strategy_id=existing.strategy_id,
    ..., qty=close_qty, ...))                    # ONE TradeRecord, qty=10, attributed to the OLD owner
existing.size -= close_qty                        # 10 - 10 = 0
if existing.size <= 1e-9: del acct.positions[fill.symbol]     # OLD position dies HERE
remainder = fill.qty - close_qty                  # 15 - 10 = 5
if remainder > 1e-9 and not fill.reduce_only:
    acct.positions[fill.symbol] = Position(direction=fill.direction, size=remainder,   # NEW position,
        strategy_id=fill.strategy_id, opened_as_of=fill.as_of, ...)                    # size=5, born HERE
```

- **How much belongs to closing the old position**: exactly `close_qty = min(fill.qty, existing.size)` —
  10 of the 15 units.
- **When the old position's Outcome becomes terminal**: at the instant `del acct.positions[fill.symbol]`
  executes — the SAME `_apply_one` call, the SAME fill, no separate bar or event required. Per Decision 1,
  this is also exactly when the OLD `position_id` disappears from the next bar-diff.
- **When the old `position_id` dies**: same instant, per Decision 1's own terminal rule (symbol-key
  absence) — one bar later from `learning_feedback`'s own *observational* point of view (Option D's
  disclosed latency), but the underlying economic fact is instantaneous and unambiguous.
- **When the new `position_id` is born**: the SAME instant, same fill, same `_apply_one` call —
  `opened_as_of = fill.as_of`, matching the CURRENT bar, which differs from whatever `opened_as_of` the
  OLD position carried (from an earlier bar) — Decision 1's diff detects this cleanly.
- **How the remaining `-5` is attributed**: entirely to the new position — `size=remainder=5`,
  `direction=fill.direction` (short), `avg_entry=fill.price`. No ambiguity; already fully and
  deterministically specified by existing, unmodified code.
- **Which strategy owns the newly opened position**: `fill.strategy_id` — **the strategy that submitted
  the flipping decision**, not necessarily the strategy that owned the old position (Lifecycle
  Specification I3). The OLD position's `TradeRecord.strategy_id` is `existing.strategy_id` (the ORIGINAL
  owner) — so a cross-strategy flip correctly attributes the closing trade to the original owner and the
  new position to the flipping strategy, using logic that already exists and needs no change.
- **Fees/slippage/realized PnL split**: `fee = fill.commission` is deducted **once, in full**, against
  `acct.balance` at the top of `_apply_one` (`:167-168`), before any open/close branching — i.e. the
  entire fill's own commission is charged once, and is subtracted only from the CLOSING side's own
  `net_pnl` (`:192,213`). The newly-opened position carries **no entry-fee cost basis at all** — this is a
  pre-existing Portfolio Simulator accounting convention, not something Learning Feedback invents or should
  "correct"; it must be reflected accurately, not normalized away.
- **One TradeRecord or multiple**: exactly **one** `TradeRecord` represents the closing side of a flip
  (`_apply_one` appends exactly once per call, `:208-214`, regardless of whether a flip occurred). The
  opening side of a flip produces **no** `TradeRecord` — `TradeRecord`s are only ever produced by the
  closing branch. The new position's first `TradeRecord` will be whenever it, in turn, eventually closes
  (possibly bars, or an entire run, later).
- **How Learning Feedback receives the old terminal Outcome**: via the normal `capture_portfolio_
  resolution` call against that one `TradeRecord`, keyed by the OLD `position_id` (Decision 1) — no
  different from any ordinary close.
- **How a new `PendingCapture` is created for the new position — the genuinely new mechanism this document
  identifies**: Phase E's original design (`register_pending_correlation`, called once per ALLOW decision)
  implicitly assumes one decision produces at most one eventual resolution. **A flip decision produces
  TWO**: it closes the old position's lifecycle AND opens a new one, in the SAME step. The new position's
  `PendingCapture` cannot come from a "fresh decision" in the usual sense — there isn't one; the flipping
  decision/order is the only decision that exists. The new `PendingCapture` must be derived FROM the same
  decision's own already-known `Observation`/`cost_model_ref`/`strategy_id` (`fill.strategy_id`, which may
  differ from the closing side's `existing.strategy_id`) at the moment the flip is detected. This is a
  capability Phase E's current `capture.py` does not have — `register_pending_correlation` is only ever
  called once, at decision time, under the *original* strategy's own attribution; a flip requires a SECOND
  registration, attributed to `fill.strategy_id`, triggered by the SAME resolution event that closes the
  old one. Flagged here as required new capability, not resolved or implemented here.
- **Atomicity**: yes at the source — both the death and the birth happen inside one `_apply_one` call
  for one fill. Per Decision 1 (Option D), `learning_feedback`'s own OBSERVATION of both halves can and
  should be made atomic too (resolve-old and register-new performed together, in the same diff pass), to
  avoid a window where the new position exists with no pending capture at all.

### Coverage of every required scenario

| Scenario | Verdict |
|---|---|
| Partial reduction without closing | `close_qty < existing.size`; `TradeRecord` produced (interim, per Decision 3); `Position`/`position_id` survive unchanged |
| Exact close to zero | `remainder == 0`; no new `Position`; clean terminal, no flip complexity |
| Close and reopen, same direction, later | two fully independent lifecycles — old id dies at the first full close, a brand-new id is born at the later reopen (symbol-key absence in between makes this unambiguous under Decision 1) |
| Long-to-short flip | as worked above |
| Short-to-long flip | symmetric, same code path (`_dir_sign`), no special-casing |
| Cross-strategy flip | already correctly attributed by existing, unmodified code (old → `existing.strategy_id`, new → `fill.strategy_id`) |
| Liquidation-driven flip | **confirmed impossible** — `_liquidate` (`:299-329`) always fully closes to flat, no remainder/reopen branch exists anywhere in the function |
| Bracket-triggered transitions | **confirmed impossible** — both TP/SL children are `reduce_only=True` (`execution_simulator.py:469,478`), and `_apply_one:220`'s flip branch explicitly excludes `reduce_only` fills |

---

## 4. Decision 3 — Outcome Semantics

### The ambiguity `Outcome`'s current shape cannot absorb silently

`Outcome` (`contracts.py:315-458`) has no field distinguishing "this is the position's final word" from
"there is more to come." A consumer reading `status=RESOLVED, normalized_result=1.2R` today reasonably
assumes the position that produced this Observation is now fully, permanently closed — no further Outcome
will ever follow it for the same position. Confirmed: today's Phase D adapters
(`build_strategy_outcome`/`build_portfolio_outcome`) each take exactly **one** `TradeRecord` and produce
exactly **one** `Outcome`, with no aggregation across a position's own multiple partial-exit
`TradeRecord`s. If Phase F naively called these adapters once per partial-exit `TradeRecord`, it would
silently produce **multiple RESOLVED Outcomes for one still-open position** — each looking, to any future
consumer (`retrieval.py`, `evidence.py`, decision_intelligence_v2's own explanation layer), like an
independent, final result. This is the exact ambiguity the CEO's instruction warns against.

### Recommendation: **Option C — both, using separate event types**

- `Outcome` keeps its current, CEO-ratified meaning **strictly**: one per position lifecycle, produced
  **only** when the position (per Decision 1's `position_id`) reaches zero size — a genuine terminal fact,
  never an interim one. No change to the existing `Outcome` schema/invariants is proposed.
- A **new**, additive, diagnostic-only companion type is required for interim, economically-meaningful
  partial realizations — mirroring the exact precedent `OperationalMetadata` already established
  (`contracts.py:462-468`: "a separate, optional, immutable, DIAGNOSTIC-ONLY companion type... never fed
  into evidence.py"). This document does not name or design that type's fields — only states that it is
  required, is structurally distinct from `Outcome`, and should be excluded from `evidence.py`/
  `retrieval.py` aggregation until a future, separately-authorized phase decides otherwise (exactly
  `OperationalMetadata`'s own current status).
- **Open aggregation question, explicitly flagged, not resolved here**: when a position closes via
  multiple partial exits, should the FINAL terminal `Outcome`'s own `normalized_result` be (a) only the
  LAST partial's own `pnl_r`, or (b) a size-weighted aggregate across every partial `TradeRecord` for that
  `position_id`? Today's Phase D adapters support neither multi-`TradeRecord` case at all (§1). This is a
  genuine, unresolved Phase D-adjacent design question this document surfaces but does not answer.

### Coverage of every required scenario

| Scenario | Disposition |
|---|---|
| Partial entry fills (scale-in) | never produces any event — no economic realization has occurred |
| Partial exits | interim event (new companion type) for every partial that does not bring the position to zero |
| Scaling in | same as partial entry — no event |
| Scaling out | same as partial exits |
| Multiple `TradeRecord`s sharing one `client_order_id` | each is economically distinct (Lifecycle Specification Finding C) — each gets its own interim event; retirement of the correlation entry is governed by `position_id` reaching zero (Decision 1), never by `client_order_id` resolution count |
| Multiple closing orders for one position | each closing `TradeRecord` (regardless of which order produced it) is interim unless it is the one that brings size to zero, which is terminal |
| Time stop / trailing stop / ordinary strategy exit | uniformly: interim if partial, terminal if it zeroes the position |
| Bracket TP / bracket SL | same rule; per Decision 2, a bracket fill's own `qty` always equals `parent.filled_qty` (the full bracket-protected quantity), so in practice these are typically terminal, but the SAME uniform rule (does this fill zero the position?) applies without special-casing |
| Liquidation | always terminal — `_liquidate` is always a full close (Decision 2) |
| Flip | the closing side is **always** terminal for the old `position_id` (a flip's `close_qty` always equals `existing.size` in full, by definition of "flip"); the new position begins a fresh lifecycle with its own eventual terminal event, whenever that occurs |
| End-of-run forced finalization (`CLOSE_AT_LAST`) | terminal — the position's real economic fate for this run is decided, permanently, at the forced close; treated identically to any other full close |
| Open positions at end of run (`HOLD_AND_MARK`) | **no Outcome is ever produced** — the position's fate is genuinely unresolved for this run; `learning_feedback`'s own bookkeeping (mirroring the already-proposed `drain_pending()`/`discard` cleanup from the Phase F design review) is retired with no fabricated terminal record, an honest "unresolved," never invented |

---

## 5. Decision 4 — Observation Ownership (resolving Finding A)

### Alternatives considered

**A. `harness.py` calls Market Intelligence and Edge Intelligence directly.**
Authoritative producer: `harness.py`'s own per-symbol loop, once per `(symbol, as_of)`. Both entry points
are confirmed pure/stateless/deterministic (§1) — cost is bounded, CPU-only analyzer functions, no I/O; not
benchmarked in this review. Determinism impact: none. Duplication risk: computing Market Intelligence
twice if both functions are called independently without reusing `evaluate_edges`'s own internal MI call
(a performance detail, not correctness). Ownership: very clear — harness.py becomes the direct owner,
extending its own "composes N live pipeline modules" framing by two. Effect on existing behavior: strictly
additive — neither Signal/Scoring/Risk/Execution/Shadow/Portfolio consumes MI/EI output, mirroring
`decision_intelligence_v2`'s own already-established "Context Memory's evidence never feeds back into
execution" precedent. Files changed: `harness.py` (new imports, two new calls in the existing per-symbol
loop). Flow A: fully compatible (Flow B only). Auditability: excellent — byte-identical/reproducible
snapshots for identical inputs.

**B. `decision_intelligence_v2` becomes part of the production decision path.**
Authoritative producer: `make_decision_v2`, which itself calls `decision_intelligence.make_decision` (v1)
internally — running an entire, currently-unused secondary "recommendation" engine every bar, purely to
obtain its own internal MI snapshot as a byproduct. Runtime cost: materially higher than A. Determinism:
`make_decision_v2` also optionally accepts `context_memory_index`/`research_stats` — if ever populated with
real, accumulating history, this introduces a much larger "identical input" surface than A's two pure
calls, though still deterministic given identical history. Duplication risk: high — re-derives
eligibility/ranking logic Risk Manager and Signal/Scoring Engine already compute independently and
differently, creating two parallel "what should the strategy do" authorities that could, in principle,
disagree. Effect on existing behavior: none functionally (guaranteed by v2's own docstring), but a much
larger, conceptually confused new surface for a purpose (Observation production) that doesn't need a full
recommendation engine. Files changed: `harness.py` + likely `decision_intelligence_v2/engine.py` (not
designed for a hot-loop caller). **Rejected** — heavier and conceptually inverted relative to A, for no
additional benefit: `make_decision_v2` is an explain-a-decision tool, not an Observation-production
primitive.

**C. A new orchestration layer owns snapshot creation, feeding both the decision path and Learning
Feedback.**
Same substantive architectural choice as A (harness.py still gains a new, disclosed dependency on Market
Intelligence/Edge Intelligence), but the glue lives in one new, dedicated module rather than inline in
`harness.py`'s own per-symbol loop — computing MI once and (ideally) reusing it for the EI call rather than
letting `evaluate_edges` recompute it internally, resolving A's own minor duplication risk if implemented
carefully. Ownership: clearer for future extensibility (one obvious place to point to for "where did this
Observation's `ContextSnapshot` come from," and a natural seam if a live-decision consumer is ever
separately authorized later). Otherwise identical cost/determinism/Flow-A/auditability profile to A. Files
changed: `harness.py` (one call site instead of two) + one new file.

**D. `capture` receives a smaller, production-native observation contract instead of the current full
`Observation`.**
Authoritative producer: raw `MarketContext`/`RiskContext`/`PortfolioState` data already flowing through
`harness.py`, translated into a new, smaller, native-shaped record, without ever invoking Market
Intelligence/Edge Intelligence. Runtime cost: lowest of all four (no new analyzer calls). Determinism:
fully deterministic (same already-flowing inputs). **Rejected outright**: Context Memory's own
`ContextSnapshot` vocabulary (`ContextTrendDirection`, `ContextStructureState`, `ContextMomentumState`,
etc.) are explicit MIRRORS of Market Intelligence/Edge Intelligence's own analyzed categories (Checkpoint
9's own design), not raw scanner features. Building those categories from raw scanner data without running
the actual analyzers designed to compute them is, by definition, the "fabricated, empty or degraded
snapshot merely to satisfy the API" the CEO's own instruction explicitly forbids. It also creates a second,
parallel, lower-fidelity "Observation" concept, undermining the comparability across runs/strategies that
Context Memory's entire design exists to provide.

### Recommendation: **Option C**

Substantively the same decision as A (accept that `harness.py`'s own dependency graph must, deliberately
and disclosed, widen to include Market Intelligence and Edge Intelligence — there is no way to produce a
real, non-degraded Observation without this), implemented as a small, named, single-purpose orchestration
seam rather than inline calls, so the "where does an Observation's data come from" question always has one
clear, auditable answer, and so the MI/EI double-computation risk can be engineered away at the same time
this seam is built. Not implemented here.

---

## 6. Recommended architecture — lifecycle diagram (informal, for review; not an implementation)

```
per (symbol, as_of), inside harness.py's existing loop:
  ctx = context_batch[symbol]                                    [existing]
  snapshot_bundle = orchestrate_market_snapshot(ctx, library_path)  <- NEW seam (Decision 4, Option C)
                     (mi_snapshot once, ei_snapshot reusing it -- avoids double computation)
  observation = capture_decision_observation(repo, build_observation(snapshot_bundle))   [Phase E, unblocked]
  ... existing signal/scoring/risk/execution/shadow flow, UNCHANGED ...
  for decision in decision_batch.decisions:
      capture_operational_metadata(repo, decision, policy_state=None, observation.id)    [Phase E, as-is]
      if ALLOW:
          register_pending_correlation(...)   -- keyed by the (Decision 1) real position_id
                                                  registry's CURRENT view (may be "about to open")

  fills = execution_simulator.advance_bar(...)                    [existing]
  position_registry.observe(portfolio_simulator.account.positions)   <- NEW, Decision 1 Option D
     -- detects: births (new position_id), deaths (position_id retiring), flips (compound: death+birth)
  portfolio_simulator.apply(fills, bar_index)                      [existing, UNCHANGED]
  for trade in newly-appended TradeRecords this bar:
      if trade fully zeroes its position (per position_registry):
          capture_portfolio_resolution(..., outcome-kind=TERMINAL)  -- Decision 3
      else:
          capture_interim_realization(..., new companion type)      -- Decision 3, NOT an Outcome
      if a flip occurred for this symbol this bar:
          resolve old position_id's PendingCapture (terminal)
          AND atomically register a new PendingCapture for the new position_id
             (attributed to fill.strategy_id, using the SAME decision's Observation/cost_model_ref)  -- Decision 2

  shadow_engine.settle_bar(...)                                    [existing, UNCHANGED]
  -- Shadow side: correlate via ShadowTradeLegRecord.position_id directly (already correct, no new registry)

[_finalize_at_end]
  CLOSE_AT_LAST: synthesized closing fills -> terminal Outcomes exactly as any ordinary full close
  HOLD_AND_MARK: position_registry entries retired with NO Outcome fabricated -- honest "unresolved"
```

---

## 7. Identifier birth/change/death table (recommended design, consolidated)

| Identifier | Born | Changes | Dies |
|---|---|---|---|
| real `position_id` (Decision 1, Option D) | first bar a symbol key appears (new or `opened_as_of` differs from prior bar) | never (whole id replaced, not mutated, on a flip) | symbol key absent from the current bar's `account.positions` |
| Shadow `position_id` (already existing, unchanged) | `engine.py:310`, at decision time | never | removed from `open_position_id` on full close (`engine.py:487`); the string persists forever as a FK on historical records |
| `client_order_id` | `builder.py:153` | never | ceases to be correlation-relevant at its own order's terminal state; demoted (per this document) from "the correlation key" to "duplicate-fill detection within one order" only |
| interim-realization event id (new type, Decision 3) | one per non-terminal closing `TradeRecord`/`ShadowTradeLegRecord` | n/a (immutable, append-only) | never — permanent diagnostic record, like `OperationalMetadata` |
| terminal `Outcome` id (`EdgeEvidenceId`) | exactly once per `position_id`'s own terminal event | n/a (immutable) | never |

---

## 8. Flip transition specification

Fully specified in Decision 2 above; not repeated here. Summary invariant: a flip is exactly one
`_apply_one` call producing exactly one `TradeRecord` (terminal for the old `position_id`) and exactly one
new `Position` (silent at birth, no `TradeRecord` of its own) — requiring `learning_feedback` to perform
"resolve-old + register-new" as one atomic step, a capability Phase E's current API does not have.

## 9. Outcome semantic contract

`Outcome` = terminal-only, one per `position_id` lifecycle, produced exactly when that lifecycle's own
`position_id` dies (Decision 1) with no fabricated record ever produced for a `HOLD_AND_MARK` position
still open at run end. A new, separate, `OperationalMetadata`-precedented companion type carries every
interim, economically-meaningful partial realization. Not implemented or named in detail here.

## 10. Observation ownership contract

The authoritative `ContextSnapshot`/`Observation` for a given `(symbol, as_of)` is produced by exactly one
new, disclosed orchestration seam (Decision 4, Option C) that calls real, unmodified
`market_intelligence.engine.build_market_intelligence`/`edge_intelligence.engine.evaluate_edges` once per
`(symbol, as_of)` — never a fabricated, empty, or degraded substitute.

## 11. Required API changes (enumerated, not implemented)

- `learning_feedback`: a new position-registry component (Decision 1); a new companion type for interim
  realizations (Decision 3); a new orchestration seam or its harness-side call sites (Decision 4); new
  capability in `capture.py` to atomically resolve-old+register-new for a flip (Decision 2); demotion of
  `client_order_id` from primary correlation key to duplicate-fill-detection-only role.
- `harness.py`: new calls into the Decision 4 seam; a new per-bar call to feed `account.positions` (or an
  equivalent read-only view) to the Decision 1 registry; new calls to the flip-aware resolution capability.
- No change proposed to `context_memory/contracts.py`'s existing `Outcome` schema (Decision 3 keeps it
  strictly terminal-only, unchanged).
- No change proposed to `portfolio_simulator.py`, `execution_simulator.py`, or `shadow_evidence/engine.py`
  (all rejected alternatives that would have required touching them; the recommended design reads them,
  never modifies them).

## 12. Expected files affected (when and if authorized)

`ai_trader/learning_feedback/capture.py`, a new file for the position registry, a new file (or extension)
for the interim-realization companion type, `ai_trader/learning_feedback/__init__.py` (exports),
`ai_trader/learning_feedback/tests/*` (new tests), `ai_trader/simulation/harness.py` (new call sites only —
no change to Signal/Scoring/Risk/Execution/Shadow/Portfolio logic), possibly one new orchestration module
(Decision 4, Option C).

## 13. Required tests (enumerated, not written)

Position-registry unit tests (birth/death/flip detection against synthetic bar-by-bar `Position` snapshots,
including the disclosed same-bar-blind-spot case, explicitly documented as a known limitation rather than
silently passing); flip-resolution atomicity tests (old resolves terminal, new registers, in one step, for
long→short, short→long, and cross-strategy flips); interim-vs-terminal classification tests for every
scenario in Decision 3's table; Observation-orchestration determinism tests (identical `MarketContext` →
byte-identical `Observation`, no MI double-computation); `HOLD_AND_MARK` end-of-run test proving no
Outcome is ever fabricated for a position never closed; full existing regression suite
(`ai_trader/simulation ai_trader/context_memory ai_trader/decision_intelligence_v2 ai_trader/decision_
comparison ai_trader/learning_feedback ai_trader/shadow_evidence ai_trader/market_intelligence ai_trader/
edge_intelligence`) plus mypy, proving zero behavior change to every frozen/existing module.

## 14. Migration and compatibility risks

- Decision 4 (Option C) is the first time `harness.py`'s own per-bar hot loop gains a new, real
  computational dependency on Market Intelligence/Edge Intelligence — a disclosed widening of its own
  composition, not previously authorized, requiring explicit sign-off distinct from the Learning Feedback
  work itself.
- The MI-double-computation risk (§1) must be engineered away, not merely noted, or every symbol/bar pays
  for Market Intelligence twice.
- The Decision 1 registry's bar-granularity blind spot (same-bar open+close+reopen) is a disclosed,
  accepted limitation, not a defect to silently paper over — it should remain documented in whatever module
  eventually implements it.
- The open Phase D aggregation question (§4, last partial vs. size-weighted terminal `normalized_result`)
  must be resolved before the interim/terminal split can be implemented — otherwise the terminal `Outcome`
  itself risks being wrong in a subtly different way than today's naive multi-Outcome bug.

## 15. Unresolved questions (explicitly left open)

- Whether any upstream mechanism (beyond `LIMIT_MAX_PER_SYMBOL`, confirmed insufficient) prevents a
  different strategy's reduce-only/opposite-direction decision from closing/flipping a position it doesn't
  own — still **[UNVERIFIED]**.
- Whether `EdgeIntelligenceSnapshot` already exposes the `MarketIntelligenceSnapshot` it computes
  internally (material to avoiding double computation in Decision 4) — **[UNVERIFIED]**.
- The exact terminal-`Outcome` aggregation rule across multiple partial-exit `TradeRecord`s for one
  `position_id` (last-partial vs. size-weighted) — an open Phase D-adjacent design question, not answered
  here.
- The exact shape/fields of the new interim-realization companion type (Decision 3) — intentionally not
  designed in this document, which only establishes that it must exist and must not be `Outcome`.
- Real runtime cost (wall-clock) of adding Market Intelligence/Edge Intelligence calls to the per-bar hot
  loop — not benchmarked in this review.

## 16. No implementation performed

No code, pseudocode, test, or wiring change was written to produce this document. No file under
`ai_trader/learning_feedback/` was modified. `ai_trader/simulation/harness.py` remains byte-identical to
its pre-review state. `ai_trader/portfolio_simulator.py`, `ai_trader/execution_simulator.py`,
`ai_trader/shadow_evidence/engine.py` were read but not modified. No correlation key, no Outcome schema
change, and no Observation-ownership option was selected or committed to — every recommendation above
awaits explicit CEO authorization.

---

## Zero-diff reverification

```
$ git status --porcelain=v1
?? LEARNING_FEEDBACK_ARCHITECTURAL_DECISION_PACKAGE.md
?? LEARNING_FEEDBACK_LIFECYCLE_SPECIFICATION.md
?? LEARNING_FEEDBACK_PHASE_F_INTEGRATION_DESIGN.md

$ git status --porcelain=v1 -- NEXT_SESSION_FLOW_A.md edge_research EDGE_DISCOVERY_REGISTRY_v1.md EDGE_RESEARCH_PROTOCOL.md EDGE_DISCOVERY_ROADMAP.md
(empty)

$ git diff --stat -- ai_trader/simulation/harness.py ai_trader/context_memory/evidence.py ai_trader/context_memory/retrieval.py
(empty)
```

Flow A untouched. `harness.py`/`evidence.py`/`retrieval.py` untouched. All three design documents
(`LEARNING_FEEDBACK_PHASE_F_INTEGRATION_DESIGN.md`, `LEARNING_FEEDBACK_LIFECYCLE_SPECIFICATION.md`, this
document) remain uncommitted, per instruction not to commit unless explicitly authorized.
