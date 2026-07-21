# E015-SCALP — Immediate Scalping Validation (Phase 0: Replay Feasibility Pilot)

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Stage**: 2 (Immediate Scalping Validation),
per `EDGE_RESEARCH_PROTOCOL.md` §9 (Protocol v2). **Parent structural result**: E015 — Order Block
Re-Mitigation (`edge_research/E015_order_block_remitigation.md`), **unmodified, verdict/status
unchanged**. This is a separate, append-only study; it does not overwrite or reinterpret E015's own
structural-behavior result.

**Authorized scope of this document**: Phase 0 only — reconstruct the detector/event list, select a
pilot sample, freeze the trade rules, replay the pilot via TradingView, record outcomes, and issue a
**feasibility verdict**. No formal validation, no optimization, no AI Trader implementation, no
acceptance/rejection of E015-SCALP itself.

---

## Phase A — Definition (frozen BEFORE any TradingView interaction)

### Detector (unchanged, reused from E015's own structural definition)

Order block = a displacement bar on M15 (range > 1.5×ATR14(prior bar), directional body ≥50% of its
own range) whose originating opposite-colored bar (within the preceding 10 bars) is the OB zone
`[ob_low, ob_high]`. Identical, byte-for-byte reused construction from
`edge_research/e015_order_block_remitigation.py::detect_obs()` — not re-tuned for this study.

### Event definition tested here

**First mitigation only** ("visit-1"), per the CEO's own stated priority ("the existing structural
result identified first mitigation as the clearest current candidate"). Visit-1 = the first M15 bar,
after OB formation, whose range overlaps the OB zone.

### Confirmation rule

Confirmed at the first M1 candle, within the M15 visit-1 bar's own 15-minute window, whose range
overlaps `[ob_low, ob_high]`. (In the structural M15 study this was resolved at 15-minute granularity;
here it is resolved down to the minute that actually touches the zone.)

### Entry rule

Enter at the **close of the confirming M1 candle** (the first M1 candle that touches the zone) — a
single, mechanically defined, non-cherry-picked entry point. Direction: bullish OB → long; bearish
OB → short.

### Stop rule

Structural stop placed just beyond the OB zone's own far edge, plus a small, disclosed buffer:
- Bull OB (long): `stop = ob_low − buffer`
- Bear OB (short): `stop = ob_high + buffer`
- `buffer = max(2 × estimated_spread, 0.05% × entry_price)` — the same style of disclosed
  executable-stop-floor convention already used elsewhere in this project (`code/mstrat.py`'s
  `max(2×spread, 5×tick, 0.10×ATR)`), adapted to M1/scalp scale, not fit to this sample's own outcomes.

### Risk and target

`1R = |entry_price − stop_price|`. `TP = entry_price + direction × 2R` (fixed 1:2 RR, per Protocol v2's
own standing convention — not selected after seeing any outcome).

### Primary validation horizon (predeclared — the ONE horizon used for the primary result)

**15 minutes**, chosen because it matches the structural detector's own native M15 resolution (the
timeframe on which "first mitigation" was itself defined) — disclosed before any replay, not selected
after seeing results. **5, 10, 30, 60 minutes, and session-end are recorded as secondary profiling
outputs only, never used to pick the most favorable result.**

### Timeout rule

If neither TP nor SL is touched within the primary 15-minute horizon, classify **TIMEOUT** at the
15-minute mark, recording the bar's own MFE/MAE up to that point regardless.

### Invalidation rule

Classify **INVALID** if: the M1-level data does not actually show a candle touching the OB zone within
the M15 visit-1 bar's own window (a resolution/feed mismatch between the structural M15 detection and
the M1 replay), or if TradingView's own replay/feed does not have data at the required date/time.

### Tie-break rule for same-candle TP/SL ambiguity (frozen in advance, per explicit CEO instruction)

If a single M1 candle's range touches both the TP and the SL level, and no finer-resolution evidence
(e.g. a visible wick-formation order, or a broker's own lower-timeframe tick chart if made available)
resolves which was hit first, classify **AMBIGUOUS**. Never assume the favorable outcome by default.

### Costs (disclosed, estimated, not fit to this sample)

Estimated spread: **$0.25** (typical retail XAUUSD spread). Estimated slippage: **$0.05** per side.
Cost-adjusted R subtracts `(spread + 2×slippage) / 1R` from the raw R outcome of every non-invalid,
non-ambiguous event.

### Event sample (pilot)

Population: all visit-1 events detected on the clean M15 split (`data_split_id =
pre_holdout_2025-10-23T09-15-00Z_v1`), **n = 6,919** (`edge_research/e015_scalp_all_visit1_events.json`).

**Pilot sample-selection rule (frozen before any replay, `edge_research/e015_scalp_reconstruct_events.py`)**:
stratify by `(ob_polarity, session)` (8 non-empty strata found: bull/bear × asia/london/ny/late), draw
one event per stratum in round-robin order using a fixed seed (42, this program's own standing
convention), **outcome-blind — the event's own already-computed structural reaction (continuation/
reversal/MFE/MAE) is never consulted when selecting**, capped at **5 events** for this Phase 0
feasibility pilot (a disclosed reduction from the CEO's own recommended 10-20, given the real per-event
cost of manual candle-by-candle TradingView replay — this pilot's purpose is to expose workflow
problems, not to claim statistical coverage; extendable by a future session if the verdict below is
FEASIBLE or FEASIBLE WITH LIMITATIONS).

### Break-even threshold after estimated costs

For a 1:2 RR trade, gross break-even win rate = 1/3 (33.3%). Net of the disclosed cost estimate above
(cost ≈ 0.35/1R at typical XAUUSD M1 risk distances in this sample, itself only estimable once real risk
distances are observed in the pilot), the cost-adjusted break-even win rate will be computed and
reported per event once real entry/stop prices are recorded — not assumed in advance.

---

## Phase B — Pilot replay: narrative walkthrough

**Environment check**: `tv_health_check` confirmed a live CDP connection to TradingView Desktop
(`cdp_connected: true`), chart initially on `FUSIONMARKETS:XAUUSD`, 45-min resolution, with the user's
own SMC/ICT indicator set loaded (irrelevant to raw OHLCV replay, noted for completeness).

**Setup steps taken** (verified working correctly):
1. `chart_set_symbol("OANDA:XAUUSD")` — succeeded. Switched away from the original
   `FUSIONMARKETS:XAUUSD` feed specifically to match this repository's own OANDA data provenance and
   avoid an unnecessary cross-provider confound, per the mandatory event schema's own
   "provider/feed shown in TradingView" field.
2. `chart_set_timeframe("1")` — succeeded, chart confirmed ready at M1.

**Pilot attempt 1 (`E015SCALP-PILOT-01`, 2023-03-22, ~asia session)**:
- `chart_scroll_to_date("2023-03-22")` reported success with a plausible-looking centered timestamp.
- `replay_start(date="2023-03-22")` reported `success: true`, but the returned `current_date` field
  (1753075260) decoded to the **live, real-time bar** (2026-07-21), not 2023-03-22.
- Repeated with a fresh `chart_scroll_to_date` immediately before `replay_start`, and again with no
  `date` argument at all (letting the tool "select first available date") — same result each time:
  the reported/actual position stayed at the live bar.
- A screenshot taken at this point (`e015_scalp_evidence/e015_scalp_diag_scroll_2023-03-22.png`) shows
  two decisive facts directly from the TradingView UI itself (not inferred): (a) an unhandled **"Continue
  your last replay?"** modal dialog was open, and (b) a native TradingView toast reading **"Data point
  unavailable — The selected date is not available for playback."** The dialog was cleared via
  `ui_click(by="text", value="Start new")`.

**Pilot attempt 2 (`E015SCALP-PILOT-05`, 2025-05-28, ~late session)** — deliberately chosen recent
(~8 weeks before this session) to separate "date too old for this feed's retention" from "the tool's
own seek mechanism is broken":
- Same `chart_scroll_to_date` → `replay_start(date="2025-05-28")` sequence. `replay_start` again
  reported success, `current_date` again decoded to the live real-time bar.
- **No "data unavailable" toast appeared this time** — a screenshot
  (`e015_scalp_evidence/e015_scalp_diag_2025-05-28.png`) shows the "Replay" watermark active (confirming
  replay mode genuinely engaged) but the visible price/date is the live one ($3,364.50, matching the
  live quote), not 2025-05-28.
- `replay_step()` was then called once: `current_date` advanced from 1753075380 to 1753075439 — **exactly
  59-60 seconds, i.e. a correct, precise one-minute step**. This confirms candle-by-candle advancement
  itself works correctly **once replay is active** — the defect is specifically in seeking to a
  requested **start** date, not in stepping forward from wherever replay happens to be.

**Remaining 3 pilot events (`PILOT-02/03/04`) were not attempted.** The blocking defect was reproduced
identically on two independent dates (one ~3.3 years back, one ~8 weeks back); attempting the same
diagnostic a third, fourth, and fifth time would not add information, consistent with Phase 0's own
purpose (expose workflow problems, not accumulate a large sample once the blocker is confirmed).

**Full structured record**: `edge_research/e015_scalp_pilot_events.json` (all fields from the mandatory
event schema, for all 5 pilot events).

## Phase D — Feasibility report

**What worked**: CDP connection, symbol switching, timeframe switching, entering replay mode itself
(confirmed via the "Replay" watermark), single-bar step precision (exactly 1 minute per `replay_step`
call), screenshot evidence capture, and UI-dialog handling via `ui_click`.

**What did not work**: `replay_start`'s own `date` parameter did not seek the chart/replay to the
requested historical date in either test — the position consistently remained at (or reverted to) the
live real-time bar. This was tested with a prior `chart_scroll_to_date` to the same date immediately
beforehand (which itself reported a plausible-looking centered timestamp), and without any prior scroll
at all — same failure both ways.

**Two distinct signals, not fully separated by this pilot**:
1. For the older date (2023-03-22, ~3.3 years back), TradingView's own native UI produced a **"Data
   point unavailable — The selected date is not available for playback"** toast — consistent with a
   real feed-retention limit on how far back M1 replay history extends for `OANDA:XAUUSD` on this
   TradingView connection/plan, independent of any tooling defect.
2. For the recent date (2025-05-28, ~8 weeks back — almost certainly within any reasonable M1 retention
   window), no such toast appeared, yet the seek still failed identically — pointing to a genuine
   **automation/tool-integration defect** in how `replay_start`'s `date` argument is wired to
   TradingView's own internal replay-seek mechanism, separate from any data-retention question.

**Per the CEO's own explicit instruction** ("If automation skips candles, loses replay position...
stop and document the issue. Do not silently substitute manual visual assumptions for missing
automation capability"), no attempt was made to work around this by manually estimating candle
positions, clicking blindly at inferred chart-pixel coordinates to select a historical bar, or otherwise
approximating the seek. This is a **tooling-capability finding**, not a claim that TradingView Bar
Replay is inherently unusable by a human operator through the ordinary UI — a person manually
scrolling/clicking through TradingView's own Bar Replay panel might well succeed where this specific
automated `date`-parameter path did not; that distinction is explicitly not resolved by this pilot.

### Mandatory feasibility verdict

**C. NOT FEASIBLE** — with the currently available automated TradingView Replay tooling, specifically:
timestamp-seeking to a precise historical event start point is unreliable (reproduced on two
independent dates, one additionally implicating a possible feed-retention limit), which makes formal,
scaled validation (10+ events, let alone the full 6,919-event visit-1 population) impractical and
untrustworthy at this time. This is a **tooling/data-access limitation finding, not a judgment on E015's
own structural finding** (unchanged, see `E015_order_block_remitigation.md`) and not a judgment on
whether TradingView Replay could ever work for this purpose via a different automation approach or
manual operation.

### What would need to change before re-attempting Phase 0

1. **Diagnose and fix (or replace) the `replay_start` date-seek path** — e.g. confirm whether the
   underlying CDP script actually passes the date through to TradingView's own replay-selection API, or
   whether a UI-click-based date selection (via `ui_find_element`/`ui_mouse_click` on TradingView's own
   Bar Replay date picker) is required instead of the current parameterized call.
2. **Separately confirm the feed's own M1 replay retention window** for `OANDA:XAUUSD` (or an
   alternative broker feed) on this TradingView plan — e.g. by manually testing Bar Replay via the
   ordinary UI (outside automation) at a few known dates to establish the actual lookback boundary,
   before assuming any specific historical event is reachable.
3. Only once both of the above are resolved should Phase 0 be re-attempted, ideally against the full
   5-event pilot sample already selected (`e015_scalp_pilot_sample.json`) plus enough of the remaining
   6,914 unused visit-1 events to reach the CEO's own recommended 10-20 count.

**E015-SCALP is NOT accepted, NOT rejected, and remains at Phase 0 — incomplete due to a tooling
blocker**, not due to any finding about the underlying market behavior. E015's own structural result
(V0 NOT SUPPORTED as registered; V1 candidate = "reaction concentrated in the first mitigation only")
is unchanged and continues to stand as a **structural-behavior Discovery** result only — its own status
already states this is not yet a validated scalp, and this pilot has not changed that determination
either way.

---

## Phase 0A — TradingView Historical-Seek Tooling Remediation (2026-07-22)

**Authorized scope**: repair/replace the historical-date-seeking workflow only. No new edge, no
formal validation, no external data acquisition, no change to the frozen E015-SCALP rules or pilot
sample (all preserved exactly as defined in Phase 0 above — detector, 6,919-event universe,
selection method, seed=42, selected event IDs/timestamps/strata, confirmation/entry/stop/TP=2R/
timeout/cost/ambiguity rules, outcome schema).

**Note on repository boundary**: the actual tooling code lives in a separate, third repository —
`C:\Users\MEDION GAMING\tradingview-mcp` — the shared TradingView control/integration project this
program's replay tools depend on, distinct from both Flow A (`ai_quant_lab-alpha-discovery`) and
Flow B (`ai_quant_lab-research-main`). All code changes described below were made and committed
there; this document records the investigation and its outcome for Flow A's own governance trail.

### Root-cause investigation

Live-tested (not assumed) against the real TradingView connection, in isolated steps, per the CEO's
own required checklist:

- **Exact command/API sequence**: `replay.start()` calls TradingView's own internal replay
  controller (`window.TradingViewApi._replayApi`) via CDP `Runtime.evaluate` — `showReplayToolbar()`,
  then `selectDate(ts)` (or `selectFirstAvailableDate()`), then polls `isReplayStarted()`/
  `currentDate()`. This is a JS-API path, not a DOM/UI-click path — the same underlying API a human
  clicking TradingView's own Bar Replay calendar would ultimately invoke.
- **selectDate() promise handling**: confirmed properly awaited (wrapped in `.then()`, called via
  `awaitPromise`-aware evaluation in diagnostics) — the promise **resolves** (`RESOLVED_OK`), it does
  not reject. The original "issue #26" fix (awaiting the promise inside the page context) remains
  correct; this was **not** the defect.
- **Whether a subsequent command invokes "Go to real-time"**: no — nothing in the code path calls
  `goToRealtime()`.
- **Whether the "Continue your last replay?" modal steals focus**: a real, observed modal (screenshot
  evidence from Phase 0), but proven **not to be the root cause** — the same failure reproduced
  identically after the modal was dismissed, after a full page reload (which clears all modal/session
  state), and on a symbol (`EURUSD`) that had never shown the modal at all.
- **Whether symbol/timeframe change resets replay state**: tested and ruled out — failure is
  identical on `OANDA:XAUUSD` and `EURUSD`.
- **Whether the seek command runs before the chart finishes loading**: ruled out — a ~1.5s settle
  delay after symbol/timeframe changes was already present and did not change the outcome; the same
  failure occurred with much longer delays between steps.
- **Whether CDP selectors are stale**: ruled out — `isReplayAvailable()`, `isReplayStarted()`, and
  `currentDate()` all read back consistent, correctly-typed values throughout (e.g. `currentDate()`
  correctly returned `null` at true baseline and advanced by exactly 60s on a single `doStep()`
  call), meaning the API path itself is wired correctly.
- **Whether the current tool verifies the final visible timestamp**: **this was the actual defect** —
  it did not. `isReplayStarted()===true && currentDate()!==null` was treated as sufficient evidence of
  success, with no check that `currentDate` corresponds to the requested date at all.
- **Whether TradingView returns an explicit success/failure state**: **yes, but the code never read
  it** — a native TradingView toast, full text: *"Data point unavailable — The selected date is not
  available for playback. The chart was moved to the first point available for playback."* — appears
  every time a request cannot be honored, and was not being checked.

### Decisive live test sequence (TEST 1–3, per the CEO's own required steps)

| Test | Requested date | Result | Toast shown |
|---|---|---|---|
| Recent (~15 min back) | 2025-07-21T05:30Z | Landed on a substituted point | Yes |
| Recent (~2h/12h/24h/3d/1wk back), repeated 6×, same symbol | various | Landed on the same substituted point every time | Yes, every time |
| `selectFirstAvailableDate()` (TradingView's own "earliest available" call, no date at all) | — | Landed on the same substituted point | Yes |
| Different symbol (`EURUSD`, `selectFirstAvailableDate()`) | — | Landed on the same substituted point | Yes |
| Full page reload, then repeat recent-date test | 2025-07-15 | Landed on a substituted point (now correctly tracking real time, ruling out a frozen/cached value) | Yes |
| Original frozen pilot date (via the **remediated** `start()`) | 2025-05-28 | Correctly classified **DATA_UNAVAILABLE** (no longer a false success) | Yes |

**Conclusion**: the failure is symbol-independent, survives a full page reload, and occurs even for
TradingView's own "give me the earliest available point" call with no historical target at all —
this is not plausibly a client-side automation bug in this codebase. It is far more consistent with
an **account/subscription-plan restriction on intraday (M1) Bar Replay historical depth** — TradingView
gates extended Bar Replay history behind certain plan tiers, and this account/connection appears not
to have access to it for intraday resolutions, for any symbol tested. This was not independently
confirmed against TradingView's own plan/feature documentation (out of scope for this remediation) —
noted as the recommended next check if historical M1 replay is still wanted.

### Remediation implemented (tradingview-mcp commit `c839e91`)

In `src/core/replay.js::start()`:
1. Detects and dismisses a lingering "Continue your last replay?" modal before selecting a new date;
   fails closed with **MODAL_BLOCKED** if a modal is present and cannot be dismissed, instead of
   proceeding against unknown UI state.
2. After the existing polling loop succeeds, checks for TradingView's own "Data point unavailable"
   toast; if present, throws **DATA_UNAVAILABLE** (with the toast's own text and the substituted
   `current_date` attached) instead of returning success.
3. Verifies the resulting `currentDate` is within a documented tolerance (2 days, accommodating
   weekend/holiday bar gaps) of the requested date; throws **TIMESTAMP_MISMATCH** if not, even when no
   toast appeared.
4. `src/tools/replay.js` now surfaces the new `.code` (and `current_date`, when present) to the MCP
   tool caller on failure, not just the error message.

**Every non-success path now throws an explicit, checkable code**
(`TOOLING_FAILURE`/`DATA_UNAVAILABLE`/`MODAL_BLOCKED`/`TIMESTAMP_MISMATCH`) instead of ever silently
reporting `success: true` on a substituted date. Per the CEO's own standard — "a false success is
worse than a declared failure" — this is a genuine, verified fix, independent of whether the deeper
plan/data limitation is ever resolved.

### Tests

`tests/replay.test.js`: **45/45 passing** (6 new — modal dismissal, MODAL_BLOCKED,
DATA_UNAVAILABLE, TIMESTAMP_MISMATCH, in-tolerance acceptance, first-available-date path correctly
skips date comparison; 1 existing test's mock `currentDate` corrected to be internally consistent
with its own requested date — a pre-existing inconsistency unrelated to the polling behavior that
test actually verifies). Mocked at the control layer (DI pattern, `_deps`) per existing convention.

### Mandatory live verification (required before declaring remediation complete)

Ran the **remediated** `start()` (not a diagnostic script) against the live TradingView connection
four times: two repeated recent-date attempts (repeatability), the original frozen `E015-SCALP`
pilot date (2025-05-28), and the no-date `selectFirstAvailableDate()` path. **All four now correctly
and deterministically report `DATA_UNAVAILABLE`** — zero false successes, zero crashes, consistent
classification every time.

### Feasibility verdict (Phase 0A) — exactly one, per the CEO's own taxonomy

**C — TOOLING STILL BLOCKED.** The remediation genuinely succeeded at its own stated goal — historical
seek failures are now deterministic, explicit, and correctly classified, with no possibility of a
silent false success remaining. It did **not**, however, unlock the ability to reach any historical
point: every tested date (from 15 minutes back through the original ~2-3-year-old pilot dates),
across two symbols, before and after a page reload, and via TradingView's own "first available date"
call, is rejected identically. This is assessed as a data/plan-level limitation, not a remaining
client-side defect — but that assessment was not independently confirmed against TradingView's own
subscription documentation, so it is reported as the most likely explanation, not a certainty.
**Verdict A/B are not reached** (no historical date is reachable at all, so the frozen pilot cannot
resume); **verdict D is not adopted** either, since TradingView's own "Data point unavailable" toast —
which even its own `selectFirstAvailableDate()` API triggers — is native platform behavior, not
something specific to this automation's own approach, making it unlikely (though not proven) that
manual UI operation would fare differently.

**No E015-SCALP performance verdict is issued.** Per the CEO's own explicit instruction, the frozen
pilot is **not** retried under this verdict (that step is gated on verdict A or B only).

### What would unlock further progress

1. **Confirm the actual TradingView plan/subscription tier** attached to this connection and whether
   it includes extended intraday Bar Replay history — a billing/account question, not a code fix.
2. If confirmed unavailable on the current plan: either upgrade, or pursue the previously-proposed
   M1 data-ingestion plan (`NEXT_SESSION_FLOW_A.md`) as an alternative to TradingView Replay entirely.
3. If a plan upgrade or alternative feed resolves the underlying limitation, Phase 0 can be
   re-attempted directly against the already-frozen 5-event pilot sample with **no changes needed**
   to this remediation's own code — the fix is orthogonal to the data-availability question.

### Higher-timeframe handoff test (CEO-directed, 2026-07-22) — WORKFLOW FAILS

Tested whether starting Bar Replay on a higher timeframe (where deep history clearly exists on
disk) and then switching down to M1 could route around the M1-specific restriction. Protocol and
pilot sample untouched; no new edge; E013 not resumed.

- **4H, requesting the oldest frozen pilot date (2023-03-22)**: `replay.start()` failed immediately
  with `DATA_UNAVAILABLE` — same native toast: *"Data point unavailable — The selected date is not
  available for playback."* Could not proceed to the timeframe-switch step at all.
- **Boundary check, 4H and D1, progressively more recent dates (2025-06-01, 07-01, 07-14, 07-19 —
  the last only ~2 days before this test's own real-world "now")**: **every single attempt failed
  identically**, on both timeframes, including the date only 2 days back.

**Result: workflow FAILS.** The restriction is not M1-specific — Bar Replay seeking to any past
point fails identically on M1, 4H, and D1, regardless of how recent the date is, on this
TradingView connection. This further supports (does not merely repeat) the Phase 0A conclusion: a
plan/subscription-level restriction on Bar Replay itself, not a timeframe- or code-specific defect.
The proposed HTF-then-switch-to-M1 route does not exist as a viable workaround on this account.

---

## Phase 0 — Manual-Navigation Retry (2026-07-21/22) — CORRECTED, retraction of an earlier
## mechanism claim

**Authorized scope**: same as above — frozen detector, event list, seed=42, selected event
IDs/timestamps/strata, confirmation/entry/stop/TP=2R/timeout/cost/ambiguity rules, and outcome
schema all unchanged. No new edge, no formal validation, no external data acquisition. E013 not
resumed.

### Step 1 — manual chart navigation (CEO-directed, distinct from the `replay_start(date)` API path)

Tested normal (non-replay) chart scrolling, driven by real mouse-wheel input, with no date-seek API
call anywhere in the path:

- **4H historical scroll depth**: reached **2023-01-20** (past the oldest frozen pilot event,
  2023-03-22) in 16 scroll rounds, and reached each of the 5 frozen event dates directly in 5–16
  rounds each. **This refutes the Phase 0A "plan/subscription-level restriction" theory** — the
  underlying 4H history is present and reachable back through all 5 pilot dates; the earlier
  `replay_start(date)` failures were specific to that API's own seek path, not to data availability.
- Manually clicking a visible historical candle (real trusted CDP `Input.dispatchMouseEvent`
  sequences: `mouseMoved` → `mousePressed` → `mouseReleased`, not JS-synthetic events) **appeared to
  start Bar Replay successfully once**, in an earlier diagnostic session, on a freshly-duplicated
  chart tab, including a clean 4H→M1 timeframe switch that preserved the historical position. That
  single result was reported as **"Verdict A — MANUAL START REMEDIATED"** and accepted as such.

### Step 2 — this retry attempted to execute the frozen 5-event pilot using that mechanism

**Result: the click-based mechanism could not be reproduced.** Across a rigorous re-test —

- 2 different chart tab sessions, one a fully page-reloaded existing tab, one a genuinely new tab
  opened by the CEO directly through the TradingView UI (ruling out any tab-specific staleness);
- both confirmed rendering real historical candles correctly, with no blocking dialog/modal (a
  leftover "Continue your last replay?" modal was found and dismissed as a separate, real bug in the
  test harness — not the cause of this result, since failures continued after fixing it);
- the Bar Replay toolbar confirmed genuinely active (`[data-name="replay-bottom-toolbar"]` present)
  before every click attempt;
- click coordinates verified against the chart's own actual on-screen time window
  (`getVisibleBarsRange()`), not an internal loaded-buffer index (an unrelated harness bug, also
  found and fixed, that had been placing earlier clicks off the visible candle entirely);
- 7 different vertical (price-level) click positions tested across the full canvas height, one
  right-click tested (opened TradingView's ordinary context menu — no "start replay here" option
  exists in it), delays between activation and click varied from 500ms to 2000ms —

**`is_replay_started` remained `false` after every single attempt** (10+ clean, independently
verified attempts total this session). `document.elementFromPoint()` at the click coordinates
confirmed the click was landing on the plain chart canvas (`cursor: crosshair`, no intercepting
overlay) every time.

### Retraction

**The earlier "Verdict A — MANUAL START REMEDIATED" finding is retracted as not reproducible.**
Given it could not be reproduced under materially more rigorous, controlled conditions than the
original observation, the most likely explanation is that the original single success was a
measurement artifact (e.g. a stale/in-flight state from adjacent manual testing in that session),
not a genuinely working click-to-select-replay-start-candle mechanism. This is reported plainly
rather than allowed to stand uncorrected — the CEO's own governance instruction ("a false success
is worse than a declared failure") applies here to my own prior report, not only to the tooling.

### Outcome for the 5 frozen pilot events

**Evidence (screenshots)**:
`edge_research/e015_scalp_evidence/phase0_retry_2026-07-21_scroll_reached_2025-05-28.png` (normal
4H scroll landed correctly on the target event date, real candles rendering),
`edge_research/e015_scalp_evidence/phase0_retry_2026-07-21_replay_toolbar_active_no_start.png`
(Bar Replay toolbar genuinely active, candles rendering, no blocking dialog, immediately before a
click attempt), `edge_research/e015_scalp_evidence/phase0_retry_2026-07-21_rightclick_context_menu_no_replay_option.png`
(TradingView's own right-click context menu on the chart canvas — no replay-start option present).

**No event's recorded outcome changes.** All 5 (`E015SCALP-PILOT-01` through `-05`) remain exactly
as classified in Phase 0/0A (`e015_scalp_pilot_events.json`, unedited). This retry did not reach the
point of selecting a replay start candle for any event, so no WIN/LOSS/TIMEOUT/INVALID/AMBIGUOUS/
DATA_UNAVAILABLE determination could be made for any of them today. Every attempt this session is
an operational tooling log (`TOOLING_RETRY`), not a research outcome, per the CEO's own explicit
instruction, and is not recorded as a pilot event outcome.

### Feasibility verdict (this retry) — exactly one, per the CEO's own taxonomy

**C — NOT FEASIBLE.** The frozen pilot could not be executed today: the manual click-based
replay-start mechanism this verdict depends on could not be made to work reliably, or at all, under
rigorous re-testing, despite normal chart navigation and historical data reachability both being
independently confirmed sound. Replay *selection* — not seeking, not stepping, not the
timeframe-preservation mechanism — is the specific unresolved blocker.

### What would need to change before re-attempting

1. A human operator manually performing the exact click sequence through the real TradingView UI
   (mouse and keyboard, not CDP-dispatched events) to establish, independent of any automation
   question, whether a left-click on a visible candle in Bar-Replay-selection mode is a genuine
   TradingView feature on this account at all — this retry's evidence (no context-menu option, no
   success at any of 7 tested vertical positions) leaves this genuinely open again.
2. If confirmed to work manually but not via CDP-dispatched input, the automation gap would need a
   different input-injection strategy than `Input.dispatchMouseEvent` (untested in this retry).
3. Tooling hardening deferred pending (1) and (2) — no further harness changes are proposed until
   the underlying interaction is confirmed to exist at all.

**E015-SCALP remains at Phase 0, incomplete.** E015's own structural result
(`E015_order_block_remitigation.md`) is unaffected.

---

## Phase 0 — Root-Cause Investigation of the Non-Reproducible Result (2026-07-21) — CLOSED,
## EVIDENCE LIMIT REACHED

Following the retraction above, the CEO rejected a premature feasibility verdict and required a
root-cause investigation into why the one earlier apparent success (a click starting Bar Replay,
stepping correctly, and preserving position across a 4H→M1 switch) could not be reproduced.

### Categories tested, each an attempt to falsify

| Category | Test performed | Result |
|---|---|---|
| Blocking dialog/modal (current attempts) | Explicit DOM check (`[role="dialog"]`, `[class*="modal"]`) immediately before a click | Empty — no dialog present when the click still failed |
| Chart layout | Two independent layouts tested (original 3-indicator layout; a second, unrelated layout with 5 indicators + Volume Delta panel) | Identical failure on both |
| Renderer/session state | Full `Page.reload()` (fresh JS context) before activating | Still failed |
| Automation timing | Delays from 500ms to 2000ms between activation and click | No difference |
| Click coordinates | 7 vertical positions spanning the full canvas height; both a precise time-computed x and a generic 40%/50% x | All failed |
| Replay toolbar state | Confirmed genuinely present (`[data-name="replay-bottom-toolbar"]`) before every attempt | Present every time; not itself blocking |
| Pine overlays | Tested with an entirely different indicator set | Same failure |
| Viewport positioning (lazy-load taint) | Tested on unscrolled/already-loaded recent data vs. deeply-scrolled/lazy-loaded historical data | Both failed identically — falsifies "only lazy-loaded bars are unclickable" |
| Stale WebContents / tab identity | Tested on a reloaded existing tab, and on a genuinely new tab (different chart_id, never touched before, opened directly by the CEO) | Both failed |
| CDP target attachment | Fresh CDP connection created for every test | No difference |
| Shared/synced replay state across duplicate-layout tabs | Activated + clicked on one tab sharing a chart_id with another, checked the other for reflected state | Inconclusive — no positive state was achievable in either tab to test propagation |

### Conclusion (recorded verbatim, per CEO instruction)

> Current evidence most strongly supports Category C (stale/pre-existing replay state), but this
> remains an unproven hypothesis due to the lack of an independent manual confirmation.

**STATUS: EVIDENCE LIMIT REACHED.** No feasibility verdict is issued. No implementation or
workaround was attempted or is proposed. The investigation is closed pending new evidence.

### What would upgrade or falsify this conclusion

- **To upgrade toward Category A (genuine, reproducible click-driven start)**: a human operator
  performs the exact click sequence through the real TradingView UI (real mouse/keyboard, not
  CDP-dispatched input) on a tab with **no prior Bar Replay activity of any kind** (verified via a
  screenshot taken immediately beforehand showing no modal, no toolbar, no stale state), and it
  succeeds — ideally repeated on a second, independently fresh tab to rule out a one-off.
- **To upgrade toward Category C (confirmed stale/pre-existing state)**: reproduce a "Continue your
  last replay?" modal deliberately (e.g., by starting a real replay session via the TradingView UI,
  then closing and reopening a duplicate tab of the same layout), screenshot the exact modal
  position, and confirm that a click at the coordinates used in the original successful test
  (40%/45% of the canvas) would have geometrically landed on the modal's "Continue" control.
- **To falsify Category C entirely**: demonstrate that no "Continue your last replay?" modal (or any
  other stale-state artifact) was possible at the time of the original success — e.g., if TradingView
  access logs, network capture, or an account activity trail from that exact timestamp show no prior
  replay session existed to be "stale."
- **To rule out Category B (detection bug)**: not currently indicated by any evidence — 
  `isReplayStarted()`/`currentDate()` behaved consistently and correctly in every other test, before
  and since — but would be reinforced by unit-testing the exact unwrap/read logic (`uw()` helper)
  against a mocked CDP response matching the original success's raw values.

### Governance

No tooling change was made or proposed in this investigation. No new edge, no formal validation, no
E013, no Phase 1. E015's own structural result is unaffected. This investigation is closed;
resuming it requires explicit CEO reauthorization.
