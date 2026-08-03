# POLICY — Level Break-and-Drive: PDH/PDL touch × Displacement — canonical schema

**candidate_id: `CAND-0009`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. **A two-event INTERACTION mechanism** combining ratified primitives.

> **Distinct, not a variant, and directionally OPPOSITE to CAND-0001.** CAND-0001 trades the *reversal*
> off a PDH/PDL (touch → reject). Here the level touch **coincides with a displacement bar**, i.e. the
> level is broken *with conviction* → continuation **through** the level. Same object (PDH/PDL), opposite
> direction thesis, gated by a second ratified event (displacement) — a different mechanism, not a
> parametric variant.

> **PART A** (entry mechanism) — three ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** (risk) — no ratified structural source — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `LEVEL-BREAK-DRIVE` |
| **version** | `1.0` |
| **family** | `level_break_with_displacement` (interaction: MK-04 × market_state via Module 7) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/institutional_levels.py` | `compute_prior_day_levels`, `detect_level_touches` (PDH/PDL touch, D7), `LevelKind` — MK-04 | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/market_state.py` | `expansion` (E010 displacement), `atr14` — ratified (Statistician v2.6.1 `2fb948f`) | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |
| `code/interactions.py` | `to_mask`, `confluence` (same-bar AND) — Module 7, ratified generic locator | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/market_state.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (three ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (levels, displacement, confluence on execution bars). |
| **activation** | A PDH/PDL level active and known (`compute_prior_day_levels`, `available_idx`=current day's first bar, D3_bis block reset). |
| **trigger** | **Same-bar confluence** (`interactions.confluence`) of a PDH/PDL **touch** (`detect_level_touches`) AND a **displacement** on that same bar (`expansion[i]==True`) whose direction is **through** the level: PDH touched with a bullish displacement (break up), PDL touched with a bearish displacement (break down). `confluence([level_touch_mask, expansion_mask])`, same bar — no lookahead. |
| **entry** | **type:** break-and-drive continuation **through** the level. **direction:** the displacement direction — PDH break → **long**, PDL break → **short** (opposite to the CAND-0001 reversal thesis). **moment:** `entry@next-open` (bar after the confluence bar; lookahead-safe). **reference price:** the broken level / displacement bar. |
| **invalidation** | Void before entry if the level touch is **not** accompanied by a same-bar displacement (that is the CAND-0001 reversal case, not this one), if the level is already consumed (D7), or if a block boundary intervenes. |
| **no_trade_rules** | No trade on a level touch without a coincident displacement. No trade when the displacement direction contradicts a break (e.g. PDH touched with a bearish displacement = rejection, not break — belongs to CAND-0001's thesis, excluded here). No trade after the level is consumed (D7). No trade on the first day of a block (D3_bis). |
| **expiry** | The setup expires at the level's consumption (D7) or block boundary (D3_bis); the confluence itself is a single-bar event. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Same-bar confluence of two ratified events plus a ratified level primitive;
all lookahead-safe. Numeric items are Statistician parameters.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

Same standing gap: fixed-ATR/RR disqualified; no ratified structural stop/exit primitive exists.

| Field | Declaration |
|---|---|
| **stop_loss** | **UNSPECIFIED.** Required: a ratified **structural** stop (e.g. back inside the broken level / the displacement bar's origin), method not value. Absent → not constructed. |
| **exit** | **UNSPECIFIED.** Ratified structural exit method absent → not constructed. |
| **management** | **UNSPECIFIED.** Dependent on the structural stop/exit → not constructed. |

---

## Verdict — **PARTIALLY DEFINED**
A distinct interaction mechanism (level break confirmed by displacement, opposite-direction to the level
reversal) with a complete, lookahead-safe entry from three ratified primitives; risk management
unspecified for lack of a ratified structural source.

## Handoff
- **Part A → Red Team, phase A** (note the direction is break-continuation, not reversal — the two-event
  gate is what separates it from CAND-0001).
- **Part B → Statistician, specification request** (structural stop/exit/management + numeric params).

**Continuous production — next candidate follows immediately.**
