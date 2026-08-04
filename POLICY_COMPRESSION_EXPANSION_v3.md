# POLICY — Compression-to-Expansion Breakout — **v3.0 (live-valid exit horizon)**

# 🟠 DEMO_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0002.** Correction only: the v2.0 exit's third term was a **discovery-only "block boundary"** —
which does not exist on a forward-going live account (a block is a construction of the discovery regime
segments), so that leg would never fire and a trade could stay open forever. Replaced with a **real-time
horizon**. Single variant, family-native, chosen with a logical reason; no optimization. **Part A and the
rest of Part B (stop, sizing, mgmt) unchanged from v2.0.** Supersedes v2.0 (kept, marked superseded).
**No new primitive** — the horizon constant is already-ratified.

## Primitive source references — W10
- **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6` · **branch** `discovery-mk-matrix-v1` · repo `.../ai_quant_lab-alpha-automation.git`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/market_state.py` | `expansion`, `atr14`, `COMPRESSION_WINDOW=460` (the setup's own volatility timescale, reused as the live hold horizon) | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

## PART B — exit (corrected); all other fields unchanged from v2.0
| Field | Method · reason |
|---|---|
| **stop_loss** | *(unchanged)* opposite extreme of the expansion bar `i` (`low[i]`/`high[i]`). |
| **exit** | **First opposing-direction expansion bar** (family-native momentum reversal) **OR** a **`COMPRESSION_WINDOW = 460`-bar time-stop** counted forward from entry. **Reason:** a compression→expansion setup is *defined* over a 460-bar volatility window, so its natural bounded horizon is that same timescale — real-time (count 460 bars from entry, no block, no future knowledge), and deliberately **not** the daily-level horizon (expansion ≠ daily-level). Replaces the discovery-only block boundary. |
| **management** | *(unchanged)* DECLARED ABSENT. |
| **sizing** | *(unchanged)* fixed 1R, no equity-%. |
| **min_trades** | *(unchanged)* deferred to the Statistician. |

**FAIL-CLOSED check:** the horizon is composable live from the ratified `COMPRESSION_WINDOW` (a forward bar
count); method stands. No lookahead.

## Verdict — **DEFINED (DEMO_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
