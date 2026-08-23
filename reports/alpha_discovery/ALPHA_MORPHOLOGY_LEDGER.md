# ALPHA_MORPHOLOGY_LEDGER — BLIND_FORWARD_STRUCTURE_DISCOVERY_V1

Primary discovery method (CEO superseding mandate 2026-08-23, + 2 corrections: STRICT candle-by-candle / no forward windows; and
TOP-DOWN H4→H1→M15→M5). The 14-module taxonomy remains the **classification map**, not the discovery driver. This ledger records
blind-forward observations, the morphologies they cluster into, and (post-replay only) their conditional outcomes. **Discovery ≠
validation**: a morphology becomes a preregistered hypothesis only when it recurs with information above baseline; it is an edge only
after §12 mechanize + §13 full quant-falsification.

## Engine architecture (hard causality wall)
- **`bfsd_engine.py`** — strict candle-by-candle replay. At each candle T the analyzer is a PURE function of history≤T: HTF/LTF
  primitives filtered to their KNOWABLE bar (MK-01 swings / MK-03 FVG = `confirmed_idx`; MK-01 breaks = break bar; Mod.5 OB =
  `formation_idx+1`, per ratified "OB cunoscut la bara i"; causal H4/H1 bars by `complete_at ≤ T`); price read only via `[:T+1]`.
  Reading is TOP-DOWN: H4 context (trend/phase) → H1 structure (continuation/correction) → M15 setup (zone reaction). If H4/H1 do
  not justify, **NO_TRADE** (never manufacture). When a setup is valid at T, a prediction is FROZEN (immutable) BEFORE T+1 reveals.
  **This file NEVER computes any outcome.** Episodes are mechanically stratified + seeded (era × H4-context × session).
- **`bfsd_score.py`** — runs only AFTER all freezes. Reads `predictions.jsonl`, computes MFE/MAE (R), target-before-stop (P2R/P1R),
  time-to-resolution, era-stability, MORPH clusters, and the §11 incremental-baseline ladder. Cannot alter any prediction.
- Frozen schema: EPISODE, T, TS, ERA, SESSION, VOL, SIDE, ZONE, ENTRY, INVAL, RISK_ATR, H4_TREND, H4_PHASE, H1_TREND, H1_PHASE,
  EXP_DIR, MORPH, EXPECT. (N1–N6 market_intelligence = context-only, unratified → deferred; price-structure stands in, disclosed.)

## Batch log
> **SCOPE CORRECTION (CEO 2026-08-24):** BFSD-BATCH-1 below is **ONE negative hypothesis test of a PREDEFINED SMC morphology**
> (H4→H1-pullback→M15-zone-reaction). It is **NOT** open-ended morphology discovery, and it does **NOT** justify "no morphology
> qualifies" or "whole campaign confirmed." A predefined setup was imposed rather than letting structure emerge. Retained only as a
> single negative datapoint. Also: **era-stability is NOT required** — regime specialists are valid; conditioning is by N1 regime,
> not by cross-era invariance. True open-ended agnostic discovery (canonical N1–N3 state + primitive-agnostic descriptors, morphology
> emergence via observed recurring sequences) is the actual campaign — engine v2 (see below).

### BFSD-BATCH-1 (2026-08-23) — PREDEFINED-SETUP hypothesis test (trend-pullback-to-zone), NOT discovery
- **60 episodes × 400 candles** replayed strictly one-at-a-time (24,000 candle-steps); **599 frozen setups** (329 LONG / 270 SHORT),
  seeded/stratified; cooldown 16 candles. Zones: bull/bear FVG, bull/bear OB, PDH/PDL (all knowable≤T).
- **Outcome (post-replay, 2R:1R bracket; analytic driftless null P2R=0.333):**
  - OVERALL **P2R=0.324**, P1R=0.477, MFE_med=7.34R, MAE_med=5.86R → **at the driftless null**.
  - LONG P2R=0.301, SHORT P2R=0.352. Era-stability P2R: D=0.335 / C=0.358 / **O=0.282 (below null)** → not era-stable.
  - Best coarse cluster SHORT|rOB P2R=0.38 but D=0.44/C=0.45/**O=0.29** (fades OOS); LONG|bOB 0.32 flat; no era-stable cluster above null.
- **§11 incremental baseline ladder (decisive):** H4-context-only random entry P2R = LONG 0.352 / SHORT 0.343 (barely above null).
  Full frozen morphology (H4+H1-pullback+M15-zone-reaction) = LONG 0.301 / SHORT 0.352. **INCREMENTAL: LONG −0.051 / SHORT +0.009.**
  → The elaborate SMC zone/reaction/pullback morphology adds **≈0 information over coarse H4 context**, and H4 context itself barely
  clears the driftless null.
- **VERDICT (SCOPED):** THIS PREDEFINED SMC setup adds no information above the H4-context baseline in this batch → not promoted.
  This is a single negative hypothesis test, **NOT** a claim about morphology in general and **NOT** "campaign confirmed." Open-ended
  emergent discovery has not yet been run (that is engine v2). S5 remains the only *validated* edge to date; nothing here changes that
  either way.
- **Morphology identified (classified, not promoted):** `MORPH = H4{trend}|{phase}|H1{trend}|{phase}|{zone}|{session}` — the
  "HTF-trend + LTF-correction + zone-reaction continuation" family. Recurs abundantly (n=599) but information ≈ baseline.

## Next accumulation (autonomous)
- Enrich the morphology GRAMMAR the engine can freeze beyond trend-pullback-to-zone: sweep→reclaim→retest→displacement;
  compression→failed-breakout→acceptance-opposite→expansion; range-boundary rotation; CHoCH-reclaim. (CEO §9 — let new structures emerge.)
- Accumulate toward ≥50–100 blind observations **per fine morphology** (more episodes / broader strata) before any cluster verdict.
- Any cluster with era-stable P2R materially above the §11 baseline → PREREGISTER → mechanize → full quant gate (§13).
- If a genuinely new mechanism emerges outside the 14 modules → flag **POTENTIAL_NEW_MODULE** for CEO (do not self-invent).

### BFSD3-BATCH-1 (2026-08-24) — PRIMARY method: top-down canonical N-node candle-by-candle READING ledger
Engine `bfsd3_engine.py` (self-contained, N1/N2 computed LIVE + memoized per HTF bar — no cache). STRICT candle-by-candle,
top-down N1(regime/H4)->N2(bias/H1)->N3(zone map/M15, live)->N4 status(M5 2021+ only)->N6 decision + ENTRY_READINESS 0-100;
freeze actionable BEFORE next candle; NO outcome at freeze. Morphology NOT imposed/mined here. Scorer `bfsd3_score.py` (secondary).
- **54 episodes / 21,600 candles / decisions BUY 278 · SELL 175 · NO_TRADE 21,147 / 453 frozen actionable readings** (mostly
  NO_TRADE = context rarely justified looking, as intended). Full schema per record (N1/N2/N3/N4-status/N6/bias/readiness/zone/
  invalidation/expected-next/confidence). N4 available 194/453 (2021+).
- **Outcomes (2R:1R; null P2R=0.333):** OVERALL **P2R=0.358** (marginal over null), P1R=0.501; BUY 0.349 / SELL 0.371.
- **READINESS CALIBRATION (key finding):** the top-down readiness score is **NOT monotone / anti-predictive at the top** —
  bins [50,60)=0.375, [60,70)=0.363, [70,80)=0.385, **[80,101)=0.258** (highest readiness = worst, below null). The naive
  canonical-alignment readiness (N1 strength × N2 magnitude × zone proximity) does not predict success and must be recalibrated
  from outcomes (this stage), never trusted as constructed.
- **EMERGENT MORPHOLOGY (clustered from the frozen reading ledger, not imposed):** one cluster reached n>=25 —
  **`BULLISH|weak_up|normal|long|DISCOUNT|ASIA` -> P2R=0.562 (d=+0.205 vs base), n=32, era D19/C5/O8.**
  Regime-specialist candidate: Asia-session pullback into a DISCOUNT confluence zone during a weak-up H4 regime with H1 long bias.
  **UNDER-POWERED (n=32, D-era-heavy) -> NOT a verdict.** This is the first morphology surfaced by open-ended top-down discovery
  that the quant screens + the predefined-SMC test did not flag. **Action: ACCUMULATE more blind observations of this regime
  (Asia × weak-up × discount) toward n>=50-100 before preregister/mechanize.**
- **VERDICT (scoped):** top-down canonical reading is marginally above null overall; readiness anti-calibrated; ONE under-powered
  emergent regime-specialist candidate to accumulate. No promotion yet. S5 unchanged as the only *validated* edge.

### BFSD3-BATCH-2 (2026-08-24) — ACCUMULATION (3 seeds, deduped by candle) — candidate REGRESSED
Appended seeds 2025 + 777 to BFSD3-BATCH-1, deduped by candle T -> ~1,269 unique frozen top-down readings. base P2R=0.338 (~null).
- **The emergent candidate REGRESSED toward base as n grew:** `BULLISH|weak_up|normal|long|disc|AS` 0.562(n32) -> **0.451(n82)**
  (+0.205 -> +0.113 over base). The initial 0.562 was mostly small-sample noise; classic regression-to-the-mean. Still modestly
  above base, present all eras (D34/C19/O29) — a MILD tendency, not a strong specialist.
- **READINESS now robustly ANTI-CALIBRATED (monotone decreasing):** bins [50,60)=0.359 [60,70)=0.341 [70,80)=0.329 [80,101)=0.315
  (top bin n=203). The naive canonical readiness (N1 strength × N2 mag × zone proximity) is mildly ANTI-predictive -> must be
  inverted/discarded, never used as constructed. (Robust design finding.)
- **No strong regime specialist at adequate n.** Top-|d| clusters are all n~27 noise flyers (both signs: BEARISH|weak_down|compressed|
  short|prem|AS 0.556 n27; BULLISH|weak_up|high_choppy|long|disc|AS 0.171 n35). The only PERSISTENT family = **Asia-DISCOUNT-BUY in
  up/weak_up normal-vol** (~0.44 P2R across n~120 combined, +~0.10 over base) — a mild, era-spread regime tendency worth further
  accumulation before any mechanize decision.
- **VERDICT (scoped):** as blind observations accumulate, emergent candidates regress toward base; no robust specialist yet. One
  mild persistent tendency (Asia-discount-BUY) under continued accumulation. Readiness score anti-calibrated. No promotion. S5 unchanged.

### BFSD3-BATCH-3 (2026-08-24) — FULL ACCUMULATION VERDICT (5 seeds, 2,004 unique blind readings)
- **Candidate FULLY REGRESSED to base:** `BULLISH|weak_up|normal|long|disc|AS` n=32->82->126, P2R=**0.562->0.451->0.389**
  (now only +0.063 over base). The 0.562 was small-sample noise; no edge survives accumulation. Other Asia-discount-BUY cells split
  around base (up|normal 0.400 n65; high_choppy 0.155 n58; compressed 0.270 n74) — net ~base, no specialist.
- **Top-down reading overall = NULL:** OVERALL P2R=**0.326** (~null 0.333), BUY 0.318 / SELL 0.339, over 2,004 blind actionable readings.
- **Readiness ROBUSTLY ANTI-CALIBRATED (monotone, full scale):** 0.342->0.336->0.319->**0.293** (top bin n=335). The naive canonical
  readiness (N1 strength × N2 magnitude × zone proximity) is mildly ANTI-predictive — a stable, reproducible design finding.
- **SCOPED VERDICT:** the FIRST full pass of the PRIMARY top-down N-node reading (N6 decision = price interacting with nearest
  confluence zone in the N1/N2 bias direction) carries NO edge, and its emergent candidate regressed to base. This is a statement
  about THIS decision rule + zone-reaction reading, NOT a global "no morphology exists." S5 remains the only validated edge.
- **NEXT (broaden emergence):** the current N6 fires only on nearest-zone interaction; broaden the reading so richer morphologies can
  emerge (record the FULL per-candle decision/structure stream, add structural events beyond zone-tap: displacement, failed-break,
  reclaim, acceptance-shift), then re-cluster. Keep accumulating; promote only a cell that stays materially above base at n>=100.

### BFSD4-BATCH-2 (2026-08-24) — BROADENED observation, OUT-OF-SAMPLE (Batch-1 frozen, no retuning)
New engine `bfsd4_engine.py`: reader now OBSERVES + tags displacement/break/failed-break(sweep)/rejection/compression/expansion at
each candle and freezes when ANY structural event appears in a directional context (tags recorded, NOT setup gates). New seeds
111/222/333/444 -> new ledger `reading_ledger_b2.jsonl` (Batch-1 untouched). 2,154 unique out-of-sample frozen readings. Scorer
`bfsd4_score.py` (secondary).
- **Overall P2R=0.302 (~/below null 0.333)**; BUY 0.315 / SELL 0.281. The broadened reader has NO overall edge.
- **No structural TRIGGER carries edge:** DISP_up +0.053(n93, =momentum), REJ_low +0.011(n695), SWEEP_up +0.009, BREAK_up +0.002,
  REJ_high +0.001; SHORT-side NEGATIVE (BREAK_dn -0.047, DISP_dn -0.105) = era-trend (shorts fade in a rising instrument).
- **Emergent cells (n>=25) top at 0.40-0.43** but only ~+0.07-0.10 over true null and INCONSISTENT: `BULLISH|up|REJ_low|nearZone|AS`
  n=81 P2R=0.407 (era-spread D26/C26/O29) WORKS, but its `weak_up` sibling n=86 P2R=0.267 FAILS. Small-n flyers both signs.
- **WATCH-CANDIDATE (accumulate, do NOT promote):** `BULLISH|up|REJ_low|nearZone|AS` — up-H4-regime + rejection-of-lows at a demand
  zone in Asia -> BUY; coherent mechanism, n=81, 0.407, spread across eras. Decisive n>=100 accumulation test pending (Batch-1's
  candidate regressed at higher n).
- **VERDICT (scoped):** broadening the observation did NOT surface a robust edge; overall at/below null. One coherent watch-candidate
  under accumulation. No promotion. S5 unchanged as the only validated edge.

### BFSD4-BATCH-2 GROWN (2026-08-24, 8 seeds, 3,911 unique OOS readings) — watch-candidate held -> ASREJ-1 PREREGISTERED
- Overall P2R=**0.297** (below null); broadened reader loses on average (conditional cells only).
- Watch-candidate `BULLISH|up|REJ_low|nearZone|AS`: n=81->**124**, P2R=0.407->**0.387** — HELD (mild regression), **+0.054 over null
  0.333**, era spread D33/C39/**O52** (OOS-heavy). Companion `up|REJ_high|nearZone|AS` n=90/0.389. First cell to hold above base past
  n>=100 across eras.
- **-> PREREGISTERED as ASREJ-1** (see `PREREG_ASREJ1.md`): up-H4-regime + H1-long + rejection-of-lows at a demand N3 zone in Asia
  -> LONG, 2R:1R. MILD (gross expectancy ~+0.16R/trade), likely trend/era-flavored; **NOT promoted** — next = mechanize + FULL quant
  gate (costs/STRESS/2x/tail/LOYO/LOEO/effN/delay/neighbor/dedup/regime/portfolio-vs-S5). Rejection under costs is the expected, clean
  outcome. No P&L claim until the gate returns.
