# POLICY — FVG Consequent-Encroachment Reaction — canonical schema

**candidate_id: `CAND-0003`.** Design artifact only. No execution, no data touched, no numeric parameter
chosen, no optimization, no variants, no SL method constructed. A **distinct family** from CAND-0001/0002:
reaction at a fair-value-gap's 50% consequent-encroachment level.

> **PART A (entry mechanism)** — ratified, lookahead-safe primitives (`imbalance_mechanics.py`, MK-03
> CLOSED) — **FULLY DEFINED.** **PART B (risk management)** — no ratified structural source — **UNSPECIFIED.**
> The market mechanism is present; only the risk-management specification is absent.

| Field | Value |
|---|---|
| **policy_id** | `FVG-CE50-REACTION` |
| **version** | `1.0` |
| **family** | `imbalance_reaction` (MK-03) |

## Primitive source references — W10 (cross-repo grounding, verifiable without co-location)

- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1`
- **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6` (full)

| source_file | primitive(s) | source_hash (sha256 of file @ commit) |
|---|---|---|
| `code/imbalance_mechanics.py` | `detect_fvgs`, `FairValueGap` (`.ce_50`, `confirmed_idx=i+1`), `detect_fvg_reactions` (Q5 consume-once, Q6 CE-50 gradient), `detect_inverse_fvgs` (Q4 invalidation) — MK-03, CLOSED (manifest v2.5.6 `00dfa6f`) | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/imbalance_mechanics.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric/selection — reserved to the Statistician; not chosen.* |
| **timeframes_used** | **M15** (FVG detection + reaction on execution bars). |
| **activation** | A 3-bar FVG exists and is **known from `confirmed_idx = i+1`** (Q1, mechanically forced, lookahead-safe): bullish `low[i+1] > high[i-1]`, zone `[high[i-1], low[i+1]]`; bearish symmetric. FVGs are **confined to their block** and do **not** survive a block boundary (Q2). `ce_50 = (upper+lower)/2`. |
| **trigger** | **First touch of the CE-50 (50% midpoint)** in the FVG's block, per `detect_fvg_reactions` step-1 (Q6): bullish = `low[j] <= ce_50` (wick reaches the midpoint from above); bearish = `high[j] >= ce_50`. **Consumed once (Q5/D7)** — no re-arm after the first CE-50 touch. |
| **entry** | **type:** reaction off the FVG acting as demand/supply. **direction:** bullish FVG → **long**, bearish FVG → **short** (the gap's own polarity). **moment:** `entry@next-open` (open of the bar after the CE-50-touch bar; lookahead-safe). **reference price:** `ce_50` (and the FVG zone `[lower, upper]`). |
| **invalidation** | Void before entry if: (a) the FVG is **consumed** (CE-50 already touched, Q5/D7); (b) the FVG has **inverted** — a decisive close beyond the far edge (bullish: `close < lower`; bearish: `close > upper`), Q4 `detect_inverse_fvgs` — so the original polarity is no longer valid; (c) block boundary reached (Q2). |
| **no_trade_rules** | No trade after consumption (Q5). No trade once the FVG has inverted (Q4 — that is a different, opposite-polarity object). No trade across a block boundary (Q2). No trade before `confirmed_idx=i+1`. |
| **expiry** | The FVG expires at its **block boundary** (Q2), or on **consumption** (first CE-50 touch, Q5), or on **inversion** (Q4), whichever first. Bar count is not a fixed constant — governed by the block/consumption/inversion events. |
| **min_trades** (per policy & per regime) | *Numeric floor — reserved to the Statistician; not chosen.* |

**PART A status: complete.** All fields defined and lookahead-safe; the CE-50 reaction gradient and
consume-once are ratified (Q5/Q6). `regimes_permitted`/`min_trades` are numeric parameters for the
Statistician.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

Same standing gap: fixed-ATR/RR disqualified; no ratified structural stop/exit primitive exists (v8.5
M_031–M_034 confirmed nonexistent).

| Field | Declaration |
|---|---|
| **stop_loss** | **UNSPECIFIED.** Required: a ratified **structural** stop (e.g. beyond the FVG's far edge / the CE-50-touch bar's invalidation), as a **method not a value**. Absent → not constructed. |
| **exit** | **UNSPECIFIED.** Ratified structural exit method absent → not constructed. |
| **management** | **UNSPECIFIED.** Dependent on the structural stop/exit → not constructed. |

---

## Verdict — **PARTIALLY DEFINED**
Entry mechanism complete and lookahead-safe (ratified CE-50 reaction gradient); risk management unspecified
for lack of a ratified structural source. Two separate things.

## Handoff
- **Part A → Red Team, phase A.**
- **Part B → Statistician, as a specification request** (structural stop/exit/management + numeric params).

**Stop-free continuous production — next candidate follows.**
