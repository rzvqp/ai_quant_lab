# VOLPATH_PROTOCOL — Volatility Path Harvesting Frontier V1 (Phase 1 frozen protocol)

CEO mandate 2026-08-24. Question: **can the PATH of a predictable volatility expansion be harvested WITHOUT predicting direction?**
Phase-1 = INFORMATION-FIRST (no strategy). Generic breakout/fade retest PROHIBITED. S5 frozen (benchmark only). Broker DISABLED.

## §18 REQUIRED FIRST ACTION

### (1) Prior VOLTIME results reconstructed (from VOLTIME_LEDGER.md)
- **VOLTIME-1:** compression → expansion MAGNITUDE is real + cross-era-stable (compression-duration dur[25+] → 9.39 ATR forward range,
  P(2R either dir)=0.99, stable D0.95/C0.96/O0.97). ✔ the information foundation this frontier builds on.
- **VOLTIME-2/3/4/5 (monetization attempts, all null/negative):** compression breakout = WR 0.333 EXACT null / gross +0.000;
  direction-resolutions (displacement/acceptance/retest) ~null; session ORBs (Asia/London/NY DST-correct) net-negative; first-move-FADE
  net-negative (P(revert-to-mid-first)=0.365 → breaks CONTINUE 63.5%, not liquidity grabs). SF-3 = session-phase whipsaw map (US-session
  cleanest 0.088, macro choppiest 0.42).

### (2) Path properties ALREADY tested (do not re-run as-is)
Aggregate forward range/ATR; P(reach ±1.5 ATR EITHER dir); median time-to-1.5ATR; whipsaw = (both +1ATR AND −1ATR within window);
ONE revert metric (P(revert-to-mid before +1R continuation) = 0.365); breakout continuation/first-break (partial: raw + displacement/
acceptance/retest confirmations). Session-phase whipsaw structure (SF-3).

### (3) Genuinely NEW under this mandate (the object of Phase 1)
The FULL two-sided path GEOMETRY, none of which VOLTIME measured explicitly:
- **Two-sided barrier matrix:** P(+k reached), P(−k reached), and **P(BOTH sides reached)** at a barrier family k∈{0.5,1,1.5,2} ATR.
- **Path ordering** over the barrier family (UP_FIRST/DOWN_FIRST/BOTH_NEAR_SIMULTANEOUS/NEITHER at symmetric distances).
- **Midpoint recross DYNAMICS:** recross COUNT (not just first), time-to-first-recross, time-between-recrosses.
- **First-break follow-through GRANULARITY:** 1/2/4-bar follow-through + MFE/MAE after first break; continues/reverses/whipsaws/double-breaks.
- **DOUBLE-SIDED break sequence:** first side breaks → recross back into range → opposite side breaks (frequency/timing/magnitude) —
  the crux for whether a straddle harvests volatility or pays whipsaw twice.
- **Range CONSUMPTION profile:** fraction of eventual total excursion in first impulse / 2 / 4 / 8 bars / remainder.
- **Alternation** small state model (up/down 0.5ATR touches from mid: UP→DOWN, DOWN→UP, 3-step) — bounded, not sequence-mined.

### (4) Phase-1 measurement protocol (FROZEN, preregistered — no post-hoc barrier/threshold selection)
- **Qualifying event:** compression endpoint = bar T where causal compression is mature: `comp_dur ≥ 12` (consecutive ATR<ATR_ma), the
  VOLTIME-1 predictive state. Deduped to non-overlapping events (≥ H apart). Frozen at T (no future): `ref=close[T]`, `atr=atr[T]`,
  compression range `[rLo=min low, rHi=max high]` over the compression window (≤40 bars), `mid=(rHi+rLo)/2`.
- **Horizon:** H = 48 bars (12h). All excursions in ATR units from `ref` (two-sided metrics) or from range boundary (first-break metrics).
- **Barrier family (FROZEN):** k ∈ {0.5, 1.0, 1.5, 2.0} ATR, symmetric. Reported for ALL k (winner not chosen post-hoc).
- **Conditional context (frozen defs only):** SESSION (Asia/London/NY/Late via DST-correct session_tz), COMPRESSION severity (atr/atr_ma
  terciles), ERA (D≤2018/C19-22/O23+). No new regime invented after seeing outcomes.
- Output: `VOLPATH_INFORMATION_LEDGER.md` (all metrics) + `VOLPATH_PHASE1_REPORT.md` (findings SUPPORTED/NOT_SUPPORTED/AMBIGUOUS/
  UNANSWERABLE + hard-gate answer).

### (5) Preregistered hypothesis family (CEO §5 H1–H8, small, selection-controlled)
H1 compression → large two-sided opportunity but SYMMETRIC path ordering. H2 first-break DIRECTION weak, but first-break QUALITY predicts
persist-vs-recross. H3 some compression classes → frequent DOUBLE-SIDED excursions (harvestable). H4 others → ONE-SIDED escape (straddle
false-activation). H5 recross count/speed encodes whipsaw-vs-expansion. H6 session changes path geometry even without predicting direction.
H7 first impulse consumes most expansion (waiting destroys opportunity). H8 significant residual expansion remains AFTER early
classification (delayed non-directional structure viable). Each → SUPPORTED/NOT_SUPPORTED/AMBIGUOUS/UNANSWERABLE.

## §19 INITIAL CEO REPORT
VOLPATH_FRONTIER = OPEN · PRIOR_VOLTIME_RESULTS_RECONSTRUCTED = YES · GENERIC_BREAKOUT_RETEST = PROHIBITED ·
GENERIC_FADE_RETEST = PROHIBITED · PHASE1_INFORMATION_FIRST = YES · PATH_GEOMETRY_PROTOCOL_FROZEN = YES ·
PHASE2_STRATEGY_TESTING = NOT_YET_AUTHORIZED_UNTIL_PHASE1_GATE · S5 = FROZEN_UNTOUCHED · BROKER = DISABLED.
Proceeding directly to Phase-1 causal measurement (no wait for confirmation per §18).
