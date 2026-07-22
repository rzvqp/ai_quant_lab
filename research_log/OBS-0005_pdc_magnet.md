# OBS-0005 — Is the prior-day close (PDC) an intraday magnet?
Type: Observation Record. **NOT a Discovery Candidate.** Date 2026-07-22 · XAUUSD H1 · loader · 16,609 bars · new perspective (mean-reversion / anchor).

**Q:** Does intraday price mean-revert toward the prior-day close (a common "PDC magnet" belief)?
**Pre-reg:** side=sign(close−PDC); magnet ⇒ detrended forward move negative when above PDC, positive when below; corr(distance_to_PDC, forward move) < 0.

**Result (n≈8k/6.5k, CI95):** OPPOSITE of a magnet. Above PDC: forward move **+0.41** K6 (CI[+0.14,+0.70]), **+0.94** K12 (CI[+0.53,+1.38]). Below PDC: **−0.53** K6 (CI[−0.85,−0.20]), **−1.06** K12. corr = +0.043/+0.050. CIs exclude 0 → a small but clean **continuation** bias relative to PDC, not reversion.

**Verdict: NEGATIVE for the PDC-magnet assumption (challenged & refuted).** The weak continuation that appears instead is economically tiny (≈0.4–1.0 over 6–12h vs σ≈9–13) and is **plausibly a trend-clustering confound** (conditioning on "above PDC" selects post-rally states), the same confound flagged in OBS-0001 — so it is NOT claimed as an effect.
**Residue NRQ-4:** does any PDC-relative continuation survive *local* detrending (subtracting a trailing trend, not the global mean)? If it vanishes, it is pure trend-clustering.
