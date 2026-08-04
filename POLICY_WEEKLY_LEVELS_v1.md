> **SUPERSEDED by POLICY_WEEKLY_LEVELS_v2.md** — v1 was NOT_CURRENTLY_TESTABLE, fail-closed on the
> trigger. The Statistician (v2.7.40, `e68e0cd`) proved the block was the THESIS not the detector (275
> touched / 6 bias-aligned). v2 reformulates via Route 3 (no bias; direction from level kind) and composes
> the weekly touch from ratified pieces. Kept for the record; do not use.

# POLICY — Prior Week High / Low (PWH/PWL) — canonical schema

**candidate_id: `CAND-0006`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. Distinct family (weekly reference levels — a higher-timeframe analogue of CAND-0001).

> **Honest verdict up front: NOT CURRENTLY TESTABLE.** The weekly-level *activation* is ratified and
> lookahead-safe, but the weekly-level *touch/reaction* trigger has **no ratified detector** —
> `detect_level_touches` handles **only PDH/PDL** and explicitly skips weekly levels ("nivelurile
> săptămânale au altă fereastră și se sar aici"). Fail-closed on the trigger — not fabricated.

| Field | Value |
|---|---|
| **policy_id** | `PWH-PWL` |
| **version** | `1.0` |
| **family** | `weekly_reference_levels` (MK-04) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/institutional_levels.py` | `compute_prior_week_levels` (D-WEEK: `days_contributing`, `completeness` COMPLETE/PARTIAL), `derive_week_index`, `ReferenceLevel`, `LevelKind.WEEKLY_HIGH/LOW` — MK-04, ratified | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/resample_ny.py` | 17:00-NY anchor → `day_index` → `week_index` (weekend gap > 1 calendar day) | `6c6237375e344337f8ad2491f66d0cb9a9e730451595cccdea4ebe6204699650` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/institutional_levels.py | sha256sum`.

---

## PART A — ENTRY MECHANISM

| Field | Definition / status |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** execution; **prior-week** high/low from the previous week's bars, `week_index` derived from the 17:00-NY `day_index` (`derive_week_index`; a weekend gap > 1 calendar day increments the week). |
| **activation** | **DEFINED, lookahead-safe.** `compute_prior_week_levels`: PWH/PWL from the prior week, `available_idx` = first bar of the current week (Q4 analogue), first week of each block UNCLASSIFIED (D3_bis), each level carrying `days_contributing` and `completeness` (COMPLETE ≥5 / PARTIAL <5, D-WEEK). Prior week fully closed → no lookahead. |
| **trigger** | **⛔ FAIL-CLOSED.** `detect_level_touches` covers **only** PDH/PDL and skips weekly ("altă fereastră"). **No ratified weekly-level touch/reaction detector exists.** Defining a weekly-touch window inline would be citing a primitive that does not exist. **STOP on the trigger.** |
| **entry / invalidation / no_trade / expiry** | **Blocked downstream** — cannot be specified until a weekly-level touch detector is ratified. |
| **min_trades** | *Numeric — Statistician.* |

## PART B — RISK MANAGEMENT — **UNSPECIFIED** (standing structural-SL gap; moot until Part A completes).

---

## Verdict — **NOT CURRENTLY TESTABLE**
Ratified, lookahead-safe **activation** (weekly levels); the **touch/reaction trigger has no ratified
primitive** (`detect_level_touches` is PDH/PDL-only by ratified design).

## Handoff / spec request
- **→ Statistician:** ratify a **weekly-level touch/reaction detector** (the "different window" the daily
  detector explicitly defers), with a disclosed availability window and consume-once rule analogous to
  `detect_level_touches`. Then this candidate completes to PARTIALLY DEFINED. Part B also → Statistician.

**Continuous production — next candidate follows.**
