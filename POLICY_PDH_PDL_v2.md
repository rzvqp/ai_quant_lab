# POLICY — PDH/PDL (Previous Day High / Low) — canonical schema — **v2.0 (Part B completed)**

# 🟠 DEMO_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**One authorized pilot policy (CEO, DEMO_BASELINE).** Part B is completed with **a single variant, chosen
with a logical reason BEFORE any result was seen — no multiple variants tested, no optimization, no search
for a best SL/TP.** Built only from ratified, verifiable primitives + raw OHLC; **no new calculation
invented, no lookahead.** Supersedes v1.2 (Part B was UNSPECIFIED there); Part A is unchanged.

Grounded in `code/institutional_levels.py` (MK-04): `compute_prior_day_levels`, `detect_level_touches`
(D7), `LevelKind`, `ReferenceLevel`, `LevelTouch`. Exploratory figures (winrate 0.435 @ n=356) carry **no
privileged status**.

| Field | Value |
|---|---|
| **policy_id** | `PDH-PDL` |
| **version** | `2.0` (DEMO_BASELINE — Part B completed; Part A unchanged from v1.2) |
| **family** | `institutional_reference_levels` (MK-04) |

## Primitive source references — W10 (cross-repo grounding)

**No new primitive is introduced by Part B** — the structural stop uses `LevelTouch.touch_idx` (already
cited) + raw touch-bar OHLC; the structural target uses the **opposite** level from the *same*
`compute_prior_day_levels` call (both PDH and PDL are already produced). The v1.2 W10 block stands:

- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/institutional_levels.py` | `compute_prior_day_levels` (produces **both** PDH and PDL), `detect_level_touches` (`LevelTouch.touch_idx`), `LevelKind`, `ReferenceLevel`, `LevelTouch` (MK-04) | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/resample_ny.py` | 17:00-NY DST-aware day anchor → `day_index` (also the same-day time-stop boundary) | `6c6237375e344337f8ad2491f66d0cb9a9e730451595cccdea4ebe6204699650` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/institutional_levels.py | sha256sum`.

---

## PART A — ENTRY MECHANISM — **UNCHANGED from v1.2, FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15**; prior-day high/low from the previous session's M15 bars, grouped by `day_index` (17:00-NY anchor). Bars-per-day counted, never assumed. **No fixed-ATR distance anywhere.** |
| **activation** | PDH and PDL activate for the current day, all known at the current day's first bar: (1) not the first day of a block (D3_bis); (2) prior session fully closed, `available_idx`=first bar of current day (Q4); (3) `PDH=max(high)`, `PDL=min(low)` over the prior day (`compute_prior_day_levels`). |
| **trigger** | **First touch** (`detect_level_touches`): PDH `high[j]>=PDH` (resistance); PDL `low[j]<=PDL` (support); window `[available_idx, current day's last bar]`, same block; **consumed once** (D7/Q5). |
| **entry** | **type:** reaction off the level (PDH resistance, PDL support). **direction:** PDH → **short**, PDL → **long**. **moment:** `entry@next-open` (open of the bar after the touch bar `touch_idx`). **reference price:** the level. |
| **invalidation** | Void before entry if the level is consumed (D7), the day ends before a touch, or it is the first day of a block (D3_bis). |
| **no_trade_rules** | No trade on the first day of a block; weekly levels excluded; no second trade on a consumed level; no trade if the prior level never matured. |
| **expiry** | Setup dies at the current day's end (`day_index` boundary) or first touch, whichever first. |
| **min_trades** | *Deferred to the Statistician's DEMO criteria (statistical-power floor, not a mechanism parameter).* |

---

## PART B — RISK MANAGEMENT — **COMPLETED (DEMO_BASELINE — single variant, structural)**

**Choice rationale, fixed BEFORE any result:** the lab's own evidence is that a **fixed-ATR** stop is
non-informative here — an identical 0.378–0.385 winrate across six distinct mechanisms with <50% overlap,
i.e. **structure dominated the signal**. The DEMO_BASELINE therefore uses a **purely structural** risk
model, anchored to the mechanism's own objects (the touch bar and the prior-day range), composed from
already-ratified primitives + raw OHLC — **no ATR distance, no fixed RR, no new calculation, one variant
only.**

| Field | Method (single chosen variant) · reason |
|---|---|
| **stop_loss** | **The extreme of the touch bar** (`LevelTouch.touch_idx`): PDL-long stop = `low[touch_idx]`; PDH-short stop = `high[touch_idx]`. **Reason:** the entry thesis is "the level holds"; its structural falsification is a breach of the very wick that tested the level. This is an event-anchored **level**, not a distance — exactly the structural direction the winrate evidence points to. (Ratified `touch_idx` + raw OHLC; no new calc.) |
| **exit** | **The opposite prior-day level** (range reversion): PDL-long target = `PDH`; PDH-short target = `PDL`. **Reason:** PDH/PDL is a **range** mechanism — a reaction off one extreme naturally targets the other; both levels come from the *same* `compute_prior_day_levels` call, so this is structural (a level), not a fixed RR. The trade resolves at the **first of**: stop breached · opposite level reached · **same-day time-stop** at the current day's close (`day_index` boundary, the mechanism's own horizon). |
| **management** (partials / breakeven / trailing) | **DECLARED ABSENT.** No partials, no breakeven, no trailing. **Reason:** DEMO_BASELINE minimalism — a single structural stop and a single structural target; management would add chosen parameters and an optimization surface, which this pilot explicitly excludes. |
| **sizing** | **Fixed 1R, risk-normalized** to the structural stop distance (position sized so `entry − stop` = 1R). **No equity-percentage.** **Reason:** all reported R-metrics are sizing-invariant, and a fixed equity-% (e.g. the 5% previously proposed) is a CEO-deauthorized, unvalidated parameter; 1R normalization avoids it. |
| **min_trades** | **Deferred to the Statistician's DEMO criteria** (the mandate assigns DEMO criteria to the Statistician). A statistical-power floor, not chosen here. |

**Part B validity guards (structural, lookahead-safe), added with the stop/target:**
- If the entry (next-open) is already **beyond the structural stop** (PDL-long: `open[touch_idx+1] <=
  low[touch_idx]`; PDH-short symmetric) → **no trade** (no positive risk / already stopped at entry).
- If the entry is already **beyond the target** (past the opposite level) → **no trade** (target already
  reached at entry).
- All Part-B coordinates (`low/high[touch_idx]`, `PDH`, `PDL`, day boundary) are known at entry → **no
  lookahead**.

**FAIL-CLOSED check:** this Part B is buildable from ratified primitives + raw OHLC **without inventing any
calculation** (stop = a bar extreme; target = an already-produced level; time-stop = an existing day
boundary). No new formula, no unratified module. The method therefore stands — the earlier "no ratified
structural-SL primitive" gap is resolved by **composition of existing primitives**, not by a new one.

---

## Verdict — **DEFINED (DEMO_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

Both parts complete: entry mechanism (Part A) unchanged and lookahead-safe; risk management (Part B) a
single structural variant chosen before results, from ratified primitives, no invention, no lookahead.

## Handoff (DEMO pipeline)
- **Red Team** — safety + lookahead audit (esp. the Part-B entry-vs-stop/target validity guards).
- **Statistician** — defines the DEMO criteria (incl. `min_trades`, `regimes_permitted`, cost convention).
- **Validation Engine** — executability check.
- **CEO** — approval. **AI Trader** — runs on DEMO only.

**This is the single authorized DEMO_BASELINE pilot. Other candidate production continues in parallel and
is unaffected. No production use.**
