# POLICY — Liquidity Void — canonical schema

**candidate_id: `CAND-0004`.** Design artifact only. No execution, no data touched, no numeric parameter
chosen, no method constructed. Distinct family (price discontinuity / void).

> **Honest verdict up front: NOT CURRENTLY TESTABLE.** The void *activation* is ratified and lookahead-
> safe, but the family's *reaction* trigger (does price return to / react at the void, and in which
> direction) has **no ratified detector** — and fabricating one would violate "don't cite what you haven't
> verified exists." Part A is therefore incomplete at the trigger (fail-closed), independent of Part B.

| Field | Value |
|---|---|
| **policy_id** | `LIQUIDITY-VOID` |
| **version** | `1.0` |
| **family** | `price_discontinuity_void` (MK Module 5) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_block_void.py` | `detect_liquidity_voids`, `LiquidityVoid`, `VoidKind`; constants `VOID_SIZE_THRESHOLD=1.20` (3×cost), `BAR_SECONDS=900` (LIQUIDITY VOID definition_3, RATIFIED) | `6ec7adbfd3bbaab2d4c1e35f1ad6de2631875319bb5312e90fba572ded32b921` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_block_void.py | sha256sum`.

---

## PART A — ENTRY MECHANISM

| Field | Definition / status |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (void detection on the c→c+1 bar transition). |
| **activation** | **DEFINED, lookahead-safe.** A void at transition `c→c+1` (`detect_liquidity_voids`, RATIFIED, hybrid): **temporal** `time[c+1]-time[c] > 900s` excluding the daily maintenance window (gap≤75min ∧ hour(c)∈{20,21} UTC; weekends included) **OR** **size** `|Open[c+1]-Close[c]| > $1.20` (3×round-trip cost, derived). Both terms are known at `c+1` — no lookahead. |
| **trigger** | **⛔ FAIL-CLOSED.** The family's mechanism is a *reaction to* the void (classic thesis: the void gets filled / mean-reverts; alternative: continuation through it). Neither is buildable from a ratified primitive — `detect_level_touches` covers **only PDH/PDL**, not voids, and there is **no ratified void-reaction / void-fill detector**. Defining a return-touch rule inline would be citing a primitive that does not exist. **STOP on the trigger.** |
| **entry / invalidation / no_trade / expiry** | **Blocked downstream of the trigger** — cannot be specified until a void-reaction primitive is ratified. |
| **min_trades** | *Numeric — Statistician.* |

**PART A status: activation DEFINED; trigger onward FAIL-CLOSED.**

## PART B — RISK MANAGEMENT — **UNSPECIFIED** (same standing structural-SL gap; moot until Part A completes).

---

## Verdict — **NOT CURRENTLY TESTABLE**
Ratified, lookahead-safe **activation** exists; the **reaction trigger has no ratified primitive**. The
market object (the void) is real and detectable — what is missing is a ratified *interaction* detector.

## Handoff / spec request
- **→ Statistician, specification request:** ratify a **void-reaction/fill detector** (e.g. first re-entry
  of the void zone `[Close[c], Open[c+1]]` within a block, with a disclosed direction convention and
  consume-once rule, analogous to `detect_fvg_reactions` / `detect_level_touches`). Once ratified, this
  candidate can be completed to PARTIALLY DEFINED.
- Part B (structural risk) also → Statistician.

**Continuous production — next candidate follows.**
