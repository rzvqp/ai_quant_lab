# POLICY — Prior Week High / Low (PWH/PWL) — **v2.0 (reformulated thesis; Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0006.** Reformulated. v1.0 was NOT_CURRENTLY_TESTABLE — but the Statistician (manifest v2.7.40,
commit `e68e0cd`) proved the block was **the thesis, not the detector**: 572 weekly levels emitted, **275
touched geometrically (48.1% — healthy)**, only **6 bias-aligned (2.2% — collapse)**. The geometry works;
the collapse is entirely at the bias stage. **v2.0 removes the bias stage.** Supersedes v1.0
(`POLICY_WEEKLY_LEVELS_v1.md`, kept for the record).

## THESIS DECISION — **Route 3 chosen (no bias; direction from touch geometry)** — reason fixed BEFORE results

The Statistician offered three routes and left the choice to Alpha. **Chosen: Route 3 — no bias filter;
the level alone decides; direction comes from the level kind (touch geometry).** Logical reason,
pre-registered:

1. **The collapse is caused by requiring bias-alignment, which structurally contradicts the touch
   geometry.** A weekly HIGH is reached ONLY by price rising to it; demanding "H1+H4 bias down" for a short
   there fights the very move that produced the touch (highs touched 147 / aligned 2; lows 128 / aligned 4).
   Route 3 deletes the contradiction at its root rather than working around it.
2. **It makes CAND-0006 the weekly-period sibling of the ratified, screening-POSITIVE level-fade family** —
   CAND-0001 (PDH/PDL) and CAND-0027 (session levels) already trade level touches as fades, direction from
   kind, NO bias filter. The 22-candidate screening found **all positives use levels, all 16 negatives
   don't, zero exceptions.** Route 3 keeps PWH/PWL inside that supported class instead of inventing a new
   thesis.
3. **It stays live-valid.** Routes 1 (bias picks direction) and 2 (inverted continuation/break) either
   reintroduce a live-bias computation (repeatedly flagged NOT live-computable in this pipeline) or adopt a
   different, unscreened momentum thesis. Route 3 needs neither — pure ratified level-fade.

**Result:** the tradable population is the healthy **275 touches**, not 6. Direction is fixed by kind
(WEEKLY_HIGH → short, WEEKLY_LOW → long). Bias is not used at all.

## SESSION CROSS-CHECK (CEO-requested — "if the same problem appears at your session candidates, same cause — verify")

**Verified: it does NOT.** CAND-0026..0031 impose **no bias-eligibility filter** — direction there already
comes from the level kind / touch geometry (fade), never from a separate H1/H4 bias. So the 275→6 collapse
mechanism (touch-geometry vs bias-direction contradiction) **cannot occur** for them; the touched
population stays healthy. This matches the Statistician's pre-data prediction that the effect worsens with
period length (daily n=356 mild, weekly n=6 severe, **sessions least affected**) — and, additionally, the
session candidates were already built the collapse-free way. No change needed to 0026..0031.

## PART A — ENTRY MECHANISM — **DEFINED**

Mechanism: a prior-week extreme is a higher-timeframe support/resistance; price reaches it and reverts.
Identical grammar to PDH/PDL (CAND-0001), one period up.

| field | value · reason |
|---|---|
| **family** | `weekly_reference_levels` (MK-04) |
| **timeframes_used** | execution TF + prior-week H/L; `week_index` from the 17:00-NY `day_index` via `derive_week_index` (weekend gap > 1 calendar day → new week). |
| **activation** | `compute_prior_week_levels` (RATIFICAT / IMPLEMENTAT, D-WEEK): PWH/PWL of the prior week, `available_idx` = first bar of the current week (Q4, no lookahead), first week of a block UNCLASSIFIED (D3_bis). **Completeness gate:** trade only `completeness == "COMPLETE"` (≥5 contributing days); **PARTIAL (<5 days) → NO TRADE** (fail-closed — a <5-day "week" is not a weekly level; uses the ratified binary flag, no invented threshold). |
| **trigger** | **first touch by penetration**, over the weekly validity window `[available_idx, last bar of the current week]` (window from ratified `week_index`): WEEKLY_HIGH → `high[j] >= price`; WEEKLY_LOW → `low[j] <= price`; consumed once (D7). **No bias condition.** |
| **entry** | `next-open` after `j`. Direction = **fade the level, from kind**: WEEKLY_HIGH → **SHORT**; WEEKLY_LOW → **LONG**. |
| **invalidation** | the touch bar's extreme beyond the level is breached (Part B). |
| **no_trade_rules** | PARTIAL week → no trade; level consumed once (D7); block reset (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | touch within `[available_idx, end of current week]`; else the level expires untouched (prior-week levels are single-week). |

> **Composition disclosure (fail-closed honesty):** `detect_level_touches` deliberately SKIPS weekly
> ("altă fereastră"), so no single ratified function returns weekly touches. The trigger is **composed**
> from ratified pieces — the penetration + consume-once semantics are exactly `detect_level_touches`'
> (mirrored), and the weekly window is exactly `derive_week_index`'s week segmentation. This is the same
> composition discipline used for the session sweep (CAND-0026): ratified semantics + ratified window,
> no invented rule. If the Statistician prefers, a `detect_weekly_level_touches` can be ratified to
> replace this composition 1:1.

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = weekly level-fade. Same risk grammar as CAND-0001 (touch-bar extreme stop; opposite level target),
one period up.

| field | method · reason |
|---|---|
| **stop_loss** | **The touch bar's extreme beyond the level:** short (WEEKLY_HIGH) → `high[j]`; long (WEEKLY_LOW) → `low[j]`. Raw OHLC at `j`, known at entry (identical to CAND-0001). |
| **exit** | **The OPPOSITE prior-week level** (WEEKLY_LOW target for a short off WEEKLY_HIGH, and vice-versa), from the same `compute_prior_week_levels` set, available at entry. **Backstop / time-stop:** the **week boundary** = last bar of the current week (`week_index`), the weekly-native live-valid horizon (mirrors the day-boundary time-stop for PDH/PDL). |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond stop or target. No lookahead. **FAIL-CLOSED
check:** stop = raw OHLC; target = ratified prior-week level; time-stop = week boundary; PARTIAL week → no
trade. Composable — **method stands**.

**W-incr note (for Statistician):** PWH/PWL is the weekly member of the level-fade family; its population is
DISJOINT in period from CAND-0001 (daily) and CAND-0027 (session), so it is a distinct test, not a subset —
but the Statistician may wish to treat {CAND-0001, CAND-0027, CAND-0006} as one level-fade family for FDR.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_prior_week_levels` (D-WEEK: `days_contributing`, `completeness`), `derive_week_index`, `detect_level_touches` (penetration + D7 semantics, mirrored for the weekly window), `ReferenceLevel`, `LevelKind.WEEKLY_HIGH/LOW` | `code/institutional_levels.py` | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |

*Verify the hash, don't assume it — `git show bf02dd2:code/institutional_levels.py | sha256sum`. (Hash
identical at `0000225`/`bf02dd2`; the file was unchanged across the session-levels commit.)*

## Verdict — **DEFINED (SCREENING_BASELINE)** · reformulated thesis (Route 3, no bias) · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

## Handoff
- **→ Red Team / Statistician:** the population is the healthy 275 touches; the collapse was the bias
  filter, now removed. Optional: ratify `detect_weekly_level_touches` to replace the composed trigger 1:1.
