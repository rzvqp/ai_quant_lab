# N1 HANDOFF INVENTORY — Canonical RawAxes Producer (READ-ONLY, CORRECTED)

**Division:** Alpha Discovery (Flow B)
**Date:** 2026-08-16 (rev. 2 — dependency separation corrected per CEO)
**Status:** `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF` — **NOT** `MISSING_N1_GLOBALLY`
**Method:** read-only inspection of the AI Trader repo at the CEO-named commit. **No file in the AI Trader
repo was modified. No code was copied into Alpha. No local-path import was created. AI Trader's regression
was not touched.** This document is an inventory, not an integration.

---

## Producer exists (correction of the prior verdict, retained)

My first report said `ROUTER_PARITY_BLOCKED_MISSING_N1_PRODUCER` — implying no `bars → RawAxes` producer
existed anywhere. **That was wrong.** AI Trader has built and wires, on the real Candidate V2 path:

```
closed bar → RawAxesBuilder → ve_brain.RawAxes → ve_brain.StrategyRouter → applicable_regimes / eligibility
```

The producer is not missing globally — it exists, is tested, and is live on AI Trader's own path. What is
missing for Alpha is a **versioned replay/research artifact** Alpha can consume without importing AI
Trader's live code or forking its detectors. Correct status: **`ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`**.

---

## §1 — CORRECTED ARTIFACT INVENTORY (explicit ve_brain vs ve_tower separation)

The previous revision wrongly folded the `ve_tower` pin into the N1 dependency/contract lines. **Code
inspection at `a98a0a4` shows the N1 RawAxes producer imports ONLY `ve_brain` + the frozen detectors — it
never imports `ve_tower`.** `raw_axes_builder.py` imports exactly `import ve_brain` and
`from ai_trader.structural_observer.vendor_bridge import (...)`. `ve_tower` appears in `bridge.py` solely
for **N3/N4** (`run_n3`/`run_n4` via `tower_client`/`tower_bar_source`/`probability_source`) — the
probability/EV feed into N6, a SEPARATE subsystem the RawAxes/Router path does not touch.

### ve_brain — the N1/Router/EV/N6 artifact
| Field | Value |
|---|---|
| version | `0.1.3` |
| build / source | `a1d2a6d` |
| validated_core | `fbc0f20` |
| N1 contract | `n1-additive-raw-axes-v1` |
| Router | `router-v1` |
| wheel SHA256 | `edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11` |
| role | `RawAxes` · `StrategyRouter` · EV · N6 |

### ve_tower — the N3/N4 artifact (NOT an N1 dependency)
| Field | Value |
|---|---|
| version | `0.3.0` |
| build | `6daf2aa` |
| state | `0207ffa` |
| role | **exclusively N3 / N4** (`run_n3` / `run_n4`) |
| N1 dependency? | **NO** — no demonstrated code dependency from the RawAxes producer. Verified: `raw_axes_builder.py` does not import `ve_tower`; `ve_tower` is reached only via the N3/N4 probability path in `bridge.py`, which is downstream of and independent from RawAxes production. |

### RawAxesBuilder — the producer (AI Trader owns it)
| Field | Value |
|---|---|
| owner | AI Trader |
| repo / commit | `ai_quant_lab-research-main` @ `a98a0a4` |
| file | `ai_trader/new_brain_bridge/raw_axes_builder.py` (router wired `bridge.py:247`) |
| detector pin | `structural_observer.vendor_bridge` @ submodule `61cbd58c3d5da19001b125b65d669ddad54a14c4` (`vendor/alpha_automation_detectors`, branch `discovery-mk-matrix-v1`) |

---

## §2 — N1 producer contract (the fields the CEO requested)

| Field | Value |
|---|---|
| **Component** | `RawAxesBuilder` → `ve_brain.RawAxes` → `ve_brain.StrategyRouter` |
| **File** | `ai_trader/new_brain_bridge/raw_axes_builder.py`; router `bridge.py:247` (`ve_brain.StrategyRouter(catalog).eligible(...)`) |
| **Commit** | `a98a0a4` (repo `ai_quant_lab-research-main`, currently HEAD) |
| **Input bars** | one `ai_trader.live_signal_source.types.Bar` per call (`symbol, ts_open, ts_close, open, high, low, close, volume`), **closed bars only**; accumulated into growing O/H/L/C arrays, **never reset** |
| **Output RawAxes** | `ve_brain.RawAxes(is_compressed: bool\|None, is_displacement: bool, direction: str\|None, structure: str\|None)` from the full accumulated history as of the last bar |
| **N1 dependencies (real, in code)** | (1) `ve_brain` 0.1.3 (`RawAxes`, `StrategyRouter`, `applicable_regimes`); (2) frozen detectors via `vendor_bridge` @ `61cbd58` (`detect_swings, label_structure, detect_breaks`; `expansion, compression, atr14`). **NOT ve_tower.** |
| **Configuration fingerprint** | detector submodule pin `61cbd58`; `compression()` window `market_state.COMPRESSION_WINDOW = 460`; `atr14` window 14; the `BreakKind → (structure, direction)` map (below). No other tunables in the builder. |
| **N1 contract version** | `n1-additive-raw-axes-v1` (ve_brain 0.1.3). Read at runtime as `ve_brain.RAW_AXIS_SCHEMA_VERSION` (`bridge.py:383`). |
| **Router version** | `router-v1` (ve_brain 0.1.3). Read as `ve_brain.ROUTER_VERSION` (`bridge.py:308,383`). Regime gate `ve_brain.applicable_regimes(RawAxes) → frozenset[SemanticRegime]`; any `None` axis ⇒ `UNCERTAIN`; RANGE retired (`RANGE_STRATEGY_ROUTING="DISABLED"`), never produced. |
| **Existing fixtures** | `ai_trader/new_brain_bridge/tests/conftest.py`: `bos_bull_bars()` (18-bar OHLC → one confirmed `BOS_BULL` at idx 14 through the REAL vendored detectors); `trend_up_regime_bars()` (460 calm bars + BOS → last bar `structure="strong", direction="up", applicable_regimes=={TREND_UP}`). Plus `test_raw_axes_builder.py`, `test_bridge.py`, `mandate2_readiness/tests/test_brain_functional_proofs.py`. **These are AI Trader's fixtures; the authoritative fixture OUTPUTS arrive WITH the N1 artifact — Alpha does not invent them.** |
| **Diff vs Alpha classifier** | confirmed BOS/CHoCH break-mapping vs Alpha swing HH+HL → different eligible populations by construction (table below) |
| **What must be packaged** | a versioned offline replay artifact exposing `RawAxesBuilder.observe(bar) → RawAxes` (+ `applicable_regimes`, `StrategyRouter`) callable over historical M15 bars WITHOUT importing `ai_trader.*` live code, pinned to ve_brain 0.1.3 + detector submodule `61cbd58` |

### `BreakKind → RawAxes` mapping (disclosed judgment call, quoted read-only)
| Break kind | structure | direction |
|---|---|---|
| `bos_bull` | `strong` | `up` |
| `bos_bear` | `strong` | `down` |
| `choch_bull` | `weak` | `weak_up` |
| `choch_bear` | `weak` | `weak_down` |
| no break in history | `None` | `None` (→ `UNCERTAIN`; no synthesized RANGE) |

### Difference vs the Alpha swing classifier (why parity fails today)
| Axis | Canonical N1 | Alpha `alpha_swing_regime_v1` |
|---|---|---|
| TREND source | latest confirmed break (BOS/CHoCH) → `structure∈{weak,strong}`+`direction` | swings HH+HL→TREND_UP, LH+LL→TREND_DOWN |
| Confidence gradient | BOS→strong, CHoCH→weak | binary, no weak/strong axis |
| Compression | 460-bar `compression()`; `None` until 460 bars | local flags, different window |
| Displacement | per-bar `expansion()` boolean | not a separate axis |
| "no signal" | honest `None` → `UNCERTAIN` | forces a label |
| Eligibility | `applicable_regimes` + `StrategyRouter.eligible` | Alpha regime episodes |

**Consequence:** different eligible-bar populations ⇒ any Alpha "edge" on the swing classifier is not
guaranteed reproducible on AI Trader's live regime. Results strictly diagnostic. No edge, no cost gate, no
ratification, no OOS until `N1_HANDOFF_PASS`.

---

## Path to unblock (per CEO)
1. AI Trader delivers **Candidate V2 Final**.
2. Architect requests a **versioned replay interface / artifact** for `RawAxesBuilder`.
3. On **`N1_HANDOFF_PASS`**: Alpha consumes the official producer → runs N1/Router parity → reruns all
   relevant hypotheses (see `N1_RERUN_MANIFEST.json`) → then applies the official cost model + MDE → new
   shortlist.

Until then Alpha stays `ALPHA_LOOP_IDLE_NO_WORK` / `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`, checkpoints
preserved, service alive. AI Trader keeps absolute CPU priority.

**Companion artifacts (this delivery):**
- `edge_research/tests/test_n1_acceptance.py` — N1 acceptance suite, explicitly `BLOCKED_ON_N1_ARTIFACT`.
- `reports/N1_RERUN_MANIFEST.json` (+ `.md`) — all 355 hypotheses flagged for canonical rerun.
- `reports/IMPLEMENTATION_QUEUE_SPECS.md` — 5 declarative mechanism specs, spec-only, m NOT incremented.
