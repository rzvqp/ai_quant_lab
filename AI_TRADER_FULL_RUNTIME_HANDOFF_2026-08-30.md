# AI_TRADER_FULL_RUNTIME_HANDOFF_2026-08-30

Cold-recovery handoff for a NEW AI Trader session. The reader is assumed to know
nothing about the old conversation that produced this file. Everything below is
either (a) mechanically verified directly by the author of this document in the
same working session that wrote it, or (b) sourced from parallel read-only
research passes over the actual repositories, each item cited to its file path.
Where something could not be verified, it is marked `UNKNOWN` rather than
assumed. This document performed **no runtime changes**: no TradingView call,
no MT5 order, no bar-379 exposure, no S5/strategy modification.

---

## 1. AUTHORITATIVE OUTPUT FILE

Verified mechanically before writing: the authoritative AI Trader worktree is
`C:\Users\MEDION GAMING\ai_quant_lab-research-main` — confirmed via `git remote -v`
(remote `trader` → `https://github.com/rzvqp/ai_quant_lab-research-main.git`,
the same remote every prior Q4/AI-Trader commit in this session was pushed to)
and via the presence of `docs/trader_apprenticeship/` (the Q4 apprenticeship
ledgers) and `ai_trader/` (the runtime code) at its root. This file is written
at that root, as instructed.

---

## 2. REPO / GIT IDENTITY

```
REPO_ROOT                = C:\Users\MEDION GAMING\ai_quant_lab-research-main
BRANCH                   = ai-trader-implementation
HEAD_COMMIT              = beab11193414587b022306cc22b133ed52b21d2f
                            "docs: point CAUSAL_REPLAY_ACCELERATOR_V1 handoff at
                            integrated commit cf6f470" (2026-08-30 00:46:18 +0300)
REMOTE_TRACKING_BRANCH   = trader/ai-trader-implementation
LOCAL_REMOTE_MATCH       = YES (0 ahead, 0 behind; both resolve to beab1119...)
WORKTREE_STATUS          = DIRTY (tracked modifications + untracked files, see below)
```

Two commits landed on this branch since the last commit this old session made
itself (`d3ce871`, the governance-audit + accelerator-design checkpoint):
`9986467` ("VE_CAUSAL_REPLAY_ACCELERATOR_V1: implementation, test, benchmark,
handoff docs") and `beab111` (current HEAD). Both are already pushed; nothing
about them is uncommitted or in doubt.

### Tracked modifications (uncommitted, all in one coherent change set)

```
M ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/gateway_ext.py
M ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/live_runtime_loop.py
M ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/soak/soak_loop.py
M ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/soak/tests/test_soak_loop.py
M ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/tests/_fixtures.py
M ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/tests/test_live_runtime_loop.py
M docs/trader_apprenticeship/REPLAY_DATA_GAP_LEDGER.md
```

This is a single not-yet-committed fix (157 insertions / 36 deletions) for a
broker-server-clock-offset bug (~+3h at `FPTradingLLC-Demo`) that was causing
date-based MT5 bar polling to silently return stale pre-weekend bars — see
§3 for detail. `REPLAY_DATA_GAP_LEDGER.md`'s modification is this old
session's own GAP-151..154 entries (Q4 replay gaps), already complete and
correct, just never committed.

### Untracked files relevant to this handoff

```
?? .claude/                                                  (session-local, not research artifact)
?? .mcp.json                                                  (MCP server config — see §13)
?? ai_trader/csv_causal_replay/                                (CSV replay adapter code — see §14)
?? ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/broker_clock.py
?? ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/tests/test_broker_clock.py
?? docs/trader_apprenticeship/AI_TRADER_Q4_M15_LOG.md
?? docs/trader_apprenticeship/AI_TRADER_Q4_MARKET_THESIS_LEDGER.md
?? docs/trader_apprenticeship/AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md
?? docs/trader_apprenticeship/AI_TRADER_Q4_NO_TRADE_LEDGER.md
?? docs/trader_apprenticeship/AI_TRADER_Q4_PATTERN_LEDGER.md
?? docs/trader_apprenticeship/AI_TRADER_Q4_TRADE_EVIDENCE_LOG.md
?? full_regression_a98a0a4_output.txt / full_regression_commit_a98a0a4.txt   (test-run artifacts)
?? scratch_verify/  scratchpad_verify/                          (scratch, not research)
```

**The entire Q4 2020 apprenticeship record (bars 1-378, all snapshots, all
pattern ledger entries) is currently UNCOMMITTED.** This is not an oversight —
under the Q4 mandate this old session operated by, Q4 outputs were explicitly
instructed to stay uncommitted pending a separate CEO checkpoint mandate (the
same pattern used for the prior Failure-Engineering and Management-Research
checkpoints, which *were* separately committed once authorized). No checkpoint
mandate for Q4 specifically has been issued yet. **This is the single most
important fact in this whole document**: if this worktree is lost/reset before
a Q4 checkpoint commit happens, the entire 378-bar prospective record is lost
with it, recoverable only from this handoff's own quoted excerpts and from
whatever git history the CSV adapter's fixture (`Q4_SEALED_1_378.csv`,
untracked, §14) preserves.

Under this mandate's own "no runtime changes / no commit unless authorized"
constraint, none of this was committed while writing this document.

---

## 3. AI TRADER RUNTIME IDENTITY

All paths relative to `ai_trader/` inside the repo above. Two runtime "loops"
exist side by side and must not be confused:

### 3.1 New Brain LIVE_SHADOW loop (never places real orders)

```
COMPONENT              = New Brain LIVE_SHADOW loop
PURPOSE                = continuous shadow-only decision pipeline (ve_brain.decide_n6
                          path), records what would have been decided, submits nothing
AUTHORITATIVE_FILE     = ai_trader/new_brain_live/entrypoint.py (module: -m
                          ai_trader.new_brain_live.entrypoint)
CURRENT_STATUS         = RUNNING — confirmed live: Windows Scheduled Task
                          `AITraderLiveShadow`, State=Running, LastRunTime
                          2026-08-30 10:17:24, LastTaskResult=267009
                          (SCHED_S_TASK_RUNNING, i.e. "currently executing", not
                          an error code)
PERSISTENT_STATE_PATH  = new_brain_live_state/xauxsd_m15.db (DEFAULT_STATE_DIR =
                          entrypoint.py's own parents[2]/"new_brain_live_state")
RESTART_BEHAVIOR       = BootTrigger + LogonTrigger, MultipleInstancesPolicy=
                          IgnoreNew, RestartOnFailure Interval=1min Count=999
                          (per AITraderLiveShadow_task.xml)
KNOWN_LIMITATIONS      = BROKER_ORDER_SUBMISSION explicitly DISABLED by design
                          (per the task XML's own description and
                          LIVE_SHADOW_PERSISTENT_SERVICE_ACTIVE.md) — this loop
                          structurally cannot submit a real order regardless of
                          any other config.
```

**Live process observation (this session, 2026-08-30):** TWO processes found
running this exact module — PID 9012 and PID 11460, both
`StartTime = 2026-08-30 10:17:24/10:17:32`, both `Responding = True`. This is
two instances of a task whose own policy is `IgnoreNew` (should prevent a
second instance). Most likely explanation: BootTrigger and LogonTrigger both
fired within ~8 seconds of each other at this morning's reboot/logon, before
`IgnoreNew` could reject the second start. **Not independently confirmed** —
flagged as `UNVERIFIED_RUNTIME_STATE` in §21, not asserted as either benign or
a fault.

### 3.2 MT5 DEMO strategy-platform pipeline (S5's actual runtime)

```
COMPONENT              = Strategy-platform pipeline (Catalog → Router → EV →
                          Risk → Execution → Ledger)
PURPOSE                = the pipeline S5 actually runs through against the MT5
                          DEMO account
AUTHORITATIVE_FILE     = ai_trader/new_brain_live/strategy_platform/pipeline.py
CURRENT_STATUS         = RUNNING (soak variant) — Scheduled Task
                          `AITraderS5MT5DemoSoak`, State=Running, LastRunTime
                          2026-08-30 10:17:24, LastTaskResult=267009
ENTRY_POINTS           = mt5_demo_bridge/run_live_demo.py (bounded manual run) and
                          mt5_demo_bridge/soak/run_soak_live.py (unattended soak,
                          -m ai_trader.new_brain_live.strategy_platform.
                          mt5_demo_bridge.soak.run_soak_live, default 60 days)
PERSISTENT_STATE_PATH  = new_brain_live_state/s5_mt5_demo_soak/ — contains
                          execution_ledger.db, shadow_ledger.db, safety_events.db
                          (all SqliteStateStore/WAL files), startup_events.log,
                          first_trade_checkpoint.json, health.json
RESTART_BEHAVIOR       = restart-reconciliation-first (reconcile_in_doubt_identities
                          runs before any new submission on every call); dedup via
                          last_processed_ts_close + ShadowLedger append-only replay
                          (already_processed check) — a bar is never reprocessed
KNOWN_LIMITATIONS      = no scheduled-task XML exists specifically for the soak
                          script itself in the repo (run_soak_live.py's own
                          docstring says it expects an operator-created task
                          "mirroring AITraderLiveShadow" but does not register
                          one) — yet a task named exactly `AITraderS5MT5DemoSoak`
                          IS running live per §3.2 above, so that task was
                          created directly in Task Scheduler, not from a
                          checked-in XML. No XML for it exists in git.
```

**Live process observation:** TWO processes of
`ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.run_soak_live`
— PID 9092 and 11452, same start-time pattern as §3.1. Same caveat applies.

**Live terminal observation:** `terminal64.exe` ("C:\Program Files\FP Trading
MT5 Terminal\terminal64.exe") confirmed running — consistent with the
`FPTradingLLC-Demo` broker referenced throughout the codebase and prior
project state.

### 3.3 Strategy Catalog / Strategy Router

```
COMPONENT   = StrategyCatalog
PURPOSE     = AI-Trader-owned strategy registry (deliberately NOT ve_brain's own
              sealed catalog — a separate admission point built as a workaround)
FILE        = ai_trader/new_brain_live/strategy_platform/catalog.py
STATUSES    = MOCK_TEST_ONLY, RESEARCH_ONLY, ALPHA_CANDIDATE, VALIDATED, DISABLED,
              RETIRED — only VALIDATED is production-eligible
              (PRODUCTION_ELIGIBLE_STATUSES = frozenset({VALIDATED}))
```

```
COMPONENT   = StrategyRouter
PURPOSE     = iterates catalog.enabled_entries(), checks eligibility
              (instrument + regime match), invokes eligible strategies, collects
              TradeHypothesis output. Does NOT decide profitability (EV engine's job)
              and does NOT admit strategies into the catalog (catalog's own job)
FILE        = ai_trader/new_brain_live/strategy_platform/router.py
```

The externally-installed `ve_brain` package has its own SEALED catalog
(`ve_brain.n6._SEALED_CATALOG`, exactly 4 hardcoded strategies, structurally
cannot accept new entries) — documented as the reason
`ai_trader/new_brain_live/strategy_platform/catalog.py` exists at all (per its
own docstring, citing `INTEGRATION_BLOCKED_VE_BRAIN_STRATEGY_CATALOG.md`, not
independently re-read for this handoff).

### 3.4 Decision / EV layer

Two separate EV paths exist — **do not conflate them**:

```
COMPONENT   = ve_brain.decide_n6 (external package)
PURPOSE     = the "real, ratified" EV/decision authority, used by the LIVE_SHADOW
              loop only (via ai_trader/new_brain_bridge/bridge.py)
STATUS      = UNTOUCHED by anything in this repo; sealed 4-strategy catalog
              blocks S5/other AI-Trader-native strategies from reaching it
```

```
COMPONENT   = RealEVDecisionEngine
PURPOSE     = re-verifies a TradeHypothesis against THIS repo's own
              StrategyCatalog, calls ve_brain.run_ev (same EV-math primitive
              decide_n6 uses internally) but bypasses decide_n6's sealed-catalog
              gate; only StrategyStatus.VALIDATED entries reach TRADE_DECISION
FILE        = ai_trader/new_brain_live/strategy_platform/real_ev_engine.py
MANDATE     = VE-AI-TRADER-GENERIC-EV-AUTHORITY-001 (per file docstring)
USED_BY     = pipeline.py (the MT5 demo bridge's actual runtime path — S5 goes
              through here, not through decide_n6)
```

Full orchestration order (`pipeline.py`'s own docstring): *MarketState →
Strategy Catalog → Strategy Router → Strategy Evaluation → EV/Decision Engine →
Risk Engine → Execution Adapter → Shadow Ledger.* The file states real order
submission is "structurally impossible in this delivery" via that path alone —
see §6 for how the actual live order path (which DOES exist, per §3.5/§5)
relates to this.

### 3.5 Execution layer / MT5 bridge

```
COMPONENT              = MT5 execution bridge
DIRECTORY              = ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/
SOLE CDP-EQUIVALENT    = ai_trader/execution_engine/adapters/mt5_gateway.py is the
CHOKE POINT              repo's only file that imports MetaTrader5 directly (per
                          gateway_ext.py's own docstring)
```

Key files and what they do (verified by reading, not inferred):

- **`gateway_ext.py`** — `Protocol`/impl classes extending the base MT5 gateway
  with three primitives: `order_calc_profit` (risk sizing), `history_deals_get`
  (restart reconciliation), `copy_rates_from_pos` (offset-independent recent-bar
  polling — added in the current *uncommitted* diff, see §2).
- **`live_runtime_loop.py`** — bar-close-driven S5 live-demo loop
  (`run_live_loop`). One bounded startup warmup (60 bars), then polls for newly
  closed M15 bars, tracks `last_processed_ts_close` to avoid reprocessing.
- **`soak/soak_loop.py`** — unattended soak orchestrator (`run_soak`, `while True`
  loop). Restart-reconciliation-first; a reconciliation ambiguity here **trips
  the safety monitor** rather than aborting outright; writes a checkpoint every
  cycle (`checkpoints.maybe_write_checkpoint`) and a `health.json` snapshot
  (`loop_alive_as_of`, `mt5_connected`, `last_reconciliation_as_of`,
  `safety_blocked`); `consecutive_gateway_exceptions >= 5` trips
  `PERSISTENT_BROKER_API_CORRUPTION`.
- **`broker_clock.py`** (untracked, new) — `measure_broker_time_offset` /
  `to_true_utc`. Fixes a live-discovered defect: MT5 `.time` fields are on the
  broker's own server clock, not true UTC (measured live at
  `FPTradingLLC-Demo` ≈ +10799s / +3.0h offset) — corrects bar timestamps
  before they reach S5's NY-session-open logic. Falls back to `0.0` offset
  (disclosed, not fabricated) if the offset can't be measured.

**Scheduler**: no cron/OS-scheduler reference exists *inside*
`mt5_demo_bridge/` itself — both loops are plain Python `while`/polling loops;
the actual unattended-restart mechanism is the external Scheduled Task
(`AITraderS5MT5DemoSoak`, confirmed live per §3.2, though its XML is not
checked into this repo).

### 3.6 Risk layer (separate from the bridge)

```
COMPONENT   = risk_manager / risk_manager_live (shadow-gate risk layer)
FILES       = ai_trader/risk_manager/ (config, guards, portfolio limits)
              ai_trader/risk_manager_live/ (engine.py: evaluate_trade_proposal;
              types.py; circuit_breaker.py)
PURPOSE     = gates whether the pipeline may proceed to the real MT5 order —
              does NOT itself size the real order (see §6 for the discrepancy
              between this layer's config and the order that actually gets sized)
```

```
COMPONENT   = risk_execution_adapter.py
PURPOSE     = thin translation from TradeHypothesis/EVDecision into
              risk_manager_live.engine.evaluate_trade_proposal and
              new_brain_bridge.execution_shadow.attempt_shadow_execution — no
              risk policy is reimplemented here (per its own docstring)
```

### 3.7 Persistent state (summary — see §3.1/§3.2 for exact paths)

`ai_trader/persistent_state/store.py` (`SqliteStateStore`, WAL-mode SQLite,
`kv_state` + `append_log` tables) is the one persistence primitive reused
everywhere: `LiveBarFeed`, `LiveSignalJournal`, `MT5PortfolioStateSource`,
`ShadowLedger`, `MT5ExecutionLedger` (the last two backing the demo bridge's
own ledgers under `new_brain_live_state/s5_mt5_demo_soak/`).

### 3.8 Config / environment variables

**No `.env` file exists anywhere in the repo** (confirmed by a repo-wide glob).
MT5 connection config is a plain in-code dataclass
(`ai_trader/mt5_demo_execution/types.py: MT5DemoConfig`), not env-driven.
`BrokerCredentials` (`ai_trader/execution_engine/adapters/connection.py`) is
instantiated with **no arguments** by both live-run entry points — both
docstrings state the scripts "connect to whatever MT5 terminal/account is
already open on this machine." **There is no required env-var/secret list to
document** for this bridge — authentication is via an already-logged-in MT5
desktop session (the `terminal64.exe` process confirmed running, §3.2), not
stored credentials in this repo.

---

## 4. S5 — COMPLETE OPERATIONAL STATE

```
STRATEGY_ID              = s5_c_2d587447_opening_range_breakout_long
STRATEGY_VERSION          = rep_7472f3d412f2
STRATEGY_NAME              = S5 — NY opening-range breakout, LONG
ALPHA_CANDIDATE_ID          = C_2d587447
AUTHORITATIVE_SPEC_PATH    = ai_trader/new_brain_live/strategy_platform/
                             s5_opening_range_breakout.py (line 7: frozen spec
                             string `S5{session=ny, mode=breakout, side=up,
                             stop=or_opp, exit=rr3}`)
```

**Entry logic**: NY session, UTC `[13:00, 21:00)`. Opening range = first 4 M15
bars (`13:00-13:59`). Entry window = bar-in-session 4-20 inclusive
(`14:00-16:59`). Trigger = `close > or_high` (breakout up only).

**Stop logic**: `stop = or_low - 2*TICK`, with `TICK = 0.01` — this is a
*ratified override* of a documented engine defect (`RT-CODE-A-0007`, which had
used `TICK = 0.1`).

**Target logic**: `target = entry + 3*risk` (fixed 3R). Max hold: 48 M15 bars
(12h).

**Direction**: LONG-only (`direction=Direction.LONG`, confirmed both in code
and in the validation report's own language, "LONG-only").

```
VALIDATION_ARTIFACT   = RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001
                         repo: aql_stat_clone
                         path: red_team/policy_reviews/
                         RT_S5_S20_CLEAN_INDEPENDENT_VALIDATION_REPORT.md
VALIDATION_COMMIT      = 633bd5dac2874ee048864c468844ffefa0897110
STATUS                 = INDEPENDENT_VALIDATION_PASS (S5 specifically; S20
                         in the same review FAILED on drawdown, not relevant
                         to S5's own status)
```

**Known validation metrics (quoted from the report, not recomputed here):**
n=295, BASE net expectancy 0.2098, STRESS net (@ 0.24 round-trip cost) 0.1925,
temporal thirds (BASE) [0.273, 0.153, 0.201], best-1%-removed BASE 0.1907,
+1-bar-delay BASE 0.1581 / STRESS 0.1370, max drawdown −6.44R, max single loss
−1.03R, win rate 0.549, profit factor 1.609, median TP 373.2 pips, 99.3% of
trades ≥70 pips. Frozen trade-ledger SHA256:
`cd4e8d4aae0104cd1041898cf136917b9ec3194c343ba6840fab0bdb7831e1d7` (295 trades).

**Cost model**: `AI_TRADER_SHADOW_COST_MODEL_v1.json` (repo root) —
`base_ratified.round_trip_total = 0.05`, `stress_ratified.round_trip_total =
0.24`, `calibration_status: RATIFIED`, XAUUSD, spread from Fusion Markets Demo
(n=175 clean obs); slippage explicitly `"COST_MODEL_UNAVAILABLE — zero real
observations"` (disclosed gap, not fabricated).

**Runtime adapter path**: wired directly into `live_runtime_loop.py` and
`soak_loop.py` (both instantiate `S5OpeningRangeBreakoutLong` /
`catalog_entry_for_s5` and build the catalog entry the MT5 demo runtime
actually runs). Broker adapter: `MT5DemoBrokerAdapter`
(`ai_trader/mt5_demo_execution/adapter.py`).

**Scheduler status**: confirmed RUNNING live (§3.2) — Scheduled Task
`AITraderS5MT5DemoSoak`, State=Running as of 2026-08-30 10:17. Connected to
`FPTradingLLC-Demo` (DEMO). No LIVE execution adapter exists anywhere in this
codebase — `execution_mode.py` defines only `DISABLED` and `MT5_DEMO_ONLY`.

**Enable/disable state**: `catalog_entry_for_s5(..., enabled: bool = True)`
default; every production call site uses the default (`enabled=False` appears
only in one test file, never in runtime code). `StrategyStatus.VALIDATED` is
the only production-eligible status, and S5 is the sole entry constructed with
it.

Not retested, not altered, per this mandate's own instruction.

---

## 5. MT5 / SHADOW / DEMO STATE

```
MT5_BRIDGE_PRESENT         = YES
BRIDGE_PATH                = ai_trader/new_brain_live/strategy_platform/mt5_demo_bridge/
BRIDGE_PROCESS_RUNNING     = YES
BRIDGE_PID                 = 9092, 11452 (two instances — see §3.2 duplication note)
SCHEDULER_RUNNING          = YES
SCHEDULER_TASK_NAME        = AITraderS5MT5DemoSoak (State=Running,
                              LastRunTime=2026-08-30 10:17:24)
                              AITraderLiveShadow (State=Running, same LastRunTime
                              — separate loop, §3.1)

BROKER / SERVER            = FP Trading MT5 Terminal (terminal64.exe confirmed
                              running); broker identity FPTradingLLC-Demo per
                              code/docs (not re-queried live from inside the
                              terminal itself this session)
ACCOUNT_MODE                = DEMO (per BrokerCredentials()-with-no-args design,
                              execution_mode.py's DISABLED/MT5_DEMO_ONLY-only
                              enum, and prior project-state confirmation — not
                              independently re-queried live via any MT5 API this
                              session, since no such tool is available to this
                              agent)
ACCOUNT_IDENTIFIER          = [not queried — no live MT5 API access from this
                              session; would need to be read from the running
                              terminal/bridge logs by whoever has that access]
BROKER_ORDER_SUBMISSION_POLICY = DISABLED for the LIVE_SHADOW loop (§3.1) by
                              hard design; the MT5 demo bridge (§3.2) DOES place
                              real orders, but only against the DEMO account —
                              no LIVE code path exists anywhere in this repo
LIVE_ORDER_SUBMISSION_ENABLED  = NO (no LIVE adapter exists in the codebase at
                              all — this is not a runtime flag, it's a
                              structural absence)

OPEN_POSITIONS              = UNKNOWN — not independently queried this session
                              (no live MT5 positions API available to this
                              agent without touching order-placement-adjacent
                              tools, which this mandate explicitly forbids).
                              Last independently-verified figure available in
                              the file record: zero orders submitted as of a
                              2026-08-29 audit (ai_quant_lab/COMPANY_STATE.md,
                              §12) — but that is now over 24h stale and MUST be
                              re-verified fresh by the new session before
                              trusting it, especially since two soak-task
                              processes have been running since this morning's
                              10:17 reboot.
PENDING_ORDERS              = UNKNOWN — same caveat as above.

LAST_KNOWN_ORDER            = UNKNOWN — not queryable from this session; check
                              ai_trader/.../mt5_demo_bridge state DB
                              (execution_ledger.db under
                              new_brain_live_state/s5_mt5_demo_soak/) directly.
LAST_KNOWN_EXECUTION_EVENT  = UNKNOWN, same caveat.
DEDUP_STATE                 = mechanism confirmed present and correctly designed
                              (§3.5: last_processed_ts_close + ShadowLedger
                              replay-based already_processed check;
                              reconcile_in_doubt_identities runs before every
                              new submission) — but its CURRENT VALUE was not
                              read this session.
RESTART_RECOVERY_STATE      = mechanism confirmed present (reconciliation.py:
                              reconcile_in_doubt_identities / any_blocked,
                              runs first on every loop start) — current value
                              not read this session.
LAST_RUNTIME_HEARTBEAT      = UNKNOWN — health.json exists at
                              new_brain_live_state/s5_mt5_demo_soak/health.json
                              per soak_loop.py's own write path, but was not
                              read this session (reading it would be safe and
                              is recommended as the new session's first
                              MT5-state check, per §19).
```

**Why these are UNKNOWN rather than guessed**: this old session's own tool
access never included a live MT5 positions/orders query capability, and this
mandate explicitly forbids inspecting via anything that risks touching order
state. The honest, correct next step is for the new session to read
`health.json` and `execution_ledger.db` directly (both pure read operations,
both explicitly safe) — not for this document to assert a number it never
actually checked.

---

## 6. RISK CONFIGURATION

```
ITEM                         CLASSIFICATION   DETAIL
RISK_PER_TRADE_CONVENTION    IMPLEMENTED      TWO CONFLICTING VALUES (see note)
EQUITY/BALANCE_BASIS         IMPLEMENTED      live account EQUITY (not balance)
LOT-SIZING_METHOD            IMPLEMENTED      broker order_calc_profit-based,
                                               rounds DOWN to volume step, never
                                               bumps under-minimum volume up
SL_BASIS                     IMPLEMENTED      structural (opening-range low − 2
                                               ticks), never adjusted to fit a
                                               target risk
MAX_POSITION/CONCURRENCY     IMPLEMENTED      shadow-gate layer only (see note)
DAILY_LOSS/PROP_GATES        IMPLEMENTED      shadow-gate layer only (see note)
NO_MARTINGALE                NOT_FOUND        no explicit code/comment; only
                                               structurally true (S5 is single-
                                               signal, single-fraction)
NO_GRID                      NOT_FOUND        same as above
FAIL-CLOSED_CONDITIONS       IMPLEMENTED      multiple explicit checks, listed below
```

**⚠ Risk-sizing discrepancy — flagged for CEO attention, not resolved here:**
the code that actually sizes the *real* MT5 order
(`mt5_demo_bridge/risk_sizer.py`, `demo_execution_adapter.py`) uses
`risk_fraction = 0.05` (5% of equity) by default. The separate shadow-gate
layer's own config (`risk_manager/config.py`, `SizingLimits.risk_per_trade_pct
= 0.005`, i.e. 0.5%) is used only to decide whether the pipeline is *allowed*
to proceed — it never determines the real order's volume. **The 0.5% figure
never reaches the real order; the real order is sized at 10x that.** This is a
genuine, currently-live discrepancy in the actual running code, not a
documentation error — it was not created by this handoff and is not resolved
by it.

**Max-position/daily-loss gates** (`risk_manager/config.py`): `max_positions=5`,
`max_per_symbol=1`, `max_correlated=2`, `max_exposure_pct=0.30`,
`max_leverage=3.0`; `max_daily_loss_pct=0.03`, `max_weekly_loss_pct=0.06`,
`max_drawdown_pct=0.12`. All enforced in the shadow-gate layer
(`risk_manager_live/engine.py` → `risk_execution_adapter.py` → `pipeline.py`),
which runs *before* `demo_execution_adapter.execute()` — so a breach blocks
the real order indirectly, via pipeline rejection, not via a duplicate check
inside the bridge itself.

**Fail-closed conditions** (all confirmed as real code, not documentation):
reconciliation ambiguity (blocks new submission), equity unavailable, symbol
capabilities unavailable, no tick / stale data, not connected, market
staleness (an undeterminable tick state is treated as **closed**, i.e.
fail-closed not fail-open), loss-calc failure, duplicate client-order-id
submission, broker-clock-offset unmeasurable (degrades to a disclosed `0.0`
fallback, not a hard stop), and 13 named soak-level safety trips (e.g.
`ACCOUNT_NOT_DEMO`, `PERSISTENT_BROKER_API_CORRUPTION`,
`RISK_EXCEEDS_5_PERCENT`) that, once tripped, block all new submissions until
a human explicitly clears them — never auto-cleared.

---

## 7. AI TRADER KNOWLEDGE / APPRENTICESHIP STATE

All paths relative to `docs/trader_apprenticeship/` in this repo unless noted.

```
ARTIFACT                                              STATUS
checkpoints/TRADER_KNOWLEDGE_CHECKPOINT_2020_Q1.md      FROZEN, authoritative
2020_Q2_H4_LOG.md (root, 8,313 lines)                   UNRESOLVED duplicate — see §8
lane_a_historical/2020_Q2_H4_LOG.md (22,570 lines)      UNRESOLVED duplicate — see §8
TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md                  FINAL, authoritative
TRADER_KNOWLEDGE_CHECKPOINT_2020_Q3.md                  FINAL, authoritative
AI_TRADER_Q3_INTEGRITY_AUDIT.md                          authoritative correction
                                                          to the Q3 checkpoint's
                                                          batching-incident count
AI_TRADER_Q2_VS_Q3_FORENSIC_REVIEW.md                   authoritative, dense
                                                          23-category comparison
AI_TRADER_TRADE_PATH_DATASET_V1.md                       authoritative (trade #57-66
                                                          MFE/MAE reconstruction)
AI_TRADER_FAILURE_CORPUS_V1.md                            authoritative
AI_TRADER_NEGATION_LIBRARY_V1.md                          authoritative, current
                                                          (4 Grade-C candidates, 0
                                                          Grade-B+)
AI_TRADER_FAILURE_ENGINEERING_REPORT_V1.md                authoritative, current
AI_TRADER_STRATEGY_READINESS_DIAGNOSTIC_V1.md             authoritative, current
AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md                  authoritative, current
AI_TRADER_MANAGEMENT_POLICY_LIBRARY_V1.md                 authoritative, current
                                                          (MGMT-004's full spec)
AI_TRADER_Q4_MANAGEMENT_PROSPECTIVE_PROTOCOL_V1.md        authoritative, frozen
                                                          forward-test spec —
                                                          NEVER redefine MGMT-004
                                                          from any other source
GOLD_BEHAVIOR_MODEL_V1.md                                 PARTIALLY STALE — §1
                                                          (PATTERN-007 raw log) is
                                                          current (n=31 as of Q3
                                                          close); §7 (CEO review
                                                          synthesis) is STALE,
                                                          last run at n=21
                                                          (2020-09-14), not
                                                          re-run against n=31
AI_TRADER_APPRENTICESHIP_MANIFEST.md                       authoritative SHA256
                                                          manifest of the whole
                                                          Q1-Q3 corpus
AI_TRADER_Q4_M15_LOG.md              (UNCOMMITTED)         current, THE Q4
                                                          replay chronicle,
                                                          bars 1-378
AI_TRADER_Q4_MARKET_THESIS_LEDGER.md (UNCOMMITTED)        current, 25 immutable
                                                          MARKET_THESIS_SNAPSHOTs
AI_TRADER_Q4_PATTERN_LEDGER.md       (UNCOMMITTED)        current, Q4-P007-001/
                                                          002/003 (003 OPEN)
AI_TRADER_Q4_NO_TRADE_LEDGER.md      (UNCOMMITTED)        current, 1 entry
AI_TRADER_Q4_TRADE_EVIDENCE_LOG.md   (UNCOMMITTED)        current, EMPTY
                                                          (zero Q4 trades)
AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md (UNCOMMITTED)  current, EMPTY
                                                          (no eligible Q4 trade
                                                          has occurred yet)
REPLAY_DATA_GAP_LEDGER.md            (MODIFIED, uncommitted) current, GAP-001
                                                          through GAP-154
Q4_GOVERNANCE_SCOPE_AUDIT_001.md     (COMMITTED, d3ce871)  authoritative — bars
                                                          288-378 causal audit,
                                                          confirms NO governance
                                                          breach, PASS
CAUSAL_REPLAY_ACCELERATOR_V1_DESIGN.md (COMMITTED, d3ce871) authoritative,
                                                          design-only, see §14
```

Do NOT rewrite any research conclusion above from memory — every file already
states its own conclusion; read the file.

---

## 8. Q1-Q3 DURABLE LEARNING SUMMARY

**Q1** — `checkpoints/TRADER_KNOWLEDGE_CHECKPOINT_2020_Q1.md`: **0 trades**,
pure observation quarter (2020-01-01 to 03-31). Two
`UNVALIDATED_TRADER_OBSERVATION` candidates: TOC-001 (fresh range extremes
usually fade, one disclosed 44+ bar counterexample) and TOC-002 (multi-bar
holds unreliable in extended-volatility/COVID-crash regime, 6/6 clean).

**Q2** — `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md`: `TOTAL_APPRENTICESHIP_TRADES
= 66` cumulative, `STRUCTURED_COMPARABLE_TRADES = 17` (#48, #51-66; the other
49 excluded from all stats as not structurally comparable). Fully-evidenced
#57-66 (n=10): net **−1.242R**. Combined n=17: **+3.925R** — but median R is
negative (−0.182R) while mean is positive (+0.231R), carried almost entirely
by one trade (#51, +6.120R); remove it and net across the remaining 16 is
**−2.195R**. Entire quarter inside one unbroken H4-BEARISH regime.
`NO_STRATEGY_CANDIDATE_READY_YET`.

**Q2 duplicate log — UNRESOLVED, do not resolve it by assumption**: two
files both named `2020_Q2_H4_LOG.md` (root, 8,313 lines, opens mid-quarter,
no formal header vs. `lane_a_historical/`, 22,570 lines, formal header,
continues from Q1). SHA256 hashes differ; NOT an identical duplicate. Both
retained, both committed, **neither marked authoritative**. The manifest's own
verdict: `UNRESOLVED (retained, not deprioritized)`.

**Q3** — `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q3.md`: **5 trades** (Q3-001 to
Q3-005), **0W/5L, net −6.106R**, all closed by 2020-07-22, new entries frozen
for the rest of the quarter (`OBSERVATION_FIRST`). PATTERN-007 raw tally at
Q3 close: n=31 (22 SUPPORT / 1 COUNTEREXAMPLE / 8 AMBIGUOUS). A dedicated
integrity audit (`AI_TRADER_Q3_INTEGRITY_AUDIT.md`) later corrected the
completion report's original batching-incident claim (it had said "5
instances / 3 excluded / 2 included," which was wrong in both directions —
true count was 7, only 1 (09-30-1159) provably defensible) and produced a
**strict-prospective tally: n=23** (15 SUPPORT / 1 COUNTEREXAMPLE / 7
AMBIGUOUS) alongside the unchanged raw n=31. Both tallies are preserved, not
merged.

**Failure Engineering** (`AI_TRADER_FAILURE_ENGINEERING_REPORT_V1.md`): 12
realized losses classified — 2 `BAD_TRADE`, 10 `GOOD_TRADE_NORMAL_LOSS`.
`AI_TRADER_NEGATION_LIBRARY_V1.md`: 4 candidates, **all Grade C**, none
Grade B+, none rejected — `NEGATION_RULES_GRADE_B_OR_HIGHER = 0`.

**Management/Exit Research** (`AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md`):
POLICY-1/2/3 (TP1-based) never triggered across any of the 12 primary trades
— `MANAGEMENT_NOT_SUPPORTED` for lack of a trigger, not for underperformance.
**MGMT-004** (breakeven-stop at +1.0R): n=4 (all Q2, SHORT-only), DELTA_R =
**+3.564R**, leave-one-out never flips sign, clears 7 of 8 success-gate
conditions fully (1 partially). **`STATUS =
MANAGEMENT_CANDIDATE_UNVALIDATED`, EVIDENCE_GRADE = B,
MANAGEMENT_CANDIDATE_READY_FOR_Q4_FORWARD_TEST = YES`.** Frozen forward spec
lives in `AI_TRADER_Q4_MANAGEMENT_PROSPECTIVE_PROTOCOL_V1.md` — never redefine
MGMT-004 from any other source.

**Playbook readiness**: `AI_TRADER_STRATEGY_READINESS_DIAGNOSTIC_V1.md` —
`PRIMARY_STRATEGY_BLOCKER = INSUFFICIENT_REGIME_DIVERSITY /
INDEPENDENCE_LIMITATION` (every trade and every P007 instance through Q3 sits
in one continuous episode). No pattern anywhere reaches
`PLAYBOOK_READY_FOR_PROSPECTIVE_TEST`.

**Execution reauthorization**: `GOLD_BEHAVIOR_MODEL_V1.md`'s own (stale, n=21)
synthesis says `READY_TO_REQUEST_EXECUTION_REAUTHORIZATION = NO`; new trade
entries were FROZEN since 2020-07-22 and never explicitly reauthorized in any
Q1-Q3 file. **No file states execution was reauthorized as of end of Q3.**
(Separately, note that the MT5 demo bridge's live DEMO-only running state,
§3.2/§5, is a distinct, later authorization for S5 specifically — not a
blanket "AI Trader apprenticeship execution reauthorization.")

**Source-file classifications** (using each file's own terms, not invented
ones): TOC-001/002 = `UNVALIDATED_TRADER_OBSERVATION`; PATTERN-007 =
`DEVELOPING_PATTERN` (never `TRADEABLE_EDGE`); all 4 Negation candidates =
`NEGATION_CANDIDATE_UNVALIDATED`/`ANECDOTAL_NEGATION`; MGMT-004 =
`MANAGEMENT_CANDIDATE_UNVALIDATED`; Q3-001/Q3-005 = `BAD_TRADE`; remaining 10
Q1-Q3 losses = `GOOD_TRADE_NORMAL_LOSS`.

---

## 9. Q4 EXACT STATE

Reconstructed directly from `docs/trader_apprenticeship/AI_TRADER_Q4_*` files
(this old session authored them directly, so these figures are also
first-hand, not re-derived from a summary):

```
Q4_COMPLETE                 = NO
LAST_CONSUMED_Q4_BAR        = 378
LAST_CONSUMED_TIMESTAMP     = 2020-10-07T02:29:59 UTC  (epoch 1602037799)
NEXT_UNSEEN_Q4_BAR          = 379
BAR_379_PREVIOUSLY_CONSUMED = NO   (mechanically verified by this session's own
                               causal-integrity audit, Q4_GOVERNANCE_SCOPE_AUDIT_001.md
                               — not re-verified again here, per §5 REUSE rule)

TRADES_TOTAL                = 0
MGMT004_TRIGGERS_TOTAL      = 0
POSITION_STATE               = FLAT (never opened a Q4 position)
```

### Q4 P007 events

```
EVENT_ID          Q4-P007-001
STATUS             RESOLVED
CLASSIFICATION      SUPPORT / DEEP_RECLAIM
BARS                103-114 (2020-10-02, ~02:29-05:29 UTC)
NOTE                richest single field-capture in the pattern's history —
                    thin-volume fakeout-reclaim → real-volume deeper break →
                    real-volume durable reclaim
```

```
EVENT_ID          Q4-P007-002
STATUS             RESOLVED
CLASSIFICATION      SUPPORT / SLOW_RECLAIM
BARS                213-222 (2020-10-05, ~07:14-09:29 UTC)
```

```
EVENT_ID          Q4-P007-003
STATUS             OPEN / UNRESOLVED  ← DO NOT RESOLVE FROM MEMORY OR INFERENCE
CLASSIFICATION      not yet assigned — depends only on bar 379+
TRIGGER_BAR         340 (2020-10-06 15:59:59 UTC) — close-based break of both
                    1902.349 and H1 EMA50 together, on real volume (1268)
LAST_KNOWN_STATE    at bar 378 (freeze point): 38 consecutive bars below EMA50
                    (bars 340-378), the longest sub-EMA excursion in the entire
                    Q1-Q4 record, still on real/heavy volume, no reclaim
                    attempt of substance
CONTEXT             bars 352-353 produced the single heaviest volume of the
                    entire quarter (4743, then 6203 — nearly double the prior
                    record of 3626 at bar 57) and the largest sustained decline
                    of the whole apprenticeship (~31pt), breaking both the
                    P007-001/002 deep-pullback low (1889.866) and the Q4
                    opening-day dip low (1884.72). Read as probable macro/news
                    event by volume signature only — NO specific cause is
                    asserted anywhere in the record (no verified news feed was
                    ever available to this apprenticeship)
FROZEN COUNTERS     consecutive_bars_below_ema50 = 38 (bars 340-378 inclusive)
                    deepest_low_this_episode = 1872.898 (bar 375)
                    heaviest_volume_this_episode = 6203 (bar 353)
```

Full field-capture for all three events (BREAK_DEPTH_ATR, WICK_BODY_RATIO,
FOLLOW_THROUGH_N_BAR, SESSION, ACTIVITY_MAGNITUDE, etc.) is in
`AI_TRADER_Q4_PATTERN_LEDGER.md` — do not re-derive it here or from memory.

---

## 10. Q4 INTEGRITY INCIDENTS

```
INCIDENT_ID   TIMESTAMP_LABEL_DRIFT (bars 68-100, two separate occurrences)
DESCRIPTION    mental-arithmetic UTC clock-label drift (up to 30min) after this
               session stopped calling python3 to verify every single bar and
               switched to arithmetic diff-checking for gaps only
SCIENTIFIC_IMPACT  NONE — every replay_step diff was independently verified as
               exactly 900s (or a logged gap); no bar was ever skipped,
               duplicated, or misread. Only the human-readable label attached
               to already-correct data was wrong.
RESOLUTION     corrected in place in AI_TRADER_Q4_M15_LOG.md with a visible
               "TIMESTAMP LABELING CORRECTION" note — NOT silently rewritten.
               Practice changed afterward: timestamps now computed via python3
               batch calls at write-time, not mental arithmetic during stepping.
INVALIDATES_Q4  NO
```

```
INCIDENT_ID   DATA_QUALITY_ANOMALY (bars 135-136)
DESCRIPTION    two consecutive bars with flat OHLC (open=high=low=close) and
               fractional volume (153.5, 133.25 — every other Q4 bar has
               whole-number volume) — most consistent with a synthetic/
               interpolated tick rather than two real 15-min candles
SCIENTIFIC_IMPACT  bars are present (not a GAP — no missing interval), but
               excluded from any morphology/volume-magnitude conclusion.
               No apprenticeship decision was open across these 2 bars.
RESOLUTION     disclosed in AI_TRADER_Q4_M15_LOG.md, retained in the causal
               sequence, flagged as excluded from analysis
INVALIDATES_Q4  NO
```

```
INCIDENT_ID   TOOLING_STALENESS_data_get_study_values (bar 191 onward)
DESCRIPTION    the data_get_study_values MCP tool began returning implausible,
               persistent values for AI_TRADER_CONTEXT_V1 (an EMA50 change of
               ~32pt in one 15-min bar — mathematically impossible for a
               50-period EMA)
SCIENTIFIC_IMPACT  isolated to that one tool's output; confirmed via
               screenshot AND data_get_pine_tables (independent methods, both
               agreeing) that the underlying replay/indicator computation was
               correct. From bar 191 onward, exact numeric H1 EMA50 was
               unavailable — only qualitative ABOVE/BELOW/slope — a disclosed
               precision limitation, not a data-integrity break.
RESOLUTION     data_get_pine_tables adopted as the working alternative for
               AI_TRADER_CONTEXT_V1 from bar 191 onward
INVALIDATES_Q4  NO
```

```
INCIDENT_ID   GAP-151 through GAP-154
DESCRIPTION    3× standard daily-rollover gaps (75min) + 1× standard weekend
               gap (49.25h), all mechanically detected via the replay
               pointer's own timestamp diff and independently zero-price-gap
               verified (last close == first open, exact)
SCIENTIFIC_IMPACT  NONE — all standard, expected, correctly classified
RESOLUTION     logged in REPLAY_DATA_GAP_LEDGER.md
INVALIDATES_Q4  NO
```

```
INCIDENT_ID   Q4_GOVERNANCE_SCOPE_AUDIT_001 (bars 288-378 authorization question)
DESCRIPTION    a later mandate asserted a prior "CEO mandate" had required
               freezing Q4 at bar 287 with design-only authorization; this
               was checked mechanically against the actual conversation
               history and found FALSE — the actual immediately-preceding
               instruction had been an explicit "continue autonomously to the
               end of Q4 without stopping," under which bars 288-378 were
               correctly consumed
SCIENTIFIC_IMPACT  NONE on the replay itself — a full mechanical audit of bars
               288-378 (bar-range contiguity, timestamp monotonicity, no
               future data exposed, P007-003 pre-registered before resolution
               and left unresolved) returned PASS on every check
RESOLUTION     documented fully, with the correction stated explicitly (not
               silently accepted), in Q4_GOVERNANCE_SCOPE_AUDIT_001.md
               (committed, d3ce871)
INVALIDATES_Q4  NO
```

None of the above invalidates any portion of the Q4 record. All are disclosed
in place in their source files — do not re-litigate any of them without new
evidence (see §17).

---

## 11. MANAGEMENT / MGMT-004

```
MGMT004_STATUS            = MANAGEMENT_CANDIDATE_UNVALIDATED (unchanged since
                             end of Q3 — Q4 has not yet produced a single
                             eligible trade to test it against)
AUTHORITATIVE_SPEC        = docs/trader_apprenticeship/
                             AI_TRADER_Q4_MANAGEMENT_PROSPECTIVE_PROTOCOL_V1.md
                             (the frozen forward-test spec) — the discovery-
                             stage full write-up is in
                             AI_TRADER_MANAGEMENT_POLICY_LIBRARY_V1.md
TRIGGER                    = first M15 close at or beyond +1.0R favorable
                             excursion from entry
ACTION                     = move stop to exactly entry price (0R), full
                             position, no partial exit, target unchanged
PROSPECTIVE_FREEZE_POINT   = frozen before any Q4 bar was consumed — never
                             redefined at any point during Q4 bars 1-378
Q4_TRIGGER_COUNT            = 0 (zero Q4 trades have been opened, so MGMT-004
                             has had zero opportunities to trigger)
KNOWN_LIMITATIONS           = discovery evidence (Q1-Q3) is n=4, all from Q2,
                             all SHORT-only, single continuous regime —
                             disclosed, unresolved by Q4 so far
VALIDATED?                  = NO — remains UNVALIDATED; clearing the Q4
                             forward-test gate (were it to trigger and hold up)
                             would move it only to a graduated research status,
                             never to "VALIDATED" outright (that requires
                             independent Statistician/Red-Team-tier review,
                             per this apprenticeship's own standing convention)
```

Do not modify or re-evaluate this spec. Any future Q4 trade must be frozen
independently of MGMT-004 first (entry logic must never be influenced by
MGMT-004's existence), then the dual CONTROL/SHADOW ledger tested against
`AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md` using the frozen spec verbatim.

---

## 12. P007

```
P007_DEFINITION        = "Severe support/H1-EMA50 break on record/heavy
                          volume, then reclaim — continuation resumes."
                          (GOLD_BEHAVIOR_MODEL_V1.md)
AUTHORITATIVE_PATH      = docs/trader_apprenticeship/GOLD_BEHAVIOR_MODEL_V1.md
                          (Q1-Q3 raw log, §1) +
                          AI_TRADER_Q4_PATTERN_LEDGER.md (Q4 events)
Q1-Q3_EVIDENCE_SUMMARY  = raw n=31 (22 SUPPORT/1 COUNTEREXAMPLE/8 AMBIGUOUS);
                          strict-prospective n=23 (15/1/7) — both tallies
                          preserved, not merged. STATUS = DEVELOPING_PATTERN,
                          never traded, never TRADEABLE_EDGE.
Q4_EVENTS                = Q4-P007-001 (SUPPORT/DEEP_RECLAIM, resolved),
                          Q4-P007-002 (SUPPORT/SLOW_RECLAIM, resolved),
                          Q4-P007-003 (OPEN/UNRESOLVED — see §9)
CURRENT_OPEN_EVENT       = Q4-P007-003
CURRENT_FROZEN_STATE     = trigger bar 340, 38 consecutive bars below EMA50 as
                          of the bar-378 freeze point, classification NOT
                          assigned
WHAT_RESOLVES_IT          = bar 379+ prospectively — either a genuine
                          close-based EMA50 reclaim (→ SUPPORT, sub-type TBD by
                          how many bars it took) or continued/deepening
                          acceptance without reclaim (→ likely COUNTEREXAMPLE,
                          the pattern's first true one in Q4 and possibly the
                          strongest counterexample in the whole apprenticeship
                          given the record volume and duration already
                          observed)
MUST_NOT_CHANGE           = the pattern's core definition (above), the
                          pre-registered PRE-CLASSIFICATION already written for
                          Q4-P007-003 before any bar past 340 was read, and the
                          raw vs. strict-prospective Q1-Q3 tally split — none
                          of these may be edited retrospectively to fit
                          whatever bar 379+ eventually shows
```

Do not resolve Q4-P007-003 in this document or from inference. It resolves
only through further causal replay.

---

## 13. TRADINGVIEW / MCP STATUS

**Approved accelerator**: `CAUSAL_REPLAY_ACCELERATOR_V1`, commit
`cf6f470cd311ae1ff9a35ae72fd0c9edaed67ec6`, repo
`https://github.com/rzvqp/tradingview-mcp-aql.git`, branch
`integration/causal-replay-accelerator-v1`. **Verified real** (not just
asserted) by this old session: the commit exists exactly as claimed, checked
out in a separate local worktree at `C:\Users\MEDION GAMING\tradingview-mcp-integration`,
and its `src/tools/causal_replay.js` genuinely registers `causal_step_snapshot`,
`causal_run_until_gate`, `causal_commit_decision`, and `causal_replay_status`
(a fourth, read-only tool not mentioned in earlier mandates but present in
code) with the described contracts (fail-closed pointer check via
`expected_pointer_before`, 8-bar heartbeat ceiling for the gated mode,
mandatory commit-before-next-bar). Two prior commits on the branch (`9986467`,
`beab111`, both already pushed) match this old session's own memory of a
"VE_CAUSAL_REPLAY_ACCELERATOR_V1" mandate and a Red Team review verdict
(`PASS_WITH_NONBLOCKING_NOTES`, `SAFE_FOR_AI_TRADER_Q4 = YES`) from a parallel
session — internally consistent, corroborated by real git artifacts, not
fabricated.

**Old TradingView dependency**: the main worktree `C:\Users\MEDION GAMING\tradingview-mcp`
(commit `164c9c1`) contains the pre-accelerator, un-augmented server — still
fully functional in principle, but does NOT expose the three (four) causal_*
tools.

**What was verified**: (1) the accelerator code is real and correctly built,
(2) the un-accelerated main worktree is what `.mcp.json` originally pointed
both server entries at — **`.mcp.json` was edited by this old session** to
point both `tradingview` and `tradingview2` server entries at
`tradingview-mcp-integration\src\server.js` instead (current committed
content of the file is quoted in full below), specifically to prevent any
future reconnection from silently falling back to the old un-accelerated
code, (3) two live `node.exe` processes running the accelerator's `server.js`
were found already running (PIDs 14036/24240 as of the old session's last
check — **do not trust these PIDs are still current**, a restart creates new
ones), confirmed healthy (Responding=True, low CPU, no crash-loop).

**What was NOT verified / the actual blocker**: despite the config being
correct and the server process(es) being alive, **this old session's own
conversation never once saw any tradingview MCP tool in its tool list — old
or new — for the remainder of its life.** Exhaustive diagnosis found: no
`claude` CLI on PATH or in standard install locations; the host is Claude
Desktop (a "CCD"/Cowork local Code session, id
`local_e0f0f7ad-c88a-4b24-b27b-e865240db734`, titled "AI TRADER"); nothing in
that old session's available tools could force a live MCP-connection
re-attach into an already-running conversation. **Conclusion reached (and not
contradicted by anything since): reconnecting the TradingView MCP server from
inside a conversation is impossible; it requires restarting that session (or
Claude Desktop itself) from outside.** If THIS new session is reading this
file, it likely means that restart already happened — the new session's
**first action regarding TradingView** should simply be to check whether the
causal_* tools are now present (a single, cheap check) before assuming
anything else needs fixing.

### `.mcp.json` — exact current content (in `C:\Users\MEDION GAMING\tradingview-mcp\.mcp.json`)

```json
{
  "mcpServers": {
    "tradingview": {
      "command": "node",
      "args": ["C:\\Users\\MEDION GAMING\\tradingview-mcp-integration\\src\\server.js"]
    },
    "tradingview2": {
      "command": "node",
      "args": ["C:\\Users\\MEDION GAMING\\tradingview-mcp-integration\\src\\server.js"],
      "env": {
        "TV_CDP_PORT": "9223"
      }
    }
  }
}
```

**Why Q4 is being (potentially) migrated away from live TradingView replay**:
not because the accelerator failed — it's real, reviewed, and ready — but
because the MCP *connection* itself proved unrecoverable from inside a running
conversation multiple times in a row, which is an operational availability
problem, not a scientific one. The CSV replay adapter (§14) is the proposed
way to make Q4 continuation resilient to exactly this kind of host-level MCP
outage in the future.

```
TRADINGVIEW_MCP_REQUIRED_FOR_FUTURE_Q4 = YES, until CSV_CAUSAL_REPLAY_ADAPTER_V1
                                          actually passes review — see §14 for
                                          why this is NOT yet "NO" despite the
                                          adapter's code existing
```

---

## 14. CSV REPLAY TRANSITION

```
DIRECTORY        = ai_trader/csv_causal_replay/ (UNTRACKED — not yet committed)
CONTENTS          __init__.py, engine.py, errors.py, gap_classification.py,
                  identity.py, persistence.py, sealed_reader.py, types.py,
                  fixtures/materialize_sealed_fixture.py,
                  fixtures/data/Q4_SEALED_1_378.csv (+ manifest JSON),
                  tests/conftest.py — NO actual test_*.py files exist yet,
                  only fixture setup
```

**What it's meant to do**: per its own `__init__.py` docstring, this is
`CSV_CAUSAL_REPLAY_ADAPTER_V1`, citing a "CEO mandate, 2026-08-30," intended to
replace the *live TradingView replay* as Q4's data source (not the
apprenticeship's decision logic — purely the bar-feed mechanism), porting the
same causal-exposure abstraction (`step`/`commit_decision`/`run_until_gate`)
from `tradingview-mcp/src/core/causal_replay.js`.

**Implementation status**: substantially coded, not just a plan.
`sealed_reader.py` implements a hardened streaming CSV reader that makes bars
beyond a boundary physically unreachable (never a bulk `read_csv().head(N)`).
`engine.py` implements the full engine with a hard `SealedBoundaryError` /
`HybridModeLockedError`. The fixture
`fixtures/data/Q4_SEALED_1_378.csv` is a materialized 2,378-row sealed dataset
(2,000 warm-up bars + exactly the 378 Q4 bars this old session itself
consumed), with `sealed_through_bar_index: 378` in its manifest — i.e. it was
built to match this exact Q4 freeze point, and its test fixture
(`conftest.py`) seeds `last_committed_bar_index=378`,
`open_event_state_reference="Q4-P007-003:OPEN"` — explicitly matching
`AI_TRADER_Q4_M15_LOG.md`'s own last line.

**⚠ Critical gap — flagged, not resolved**: the code repeatedly cites two
documents that **do not exist anywhere on disk**:
`docs/trader_apprenticeship/CSV_CAUSAL_REPLAY_ADAPTER_V1_SPEC.md` and
`CSV_CAUSAL_REPLAY_ADAPTER_V1_HANDOFF.md`. A repo-wide search (across this
repo, the main `ai_quant_lab` hub, and `ai_quant_lab-data-acq`) found **no**
VE mandate-status document and **no** Red Team review file for this adapter
anywhere — unlike the TradingView accelerator (§13), which genuinely does have
a corroborated review trail. **This means: unlike the TradingView
accelerator, the CSV adapter has NOT been shown to be reviewed or approved by
anything outside its own source code.** No parity gate (a proof that the CSV
adapter reproduces identical bars/behavior to the TradingView replay it would
replace) exists anywhere either.

```
VE_MANDATE_STATUS        = code exists citing a mandate; the mandate document
                            itself NOT_FOUND on disk
RED_TEAM_REVIEW_REQUIRED  = YES — and has NOT yet happened (no review artifact
                            found)
PARITY_GATE               = NOT_FOUND — required before this adapter can be
                            trusted to reproduce the TradingView replay's
                            behavior; does not exist yet
BAR_379_SEALED_BOUNDARY   = correctly implemented and consistent with the live
                            record (378/379 boundary matches exactly)
AI_TRADER_RESUME_CONDITION = the CSV adapter should NOT be used to resume Q4
                            until (a) its own spec/handoff docs exist, (b) a
                            parity gate proves it matches TradingView replay
                            behavior for at least the already-known bars 1-378,
                            and (c) Red Team has reviewed it — none of these
                            three has happened yet
```

Do not inspect or consume bar 379 via this adapter or any other path without
those three gates passing.

---

## 15. PROCESS / SERVICE INVENTORY

Live-observed by this old session, 2026-08-30 (timestamps below are all from
this morning's boot/logon, ~10:17):

```
PROCESS                     PID          COMMAND                                          PURPOSE                    OWNING_COMPONENT     SAFE_TO_RESTART   STATE_DEPENDENCY
terminal64.exe               8424        FP Trading MT5 Terminal.exe                       MT5 broker terminal        broker connection    NO — would drop      MT5 session
                                                                                                                                              live MT5 session
python.exe (entrypoint)      9012, 11460  -m ai_trader.new_brain_live.entrypoint            LIVE_SHADOW loop (§3.1)    New Brain            YES (task-managed,   new_brain_live_state/
                                                                                                                                              RestartOnFailure)     xauxsd_m15.db
python.exe (soak)            9092, 11452  -m ...mt5_demo_bridge.soak.run_soak_live          S5 MT5 demo soak (§3.2)   Strategy platform    CAUTION — mid-soak    new_brain_live_state/
                                                                                                                                              restart triggers      s5_mt5_demo_soak/*
                                                                                                                                              reconciliation, not   
                                                                                                                                              destructive by design 
python.exe (ve_tower)        11728, 5764  -m ve_tower_worker.cli --host 127.0.0.1 --port 0  ve_tower worker (unrelated
                                                                                              to AI Trader specifically — not investigated further, out of this handoff's scope)
node.exe (codex MCP)         3752, 11036  codex.js mcp-server                                unrelated MCP server (Claude Desktop's own codex integration, not AI Trader)
node.exe (tradingview accel) 14036, 24240 (as of old session's last check — LIKELY STALE)   tradingview-mcp-integration/src/server.js — see §13
```

Duplicate-instance note (§3.1/§3.2): both `entrypoint.py` and `run_soak_live.py`
show exactly TWO live processes each, all four started within an 8-second
window this morning. Most likely a BootTrigger+LogonTrigger near-simultaneous
firing at today's reboot, given `MultipleInstancesPolicy=IgnoreNew` should
otherwise prevent this — **not independently confirmed**, flagged in §21.

Do not terminate anything above under this mandate.

---

## 16. AUTOMATION / REPORTING

```
Telegram reporting
  CODE       = ai_trader/telegram_notifier/ (sender.py, credentials.py,
               rate_limiter.py, redaction.py, types.py)
  CROSS-REPO ENTRY POINT = C:\Users\MEDION GAMING\tools\notify.py
               (standalone, outside all repos), invoked as:
               notify.py "<DIVISION>" "<status line>" ["<commit>"] ["<verdict>"]
               reads bot token/chat ID from the Windows registry (HKCU\Environment)
  DOCS       = TELEGRAM_NOTIFIER_PHASE5_DESIGN.md,
               TELEGRAM_NOTIFIER_PHASE5_IMPLEMENTATION_REPORT.md,
               TELEGRAM_NOTIFIER_CROSS_DIVISION_USAGE.md
  LAST_KNOWN_STATUS = implemented per docs; not exercised by this old session
  RESTART_REQUIREMENT = none — it's invoked per-call, not a persistent process

Scheduler
  PROCESS/PATH = Windows Scheduled Tasks AITraderLiveShadow (XML checked in:
               ai_trader/new_brain_live/AITraderLiveShadow_task.xml) and
               AITraderS5MT5DemoSoak (confirmed live, State=Running, but its
               XML is NOT checked into this repo — created directly in Task
               Scheduler at some point outside this repo's history)
  PURPOSE      = unattended restart of the two runtime loops, §3.1/§3.2
  LAST_KNOWN_STATUS = both Running, LastRunTime 2026-08-30 10:17:24, both
               LastTaskResult=267009 (currently executing, not an error)
  RESTART_REQUIREMENT = self-managing (RestartOnFailure, 999 retries, 1min
               interval) — no manual restart needed under normal operation

Heartbeat/status/checkpoint files
  ai_trader/new_brain_live/heartbeat.py — overwritten current-status snapshot
               via SqliteStateStore, read by ai_trader/new_brain_live/watchdog.py
  new_brain_live_state/s5_mt5_demo_soak/health.json — soak loop's own health
               snapshot (loop_alive_as_of, mt5_connected,
               last_reconciliation_as_of, safety_blocked) — NOT read this
               session, recommended as new session's first MT5 check (§19)
  research_log/SESSION_STATE.md (this repo), plus equivalents in
               ai_quant_lab-data-acq and ai_quant_lab/alpha_instance_2
  AI_TRADER_PROJECT_STATE.md, AI_TRADER_NEXT_SESSION.md (this repo root)

Company/project-level memory index
  ai_quant_lab/COMPANY_STATE.md — the top-level cross-department pointer doc.
               Its own instructions: verify repo HEADs, read department-
               specific authoritative artifacts, "wait for CEO authorization
               before starting any new work." ⚠ States
               `Q4_APPRENTICESHIP_STARTED = NO` as of its own STATUS_DATE
               2026-08-29 — this is now STALE and CONTRADICTS the actual file
               record (378 Q4 bars exist, dated up to 2026-08-30). See §21.
```

No test notification was sent to verify Telegram status — not strictly
necessary and this mandate discourages it unless required.

---

## 17. DO_NOT_REOPEN_WITHOUT_NEW_EVIDENCE

- **PATTERN-007's Q1-Q3 raw tally (n=31) and strict-prospective tally (n=23)**
  — both are final for that period; the difference between them is itself the
  documented finding (batching-integrity correction), not an unresolved
  question. Do not re-derive either number.
- **The 4 Grade-C Negation candidates** — none were promoted, none were
  rejected; they simply lack Grade-B+ evidence. Do not manufacture a promotion
  from a single new Q4 data point.
- **POLICY-1/2/3 (TP1-based management)** — `MANAGEMENT_NOT_SUPPORTED` for lack
  of any triggering trade across the whole Q1-Q3 record. Do not retest without
  a trade that actually reaches a genuine TP1.
- **The Q2 duplicate-log question** — explicitly `UNRESOLVED`, both files
  retained. Do not pick one as authoritative without doing the diff-against-
  `TRADE_EVIDENCE_LOG.md` work the forensic review itself recommended and never
  did.
- **Live/real-money execution** — no LIVE adapter exists anywhere in this
  codebase (`execution_mode.py` has only `DISABLED`/`MT5_DEMO_ONLY`). This is
  not a config flag waiting to be flipped; it is a structural absence. Do not
  attempt to add one without a fresh, explicit CEO mandate.
- **Q1 2021 data** — never authorized, never touched, at any point in the
  entire apprenticeship (Q1-Q4 2020 only). Remains prohibited.
- **Sealed `ve_brain.n6._SEALED_CATALOG`** — structurally cannot accept new
  strategies; `RealEVDecisionEngine` was built specifically as the sanctioned
  workaround (§3.4). Do not attempt to modify the sealed catalog itself.
- **The "freeze at bar 287" governance claim** — mechanically proven false
  against the actual conversation record (§10, `Q4_GOVERNANCE_SCOPE_AUDIT_001.md`).
  Do not treat any future reference to "bar 287 as the authorized boundary" as
  correct without re-checking it — the real boundary is bar 378/379 (§9).

---

## 18. REUSE > REBUILD

```
COMPONENT                          DECISION                REASON
S5 (strategy spec + validation)     REUSE_AS_IS             independently validated
                                                             (§4), do not retest
MT5 bridge (mt5_demo_bridge/)       REUSE_AFTER_VERIFICATION  code is sound and live-
                                                             running, but has an
                                                             uncommitted diff (§2/§3.5)
                                                             and an unresolved risk-
                                                             sizing discrepancy (§6) —
                                                             verify both before trusting
                                                             blindly, don't rebuild
Risk engine (risk_manager/,         REUSE_AFTER_VERIFICATION  sound design, but the 5%
  risk_manager_live/)                                        vs 0.5% discrepancy (§6)
                                                             needs a decision, not a
                                                             rebuild
Decision engine (RealEVDecisionEngine,
  ve_brain.decide_n6)                REUSE_AS_IS             both paths work as
                                                             designed and documented
                                                             (§3.4); do not merge or
                                                             alter them
Strategy Catalog / Router           REUSE_AS_IS              working exactly as
                                                             designed (§3.3)
Q1-Q4 apprenticeship ledgers        REUSE_AS_IS               all authoritative (§7);
                                                             Q4 specifically also
                                                             REQUIRES a commit soon
                                                             (§2) — reuse, don't
                                                             rebuild, but don't lose it
P007 (definition + Q1-Q4 evidence)   REUSE_AS_IS              do not redefine; Q4-P007-003
                                                             specifically stays OPEN
MGMT-004                            REUSE_AS_IS              frozen spec, do not retune
                                                             (§11)
Failure Engineering / Negation      REUSE_AS_IS              all Grade C, stable, no
  Library                                                     new evidence to act on
Management/Exit Research            REUSE_AS_IS              MGMT-004's discovery
                                                             evidence, do not redo
TradingView causal-replay            REUSE_AFTER_VERIFICATION  code verified real and
  accelerator (cf6f470)                                       correct (§13) but its
                                                             LIVE CONNECTION has never
                                                             once been confirmed
                                                             working — verify
                                                             connectivity before relying
                                                             on it, don't rebuild it
CSV_CAUSAL_REPLAY_ADAPTER_V1        DO_NOT_USE (yet)          code exists and looks
                                                             functional, but has NO
                                                             spec doc, NO handoff doc,
                                                             NO parity gate, NO Red
                                                             Team review on file (§14)
                                                             — do not treat as ready;
                                                             also do not rebuild it,
                                                             the code itself may well be
                                                             fine once reviewed
```

No component above has a concrete blocker that would justify a rebuild
recommendation — every "REUSE_AFTER_VERIFICATION" or "DO_NOT_USE (yet)" is a
verification/review gap, not a design flaw found in the code itself.

---

## 19. NEW SESSION STARTUP ORDER

Exact cold-start sequence — no order submission during any of this:

1. **Verify Git/worktree identity** — confirm `C:\Users\MEDION GAMING\ai_quant_lab-research-main`
   is on branch `ai-trader-implementation`, HEAD matches (or is a descendant
   of) `beab1119...`, and local == remote (`git status --short --branch`).
2. **Read this file in full** (`AI_TRADER_FULL_RUNTIME_HANDOFF_2026-08-30.md`) —
   already done if you're reading this.
3. **Read the latest AI Trader state/ledger files** — at minimum
   `AI_TRADER_Q4_M15_LOG.md`, `AI_TRADER_Q4_PATTERN_LEDGER.md` (§7, §9) — do
   not trust this handoff's Q4 summary as a substitute for the primary source.
4. **Verify S5 identity** — re-read
   `ai_trader/new_brain_live/strategy_platform/s5_opening_range_breakout.py`
   and confirm it still matches the spec quoted in §4. Do not retest it.
5. **Verify MT5 bridge/runtime state, read-only** — read
   `new_brain_live_state/s5_mt5_demo_soak/health.json` and
   `execution_ledger.db` directly (§5's UNKNOWNs should be resolved here, by
   the new session, not assumed).
6. **Verify open/pending MT5 orders BEFORE enabling any execution** — this is
   the one item this old session could genuinely not check (§5) — do it first,
   before anything execution-adjacent.
7. **Verify risk config** — confirm whether the 5%/0.5% discrepancy (§6) has
   been intentionally resolved or is still live; do not silently "fix" it
   without a decision.
8. **Verify CSV causal replay adapter handoff, when available** — check
   whether `CSV_CAUSAL_REPLAY_ADAPTER_V1_SPEC.md` /
   `..._HANDOFF.md` now exist (§14) — they did not as of this handoff.
9. **Verify Red Team approval of the CSV adapter** — check for a review
   artifact; none existed as of this handoff (§14). Do not use the adapter
   without one.
10. **Restore Q4 durable state** — confirm `LAST_CONSUMED_Q4_BAR = 378`,
    `LAST_CONSUMED_TIMESTAMP = 2020-10-07T02:29:59 UTC` against whatever
    replay mechanism (TradingView MCP or, once cleared, the CSV adapter) is
    actually in use — mechanically, not by trusting this document alone.
11. **Confirm next unseen Q4 bar** — must be exactly 379, confirmed via a
    read-only status call before any step/advance call.
12. **Resume prospectively only after all gates above pass** — in ATOMIC mode
    first, since Q4-P007-003 remains open and capable of resolving (§9, §12).

---

## 20. NEXT SESSION HARD SAFETY

```
NEW_SESSION_ORDER_SUBMISSION_DEFAULT = DISABLED_UNTIL_RUNTIME_VERIFIED
NEW_SESSION_Q4_REPLAY_DEFAULT         = STOPPED_UNTIL_CSV_ADAPTER_PASS
                                        (or, alternatively, until TradingView
                                        MCP connectivity is freshly confirmed —
                                        either path is acceptable, neither is
                                        currently confirmed working)
NEW_SESSION_S5                        = REUSE_EXISTING_VALIDATED_SPEC
NEW_SESSION_MGMT004                    = PRESERVE_PROSPECTIVE_SPEC
NEW_SESSION_P007                       = PRESERVE_FROZEN_STATE
Q1_2021                                = PROHIBITED UNTIL CEO AUTHORIZATION
```

---

## 21. CONTRADICTIONS / UNKNOWN STATE

### CONTRADICTIONS

1. **`ai_quant_lab/COMPANY_STATE.md` states `Q4_APPRENTICESHIP_STARTED = NO`**
   as of its own `STATUS_DATE 2026-08-29` — this directly contradicts the
   actual file record in this repo (378 Q4 bars consumed, files dated through
   2026-08-30). `COMPANY_STATE.md` is simply stale on this specific point; it
   was not updated after Q4 apprenticeship work began. Do not trust it for Q4
   status — trust `AI_TRADER_Q4_M15_LOG.md` directly.
2. **Risk sizing**: the real MT5 order sizer uses 5% risk-per-trade;
   `risk_manager`'s configured default is 0.5%. The 0.5% figure is enforced as
   a *gate* but never actually reaches the real order's size. This is a live
   discrepancy in running code (§6), not a typo — needs an explicit decision,
   not a silent pick.
3. **`AITraderS5MT5DemoSoak` scheduled task is confirmed running live**, but
   no XML for it exists anywhere in this git repo (only `AITraderLiveShadow`'s
   XML is checked in) — meaning it was created directly in Task Scheduler at
   some point, out of band with version control. Reproducing this task from a
   fresh checkout would currently require manual recreation.
4. **CSV adapter code cites documents that don't exist** (§14) — the code
   itself is real and detailed, but its own cited spec/handoff docs were
   apparently never written or never committed. This is either an in-progress
   commit that hasn't landed yet, or a genuine gap — not distinguishable from
   here.

### UNVERIFIED_RUNTIME_STATE

- Whether the 2x-duplicate `entrypoint.py` and `run_soak_live.py` processes
  (§3.1, §3.2, §15) are benign (near-simultaneous Boot+Logon triggers) or a
  genuine `IgnoreNew`-policy failure — not independently confirmed.
- Current MT5 open positions / pending orders (§5) — the last figure on file
  is a 2026-08-29 audit (zero), now >24h stale.
- Whether the TradingView MCP connection has been restored since this old
  session's last check (it had not, as of this handoff's writing).

### STALE_DOCUMENTS

- `ai_quant_lab/COMPANY_STATE.md` — Q4 status specifically (see contradiction
  #1 above). Other sections of it were not re-audited here.
- `GOLD_BEHAVIOR_MODEL_V1.md` §7 (the CEO-review synthesis) — last run at
  PATTERN-007 n=21, never re-run against the final Q3 n=31, let alone the Q4
  events on top of it (§7 note in this document).

### MISSING_ARTIFACTS

- `docs/trader_apprenticeship/CSV_CAUSAL_REPLAY_ADAPTER_V1_SPEC.md`
- `CSV_CAUSAL_REPLAY_ADAPTER_V1_HANDOFF.md`
- Any Red Team review artifact for the CSV adapter
- A Windows Scheduled Task XML for `AITraderS5MT5DemoSoak` (task exists live,
  file does not)

### SESSION_ONLY_KNOWLEDGE_NOT_FOUND_ON_DISK

**One item exists**, and it is itself already remedied by a second document,
not by this section: the full, blow-by-blow chronological decision log of the
old conversation that produced this handoff (every mandate received, every
diagnostic step taken to investigate the MCP disconnection, the exact
reasoning for each rejected alternative) lived only in that conversation and
was captured, before this document, in a separate, narrower handoff file:

```
C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\AI_TRADER_HANDOFF_2026-08-30.md
```

That file is scoped specifically to the Q4-replay-and-MCP-reconnection
episode (a subset of what this document covers) and contains more granular
session narrative than this document repeats. **Read it too** if the MCP
reconnection story in §13 here isn't detailed enough — it is the primary
source for that specific sub-episode. Everything else material that this old
session learned has been transcribed into the actual repository files cited
throughout this document; nothing else was identified as existing only in
conversational memory.

---

## 22. FINAL RECOVERY SNAPSHOT

```
AI_TRADER_FULL_RUNTIME_HANDOFF_COMPLETE = YES

AI_TRADER_REPO      = C:\Users\MEDION GAMING\ai_quant_lab-research-main
AI_TRADER_BRANCH    = ai-trader-implementation
AI_TRADER_HEAD      = beab11193414587b022306cc22b133ed52b21d2f
LOCAL_REMOTE_MATCH  = YES

S5_PRESENT              = YES
S5_IDENTITY_VERIFIED    = YES
S5_STATUS               = VALIDATED (independent), STATUS_CANDIDATE_READY,
                          currently RUNNING live on MT5 DEMO
                          (FPTradingLLC-Demo), never retested or altered by
                          this handoff

MT5_BRIDGE_PRESENT      = YES
MT5_BRIDGE_RUNNING      = YES (2 processes observed, see §15 duplication note)
MT5_ACCOUNT_MODE        = DEMO (by code design; not live-requeried this session)
ORDER_SUBMISSION_CURRENTLY_ENABLED = UNKNOWN (structurally DEMO-only, no LIVE
                          path exists at all; whether the DEMO path is
                          currently actively submitting was not queried live)
OPEN_POSITIONS          = UNKNOWN (not queried this session — see §5)
PENDING_ORDERS          = UNKNOWN (not queried this session — see §5)
DEDUP_STATE_VERIFIED    = NO (mechanism confirmed present in code, current
                          value not read)

RISK_CONFIG_VERIFIED    = YES (read and documented, §6) — but a genuine
                          unresolved 5%/0.5% discrepancy exists within it

Q1_STATE_RECOVERABLE    = YES
Q2_STATE_RECOVERABLE    = YES (with one disclosed unresolved duplicate file)
Q3_STATE_RECOVERABLE    = YES
Q4_STATE_RECOVERABLE    = YES (but currently UNCOMMITTED — see §2's warning)

Q4_COMPLETE              = NO
LAST_CONSUMED_Q4_BAR     = 378
LAST_CONSUMED_TIMESTAMP  = 2020-10-07T02:29:59 UTC
NEXT_UNSEEN_Q4_BAR       = 379
BAR_379_PREVIOUSLY_CONSUMED = NO

OPEN_P007_EVENT          = Q4-P007-003
OPEN_P007_STATUS         = OPEN / UNRESOLVED (38 consecutive bars below EMA50
                          at freeze point; classification not assigned)
MGMT004_STATUS           = MANAGEMENT_CANDIDATE_UNVALIDATED
MGMT004_TRIGGERS_TOTAL   = 0

TRADINGVIEW_MCP_REQUIRED = YES (until the CSV adapter passes its three
                          missing gates — spec doc, parity gate, Red Team
                          review — or TradingView MCP connectivity is freshly
                          reconfirmed)
CSV_REPLAY_TRANSITION_STATUS = CODED_BUT_UNREVIEWED — not ready for use

EXECUTION_SAFE_TO_RESUME_NOW = NO (open positions/orders unverified; risk-
                          sizing discrepancy unresolved; see §19 startup order)
Q4_SAFE_TO_RESUME_NOW    = NO (no working replay connection confirmed as of
                          this handoff; restoration gate at bar 378 must pass
                          first, per the mandate that governs Q4 resumption)

SESSION_ONLY_CRITICAL_KNOWLEDGE_MISSING_FROM_DISK = NO
MISSING_ITEMS            = none beyond what's already captured in this
                          document and in the companion handoff file cited in
                          §21 (both now on disk)

NEW_SESSION_FIRST_ACTION = Verify whether any TradingView MCP tool
                          (old or accelerator) is now present in the tool
                          list. If yes, proceed to §19 step 1. If no, do NOT
                          re-attempt in-conversation MCP reconnection (already
                          proven impossible, §13) — report the same blocker
                          this old session reported and wait for an external
                          restart.
```
