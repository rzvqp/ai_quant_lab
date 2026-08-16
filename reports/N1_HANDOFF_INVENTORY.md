# N1 HANDOFF INVENTORY — Canonical RawAxes Producer (READ-ONLY)

**Division:** Alpha Discovery (Flow B)
**Date:** 2026-08-16
**Status:** `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF` — **NOT** `MISSING_N1_GLOBALLY`
**Method:** read-only inspection of the AI Trader repo at the CEO-named commit. **No file in the AI Trader
repo was modified. No code was copied into Alpha. No local-path import was created. AI Trader's regression
was not touched.** This document is an inventory, not an integration.

---

## Correction of the prior verdict

My previous report said `ROUTER_PARITY_BLOCKED_MISSING_N1_PRODUCER` — implying no `bars → RawAxes`
producer existed anywhere. **That was wrong.** The CEO's correction is confirmed by direct inspection:
AI Trader has built and wires, on the real Candidate V2 path, exactly

```
closed bar → RawAxesBuilder → ve_brain.RawAxes → ve_brain.StrategyRouter → eligibility
```

The producer is not missing globally. It exists, is tested, and is live on AI Trader's own path. What is
missing is a **versioned replay/research interface** Alpha can consume without importing AI Trader's live
code or forking its detectors. Correct status: **`ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`**.

---

## Inventory (the fields the CEO requested)

| Field | Value |
|---|---|
| **Component** | `RawAxesBuilder` → `ve_brain.RawAxes` → `ve_brain.StrategyRouter` |
| **File** | `ai_trader/new_brain_bridge/raw_axes_builder.py` (builder); router wired in `ai_trader/new_brain_bridge/bridge.py:247` (`ve_brain.StrategyRouter(catalog).eligible(...)`) |
| **Commit** | `a98a0a4` ("Wire bridge.py exclusively to AI_TRADER_SHADOW_COST_MODEL_v1, ratify cost subcontract"), repo `ai_quant_lab-research-main`, currently HEAD |
| **Input bars** | One `ai_trader.live_signal_source.types.Bar` per call (`symbol, ts_open, ts_close, open, high, low, close, volume`), **closed bars only** (`LiveBarFeed` guarantees never a forming bar). `RawAxesBuilder` accumulates every bar into growing O/H/L/C arrays, **never reset** (matches `StructuralObserver`'s single-continuous-block convention). |
| **Output RawAxes** | `ve_brain.RawAxes(is_compressed: bool\|None, is_displacement: bool, direction: str\|None, structure: str\|None)`, derived from the FULL accumulated history as of the last bar. |
| **Dependencies** | (1) `ve_brain` external artifact (`import ve_brain`, never modified — the N1 contract + `StrategyRouter` + `applicable_regimes` live here). (2) Frozen vendored detectors via `ai_trader/structural_observer/vendor_bridge.py`: `detect_swings, label_structure, detect_breaks` (structure/direction), `expansion, compression, atr14` (displacement/compression). Vendored as a **git submodule pinned to `61cbd58c3d5da19001b125b65d669ddad54a14c4`** (`vendor/alpha_automation_detectors`, tracking `ai_quant_lab-alpha-automation` branch `discovery-mk-matrix-v1`) — the SAME detector lineage as Alpha's own repo. |
| **Configuration fingerprint** | Determined by: the vendored-detector submodule pin `61cbd58…`; `compression()` trailing window `market_state.COMPRESSION_WINDOW = 460` bars (until 460 bars accumulate, `is_compressed` is honestly `None`); `atr14` window 14; the `BreakKind → (structure, direction)` mapping table (below). No other tunables in the builder itself. |
| **N1 contract version** | `ve_brain.RAW_AXIS_SCHEMA_VERSION` (symbolic — exact string sealed in the `ve_brain` artifact; read at runtime in `bridge.py:383`, not deduced here). `ve_brain` artifact identity per the tower pin: `ve_tower 0.3.0`, `package_build_commit 6daf2aa`, `state_delivery_commit 0207ffa`; N3/N4 contract versions sourced from `HANDOFF_MANIFEST-0.3.0.json` (`ai_quant_lab-wp5b` commit `12f9241`). |
| **Router version** | `ve_brain.ROUTER_VERSION` (symbolic — read at `bridge.py:308,383`; exact string sealed in `ve_brain`). Router entrypoint: `ve_brain.StrategyRouter(catalog).eligible(axes, market_event_id, bias_direction, confidence)`. Regime gate: `ve_brain.applicable_regimes(RawAxes) → frozenset[SemanticRegime]`; any `None` axis ⇒ `UNCERTAIN`; RANGE retired (`RANGE_STRATEGY_ROUTING="DISABLED"`), never produced. |
| **Existing fixtures** | `ai_trader/new_brain_bridge/tests/conftest.py`: `bos_bull_bars()` — a hand-verified 18-bar OHLC sequence producing exactly one confirmed `BOS_BULL` at idx 14 through the REAL vendored detectors; `trend_up_regime_bars()` — 460 calm bars (to clear the compression window) + the BOS sequence, independently verified to leave the last bar at `structure="strong", direction="up", applicable_regimes=={TREND_UP}`. Plus `test_raw_axes_builder.py`, `test_bridge.py`, and `test_brain_functional_proofs.py::…applicable_regimes(axes)=={TREND_UP}` in `mandate2_readiness/tests`. |
| **Difference vs the Alpha classifier** | **Different definitions by construction** → the eligible populations do not coincide. See table below. |
| **What must be packaged for replay/research** | A **versioned, offline replay artifact** exposing `RawAxesBuilder.observe(bar) → RawAxes` (+ `applicable_regimes`) that Alpha can call over historical M15 bars, WITHOUT importing `ai_trader.*` live code or the live `Bar`/`LiveBarFeed` stack, and pinned to the same `ve_brain` artifact + detector submodule `61cbd58`. This is the artifact the Architect will request from AI Trader after Candidate V2 Final. |

---

## `BreakKind → RawAxes` mapping (the disclosed judgment call, quoted read-only)

| Break kind | structure | direction |
|---|---|---|
| `bos_bull` (confirmed continuation) | `strong` | `up` |
| `bos_bear` | `strong` | `down` |
| `choch_bull` (early reversal, unconfirmed) | `weak` | `weak_up` |
| `choch_bear` | `weak` | `weak_down` |
| no break in accumulated history | `None` | `None` (→ `UNCERTAIN`; **no synthesized RANGE**) |

---

## Difference vs the Alpha swing classifier (why parity fails today)

| Axis | Canonical N1 (`RawAxesBuilder` + `ve_brain`) | Alpha `alpha_swing_regime_v1` |
|---|---|---|
| TREND source | Latest **confirmed structural break** (`detect_breaks`: BOS/CHoCH) mapped to `structure ∈ {weak,strong}` + `direction` | Swing sequence **HH+HL → TREND_UP**, LH+LL → TREND_DOWN (MK-01) |
| Confidence gradient | BOS → `strong`/CONFIRMED end; CHoCH → `weak` end | binary regime label, no weak/strong axis |
| Compression | `compression()` over a **460-bar** trailing window; `None` until 460 bars | local compression flags, different window |
| Displacement | `expansion()` per-bar boolean | not modeled as a separate axis |
| "no signal" | honest `None` axis → `UNCERTAIN` | forces a regime label |
| Eligibility | `ve_brain.applicable_regimes(RawAxes)` + `StrategyRouter.eligible(...)` | Alpha's own regime episodes |

**Consequence:** the two produce different eligible-bar populations, so any Alpha "edge" measured on the
swing classifier is **not guaranteed reproducible on AI Trader's live regime**. Results remain strictly
diagnostic. No edge, no cost gate, no ratification, no OOS access until `N1_HANDOFF_PASS`.

---

## Path to unblock (per CEO)

1. AI Trader delivers **Candidate V2 Final**.
2. Architect requests a **versioned replay interface / artifact** for `RawAxesBuilder`.
3. On **`N1_HANDOFF_PASS`**: Alpha consumes the official producer → runs N1/Router parity → **reruns all
   relevant hypotheses** on the canonical eligibility → then applies the official cost model + MDE.

Until then Alpha stays `ALPHA_LOOP_IDLE_NO_WORK` / `ALPHA_BLOCKED_CANONICAL_N1_HANDOFF`, checkpoints
preserved, service alive.
