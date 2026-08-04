# POLICY — PDH/PDL × FVG-CE50 Direction-Aligned Confluence — canonical schema — **v2.0 (Part B completed)**

# 🟠 DEMO_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**One authorized pilot Part B — single variant, chosen with a logical reason BEFORE any result; no
multiple variants, no optimization.** Structural, composed from ratified primitives + raw OHLC, no new
calculation, no lookahead. Supersedes v1.0 (Part B UNSPECIFIED). Part A unchanged.

| Field | Value |
|---|---|
| **policy_id** | `LEVEL-FVG-CONFLUENCE` |
| **version** | `2.0` (DEMO_BASELINE — Part B completed; Part A unchanged from v1.0) |
| **family** | `multi_structure_confluence` (MK-04 × MK-03 via Module 7) |

## Primitive source references — W10
**No new primitive introduced by Part B** — the stop uses `LevelTouch.touch_idx` (+ raw OHLC) and
`FairValueGap.lower`/`.upper`; the target uses the **opposite** level from the same `compute_prior_day_levels`
call. All already cited in v1.0. v1.0 W10 block stands:
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/institutional_levels.py` | `compute_prior_day_levels` (both PDH & PDL), `detect_level_touches` (`LevelTouch.touch_idx`), `LevelKind` | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/imbalance_mechanics.py` | `detect_fvgs`, `detect_fvg_reactions` (CE-50), `FairValueGap` (`lower`, `upper`, `ce_50`) | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |
| `code/interactions.py` | `to_mask`, `confluence` (same-bar AND) | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/institutional_levels.py | sha256sum`.

---

## PART A — ENTRY MECHANISM — **UNCHANGED from v1.0** (see `POLICY_LEVEL_FVG_CONFLUENCE_v1.md`)
Activation = a PDH/PDL level + an FVG both active. Trigger = same-bar direction-aligned `confluence` of a
PDH/PDL touch and an FVG CE-50 touch (PDL support × bullish FVG → long; PDH resistance × bearish FVG →
short). Entry = the agreed direction, `entry@next-open`. `regimes_permitted` / `min_trades` = Statistician.

---

## PART B — RISK MANAGEMENT — **COMPLETED (DEMO_BASELINE — single variant, structural)**

**Choice rationale, fixed BEFORE any result:** fixed-ATR is non-informative (structure dominated). This is
a **two-structure confluence** family — its risk should respect **both** aligned structures. Distinct from
the single-structure candidates: the stop spans **both** floors, and the exit uses the **level** component
(which anchors a daily range). One variant only.

| Field | Method (single chosen variant) · reason |
|---|---|
| **stop_loss** | **Below BOTH structures — the deeper of the two floors.** Bullish confluence (long, PDL × bullish FVG) → stop = `min(low[touch_idx], FVG.lower)`; bearish (short) → stop = `max(high[touch_idx], FVG.upper)`. **Reason:** a confluence's edge is the *alignment* of two structures; it is not falsified until the aligned zone is **comprehensively** broken, so the stop sits beyond the deeper structural floor (the touch bar that tested the level, and the FVG's inversion edge). (`min`/`max` of two ratified prices is a selection, not a new formula.) |
| **exit** | **The opposite prior-day level** (range reversion): PDL-long → target = `PDH`; PDH-short → `PDL`. **Reason:** the confluence *contains* a PDH/PDL level, which anchors a daily range — so the opposite level is the natural structural target (this logic applies **because** a level is present, not by blind reuse). Resolves at the **first of**: stop breached · opposite level reached · same-day time-stop (`day_index` boundary). |
| **management** | **DECLARED ABSENT** (no partials/breakeven/trailing) — DEMO_BASELINE minimalism. |
| **sizing** | **Fixed 1R, risk-normalized** to `entry − stop`. No equity-%. R-metrics are sizing-invariant. |
| **min_trades** | **Deferred to the Statistician's DEMO criteria.** |

**Validity guards (structural, lookahead-safe):** no trade if the entry (`next-open`) is already beyond the
combined stop or beyond the opposite-level target. All Part-B coordinates (`low/high[touch_idx]`,
`FVG.lower/upper`, `PDH`, `PDL`, day boundary) known at entry → no lookahead.

**FAIL-CLOSED check:** buildable from ratified primitives + raw OHLC without inventing any calculation
(stop = deeper of two ratified floors; target = an already-produced opposite level; time-stop = day
boundary). Method stands.

---

## Verdict — **DEFINED (DEMO_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
## Handoff (DEMO pipeline): Red Team → Statistician (DEMO criteria) → VE → CEO → AI Trader (DEMO only).
**Other candidate production continues in parallel. No production use.**
