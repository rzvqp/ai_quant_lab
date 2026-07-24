# MT5 Connectivity Probe — Report

**Scope executed**: exactly the CEO's own authorized list — terminal detection, connecting to the local
MetaTrader5 API, verifying connection status, reading terminal info, reading demo account info, reading
available symbols, reading one tick/market data point. **Nothing forbidden was called**: no
`order_send`/`order_check`/`order_calc_margin`/`order_calc_profit`, no `positions_get` (not on the
authorized list, so not read either), no terminal/settings modification of any kind. The probe script
(`mt5_connectivity_probe.py`) is committed alongside this report for full reproducibility/auditability —
it performs zero write operations, verified by direct inspection (only `initialize`/`terminal_info`/
`account_info`/`symbols_get`/`symbol_info_tick`/`symbol_info`/`shutdown` are called, all read-only per the
official `MetaTrader5` Python package's own API surface).

**One environment change made to run this probe**: the `MetaTrader5` PyPI package (v5.0.5735) was
installed into the project's own venv (`pip install MetaTrader5`) — not yet added to `requirements.txt`,
since that would be an implementation step, not part of a probe; left for the CEO's own decision when
Broker Adapter implementation is actually authorized.

## 1. Does the connection work?

**Yes — fully, on the first attempt, no errors.** `mt5.initialize()` succeeded; `terminal_info().connected
== True`; `account_info()` returned a live demo account snapshot; `symbols_get()` returned 251 symbols;
`symbol_info_tick("XAUUSD")` returned a real, current tick.

**Terminal**: FP Trading MT5 Terminal (build 5836), company "FP Trading LLC", path `C:\Program Files\FP
Trading MT5 Terminal`, connected to server.

**Account** (demo, confirmed — real login number deliberately redacted from this report/script output as
a precaution even though it's a demo account): name `DEMO_020`, server `FusionMarkets-Demo`, company
"Fusion Markets Pty Ltd", currency PLN, balance 5000.0, equity 5000.0, leverage 1:500, `trade_mode = 0`
(`ACCOUNT_TRADE_MODE_DEMO` — genuinely a demo account, not real money), `trade_allowed = True` at the
account level.

**Market data**: `XAUUSD` present among 251 available symbols; live tick retrieved — bid 4054.55 / ask
4054.62 (7-point spread), `digits=2`, `point=0.01`, `trade_contract_size=100.0`, `volume_min=0.01`,
`volume_step=0.01` — real, usable contract-specification data, not placeholder/stale values.

## 2. Technical limitations found

1. **`terminal_info().trade_allowed == False`** (distinct from `account_info().trade_allowed == True`) —
   this is the terminal's own "AlgoTrading" toggle (a manual UI switch in MT5, separate from the account's
   own trading permission). **Any future `order_send()` call would be rejected at the terminal level even
   once Broker Adapter implementation is authorized**, until this toggle is manually enabled in the
   terminal itself — a real, concrete, disclosed blocker for the eventual "MT5 Live Integration"
   step (step 3), not for this probe (which never attempted an order).
2. **`dlls_allowed == False`** — irrelevant to the standard Python `MetaTrader5` package (it doesn't
   require DLL imports to be enabled), but worth knowing if any future custom-indicator/DLL-based
   integration were ever considered — it is not, per this project's own scope.
3. **Python 3.14 (cp314) wheel** — the installed package is a genuine, current, compatible wheel for this
   project's own Python version; no compatibility issue found.
4. **No other blocker found** — no connection timeout, no permission error, no missing-symbol issue,
   no stale/zero market data.

## 3. Recommended architecture for MT5 integration

Confirms and refines `BROKER_ADAPTER_DESIGN.md`'s own `RealBrokerAdapterBase`/`BrokerConnectionLifecycle`
design against real, now-verified data shapes — no architectural change needed, mapping is direct:

- **`BrokerConnectionLifecycle.connect()`** → `mt5.initialize()` (optionally with explicit `path=`,
  `login=`, `password=`, `server=` kwargs for a future non-interactive/headless connection — this probe
  relied on the terminal already being open and authenticated, exactly as the CEO's own instruction
  specified; a real `MT5BrokerAdapter` should support both modes, since a live/production deployment may
  not always have a human pre-authenticating the terminal).
- **`BrokerConnectionLifecycle.is_connected()`** → `mt5.terminal_info().connected` (confirmed a real,
  live-queryable boolean field this session).
- **`BrokerConnectionLifecycle.disconnect()`** → `mt5.shutdown()`.
- **`BrokerAdapter.capabilities()`** → built from `mt5.symbol_info(symbol)` per traded symbol
  (`volume_min`/`volume_max`/`volume_step` → `BrokerCapabilities`'s own tick/lot/qty limit fields;
  `trade_mode`/`filling_mode`/`trade_calc_mode` → order-type/TIF support flags) — every field
  `BrokerCapabilities` already declares has a real, confirmed MT5 counterpart; no gap found.
- **`BrokerAdapter.query_status`/`query_open_orders`** (step 3, not this probe) would map onto MT5's own
  `positions_get()`/`orders_get()`/`history_deals_get()` — **not called this session** (outside the
  CEO's own authorized list), so this specific mapping is a design recommendation only, not yet verified
  against real data; flagged as the first thing to verify empirically (still read-only) when MT5 Live
  Integration (step 3) begins.
- **The `terminal_info().trade_allowed` toggle (finding 1 above) should be checked by
  `RealBrokerAdapterBase` at `connect()` time** and surfaced as a disclosed, non-fatal warning/capability
  flag — never silently ignored, since it will otherwise cause every future `submit_order` to fail with a
  confusing, terminal-level rejection rather than a clearly diagnosed one.
- **Credential handling** (per `BROKER_ADAPTER_DESIGN.md` §3): this probe relied on the terminal's own
  pre-existing authentication (no `login`/`password`/`server` args passed to `initialize()`) —
  confirming the "already-authenticated terminal" mode works exactly as expected. The
  constructor-injected-credentials mode for a non-interactive scenario remains unverified (not attempted
  this session, no credentials were available or appropriate to test with) — disclosed as still open for
  step 3, not resolved here.

**No change recommended to `BROKER_ADAPTER_DESIGN.md`'s own architecture** — this probe served as
empirical confirmation, not a redesign trigger.

---

**Per the CEO's own explicit instruction: not continuing Broker Adapter implementation.** Awaiting CEO
review of these findings before any further step.
