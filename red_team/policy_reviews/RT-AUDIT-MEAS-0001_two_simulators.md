# RED TEAM — MEASUREMENT AUDIT · the two economic-verdict simulators (trade-by-trade)
### RT-AUDIT-MEAS-0001 · `edge_research/_screen.py` (Alpha) vs `code/mstrat.py` (historical) — do they agree, trade-by-trade?
**Date:** 2026-08-13 · **Auditor:** Red Team · **Mandate:** CEO — audit the INSTRUMENTS. Two prior measurement errors (D1 loss-as-win; TICK 2× cost) both moved the leaderboard. Per the mandatory addendum: **trade-by-trade** comparison with the full field set, a synthetic fixture with known outcomes covering all seven cases, an explicit convention matrix, and a `CANONICAL_TRADE_SIMULATION_CONTRACT`. **No engine modified; no repair; verified by running both `simulate` loops (replicated verbatim from source) on one fixture.**

## VERDICT — **FAIL. The two simulators diverge on the VERY FIRST trade, and on five conventions.**
Trade-by-trade, they disagree on **every** trade (cost), catastrophically on small stops (floor, 50×), and on window-boundary hits (a target becomes a time-exit). They agree only on same-bar precedence, time-exit price (when both scan the bar), timezone anchor, entry, and long/short symmetry. **Per the CEO's directive: until this audit closes and a single canonical semantics is adopted and both engines re-run against it, NO leaderboard and NO economic elimination may be treated as definitive.**

---

## 1. TRADE-BY-TRADE (synthetic fixture, known outcomes) — full fields
Identical bars, identical trades, both engines (`R` in risk units; cost = `2·(spread+slip)·tick = 0.40` round-trip):

| # | case | engine | eff. stop | exit@ | exit_px | reason | gross_R | cost_R | **net_R** |
|---|---|---|---|---|---|---|---|---|---|
| T1 | target-only L | screen | 98.0 | 4 | 102.0 | target | +1.00 | 0.00 | **+1.00** |
|    |               | mstrat | 98.0 | 4 | 102.0 | target | +1.00 | −0.20 | **+0.80** |
| T2 | stop-only L | screen | 98.0 | 12 | 98.0 | stop | −1.00 | 0.00 | **−1.00** |
|    |             | mstrat | 98.0 | 12 | 98.0 | stop | −1.00 | −0.20 | **−1.20** |
| T3 | same-bar SL+TP L | screen | 98.0 | 20 | 98.0 | **stop_wc** | −1.00 | 0.00 | **−1.00** |
|    |                  | mstrat | 98.0 | 20 | 98.0 | **stop** | −1.00 | −0.20 | **−1.20** |
| T4 | time-exit L | screen | 95.0 | 32 | 100.0 | time | +0.00 | 0.00 | **0.00** |
|    |             | mstrat | 95.0 | 32 | 100.0 | time | +0.00 | −0.08 | **−0.08** |
| **T5** | **small-stop (floor) L** | screen | **99.9** | 36 | 100.5 | target | **+5.00** | 0.00 | **+5.00** |
|    |                          | mstrat | **99.0 (floored)** | 36 | 100.5 | target | **+0.50** | −0.40 | **+0.10** |
| T6 | target-only S | screen | 102.0 | 44 | 98.0 | target | +1.00 | 0.00 | **+1.00** |
|    |               | mstrat | 102.0 | 44 | 98.0 | target | +1.00 | −0.20 | **+0.80** |
| T7 | stop-only S | screen | 102.0 | 52 | 102.0 | stop | −1.00 | 0.00 | **−1.00** |
|    |             | mstrat | 102.0 | 52 | 102.0 | stop | −1.00 | −0.20 | **−1.20** |
| **B** | **target hit on last window bar** | screen | 98.0 | 7 | **102.0 / target** | — | — | **+1.00** |
|    |                                   | mstrat | 98.0 | 7 | **100.0 / time** | — | — | **−0.20** |

**FIRST DIVERGENCE = T1 (the first trade):** cost. `screen` reads GROSS (+1.00), `mstrat` NET (+0.80). **Every** trade diverges on cost. **T5** additionally diverges 50× (floor widens the stop 99.9→99.0). **B** diverges on **reason AND R** (a win becomes a time-exit) from the window off-by-one.

## 2. CONVENTION MATRIX (explicit, all requested aspects)
| aspect | `_screen.py` | `mstrat.py` | `demo_gate` | agree? |
|---|---|---|---|---|
| **tick_size** | not used (no floor/cost) | **0.1** (10× wrong, RT-CODE-A-0007) | parameter | **DIVERGE** |
| point_size | not modeled (R-based) | not modeled | n/a | agree (both omit) |
| contract_size | not modeled | not modeled | n/a | agree (both omit) |
| **spread** | **none (GROSS)** | `spread_ticks·tick` | observed | **DIVERGE** |
| commission | not a line item | lumped in "cost" | n/a | agree (both omit as line) |
| **slippage** | **none** | `slip_ticks·tick` (in cost) | fill-based | **DIVERGE** |
| rounding | no tick rounding | no tick rounding | no | agree (both raw float) |
| **risk floor** | **NONE** | `max(2·spread·tick, 5·tick, 0.10·ATR)` | same floor | **DIVERGE** |
| same-bar SL/TP precedence | **stop-first WC** | **stop-first WC** | stop-first | **AGREE** |
| entry | next-open `o[si+1]` | next-open `o[ei]` | next-open | AGREE |
| long/short | symmetric | symmetric | symmetric | AGREE |
| timezone / day anchor | 17:00-NY | 17:00-NY (resample_ny) | day_index | AGREE (anchor) |
| **window horizon** | `[ei, ei+tsb]` **inclusive** | `[ei, ei+to)` **exclusive** | day boundary | **DIVERGE (off-by-one)** |
| **block segmentation** | **>72h time-gap** | **manifest discovery segments** | day_index | **DIVERGE (populations)** |

## 3. DEFECTS (per the required format)

### DEFECT M-1 — GROSS vs NET cost (every trade)
- **COMPONENT:** `_screen.simulate` (gross, no cost) vs `mstrat.simulate` (`R=(dir·(ex−entry)−2·cost)/risk`).
- **CAUSE:** two different economic definitions of R — Alpha's screen is deliberately gross ("costs measured downstream"); mstrat nets round-trip cost. Never reconciled; `demo_gate` is a third (parametric).
- **HISTORICAL RESULTS AFFECTED:** every `_screen` metric (Alpha's screen verdicts) is **higher than the same strategy's net R** by `2·cost/risk`; every `mstrat` metric is net. The two are not the same number for any trade.
- **VERDICTS SUSPECT:** any comparison of an Alpha screen verdict to an `mstrat` leaderboard row.
- **RERUN:** re-express both on ONE cost convention (canonical §4) before comparing.

### DEFECT M-2 — Risk floor present in one engine, absent in the other (small stops)
- **COMPONENT:** `mstrat.simulate` floors risk to `max(2·spread·tick, 5·tick, 0.10·ATR)`; `_screen.simulate` has **no floor** (`risk=abs(entry−stop)`).
- **CAUSE:** divergent handling of tiny stops — `mstrat` widens the stop (deflating R), `_screen` keeps raw R and relies on a **fat-tail screen**. Compounded by the **TICK error**: at ATR<5 the binder is `5·tick=0.5` (should be `0.05`, 10× too wide).
- **HISTORICAL RESULTS AFFECTED:** every small-stop / low-ATR strategy on `mstrat` — R crushed (T5: +5.00 → +0.10, 50×). Exactly the eliminated families (level-fade, void, BPR, CAND-0009 are small-stop).
- **VERDICTS SUSPECT:** `mstrat`'s small-stop/low-ATR leaderboard rankings and eliminations. The CEO's own evidence: TICK fix **flipped 529 hypotheses negative→positive** and moved **S3 −0.39 → +0.23** — the floor compounds this at low ATR.
- **RERUN:** `mstrat` full campaign with tick 0.01 (floor `5·0.01=0.05`) and the reconciled floor semantics.

### DEFECT M-3 — Window off-by-one (boundary-bar hits)
- **COMPONENT:** `_screen` scans `[ei, ei+tsb]` **inclusive** (tsb+1 bars); `mstrat` scans `[ei, ei+to)` **exclusive** (to bars).
- **CAUSE:** inconsistent horizon-window convention. A stop/target touched **only** on bar `ei+horizon` is seen by `_screen`, missed by `mstrat`.
- **HISTORICAL RESULTS AFFECTED:** any trade whose exit lands on the last horizon bar — `_screen` books a target/stop, `mstrat` books a time-exit (fixture B: **+1.00 target vs −0.20 time**). Different `n`-of-wins, different R, different exit-mix — silently.
- **VERDICTS SUSPECT:** exit-reason distributions and win-rates across the two; any strategy with short horizons (more boundary hits).
- **RERUN:** fix the window to one convention and re-run both.

### DEFECT M-4 — Divergent block population
- **COMPONENT:** `_screen.derive_blocks` (>72h gaps) vs `mstrat` (manifest discovery segments).
- **CAUSE:** different segmentation → different first-bar-UNCLASSIFIED (D3_bis) exclusions → different trade sets. `_screen`'s own docstring concedes the formal run uses manifest segments.
- **HISTORICAL RESULTS AFFECTED:** `n`, and which signals survive, differ between the two even with identical execution — the numbers are not the same population.
- **VERDICTS SUSPECT:** any cross-engine `n`/aggregate comparison.
- **RERUN:** run both on the manifest segments for any comparison.

### DEFECT M-5 — TICK=0.1 contamination across the `mstrat` ecosystem (already reported, blast radius here)
- **COMPONENT:** `mstrat.py`, `s1.py`, `mtf.py`, `synth_price.py`, `trading_strategies.py`, `task2_cost_rerun.py`, `lm001_*`, `alpha_lab.CFG.tick` — all 0.1. `_screen.py` uses **no tick** → TICK-independent.
- **CAUSE:** the 10× tick error (RT-CODE-A-0007) lives in the entire historical ecosystem; the screener does not.
- **HISTORICAL RESULTS AFFECTED:** every `mstrat`-based leaderboard number (1,972 hypotheses) carries a 2× cost + the wrong floor; Alpha's `_screen` verdicts are clean of it.
- **VERDICTS SUSPECT:** the entire `mstrat` leaderboard for cost/floor-sensitive strategies.
- **RERUN:** corrected-tick re-run of the whole `mstrat` campaign.

## 4. WHAT IS AGREED (verified)
Same-bar SL/TP precedence (**both stop-first worst-case**, T3); time-exit price when both scan the bar (T4); next-open entry; long/short symmetry (T1/T6, T2/T7); the 17:00-NY day anchor; and that neither models point/contract size or tick-rounding (both R-based on raw prices). **No D1-style optimism in either screener** (the demo engine's D1 was a third engine, fixed).

## 5. WHAT IS INVALIDATED / WHAT HOLDS (direct)
- **Logically robust:** Alpha's `_screen` **gross-negative eliminations** (gross-negative ⇒ net-negative) and the **`level-fade = fat-tail`** structural finding (independent of floor/cost/tick) are conservative and hold *within `_screen`'s own basis*.
- **Suspect:** `mstrat`'s small-stop/low-ATR leaderboard (M-2, M-5); all cross-engine comparisons (M-1, M-3, M-4).
- **Procedural (CEO directive, overrides the above):** until this audit closes with a single canonical semantics adopted and BOTH engines re-run against it, **no leaderboard and no economic elimination is definitive** — because neither engine is yet shown to implement the canonical semantics, and they demonstrably disagree.

---

## 6. CANONICAL_TRADE_SIMULATION_CONTRACT (the single economic semantics all lab simulators must obey)
1. **Instrument:** `tick_size = 0.01` (XAUUSD instrument spec); declare `point_size`/`contract_size` explicitly, or document the engine as **R-based** (dimensionless) — it may not silently omit them.
2. **Entry:** next-open, `open[signal_idx+1]`; no lookahead (every stop/target known at entry).
3. **Risk denominator:** `executable_risk = max(strategy_stop_distance, min_executable_risk)`, `min_executable_risk = max(2·effective_spread, 5·tick_size, 0.10·ATR)` with **tick 0.01** (⇒ `5·tick = 0.05`, not 0.5). The floor is **required** (raw R explodes on tiny stops — the S6 artifact); it must use the correct tick. A GROSS-no-floor result is a **screen convenience**, labeled `gross`, and **never compared to a net verdict**.
4. **Cost:** economic verdicts are **NET**: `R = (dir·(exit−entry) − round_trip_cost)/executable_risk`, `round_trip_cost = 2·(spread + slippage)·tick` (or observed spread/slippage on DEMO). Commission a separate line if applicable.
5. **Intrabar (same-bar):** **worst-case STOP > TIME-STOP > TARGET**; scan **from the entry bar inclusive** (the open is the first tick).
6. **Horizon window:** a single explicit convention `[entry_idx, entry_idx + horizon]` — pick inclusive OR exclusive and use it in every engine (the off-by-one is not allowed to differ).
7. **Time-stop:** exit at the close of the horizon's last scanned bar; the horizon must be **live-valid** (a bar count or a calendar boundary), never a discovery-block boundary (Finding H′).
8. **Timezone / day / session:** 17:00-NY anchor everywhere; day/week/session indices derived caller-side from it, identically.
9. **Blocks:** any **formal / leaderboard** verdict uses the **manifest discovery segments**; a gap-derived quick-screen block is a screen convenience and is **not comparable** to a formal run.
10. **Fat-tail reporting:** always report single-best share and top-1%-trimmed avg_R/PF; a positive total built on <1% of trades is not edge (orthogonal to the floor — keep it).
11. **Provenance:** every emitted verdict declares which contract version, tick, cost, floor, window, and block model produced it — so two numbers are only compared when these match.

## HANDOFF → CEO / Statistician
1. **Freeze:** treat every existing leaderboard and economic elimination as **non-definitive** until the canonical contract is adopted and both engines re-run against it (CEO directive).
2. **Reconcile** `_screen`, `mstrat`, and `demo_gate` to the canonical semantics (§6) — the five divergences (M-1…M-5) are the exact gaps.
3. **Re-run** the `mstrat` 1,972-campaign under corrected tick + floor + reconciled cost/window/blocks; the 529-flip is a lower bound on the movement.
4. Alpha's gross-negative eliminations and the fat-tail finding are the safest survivors, but even they must be re-expressed on the canonical net-with-corrected-floor basis before being called final.

Red Team designed no remedy, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
