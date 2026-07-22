# Learning/Research Feedback — Formal Lifecycle Specification

Status: **SPECIFICATION ONLY.** No code, no pseudocode, no implementation. Nothing in this document has
been implemented; `ai_trader/learning_feedback/` and `ai_trader/simulation/harness.py` are unchanged from
the state reported after Phase E (commit `c598676`) and the Phase F design review. No correlation key is
selected here — this document's purpose is to make the selection possible, by proving, from the real
source, exactly which identifier survives which transition.

Every claim below is either a direct citation (file:line, quoted) from this repository's real
implementation, or explicitly marked **[UNVERIFIED]** where the review could not establish a fact with
certainty and is flagging it rather than assuming it.

Two structurally different worlds are specified separately throughout, because §3 proves they are **not**
symmetric: the **Real/Portfolio** world (one shared account, `ai_trader/simulation/portfolio_simulator.py`)
and the **Shadow/Strategy** world (one fully isolated account per strategy,
`ai_trader/shadow_evidence/engine.py`). A correlation design that treats them identically would be wrong
for at least one of them — proven in §7.

---

## 1. Entity Catalog

For each entity: defining type, module, identifier field(s), mutability, and its single owning module
(the only module allowed to construct/mutate it).

| # | Entity | Type / file | Identifier field(s) | Mutable? | Owner |
|---|---|---|---|---|---|
| E1 | Opportunity | (Scoring Engine output, consumed by Risk Manager; no dedicated frozen type inspected in this review — carries `score_id`/`signal_id`, not itself a Context Memory concern) | `score_id`, `signal_id` | n/a | Scoring Engine |
| E2 | RiskDecision | `risk_manager/types.py:156-177` | `decision_id` | No — `frozen=True, slots=True` | Risk Manager (`risk_manager/assembler.py`) |
| E3 | OrderRequest | `execution_engine/types.py:187-215` | `client_order_id`, `order_request_id`, `decision_id` (carried) | No — `frozen=True, slots=True` | Execution Engine (`execution_engine/builder.py`) |
| E4 | OrderRecord (Ledger entry) | `execution_engine/ledger.py` (wraps `OrderRequest` + mutable `OrderState`) | `client_order_id` (Ledger key, `ledger.py:51-52`) | Yes — `state`/`filled_qty`/`reasons` change | Execution Engine (`pipeline.py`, `reconciler.py`, `lifecycle.py`) |
| E5 | WorkingOrder | `simulation/types.py:167-205`, `@dataclass(slots=True)` (mutable) | `client_order_id` | Yes — `state`, `filled_qty`, `avg_price` | Execution Simulator (`simulation/execution_simulator.py`) |
| E6 | Bracket child WorkingOrder (TP/SL) | same type as E5, distinct instances | `f"{parent.client_order_id}-TP"` / `"-SL"` | Yes (same as E5) | Execution Simulator (`_activate_bracket_children`, `execution_simulator.py:456-480`) |
| E7 | SimFillEvent | `simulation/types.py:208-230`, `frozen=True` | `client_order_id` (carried, not a fresh id) | No | Execution Simulator (`_match_one`, `execution_simulator.py:327-352`) |
| E8 | Position (real) | `simulation/portfolio_simulator.py:28-46`, `@dataclass(slots=True)` (mutable) | **none of its own** — identity is the `symbol` dict key in `SimAccount.positions: dict[str, Position]` (`:89`) | Yes — `size`, `avg_entry`, `strategy_id`, `mfe`, `mae` | Portfolio Simulator (`_apply_one`, `portfolio_simulator.py:164-226`) |
| E9 | TradeRecord (real) | `simulation/portfolio_simulator.py:49-69`, `frozen=True` | `client_order_id` (= the closing fill's own id, or `f"LIQUIDATION-{symbol}-{as_of}"`) | No | Portfolio Simulator (`_apply_one:208-214`, `_liquidate:323-328`) |
| E10 | `_PendingEntry` (Shadow) | `shadow_evidence/engine.py` (~line 107-110) | `position_id` | Yes, until promoted or discarded | Shadow Evidence (`ShadowEvidenceEngine`) |
| E11 | `position_id` (Shadow) | plain `str`, not a dataclass | itself the identifier | No (never reassigned once minted) | Shadow Evidence (`engine.py:310`) |
| E12 | ShadowPositionRecord | `shadow_evidence/types.py:69+` | `position_id` | Replaced wholesale on each leg event (new frozen instance, same id) under `self._positions[position_id]` | Shadow Evidence |
| E13 | ShadowTradeLegRecord | `shadow_evidence/types.py:130+`, `frozen=True` | none of its own; carries `leg: TradeRecord` + `position_id` (FK) | No | Shadow Evidence (`_record_new_trade_legs`, `engine.py:460-473`) |
| E14 | Outcome | `context_memory/contracts.py:315-458`, `frozen=True` | `EdgeEvidenceId` (content hash, `identities.py::compute_edge_evidence_id`) | No — append-only | `learning_feedback/adapters.py` (`build_strategy_outcome`/`build_portfolio_outcome`) |
| E15 | Observation | `context_memory/contracts.py:252-307`, `frozen=True` | `ObservationId` (content hash) | No — append-only | `learning_feedback/capture.py` (`capture_decision_observation`), blocked today per Finding A |
| E16 | OperationalMetadata | `context_memory/contracts.py:479-519`, `frozen=True` | `OperationalMetadataId` (content hash) | No — append-only | `learning_feedback/capture.py` (`capture_operational_metadata`) |
| E17 | PendingCapture (Phase E, proposed correlation state) | `learning_feedback/capture.py:79-96`, `frozen=True` | today: `client_order_ids: tuple[str,...]` | No (whole object replaced on registration) | `learning_feedback/capture.py::CorrelationMap` |

---

## 2. Ownership boundaries

Six modules, each owning exactly the entities listed, with zero write access to another module's
entities (verified by import/call-site inspection across all prior investigations in this session):

- **Risk Manager** (`risk_manager/`) owns E1→E2. Never constructs an order, fill, or position.
- **Execution Engine** (`execution_engine/`) owns E3, E4. Never touches `SimAccount`/`Position` directly
  — it only returns `OrderStatus` (a value, not E8/E9) to its caller.
- **Execution Simulator** (`simulation/execution_simulator.py`) owns E5, E6, E7. It is a `BrokerAdapter`
  implementation from Execution Engine's point of view — Execution Engine never reaches into its
  `WorkingOrder` book directly; it only sees `BrokerAck`/`BrokerOrderState`/`Fill` (its own contract
  types, `execution_engine/types.py`).
- **Portfolio Simulator** (`simulation/portfolio_simulator.py`) owns E8, E9. It is the *sole* writer of
  `SimAccount.positions`/`trade_ledger` — confirmed no other module imports `Position`/mutates
  `SimAccount` (only `harness.py` calls `.apply()`/`.to_portfolio_state()`/`.mark_to_market()`/
  `.register_stop_hint()`/`.record_risk_event()`, all public methods, never touching `.account.positions`
  directly except read-only at `harness.py:353,524,528,536` for liquidation/overlay bookkeeping).
- **Shadow Evidence** (`shadow_evidence/engine.py`) owns E10-E13, and internally **also** owns its own
  private instances of E2-E9 (one full Risk Manager/Execution Engine/Execution Simulator/Portfolio
  Simulator per strategy, `_account_for`, `engine.py:200-217`) — a structurally separate, parallel copy
  of the entire E1-E9 chain, not a view onto the real one.
- **Context Memory + `learning_feedback`** own E14-E17. Zero write access to any of E1-E13 (confirmed:
  `context_memory` has zero import dependency on any of the other packages — Checkpoint 9's own design
  choice, `context_memory/enums.py:1-24`).

**Consequence**: any correlation mechanism Phase F builds must live entirely inside `learning_feedback`
(or `harness.py`'s own orchestration of it) — it cannot be pushed down into `portfolio_simulator.py`/
`execution_simulator.py` without violating their existing ownership boundaries (a change those modules'
own docs describe as frozen/stable production code, Flow A-adjacent in spirit even though technically
Flow B's own simulation core). This is a design constraint, not a preference.

---

## 3. Formal state machine

### 3A. Real/Portfolio path

```
[E2 RiskDecision]
   | risk_manager/assembler.py:33 -- decision_id = f"{strategy_id}|{symbol}|{as_of}"
   | ALLOW only (harness.py:464-466)
   v
[E3 OrderRequest] --- builder.py:148-153: client_order_id = f"{prefix}-{decision_id}"
   |                   (exactly ONE per RiskDecision -- builder.py:118-134, confirmed no branch
   |                    produces more than one OrderRequest; BracketLegs is a nested price pair,
   |                    not a second order)
   v
[E4 OrderRecord, Ledger] --- pipeline.py:107-133
   |  branch A: VALIDATION FAILURE -> REJECTED (terminal, no fill ever)         [see 3A-i]
   |  branch B: BROKER REJECTS (ack.accepted=False) -> REJECTED (terminal)      [see 3A-i]
   |  branch C: adapter.submit_order raises -> FAILED (terminal)                [see 3A-i]
   |  branch D: accepted -> QUEUED -> (adapter-internal) ACKNOWLEDGED
   v
[E5 WorkingOrder, Execution Simulator book] --- keyed by the SAME client_order_id as E3/E4
   |  per advance_bar() call (harness.py:562):
   |  - no data this cycle -> stays working, unterminal                        (execution_simulator.py:218-220)
   |  - as_of > valid_until -> EXPIRED (terminal, no fill)                     [see 3A-ii]     (execution_simulator.py:215-217,440-443)
   |  - FOK not fully fillable -> CANCELLED "FOK_NOT_FILLED" (terminal)        [see 3A-iii]    (execution_simulator.py:427-428)
   |  - IOC remainder -> CANCELLED "IOC_UNFILLED_REMAINDER"/"...PARTIAL..."    [see 3A-iii]    (execution_simulator.py:436-437)
   |  - explicit cancel_order() call -> CANCELLED "CANCEL_REQUESTED"          [see 3A-iv]      (execution_simulator.py:162-171)
   |     (not currently called from harness.py -- see Finding, row 8 of the prior design review)
   |  - would_trigger -> fill_qty computed (FULL_FILL or FIXED_FRACTION policy)
   v
[E7 SimFillEvent] --- _match_one, execution_simulator.py:327-352
   |  MAY repeat: PartialFillPolicy.FIXED_FRACTION can produce MULTIPLE SimFillEvents for the
   |  SAME WorkingOrder/client_order_id across multiple bars (confirmed :408-414)
   |  IF order_type is BRACKET and this fill FULLY closes the WorkingOrder (remaining_qty<=1e-12):
   |     -> _activate_bracket_children (execution_simulator.py:456-480) births E6 (TP, SL, or both,
   |        conditional on which of BracketLegs.take_profit/stop_loss is non-None)
   |     -> the losing E6 sibling is later CANCELLED "OCO_SIBLING_FILLED" (terminal, no fill)  [see 3A-v]
   v
[E8 Position] --- portfolio_simulator.py::_apply_one, keyed SOLELY by fill.symbol (:166)
   |  branch OPEN (existing is None, not reduce_only): new Position born, strategy_id=fill.strategy_id (:174-178)
   |  branch SCALE-IN (same direction, not reduce_only): existing Position MUTATED in place,
   |     weighted-average avg_entry/size (:181-186) -- strategy_id is NOT reassigned here
   |  branch REDUCE/CLOSE (opposite direction OR reduce_only): (:188-226)
   |     -> births E9 TradeRecord (client_order_id = fill.client_order_id, strategy_id = EXISTING
   |        position's strategy_id, i.e. the ORIGINAL owner, NOT necessarily fill.strategy_id -- :209)
   |     -> existing.size -= close_qty; if size<=1e-9: del acct.positions[fill.symbol]  (Position DIES)
   |     -> IF remainder>0 and not reduce_only (a "flip"): a NEW Position is born at the SAME
   |        symbol key, strategy_id = fill.strategy_id (THE FLIPPING FILL's OWN strategy -- may
   |        differ from the position that just died) (:220-226)
   |  NOTHING IN THIS FUNCTION COMPARES fill.strategy_id TO existing.strategy_id -- confirmed by
   |  full read of _apply_one (:164-226): a reduce/close fill from ANY strategy_id will close
   |  whatever Position currently occupies that symbol slot.
   v
[E9 TradeRecord] --- one per closing fill (partial or full); MAY repeat under the SAME
   |  client_order_id (multiple partial-exit fills of one WorkingOrder each produce their own
   |  TradeRecord, confirmed PORTFOLIO_SIMULATOR.md:64-66: "one record per closed trade (and per
   |  partial exit)")
   v
[E14 Outcome, PORTFOLIO kind] --- learning_feedback/adapters.py::build_portfolio_outcome
      RESOLVED (pnl_r present) or UNAVAILABLE (pnl_r None) -- Phase D, unchanged by this document
```

**3A-i / ii / iii / iv / v — terminal-without-fill dispositions, all currently unobserved by any code in
`learning_feedback`** (this restates, with exact line citations, the three gaps the Phase F design review
already found — rows 7/8/9 of that document — now placed precisely in the formal chain above rather than
described in prose only).

### 3B. Shadow/Strategy path

Structurally identical E2→E9 chain, but every instance (Risk Manager, Execution Engine, Execution
Simulator, Portfolio Simulator) is its own strategy-private object (`_account_for`, `engine.py:200-217`),
using the `SHADOW-CID`/`SHADOW-REQ` prefixes (`_SHADOW_EXEC_CONFIG`, `engine.py:68`). Shadow overlays one
**additional** identifier and one **additional** state machine on top:

```
[Shadow decision, ALLOW] --- engine.py ~line 300-312
   v
[E11 position_id] = f"{run_id}:{strategy_id}:{symbol}:{as_of}:{decision.decision_id}"   engine.py:310
   |   BORN here -- BEFORE the virtual entry order is known to have filled. Stored on a
   |   provisional E10 _PendingEntry, not yet a live position.
   v
[virtual entry fill confirmed]
   |  account.open_position_id[symbol] = pending.position_id                             engine.py:444
   |  self._positions[pending.position_id] = ShadowPositionRecord(...)                    engine.py:438-439
   |  -- position_id is now LIVE (queryable via open_position_id[symbol])
   |  -- if the virtual entry NEVER fills, position_id simply stays on the discarded
   |     _PendingEntry, is never promoted, and never becomes a correlation-relevant identifier
   v
[every subsequent closing/reducing Shadow fill, ANY mechanism -- ordinary exit, time-stop,
 trailing-stop, bracket TP/SL, window-end forced close]
   |  position_id = account.open_position_id.get(trade.symbol)     engine.py:463
   |     (defensive raise if None -- engine.py:464-470 -- "a closing fill implies a tracked
   |     open position_id," treated as an invariant, not a routine miss)
   |  self.trade_legs.append(ShadowTradeLegRecord(leg=trade, position_id=position_id, ...))  engine.py:473
   |  self._positions[position_id] = ShadowPositionRecord(...)  (replaced, same id)          engine.py:476-477
   |  IF fully closed: del account.open_position_id[trade.symbol]                            engine.py:487
   |     -- position_id DIES as a live lookup key here; the E12/E13 records referencing it
   |     persist permanently in Shadow's own store
   v
[E14 Outcome, STRATEGY kind] --- learning_feedback/adapters.py::build_strategy_outcome
      consumes the LATEST ShadowPositionRecord (by position_id) + the specific closing
      ShadowTradeLegRecord.leg (a TradeRecord, same type as E9)
```

Crucially, `open_position_id` is keyed by `symbol` **alone**, exactly like the real side's
`acct.positions` — but because each strategy owns a **structurally separate** `open_position_id` dict
instance (one per `_account_for(strategy_id)`), the *effective* global key is `(strategy_id, symbol)`
with **zero risk of cross-strategy interference** — a different, and safer, guarantee than the real side
has (§3A: real `strategy_id` on `Position` is a mutable attribute of a symbol-keyed slot shared by every
strategy, not a namespace).

---

## 4. Cross-cutting invariants (verified, with citations)

- **I1 — One order per decision (real side)**: `builder.py:118-134`'s branching always produces exactly
  one `OrderRequest`, one `client_order_id`, regardless of bracket/reduce/limit/market. No code path
  anywhere in `execution_engine/` constructs a second order from one `RiskDecision`.
- **I2 — Bracket children are derived, not decided at build time, and independently conditional**:
  `{parent}-TP`/`{parent}-SL` (`execution_simulator.py:464,473`) exist **only if and after** the parent
  WorkingOrder fully fills (`:343,346`), and **confirmed by direct read** (`_activate_bracket_children`,
  `:456-480`): `if plan.take_profit is not None:` (`:463`) and `if plan.stop_loss is not None:` (`:472`)
  each independently gate creation of their own child — `plan is None or (plan.take_profit is None and
  plan.stop_loss is None)` short-circuits entirely (`:458`) if neither leg exists. So the true alias
  count is 1 (no bracket, or a bracket with neither leg set — degenerate/unreachable via `builder.py`'s
  own `elif stop is not None or target is not None:` gate), 2 (parent + exactly one child), or 3 (parent +
  both children) — **never assume 3**; the correct alias-registration rule is
  `{parent_id}` always, `{parent_id}-TP` iff `decision.constraints.target is not None`,
  `{parent_id}-SL` iff `decision.constraints.stop is not None`, computed independently, not as a single
  three-way branch.
- **I3 — Real Position identity is symbol-only, account-wide**: `acct.positions: dict[str, Position]`
  (`portfolio_simulator.py:89`) has no per-strategy partition. `_apply_one` (`:164-226`) never checks
  `fill.strategy_id == existing.strategy_id`. **A reduce/close fill from a different strategy than the
  one that opened the position will close it anyway**, attributing the resulting `TradeRecord` to the
  *original* opener's `strategy_id` (`:209`, uses `existing.strategy_id`) — and a flip attributes the
  *new* Position to the *closing* fill's own `strategy_id` (`:223`), which can differ from both. Whether
  **Partially verified**: `check_max_per_symbol` (`risk_manager/limits.py:46-51`) counts
  `portfolio.open_positions` matching `symbol` (`:47`, no `strategy_id` filter — account-wide) and denies
  a **new opening** decision once `count >= limit`. Since `acct.positions` holds at most one `Position`
  per symbol (this same invariant), a `max_per_symbol` of 1 (plausible default — exact configured value
  **[UNVERIFIED]**) would block a *second strategy from opening* a symbol another strategy already holds.
  **This does not resolve the flip risk**: `check_max_per_symbol` gates *opening* decisions only; nothing
  found in `risk_manager/limits.py`/`guards.py`/`sizing.py` re-checks "does this reduce_only/opposite-
  direction decision's own `strategy_id` match the position's current owner" for a *closing* decision.
  Whether some other, not-yet-found mechanism prevents a different strategy from submitting a reduce-only
  decision against a symbol it doesn't own remains **[UNVERIFIED]**. This spec conservatively treats the
  flip/cross-strategy-close risk (§7) as live rather than assuming it away.
- **I4 — Shadow Position identity is strategy-namespaced, symbol-keyed within that namespace**: proven in
  §3B — structurally safe from I3's cross-strategy risk, because each strategy's `open_position_id` dict
  is a physically separate object.
- **I5 — `client_order_id` survives exactly one order's own fills, never a subsequent order's**: proven
  in §0/Finding B of the prior design review (time-stop/trailing-stop/ordinary-exit/liquidation all mint
  new, structurally unrelated ids) — restated here as a formal invariant because it is the central fact
  the canonical key selection depends on.
- **I6 — Outcome/Observation/OperationalMetadata are append-only and idempotent by content hash** —
  `context_memory/repository.py:36,241-267` — already proven in the prior design review's §5, unchanged.
- **I7 — A DENY decision never produces `client_order_id`, `WorkingOrder`, `Fill`, `Position`, or
  `TradeRecord`** — `pipeline.py:172-177` intercepts before any `OrderRequest` is built; confirmed in the
  prior design review.

---

## 5. Terminal states catalog

| Entity | Terminal states | Produces a Learning Outcome? |
|---|---|---|
| E4 OrderRecord | `FILLED, CANCELLED, REJECTED, EXPIRED, FAILED` (`execution_engine/types.py:92-94`) | Only via the E5→E7→E9 chain if `FILLED`; the other four are terminal-without-fill |
| E5/E6 WorkingOrder | `FILLED, CANCELLED, REJECTED, EXPIRED` (`simulation/types.py:160-163`) | Same as above |
| E8 Position | deleted from `acct.positions` (no explicit "closed" state — deletion IS the terminal transition), OR forcibly closed via `_liquidate` | Yes, via the TradeRecord that closed it |
| E11 position_id (Shadow) | removed from `open_position_id` (`engine.py:487`) — the id itself never becomes invalid, only stops being a *live* lookup key | Yes, via the ShadowTradeLegRecord that closed it |
| E14 Outcome | none — append-only, immutable forever once written | n/a (it IS the terminal record) |

**No terminal state is currently swept into a Context Memory disposition** except the fill-producing path
(E7→E9→E14). This is Finding B/row-7/9/10 restated formally: every non-fill terminal state (E4/E5
REJECTED/CANCELLED/EXPIRED/FAILED) has an entity-level terminal state defined by the *existing* production
code, but no `learning_feedback` function consumes it today.

---

## 6. Identifier survival matrix

For every identifier: where born, where (if ever) it changes, where it dies, and — the determining
question for a correlation key — **does it survive from Position-open to Position-close, for every
closing mechanism (not just the bracket case)?**

| Identifier | Born | Changes | Dies | Survives open→close (ALL mechanisms)? |
|---|---|---|---|---|
| `decision_id` (E2) | `risk_manager/assembler.py:33` | never (frozen) | conceptually irrelevant after `execute()` consumes it once | **No** — a new one is minted for every later decision, including the one that eventually closes the position |
| `client_order_id` (E3/E4/E5/E7/E9, real) | `builder.py:153` | never (same string threaded through E3→E9) | ceases to be *correlation-relevant* once its own order reaches a terminal state | **No**, except for the specific bracket-child derivation (E6), which survives from the PARENT's fill to that SAME order's own TP/SL resolution — not to a later, independent order |
| `symbol` (dict key, real `Position`) | at Position birth (`portfolio_simulator.py:174`) | never changes (it IS the dict key) | when `del acct.positions[symbol]` | **Yes, always** — every closing code path (`_apply_one`, `_liquidate`) looks up the position by `symbol` alone before booking the TradeRecord |
| `Position.strategy_id` (real, an attribute, not a key) | at Position birth, = opening fill's `strategy_id` | **reassigned on a flip** to the flipping fill's own `strategy_id` (`:223`) | dies with the Position | **Yes for the closing TradeRecord's own `strategy_id` field** (`:209` uses the position's CURRENT `strategy_id`, whatever it is at close time) — but this is NOT a stable value across the position's own lifetime if a flip occurred, so it cannot safely be a correlation-map KEY component decided once at open time |
| `run_id` (`SimulationContext.run_id`) | run construction (`simulation/config.py:130`) | never | end of run | **Yes, trivially — spans everything** |
| `position_id` (E11, Shadow only) | `engine.py:310`, at decision time (before fill confirmation) | never reassigned | removed from `open_position_id` on full close (`:487`), but the id string itself persists forever as a FK on E12/E13 | **Yes, always** — proven in §3B, this is Shadow's own already-correct, already-implemented answer |
| `(strategy_id, symbol)` as a compound key, Shadow | implicit (one `open_position_id` dict per strategy) | never | when the strategy's own `open_position_id[symbol]` entry is deleted | **Yes** — safe due to I4 (structural per-strategy isolation) |
| `(strategy_id, symbol)` as a compound key, real | n/a (no such key exists in the real implementation) | n/a | n/a | **No** — I3 proves `strategy_id` is not stable for a real Position across a flip, and is not even part of the real dict's own key today |

**Conclusion, proven rather than assumed**: on the real/Portfolio side, the only identifier proven to
survive every closing mechanism (ordinary exit, time-stop, trailing-stop, bracket, liquidation, flip) is
**`symbol` alone** (scoped by `run_id`). On the Shadow/Strategy side, Shadow already has, and uses, a
purpose-built survivor: **`position_id`**, and the review found no reason to duplicate or replace it —
Shadow does not need help from `learning_feedback`, only a purely-*reading* integration.

---

## 7. Proposed canonical correlation key (derived from §6, not assumed)

**This section proposes; it does not select.** Per the CEO's instruction, selection happens after this
document is reviewed.

- **PORTFOLIO-kind (real) correlation key**: `(run_id, symbol)` — **not** `(run_id, strategy_id, symbol)`.
  Including `strategy_id` in the key would be *actively wrong* whenever a flip reassigns the position to a
  different strategy mid-lifetime (I3) — the entry registered under the original strategy's id would
  never be found by a resolution keyed on the new owner's id, silently leaking the same way Finding B
  already described for `client_order_id`. **A genuinely new, fourth gap this document discovered**: even
  `(run_id, symbol)` is only correct if the correlation entry itself is updated (not just looked up) at
  flip time — a flip both closes the OLD position (needs its own Outcome, keyed to whatever decision
  opened it) and opens a NEW one (needs a fresh registration, keyed to the flipping decision) — Phase F
  must handle a flip as "resolve one pending entry AND register a new one," atomically, in one fill
  event. Not designed here; flagged for the CEO's decision alongside Findings A-C.
- **PORTFOLIO-kind, second finding**: `Position` (E8) has **no identifier of its own** at all — unlike
  Shadow's `position_id`, the real side has nothing to mirror. The smallest correction is for
  `learning_feedback` to maintain its **own** external position-tracking state (an
  `open_position_key: dict[str, PendingCapture]` keyed by `symbol`, updated on every real fill exactly as
  `_apply_one` updates `acct.positions` — open/scale-in/reduce/close/flip, mirrored one-for-one) rather
  than modifying `portfolio_simulator.py` itself (respecting the ownership boundary in §2). This can be
  built without changing any frozen module — `harness.py` already sees every `SimFillEvent`
  (`fills = self.execution_simulator.advance_bar(...)`, `harness.py:562`) before handing them to
  `portfolio_simulator.apply()`, so a parallel, read-only tap is possible.
- **STRATEGY-kind (Shadow) correlation key**: `(run_id, position_id)`, using Shadow's own already-existing
  `position_id` (E11) directly — no new identifier needed, no derived tracking needed.
  `capture_strategy_resolution` should be re-pointed to key off `ShadowTradeLegRecord.position_id`, not
  `TradeRecord.client_order_id` (the latter is still available on `leg.client_order_id` for diagnostic/
  audit purposes, just not as the correlation key).
- **`client_order_id`'s remaining role**: still useful, but demoted from "the correlation key" to "a
  per-fill identity used only to detect true duplicate resolution of the SAME fill" (Finding C's own
  partial-fill problem) — orthogonal to *which position* an Outcome belongs to.

---

## 8. What this document does not resolve

- Finding A (Market Intelligence/Edge Intelligence ownership) — untouched, still an architectural
  blocker, not addressed by this lifecycle work.
- I2's unconfirmed bracket-child-creation conditionality — needs a direct source read before
  implementation.
- I3's open **[UNVERIFIED]** question of whether Risk Manager/Portfolio Architect already prevents
  cross-strategy symbol contention upstream (if it does, §7's flip-handling gap is unreachable in
  practice and can be deprioritized; if not, it is a live risk).
- Finding C (partial-fill incremental-vs-terminal Outcome semantics) — the CEO's own new questions
  (incremental vs terminal Outcome, whether aggregation happens before persistence, when a position
  becomes "eligible" for Learning Feedback) are not answered here; this document only establishes which
  identifier is available at each point in the chain that any answer to those questions would attach to.
- No implementation, no test, no wiring change. `git status` for this session's design-only work:

```
$ git status --porcelain=v1
?? LEARNING_FEEDBACK_LIFECYCLE_SPECIFICATION.md
?? LEARNING_FEEDBACK_PHASE_F_INTEGRATION_DESIGN.md
```

Both documents are uncommitted, pending review. Flow A and every frozen module remain untouched (same
zero-diff proof as the prior design review — re-verified, unchanged, at the time of this writing).

Awaiting CEO review before any canonical key is formally selected or any Phase F implementation begins.
