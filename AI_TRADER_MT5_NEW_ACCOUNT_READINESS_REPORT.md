# AI_TRADER_MT5_NEW_ACCOUNT_READINESS_REPORT

**Mandate**: `AI-TRADER-MT5-NEW-ACCOUNT-READINESS-001`
**Scope**: detect and mechanically verify the newly-logged-in MT5 account, bind the AI Trader DEMO
runtime to it, and confirm operational readiness -- read-only / dry-run only. `BROKER_ORDER_SUBMISSION`
stayed `DISABLED` throughout; no `order_send`/`order_check`/`order_calc_margin` call was made anywhere
in this mandate's work (confirmed by this package's own pre-existing AST guards, re-run clean).

## What was found

The previously-observed blocker (`mt5.initialize()` -> `(-6) Terminal: Authorization failed`) is
resolved -- the account switch itself was what fixed it, not any code change. The new account is on a
**different broker/server** than every prior mandate in this project (`FPTradingLLC-Demo`, not
`FusionMarkets-Demo`) -- this exposed one real, genuine defect: `run_live_demo.py` and `soak/run_soak_
live.py` both hardcoded `MT5DemoConfig(expected_server="FusionMarkets-Demo")`. Left as-is, that stale
pin would have caused `MT5DemoBrokerAdapter.submit_order`'s own defense-in-depth server check to refuse
every future order with `UNEXPECTED_SERVER`, even though the new account is genuinely, mechanically
DEMO. Fixed in both entrypoints: a bare, unpinned probe now discovers whatever account is CURRENTLY
logged in and pins `expected_server` to that observed value for the rest of the process's own lifetime --
still a real safety net against a mid-session switch, just never stale from a prior mandate's account.
New, dedicated module `account_identity.py` (7 new tests) makes this binding explicit and persisted
(`new_brain_live_state/s5_mt5_account_readiness/account_identity.json`, gitignored, raw login number
never committed or printed in full anywhere -- always masked as `***NN`).

## Required report

```
CURRENT_ACCOUNT:
  login: ***04 (masked)
  server: FPTradingLLC-Demo
  trade_mode: 0 (DEMO)
  currency: EUR
  balance: 3000.0
  equity: 3000.0

MT5_INITIALIZE:            PASS
MT5_TERMINAL_INFO:         PASS  (connected=true, algo_trading_allowed=true, build 6140)
MT5_ACCOUNT_INFO:          PASS  (trade_allowed=true, trade_expert=true)

DEMO_GATE:                 PASS  (trade_mode read directly from account_info(), == AccountTradeMode.DEMO;
                                   never inferred from server name, account name, balance, or prior config)

XAUUSD_SYMBOL:              XAUUSD  (literal name resolves directly on this broker -- no suffix/prefix
                                      remapping needed; mechanically confirmed via symbols_get() scan for
                                      every XAU-containing name: XAUAUD/XAUUSD/XAUEUR/XAUGBP/XAUSGD/XAUCNH
                                      all exist, XAUUSD is the correct USD-quoted one, already
                                      visible=true/select=true)

SYMBOL_SPEC:
  tick_size:      0.01
  tick_value:     (not read from the static symbol_info field, which reports 0.0/stale before a
                   symbol is actively selected -- risk_sizer.py already uses the broker's own
                   order_calc_profit exclusively, confirmed correct on this exact account below)
  contract_size:  100.0
  volume_min:     0.01
  volume_max:     20.0   (differs from the previous broker's 100.0 -- broker-specific, read fresh,
                          never assumed)
  volume_step:    0.01

RISK_ENGINE_5_PERCENT:     PASS
  -- dry run, synthetic S5-shaped LONG (entry=2450.00, SL=2440.00, 10.00 canonical-style distance):
     risk_budget = equity(3000.0) * 0.05 = 150.00 EUR
     loss_per_1_lot (real order_calc_profit on THIS account/symbol) = 856.93 EUR
     raw_volume = 0.175... -> rounded DOWN to 0.17 lots (volume_step=0.01)
     modeled_risk = 145.68 EUR = 4.856% -- correctly <= 5%, never rounded up through the budget
  -- fail-closed re-confirmed on this real account: an artificially huge SL distance (chosen so even the
     0.01-lot minimum would exceed the 5% budget) correctly returns approved=False /
     MIN_VOLUME_EXCEEDS_RISK_BUDGET; an SL on the wrong side of entry for a LONG correctly returns
     approved=False / INVALID_SL_DISTANCE. Neither test touched the broker beyond the same read-only
     order_calc_profit call the approved case used.

OLD_ACCOUNT_STATE_REMOVED: PASS
  -- no previous account identity had ever been persisted by this exact mechanism (new this mandate);
     the ONE real place old-account state actually lived in code (the hardcoded expected_server literal)
     is fixed, see "What was found" above. Both execution ledgers
     (s5_mt5_demo/, s5_mt5_demo_soak/) were mechanically checked for leftover non-terminal (in-doubt)
     identities from the prior account/broker -- zero found (neither prior mandate's live/soak runs ever
     reached a successful order_send, so there was nothing to carry over).

RESTART_PERSISTENCE:       PASS
  -- proven twice: (1) within the readiness-check process itself (persist -> reload -> compare against a
     fresh live re-read); (2) genuinely across process boundaries -- the entire readiness check was run a
     SECOND time as a fully independent process invocation and produced an identical, consistent result,
     with OLD_ACCOUNT_STATE_REMOVED correctly reporting "same account already bound" on the second run
     rather than re-treating it as a new identity.

MARKET_STATUS:              CLOSED
  -- correctly determined from live tick staleness (age > 120s), never treated as a failure condition;
     every readiness check above ran successfully without needing a fresh quote or any order.

BROKER_ORDER_SUBMISSION:    DISABLED
```

## Final status

**`AI_TRADER_NEW_MT5_DEMO_ACCOUNT_READY`**

`ACCOUNT_READY` is what this report proves; `MARKET_OPEN_EXECUTION_READY` is a separate, not-yet-true
condition (market is closed) that this mandate never claims. No order was placed. S5's strategy/EV/risk
logic was not touched (only the account-binding/config layer was fixed, per section 3's own explicit
instruction). `BROKER_ORDER_SUBMISSION` remains `DISABLED`.

## Regression / static checks

`pytest ai_trader/new_brain_live/strategy_platform/` -> **271 passed** (264 pre-existing unchanged + 7
new in `account_identity.py`'s own test file). `pytest ai_trader/mt5_demo_execution/ ai_trader/
execution_engine/adapters/` -> **103 passed, 2 skipped** (unchanged). `mypy --strict ai_trader/new_brain_
live/strategy_platform/` -> **Success: no issues found in 70 source files**.

Per the CEO's directive: report and stop. No order placed.
