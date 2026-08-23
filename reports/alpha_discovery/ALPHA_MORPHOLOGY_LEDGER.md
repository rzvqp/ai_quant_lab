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
### BFSD-BATCH-1 (2026-08-23) — top-down trend-pullback-to-zone morphology
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
- **VERDICT: no morphology promoted to MECHANIZE.** Under genuine strict candle-by-candle blind observation, top-down SMC structure
  does not carry directional information above baseline — consistent with the full quant-screen campaign (directional primitives →
  era-trend; structural → coinflip). S5 remains the sole edge.
- **Morphology identified (classified, not promoted):** `MORPH = H4{trend}|{phase}|H1{trend}|{phase}|{zone}|{session}` — the
  "HTF-trend + LTF-correction + zone-reaction continuation" family. Recurs abundantly (n=599) but information ≈ baseline.

## Next accumulation (autonomous)
- Enrich the morphology GRAMMAR the engine can freeze beyond trend-pullback-to-zone: sweep→reclaim→retest→displacement;
  compression→failed-breakout→acceptance-opposite→expansion; range-boundary rotation; CHoCH-reclaim. (CEO §9 — let new structures emerge.)
- Accumulate toward ≥50–100 blind observations **per fine morphology** (more episodes / broader strata) before any cluster verdict.
- Any cluster with era-stable P2R materially above the §11 baseline → PREREGISTER → mechanize → full quant gate (§13).
- If a genuinely new mechanism emerges outside the 14 modules → flag **POTENTIAL_NEW_MODULE** for CEO (do not self-invent).
