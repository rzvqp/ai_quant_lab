# AI Trader — Risk Audit

**Mode: READ-ONLY.** No code, configuration, or threshold was modified to produce this report. No live
signal source was built. No Phase 1-10 code was touched. No 5%-sizing logic was implemented. Repo
`ai_quant_lab-research-main`, branch `ai-trader-implementation`, third in the CEO's stated audit sequence
(Knowledge Transfer → Decision Logic → **Risk** → Demo Readiness).

## Scope

The risk-control stack **as a system**, not component-by-component: `risk_manager`'s frozen guards/
limits/filters, `risk_manager_live`'s additional volume-step and free-margin checks, and
`portfolio_manager_live`'s exposure caps — the gaps and interaction effects *between* these three layers,
which no single component's own unit tests can surface (each layer's tests correctly prove that layer
does what it claims; none of them proves the three layers agree with each other). Includes the two
Decision Logic Audit findings that touch risk (dead quality_factor scaling, missing direction/stop
check), extended here with their risk-specific consequences.

## Method

Full direct reading of `risk_manager/guards.py`, `limits.py`, `filters.py`, `config.py`, and the relevant
parts of `types.py` (`PortfolioState`); `risk_manager_live/engine.py` (already read for the Decision Logic
Audit, re-examined here for risk-specific interaction); `portfolio_manager_live/aggregation.py`,
`engine.py`, `types.py` in full. Every finding cites the exact file/line read.

---

## Findings

### 1. The loss/drawdown circuit breaker is designed to persist but doesn't — three uncoordinated "stop trading" mechanisms exist, none linked to each other

`risk_manager/guards.py`'s `check_daily_loss`/`check_weekly_loss`/`check_max_drawdown` (lines 23-50) each
return `escalate_to=EngineState.SUSPENDED` on breach. The module's own docstring (lines 1-6) states this
is deliberate: *"the caller... applies that escalation to the engine's own state, this module only
reports what escalation (if any) a breach implies."* But `risk_manager_live/engine.py` — the only live
caller of these guards, which explicitly bypasses `risk_manager.engine` entirely (its own docstring: *"never
routes through `RiskManager.evaluate()`/`allow_trade()`"*) — reads only `result.passed`/`result.reason`
from each `GuardResult` (`risk_manager_live/engine.py:123-126`); **`result.escalate_to` is never read
anywhere in the live pipeline.** The escalation signal the frozen module was explicitly designed to
produce has no live consumer.

This compounds with two further facts, both confirmed by direct reading:

- `PortfolioState.realized_pnl_pct_daily`/`unrealized_pnl_pct_daily`/`_weekly` variants and
  `consecutive_losses`/`minutes_since_last_loss` (`risk_manager/types.py:330-336`) are **raw,
  caller-supplied input fields**, not computed internally from `open_positions`/`recent_closed_positions`
  in the same object. Nothing in `risk_manager`/`risk_manager_live`/`portfolio_manager_live` derives
  today's P&L from trade history; a caller must supply it fresh on every call, and nothing cross-checks
  that figure against the position lists sitting right next to it in the same dataclass.
- `execution_orchestrator.orchestrate()`'s own `emergency_stop: bool` parameter
  (`execution_orchestrator/engine.py:69,76-80`) is a **third, entirely separate mechanism** — a bare
  external flag, checked first, with zero code deriving it from a guard breach, an `EngineState`, or
  anything computed from `PortfolioState`. It is purely whatever the caller happens to pass.

**Net effect**: a real daily-loss breach today denies *that one proposal* (via `reason_codes`,
correctly) but leaves no trace anywhere that trading should stay halted for the rest of the day. If a
future caller re-invokes `evaluate_trade_proposal` on a later signal with a *slightly* recovered
`realized_pnl_pct_daily`/`unrealized_pnl_pct_daily` figure (e.g. an open position's floating loss
narrows), the guard would pass again — the system has no persistent memory that the account already
breached its daily limit once today. The `EngineState.SUSPENDED` concept the frozen module anticipated,
and the `emergency_stop` flag Phase 9 actually built, are two unconnected answers to the same underlying
need ("stop everything after a serious breach"), and the first one is currently a no-op in the live
wiring.

### 2. Two independently-configured ceilings govern the same "total exposure" quantity, with no code linking them

`risk_manager/config.py::PortfolioLimits.max_exposure_pct` defaults to `0.30`
(`risk_manager/config.py:39`), checked pre-sizing (coarse "is there room at all," `limits.py:66-71`) and
again, fine-grained, inside `compute_sizing`'s own `remaining_exposure_pct` clamp
(`risk_manager/sizing.py:48-49`). Separately, `portfolio_manager_live/types.py::PortfolioManagerConfig.
max_total_exposure_pct` also defaults to `0.30` (`portfolio_manager_live/types.py:111`), checked
*post-sizing* against `snapshot.total_exposure_pct = portfolio.portfolio_risk_pct +
request.approved_risk_pct` (`aggregation.py:36`, `engine.py:45-51`).

Confirmed **not** a data-consistency problem: `execution_orchestrator/engine.py` passes the identical
`deps.portfolio` object reference to both `evaluate_trade_proposal` (line 151) and
`evaluate_portfolio_authorization` (line 176) — both layers read the same `PortfolioState.
portfolio_risk_pct`. The problem is the **ceiling itself is defined twice**, in two separate dataclasses
in two separate packages, with no shared constant and no code asserting they agree. They happen to share
the same default value (`0.30`) today — that is convention, not enforcement. If either is ever tuned
independently (the natural next step once the 5%-risk sizing design in
`RISK_SIZING_5PCT_XAUUSD_DESIGN.md` is implemented, which will itself require touching
`SizingLimits.risk_per_trade_pct`), the two layers can silently diverge: if `RiskConfig`'s cap ends up
looser than `PortfolioManagerConfig`'s, Risk Manager approves and sizes a trade that Portfolio Manager
then rejects (wasted work, confusing "approved-then-denied" audit trail); if the reverse, Portfolio
Manager's own ceiling becomes permanently unreachable dead code, since Risk Manager's sizing clamp would
already have kept every proposal within the tighter cap.

A related, smaller instance of the same pattern, **self-disclosed in the code** (not hidden):
`ExposureSnapshot.portfolio_heat_pct` is set to the exact same value as `total_exposure_pct`
(`aggregation.py:37-39`, comment: *"same formula as total exposure, evaluated against a SEPARATE,
distinctly-named ceiling — not a fabricated alternative metric"*), then checked against a *third*
independently-configured default (`max_portfolio_heat_pct = 0.30`, `types.py:116`). Three ceilings, one
underlying number, three separately-tunable config fields — the disclosure means this one is a known,
accepted redundancy rather than a hidden bug, but it is still worth listing alongside Finding 2's less
disclosed sibling, since both share the identical risk: someone tunes one threshold and doesn't know to
tune the others.

### 3. Confidence-based risk-budget scaling is dead code (extends Decision Logic Audit #1) — every live-eligible trade risks the identical percentage of equity

Already established in `AI_TRADER_DECISION_LOGIC_AUDIT.md` §1: `Grade.A → PREMIUM` and `Grade.B → STRONG`
both map to `quality_factor = 1.0` (`risk_manager/config.py:27-33`), and only A/B can ever reach sizing.
Stated in risk terms specifically: `risk_manager/sizing.py:43`'s `effective_risk_pct =
risk_per_trade_pct * quality_factor` reduces, for every trade that can structurally reach it today, to
`effective_risk_pct = risk_per_trade_pct` — a single flat constant
(`SizingLimits.risk_per_trade_pct`, currently `0.005`). The confidence-tiered risk budgeting that
`POSITION_SIZING.md` describes and that `QUALITY_FACTOR`'s own 0.5/0.75/1.0 spread implies is not, in the
live wiring as it stands, a real control — every approved trade today would risk the exact same
percentage regardless of whether it barely cleared the Grade B threshold or scored a perfect Grade A.
This matters more for a Risk Audit than a Decision Logic Audit: it is not just an inconsistency, it is a
**risk-control feature that reads as present (the arithmetic exists, the config field exists) but is
inert** — the kind of gap that is easy to miss because nothing about it looks broken from a type or test
standpoint.

### 4. No direction-vs-stop validation means the sizing formula's own risk-cap assumption is unverified (extends Decision Logic Audit #2)

Already established in `AI_TRADER_DECISION_LOGIC_AUDIT.md` §2 as a structural gap; the risk-specific
consequence is sharper than "a malformed order could be submitted." `compute_sizing`'s entire premise —
`size_units = risk_budget_currency / (stop_distance * point_value)` — assumes the resulting position's
maximum loss is bounded at `stop_distance × point_value × size_units ≈ risk_budget_currency`. That bound
only holds if the stop is genuinely on the loss side of entry for the stated direction. Since nothing
anywhere in `CandidateSignal`/`TradeProposal`/`ApprovedTradeIntent`/`evaluate_trade_proposal` checks this
(only `stop_distance = abs(entry - stop) > 0` is verified — direction-agnostic), a direction/stop mismatch
would not just produce a "weird" order: it would produce a position sized as though a risk cap exists
when, in reality, the adverse-movement side has no bracket leg bounding it at all. The risk system's
central promise — "this trade can lose at most X% of equity" — is not actually verified anywhere for the
one input (the stop's side relative to entry) that promise most depends on.

### 5. No mechanism accounts for multiple candidates evaluated in the same cycle against a shared, static snapshot

`PortfolioState` and `AccountState` are immutable dataclasses; nothing in `execution_orchestrator.
orchestrate()` mutates or threads an updated snapshot from one candidate's approval into the next. Today
this is moot — `orchestrate()` is only ever called with test fixtures, one `CandidateSignal` at a time
(`AI_TRADER_PROJECT_STATE.md` §7). But the moment a real signal source exists and evaluates more than one
candidate per cycle against the *same* `PortfolioState`/`AccountState` objects (the natural way to build
one, absent an explicit note against it), every check that depends on "how much room is left" —
`check_max_exposure`, `compute_sizing`'s `remaining_exposure_pct`/`remaining_group_budget_pct` clamps, the
free-margin check (`account.margin_free`, `risk_manager_live/engine.py:194-201`),
`portfolio_manager_live`'s every exposure/heat/daily-count check — would evaluate each candidate against
the *pre-cycle* snapshot, not accounting for any other candidate approved earlier in the same cycle. Two
independently-fine candidates could each individually pass every margin/exposure check and still, taken
together, exceed the account's actual free margin or the portfolio's actual exposure cap. This is a gap
in what "the system" needs to guarantee (candidates evaluated together must not double-spend the same
capital/margin/exposure budget), not in any single function, which is exactly the kind of thing a
system-level Risk Audit — rather than each component's own unit tests — is positioned to catch.

---

## What was checked and found consistent (not just assumed)

- **Correlation-group logic is genuinely shared, not duplicated.** `risk_manager/sizing.py:56`
  (`compute_sizing`'s group-budget clamp) and `portfolio_manager_live/aggregation.py:65,71`
  (`find_long_short_conflicts`) both call the identical `RiskConfig.correlation_group_for()` — one
  function, one config source, two call sites checking genuinely different properties (risk-budget
  headroom vs. opposing-direction conflict). Not a redundancy risk.
- **Coarse/fine exposure-check layering is intentional and correctly documented**, not an oversight:
  `limits.py:6-14`'s own docstring explains `LIMIT_MAX_EXPOSURE` is a coarse pre-sizing gate with a
  matching fine-grained sizing-time clamp, while `LIMIT_MAX_LEVERAGE`/`LIMIT_MAX_OVERNIGHT` are
  deliberately coarse-only (no per-trade clamp exists for those two axes, and the doc says so explicitly
  rather than silently omitting one).
  - **This does mean leverage/overnight exposure have no fine-grained per-trade clamp** — worth noting as
    a disclosed, not hidden, asymmetry: a trade could pass the coarse `LIMIT_MAX_LEVERAGE`/
    `LIMIT_MAX_OVERNIGHT` checks (portfolio not yet over the cap) and then, once sized, push the portfolio
    over either cap with no earlier warning — by design, per the same docstring, not a gap this audit is
    the first to notice.
- **Volume-step rounding never grants more size than risk-approved** (re-confirmed from the Decision
  Logic Audit, risk-relevant here too): `math.floor` at `risk_manager_live/engine.py:178`, rounds down
  only.
- **Portfolio Manager cannot approve a risk figure Risk Manager didn't itself compute**:
  `PortfolioAuthorizationRequest.monetary_risk`/`approved_risk_pct`
  (`execution_orchestrator/engine.py:172`) are taken directly from `risk_decision.monetary_risk`/
  `.approved_risk` — no re-derivation, no possibility of the two layers disagreeing about how much risk
  this specific trade represents.
- **Fail-closed/full-audit-trail discipline holds across all three layers**: guards/limits/filters
  (`risk_manager`), the two additive checks (`risk_manager_live`), and every one of Portfolio Manager's
  nine checks (`portfolio_manager_live/engine.py:45-130`) all run to completion and record a trace step
  regardless of pass/fail — none of the three layers short-circuits its own audit trail, confirmed by
  reading every check function, not sampled.
- **Pre-trade filters' fail-safe-on-missing-data default is real, not just claimed**: `check_spread`/
  `check_liquidity` (`filters.py:50-68`) explicitly deny when no threshold is configured for a symbol,
  rather than defaulting to pass — confirmed by reading the actual comparison logic, matching the module's
  own stated "cannot confirm safe, never assume safe" principle (`filters.py:6`).

---

## Severity assessment

| # | Finding | Blast radius if a live signal source is built without addressing it |
|---|---|---|
| 1 | No persistent loss/drawdown escalation | **Highest** — the one control most directly meant to stop catastrophic compounding losses is currently a per-call check with no memory, not a circuit breaker |
| 4 | No direction/stop validation | **High** — silently unbounded downside on a malformed signal, invalidating the sizing formula's core promise |
| 5 | No cross-candidate budget accounting within one cycle | **Medium-high**, scales with how many candidates a future signal source evaluates per cycle |
| 2 | Duplicate, unlinked exposure ceilings | **Medium** — today harmless (same default), becomes live risk the first time either config is tuned alone |
| 3 | Dead quality-factor scaling | **Medium** — not unsafe by itself (every trade still respects the flat risk cap), but a designed differentiation control is silently absent |

## Verdict

**The risk-control stack is well-tested component-by-component and fail-closed at every individual
boundary — but as a system, it has one real circuit-breaker gap (Finding 1) and one real unverified
safety assumption (Finding 4) that no component's own test suite could have caught, because both are
about what happens *between* layers, not within one.** Findings 2, 3, and 5 are lower-severity but
compound the same theme: several controls that read as real (a config field, a formula) are either
duplicated-without-enforcement or structurally inert given how the live pipeline currently calls them.
None of the five is exploitable today for the same reason the Decision Logic Audit's findings weren't —
no live signal source exists (`AI_TRADER_PROJECT_STATE.md` §7) — but Findings 1 and 4 in particular should
be resolved, not merely accepted, before one is ever built; a circuit breaker that doesn't persist and a
risk cap that isn't verified are exactly the two things a risk system exists to prevent.

**Stopping here per instruction.** No fix was applied to any finding. No live signal source was built.
Phases 1-10 were not touched. The 5%-sizing design was not implemented — though Finding 2 is directly
relevant to it: implementing that design will require touching `SizingLimits.risk_per_trade_pct`, and
whoever does so should also address the duplicate-ceiling gap in the same pass rather than tune one side
and leave the other stale, per this audit's own finding. Next in the CEO's stated sequence: Demo
Readiness Audit — not started, not authorized by this report.
