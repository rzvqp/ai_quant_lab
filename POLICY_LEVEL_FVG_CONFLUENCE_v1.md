# POLICY — PDH/PDL × FVG-CE50 Direction-Aligned Confluence — canonical schema

**candidate_id: `CAND-0007`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. **A multi-primitive INTERACTION mechanism** (per the operational priority: prefer
mechanisms from combining two or more ratified primitives over 1:1 single-primitive policies).

> **Not a duplicate, not a parametric variant.** CAND-0001 (PDH/PDL reaction alone) and CAND-0003 (FVG
> CE-50 reaction alone) are single-primitive. This candidate is their **confluence** — a distinct
> *confirmation* hypothesis: a reaction is taken **only when both structures coincide and agree in
> direction**. The mechanism is the interaction, not either primitive.

> **PART A** (entry mechanism) — three ratified, lookahead-safe primitives combined by the ratified
> confluence locator — **FULLY DEFINED.** **PART B** (risk) — no ratified structural source — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `LEVEL-FVG-CONFLUENCE` |
| **version** | `1.0` |
| **family** | `multi_structure_confluence` (interaction: MK-04 × MK-03 via Module 7) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/institutional_levels.py` | `compute_prior_day_levels`, `detect_level_touches` (PDH/PDL touch, consume-once D7), `LevelKind` — MK-04 | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/imbalance_mechanics.py` | `detect_fvgs`, `detect_fvg_reactions` (CE-50 touch Q6, consume-once Q5), `FairValueGap.ce_50`, `FVGKind` — MK-03 | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |
| `code/interactions.py` | `to_mask`, `dilate` (trailing only, `after=0`, strictly causal), `confluence` (same-bar AND) — Module 7, ratified GENERIC locator (Statistician v2.6.1 `2fb948f`) | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify (example):* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/interactions.py | sha256sum`.

**Module-7 ruling honored:** `interactions.py` is a generic locator; the specific combination below is a
*hypothesis* choice, which this policy pre-registers (the module explicitly sanctions reusing it "ca
mecanism de detecție" inside a separately pre-registered hypothesis). No trade logic lives in the module.

---

## PART A — ENTRY MECHANISM (three ratified primitives, combined) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (levels, FVGs, and confluence all on execution bars). |
| **activation** | Both structures active and known without lookahead: (1) a PDH/PDL level (`compute_prior_day_levels`, `available_idx`=current day's first bar, D3_bis block reset); (2) a 3-bar FVG (`confirmed_idx=i+1`, block-confined). |
| **trigger** | **Direction-aligned confluence** at the same bar (`interactions.confluence`): the bar is BOTH a PDH/PDL touch (`detect_level_touches`) AND an FVG CE-50 touch (`detect_fvg_reactions`) that **agree in direction** — `confluence([support_mask, bullish_fvg_ce50_mask])` for longs (PDL support + bullish FVG demand), symmetric `confluence([resistance_mask, bearish_fvg_ce50_mask])` for shorts. A trailing tolerance is available **only** via `dilate(before=k, after=0)` (strictly causal); a symmetric window (`after>0`) would be lookahead and is **excluded** (fail-closed). Each constituent is consume-once (D7/Q5). |
| **entry** | **type:** confirmed reaction at the confluence. **direction:** the agreed direction — **long** (PDL support × bullish FVG), **short** (PDH resistance × bearish FVG). **moment:** `entry@next-open` (bar after the confluence bar; lookahead-safe). **reference price:** the confluence zone (overlap of the level and the FVG). |
| **invalidation** | Void before entry if EITHER constituent is consumed (level touched already, D7; FVG CE-50 already touched, Q5), the FVG has inverted (Q4), or a block boundary is crossed (D3_bis / Q2). **No confluence, or direction disagreement → no setup.** |
| **no_trade_rules** | No trade without same-bar (or trailing-dilated) confluence. No trade when the FVG polarity and the level side disagree (e.g. bullish FVG at PDH resistance). No trade after either constituent is consumed/inverted. No trade across a block boundary. No trade on the first day of a block (D3_bis). No trade before `confirmed_idx=i+1`. |
| **expiry** | The setup expires when EITHER constituent expires — at its block boundary, or on consumption, or (FVG) on inversion — whichever first. Governed by events, not a fixed bar count. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Three ratified, lookahead-safe primitives combined by the ratified confluence
locator; same-bar confluence and trailing-only dilation keep it causal. Numeric items (`regimes_permitted`,
`min_trades`, the trailing dilation tolerance `k`) are parameters for the Statistician — the interaction
mechanism is fully specified around them.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

Same standing gap: fixed-ATR/RR disqualified; no ratified structural stop/exit primitive exists.

| Field | Declaration |
|---|---|
| **stop_loss** | **UNSPECIFIED.** Required: a ratified **structural** stop (e.g. beyond the confluence zone / the FVG far edge / the level), method not value. Absent → not constructed. |
| **exit** | **UNSPECIFIED.** Ratified structural exit method absent → not constructed. |
| **management** | **UNSPECIFIED.** Dependent on the structural stop/exit → not constructed. |

---

## Verdict — **PARTIALLY DEFINED**
A richer, distinct interaction mechanism (level × FVG confluence) with a complete, lookahead-safe entry
built from three ratified primitives; risk management unspecified for lack of a ratified structural source.

## Handoff
- **Part A → Red Team, phase A** (confluence/confirmation mechanism; check the direction-alignment and the
  trailing-only tolerance).
- **Part B → Statistician, specification request** (structural stop/exit/management + numeric params,
  incl. the trailing dilation tolerance `k`).

**Continuous production — next candidate follows.**
