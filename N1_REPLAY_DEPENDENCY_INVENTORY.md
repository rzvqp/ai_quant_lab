# N1 Replay — Exact Dependency Inventory for VE Packaging

Every entry below was found by grepping `ai_trader/n1_replay/`'s own real import statements (excluding
`tests/`), then following each real transitive import one level at a time — nothing here is assumed or
approximated. The chain has one disclosed unbounded tail (see "Known incomplete tail" below); everything
else is a closed, exact list.

## 1. External artifact

- **`ve_brain`** wheel `0.1.3`, SHA-256 `edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11`
  (`ve_brain-0.1.3-py3-none-any.whl`, 34,250 bytes). Install as-is; no modification.

## 2. This package

- **`ai_trader/n1_replay/`** in full: `__init__.py`, `engine.py`, `types.py`, `errors.py`, `identity.py`,
  `fixtures/__init__.py`, `fixtures/canonical_bars.py`. (Test files under `n1_replay/tests/` are dev-time
  only — not needed at runtime by an Alpha consumer, only by anyone re-verifying this package's own
  claims.)

## 3. Direct `ai_trader` dependencies (imported by `n1_replay/*.py` itself)

| Module | What's used | Blob SHA-1 (current) |
|---|---|---|
| `ai_trader.new_brain_bridge.raw_axes_builder` | `RawAxesBuilder` (the real, stateful N1 producer) | `d071c8cbd993cb9377b70af6b61e353d4c101966` |
| `ai_trader.live_signal_source.types` | `Bar` | `fc5d534e95d2973f5b6e66dade8119ee81fef774` |
| `ai_trader.mandate2_readiness.wheel_verification` | `PINNED_WHEEL_SHA256` (one constant) | `99066d6386f3e830408deab11265439860c36b6b` |

## 4. Transitive: `raw_axes_builder.py`'s own dependency

- **`ai_trader.structural_observer.vendor_bridge`** (blob SHA-1 `bb53680c2180a23366b9aa5a08130b4410ea6683`)
  — the bridge into the vendored detector source. This module does a `sys.path` insertion at import time
  and is NOT self-contained: it requires the actual vendored files to be physically present at
  `<repo_root>/vendor/alpha_automation_detectors/code/`.

## 5. Transitive: the vendored detector source itself (git submodule)

- **Submodule**: `vendor/alpha_automation_detectors`, tracking `ai_quant_lab-alpha-automation` branch
  `discovery-mk-matrix-v1`, **pinned commit `61cbd58c3d5da19001b125b65d669ddad54a14c4`**.
- **Files actually consumed** (flat, non-namespaced imports — `code/` itself must be on `sys.path`,
  matching `vendor_bridge.py`'s own documented reason for existing):
  - `code/market_structure.py` — `Block`, `detect_swings`, `label_structure`, `detect_breaks`
  - `code/market_state.py` — `expansion`, `compression`, `atr14`
- VE packaging Alpha needs EITHER the submodule checked out at that exact commit, OR the two flat `.py`
  files extracted at that commit (content-identical either way — the commit pin is what matters, not the
  delivery mechanism).

## 6. Transitive: `Bar`'s own dependency chain

- `ai_trader.live_signal_source.types` imports `ai_trader.signal_engine.types.Direction`
  (blob SHA-1 `16fba869be2205cad66f2117a0a799e5e6447fc2`), which in turn imports:
  - `ai_trader.market_scanner.types.DataQualityLevel`
  - `ai_trader.strategy_manager.contract.{ConfidenceLevel, Regime}`

## 7. Optional: official fixtures' own data source

- `ai_trader/n1_replay/fixtures/canonical_bars.py` imports `bos_bull_bars`/`trend_up_regime_bars` from
  **`ai_trader.new_brain_bridge.tests.conftest`** (blob SHA-1 `9bbbc242654019ccc8834ebdc03d14b4a9884354`)
  — a `tests/` module, not ordinarily a packaging dependency. This was a deliberate reuse decision (the
  CEO's own "Nu recrea și nu simplifica algoritmul" — these bar sequences are already independently
  verified against the real detectors; inventing a second sequence would just be a second unverified
  guess). **Flagging for VE's decision, not resolving unilaterally here**: either (a) package this one
  `tests/conftest.py` file alongside `n1_replay/` as-is, or (b) VE copies the two bar-sequence constant
  arrays (`BOS_BULL_HIGHS`/`_LOWS`/`_CLOSES`/`_OPENS` and the calm-prefix generation logic, ~35 lines
  total) directly into `n1_replay/fixtures/` to remove the `tests/`-module dependency entirely. Both
  preserve the exact same verified bar content; (b) only changes where the data physically lives.

## Known incomplete tail

Item 6's chain (`market_scanner.types`, `strategy_manager.contract`) was traced one level past `Bar`
and not followed further by hand — each of those two modules may have its own further imports.
**Recommendation, not resolved here**: before final packaging, VE should run a proper transitive
import-closure tool (e.g. `pydeps`/`modulegraph`, or this repo's own AST-walking convention already
used by `n1_replay/tests/test_ast_guard.py`) rooted at `ai_trader.n1_replay`, rather than trust a
hand-traced list for the full depth. Everything ABOVE this line (items 1-5, and the two named modules in
item 6) is confirmed exact via direct grep/`git hash-object`, not estimated.

## Explicitly NOT required (confirmed absent from the import graph)

- `ve_tower` (no import anywhere in `n1_replay/` or its traced dependencies — N1/Router are `ve_brain`-only)
- `ai_trader.new_brain_live`, `ai_trader.execution_orchestrator`, `ai_trader.order_manager`,
  `ai_trader.mt5_demo_execution`, `ai_trader.risk_manager_live`, `ai_trader.mt5_pnl_source`,
  `ai_trader.mandate2_readiness.broker_gate` (all statically confirmed absent by
  `n1_replay/tests/test_ast_guard.py::test_no_source_file_imports_ai_trader_live_process_packages`)
