# OBS-0016 — Asymmetric volatility / leverage effect on gold?
Type: Observation Record. **NOT a Discovery Candidate.** Date 2026-07-22 · XAUUSD daily · loader · 874 days.

**Q:** Does gold show the equity-style leverage effect (down days → higher next-day volatility)?
**Pre-reg:** next-day Parkinson range after up vs down days; corr(return_t, range_{t+1}); daily range persistence.

**Result:** next-day range after UP days **125.6e-4** (CI[118,133]) vs DOWN days **120.1e-4** (CI[113,127]) — overlapping CIs, and the sign is **opposite** to equities; corr(return_t, range_{t+1}) = **+0.064** (equities: negative). Daily range persistence corr = **+0.257**.

**Verdict: NEGATIVE for an equity-style leverage effect — gold's volatility is symmetric in return sign (challenges a "universal" assumption).** Daily-scale range persistence confirmed (+0.26), consistent with the H1 clustering (OBS-0006/0007).
**Residue:** gold vol asymmetry (if any) is weakly *opposite* to equities — a mechanism question (safe-haven inflows on down days dampening vol?) for later.
