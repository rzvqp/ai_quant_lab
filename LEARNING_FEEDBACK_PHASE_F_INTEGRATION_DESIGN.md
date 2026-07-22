# Learning/Research Feedback — Phase F Integration Design (Design & Verification Only)

Status: **DESIGN ONLY — Phase F implementation NOT authorized.** Nothing in this document has been
implemented. `ai_trader/learning_feedback/{adapters.py,capture.py}` (Phases D/E, commits `ef5f511`,
`c598676`) remain fully unwired; `harness.py` is byte-identical to its pre-Phase-D state (verified via
`git diff --stat` at the end of this document).

This document answers the CEO's Phase F design-review request: a precise, citation-backed integration
design covering every required lifecycle point, produced by directly reading `harness.py` and the real
execution/portfolio/shadow lifecycle — not by re-deriving from Phase E's own docstrings, which this
review found to be **wrong on two load-bearing points** (§2, §4 below). Both are reported here per the
CEO's explicit instruction: *"If the existing Phase E API cannot express the required cleanup safely,
report the exact API gap before implementation. Do not silently work around it in harness.py."*

---

## 0. Two blocking findings, up front

### Finding A — `harness.py` has no Market Intelligence / Edge Intelligence integration today

`harness.py`'s own module docstring (line 1-6) states it composes exactly **six** live pipeline modules:
Market Scanner, Strategy Manager, Signal Engine, Scoring Engine, Risk Manager, Execution Engine. Its
import block (`harness.py:16-45`) contains **zero** imports from `ai_trader.market_intelligence` or
`ai_trader.edge_intelligence`, confirmed by full-file grep. Per-symbol context (`ctx`, from
`context_batch = self._scanner.scan(...)`, `harness.py:389`) is a `MarketContext` — `dict[str, Any]`
(`ai_trader/strategy_runtime/context_access.py:17`), a raw Market **Scanner** feature dict, structurally
different from `market_intelligence.types.MarketIntelligenceSnapshot` (a typed dataclass with
`.trend`/`.momentum`/`.structure`/`.volatility`/`.liquidity`/`.expansion`/`.confidence`/`.session`).

`market_intelligence.engine.build_market_intelligence` and `edge_intelligence`'s own engine are, in this
entire repository, invoked from exactly one place: `decision_intelligence_v2.engine.make_decision_v2`
(`decision_intelligence_v2/engine.py:32`), whose own docstring (lines 12-14) states it is *"Completely
independent from Signal Engine, Scoring Engine, Risk Manager, Shadow Evidence, and Execution Engine ...
none of those packages is imported anywhere in this one."* The only real caller of `make_decision_v2`
found anywhere in the repo is a test (`ai_trader/decision_comparison/tests/test_integration.py`) — it has
**no production/live wiring**.

**Consequence for Phase F**: `capture_decision_observation` requires an `Observation`, built via
`decision_intelligence_v2.adapters.build_context_snapshot(mi_snapshot)` /
`build_present_edge_reference(...)` — both of which require a real `MarketIntelligenceSnapshot`/
`EdgeIntelligenceSnapshot`. **`harness.py` cannot produce either today.** `make_decision_v2`'s own
signature (`context: MarketContext, ...`) confirms `build_market_intelligence` is *capable* of consuming
the same `MarketContext` dict shape `harness.py` already has in hand per symbol per bar (`ctx` at
`harness.py:413`) — so the raw ingredient exists — but **no code anywhere calls
`build_market_intelligence`/an Edge Intelligence engine from `harness.py`'s own per-bar loop**, and
adding that call is a new, non-trivial integration decision (a new dependency edge from `harness.py` onto
two packages Phase 7's own design deliberately kept execution-independent, run once per symbol per bar in
the live simulation hot loop) that is outside Phase E's stated scope and was not raised by the
Implementation Plan.

**This is reported, not silently worked around.** Phase F cannot wire `capture_decision_observation`/
`capture_operational_metadata` (which needs an `ObservationId` to attach to) into `harness.py` until this
precondition is explicitly decided by the CEO. Two options exist (not implemented, listed for the
decision only):
  - **Option 1**: Add a new call to `build_market_intelligence(ctx)` (+ an Edge Intelligence engine call)
    inside `harness.py`'s per-symbol loop, before the Shadow tap / Risk Manager evaluate — a real,
    disclosed widening of `harness.py`'s own dependency graph and per-bar computational cost.
  - **Option 2**: Build a *degraded* `ContextSnapshot` directly from the `MarketContext` dict already in
    hand (bypassing Market Intelligence/Edge Intelligence entirely) — cheaper, but a materially different,
    lower-fidelity meaning of "Observation" than Checkpoint 9's design intends, and `present_edges` would
    need an entirely different, not-yet-designed source (Edge Intelligence today is the only producer of
    `EdgeState`).

Every lifecycle-table row below that references Observation capture is written **as if this precondition
is resolved** (so the table remains useful once the CEO picks an option) — it is not resolved by this
document.

### Finding B — `client_order_id` correlation only works for the bracket TP/SL sub-case; it silently drops every ordinary exit

Phase E's own `capture.py` docstring (lines 9-15) claims `client_order_id` is *"deterministically built at
decision time... and carried forward unchanged onto `TradeRecord.client_order_id`... at resolution time."*
This is **only true for the bracket TP/SL sub-case**. It is **false** for every other close, which is the
dominant case in practice:

- **Bracket TP/SL** (the one case that *does* work): `ai_trader/simulation/execution_simulator.py:464,473`
  — `tp_id = f"{parent.client_order_id}-TP"` / `sl_id = f"{parent.client_order_id}-SL"`, built inside
  `_activate_bracket_children` (`execution_simulator.py:456-480`), called only once the **parent** order
  fully fills (`execution_simulator.py:343,346`). Deterministically derivable from the parent's own id —
  Phase E's pre-registration of these two aliases at decision time is *sound*, provided harness knows
  which of stop/target `decision.constraints` actually set (§4 below has the exact condition).
- **Ordinary strategy exit** (a later, separate `RiskDecision` on an opposite/close signal): its
  `client_order_id` is `f"{prefix}-{decision_id}"` where `decision_id = f"{strategy_id}|{symbol}|{as_of}"`
  (`risk_manager/assembler.py:33`) — built from the **exit's own, later** `as_of`, sharing no derivable
  relationship with the entry decision's id. Confirmed: no `entry_decision_id`/`parent_client_order_id`/
  `position_id` field exists anywhere on `RiskDecision`, `Constraints`, `Sizing`, `PortfolioImpact`
  (`risk_manager/types.py:100-177`), or `OrderRequest` (`execution_engine/types.py:187-215`).
- **Time-stop close**: `decision_id = f"TIMESTOP-{position.strategy_id}-{position.symbol}-{as_of}"`
  (`simulation/time_stop.py:81`) — a brand-new id, unrelated to the entry's.
- **Trailing-stop close**: `decision_id = f"TRAILSTOP-{position.strategy_id}-{position.symbol}-{as_of}"`
  (`simulation/trailing_stop.py:104`) — same, unrelated.
- **Liquidation close**: `client_order_id = f"LIQUIDATION-{symbol}-{as_of}"` (`portfolio_simulator.py:324`)
  — synthetic, unrelated to any decision.
- **Shadow's own `-CLOSE-AT-END-` window-end close** (`shadow_evidence/engine.py:517`): same pattern.

`CorrelationMap.pop_for_resolution` (`capture.py:131-148`) looks up `self._pending.get(client_order_id)`
using the **closing fill's own id**. For every case above except the bracket TP/SL alias, that id was
**never registered** (only the entry's own id — and its TP/SL derivatives — were registered at decision
time), so the lookup returns `None`. `capture_strategy_resolution`/`capture_portfolio_resolution` treat
this exactly like an "unknown key" — log at INFO, return `None`, **no error, no visible failure**
(`capture.py:224-230,256-262`). Per the harness's own time-stop/trailing-stop overlay code
(`harness.py:489-560`) being ordinary, non-exceptional per-bar logic (not a rare edge case), and given
that in this backtest architecture *every* non-bracket exit follows this same "new decision, new id"
pattern, **the current correlation design would silently drop the large majority of real Strategy/
Portfolio Outcomes** were it wired in today — while reporting `True`/successful capture rates in
whatever aggregate wiring-health metric a future Phase F might track only for the minority bracket case.

Shadow Evidence already solves the identical problem correctly, and is the precedent for the proposed
fix: `ShadowEvidenceEngine` never tries to derive the entry↔exit link from `client_order_id` strings at
all. It keeps its own engine-internal `position_id` state — minted at virtual-entry time
(`position_id = f"{run_id}:{strategy_id}:{symbol}:{as_of}:{decision.decision_id}"`, `engine.py:310`),
stored in `account.open_position_id[symbol]` (`engine.py:444`), and looked up by
`_record_new_trade_legs` (`engine.py:460-473`) for **every** subsequent closing leg regardless of that
leg's own `client_order_id` — bracket, time-stop, trailing-stop, or ordinary exit, uniformly.

**Proposed smallest correction (not implemented — requires a CEO decision before Phase F)**: extend
`PendingCapture`/`CorrelationMap` with a **second, position-scoped key**
`(run_id, strategy_id, symbol)` → currently-open `PendingCapture`, populated/updated the same way Shadow
already tracks `open_position_id`, used as the resolution lookup for every close *except* the bracket
TP/SL case (which can keep resolving via the existing alias mechanism, since it is correct and provably
so). This does not discard the existing `client_order_id`-keyed map — it is still useful for exact
partial-fill/duplicate-fill bookkeeping (§Finding C) — it adds the missing link Shadow already has and
the real-portfolio side does not.

### Finding C — first-resolution-wins conflicts with confirmed partial-fill semantics

Confirmed directly from `execution_simulator.py`/`portfolio_simulator.py`:
- One `client_order_id` **can** produce multiple `SimFillEvent`s across bars
  (`PartialFillPolicy.FIXED_FRACTION`, `execution_simulator.py:408-414`, `_match_one:327-348`).
- Each such partial fill produces its **own** `TradeRecord`, sharing that same `client_order_id`
  (`portfolio_simulator.py:209`, `_apply_one`), confirmed by `PORTFOLIO_SIMULATOR.md:64-66`: *"one record
  per closed trade (and per partial exit)."*
- These are **economically distinct** events (different `qty`/`price`/`gross_pnl` each), not duplicates
  of one underlying fact.

`CorrelationMap.pop_for_resolution` retires an entry (moves it from `_pending` to
`_resolved_client_order_ids`) on its **first** successful lookup (`capture.py:142-148`); every subsequent
resolution attempt against the same `client_order_id` is treated as a duplicate and dropped
(`capture.py:225-230`, confirmed by `test_strategy_resolution_duplicate_second_attempt_returns_none` in
`tests/test_capture.py`). Applied to a genuine multi-bar partial exit, this **silently discards every
partial after the first** — conflicting with the CEO's explicit "do not discard economically meaningful
later fills" instruction.

**Proposed smallest correction (not implemented)**: split retirement from resolution. Add a
`remaining_qty`/`is_final` signal the Phase F caller passes to resolution (derivable from the
`TradeRecord`/`Position` state already available at the harness call site — a `TradeRecord` alone doesn't
carry "is this the last partial," but the harness's own view of `Position`/`WorkingOrder.remaining_qty`
does) so `CorrelationMap` only retires the entry once the underlying order/position is genuinely fully
closed, and every partial in between produces its own captured Outcome without being treated as a
duplicate. Exact API shape is a Phase F implementation decision, not resolved here.

---

## 1. Exact lifecycle call graph (as it exists in `harness.py` today, before any Phase F change)

```
SimulationHarness.step()                                              harness.py:293-319
  self._clock.tick() -> as_of                                          harness.py:299
  self._run_one_bar(as_of)                                             harness.py:305
    self._data_source.feed_up_to(...); self._scanner.advance_clock()   harness.py:383-384
    bars = self._data_source.base_bars_at(as_of)                       harness.py:386
    if phase_running:
      context_batch = self._scanner.scan(as_of, symbols)                harness.py:389
      for symbol:                                                       harness.py:409-483
        ctx = context_batch[...]                     (MarketContext = dict[str, Any])
        signal_batch = self._signal_engine.evaluate(ctx, handles, ...)  harness.py:413
        score_batch  = self._scoring_engine.score_batch(...)            harness.py:414
        risk_context = _build_risk_context(...)                         harness.py:416
        portfolio_state = self.portfolio_simulator.to_portfolio_state() harness.py:417
        self.shadow_engine.observe(as_of, score_batch, risk_context)    harness.py:435  <-- SHADOW TAP
        risk_opportunities = filter by health_eligible_ids               harness.py:446-449
        architected_opportunities = PortfolioArchitect (optional)        harness.py:455-462
        decision_batch = self._risk_manager.evaluate(...)               harness.py:463  <-- RiskDecision(s)
        for decision in decision_batch.decisions:
          if decision.decision is Decision.ALLOW:
            status = self._execution_engine.execute(decision, ps)       harness.py:466  <-- client_order_id born
            self.portfolio_simulator.register_stop_hint(...)            harness.py:469
          else:  # DENY
            self.portfolio_simulator.record_risk_event(...)             harness.py:477-483
      time-stop overlay: build_time_stop_decision(...)                  harness.py:489-517
        -> new RiskDecision(decision_id=f"TIMESTOP-{sid}-{sym}-{as_of}")
        -> self._execution_engine.execute(...)                          harness.py:506
        -> self.shadow_engine.apply_time_stops(...)                     harness.py:513
      trailing-stop overlay: build_trailing_stop_decision(...)          harness.py:519-560
        -> new RiskDecision(decision_id=f"TRAILSTOP-{sid}-{sym}-{as_of}")
        -> self._execution_engine.execute(...)                          harness.py:549
        -> self.shadow_engine.apply_trailing_stops(...)                 harness.py:556
    fills = self.execution_simulator.advance_bar(as_of, bars)           harness.py:562  <-- real fills
      (internally: bracket -TP/-SL child activation on parent fill,      execution_simulator.py:343-346,456-480
       OCO sibling cancellation,                                         execution_simulator.py:445-454
       partial fills accumulate on same client_order_id)                 execution_simulator.py:327-348
    self.portfolio_simulator.apply(fills, bar_index)                    harness.py:564  <-- TradeRecord(s) born
    self._execution_engine.reconcile()                                  harness.py:566  <-- terminal-state sync
    self.portfolio_simulator.mark_to_market(...)                        harness.py:567
    self.shadow_engine.settle_bar(...)                                  harness.py:576  <-- Shadow TradeRecord(s)
  [replay exhausted, or stop_now() called]
  self._finalize_at_end()                                               harness.py:335-376
    close_at_end_policy -> synthesize reduce-only closing fills           harness.py:347-365
    self.portfolio_simulator.apply(fills, bar_index)                    harness.py:365
    self.shadow_engine.finalize_at_end(...)                             harness.py:372
```

`run_id`: **not read anywhere in `harness.py` today**, but already exists, unused, on
`SimulationContext.run_id` (`simulation/config.py:130`, non-empty validated at `:161-162`) — the correct,
already-available source for `CorrelationMap(run_id=self.context.run_id)` construction, requiring no new
field.

`policy_state` (Strategy Health): **no Strategy Health module is imported or called anywhere in
`harness.py`** (confirmed by full-file grep for `policy_state`/`StrategyHealth`). The only touchpoint is
the externally-supplied `health_eligible_ids: frozenset[str] | None` constructor parameter
(`harness.py:72,149`), a plain eligibility filter, not a policy-state string. `capture_operational_metadata`
would have to be called with `policy_state=None` — already a supported value (`build_operational_metadata`
accepts `policy_state: str | None`, exercised by
`test_build_operational_metadata_policy_state_may_be_none`). Not a blocker, just disclosed: Phase F cannot
report a real policy state today, only `None`.

---

## 2. Required lifecycle table

Every row assumes Finding A is resolved (an `ObservationId` is obtainable) and Finding B's proposed
position-scoped correlation exists, unless the row is specifically about the gap itself.

| # | Lifecycle event | Production source function | Data available | Phase E capture function | Expected result | Cleanup action | Failure behaviour | Wiring required in Phase F? |
|---|---|---|---|---|---|---|---|---|
| 1 | Decision observation capture | `harness.py:389` (`context_batch`) — once per `(symbol, as_of)`, **before** the per-strategy decision loop | `ctx` (`MarketContext` dict) → (pending Finding A) `MarketIntelligenceSnapshot`/`EdgeIntelligenceSnapshot` set for every strategy active on this symbol this bar | `capture_decision_observation` | New or idempotent-duplicate `ObservationId` | none (append-only; repository's own duplicate policy is already idempotent, `repository.py:36`) | drop+log, `None` returned (`capture.py:172-176`) | **YES** — blocked on Finding A |
| 2 | Operational metadata capture | `harness.py:463-483`, once per `decision` in `decision_batch.decisions` (ALLOW and DENY both) | `RiskDecision`, `policy_state=None` (Finding A/policy_state note), the `ObservationId` from row 1 | `capture_operational_metadata` | New `OperationalMetadataId`; `UnmappedDenialCodeError` fails closed for a code outside `ALL_DENIAL_CODES` (`adapters.py:129-144`) — this one DOES escape `capture_operational_metadata`'s own try/except? **No** — `capture_operational_metadata` catches `Exception` generically (`capture.py:185-190`), so an unmapped code is swallowed into a `None` return, not surfaced. Flagged in §6 (Failure Policy) as needing a severity reclassification. | none | drop+log, `None` returned | **YES** — blocked on Finding A |
| 3 | Pending correlation registration | Immediately after row 2, for `ALLOW` decisions only (a DENY never reaches `execute()`, so never gets a real `client_order_id`, so has nothing to correlate to a future resolution) | `status.client_order_id` (`harness.py:466`), `decision.constraints.stop`/`.target` (for computing TP/SL aliases per Finding B), `entry.observation_id` | `register_pending_correlation` | `True`/pending entry stored under (proposed) both the `client_order_id` alias set AND the `(run_id, strategy_id, symbol)` position key | none yet (entry stays pending until resolution or a terminal non-fill event, rows 6-10, retires it) | `False` returned on `DuplicateDecisionCaptureError`/mismatch (`capture.py:193-205`) — **currently silent**; §6 reclassifies a duplicate registration as an invariant violation, not a routine drop | **YES** |
| 4 | Real Portfolio outcome resolution | `harness.py:564`, `portfolio_simulator.apply(fills, bar_index)` — one call per `TradeRecord` produced inside `_apply_one`/`_liquidate` | `TradeRecord` (has `client_order_id`, `strategy_id`, `symbol`, `pnl_r`, `exit_as_of`, `holding_bars`) | `capture_portfolio_resolution` | `EdgeEvidenceId` (RESOLVED or UNAVAILABLE per Phase D) **only if** the correlation lookup hits — currently fails for every non-bracket close (Finding B) | pop from pending map (partial-fill-aware per Finding C's proposed fix) | drop+log, `None` returned for unknown/duplicate/kind-mismatch | **YES** — blocked on Finding B correction |
| 5 | Shadow Strategy outcome resolution | `harness.py:576`, `shadow_engine.settle_bar(...)` — internally, `ShadowEvidenceEngine._record_new_trade_legs` (`shadow_evidence/engine.py:460-473`) is where each closing `ShadowTradeLegRecord` is produced | `ShadowPositionRecord` + closing `TradeRecord` leg (Shadow's own `client_order_id`/`position_id` state, `engine.py:310,444`) | `capture_strategy_resolution` | Same shape as row 4, for `OutcomeKind.STRATEGY` | pop from pending map | drop+log, `None` returned | **YES** — blocked on Finding B correction (Shadow's own internal `position_id` should be the actual correlation key here, not `client_order_id` string derivation — see Finding B's proposed fix, which mirrors Shadow's own working design) |
| 6 | Order denial | `harness.py:477-483` (`decision.decision is Decision.DENY`) | `RiskDecision` with `denied_reasons` set; row 2's `capture_operational_metadata` already records this — **no `client_order_id` is ever minted for a DENY** (`pipeline.py:172-177`, synthetic id only, never Ledgered) | none (no pending correlation is ever registered for a DENY — row 3 is skipped by construction) | n/a — `OperationalMetadata` alone documents the denial | n/a — nothing was ever registered to clean up | n/a | **YES** for row 2 only; nothing extra for denial itself |
| 7 | Order rejection (post-ALLOW, execution-layer) | `pipeline.py:107-133` — validation rejection or broker/adapter rejection, both produce `OrderState.REJECTED` with a real, Ledgered `client_order_id` (built pre-rejection) | `OrderStatus{client_order_id, state=REJECTED, reasons}` returned synchronously from `execute()` (`harness.py:466`) | none exists today — Phase E has no "resolve as rejected, never entered the market" path; only `capture_strategy_resolution`/`capture_portfolio_resolution` (which expect a filled `TradeRecord`/`ShadowPositionRecord`) exist | An `Outcome` should arguably never be produced (no economic event occurred) but the **pending correlation entry registered in row 3 must still be retired**, or it leaks forever | **retire the pending entry** for this `client_order_id` — **no existing Phase E function does this**; `pop_for_resolution` requires a `TradeRecord`, which doesn't exist for a rejection | n/a today | **YES — this is a genuine API gap.** Phase E needs a new, small function (e.g. `discard_pending_correlation(correlation, run_id, client_order_id) -> bool`) that retires an entry with no `Outcome` produced, for rejection/cancellation/expiry alike (rows 7-10) |
| 8 | Order cancellation | `execution_engine/engine.py:190-213` (`ExecutionEngine.cancel()`) — **not called anywhere in `harness.py` today** (confirmed: no call site found); OCO-sibling cancellation IS active (`execution_simulator.py:445-454`, `reason="OCO_SIBLING_FILLED"`) but that's the LOSING bracket leg, whose alias was pre-registered under the SAME `PendingCapture` as the winner (Finding B) — so no separate cleanup is needed there, it retires together with the winning leg's resolution | For an OCO-sibling cancel: nothing extra needed (handled by row 4/5's alias-group retirement). For an explicit top-level cancel (not currently exercised by any `harness.py` call site): would need the same `discard_pending_correlation` as row 7 | Same gap as row 7 | Same as row 7 | Same as row 7 | n/a today | **NO new wiring for OCO-sibling case** (already covered structurally); **N/A for explicit cancel** since nothing in `harness.py` calls `ExecutionEngine.cancel()` today — out of scope unless that changes |
| 9 | Order expiry (TIF) | `execution_simulator.py:215-217,440-443` (`_expire`, `wo.state = EXPIRED`, `reason="EXPIRED_TIF"`) | `WorkingOrder` reaching `valid_until` — **`advance_bar`'s return value is `fills` only** (`harness.py:562`); an expiry event is **not surfaced to `harness.py` at all** today (confirmed: `execution_simulator.py` has no public API returning expired-order events, only `SimFillEvent`s) | Same gap as row 7 | Same as row 7 | Same as row 7 | Same as row 7 | n/a today | **YES — second genuine API gap, upstream of Phase E**: `harness.py` cannot call `discard_pending_correlation` for an expired order because it is never told an order expired. This needs either a new `ExecutionSimulator` query (e.g. "orders that transitioned to a terminal non-fill state this bar") or a `reconcile()`-driven sweep. Not resolved here — reported for the CEO's decision |
| 10 | Working orders that never fill (still open at run end) | Never terminal during the run itself; only resolved at `_finalize_at_end` (`harness.py:335-376`) via synthesized reduce-only closing fills for **open positions** (`harness.py:349-365`) — an order that never got its first fill (still `ACKNOWLEDGED`/`QUEUED`, no `Position` exists) is **not** covered by `_finalize_at_end`'s own logic, which only iterates `self.portfolio_simulator.account.positions` (already-open positions), not the Execution Engine's own still-open `Ledger` entries | `ExecutionEngine`'s own Ledger (`ledger.open_orders()`, `ledger.py:57-58`) — never consulted by `harness.py`'s finalize path today | Same gap as row 7 (retire without an Outcome) — **plus a second, distinct gap**: nothing in `harness.py`'s `_finalize_at_end` even enumerates never-filled orders to know they need retiring | Same as row 7 | **retire every still-pending correlation entry at end of run**, regardless of whether the underlying order ever partially filled | Same as row 7 | **YES — third gap.** End-of-run finalization (row 13) must sweep the `CorrelationMap`'s own remaining pending entries directly (it doesn't need the Ledger — the `CorrelationMap` already knows everything it registered and never resolved) — this is achievable with the SAME new `discard_pending_correlation`/a bulk `drain_pending()` function, called once at `_finalize_at_end` time |
| 11 | Partial fills | `execution_simulator.py:327-348` (accumulate on same `client_order_id`); `portfolio_simulator.py:209` (one `TradeRecord` per partial exit fill) | Multiple `TradeRecord`s, same `client_order_id`, each with distinct `qty`/`price`/`net_pnl` | `capture_strategy_resolution`/`capture_portfolio_resolution`, called **once per partial** | Multiple distinct `Outcome`s (Finding C's proposed fix) — **not** today's first-wins/rest-dropped behavior | retire the pending entry only once the position/order is genuinely fully closed (needs the `remaining_qty`/`is_final` signal, Finding C) | Current: silent drop of every partial after the first. **Load-bearing gap — requires CEO decision per Finding C** | **YES — blocked on Finding C correction** |
| 12 | Bracket parent/TP/SL aliases | `execution_simulator.py:456-480` (`_activate_bracket_children`, materialized only after parent fills) | `decision.constraints.stop`/`.target` at decision time (already known, `harness.py:468-469` already reads `decision.constraints.stop` for `register_stop_hint`) | `register_pending_correlation` pre-registers `parent_id` always, `f"{parent_id}-TP"` iff `constraints.target is not None`, `f"{parent_id}-SL"` iff `constraints.stop is not None` — matching `builder.py:123-127`'s own `stop is not None or target is not None` bracket-trigger condition exactly | One `PendingCapture` reachable via 1-3 aliases; resolving any one retires all (`capture.py:145-147`, already correct) | already correct — no change needed here | already correct | **Partially already correct** — the ONLY fix needed is computing the alias SET conditionally on which of stop/target is actually set (today's `capture.py` docstring implies always-3; the real system can produce 1, 2, or 3 depending on `Constraints`) |
| 13 | End-of-run pending-state finalization | `harness.py:335-376` (`_finalize_at_end`) | Whatever remains in `CorrelationMap._pending` after the last bar's resolution attempts | New `drain_pending()`/`discard_pending_correlation` calls, one per remaining entry (row 7/10's proposed new function) | Every remaining pending entry is retired with **no** fabricated `Outcome` — an order that never filled produced no economic event and must not synthesize one | `CorrelationMap` ends the run with `pending_count() == 0`, always | should never raise; a non-empty pending set at end-of-run is an expected, disclosed outcome for interrupted/`STOPPED` runs, not a bug | **YES — needs the new function from rows 7/9/10** |

**No supported terminal lifecycle is left with an indefinite pending entry**, given the new
`discard_pending_correlation`/`drain_pending` function proposed in rows 7/9/10/13 is added. Without it,
rows 7, 9, and 10 currently have **no** disposition at all under the existing Phase E API — this is the
third concrete API gap this review found (alongside Findings B and C).

---

## 3. Cancellation / expiry / end-of-run cleanup design (summary)

Not implemented. The design direction, pending CEO authorization:
- Add `CorrelationMap.discard(run_id, client_order_id) -> PendingCapture | None` — same run-id-mismatch
  and unknown-key semantics as `pop_for_resolution`, but never touches Context Memory (no `Outcome`
  produced); retires all of the entry's own aliases together, exactly like `pop_for_resolution` does.
- Add `CorrelationMap.drain_pending() -> tuple[PendingCapture, ...]` — returns and retires every entry
  still pending, for `_finalize_at_end` to call once per run.
- `harness.py`'s own visibility gaps (rows 9/10: expiry and never-filled orders are not surfaced to
  `harness.py` at all today) are **execution-layer gaps**, not `learning_feedback` gaps — they need their
  own, separately-scoped fix in `execution_simulator.py`/`engine.py` (e.g. `advance_bar` returning
  terminal-non-fill events alongside fills) before Phase F can react to them bar-by-bar. Until then, the
  only correct behavior is the row-13 end-of-run sweep, which is sufficient to guarantee no *permanent*
  leak (bounded by run length) but cannot capture rejection/expiry/cancellation as *timely* diagnostic
  signal during the run.

## 4. Partial-fill compatibility verdict

**CONFLICT CONFIRMED** (Finding C). First-resolution-wins is not compatible with confirmed production
partial-fill semantics. Smallest proposed correction: retire only on a caller-supplied "this is the final
fill for this order/position" signal, not on the first successful resolution. Exact signal shape (a new
parameter threaded through `capture_strategy_resolution`/`capture_portfolio_resolution`, or a separate
explicit `finalize_position(...)` call) is a Phase F implementation decision, not resolved here.

## 5. Duplicate-emission prevention proof

- **Observation**: cannot be duplicated at the storage layer regardless of call count — `repository.py`'s
  own duplicate policy (`repository.py:36`, `_JsonlStream.append`, lines 241-267) is idempotent by content
  hash; a byte-identical `Observation` appended twice returns the same `ObservationId`, writes nothing
  twice. Proven structurally, not just by convention.
- **OperationalMetadata**: same idempotent guarantee applies at the storage layer. The remaining question
  — "does `harness.py`'s own `decision_batch.decisions` ever contain two decisions for the same
  `(observation_id, strategy_id)` in one bar?" — was **not fully resolved** in this review (would require
  reading `risk_manager/assembler.py`'s own opportunity-to-decision cardinality guarantee end to end,
  which decision_batch construction). Flagged as an open item to verify before Phase F implementation,
  not assumed either way.
- **Both Strategy and Portfolio outcomes for the same pending capture**: structurally prevented today by
  `entry.outcome_kind` isolation (`capture.py:231-236,263-268`) — a `PendingCapture` is tagged
  `STRATEGY` or `PORTFOLIO` at registration and the wrong-kind resolution function is rejected. This part
  of Phase E's design is sound and requires no change.
- **Outcomes for denied decisions**: structurally impossible — a DENY never reaches `execute()`, so no
  `client_order_id` is ever registered for one (row 6), so no resolution path can ever be attempted
  against it.
- **Duplicate outcomes through end-of-run finalization**: the proposed `drain_pending()` (§3) explicitly
  never produces an `Outcome` — it only retires bookkeeping state — so it cannot duplicate anything
  `capture_strategy_resolution`/`capture_portfolio_resolution` already wrote during the run.

## 6. Failure-severity matrix

| Failure | Current Phase E behaviour | Proposed Phase F classification |
|---|---|---|
| Unknown/duplicate-resolution `client_order_id` (after Finding B's fix) | drop+log, `None` | **expected drop-and-log** — genuinely can happen for a position opened before this run's own history starts, or (before Finding B's fix) is the current silent-majority-loss bug — must not remain silent until Finding B is fixed |
| `DuplicateDecisionCaptureError` at registration | `False`, log | **invariant violation** — two decisions registering the same `client_order_id` in one run means the correlation key itself collided; should be loud (at minimum a WARNING-level structured log with both decision ids), arguably fail-closed-the-run for a backtest (never silently continue with corrupted correlation state) |
| `UnmappedDenialCodeError` inside `capture_operational_metadata` | currently swallowed into generic `None` (capture.py:185-190) | **invariant violation, not a routine drop** — an unmapped denial code means Risk Manager emitted a code Phase D's own exhaustive mapping doesn't know about; this should be distinguished from an ordinary I/O failure, not folded into the same catch-all |
| Repository I/O failure (disk full, permission) inside any `capture_*` call | drop+log, `None`/`False` | **recoverable runtime issue** — log loudly, but a backtest run should not halt for a diagnostic-only write failure (Context Memory is explicitly never a learning target that gates trading behavior) |
| Order rejection / cancellation / expiry (rows 7-9) with no discard call issued (until Findings' fixes land) | pending entry leaks for the rest of the run, silently | **unsupported lifecycle today** — not actually causing incorrect Outcomes (nothing resolves against a leaked entry), but bloats `CorrelationMap` memory for a long run; end-of-run `drain_pending()` bounds it, but it is not "timely" observability |

The recommendation: Phase F must NOT let `capture_operational_metadata`'s current blanket `except
Exception` continue to swallow `UnmappedDenialCodeError` and `DuplicateDecisionCaptureError` identically
to an ordinary I/O failure — these two are genuine correctness invariants, not routine drops, and hiding
them defeats "the harness must retain sufficient observability for scientific audit" (CEO's own
requirement). Exact mechanism (re-raise a narrower exception type, a separate counter/metric,
a structured warning distinct from the routine drop-and-log path) is a Phase F implementation decision.

## 7. Exact files expected to change (when Phase F is authorized)

- `ai_trader/learning_feedback/capture.py` — add `discard`/`drain_pending` (§3), adjust
  `PendingCapture`/`CorrelationMap` for partial-fill-aware retirement (Finding C), adjust alias
  computation to be conditional on `constraints.stop`/`.target` individually (row 12).
- `ai_trader/learning_feedback/tests/test_capture.py` — new tests for the above.
- `ai_trader/simulation/harness.py` — the actual wiring: `CorrelationMap` construction using
  `self.context.run_id`; Observation/OperationalMetadata/pending-registration calls in the per-symbol
  decision loop; resolution calls after `portfolio_simulator.apply(fills, ...)` and
  `shadow_engine.settle_bar(...)`; `drain_pending()` call inside `_finalize_at_end`.
- Possibly `ai_trader/simulation/execution_simulator.py` / `ai_trader/execution_engine/engine.py` — only
  if the CEO decides rows 9/10 need timely (not just end-of-run) visibility, which requires new
  return/query surface for terminal-non-fill events. Not required for a correct (if less timely) Phase F.
- Possibly `ai_trader/simulation/harness.py` + a new call into `market_intelligence`/`edge_intelligence`
  — only if the CEO picks Finding A's Option 1. Not required if Option 2 (degraded snapshot) is chosen
  instead, in which case `ai_trader/decision_intelligence_v2/adapters.py` or a new, small
  harness-scoped adapter would change instead.

## 8. Exact tests required (when Phase F is authorized)

- Unit: `discard`/`drain_pending` semantics (retire without Outcome, alias-group retirement, run-mismatch
  rejection) in `test_capture.py`.
- Unit: partial-fill-aware retirement — N partial resolutions against one `client_order_id` before the
  final one, each producing a distinct `Outcome`, only the last one retiring the entry.
- Unit: conditional bracket alias computation — stop-only, target-only, both, neither.
- Harness-level integration (no mocking of `execution_simulator`/`portfolio_simulator`/`shadow_engine` —
  real objects, synthetic bars, per the DoD's own established "no harness-level shortcuts" convention
  from Phases A-E): a full run exercising (a) an ordinary entry+exit via a later opposite signal, proving
  the position-scoped correlation fix actually resolves it; (b) a bracket entry+TP fill; (c) a bracket
  entry+SL fill; (d) a denied decision producing only `OperationalMetadata`, no pending entry; (e) a
  position still open at `_finalize_at_end`, proving `drain_pending()` empties `CorrelationMap` with no
  Outcome fabricated for it; (f) confirming the Context Memory repository the run wrote to matches
  expectations (row counts, RESOLVED vs UNAVAILABLE mix) end to end.
- Regression: full existing `pytest ai_trader/simulation ai_trader/context_memory
  ai_trader/decision_intelligence_v2 ai_trader/decision_comparison ai_trader/learning_feedback
  ai_trader/shadow_evidence` plus mypy, to prove nothing in the six composed live modules changed
  behavior.

## 9. Flow A confirmation

Flow A remains completely untouched by this document and by everything it proposes — every file listed in
§7 is Flow B (`ai_trader/learning_feedback/`, `ai_trader/simulation/harness.py`,
`ai_trader/simulation/execution_simulator.py`, `ai_trader/execution_engine/engine.py`,
`ai_trader/decision_intelligence_v2/adapters.py`). Verified for this document itself:

```
$ git status --porcelain=v1 -- NEXT_SESSION_FLOW_A.md edge_research EDGE_DISCOVERY_REGISTRY_v1.md EDGE_RESEARCH_PROTOCOL.md EDGE_DISCOVERY_ROADMAP.md
(empty)
$ git diff --stat -- ai_trader/simulation/harness.py ai_trader/context_memory/evidence.py ai_trader/context_memory/retrieval.py
(empty)
```

---

## Summary recommendation

Do not begin Phase F implementation yet. Three concrete decisions are needed first:

1. **Finding A**: how (or whether) `harness.py` gains a Market Intelligence/Edge Intelligence integration
   at all — a real architectural decision, not a Phase F detail.
2. **Finding B**: authorize the position-scoped `(run_id, strategy_id, symbol)` correlation addition
   (mirroring Shadow Evidence's own already-working `open_position_id` design) alongside the existing
   `client_order_id` alias mechanism, which stays correct for the bracket sub-case only.
3. **Finding C**: authorize splitting "resolve" from "retire" so multi-partial-fill exits are not
   silently truncated to their first partial.

This document makes no code change and awaits explicit CEO authorization before Phase F implementation
begins, per the CEO's own instruction.
