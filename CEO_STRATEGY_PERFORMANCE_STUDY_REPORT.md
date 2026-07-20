# CEO Strategy Portfolio Performance Study — Scenario A (Isolated) vs Scenario B (Competitive)

**Status: PROVISIONALLY ACCEPTED, audited and finalized 2026-07-20.** **Type**: CEO-directed research
study — NOT a Phase 7 checkpoint, NOT production work, does not change architecture state. **Scope
discipline honored throughout, both in the original study and this audit pass**: no algorithm was
modified, no parameter was tuned, no strategy was added or eliminated, `decision_intelligence`/
`decision_intelligence_v2`/`context_memory`/any Portfolio module was not touched, no production file was
modified (`git status --porcelain -- ai_trader/` confirmed empty at both the original study's close and
this audit's close). Every number in this report is produced by an already-shipped, unmodified function
— the exact list is in §1.

## 1. Methodological Verification (2026-07-20 audit)

Each of the CEO's eleven required checks, verified directly against source and data — not asserted:

**1. Same historical period, both scenarios.** `phase69a_isolated_run.py` (the isolated-scenario driver)
imports and calls `new_harness()` **directly from** `phase69a_funnel_run.py` (the competitive-scenario
driver) — confirmed by reading both files. `new_harness()` constructs one `SimulationContext` with
`date_range=DateRange(WINDOW_START, WINDOW_END)` where `WINDOW_START=1_729_674_000` (2024-10-23 09:00
UTC) and `WINDOW_END=1_761_210_000` (2025-10-23 09:00 UTC) — the identical 365-day, 23,639-M15-bar
window in both scenarios, by construction (one shared function, not two independently-written configs
that happen to agree).

**2. Same market data, both scenarios.** Both drivers pass the same `DATA_DIR = REPO_ROOT / "data" /
"market"` and `symbols=("XAUUSD",)` into the same `new_harness()` call — same `ReplayDataSource` reading
the same files.

**3. Same costs/spread/slippage/settlement, both scenarios.** `new_harness()` builds one `RiskConfig`
(`_risk_config()`: `reference_spread["XAUUSD"]=0.10`, `liquidity_floor["XAUUSD"]=1.0`,
`sizing.risk_per_trade_pct=0.05`) and passes it, along with the same `ManagerConfig`,
`enable_time_stops=True`, `enable_trailing_stops=True`, and `warmup_bars=200`, into the same
`SimulationHarness(...)` constructor for BOTH scenarios. Neither driver script overrides the harness's
own default cost model or fill model anywhere — both scenarios inherit the identical, unmodified
defaults. The only parameter that ever differs between the two calls is `strategy_id_filter`
(`None` for competitive, `frozenset({sid})` per isolated run).

**4. No look-ahead / future leakage.** Both scenarios run through the standard, unmodified
`SimulationHarness`/`MarketScanner`/`ReplayDataSource` pipeline — the same pipeline that governs every
other backtest in this project (Wave D, Phase 6.9, the Relevance Audit, all of Phase 6.10). Neither
driver script constructs a custom or future-peeking data path. `ai_trader.strategy_runtime.
context_access`'s own documented guarantee ("every value comes from `select_lookahead_safe_bars`-
produced data for the context's own `as_of`, with no way to peek ahead without bypassing this module
entirely") applies identically to both runs — inherited, not re-derived, exactly as every prior phase in
this project has relied on it.

**5. Same strategy version/parameters, both scenarios.** Both calls to `new_harness()` pass
`use_strategy_runtime=True` with no strategy-specific override — every strategy's own contract and
implementation is loaded from the same, single, unmodified Strategy Library in both scenarios;
`strategy_id_filter` only changes WHICH strategies are permitted to submit signals, never how any
strategy computes them.

**6. The 823 isolated and 142 competitive trades are comparable closed trades.**
`ai_trader/simulation/portfolio_simulator.py::TradeRecord` declares `exit_price: float` and
`exit_as_of: int` as non-optional, required fields (frozen dataclass, no `| None`, no default) — there
is no code path by which an open/floating position can appear in `account.trade_ledger` (the source of
every saved trade in both JSON files) with this shape. Every one of the 823 + 142 = 965 saved trades is
structurally a genuinely closed position.

**7. Zero-isolated-trade strategies were not blocked by data errors, warm-up, eligibility, or
integration bugs.** All 14 zero-isolated-trade strategies (S3, S7, S9, S11, S12, S15, S17, S19, S20,
S23, S27, S31, S38, S51) were checked directly: their own `risk_deny_reasons` contain only
`NOT_ACTIONABLE` (dominant), `SIZE_BELOW_MIN`, `INVALID_INPUT`, and `BELOW_FLOOR` — all pre-existing,
documented `RiskManager` categories describing genuine setup/eligibility gates, never an error code.
Both full JSON files (all 43 strategies × both scenarios) were scanned for every error/bug-indicating
deny-reason code this codebase defines (`INTERNAL_ERROR`, `SCHEMA_MISMATCH`, `PORTFOLIO_UNAVAILABLE`,
`DATA_DEGRADED`): **zero occurrences found anywhere.** `INVALID_INPUT` (present for S12, S51) is
`ai_trader/risk_manager/pipeline.py`'s own pre-existing "missing/invalid trade_context" defensive gate
on a malformed per-bar context, not a system failure.

**8. Profit factor, expectancy, drawdown, recovery factor, and Sharpe come exclusively from existing
infrastructure, never reinterpreted.** Confirmed by direct source citation in §2 of the original study
(unchanged in this audit): `compute_window_metrics` (win rate/PF/expectancy/net R/net PnL/drawdown/
monthly consistency/equity stability/max losing streak/avg holding bars), `_sharpe_ratio`/
`_best_worst_month`/`_direction_stats`/`_max_consecutive_wins` from `shadow_evidence/research.py`. The
two DERIVED ratios (payoff ratio, recovery factor) use the EXACT SAME formula
`ai_trader/simulation/performance_analyzer.py` already applies internally — reused verbatim, never
altered. **One explicit, disclosed substitution** (unchanged from the original study, restated here for
completeness): recovery factor uses the trade-sequence-based `max_drawdown` from `compute_window_metrics`
rather than the equity-curve-based `max_drawdown_pct` saved in the isolated scenario's own
`performance` block — because no per-strategy equity curve exists for the competitive scenario at all,
and the SAME drawdown definition must be used in both scenarios for the comparison to be valid. This is
a disclosed methodology choice, not a reinterpretation of what either existing function computes.

**9. The Alpha-proxy is exactly defined and never presented as demonstrated statistical alpha.** §5 of
this report states verbatim: "no beta-adjusted excess-return calculation exists anywhere in
`ai_trader/`, so this is raw profit generated, explicitly not risk/beta-adjusted alpha." Net PnL (an
already-computed field) is the only value used for this ranking; no new calculation was introduced.

**10/11. Rankings correctly treat small-sample strategies; no strategy with zero losses or an
undefined/infinite profit factor is classified artificially at the top without a sample-size
penalty.** Two audit-driven fixes were made to the ORIGINAL study's presentation (the underlying
computed numbers were already correct — this is a fix to how they were ranked/displayed, not a
recomputation):
- **Profit factor can never be infinite.** Verified by direct source read: `compute_window_metrics`
  (`ai_trader/strategy_health/metrics.py` line 78: `(gross_win / gross_loss) if gross_loss > 0 else
  None`) and `performance_analyzer.analyze()` (line 313, identical pattern) both return `None` on zero
  losing trades — never `inf`. No strategy anywhere in this dataset has an undefined/infinite PF.
- **Every ranking is now segmented into a "reliable sample (n≥25)" tier and a separately-labeled "small
  sample (n<25)" tier** (`ceo_strategy_performance_study_tables.md`, every ranking section). In the
  original study's single mixed-reliability tables, small-sample strategies (e.g. S8, n=4, PF=6.46)
  appeared ABOVE reliable strategies (e.g. S1, n=54, PF=1.59) with no sample-size signal attached — a
  genuine methodological gap the CEO's own audit correctly identified. This is now fixed at the
  presentation layer: the two tiers are never merged into one ranked list again.

## 2. Reproducibility Audit

**Reproduction command** (run from the repository root, no new backtest, existing scripts only):
```
"./venv/Scripts/python.exe" ceo_strategy_performance_study.py
```
This single script both computes every metric AND writes both output artifacts
(`ceo_strategy_performance_study_data.json`, `ceo_strategy_performance_study_tables.md`) — it is now the
one, final, canonical script for this study (the earlier two-script split has been folded into it; see
§5).

**Confirmed by running it twice, independently, and diffing every byte of both outputs:**
- Isolated total trades: **823** (both runs).
- Competitive total trades: **142** (both runs).
- The six Category-A candidates: **S1, S13, S39, S40, S46, S48** (both runs, identical order).
- ACTIVE strategies in isolation: **S42, S46** (both runs).
- ACTIVE strategies competitively: **zero** (both runs).
- `ceo_strategy_performance_study_data.json`: **byte-for-byte identical** across both runs (`diff`
  reports no difference).
- `ceo_strategy_performance_study_tables.md`: **byte-for-byte identical** across both runs, AFTER one
  audit-found-and-fixed bug (below).

**One genuine non-determinism was found and fixed during this audit**: the "highly correlated with"
column in the correlation-flags table built its candidate list via `sorted(set(pairs), key=-abs(value))`
— ties at equal `|correlation|` (common with 2–6-trade series producing many exact ±1.00 values) had no
defined secondary order, and Python's per-process string-hash randomization made `set()` iteration order
change between runs, producing a different (but numerically identical) column order each time. Fixed by
replacing the `set()`-based de-duplication with a `dict` plus an explicit, deterministic secondary sort
key (partner `strategy_id`, alphabetical). **This affected only the DISPLAY order of a descriptive list
column — the underlying correlation VALUES, the six candidates, the classification, and every numeric
ranking were never affected** (the raw `data.json` was already byte-identical across runs before this
fix, confirming the underlying computation was deterministic throughout; only one presentation-layer
list needed the fix).

**Zero `ai_trader/` changes**, confirmed via `git status --porcelain -- ai_trader/` before and after
every run in this audit: empty both times.

## 3. Blocking Analysis — Five Categories, Per Strategy

Full 43-row table: `ceo_strategy_performance_study_tables.md`, Table 2. Every count below is read
directly from the already-saved `risk_deny_reasons`/`order_counts` funnel data — no re-simulation.

**The five categories, mapped onto already-recorded fields (no new counting logic)**:
1. **Nonexistent signals** = `risk_deny_reasons['NOT_ACTIONABLE']` — the strategy's own setup never
   fired this bar.
2. **Generated but ineligible** = every OTHER deny reason except `NOT_ACTIONABLE` and
   `LIMIT_MAX_PER_SYMBOL` (`SIZE_BELOW_MIN`, `BELOW_FLOOR`, `COOLDOWN_*`, `INVALID_INPUT`, etc.) — a
   real setup was detected and scored but failed a sizing/eligibility/quality gate.
3. **Eligible but blocked by an already-open position** = `risk_deny_reasons['LIMIT_MAX_PER_SYMBOL']`
   specifically, and ONLY that reason.
4. **Executed** = `order_counts['filled']` (equals `n_trades`).
5. **Non-finalized / excluded from metrics** = `order_counts['cancelled'] + order_counts['expired']`.

**Per-strategy fields now reported (Table 2)**: isolated trade count, competitive trade count,
opportunities lost (isolated − competitive), **retention %** (competitive ÷ isolated), **crowding %**
(shared-slot denials ÷ ALL competitive-scenario denial events — a properly bounded [0%, 100%] fraction;
an earlier draft of this metric divided by opportunities-lost instead, which produced figures over 100%
since shared-slot denials are per-BAR events while opportunities-lost is a per-TRADE count — fixed
during this audit), and the **principal loss reason**, computed per strategy as whichever deny-reason
category shows the LARGEST numeric increase from isolated to competitive — never assumed to be
`LIMIT_MAX_PER_SYMBOL`, per the CEO's own explicit instruction not to presume the 823-minus-142 gap is
entirely shared-slot blocking.

**Result of that check — genuinely mixed, not uniform.** Across all 43 strategies: **24 show
`LIMIT_MAX_PER_SYMBOL` as the principal (largest-increasing) reason**, **7 show `BELOW_FLOOR` instead**
(a position-sizing eligibility gate, not the shared-slot rule), and **12 show no increase in any
category** (mostly the zero/near-zero-trade strategies). **This is exactly why the CEO's own instruction
not to presume the cause was correct to give** — an earlier draft of this report asserted "no exception
was found," which was FALSE and has been corrected here after re-checking every strategy individually.

**The 7 `BELOW_FLOOR`-principal strategies**: S14 (+74), S4 (+808), **S40 (+376)**, S41 (+325), S43
(+1,044), **S46 (+49)**, **S48 (+426)** — bold = also a Category-A candidate (§4). `BELOW_FLOOR` denies
a signal whose computed position size falls below the minimum tradeable size — a plausible, disclosed
mechanism (not traced further in this audit) is that the competitive scenario's shared account equity/
exposure dynamics compute a different position size than an isolated strategy's own dedicated $2,000
capital would, for the same nominal risk %, more often pushing the result below the floor. **This is
disclosed as a plausible mechanism, not asserted as verified** — confirming it would require tracing
`risk_manager/sizing.py`'s own exact formula against both scenarios' equity curves, out of this study's
own scope.

**Even where `BELOW_FLOOR` is the LARGEST-increasing category, `LIMIT_MAX_PER_SYMBOL` is usually still a
large, real, independent contributor** — not negligible just because it is not #1: S40's own
`LIMIT_MAX_PER_SYMBOL` delta is `+170` (isolated 1,836 → competitive 2,006 — note the large ISOLATED
count itself, since a single strategy can already deny its own later signals while its own earlier
position is still open, even with zero competition; the delta isolates the competition-specific
increment). S48's own `LIMIT_MAX_PER_SYMBOL` delta is `+322`, nearly as large as its `BELOW_FLOOR`
delta of `+426`. **S46 is the one genuine exception where shared-slot denials actually DECREASED under
competition** (`478→458`, delta `-20`) — consistent with §3.2 of the original study's own observation
that S46 "retains the largest share of its opportunity set proportionally" among the candidates.

**Important nuance surfaced by this audit, not present in the original study**: crowding % (share of ALL
denial EVENTS specifically due to the shared slot) is typically small — 1–5% for most strategies — because
`NOT_ACTIONABLE` dominates total denial volume overwhelmingly (tens of thousands of "no setup this bar"
events vs. hundreds of shared-slot denials). **This does NOT mean the shared slot is a minor factor** —
it means most bars never reach the stage where the shared slot could even matter. The correct, CEO-
requested causal question — "of the trades that WOULD have happened, which ones did NOT, and why" — is
answered by the **principal loss reason** column, not the crowding % column; both are now reported, and
this report does not let the small crowding-% figure be misread as contradicting the dominant-cause
finding.

## 4. Final Classification (A/B/C/D/E)

Full 43-row table with an exact, numeric justification per strategy: `ceo_strategy_performance_study_
tables.md`, Table 4. **No strategy was eliminated. No threshold was modified** — `MIN_TRADES_RELIABLE =
25` is reused verbatim from `code/alpha_lab.py`'s own live `MINTR` constant (the same reuse this whole
Context Memory/Decision Intelligence effort already established as precedent); profitability is defined
as `profit_factor > 1.0 AND expectancy_r > 0.0` (the same pairing the original study already used).

| Category | Definition | Count | Strategies |
|---|---|---|---|
| **A — Candidate** | reliable (n≥25) AND profitable | **6** | S1, S13, S39, S40, S46, S48 |
| **B — Promising** | profitable but under-sampled (n<25) | **10** | S18, S28, S30, S41, S42, S45, S5, S50, S6, S8 |
| **C — Reliable but unprofitable** | reliable (n≥25), NOT profitable | **4** | S10, S25, S4, S44 |
| **D — Inactive** | zero isolated trades | **14** | S3, S7, S9, S11, S12, S15, S17, S19, S20, S23, S27, S31, S38, S51 |
| **E — Inconclusive** | non-zero but under-sampled AND unprofitable/mixed | **9** | S14, S16, S2, S21, S22, S24, S26, S29, S43 |

Total: 6+10+4+14+9 = 43. Every strategy's own exact justification string (citing its own n_trades,
profit_factor, expectancy_r, and health state) is in Table 4 — e.g. S1: *"Candidate — reliable and
profitable: n=54 (>= 25), PF=1.59 (>1), Exp_R=0.249 (>0), health=WATCHLIST."*

**Note on D vs. E**: the original study's Table 4 had merged D and E into one "INSUFFICIENT EVIDENCE"
bucket (14+9=23, matching this audit's separated D+E total exactly) — this audit separates them per the
CEO's own explicit five-category taxonomy, since "never traded at all" (D) and "traded a little, with
weak/negative results" (E) are meaningfully different findings, not one undifferentiated "we don't
know" bucket.

## 5. Artifact Preservation

**Kept** (the complete, final artifact set):
- `CEO_STRATEGY_PERFORMANCE_STUDY_REPORT.md` — this report.
- `ceo_strategy_performance_study_tables.md` — full 43-row tables (master comparison, 5-category
  blocking taxonomy, robustness/payoff/recovery/best-worst-month, tiered rankings, correlation flags,
  final A–E classification).
- `ceo_strategy_performance_study_data.json` — full machine-readable result, every computed field, all
  43 strategies, both scenarios.
- `ceo_strategy_performance_study.py` — the single, final analysis + report-generation script.

**Removed**: `ceo_strategy_performance_report_gen.py` — its table-generation logic was folded directly
into `ceo_strategy_performance_study.py` (now one canonical script, per the CEO's own "keep THE final
analysis script" instruction) rather than kept as a second, separately-invoked stage. This is the only
file removed; it was genuinely superseded, not merely redundant, and its logic is fully present (and
extended with the audit fixes) in the file that replaces it.

**Not touched, not removed**: `phase69a_isolated_funnel.json`, `phase69a_competitive_funnel.json`, and
every `phase69a_*.py` script — these are Phase 6.9A's own preserved diagnostic artifacts, the data
source this study reads from; this study has no authority over them and did not modify them.

### Reproduction (README)

```
cd "C:\Users\MEDION GAMING\ai_quant_lab-research-main"
"./venv/Scripts/python.exe" ceo_strategy_performance_study.py
```
Reads `phase69a_isolated_funnel.json`/`phase69a_competitive_funnel.json` (must be present, unmodified,
at repo root), computes every metric via the existing functions listed in §1, and overwrites
`ceo_strategy_performance_study_data.json`/`ceo_strategy_performance_study_tables.md` in place. No
network access, no other input files, no `ai_trader/` import that mutates state. Running it twice in a
row produces byte-identical output (verified in §2).

## 6. What This Study Still Does Not Claim (unchanged from the original study, restated for completeness)

- **Not a statistical validation.** No p-values, no bootstrap, no FDR correction. Sample sizes for most
  strategies (especially competitive-scenario) are too small for inference, disclosed throughout.
- **Not the full historical range.** Covers the same 1-year Phase 6.9A window, not Wave D's 3.6-year
  range — the only window with a genuine paired isolated/competitive dataset already saved.
- **Not a Portfolio Architect design.** Recommends candidates for a future Portfolio Architect's own
  consideration; does not design, propose, or implement any capital-allocation or multi-position
  architecture.
- **Regime-worst-performance remains a temporal (best/worst MONTH) proxy, not a true market-regime
  join** — disclosed and unchanged from the original study (§1 of the original methodology section).
- **Correlation/diversification data remains unreliable for most strategy pairs** given competitive-
  scenario data sparsity — restated, not resolved, by this audit.

## 7. Final Report to CEO

- **Files kept**: `CEO_STRATEGY_PERFORMANCE_STUDY_REPORT.md`, `ceo_strategy_performance_study_tables.md`,
  `ceo_strategy_performance_study_data.json`, `ceo_strategy_performance_study.py`.
- **Files removed**: `ceo_strategy_performance_report_gen.py` (superseded, folded into the final script).
- **Commit hash**: recorded after commit, see final session output.
- **Reproduction command**: `"./venv/Scripts/python.exe" ceo_strategy_performance_study.py` (§5).
- **Verification results**: all 11 CEO-required methodological checks passed (§1); reproducibility
  confirmed byte-for-byte on both output files after one genuine (display-order-only) non-determinism
  was found and fixed (§2); blocking taxonomy correctly separates the five requested categories per
  strategy and does not presume shared-slot blocking without checking (§3); classification split into
  the five requested categories with zero strategies eliminated and zero thresholds altered (§4).
- **Remaining limitations**: unchanged from §6 above — no statistical validation, 1-year window only,
  no Portfolio Architect design, temporal (not true regime) worst-performance proxy, thin competitive-
  scenario correlation data.
- **The six candidates are UNCHANGED after audit**: S1, S13, S39, S40, S46, S48.
- **Shared-slot crowding is the demonstrated dominant cause of lost trade opportunities across the
  portfolio as a whole, but NOT universally per-strategy** — the per-strategy "principal loss reason"
  computation in §3 shows `LIMIT_MAX_PER_SYMBOL` as the largest-increasing denial category for 24 of 43
  strategies; **7 strategies, including three of the six candidates (S40, S46, S48), show `BELOW_FLOOR`
  (a position-sizing gate) as their own largest-increasing category instead** — a genuine, checked
  finding, not an exception that was overlooked. An earlier draft of this report incorrectly asserted no
  exception existed; that claim has been corrected here after re-verifying every one of the 43 strategies
  individually, exactly the kind of error this audit was requested to catch.
