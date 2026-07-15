# Strategy Runtime Integration Gap — Analysis (read-only)

**Date:** 2026-07-15. **Scope:** read-only investigation of why the Simulation Framework (Phase 6.7,
READY) produces zero trades against real historical data. **No code was written, no strategy file was
modified, nothing was optimized, no Learning Engine work was started.** Every claim below was verified
directly against the repository — either by reading source/data files, or by running the real,
unmodified `StrategyManager`/`MarketScanner` against the real `knowledge/strategies/` library and
reporting its actual output. Nothing here is inferred from documentation alone where the code itself
could be run and observed.

---

## Executive summary

There are **two independent, stacked gaps**, not one:

1. **Contract-format gap (blocks loading):** all 51 `knowledge/strategies/S*/strategy.json` files are in
   the Research Lab's own v0 "research contract" shape (`id`/`entry_rules`/`exit_rules`/`grammar`/
   `executable_default`/`performance`/...). None of them contain the six top-level keys Strategy
   Interface v1 requires (`interface_version`, `identity`, `lifecycle`, `semantics`, `execution`,
   `evidence`, `provenance`). Loading the real library through the real `StrategyManager` confirms **all
   51/51 fail schema validation identically** and are quarantined as `Health.INVALID` before ever
   reaching the registry as loaded. `StrategyManager.active_strategies()` therefore always returns an
   empty list.
2. **Runtime-logic gap (blocks signal generation, independent of #1):** even a hypothetically
   v1-valid contract would still produce nothing, because `StrategyRuntimeHandle` (the object Signal
   Engine calls) is a **universal, strategy-agnostic stub** — every method except `required_context()`
   unconditionally raises `StrategyApiNotImplementedError`, by explicit design (`handle.py`'s own
   docstring: "a deliberate, documented scope boundary, not an oversight"). No strategy, however
   perfectly its contract were migrated, has any actual entry/exit/stop evaluation logic wired into the
   AI Trader runtime today.

Closing gap #1 alone (a pure JSON restructuring exercise) would still yield zero trades. Both gaps must
close, for at least one strategy, before the Simulation Framework can produce a single real trade.

---

## 1. Which S1–S51 strategies have actual executable setup-generation code

**None.** `find knowledge/strategies -iname "*.py"` returns zero results. Every one of the 51 strategy
folders contains exactly two files: `README.md` and `strategy.json` — confirmed by listing all 51
folders directly; the pattern is uniform, with no exception. There is no Python (or any other
executable) code anywhere under `knowledge/strategies/`.

## 2. Which strategies exist only as JSON/README specifications

**All 51.** Same evidence as §1 — every strategy, including the six explicitly named
`S32_not_implemented` … `S37_not_implemented`, has only a prose README and a JSON spec. The JSON's own
`executable_default.params` field is not executable code either — it is a **parameter tuple** into the
frozen Research Lab engine's grammar (`code/mstrat.py`/`code/families.py`), meaningful only to that
batch backtester, not to any AI Trader runtime component.

## 3. Which strategy contracts are still v0 seed format

**All 51.** Every `strategy.json` uses the same flat shape: `id, name, klass, slug, status, timeframe,
sessions, long_short, htf_context, mechanism, entry_rules, exit_rules, stop_loss_rules,
required_confirmations, invalid_conditions, position_sizing, grammar, executable_default, performance,
monte_carlo, walk_forward, confidence, validation_status, provenance`. None carry an
`interface_version` field or any of Strategy Interface v1's required top-level keys (§4). This is the
Research Lab's own publication format (`knowledge/strategies/library_manifest.json`'s own header:
`"interface": "Research-Lab -> AI-Trader"`, `"engine": "mstrat.py v2 (FROZEN)"`) — a research-artifact
export, not an AI-Trader-runtime contract. `library_manifest.json`'s own per-strategy `status` field
(`IMPLEMENTED` for 43, `INVALID` for 2 — S47, S49 — `NOT_IMPLEMENTED` for 6 — S32–S37) describes
**research-engine executability** (can `mstrat.py` run this grammar tuple), which is completely
orthogonal to AI-Trader-runtime loadability — confirmed by §4 below, where all 51 (including the 43
marked "IMPLEMENTED" by the Research Lab) fail identically at the AI Trader boundary.

## 4. Which contracts fail Strategy Interface v1 validation

**All 51 — verified empirically**, not inferred. Ran the real `StrategyManager.load_library()` (no
mocks, no modification, default `library_path` = `knowledge/strategies/`, the same path the Simulation
Harness itself uses) and read the resulting `LoadReport` directly:

```
loaded=()
failed = 51 LoadFailure entries, EVERY ONE:
  health=Health.INVALID
  reasons=("data must contain ['evidence', 'execution', 'identity', 'interface_version',
            'lifecycle', 'semantics'] properties",)
counts_by_lifecycle = {'INVALID': 51, everything else: 0}
counts_by_health    = {'INVALID': 51, everything else: 0}
```

Every strategy fails the exact same `jsonschema` structural check — none get past schema validation to
reach any deeper compatibility/semantic check. This is the single most concrete, reproducible fact in
this report: `active_strategies()` on the real library is provably always `[]`.

## 5. Why Strategy Manager currently quarantines real strategies

`loader.py` runs each `strategy.json` through `strategy_manager/schema_validation.py`'s compiled
`strategy_contract.v1.schema.json` validator before anything else — this is the FIRST gate, ahead of
compatibility checking, ahead of the Context Aggregator, ahead of lifecycle assignment. A structural
failure here maps directly to `Health.INVALID` (`lifecycle.py`'s own comment: "T15: quarantine;
Health.INCOMPATIBLE carries the specific reason" — the more general INVALID path applies when the
document doesn't even parse as a valid contract). `Health.INVALID` is explicitly excluded from
`ACTIVATABLE_LIFECYCLES` (`types.py`), so these 51 entries sit in the registry (visible via
`list_strategies()`/`snapshot()`, per the Manager's own "never silently drop, always disclose"
convention — `health.py`: "N strategy(ies) are quarantined (CORRUPTED/INVALID/INCOMPATIBLE)") but are
never returned by `active_strategies()`. This is Strategy Manager working exactly as designed against
malformed input — not a Strategy Manager defect.

## 6. Why Signal Engine produces zero actionable signals

Two independent, sufficient causes, either one alone would be enough:

- **Upstream starvation (the actual cause in the current repo state):** `active_strategies()` returns
  `[]` (§4/§5), so the Simulation Harness's `signal_engine.evaluate(ctx, handles=[], ...)` call has
  nothing to evaluate — an empty `handles` list produces an empty `SignalBatch`, deterministically,
  every bar. This is what Phase 6.7's own full-history benchmark run actually exercised (83,479 bars,
  zero trades) — confirmed to be starvation, not a Signal-Engine-side rejection, since no real handle
  ever reached `evaluate()` in the first place.
- **Downstream stub (would still block signals even with zero strategies fixed at the contract layer):**
  `ai_trader/strategy_manager/handle.py`'s `StrategyRuntimeHandle.detect/generate_signal/get_score/
  can_trade/can_open_position/explain_signal/health` all unconditionally raise
  `StrategyApiNotImplementedError`. Signal Engine's own `pipeline.py` catches this by design and
  classifies it as `SignalState.INVALID` / `CORRUPTED_OUTPUT` (never propagated, never crashes) —
  confirmed by reading `pipeline.py` directly, which names this exact exception class in its own
  docstring as the expected, handled case. So even after §1–§5 are fixed for one strategy, that
  strategy's `StrategyHandle.api` would still need REAL evaluation logic — the generic
  `StrategyRuntimeHandle` object never provides any, for any strategy, by design.

## 7. What exact adapter or migration layer is required

Two distinct, separately-scoped pieces of work — do not conflate them:

- **(A) Contract migration layer** — a one-time, offline transform of each `strategy.json`'s v0 research
  fields into Strategy Interface v1's required shape (`interface_version`, `identity`, `lifecycle`,
  `semantics`, `execution`, `evidence`, `provenance` — see `knowledge/interface/
  strategy_contract.v1.schema.json` for the exact nested shape of each). This is pure data
  restructuring: mapping `entry_rules`/`stop_loss_rules`/`exit_rules`/`grammar`/`executable_default`
  prose+params into v1's structured fields. No new trading logic is invented here — the mechanism stays
  exactly what the Research Lab already validated (or didn't — `validation_status`/`confidence`/
  `monte_carlo` fields must carry over honestly, unchanged).
- **(B) Runtime strategy evaluator(s)** — actual Python code implementing `STRATEGY_API_v1.md`'s 7
  methods (`required_context`, `detect`, `generate_signal`, `get_score`, `can_trade`,
  `can_open_position`, `explain_signal`, `health`) against the live, bar-by-bar `MarketContext` shape
  Signal Engine actually passes in — a fundamentally different execution model from the Research Lab's
  own whole-DataFrame batch sweep (§8). Either: (B1) one hand-written evaluator per strategy (highest
  fidelity, most work), or (B2) a single shared rule-interpreter that reads a strategy's now-structured
  v1 `semantics`/`execution` fields and evaluates them generically against `MarketContext` (less work
  per strategy, but the interpreter itself is new, non-trivial logic that needs its own design/review —
  a real engineering decision for whoever scopes the next phase, not a decision made here).

## 8. Whether existing research functions can be reused without importing Research Lab at runtime

**Not directly — the code itself is architecturally incompatible with per-bar runtime evaluation, but
the underlying formulas can be reused as a reference to port, not as a library to call.**
`code/mstrat.py`/`code/families.py` are vectorized, whole-history `pandas`/`numpy` batch functions
(`load()` pulls the ENTIRE `s1.load_s1()` DataFrame; `setups(d, h)` sweeps a whole hypothesis grammar
over the whole DataFrame at once) coupled to `alpha_lab.CFG` and the Research Lab's own data-loading
module — the opposite shape from Signal Engine's `evaluate_strategy(context: MarketContext, handle,
trader_state)`, which is called once per symbol per bar with only the lookahead-safe rolling-window
features Market Scanner has already computed for that instant. Importing `code/mstrat.py` at AI Trader
runtime would also directly violate the already-established, repeatedly-reconfirmed boundary (Strategy
Manager's own architecture doc: "no Research-Lab access"; the 0-diff invariant every phase since 6.1 has
verified). The correct reuse is: read the relevant formula/threshold logic from `code/mstrat.py`/
`families.py` OFFLINE (as a human/design reference, exactly as this report itself just did), and
re-implement the equivalent per-bar logic natively as new, reviewed AI Trader code in (B) above — never
import the Research Lab module itself into any `ai_trader/` file.

## 9. How to preserve strict Research Lab ↔ AI Trader separation

Mirror the pattern every module since Phase 5.1 has already established, with no new mechanism needed:
- **Reads of `code/`/`results/`/`knowledge/{strategies,interface}` are always OFFLINE/DESIGN-TIME**
  (a migration script run once by a human/session, its OUTPUT committed as data — new/updated
  `strategy.json` v1 files under `knowledge/strategies/`) — never an `import` inside `ai_trader/`.
- **`ai_trader/` code only ever reads `knowledge/strategies/*.json` through `StrategyManager.load_library()`**
  exactly as today — the contract IS the boundary; nothing new to invent here.
- **The 0-diff check already used by every phase** (`git diff cef57c1~1 HEAD -- code/ results/ knowledge/`)
  would need to tolerate `knowledge/strategies/` changes for this specific phase — the CEO would need to
  explicitly re-scope that invariant for a "migrate the Strategy Library" phase (it currently asserts
  the WHOLE `knowledge/` tree is frozen; strategy contract migration is a deliberate, in-scope exception
  to disclose and get explicit sign-off on, not something to silently reinterpret).
- **The runtime evaluator(s) (B) are pure, new `ai_trader/` code** — no Research Lab import, reviewed
  and tested exactly like every other AI Trader module (mypy --strict, adversarial review, etc.).

## 10. What minimum vertical slice should be implemented first

**One strategy, end-to-end, not a batch migration.** Candidate: **S1 (Confirmed Liquidity Sweep
Reversal)** — already the best-specified contract in the library (explicit, mechanical entry/exit/stop
rules; a documented, bounded state machine: sweep → confirmation window → next-open entry; no
higher-timeframe context required, `htf_context: "none"`), and its Research Lab verdict is honestly
disclosed as "no confirmed alpha" (`validation_status: "EXPLORATORY"`) — meaning the vertical slice's
purpose is to PROVE THE PIPE WORKS, not to expect real profitability from this specific strategy.
Rationale for one-strategy-first: the goal of the next phase is to prove the (A)+(B) integration
mechanics end-to-end through the ALREADY-READY Simulation Framework (Phase 6.7) before paying the cost
of doing it 50 more times — exactly the same "smaller scale baseline first" discipline
`SIMULATION_HANDOFF.md` §12 already established for the Simulation Framework's own benchmark.

---

## Recommended phased integration plan (NOT authorized to begin — CEO gate required)

**Phase A — Contract migration (data only, no runtime code):**
Design the v0→v1 field mapping once, against `strategy_contract.v1.schema.json`; migrate S1 first (the
vertical-slice candidate), producing a NEW, schema-valid `strategy.json` for S1 only. Verify with
`StrategyManager.load_library()` that S1 (and only S1) now loads with `Health.LOADED` and an
`ACTIVATABLE` lifecycle. Do not touch S2–S51 in Phase A — prove the transform on one before deciding
whether to batch or hand-review the rest.

**Phase B — Runtime evaluator for the frozen subset (new `ai_trader/` code):**
Implement a real `StrategyRuntimeHandle`-conformant evaluator for S1 only (decision B1 vs B2 from §7 is
itself a design choice for that phase to make and document, not pre-decided here). Unit-test it directly
against hand-constructed `MarketContext` fixtures (mirroring every prior module's own fixture-first
testing discipline) before touching the composed pipeline at all.

**Phase C — Connect to Strategy Manager / Signal Engine:**
Wire the Phase B evaluator into the real registry so `active_strategies()` returns the S1 handle and
Signal Engine's real `evaluate()` call reaches real logic instead of the stub. Prove end-to-end via the
Execution Engine's own existing "real ALLOW decision" test pattern (`TestRealAllowDecisionFillsEndToEnd`)
extended one level further upstream — a real `MarketContext` → real `detect`/`generate_signal` → real
`StrategySignal`, not a fixture-forced one.

**Phase D — First real end-to-end XAUUSD backtest:**
Run the (already READY) Simulation Framework over historical XAUUSD data with the CEO-specified account
parameters — **starting capital 2,000 USD, risk per trade 5%** — through the real S1 evaluator. This is
the first run where a genuine `RiskDecision.ALLOW` can be produced by real strategy logic rather than a
test fixture; expect it to surface additional, currently-invisible integration gaps (sizing at this
capital scale, `min_qty`/`lot_step` interaction, whether 5%-per-trade risk is compatible with Risk
Manager's own configured limits) — budget time to discover and document those, not just to run the
number and declare success.

**Explicit stop conditions for whoever picks this up:** do not implement Phases A–D without a fresh CEO
go-ahead for that specific phase (same standing rule as every prior phase); do not batch-migrate S2–S51
before Phase A proves out on S1; do not begin Learning Engine, Broker Adapter, MT5, or live/paper trading
under cover of this plan.
