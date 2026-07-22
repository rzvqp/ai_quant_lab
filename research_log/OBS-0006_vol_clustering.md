# OBS-0006 — Volatility clustering and its session condition (ORQ-007)
Type: Observation Record. **NOT a Discovery Candidate** (confirmation + refinement of the promoted Volatility primitive). Date 2026-07-22 · XAUUSD H1 · loader · 16,623 bars · official metric Parkinson log-range r=ln(H/L).

**Q:** Confirm H1 volatility clustering on the official metric, and identify WHERE persistence concentrates (ORQ-007 clustering-condition).
**Pre-reg:** lag-autocorr of r; conditional r_(t+1) by r_t quartile; lag-1 acf within each session.

**Result:** Strong clustering — acf(r): lag1 **+0.53**, lag2 +0.37, lag3 +0.25, decaying to +0.17 by lag12, then a **rebound at lag24 (+0.345)** = clear intraday time-of-day (daily) volatility seasonality. High-quartile r_t ⇒ next-bar range **2.55×** that after low-quartile. Session condition: lag-1 persistence strongest in **Asia (+0.49)** and **NY (+0.41)**, weakest **London (+0.28)**; mean range highest NY (0.00305), lowest late (0.00166).

**Verdict: CONFIRMATION + two refinements.** (1) Persistence is **session-dependent** (Asia/NY > London). (2) A robust **lag-24 daily seasonality** in r — hour-of-day volatility signature. Both are concrete descriptive additions to the volatility primitive; neither is a new standalone phenomenon → no candidate.
**Residue NRQ-5:** is the lag-24 seasonality a fixed hour-of-day profile (news/session opens) separable from same-state clustering? Pre-register an hour-of-day mean-r profile + partial autocorr controlling for hour.
