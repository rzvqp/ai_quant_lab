# OBS-0017 — Marginal overshoot of a structural swing high: reversal tell?
Type: Observation Record. **NOT a Discovery Candidate.** Date 2026-07-22 · XAUUSD · **observation-first (TVRE primary)** · Python validation.
**First record produced under the corrected methodology (TradingView = eyes, Python = statistician).**

## TradingView Replay observation (origin of the question)
- **Session:** replay anchored **2025-03-09** (pre-cutoff), XAUUSD. Observed **H4** then **H1** (multi-TF).
- **Screenshots:** `screenshots/obs0017_h4_2025-03-09.png`, `screenshots/obs0017_h1_2025-03-09.png` (read visually; low-res strip — see limitation).
- **What I saw (SMC structure, H4):** an uptrend printing HH 2954.96 → HL 2916.82 → **HH 2956.31 — a *marginal* new high, only +1.35 (+0.05%) above the prior high** (a near-double-top with an "upside liquidity" tag) → **LL 2832.72 (a sharp ~124-pt breakdown)** → **LH 2929.98 (failed retest, highs never reclaimed)** → HL 2891.15. On H1 the same region showed demand order-blocks (+OB) below.
- **Behavioural read:** a swing high was *marginally overshot and then violently reversed*, with the retest failing — a textbook "failed breakout / liquidity sweep."

## Emergent question (from the observation, not a dataset)
At H4 **structural swing highs** (pivots), does a **marginal** overshoot (small failed new high, like the 2956.31 poke) precede reversal more reliably than a **decisive** break? This is distinct from my earlier nulls at arbitrary prior-**day** levels (OBS-0001/0004) — it concerns genuine swing structure.

## Python validation
Swing = pivot high/low (±3 bars); first later exceedance = event; overshoot in ATR; continuation-excess (detrended), K6/K12.
- **Swing highs (384):** corr(overshoot, excess) = −0.03/−0.07 (≈0, wrong sign). Marginal tercile K6 mean +1.2 (median −3.1), **CI95 spans 0**. **Not supported.**
- **Swing lows (309):** all terciles significantly negative-excess (K12 marginal −9.6 CI[−14.5,−4.5]; excludes 0) = a **break→bounce-up** tendency — but consistent with the ambient uptrend (buy-the-dip), **confound-suspected**.

## Verdict
**NEGATIVE for the observed hypothesis.** The marginal-overshoot-reversal pattern I watched at 2955 does **not** generalize across H4 swing highs (overshoot magnitude is uninformative). A vivid single instance was an anecdote — the statistician correctly refused to confirm it. The swing-**low** "break→bounce" is significant but almost surely trend-conditioning, not a level mechanism.
**Residue NRQ-6:** does the swing-low bounce survive regime control (test in flat/down sub-periods)? If it vanishes, it is pure buy-the-dip.
**Methodology note:** screenshots render as low-res horizontal strips (limited fine candle detail); I compensated with the SMC label/box structural data. Observation-first origin worked as intended (eyes → hypothesis → Python falsification).
