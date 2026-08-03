# POLICY — PDH/PDL (Previous Day High / Low) — canonical schema

**Design artifact only. No execution, no data touched, no numeric parameter chosen, no optimization, no
multiple variants.** First candidate from the operational pipeline, formalized for handoff to **Red Team,
phase A**. Exploratory figures (winrate 0.435 @ n=356, expectancy_$ +0.334, gross edge +0.534, positive
4/4 sessions, 6/7 years) carry **no privileged status** and are not reproduced or relied on here.

Grounded in the real, ratified detectors `compute_prior_day_levels` and `detect_level_touches`
(`code/institutional_levels.py`, MK-04). Decision IDs cited are those detectors' own (D3_bis, Q4, Q5/D7,
17:00-NY day anchor).

---

## Schema

| Field | Value |
|---|---|
| **policy_id** | `PDH-PDL` |
| **version** | `1.0` (draft for Red Team phase A) |
| **family** | `institutional_reference_levels` (MK-04) |
| **regimes_permitted** | **PENDING — STATISTICIAN.** A regime selection is a numeric/threshold decision explicitly reserved to the Statistician; not chosen here. |
| **timeframes_used** | **DEFINED.** Execution/touch resolution = **M15**. Levels = **prior-day** high/low aggregated from the M15 bars of the previous session, grouped by `day_index` (17:00-NY DST-aware anchor, `resample_ny.py`, caller-side; bars-per-day are COUNTED via the `sub` column, never assumed 92/96). No fixed-ATR distance is used anywhere (per the design constraint). |

### activation — DEFINED (lookahead-safe)
A PDH and a PDL become active for the **current** trading day when **all** hold, all knowable at the
current day's first bar with no lookahead:
1. The current day is **not the first day of its structural block** (D3_bis: the first day of each block
   is UNCLASSIFIED and emits no level — borrowing a prior period from outside the block would violate
   quarantine).
2. The prior session has **fully closed** (its high/low are final); `available_idx` = the **first bar of
   the current day** (Q4), the earliest bar at which the level is known without lookahead.
3. `PDH = max(high)` over the prior day's bars; `PDL = min(low)` over the prior day's bars
   (`compute_prior_day_levels`).

### trigger — DEFINED (lookahead-safe, mechanical)
The **first touch** of a level inside the current day's availability window, per `detect_level_touches`:
- PDH (resistance): `high[j] >= PDH`. PDL (support): `low[j] <= PDL`.
- Window: `[available_idx, last bar of the current day]`, same block; day boundary via `day_index`.
- **Consumed once (D7 / Q5):** a matured level is consumed at its **first** touch and does **not** re-arm
  on a second touch the same day.

### entry — type/moment/reference DEFINED; direction is the detector's own S/R reading (flagged)
- **type:** reaction / rejection off the touched reference level (the detector encodes PDH as
  *resistance* and PDL as *support*; consumption-at-first-touch fits a one-shot reaction, not a
  breakout-continuation model).
- **direction (structural reading, not a chosen variant):** touch of **PDH → short**; touch of
  **PDL → long** (counter to the approach into the level). *Flag for Red Team / Statistician:* this
  direction is read from the detector's S/R semantics; it must be reconciled with the exact direction
  convention under which the exploratory edge was measured before any test — I do not assume they match.
- **moment:** `entry@next-open` — the open of the bar **immediately after** the trigger (touch) bar
  (lookahead-safe convention already established in the lab). Not immediate-intrabar (which would require
  sub-bar path assumptions).
- **reference price:** the level itself (`PDH`/`PDL`) as the event reference; fill at the next-open.

### invalidation — DEFINED (lookahead-safe)
The setup is void **before entry** if any holds: (a) the level is **consumed** — its first touch already
occurred (D7, no re-arm); (b) the current day **ends** before any touch (→ expiry); (c) the day is the
**first of its block** so no level was ever emitted (D3_bis).

### stop_loss — ⛔ FAIL-CLOSED (method not definable from available material)
The design constraint requires a **structural** stop (fixed-ATR is prohibited — it produced an identical
0.378–0.385 winrate across six distinct mechanisms, structure dominating signal) and names the **v8.5
mechanism library, M_031–M_034**, as the material. **That library / those mechanism IDs could not be
located in any accessible repository** (searched alpha-automation, ai_quant_lab, research-main, families,
stratdev — exact tokens `M_031`–`M_034`: zero matches). **I do not invent a structural-SL method** —
choosing one would be selecting a mechanism, which is prohibited. **STOP on this field.** To complete:
provide access to the v8.5 library M_031–M_034 (or the specific structural-SL mechanism to apply).

### exit — ⛔ FAIL-CLOSED (same material gap as stop_loss)
Structural exit (method, not a fixed value) is likewise to be derived from M_031–M_034, unavailable.
**STOP on this field**; not invented.

### management (partials / breakeven / trailing) — ⛔ FAIL-CLOSED
Fully dependent on the structural stop/exit method (M_031–M_034). Cannot be defined without it. **STOP.**

### no_trade_rules — DEFINED (explicit)
- No trade on the **first day of any structural block** (D3_bis UNCLASSIFIED — no level emitted).
- **Weekly levels are excluded** from this policy's daily window (`detect_level_touches` skips
  non-PDH/PDL levels; a separate window governs weekly levels).
- No **second** trade on a level already consumed the same day (D7, no re-arm).
- No trade if the prior session's level never matured (block reset / missing prior period).

### expiry — DEFINED
The setup dies at the **end of the current trading day** (the `day_index` boundary at the next 17:00-NY
anchor) **or** at the level's first touch (consumption), whichever comes first. **Bar count is not a
constant** — a day's bars are COUNTED, never assumed 92/96 (the 21:00-UTC maintenance gap makes day
length vary); expiry is defined by the day boundary, not a fixed bar number.

### min_trades (per policy and per regime) — PENDING — STATISTICIAN
A minimum-sample floor is a numeric threshold reserved to the Statistician; not chosen here.

---

## Verdict — **PARTIALLY DEFINED**

- **DEFINED, lookahead-safe:** family, timeframes_used, activation, trigger, entry (type/moment/reference;
  direction flagged for reconciliation), invalidation, no_trade_rules, expiry.
- **FAIL-CLOSED (stopped, not invented):** stop_loss, exit, management — all blocked on the v8.5
  mechanism library M_031–M_034, which is not present in any accessible repository.
- **PENDING STATISTICIAN (numeric, not chosen):** regimes_permitted, min_trades.

**Handoff:** Red Team, phase A. **Two items to unblock before the policy can become fully DEFINED:**
(1) access to v8.5 mechanism library M_031–M_034 for the structural stop/exit/management methods;
(2) confirmation of the entry direction against the exploratory edge's own convention.

**Stop here — no execution, no promotion.**
