# Mandate 4.2 — E004 fill control run. NUMBERS + mechanical label only.

Executes `STATISTICIAN_E004_FILL_CONTROL_SPEC_v1.0.md` (`ai_quant_lab` `statistician-foundation` @
`b02c5a1`), read integrally. Script `edge_research/mandate42_e004_control.py`, raw
`edge_research/mandate42_e004_control_results.json`. Static label **`CONTROL_RUN_E004_FILL`**.
**No interpretation, no conclusion — the label is read from the table, not chosen.**

**Data:** official loader v6 (`flowA_common_v6_context_derived_2026-07-27`), manifest v2.5.0. M15_v2
discovery half, **130,491 bars**, 2011-07-26 → 2021-09-03, 3 regimes (bear/bull/correction). Sealed
untouched. Regime 4 (2022-2026) excluded (SAME-WINDOW-RESAMPLED), per spec §2.

**Control (spec §1):** same 3-bar imbalance as E004 (no hour window, no first-of-session), **one instance
per trading day chosen uniformly at random, seed=7**, drawn over days in chronological order. `fill` =
re-enter zone within 50 M15 bars of formation. **E004 fill recalculated on this exact window**, with the
fill horizon confined WITHIN each regime's contiguous bars (no cross-regime leakage) — hence not reused
from Mandate 4.1's 0.662–0.736 (the recomputed figures are near-identical, confirming boundary leakage was
negligible).

## Per regime (descriptive)

| Regime | E004 fill (n) | Control fill (n) |
|---|---|---|
| bear (-42.0%) | 0.7177 (464) | 0.8471 (667) |
| bull (+86.3%) | 0.7364 (478) | 0.8569 (671) |
| corr (-17.4%) | 0.6622 (222) | 0.8416 (322) |

## Pooled + test (spec §3)

| | value |
|---|---|
| **E004 fill (pooled)** | **0.7148** (n=1164) |
| **Control fill (pooled)** | **0.8500** (n=1660) |
| Fisher exact, one-sided (H1: p_E004 > p_control) | **p = 1.000**, does NOT reject at α=0.05 |
| odds ratio (E004/control) | 0.406 |

Factual (not interpretation): the pooled E004 fill rate (0.715) is **below** the control rate (0.850),
which is why the one-sided test (H1: E004 > control) does not reject.

## Mechanical label (spec §4 pre-registered thresholds)

| Control rate (pooled) | Fisher | Label |
|---|---|---|
| ≤ 0.512 | rejects | CONFIRMED_STRUCTURAL_ANOMALY |
| (0.512 – 0.886) | any | **OBSERVED_NOT_DISTINCTIVE** ← |
| ≥ 0.886 | — | OBSERVED_BELOW_BASELINE |

Control pooled rate = **0.850**, which lies in (0.512, 0.886); Fisher does not reject.

## → **`OBSERVED_NOT_DISTINCTIVE`**

Read mechanically from the pre-registered table (control rate 0.850 ∈ (0.512, 0.886)). The final verdict
remains the Statistician's separate determination (spec §5). No interpretation drawn here.
