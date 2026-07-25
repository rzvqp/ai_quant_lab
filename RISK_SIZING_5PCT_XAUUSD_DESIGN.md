# Equity-Based Dynamic Position Sizing (5% risk/trade, XAUUSD DEMO) — Design

**Status: DESIGN ONLY — no code written. Awaiting CEO approval before any implementation.**

**CEO scope (2026-07-25)**: each trade must risk exactly 5% of the DEMO account's current equity.
Volume must be computed automatically from stop-loss distance and the instrument's monetary value — not
a fixed lot size. Applies to XAUUSD, DEMO account, once the market reopens Monday. Phase 10 stays closed;
this is parallel design work, not a new phase — no code changes until explicitly approved.

---

## 0. Headline finding: the sizing formula already exists and is already reused live — this is a gap-fill, not a new engine

`ai_trader/risk_manager/sizing.py::compute_sizing` already computes
`risk_budget_currency = risk_per_trade_pct * portfolio.equity`, then
`size_units = risk_budget_currency / (stop_distance * point_value)`, and
`ai_trader/risk_manager_live/engine.py::evaluate_trade_proposal` already calls it live (step 6), then
converts to broker lots via `InstrumentSpecification.contract_size`/`lot_step` (step 7) and checks free
margin (step 8). **`LiveRiskDecision.calculated_volume` is already an auto-computed lot size, not a fixed
value, and no code anywhere downstream (`order_manager`, `execution_engine`, `mt5_demo_execution`) ever
overrides it** — `ApprovedTradeIntent.volume`'s own docstring already states it "arrives pre-sized and
pre-rounded by risk_manager_live." This design changes none of that arithmetic. It closes four gaps that
currently stop the existing formula from running correctly, unattended, against the live DEMO account:

| # | Gap | Current state | Needed for this feature |
|---|---|---|---|
| G1 | Risk-per-trade percentage | `RiskConfig.sizing.risk_per_trade_pct` defaults to `0.005` (0.5%) | `0.05` (5%) for the XAUUSD DEMO profile — **pure config, zero code** |
| G2 | Instrument monetary value | `RiskConfig.sizing.point_value` is a manually-maintained `dict[str, float]`, default `1.0` if the symbol is absent — never derived from real MT5 contract data | Computed automatically from live MT5 `symbol_info()` |
| G3 | Live account equity | `AccountState`/`PortfolioState.equity` are constructed only in test fixtures; nothing today reads MT5 `account_info()` into either | A live projection function, called before every sizing decision |
| G4 | Safety ceiling | `MT5DemoConfig.max_order_volume` defaults to `0.01` lots — a **hard, static** ceiling sized for minimal-volume infra testing (Phase 10), not for real 5%-risk position sizes | Needs an explicit CEO decision (§6) — a correctly-computed larger volume would currently be REJECTED at the adapter, not sent |

---

## 1. G1 — risk-per-trade percentage: no new code

Set `RiskConfig.sizing.risk_per_trade_pct = 0.05` in whatever `RiskConfig` instance the XAUUSD DEMO
caller constructs (e.g. a new `xauusd_demo_risk_config()` factory function, or a config file/constant —
naming TBD, CEO's call). Everything downstream (`compute_sizing`'s own `min`-clamp against
`remaining_exposure_pct`/`remaining_group_budget_pct`, `max_position_notional_pct`,
`min_allocation_risk_pct`) is reused completely unmodified. **Open item**: confirm 5% risk/trade doesn't
make other portfolio-level caps in the same `RiskConfig` (e.g. `max_position_notional_pct=0.20` by
default) too tight or effectively redundant for a single-symbol XAUUSD DEMO profile — this is a config
values question for the CEO, not an engineering one (§6).

## 2. G2 — instrument monetary value, derived automatically instead of manually configured

**Proposed new, additive types** (package: extend `ai_trader/mt5_demo_execution/`, since it already owns
the live MT5 read path — no change to the frozen `execution_engine/adapters/mt5_adapter.py`):

```
MT5InstrumentValue (frozen, slots) — new type, mt5_demo_execution/types.py
    symbol: str
    tick_size: float          # MT5 symbol_info().trade_tick_size
    tick_value: float         # MT5 symbol_info().trade_tick_value (account-currency value of one tick)
    contract_size: float      # MT5 symbol_info().trade_contract_size
    as_of: int
```

**Proposed new, additive function** (`mt5_demo_execution/instrument_value.py` or similar):

```
read_instrument_value(gateway: MT5DemoGateway, symbol: str) -> MT5InstrumentValue
    # reads mt5.symbol_info(symbol) directly, extracts trade_tick_size/trade_tick_value/trade_contract_size
    # (fields the repo's existing MT5SymbolCapabilities/symbol_capabilities() does NOT currently extract)

instrument_specification_from_mt5(value: MT5InstrumentValue, existing: MT5SymbolCapabilities) -> InstrumentSpecification
    # point_value = value.tick_value / value.tick_size   -- monetary value of a 1.0 price-unit move
    # everything else (tick_size, lot_step, min/max_volume, contract_size) copied from the
    # ALREADY-READ MT5SymbolCapabilities (symbol_capabilities(), unmodified) -- no duplicate read
```

This makes `RiskConfig.sizing.point_value` (the manual dict) unnecessary for XAUUSD going forward — the
live-derived value replaces the lookup for this symbol. The manual dict itself is not removed (other,
non-live/backtest callers still use it; removing a still-used mechanism is out of scope and not a "real
bug" per the standing fix-only-what's-demonstrated rule).

**Verification requirement before trusting the formula** (mirrors the Phase 10 comment-length precedent):
`point_value = tick_value / tick_size` must be empirically confirmed against XAUUSD on the actual tested
terminal/broker via a **read-only** `symbol_info()` call before the first real sizing decision uses it —
no order-placing call is needed to verify this, exactly like the BTCUSD comment-length sweep needed none.

## 3. G3 — live equity: one function, one call site, feeds both equity fields consistently

Today `evaluate_trade_proposal` reads `portfolio.equity` (`PortfolioState`, used for sizing) and
`account.margin_free` (`AccountState`, used for the margin check) — **two different objects that must
agree on the same equity figure for a single decision to be internally consistent**, and neither is
currently ever populated live.

**Proposed new, additive function** (`mt5_demo_execution/account_state.py` or similar):

```
account_state_from_mt5(gateway: MT5DemoGateway, as_of: int) -> tuple[AccountState, float]
    # single mt5.account_info() read; returns AccountState (currency/balance/equity/margin_used/
    # margin_free/margin_level/leverage/is_demo) AND the raw equity float, so the caller can build
    # PortfolioState.equity from the exact same read -- one MT5 call, one timestamp, no drift between
    # the two equity figures a single sizing decision depends on.
```

The caller (the eventual live-trading orchestration script/loop — not yet built, out of this design's
scope) is responsible for constructing `PortfolioState` (open positions, daily P&L, consecutive losses,
etc.) around that same equity figure; this function only owns the "read equity from MT5, once" concern.

**Open item**: MT5 `account_info()` exposes both `balance` (excludes floating P&L of open positions) and
`equity` (includes it). Standard risk-management practice sizes new trades against **equity** (the
CEO's own wording, "equity-ul curent," already says this) — proposing to use the raw MT5 `equity` field
for both `AccountState.equity` and `PortfolioState.equity`. Flagging for explicit confirmation since it
directly sets the risked dollar amount on every trade (§6).

## 4. G4 — the safety ceiling conflict (the one item that blocks this feature from ever sending, unresolved)

`MT5DemoBrokerAdapter.submit_order` rejects any `order.quantity > self._config.max_order_volume`
(`0.01` lots by default) — a **hard safety control**, deliberately kept from Phase 10's "minimal
configurable volume" testing instruction, and per the standing rule ("Nu elimina niciun control de
risc") it must not simply be deleted or silently raised. A correctly-computed 5%-risk XAUUSD position
size will, in essentially all realistic stop-loss distances, exceed `0.01` lots — so without an explicit
decision here, every dynamically-sized order this feature produces would be rejected at the adapter, not
sent. This is not an engineering gap; it is a decision the design cannot resolve on its own (§6).

## 5. What this design deliberately does NOT change

- `risk_manager/sizing.py::compute_sizing` — reused byte-identical, zero modification.
- `risk_manager_live/engine.py::evaluate_trade_proposal` — reused byte-identical; it already consumes
  `AccountState`/`InstrumentSpecification`/`PortfolioState` as parameters, so live-populated instances
  slot in with no signature change.
- `order_manager`, `execution_engine`, `portfolio_manager_live`, `execution_orchestrator`,
  `confidence_engine`, `recognition_engine_live` — no change; `ApprovedTradeIntent.volume` keeps arriving
  pre-sized exactly as today.
- The frozen `RiskConfig.sizing.point_value` manual dict — kept, not removed; the live-derived value only
  supersedes it for XAUUSD's live sizing call site.
- No new order-submission logic, no new broker call beyond two additional **read-only** MT5 calls
  (`symbol_info()` field extraction, `account_info()` field extraction) — neither calls `order_check`/
  `order_send`.

## 6. Open questions — explicit CEO decision required before any code is written

1. **Safety ceiling (§4)**: how should `MT5DemoConfig.max_order_volume` be handled once dynamic sizing is
   live? Options to choose from (or propose another): (a) raise it to a new, still-hard, CEO-specified
   lot ceiling sized for legitimate XAUUSD DEMO positions; (b) keep `0.01` as an absolute ceiling and
   have the sizing/order-manager layer clamp-and-warn rather than compute past it (defeats the "risk
   exactly 5%" intent — a clamped trade risks less than 5%); (c) something else. **No implementation can
   proceed until this is decided — this is the actual blocker, not an engineering unknown.**
2. **Equity field**: confirm MT5's `equity` (includes floating P&L), not `balance`, is the correct 5%
   base (§3).
3. **Point-value formula**: confirm `tick_value / tick_size` is the intended "instrument value" for the
   arithmetic (§2), and confirm it should be empirically verified via a read-only `symbol_info()` check
   against the real XAUUSD terminal before being trusted (same discipline as the Phase 10 comment-length
   fix).
4. **Portfolio-level caps**: confirm existing `RiskConfig` portfolio-level percentage caps
   (`max_position_notional_pct`, exposure/group-budget caps in `risk_manager`'s frozen guards) don't need
   re-tuning for a 5%-risk-per-trade regime, or whether the CEO wants those revisited alongside this
   change.
5. Naming/location for the new `RiskConfig` factory (or equivalent config source) that sets
   `risk_per_trade_pct=0.05` for the XAUUSD DEMO profile specifically, without changing the frozen
   default (0.5%) for any other caller.

## 7. Proposed validation plan (once approved)

- Unit tests for `read_instrument_value`/`instrument_specification_from_mt5`/`account_state_from_mt5`
  against a fake gateway (mirroring `FakeMT5DemoGateway`'s existing pattern) — pure projection logic, no
  network/terminal dependency.
- A read-only integration test (gated behind its own new env var, mirroring
  `MT5_REAL_DEMO_ORDER_TEST`/`MT5_REAL_TERMINAL_TEST`) that reads live XAUUSD `symbol_info()`/
  `account_info()` and asserts the derived `point_value`/`equity` are positive and structurally sane —
  no order-related call, exactly like the Phase 10 comment-length sweep.
- A full regression of `risk_manager`, `risk_manager_live`, `mt5_demo_execution` after wiring, confirming
  zero change to any existing test (all current tests use fixture-supplied `AccountState`/
  `InstrumentSpecification`/`point_value`, so behavior for every existing caller stays byte-identical).
- Only after all of the above passes and the CEO separately authorizes it: a single, minimal-volume,
  read-only-first (`order_check` only) dry run confirming a 5%-risk-computed `ApprovedTradeIntent` flows
  correctly through the existing dry-run leg — no real order — before ever considering a real send at a
  properly-sized volume.

## 8. Summary

This is a **gap-fill design**, not a new engine: the risk-sizing math (`compute_sizing`) and its live
caller (`evaluate_trade_proposal`) already do exactly what was asked — compute volume from stop distance
and instrument value, not a fixed lot. What's missing is (a) the 5% config value itself (trivial), (b) a
live, automatic source for "instrument value" in place of the manual dict, and (c) a live source for
account equity in place of test fixtures — plus (d) an unavoidable decision about the current 0.01-lot
safety ceiling, which as configured today would silently defeat the feature by rejecting every correctly
-sized order. No code changes are proposed to be made until the open questions in §6 are answered.
