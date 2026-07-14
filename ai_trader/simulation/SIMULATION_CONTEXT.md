# Simulation Context v1 — the run spec + runtime context (design)

Two things: (A) the **`SimulationContext`** — the immutable specification of ONE simulation run (everything needed
to reproduce it bit-for-bit), and (B) the **runtime context** threaded through the per-bar loop. Design only — no
code. The machine shape of the run spec + report is in `SIMULATION_SCHEMA.json`.

---

## A. `SimulationContext` (immutable run spec)
A run is fully determined by this object + the historical data + the composed module versions. Nothing outside it
may influence results (the determinism law).

### A.1 Time & data
| field | meaning |
|---|---|
| `run_id` | unique id for the run |
| `date_range` | `{ start, end }` (UTC) — the replay window |
| `symbols[]` | the instruments to replay (multi-symbol) |
| `timeframes[]` | base + context timeframes (e.g. `["M15","H1","H4","D1"]`); base = the heartbeat |
| `data_source` | the replay data-source id (`replay` / `lab-parity`), read-only historical bars |
| `warmup_bars` | leading bars replayed to satisfy scanner/feature warmup (excluded from stats) |

### A.2 Capital & account
| field | meaning |
|---|---|
| `starting_balance` | initial account balance (base currency) |
| `base_currency` | account currency |
| `leverage_max` | account max leverage (margin sim) |
| `margin_model` | `{ initial_margin_pct, maintenance_margin_pct }` |

### A.3 Cost & fill models (deterministic)
| field | meaning |
|---|---|
| `cost_model` | `{ spread_model, commission_model }` — spread (fixed ticks or per-symbol schedule) + commission (per-lot / per-notional) |
| `fill_model` | `{ entry_timing: "next_open", intrabar: "stop_before_target", partial_fill_policy, limit_touch_rule, slippage_model }` |
| `slippage_model` | `{ type: "fixed"|"atr_fraction"|"seeded_random", params, seed_key }` — if random, seeded deterministically (A.5) |
| `cost_model_version`, `fill_model_version` | pin the models so the report is reproducible |

### A.4 Strategy set & risk
| field | meaning |
|---|---|
| `strategy_set` | which Strategy Library strategies are ACTIVE for this run (ids or "all activatable") |
| `risk_config` | the Risk Manager `RiskConfig` (limits + sizing params) for this run — versioned |
| `capital_allocation` | initial per-strategy / per-group allocation policy (advisory; Risk Manager enforces) |

### A.5 Determinism controls
| field | meaning |
|---|---|
| `run_seed` | the master seed; all stochastic draws derive from `hash(run_seed, stable_key)` (e.g. order id + as_of) |
| `deterministic` | `true` (v1 always) — asserts no wall-clock / unseeded RNG anywhere |
| `module_versions` | the composed pipeline versions (scanner/manager/signal/scoring/risk/execution + all schema versions) recorded at run start |

### A.6 Output controls
| field | meaning |
|---|---|
| `record` | what to persist: `{ trade_history, execution_log, equity_curve, risk_events, per_bar_snapshots? }` |
| `stats_rollups` | which roll-ups to compute: `session`, `daily`, `monthly` |
| `close_at_end_policy` | `close_at_last` \| `hold_and_mark` for positions open at `date_range.end` |

**Immutability:** the `SimulationContext` is frozen at run start; a change to ANY field is a NEW run (new `run_id`).
Two runs with the same `SimulationContext` + data + module versions MUST produce identical results.

---

## B. Runtime context (threaded through the per-bar loop)
Derived from the `SimulationContext`; carries the moving state the harness threads through the pipeline each bar.
It is NOT tunable mid-run (determinism).

| field | meaning |
|---|---|
| `as_of` | the current replay bar's close timestamp (UTC epoch seconds) — the single clock |
| `bar_index` | monotonic base-bar counter since run start |
| `phase` | `WARMUP` \| `RUNNING` (WARMUP bars excluded from stats) |
| `mode` | `SIMULATION` (always here; `LIVE` is the future counterpart with the same shape) |
| `portfolio_state` | the current `PortfolioState` from the Portfolio Simulator (the same shape the Risk Manager reads live) |
| `risk_context` | the market-risk snapshot for `as_of` (volatility/spread/liquidity/session/calendar), assembled from the MarketContext (not fetched) |
| `run_seed`, `seed_for(key)` | deterministic sub-seed derivation for any stochastic model |

## C. Relationship to live
- `mode=SIMULATION` vs `mode=LIVE` is the ONLY conceptual difference; the runtime-context SHAPE is identical, so
  the pipeline modules cannot tell simulation from live. Going live swaps the Execution Simulator for a Broker
  Adapter and the Portfolio Simulator's virtual account for a real account — the `PortfolioState`/`RiskContext`/
  `MarketContext` shapes are unchanged.
- Because everything that can affect a result is inside the `SimulationContext` (including `run_seed` and the
  model versions), a run is a reproducible, self-describing artifact — the basis for running thousands of
  comparable simulations.
