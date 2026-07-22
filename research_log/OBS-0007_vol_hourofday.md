# OBS-0007 — Volatility seasonality: hour-of-day profile vs same-state clustering
Type: Observation Record. **NOT a Discovery Candidate** (refines promoted Volatility primitive). Date 2026-07-22 · XAUUSD H1 · loader · 16,623 bars · NRQ-5.

**Q:** Is the lag-24 vol autocorrelation a fixed hour-of-day profile, and does 1-bar clustering survive deseasonalizing?
**Pre-reg:** mean r by UTC hour; rhat=r−hour_mean; compare acf1/acf24 of r vs rhat.

**Result:** Strong hour-of-day profile — peak **13–14h UTC (NY open, 47.9e-4)**, trough 20–21h/04h (~12–16e-4), **peak/trough 4.27×**. Deseasonalized: acf1 stays high (+0.47 vs raw +0.53) while acf24 drops (+0.24 vs +0.35 but ≠0).

**Verdict: CONFIRM + decomposition (robust, large n).** XAUUSD H1 volatility = (a) a **fixed intraday hour-of-day profile** (4.3×, NY-open peak) + (b) **same-state 1-bar clustering** that survives deseasonalizing + (c) residual **day-to-day regime persistence** (acf24 of rhat still +0.24). Three separable components; concrete addition to the Volatility primitive. Not novel → no candidate.
**Residue:** the residual daily persistence (c) = a vol-regime that spans a whole day beyond the hour profile; candidate for a "daily vol state" descriptor later.
