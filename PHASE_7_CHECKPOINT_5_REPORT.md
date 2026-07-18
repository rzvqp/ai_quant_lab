# Phase 7 — Checkpoint 5: Market Intelligence Layer

## 1. Executive Summary

Checkpoint 5 builds the **Market Intelligence layer** (`ai_trader/market_intelligence/`) — the first
component of the AI Trader's reasoning process. It answers exactly one question, continuously: *"What
is the market doing right now?"* It never answers *"What trade should I take?"* — no BUY/SELL signal,
no execution, no optimization, no portfolio decision, and no health classification exists anywhere in
this package.

Nine market dimensions are objectively described from the existing `MarketContext`: Trend, Market
Structure, Momentum, Volatility, Liquidity behaviour, Expansion vs Compression, Session behaviour,
Multi-timeframe agreement, and Context confidence. Every reading reuses this repo's own
already-computed, already-tested features wherever they exist (`market_scanner`'s M15/H1/H4/D1
indicator features); the one dimension with no existing centralized implementation — Market
Structure (swing points, prevailing structure, BOS/CHoCH break classification) — is new, disclosed
logic built directly from raw OHLC bars.

The layer is a pure, read-only function of an already-produced `MarketContext`: `build_market_intelligence(context) -> MarketIntelligenceSnapshot`.
It is not wired into `harness.py`, the Signal Engine, Scoring Engine, Risk Manager, Execution Engine,
or Shadow Evidence — it has no callers in production code yet, by design, matching the CEO's framing
that this checkpoint delivers the foundation future components (Edge Intelligence, Decision AI,
Strategy Health, Portfolio Architect, Learning Engine, Live AI Trader) will build on.

## 2. Architecture

```
MarketContext (ai_trader.strategy_runtime.context_access)
        |
        v
build_market_intelligence(context)              <- single public entry point (engine.py)
        |
        +--> analyze_trend(context)              -> {"M15": TrendReading, "H1": .., "H4": .., "D1": ..}
        +--> analyze_momentum(context)            -> {"M15": MomentumReading, "H1": .., "H4": .., "D1": ..}
        +--> analyze_structure(context)           -> StructureReading   (M15, new swing/BOS/CHoCH logic)
        +--> analyze_volatility(context)          -> VolatilityReading
        +--> analyze_liquidity(context)           -> LiquidityReading
        +--> analyze_expansion(context)           -> ExpansionReading
        +--> analyze_session(context)             -> SessionReading
        |
        +--> analyze_multi_timeframe_agreement(trend_readings)   -> MultiTimeframeAgreement
        |        (pure function OVER the trend readings above -- never re-touches context)
        |
        +--> compute_context_confidence(data_quality_level, agreement, volatility)
                 (pure function OVER the agreement + volatility readings above)
        |
        v
MarketIntelligenceSnapshot   (symbol, as_of, trend, momentum, structure, volatility, liquidity,
                               expansion, session, multi_timeframe_agreement, confidence)
```

Every dimension is computed independently from the same read-only `context` — no analyzer depends on
another analyzer's output, except `agreement` (depends on `trend`'s readings) and `confidence` (depends
on `agreement` + `volatility`'s readings), which take those results as explicit function arguments
rather than recomputing anything. This mirrors the generic-aggregation-over-explicit-arguments pattern
already established by `shadow_evidence/aggregation.py` and `shadow_evidence/research.py`.

## 3. Data Flow

1. Something upstream (not part of this checkpoint) already produced a `MarketContext` — the same
   read-only dict-shaped view strategies consume via `context_access`, containing per-timeframe bars,
   features, feature history, session info, and a data-quality level.
2. `build_market_intelligence(context)` is called once per bar/context snapshot.
3. Each of the seven independent analyzers reads only the fields it needs via the public
   `context_access` accessors (`feature`, `flag`, `bars`, `last_bar`, `session_name`,
   `data_quality_level`, etc.) — never touching the raw dict directly.
4. Two derived analyzers (agreement, confidence) consume the already-computed readings, not the raw
   context.
5. All nine readings are assembled into one immutable `MarketIntelligenceSnapshot` and returned. The
   input `context` is never mutated (verified by `test_build_market_intelligence_never_mutates_the_input_context`).
6. Missing or insufficient data at any stage degrades honestly to `UNKNOWN`/`None` at that dimension
   only — it never fabricates a value and never raises.

## 4. Public API

```python
from ai_trader.market_intelligence.engine import build_market_intelligence

snapshot = build_market_intelligence(context)   # MarketContext -> MarketIntelligenceSnapshot
```

This is the **only** function future components are expected to call. Every analyzer module
(`trend.py`, `momentum.py`, `structure.py`, `volatility.py`, `liquidity.py`, `expansion.py`,
`session_behavior.py`, `agreement.py`, `confidence.py`) also exposes its own `analyze_*`/`compute_*`
function directly, for callers that need one dimension in isolation without paying for the rest.

## 5. Internal Components

| Module | Responsibility |
|---|---|
| `types.py` | All dataclasses/enums — the shared vocabulary every other module and every future consumer imports. |
| `trend.py` | Per-timeframe (M15/H1/H4/D1) trend direction + strength, reusing existing `m_trend_up`/`h1_trend_up`/`h4_trend_up`/`d1_trend_up`/EMA features. |
| `momentum.py` | Per-timeframe RSI-based momentum state + rate of change, reusing existing RSI features. |
| `structure.py` | **New.** Fractal swing-point detection, prevailing structure (higher-high/higher-low vs lower-high/lower-low), BOS vs CHoCH break classification from raw M15 bars. |
| `volatility.py` | ATR/ATR-moving-average ratio regime classification, bounds mirrored from `risk_manager`'s own documented (frozen, untouched) volatility filter. |
| `liquidity.py` | Rolling-volume-ratio regime classification (thin/normal/thick). |
| `expansion.py` | Compression vs displacement/expansion state from existing `compress`/`disp` features. |
| `session_behavior.py` | Session name, bar-in-session, opening-range position, VWAP relation, session gap. |
| `agreement.py` | Multi-timeframe directional agreement score/level over the trend readings. |
| `confidence.py` | Overall context confidence score blending data quality, agreement, and volatility penalty. |
| `engine.py` | `build_market_intelligence()` — wires all of the above into one snapshot. |

## 6. Data Structures

All immutable `@dataclass` types, defined once in `types.py`:
`TrendReading`, `MomentumReading`, `StructureReading` (+ `SwingPoint`), `VolatilityReading`,
`LiquidityReading`, `ExpansionReading`, `SessionReading`, `MultiTimeframeAgreement`,
`ContextConfidence`, and the top-level `MarketIntelligenceSnapshot`. Each carries an explicit
`*State`/`*Direction`/`*Regime`/`*Level` enum with an `UNKNOWN` member — the only value ever used when
data is missing or insufficient. No field here duplicates or reinterprets a `strategy_health` or
`shadow_evidence` type; there is zero overlap with `WindowMetrics`, `HealthState`, or `WindowScore`.

## 7. Extension Points

The design is intentionally shallow so future layers can compose over it without redesign:
- **Edge Intelligence** / **Decision AI** can take a `MarketIntelligenceSnapshot` (or a history of them)
  as a pure input feature set — no changes needed here.
- **Strategy Health** / **Portfolio Architect** remain fully decoupled — this package imports nothing
  from `strategy_health` or `shadow_evidence`, and nothing in this package is a scoring/classification
  output.
- **Learning Engine** can be fed a time series of snapshots directly, since every reading is
  deterministic and reproducible from the same context.
- **Live AI Trader** can call `build_market_intelligence()` once per bar exactly as the (not-yet-built)
  research/backtest driver will, with identical semantics in both.
- New dimensions can be added as new analyzer modules + new dataclass fields without touching existing
  ones, following the same "independent pure function over `MarketContext`" shape.

## 8. Test Strategy

- **Unit tests** (one file per analyzer, `ai_trader/market_intelligence/tests/test_*.py`): hand-built
  `MarketContext` fixtures via `tests/_fixtures.py`, covering the full-data path, the no-data/insufficient-data
  path (must degrade to `UNKNOWN`/`None`, never raise), and a determinism check (`analyze_x(ctx) == analyze_x(ctx)`)
  for every module. `structure.py` additionally has hand-traced fixtures for bullish/bearish BOS, bullish
  CHoCH, ranging (no break), insufficient-swings UNCLEAR, and highs/lows-disagree UNCLEAR.
- **Engine-level unit tests** (`test_engine.py`): full-data snapshot assembly, honest degradation with
  zero data, determinism, and non-mutation of the input context.
- **Real-data integration test** (`test_integration.py`, new in this checkpoint): drives a real
  `MarketScanner` + `ReplayDataSource` pair directly (the same construction `SimulationHarness.load()`
  itself uses) over real XAUUSD market data for the established 85-day window, feeding ~300 real,
  fully-warmed-up contexts into `build_market_intelligence()` to confirm it never raises over real data,
  is deterministic on real contexts, and produces genuinely non-trivial (not permanently `UNKNOWN`)
  readings across trend, volatility, structure, and session dimensions — proving real wiring, not just
  fixture correctness.

## 9. Files Modified / Added

All files are new; nothing pre-existing was modified.

```
ai_trader/market_intelligence/__init__.py
ai_trader/market_intelligence/types.py
ai_trader/market_intelligence/trend.py
ai_trader/market_intelligence/momentum.py
ai_trader/market_intelligence/structure.py
ai_trader/market_intelligence/volatility.py
ai_trader/market_intelligence/liquidity.py
ai_trader/market_intelligence/expansion.py
ai_trader/market_intelligence/session_behavior.py
ai_trader/market_intelligence/agreement.py
ai_trader/market_intelligence/confidence.py
ai_trader/market_intelligence/engine.py
ai_trader/market_intelligence/tests/__init__.py
ai_trader/market_intelligence/tests/_fixtures.py
ai_trader/market_intelligence/tests/test_trend.py
ai_trader/market_intelligence/tests/test_momentum.py
ai_trader/market_intelligence/tests/test_structure.py
ai_trader/market_intelligence/tests/test_volatility.py
ai_trader/market_intelligence/tests/test_liquidity.py
ai_trader/market_intelligence/tests/test_expansion.py
ai_trader/market_intelligence/tests/test_session_behavior.py
ai_trader/market_intelligence/tests/test_agreement.py
ai_trader/market_intelligence/tests/test_confidence.py
ai_trader/market_intelligence/tests/test_engine.py
ai_trader/market_intelligence/tests/test_integration.py
```

No file outside `ai_trader/market_intelligence/` was touched. `harness.py`, the Signal Engine, Scoring
Engine, Risk Manager, Execution Engine, and Shadow Evidence are byte-for-byte unchanged from the
Checkpoint 4 commit.

## 10. Validation

```
pytest ai_trader/ -q
    -> 1752 passed (Checkpoint 4 baseline 1690 + 62 net new, zero regressions, zero failures)

mypy --strict ai_trader/ --exclude 'tests/'
    -> Success: no issues found in 185 source files (Checkpoint 4 baseline: 173)

coverage report --omit="*\tests\*"
    -> TOTAL 10612 stmts, 432 miss, 96%  (Checkpoint 4 baseline: 10249 stmts, 432 miss, 96%)
    -> +363 new statements from market_intelligence, +0 net new misses
    -> every market_intelligence/*.py source file: 100% covered individually
       (__init__ 1/1, agreement 19/19, confidence 11/11, engine 19/19, expansion 16/16,
        liquidity 26/26, momentum 27/27, session_behavior 21/21, structure 55/55,
        trend 32/32, types 112/112, volatility 24/24)
```

**Adversarial scope review** (grep-verified against the CEO's explicit DO-NOT list):
- No import of `ai_trader.strategy_health.scoring`, `.classifier`, or `.evaluator` anywhere in the package.
- No `HealthState` or `WindowScore` type used or produced anywhere in the package.
- No import of `signal_engine`, `scoring_engine`, `risk_manager`, `execution_engine`, or `shadow_evidence`
  in any `market_intelligence` source or test file (two comment-only mentions of `risk_manager` in
  `volatility.py`/`types.py` document where its documented volatility bounds were mirrored from —
  no import, no call, no coupling).
- No reference to `market_intelligence` anywhere in `harness.py` — the layer is not wired into the
  simulation/live runtime in this checkpoint, as instructed.
- No BUY/SELL/order-submission logic, no optimization, no portfolio-allocation logic anywhere in the package.

## 11. Commit Hash / Branch / Working Tree Status

- Branch: `ai-trader-implementation`
- Parent commit: `b1bd95314cf6d3d3bd8d07ac57bc4c3099ed0669` (Checkpoint 4)
- This checkpoint's commit hash: recorded after commit (see below)
- Working tree: clean after commit (all `market_intelligence/` files added, nothing else changed)
