# AI Trader — Decision Logic Audit

**Mode: READ-ONLY.** No code, configuration, threshold, or document logic was modified to produce this
report (only two pre-existing documentation inaccuracies were corrected in passing, per explicit
instruction — see the commit this lands in). No live signal source was built. No Phase 1-10 code was
touched. No 5%-sizing logic was implemented. Repo `ai_quant_lab-research-main`, branch
`ai-trader-implementation`, second in the CEO's stated audit sequence (after the Knowledge Transfer
Audit).

## Scope

How `TradeProposal`/`ApprovedTradeIntent` construction, confidence grading, and risk sizing interact
end-to-end — **logic correctness**, not structural/type correctness (the latter is already covered by
the 277 unit tests catalogued in `AI_TRADER_TEST_STATUS.md`, all of which pass). Concretely: does the
data that actually flows through `execution_orchestrator.orchestrate()` — from `CandidateSignal` through
`TradeProposal`, `ConfidenceAssessment`, `LiveRiskDecision`, and `ApprovedTradeIntent`, down to the
`OrderRequest` handed to Order Manager — mean what its own field names and design docs claim it means,
consistently, at every hop? **Portfolio Manager's exposure/conflict logic and MT5-level safety controls
were deliberately not re-examined here** — the former is the natural subject of the still-pending "Risk
Audit," the latter was already operationally validated in Phase 10/the BTCUSD test; re-auditing either
would blur this audit's scope rather than sharpen it.

## Method

Direct reading of the actual source — `execution_orchestrator/engine.py` (full), `confidence_engine/
engine.py`+`types.py` (full), `risk_manager_live/engine.py`+`types.py` (full), `risk_manager/sizing.py`+
`config.py` (full), `recognition_engine_live/engine.py`+`patterns.py` (full), `order_manager/builder.py`+
`engine.py` (relevant sections), `execution_orchestrator/types.py`'s `CandidateSignal`/
`OrchestratorConfig`, `execution_engine/types.py`'s `OrderRequest`. Every finding below cites the exact
file and is traceable to a specific line of code actually read, not inferred from a design doc's
description of what the code is supposed to do.

---

## Findings

### 1. Confidence-grade-to-position-size scaling is dead code for every trade that can actually reach it

`risk_manager/sizing.py::compute_sizing` scales the risk budget by a `quality_factor` meant to give
higher-confidence trades a larger risk allocation: `effective_risk_pct = risk_per_trade_pct *
quality_factor`. `risk_manager/config.py`'s `QUALITY_FACTOR` table maps `Quality.POOR/WEAK → 0.5`,
`MODERATE → 0.75`, `STRONG/PREMIUM → 1.0`. `confidence_engine/types.py`'s `GRADE_TO_QUALITY` maps
`Grade.A → PREMIUM`, `Grade.B → STRONG`, `Grade.C → MODERATE`, `Grade.D → WEAK`.

But `ConfidenceAssessment.__post_init__` (`confidence_engine/types.py:102-103`) makes it a **structural
invariant** that only Grade A or B may ever be `eligible_for_risk_evaluation=True`, and
`execution_orchestrator/engine.py:135-142` only builds a `TradeProposal` — the object that eventually
reaches `compute_sizing` — when `confidence.eligible_for_risk_evaluation` is `True`. **Grade C and D
proposals never reach risk sizing at all**, which is by design (correctly fail-closed). The consequence
that does not look designed: **Grade A → PREMIUM → quality_factor 1.0, and Grade B → STRONG → quality_
factor 1.0 — the same value.** Every trade that can structurally reach `compute_sizing` today receives
the identical quality_factor (1.0), regardless of whether it was graded A or B. The 0.75/0.5 quality-scaled
tiers exist in the arithmetic but are permanently unreachable given the current eligibility gate and the
current `GRADE_TO_QUALITY` mapping — the "quality-scaled position sizing" the design docs describe does
not, in the live wiring as it stands, actually scale anything.

**Not a claim that this is wrong** — treating A and B identically for sizing purposes may be entirely
intentional (both cross the same "eligible" bar). But it is worth an explicit decision one way or the
other, since right now it is an emergent consequence of two independently-designed mappings interacting,
not a stated choice anywhere.

### 2. No stop-loss/direction consistency check exists anywhere in the pipeline

Read in full: `CandidateSignal.__post_init__` (`execution_orchestrator/types.py:58-68`),
`TradeProposal.__post_init__` (`risk_manager_live/types.py:33-46`), `ApprovedTradeIntent.__post_init__`
(`order_manager/types.py:44-58`), and `evaluate_trade_proposal`'s own calculability gate
(`risk_manager_live/engine.py:109-120`). **None of them validates that `stop`/`target` sit on the correct
side of `entry` for the stated `direction`** (for a LONG, a logically valid stop-loss is below entry and
a take-profit above; for a SHORT, the reverse). The only check performed anywhere is
`stop_distance = abs(entry - stop)`, which is direction-agnostic — it is satisfied equally by a correct
stop and by one on the wrong side of entry. A malformed or buggy signal source (once built — none exists
today, `AI_TRADER_PROJECT_STATE.md` §7) could hand the orchestrator a LONG candidate with a stop *above*
entry, and it would pass every existing gate, get sized by `compute_sizing` (which only uses the
magnitude of the distance, not its sign relative to direction), and be submitted as a structurally
backwards bracket order — silently.

### 3. `CandidateSignal.magic_number`/`.comment` are validated, threaded through, and then discarded before reaching the broker

`CandidateSignal` requires non-empty `magic_number`/`comment` (`execution_orchestrator/types.py:54-66`,
`comment` checked in `__post_init__`). The orchestrator copies both straight into `ApprovedTradeIntent`
(`execution_orchestrator/engine.py:199`). `order_manager/engine.py::process_approved_intent` reads
`intent.magic_number`/`intent.comment` — **but only to write them into the audit journal**
(`order_manager/engine.py:55-56,74`). `order_manager/builder.py::build_order_request`, which constructs
the actual `OrderRequest` that flows downstream, never reads either field — confirmed by reading the
function in full (`order_manager/builder.py:49-103`); `OrderRequest` itself
(`execution_engine/types.py:187-215`) has **no `magic_number` or `comment` field at all**. The real MT5
payload's `magic`/`comment` are instead computed independently and deterministically by
`mt5_demo_execution/request_builder.py`'s `_magic_number_for(order.client_order_id)`/
`_comment_for(order.strategy_id, order.decision_id)` — values derived from `client_order_id`/
`decision_id` (themselves derived from `intent.proposal_id`), not from `intent.magic_number`/`.comment`
at all. **A caller-supplied value meant to tag a specific order at the broker is validated, recorded in
the audit journal, and then silently has no effect on the order actually sent** — the field names imply
a guarantee ("this magic number/comment will identify the order") that the code does not keep. This
matches the exact pattern already flagged once for the Strategy Library's evidence fields in
`AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` §3.2 (data loaded, validated, and then structurally ignored) —
worth noting this is not a one-off, but a recurring shape in this codebase.

### 4. Recognition Engine's confidence contribution is keyed to one fixed dimension, not to the strategy's own thesis

`recognition_engine_live/engine.py::recognize` (confirmed by full read) correctly keys its historical
statistics query by **both** `strategy_id` and `pattern.dimension`
(`compute_conditional_statistics(repository, candidate.strategy_id, pattern.outcome_kind,
pattern.dimension, policy)`, line 58) — so the "favorable_rate" that feeds `confidence_engine` genuinely
is that specific strategy's own historical performance, not a generic pool. However, **which single
dimension gets checked is fixed per orchestration call, not per strategy**:
`OrchestratorConfig.recognition_pattern_id` defaults to `"REC-SESSION-STRATEGY"`
(`execution_orchestrator/types.py:76`) — always the SESSION dimension unless a caller explicitly
overrides it — and `CandidateSignal` carries no field indicating which of the 15
`AUTHORIZED_PATTERNS` dimensions its own edge thesis actually concerns. A strategy whose real premise is,
say, a volatility-regime effect would, under the default configuration, have its confidence grade partly
built from "how has this strategy performed conditioned on session" — a dimension unrelated to its own
stated logic — unless the orchestrator's caller manually supplies a different, matching
`recognition_pattern_id` for that specific strategy on that specific call. Since `recognition_pattern_id`
is one static value per `orchestrate()` invocation, not a per-candidate lookup, there is no mechanism
today for the system to pick the dimension a given strategy actually cares about automatically.

### 5. `LiveRiskDecision`'s approved⇒populated-fields invariant is enforced by a bare `assert`, not by the type itself, and not inside the module's own fail-closed try/except pattern

`risk_manager_live/types.py`'s `LiveRiskDecision.__post_init__` (lines 141-150, read in full) enforces
only two invariants: approved ⇒ non-empty `calculation_trace`, and denied ⇒ non-empty `reason_codes`. It
does **not** enforce "approved ⇒ `calculated_volume`/`monetary_risk`/`approved_risk` are non-`None`",
even though all three are typed `float | None`. `execution_orchestrator/engine.py:166-167` instead
guards this with two bare `assert` statements, sitting *between* two `try`/`except` blocks rather than
inside either. This is weaker than every other check in the same function, which is otherwise
consistently wrapped in `try: ... except Exception: return _denied(...)` per the module's own stated
contract ("Fail-closed throughout: any exception at any stage aborts the run, never propagates" —
`execution_orchestrator/engine.py:5`). A bare `assert` (a) is stripped entirely if Python is ever run
with `-O`, and (b) if it does fire, raises `AssertionError` uncaught, breaking that documented
"never propagates" guarantee. **Confirmed currently unreachable**: `evaluate_trade_proposal`'s only
`approved=True` return path (`risk_manager_live/engine.py:203-208`) unconditionally supplies all three
fields as real floats, so the assert cannot fire against today's code. But nothing in the type system
prevents a future edit to `evaluate_trade_proposal` — or any other caller, since `LiveRiskDecision` is a
plain public dataclass anyone can construct — from producing `approved=True` with one of these fields
`None`, and the orchestrator would then either silently skip the check (`-O`) or crash out of its own
documented fail-closed contract.

---

## What was checked and found consistent (not just assumed)

- **Reason-code discipline**: every deny path read in `evaluate_trade_proposal`, `assess_confidence`, and
  `orchestrate` itself carries at least one reason code, and every approved/eligible result carries a
  non-empty trace — consistent with the "never a silent refusal" rule stated across every phase's design
  doc.
- **Fail-closed exception handling**: every external-call boundary in `orchestrate()` (context engine,
  recognition engine, confidence engine, risk manager, portfolio manager, order manager) is individually
  wrapped in its own `try/except Exception`, each degrading to a `_denied(...)` result with a specific
  reason code — genuinely never a bare re-raise, with the one exception noted in Finding 5.
  `assess_confidence` itself degrades to `Grade.D`/`eligible=False` on any internal exception
  (`confidence_engine/engine.py:78-81`), never propagating.
  - **Note found while confirming this**: `execution_orchestrator/engine.py:120-122`'s comment on the
    Recognition Engine `except` clause claims *"Confidence Engine handles a missing `RecognitionResult`
    explicitly (it is optional input, Phase 8's own design)"* — confirmed true by reading
    `confidence_engine/engine.py:61-68`: when `recognition is None`, `recognition_component` stays `None`
    and is excluded from the score average entirely (only `context_component` counts), which is a
    **different** mathematical treatment than when recognition *was* queried but returned insufficient
    evidence (`recognition_component` is explicitly floored to `0.0`, diluting the average toward D). Both
    behaviors are individually reasonable and both are deliberate (`# conservative: absent/insufficient
    evidence never boosts a score`, `confidence_engine/engine.py:68`), but they are not the *same*
    treatment for what could look like the same underlying situation ("no reliable recognition signal") —
    worth being aware this distinction exists rather than assuming "no recognition" and "insufficient
    recognition" grade identically. Not flagged as a separate numbered finding since it is explicitly
    intentional and disclosed in-code, unlike Findings 1-5.
- **Volume-step rounding never grants more size than risk-approved**: `risk_manager_live/engine.py:178`
  rounds down (`math.floor`), never up — confirmed correct direction.
- **Portfolio-request construction uses the Risk Manager's own approved figures, not re-derived ones**:
  `PortfolioAuthorizationRequest.monetary_risk`/`approved_risk_pct`
  (`execution_orchestrator/engine.py:172`) are taken directly from `risk_decision.monetary_risk`/
  `.approved_risk` — Portfolio Manager cannot receive a risk figure Risk Manager didn't itself compute and
  approve.
- **`ApprovedTradeIntent.volume` is genuinely pre-computed, never a fixed lot** — confirmed by reading the
  full chain from `compute_sizing` through `evaluate_trade_proposal`'s volume-step rounding
  (§6 of `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md`'s "headline finding" independently re-confirmed here by
  direct code read, not re-cited from that report).

---

## Severity assessment

None of the five findings is exploitable today, because the one thing that would exercise any of them —
a live signal source constructing a real `CandidateSignal` — does not exist
(`AI_TRADER_PROJECT_STATE.md` §7). All five become materially relevant the moment that changes:

| # | Finding | Would matter when |
|---|---|---|
| 1 | Quality-factor scaling inert (A and B sized identically) | As soon as real signals exist, if differentiated sizing between A/B trades was ever assumed to be happening |
| 2 | No direction/stop consistency check | As soon as any signal source can produce a malformed direction/stop pair — includes bugs in a future signal source, not just adversarial input |
| 3 | magic_number/comment discarded before the broker | If any future operator/tooling relies on `CandidateSignal.magic_number` to actually identify an order at MT5 |
| 4 | Recognition dimension not strategy-aware | As soon as more than one strategy with different theses shares one `orchestrate()` caller/config |
| 5 | Bare `assert` outside fail-closed pattern | Only if `evaluate_trade_proposal` or a future alternate caller of `LiveRiskDecision` ever changes to allow a partially-populated approved decision |

## Verdict

**Structurally sound, logically incomplete.** The fail-closed discipline, reason-code completeness, and
audit-trail completeness established across Phases 2-10 hold up under this audit — nothing found here
contradicts that discipline. What this audit adds is five specific, code-verified points where the
*trading logic itself* — as opposed to its structural safety net — has gaps or unintended flattening that
the unit test suite does not surface (because the tests validate that each function does what it says,
not whether what it says is what the overall system needs). None require urgent action given no live
signal source exists to reach them, but all five should be resolved (fixed, or explicitly accepted as
intentional and documented as such) before a live signal source is ever built — building that source is
explicitly out of scope for this audit and remains unauthorized (`AI_TRADER_DECISIONS.md`).

**Stopping here per instruction.** No fix was applied to any of the five findings. No live signal source
was built. Phases 1-10 were not touched. The 5%-sizing design was not implemented. Next in the CEO's
stated sequence: Risk Audit, then Demo Readiness Audit — neither started, neither authorized by this
report.
