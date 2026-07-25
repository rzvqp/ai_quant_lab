# AI Trader — Official Project State

**Last updated**: 2026-07-25. **Repository**: `ai_quant_lab-research-main`. **Branch**:
`ai-trader-implementation`. This document is written to be self-contained: a new Claude session opening
only this repository (no access to any prior conversation) should be able to reconstruct the exact
current state of the AI Trader project from this file plus the files it cites.

---

## 1. Objective

Build a live-execution decision pipeline ("AI Trader") that reads market context, evaluates whether a
recognized pattern/strategy has a favorable historical edge, sizes and risk-checks a trade, and can send
it to a MetaTrader 5 DEMO account — while remaining structurally incapable of LIVE/CONTEST trading,
importing `MetaTrader5` outside one designated adapter, or bypassing any risk/portfolio control. This is
separate from, and does not yet consume, the "Research Lab" backtest/discovery effort that also lives in
this repository (Edge Discovery Registry, Strategy families S1-S51, Alpha Discovery/Red Team) — see §9
and `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` for the exact, code-verified relationship between the two.

## 2. Current architecture — the live decision chain

```
Market Data (market_scanner, pre-existing)
        |
Context Engine (context_engine.build_context_snapshot)
        |  wraps market_intelligence.build_market_intelligence + edge_intelligence.evaluate_edges
        v
Recognition Engine (recognition_engine_live.recognize)  [optional per candidate]
        v
Confidence Engine (confidence_engine.assess_confidence)  -> Grade A-D
        v
[caller builds TradeProposal]
        v
Risk Manager (risk_manager_live.evaluate_trade_proposal)   -- computes position size, not a fixed lot
        v
[caller builds PortfolioAuthorizationRequest]
        v
Portfolio Manager (portfolio_manager_live.evaluate_portfolio_authorization)
        v
[caller builds ApprovedTradeIntent]
        v
Order Manager (order_manager.process_approved_intent)
        v
Broker Adapter: DryRunBrokerAdapter | MT5DemoBrokerAdapter (MT5 DEMO only)
```

`execution_orchestrator.orchestrate()` (Phase 9) runs this whole chain for one `CandidateSignal`.
`mt5_demo_execution.send_after_dry_run_gate()` (Phase 10) runs it twice — DRY_RUN then DEMO, separate
ledgers/journals — never sending to DEMO unless the same intent's dry run already reached
`ACKNOWLEDGED`. **`CandidateSignal` is never constructed anywhere in production code today** — see §7.

## 3. Phases completed

| Phase | Package | Commit | Tests | Status |
|---|---|---|---|---|
| 1 | Broker Adapter (read-only MT5) | `7434fb0` (pre-existing, approved before this phase sequence) | — | CLOSED |
| 2 | Risk Manager (live) | `1d68521` | 37 | CLOSED |
| 3 | Order Manager (dry-run) | `d19ae94` | 43 | CLOSED |
| 4 | Portfolio Manager (live) | `1c2b171` | 37 | CLOSED |
| 5 | Telegram Notification Service | `4d73114` | 34 | CLOSED |
| 6 | Context Engine | `5fa91f7` | 19 | CLOSED |
| 7 | Recognition Engine (live wiring) | `327d0fc` | 23 | CLOSED |
| 8 | Confidence Engine | `1d2950a` | 23 | CLOSED |
| 9 | Execution Orchestrator | `c5f04e6` | 18 | CLOSED |
| 10 | MT5 Demo Execution | `dbfadd3` | 43 (42 + 1 gated) | CLOSED, operationally validated (§6) |

Consolidated report: `AI_TRADER_PHASES_2_10_FINAL_REPORT.md` (updated `a3f2288` with the BTCUSD outcome).
Per-phase design + implementation reports exist at repo root, e.g. `RISK_MANAGER_LIVE_PHASE2_DESIGN.md` /
`_IMPLEMENTATION_REPORT.md`, following the same naming pattern for every phase 2-10.

Two narrow, explicitly CEO-authorized architecture fixes were applied mid-sequence (both pure
type-widening, zero behavior change, disclosed in the Phase 10 design doc §0):
`order_manager.types.OrderExecutionResult.dry_run` (was hardcoded `True`; now reflects the adapter
actually used via `isinstance` check) and `execution_orchestrator.types.OrchestratorDependencies.adapter`
(widened from `DryRunBrokerAdapter` to the general `BrokerAdapter` protocol).

## 4. MT5 integration

`ai_trader/execution_engine/adapters/mt5_gateway.py` (Phase 1, frozen) — `RealMT5Gateway` is the sole
module in the entire `ai_trader/` tree with `import MetaTrader5`; verified by a static test in every
package that touches MT5 (`test_no_literal_metatrader5_import_in_this_package`, repeated per-package).
`ai_trader/execution_engine/adapters/mt5_adapter.py::MT5ReadOnlyBrokerAdapter` — DEMO/server verification,
`AccountTradeMode`, `AlgoTradingStatus`. `ai_trader/mt5_demo_execution/` (Phase 10) extends both purely
by subclassing (`RealMT5DemoGateway(RealMT5Gateway)`, `MT5DemoBrokerAdapter(MT5ReadOnlyBrokerAdapter)`) —
zero modification to the Phase 1 files. Safety gates (all fail-closed, all tested): AlgoTrading
re-verified on every `submit_order` call; DEMO re-verified on every call; configurable minimal volume
ceiling (`MT5DemoConfig.max_order_volume`, default `0.01` lots); `order_check` always called before
`order_send`; idempotent submission; dry-run-must-pass-first gate; REAL/CONTEST structurally refused;
market-open pre-check before any transmission. No cancel_order (disclosed, out of Phase 10's named scope).

## 5. Telegram integration

`ai_trader/telegram_notifier/` (Phase 5) — deliberately **zero** dependency on any trading-domain
package, verified by its own import-independence test (the strictest of the whole session: forbids
`risk_manager*`, `execution_engine`, `order_manager`, `portfolio_manager_live`, `scoring_engine`,
`signal_engine`). Public API: `notify()`/`notify_fire_and_forget()`, taking only a domain-free
`NotificationEvent` (plain strings + a flat string map). Cannot see a trading-domain type, let alone act
on one — used only for best-effort, fire-and-forget notification of outcomes already decided by the rest
of the pipeline. Credentials via environment variables (`TELEGRAM_BOT_TOKEN`,
`TELEGRAM_CHAT_ID_PRIMARY`/`_SECONDARY`), never hardcoded (verified §13/`AI_TRADER_TEST_STATUS.md`).

## 6. Primary instrument: XAUUSD. BTCUSD was infrastructure-only.

**XAUUSD is AI Trader's primary/intended trading instrument.** BTCUSD was used exactly once, on
2026-07-25, under explicit separate CEO authorization, **solely to validate the Phase 10 execution
infrastructure while XAUUSD's market was closed for the weekend** — not as an approved strategy or
symbol (see `AI_TRADER_DECISIONS.md` item 2). Full history:

- **Phase 10 gated real-terminal test (XAUUSD, market closed)**: correctly stopped at
  `PENDING_MARKET_OPEN` before any transmission — proved the market-closed gate works, no order sent.
- **BTCUSD operational test, attempt 1**: stopped fail-closed at check #3 — **AlgoTrading disabled** at
  the terminal. No order sent. CEO confirmed this as the expected, correct behavior.
- CEO manually enabled AlgoTrading in the MT5 terminal UI (not by any code in this repo — no code path
  anywhere can programmatically activate it, verified by a dedicated static test).
- **Attempt 2**: dry-run leg rejected — the standalone test script's own `strategy_id` value
  (`"PHASE10_BTCUSD_INFRA_TEST"`) did not match `ORDER_SCHEMA.json`'s required `^S\d+$` pattern. Fixed in
  the script (not in any `ai_trader` component) to `"S999"`, CEO-authorized re-run.
- **Attempt 3**: `NOT_CONNECTED` — the dry-run leg's `DryRunBrokerAdapter` was never `.connect()`-ed in
  the test script's own setup. Fixed in the script; not an `ai_trader` component bug.
- **Attempt 4**: all 12 pre-send checks passed, dry-run reached `ACKNOWLEDGED`, but the real DEMO
  `order_check()` call returned `None`. Stopped immediately, zero code touched, per the CEO's explicit
  "do not modify anything" instruction for that test. A **read-only** diagnostic (`order_check`/
  `last_error()` only, no order placed) revealed the real MT5 error: `(-2, 'Invalid "comment" argument')`.
  A second **read-only** diagnostic (a comment-length sweep, `order_check` only, 10-31 chars) empirically
  confirmed: 28 characters accepted, 29-31 rejected, on this specific terminal/broker
  (`FusionMarkets-Demo`, build 5836). CEO-authorized minimal fix: `request_builder.py`'s
  `_COMMENT_MAX_LENGTH` constant changed from `31` (MT5's documented general limit, not honored by this
  broker) to `27` (one character of margin below the empirically-confirmed-working 28).
  **Explicit, CEO-mandated disclosure, consecrated in the module's own docstring and in
  `BTCUSD_PHASE10_OPERATIONAL_TEST_REPORT.md`: this 27-char value is a CONSERVATIVE, broker/terminal
  -specific value confirmed for the ONE terminal actually tested — it is NOT a universal MT5 protocol
  limit, and any broker/terminal/build change MUST be re-verified via a read-only `order_check()` call
  before trusting it again.**
- **Attempt 5 — full success**: all 12 checks passed. Real DEMO order sent: **ticket `491745557`**,
  **0.01 lots BTCUSD**, filled at 63984.0, `order_send` retcode **`10009`** (`TRADE_RETCODE_DONE`),
  `dry_run=False`. Position **closed immediately** after confirmation (close price 63967.0, retcode
  `10009`). Final verification: **0 open positions, 0 open orders.**
- Committed as `a3ef1c7` (script, three journals, the fix, the rewritten report), documentation
  finalized in `a3f2288`.
- **CEO decision (2026-07-25, verbatim closing)**: *"Testul operațional Phase 10 pe BTCUSD DEMO este
  ACCEPTED și CLOSED."* Full path confirmed validated: AI Trader → Execution Orchestrator → Order
  Manager → Broker Adapter → MT5 `order_check` → MT5 `order_send` → confirmation → controlled close →
  final verification. **Phase 10 stays closed; the BTCUSD test validated its already-built send path, it
  did not open new scope, and it does not make BTCUSD an approved strategy or symbol.**

## 7. Current state of DEMO execution

**No continuous or unattended DEMO execution has ever run, and none is currently authorized.** The
send-capable infrastructure (Phase 10) is built, unit-tested (43 tests), and has been operationally
proven exactly once, manually, for a single order, under explicit CEO supervision (§6). Beyond that:

- **`CandidateSignal` — the type that starts a real trade candidate through the orchestrator — is
  constructed nowhere in production code**, confirmed by `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md`
  (repo-wide grep, exactly one hit, in a test fixture). There is currently **no live signal source at
  all** feeding the pipeline — it is fully wired and tested but structurally dormant.
- No scheduler, loop, or cron-like mechanism exists anywhere in `ai_trader/` to run the pipeline
  unattended.
- Continuous DEMO execution requires (a) building a real signal source, (b) the CEO's explicit
  authorization, and (c) resolving the open items in `AI_TRADER_DECISIONS.md`.

## 8. Known limitations (disclosed, not hidden)

- `cancel_order` not implemented on `MT5DemoBrokerAdapter` (out of Phase 10's named scope).
- `risk_context: RiskContext` (ATR/spread/liquidity) has no live producer anywhere in Phases 2-9 —
  remains caller-supplied; a disclosed gap since Phase 2.
- Market-open check (Phase 10) is a tick-recency heuristic, not a fabricated session-hours table.
- `strategy_health_component` (Confidence Engine, Phase 8) is permanently `None` — no authorized live
  strategy-health signal exists in this pipeline; explicit, disclosed placeholder.
- Recognition Engine's `AUTHORIZED_PATTERNS` catalog (Phase 7) is 15 generic per-`ContextDimension`
  statistical buckets, not implementations of any specific Research-Lab edge's structure/confirmation/
  invalidation logic (see §9).
- The comment-length constant (§6) is a conservative, single-broker-confirmed value, not a universal MT5
  guarantee — re-verification required on any broker/terminal/build change.
- `AccountState`/`InstrumentSpecification`/`PortfolioState.equity` are populated only by test fixtures
  today — no live bridge from MT5 `account_info()`/`symbol_info()` exists yet (identified during 5%-risk
  sizing design work, see §11 and `RISK_SIZING_5PCT_XAUUSD_DESIGN.md`).

## 9. Technical debt

- No live signal source (§7) — the single largest structural gap; nothing else in this document matters
  operationally until it's addressed.
- No live equity/instrument-value bridge from MT5 into `risk_manager_live`'s sizing inputs (§11).
- `edge_intelligence` loads the Strategy Library's validation evidence (matched-null/global-FDR/
  walk-forward/holdout status) but never reads it in its own verdict logic, and its whole output snapshot
  is never consumed by anything downstream — a genuinely wired but functionally inert link (full detail:
  `AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` §3.2).
- `RecognitionCandidate.strategy_id`/`CandidateSignal.strategy_id` are free-form strings with **no
  membership check** against any strategy registry — if a signal source is ever built without also adding
  this, nothing in the type system would stop an unvalidated or explicitly rejected strategy ID from
  reaching a live decision.
- Three older packages' READMEs (`scoring_engine`, `risk_manager`, `strategy_manager`) claim "no runtime
  code, Research Lab untouched," contradicted by their own substantial `.py` implementations — a
  documentation-hygiene debt, reported not corrected (`AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md` §10).
- None of the 9 live-wired packages (Phases 2-10) has its own architecture/README doc — their only
  documentation is inline docstrings; the "Research Lab: NO" assurance that exists for older batch
  packages was never restated for the newer live ones.

## 10. Elements not yet validated

- Continuous/unattended DEMO execution — never run.
- The XAUUSD real-terminal send path specifically — validated only by proxy through BTCUSD's identical
  code path (§6); the gated XAUUSD integration test itself has only been exercised through the
  market-closed `PENDING_MARKET_OPEN` branch, never a live XAUUSD send.
- 5%-equity-risk-per-trade dynamic sizing — **design-only**, not implemented, pending CEO decisions
  (`RISK_SIZING_5PCT_XAUUSD_DESIGN.md`, committed `125e171`, awaiting review).
- Any transfer of Research Lab edges/strategies into the live decision chain — audited and found **not
  transferred** at the code level (`AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md`, verdict **NOT READY**).
- Portfolio-level caps' compatibility with a hypothetical 5%-per-trade risk regime — open question, not
  yet analyzed in depth.

## 11. Parallel design work (not implemented)

`RISK_SIZING_5PCT_XAUUSD_DESIGN.md` — design for equity-based dynamic position sizing (5% risk/trade,
volume computed from stop distance + instrument value, not a fixed lot). Finding: the sizing formula
already exists and is already live-wired (`risk_manager/sizing.py::compute_sizing`,
`risk_manager_live/engine.py::evaluate_trade_proposal`) — this is a gap-fill, not a new engine. Five
explicit CEO decisions are required before any code is written, most importantly how to handle the
current hard 0.01-lot safety ceiling (`MT5DemoConfig.max_order_volume`), which as configured today would
reject any correctly-computed 5%-risk order. **No code has been written for this feature.**

## 12. All official files relevant to AI Trader's current state

**This document set** (created/updated in this official save): `AI_TRADER_PROJECT_STATE.md` (this file),
`AI_TRADER_PROJECT_AUDIT.md`, `AI_TRADER_NEXT_SESSION.md`, `AI_TRADER_DECISIONS.md`,
`AI_TRADER_COMPONENT_INVENTORY.md`, `AI_TRADER_TEST_STATUS.md`.

**Consolidated / audit reports**: `AI_TRADER_PHASES_2_10_FINAL_REPORT.md`,
`AI_TRADER_KNOWLEDGE_TRANSFER_AUDIT.md`, `BTCUSD_PHASE10_OPERATIONAL_TEST_REPORT.md`.

**Per-phase design + implementation reports** (repo root): `RISK_MANAGER_LIVE_PHASE2_DESIGN.md` /
`_IMPLEMENTATION_REPORT.md`, `ORDER_MANAGER_PHASE3_DESIGN.md` / `_IMPLEMENTATION_REPORT.md`,
`PORTFOLIO_MANAGER_PHASE4_DESIGN.md` / `_IMPLEMENTATION_REPORT.md`,
`TELEGRAM_NOTIFIER_PHASE5_DESIGN.md` / `_IMPLEMENTATION_REPORT.md`,
`CONTEXT_ENGINE_PHASE6_DESIGN.md` / `_IMPLEMENTATION_REPORT.md`,
`RECOGNITION_ENGINE_PHASE7_DESIGN.md` / `_IMPLEMENTATION_REPORT.md` (plus the earlier
`RECOGNITION_ENGINE_DESIGN.md`/`_PHASE1_DESIGN.md`/`_PHASE0_DIAGNOSTIC_REPORT.md`/
`_PHASE1A_IMPLEMENTATION_REPORT.md` for the batch-side Recognition Engine this phase wraps),
`CONFIDENCE_ENGINE_PHASE8_DESIGN.md` / `_IMPLEMENTATION_REPORT.md`,
`EXECUTION_ORCHESTRATOR_PHASE9_DESIGN.md` / `_IMPLEMENTATION_REPORT.md`,
`MT5_DEMO_EXECUTION_PHASE10_DESIGN.md` / `_IMPLEMENTATION_REPORT.md`,
`BROKER_ADAPTER_DESIGN.md` / `BROKER_ADAPTER_LAYER_A_B_IMPLEMENTATION_REPORT.md` (Phase 1),
`MT5_CONNECTIVITY_PROBE_REPORT.md`.

**Committed but awaiting CEO decision before any implementation**: `RISK_SIZING_5PCT_XAUUSD_DESIGN.md`
(committed `125e171`).

**Unrelated to AI Trader specifically (Research Lab / batch pipeline docs)** — exist in the same repo,
out of this document's scope; see `PROJECT_STATE_v2.md`, `PROJECT_AUDIT.md`, `NEXT_SESSION.md`,
`RECONSTRUCTION_PROMPT.md`, `CHANGELOG.md`, `EDGE_DISCOVERY_REGISTRY_v1.md`, `STRATEGY_REGISTRY.md`,
`CEO_STRATEGY_PERFORMANCE_ATLAS.md`, and the `PHASE_6_*`/`PHASE_7_*` checkpoint report families for that
history.
