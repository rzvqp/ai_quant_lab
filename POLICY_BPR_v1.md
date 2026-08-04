# POLICY — Balanced Price Range (BPR) — canonical schema

**candidate_id: `CAND-0005`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. Distinct family (overlapping opposite-polarity FVGs form a balanced range).

> **Honest verdict up front: NOT CURRENTLY TESTABLE.** The BPR *activation* (the zone) is ratified and
> lookahead-safe, but the family's *reaction* trigger at the BPR zone has **no ratified detector**
> (`detect_fvg_reactions` covers single FVG CE-50, not the BPR zone). Fail-closed on the trigger — not
> fabricated.

| Field | Value |
|---|---|
| **policy_id** | `BPR` |
| **version** | `1.0` |
| **family** | `balanced_price_range` (MK-03) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/imbalance_mechanics.py` | `count_bpr` (D-BPR), `BalancedPriceRange` (upper/lower, bullish_fvg_idx, bearish_fvg_idx), `detect_fvgs` — MK-03, CLOSED | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/imbalance_mechanics.py | sha256sum`.

---

## PART A — ENTRY MECHANISM

| Field | Definition / status |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (FVG detection + BPR overlap). |
| **activation** | **DEFINED, lookahead-safe.** A BPR = overlap of a bullish and a bearish FVG within a ≤3-bar window (D-BPR, `count_bpr` / `BalancedPriceRange`); each FVG is known from its own `confirmed_idx=i+1` (Q1), confined to its block (Q2). The BPR zone `[lower, upper]` is thus known without lookahead. |
| **trigger** | **⛔ FAIL-CLOSED.** The family's mechanism is a *reaction at the BPR zone*; `count_bpr` only counts BPRs (at overlap thresholds 0.00/0.10/0.25), and `detect_fvg_reactions` reacts to a **single FVG's CE-50**, not the BPR zone. **No ratified BPR-reaction detector exists.** Reusing the FVG CE-50 rule on a BPR would be applying a primitive outside its ratified scope. **STOP on the trigger.** |
| **entry / invalidation / no_trade / expiry** | **Blocked downstream of the trigger** — cannot be specified until a BPR-reaction primitive is ratified. |
| **min_trades** | *Numeric — Statistician.* |

## PART B — RISK MANAGEMENT — **UNSPECIFIED** (standing structural-SL gap; moot until Part A completes).

---

## Verdict — **NOT CURRENTLY TESTABLE**
Ratified, lookahead-safe **activation** (the BPR zone); the **reaction trigger has no ratified primitive**.

## Handoff / spec request
- **→ Statistician:** ratify a **BPR-reaction detector** (reaction/consumption at the BPR zone, with a
  disclosed direction convention and consume-once rule, analogous to `detect_fvg_reactions`). Then this
  candidate can be completed to PARTIALLY DEFINED. Part B (structural risk) also → Statistician.

**Continuous production — next candidate follows.**
