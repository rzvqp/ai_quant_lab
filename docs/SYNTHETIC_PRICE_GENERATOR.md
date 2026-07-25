# SYNTHETIC_PRICE_GENERATOR — code/synth_price.py

Purpose: manufacture OHLC+ATR price frames with KNOWN ground truth so the matched-null engine can be
calibrated (no edge → p uniform) and power-tested (injected edge → detection). It is NOT a backtester and
NOT part of the official engine; execution is always `mstrat.simulate`. It replaces the invalid practice of
validating on bare synthetic R-series (which caused the documented scale-mismatch miscalibration).

## Frame schema (consumed by mstrat.simulate unchanged)
`time` (int epoch, 900 s M15 grid), `open, high, low, close` (float), `volume` (int), `m_atr` (float, >0),
plus stratification helpers `session` (asia/london/ny by synthetic hour), `month`, `atrq` (ATR quintile).
`high`/`low` are constructed to bracket `open`/`close`; `m_atr` = 14-bar rolling mean true range (>0).

## gen_series(...) — data-generating process
- Conditional volatility: GARCH(1,1)-lite; `vol_clustering` in [0,1) sets persistence (0 = homoskedastic).
- Returns: `r_t = drift_t + ar1·(r_{t-1}-drift_{t-1}) + z_t·vol_t`; `ar1` gives momentum(+)/mean-reversion(−).
- Regimes: optional `[(start_frac, vol_mult, drift_add), …]` piecewise overlays.
- Gaps: `gap_rate` probability per bar of an open jump of `gap_size·local_sd`.
- Price = `p0·exp(cumsum(r))`; intrabar wicks scale with local vol.
- Fully seeded and reproducible (test_reproducible).

## Signal templates (signal_bars, dirs)
- `exo_signals` — EXOGENOUS, price-independent random bars + fixed direction. The clean ground-truth
  template for calibration/power: under a null series both observed and matched-null are exchangeable.
- `breakout_signals`, `sweep_signals`, `timeofday_signals` — ENDOGENOUS price-based rules used to stress
  the null against realistic structure (adversarial battery).

## inject_edge(df, signal_bars, dirs, edge_atr, horizon, seed)
Adds a persistent forward level shift of total size ≈ `edge_atr·ATR` spread over `horizon` bars after each
signal, in the signal's direction, then rebuilds OHLC and recomputes `m_atr`. `edge_atr=0` is a strict
no-op (test_inject_zero_is_noop). Ground truth: an alpha exists at these signals iff `edge_atr>0`. Verified
monotone: observed expectancy rises with `edge_atr` (test_edge_monotone, e.g. [-0.01, 0.28, 0.54, 0.97]).

## make_setups(...)
Builds engine-compatible setups `{si,ei=si+1,dir,stop,exit_kind,exit_param}` with ATR- or structural stops
and a chosen exit rule, for execution by `mstrat.simulate` (stop-floor + costs + overlap applied there).

## Tests: tests/test_synthetic_generator.py
OHLC validity, reproducibility, edge=0 no-op, edge raises expectancy, monotonicity in edge magnitude.
