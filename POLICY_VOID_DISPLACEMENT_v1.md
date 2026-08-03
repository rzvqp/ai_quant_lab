# POLICY — Gap-and-Go: Displacement out of a Liquidity Void — canonical schema

**candidate_id: `CAND-0008`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. **A two-primitive INTERACTION mechanism** (operational priority: combine ratified
primitives).

> **Distinct, not a variant.** It is not CAND-0004 (a void alone, which is NOT CURRENTLY TESTABLE for lack
> of a ratified reaction trigger) — here the trigger is a **ratified displacement** on the void's
> downstream bar, which both makes it testable and defines a **different mechanism** (a gap that is
> immediately driven, not merely a gap). It is not CAND-0002 (a compression coil resolving) — the
> pre-condition here is a price discontinuity, not a low-volatility state.

> **PART A** (entry mechanism) — two ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** (risk) — no ratified structural source — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `VOID-DISPLACEMENT` |
| **version** | `1.0` |
| **family** | `discontinuity_driven_displacement` (interaction: Module 5 × market_state) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_block_void.py` | `detect_liquidity_voids`, `LiquidityVoid` (`at_idx`=c, `VoidKind`), `VOID_SIZE_THRESHOLD=1.20` — RATIFIED (definition_3) | `6ec7adbfd3bbaab2d4c1e35f1ad6de2631875319bb5312e90fba572ded32b921` |
| `code/market_state.py` | `expansion` (E010 displacement: `range>1.5×ATR14[i-1]` ∧ `|close-open|>=0.5×range`), `atr14` — ratified (Statistician v2.6.1 `2fb948f`) | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_block_void.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (two ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (void detection on the c→c+1 transition; displacement on execution bars). |
| **activation** | A **liquidity void** at transition `c→c+1` (`detect_liquidity_voids`, RATIFIED): temporal (`gap>900s`, maintenance window {20,21}h/≤75min excluded, weekends included) OR size (`|Open[c+1]-Close[c]|>$1.20`). Both terms known at bar `c+1` — no lookahead. |
| **trigger** | The void's **downstream bar** `i = c+1` is itself a **displacement/expansion bar** (`expansion[i]==True`): a gap that is immediately driven, not merely a gap. Both are known at bar `i`'s close (the void at `c<i`; the expansion on bar `i`). No lookahead. |
| **entry** | **type:** continuation of the driven gap ("gap-and-go"). **direction:** `sign(close[i]-open[i])` of the expansion bar — bullish displacement → **long**, bearish → **short**. **moment:** `entry@next-open` (open of bar `i+1`; lookahead-safe). **reference price:** the void/displacement bar `i`. |
| **invalidation** | Void (setup) before entry if the void's downstream bar is **not** an expansion (no gap-and-go), or a block boundary intervenes. |
| **no_trade_rules** | No trade unless the bar immediately after a liquidity void is a displacement. Maintenance-window pseudo-gaps are already excluded by the ratified void definition (not re-handled here). No trade across a block boundary. No trade before `atr14` is valid (first 14 bars). |
| **expiry** | Evaluated only on the void's immediate downstream bar (`c+1`); if that bar is not a displacement, the setup expires (1 bar). No fixed multi-bar window chosen. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Two ratified, lookahead-safe primitives; the void→displacement alignment is
the void's own downstream bar (index `c+1 > c`), causal. Numeric items are Statistician parameters.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

Same standing gap: fixed-ATR/RR disqualified; no ratified structural stop/exit primitive exists.

| Field | Declaration |
|---|---|
| **stop_loss** | **UNSPECIFIED.** Required: a ratified **structural** stop (e.g. the far edge of the void/displacement bar), method not value. Absent → not constructed. |
| **exit** | **UNSPECIFIED.** Ratified structural exit method absent → not constructed. |
| **management** | **UNSPECIFIED.** Dependent on the structural stop/exit → not constructed. |

---

## Verdict — **PARTIALLY DEFINED**
A distinct interaction mechanism (void → immediate displacement) with a complete, lookahead-safe entry
built from two ratified primitives; risk management unspecified for lack of a ratified structural source.

## Handoff
- **Part A → Red Team, phase A.**
- **Part B → Statistician, specification request** (structural stop/exit/management + numeric params).

**Continuous production — next candidate follows immediately.**
