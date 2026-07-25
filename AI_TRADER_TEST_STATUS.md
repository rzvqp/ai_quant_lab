# AI Trader — Test Status

**Last updated**: 2026-07-25. Repo `ai_quant_lab-research-main`, branch `ai-trader-implementation`.

## 1. Three distinct kinds of "tested" — do not conflate

| Kind | What it proves | What it does NOT prove |
|---|---|---|
| **Automated unit/integration test** (pytest, fixture/fake-driven) | Code behaves correctly against controlled, synthetic inputs; type/invariant/fail-closed discipline holds | Nothing about a real broker, real market, or real network — fakes can't lie about real-world quirks (e.g. the comment-length bug was invisible to the fake gateway) |
| **Gated real-terminal integration test** (env-var gated, e.g. `MT5_REAL_TERMINAL_TEST`, `MT5_REAL_DEMO_ORDER_TEST`) | Code behaves correctly against the actual MT5 terminal API, for whatever scenario the terminal happens to be in at run time (market open/closed, AlgoTrading on/off) | Full coverage of every broker/terminal/market-state combination — only proves the specific run that happened |
| **DEMO real-money-shaped test** (an actual order placed on a DEMO account) | The complete real-world path works end-to-end for one specific order, once | Sustained/repeated/unattended operation, or any other symbol/direction/size than what was actually sent |

Only the BTCUSD test (§4) is the third kind. Everything else in this project to date is the first or
second kind.

## 2. Per-package automated test counts (re-collected this session, 2026-07-25)

| Package | Tests | mypy --strict |
|---|---|---|
| `risk_manager_live` | 37 | clean |
| `order_manager` | 43 | clean |
| `portfolio_manager_live` | 37 | clean |
| `telegram_notifier` | 34 | clean |
| `context_engine` | 19 | clean |
| `recognition_engine_live` | 23 | clean |
| `confidence_engine` | 23 | clean |
| `execution_orchestrator` | 18 | clean |
| `mt5_demo_execution` | 43 (42 + 1 gated, skipped by default) | clean |
| **Phase 2-10 subtotal** | **277** | **107 source files, 0 issues** |

## 3. Regression results

**Scoped regression, run this session (2026-07-25)** — every Phase 1-10 package plus direct dependencies
(`execution_engine`, `risk_manager`, `edge_intelligence`, `market_intelligence`, `context_memory`,
`scoring_engine`):
```
pytest ai_trader/risk_manager_live ai_trader/order_manager ai_trader/portfolio_manager_live \
  ai_trader/telegram_notifier ai_trader/context_engine ai_trader/recognition_engine_live \
  ai_trader/confidence_engine ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/execution_engine ai_trader/risk_manager ai_trader/edge_intelligence \
  ai_trader/market_intelligence ai_trader/context_memory ai_trader/scoring_engine -q
-> 1332 passed, 2 skipped, 0 failed, 14.31s
```
The 2 skips are the two gated real-terminal tests (Phase 1's `MT5_REAL_TERMINAL_TEST`, Phase 10's
`MT5_REAL_DEMO_ORDER_TEST`), by design — neither runs without its dedicated env var.

**Full-repository regression** (`pytest ai_trader -q`, every package including the batch/research side):
last run **2026-07-25 earlier this session**, before Phase 10's first DEMO attempt, per the CEO's own
"before first DEMO execution" requirement: **2714 passed, 2 skipped, 0 failed, ~4h14m22s**. **Not
re-run in full during this official-save task** — a full run takes ~4 hours and was judged out of scope
for a documentation/inventory task; the scoped regression above covers everything the live AI Trader
pipeline actually touches. Recommend a fresh full-suite run before authorizing anything beyond this save
(e.g. before any future Decision Logic / Risk / Demo Readiness audit that itself changes code).

## 4. Operational (real DEMO) tests

**Phase 10 gated real-terminal test, XAUUSD** (market closed at time of run):
```
MT5_REAL_DEMO_ORDER_TEST=1 pytest ai_trader/mt5_demo_execution/tests/test_mt5_demo_real_terminal_integration.py -v -s
-> 1 skipped: "PENDING_MARKET_OPEN: XAUUSD market is closed (or undeterminable) -- stopping before any transmission"
```
Connected to the real terminal, confirmed DEMO account + XAUUSD availability, detected the closed market,
stopped before any `order_check`/`order_send` call. No order sent. Correct, expected behavior.

**BTCUSD operational test, root-level script `btcusd_phase10_operational_test.py`** (not part of the
`ai_trader` package, mirrors the `mt5_connectivity_probe.py` precedent) — 5 attempts, full chronology:

| Attempt | Outcome | Root cause | Fix | Fix location |
|---|---|---|---|---|
| 1 | Stopped fail-closed at check #3 | AlgoTrading disabled at terminal | None — correct behavior, CEO confirmed | — |
| 2 | Dry-run rejected | Test script's own `strategy_id` ("PHASE10_BTCUSD_INFRA_TEST") failed `ORDER_SCHEMA.json`'s `^S\d+$` pattern | Changed to `"S999"` | Test script only, not `ai_trader` |
| 3 | `NOT_CONNECTED` | Dry-run adapter never `.connect()`-ed | Added the missing call | Test script only, not `ai_trader` |
| 4 | `order_check()` returned `None` | Real MT5 bug: `(-2, 'Invalid "comment" argument')` for comments ≥29 chars on this broker | Diagnosed via 2 read-only `order_check` sweeps (zero orders placed); `_COMMENT_MAX_LENGTH` 31→27 | `ai_trader/mt5_demo_execution/request_builder.py` (CEO-authorized) |
| 5 | **SUCCESS** | — | — | — |

Attempt 5 result: ticket `491745557`, 0.01 lots BTCUSD, filled 63984.0, `order_send` retcode `10009`,
position closed immediately (close price 63967.0, retcode `10009`), final state verified flat (0
positions, 0 orders). Journals: `btcusd_phase10_operational_test_journal.jsonl`,
`btcusd_phase10_dry_run_journal.jsonl`, `btcusd_phase10_demo_order_journal.jsonl` (all committed).

**Post-fix regression** (confirming the comment-length fix broke nothing pre-existing):
```
pytest ai_trader/mt5_demo_execution ai_trader/execution_orchestrator ai_trader/order_manager \
  ai_trader/execution_engine -q
-> 358 passed, 2 skipped, 0 failed
mypy --strict ai_trader/mt5_demo_execution -> clean
```

## 5. Problems found and their resolutions (consolidated)

| Problem | Where found | Resolution |
|---|---|---|
| `FrozenInstanceError` on direct mutation of a frozen `SizingLimits` | `risk_manager_live/tests/test_reused_controls.py` (Phase 2, pre-existing bug) | Fixed to use `dataclasses.replace()` |
| Recurring docstring-literal-substring false positives (~4-5×) | Various `test_import_independence.py` across Phases 2-10 | Reworded docstrings, never weakened the test |
| `OrderExecutionResult.dry_run` hardcoded `True`-only invariant | Phase 10 architecture investigation | CEO-authorized minimal type-widening fix (Order Manager + Execution Orchestrator) |
| `strategy_id` schema-pattern rejection | BTCUSD test attempt 2 | Test script fix (`"S999"`) |
| `NOT_CONNECTED` | BTCUSD test attempt 3 | Test script fix (missing `.connect()`) |
| MT5 comment-field length limit narrower than documented | BTCUSD test attempt 4 | `request_builder.py` constant 31→27, CEO-authorized, disclosed as broker-specific and non-universal |

## 6. Secrets/credentials sweep of the current working tree (2026-07-25)

Performed for this official save, per the CEO's explicit instruction. Checked: hardcoded API keys,
passwords, tokens (`git grep` for key/secret/password/token literal patterns), tracked `.env` files, MT5
login/password literals, Telegram token literals.

**Result: clean.** No hardcoded secrets found. `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID_PRIMARY`/
`_SECONDARY` appear only as environment-variable *names* (`telegram_notifier/credentials.py:10`) or as
placeholder test values (`"TOK"`, `"111"`, `"222"` in `test_credentials.py`). No `.env` file is tracked by
git. No MT5 login/password literal found anywhere in tracked `.py` files. A dedicated existing test,
`execution_engine/adapters/tests/test_credential_safety.py`, already guards this class of leak.
