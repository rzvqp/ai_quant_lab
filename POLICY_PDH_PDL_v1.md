# POLICY — PDH/PDL (Previous Day High / Low) — canonical schema

**Design artifact only. No execution, no data touched, no numeric parameter chosen, no optimization, no
variants, no SL method constructed.** First candidate from the operational pipeline.

> **Read this first — the two parts are independent and must not be conflated.**
> **PART A (entry mechanism)** — context, regime, trigger, entry, invalidation, no-trade, expiry — is
> built on **ratified primitives in the repo** and is **fully DEFINED**.
> **PART B (risk management)** — stop_loss, exit, management — has **no ratified structural source** and
> is **UNSPECIFIED**.
> **The market mechanism is present and complete. What is absent is the risk-management *specification* —
> a distinct thing.** A PARTIALLY DEFINED verdict here means the entry mechanism is complete and the risk
> layer is not; it does **not** mean the market edge is missing.

Grounded in the ratified detectors in `code/institutional_levels.py` (MK-04): `compute_prior_day_levels`,
`compute_prior_week_levels`, `detect_level_touches` (consumption D7), `LevelKind`, `ReferenceLevel`,
`LevelTouch`. Decision IDs cited are those detectors' own (D3_bis, Q4, Q5/D7, 17:00-NY anchor). Exploratory
figures (winrate 0.435 @ n=356, expectancy_$ +0.334, gross edge +0.534, 4/4 sessions, 6/7 years) carry
**no privileged status** and are not relied on here.

| Field | Value |
|---|---|
| **policy_id** | `PDH-PDL` |
| **version** | `1.2` (W10: cross-repo primitive-source references added; no mechanism change) |
| **family** | `institutional_reference_levels` (MK-04) |

## Primitive source references — W10 (cross-repo grounding, verifiable without co-location)

The cited primitives live on a **different branch** than this policy (which is on `alpha-automation-v1`).
Each is pinned below so a consumer can verify grounding without the files being co-located.

- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1`
- **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6` (full)

| source_file | primitive(s) | source_hash (sha256 of file @ commit) |
|---|---|---|
| `code/institutional_levels.py` | `compute_prior_day_levels`, `detect_level_touches`, `LevelKind`, `ReferenceLevel`, `LevelTouch` (MK-04, ratified) | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/resample_ny.py` | 17:00-NY DST-aware day anchor feeding `day_index` (caller-side) | `6c6237375e344337f8ad2491f66d0cb9a9e730451595cccdea4ebe6204699650` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/institutional_levels.py | sha256sum`
against `alpha1/discovery-mk-matrix-v1`.

---

## PART A — ENTRY MECHANISM (ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric/selection decision reserved to the Statistician — not chosen here.* (This is a parameter gap, not a mechanism gap.) |
| **timeframes_used** | **M15** execution/touch; **prior-day** high/low aggregated from the previous session's M15 bars, grouped by `day_index` (17:00-NY DST-aware anchor, `resample_ny.py`, caller-side). Bars-per-day are **counted** (`sub` column), never assumed 92/96. **No fixed-ATR distance anywhere.** |
| **activation** | A PDH and PDL activate for the current day when, all knowable at the current day's first bar with no lookahead: (1) the day is **not the first of its structural block** (D3_bis: first day = UNCLASSIFIED, no level, no cross-block borrow); (2) the prior session has **fully closed**, `available_idx` = **first bar of the current day** (Q4); (3) `PDH=max(high)`, `PDL=min(low)` over the prior day (`compute_prior_day_levels`). |
| **trigger** | **First touch** in the current day's window (`detect_level_touches`): PDH `high[j] >= PDH` (resistance); PDL `low[j] <= PDL` (support). Window `[available_idx, current day's last bar]`, same block. **Consumed once (D7/Q5)** — a matured level does not re-arm on a second same-day touch. |
| **entry** | **type:** reaction/rejection off the touched reference level (grounded in `LevelKind`: PDH is *resistance*, PDL is *support*; consumption-at-first-touch fits a one-shot reaction, not breakout-continuation). **direction:** PDH touch → **short**; PDL touch → **long** (counter to the approach — the detector's own S/R semantics, not a chosen variant). **moment:** `entry@next-open` — open of the bar immediately after the trigger bar (lookahead-safe; avoids sub-bar path assumptions). **reference price:** the level (`PDH`/`PDL`); fill at next-open. |
| **invalidation** | Void before entry if: (a) the level is **consumed** (first touch already occurred, D7); (b) the current day **ends** before any touch (→ expiry); (c) the day is the **first of its block** (D3_bis — no level emitted). |
| **no_trade_rules** | No trade on the **first day of any block** (D3_bis). **Weekly levels excluded** from the daily window (`detect_level_touches` skips non-PDH/PDL). No **second** trade on a level already consumed the same day (D7). No trade if the prior session's level never matured (block reset / missing prior period). |
| **expiry** | Setup dies at the **current day's end** (`day_index` boundary at the next 17:00-NY anchor) **or** at first touch (consumption), whichever first. **Bar count is not constant** — day length is counted, never assumed (21:00-UTC maintenance gap makes it vary); expiry is the day boundary, not a fixed bar number. |
| **min_trades** (per policy & per regime) | *Numeric floor reserved to the Statistician — not chosen here.* (Parameter gap, not a mechanism gap.) |

**PART A status: complete.** Every mechanism field is defined and observable without lookahead. The two
`regimes_permitted` / `min_trades` items are **numeric parameters** awaiting the Statistician — the
*mechanism* is fully specified around them.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

The design requires a **structural** risk model: fixed-ATR SL/TP is disqualified because it produced an
**identical 0.378–0.385 winrate across six distinct mechanisms** (structure dominated the signal), so the
risk model must be derived from market structure to carry any information. The referenced material — the
**v8.5 mechanism library, M_031–M_034** — was **confirmed nonexistent** (exhaustively verified: zero in
code, zero in history across all branches, zero in the manifest; the citation was an error, not an access
problem). **No other ratified structural-SL/exit primitive exists in the repo for this family.**

| Field | Declaration (method required · why absent) |
|---|---|
| **stop_loss** | **UNSPECIFIED.** *Required:* a **ratified structural stop method** for reference-level reactions — anchored to observable structure (e.g. the source-swing behind the prior-day extreme, or the touch bar's own structural invalidation point), expressed as a **method, not a value**, and explicitly **not** fixed-ATR. *Why absent:* the only cited source (v8.5 M_031–M_034) does not exist; no ratified structural-SL primitive is available. **I do not construct one** (that would be choosing a mechanism). |
| **exit** | **UNSPECIFIED.** Same requirement and same gap — a ratified structural exit **method**, not a fixed target. Not constructed. |
| **management** (partials / breakeven / trailing) | **UNSPECIFIED.** Fully dependent on the structural stop/exit method above; cannot be declared until that method exists. Not constructed. |

**PART B status: blocked at the source.** This is a **specification gap in the risk layer**, not a gap in
the market mechanism (Part A is complete).

---

## Verdict — **PARTIALLY DEFINED**

Entry mechanism (Part A) complete and lookahead-safe; risk management (Part B) unspecified for lack of a
ratified structural source. The two are separate: **the market mechanism is present; only the
risk-management specification is missing.**

## Handoff
- **Part A (entry mechanism) → Red Team, phase A.**
- **Part B (risk management) → Statistician, as a specification request**: a ratified structural
  stop/exit/management method for reference-level policies (replacing the nonexistent v8.5 M_031–M_034),
  plus the numeric parameters (`regimes_permitted`, `min_trades`).

**Stop here — no execution, no promotion.**
