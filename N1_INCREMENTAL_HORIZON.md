# N1 incremental replay — dependency-horizon proof (from code, not W=500 guessed)

Root cause of O(n²): `RawAxesBuilder.observe(bar)` (blob `d071c8cb`) appends the bar to growing arrays and re-runs
`detect_swings`/`detect_breaks`/`expansion`/`compression` over the **entire** `Block(0, len)` each call, using only the
last bar's `exp`/`comp` and the **latest** break. The per-bar work grows with history → O(n²)+.

Each axis's true lookback, read from the vendored detectors (@`61cbd58c`):

| axis / detector | source (blob) | mathematical lookback | warmup | persistent state | bounded? | can old history be dropped? |
|---|---|---|---|---|---|---|
| `atr14` | market_state `3f88f8c8` | trailing 14 (`tr.rolling(14)`) | 14 | rolling window | **bounded 14** | yes, beyond 14 |
| `is_displacement` (`expansion`) | market_state `3f88f8c8` | `range[i] > 1.5·atr14[i-1]` + body ⇒ bars `[i-15, i]` | 15 | rolling | **bounded ≈15** | yes, beyond 15 |
| `is_compressed` (`compression`) | market_state `3f88f8c8` | `ln(h/l) ≤ P10` over trailing `[i-459, i]`; `valid` until `i≥459` | **460** | rolling window | **bounded 460** | yes, beyond 460 |
| swing detection (`detect_swings`, k=2) | market_structure `52bb1eba` | fractal window `[idx-2, idx+2]` = 5 bars/swing; confirmed at `idx+2` | 5 | swing list (accumulates) | per-swing bounded 5 | swing DETECTION yes; swing LIST feeds breaks (below) |
| `label_structure` | market_structure `52bb1eba` | vs last same-type swing in block | — | `last_high`/`last_low` (1 each) | **UNBOUNDED** (last swing can be old) | NO — but state is O(1) |
| `structure` + `direction` (`detect_breaks`) | market_structure `52bb1eba` | `live_hh/ll/hl/lh` = last UNCONSUMED CONFIRMED swing (arbitrarily old) + `consumed` set + latest break persists until superseded | — | 4 label stacks + consumed set + latest break | **UNBOUNDED** | **NO — must not truncate** |

**Causality (verified):** every detector output at bar `i` depends only on bars `≤ i` (`compression` window is
trailing "niciodată viitor"; `expansion` uses `atr14[i-1]`; `detect_breaks` uses swings `confirmed_idx < c` and a
`consumed` set that only accumulates forward). So a single forward pass reproduces the per-bar outputs exactly — no
lookahead.

## Design determination (per §2)

- **Bounded axes** (`is_compressed`, `is_displacement`, `atr14`): a rolling trailing buffer of **`HISTORY_HORIZON = 460`**
  bars (= `COMPRESSION_WINDOW`, the max bounded lookback) is sufficient. `expansion`/`compression` are called on the
  buffer via the UNMODIFIED functions → byte-identical. `HISTORY_HORIZON_VERSION = "n1-history-horizon-v1"`, horizon
  `460`, safety margin explicit (no bars older than 460 can affect these axes — proven above, not guessed).
- **Unbounded axes** (`structure`, `direction`): **NOT truncated.** Maintained by SUFFICIENT INCREMENTAL STATE that
  replays the ratified `detect_swings`/`label_structure`/`detect_breaks` FORWARD LOGIC once (O(1) amortized/bar): the
  accumulating swing list, per-label `last_high/last_low`, the 4 `live_*` label stacks, the `consumed` set, and the
  persistent latest break. This is an "implementare incrementală demonstrat echivalentă" (§1) — proven byte-equal to
  0.1.0 by exhaustive parity, NOT a windowed approximation.
- **Note:** `W=500`/`W=800` (Alpha's empirical parity) are ≥ 460 so they happen to also cover the bounded axes, but
  they do NOT bound `structure/direction`; the horizon `460` is the code-derived bounded-axis figure and is bound into
  the evaluation/configuration identity. The unbounded axes rely on state, not `W`.

Complexity after the fix: rolling exp/comp O(460)/bar + incremental swing/break O(1)/bar ⇒ **O(n) total, bounded
marginal cost** (no O(n) growth per bar). This is delivered as `replay_batch` (single O(n) forward pass = the canonical
ledger) and a streaming `N1IncrementalReplayEngine` sharing the same incremental core, with snapshot carrying the
persistent state. Vendored detectors stay byte-identical; RawAxes are assembled exactly as `RawAxesBuilder` does and
fed through the UNMODIFIED result-builder, so all downstream fingerprints/identity match 0.1.0.
