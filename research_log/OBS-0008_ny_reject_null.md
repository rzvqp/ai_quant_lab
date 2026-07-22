# OBS-0008 — NY-session prior-day-high sweep-reject reversion (matched-null)
Type: Observation Record. **STRONG TENTATIVE — candidate-precursor, NOT yet a Discovery Candidate.** Date 2026-07-22 · XAUUSD H1 · loader · n=42 NY up-reject · escalates OBS-0003 (NRQ-1b).

**Q:** Does the NY up-reject reversion survive testing against the NY session's OWN forward baseline (not global drift) and a session-matched null?
**Pre-reg:** continuation-excess vs NY-baseline drift; matched null = random NY bars, same K, 3000 resamples; confirm if mean CI95<0 AND null left-tail p<0.05.

**Result:** K6 excess **−3.64, CI95[−6.90,−0.12] (excludes 0)**, null_left_p=**0.021**; K12 excess −4.80, CI95[−8.88,+0.05] (touches 0), null_left_p=0.029. P(continue)=0.36/0.26. The reject group reverses well below the NY-bar baseline.

**Verdict: leading lead, deliberately NOT frozen.** The effect survives a *pre-registered same-data matched null* — but it was **selected from ~12 session×direction cells** in OBS-0003, so null_left_p=0.021 is **not selection-corrected** (Bonferroni ~0.25) and n=42 is small. Freezing a Discovery Candidate here would risk manufacturing one from a selected cell.
**Escalation (blocking before any candidate):** OBS-0012 tests ALL reject cells under the same matched null (is NY-up uniquely significant?); then a reserved-holdout confirmation. Mechanism hypothesis (descriptive): NY-session stop-runs at prior-day highs that fail. No edge/strategy claim.
