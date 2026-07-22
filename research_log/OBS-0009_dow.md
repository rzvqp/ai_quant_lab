# OBS-0009 — Day-of-week structure (volatility & returns)
Type: Observation Record. **NOT a Discovery Candidate.** Date 2026-07-22 · XAUUSD H1 · loader · E008-adjacent.

**Q:** Is there a repeatable weekday signature in H1 volatility or daily returns?
**Pre-reg:** mean Parkinson r by weekday; mean daily close-change by weekday; bootstrap CI.

**Result:** Volatility rises through the week — **Monday 24.8e-4 (CI[24.2,25.5]) < Friday 27.1e-4 (CI[26.4,27.8])**, non-overlapping CIs (~9% gradient). Returns: all weekday CIs include 0 (Thursday +4.10 barely touches [+0.05,+8.63]).

**Verdict: NEGATIVE for weekday returns; weak CONFIRM for a weekday volatility gradient (Fri>Mon).** Small, robust vol gradient; no exploitable directional weekday bias. Minor structural fact.
**Residue:** none material.
