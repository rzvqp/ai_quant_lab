# N1 REPLAY — Full dependency closure (VE, git-only, from `21ae632`)

Resolved by AST transitive-import closure rooted at `ai_trader.n1_replay` over the tree at handoff commit
`21ae632` (runtime imports only, `tests/` excluded), plus the detector closure at the pinned submodule commit
`61cbd58c` — **not** a hand-trace. This resolves AI Trader's disclosed incomplete tail.

## Corrections found vs AI Trader's `N1_REPLAY_DEPENDENCY_INVENTORY.md`
1. **`vendor_bridge` imports FOUR detectors, not two.** AI Trader listed `market_structure` + `market_state`; the real
   imports also include **`imbalance_mechanics`** (`detect_fvgs`, `detect_fvg_reactions`) and **`order_flow`**.
2. **`order_flow` imports a fifth detector, `order_block_void`** — missed by the hand-trace.
3. **ai_trader tail closed**: the only module past `Bar`'s traced pair is **`ai_trader.market_scanner.exceptions`**
   (imported by `market_scanner.types`). No further depth.
4. **`market_structure` @ `61cbd58c` is blob `52bb1eba…`, a DIFFERENT version than ve_tower's `d734ac9a…`** — the N1
   replay detectors must be pinned to `61cbd58c`, not reused from ve_tower.

## Matrix — ai_trader.* runtime closure (14 modules), source commit `21ae632`

| module | repo | git blob SHA1 | role | imported by | runtime/test | packaged? |
|---|---|---|---|---|---|---|
| `n1_replay/__init__.py` | wp5b | `5e3d1d95…` | public surface | Alpha | runtime | vendor |
| `n1_replay/engine.py` | wp5b | `f2df0402…` | replay engine (initialize/observe/snapshot/restore/replay/reset) | `__init__` | runtime | vendor |
| `n1_replay/errors.py` | wp5b | `2eff7d33…` | reason-code errors | engine/types | runtime | vendor |
| `n1_replay/identity.py` | wp5b | `08611d44…` | EvaluationIdentity, ROUTER_VERSION, fingerprints | engine/types | runtime | vendor |
| `n1_replay/types.py` | wp5b | `c58d4001…` | N1ReplayResult, N1ReplaySnapshot | engine | runtime | vendor |
| `n1_replay/fixtures/canonical_bars.py` | wp5b | `4c13daf4…` | official bar fixtures | tests/parity | **test-only** | see VE decision |
| `n1_replay/fixtures/__init__.py` | wp5b | `2f481def…` | — | — | test-only | vendor |
| `live_signal_source/types.py` | wp5b | `fc5d534e…` | `Bar` | engine/types | runtime | vendor |
| `signal_engine/types.py` | wp5b | `16fba869…` | `Direction` | Bar | runtime | vendor |
| `market_scanner/types.py` | wp5b | `09ef6224…` | `DataQualityLevel` | Bar chain | runtime | vendor |
| `market_scanner/exceptions.py` | wp5b | `729eb8f8…` | scanner exceptions | market_scanner/types | runtime | vendor (**tail-resolved**) |
| `strategy_manager/contract.py` | wp5b | `30bb43f3…` | `ConfidenceLevel`, `Regime` | Bar chain | runtime | vendor |
| `mandate2_readiness/wheel_verification.py` | wp5b | `99066d63…` | `PINNED_WHEEL_SHA256` | identity | runtime | vendor |
| `new_brain_bridge/raw_axes_builder.py` | wp5b | `d071c8cb…` | **`RawAxesBuilder`** (stateful N1 producer) | engine | runtime | vendor |
| `structural_observer/vendor_bridge.py` | wp5b | `bb53680c…` | sys.path bridge into detectors | raw_axes_builder | runtime | vendor (adapt path) |

## Matrix — vendored detectors, source repo `ai_quant_lab-alpha-automation`, submodule pin `61cbd58c`

| module | git blob SHA1 | imports | packaged? |
|---|---|---|---|
| `code/market_structure.py` | `52bb1eba76d1dee96fae3ed5f5e434c53612176a` | (stdlib) | vendor @61cbd58c |
| `code/market_state.py` | `3f88f8c88988d2b74caf70c199907cf0871c3019` | (stdlib+numpy) | vendor @61cbd58c |
| `code/imbalance_mechanics.py` | `aa1c6d36d6395a1266b17848296a4c74631ab7c1` | market_structure | vendor @61cbd58c |
| `code/order_flow.py` | `23b0470086efa24f7b50048e973ecc90fa4a8cb7` | market_state, order_block_void | vendor @61cbd58c |
| `code/order_block_void.py` | `2b0f3f37154c4df475e1e7ef0fa782d6f808de9b` | (stdlib) | vendor @61cbd58c |

## External artifact (install as-is, NOT vendored)
- **`ve_brain` 0.1.3**, wheel SHA-256 `edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11` (already committed at
  `ve_brain/release/`). Detector commit reference `dc28e4a` (measurement-contract A2, the ve_brain SOURCE_COMMIT).

## Dependency profile
- Detectors need **numpy** (`market_state`). The ai_trader.* closure is stdlib + `ve_brain`. So `ve_n1_replay` deps =
  `ve_brain` (pinned wheel) + `numpy`. No `ve_tower`, no MT5/broker, no `ai_trader.*` at runtime for the consumer.

## VE decision — fixtures/canonical_bars.py → `new_brain_bridge.tests.conftest` (test-only)
AI Trader flagged the choice (a) package `tests/conftest.py` or (b) copy the verified bar-constant arrays into
`fixtures/`. **Decision: (b)** — copy the constant bar arrays (DATA, already independently verified against the real
detectors) into the vendored `fixtures/`, removing the `tests/`-module dependency. This copies DATA, not algorithm
(honors "Nu recrea algoritmul"), and keeps the artifact free of a `tests/` runtime edge. The fixtures remain test-only.

## Packaging plan (Etapa 2, next)
New independent artifact **`ve_n1_replay` 0.1.0**: vendor the 14 ai_trader.* runtime modules + 5 detectors
byte-identical (git blobs above) into an isolated internal namespace with a bootstrap loader (same pattern as
ve_tower's `_tower`, so the flat/bare detector imports resolve without global collision, and `ai_trader.*` imports are
remapped to the vendored package). Depends on `ve_brain` (pinned) + numpy. Public surface preserved:
`initialize/observe_closed_bar/snapshot/restore/replay/reset`. Parity A(source@21ae632) vs B(installed wheel).
