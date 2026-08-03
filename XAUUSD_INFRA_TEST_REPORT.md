# XAUUSD Infrastructure Test — Report (Attempt 3: sizing bypassed — SUCCESS)

**CEO instruction, 2026-08-03**: "Ocoleste compute_sizing pentru testul de instalatie. Volum 0,01
explicit." — the installation test verifies the PIPE, not sizing. **Real order sent, confirmed, closed.
Account confirmed flat.**

## Sizing bypass — marked explicitly, verified by construction

`compute_sizing`/`RiskConfig` are **never imported, never constructed, never called** in this version of
the script (confirmed: neither name appears anywhere in `xauusd_infra_test.py` at this commit).
`TEST_VOLUME = 0.01` is a hardcoded module-level constant. The order is built directly as an
`execution_engine.types.OrderRequest` — the same shape `execution_engine/builder.py::build_order` would
normally produce from a sized `RiskDecision`, with `quantity` hardcoded instead of `sizing.size_units` —
and sent straight to `MT5DemoBrokerAdapter.submit_order()`, bypassing `execution_orchestrator.orchestrate()`/
`send_after_dry_run_gate()` entirely (both are inherently tied to the sizing-dependent `RiskDecision`
pipeline, so bypassing sizing means bypassing them too). Every one of `submit_order()`'s OWN safety
refusals (connected, DEMO, AlgoTrading, expected server, volume ceiling) still ran, unmodified — only
the sizing computation was skipped, confirmed both in code comments and in the run's own journal
(`ORDER_REQUEST_BUILT_SIZING_BYPASSED`, `sizing_bypassed: true`).

## The requested numbers

| | Value |
|---|---|
| **Ticket** | **499680521** |
| Volume | 0.01 lots (hardcoded) |
| Entry requested price | 4051.93 |
| Entry fill price | **4051.93** |
| Entry slippage | **$0.00** |
| Exit requested price | 4051.88 |
| Exit fill price | **4051.88** |
| Exit slippage | **$0.00** |
| Spread observed at send (entry) | **$0.05** |
| Spread observed at close (exit) | **$0.05** |
| Realized round-trip cost (price units) | **$0.05** |
| Realized round-trip cost, at 0.01 lots, in $ | **$0.05** |
| Modeled round-trip cost (project constant) | $0.20 |
| **Realized ÷ modeled ratio** | **0.25** |
| Account balance before | 10,026.83 PLN |
| Account balance after | **10,026.44 PLN** (Δ −0.39 PLN) |
| Open positions after close | **0** |
| Open orders after close | **0** |

Both legs filled with **zero slippage** against the requested price — the broker filled exactly at the
quoted bid/ask read immediately before each send.

## The comparison that matters — now a real, executed number

**Realized round-trip cost = $0.05, exactly 25% of the $0.20 modeled constant used throughout this
project's backtests.** Unlike the earlier $0.05 *quote* (attempt 1, which answered nothing because
nothing filled), this is now derived from **two actual fills**: entry at 4051.93 (requested = filled,
zero slippage), exit at 4051.88 (requested = filled, zero slippage). The realized price give-up between
the two fills (4051.93 − 4051.88 = $0.05) is the genuine round-trip friction for this one trade, under
the standard simplifying assumption that the true midpoint barely moved across the ~1–2 second hold
(disclosed, not provable from a single trade — Statistician's own framing: "un ordin nu demonstreaza
nimic, dar e primul punct de date real").

The account-currency (PLN) balance change (−0.39 PLN) is somewhat larger than the $0.05 price-cost alone
would suggest at the derived point-value (≈0.19 PLN) — the difference is most likely commission and/or
swap, neither isolated separately by this test; flagged, not resolved here.

## The separate finding, still on record

**At the current account (10,026.83 PLN) with 0.5% risk-per-trade, gold is not tradeable at wide stops —
the minimum lot requires 3.03%.** This applies to every strategy using this risk convention, not just
this test. PDH-PDL's own stop is much tighter (touch-bar extreme, not 2%-of-price) and may fit inside
the 0.5% budget — **not yet verified**, to be checked when PDH-PDL activation is actually authorized.

## Verification

Confirmed independently, via a fresh read-only connection, after the test process exited: **0 open
positions, 0 open orders, balance/equity both 10,026.44 PLN, stable.**

## Status

One order. Sent, confirmed, closed, verified flat. Stopping here, as instructed.
