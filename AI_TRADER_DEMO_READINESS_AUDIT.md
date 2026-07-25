# AI Trader — Demo Readiness Audit

**Mode: READ-ONLY.** No code, configuration, or threshold was modified. No live signal source was built.
No Phase 1-10 code was touched. No 5%-sizing logic was implemented. Repo `ai_quant_lab-research-main`,
branch `ai-trader-implementation` — last in the CEO's stated audit sequence (Knowledge Transfer → Decision
Logic → Risk → **Demo Readiness**).

## The question this audit actually answers

Risk Audit Finding #1 established that `risk_manager_live` never reads the `EngineState.SUSPENDED`
escalation `risk_manager/guards.py` signals on a loss/drawdown breach, and that the P&L fields those
guards check are raw, caller-supplied inputs with no persistent memory across calls. Unassisted execution
means, by definition, that nobody is watching. Without persistent suspension state, a system that hits a
drawdown limit blocks the current trade and re-evaluates the next one from scratch, from whatever fields
the caller hands it. That reframes what this audit is for. Not "is the system ready for continuous DEMO"
— **what, at minimum, would need to exist before unassisted execution is even a discussable question?**

Below is that list: each precondition, and its actual current state — EXISTS, PARTIAL, or DOESN'T EXIST —
with the evidence behind each status. Nothing here is implemented, estimated, or ordered. The numbering
is for reference only, not priority; that decision is explicitly not this audit's to make.

---

## 1. A persistent record that "this account already breached a loss/drawdown limit today" — **DOESN'T EXIST**

The precondition the CEO's question points at directly. `guards.py`'s `check_daily_loss`/
`check_weekly_loss`/`check_max_drawdown` correctly deny the *individual* proposal in front of them
(confirmed, `risk_manager_live/engine.py:123-126` reads `result.passed`/`result.reason` from every
`GuardResult`), but `result.escalate_to` — the `EngineState.SUSPENDED` signal those same functions
return — is read nowhere: a repo-wide search for `EngineState` in `risk_manager_live`,
`execution_orchestrator`, and `portfolio_manager_live` returns zero hits. `execution_orchestrator`'s own
`emergency_stop: bool` parameter (`execution_orchestrator/engine.py:69`) is a separate, external,
caller-supplied flag with no code deriving it from a guard breach. Nothing in this codebase currently
turns "we breached the daily loss limit at 14:03" into a fact that's still true at 14:04 for the next
candidate.

## 2. Automatic computation of today's/this week's realized+unrealized P&L from actual position history — **DOESN'T EXIST**

Even if Precondition 1 existed, it would have nothing reliable to latch onto today.
`PortfolioState.realized_pnl_pct_daily`/`unrealized_pnl_pct_daily`/the weekly variants/
`consecutive_losses`/`minutes_since_last_loss` (`risk_manager/types.py:330-336`) are plain dataclass
fields, defaulting to `0.0`/`0`/`None`, supplied fresh by whatever caller builds the `PortfolioState` —
nothing in `risk_manager`, `risk_manager_live`, or `portfolio_manager_live` derives them from
`open_positions`/`recent_closed_positions` sitting in the same object, and nothing cross-checks the two
for consistency. A persistent suspension mechanism (Precondition 1) would still depend entirely on a
not-yet-built caller supplying accurate numbers on every single call.

## 3. Accounting for more than one candidate sharing risk/margin/exposure budget within the same cycle — **DOESN'T EXIST**

Risk Audit Finding #5, restated here as a precondition rather than an observation, per instruction: under
attended, one-off testing (all of this project's history to date), "one candidate per cycle" was true by
construction — nobody built a second one. Under unassisted execution, evaluating more than one candidate
per cycle is the expected mode, not an edge case. `PortfolioState`/`AccountState` are immutable and
nothing in `execution_orchestrator.orchestrate()` threads an updated snapshot from one candidate's
approval into the next (confirmed by full reading of `orchestrate()` — each call receives its
`OrchestratorDependencies` from the caller, unmodified from the previous call). Every budget check that
depends on "how much room is left" — `LIMIT_MAX_EXPOSURE`, `compute_sizing`'s exposure/group clamps, the
free-margin check, every one of Portfolio Manager's nine checks — would evaluate each candidate in a
batch against the *same* pre-batch snapshot, capable of jointly approving more risk/margin than the
account actually has room for.

## 4. Reconciliation between the research cost model and what live execution actually charges — **DOESN'T EXIST / NOT QUANTIFIABLE WITH CURRENT DATA**

Independently verified: `ai_quant_lab`'s `statistician/STATISTICIAN_NET_OF_COST_OUTCOME_DEFINITION_v1.0.md`
exists exactly as cited (read in full, not taken on the CEO's word alone). It defines, from
`code/alpha_lab.py`/`code/mstrat.py`'s actual `CFG` dict: `cost_round_trip = 2 × (spread_ticks +
slip_ticks) × tick = 2 × (1.0 + 1.0) × 0.1 = 0.4 points` for XAUUSD, and states explicitly: *"Nu există o
variabilă de comision separată nicăieri în mstrat.py sau alpha_lab.py"* — no commission variable exists
in either file it checked.

Two things worth adding, found independently while trying to quantify the divergence:

- **This repo (`ai_trader/simulation/config.py::CostModel`) has its own commission concept, separate from
  the Statistician's two files** — `commission_model: str = "per_lot"`, `commission_per_lot: float =
  0.0`, explicitly disclosed as *"conservative placeholders, never tuned against results"*
  (`simulation/config.py:41-51`). `spread_ticks: float = 1.0` and `SlippageModel.fixed_ticks: float =
  1.0` here match the Statistician's own defaults exactly — the two independently-maintained cost models
  (this repo's batch simulator, `ai_quant_lab`'s research scripts) agree on their *assumed* spread/slip
  values, and both leave commission at zero, one by omission, one by an explicit, disclosed placeholder.
  Neither number has ever been set from a real broker rate.
- **One real, historical data point exists, and only one**: Phase 1's connectivity probe
  (`MT5_CONNECTIVITY_PROBE_REPORT.md:33-35`) captured a live XAUUSD tick on this exact account
  (`FusionMarkets-Demo`, `DEMO_020`) — bid 4054.55 / ask 4054.62, a 0.07-price-unit (7-point) spread,
  against the research model's assumed 0.1-price-unit spread component. The real, single-snapshot spread
  was *tighter* than assumed, not wider — but it is one tick, from an earlier, unspecified session, not a
  sampled distribution, and it predates Phase 10 entirely. The same probe also recorded the account's real
  `point=0.01` (`digits=2`) — the actual broker tick size is **10× smaller** than the `tick=0.1` the
  research `CFG` uses, and nothing anywhere establishes whether the research model's "tick" is meant to
  equal the broker's real price increment or is an independent, coarser unit of its own. That ambiguity
  is itself part of the divergence, not just the missing commission figure.
- **The BTCUSD test (the only real order this project has ever sent) captured no cost data at all
  usable here**: `MT5OrderSendResult`/`MT5OrderCheckResult` (`mt5_demo_execution/types.py:32-62`) have no
  commission field — confirmed by reading both dataclasses in full — and MT5 exposes commission only via
  deal/position history, which this codebase never queries. The three BTCUSD journals contain zero
  commission entries (checked directly). The observed 17-point difference between the entry fill (63984.0)
  and the closing fill (63967.0) cannot be used as a cost proxy: it conflates real BTCUSD price movement
  during the seconds the position was open with spread, and MT5 commission on a per-lot/commission-based
  account is a separate ledger debit, never embedded in the fill price at all. BTCUSD's own tick/point
  size is also unrelated to XAUUSD's, so even its captured spread (17.0 / 1700 points) isn't a stand-in
  for the actual, live-trading-relevant instrument.

**What's missing to actually quantify the divergence**: a real per-lot commission rate or observed
commission charge from this specific broker/account (nothing in this codebase or its captured data
contains one); a sampled, multi-session real XAUUSD spread observation (one historical tick is not
that); any empirical slippage measurement (requested vs. filled price, isolated from ordinary price
movement) for either instrument. Without those three, the Statistician's 0.4-point round-trip figure
cannot be confirmed or refuted against this specific account's live reality — only bounded as "plausible
on the one spread data point available, unverified on slippage, and unverified — likely understated,
since it's currently zero — on commission."

## 5. A live bridge from MT5 account/symbol data into `AccountState`/`InstrumentSpecification`/`PortfolioState.equity` — **DOESN'T EXIST**

Established originally during the Knowledge Transfer Audit and the risk-sizing design work, re-confirmed
here as a readiness precondition: `AccountState` is constructed only in test fixtures repo-wide. Every
precondition above that depends on "real account equity" or "real instrument specification" (2, 3, 4's
commission/spread reconciliation, and the pending 5%-sizing design) inherits this same gap.

## 6. A live signal source (something that actually constructs `CandidateSignal`) — **DOESN'T EXIST**

Repeated across all three prior audits, restated here because it is a precondition for *this* audit's
subject specifically: unassisted execution cannot be discussed at all — not "not ready," literally
undefined — while nothing produces the input the rest of the pipeline would act on. Confirmed again:
`CandidateSignal(` appears exactly once in the repository, in
`execution_orchestrator/tests/_fixtures.py:31`.

## 7. Any mechanism to run the pipeline repeatedly, unattended (scheduler/loop/cron equivalent) — **DOESN'T EXIST**

Repo-wide search for scheduling/loop constructs (`while True`, `schedule`, `cron`, `APScheduler`,
`asyncio.sleep`, `time.sleep` used as a driving loop) in `ai_trader/` production code returns nothing
resembling a repeat-forever driver — the two hits that exist (`execution_engine/adapters/base.py`,
`telegram_notifier/sender.py`) are both bounded retry-with-backoff loops inside a single call, not an
unattended run loop. Nothing in this repository would call `orchestrate()` a second time without a human
or an external script doing so.

## 8. A single, authoritative "how much risk/exposure is currently in use" definition — **PARTIAL**

Risk Audit Finding #2, restated as a precondition: `RiskConfig.portfolio_limits.max_exposure_pct` and
`PortfolioManagerConfig.max_total_exposure_pct` are two independently-configured dataclasses (different
packages, no shared constant), both defaulting to `0.30` today by coincidence of convention, not
enforcement. Confirmed they read the *same* underlying `portfolio.portfolio_risk_pct` (the same object
reference is passed to both layers by `execution_orchestrator`), so the data isn't inconsistent — the
*ceiling* is defined twice, with nothing keeping the two numbers equal if either is ever tuned alone. This
is "partial" rather than "doesn't exist": the concept and enforcement both exist, twice, unreconciled.

## 9. A working (or explicitly disabled) confidence-to-risk differentiation — **PARTIAL**

Decision Logic Audit #1 / Risk Audit #3, restated as a precondition: `QUALITY_FACTOR`
(`risk_manager/config.py:27-33`) and the sizing formula that consumes it both exist and run correctly.
But `Grade.A → PREMIUM` and `Grade.B → STRONG` both map to `quality_factor = 1.0`, and only A/B can ever
reach sizing (`ConfidenceAssessment.__post_init__`), so every trade that structurally can reach the live
sizing formula today receives the identical factor. The mechanism exists; whether it's *supposed* to be
inert (treat A and B identically) or is an unintended flattening has not been decided either way.

## 10. Validation that a stop-loss is actually on the loss side of entry for the stated direction — **DOESN'T EXIST**

Decision Logic Audit #2 / Risk Audit #4, restated as a precondition: confirmed, once more, that the only
check anywhere in the pipeline is `stop_distance = abs(proposal.entry - proposal.stop)`
(`risk_manager_live/engine.py:109`) — direction-agnostic. `compute_sizing`'s entire risk-cap promise
depends on this relationship holding; nothing verifies it does.

## 11. Ownership and daily reset of `PortfolioDailyState` (trade count / heat budget, separate from P&L) — **DOESN'T EXIST**

`PortfolioDailyState`'s own docstring (`portfolio_manager_live/types.py:48-51`) states: *"Caller-owned,
caller-persisted... A future Execution Orchestrator (Phase 9) owns tracking and resetting this daily."*
Phase 9 is built; `execution_orchestrator.orchestrate()` takes `deps.daily_state` as an already-built,
caller-supplied argument (`execution_orchestrator/types.py`) and neither tracks nor resets it — the
"future" owner the docstring anticipated does not exist in the code that was supposed to become it. This
is a second, independent "daily state" concept from Precondition 2 (which is P&L-based) — nothing unifies
"how much risk, how many trades, and how much loss has this account taken today" into one tracked,
reset-on-schedule state.

## 12. Failure-visible alerting when the notification channel itself fails, under unattended operation — **PARTIAL**

`notify_fire_and_forget` (`telegram_notifier/sender.py:116-125`) spawns a daemon thread running `notify()`
(which itself retries with backoff) and returns immediately, discarding the `NotificationOutcome`
entirely — confirmed by reading the function in full. Under attended operation this is a reasonable
design (a human watching the chart is a redundant channel). Under unassisted operation, if Telegram itself
is unreachable after its own internal retries exhaust, nothing anywhere records or surfaces that fact —
the one channel meant to tell a human something happened has no fallback for its own failure.

## 13. Automatic/periodic reconciliation against the broker during unattended operation — **PARTIAL**

`execution_orchestrator.reconcile_orchestrated_orders` (`execution_orchestrator/engine.py:223-226`) wraps
the existing, unmodified `execution_engine.reconciler.reconcile_all_open` — the mechanism exists and is
callable. Nothing calls it periodically or automatically; it requires an external caller to decide to
invoke it, the same "no scheduler" gap as Precondition 7, specific here to position/order reconciliation
rather than the main decision loop.

## 14. Whether the live decision chain is actually informed by anything statistically validated — **DOESN'T EXIST (already audited)**

Not re-derived here — `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md`'s own verdict stands: zero Research-Lab
edges are code-linked into the live decision chain, and traceability from a live decision back to a
validated edge is structurally impossible today (no field for it exists anywhere in the relevant types).
Listed here only because it is, factually, also a precondition this audit's subject depends on — included
for completeness of "what would need to exist," not as new analysis.

---

**Stopping here per instruction.** This is a status list, not a conclusion. No precondition above was
implemented, no fix was proposed, no order or priority was assigned beyond the list's own numbering
(reference only). No live signal source was built, no Phase 1-10 code was touched, no 5%-sizing logic was
implemented. This closes the CEO's stated audit sequence (Knowledge Transfer → Decision Logic → Risk →
Demo Readiness) — what, if anything, gets built next is not this report's decision.
